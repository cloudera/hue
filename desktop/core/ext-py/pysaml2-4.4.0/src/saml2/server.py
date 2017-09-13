#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""Contains classes and functions that a SAML2.0 Identity provider (IdP)
or attribute authority (AA) may use to conclude its tasks.
"""
import logging
import os

import importlib
import dbm
import shelve
import six
import threading

from saml2 import saml
from saml2 import element_to_extension_element
from saml2 import class_name
from saml2 import BINDING_HTTP_REDIRECT
from saml2.argtree import add_path, is_set

from saml2.entity import Entity
from saml2.eptid import Eptid
from saml2.eptid import EptidShelve
from saml2.samlp import NameIDMappingResponse
from saml2.sdb import SessionStorage
from saml2.schema import soapenv

from saml2.request import AuthnRequest
from saml2.request import AssertionIDRequest
from saml2.request import AttributeQuery
from saml2.request import NameIDMappingRequest
from saml2.request import AuthzDecisionQuery
from saml2.request import AuthnQuery

from saml2.s_utils import MissingValue
from saml2.s_utils import rndstr
from saml2.s_utils import Unknown

from saml2.sigver import pre_signature_part
from saml2.sigver import signed_instance_factory
from saml2.sigver import CertificateError

from saml2.assertion import Assertion
from saml2.assertion import Policy
from saml2.assertion import restriction_from_attribute_spec
from saml2.assertion import filter_attribute_value_assertions

from saml2.ident import IdentDB, decode
from saml2.profile import ecp

logger = logging.getLogger(__name__)

AUTHN_DICT_MAP = {
    "decl": "authn_decl",
    "authn_auth": "authn_auth",
    "class_ref": "authn_class",
    "authn_instant": "authn_instant",
    "subject_locality": "subject_locality"
}


def _shelve_compat(name, *args, **kwargs):
    try:
        return shelve.open(name, *args, **kwargs)
    except dbm.error[0]:
        # Python 3 whichdb needs to try .db to determine type
        if name.endswith('.db'):
            name = name.rsplit('.db', 1)[0]
            return shelve.open(name, *args, **kwargs)
        else:
            raise


class Server(Entity):
    """ A class that does things that IdPs or AAs do """

    def __init__(self, config_file="", config=None, cache=None, stype="idp",
                 symkey="", msg_cb=None):
        Entity.__init__(self, stype, config, config_file, msg_cb=msg_cb)
        self.eptid = None
        self.init_config(stype)
        self.cache = cache
        self.ticket = {}
        #
        self.session_db = self.choose_session_storage()
        # Needed for
        self.symkey = symkey
        self.seed = rndstr()
        self.iv = os.urandom(16)
        self.lock = threading.Lock()

    def getvalid_certificate_str(self):
        if self.sec.cert_handler is not None:
            return self.sec.cert_handler._last_validated_cert
        return None

    def support_AssertionIDRequest(self):
        return True

    def support_AuthnQuery(self):
        return True

    def choose_session_storage(self):
        _spec = self.config.getattr("session_storage", "idp")
        if not _spec:
            return SessionStorage()
        elif isinstance(_spec, six.string_types):
            if _spec.lower() == "memory":
                return SessionStorage()
        else:  # Should be tuple
            typ, data = _spec
            if typ.lower() == "mongodb":
                from saml2.mongo_store import SessionStorageMDB

                return SessionStorageMDB(database=data, collection="session")

        raise NotImplementedError("No such storage type implemented")

    def init_config(self, stype="idp"):
        """ Remaining init of the server configuration

        :param stype: The type of Server ("idp"/"aa")
        """
        if stype == "aa":
            return

        # subject information is stored in a database
        # default database is in memory which is OK in some setups
        dbspec = self.config.getattr("subject_data", "idp")
        idb = None
        typ = ""
        if not dbspec:
            idb = {}
        elif isinstance(dbspec, six.string_types):
            idb = _shelve_compat(dbspec, writeback=True, protocol=2)
        else:  # database spec is a a 2-tuple (type, address)
            # print(>> sys.stderr, "DBSPEC: %s" % (dbspec,))
            (typ, addr) = dbspec
            if typ == "shelve":
                idb = _shelve_compat(addr, writeback=True, protocol=2)
            elif typ == "memcached":
                import memcache

                idb = memcache.Client(addr)
            elif typ == "dict":  # in-memory dictionary
                idb = {}
            elif typ == "mongodb":
                from saml2.mongo_store import IdentMDB

                self.ident = IdentMDB(database=addr, collection="ident")

            elif typ == "identdb":
                mod, clas = addr.rsplit('.', 1)
                mod = importlib.import_module(mod)
                self.ident = getattr(mod, clas)()

        if typ == "mongodb" or typ == "identdb":
            pass
        elif idb is not None:
            self.ident = IdentDB(idb)
        elif dbspec:
            raise Exception("Couldn't open identity database: %s" %
                            (dbspec,))

        try:
            _domain = self.config.getattr("domain", "idp")
            if _domain:
                self.ident.domain = _domain

            self.ident.name_qualifier = self.config.entityid

            dbspec = self.config.getattr("edu_person_targeted_id", "idp")
            if not dbspec:
                pass
            else:
                typ = dbspec[0]
                addr = dbspec[1]
                secret = dbspec[2]
                if typ == "shelve":
                    self.eptid = EptidShelve(secret, addr)
                elif typ == "mongodb":
                    from saml2.mongo_store import EptidMDB

                    self.eptid = EptidMDB(secret, database=addr,
                                          collection="eptid")
                else:
                    self.eptid = Eptid(secret)
        except Exception:
            self.ident.close()
            raise

    def wants(self, sp_entity_id, index=None):
        """ Returns what attributes the SP requires and which are optional
        if any such demands are registered in the Metadata.

        :param sp_entity_id: The entity id of the SP
        :param index: which of the attribute consumer services its all about
            if index == None then all attribute consumer services are clumped
            together.
        :return: 2-tuple, list of required and list of optional attributes
        """
        return self.metadata.attribute_requirement(sp_entity_id, index)

    def verify_assertion_consumer_service(self, request):
        _acs = request.assertion_consumer_service_url
        _aci = request.assertion_consumer_service_index
        _binding = request.protocol_binding
        _eid = request.issuer.text
        if _acs:
            # look up acs in for that binding in the metadata given the issuer
            # Assuming the format is entity
            for acs in self.metadata.assertion_consumer_service(_eid, _binding):
                if _acs == acs.text:
                    return True
        elif _aci:
            for acs in self.metadata.assertion_consumer_service(_eid, _binding):
                if _aci == acs.index:
                    return True

        return False

    # -------------------------------------------------------------------------
    def parse_authn_request(self, enc_request, binding=BINDING_HTTP_REDIRECT):
        """Parse a Authentication Request

        :param enc_request: The request in its transport format
        :param binding: Which binding that was used to transport the message
            to this entity.
        :return: A request instance
        """

        return self._parse_request(enc_request, AuthnRequest,
                                   "single_sign_on_service", binding)

    def parse_attribute_query(self, xml_string, binding):
        """ Parse an attribute query

        :param xml_string: The Attribute Query as an XML string
        :param binding: Which binding that was used for the request
        :return: A query instance
        """

        return self._parse_request(xml_string, AttributeQuery,
                                   "attribute_service", binding)

    def parse_authz_decision_query(self, xml_string, binding):
        """ Parse an authorization decision query

        :param xml_string: The Authz decision Query as an XML string
        :param binding: Which binding that was used when receiving this query
        :return: Query instance
        """

        return self._parse_request(xml_string, AuthzDecisionQuery,
                                   "authz_service", binding)

    def parse_assertion_id_request(self, xml_string, binding):
        """ Parse an assertion id query

        :param xml_string: The AssertionIDRequest as an XML string
        :param binding: Which binding that was used when receiving this request
        :return: Query instance
        """

        return self._parse_request(xml_string, AssertionIDRequest,
                                   "assertion_id_request_service", binding)

    def parse_authn_query(self, xml_string, binding):
        """ Parse an authn query

        :param xml_string: The AuthnQuery as an XML string
        :param binding: Which binding that was used when receiving this query
        :return: Query instance
        """

        return self._parse_request(xml_string, AuthnQuery,
                                   "authn_query_service", binding)

    def parse_name_id_mapping_request(self, xml_string, binding):
        """ Parse a nameid mapping request

        :param xml_string: The NameIDMappingRequest as an XML string
        :param binding: Which binding that was used when receiving this request
        :return: Query instance
        """

        return self._parse_request(xml_string, NameIDMappingRequest,
                                   "name_id_mapping_service", binding)

    @staticmethod
    def update_farg(in_response_to, consumer_url, farg=None):
        if not farg:
            farg = add_path(
                {},
                ['assertion', 'subject', 'subject_confirmation', 'method',
                 saml.SCM_BEARER])
            add_path(
                farg['assertion']['subject']['subject_confirmation'],
                ['subject_confirmation_data', 'in_response_to', in_response_to])
            add_path(
                farg['assertion']['subject']['subject_confirmation'],
                ['subject_confirmation_data', 'recipient', consumer_url])
        else:
            if not is_set(farg,
                          ['assertion', 'subject', 'subject_confirmation',
                           'method']):
                add_path(farg,
                         ['assertion', 'subject', 'subject_confirmation',
                          'method', saml.SCM_BEARER])
            if not is_set(farg,
                          ['assertion', 'subject', 'subject_confirmation',
                           'subject_confirmation_data', 'in_response_to']):
                add_path(farg,
                         ['assertion', 'subject', 'subject_confirmation',
                          'subject_confirmation_data', 'in_response_to',
                          in_response_to])
            if not is_set(farg, ['assertion', 'subject', 'subject_confirmation',
                                 'subject_confirmation_data', 'recipient']):
                add_path(farg,
                         ['assertion', 'subject', 'subject_confirmation',
                          'subject_confirmation_data', 'recipient',
                          consumer_url])
        return farg

    def setup_assertion(self, authn, sp_entity_id, in_response_to, consumer_url,
                        name_id, policy, _issuer, authn_statement, identity,
                        best_effort, sign_response, farg=None,
                        session_not_on_or_after=None, **kwargs):
        """
        Construct and return the Assertion

        :param authn: Authentication information
        :param sp_entity_id:
        :param in_response_to: The ID of the request this is an answer to
        :param consumer_url: The recipient of the assertion
        :param name_id: The NameID of the subject
        :param policy: Assertion policies
        :param _issuer: Issuer of the statement
        :param authn_statement: An AuthnStatement instance
        :param identity: Identity information about the Subject
        :param best_effort: Even if not the SPs demands can be met send a
            response.
        :param sign_response: Sign the response, only applicable if
            ErrorResponse
        :param kwargs: Extra keyword arguments
        :return: An Assertion instance
        """

        ast = Assertion(identity)
        ast.acs = self.config.getattr("attribute_converters", "idp")
        if policy is None:
            policy = Policy()
        try:
            ast.apply_policy(sp_entity_id, policy, self.metadata)
        except MissingValue as exc:
            if not best_effort:
                return self.create_error_response(in_response_to, consumer_url,
                                                  exc, sign_response)

        farg = self.update_farg(in_response_to, consumer_url, farg)

        if authn:  # expected to be a dictionary
            # Would like to use dict comprehension but ...
            authn_args = dict(
                [(AUTHN_DICT_MAP[k], v) for k, v in authn.items() if
                 k in AUTHN_DICT_MAP])
            authn_args.update(kwargs)

            assertion = ast.construct(
                sp_entity_id, self.config.attribute_converters, policy,
                issuer=_issuer, farg=farg['assertion'], name_id=name_id,
                session_not_on_or_after=session_not_on_or_after,
                **authn_args)

        elif authn_statement:  # Got a complete AuthnStatement
            assertion = ast.construct(
                sp_entity_id, self.config.attribute_converters, policy,
                issuer=_issuer, authn_statem=authn_statement,
                farg=farg['assertion'], name_id=name_id,
                **kwargs)
        else:
            assertion = ast.construct(
                sp_entity_id, self.config.attribute_converters, policy,
                issuer=_issuer, farg=farg['assertion'], name_id=name_id,
                session_not_on_or_after=session_not_on_or_after,
                **kwargs)
        return assertion

    def _authn_response(self, in_response_to, consumer_url,
                        sp_entity_id, identity=None, name_id=None,
                        status=None, authn=None, issuer=None, policy=None,
                        sign_assertion=False, sign_response=False,
                        best_effort=False, encrypt_assertion=False,
                        encrypt_cert_advice=None, encrypt_cert_assertion=None,
                        authn_statement=None,
                        encrypt_assertion_self_contained=False,
                        encrypted_advice_attributes=False,
                        pefim=False, sign_alg=None, digest_alg=None,
                        farg=None, session_not_on_or_after=None):
        """ Create a response. A layer of indirection.

        :param in_response_to: The session identifier of the request
        :param consumer_url: The URL which should receive the response
        :param sp_entity_id: The entity identifier of the SP
        :param identity: A dictionary with attributes and values that are
            expected to be the bases for the assertion in the response.
        :param name_id: The identifier of the subject
        :param status: The status of the response
        :param authn: A dictionary containing information about the
            authn context.
        :param issuer: The issuer of the response
        :param policy:
        :param sign_assertion: Whether the assertion should be signed or not
        :param sign_response: Whether the response should be signed or not
        :param best_effort: Even if not the SPs demands can be met send a
            response.
        :param encrypt_assertion: True if assertions should be encrypted.
        :param encrypt_assertion_self_contained: True if all encrypted
        assertions should have alla namespaces
        selfcontained.
        :param encrypted_advice_attributes: True if assertions in the advice
        element should be encrypted.
        :param encrypt_cert_advice: Certificate to be used for encryption of
        assertions in the advice element.
        :param encrypt_cert_assertion: Certificate to be used for encryption
        of assertions.
        :param authn_statement: Authentication statement.
        :param sign_assertion: True if assertions should be signed.
        :param pefim: True if a response according to the PEFIM profile
        should be created.
        :param farg: Argument to pass on to the assertion constructor
        :return: A response instance
        """

        if farg is None:
            assertion_args = {}

        args = {}
        # if identity:
        _issuer = self._issuer(issuer)

        # if encrypt_assertion and show_nameid:
        #    tmp_name_id = name_id
        #    name_id = None
        #    name_id = None
        #    tmp_authn = authn
        #    authn = None
        #    tmp_authn_statement = authn_statement
        #    authn_statement = None

        if pefim:
            encrypted_advice_attributes = True
            encrypt_assertion_self_contained = True
            assertion_attributes = self.setup_assertion(
                None, sp_entity_id, None, None, None, policy, None, None,
                identity, best_effort, sign_response, farg=farg)
            assertion = self.setup_assertion(
                authn, sp_entity_id, in_response_to, consumer_url, name_id,
                policy, _issuer, authn_statement, [], True, sign_response,
                farg=farg, session_not_on_or_after=session_not_on_or_after)
            assertion.advice = saml.Advice()

            # assertion.advice.assertion_id_ref.append(saml.AssertionIDRef())
            # assertion.advice.assertion_uri_ref.append(saml.AssertionURIRef())
            assertion.advice.assertion.append(assertion_attributes)
        else:
            assertion = self.setup_assertion(
                authn, sp_entity_id, in_response_to, consumer_url, name_id,
                policy, _issuer, authn_statement, identity, True,
                sign_response, farg=farg,
                session_not_on_or_after=session_not_on_or_after)

        to_sign = []
        if not encrypt_assertion:
            if sign_assertion:
                assertion.signature = pre_signature_part(assertion.id,
                                                         self.sec.my_cert, 2,
                                                         sign_alg=sign_alg,
                                                         digest_alg=digest_alg)
                to_sign.append((class_name(assertion), assertion.id))

        args["assertion"] = assertion

        if (self.support_AssertionIDRequest() or self.support_AuthnQuery()):
            self.session_db.store_assertion(assertion, to_sign)

        return self._response(
            in_response_to, consumer_url, status, issuer, sign_response,
            to_sign, sp_entity_id=sp_entity_id,
            encrypt_assertion=encrypt_assertion,
            encrypt_cert_advice=encrypt_cert_advice,
            encrypt_cert_assertion=encrypt_cert_assertion,
            encrypt_assertion_self_contained=encrypt_assertion_self_contained,
            encrypted_advice_attributes=encrypted_advice_attributes,
            sign_assertion=sign_assertion,
            pefim=pefim, sign_alg=sign_alg, digest_alg=digest_alg, **args)

    # ------------------------------------------------------------------------

    # noinspection PyUnusedLocal
    def create_attribute_response(self, identity, in_response_to, destination,
                                  sp_entity_id, userid="", name_id=None,
                                  status=None, issuer=None,
                                  sign_assertion=False, sign_response=False,
                                  attributes=None, sign_alg=None,
                                  digest_alg=None, farg=None, **kwargs):
        """ Create an attribute assertion response.

        :param identity: A dictionary with attributes and values that are
            expected to be the bases for the assertion in the response.
        :param in_response_to: The session identifier of the request
        :param destination: The URL which should receive the response
        :param sp_entity_id: The entity identifier of the SP
        :param userid: A identifier of the user
        :param name_id: The identifier of the subject
        :param status: The status of the response
        :param issuer: The issuer of the response
        :param sign_assertion: Whether the assertion should be signed or not
        :param sign_response: Whether the whole response should be signed
        :param attributes:
        :param kwargs: To catch extra keyword arguments
        :return: A response instance
        """

        policy = self.config.getattr("policy", "aa")

        if not name_id and userid:
            try:
                name_id = self.ident.construct_nameid(userid, policy,
                                                      sp_entity_id)
                logger.warning("Unspecified NameID format")
            except Exception:
                pass

        to_sign = []

        if identity:
            farg = self.update_farg(in_response_to, sp_entity_id, farg=farg)

            _issuer = self._issuer(issuer)
            ast = Assertion(identity)
            if policy:
                ast.apply_policy(sp_entity_id, policy, self.metadata)
            else:
                policy = Policy()

            if attributes:
                restr = restriction_from_attribute_spec(attributes)
                ast = filter_attribute_value_assertions(ast)

            assertion = ast.construct(
                sp_entity_id, self.config.attribute_converters, policy,
                issuer=_issuer, name_id=name_id,
                farg=farg['assertion'])

            if sign_assertion:
                assertion.signature = pre_signature_part(assertion.id,
                                                         self.sec.my_cert, 1,
                                                         sign_alg=sign_alg,
                                                         digest_alg=digest_alg)
                # Just the assertion or the response and the assertion ?
                to_sign = [(class_name(assertion), assertion.id)]
                kwargs['sign_assertion'] = True

            kwargs["assertion"] = assertion

        if sp_entity_id:
            kwargs['sp_entity_id'] = sp_entity_id

        return self._response(in_response_to, destination, status, issuer,
                              sign_response, to_sign, sign_alg=sign_alg,
                              digest_alg=digest_alg, **kwargs)

    # ------------------------------------------------------------------------

    def gather_authn_response_args(self, sp_entity_id, name_id_policy, userid,
                                   **kwargs):
        param_default = {
            'sign_assertion': False,
            'sign_response': False,
            'encrypt_assertion': False,
            'encrypt_assertion_self_contained': True,
            'encrypted_advice_attributes': False,
            'encrypt_cert_advice': None,
            'encrypt_cert_assertion': None
        }

        args = {}

        try:
            args["policy"] = kwargs["release_policy"]
        except KeyError:
            args["policy"] = self.config.getattr("policy", "idp")

        try:
            args['best_effort'] = kwargs["best_effort"]
        except KeyError:
            args['best_effort'] = False

        for param in ['sign_assertion', 'sign_response', 'encrypt_assertion',
                      'encrypt_assertion_self_contained',
                      'encrypted_advice_attributes', 'encrypt_cert_advice',
                      'encrypt_cert_assertion']:
            try:
                _val = kwargs[param]
            except:
                _val = None

            if _val is None:
                _val = self.config.getattr(param, "idp")

            if _val is None:
                args[param] = param_default[param]
            else:
                args[param] = _val

        for arg, attr, eca, pefim in [
            ('encrypted_advice_attributes', 'verify_encrypt_cert_advice',
             'encrypt_cert_advice', kwargs["pefim"]),
            ('encrypt_assertion', 'verify_encrypt_cert_assertion',
             'encrypt_cert_assertion', False)]:

            if args[arg] or pefim:
                _enc_cert = self.config.getattr(attr, "idp")

                if _enc_cert is not None:
                    if kwargs[eca] is None:
                        raise CertificateError(
                            "No SPCertEncType certificate for encryption "
                            "contained in authentication "
                            "request.")
                    if not _enc_cert(kwargs[eca]):
                        raise CertificateError(
                            "Invalid certificate for encryption!")

        if 'name_id' not in kwargs or not kwargs['name_id']:
            nid_formats = []
            for _sp in self.metadata[sp_entity_id]["spsso_descriptor"]:
                if "name_id_format" in _sp:
                    nid_formats.extend([n["text"] for n in
                                        _sp["name_id_format"]])
            try:
                snq = name_id_policy.sp_name_qualifier
            except AttributeError:
                snq = sp_entity_id

            if not snq:
                snq = sp_entity_id

            kwa = {"sp_name_qualifier": snq}

            try:
                kwa["format"] = name_id_policy.format
            except AttributeError:
                pass

            _nids = self.ident.find_nameid(userid, **kwa)
            # either none or one
            if _nids:
                args['name_id'] = _nids[0]
            else:
                args['name_id'] = self.ident.construct_nameid(
                    userid, args['policy'], sp_entity_id, name_id_policy)
                logger.debug("construct_nameid: %s => %s", userid,
                             args['name_id'])
        else:
            args['name_id'] = kwargs['name_id']

        for param in ['status', 'farg']:
            try:
                args[param] = kwargs[param]
            except KeyError:
                pass

        return args

    def create_authn_response(self, identity, in_response_to, destination,
                              sp_entity_id, name_id_policy=None, userid=None,
                              name_id=None, authn=None, issuer=None,
                              sign_response=None, sign_assertion=None,
                              encrypt_cert_advice=None,
                              encrypt_cert_assertion=None,
                              encrypt_assertion=None,
                              encrypt_assertion_self_contained=True,
                              encrypted_advice_attributes=False, pefim=False,
                              sign_alg=None, digest_alg=None,
                              session_not_on_or_after=None,
                              **kwargs):
        """ Constructs an AuthenticationResponse

        :param identity: Information about an user
        :param in_response_to: The identifier of the authentication request
            this response is an answer to.
        :param destination: Where the response should be sent
        :param sp_entity_id: The entity identifier of the Service Provider
        :param name_id_policy: How the NameID should be constructed
        :param userid: The subject identifier
        :param name_id: The identifier of the subject. A saml.NameID instance.
        :param authn: Dictionary with information about the authentication
            context
        :param issuer: Issuer of the response
        :param sign_assertion: Whether the assertion should be signed or not.
        :param sign_response: Whether the response should be signed or not.
        :param encrypt_assertion: True if assertions should be encrypted.
        :param encrypt_assertion_self_contained: True if all encrypted
        assertions should have alla namespaces
        selfcontained.
        :param encrypted_advice_attributes: True if assertions in the advice
        element should be encrypted.
        :param encrypt_cert_advice: Certificate to be used for encryption of
        assertions in the advice element.
        :param encrypt_cert_assertion: Certificate to be used for encryption
        of assertions.
        :param sign_assertion: True if assertions should be signed.
        :param pefim: True if a response according to the PEFIM profile
        should be created.
        :return: A response instance
        """

        try:
            args = self.gather_authn_response_args(
                sp_entity_id, name_id_policy=name_id_policy, userid=userid,
                name_id=name_id, sign_response=sign_response,
                sign_assertion=sign_assertion,
                encrypt_cert_advice=encrypt_cert_advice,
                encrypt_cert_assertion=encrypt_cert_assertion,
                encrypt_assertion=encrypt_assertion,
                encrypt_assertion_self_contained
                =encrypt_assertion_self_contained,
                encrypted_advice_attributes=encrypted_advice_attributes,
                pefim=pefim, **kwargs)
        except IOError as exc:
            response = self.create_error_response(in_response_to,
                                                  destination,
                                                  sp_entity_id,
                                                  exc, name_id)
            return ("%s" % response).split("\n")

        try:
            _authn = authn
            if (sign_assertion or sign_response) and \
                    self.sec.cert_handler.generate_cert():
                with self.lock:
                    self.sec.cert_handler.update_cert(True)
                    return self._authn_response(
                        in_response_to, destination, sp_entity_id, identity,
                        authn=_authn, issuer=issuer, pefim=pefim,
                        sign_alg=sign_alg, digest_alg=digest_alg,
                        session_not_on_or_after=session_not_on_or_after, **args)
            return self._authn_response(
                in_response_to, destination, sp_entity_id, identity,
                authn=_authn, issuer=issuer, pefim=pefim, sign_alg=sign_alg,
                digest_alg=digest_alg,
                session_not_on_or_after=session_not_on_or_after, **args)

        except MissingValue as exc:
            return self.create_error_response(in_response_to, destination,
                                              sp_entity_id, exc, name_id)

    def create_authn_request_response(self, identity, in_response_to,
                                      destination, sp_entity_id,
                                      name_id_policy=None, userid=None,
                                      name_id=None, authn=None, authn_decl=None,
                                      issuer=None, sign_response=False,
                                      sign_assertion=False,
                                      session_not_on_or_after=None, **kwargs):

        return self.create_authn_response(identity, in_response_to, destination,
                                          sp_entity_id, name_id_policy, userid,
                                          name_id, authn, issuer,
                                          sign_response, sign_assertion,
                                          authn_decl=authn_decl,
                                          session_not_on_or_after=session_not_on_or_after)

    # noinspection PyUnusedLocal
    def create_assertion_id_request_response(self, assertion_id, sign=False,
                                             sign_alg=None,
                                             digest_alg=None, **kwargs):
        """

        :param assertion_id:
        :param sign:
        :return:
        """

        try:
            (assertion, to_sign) = self.session_db.get_assertion(assertion_id)
        except KeyError:
            raise Unknown

        if to_sign:
            if assertion.signature is None:
                assertion.signature = pre_signature_part(assertion.id,
                                                         self.sec.my_cert, 1,
                                                         sign_alg=sign_alg,
                                                         digest_alg=digest_alg)

            return signed_instance_factory(assertion, self.sec, to_sign)
        else:
            return assertion

    # noinspection PyUnusedLocal
    def create_name_id_mapping_response(self, name_id=None, encrypted_id=None,
                                        in_response_to=None,
                                        issuer=None, sign_response=False,
                                        status=None, sign_alg=None,
                                        digest_alg=None, **kwargs):
        """
        protocol for mapping a principal's name identifier into a
        different name identifier for the same principal.
        Done over soap.

        :param name_id:
        :param encrypted_id:
        :param in_response_to:
        :param issuer:
        :param sign_response:
        :param status:
        :return:
        """
        # Done over SOAP

        ms_args = self.message_args()

        _resp = NameIDMappingResponse(name_id, encrypted_id,
                                      in_response_to=in_response_to, **ms_args)

        if sign_response:
            return self.sign(_resp, sign_alg=sign_alg, digest_alg=digest_alg)
        else:
            logger.info("Message: %s", _resp)
            return _resp

    def create_authn_query_response(self, subject, session_index=None,
                                    requested_context=None, in_response_to=None,
                                    issuer=None, sign_response=False,
                                    status=None, sign_alg=None, digest_alg=None,
                                    **kwargs):
        """
        A successful <Response> will contain one or more assertions containing
        authentication statements.

        :return:
        """

        margs = self.message_args()
        asserts = []
        for statement in self.session_db.get_authn_statements(
                subject.name_id, session_index, requested_context):
            asserts.append(saml.Assertion(authn_statement=statement,
                                          subject=subject, **margs))

        if asserts:
            args = {"assertion": asserts}
        else:
            args = {}

        return self._response(in_response_to, "", status, issuer,
                              sign_response, to_sign=[], sign_alg=sign_alg,
                              digest_alg=digest_alg, **args)

    # ---------

    def parse_ecp_authn_request(self):
        pass

    def create_ecp_authn_request_response(self, acs_url, identity,
                                          in_response_to, destination,
                                          sp_entity_id, name_id_policy=None,
                                          userid=None, name_id=None, authn=None,
                                          issuer=None, sign_response=False,
                                          sign_assertion=False, **kwargs):

        # ----------------------------------------
        # <ecp:Response
        # ----------------------------------------

        ecp_response = ecp.Response(assertion_consumer_service_url=acs_url)
        header = soapenv.Header()
        header.extension_elements = [element_to_extension_element(ecp_response)]

        # ----------------------------------------
        # <samlp:Response
        # ----------------------------------------

        response = self.create_authn_response(identity, in_response_to,
                                              destination, sp_entity_id,
                                              name_id_policy, userid, name_id,
                                              authn, issuer,
                                              sign_response, sign_assertion)
        body = soapenv.Body()
        body.extension_elements = [element_to_extension_element(response)]

        soap_envelope = soapenv.Envelope(header=header, body=body)

        return "%s" % soap_envelope

    def close(self):
        self.ident.close()

    def clean_out_user(self, name_id):
        """
        Remove all authentication statements that belongs to a user identified
        by a NameID instance

        :param name_id: NameID instance
        :return: The local identifier for the user
        """

        lid = self.ident.find_local_id(name_id)
        logger.info("Clean out %s", lid)

        # remove the authentications
        try:
            for _nid in [decode(x) for x in self.ident.db[lid].split(" ")]:
                try:
                    self.session_db.remove_authn_statements(_nid)
                except KeyError:
                    pass
        except KeyError:
            pass

        return lid
