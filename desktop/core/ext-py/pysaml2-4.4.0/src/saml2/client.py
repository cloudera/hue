# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
import six

"""Contains classes and functions that a SAML2.0 Service Provider (SP) may use
to conclude its tasks.
"""
from saml2.request import LogoutRequest
import saml2

from saml2 import saml, SAMLError
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_SOAP

import saml2.xmldsig as ds

from saml2.ident import decode, code
from saml2.httpbase import HTTPError
from saml2.s_utils import sid
from saml2.s_utils import status_message_factory
from saml2.s_utils import success_status_factory
from saml2.samlp import STATUS_REQUEST_DENIED
from saml2.samlp import STATUS_UNKNOWN_PRINCIPAL
from saml2.time_util import not_on_or_after
from saml2.saml import AssertionIDRef
from saml2.client_base import Base
from saml2.client_base import SignOnError
from saml2.client_base import LogoutError
from saml2.client_base import NoServiceDefined
from saml2.mdstore import destinations

import logging

logger = logging.getLogger(__name__)


class Saml2Client(Base):
    """ The basic pySAML2 service provider class """

    def prepare_for_authenticate(
            self, entityid=None, relay_state="",
            binding=saml2.BINDING_HTTP_REDIRECT, vorg="", nameid_format=None,
            scoping=None, consent=None, extensions=None, sign=None,
            response_binding=saml2.BINDING_HTTP_POST, **kwargs):
        """ Makes all necessary preparations for an authentication request.

        :param entityid: The entity ID of the IdP to send the request to
        :param relay_state: To where the user should be returned after
            successfull log in.
        :param binding: Which binding to use for sending the request
        :param vorg: The entity_id of the virtual organization I'm a member of
        :param nameid_format:
        :param scoping: For which IdPs this query are aimed.
        :param consent: Whether the principal have given her consent
        :param extensions: Possible extensions
        :param sign: Whether the request should be signed or not.
        :param response_binding: Which binding to use for receiving the response
        :param kwargs: Extra key word arguments
        :return: session id and AuthnRequest info
        """

        reqid, negotiated_binding, info = \
            self.prepare_for_negotiated_authenticate(
                entityid=entityid,
                relay_state=relay_state,
                binding=binding,
                vorg=vorg,
                nameid_format=nameid_format,
                scoping=scoping,
                consent=consent,
                extensions=extensions,
                sign=sign,
                response_binding=response_binding,
                **kwargs)

        assert negotiated_binding == binding

        return reqid, info

    def prepare_for_negotiated_authenticate(
            self, entityid=None, relay_state="", binding=None, vorg="",
            nameid_format=None, scoping=None, consent=None, extensions=None,
            sign=None, response_binding=saml2.BINDING_HTTP_POST, **kwargs):
        """ Makes all necessary preparations for an authentication request
        that negotiates
        which binding to use for authentication.

        :param entityid: The entity ID of the IdP to send the request to
        :param relay_state: To where the user should be returned after
            successfull log in.
        :param binding: Which binding to use for sending the request
        :param vorg: The entity_id of the virtual organization I'm a member of
        :param nameid_format:
        :param scoping: For which IdPs this query are aimed.
        :param consent: Whether the principal have given her consent
        :param extensions: Possible extensions
        :param sign: Whether the request should be signed or not.
        :param response_binding: Which binding to use for receiving the response
        :param kwargs: Extra key word arguments
        :return: session id and AuthnRequest info
        """

        expected_binding = binding

        for binding in [BINDING_HTTP_REDIRECT, BINDING_HTTP_POST]:
            if expected_binding and binding != expected_binding:
                continue

            destination = self._sso_location(entityid, binding)
            logger.info("destination to provider: %s", destination)

            reqid, request = self.create_authn_request(
                destination, vorg, scoping, response_binding, nameid_format,
                consent=consent, extensions=extensions, sign=sign,
                **kwargs)

            _req_str = str(request)

            logger.info("AuthNReq: %s", _req_str)

            try:
                args = {'sigalg': kwargs["sigalg"]}
            except KeyError:
                args = {}

            http_info = self.apply_binding(binding, _req_str, destination,
                                           relay_state, **args)

            return reqid, binding, http_info
        else:
            raise SignOnError(
                "No supported bindings available for authentication")

    def global_logout(self, name_id, reason="", expire=None, sign=None,
                      sign_alg=None, digest_alg=None):
        """ More or less a layer of indirection :-/
        Bootstrapping the whole thing by finding all the IdPs that should
        be notified.

        :param name_id: The identifier of the subject that wants to be
            logged out.
        :param reason: Why the subject wants to log out
        :param expire: The latest the log out should happen.
            If this time has passed don't bother.
        :param sign: Whether the request should be signed or not.
            This also depends on what binding is used.
        :return: Depends on which binding is used:
            If the HTTP redirect binding then a HTTP redirect,
            if SOAP binding has been used the just the result of that
            conversation.
        """

        if isinstance(name_id, six.string_types):
            name_id = decode(name_id)

        logger.info("logout request for: %s", name_id)

        # find out which IdPs/AAs I should notify
        entity_ids = self.users.issuers_of_info(name_id)
        return self.do_logout(name_id, entity_ids, reason, expire, sign,
                              sign_alg=sign_alg, digest_alg=digest_alg)

    def do_logout(self, name_id, entity_ids, reason, expire, sign=None,
                  expected_binding=None, sign_alg=None, digest_alg=None,
                  **kwargs):
        """

        :param name_id: Identifier of the Subject (a NameID instance)
        :param entity_ids: List of entity ids for the IdPs that have provided
            information concerning the subject
        :param reason: The reason for doing the logout
        :param expire: Try to logout before this time.
        :param sign: Whether to sign the request or not
        :param expected_binding: Specify the expected binding then not try it
            all
        :param kwargs: Extra key word arguments.
        :return:
        """
        # check time
        if not not_on_or_after(expire):  # I've run out of time
            # Do the local logout anyway
            self.local_logout(name_id)
            return 0, "504 Gateway Timeout", [], []

        not_done = entity_ids[:]
        responses = {}

        for entity_id in entity_ids:
            logger.debug("Logout from '%s'", entity_id)
            # for all where I can use the SOAP binding, do those first
            for binding in [BINDING_SOAP, BINDING_HTTP_POST,
                            BINDING_HTTP_REDIRECT]:
                if expected_binding and binding != expected_binding:
                    continue
                try:
                    srvs = self.metadata.single_logout_service(entity_id,
                                                               binding,
                                                               "idpsso")
                except:
                    srvs = None

                if not srvs:
                    logger.debug("No SLO '%s' service", binding)
                    continue

                destination = destinations(srvs)[0]
                logger.info("destination to provider: %s", destination)
                try:
                    session_info = self.users.get_info_from(name_id,
                                                            entity_id,
                                                            False)
                    session_indexes = [session_info['session_index']]
                except KeyError:
                    session_indexes = None
                req_id, request = self.create_logout_request(
                    destination, entity_id, name_id=name_id, reason=reason,
                    expire=expire, session_indexes=session_indexes)

                # to_sign = []
                if binding.startswith("http://"):
                    sign = True

                if sign is None:
                    sign = self.logout_requests_signed

                sigalg = None
                if sign:
                    if binding == BINDING_HTTP_REDIRECT:
                        sigalg = kwargs.get(
                            "sigalg", ds.DefaultSignature().get_sign_alg())
                        # key = kwargs.get("key", self.signkey)
                        srequest = str(request)
                    else:
                        srequest = self.sign(request, sign_alg=sign_alg,
                                             digest_alg=digest_alg)
                else:
                    srequest = str(request)

                relay_state = self._relay_state(req_id)

                http_info = self.apply_binding(binding, srequest, destination,
                                               relay_state, sigalg=sigalg)

                if binding == BINDING_SOAP:
                    response = self.send(**http_info)

                    if response and response.status_code == 200:
                        not_done.remove(entity_id)
                        response = response.text
                        logger.info("Response: %s", response)
                        res = self.parse_logout_request_response(response,
                                                                 binding)
                        responses[entity_id] = res
                    else:
                        logger.info("NOT OK response from %s", destination)

                else:
                    self.state[req_id] = {"entity_id": entity_id,
                                          "operation": "SLO",
                                          "entity_ids": entity_ids,
                                          "name_id": code(name_id),
                                          "reason": reason,
                                          "not_on_of_after": expire,
                                          "sign": sign}

                    responses[entity_id] = (binding, http_info)
                    not_done.remove(entity_id)

                # only try one binding
                break

        if not_done:
            # upstream should try later
            raise LogoutError("%s" % (entity_ids,))

        return responses

    def local_logout(self, name_id):
        """ Remove the user from the cache, equals local logout

        :param name_id: The identifier of the subject
        """
        self.users.remove_person(name_id)
        return True

    def is_logged_in(self, name_id):
        """ Check if user is in the cache

        :param name_id: The identifier of the subject
        """
        identity = self.users.get_identity(name_id)[0]
        return bool(identity)

    def handle_logout_response(self, response, sign_alg=None, digest_alg=None):
        """ handles a Logout response

        :param response: A response.Response instance
        :return: 4-tuple of (session_id of the last sent logout request,
            response message, response headers and message)
        """

        logger.info("state: %s", self.state)
        status = self.state[response.in_response_to]
        logger.info("status: %s", status)
        issuer = response.issuer()
        logger.info("issuer: %s", issuer)
        del self.state[response.in_response_to]
        if status["entity_ids"] == [issuer]:  # done
            self.local_logout(decode(status["name_id"]))
            return 0, "200 Ok", [("Content-type", "text/html")], []
        else:
            status["entity_ids"].remove(issuer)
            if "sign_alg" in status:
                sign_alg = status["sign_alg"]
            return self.do_logout(decode(status["name_id"]),
                                  status["entity_ids"],
                                  status["reason"], status["not_on_or_after"],
                                  status["sign"], sign_alg=sign_alg,
                                  digest_alg=digest_alg)

    def _use_soap(self, destination, query_type, **kwargs):
        _create_func = getattr(self, "create_%s" % query_type)
        _response_func = getattr(self, "parse_%s_response" % query_type)
        try:
            response_args = kwargs["response_args"]
            del kwargs["response_args"]
        except KeyError:
            response_args = None

        qid, query = _create_func(destination, **kwargs)

        response = self.send_using_soap(query, destination)

        if response.status_code == 200:
            if not response_args:
                response_args = {"binding": BINDING_SOAP}
            else:
                response_args["binding"] = BINDING_SOAP

            logger.info("Verifying response")
            if response_args:
                response = _response_func(response.content, **response_args)
            else:
                response = _response_func(response.content)
        else:
            raise HTTPError("%d:%s" % (response.status_code, response.error))

        if response:
            # not_done.remove(entity_id)
            logger.info("OK response from %s", destination)
            return response
        else:
            logger.info("NOT OK response from %s", destination)

        return None

    # noinspection PyUnusedLocal
    def do_authz_decision_query(self, entity_id, action,
                                subject_id, nameid_format,
                                evidence=None, resource=None,
                                sp_name_qualifier=None,
                                name_qualifier=None,
                                consent=None, extensions=None, sign=False):

        subject = saml.Subject(
            name_id=saml.NameID(text=subject_id, format=nameid_format,
                                sp_name_qualifier=sp_name_qualifier,
                                name_qualifier=name_qualifier))

        srvs = self.metadata.authz_service(entity_id, BINDING_SOAP)
        for dest in destinations(srvs):
            resp = self._use_soap(dest, "authz_decision_query",
                                  action=action, evidence=evidence,
                                  resource=resource, subject=subject)
            if resp:
                return resp

        return None

    def do_assertion_id_request(self, assertion_ids, entity_id,
                                consent=None, extensions=None, sign=False):

        srvs = self.metadata.assertion_id_request_service(entity_id,
                                                          BINDING_SOAP)
        if not srvs:
            raise NoServiceDefined("%s: %s" % (entity_id,
                                               "assertion_id_request_service"))

        if isinstance(assertion_ids, six.string_types):
            assertion_ids = [assertion_ids]

        _id_refs = [AssertionIDRef(_id) for _id in assertion_ids]

        for destination in destinations(srvs):
            res = self._use_soap(destination, "assertion_id_request",
                                 assertion_id_refs=_id_refs, consent=consent,
                                 extensions=extensions, sign=sign)
            if res:
                return res

        return None

    def do_authn_query(self, entity_id,
                       consent=None, extensions=None, sign=False):

        srvs = self.metadata.authn_request_service(entity_id, BINDING_SOAP)

        for destination in destinations(srvs):
            resp = self._use_soap(destination, "authn_query", consent=consent,
                                  extensions=extensions, sign=sign)
            if resp:
                return resp

        return None

    def do_attribute_query(self, entityid, subject_id,
                           attribute=None, sp_name_qualifier=None,
                           name_qualifier=None, nameid_format=None,
                           real_id=None, consent=None, extensions=None,
                           sign=False, binding=BINDING_SOAP, nsprefix=None):
        """ Does a attribute request to an attribute authority, this is
        by default done over SOAP.

        :param entityid: To whom the query should be sent
        :param subject_id: The identifier of the subject
        :param attribute: A dictionary of attributes and values that is
            asked for
        :param sp_name_qualifier: The unique identifier of the
            service provider or affiliation of providers for whom the
            identifier was generated.
        :param name_qualifier: The unique identifier of the identity
            provider that generated the identifier.
        :param nameid_format: The format of the name ID
        :param real_id: The identifier which is the key to this entity in the
            identity database
        :param binding: Which binding to use
        :param nsprefix: Namespace prefixes preferred before those automatically
            produced.
        :return: The attributes returned if BINDING_SOAP was used.
            HTTP args if BINDING_HTT_POST was used.
        """

        if real_id:
            response_args = {"real_id": real_id}
        else:
            response_args = {}

        if not binding:
            binding, destination = self.pick_binding("attribute_service",
                                                     None,
                                                     "attribute_authority",
                                                     entity_id=entityid)
        else:
            srvs = self.metadata.attribute_service(entityid, binding)
            if srvs is []:
                raise SAMLError("No attribute service support at entity")

            destination = destinations(srvs)[0]

        if binding == BINDING_SOAP:
            return self._use_soap(destination, "attribute_query",
                                  consent=consent, extensions=extensions,
                                  sign=sign, subject_id=subject_id,
                                  attribute=attribute,
                                  sp_name_qualifier=sp_name_qualifier,
                                  name_qualifier=name_qualifier,
                                  nameid_format=nameid_format,
                                  response_args=response_args)
        elif binding == BINDING_HTTP_POST:
            mid = sid()
            query = self.create_attribute_query(destination, subject_id,
                                                attribute, mid, consent,
                                                extensions, sign, nsprefix)
            self.state[query.id] = {"entity_id": entityid,
                                    "operation": "AttributeQuery",
                                    "subject_id": subject_id,
                                    "sign": sign}
            relay_state = self._relay_state(query.id)
            return self.apply_binding(binding, "%s" % query, destination,
                                      relay_state)
        else:
            raise SAMLError("Unsupported binding")

    def handle_logout_request(self, request, name_id, binding, sign=False,
                              relay_state=""):
        """
        Deal with a LogoutRequest

        :param request: The request as text string
        :param name_id: The id of the current user
        :param binding: Which binding the message came in over
        :param sign: Whether the response will be signed or not
        :return: Keyword arguments which can be used to send the response
            what's returned follow different patterns for different bindings.
            If the binding is BINDIND_SOAP, what is returned looks like this::

                {
                    "data": <the SOAP enveloped response>
                    "url": "",
                    'headers': [('content-type', 'application/soap+xml')]
                    'method': "POST
                }
        """
        logger.info("logout request: %s", request)

        _req = self._parse_request(request, LogoutRequest,
                                   "single_logout_service", binding)

        if _req.message.name_id == name_id:
            try:
                if self.local_logout(name_id):
                    status = success_status_factory()
                else:
                    status = status_message_factory("Server error",
                                                    STATUS_REQUEST_DENIED)
            except KeyError:
                status = status_message_factory("Server error",
                                                STATUS_REQUEST_DENIED)
        else:
            status = status_message_factory("Wrong user",
                                            STATUS_UNKNOWN_PRINCIPAL)

        if binding == BINDING_SOAP:
            response_bindings = [BINDING_SOAP]
        elif binding == BINDING_HTTP_POST or BINDING_HTTP_REDIRECT:
            response_bindings = [BINDING_HTTP_POST, BINDING_HTTP_REDIRECT]
        else:
            response_bindings = self.config.preferred_binding[
                "single_logout_service"]

        response = self.create_logout_response(_req.message, response_bindings,
                                               status, sign)
        rinfo = self.response_args(_req.message, response_bindings)

        return self.apply_binding(rinfo["binding"], response,
                                  rinfo["destination"], relay_state,
                                  response=True)
