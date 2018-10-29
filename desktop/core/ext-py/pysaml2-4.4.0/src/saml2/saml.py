#!/usr/bin/env python

#
# Generated Mon May  2 14:23:33 2011 by parse_xsd.py version 0.4.
#
from saml2.validate import valid_ipv4, MustValueError
from saml2.validate import valid_ipv6
from saml2.validate import ShouldValueError
from saml2.validate import valid_domain_name

import saml2
from saml2 import SamlBase

import six
from saml2 import xmldsig as ds
from saml2 import xmlenc as xenc

NAMESPACE = 'urn:oasis:names:tc:SAML:2.0:assertion'

XSI_NAMESPACE = 'http://www.w3.org/2001/XMLSchema-instance'
XS_NAMESPACE = 'http://www.w3.org/2001/XMLSchema'

XSI_TYPE = '{%s}type' % XSI_NAMESPACE
XSI_NIL = '{%s}nil' % XSI_NAMESPACE

NAMEID_FORMAT_EMAILADDRESS = (
    "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress")
NAMEID_FORMAT_UNSPECIFIED1 = (
    "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified")
NAMEID_FORMAT_UNSPECIFIED = (
    "urn:oasis:names:tc:SAML:2.0:nameid-format:unspecified")
NAMEID_FORMAT_ENCRYPTED = (
    "urn:oasis:names:tc:SAML:2.0:nameid-format:encrypted")
NAMEID_FORMAT_PERSISTENT = (
    "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent")
NAMEID_FORMAT_TRANSIENT = (
    "urn:oasis:names:tc:SAML:2.0:nameid-format:transient")
NAMEID_FORMAT_ENTITY = (
    "urn:oasis:names:tc:SAML:2.0:nameid-format:entity")
NAMEID_FORMATS_SAML2 = (
    ('NAMEID_FORMAT_EMAILADDRESS', NAMEID_FORMAT_EMAILADDRESS),
    ('NAMEID_FORMAT_ENCRYPTED', NAMEID_FORMAT_ENCRYPTED),
    ('NAMEID_FORMAT_ENTITY', NAMEID_FORMAT_ENTITY),
    ('NAMEID_FORMAT_PERSISTENT', NAMEID_FORMAT_PERSISTENT),
    ('NAMEID_FORMAT_TRANSIENT', NAMEID_FORMAT_TRANSIENT),
    ('NAMEID_FORMAT_UNSPECIFIED', NAMEID_FORMAT_UNSPECIFIED),
)
PROFILE_ATTRIBUTE_BASIC = (
    "urn:oasis:names:tc:SAML:2.0:profiles:attribute:basic")

AUTHN_PASSWORD = "urn:oasis:names:tc:SAML:2.0:ac:classes:Password"
AUTHN_PASSWORD_PROTECTED = \
    "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport"

NAME_FORMAT_UNSPECIFIED = (
    "urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified")
NAME_FORMAT_URI = "urn:oasis:names:tc:SAML:2.0:attrname-format:uri"
NAME_FORMAT_BASIC = "urn:oasis:names:tc:SAML:2.0:attrname-format:basic"
NAME_FORMATS_SAML2 = (
    ('NAME_FORMAT_BASIC', NAME_FORMAT_BASIC),
    ('NAME_FORMAT_URI', NAME_FORMAT_URI),
    ('NAME_FORMAT_UNSPECIFIED', NAME_FORMAT_UNSPECIFIED),
)
DECISION_TYPE_PERMIT = "Permit"
DECISION_TYPE_DENY = "Deny"
DECISION_TYPE_INDETERMINATE = "Indeterminate"

CONSENT_UNSPECIFIED = "urn:oasis:names:tc:SAML:2.0:consent:unspecified"
CONSENT_OBTAINED = "urn:oasis:names:tc:SAML:2.0:consent:obtained"
CONSENT_PRIOR = "urn:oasis:names:tc:SAML:2.0:consent:prior"
CONSENT_IMPLICIT = "urn:oasis:names:tc:SAML:2.0:consent:current-implicit"
CONSENT_EXPLICIT = "urn:oasis:names:tc:SAML:2.0:consent:current-explicit"
CONSENT_UNAVAILABLE = "urn:oasis:names:tc:SAML:2.0:consent:unavailable"
CONSENT_INAPPLICABLE = "urn:oasis:names:tc:SAML:2.0:consent:inapplicable"

SCM_HOLDER_OF_KEY = "urn:oasis:names:tc:SAML:2.0:cm:holder-of-key"
SCM_SENDER_VOUCHES = "urn:oasis:names:tc:SAML:2.0:cm:sender-vouches"
SCM_BEARER = "urn:oasis:names:tc:SAML:2.0:cm:bearer"

# -----------------------------------------------------------------------------
XSD = "xs:"
NS_SOAP_ENC = "http://schemas.xmlsoap.org/soap/encoding/"

# -----------------------------------------------------------------------------


def _decode_attribute_value(typ, text):
    if typ == XSD + "string":
        return text or ""
    if typ == XSD + "integer" or typ == XSD + "int":
        return str(int(text))
    if typ == XSD + "float" or typ == XSD + "double":
        return str(float(text))
    if typ == XSD + "boolean":
        return "%s" % (text == "true" or text == "True")
    if typ == XSD + "base64Binary":
        import base64

        return base64.decodestring(text)
    raise ValueError("type %s not supported" % type)


def _verify_value_type(typ, val):
    #  print("verify value type: %s, %s" % (typ, val))
    if typ == XSD + "string":
        try:
            return str(val)
        except UnicodeEncodeError:
            if six.PY2:
                return unicode(val)
            else:
                return val.decode('utf8')
    if typ == XSD + "integer" or typ == XSD + "int":
        return int(val)
    if typ == XSD + "float" or typ == XSD + "double":
        return float(val)
    if typ == XSD + "boolean":
        if val.lower() == "true" or val.lower() == "false":
            pass
        else:
            raise ValueError("Faulty boolean value")
    if typ == XSD + "base64Binary":
        import base64

        return base64.decodestring(val.encode('utf-8'))


