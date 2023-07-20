# !/usr/bin/env python
#


"""Contains classes and functions that a SAML2.0 Service Provider (SP) may use
to conclude its tasks.
"""
import logging

import saml2
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_SOAP
from saml2 import SAMLError
from saml2 import saml
from saml2.client_base import Base
from saml2.client_base import LogoutError
from saml2.client_base import NoServiceDefined
from saml2.client_base import SignOnError
from saml2.httpbase import HTTPError
from saml2.ident import code
from saml2.ident import decode
from saml2.mdstore import locations
from saml2.s_utils import sid
from saml2.s_utils import status_message_factory
from saml2.s_utils import success_status_factory
from saml2.saml import AssertionIDRef
from saml2.samlp import STATUS_REQUEST_DENIED
from saml2.samlp import STATUS_UNKNOWN_PRINCIPAL
from saml2.time_util import not_on_or_after


logger = logging.getLogger(__name__)


class Saml2Client(Base):
    """The basic pySAML2 service provider class"""

    def prepare_for_authenticate(
        self,
        entityid=None,
        relay_state="",
        binding=saml2.BINDING_HTTP_REDIRECT,
        vorg="",
        nameid_format=None,
        scoping=None,
        consent=None,
        extensions=None,
        sign=None,
        sigalg=None,
        digest_alg=None,
        response_binding=saml2.BINDING_HTTP_POST,
        **kwargs,
    ):
        """Makes all necessary preparations for an authentication request.

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

        reqid, negotiated_binding, info = self.prepare_for_negotiated_authenticate(
            entityid=entityid,
            relay_state=relay_state,
            binding=binding,
            vorg=vorg,
            nameid_format=nameid_format,
            scoping=scoping,
            consent=consent,
            extensions=extensions,
            sign=sign,
            sigalg=sigalg,
            digest_alg=digest_alg,
            response_binding=response_binding,
            **kwargs,
        )

        if negotiated_binding != binding:
            raise ValueError(f"Negotiated binding '{negotiated_binding}' does not match binding to use '{binding}'")

        return reqid, info

    def prepare_for_negotiated_authenticate(
        self,
        entityid=None,
        relay_state="",
        binding=None,
        vorg="",
        nameid_format=None,
        scoping=None,
        consent=None,
        extensions=None,
        sign=None,
        response_binding=saml2.BINDING_HTTP_POST,
        sigalg=None,
        digest_alg=None,
        **kwargs,
    ):
        """Makes all necessary preparations for an authentication request
        that negotiates which binding to use for authentication.

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
        bindings_to_try = [BINDING_HTTP_REDIRECT, BINDING_HTTP_POST] if not expected_binding else [expected_binding]

        binding_destinations = []
        unsupported_bindings = []
        for binding in bindings_to_try:
            try:
                destination = self._sso_location(entityid, binding)
            except Exception:
                unsupported_bindings.append(binding)
            else:
                binding_destinations.append((binding, destination))

        for binding, destination in binding_destinations:
            logger.debug("destination to provider: %s", destination)

            # XXX - sign_post will embed the signature to the xml doc
            # XXX   ^through self.create_authn_request(...)
            # XXX - sign_redirect will add the signature to the query params
            # XXX   ^through self.apply_binding(...)
            sign_redirect = sign and binding == BINDING_HTTP_REDIRECT
            sign_post = sign and not sign_redirect

            reqid, request = self.create_authn_request(
                destination=destination,
                vorg=vorg,
                scoping=scoping,
                binding=response_binding,
                nameid_format=nameid_format,
                consent=consent,
                extensions=extensions,
                sign=sign_post,
                sign_alg=sigalg,
                digest_alg=digest_alg,
                **kwargs,
            )

            _req_str = str(request)
            logger.debug("AuthNReq: %s", _req_str)

            http_info = self.apply_binding(
                binding,
                _req_str,
                destination,
                relay_state,
                sign=sign_redirect,
                sigalg=sigalg,
            )

            return reqid, binding, http_info
        else:
            error_context = {
                "message": "No supported bindings available for authentication",
                "bindings_to_try": bindings_to_try,
                "unsupported_bindings": unsupported_bindings,
            }
            raise SignOnError(error_context)

    def global_logout(
        self,
        name_id,
        reason="",
        expire=None,
        sign=None,
        sign_alg=None,
        digest_alg=None,
    ):
        """More or less a layer of indirection :-/
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

        if isinstance(name_id, str):
            name_id = decode(name_id)

        logger.debug("logout request for: %s", name_id)

        # find out which IdPs/AAs I should notify
        entity_ids = self.users.issuers_of_info(name_id)
        return self.do_logout(
            name_id,
            entity_ids,
            reason,
            expire,
            sign,
            sign_alg=sign_alg,
            digest_alg=digest_alg,
        )

    def do_logout(
        self,
        name_id,
        entity_ids,
        reason,
        expire,
        sign=None,
        expected_binding=None,
        sign_alg=None,
        digest_alg=None,
        **kwargs,
    ):
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

        bindings_slo_preferred = self.config.preferred_binding["single_logout_service"]

        for entity_id in entity_ids:
            logger.debug("Logout from '%s'", entity_id)

            bindings_slo_supported = self.metadata.single_logout_service(entity_id=entity_id, typ="idpsso")
            bindings_slo_preferred_and_supported = (
                binding for binding in bindings_slo_preferred if binding in bindings_slo_supported
            )
            bindings_slo_choices = filter(
                lambda x: x,
                (
                    expected_binding,
                    *bindings_slo_preferred_and_supported,
                    *bindings_slo_supported,
                ),
            )
            binding = next(bindings_slo_choices, None)
            if not binding:
                logger.info(
                    {
                        "message": "Entity does not support SLO",
                        "entity": entity_id,
                    }
                )
                continue

            service_info = bindings_slo_supported[binding]
            service_location = next(locations(service_info), None)
            if not service_location:
                logger.info(
                    {
                        "message": "Entity SLO service does not have a location",
                        "entity": entity_id,
                        "service_location": service_location,
                    }
                )
                continue

            try:
                session_info = self.users.get_info_from(name_id, entity_id, False)
                session_index = session_info.get("session_index")
                session_indexes = [session_index] if session_index else None
            except KeyError:
                session_indexes = None

            sign = sign if sign is not None else self.logout_requests_signed
            sign_redirect = sign and binding == BINDING_HTTP_REDIRECT
            sign_post = sign and not sign_redirect

            log_report = {
                "message": "Invoking SLO on entity",
                "entity": entity_id,
                "binding": binding,
                "location": service_location,
                "session_indexes": session_indexes,
                "sign": sign,
            }
            logger.info(log_report)

            req_id, request = self.create_logout_request(
                service_location,
                entity_id,
                name_id=name_id,
                reason=reason,
                expire=expire,
                session_indexes=session_indexes,
                sign=sign_post,
                sign_alg=sign_alg,
                digest_alg=digest_alg,
            )
            relay_state = self._relay_state(req_id)
            http_info = self.apply_binding(
                binding,
                str(request),
                service_location,
                relay_state,
                sign=sign_redirect,
                sigalg=sign_alg,
            )

            if binding == BINDING_SOAP:
                response = self.send(**http_info)
                if response and response.status_code == 200:
                    not_done.remove(entity_id)
                    response_text = response.text
                    log_report_response = {
                        **log_report,
                        "message": "Response from SLO service",
                        "response_text": response_text,
                    }
                    logger.debug(log_report_response)
                    res = self.parse_logout_request_response(response_text, binding)
                    responses[entity_id] = res
                else:
                    log_report_response = {
                        **log_report,
                        "message": "Bad status_code response from SLO service",
                        "status_code": (response and response.status_code),
                    }
                    logger.info(log_report_response)
            else:
                self.state[req_id] = {
                    "entity_id": entity_id,
                    "operation": "SLO",
                    "entity_ids": entity_ids,
                    "name_id": code(name_id),
                    "reason": reason,
                    "not_on_or_after": expire,
                    "sign": sign,
                }
                responses[entity_id] = (binding, http_info)
                not_done.remove(entity_id)

        if not_done:
            # upstream should try later
            raise LogoutError(f"{entity_ids}")

        return responses

    def local_logout(self, name_id):
        """Remove the user from the cache, equals local logout

        :param name_id: The identifier of the subject
        """
        self.users.remove_person(name_id)
        return True

    def is_logged_in(self, name_id):
        """Check if user is in the cache

        :param name_id: The identifier of the subject
        """
        identity = self.users.get_identity(name_id)[0]
        return bool(identity)

    def handle_logout_response(self, response, sign_alg=None, digest_alg=None):
        """handles a Logout response

        :param response: A response.Response instance
        :return: 4-tuple of (session_id of the last sent logout request,
            response message, response headers and message)
        """

        logger.debug("state: %s", self.state)
        status = self.state[response.in_response_to]
        logger.debug("status: %s", status)
        issuer = response.issuer()
        logger.debug("issuer: %s", issuer)
        del self.state[response.in_response_to]
        if status["entity_ids"] == [issuer]:  # done
            self.local_logout(decode(status["name_id"]))
            return 0, "200 Ok", [("Content-type", "text/html")], []
        else:
            status["entity_ids"].remove(issuer)
            if "sign_alg" in status:
                sign_alg = status["sign_alg"]
            return self.do_logout(
                decode(status["name_id"]),
                status["entity_ids"],
                status["reason"],
                status["not_on_or_after"],
                status["sign"],
                sign_alg=sign_alg,
                digest_alg=digest_alg,
            )

    def _use_soap(self, destination, query_type, **kwargs):
        _create_func = getattr(self, f"create_{query_type}")
        _response_func = getattr(self, f"parse_{query_type}_response")
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

            logger.debug("Verifying response")
            if response_args:
                response = _response_func(response.content, **response_args)
            else:
                response = _response_func(response.content)
        else:
            raise HTTPError(f"{int(response.status_code)}:{response.error}")

        if response:
            # not_done.remove(entity_id)
            logger.debug("OK response from %s", destination)
            return response
        else:
            logger.debug("NOT OK response from %s", destination)

        return None

    # noinspection PyUnusedLocal
    def do_authz_decision_query(
        self,
        entity_id,
        action,
        subject_id,
        nameid_format,
        evidence=None,
        resource=None,
        sp_name_qualifier=None,
        name_qualifier=None,
        consent=None,
        extensions=None,
        sign=False,
    ):

        subject = saml.Subject(
            name_id=saml.NameID(
                text=subject_id,
                format=nameid_format,
                sp_name_qualifier=sp_name_qualifier,
                name_qualifier=name_qualifier,
            )
        )

        srvs = self.metadata.authz_service(entity_id, BINDING_SOAP)
        for dest in locations(srvs):
            resp = self._use_soap(
                dest, "authz_decision_query", action=action, evidence=evidence, resource=resource, subject=subject
            )
            if resp:
                return resp

        return None

    def do_assertion_id_request(self, assertion_ids, entity_id, consent=None, extensions=None, sign=False):

        srvs = self.metadata.assertion_id_request_service(entity_id, BINDING_SOAP)
        if not srvs:
            raise NoServiceDefined(f"{entity_id}: assertion_id_request_service")

        if isinstance(assertion_ids, str):
            assertion_ids = [assertion_ids]

        _id_refs = [AssertionIDRef(_id) for _id in assertion_ids]

        for destination in locations(srvs):
            res = self._use_soap(
                destination,
                "assertion_id_request",
                assertion_id_refs=_id_refs,
                consent=consent,
                extensions=extensions,
                sign=sign,
            )
            if res:
                return res

        return None

    def do_authn_query(self, entity_id, consent=None, extensions=None, sign=False):

        srvs = self.metadata.authn_request_service(entity_id, BINDING_SOAP)

        for destination in locations(srvs):
            resp = self._use_soap(destination, "authn_query", consent=consent, extensions=extensions, sign=sign)
            if resp:
                return resp

        return None

    def do_attribute_query(
        self,
        entityid,
        subject_id,
        attribute=None,
        sp_name_qualifier=None,
        name_qualifier=None,
        nameid_format=None,
        real_id=None,
        consent=None,
        extensions=None,
        sign=False,
        binding=BINDING_SOAP,
        nsprefix=None,
        sign_alg=None,
        digest_alg=None,
    ):
        """Does a attribute request to an attribute authority, this is
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
            binding, destination = self.pick_binding(
                "attribute_service", None, "attribute_authority", entity_id=entityid
            )
        else:
            srvs = self.metadata.attribute_service(entityid, binding)
            if srvs is []:
                raise SAMLError("No attribute service support at entity")

            destination = next(locations(srvs), None)

        if binding == BINDING_SOAP:
            return self._use_soap(
                destination,
                "attribute_query",
                consent=consent,
                extensions=extensions,
                sign=sign,
                sign_alg=sign_alg,
                digest_alg=digest_alg,
                subject_id=subject_id,
                attribute=attribute,
                sp_name_qualifier=sp_name_qualifier,
                name_qualifier=name_qualifier,
                format=nameid_format,
                response_args=response_args,
            )
        elif binding == BINDING_HTTP_POST:
            mid = sid()
            query = self.create_attribute_query(
                destination,
                name_id=subject_id,
                attribute=attribute,
                message_id=mid,
                consent=consent,
                extensions=extensions,
                sign=sign,
                sign_alg=sign_alg,
                digest_alg=digest_alg,
                nsprefix=nsprefix,
            )
            self.state[query.id] = {
                "entity_id": entityid,
                "operation": "AttributeQuery",
                "subject_id": subject_id,
                "sign": sign,
            }
            relay_state = self._relay_state(query.id)
            return self.apply_binding(
                binding,
                str(query),
                destination,
                relay_state,
                sign=False,
                sigalg=sign_alg,
            )
        else:
            raise SAMLError("Unsupported binding")

    def handle_logout_request(
        self,
        request,
        name_id,
        binding,
        sign=None,
        sign_alg=None,
        digest_alg=None,
        relay_state=None,
        sigalg=None,
        signature=None,
    ):
        """
        Deal with a LogoutRequest

        :param request: The request as text string
        :param name_id: The id of the current user
        :param binding: Which binding the message came in over
        :param sign: Whether the response will be signed or not
        :param sign_alg: The signing algorithm for the response
        :param digest_alg: The digest algorithm for the the response
        :param relay_state: The relay state of the request
        :param sigalg: The SigAlg query param of the request
        :param signature: The Signature query param of the request
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
        logger.debug("logout request: %s", request)

        _req = self.parse_logout_request(
            xmlstr=request,
            binding=binding,
            relay_state=relay_state,
            sigalg=sigalg,
            signature=signature,
        )

        if _req.message.name_id == name_id:
            try:
                if self.local_logout(name_id):
                    status = success_status_factory()
                else:
                    status = status_message_factory("Server error", STATUS_REQUEST_DENIED)
            except KeyError:
                status = status_message_factory("Server error", STATUS_REQUEST_DENIED)
        else:
            status = status_message_factory("Wrong user", STATUS_UNKNOWN_PRINCIPAL)

        response_bindings = {
            BINDING_SOAP: [BINDING_SOAP],
            BINDING_HTTP_POST: [BINDING_HTTP_POST, BINDING_HTTP_REDIRECT],
            BINDING_HTTP_REDIRECT: [BINDING_HTTP_REDIRECT, BINDING_HTTP_POST],
        }.get(binding, [])

        for response_binding in response_bindings:
            sign = sign if sign is not None else self.logout_responses_signed
            sign_redirect = sign and response_binding == BINDING_HTTP_REDIRECT
            sign_post = sign and not sign_redirect

            try:
                response = self.create_logout_response(
                    _req.message,
                    bindings=[response_binding],
                    status=status,
                    sign=sign_post,
                    sign_alg=sign_alg,
                    digest_alg=digest_alg,
                )
                rinfo = self.response_args(_req.message, [response_binding])

                return self.apply_binding(
                    rinfo["binding"],
                    response,
                    rinfo["destination"],
                    relay_state,
                    response=True,
                    sign=sign_redirect,
                    sigalg=sign_alg,
                )
            except Exception:
                continue

        log_ctx = {
            "message": "No supported bindings found to create LogoutResponse",
            "issuer": _req.issuer.text,
            "response_bindings": response_bindings,
        }
        raise SAMLError(log_ctx)
