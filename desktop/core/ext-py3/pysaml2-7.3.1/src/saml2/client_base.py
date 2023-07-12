#!/usr/bin/env python
#

"""Contains classes and functions that a SAML2.0 Service Provider (SP) may use
to conclude its tasks.
"""
import logging
import threading
import time
from typing import Mapping
from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import urlparse
from warnings import warn as _warn

import saml2
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_PAOS
from saml2 import BINDING_SOAP
from saml2 import SAMLError
from saml2 import saml
from saml2 import samlp
from saml2 import soap
from saml2.entity import Entity
from saml2.extension import sp_type
from saml2.extension.requested_attributes import RequestedAttribute
from saml2.extension.requested_attributes import RequestedAttributes
from saml2.mdstore import locations
from saml2.population import Population
from saml2.profile import ecp
from saml2.profile import paos
from saml2.response import AssertionIDResponse
from saml2.response import AttributeResponse
from saml2.response import AuthnQueryResponse
from saml2.response import AuthnResponse
from saml2.response import AuthzResponse
from saml2.response import NameIDMappingResponse
from saml2.response import StatusError
from saml2.s_utils import UnravelError
from saml2.s_utils import do_attributes
from saml2.s_utils import signature
from saml2.saml import NAMEID_FORMAT_PERSISTENT
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.saml import AuthnContextClassRef
from saml2.samlp import AttributeQuery
from saml2.samlp import AuthnQuery
from saml2.samlp import AuthnRequest
from saml2.samlp import AuthzDecisionQuery
from saml2.samlp import Extensions
from saml2.samlp import NameIDMappingRequest
from saml2.samlp import RequestedAuthnContext
from saml2.soap import make_soap_enveloped_saml_thingy


logger = logging.getLogger(__name__)

SSO_BINDING = saml2.BINDING_HTTP_REDIRECT

FORM_SPEC = """<form method="post" action="%s">
   <input type="hidden" name="SAMLRequest" value="%s" />
   <input type="hidden" name="RelayState" value="%s" />
   <input type="submit" value="Submit" />
</form>"""

LAX = False

ECP_SERVICE = "urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp"
ACTOR = "http://schemas.xmlsoap.org/soap/actor/next"
MIME_PAOS = "application/vnd.paos+xml"


class IdpUnspecified(SAMLError):
    pass


class VerifyError(SAMLError):
    pass


class SignOnError(SAMLError):
    pass


class LogoutError(SAMLError):
    pass


class NoServiceDefined(SAMLError):
    pass


def create_requested_attribute_node(requested_attrs, attribute_converters):
    items = []
    for attr in requested_attrs:
        friendly_name = attr.get("friendly_name")
        name = attr.get("name")
        name_format = attr.get("name_format")
        is_required = str(attr.get("required", False)).lower()

        if not name and not friendly_name:
            raise ValueError("Missing required attribute: 'name' or 'friendly_name'")

        if not name:
            for converter in attribute_converters:
                try:
                    name = converter._to[friendly_name.lower()]
                except KeyError:
                    continue
                else:
                    if not name_format:
                        name_format = converter.name_format
                    break

        if not friendly_name:
            for converter in attribute_converters:
                try:
                    friendly_name = converter._fro[name.lower()]
                except KeyError:
                    continue
                else:
                    if not name_format:
                        name_format = converter.name_format
                    break

        items.append(
            RequestedAttribute(
                is_required=is_required,
                name_format=name_format,
                friendly_name=friendly_name,
                name=name,
            )
        )

    node = RequestedAttributes(extension_elements=items)
    return node