class AttributeValueBase(SamlBase):
    def __init__(self,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        self._extatt = {}

        SamlBase.__init__(self,
                          text=None,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        if self._extatt:
            self.extension_attributes = self._extatt

        if not text:
            self.extension_attributes = {XSI_NIL: 'true'}
        else:
            self.set_text(text)

    def __setattr__(self, key, value):
        if key == "text":
            self.set_text(value)
        else:
            SamlBase.__setattr__(self, key, value)

    def verify(self):
        if not self.text:
            assert self.extension_attributes
            assert self.extension_attributes[XSI_NIL] == "true"
            return True
        else:
            SamlBase.verify(self)

    def set_type(self, typ):
        try:
            del self.extension_attributes[XSI_NIL]
        except KeyError:
            pass

        try:
            self.extension_attributes[XSI_TYPE] = typ
        except AttributeError:
            self._extatt[XSI_TYPE] = typ

        if typ.startswith('xs:'):
            try:
                self.extension_attributes['xmlns:xs'] = XS_NAMESPACE
            except AttributeError:
                self._extatt['xmlns:xs'] = XS_NAMESPACE


    def get_type(self):
        try:
            return self.extension_attributes[XSI_TYPE]
        except (KeyError, AttributeError):
            try:
                return self._extatt[XSI_TYPE]
            except KeyError:
                return ""

    def clear_type(self):
        try:
            del self.extension_attributes[XSI_TYPE]
        except KeyError:
            pass
        try:
            del self._extatt[XSI_TYPE]
        except KeyError:
            pass

    def set_text(self, val, base64encode=False):
        typ = self.get_type()
        if base64encode:
            import base64

            val = base64.encodestring(val)
            self.set_type("xs:base64Binary")
        else:
            if isinstance(val, six.binary_type):
                val = val.decode('utf-8')
            if isinstance(val, six.string_types):
                if not typ:
                    self.set_type("xs:string")
                else:
                    try:
                        assert typ == "xs:string"
                    except AssertionError:
                        if typ == "xs:int":
                            _ = int(val)
                        elif typ == "xs:boolean":
                            if val.lower() not in ["true", "false"]:
                                raise ValueError("Not a boolean")
                        elif typ == "xs:float":
                            _ = float(val)
                        elif typ == "xs:base64Binary":
                            pass
                        else:
                            ValueError("Type and value doesn't match")
            elif isinstance(val, bool):
                if val:
                    val = "true"
                else:
                    val = "false"
                if not typ:
                    self.set_type("xs:boolean")
                else:
                    assert typ == "xs:boolean"
            elif isinstance(val, int):
                val = str(val)
                if not typ:
                    self.set_type("xs:integer")
                else:
                    assert typ == "xs:integer"
            elif isinstance(val, float):
                val = str(val)
                if not typ:
                    self.set_type("xs:float")
                else:
                    assert typ == "xs:float"
            elif not val:
                try:
                    self.extension_attributes[XSI_TYPE] = typ
                except AttributeError:
                    self._extatt[XSI_TYPE] = typ
                val = ""
            else:
                if typ == "xs:anyType":
                    pass
                else:
                    raise ValueError

        SamlBase.__setattr__(self, "text", val)
        return self

    def harvest_element_tree(self, tree):
        # Fill in the instance members from the contents of the XML tree.
        for child in tree:
            self._convert_element_tree_to_member(child)
        for attribute, value in iter(tree.attrib.items()):
            self._convert_element_attribute_to_member(attribute, value)
        if tree.text:
            #print("set_text:", tree.text)
            # clear type
            #self.clear_type()
            self.set_text(tree.text)
            if XSI_NIL in self.extension_attributes:
                del self.extension_attributes[XSI_NIL]
            try:
                typ = self.extension_attributes[XSI_TYPE]
                _verify_value_type(typ, getattr(self, "text"))
            except KeyError:
                pass


class BaseIDAbstractType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:BaseIDAbstractType element """

    c_tag = 'BaseIDAbstractType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['NameQualifier'] = ('name_qualifier', 'string', False)
    c_attributes['SPNameQualifier'] = ('sp_name_qualifier', 'string', False)

    def __init__(self,
                 name_qualifier=None,
                 sp_name_qualifier=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.name_qualifier = name_qualifier
        self.sp_name_qualifier = sp_name_qualifier


class NameIDType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:NameIDType element """

    c_tag = 'NameIDType'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'string'}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['NameQualifier'] = ('name_qualifier', 'string', False)
    c_attributes['SPNameQualifier'] = ('sp_name_qualifier', 'string', False)
    c_attributes['Format'] = ('format', 'anyURI', False)
    c_attributes['SPProvidedID'] = ('sp_provided_id', 'string', False)

    def __init__(self,
                 name_qualifier=None,
                 sp_name_qualifier=None,
                 format=None,
                 sp_provided_id=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.name_qualifier = name_qualifier
        self.sp_name_qualifier = sp_name_qualifier
        self.format = format
        self.sp_provided_id = sp_provided_id


def name_id_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(NameIDType_, xml_string)


class EncryptedElementType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:EncryptedElementType element
    """

    c_tag = 'EncryptedElementType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{http://www.w3.org/2001/04/xmlenc#}EncryptedData'] = (
        'encrypted_data',
        xenc.EncryptedData)
    c_children['{http://www.w3.org/2001/04/xmlenc#}EncryptedKey'] = (
        'encrypted_key',
        [xenc.EncryptedKey])
    c_cardinality['encrypted_key'] = {"min": 0}
    c_child_order.extend(['encrypted_data', 'encrypted_key'])

    def __init__(self,
                 encrypted_data=None,
                 encrypted_key=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.encrypted_data = encrypted_data
        self.encrypted_key = encrypted_key or []


def encrypted_element_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(EncryptedElementType_, xml_string)


class EncryptedID(EncryptedElementType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:EncryptedID element """

    c_tag = 'EncryptedID'
    c_namespace = NAMESPACE
    c_children = EncryptedElementType_.c_children.copy()
    c_attributes = EncryptedElementType_.c_attributes.copy()
    c_child_order = EncryptedElementType_.c_child_order[:]
    c_cardinality = EncryptedElementType_.c_cardinality.copy()


def encrypted_id_from_string(xml_string):
    return saml2.create_class_from_xml_string(EncryptedID, xml_string)


class Issuer(NameIDType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:Issuer element """

    c_tag = 'Issuer'
    c_namespace = NAMESPACE
    c_children = NameIDType_.c_children.copy()
    c_attributes = NameIDType_.c_attributes.copy()
    c_child_order = NameIDType_.c_child_order[:]
    c_cardinality = NameIDType_.c_cardinality.copy()


def issuer_from_string(xml_string):
    return saml2.create_class_from_xml_string(Issuer, xml_string)


class AssertionIDRef(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AssertionIDRef element """

    c_tag = 'AssertionIDRef'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'NCName'}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def assertion_id_ref_from_string(xml_string):
    return saml2.create_class_from_xml_string(AssertionIDRef, xml_string)


class AssertionURIRef(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AssertionURIRef element """

    c_tag = 'AssertionURIRef'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'anyURI'}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def assertion_uri_ref_from_string(xml_string):
    return saml2.create_class_from_xml_string(AssertionURIRef, xml_string)


class SubjectConfirmationDataType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:SubjectConfirmationDataType
    element """

    c_tag = 'SubjectConfirmationDataType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['NotBefore'] = ('not_before', 'dateTime', False)
    c_attributes['NotOnOrAfter'] = ('not_on_or_after', 'dateTime', False)
    c_attributes['Recipient'] = ('recipient', 'anyURI', False)
    c_attributes['InResponseTo'] = ('in_response_to', 'NCName', False)
    c_attributes['Address'] = ('address', 'string', False)
    c_any = {"namespace": "##any", "processContents": "lax", "minOccurs": "0",
             "maxOccurs": "unbounded"}
    c_any_attribute = {"namespace": "##other", "processContents": "lax"}

    def __init__(self,
                 not_before=None,
                 not_on_or_after=None,
                 recipient=None,
                 in_response_to=None,
                 address=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.not_before = not_before
        self.not_on_or_after = not_on_or_after
        self.recipient = recipient
        self.in_response_to = in_response_to
        self.address = address


def subject_confirmation_data_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SubjectConfirmationDataType_,
                                              xml_string)


class KeyInfoConfirmationDataType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:KeyInfoConfirmationDataType
    element """

    c_tag = 'KeyInfoConfirmationDataType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{http://www.w3.org/2000/09/xmldsig#}KeyInfo'] = ('key_info',
                                                                 [ds.KeyInfo])
    c_cardinality['key_info'] = {"min": 1}
    c_child_order.extend(['key_info'])

    def __init__(self,
                 key_info=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.key_info = key_info or []


def key_info_confirmation_data_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyInfoConfirmationDataType_,
                                              xml_string)


class ConditionAbstractType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:ConditionAbstractType
    element """

    c_tag = 'ConditionAbstractType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


class Audience(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:Audience element """

    c_tag = 'Audience'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'anyURI'}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def audience_from_string(xml_string):
    return saml2.create_class_from_xml_string(Audience, xml_string)


class OneTimeUseType_(ConditionAbstractType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:OneTimeUseType element """

    c_tag = 'OneTimeUseType'
    c_namespace = NAMESPACE
    c_children = ConditionAbstractType_.c_children.copy()
    c_attributes = ConditionAbstractType_.c_attributes.copy()
    c_child_order = ConditionAbstractType_.c_child_order[:]
    c_cardinality = ConditionAbstractType_.c_cardinality.copy()


def one_time_use_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(OneTimeUseType_, xml_string)


class ProxyRestrictionType_(ConditionAbstractType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:ProxyRestrictionType element
    """

    c_tag = 'ProxyRestrictionType'
    c_namespace = NAMESPACE
    c_children = ConditionAbstractType_.c_children.copy()
    c_attributes = ConditionAbstractType_.c_attributes.copy()
    c_child_order = ConditionAbstractType_.c_child_order[:]
    c_cardinality = ConditionAbstractType_.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Audience'] = ('audience',
                                                                     [Audience])
    c_cardinality['audience'] = {"min": 0}
    c_attributes['Count'] = ('count', 'nonNegativeInteger', False)
    c_child_order.extend(['audience'])

    def __init__(self,
                 audience=None,
                 count=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        ConditionAbstractType_.__init__(
            self, text=text, extension_elements=extension_elements,
            extension_attributes=extension_attributes)
        self.audience = audience or []
        self.count = count


def proxy_restriction_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ProxyRestrictionType_, xml_string)


class EncryptedAssertion(EncryptedElementType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:EncryptedAssertion element """

    c_tag = 'EncryptedAssertion'
    c_namespace = NAMESPACE
    c_children = EncryptedElementType_.c_children.copy()
    c_attributes = EncryptedElementType_.c_attributes.copy()
    c_child_order = EncryptedElementType_.c_child_order[:]
    c_cardinality = EncryptedElementType_.c_cardinality.copy()


def encrypted_assertion_from_string(xml_string):
    return saml2.create_class_from_xml_string(EncryptedAssertion, xml_string)


class StatementAbstractType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:StatementAbstractType element
    """

    c_tag = 'StatementAbstractType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


class SubjectLocalityType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:SubjectLocalityType element """

    c_tag = 'SubjectLocalityType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['Address'] = ('address', 'string', False)
    c_attributes['DNSName'] = ('dns_name', 'string', False)

    def __init__(self,
                 address=None,
                 dns_name=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.address = address
        self.dns_name = dns_name


def subject_locality_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SubjectLocalityType_, xml_string)


class AuthnContextClassRef(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AuthnContextClassRef element
    """

    c_tag = 'AuthnContextClassRef'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'anyURI'}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def authn_context_class_ref_from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthnContextClassRef, xml_string)


class AuthnContextDeclRef(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AuthnContextDeclRef element """

    c_tag = 'AuthnContextDeclRef'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'anyURI'}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def authn_context_decl_ref_from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthnContextDeclRef, xml_string)


class AuthnContextDecl(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AuthnContextDecl element """

    c_tag = 'AuthnContextDecl'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'anyType'}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def authn_context_decl_from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthnContextDecl, xml_string)


class AuthenticatingAuthority(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AuthenticatingAuthority
    element """

    c_tag = 'AuthenticatingAuthority'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'anyURI'}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def authenticating_authority_from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthenticatingAuthority,
                                              xml_string)


class DecisionType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:DecisionType element """

    c_tag = 'DecisionType'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'string', 'enumeration': ['Permit', 'Deny',
                                                      'Indeterminate']}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def decision_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(DecisionType_, xml_string)


class ActionType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:ActionType element """

    c_tag = 'ActionType'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'string'}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['Namespace'] = ('namespace', 'anyURI', True)

    def __init__(self,
                 namespace=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.namespace = namespace


def action_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ActionType_, xml_string)


class AttributeValue(AttributeValueBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AttributeValue element """

    c_tag = 'AttributeValue'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'anyType'}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def attribute_value_from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributeValue, xml_string)


class EncryptedAttribute(EncryptedElementType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:EncryptedAttribute element """

    c_tag = 'EncryptedAttribute'
    c_namespace = NAMESPACE
    c_children = EncryptedElementType_.c_children.copy()
    c_attributes = EncryptedElementType_.c_attributes.copy()
    c_child_order = EncryptedElementType_.c_child_order[:]
    c_cardinality = EncryptedElementType_.c_cardinality.copy()


def encrypted_attribute_from_string(xml_string):
    return saml2.create_class_from_xml_string(EncryptedAttribute, xml_string)


class BaseID(BaseIDAbstractType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:BaseID element """

    c_tag = 'BaseID'
    c_namespace = NAMESPACE
    c_children = BaseIDAbstractType_.c_children.copy()
    c_attributes = BaseIDAbstractType_.c_attributes.copy()
    c_child_order = BaseIDAbstractType_.c_child_order[:]
    c_cardinality = BaseIDAbstractType_.c_cardinality.copy()


def base_id_from_string(xml_string):
    return saml2.create_class_from_xml_string(BaseID, xml_string)


class NameID(NameIDType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:NameID element """

    c_tag = 'NameID'
    c_namespace = NAMESPACE
    c_children = NameIDType_.c_children.copy()
    c_attributes = NameIDType_.c_attributes.copy()
    c_child_order = NameIDType_.c_child_order[:]
    c_cardinality = NameIDType_.c_cardinality.copy()


def name_id_from_string(xml_string):
    return saml2.create_class_from_xml_string(NameID, xml_string)


class SubjectConfirmationData(SubjectConfirmationDataType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:SubjectConfirmationData
    element """

    c_tag = 'SubjectConfirmationData'
    c_namespace = NAMESPACE
    c_children = SubjectConfirmationDataType_.c_children.copy()
    c_attributes = SubjectConfirmationDataType_.c_attributes.copy()
    c_child_order = SubjectConfirmationDataType_.c_child_order[:]
    c_cardinality = SubjectConfirmationDataType_.c_cardinality.copy()


def subject_confirmation_data_from_string(xml_string):
    return saml2.create_class_from_xml_string(SubjectConfirmationData,
                                              xml_string)


class Condition(ConditionAbstractType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:Condition element """

    c_tag = 'Condition'
    c_namespace = NAMESPACE
    c_children = ConditionAbstractType_.c_children.copy()
    c_attributes = ConditionAbstractType_.c_attributes.copy()
    c_child_order = ConditionAbstractType_.c_child_order[:]
    c_cardinality = ConditionAbstractType_.c_cardinality.copy()


def condition_from_string(xml_string):
    return saml2.create_class_from_xml_string(Condition, xml_string)


class AudienceRestrictionType_(ConditionAbstractType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AudienceRestrictionType
    element """

    c_tag = 'AudienceRestrictionType'
    c_namespace = NAMESPACE
    c_children = ConditionAbstractType_.c_children.copy()
    c_attributes = ConditionAbstractType_.c_attributes.copy()
    c_child_order = ConditionAbstractType_.c_child_order[:]
    c_cardinality = ConditionAbstractType_.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Audience'] = ('audience',
                                                                     [Audience])
    c_cardinality['audience'] = {"min": 1}
    c_child_order.extend(['audience'])

    def __init__(self,
                 audience=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        ConditionAbstractType_.__init__(
            self, text=text, extension_elements=extension_elements,
            extension_attributes=extension_attributes)
        self.audience = audience or []


def audience_restriction_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AudienceRestrictionType_,
                                              xml_string)


class OneTimeUse(OneTimeUseType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:OneTimeUse element """

    c_tag = 'OneTimeUse'
    c_namespace = NAMESPACE
    c_children = OneTimeUseType_.c_children.copy()
    c_attributes = OneTimeUseType_.c_attributes.copy()
    c_child_order = OneTimeUseType_.c_child_order[:]
    c_cardinality = OneTimeUseType_.c_cardinality.copy()


def one_time_use_from_string(xml_string):
    return saml2.create_class_from_xml_string(OneTimeUse, xml_string)


class ProxyRestriction(ProxyRestrictionType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:ProxyRestriction element """

    c_tag = 'ProxyRestriction'
    c_namespace = NAMESPACE
    c_children = ProxyRestrictionType_.c_children.copy()
    c_attributes = ProxyRestrictionType_.c_attributes.copy()
    c_child_order = ProxyRestrictionType_.c_child_order[:]
    c_cardinality = ProxyRestrictionType_.c_cardinality.copy()


def proxy_restriction_from_string(xml_string):
    return saml2.create_class_from_xml_string(ProxyRestriction, xml_string)


class Statement(StatementAbstractType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:Statement element """

    c_tag = 'Statement'
    c_namespace = NAMESPACE
    c_children = StatementAbstractType_.c_children.copy()
    c_attributes = StatementAbstractType_.c_attributes.copy()
    c_child_order = StatementAbstractType_.c_child_order[:]
    c_cardinality = StatementAbstractType_.c_cardinality.copy()


def statement_from_string(xml_string):
    return saml2.create_class_from_xml_string(Statement, xml_string)


class SubjectLocality(SubjectLocalityType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:SubjectLocality element """

    c_tag = 'SubjectLocality'
    c_namespace = NAMESPACE
    c_children = SubjectLocalityType_.c_children.copy()
    c_attributes = SubjectLocalityType_.c_attributes.copy()
    c_child_order = SubjectLocalityType_.c_child_order[:]
    c_cardinality = SubjectLocalityType_.c_cardinality.copy()

    def verify(self):
        if self.address:
            # dotted-decimal IPv4 or RFC3513 IPv6 address
            if valid_ipv4(self.address) or valid_ipv6(self.address):
                pass
            else:
                raise ShouldValueError("Not an IPv4 or IPv6 address")
        elif self.dns_name:
            valid_domain_name(self.dns_name)

        return SubjectLocalityType_.verify(self)


def subject_locality_from_string(xml_string):
    return saml2.create_class_from_xml_string(SubjectLocality, xml_string)


class AuthnContextType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AuthnContextType element """

    c_tag = 'AuthnContextType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:assertion}AuthnContextClassRef'] = (
            'authn_context_class_ref', AuthnContextClassRef)
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}AuthnContextDecl'] = (
        'authn_context_decl',
        AuthnContextDecl)
    c_cardinality['authn_context_decl'] = {"min": 0, "max": 1}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}AuthnContextDeclRef'] = (
        'authn_context_decl_ref',
        AuthnContextDeclRef)
    c_cardinality['authn_context_decl_ref'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:assertion}AuthenticatingAuthority'] = (
            'authenticating_authority', [AuthenticatingAuthority])
    c_cardinality['authenticating_authority'] = {"min": 0}
    c_child_order.extend(['authn_context_class_ref', 'authn_context_decl',
                          'authn_context_decl_ref', 'authenticating_authority'])

    def __init__(self,
                 authn_context_class_ref=None,
                 authn_context_decl=None,
                 authn_context_decl_ref=None,
                 authenticating_authority=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.authn_context_class_ref = authn_context_class_ref
        self.authn_context_decl = authn_context_decl
        self.authn_context_decl_ref = authn_context_decl_ref
        self.authenticating_authority = authenticating_authority or []

    def verify(self):
        # either <AuthnContextDecl> or <AuthnContextDeclRef> not both
        if self.authn_context_decl:
            assert self.authn_context_decl_ref is None
        elif self.authn_context_decl_ref:
            assert self.authn_context_decl is None

        return SamlBase.verify(self)


def authn_context_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthnContextType_, xml_string)


class Action(ActionType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:Action element """

    c_tag = 'Action'
    c_namespace = NAMESPACE
    c_children = ActionType_.c_children.copy()
    c_attributes = ActionType_.c_attributes.copy()
    c_child_order = ActionType_.c_child_order[:]
    c_cardinality = ActionType_.c_cardinality.copy()


def action_from_string(xml_string):
    return saml2.create_class_from_xml_string(Action, xml_string)


class AttributeType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AttributeType element """

    c_tag = 'AttributeType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'] = (
        'attribute_value',
        [AttributeValue])
    c_cardinality['attribute_value'] = {"min": 0}
    c_attributes['Name'] = ('name', 'string', True)
    c_attributes['NameFormat'] = ('name_format', 'anyURI', False)
    c_attributes['FriendlyName'] = ('friendly_name', 'string', False)
    c_child_order.extend(['attribute_value'])
    c_any_attribute = {"namespace": "##other", "processContents": "lax"}

    def __init__(self,
                 attribute_value=None,
                 name=None,
                 name_format=NAME_FORMAT_URI,
                 friendly_name=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.attribute_value = attribute_value or []
        self.name = name
        self.name_format = name_format
        self.friendly_name = friendly_name


def attribute_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributeType_, xml_string)


class SubjectConfirmationType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:SubjectConfirmationType
    element """

    c_tag = 'SubjectConfirmationType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}BaseID'] = ('base_id',
                                                                   BaseID)
    c_cardinality['base_id'] = {"min": 0, "max": 1}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}NameID'] = ('name_id',
                                                                   NameID)
    c_cardinality['name_id'] = {"min": 0, "max": 1}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}EncryptedID'] = (
        'encrypted_id',
        EncryptedID)
    c_cardinality['encrypted_id'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmationData'] = (
            'subject_confirmation_data', SubjectConfirmationData)
    c_cardinality['subject_confirmation_data'] = {"min": 0, "max": 1}
    c_attributes['Method'] = ('method', 'anyURI', True)
    c_child_order.extend(['base_id', 'name_id', 'encrypted_id',
                          'subject_confirmation_data'])

    def __init__(self,
                 base_id=None,
                 name_id=None,
                 encrypted_id=None,
                 subject_confirmation_data=None,
                 method=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.base_id = base_id
        self.name_id = name_id
        self.encrypted_id = encrypted_id
        self.subject_confirmation_data = subject_confirmation_data
        self.method = method


def subject_confirmation_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SubjectConfirmationType_,
                                              xml_string)


class AudienceRestriction(AudienceRestrictionType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AudienceRestriction element """

    c_tag = 'AudienceRestriction'
    c_namespace = NAMESPACE
    c_children = AudienceRestrictionType_.c_children.copy()
    c_attributes = AudienceRestrictionType_.c_attributes.copy()
    c_child_order = AudienceRestrictionType_.c_child_order[:]
    c_cardinality = AudienceRestrictionType_.c_cardinality.copy()


def audience_restriction_from_string(xml_string):
    return saml2.create_class_from_xml_string(AudienceRestriction, xml_string)


class AuthnContext(AuthnContextType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AuthnContext element """

    c_tag = 'AuthnContext'
    c_namespace = NAMESPACE
    c_children = AuthnContextType_.c_children.copy()
    c_attributes = AuthnContextType_.c_attributes.copy()
    c_child_order = AuthnContextType_.c_child_order[:]
    c_cardinality = AuthnContextType_.c_cardinality.copy()


def authn_context_from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthnContext, xml_string)


class Attribute(AttributeType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:Attribute element """

    c_tag = 'Attribute'
    c_namespace = NAMESPACE
    c_children = AttributeType_.c_children.copy()
    c_attributes = AttributeType_.c_attributes.copy()
    c_child_order = AttributeType_.c_child_order[:]
    c_cardinality = AttributeType_.c_cardinality.copy()


def attribute_from_string(xml_string):
    return saml2.create_class_from_xml_string(Attribute, xml_string)


class SubjectConfirmation(SubjectConfirmationType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:SubjectConfirmation element """

    c_tag = 'SubjectConfirmation'
    c_namespace = NAMESPACE
    c_children = SubjectConfirmationType_.c_children.copy()
    c_attributes = SubjectConfirmationType_.c_attributes.copy()
    c_child_order = SubjectConfirmationType_.c_child_order[:]
    c_cardinality = SubjectConfirmationType_.c_cardinality.copy()


def subject_confirmation_from_string(xml_string):
    return saml2.create_class_from_xml_string(SubjectConfirmation, xml_string)


class ConditionsType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:ConditionsType element """

    c_tag = 'ConditionsType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Condition'] = (
        'condition',
        [Condition])
    c_cardinality['condition'] = {"min": 0}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}AudienceRestriction'] = (
        'audience_restriction',
        [AudienceRestriction])
    c_cardinality['audience_restriction'] = {"min": 0}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}OneTimeUse'] = (
        'one_time_use',
        [OneTimeUse])
    c_cardinality['one_time_use'] = {"min": 0}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}ProxyRestriction'] = (
        'proxy_restriction',
        [ProxyRestriction])
    c_cardinality['proxy_restriction'] = {"min": 0}
    c_attributes['NotBefore'] = ('not_before', 'dateTime', False)
    c_attributes['NotOnOrAfter'] = ('not_on_or_after', 'dateTime', False)
    c_child_order.extend(['condition', 'audience_restriction', 'one_time_use',
                          'proxy_restriction'])

    def __init__(self,
                 condition=None,
                 audience_restriction=None,
                 one_time_use=None,
                 proxy_restriction=None,
                 not_before=None,
                 not_on_or_after=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.condition = condition or []
        self.audience_restriction = audience_restriction or []
        self.one_time_use = one_time_use or []
        self.proxy_restriction = proxy_restriction or []
        self.not_before = not_before
        self.not_on_or_after = not_on_or_after

    def verify(self):
        if self.one_time_use:
            assert len(self.one_time_use) == 1
        if self.proxy_restriction:
            assert len(self.proxy_restriction) == 1

        return SamlBase.verify(self)


def conditions_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ConditionsType_, xml_string)


