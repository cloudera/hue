#!/usr/bin/env python

#
# Generated Tue Jul 18 14:58:29 2017 by parse_xsd.py version 0.5.
#

import saml2
from saml2 import SamlBase
from saml2 import saml


NAMESPACE = "http://eidas.europa.eu/saml-extensions"


class RequestedAttributeType_(SamlBase):
    """The http://eidas.europa.eu/saml-extensions:RequestedAttributeType element"""

    c_tag = "RequestedAttributeType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue"] = ("attribute_value", [saml.AttributeValue])
    c_cardinality["attribute_value"] = {"min": 0}
    c_attributes["Name"] = ("name", "None", True)
    c_attributes["NameFormat"] = ("name_format", "None", True)
    c_attributes["FriendlyName"] = ("friendly_name", "None", False)
    c_attributes["isRequired"] = ("is_required", "None", False)
    c_child_order.extend(["attribute_value"])

    def __init__(
        self,
        attribute_value=None,
        name=None,
        name_format=None,
        friendly_name=None,
        is_required=None,
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
        self.attribute_value = attribute_value or []
        self.name = name
        self.name_format = name_format
        self.friendly_name = friendly_name
        self.is_required = is_required


def requested_attribute_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestedAttributeType_, xml_string)


class RequestedAttribute(RequestedAttributeType_):
    """The http://eidas.europa.eu/saml-extensions:RequestedAttribute element"""

    c_tag = "RequestedAttribute"
    c_namespace = NAMESPACE
    c_children = RequestedAttributeType_.c_children.copy()
    c_attributes = RequestedAttributeType_.c_attributes.copy()
    c_child_order = RequestedAttributeType_.c_child_order[:]
    c_cardinality = RequestedAttributeType_.c_cardinality.copy()


def requested_attribute_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestedAttribute, xml_string)


class RequestedAttributesType_(SamlBase):
    """The http://eidas.europa.eu/saml-extensions:RequestedAttributesType element"""

    c_tag = "RequestedAttributesType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://eidas.europa.eu/saml-extensions}RequestedAttribute"] = (
        "requested_attribute",
        [RequestedAttribute],
    )
    c_cardinality["requested_attribute"] = {"min": 0}
    c_child_order.extend(["requested_attribute"])

    def __init__(
        self,
        requested_attribute=None,
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
        self.requested_attribute = requested_attribute or []


def requested_attributes_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestedAttributesType_, xml_string)


class RequestedAttributes(RequestedAttributesType_):
    """The http://eidas.europa.eu/saml-extensions:RequestedAttributes element"""

    c_tag = "RequestedAttributes"
    c_namespace = NAMESPACE
    c_children = RequestedAttributesType_.c_children.copy()
    c_attributes = RequestedAttributesType_.c_attributes.copy()
    c_child_order = RequestedAttributesType_.c_child_order[:]
    c_cardinality = RequestedAttributesType_.c_cardinality.copy()


def requested_attributes_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestedAttributes, xml_string)


ELEMENT_FROM_STRING = {
    RequestedAttributes.c_tag: requested_attributes_from_string,
    RequestedAttributesType_.c_tag: requested_attributes_type__from_string,
    RequestedAttribute.c_tag: requested_attribute_from_string,
    RequestedAttributeType_.c_tag: requested_attribute_type__from_string,
}

ELEMENT_BY_TAG = {
    "RequestedAttributes": RequestedAttributes,
    "RequestedAttributesType": RequestedAttributesType_,
    "RequestedAttribute": RequestedAttribute,
    "RequestedAttributeType": RequestedAttributeType_,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)
