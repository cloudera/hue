#!/usr/bin/env python

#
# Generated Sun Jun 14 13:41:29 2015 by parse_xsd.py version 0.5.
#

import saml2
from saml2 import SamlBase
from saml2.ws import wsaddr as wsa
from saml2.ws import wssec as wsse
from saml2.ws import wsutil as wsu


NAMESPACE = "http://docs.oasis-open.org/ws-sx/ws-trust/200512/"


class RequestSecurityTokenType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestSecurityTokenType element"""

    c_tag = "RequestSecurityTokenType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["Context"] = ("context", "anyURI", False)

    def __init__(
        self,
        context=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.context = context


def request_security_token_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestSecurityTokenType_, xml_string)


class TokenType(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:TokenType element"""

    c_tag = "TokenType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def token_type_from_string(xml_string):
    return saml2.create_class_from_xml_string(TokenType, xml_string)


class RequestTypeOpenEnum_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestTypeOpenEnum element"""

    c_tag = "RequestTypeOpenEnum"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def request_type_open_enum__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestTypeOpenEnum_, xml_string)


class RequestTypeEnum_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestTypeEnum element"""

    c_tag = "RequestTypeEnum"
    c_namespace = NAMESPACE
    c_value_type = {
        "base": "xs:anyURI",
        "enumeration": [
            "http://docs.oasis-open.org/ws-sx/ws-trust/200512/Issue",
            "http://docs.oasis-open.org/ws-sx/ws-trust/200512/Renew",
            "http://docs.oasis-open.org/ws-sx/ws-trust/200512/Cancel",
            "http://docs.oasis-open.org/ws-sx/ws-trust/200512/STSCancel",
            "http://docs.oasis-open.org/ws-sx/ws-trust/200512/Validate",
        ],
    }
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def request_type_enum__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestTypeEnum_, xml_string)


class RequestSecurityTokenResponseType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestSecurityTokenResponseType element"""

    c_tag = "RequestSecurityTokenResponseType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["Context"] = ("context", "anyURI", False)

    def __init__(
        self,
        context=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.context = context


def request_security_token_response_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestSecurityTokenResponseType_, xml_string)


class RequestedSecurityTokenType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestedSecurityTokenType element"""

    c_tag = "RequestedSecurityTokenType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def requested_security_token_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestedSecurityTokenType_, xml_string)


class BinarySecretTypeEnum_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:BinarySecretTypeEnum element"""

    c_tag = "BinarySecretTypeEnum"
    c_namespace = NAMESPACE
    c_value_type = {
        "base": "xs:anyURI",
        "enumeration": [
            "http://docs.oasis-open.org/ws-sx/ws-trust/200512/AsymmetricKey",
            "http://docs.oasis-open.org/ws-sx/ws-trust/200512/SymmetricKey",
            "http://docs.oasis-open.org/ws-sx/ws-trust/200512/Nonce",
        ],
    }
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def binary_secret_type_enum__from_string(xml_string):
    return saml2.create_class_from_xml_string(BinarySecretTypeEnum_, xml_string)


class BinarySecretTypeOpenEnum_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:BinarySecretTypeOpenEnum element"""

    c_tag = "BinarySecretTypeOpenEnum"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def binary_secret_type_open_enum__from_string(xml_string):
    return saml2.create_class_from_xml_string(BinarySecretTypeOpenEnum_, xml_string)


class ClaimsType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:ClaimsType element"""

    c_tag = "ClaimsType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["Dialect"] = ("dialect", "anyURI", False)

    def __init__(
        self,
        dialect=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.dialect = dialect


def claims_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ClaimsType_, xml_string)


class EntropyType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:EntropyType element"""

    c_tag = "EntropyType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def entropy_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(EntropyType_, xml_string)


class LifetimeType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:LifetimeType element"""

    c_tag = "LifetimeType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Created"] = (
        "created",
        wsu.Created,
    )
    c_cardinality["created"] = {"min": 0, "max": 1}
    c_children["{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Expires"] = (
        "expires",
        wsu.Expires,
    )
    c_cardinality["expires"] = {"min": 0, "max": 1}
    c_child_order.extend(["created", "expires"])

    def __init__(
        self,
        created=None,
        expires=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.created = created
        self.expires = expires


def lifetime_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(LifetimeType_, xml_string)


class RequestSecurityTokenCollectionType_RequestSecurityToken(RequestSecurityTokenType_):

    c_tag = "RequestSecurityToken"
    c_namespace = NAMESPACE
    c_children = RequestSecurityTokenType_.c_children.copy()
    c_attributes = RequestSecurityTokenType_.c_attributes.copy()
    c_child_order = RequestSecurityTokenType_.c_child_order[:]
    c_cardinality = RequestSecurityTokenType_.c_cardinality.copy()


def request_security_token_collection_type__request_security_token_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestSecurityTokenCollectionType_RequestSecurityToken, xml_string)


class RequestSecurityTokenCollectionType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestSecurityTokenCollectionType element"""

    c_tag = "RequestSecurityTokenCollectionType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://docs.oasis-open.org/ws-sx/ws-trust/200512/}RequestSecurityToken"] = (
        "request_security_token",
        [RequestSecurityTokenCollectionType_RequestSecurityToken],
    )
    c_cardinality["request_security_token"] = {"min": 2}
    c_child_order.extend(["request_security_token"])

    def __init__(
        self,
        request_security_token=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.request_security_token = request_security_token or []


def request_security_token_collection_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestSecurityTokenCollectionType_, xml_string)


class ComputedKeyEnum_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:ComputedKeyEnum element"""

    c_tag = "ComputedKeyEnum"
    c_namespace = NAMESPACE
    c_value_type = {
        "base": "xs:anyURI",
        "enumeration": [
            "http://docs.oasis-open.org/ws-sx/ws-trust/200512/CK/PSHA1",
            "http://docs.oasis-open.org/ws-sx/ws-trust/200512/CK/HASH",
        ],
    }
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def computed_key_enum__from_string(xml_string):
    return saml2.create_class_from_xml_string(ComputedKeyEnum_, xml_string)


class ComputedKeyOpenEnum_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:ComputedKeyOpenEnum element"""

    c_tag = "ComputedKeyOpenEnum"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def computed_key_open_enum__from_string(xml_string):
    return saml2.create_class_from_xml_string(ComputedKeyOpenEnum_, xml_string)