class AuthnStatementType_(StatementAbstractType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AuthnStatementType element """

    c_tag = 'AuthnStatementType'
    c_namespace = NAMESPACE
    c_children = StatementAbstractType_.c_children.copy()
    c_attributes = StatementAbstractType_.c_attributes.copy()
    c_child_order = StatementAbstractType_.c_child_order[:]
    c_cardinality = StatementAbstractType_.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}SubjectLocality'] = (
        'subject_locality', SubjectLocality)
    c_cardinality['subject_locality'] = {"min": 0, "max": 1}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}AuthnContext'] = (
        'authn_context', AuthnContext)
    c_attributes['AuthnInstant'] = ('authn_instant', 'dateTime', True)
    c_attributes['SessionIndex'] = ('session_index', 'string', False)
    c_attributes['SessionNotOnOrAfter'] = ('session_not_on_or_after',
                                           'dateTime', False)
    c_child_order.extend(['subject_locality', 'authn_context'])

    def __init__(self,
                 subject_locality=None,
                 authn_context=None,
                 authn_instant=None,
                 session_index=None,
                 session_not_on_or_after=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        StatementAbstractType_.__init__(
            self, text=text, extension_elements=extension_elements,
            extension_attributes=extension_attributes)
        self.subject_locality = subject_locality
        self.authn_context = authn_context
        self.authn_instant = authn_instant
        self.session_index = session_index
        self.session_not_on_or_after = session_not_on_or_after


def authn_statement_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthnStatementType_, xml_string)


class AttributeStatementType_(StatementAbstractType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AttributeStatementType
    element """

    c_tag = 'AttributeStatementType'
    c_namespace = NAMESPACE
    c_children = StatementAbstractType_.c_children.copy()
    c_attributes = StatementAbstractType_.c_attributes.copy()
    c_child_order = StatementAbstractType_.c_child_order[:]
    c_cardinality = StatementAbstractType_.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'] = (
        'attribute',
        [Attribute])
    c_cardinality['attribute'] = {"min": 0}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}EncryptedAttribute'] = (
        'encrypted_attribute',
        [EncryptedAttribute])
    c_cardinality['encrypted_attribute'] = {"min": 0}
    c_child_order.extend(['attribute', 'encrypted_attribute'])

    def __init__(self,
                 attribute=None,
                 encrypted_attribute=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        StatementAbstractType_.__init__(
            self, text=text, extension_elements=extension_elements,
            extension_attributes=extension_attributes)
        self.attribute = attribute or []
        self.encrypted_attribute = encrypted_attribute or []


def attribute_statement_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributeStatementType_,
                                              xml_string)


