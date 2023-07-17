#!/usr/bin/env python

#
# Generated Tue Jul 18 15:03:44 2017 by parse_xsd.py version 0.5.
#

import saml2
from saml2 import SamlBase


NAMESPACE = "http://eidas.europa.eu/saml-extensions"


class SPTypeType_(SamlBase):
    """The http://eidas.europa.eu/saml-extensions:SPTypeType element"""

    c_tag = "SPTypeType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "xsd:string", "enumeration": ["public", "private"]}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def sp_type_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SPTypeType_, xml_string)


class SPType(SPTypeType_):
    """The http://eidas.europa.eu/saml-extensions:SPType element"""

    c_tag = "SPType"
    c_namespace = NAMESPACE
    c_children = SPTypeType_.c_children.copy()
    c_attributes = SPTypeType_.c_attributes.copy()
    c_child_order = SPTypeType_.c_child_order[:]
    c_cardinality = SPTypeType_.c_cardinality.copy()


def sp_type_from_string(xml_string):
    return saml2.create_class_from_xml_string(SPType, xml_string)


ELEMENT_FROM_STRING = {
    SPType.c_tag: sp_type_from_string,
    SPTypeType_.c_tag: sp_type_type__from_string,
}

ELEMENT_BY_TAG = {
    "SPType": SPType,
    "SPTypeType": SPTypeType_,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)