class RequestedReferenceType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestedReferenceType element"""

    c_tag = "RequestedReferenceType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}SecurityTokenReference"
    ] = ("security_token_reference", wsse.SecurityTokenReference)
    c_child_order.extend(["security_token_reference"])

    def __init__(
        self,
        security_token_reference=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.security_token_reference = security_token_reference


def requested_reference_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestedReferenceType_, xml_string)


class RequestedProofTokenType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestedProofTokenType element"""

    c_tag = "RequestedProofTokenType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def requested_proof_token_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestedProofTokenType_, xml_string)


class RenewTargetType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RenewTargetType element"""

    c_tag = "RenewTargetType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def renew_target_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RenewTargetType_, xml_string)


class AllowPostdatingType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:AllowPostdatingType element"""

    c_tag = "AllowPostdatingType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def allow_postdating_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AllowPostdatingType_, xml_string)


class RenewingType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RenewingType element"""

    c_tag = "RenewingType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["Allow"] = ("allow", "boolean", False)
    c_attributes["OK"] = ("ok", "boolean", False)

    def __init__(
        self,
        allow=None,
        ok=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.allow = allow
        self.ok = ok


def renewing_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RenewingType_, xml_string)


class CancelTargetType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:CancelTargetType element"""

    c_tag = "CancelTargetType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def cancel_target_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(CancelTargetType_, xml_string)


class RequestedTokenCancelledType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestedTokenCancelledType element"""

    c_tag = "RequestedTokenCancelledType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def requested_token_cancelled_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestedTokenCancelledType_, xml_string)


class ValidateTargetType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:ValidateTargetType element"""

    c_tag = "ValidateTargetType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def validate_target_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ValidateTargetType_, xml_string)


class StatusCodeEnum_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:StatusCodeEnum element"""

    c_tag = "StatusCodeEnum"
    c_namespace = NAMESPACE
    c_value_type = {
        "base": "xs:anyURI",
        "enumeration": [
            "http://docs.oasis-open.org/ws-sx/ws-trust/200512/status/valid",
            "http://docs.oasis-open.org/ws-sx/ws-trust/200512/status/invalid",
        ],
    }
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def status_code_enum__from_string(xml_string):
    return saml2.create_class_from_xml_string(StatusCodeEnum_, xml_string)


class StatusCodeOpenEnum_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:StatusCodeOpenEnum element"""

    c_tag = "StatusCodeOpenEnum"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def status_code_open_enum__from_string(xml_string):
    return saml2.create_class_from_xml_string(StatusCodeOpenEnum_, xml_string)