class SubjectType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:SubjectType element """

    c_tag = 'SubjectType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}BaseID'] = ('base_id',
                                                                   BaseID)
    c_cardinality['base_id'] = {"min": 0, "max": 1}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}NameID'] = ('name_id',
                                                                   NameID)
    c_cardinality['name_id'] = {"min": 0, "max": 1}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}EncryptedID'] = (
        'encrypted_id', EncryptedID)
    c_cardinality['encrypted_id'] = {"min": 0, "max": 1}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmation'] = (
        'subject_confirmation', [SubjectConfirmation])
    c_cardinality['subject_confirmation'] = {"min": 0}
    c_child_order.extend(['base_id', 'name_id', 'encrypted_id',
                          'subject_confirmation'])

    def __init__(self,
                 base_id=None,
                 name_id=None,
                 encrypted_id=None,
                 subject_confirmation=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.base_id = base_id
        self.name_id = name_id
        self.encrypted_id = encrypted_id
        self.subject_confirmation = subject_confirmation or []


def subject_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SubjectType_, xml_string)


class Conditions(ConditionsType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:Conditions element """

    c_tag = 'Conditions'
    c_namespace = NAMESPACE
    c_children = ConditionsType_.c_children.copy()
    c_attributes = ConditionsType_.c_attributes.copy()
    c_child_order = ConditionsType_.c_child_order[:]
    c_cardinality = ConditionsType_.c_cardinality.copy()


