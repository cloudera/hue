import base64
from binascii import hexlify
import copy
from hashlib import sha1
import logging
import zlib

import requests

from saml2 import BINDING_HTTP_ARTIFACT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_PAOS
from saml2 import BINDING_SOAP
from saml2 import BINDING_URI
from saml2 import VERSION
from saml2 import SamlBase
from saml2 import SAMLError
from saml2 import class_name
from saml2 import element_to_extension_element
from saml2 import extension_elements_to_elements
from saml2 import request as saml_request
from saml2 import response as saml_response
from saml2 import saml
from saml2 import samlp
from saml2 import soap
from saml2.config import config_factory
from saml2.httpbase import HTTPBase
from saml2.mdstore import all_locations
from saml2.metadata import ENDPOINTS
from saml2.pack import http_form_post_message
from saml2.pack import http_redirect_message
from saml2.profile import ecp
from saml2.profile import paos
from saml2.profile import samlec
from saml2.response import LogoutResponse
from saml2.response import UnsolicitedResponse
from saml2.s_utils import UnravelError
from saml2.s_utils import UnsupportedBinding
from saml2.s_utils import decode_base64_and_inflate
from saml2.s_utils import error_status_factory
from saml2.s_utils import rndbytes
from saml2.s_utils import sid
from saml2.s_utils import success_status_factory
from saml2.saml import NAMEID_FORMAT_ENTITY
from saml2.saml import EncryptedAssertion
from saml2.saml import Issuer
from saml2.saml import NameID
from saml2.samlp import Artifact
from saml2.samlp import ArtifactResolve
from saml2.samlp import ArtifactResponse
from saml2.samlp import AssertionIDRequest
from saml2.samlp import AttributeQuery
from saml2.samlp import AuthnQuery
from saml2.samlp import AuthnRequest
from saml2.samlp import AuthzDecisionQuery
from saml2.samlp import LogoutRequest
from saml2.samlp import ManageNameIDRequest
from saml2.samlp import NameIDMappingRequest
from saml2.samlp import SessionIndex
from saml2.samlp import artifact_resolve_from_string
from saml2.samlp import response_from_string
from saml2.sigver import SignatureError
from saml2.sigver import SigverError
from saml2.sigver import get_pem_wrapped_unwrapped
from saml2.sigver import make_temp
from saml2.sigver import pre_encrypt_assertion
from saml2.sigver import pre_encryption_part
from saml2.sigver import pre_signature_part
from saml2.sigver import security_context
from saml2.sigver import signed_instance_factory
from saml2.soap import class_instances_from_soap_enveloped_saml_thingies
from saml2.soap import open_soap_envelope
from saml2.soap import parse_soap_enveloped_saml_artifact_resolve
from saml2.time_util import instant
from saml2.virtual_org import VirtualOrg
from saml2.xmldsig import DIGEST_ALLOWED_ALG
from saml2.xmldsig import SIG_ALLOWED_ALG
from saml2.xmldsig import DefaultSignature


logger = logging.getLogger(__name__)

__author__ = "rolandh"

ARTIFACT_TYPECODE = b"\x00\x04"

SERVICE2MESSAGE = {
    "single_sign_on_service": AuthnRequest,
    "attribute_service": AttributeQuery,
    "authz_service": AuthzDecisionQuery,
    "assertion_id_request_service": AssertionIDRequest,
    "authn_query_service": AuthnQuery,
    "manage_name_id_service": ManageNameIDRequest,
    "name_id_mapping_service": NameIDMappingRequest,
    "artifact_resolve_service": ArtifactResolve,
    "single_logout_service": LogoutRequest,
}


class UnknownBinding(SAMLError):
    pass


def create_artifact(entity_id, message_handle, endpoint_index=0):
    """
    SAML_artifact   := B64(TypeCode EndpointIndex RemainingArtifact)
    TypeCode        := Byte1Byte2
    EndpointIndex   := Byte1Byte2

    RemainingArtifact := SourceID MessageHandle
    SourceID          := 20-byte_sequence
    MessageHandle     := 20-byte_sequence

    :param entity_id:
    :param message_handle:
    :param endpoint_index:
    :return:
    """
    if not isinstance(entity_id, bytes):
        entity_id = entity_id.encode("utf-8")
    sourceid = sha1(entity_id)

    if not isinstance(message_handle, bytes):
        message_handle = message_handle.encode("utf-8")
    ter = b"".join((ARTIFACT_TYPECODE, (f"{endpoint_index:02x}").encode("ascii"), sourceid.digest(), message_handle))
    return base64.b64encode(ter).decode("ascii")


