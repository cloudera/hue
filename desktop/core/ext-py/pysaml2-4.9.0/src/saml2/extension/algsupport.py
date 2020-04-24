#!/usr/bin/env python

#
# Generated Sat Mar  8 16:15:12 2014 by parse_xsd.py version 0.5.
#

import saml2
from saml2 import SamlBase


NAMESPACE = 'urn:oasis:names:tc:SAML:metadata:algsupport'


class DigestMethodType_(SamlBase):
    """The urn:oasis:names:tc:SAML:metadata:algsupport:DigestMethodType
    element """

    c_tag = 'DigestMethodType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['Algorithm'] = ('algorithm', 'anyURI', True)

    def __init__(self,
                 algorithm=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.algorithm = algorithm


def digest_method_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(DigestMethodType_, xml_string)


class SigningMethodType_(SamlBase):
    """The urn:oasis:names:tc:SAML:metadata:algsupport:SigningMethodType
    element """

    c_tag = 'SigningMethodType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['Algorithm'] = ('algorithm', 'anyURI', True)
    c_attributes['MinKeySize'] = ('min_key_size', 'positiveInteger', False)
    c_attributes['MaxKeySize'] = ('max_key_size', 'positiveInteger', False)

    def __init__(self,
                 algorithm=None,
                 min_key_size=None,
                 max_key_size=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.algorithm = algorithm
        self.min_key_size = min_key_size
        self.max_key_size = max_key_size


def signing_method_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SigningMethodType_, xml_string)


class DigestMethod(DigestMethodType_):
    """The urn:oasis:names:tc:SAML:metadata:algsupport:DigestMethod element """

    c_tag = 'DigestMethod'
    c_namespace = NAMESPACE
    c_children = DigestMethodType_.c_children.copy()
    c_attributes = DigestMethodType_.c_attributes.copy()
    c_child_order = DigestMethodType_.c_child_order[:]
    c_cardinality = DigestMethodType_.c_cardinality.copy()


def digest_method_from_string(xml_string):
    return saml2.create_class_from_xml_string(DigestMethod, xml_string)


class SigningMethod(SigningMethodType_):
    """The urn:oasis:names:tc:SAML:metadata:algsupport:SigningMethod element """

    c_tag = 'SigningMethod'
    c_namespace = NAMESPACE
    c_children = SigningMethodType_.c_children.copy()
    c_attributes = SigningMethodType_.c_attributes.copy()
    c_child_order = SigningMethodType_.c_child_order[:]
    c_cardinality = SigningMethodType_.c_cardinality.copy()


def signing_method_from_string(xml_string):
    return saml2.create_class_from_xml_string(SigningMethod, xml_string)


ELEMENT_FROM_STRING = {
    DigestMethod.c_tag: digest_method_from_string,
    DigestMethodType_.c_tag: digest_method_type__from_string,
    SigningMethod.c_tag: signing_method_from_string,
    SigningMethodType_.c_tag: signing_method_type__from_string,
}

ELEMENT_BY_TAG = {
    'DigestMethod': DigestMethod,
    'DigestMethodType': DigestMethodType_,
    'SigningMethod': SigningMethod,
    'SigningMethodType': SigningMethodType_,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)