def conditions_from_string(xml_string):
    return saml2.create_class_from_xml_string(Conditions, xml_string)


class AuthnStatement(AuthnStatementType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AuthnStatement element """

    c_tag = 'AuthnStatement'
    c_namespace = NAMESPACE
    c_children = AuthnStatementType_.c_children.copy()
    c_attributes = AuthnStatementType_.c_attributes.copy()
    c_child_order = AuthnStatementType_.c_child_order[:]
    c_cardinality = AuthnStatementType_.c_cardinality.copy()


def authn_statement_from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthnStatement, xml_string)


class AttributeStatement(AttributeStatementType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AttributeStatement element """

    c_tag = 'AttributeStatement'
    c_namespace = NAMESPACE
    c_children = AttributeStatementType_.c_children.copy()
    c_attributes = AttributeStatementType_.c_attributes.copy()
    c_child_order = AttributeStatementType_.c_child_order[:]
    c_cardinality = AttributeStatementType_.c_cardinality.copy()


def attribute_statement_from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributeStatement, xml_string)


class Subject(SubjectType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:Subject element """

    c_tag = 'Subject'
    c_namespace = NAMESPACE
    c_children = SubjectType_.c_children.copy()
    c_attributes = SubjectType_.c_attributes.copy()
    c_child_order = SubjectType_.c_child_order[:]
    c_cardinality = SubjectType_.c_cardinality.copy()


def subject_from_string(xml_string):
    return saml2.create_class_from_xml_string(Subject, xml_string)


#..................
# ['AuthzDecisionStatement', 'EvidenceType', 'AdviceType', 'Evidence',
# 'Assertion', 'AssertionType', 'AuthzDecisionStatementType', 'Advice']
class EvidenceType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:EvidenceType element """

    c_tag = 'EvidenceType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}AssertionIDRef'] = (
        'assertion_id_ref', [AssertionIDRef])
    c_cardinality['assertion_id_ref'] = {"min": 0}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}AssertionURIRef'] = (
        'assertion_uri_ref', [AssertionURIRef])
    c_cardinality['assertion_uri_ref'] = {"min": 0}
    c_cardinality['assertion'] = {"min": 0}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}EncryptedAssertion'] = (
        'encrypted_assertion', [EncryptedAssertion])
    c_cardinality['encrypted_assertion'] = {"min": 0}
    c_child_order.extend(['assertion_id_ref', 'assertion_uri_ref', 'assertion',
                          'encrypted_assertion'])

    def __init__(self,
                 assertion_id_ref=None,
                 assertion_uri_ref=None,
                 assertion=None,
                 encrypted_assertion=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.assertion_id_ref = assertion_id_ref or []
        self.assertion_uri_ref = assertion_uri_ref or []
        self.assertion = assertion or []
        self.encrypted_assertion = encrypted_assertion or []


def evidence_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(EvidenceType_, xml_string)


class Evidence(EvidenceType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:Evidence element """

    c_tag = 'Evidence'
    c_namespace = NAMESPACE
    c_children = EvidenceType_.c_children.copy()
    c_attributes = EvidenceType_.c_attributes.copy()
    c_child_order = EvidenceType_.c_child_order[:]
    c_cardinality = EvidenceType_.c_cardinality.copy()


def evidence_from_string(xml_string):
    return saml2.create_class_from_xml_string(Evidence, xml_string)


class AuthzDecisionStatementType_(StatementAbstractType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AuthzDecisionStatementType
    element """

    c_tag = 'AuthzDecisionStatementType'
    c_namespace = NAMESPACE
    c_children = StatementAbstractType_.c_children.copy()
    c_attributes = StatementAbstractType_.c_attributes.copy()
    c_child_order = StatementAbstractType_.c_child_order[:]
    c_cardinality = StatementAbstractType_.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Action'] = (
        'action', [Action])
    c_cardinality['action'] = {"min": 1}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Evidence'] = (
        'evidence', Evidence)
    c_cardinality['evidence'] = {"min": 0, "max": 1}
    c_attributes['Resource'] = ('resource', 'anyURI', True)
    c_attributes['Decision'] = ('decision', DecisionType_, True)
    c_child_order.extend(['action', 'evidence'])

    def __init__(self,
                 action=None,
                 evidence=None,
                 resource=None,
                 decision=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        StatementAbstractType_.__init__(
            self, text=text, extension_elements=extension_elements,
            extension_attributes=extension_attributes)
        self.action = action or []
        self.evidence = evidence
        self.resource = resource
        self.decision = decision


def authz_decision_statement_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthzDecisionStatementType_,
                                              xml_string)