class Entity(HTTPBase):
    def __init__(self, entity_type, config=None, config_file="", virtual_organization="", msg_cb=None):
        self.entity_type = entity_type
        self.users = None

        if config:
            self.config = config
        elif config_file:
            self.config = config_factory(entity_type, config_file)
        else:
            raise SAMLError("Missing configuration")

        def_sig = DefaultSignature()
        self.signing_algorithm = self.config.getattr("signing_algorithm") or def_sig.get_sign_alg()
        self.digest_algorithm = self.config.getattr("digest_algorithm") or def_sig.get_digest_alg()

        sign_config_per_entity_type = {
            "sp": self.config.getattr("authn_requests_signed", "sp"),
            "idp": self.config.getattr("sign_response", "idp"),
        }
        sign_config = sign_config_per_entity_type.get(self.entity_type, False)
        self.should_sign = sign_config

        for item in ["cert_file", "key_file", "ca_certs"]:
            _val = getattr(self.config, item, None)
            if not _val:
                continue

            if _val.startswith("http"):
                r = requests.request("GET", _val, timeout=self.config.http_client_timeout)
                if r.status_code == 200:
                    tmp = make_temp(r.text, ".pem", False, self.config.delete_tmpfiles)
                    setattr(self.config, item, tmp.name)
                else:
                    raise Exception(f"Could not fetch certificate from {_val}")

        HTTPBase.__init__(
            self,
            self.config.verify_ssl_cert,
            self.config.ca_certs,
            self.config.key_file,
            self.config.cert_file,
            self.config.http_client_timeout,
        )

        if self.config.vorg:
            for vo in self.config.vorg.values():
                vo.sp = self

        self.metadata = self.config.metadata
        self.debug = self.config.debug

        self.sec = security_context(self.config)

        if virtual_organization:
            if isinstance(virtual_organization, str):
                self.vorg = self.config.vorg[virtual_organization]
            elif isinstance(virtual_organization, VirtualOrg):
                self.vorg = virtual_organization
        else:
            self.vorg = None

        self.artifact = {}
        if self.metadata:
            self.sourceid = self.metadata.construct_source_id()
        else:
            self.sourceid = {}

        self.msg_cb = msg_cb

    def reload_metadata(self, metadata_conf):
        """
        Reload metadata configuration.

        Load a new metadata configuration as defined by metadata_conf (by
        passing this to Config.load_metadata) and make this entity (as well as
        subordinate objects with own metadata reference) use the new metadata.

        The structure of metadata_conf is the same as the 'metadata' entry in
        the configuration passed to saml2.Config.

        param metadata_conf: Metadata configuration as passed to Config.load_metadata
        return: True if successfully reloaded
        """
        logger.debug("Loading new metadata")
        try:
            self.metadata.reload(metadata_conf)
        except Exception as ex:
            logger.error(f"Loading metadata failed; reason: {str(ex)}")
            return False

        self.sourceid = self.metadata.construct_source_id()

        return True

    def _issuer(self, entityid=None):
        """Return an Issuer instance"""
        if entityid:
            if isinstance(entityid, Issuer):
                return entityid
            else:
                return Issuer(text=entityid, format=NAMEID_FORMAT_ENTITY)
        else:
            return Issuer(text=self.config.entityid, format=NAMEID_FORMAT_ENTITY)

    # XXX DONE will actually use sign_alg and digest_alg for the Redirect-Binding
    # XXX DONE deepest level - needs to decide the sign_alg (no digest_alg here)
    # XXX verify digest_alg is not needed
    # XXX deprecate sigalg for sign_alg
    def apply_binding(
        self,
        binding,
        msg_str,
        destination="",
        relay_state="",
        response=False,
        sign=None,
        sigalg=None,
        **kwargs,
    ):
        """
        Construct the necessary HTTP arguments dependent on Binding

        :param binding: Which binding to use
        :param msg_str: The return message as a string (XML) if the message is
            to be signed it MUST contain the signature element.
        :param destination: Where to send the message
        :param relay_state: Relay_state if provided
        :param response: Which type of message this is
        :param kwargs: response type specific arguments
        :return: A dictionary
        """

        # XXX SIG_ALLOWED_ALG should be configurable
        # XXX should_sign stems from authn_requests_signed and sign_response
        # XXX based on the type of the entity
        # XXX but should also take into account the type of message (Authn/Logout/etc)
        # XXX should_sign should be split and the exact config options should be checked
        sign = sign if sign is not None else self.should_sign
        sign_alg = sigalg or self.signing_algorithm
        if sign_alg not in [long_name for short_name, long_name in SIG_ALLOWED_ALG]:
            raise Exception(f"Signature algo not in allowed list: {sign_alg}")

        # unless if BINDING_HTTP_ARTIFACT
        if response:
            typ = "SAMLResponse"
        else:
            typ = "SAMLRequest"

        if binding == BINDING_HTTP_POST:
            logger.debug("HTTP POST")
            info = http_form_post_message(msg_str, destination, relay_state, typ)
            info["url"] = destination
            info["method"] = "POST"
        elif binding == BINDING_HTTP_REDIRECT:
            logger.debug("HTTP REDIRECT")
            info = http_redirect_message(
                message=msg_str,
                location=destination,
                relay_state=relay_state,
                typ=typ,
                sign=sign,
                sigalg=sign_alg,
                backend=self.sec.sec_backend,
            )
            info["url"] = str(destination)
            info["method"] = "GET"
        elif binding == BINDING_SOAP or binding == BINDING_PAOS:
            info = self.use_soap(msg_str, destination, sign=sign, sigalg=sign_alg, **kwargs)
        elif binding == BINDING_URI:
            info = self.use_http_uri(msg_str, typ, destination)
        elif binding == BINDING_HTTP_ARTIFACT:
            if response:
                info = self.use_http_artifact(msg_str, destination, relay_state)
                info["method"] = "GET"
                info["status"] = 302  # TODO: should be 303 on >= HTTP/1.1
            else:
                info = self.use_http_artifact(msg_str, destination, relay_state)
        else:
            raise SAMLError(f"Unknown binding type: {binding}")

        return info

    def pick_binding(self, service, bindings=None, descr_type="", request=None, entity_id=""):
        if request and not entity_id:
            entity_id = request.issuer.text.strip()

        sfunc = getattr(self.metadata, service)

        if not bindings:
            if request and request.protocol_binding:
                bindings = [request.protocol_binding]
            else:
                bindings = self.config.preferred_binding[service]

        if not descr_type:
            if self.entity_type == "sp":
                descr_type = "idpsso"
            else:
                descr_type = "spsso"

        _url = getattr(request, f"{service}_url", None)
        _index = getattr(request, f"{service}_index", None)

        for binding in bindings:
            try:
                srvs = sfunc(entity_id, binding, descr_type)
                if srvs:
                    if _url:
                        for srv in srvs:
                            if srv["location"] == _url:
                                return binding, _url
                    elif _index:
                        for srv in srvs:
                            if srv["index"] == _index:
                                return binding, srv["location"]
                    else:
                        destination = next(all_locations(srvs), None)
                        return binding, destination
            except UnsupportedBinding:
                pass

        logger.error("Failed to find consumer URL: %s, %s, %s", entity_id, bindings, descr_type)
        # logger.error("Bindings: %s", bindings)
        # logger.error("Entities: %s", self.metadata)

        raise SAMLError("Unknown entity or unsupported bindings")

    def message_args(self, message_id=0):
        if not message_id:
            message_id = sid()

        margs = {
            "id": message_id,
            "version": VERSION,
            "issue_instant": instant(),
            "issuer": self._issuer(),
        }
        return margs

    def response_args(self, message, bindings=None, descr_type=""):
        """

        :param message: The message to which a reply is constructed
        :param bindings: Which bindings can be used.
        :param descr_type: Type of descriptor (spssp, idpsso, )
        :return: Dictionary
        """
        info = {"in_response_to": message.id}

        if isinstance(message, AuthnRequest):
            rsrv = "assertion_consumer_service"
            descr_type = "spsso"
            info["sp_entity_id"] = message.issuer.text
            info["name_id_policy"] = message.name_id_policy
        elif isinstance(message, LogoutRequest):
            rsrv = "single_logout_service"
        elif isinstance(message, AttributeQuery):
            info["sp_entity_id"] = message.issuer.text
            rsrv = "attribute_consuming_service"
            descr_type = "spsso"
        elif isinstance(message, ManageNameIDRequest):
            rsrv = "manage_name_id_service"
        # The once below are solely SOAP so no return destination needed
        elif isinstance(message, AssertionIDRequest):
            rsrv = ""
        elif isinstance(message, ArtifactResolve):
            rsrv = ""
        elif isinstance(message, AssertionIDRequest):
            rsrv = ""
        elif isinstance(message, NameIDMappingRequest):
            rsrv = ""
        else:
            raise SAMLError("No support for this type of query")

        if bindings == [BINDING_SOAP]:
            info["binding"] = BINDING_SOAP
            info["destination"] = ""
            return info

        if rsrv:
            if not descr_type:
                if self.entity_type == "sp":
                    descr_type = "idpsso"
                else:
                    descr_type = "spsso"

            binding, destination = self.pick_binding(rsrv, bindings, descr_type=descr_type, request=message)
            info["binding"] = binding
            info["destination"] = destination

        return info

    @staticmethod
    def unravel(txt, binding, msgtype="response"):
        """
        Will unpack the received text. Depending on the context the original
         response may have been transformed before transmission.
        :param txt:
        :param binding:
        :param msgtype:
        :return:
        """
        # logger.debug("unravel '%s'", txt)
        if binding not in [
            BINDING_HTTP_REDIRECT,
            BINDING_HTTP_POST,
            BINDING_SOAP,
            BINDING_URI,
            BINDING_HTTP_ARTIFACT,
            None,
        ]:
            raise UnknownBinding(f"Don't know how to handle '{binding}'")

        try:
            if binding == BINDING_HTTP_REDIRECT:
                xmlstr = decode_base64_and_inflate(txt)
            elif binding == BINDING_HTTP_POST:
                try:
                    xmlstr = decode_base64_and_inflate(txt)
                except zlib.error:
                    xmlstr = base64.b64decode(txt)
            elif binding == BINDING_SOAP:
                func = getattr(soap, f"parse_soap_enveloped_saml_{msgtype}")
                xmlstr = func(txt)
            elif binding == BINDING_HTTP_ARTIFACT:
                xmlstr = base64.b64decode(txt)
            else:
                xmlstr = txt
        except Exception:
            raise UnravelError(f"Unravelling binding '{binding}' failed")

        return xmlstr

    @staticmethod
    def parse_soap_message(text):
        """

        :param text: The SOAP message
        :return: A dictionary with two keys "body" and "header"
        """
        return class_instances_from_soap_enveloped_saml_thingies(text, [paos, ecp, samlp, samlec])

    @staticmethod
    def unpack_soap_message(text):
        """
        Picks out the parts of the SOAP message, body and headers apart
        :param text: The SOAP message
        :return: A dictionary with two keys "body"/"header"
        """
        return open_soap_envelope(text)

    # --------------------------------------------------------------------------

    # XXX DONE will actually use sign_alg and digest_alg for the POST-Binding
    # XXX DONE deepest level - needs to decide the sign_alg and digest_alg value
    # XXX a controler for signed_instance_factory
    # XXX syncs pre_signature_part and signed_instance_factory
    # XXX makes sure pre_signature_part is called before signed_instance_factory
    # XXX calls pre_signature_part - must have sign_alg & digest_alg
    # XXX calls signed_instance_factory - after pre_signature_part
    # XXX !!expects a msg object!!
    def sign(
        self,
        msg,
        mid=None,
        to_sign=None,
        sign_prepare=None,
        sign_alg=None,
        digest_alg=None,
    ):
        # XXX sig/digest-allowed should be configurable
        sign_alg = sign_alg or self.signing_algorithm
        digest_alg = digest_alg or self.digest_algorithm
        if sign_alg not in [long_name for short_name, long_name in SIG_ALLOWED_ALG]:
            raise Exception(f"Signature algo not in allowed list: {sign_alg}")
        if digest_alg not in [long_name for short_name, long_name in DIGEST_ALLOWED_ALG]:
            raise Exception(f"Digest algo not in allowed list: {digest_alg}")

        if msg.signature is None:
            msg.signature = pre_signature_part(msg.id, self.sec.my_cert, 1, sign_alg=sign_alg, digest_alg=digest_alg)

        if sign_prepare:
            return msg

        if mid is None:
            mid = msg.id

        try:
            to_sign += [(class_name(msg), mid)]
        except (AttributeError, TypeError):
            to_sign = [(class_name(msg), mid)]

        logger.debug("REQUEST: %s", msg)
        return signed_instance_factory(msg, self.sec, to_sign)

    # XXX DONE will actually use sign the POST-Binding
    # XXX DONE deepest level - needs to decide the sign value
    # XXX DONE calls self.sign must figure out sign
    # XXX DONE ensure both SPs and IdPs go through this
    # XXX DONE ensure this works for the POST-Binding
    def _message(
        self,
        request_cls,
        destination=None,
        message_id=0,
        consent=None,
        extensions=None,
        sign=None,
        sign_prepare=None,
        nsprefix=None,
        sign_alg=None,
        digest_alg=None,
        **kwargs,
    ):
        """
        Some parameters appear in all requests so simplify by doing
        it in one place

        :param request_cls: The specific request type
        :param destination: The recipient
        :param message_id: A message identifier
        :param consent: Whether the principal have given her consent
        :param extensions: Possible extensions
        :param sign: Whether the request should be signed or not.
        :param sign_prepare: Whether the signature should be prepared or not.
        :param kwargs: Key word arguments specific to one request type
        :return: A tuple containing the request ID and an instance of the
            request_cls
        """
        if not message_id:
            message_id = sid()

        for key, val in self.message_args(message_id).items():
            if key not in kwargs:
                kwargs[key] = val

        req = request_cls(**kwargs)

        if destination:
            req.destination = destination

        if consent:
            req.consent = "true"

        if extensions:
            req.extensions = extensions

        if nsprefix:
            req.register_prefix(nsprefix)

        if self.msg_cb:
            req = self.msg_cb(req)

        reqid = req.id

        sign = sign if sign is not None else self.should_sign
        if sign:
            signed_req = self.sign(
                req,
                sign_prepare=sign_prepare,
                sign_alg=sign_alg,
                digest_alg=digest_alg,
            )
            req = signed_req

        logger.debug("REQUEST: %s", req)
        return reqid, req

    @staticmethod
    def _filter_args(instance, extensions=None, **kwargs):
        args = {}
        if extensions is None:
            extensions = []

        allowed_attributes = instance.keys()
        for key, val in kwargs.items():
            if key in allowed_attributes:
                args[key] = val
            elif isinstance(val, SamlBase):
                # extension elements allowed ?
                extensions.append(element_to_extension_element(val))

        return args, extensions

    def _add_info(self, msg, **kwargs):
        """
        Add information to a SAML message. If the attribute is not part of
        what's defined in the SAML standard add it as an extension.

        :param msg:
        :param kwargs:
        :return:
        """

        args, extensions = self._filter_args(msg, **kwargs)
        for key, val in args.items():
            setattr(msg, key, val)

        if extensions:
            if msg.extension_elements:
                msg.extension_elements.extend(extensions)
            else:
                msg.extension_elements = extensions

    def has_encrypt_cert_in_metadata(self, sp_entity_id):
        """Verifies if the metadata contains encryption certificates.

        :param sp_entity_id: Entity ID for the calling service provider.
        :return: True if encrypt cert exists in metadata, otherwise False.
        """
        if sp_entity_id is not None:
            _certs = self.metadata.certs(sp_entity_id, "any", "encryption")
            if len(_certs) > 0:
                return True
        return False

    def _encrypt_assertion(self, encrypt_cert, sp_entity_id, response, node_xpath=None):
        """Encryption of assertions.

        :param encrypt_cert: Certificate to be used for encryption.
        :param sp_entity_id: Entity ID for the calling service provider.
        :param response: A samlp.Response
        :param node_xpath: Unquie path to the element to be encrypted.
        :return: A new samlp.Resonse with the designated assertion encrypted.
        """
        _certs = []

        if encrypt_cert:
            _certs.append((None, encrypt_cert))
        elif sp_entity_id is not None:
            _certs = self.metadata.certs(sp_entity_id, "any", "encryption")
        exception = None
        for _cert_name, _cert in _certs:
            wrapped_cert, unwrapped_cert = get_pem_wrapped_unwrapped(_cert)
            try:
                tmp = make_temp(
                    wrapped_cert.encode("ascii"),
                    decode=False,
                    delete_tmpfiles=self.config.delete_tmpfiles,
                )
                response = self.sec.encrypt_assertion(
                    response,
                    tmp.name,
                    pre_encryption_part(key_name=_cert_name, encrypt_cert=unwrapped_cert),
                    node_xpath=node_xpath,
                )
                return response
            except Exception as ex:
                exception = ex
        if exception:
            raise exception
        return response

    # XXX DONE calls self.sign must figure out sign
    # XXX calls signed_instance_factory - must have called pre_signature_part
    # XXX calls pre_signature_part - must figure out sign_alg/digest_alg
    def _response(
        self,
        in_response_to,
        consumer_url=None,
        status=None,
        issuer=None,
        sign=None,
        to_sign=None,
        sp_entity_id=None,
        encrypt_assertion=False,
        encrypt_assertion_self_contained=False,
        encrypted_advice_attributes=False,
        encrypt_cert_advice=None,
        encrypt_cert_assertion=None,
        sign_assertion=None,
        pefim=False,
        sign_alg=None,
        digest_alg=None,
        **kwargs,
    ):
        """Create a Response.
            Encryption:
                encrypt_assertion must be true for encryption to be
                performed. If encrypted_advice_attributes also is
                true, then will the function try to encrypt the assertion in
                the the advice element of the main
                assertion. Only one assertion element is allowed in the
                advice element, if multiple assertions exists
                in the advice element the main assertion will be encrypted
                instead, since it's no point to encrypt
                If encrypted_advice_attributes is
                false the main assertion will be encrypted. Since the same key

        :param in_response_to: The session identifier of the request
        :param consumer_url: The URL which should receive the response
        :param status: An instance of samlp.Status
        :param issuer: The issuer of the response
        :param sign: Whether the response should be signed or not
        :param to_sign: If there are other parts to sign
        :param sp_entity_id: Entity ID for the calling service provider.
        :param encrypt_assertion: True if assertions should be encrypted.
        :param encrypt_assertion_self_contained: True if all encrypted
        assertions should have alla namespaces selfcontained.
        :param encrypted_advice_attributes: True if assertions in the advice
        element should be encrypted.
        :param encrypt_cert_advice: Certificate to be used for encryption of
        assertions in the advice element.
        :param encrypt_cert_assertion: Certificate to be used for encryption
        of assertions.
        :param sign_assertion: True if assertions should be signed.
        :param pefim: True if a response according to the PEFIM profile
        should be created.
        :param kwargs: Extra key word arguments
        :return: A Response instance
        """

        if not status:
            status = success_status_factory()

        _issuer = self._issuer(issuer)

        response = samlp.Response(id=sid(), version=VERSION, issue_instant=instant())
        response.issuer = _issuer
        response.in_response_to = in_response_to
        response.status = status

        if consumer_url:
            response.destination = consumer_url

        self._add_info(response, **kwargs)

        sign = sign if sign is not None else self.should_sign
        if to_sign and not sign and not encrypt_assertion:
            return signed_instance_factory(response, self.sec, to_sign)

        has_encrypt_cert = self.has_encrypt_cert_in_metadata(sp_entity_id)
        if not has_encrypt_cert and encrypt_cert_advice is None:
            encrypted_advice_attributes = False
        if not has_encrypt_cert and encrypt_cert_assertion is None:
            encrypt_assertion = False

        # XXX if encrypt_assertion or encrypted_advice_attributes
        # XXX once in, response becomes a str and uses signed_instance_factory
        if (
            # XXX goto part-C
            encrypt_assertion
            or (
                # XXX goto part-B
                encrypted_advice_attributes
                and response.assertion.advice is not None
                and len(response.assertion.advice.assertion) == 1
            )
        ):
            # XXX sig/digest-allowed should be configurable
            sign_alg = sign_alg or self.signing_algorithm
            digest_alg = digest_alg or self.digest_algorithm

            # XXX part-A (common) prepare sign response
            if sign:
                response.signature = pre_signature_part(
                    response.id,
                    self.sec.my_cert,
                    1,
                    sign_alg=sign_alg,
                    digest_alg=digest_alg,
                )
                sign_class = [(class_name(response), response.id)]
            else:
                sign_class = []

            # XXX part-B if encrypted_advice_attributes
            if (
                encrypted_advice_attributes
                and response.assertion.advice is not None
                and len(response.assertion.advice.assertion) > 0
            ):
                _assertions = response.assertion
                if not isinstance(_assertions, list):
                    _assertions = [_assertions]

                for _assertion in _assertions:
                    _assertion.advice.encrypted_assertion = []
                    _assertion.advice.encrypted_assertion.append(EncryptedAssertion())
                    _advice_assertions = copy.deepcopy(_assertion.advice.assertion)
                    _assertion.advice.assertion = []

                    if not isinstance(_advice_assertions, list):
                        _advice_assertions = [_advice_assertions]

                    for tmp_assertion in _advice_assertions:
                        to_sign_advice = []
                        # XXX prepare sign assertion
                        if sign_assertion and not pefim:
                            tmp_assertion.signature = pre_signature_part(
                                tmp_assertion.id,
                                self.sec.my_cert,
                                1,
                                sign_alg=sign_alg,
                                digest_alg=digest_alg,
                            )
                            to_sign_advice.append(
                                (class_name(tmp_assertion), tmp_assertion.id),
                            )

                        # XXX prepare encrypt assertion
                        # tmp_assertion = response.assertion.advice.assertion[0]
                        _assertion.advice.encrypted_assertion[0].add_extension_element(tmp_assertion)
                        if encrypt_assertion_self_contained:
                            advice_tag = response.assertion.advice._to_element_tree().tag
                            assertion_tag = tmp_assertion._to_element_tree().tag
                            response = (
                                response.get_xml_string_with_self_contained_assertion_within_advice_encrypted_assertion(
                                    assertion_tag, advice_tag
                                )
                            )
                        node_xpath = "".join(
                            [
                                f'/*[local-name()="{v}"]'
                                for v in ["Response", "Assertion", "Advice", "EncryptedAssertion", "Assertion"]
                            ]
                        )

                        # XXX sign assertion
                        if to_sign_advice:
                            response = signed_instance_factory(response, self.sec, to_sign_advice)

                        # XXX encrypt assertion
                        response = self._encrypt_assertion(
                            encrypt_cert_advice,
                            sp_entity_id,
                            response,
                            node_xpath=node_xpath,
                        )
                        response = response_from_string(response)

            # XXX part-C if encrypt_assertion
            if encrypt_assertion:
                to_sign_assertion = []

                # XXX prepare sign assertion
                if sign_assertion:
                    _assertions = response.assertion

                    if not isinstance(_assertions, list):
                        _assertions = [_assertions]

                    for _assertion in _assertions:
                        _assertion.signature = pre_signature_part(
                            _assertion.id,
                            self.sec.my_cert,
                            2,
                            sign_alg=sign_alg,
                            digest_alg=digest_alg,
                        )
                        to_sign_assertion.append(
                            (class_name(_assertion), _assertion.id),
                        )

                # XXX prepare encrypt assertion
                if encrypt_assertion_self_contained:
                    try:
                        assertion_tag = response.assertion._to_element_tree().tag
                    except Exception:
                        assertion_tag = response.assertion[0]._to_element_tree().tag
                    response = pre_encrypt_assertion(response)
                    response = response.get_xml_string_with_self_contained_assertion_within_encrypted_assertion(
                        assertion_tag
                    )
                else:
                    response = pre_encrypt_assertion(response)

                # XXX sign assertion
                if to_sign_assertion:
                    response = signed_instance_factory(response, self.sec, to_sign_assertion)

                # XXX encrypt assertion
                response = self._encrypt_assertion(encrypt_cert_assertion, sp_entity_id, response)
            else:
                # XXX sign other parts! (defiend by to_sign)
                if to_sign:
                    response = signed_instance_factory(response, self.sec, to_sign)

            # XXX part-D (common) sign response
            # XXX handle response having been signed/encrypted => str
            if sign:
                return signed_instance_factory(response, self.sec, sign_class)
            else:
                return response

        # XXX sign response
        if sign:
            return self.sign(response, to_sign=to_sign, sign_alg=sign_alg, digest_alg=digest_alg)

        return response

    # XXX DONE calls self.sign must figure out sign
    def _status_response(
        self,
        response_class,
        issuer,
        status,
        sign=None,
        sign_alg=None,
        digest_alg=None,
        **kwargs,
    ):
        """Create a StatusResponse.

        :param response_class: Which subclass of StatusResponse that should be
            used
        :param issuer: The issuer of the response message
        :param status: The return status of the response operation
        :param sign: Whether the response should be signed or not
        :param kwargs: Extra arguments to the response class
        :return: Class instance or string representation of the instance
        """

        mid = sid()

        for key in ["binding"]:
            kwargs.pop(key, None)

        if not status:
            status = success_status_factory()

        response = response_class(
            issuer=issuer,
            id=mid,
            version=VERSION,
            issue_instant=instant(),
            status=status,
            **kwargs,
        )

        sign = sign if sign is not None else self.should_sign
        if sign:
            return self.sign(response, mid, sign_alg=sign_alg, digest_alg=digest_alg)
        else:
            return response

    # ------------------------------------------------------------------------

    @staticmethod
    def srv2typ(service):
        for typ in ["aa", "pdp", "aq"]:
            if service in ENDPOINTS[typ]:
                if typ == "aa":
                    return "attribute_authority"
                elif typ == "aq":
                    return "authn_authority"
                else:
                    return typ

    def _parse_request(
        self,
        enc_request,
        request_cls,
        service,
        binding,
        relay_state=None,
        sigalg=None,
        signature=None,
    ):
        """Parse a Request

        :param enc_request: The request in its transport format
        :param request_cls: The type of requests I expect
        :param service:
        :param binding: Which binding that was used to transport the message
            to this entity.
        :return: A request instance
        """

        # _log_info = logger.info
        _log_debug = logger.debug

        # The addresses I should receive messages like this on
        receiver_addresses = self.config.endpoint(service, binding, self.entity_type)
        if not receiver_addresses and self.entity_type == "idp":
            for typ in ["aa", "aq", "pdp"]:
                receiver_addresses = self.config.endpoint(service, binding, typ)
                if receiver_addresses:
                    break

        _log_debug("receiver addresses: %s", receiver_addresses)
        _log_debug("Binding: %s", binding)

        try:
            timeslack = self.config.accepted_time_diff
            if not timeslack:
                timeslack = 0
        except AttributeError:
            timeslack = 0

        _request = request_cls(self.sec, receiver_addresses, self.config.attribute_converters, timeslack=timeslack)

        xmlstr = self.unravel(enc_request, binding, request_cls.msgtype)
        must = self.config.getattr("want_authn_requests_signed", "idp")
        only_valid_cert = self.config.getattr("want_authn_requests_only_with_valid_cert", "idp")
        if only_valid_cert is None:
            only_valid_cert = False
        if only_valid_cert:
            must = True
        _request = _request.loads(
            xmlstr,
            binding,
            origdoc=enc_request,
            must=must,
            only_valid_cert=only_valid_cert,
            relay_state=relay_state,
            sigalg=sigalg,
            signature=signature,
        )

        _log_debug("Loaded request")

        if _request:
            _request.verify()
            _log_debug("Verified request")

        if not _request:
            return None
        else:
            return _request

    # ------------------------------------------------------------------------

    # XXX DONE ent create > _response
    def create_error_response(
        self,
        in_response_to,
        destination,
        info,
        sign=None,
        issuer=None,
        sign_alg=None,
        digest_alg=None,
        **kwargs,
    ):
        """Create a error response.

        :param in_response_to: The identifier of the message this is a response
            to.
        :param destination: The intended recipient of this message
        :param info: Either an Exception instance or a 2-tuple consisting of
            error code and descriptive text
        :param sign: Whether the response should be signed or not
        :param issuer: The issuer of the response
        :param kwargs: To capture key,value pairs I don't care about
        :return: A response instance
        """
        status = error_status_factory(info)

        return self._response(
            in_response_to,
            destination,
            status,
            issuer,
            sign,
            sign_alg=sign_alg,
            digest_alg=digest_alg,
        )

    # ------------------------------------------------------------------------

    # XXX DONE ent create > _message
    def create_logout_request(
        self,
        destination,
        issuer_entity_id,
        subject_id=None,
        name_id=None,
        reason=None,
        expire=None,
        message_id=0,
        consent=None,
        extensions=None,
        sign=None,
        session_indexes=None,
        sign_alg=None,
        digest_alg=None,
    ):
        """Constructs a LogoutRequest

        :param destination: Destination of the request
        :param issuer_entity_id: The entity ID of the IdP the request is
            target at.
        :param subject_id: The identifier of the subject
        :param name_id: A NameID instance identifying the subject
        :param reason: An indication of the reason for the logout, in the
            form of a URI reference.
        :param expire: The time at which the request expires,
            after which the recipient may discard the message.
        :param message_id: Request identifier
        :param consent: Whether the principal have given her consent
        :param extensions: Possible extensions
        :param sign: Whether the query should be signed or not.
        :param session_indexes: SessionIndex instances or just values
        :return: A LogoutRequest instance
        """

        if subject_id:
            if self.entity_type == "idp":
                name_id = NameID(text=self.users.get_entityid(subject_id, issuer_entity_id, False))
            else:
                name_id = NameID(text=subject_id)

        if not name_id:
            raise SAMLError("Missing subject identification")

        args = {}
        if session_indexes:
            sis = []
            for si in session_indexes:
                if isinstance(si, SessionIndex):
                    sis.append(si)
                else:
                    sis.append(SessionIndex(text=si))
            args["session_index"] = sis

        return self._message(
            LogoutRequest,
            destination,
            message_id,
            consent,
            extensions,
            sign,
            name_id=name_id,
            reason=reason,
            not_on_or_after=expire,
            issuer=self._issuer(),
            sign_alg=sign_alg,
            digest_alg=digest_alg,
            **args,
        )

    # XXX DONE ent create > _status_response
    def create_logout_response(
        self,
        request,
        bindings=None,
        status=None,
        sign=None,
        issuer=None,
        sign_alg=None,
        digest_alg=None,
    ):
        """Create a LogoutResponse.

        :param request: The request this is a response to
        :param bindings: Which bindings that can be used for the response
            If None the preferred bindings are gathered from the configuration
        :param status: The return status of the response operation
            If None the operation is regarded as a Success.
        :param issuer: The issuer of the message
        :return: HTTP args
        """

        rinfo = self.response_args(request, bindings)

        if not issuer:
            issuer = self._issuer()

        response = self._status_response(
            samlp.LogoutResponse,
            issuer,
            status,
            sign,
            sign_alg=sign_alg,
            digest_alg=digest_alg,
            **rinfo,
        )

        logger.debug("Response: %s", response)

        return response

    # XXX DONE ent create > _message
    def create_artifact_resolve(
        self,
        artifact,
        destination,
        sessid,
        consent=None,
        extensions=None,
        sign=None,
        sign_alg=None,
        digest_alg=None,
    ):
        """
        Create a ArtifactResolve request

        :param artifact:
        :param destination:
        :param sessid: session id
        :param consent:
        :param extensions:
        :param sign:
        :return: The request message
        """

        artifact = Artifact(text=artifact)

        return self._message(
            ArtifactResolve,
            destination,
            sessid,
            consent,
            extensions,
            sign,
            artifact=artifact,
            sign_alg=sign_alg,
            digest_alg=digest_alg,
        )

    # XXX DONE ent create > _status_response
    def create_artifact_response(
        self,
        request,
        artifact,
        bindings=None,
        status=None,
        sign=None,
        issuer=None,
        sign_alg=None,
        digest_alg=None,
    ):
        """
        Create an ArtifactResponse
        :return:
        """

        rinfo = self.response_args(request, bindings)
        response = self._status_response(
            ArtifactResponse,
            issuer,
            status,
            sign=sign,
            sign_alg=sign_alg,
            digest_alg=digest_alg,
            **rinfo,
        )

        msg = element_to_extension_element(self.artifact[artifact])
        response.extension_elements = [msg]

        logger.debug("Response: %s", response)

        return response

    # XXX DONE ent create > _message
    def create_manage_name_id_request(
        self,
        destination,
        message_id=0,
        consent=None,
        extensions=None,
        sign=None,
        name_id=None,
        new_id=None,
        encrypted_id=None,
        new_encrypted_id=None,
        terminate=None,
        sign_alg=None,
        digest_alg=None,
    ):
        """

        :param destination:
        :param message_id:
        :param consent:
        :param extensions:
        :param sign:
        :param name_id:
        :param new_id:
        :param encrypted_id:
        :param new_encrypted_id:
        :param terminate:
        :return:
        """
        kwargs = self.message_args(message_id)

        if name_id:
            kwargs["name_id"] = name_id
        elif encrypted_id:
            kwargs["encrypted_id"] = encrypted_id
        else:
            raise AttributeError("One of NameID or EncryptedNameID has to be provided")

        if new_id:
            kwargs["new_id"] = new_id
        elif new_encrypted_id:
            kwargs["new_encrypted_id"] = new_encrypted_id
        elif terminate:
            kwargs["terminate"] = terminate
        else:
            raise AttributeError("One of NewID, NewEncryptedNameID or Terminate has to be " "provided")

        return self._message(
            ManageNameIDRequest,
            destination,
            consent=consent,
            extensions=extensions,
            sign=sign,
            sign_alg=sign_alg,
            digest_alg=digest_alg,
            **kwargs,
        )

    def parse_manage_name_id_request(self, xmlstr, binding=BINDING_SOAP):
        """Deal with a LogoutRequest

        :param xmlstr: The response as a xml string
        :param binding: What type of binding this message came through.
        :return: None if the reply doesn't contain a valid SAML LogoutResponse,
            otherwise the reponse if the logout was successful and None if it
            was not.
        """

        return self._parse_request(xmlstr, saml_request.ManageNameIDRequest, "manage_name_id_service", binding)

    # XXX DONE ent create > _status_response
    def create_manage_name_id_response(
        self,
        request,
        bindings=None,
        status=None,
        sign=None,
        issuer=None,
        sign_alg=None,
        digest_alg=None,
        **kwargs,
    ):

        rinfo = self.response_args(request, bindings)

        response = self._status_response(
            samlp.ManageNameIDResponse,
            issuer,
            status,
            sign,
            sign_alg=sign_alg,
            digest_alg=digest_alg,
            **rinfo,
        )

        logger.debug("Response: %s", response)

        return response

    def parse_manage_name_id_request_response(self, string, binding=BINDING_SOAP):
        return self._parse_response(
            string,
            saml_response.ManageNameIDResponse,
            "manage_name_id_service",
            binding,
            asynchop=False,
        )

    # ------------------------------------------------------------------------

    def _parse_response(
        self,
        xmlstr,
        response_cls,
        service,
        binding,
        outstanding_certs=None,
        **kwargs,
    ):
        """Deal with a Response

        :param xmlstr: The response as a xml string
        :param response_cls: What type of response it is
        :param binding: What type of binding this message came through.
        :param outstanding_certs: Certificates that belongs to me that the
                IdP may have used to encrypt a response/assertion/..
        :param kwargs: Extra key word arguments
        :return: None if the reply doesn't contain a valid SAML Response,
            otherwise the response.
        """

        if self.config.accepted_time_diff:
            kwargs["timeslack"] = self.config.accepted_time_diff

        if "asynchop" not in kwargs:
            if binding in [BINDING_SOAP, BINDING_PAOS]:
                kwargs["asynchop"] = False
            else:
                kwargs["asynchop"] = True

        response = None
        if not xmlstr:
            return response

        if "return_addrs" not in kwargs:
            bindings = {
                BINDING_SOAP,
                BINDING_HTTP_REDIRECT,
                BINDING_HTTP_POST,
            }
            if binding in bindings:
                # expected return address
                kwargs["return_addrs"] = self.config.endpoint(service, binding=binding, context=self.entity_type)

        try:
            response = response_cls(self.sec, **kwargs)
        except Exception as exc:
            logger.error(str(exc))
            raise

        xmlstr = self.unravel(xmlstr, binding, response_cls.msgtype)
        if not xmlstr:  # Not a valid reponse
            return None

        try:
            response_is_signed = False
            # Record the response signature requirement.
            require_response_signature = response.require_response_signature
            # Force the requirement that the response be signed in order to
            # force signature checking to happen so that we can know whether
            # or not the response is signed. The attribute on the response class
            # is reset to the recorded value in the finally clause below.
            response.require_response_signature = True
            response = response.loads(xmlstr, False, origxml=xmlstr)
        except SigverError as err:
            if require_response_signature:
                logger.error("Signature Error: %s", str(err))
                raise
            else:
                # The response is not signed but a signature is not required
                # so reset the attribute on the response class to the recorded
                # value and attempt to consume the unpacked XML again.
                response.require_response_signature = require_response_signature
                response = response.loads(xmlstr, False, origxml=xmlstr)
        except UnsolicitedResponse:
            logger.error("Unsolicited response")
            raise
        except Exception as err:
            if "not well-formed" in f"{err}":
                logger.error("Not well-formed XML")
            raise
        else:
            response_is_signed = True
        finally:
            response.require_response_signature = require_response_signature

        logger.debug("XMLSTR: %s", xmlstr)

        if not response:
            return response

        keys = None
        if outstanding_certs:
            try:
                cert = outstanding_certs[response.in_response_to]
            except KeyError:
                keys = None
            else:
                if not isinstance(cert, list):
                    cert = [cert]
                keys = []
                for _cert in cert:
                    keys.append(_cert["key"])

        try:
            assertions_are_signed = False
            # Record the assertions signature requirement.
            require_signature = response.require_signature
            # Force the requirement that the assertions be signed in order to
            # force signature checking to happen so that we can know whether
            # or not the assertions are signed. The attribute on the response class
            # is reset to the recorded value in the finally clause below.
            response.require_signature = True
            # Verify that the assertion is syntactically correct and the
            # signature on the assertion is correct if present.
            response.verify(keys)
        except SignatureError as err:
            if require_signature:
                logger.error("Signature Error: %s", str(err))
                raise
            else:
                response.require_signature = require_signature
                response.verify(keys)
        else:
            assertions_are_signed = True
        finally:
            response.require_signature = require_signature

        # If so configured enforce that either the response is signed
        # or the assertions within it are signed.
        if response.require_signature_or_response_signature:
            if not response_is_signed and not assertions_are_signed:
                msg = "Neither the response nor the assertions are signed"
                logger.error(msg)
                raise SigverError(msg)

        return response

    # ------------------------------------------------------------------------

    def parse_logout_request_response(self, xmlstr, binding=BINDING_SOAP):
        return self._parse_response(xmlstr, LogoutResponse, "single_logout_service", binding)

    # ------------------------------------------------------------------------

    def parse_logout_request(
        self,
        xmlstr,
        binding=BINDING_SOAP,
        relay_state=None,
        sigalg=None,
        signature=None,
    ):
        """Deal with a LogoutRequest

        :param xmlstr: The response as a xml string
        :param binding: What type of binding this message came through.
        :return: None if the reply doesn't contain a valid SAML LogoutResponse,
            otherwise the reponse if the logout was successful and None if it
            was not.
        """

        return self._parse_request(
            enc_request=xmlstr,
            request_cls=saml_request.LogoutRequest,
            service="single_logout_service",
            binding=binding,
            relay_state=relay_state,
            sigalg=sigalg,
            signature=signature,
        )

    def use_artifact(self, message, endpoint_index=0):
        """

        :param message:
        :param endpoint_index:
        :return:
        """
        message_handle = sha1(str(message).encode("utf-8"))
        message_handle.update(rndbytes())
        mhd = message_handle.digest()
        saml_art = create_artifact(self.config.entityid, mhd, endpoint_index)
        self.artifact[saml_art] = message
        return saml_art

    def artifact2destination(self, artifact, descriptor):
        """
        Translate an artifact into a receiver location

        :param artifact: The Base64 encoded SAML artifact
        :return:
        """

        _art = base64.b64decode(artifact)

        typecode = _art[:2]
        if typecode != ARTIFACT_TYPECODE:
            raise ValueError(f"Invalid artifact typecode {repr(typecode)} should be {repr(ARTIFACT_TYPECODE)}")

        try:
            endpoint_index = str(int(_art[2:4]))
        except ValueError:
            endpoint_index = str(int(hexlify(_art[2:4])))
        entity = self.sourceid[_art[4:24]]

        destination = None
        for desc in entity[f"{descriptor}_descriptor"]:
            for srv in desc["artifact_resolution_service"]:
                if srv["index"] == endpoint_index:
                    destination = srv["location"]
                    break

        return destination

    # XXX DONE uses sign but not a create_*
    def artifact2message(
        self,
        artifact,
        descriptor,
        sign=None,
        sign_alg=None,
        digest_alg=None,
    ):
        """

        :param artifact: The Base64 encoded SAML artifact as sent over the net
        :param descriptor: The type of entity on the other side
        :param sign: Whether ArtifactResolve should be signed or not
        :return: A SAML message (request/response)
        """

        destination = self.artifact2destination(artifact, descriptor)

        if not destination:
            raise SAMLError("Missing endpoint location")

        _sid = sid()
        mid, msg = self.create_artifact_resolve(
            artifact,
            destination,
            _sid,
            sign=sign,
            sign_alg=sign_alg,
            digest_alg=digest_alg,
        )
        return self.send_using_soap(msg, destination)

    def parse_artifact_resolve(self, txt, **kwargs):
        """
        Always done over SOAP

        :param txt: The SOAP enveloped ArtifactResolve
        :param kwargs:
        :return: An ArtifactResolve instance
        """

        _resp = parse_soap_enveloped_saml_artifact_resolve(txt)
        return artifact_resolve_from_string(_resp)

    def parse_artifact_resolve_response(self, xmlstr):
        kwargs = {"entity_id": self.config.entityid, "attribute_converters": self.config.attribute_converters}

        resp = self._parse_response(xmlstr, saml_response.ArtifactResponse, "artifact_resolve", BINDING_SOAP, **kwargs)
        # should just be one
        elems = extension_elements_to_elements(resp.response.extension_elements, [samlp, saml])
        return elems[0]
