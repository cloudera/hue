#!/usr/bin/env python

#
# Generated Sun Jun 14 13:29:15 2015 by parse_xsd.py version 0.5.
#

import saml2
from saml2 import SamlBase

from saml2 import xmldsig as ds
from saml2.schema import soapenv
from saml2.ws import wsutil as wsu

NAMESPACE = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'

class AttributedString_(SamlBase):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:AttributedString element """

    c_tag = 'AttributedString'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'string'}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id'] = ('Id', 'string', False)

    def __init__(self,
            Id=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        SamlBase.__init__(self, 
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.Id=Id

def attributed_string__from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributedString_, xml_string)

class PasswordString_(AttributedString_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:PasswordString element """

    c_tag = 'PasswordString'
    c_namespace = NAMESPACE
    c_children = AttributedString_.c_children.copy()
    c_attributes = AttributedString_.c_attributes.copy()
    c_child_order = AttributedString_.c_child_order[:]
    c_cardinality = AttributedString_.c_cardinality.copy()
    c_attributes['Type'] = ('type', 'anyURI', False)

    def __init__(self,
            type=None,
            Id=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        AttributedString_.__init__(self, 
                Id=Id,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.type=type

def password_string__from_string(xml_string):
    return saml2.create_class_from_xml_string(PasswordString_, xml_string)

class EncodedString_(AttributedString_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:EncodedString element """

    c_tag = 'EncodedString'
    c_namespace = NAMESPACE
    c_children = AttributedString_.c_children.copy()
    c_attributes = AttributedString_.c_attributes.copy()
    c_child_order = AttributedString_.c_child_order[:]
    c_cardinality = AttributedString_.c_cardinality.copy()
    c_attributes['EncodingType'] = ('encoding_type', 'anyURI', False)

    def __init__(self,
            encoding_type=None,
            Id=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        AttributedString_.__init__(self, 
                Id=Id,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.encoding_type=encoding_type

def encoded_string__from_string(xml_string):
    return saml2.create_class_from_xml_string(EncodedString_, xml_string)

class UsernameTokenType_Username(AttributedString_):

    c_tag = 'Username'
    c_namespace = NAMESPACE
    c_children = AttributedString_.c_children.copy()
    c_attributes = AttributedString_.c_attributes.copy()
    c_child_order = AttributedString_.c_child_order[:]
    c_cardinality = AttributedString_.c_cardinality.copy()

def username_token_type__username_from_string(xml_string):
    return saml2.create_class_from_xml_string(UsernameTokenType_Username, xml_string)

class UsernameTokenType_(SamlBase):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:UsernameTokenType element """

    c_tag = 'UsernameTokenType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Username'] = ('username', UsernameTokenType_Username)
    c_attributes['{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id'] = ('Id', 'None', False)
    c_child_order.extend(['username'])

    def __init__(self,
            username=None,
            Id=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        SamlBase.__init__(self, 
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.username=username
        self.Id=Id

def username_token_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(UsernameTokenType_, xml_string)

class BinarySecurityTokenType_(EncodedString_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:BinarySecurityTokenType element """

    c_tag = 'BinarySecurityTokenType'
    c_namespace = NAMESPACE
    c_children = EncodedString_.c_children.copy()
    c_attributes = EncodedString_.c_attributes.copy()
    c_child_order = EncodedString_.c_child_order[:]
    c_cardinality = EncodedString_.c_cardinality.copy()
    c_attributes['ValueType'] = ('value_type', 'anyURI', False)

    def __init__(self,
            value_type=None,
            encoding_type=None,
            Id=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        EncodedString_.__init__(self, 
                encoding_type=encoding_type,
                Id=Id,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.value_type=value_type

def binary_security_token_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(BinarySecurityTokenType_, xml_string)

class KeyIdentifierType_(EncodedString_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:KeyIdentifierType element """

    c_tag = 'KeyIdentifierType'
    c_namespace = NAMESPACE
    c_children = EncodedString_.c_children.copy()
    c_attributes = EncodedString_.c_attributes.copy()
    c_child_order = EncodedString_.c_child_order[:]
    c_cardinality = EncodedString_.c_cardinality.copy()
    c_attributes['ValueType'] = ('value_type', 'anyURI', False)

    def __init__(self,
            value_type=None,
            encoding_type=None,
            Id=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        EncodedString_.__init__(self, 
                encoding_type=encoding_type,
                Id=Id,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.value_type=value_type

def key_identifier_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyIdentifierType_, xml_string)

class TUsage_(SamlBase):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:tUsage element """

    c_tag = 'tUsage'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()

def t_usage__from_string(xml_string):
    return saml2.create_class_from_xml_string(TUsage_, xml_string)

class ReferenceType_(SamlBase):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:ReferenceType element """

    c_tag = 'ReferenceType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['URI'] = ('uri', 'anyURI', False)
    c_attributes['ValueType'] = ('value_type', 'anyURI', False)

    def __init__(self,
            uri=None,
            value_type=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        SamlBase.__init__(self, 
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.uri=uri
        self.value_type=value_type

def reference_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ReferenceType_, xml_string)

class EmbeddedType_(SamlBase):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:EmbeddedType element """

    c_tag = 'EmbeddedType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['ValueType'] = ('value_type', 'anyURI', False)

    def __init__(self,
            value_type=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        SamlBase.__init__(self, 
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.value_type=value_type

def embedded_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(EmbeddedType_, xml_string)

class SecurityTokenReferenceType_(SamlBase):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:SecurityTokenReferenceType element """

    c_tag = 'SecurityTokenReferenceType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id'] = ('Id', 'None', False)
    c_attributes['Usage'] = ('Usage', 'None', False)

    def __init__(self,
            Id=None,
            Usage=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        SamlBase.__init__(self, 
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.Id=Id
        self.Usage=Usage

def security_token_reference_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SecurityTokenReferenceType_, xml_string)

class SecurityHeaderType_(SamlBase):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:SecurityHeaderType element """

    c_tag = 'SecurityHeaderType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()

def security_header_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SecurityHeaderType_, xml_string)

class TransformationParametersType_(SamlBase):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:TransformationParametersType element """

    c_tag = 'TransformationParametersType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()

def transformation_parameters_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(TransformationParametersType_, xml_string)

class UsernameToken(UsernameTokenType_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:UsernameToken element """

    c_tag = 'UsernameToken'
    c_namespace = NAMESPACE
    c_children = UsernameTokenType_.c_children.copy()
    c_attributes = UsernameTokenType_.c_attributes.copy()
    c_child_order = UsernameTokenType_.c_child_order[:]
    c_cardinality = UsernameTokenType_.c_cardinality.copy()

def username_token_from_string(xml_string):
    return saml2.create_class_from_xml_string(UsernameToken, xml_string)

class BinarySecurityToken(BinarySecurityTokenType_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:BinarySecurityToken element """

    c_tag = 'BinarySecurityToken'
    c_namespace = NAMESPACE
    c_children = BinarySecurityTokenType_.c_children.copy()
    c_attributes = BinarySecurityTokenType_.c_attributes.copy()
    c_child_order = BinarySecurityTokenType_.c_child_order[:]
    c_cardinality = BinarySecurityTokenType_.c_cardinality.copy()

def binary_security_token_from_string(xml_string):
    return saml2.create_class_from_xml_string(BinarySecurityToken, xml_string)


class Reference(ReferenceType_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:Reference element """

    c_tag = 'Reference'
    c_namespace = NAMESPACE
    c_children = ReferenceType_.c_children.copy()
    c_attributes = ReferenceType_.c_attributes.copy()
    c_child_order = ReferenceType_.c_child_order[:]
    c_cardinality = ReferenceType_.c_cardinality.copy()

def reference_from_string(xml_string):
    return saml2.create_class_from_xml_string(Reference, xml_string)


class Embedded(EmbeddedType_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:Embedded element """

    c_tag = 'Embedded'
    c_namespace = NAMESPACE
    c_children = EmbeddedType_.c_children.copy()
    c_attributes = EmbeddedType_.c_attributes.copy()
    c_child_order = EmbeddedType_.c_child_order[:]
    c_cardinality = EmbeddedType_.c_cardinality.copy()

def embedded_from_string(xml_string):
    return saml2.create_class_from_xml_string(Embedded, xml_string)


class KeyIdentifier(KeyIdentifierType_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:KeyIdentifier element """

    c_tag = 'KeyIdentifier'
    c_namespace = NAMESPACE
    c_children = KeyIdentifierType_.c_children.copy()
    c_attributes = KeyIdentifierType_.c_attributes.copy()
    c_child_order = KeyIdentifierType_.c_child_order[:]
    c_cardinality = KeyIdentifierType_.c_cardinality.copy()

def key_identifier_from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyIdentifier, xml_string)


class SecurityTokenReference(SecurityTokenReferenceType_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:SecurityTokenReference element """

    c_tag = 'SecurityTokenReference'
    c_namespace = NAMESPACE
    c_children = SecurityTokenReferenceType_.c_children.copy()
    c_attributes = SecurityTokenReferenceType_.c_attributes.copy()
    c_child_order = SecurityTokenReferenceType_.c_child_order[:]
    c_cardinality = SecurityTokenReferenceType_.c_cardinality.copy()

def security_token_reference_from_string(xml_string):
    return saml2.create_class_from_xml_string(SecurityTokenReference, xml_string)


class Security(SecurityHeaderType_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:Security element """

    c_tag = 'Security'
    c_namespace = NAMESPACE
    c_children = SecurityHeaderType_.c_children.copy()
    c_attributes = SecurityHeaderType_.c_attributes.copy()
    c_child_order = SecurityHeaderType_.c_child_order[:]
    c_cardinality = SecurityHeaderType_.c_cardinality.copy()

def security_from_string(xml_string):
    return saml2.create_class_from_xml_string(Security, xml_string)


class TransformationParameters(TransformationParametersType_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:TransformationParameters element """

    c_tag = 'TransformationParameters'
    c_namespace = NAMESPACE
    c_children = TransformationParametersType_.c_children.copy()
    c_attributes = TransformationParametersType_.c_attributes.copy()
    c_child_order = TransformationParametersType_.c_child_order[:]
    c_cardinality = TransformationParametersType_.c_cardinality.copy()

def transformation_parameters_from_string(xml_string):
    return saml2.create_class_from_xml_string(TransformationParameters, xml_string)


class Password(PasswordString_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:Password element """

    c_tag = 'Password'
    c_namespace = NAMESPACE
    c_children = PasswordString_.c_children.copy()
    c_attributes = PasswordString_.c_attributes.copy()
    c_child_order = PasswordString_.c_child_order[:]
    c_cardinality = PasswordString_.c_cardinality.copy()

def password_from_string(xml_string):
    return saml2.create_class_from_xml_string(Password, xml_string)


class Nonce(EncodedString_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:Nonce element """

    c_tag = 'Nonce'
    c_namespace = NAMESPACE
    c_children = EncodedString_.c_children.copy()
    c_attributes = EncodedString_.c_attributes.copy()
    c_child_order = EncodedString_.c_child_order[:]
    c_cardinality = EncodedString_.c_cardinality.copy()

def nonce_from_string(xml_string):
    return saml2.create_class_from_xml_string(Nonce, xml_string)


class FaultcodeEnum_(SamlBase):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd:FaultcodeEnum element """

    c_tag = 'FaultcodeEnum'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'xsd:QName', 'enumeration': ['wsse:UnsupportedSecurityToken', 'wsse:UnsupportedAlgorithm', 'wsse:InvalidSecurity', 'wsse:InvalidSecurityToken', 'wsse:FailedAuthentication', 'wsse:FailedCheck', 'wsse:SecurityTokenUnavailable']}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()

def faultcode_enum__from_string(xml_string):
    return saml2.create_class_from_xml_string(FaultcodeEnum_, xml_string)


#..................
('#', [])
ELEMENT_FROM_STRING = {
    AttributedString_.c_tag: attributed_string__from_string,
    PasswordString_.c_tag: password_string__from_string,
    EncodedString_.c_tag: encoded_string__from_string,
    UsernameTokenType_.c_tag: username_token_type__from_string,
    BinarySecurityTokenType_.c_tag: binary_security_token_type__from_string,
    KeyIdentifierType_.c_tag: key_identifier_type__from_string,
    TUsage_.c_tag: t_usage__from_string,
    ReferenceType_.c_tag: reference_type__from_string,
    EmbeddedType_.c_tag: embedded_type__from_string,
    SecurityTokenReferenceType_.c_tag: security_token_reference_type__from_string,
    SecurityHeaderType_.c_tag: security_header_type__from_string,
    TransformationParametersType_.c_tag: transformation_parameters_type__from_string,
    UsernameToken.c_tag: username_token_from_string,
    BinarySecurityToken.c_tag: binary_security_token_from_string,
    Reference.c_tag: reference_from_string,
    Embedded.c_tag: embedded_from_string,
    KeyIdentifier.c_tag: key_identifier_from_string,
    SecurityTokenReference.c_tag: security_token_reference_from_string,
    Security.c_tag: security_from_string,
    TransformationParameters.c_tag: transformation_parameters_from_string,
    Password.c_tag: password_from_string,
    Nonce.c_tag: nonce_from_string,
    FaultcodeEnum_.c_tag: faultcode_enum__from_string,
    UsernameTokenType_Username.c_tag: username_token_type__username_from_string,
}

ELEMENT_BY_TAG = {
    'AttributedString': AttributedString_,
    'PasswordString': PasswordString_,
    'EncodedString': EncodedString_,
    'UsernameTokenType': UsernameTokenType_,
    'BinarySecurityTokenType': BinarySecurityTokenType_,
    'KeyIdentifierType': KeyIdentifierType_,
    'tUsage': TUsage_,
    'ReferenceType': ReferenceType_,
    'EmbeddedType': EmbeddedType_,
    'SecurityTokenReferenceType': SecurityTokenReferenceType_,
    'SecurityHeaderType': SecurityHeaderType_,
    'TransformationParametersType': TransformationParametersType_,
    'UsernameToken': UsernameToken,
    'BinarySecurityToken': BinarySecurityToken,
    'Reference': Reference,
    'Embedded': Embedded,
    'KeyIdentifier': KeyIdentifier,
    'SecurityTokenReference': SecurityTokenReference,
    'Security': Security,
    'TransformationParameters': TransformationParameters,
    'Password': Password,
    'Nonce': Nonce,
    'FaultcodeEnum': FaultcodeEnum_,
    'Username': UsernameTokenType_Username,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)