class AuthzDecisionStatement(AuthzDecisionStatementType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AuthzDecisionStatement
    element """

    c_tag = 'AuthzDecisionStatement'
    c_namespace = NAMESPACE
    c_children = AuthzDecisionStatementType_.c_children.copy()
    c_attributes = AuthzDecisionStatementType_.c_attributes.copy()
    c_child_order = AuthzDecisionStatementType_.c_child_order[:]
    c_cardinality = AuthzDecisionStatementType_.c_cardinality.copy()


def authz_decision_statement_from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthzDecisionStatement,
                                              xml_string)


#..................
# ['Assertion', 'AssertionType', 'AdviceType', 'Advice']
class AssertionType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AssertionType element """

    c_tag = 'AssertionType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Issuer'] = ('issuer',
                                                                   Issuer)
    c_children['{http://www.w3.org/2000/09/xmldsig#}Signature'] = ('signature',
                                                                   ds.Signature)
    c_cardinality['signature'] = {"min": 0, "max": 1}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Subject'] = ('subject',
                                                                    Subject)
    c_cardinality['subject'] = {"min": 0, "max": 1}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Conditions'] = (
        'conditions', Conditions)
    c_cardinality['conditions'] = {"min": 0, "max": 1}
    c_cardinality['advice'] = {"min": 0, "max": 1}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Statement'] = (
        'statement', [Statement])
    c_cardinality['statement'] = {"min": 0}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}AuthnStatement'] = (
        'authn_statement', [AuthnStatement])
    c_cardinality['authn_statement'] = {"min": 0}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:assertion}AuthzDecisionStatement'] = (
            'authz_decision_statement', [AuthzDecisionStatement])
    c_cardinality['authz_decision_statement'] = {"min": 0}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}AttributeStatement'] = (
        'attribute_statement', [AttributeStatement])
    c_cardinality['attribute_statement'] = {"min": 0}
    c_attributes['Version'] = ('version', 'string', True)
    c_attributes['ID'] = ('id', 'ID', True)
    c_attributes['IssueInstant'] = ('issue_instant', 'dateTime', True)
    c_child_order.extend(['issuer', 'signature', 'subject', 'conditions',
                          'advice', 'statement', 'authn_statement',
                          'authz_decision_statement', 'attribute_statement'])

    def __init__(self,
                 issuer=None,
                 signature=None,
                 subject=None,
                 conditions=None,
                 advice=None,
                 statement=None,
                 authn_statement=None,
                 authz_decision_statement=None,
                 attribute_statement=None,
                 version=None,
                 id=None,
                 issue_instant=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.issuer = issuer
        self.signature = signature
        self.subject = subject
        self.conditions = conditions
        self.advice = advice
        self.statement = statement or []
        self.authn_statement = authn_statement or []
        self.authz_decision_statement = authz_decision_statement or []
        self.attribute_statement = attribute_statement or []
        self.version = version
        self.id = id
        self.issue_instant = issue_instant

    def verify(self):
        # If no statement MUST contain a subject element
        if self.attribute_statement or self.statement or \
                self.authn_statement or self.authz_decision_statement:
            pass
        elif not self.subject:
            raise MustValueError(
                "If no statement MUST contain a subject element")

        if self.authn_statement and not self.subject:
            raise MustValueError(
                "An assertion with an AuthnStatement must contain a Subject")

        return SamlBase.verify(self)


def assertion_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AssertionType_, xml_string)