class Challenge(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:Challenge element"""

    c_tag = "Challenge"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def challenge_from_string(xml_string):
    return saml2.create_class_from_xml_string(Challenge, xml_string)


class BinaryExchangeType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:BinaryExchangeType element"""

    c_tag = "BinaryExchangeType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["ValueType"] = ("value_type", "anyURI", True)
    c_attributes["EncodingType"] = ("encoding_type", "anyURI", True)

    def __init__(
        self,
        value_type=None,
        encoding_type=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.value_type = value_type
        self.encoding_type = encoding_type


def binary_exchange_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(BinaryExchangeType_, xml_string)


class RequestKETType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestKETType element"""

    c_tag = "RequestKETType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def request_ket_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestKETType_, xml_string)


class KeyExchangeTokenType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:KeyExchangeTokenType element"""

    c_tag = "KeyExchangeTokenType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def key_exchange_token_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyExchangeTokenType_, xml_string)


class CombinedHash(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:CombinedHash element"""

    c_tag = "CombinedHash"
    c_namespace = NAMESPACE
    c_value_type = {"base": "base64Binary"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def combined_hash_from_string(xml_string):
    return saml2.create_class_from_xml_string(CombinedHash, xml_string)


class OnBehalfOfType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:OnBehalfOfType element"""

    c_tag = "OnBehalfOfType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def on_behalf_of_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(OnBehalfOfType_, xml_string)


class Issuer(wsa.EndpointReferenceType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:Issuer element"""

    c_tag = "Issuer"
    c_namespace = NAMESPACE
    c_children = wsa.EndpointReferenceType_.c_children.copy()
    c_attributes = wsa.EndpointReferenceType_.c_attributes.copy()
    c_child_order = wsa.EndpointReferenceType_.c_child_order[:]
    c_cardinality = wsa.EndpointReferenceType_.c_cardinality.copy()


def issuer_from_string(xml_string):
    return saml2.create_class_from_xml_string(Issuer, xml_string)


class AuthenticationType(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:AuthenticationType element"""

    c_tag = "AuthenticationType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def authentication_type_from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthenticationType, xml_string)


class KeyTypeEnum_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:KeyTypeEnum element"""

    c_tag = "KeyTypeEnum"
    c_namespace = NAMESPACE
    c_value_type = {
        "base": "xs:anyURI",
        "enumeration": [
            "http://docs.oasis-open.org/ws-sx/ws-trust/200512/PublicKey",
            "http://docs.oasis-open.org/ws-sx/ws-trust/200512/SymmetricKey",
            "http://docs.oasis-open.org/wssx/wstrust/200512/Bearer",
        ],
    }
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def key_type_enum__from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyTypeEnum_, xml_string)


class KeyTypeOpenEnum_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:KeyTypeOpenEnum element"""

    c_tag = "KeyTypeOpenEnum"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def key_type_open_enum__from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyTypeOpenEnum_, xml_string)


class KeySize(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:KeySize element"""

    c_tag = "KeySize"
    c_namespace = NAMESPACE
    c_value_type = {"base": "unsignedInt"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def key_size_from_string(xml_string):
    return saml2.create_class_from_xml_string(KeySize, xml_string)


class SignatureAlgorithm(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:SignatureAlgorithm element"""

    c_tag = "SignatureAlgorithm"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def signature_algorithm_from_string(xml_string):
    return saml2.create_class_from_xml_string(SignatureAlgorithm, xml_string)


class EncryptionAlgorithm(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:EncryptionAlgorithm element"""

    c_tag = "EncryptionAlgorithm"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def encryption_algorithm_from_string(xml_string):
    return saml2.create_class_from_xml_string(EncryptionAlgorithm, xml_string)


class CanonicalizationAlgorithm(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:CanonicalizationAlgorithm element"""

    c_tag = "CanonicalizationAlgorithm"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def canonicalization_algorithm_from_string(xml_string):
    return saml2.create_class_from_xml_string(CanonicalizationAlgorithm, xml_string)


class ComputedKeyAlgorithm(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:ComputedKeyAlgorithm element"""

    c_tag = "ComputedKeyAlgorithm"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def computed_key_algorithm_from_string(xml_string):
    return saml2.create_class_from_xml_string(ComputedKeyAlgorithm, xml_string)


class EncryptionType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:EncryptionType element"""

    c_tag = "EncryptionType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def encryption_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(EncryptionType_, xml_string)


class ProofEncryptionType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:ProofEncryptionType element"""

    c_tag = "ProofEncryptionType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def proof_encryption_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ProofEncryptionType_, xml_string)


class UseKeyType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:UseKeyType element"""

    c_tag = "UseKeyType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["Sig"] = ("sig", "anyURI", False)

    def __init__(
        self,
        sig=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.sig = sig


def use_key_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(UseKeyType_, xml_string)


class KeyWrapAlgorithm(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:KeyWrapAlgorithm element"""

    c_tag = "KeyWrapAlgorithm"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def key_wrap_algorithm_from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyWrapAlgorithm, xml_string)


class SignWith(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:SignWith element"""

    c_tag = "SignWith"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def sign_with_from_string(xml_string):
    return saml2.create_class_from_xml_string(SignWith, xml_string)


class EncryptWith(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:EncryptWith element"""

    c_tag = "EncryptWith"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def encrypt_with_from_string(xml_string):
    return saml2.create_class_from_xml_string(EncryptWith, xml_string)


class DelegateToType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:DelegateToType element"""

    c_tag = "DelegateToType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def delegate_to_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(DelegateToType_, xml_string)


class Forwardable(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:Forwardable element"""

    c_tag = "Forwardable"
    c_namespace = NAMESPACE
    c_value_type = {"base": "boolean"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def forwardable_from_string(xml_string):
    return saml2.create_class_from_xml_string(Forwardable, xml_string)


class Delegatable(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:Delegatable element"""

    c_tag = "Delegatable"
    c_namespace = NAMESPACE
    c_value_type = {"base": "boolean"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def delegatable_from_string(xml_string):
    return saml2.create_class_from_xml_string(Delegatable, xml_string)


class ParticipantType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:ParticipantType element"""

    c_tag = "ParticipantType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def participant_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ParticipantType_, xml_string)


class RequestSecurityToken(RequestSecurityTokenType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestSecurityToken element"""

    c_tag = "RequestSecurityToken"
    c_namespace = NAMESPACE
    c_children = RequestSecurityTokenType_.c_children.copy()
    c_attributes = RequestSecurityTokenType_.c_attributes.copy()
    c_child_order = RequestSecurityTokenType_.c_child_order[:]
    c_cardinality = RequestSecurityTokenType_.c_cardinality.copy()


def request_security_token_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestSecurityToken, xml_string)


class RequestType(RequestTypeOpenEnum_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestType element"""

    c_tag = "RequestType"
    c_namespace = NAMESPACE
    c_children = RequestTypeOpenEnum_.c_children.copy()
    c_attributes = RequestTypeOpenEnum_.c_attributes.copy()
    c_child_order = RequestTypeOpenEnum_.c_child_order[:]
    c_cardinality = RequestTypeOpenEnum_.c_cardinality.copy()


def request_type_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestType, xml_string)


class RequestSecurityTokenResponse(RequestSecurityTokenResponseType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestSecurityTokenResponse element"""

    c_tag = "RequestSecurityTokenResponse"
    c_namespace = NAMESPACE
    c_children = RequestSecurityTokenResponseType_.c_children.copy()
    c_attributes = RequestSecurityTokenResponseType_.c_attributes.copy()
    c_child_order = RequestSecurityTokenResponseType_.c_child_order[:]
    c_cardinality = RequestSecurityTokenResponseType_.c_cardinality.copy()


def request_security_token_response_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestSecurityTokenResponse, xml_string)


class RequestedSecurityToken(RequestedSecurityTokenType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestedSecurityToken element"""

    c_tag = "RequestedSecurityToken"
    c_namespace = NAMESPACE
    c_children = RequestedSecurityTokenType_.c_children.copy()
    c_attributes = RequestedSecurityTokenType_.c_attributes.copy()
    c_child_order = RequestedSecurityTokenType_.c_child_order[:]
    c_cardinality = RequestedSecurityTokenType_.c_cardinality.copy()


def requested_security_token_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestedSecurityToken, xml_string)


class BinarySecretType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:BinarySecretType element"""

    c_tag = "BinarySecretType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "base64Binary"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["Type"] = ("type", BinarySecretTypeOpenEnum_, False)

    def __init__(
        self,
        type=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.type = type


def binary_secret_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(BinarySecretType_, xml_string)


class Claims(ClaimsType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:Claims element"""

    c_tag = "Claims"
    c_namespace = NAMESPACE
    c_children = ClaimsType_.c_children.copy()
    c_attributes = ClaimsType_.c_attributes.copy()
    c_child_order = ClaimsType_.c_child_order[:]
    c_cardinality = ClaimsType_.c_cardinality.copy()


def claims_from_string(xml_string):
    return saml2.create_class_from_xml_string(Claims, xml_string)


class Entropy(EntropyType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:Entropy element"""

    c_tag = "Entropy"
    c_namespace = NAMESPACE
    c_children = EntropyType_.c_children.copy()
    c_attributes = EntropyType_.c_attributes.copy()
    c_child_order = EntropyType_.c_child_order[:]
    c_cardinality = EntropyType_.c_cardinality.copy()


def entropy_from_string(xml_string):
    return saml2.create_class_from_xml_string(Entropy, xml_string)


class Lifetime(LifetimeType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:Lifetime element"""

    c_tag = "Lifetime"
    c_namespace = NAMESPACE
    c_children = LifetimeType_.c_children.copy()
    c_attributes = LifetimeType_.c_attributes.copy()
    c_child_order = LifetimeType_.c_child_order[:]
    c_cardinality = LifetimeType_.c_cardinality.copy()


def lifetime_from_string(xml_string):
    return saml2.create_class_from_xml_string(Lifetime, xml_string)


class RequestSecurityTokenCollection(RequestSecurityTokenCollectionType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestSecurityTokenCollection element"""

    c_tag = "RequestSecurityTokenCollection"
    c_namespace = NAMESPACE
    c_children = RequestSecurityTokenCollectionType_.c_children.copy()
    c_attributes = RequestSecurityTokenCollectionType_.c_attributes.copy()
    c_child_order = RequestSecurityTokenCollectionType_.c_child_order[:]
    c_cardinality = RequestSecurityTokenCollectionType_.c_cardinality.copy()


def request_security_token_collection_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestSecurityTokenCollection, xml_string)


class RequestSecurityTokenResponseCollectionType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestSecurityTokenResponseCollectionType element"""

    c_tag = "RequestSecurityTokenResponseCollectionType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://docs.oasis-open.org/ws-sx/ws-trust/200512/}RequestSecurityTokenResponse"] = (
        "request_security_token_response",
        [RequestSecurityTokenResponse],
    )
    c_cardinality["request_security_token_response"] = {"min": 1}
    c_child_order.extend(["request_security_token_response"])

    def __init__(
        self,
        request_security_token_response=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.request_security_token_response = request_security_token_response or []


def request_security_token_response_collection_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestSecurityTokenResponseCollectionType_, xml_string)


class ComputedKey(ComputedKeyOpenEnum_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:ComputedKey element"""

    c_tag = "ComputedKey"
    c_namespace = NAMESPACE
    c_children = ComputedKeyOpenEnum_.c_children.copy()
    c_attributes = ComputedKeyOpenEnum_.c_attributes.copy()
    c_child_order = ComputedKeyOpenEnum_.c_child_order[:]
    c_cardinality = ComputedKeyOpenEnum_.c_cardinality.copy()


def computed_key_from_string(xml_string):
    return saml2.create_class_from_xml_string(ComputedKey, xml_string)


class RequestedAttachedReference(RequestedReferenceType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestedAttachedReference element"""

    c_tag = "RequestedAttachedReference"
    c_namespace = NAMESPACE
    c_children = RequestedReferenceType_.c_children.copy()
    c_attributes = RequestedReferenceType_.c_attributes.copy()
    c_child_order = RequestedReferenceType_.c_child_order[:]
    c_cardinality = RequestedReferenceType_.c_cardinality.copy()


def requested_attached_reference_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestedAttachedReference, xml_string)


class RequestedUnattachedReference(RequestedReferenceType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestedUnattachedReference element"""

    c_tag = "RequestedUnattachedReference"
    c_namespace = NAMESPACE
    c_children = RequestedReferenceType_.c_children.copy()
    c_attributes = RequestedReferenceType_.c_attributes.copy()
    c_child_order = RequestedReferenceType_.c_child_order[:]
    c_cardinality = RequestedReferenceType_.c_cardinality.copy()


def requested_unattached_reference_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestedUnattachedReference, xml_string)


class RequestedProofToken(RequestedProofTokenType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestedProofToken element"""

    c_tag = "RequestedProofToken"
    c_namespace = NAMESPACE
    c_children = RequestedProofTokenType_.c_children.copy()
    c_attributes = RequestedProofTokenType_.c_attributes.copy()
    c_child_order = RequestedProofTokenType_.c_child_order[:]
    c_cardinality = RequestedProofTokenType_.c_cardinality.copy()


def requested_proof_token_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestedProofToken, xml_string)


class IssuedTokens(RequestSecurityTokenResponseCollectionType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:IssuedTokens element"""

    c_tag = "IssuedTokens"
    c_namespace = NAMESPACE
    c_children = RequestSecurityTokenResponseCollectionType_.c_children.copy()
    c_attributes = RequestSecurityTokenResponseCollectionType_.c_attributes.copy()
    c_child_order = RequestSecurityTokenResponseCollectionType_.c_child_order[:]
    c_cardinality = RequestSecurityTokenResponseCollectionType_.c_cardinality.copy()


def issued_tokens_from_string(xml_string):
    return saml2.create_class_from_xml_string(IssuedTokens, xml_string)


class RenewTarget(RenewTargetType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RenewTarget element"""

    c_tag = "RenewTarget"
    c_namespace = NAMESPACE
    c_children = RenewTargetType_.c_children.copy()
    c_attributes = RenewTargetType_.c_attributes.copy()
    c_child_order = RenewTargetType_.c_child_order[:]
    c_cardinality = RenewTargetType_.c_cardinality.copy()


def renew_target_from_string(xml_string):
    return saml2.create_class_from_xml_string(RenewTarget, xml_string)


class AllowPostdating(AllowPostdatingType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:AllowPostdating element"""

    c_tag = "AllowPostdating"
    c_namespace = NAMESPACE
    c_children = AllowPostdatingType_.c_children.copy()
    c_attributes = AllowPostdatingType_.c_attributes.copy()
    c_child_order = AllowPostdatingType_.c_child_order[:]
    c_cardinality = AllowPostdatingType_.c_cardinality.copy()


def allow_postdating_from_string(xml_string):
    return saml2.create_class_from_xml_string(AllowPostdating, xml_string)


class Renewing(RenewingType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:Renewing element"""

    c_tag = "Renewing"
    c_namespace = NAMESPACE
    c_children = RenewingType_.c_children.copy()
    c_attributes = RenewingType_.c_attributes.copy()
    c_child_order = RenewingType_.c_child_order[:]
    c_cardinality = RenewingType_.c_cardinality.copy()


def renewing_from_string(xml_string):
    return saml2.create_class_from_xml_string(Renewing, xml_string)


class CancelTarget(CancelTargetType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:CancelTarget element"""

    c_tag = "CancelTarget"
    c_namespace = NAMESPACE
    c_children = CancelTargetType_.c_children.copy()
    c_attributes = CancelTargetType_.c_attributes.copy()
    c_child_order = CancelTargetType_.c_child_order[:]
    c_cardinality = CancelTargetType_.c_cardinality.copy()


def cancel_target_from_string(xml_string):
    return saml2.create_class_from_xml_string(CancelTarget, xml_string)


class RequestedTokenCancelled(RequestedTokenCancelledType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestedTokenCancelled element"""

    c_tag = "RequestedTokenCancelled"
    c_namespace = NAMESPACE
    c_children = RequestedTokenCancelledType_.c_children.copy()
    c_attributes = RequestedTokenCancelledType_.c_attributes.copy()
    c_child_order = RequestedTokenCancelledType_.c_child_order[:]
    c_cardinality = RequestedTokenCancelledType_.c_cardinality.copy()


def requested_token_cancelled_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestedTokenCancelled, xml_string)


class ValidateTarget(ValidateTargetType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:ValidateTarget element"""

    c_tag = "ValidateTarget"
    c_namespace = NAMESPACE
    c_children = ValidateTargetType_.c_children.copy()
    c_attributes = ValidateTargetType_.c_attributes.copy()
    c_child_order = ValidateTargetType_.c_child_order[:]
    c_cardinality = ValidateTargetType_.c_cardinality.copy()


def validate_target_from_string(xml_string):
    return saml2.create_class_from_xml_string(ValidateTarget, xml_string)


class StatusType_Code(StatusCodeOpenEnum_):

    c_tag = "Code"
    c_namespace = NAMESPACE
    c_children = StatusCodeOpenEnum_.c_children.copy()
    c_attributes = StatusCodeOpenEnum_.c_attributes.copy()
    c_child_order = StatusCodeOpenEnum_.c_child_order[:]
    c_cardinality = StatusCodeOpenEnum_.c_cardinality.copy()


def status_type__code_from_string(xml_string):
    return saml2.create_class_from_xml_string(StatusType_Code, xml_string)


class StatusType_Reason(SamlBase):

    c_tag = "Reason"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def status_type__reason_from_string(xml_string):
    return saml2.create_class_from_xml_string(StatusType_Reason, xml_string)


class StatusType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:StatusType element"""

    c_tag = "StatusType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://docs.oasis-open.org/ws-sx/ws-trust/200512/}Code"] = ("code", StatusType_Code)
    c_children["{http://docs.oasis-open.org/ws-sx/ws-trust/200512/}Reason"] = ("reason", StatusType_Reason)
    c_cardinality["reason"] = {"min": 0, "max": 1}
    c_child_order.extend(["code", "reason"])

    def __init__(
        self,
        code=None,
        reason=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.code = code
        self.reason = reason


def status_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(StatusType_, xml_string)


class SignChallengeType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:SignChallengeType element"""

    c_tag = "SignChallengeType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://docs.oasis-open.org/ws-sx/ws-trust/200512/}Challenge"] = ("challenge", Challenge)
    c_child_order.extend(["challenge"])

    def __init__(
        self,
        challenge=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.challenge = challenge


def sign_challenge_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SignChallengeType_, xml_string)


class BinaryExchange(BinaryExchangeType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:BinaryExchange element"""

    c_tag = "BinaryExchange"
    c_namespace = NAMESPACE
    c_children = BinaryExchangeType_.c_children.copy()
    c_attributes = BinaryExchangeType_.c_attributes.copy()
    c_child_order = BinaryExchangeType_.c_child_order[:]
    c_cardinality = BinaryExchangeType_.c_cardinality.copy()


def binary_exchange_from_string(xml_string):
    return saml2.create_class_from_xml_string(BinaryExchange, xml_string)


class RequestKET(RequestKETType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestKET element"""

    c_tag = "RequestKET"
    c_namespace = NAMESPACE
    c_children = RequestKETType_.c_children.copy()
    c_attributes = RequestKETType_.c_attributes.copy()
    c_child_order = RequestKETType_.c_child_order[:]
    c_cardinality = RequestKETType_.c_cardinality.copy()


def request_ket_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestKET, xml_string)


class KeyExchangeToken(KeyExchangeTokenType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:KeyExchangeToken element"""

    c_tag = "KeyExchangeToken"
    c_namespace = NAMESPACE
    c_children = KeyExchangeTokenType_.c_children.copy()
    c_attributes = KeyExchangeTokenType_.c_attributes.copy()
    c_child_order = KeyExchangeTokenType_.c_child_order[:]
    c_cardinality = KeyExchangeTokenType_.c_cardinality.copy()


def key_exchange_token_from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyExchangeToken, xml_string)


class AuthenticatorType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:AuthenticatorType element"""

    c_tag = "AuthenticatorType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://docs.oasis-open.org/ws-sx/ws-trust/200512/}CombinedHash"] = ("combined_hash", CombinedHash)
    c_cardinality["combined_hash"] = {"min": 0, "max": 1}
    c_child_order.extend(["combined_hash"])

    def __init__(
        self,
        combined_hash=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.combined_hash = combined_hash


def authenticator_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthenticatorType_, xml_string)


class OnBehalfOf(OnBehalfOfType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:OnBehalfOf element"""

    c_tag = "OnBehalfOf"
    c_namespace = NAMESPACE
    c_children = OnBehalfOfType_.c_children.copy()
    c_attributes = OnBehalfOfType_.c_attributes.copy()
    c_child_order = OnBehalfOfType_.c_child_order[:]
    c_cardinality = OnBehalfOfType_.c_cardinality.copy()


def on_behalf_of_from_string(xml_string):
    return saml2.create_class_from_xml_string(OnBehalfOf, xml_string)


class KeyType(KeyTypeOpenEnum_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:KeyType element"""

    c_tag = "KeyType"
    c_namespace = NAMESPACE
    c_children = KeyTypeOpenEnum_.c_children.copy()
    c_attributes = KeyTypeOpenEnum_.c_attributes.copy()
    c_child_order = KeyTypeOpenEnum_.c_child_order[:]
    c_cardinality = KeyTypeOpenEnum_.c_cardinality.copy()


def key_type_from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyType, xml_string)


class Encryption(EncryptionType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:Encryption element"""

    c_tag = "Encryption"
    c_namespace = NAMESPACE
    c_children = EncryptionType_.c_children.copy()
    c_attributes = EncryptionType_.c_attributes.copy()
    c_child_order = EncryptionType_.c_child_order[:]
    c_cardinality = EncryptionType_.c_cardinality.copy()


def encryption_from_string(xml_string):
    return saml2.create_class_from_xml_string(Encryption, xml_string)


class ProofEncryption(ProofEncryptionType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:ProofEncryption element"""

    c_tag = "ProofEncryption"
    c_namespace = NAMESPACE
    c_children = ProofEncryptionType_.c_children.copy()
    c_attributes = ProofEncryptionType_.c_attributes.copy()
    c_child_order = ProofEncryptionType_.c_child_order[:]
    c_cardinality = ProofEncryptionType_.c_cardinality.copy()


def proof_encryption_from_string(xml_string):
    return saml2.create_class_from_xml_string(ProofEncryption, xml_string)


class UseKey(UseKeyType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:UseKey element"""

    c_tag = "UseKey"
    c_namespace = NAMESPACE
    c_children = UseKeyType_.c_children.copy()
    c_attributes = UseKeyType_.c_attributes.copy()
    c_child_order = UseKeyType_.c_child_order[:]
    c_cardinality = UseKeyType_.c_cardinality.copy()


def use_key_from_string(xml_string):
    return saml2.create_class_from_xml_string(UseKey, xml_string)


class DelegateTo(DelegateToType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:DelegateTo element"""

    c_tag = "DelegateTo"
    c_namespace = NAMESPACE
    c_children = DelegateToType_.c_children.copy()
    c_attributes = DelegateToType_.c_attributes.copy()
    c_child_order = DelegateToType_.c_child_order[:]
    c_cardinality = DelegateToType_.c_cardinality.copy()


def delegate_to_from_string(xml_string):
    return saml2.create_class_from_xml_string(DelegateTo, xml_string)


class ParticipantsType_Primary(ParticipantType_):

    c_tag = "Primary"
    c_namespace = NAMESPACE
    c_children = ParticipantType_.c_children.copy()
    c_attributes = ParticipantType_.c_attributes.copy()
    c_child_order = ParticipantType_.c_child_order[:]
    c_cardinality = ParticipantType_.c_cardinality.copy()


def participants_type__primary_from_string(xml_string):
    return saml2.create_class_from_xml_string(ParticipantsType_Primary, xml_string)


class ParticipantsType_Participant(ParticipantType_):

    c_tag = "Participant"
    c_namespace = NAMESPACE
    c_children = ParticipantType_.c_children.copy()
    c_attributes = ParticipantType_.c_attributes.copy()
    c_child_order = ParticipantType_.c_child_order[:]
    c_cardinality = ParticipantType_.c_cardinality.copy()


def participants_type__participant_from_string(xml_string):
    return saml2.create_class_from_xml_string(ParticipantsType_Participant, xml_string)


class ParticipantsType_(SamlBase):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:ParticipantsType element"""

    c_tag = "ParticipantsType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://docs.oasis-open.org/ws-sx/ws-trust/200512/}Primary"] = ("primary", ParticipantsType_Primary)
    c_cardinality["primary"] = {"min": 0, "max": 1}
    c_children["{http://docs.oasis-open.org/ws-sx/ws-trust/200512/}Participant"] = (
        "participant",
        [ParticipantsType_Participant],
    )
    c_cardinality["participant"] = {"min": 0}
    c_child_order.extend(["primary", "participant"])

    def __init__(
        self,
        primary=None,
        participant=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.primary = primary
        self.participant = participant or []


def participants_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ParticipantsType_, xml_string)


class BinarySecret(BinarySecretType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:BinarySecret element"""

    c_tag = "BinarySecret"
    c_namespace = NAMESPACE
    c_children = BinarySecretType_.c_children.copy()
    c_attributes = BinarySecretType_.c_attributes.copy()
    c_child_order = BinarySecretType_.c_child_order[:]
    c_cardinality = BinarySecretType_.c_cardinality.copy()


def binary_secret_from_string(xml_string):
    return saml2.create_class_from_xml_string(BinarySecret, xml_string)


class RequestSecurityTokenResponseCollection(RequestSecurityTokenResponseCollectionType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:RequestSecurityTokenResponseCollection element"""

    c_tag = "RequestSecurityTokenResponseCollection"
    c_namespace = NAMESPACE
    c_children = RequestSecurityTokenResponseCollectionType_.c_children.copy()
    c_attributes = RequestSecurityTokenResponseCollectionType_.c_attributes.copy()
    c_child_order = RequestSecurityTokenResponseCollectionType_.c_child_order[:]
    c_cardinality = RequestSecurityTokenResponseCollectionType_.c_cardinality.copy()


def request_security_token_response_collection_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestSecurityTokenResponseCollection, xml_string)


class Status(StatusType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:Status element"""

    c_tag = "Status"
    c_namespace = NAMESPACE
    c_children = StatusType_.c_children.copy()
    c_attributes = StatusType_.c_attributes.copy()
    c_child_order = StatusType_.c_child_order[:]
    c_cardinality = StatusType_.c_cardinality.copy()


def status_from_string(xml_string):
    return saml2.create_class_from_xml_string(Status, xml_string)


class SignChallenge(SignChallengeType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:SignChallenge element"""

    c_tag = "SignChallenge"
    c_namespace = NAMESPACE
    c_children = SignChallengeType_.c_children.copy()
    c_attributes = SignChallengeType_.c_attributes.copy()
    c_child_order = SignChallengeType_.c_child_order[:]
    c_cardinality = SignChallengeType_.c_cardinality.copy()


def sign_challenge_from_string(xml_string):
    return saml2.create_class_from_xml_string(SignChallenge, xml_string)


class SignChallengeResponse(SignChallengeType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:SignChallengeResponse element"""

    c_tag = "SignChallengeResponse"
    c_namespace = NAMESPACE
    c_children = SignChallengeType_.c_children.copy()
    c_attributes = SignChallengeType_.c_attributes.copy()
    c_child_order = SignChallengeType_.c_child_order[:]
    c_cardinality = SignChallengeType_.c_cardinality.copy()


def sign_challenge_response_from_string(xml_string):
    return saml2.create_class_from_xml_string(SignChallengeResponse, xml_string)


class Authenticator(AuthenticatorType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:Authenticator element"""

    c_tag = "Authenticator"
    c_namespace = NAMESPACE
    c_children = AuthenticatorType_.c_children.copy()
    c_attributes = AuthenticatorType_.c_attributes.copy()
    c_child_order = AuthenticatorType_.c_child_order[:]
    c_cardinality = AuthenticatorType_.c_cardinality.copy()


def authenticator_from_string(xml_string):
    return saml2.create_class_from_xml_string(Authenticator, xml_string)


class Participants(ParticipantsType_):
    """The http://docs.oasis-open.org/ws-sx/ws-trust/200512/:Participants element"""

    c_tag = "Participants"
    c_namespace = NAMESPACE
    c_children = ParticipantsType_.c_children.copy()
    c_attributes = ParticipantsType_.c_attributes.copy()
    c_child_order = ParticipantsType_.c_child_order[:]
    c_cardinality = ParticipantsType_.c_cardinality.copy()


def participants_from_string(xml_string):
    return saml2.create_class_from_xml_string(Participants, xml_string)


ELEMENT_FROM_STRING = {
    RequestSecurityToken.c_tag: request_security_token_from_string,
    RequestSecurityTokenType_.c_tag: request_security_token_type__from_string,
    TokenType.c_tag: token_type_from_string,
    RequestType.c_tag: request_type_from_string,
    RequestTypeOpenEnum_.c_tag: request_type_open_enum__from_string,
    RequestTypeEnum_.c_tag: request_type_enum__from_string,
    RequestSecurityTokenResponse.c_tag: request_security_token_response_from_string,
    RequestSecurityTokenResponseType_.c_tag: request_security_token_response_type__from_string,
    RequestedSecurityToken.c_tag: requested_security_token_from_string,
    RequestedSecurityTokenType_.c_tag: requested_security_token_type__from_string,
    BinarySecret.c_tag: binary_secret_from_string,
    BinarySecretType_.c_tag: binary_secret_type__from_string,
    BinarySecretTypeEnum_.c_tag: binary_secret_type_enum__from_string,
    BinarySecretTypeOpenEnum_.c_tag: binary_secret_type_open_enum__from_string,
    Claims.c_tag: claims_from_string,
    ClaimsType_.c_tag: claims_type__from_string,
    Entropy.c_tag: entropy_from_string,
    EntropyType_.c_tag: entropy_type__from_string,
    Lifetime.c_tag: lifetime_from_string,
    LifetimeType_.c_tag: lifetime_type__from_string,
    RequestSecurityTokenCollection.c_tag: request_security_token_collection_from_string,
    RequestSecurityTokenCollectionType_.c_tag: request_security_token_collection_type__from_string,
    RequestSecurityTokenResponseCollection.c_tag: request_security_token_response_collection_from_string,
    RequestSecurityTokenResponseCollectionType_.c_tag: request_security_token_response_collection_type__from_string,
    ComputedKey.c_tag: computed_key_from_string,
    ComputedKeyEnum_.c_tag: computed_key_enum__from_string,
    ComputedKeyOpenEnum_.c_tag: computed_key_open_enum__from_string,
    RequestedAttachedReference.c_tag: requested_attached_reference_from_string,
    RequestedUnattachedReference.c_tag: requested_unattached_reference_from_string,
    RequestedReferenceType_.c_tag: requested_reference_type__from_string,
    RequestedProofToken.c_tag: requested_proof_token_from_string,
    RequestedProofTokenType_.c_tag: requested_proof_token_type__from_string,
    IssuedTokens.c_tag: issued_tokens_from_string,
    RenewTarget.c_tag: renew_target_from_string,
    RenewTargetType_.c_tag: renew_target_type__from_string,
    AllowPostdating.c_tag: allow_postdating_from_string,
    AllowPostdatingType_.c_tag: allow_postdating_type__from_string,
    Renewing.c_tag: renewing_from_string,
    RenewingType_.c_tag: renewing_type__from_string,
    CancelTarget.c_tag: cancel_target_from_string,
    CancelTargetType_.c_tag: cancel_target_type__from_string,
    RequestedTokenCancelled.c_tag: requested_token_cancelled_from_string,
    RequestedTokenCancelledType_.c_tag: requested_token_cancelled_type__from_string,
    ValidateTarget.c_tag: validate_target_from_string,
    ValidateTargetType_.c_tag: validate_target_type__from_string,
    Status.c_tag: status_from_string,
    StatusType_.c_tag: status_type__from_string,
    StatusCodeEnum_.c_tag: status_code_enum__from_string,
    StatusCodeOpenEnum_.c_tag: status_code_open_enum__from_string,
    SignChallenge.c_tag: sign_challenge_from_string,
    SignChallengeResponse.c_tag: sign_challenge_response_from_string,
    SignChallengeType_.c_tag: sign_challenge_type__from_string,
    Challenge.c_tag: challenge_from_string,
    BinaryExchange.c_tag: binary_exchange_from_string,
    BinaryExchangeType_.c_tag: binary_exchange_type__from_string,
    RequestKET.c_tag: request_ket_from_string,
    RequestKETType_.c_tag: request_ket_type__from_string,
    KeyExchangeToken.c_tag: key_exchange_token_from_string,
    KeyExchangeTokenType_.c_tag: key_exchange_token_type__from_string,
    Authenticator.c_tag: authenticator_from_string,
    AuthenticatorType_.c_tag: authenticator_type__from_string,
    CombinedHash.c_tag: combined_hash_from_string,
    OnBehalfOf.c_tag: on_behalf_of_from_string,
    OnBehalfOfType_.c_tag: on_behalf_of_type__from_string,
    Issuer.c_tag: issuer_from_string,
    AuthenticationType.c_tag: authentication_type_from_string,
    KeyType.c_tag: key_type_from_string,
    KeyTypeEnum_.c_tag: key_type_enum__from_string,
    KeyTypeOpenEnum_.c_tag: key_type_open_enum__from_string,
    KeySize.c_tag: key_size_from_string,
    SignatureAlgorithm.c_tag: signature_algorithm_from_string,
    EncryptionAlgorithm.c_tag: encryption_algorithm_from_string,
    CanonicalizationAlgorithm.c_tag: canonicalization_algorithm_from_string,
    ComputedKeyAlgorithm.c_tag: computed_key_algorithm_from_string,
    Encryption.c_tag: encryption_from_string,
    EncryptionType_.c_tag: encryption_type__from_string,
    ProofEncryption.c_tag: proof_encryption_from_string,
    ProofEncryptionType_.c_tag: proof_encryption_type__from_string,
    UseKey.c_tag: use_key_from_string,
    UseKeyType_.c_tag: use_key_type__from_string,
    KeyWrapAlgorithm.c_tag: key_wrap_algorithm_from_string,
    SignWith.c_tag: sign_with_from_string,
    EncryptWith.c_tag: encrypt_with_from_string,
    DelegateTo.c_tag: delegate_to_from_string,
    DelegateToType_.c_tag: delegate_to_type__from_string,
    Forwardable.c_tag: forwardable_from_string,
    Delegatable.c_tag: delegatable_from_string,
    Participants.c_tag: participants_from_string,
    ParticipantsType_.c_tag: participants_type__from_string,
    ParticipantType_.c_tag: participant_type__from_string,
    StatusType_Code.c_tag: status_type__code_from_string,
    StatusType_Reason.c_tag: status_type__reason_from_string,
    ParticipantsType_Primary.c_tag: participants_type__primary_from_string,
    ParticipantsType_Participant.c_tag: participants_type__participant_from_string,
}

ELEMENT_BY_TAG = {
    "RequestSecurityToken": RequestSecurityToken,
    "RequestSecurityTokenType": RequestSecurityTokenType_,
    "TokenType": TokenType,
    "RequestType": RequestType,
    "RequestTypeOpenEnum": RequestTypeOpenEnum_,
    "RequestTypeEnum": RequestTypeEnum_,
    "RequestSecurityTokenResponse": RequestSecurityTokenResponse,
    "RequestSecurityTokenResponseType": RequestSecurityTokenResponseType_,
    "RequestedSecurityToken": RequestedSecurityToken,
    "RequestedSecurityTokenType": RequestedSecurityTokenType_,
    "BinarySecret": BinarySecret,
    "BinarySecretType": BinarySecretType_,
    "BinarySecretTypeEnum": BinarySecretTypeEnum_,
    "BinarySecretTypeOpenEnum": BinarySecretTypeOpenEnum_,
    "Claims": Claims,
    "ClaimsType": ClaimsType_,
    "Entropy": Entropy,
    "EntropyType": EntropyType_,
    "Lifetime": Lifetime,
    "LifetimeType": LifetimeType_,
    "RequestSecurityTokenCollection": RequestSecurityTokenCollection,
    "RequestSecurityTokenCollectionType": RequestSecurityTokenCollectionType_,
    "RequestSecurityTokenResponseCollection": RequestSecurityTokenResponseCollection,
    "RequestSecurityTokenResponseCollectionType": RequestSecurityTokenResponseCollectionType_,
    "ComputedKey": ComputedKey,
    "ComputedKeyEnum": ComputedKeyEnum_,
    "ComputedKeyOpenEnum": ComputedKeyOpenEnum_,
    "RequestedAttachedReference": RequestedAttachedReference,
    "RequestedUnattachedReference": RequestedUnattachedReference,
    "RequestedReferenceType": RequestedReferenceType_,
    "RequestedProofToken": RequestedProofToken,
    "RequestedProofTokenType": RequestedProofTokenType_,
    "IssuedTokens": IssuedTokens,
    "RenewTarget": RenewTarget,
    "RenewTargetType": RenewTargetType_,
    "AllowPostdating": AllowPostdating,
    "AllowPostdatingType": AllowPostdatingType_,
    "Renewing": Renewing,
    "RenewingType": RenewingType_,
    "CancelTarget": CancelTarget,
    "CancelTargetType": CancelTargetType_,
    "RequestedTokenCancelled": RequestedTokenCancelled,
    "RequestedTokenCancelledType": RequestedTokenCancelledType_,
    "ValidateTarget": ValidateTarget,
    "ValidateTargetType": ValidateTargetType_,
    "Status": Status,
    "StatusType": StatusType_,
    "StatusCodeEnum": StatusCodeEnum_,
    "StatusCodeOpenEnum": StatusCodeOpenEnum_,
    "SignChallenge": SignChallenge,
    "SignChallengeResponse": SignChallengeResponse,
    "SignChallengeType": SignChallengeType_,
    "Challenge": Challenge,
    "BinaryExchange": BinaryExchange,
    "BinaryExchangeType": BinaryExchangeType_,
    "RequestKET": RequestKET,
    "RequestKETType": RequestKETType_,
    "KeyExchangeToken": KeyExchangeToken,
    "KeyExchangeTokenType": KeyExchangeTokenType_,
    "Authenticator": Authenticator,
    "AuthenticatorType": AuthenticatorType_,
    "CombinedHash": CombinedHash,
    "OnBehalfOf": OnBehalfOf,
    "OnBehalfOfType": OnBehalfOfType_,
    "Issuer": Issuer,
    "AuthenticationType": AuthenticationType,
    "KeyType": KeyType,
    "KeyTypeEnum": KeyTypeEnum_,
    "KeyTypeOpenEnum": KeyTypeOpenEnum_,
    "KeySize": KeySize,
    "SignatureAlgorithm": SignatureAlgorithm,
    "EncryptionAlgorithm": EncryptionAlgorithm,
    "CanonicalizationAlgorithm": CanonicalizationAlgorithm,
    "ComputedKeyAlgorithm": ComputedKeyAlgorithm,
    "Encryption": Encryption,
    "EncryptionType": EncryptionType_,
    "ProofEncryption": ProofEncryption,
    "ProofEncryptionType": ProofEncryptionType_,
    "UseKey": UseKey,
    "UseKeyType": UseKeyType_,
    "KeyWrapAlgorithm": KeyWrapAlgorithm,
    "SignWith": SignWith,
    "EncryptWith": EncryptWith,
    "DelegateTo": DelegateTo,
    "DelegateToType": DelegateToType_,
    "Forwardable": Forwardable,
    "Delegatable": Delegatable,
    "Participants": Participants,
    "ParticipantsType": ParticipantsType_,
    "ParticipantType": ParticipantType_,
    "Code": StatusType_Code,
    "Reason": StatusType_Reason,
    "Primary": ParticipantsType_Primary,
    "Participant": ParticipantsType_Participant,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)
