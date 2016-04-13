#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""Contains classes and functions that a SAML2.0 Identity provider (IdP)
or attribute authority (AA) may use to conclude its tasks.
"""
import logging
import os

import importlib
import shelve
import threading

from saml2 import saml
from saml2 import element_to_extension_element
from saml2 import class_name
from saml2 import BINDING_HTTP_REDIRECT

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

from saml2.s_utils import MissingValue, Unknown, rndstr

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


class Server(Entity):
    """ A class that does things that IdPs or AAs do """

    def __init__(self, config_file="", config=None, cache=None, stype="idp",
                 symkey=""):
        Entity.__init__(self, stype, config, config_file)
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
        elif isinstance(_spec, basestring):
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
        elif isinstance(dbspec, basestring):
            idb = shelve.open(dbspec, writeback=True)
        else:  # database spec is a a 2-tuple (type, address)
            #print >> sys.stderr, "DBSPEC: %s" % (dbspec,)
            (typ, addr) = dbspec
            if typ == "shelve":
                idb = shelve.open(addr, writeback=True)
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
        :return: A dictionary with keys:
            consumer_url - as gotten from the SPs entity_id and the metadata
            id - the id of the request
            sp_entity_id - the entity id of the SP
            request - The verified request
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

    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------

    def _authn_response(self, in_response_to, consumer_url,
                        sp_entity_id, identity=None, name_id=None,
                        status=None, authn=None, issuer=None, policy=None,
                        sign_assertion=False, sign_response=False,
                        best_effort=False, encrypt_assertion=False,
                        encrypt_cert=None, authn_statement=None):
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
        :param sign_assertion: Whether the assertion should be signed or not
        :param sign_response: Whether the response should be signed or not
        :param best_effort: Even if not the SPs demands can be met send a
            response.
        :return: A response instance
        """

        to_sign = []
        args = {}
        #if identity:
        _issuer = self._issuer(issuer)
        ast = Assertion(identity)
        ast.acs = self.config.getattr("attribute_converters", "idp")
        if policy is None:
            policy = Policy()
        try:
            ast.apply_policy(sp_entity_id, policy, self.metadata)
        except MissingValue, exc:
            if not best_effort:
                return self.create_error_response(in_response_to, consumer_url,
                                                  exc, sign_response)

        if authn:  # expected to be a dictionary
            # Would like to use dict comprehension but ...
            authn_args = dict([
                (AUTHN_DICT_MAP[k], v) for k, v in authn.items()
                if k in AUTHN_DICT_MAP])

            assertion = ast.construct(sp_entity_id, in_response_to,
                                      consumer_url, name_id,
                                      self.config.attribute_converters,
                                      policy, issuer=_issuer,
                                      **authn_args)
        elif authn_statement:  # Got a complete AuthnStatement
            assertion = ast.construct(sp_entity_id, in_response_to,
                                      consumer_url, name_id,
                                      self.config.attribute_converters,
                                      policy, issuer=_issuer,
                                      authn_statem=authn_statement)
        else:
            assertion = ast.construct(sp_entity_id, in_response_to,
                                      consumer_url, name_id,
                                      self.config.attribute_converters,
                                      policy, issuer=_issuer)

        if sign_assertion is not None and sign_assertion:
            assertion.signature = pre_signature_part(assertion.id,
                                                     self.sec.my_cert, 1)
            # Just the assertion or the response and the assertion ?
            to_sign = [(class_name(assertion), assertion.id)]

        # Store which assertion that has been sent to which SP about which
        # subject.

        # self.cache.set(assertion.subject.name_id.text,
        #                 sp_entity_id, {"ava": identity, "authn": authn},
        #                 assertion.conditions.not_on_or_after)

        args["assertion"] = assertion

        if self.support_AssertionIDRequest() or self.support_AuthnQuery():
            self.session_db.store_assertion(assertion, to_sign)

        return self._response(in_response_to, consumer_url, status, issuer,
                              sign_response, to_sign, encrypt_assertion=encrypt_assertion,
                              encrypt_cert=encrypt_cert, **args)

    # ------------------------------------------------------------------------

    #noinspection PyUnusedLocal
    def create_attribute_response(self, identity, in_response_to, destination,
                                  sp_entity_id, userid="", name_id=None,
                                  status=None, issuer=None,
                                  sign_assertion=False, sign_response=False,
                                  attributes=None, **kwargs):
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
        args = {}
        if identity:
            _issuer = self._issuer(issuer)
            ast = Assertion(identity)
            if policy:
                ast.apply_policy(sp_entity_id, policy, self.metadata)
            else:
                policy = Policy()

            if attributes:
                restr = restriction_from_attribute_spec(attributes)
                ast = filter_attribute_value_assertions(ast)

            assertion = ast.construct(sp_entity_id, in_response_to,
                                      destination, name_id,
                                      self.config.attribute_converters,
                                      policy, issuer=_issuer)

            if sign_assertion:
                assertion.signature = pre_signature_part(assertion.id,
                                                         self.sec.my_cert, 1)
                # Just the assertion or the response and the assertion ?
                to_sign = [(class_name(assertion), assertion.id)]

            args["assertion"] = assertion

        return self._response(in_response_to, destination, status, issuer,
                              sign_response, to_sign, **args)

    # ------------------------------------------------------------------------

    def create_authn_response(self, identity, in_response_to, destination,
                              sp_entity_id, name_id_policy=None, userid=None,
                              name_id=None, authn=None, issuer=None,
                              sign_response=None, sign_assertion=None,
                              encrypt_cert=None, encrypt_assertion=None,
                              **kwargs):
        """ Constructs an AuthenticationResponse

        :param identity: Information about an user
        :param in_response_to: The identifier of the authentication request
            this response is an answer to.
        :param destination: Where the response should be sent
        :param sp_entity_id: The entity identifier of the Service Provider
        :param name_id_policy: How the NameID should be constructed
        :param userid: The subject identifier
        :param authn: Dictionary with information about the authentication
            context
        :param issuer: Issuer of the response
        :param sign_assertion: Whether the assertion should be signed or not.
        :param sign_response: Whether the response should be signed or not.
        :return: A response instance
        """

        try:
            policy = kwargs["release_policy"]
        except KeyError:
            policy = self.config.getattr("policy", "idp")

        try:
            best_effort = kwargs["best_effort"]
        except KeyError:
            best_effort = False

        if sign_assertion is None:
            sign_assertion = self.config.getattr("sign_assertion", "idp")
        if sign_assertion is None:
            sign_assertion = False

        if sign_response is None:
            sign_response = self.config.getattr("sign_response", "idp")
        if sign_response is None:
            sign_response = False

        if encrypt_assertion is None:
            encrypt_assertion = self.config.getattr("encrypt_assertion", "idp")
        if encrypt_assertion is None:
            encrypt_assertion = False

        if encrypt_assertion:
            if encrypt_cert is not None:
                verify_encrypt_cert = self.config.getattr("verify_encrypt_cert", "idp")
                if verify_encrypt_cert is not None:
                    if not verify_encrypt_cert(encrypt_cert):
                        raise CertificateError("Invalid certificate for encryption!")
            else:
                raise CertificateError("No SPCertEncType certificate for encryption contained in authentication "
                                       "request.")
        else:
            encrypt_assertion = False

        if not name_id:
            try:
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
                    name_id = _nids[0]
                else:
                    name_id = self.ident.construct_nameid(userid, policy,
                                                          sp_entity_id,
                                                          name_id_policy)
                    logger.debug("construct_nameid: %s => %s" % (userid,
                                                                 name_id))
            except IOError, exc:
                response = self.create_error_response(in_response_to,
                                                      destination,
                                                      sp_entity_id,
                                                      exc, name_id)
                return ("%s" % response).split("\n")

        try:
            _authn = authn
            if (sign_assertion or sign_response) and self.sec.cert_handler.generate_cert():
                with self.lock:
                    self.sec.cert_handler.update_cert(True)
                    return self._authn_response(in_response_to,  # in_response_to
                                                destination,  # consumer_url
                                                sp_entity_id,  # sp_entity_id
                                                identity,  # identity as dictionary
                                                name_id,
                                                authn=_authn,
                                                issuer=issuer,
                                                policy=policy,
                                                sign_assertion=sign_assertion,
                                                sign_response=sign_response,
                                                best_effort=best_effort,
                                                encrypt_assertion=encrypt_assertion,
                                                encrypt_cert=encrypt_cert)
            return self._authn_response(in_response_to,  # in_response_to
                                        destination,  # consumer_url
                                        sp_entity_id,  # sp_entity_id
                                        identity,  # identity as dictionary
                                        name_id,
                                        authn=_authn,
                                        issuer=issuer,
                                        policy=policy,
                                        sign_assertion=sign_assertion,
                                        sign_response=sign_response,
                                        best_effort=best_effort,
                                        encrypt_assertion=encrypt_assertion,
                                        encrypt_cert=encrypt_cert)

        except MissingValue, exc:
            return self.create_error_response(in_response_to, destination,
                                              sp_entity_id, exc, name_id)

    def create_authn_request_response(self, identity, in_response_to,
                                      destination, sp_entity_id,
                                      name_id_policy=None, userid=None,
                                      name_id=None, authn=None, authn_decl=None,
                                      issuer=None, sign_response=False,
                                      sign_assertion=False, **kwargs):

        return self.create_authn_response(identity, in_response_to, destination,
                                          sp_entity_id, name_id_policy, userid,
                                          name_id, authn, issuer,
                                          sign_response, sign_assertion,
                                          authn_decl=authn_decl)

    #noinspection PyUnusedLocal
    def create_assertion_id_request_response(self, assertion_id, sign=False,
                                             **kwargs):
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
                                                         self.sec.my_cert, 1)

            return signed_instance_factory(assertion, self.sec, to_sign)
        else:
            return assertion

    #noinspection PyUnusedLocal
    def create_name_id_mapping_response(self, name_id=None, encrypted_id=None,
                                        in_response_to=None,
                                        issuer=None, sign_response=False,
                                        status=None, **kwargs):
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
            return self.sign(_resp)
        else:
            logger.info("Message: %s" % _resp)
            return _resp

    def create_authn_query_response(self, subject, session_index=None,
                                    requested_context=None, in_response_to=None,
                                    issuer=None, sign_response=False,
                                    status=None, **kwargs):
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
                              sign_response, to_sign=[], **args)

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
        logger.info("Clean out %s" % lid)

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