class Assertion(AssertionType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:Assertion element """

    c_tag = 'Assertion'
    c_namespace = NAMESPACE
    c_children = AssertionType_.c_children.copy()
    c_attributes = AssertionType_.c_attributes.copy()
    c_child_order = AssertionType_.c_child_order[:]
    c_cardinality = AssertionType_.c_cardinality.copy()


def assertion_from_string(xml_string):
    return saml2.create_class_from_xml_string(Assertion, xml_string)


class AdviceType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:assertion:AdviceType element """

    c_tag = 'AdviceType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}AssertionIDRef'] = (
        'assertion_id_ref', [AssertionIDRef])
    c_cardinality['assertion_id_ref'] = {"min": 0}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}AssertionURIRef'] = (
        'assertion_uri_ref', [AssertionURIRef])
    c_cardinality['assertion_uri_ref'] = {"min": 0}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Assertion'] = (
        'assertion', [Assertion])
    c_cardinality['assertion'] = {"min": 0}
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}EncryptedAssertion'] = (
        'encrypted_assertion', [EncryptedAssertion])
    c_cardinality['encrypted_assertion'] = {"min": 0}
    c_child_order.extend(['assertion_id_ref', 'assertion_uri_ref', 'assertion',
                          'encrypted_assertion'])
    c_any = {"namespace": "##other", "processContents": "lax"}

    def __init__(self,
                 assertion_id_ref=None,
                 assertion_uri_ref=None,
                 assertion=None,
                 encrypted_assertion=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.assertion_id_ref = assertion_id_ref or []
        self.assertion_uri_ref = assertion_uri_ref or []
        self.assertion = assertion or []
        self.encrypted_assertion = encrypted_assertion or []


def advice_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AdviceType_, xml_string)


class Advice(AdviceType_):
    """The urn:oasis:names:tc:SAML:2.0:assertion:Advice element """

    c_tag = 'Advice'
    c_namespace = NAMESPACE
    c_children = AdviceType_.c_children.copy()
    c_attributes = AdviceType_.c_attributes.copy()
    c_child_order = AdviceType_.c_child_order[:]
    c_cardinality = AdviceType_.c_cardinality.copy()


def advice_from_string(xml_string):
    return saml2.create_class_from_xml_string(Advice, xml_string)


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
EvidenceType_.c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Assertion'] = (
    'assertion', [Assertion])