class Base(Entity):
    """The basic pySAML2 service provider class"""

    def __init__(
        self, config=None, identity_cache=None, state_cache=None, virtual_organization="", config_file="", msg_cb=None
    ):
        """
        :param config: A saml2.config.Config instance
        :param identity_cache: Where the class should store identity information
        :param state_cache: Where the class should keep state information
        :param virtual_organization: A specific virtual organization
        """

        Entity.__init__(self, "sp", config, config_file, virtual_organization, msg_cb=msg_cb)

        self.users = Population(identity_cache)
        self.lock = threading.Lock()
        # for server state storage
        if state_cache is None:
            self.state = {}  # in memory storage
        else:
            self.state = state_cache

        attribute_defaults = {
            "logout_requests_signed": False,
            "logout_responses_signed": False,
            "allow_unsolicited": False,
            "authn_requests_signed": False,
            "want_assertions_signed": False,
            "want_response_signed": True,
            "want_assertions_or_response_signed": False,
        }
        for attr, val_default in attribute_defaults.items():
            val_config = self.config.getattr(attr, "sp")
            val = val_config if val_config is not None else val_default
            if val == "true":
                val = True
            setattr(self, attr, val)

        if self.entity_type == "sp" and not any(
            [
                self.want_assertions_signed,
                self.want_response_signed,
                self.want_assertions_or_response_signed,
            ]
        ):
            warn_msg = (
                "The SAML service provider accepts "
                "unsigned SAML Responses and Assertions. "
                "This configuration is insecure. "
                "Consider setting want_assertions_signed, want_response_signed "
                "or want_assertions_or_response_signed configuration options."
            )
            logger.warning(warn_msg)
            _warn(warn_msg)

        self.artifact2response = {}

    #
    # Private methods
    #

    def _relay_state(self, session_id):
        vals = [session_id, str(int(time.time()))]
        if self.config.secret is None:
            vals.append(signature("", vals))
        else:
            vals.append(signature(self.config.secret, vals))
        return "|".join(vals)

    def _sso_location(self, entityid=None, binding=BINDING_HTTP_REDIRECT):
        if entityid:
            # verify that it's in the metadata
            srvs = self.metadata.single_sign_on_service(entityid, binding)
            if srvs:
                return next(locations(srvs), None)
            else:
                logger.info("_sso_location: %s, %s", entityid, binding)
                raise IdpUnspecified("No IdP to send to given the premises")

        # get the idp location from the metadata. If there is more than one
        # IdP in the configuration raise exception
        eids = self.metadata.with_descriptor("idpsso")
        if len(eids) > 1:
            raise IdpUnspecified(f"Too many IdPs to choose from: {eids}")

        try:
            srvs = self.metadata.single_sign_on_service(list(eids.keys())[0], binding)
            return next(locations(srvs), None)

        except IndexError:
            raise IdpUnspecified("No IdP to send to given the premises")

    def sso_location(self, entityid=None, binding=BINDING_HTTP_REDIRECT):
        return self._sso_location(entityid, binding)

    def _my_name(self):
        return self.config.name

    #
    # Public API
    #

    def add_vo_information_about_user(self, name_id):
        """Add information to the knowledge I have about the user. This is
        for Virtual organizations.

        :param name_id: The subject identifier
        :return: A possibly extended knowledge.
        """

        ava = {}
        try:
            (ava, _) = self.users.get_identity(name_id)
        except KeyError:
            pass

        # is this a Virtual Organization situation
        if self.vorg:
            if self.vorg.do_aggregation(name_id):
                # Get the extended identity
                ava = self.users.get_identity(name_id)[0]
        return ava

    # noinspection PyUnusedLocal
    @staticmethod
    def is_session_valid(_session_id):
        """Place holder. Supposed to check if the session is still valid."""
        return True

    def service_urls(self, binding=BINDING_HTTP_POST):
        _res = self.config.endpoint("assertion_consumer_service", binding, "sp")
        if _res:
            return _res
        else:
            return None

    # XXX DONE sp create > _message
    def create_authn_request(
        self,
        destination,
        vorg="",
        scoping=None,
        binding=BINDING_HTTP_POST,
        nameid_format=None,
        service_url_binding=None,
        message_id=0,
        consent=None,
        extensions=None,
        sign=None,
        sign_prepare=None,
        sign_alg=None,
        digest_alg=None,
        allow_create=None,
        requested_attributes=None,
        **kwargs,
    ):
        """Creates an authentication request.

        :param destination: Where the request should be sent.
        :param vorg: The virtual organization the service belongs to.
        :param scoping: The scope of the request
        :param binding: The protocol to use for the Response !!
        :param nameid_format: Format of the NameIDPolicy
        :param service_url_binding: Where the reply should be sent dependent
            on reply binding.
        :param message_id: The identifier for this request
        :param consent: Whether the principal have given her consent
        :param extensions: Possible extensions
        :param sign: Whether the request should be signed or not.
        :param sign_prepare: Whether the signature should be prepared or not.
        :param sign_alg: The request signature algorithm
        :param digest_alg: The request digest algorithm
        :param allow_create: If the identity provider is allowed, in the course
            of fulfilling the request, to create a new identifier to represent
            the principal.
        :param requested_attributes: A list of dicts which define attributes to
            be used as eIDAS Requested Attributes for this request. If not
            defined the configuration option requested_attributes will be used,
            if defined. The format is the same as the requested_attributes
            configuration option.
        :param kwargs: Extra key word arguments
        :return: either a tuple of request ID and <samlp:AuthnRequest> instance
                 or a tuple of request ID and str when sign is set to True
        """
        args = {}

        # AssertionConsumerServiceURL
        # AssertionConsumerServiceIndex
        hide_assertion_consumer_service = self.config.getattr("hide_assertion_consumer_service", "sp")
        assertion_consumer_service_url = kwargs.pop("assertion_consumer_service_urls", [None])[0] or kwargs.pop(
            "assertion_consumer_service_url", None
        )
        assertion_consumer_service_index = kwargs.pop("assertion_consumer_service_index", None)
        service_url = (self.service_urls(service_url_binding or binding) or [None])[0]
        if hide_assertion_consumer_service:
            args["assertion_consumer_service_url"] = None
            binding = None
        elif assertion_consumer_service_url:
            args["assertion_consumer_service_url"] = assertion_consumer_service_url
        elif assertion_consumer_service_index:
            args["assertion_consumer_service_index"] = assertion_consumer_service_index
        elif service_url:
            args["assertion_consumer_service_url"] = service_url

        # ProviderName
        provider_name = kwargs.get("provider_name")
        if not provider_name and binding != BINDING_PAOS:
            provider_name = self._my_name()
        args["provider_name"] = provider_name

        requested_authn_context = (
            kwargs.pop("requested_authn_context", None) or self.config.getattr("requested_authn_context", "sp") or {}
        )
        if isinstance(requested_authn_context, RequestedAuthnContext):
            args["requested_authn_context"] = requested_authn_context
        elif isinstance(requested_authn_context, Mapping):
            requested_authn_context_accrs = requested_authn_context.get("authn_context_class_ref", [])
            requested_authn_context_comparison = requested_authn_context.get("comparison", "exact")
            if requested_authn_context_accrs:
                args["requested_authn_context"] = RequestedAuthnContext(
                    authn_context_class_ref=[AuthnContextClassRef(accr) for accr in requested_authn_context_accrs],
                    comparison=requested_authn_context_comparison,
                )
        else:
            logger.warning(
                {
                    "message": "Cannot process requested_authn_context",
                    "requested_authn_context": requested_authn_context,
                    "type_of_requested_authn_context": type(requested_authn_context),
                }
            )

        # Allow argument values either as class instances or as dictionaries
        # all of these have cardinality 0..1
        _msg = AuthnRequest()
        for param in ["scoping", "conditions", "subject"]:
            _item = kwargs.pop(param, None)
            if not _item:
                continue

            if isinstance(_item, _msg.child_class(param)):
                args[param] = _item
            else:
                raise ValueError(f"Wrong type for param {param}")

        # NameIDPolicy
        nameid_policy_format_config = self.config.getattr("name_id_policy_format", "sp")
        nameid_policy_format = nameid_format or nameid_policy_format_config or None

        allow_create_config = self.config.getattr("name_id_format_allow_create", "sp")
        allow_create = (
            None
            # SAML 2.0 errata says AllowCreate MUST NOT be used for transient ids
            if nameid_policy_format == NAMEID_FORMAT_TRANSIENT
            else allow_create
            if allow_create
            else str(bool(allow_create_config)).lower()
        )

        name_id_policy = (
            kwargs.pop("name_id_policy", None)
            if "name_id_policy" in kwargs
            else None
            if not nameid_policy_format
            else samlp.NameIDPolicy(allow_create=allow_create, format=nameid_policy_format)
        )

        if name_id_policy and vorg:
            name_id_policy.sp_name_qualifier = vorg
            name_id_policy.format = nameid_policy_format or NAMEID_FORMAT_PERSISTENT

        args["name_id_policy"] = name_id_policy

        # eIDAS SPType
        conf_sp_type = self.config.getattr("sp_type", "sp")
        conf_sp_type_in_md = self.config.getattr("sp_type_in_metadata", "sp")
        if conf_sp_type and conf_sp_type_in_md is False:
            if not extensions:
                extensions = Extensions()
            item = sp_type.SPType(text=conf_sp_type)
            extensions.add_extension_element(item)

        # eIDAS RequestedAttributes
        requested_attrs = requested_attributes or self.config.getattr("requested_attributes", "sp") or []
        if requested_attrs:
            req_attrs_node = create_requested_attribute_node(requested_attrs, self.config.attribute_converters)
            if not extensions:
                extensions = Extensions()
            extensions.add_extension_element(req_attrs_node)

        # ForceAuthn
        force_authn = str(kwargs.pop("force_authn", None) or self.config.getattr("force_authn", "sp")).lower() in [
            "true",
            "1",
        ]
        if force_authn:
            kwargs["force_authn"] = "true"

        if kwargs:
            _args, extensions = self._filter_args(AuthnRequest(), extensions, **kwargs)
            args.update(_args)
        args.pop("id", None)

        # client_crt = kwargs.get("client_crt")
        nsprefix = kwargs.get("nsprefix")

        msg = self._message(
            AuthnRequest,
            destination,
            message_id,
            consent,
            extensions,
            sign,
            sign_prepare,
            sign_alg=sign_alg,
            digest_alg=digest_alg,
            protocol_binding=binding,
            scoping=scoping,
            nsprefix=nsprefix,
            **args,
        )

        return msg

    # XXX DONE sp create > _message
    def create_attribute_query(
        self,
        destination,
        name_id=None,
        attribute=None,
        message_id=0,
        consent=None,
        extensions=None,
        sign=None,
        sign_prepare=None,
        sign_alg=None,
        digest_alg=None,
        **kwargs,
    ):
        """Constructs an AttributeQuery

        :param destination: To whom the query should be sent
        :param name_id: The identifier of the subject
        :param attribute: A dictionary of attributes and values that is
            asked for. The key are one of 4 variants:
            3-tuple of name_format,name and friendly_name,
            2-tuple of name_format and name,
            1-tuple with name or
            just the name as a string.
        :param sp_name_qualifier: The unique identifier of the
            service provider or affiliation of providers for whom the
            identifier was generated.
        :param name_qualifier: The unique identifier of the identity
            provider that generated the identifier.
        :param format: The format of the name ID
        :param message_id: The identifier of the session
        :param consent: Whether the principal have given her consent
        :param extensions: Possible extensions
        :param sign: Whether the query should be signed or not.
        :param sign_prepare: Whether the Signature element should be added.
        :return: Tuple of request ID and an AttributeQuery instance
        """

        if name_id is None:
            if "subject_id" in kwargs:
                name_id = saml.NameID(text=kwargs["subject_id"])
                for key in ["sp_name_qualifier", "name_qualifier", "format"]:
                    try:
                        setattr(name_id, key, kwargs[key])
                    except KeyError:
                        pass
            else:
                raise AttributeError("Missing required parameter")
        elif isinstance(name_id, str):
            name_id = saml.NameID(text=name_id)
            for key in ["sp_name_qualifier", "name_qualifier", "format"]:
                try:
                    setattr(name_id, key, kwargs[key])
                except KeyError:
                    pass

        subject = saml.Subject(name_id=name_id)

        if attribute:
            attribute = do_attributes(attribute)

        try:
            nsprefix = kwargs["nsprefix"]
        except KeyError:
            nsprefix = None

        return self._message(
            AttributeQuery,
            destination,
            message_id,
            consent,
            extensions,
            sign,
            sign_prepare,
            subject=subject,
            attribute=attribute,
            nsprefix=nsprefix,
            sign_alg=sign_alg,
            digest_alg=digest_alg,
        )

    # MUST use SOAP for
    # AssertionIDRequest, SubjectQuery,
    # AuthnQuery, AttributeQuery, or AuthzDecisionQuery
    # XXX DONE sp create > _message
    def create_authz_decision_query(
        self,
        destination,
        action,
        evidence=None,
        resource=None,
        subject=None,
        message_id=0,
        consent=None,
        extensions=None,
        sign=None,
        sign_alg=None,
        digest_alg=None,
        **kwargs,
    ):
        """Creates an authz decision query.

        :param destination: The IdP endpoint
        :param action: The action you want to perform (has to be at least one)
        :param evidence: Why you should be able to perform the action
        :param resource: The resource you want to perform the action on
        :param subject: Who wants to do the thing
        :param message_id: Message identifier
        :param consent: If the principal gave her consent to this request
        :param extensions: Possible request extensions
        :param sign: Whether the request should be signed or not.
        :return: AuthzDecisionQuery instance
        """

        return self._message(
            AuthzDecisionQuery,
            destination,
            message_id,
            consent,
            extensions,
            sign,
            action=action,
            evidence=evidence,
            resource=resource,
            subject=subject,
            sign_alg=sign_alg,
            digest_alg=digest_alg,
            **kwargs,
        )

    # XXX DONE sp create > self.create_authz_decision_query (FIXME pass sign/sign_alg/etc) > _message
    def create_authz_decision_query_using_assertion(
        self,
        destination,
        assertion,
        action=None,
        resource=None,
        subject=None,
        message_id=0,
        consent=None,
        extensions=None,
        sign=None,
        sign_alg=None,
        digest_alg=None,
        nsprefix=None,
    ):
        """Makes an authz decision query based on a previously received
        Assertion.

        :param destination: The IdP endpoint to send the request to
        :param assertion: An Assertion instance
        :param action: The action you want to perform (has to be at least one)
        :param resource: The resource you want to perform the action on
        :param subject: Who wants to do the thing
        :param message_id: Message identifier
        :param consent: If the principal gave her consent to this request
        :param extensions: Possible request extensions
        :param sign: Whether the request should be signed or not.
        :return: AuthzDecisionQuery instance
        """

        if action:
            if isinstance(action, str):
                _action = [saml.Action(text=action)]
            else:
                _action = [saml.Action(text=a) for a in action]
        else:
            _action = None

        return self.create_authz_decision_query(
            destination,
            _action,
            saml.Evidence(assertion=assertion),
            resource,
            subject,
            message_id=message_id,
            consent=consent,
            extensions=extensions,
            sign=sign,
            sign_alg=sign_alg,
            digest_alg=digest_alg,
            nsprefix=nsprefix,
        )

    @staticmethod
    def create_assertion_id_request(assertion_id_refs, **kwargs):
        """

        :param assertion_id_refs:
        :return: One ID ref
        """

        if isinstance(assertion_id_refs, str):
            return 0, assertion_id_refs
        else:
            return 0, assertion_id_refs[0]

    # XXX DONE sp create > _message
    def create_authn_query(
        self,
        subject,
        destination=None,
        authn_context=None,
        session_index="",
        message_id=0,
        consent=None,
        extensions=None,
        sign=None,
        nsprefix=None,
        sign_alg=None,
        digest_alg=None,
    ):
        """

        :param subject: The subject its all about as a <Subject> instance
        :param destination: The IdP endpoint to send the request to
        :param authn_context: list of <RequestedAuthnContext> instances
        :param session_index: a specified session index
        :param message_id: Message identifier
        :param consent: If the principal gave her consent to this request
        :param extensions: Possible request extensions
        :param sign: Whether the request should be signed or not.
        :return:
        """
        return self._message(
            AuthnQuery,
            destination,
            message_id,
            consent,
            extensions,
            sign,
            subject=subject,
            session_index=session_index,
            requested_authn_context=authn_context,
            nsprefix=nsprefix,
            sign_alg=sign_alg,
            digest_alg=digest_alg,
        )

    # XXX DONE sp create > _message
    def create_name_id_mapping_request(
        self,
        name_id_policy,
        name_id=None,
        base_id=None,
        encrypted_id=None,
        destination=None,
        message_id=0,
        consent=None,
        extensions=None,
        sign=None,
        nsprefix=None,
        sign_alg=None,
        digest_alg=None,
    ):
        """

        :param name_id_policy:
        :param name_id:
        :param base_id:
        :param encrypted_id:
        :param destination:
        :param message_id: Message identifier
        :param consent: If the principal gave her consent to this request
        :param extensions: Possible request extensions
        :param sign: Whether the request should be signed or not.
        :return:
        """

        if not name_id and not base_id and not encrypted_id:
            raise ValueError("At least one of name_id, base_id or encrypted_id must be present.")

        id_attr = {
            "name_id": name_id,
            "base_id": (base_id if not name_id else None),
            "encrypted_id": (encrypted_id if not name_id and not base_id else None),
        }

        return self._message(
            NameIDMappingRequest,
            destination,
            message_id,
            consent,
            extensions,
            sign,
            name_id_policy=name_id_policy,
            **id_attr,
            nsprefix=nsprefix,
            sign_alg=sign_alg,
            digest_alg=digest_alg,
        )

    # ======== response handling ===========

    def parse_authn_request_response(self, xmlstr, binding, outstanding=None, outstanding_certs=None, conv_info=None):
        """Deal with an AuthnResponse

        :param xmlstr: The reply as a xml string
        :param binding: Which binding that was used for the transport
        :param outstanding: A dictionary with session IDs as keys and
            the original web request from the user before redirection
            as values.
        :param outstanding_certs:
        :param conv_info: Information about the conversation.
        :return: An response.AuthnResponse or None
        """

        if not getattr(self.config, "entityid", None):
            raise SAMLError("Missing entity_id specification")

        if not xmlstr:
            return None

        kwargs = {
            "outstanding_queries": outstanding,
            "outstanding_certs": outstanding_certs,
            "allow_unsolicited": self.allow_unsolicited,
            "want_assertions_signed": self.want_assertions_signed,
            "want_assertions_or_response_signed": self.want_assertions_or_response_signed,
            "want_response_signed": self.want_response_signed,
            "return_addrs": self.service_urls(binding=binding),
            "entity_id": self.config.entityid,
            "attribute_converters": self.config.attribute_converters,
            "allow_unknown_attributes": self.config.allow_unknown_attributes,
            "conv_info": conv_info,
        }

        try:
            resp = self._parse_response(xmlstr, AuthnResponse, "assertion_consumer_service", binding, **kwargs)
        except StatusError as err:
            logger.error("SAML status error: %s", str(err))
            raise
        except UnravelError:
            return None
        except Exception as err:
            logger.error("XML parse error: %s", str(err))
            raise

        if not isinstance(resp, AuthnResponse):
            logger.error("Response type not supported: %s", saml2.class_name(resp))
            return None

        if resp.assertion and len(resp.response.encrypted_assertion) == 0 and resp.name_id:
            self.users.add_information_about_person(resp.session_info())
            logger.info("--- ADDED person info ----")

        return resp

    # ------------------------------------------------------------------------
    # SubjectQuery, AuthnQuery, RequestedAuthnContext, AttributeQuery,
    # AuthzDecisionQuery all get Response as response

    def parse_authz_decision_query_response(self, response, binding=BINDING_SOAP):
        """Verify that the response is OK"""
        kwargs = {
            "entity_id": self.config.entityid,
            "attribute_converters": self.config.attribute_converters,
        }

        return self._parse_response(response, AuthzResponse, "", binding, **kwargs)

    def parse_authn_query_response(self, response, binding=BINDING_SOAP):
        """Verify that the response is OK"""
        kwargs = {"entity_id": self.config.entityid, "attribute_converters": self.config.attribute_converters}

        return self._parse_response(response, AuthnQueryResponse, "", binding, **kwargs)

    def parse_assertion_id_request_response(self, response, binding):
        """Verify that the response is OK"""
        kwargs = {"entity_id": self.config.entityid, "attribute_converters": self.config.attribute_converters}

        res = self._parse_response(response, AssertionIDResponse, "", binding, **kwargs)
        return res

    # ------------------------------------------------------------------------

    def parse_attribute_query_response(self, response, binding):
        kwargs = {"entity_id": self.config.entityid, "attribute_converters": self.config.attribute_converters}

        return self._parse_response(response, AttributeResponse, "attribute_consuming_service", binding, **kwargs)

    def parse_name_id_mapping_request_response(self, txt, binding=BINDING_SOAP):
        """

        :param txt: SOAP enveloped SAML message
        :param binding: Just a placeholder, it's always BINDING_SOAP
        :return: parsed and verified <NameIDMappingResponse> instance
        """

        return self._parse_response(txt, NameIDMappingResponse, "", binding)

    # ------------------- ECP ------------------------------------------------

    # XXX DONE sp create > create_authn_request (FIXME DONE sign/sign_alg/etc) > _message
    def create_ecp_authn_request(
        self,
        entityid=None,
        relay_state="",
        sign=None,
        sign_alg=None,
        digest_alg=None,
        **kwargs,
    ):
        """Makes an authentication request.

        :param entityid: The entity ID of the IdP to send the request to
        :param relay_state: A token that can be used by the SP to know
            where to continue the conversation with the client
        :param sign: Whether the request should be signed or not.
        :return: SOAP message with the AuthnRequest
        """

        # ----------------------------------------
        # <paos:Request>
        # ----------------------------------------
        my_url = self.service_urls(BINDING_PAOS)[0]

        # must_understand and act according to the standard
        #
        paos_request = paos.Request(
            must_understand="1",
            actor=ACTOR,
            response_consumer_url=my_url,
            service=ECP_SERVICE,
        )

        # ----------------------------------------
        # <ecp:RelayState>
        # ----------------------------------------

        relay_state = ecp.RelayState(
            actor=ACTOR,
            must_understand="1",
            text=relay_state,
        )

        # ----------------------------------------
        # <samlp:AuthnRequest>
        # ----------------------------------------

        try:
            authn_req = kwargs["authn_req"]
            try:
                req_id = authn_req.id
            except AttributeError:
                req_id = 0  # Unknown but since it's SOAP it doesn't matter
        except KeyError:
            try:
                _binding = kwargs["binding"]
            except KeyError:
                _binding = BINDING_SOAP
                kwargs["binding"] = _binding

            logger.debug("entityid: %s, binding: %s", entityid, _binding)

            # The IDP publishes support for ECP by using the SOAP binding on
            # SingleSignOnService
            _, location = self.pick_binding("single_sign_on_service", [_binding], entity_id=entityid)
            req_id, authn_req = self.create_authn_request(
                location,
                service_url_binding=BINDING_PAOS,
                sign=sign,
                sign_alg=sign_alg,
                digest_alg=digest_alg,
                **kwargs,
            )

        # ----------------------------------------
        # The SOAP envelope
        # ----------------------------------------

        soap_envelope = make_soap_enveloped_saml_thingy(authn_req, [paos_request, relay_state])

        return req_id, str(soap_envelope)

    def parse_ecp_authn_response(self, txt, outstanding=None):
        rdict = soap.class_instances_from_soap_enveloped_saml_thingies(txt, [paos, ecp, samlp])

        _relay_state = None
        for item in rdict["header"]:
            if item.c_tag == "RelayState" and item.c_namespace == ecp.NAMESPACE:
                _relay_state = item

        response = self.parse_authn_request_response(rdict["body"], BINDING_PAOS, outstanding)

        return response, _relay_state

    @staticmethod
    def can_handle_ecp_response(response):
        try:
            accept = response.headers["accept"]
        except KeyError:
            try:
                accept = response.headers["Accept"]
            except KeyError:
                return False

        if MIME_PAOS in accept:
            return True
        else:
            return False

    # ----------------------------------------------------------------------
    # IDP discovery
    # ----------------------------------------------------------------------

    @staticmethod
    def create_discovery_service_request(url, entity_id, **kwargs):
        """
        Created the HTTP redirect URL needed to send the user to the
        discovery service.

        :param url: The URL of the discovery service
        :param entity_id: The unique identifier of the service provider
        :param return: The discovery service MUST redirect the user agent
            to this location in response to this request
        :param policy: A parameter name used to indicate the desired behavior
            controlling the processing of the discovery service
        :param returnIDParam: A parameter name used to return the unique
            identifier of the selected identity provider to the original
            requester.
        :param isPassive: A boolean value True/False that controls
            whether the discovery service is allowed to visibly interact with
            the user agent.
        :return: A URL
        """

        args = {
            "entityID": entity_id,
            "policy": kwargs.get("policy"),
            "returnIDParam": kwargs.get("returnIDParam"),
            "return": kwargs.get("return_url") or kwargs.get("return"),
            "isPassive": (None if "isPassive" not in kwargs.keys() else "true" if kwargs.get("isPassive") else "false"),
        }

        params = urlencode({k: v for k, v in args.items() if v})
        # url can already contain some parameters
        if "?" in url:
            return f"{url}&{params}"
        else:
            return f"{url}?{params}"

    @staticmethod
    def parse_discovery_service_response(url="", query="", returnIDParam="entityID"):
        """
        Deal with the response url from a Discovery Service

        :param url: the url the user was redirected back to or
        :param query: just the query part of the URL.
        :param returnIDParam: This is where the identifier of the IdP is
            place if it was specified in the query. Default is 'entityID'
        :return: The IdP identifier or "" if none was given
        """

        if url:
            part = urlparse(url)
            qsd = parse_qs(part[4])
        elif query:
            qsd = parse_qs(query)
        else:
            qsd = {}

        try:
            return qsd[returnIDParam][0]
        except KeyError:
            return ""
