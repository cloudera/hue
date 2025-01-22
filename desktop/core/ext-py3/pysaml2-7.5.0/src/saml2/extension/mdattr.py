#!/usr/bin/env python

#
# Generated Mon May  2 14:23:34 2011 by parse_xsd.py version 0.4.
#

import saml2
from saml2 import SamlBase
from saml2 import saml


NAMESPACE = "urn:oasis:names:tc:SAML:metadata:attribute"


class EntityAttributesType_(SamlBase):
    """The urn:oasis:names:tc:SAML:metadata:attribute:EntityAttributesType element"""

    c_tag = "EntityAttributesType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:2.0:assertion}Attribute"] = ("attribute", [saml.Attribute])
    c_cardinality["attribute"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:assertion}Assertion"] = ("assertion", [saml.Assertion])
    c_cardinality["assertion"] = {"min": 0}
    c_child_order.extend(["attribute", "assertion"])

    def __init__(
        self,
        attribute=None,
        assertion=None,
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
        self.attribute = attribute or []
        self.assertion = assertion or []


def entity_attributes_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(EntityAttributesType_, xml_string)


class EntityAttributes(EntityAttributesType_):
    """The urn:oasis:names:tc:SAML:metadata:attribute:EntityAttributes element"""

    c_tag = "EntityAttributes"
    c_namespace = NAMESPACE
    c_children = EntityAttributesType_.c_children.copy()
    c_attributes = EntityAttributesType_.c_attributes.copy()
    c_child_order = EntityAttributesType_.c_child_order[:]
    c_cardinality = EntityAttributesType_.c_cardinality.copy()


def entity_attributes_from_string(xml_string):
    return saml2.create_class_from_xml_string(EntityAttributes, xml_string)


ELEMENT_FROM_STRING = {
    EntityAttributes.c_tag: entity_attributes_from_string,
    EntityAttributesType_.c_tag: entity_attributes_type__from_string,
}

ELEMENT_BY_TAG = {
    "EntityAttributes": EntityAttributes,
    "EntityAttributesType": EntityAttributesType_,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)