Evidence.c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Assertion'] = (
    'assertion', [Assertion])
AssertionType_.c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Advice'] = (
    'advice', Advice)
Assertion.c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Advice'] = (
    'advice', Advice)
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

AG_IDNameQualifiers = [
    ('NameQualifier', 'string', False),
    ('SPNameQualifier', 'string', False),
]

ELEMENT_FROM_STRING = {
    BaseID.c_tag: base_id_from_string,
    NameID.c_tag: name_id_from_string,
    NameIDType_.c_tag: name_id_type__from_string,
    EncryptedElementType_.c_tag: encrypted_element_type__from_string,
    EncryptedID.c_tag: encrypted_id_from_string,
    Issuer.c_tag: issuer_from_string,
    AssertionIDRef.c_tag: assertion_id_ref_from_string,
    AssertionURIRef.c_tag: assertion_uri_ref_from_string,
    Assertion.c_tag: assertion_from_string,
    AssertionType_.c_tag: assertion_type__from_string,
    Subject.c_tag: subject_from_string,
    SubjectType_.c_tag: subject_type__from_string,
    SubjectConfirmation.c_tag: subject_confirmation_from_string,
    SubjectConfirmationType_.c_tag: subject_confirmation_type__from_string,
    SubjectConfirmationData.c_tag: subject_confirmation_data_from_string,
    SubjectConfirmationDataType_.c_tag:
    subject_confirmation_data_type__from_string,
    KeyInfoConfirmationDataType_.c_tag:
    key_info_confirmation_data_type__from_string,
    Conditions.c_tag: conditions_from_string,
    ConditionsType_.c_tag: conditions_type__from_string,
    Condition.c_tag: condition_from_string,
    AudienceRestriction.c_tag: audience_restriction_from_string,
    AudienceRestrictionType_.c_tag: audience_restriction_type__from_string,
    Audience.c_tag: audience_from_string,
    OneTimeUse.c_tag: one_time_use_from_string,
    OneTimeUseType_.c_tag: one_time_use_type__from_string,
    ProxyRestriction.c_tag: proxy_restriction_from_string,
    ProxyRestrictionType_.c_tag: proxy_restriction_type__from_string,
    Advice.c_tag: advice_from_string,
    AdviceType_.c_tag: advice_type__from_string,
    EncryptedAssertion.c_tag: encrypted_assertion_from_string,
    Statement.c_tag: statement_from_string,
    AuthnStatement.c_tag: authn_statement_from_string,
    AuthnStatementType_.c_tag: authn_statement_type__from_string,
    SubjectLocality.c_tag: subject_locality_from_string,
    SubjectLocalityType_.c_tag: subject_locality_type__from_string,
    AuthnContext.c_tag: authn_context_from_string,
    AuthnContextType_.c_tag: authn_context_type__from_string,
    AuthnContextClassRef.c_tag: authn_context_class_ref_from_string,
    AuthnContextDeclRef.c_tag: authn_context_decl_ref_from_string,
    AuthnContextDecl.c_tag: authn_context_decl_from_string,
    AuthenticatingAuthority.c_tag: authenticating_authority_from_string,
    AuthzDecisionStatement.c_tag: authz_decision_statement_from_string,
    AuthzDecisionStatementType_.c_tag:
    authz_decision_statement_type__from_string,
    DecisionType_.c_tag: decision_type__from_string,
    Action.c_tag: action_from_string,
    ActionType_.c_tag: action_type__from_string,
    Evidence.c_tag: evidence_from_string,
    EvidenceType_.c_tag: evidence_type__from_string,
    AttributeStatement.c_tag: attribute_statement_from_string,
    AttributeStatementType_.c_tag: attribute_statement_type__from_string,
    Attribute.c_tag: attribute_from_string,
    AttributeType_.c_tag: attribute_type__from_string,
    AttributeValue.c_tag: attribute_value_from_string,
    EncryptedAttribute.c_tag: encrypted_attribute_from_string,
}

ELEMENT_BY_TAG = {
    'BaseID': BaseID,
    'NameID': NameID,
    'NameIDType': NameIDType_,
    'EncryptedElementType': EncryptedElementType_,
    'EncryptedID': EncryptedID,
    'Issuer': Issuer,
    'AssertionIDRef': AssertionIDRef,
    'AssertionURIRef': AssertionURIRef,
    'Assertion': Assertion,
    'AssertionType': AssertionType_,
    'Subject': Subject,
    'SubjectType': SubjectType_,
    'SubjectConfirmation': SubjectConfirmation,
    'SubjectConfirmationType': SubjectConfirmationType_,
    'SubjectConfirmationData': SubjectConfirmationData,
    'SubjectConfirmationDataType': SubjectConfirmationDataType_,
    'KeyInfoConfirmationDataType': KeyInfoConfirmationDataType_,
    'Conditions': Conditions,
    'ConditionsType': ConditionsType_,
    'Condition': Condition,
    'AudienceRestriction': AudienceRestriction,
    'AudienceRestrictionType': AudienceRestrictionType_,
    'Audience': Audience,
    'OneTimeUse': OneTimeUse,
    'OneTimeUseType': OneTimeUseType_,
    'ProxyRestriction': ProxyRestriction,
    'ProxyRestrictionType': ProxyRestrictionType_,
    'Advice': Advice,
    'AdviceType': AdviceType_,
    'EncryptedAssertion': EncryptedAssertion,
    'Statement': Statement,
    'AuthnStatement': AuthnStatement,
    'AuthnStatementType': AuthnStatementType_,
    'SubjectLocality': SubjectLocality,
    'SubjectLocalityType': SubjectLocalityType_,
    'AuthnContext': AuthnContext,
    'AuthnContextType': AuthnContextType_,
    'AuthnContextClassRef': AuthnContextClassRef,
    'AuthnContextDeclRef': AuthnContextDeclRef,
    'AuthnContextDecl': AuthnContextDecl,
    'AuthenticatingAuthority': AuthenticatingAuthority,
    'AuthzDecisionStatement': AuthzDecisionStatement,
    'AuthzDecisionStatementType': AuthzDecisionStatementType_,
    'DecisionType': DecisionType_,
    'Action': Action,
    'ActionType': ActionType_,
    'Evidence': Evidence,
    'EvidenceType': EvidenceType_,
    'AttributeStatement': AttributeStatement,
    'AttributeStatementType': AttributeStatementType_,
    'Attribute': Attribute,
    'AttributeType': AttributeType_,
    'AttributeValue': AttributeValue,
    'EncryptedAttribute': EncryptedAttribute,
    'BaseIDAbstractType': BaseIDAbstractType_,
    'ConditionAbstractType': ConditionAbstractType_,
    'StatementAbstractType': StatementAbstractType_,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)
