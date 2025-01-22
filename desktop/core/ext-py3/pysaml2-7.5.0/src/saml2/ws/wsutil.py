#!/usr/bin/env python

#
# Generated Sun Jun 14 12:18:10 2015 by parse_xsd.py version 0.5.
#

import saml2
from saml2 import SamlBase


NAMESPACE = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"


class TTimestampFault_(SamlBase):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd:tTimestampFault element"""

    c_tag = "tTimestampFault"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def t_timestamp_fault__from_string(xml_string):
    return saml2.create_class_from_xml_string(TTimestampFault_, xml_string)


class AttributedDateTime_(SamlBase):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd:AttributedDateTime element"""

    c_tag = "AttributedDateTime"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["Id"] = ("Id", "anyURI", False)

    def __init__(
        self,
        Id=None,
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
        self.Id = Id


def attributed_date_time__from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributedDateTime_, xml_string)


class AttributedURI_(SamlBase):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd:AttributedURI element"""

    c_tag = "AttributedURI"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["Id"] = ("Id", "anyURI", False)

    def __init__(
        self,
        Id=None,
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
        self.Id = Id


def attributed_ur_i__from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributedURI_, xml_string)


class Expires(AttributedDateTime_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd:Expires element"""

    c_tag = "Expires"
    c_namespace = NAMESPACE
    c_children = AttributedDateTime_.c_children.copy()
    c_attributes = AttributedDateTime_.c_attributes.copy()
    c_child_order = AttributedDateTime_.c_child_order[:]
    c_cardinality = AttributedDateTime_.c_cardinality.copy()


def expires_from_string(xml_string):
    return saml2.create_class_from_xml_string(Expires, xml_string)


class Created(AttributedDateTime_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd:Created element"""

    c_tag = "Created"
    c_namespace = NAMESPACE
    c_children = AttributedDateTime_.c_children.copy()
    c_attributes = AttributedDateTime_.c_attributes.copy()
    c_child_order = AttributedDateTime_.c_child_order[:]
    c_cardinality = AttributedDateTime_.c_cardinality.copy()


def created_from_string(xml_string):
    return saml2.create_class_from_xml_string(Created, xml_string)


class TimestampType_(SamlBase):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd:TimestampType element"""

    c_tag = "TimestampType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Created"] = (
        "created",
        Created,
    )
    c_cardinality["created"] = {"min": 0, "max": 1}
    c_children["{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Expires"] = (
        "expires",
        Expires,
    )
    c_cardinality["expires"] = {"min": 0, "max": 1}
    c_attributes["Id"] = ("Id", "anyURI", False)
    c_child_order.extend(["created", "expires"])

    def __init__(
        self,
        created=None,
        expires=None,
        Id=None,
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
        self.Id = Id


def timestamp_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(TimestampType_, xml_string)


class Timestamp(TimestampType_):
    """The http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd:Timestamp element"""

    c_tag = "Timestamp"
    c_namespace = NAMESPACE
    c_children = TimestampType_.c_children.copy()
    c_attributes = TimestampType_.c_attributes.copy()
    c_child_order = TimestampType_.c_child_order[:]
    c_cardinality = TimestampType_.c_cardinality.copy()


def timestamp_from_string(xml_string):
    return saml2.create_class_from_xml_string(Timestamp, xml_string)


# ..................
AG_commonAtts = [
    ("Id", "", False),
]

ELEMENT_FROM_STRING = {
    TTimestampFault_.c_tag: t_timestamp_fault__from_string,
    AttributedDateTime_.c_tag: attributed_date_time__from_string,
    AttributedURI_.c_tag: attributed_ur_i__from_string,
    TimestampType_.c_tag: timestamp_type__from_string,
    Timestamp.c_tag: timestamp_from_string,
    Expires.c_tag: expires_from_string,
    Created.c_tag: created_from_string,
}

ELEMENT_BY_TAG = {
    "tTimestampFault": TTimestampFault_,
    "AttributedDateTime": AttributedDateTime_,
    "AttributedURI": AttributedURI_,
    "TimestampType": TimestampType_,
    "Timestamp": Timestamp,
    "Expires": Expires,
    "Created": Created,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)
