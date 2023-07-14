#!/usr/bin/env python

#
# Generated Sun Mar 20 18:06:44 2011 by parse_xsd.py version 0.4.
#

import saml2
from saml2 import SamlBase
from saml2 import xmldsig as ds


NAMESPACE = "urn:mace:shibboleth:metadata:1.0"


class Scope(SamlBase):
    """The urn:mace:shibboleth:metadata:1.0:Scope element"""

    c_tag = "Scope"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["regexp"] = ("regexp", "boolean", False)

    def __init__(self, regexp="false", text=None, extension_elements=None, extension_attributes=None):
        SamlBase.__init__(
            self, text=text, extension_elements=extension_elements, extension_attributes=extension_attributes
        )
        self.regexp = regexp


def scope_from_string(xml_string):
    return saml2.create_class_from_xml_string(Scope, xml_string)


class KeyAuthority(SamlBase):
    """The urn:mace:shibboleth:metadata:1.0:KeyAuthority element"""

    c_tag = "KeyAuthority"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}KeyInfo"] = ("key_info", [ds.KeyInfo])
    c_cardinality["key_info"] = {"min": 1}
    c_attributes["VerifyDepth"] = ("verify_depth", "unsignedByte", False)
    c_child_order.extend(["key_info"])

    def __init__(self, key_info=None, verify_depth="1", text=None, extension_elements=None, extension_attributes=None):
        SamlBase.__init__(
            self, text=text, extension_elements=extension_elements, extension_attributes=extension_attributes
        )
        self.key_info = key_info or []
        self.verify_depth = verify_depth


def key_authority_from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyAuthority, xml_string)


ELEMENT_FROM_STRING = {
    Scope.c_tag: scope_from_string,
    KeyAuthority.c_tag: key_authority_from_string,
}

ELEMENT_BY_TAG = {
    "Scope": Scope,
    "KeyAuthority": KeyAuthority,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)
