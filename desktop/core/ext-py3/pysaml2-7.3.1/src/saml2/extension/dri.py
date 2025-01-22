#!/usr/bin/env python

#
# Generated Mon Oct 25 16:19:28 2010 by parse_xsd.py version 0.4.
#

import saml2
from saml2 import SamlBase
from saml2 import md


NAMESPACE = "urn:oasis:names:tc:SAML:2.0:metadata:dri"


class CreationInstant(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:dri:CreationInstant element"""

    c_tag = "CreationInstant"
    c_namespace = NAMESPACE
    c_value_type = {"base": "datetime"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def creation_instant_from_string(xml_string):
    return saml2.create_class_from_xml_string(CreationInstant, xml_string)


class SerialNumber(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:dri:SerialNumber element"""

    c_tag = "SerialNumber"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def serial_number_from_string(xml_string):
    return saml2.create_class_from_xml_string(SerialNumber, xml_string)


class UsagePolicy(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:dri:UsagePolicy element"""

    c_tag = "UsagePolicy"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def usage_policy_from_string(xml_string):
    return saml2.create_class_from_xml_string(UsagePolicy, xml_string)


class PublisherType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:dri:PublisherType element"""

    c_tag = "PublisherType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["PublisherID"] = ("publisher_id", "md:entityIDType", True)
    c_attributes["CreationInstant"] = ("creation_instant", "datetime", False)
    c_attributes["SerialNumber"] = ("serial_number", "string", False)

    def __init__(
        self,
        publisher_id=None,
        creation_instant=None,
        serial_number=None,
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
        self.publisher_id = publisher_id
        self.creation_instant = creation_instant
        self.serial_number = serial_number


def publisher_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(PublisherType_, xml_string)


class RegistrationAuthority(md.EntityIDType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:dri:RegistrationAuthority
    element"""

    c_tag = "RegistrationAuthority"
    c_namespace = NAMESPACE
    c_children = md.EntityIDType_.c_children.copy()
    c_attributes = md.EntityIDType_.c_attributes.copy()
    c_child_order = md.EntityIDType_.c_child_order[:]
    c_cardinality = md.EntityIDType_.c_cardinality.copy()


def registration_authority_from_string(xml_string):
    return saml2.create_class_from_xml_string(RegistrationAuthority, xml_string)


class RegistrationInstant(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:dri:RegistrationInstant
    element"""

    c_tag = "RegistrationInstant"
    c_namespace = NAMESPACE
    c_value_type = {"base": "datetime"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def registration_instant_from_string(xml_string):
    return saml2.create_class_from_xml_string(RegistrationInstant, xml_string)


class RegistrationPolicy(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:dri:RegistrationPolicy
    element"""

    c_tag = "RegistrationPolicy"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def registration_policy_from_string(xml_string):
    return saml2.create_class_from_xml_string(RegistrationPolicy, xml_string)


class Publisher(PublisherType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:dri:Publisher element"""

    c_tag = "Publisher"
    c_namespace = NAMESPACE
    c_children = PublisherType_.c_children.copy()
    c_attributes = PublisherType_.c_attributes.copy()
    c_child_order = PublisherType_.c_child_order[:]
    c_cardinality = PublisherType_.c_cardinality.copy()


def publisher_from_string(xml_string):
    return saml2.create_class_from_xml_string(Publisher, xml_string)


class RegistrationInfoType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:dri:RegistrationInfoType
    element"""

    c_tag = "RegistrationInfoType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata:dri}RegistrationAuthority"] = (
        "registration_authority",
        RegistrationAuthority,
    )
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata:dri}RegistrationInstant"] = (
        "registration_instant",
        RegistrationInstant,
    )
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata:dri}RegistrationPolicy"] = (
        "registration_policy",
        RegistrationPolicy,
    )
    c_cardinality["registration_policy"] = {"min": 0, "max": 1}
    c_child_order.extend(["registration_authority", "registration_instant", "registration_policy"])

    def __init__(
        self,
        registration_authority=None,
        registration_instant=None,
        registration_policy=None,
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
        self.registration_authority = registration_authority
        self.registration_instant = registration_instant
        self.registration_policy = registration_policy


def registration_info_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RegistrationInfoType_, xml_string)


class PublishersType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:dri:PublishersType element"""

    c_tag = "PublishersType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata:dri}Publisher"] = ("publisher", [Publisher])
    c_cardinality["publisher"] = {"min": 0}
    c_child_order.extend(["publisher"])

    def __init__(
        self,
        publisher=None,
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
        self.publisher = publisher or []


def publishers_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(PublishersType_, xml_string)


class RegistrationInfo(RegistrationInfoType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:dri:RegistrationInfo element"""

    c_tag = "RegistrationInfo"
    c_namespace = NAMESPACE
    c_children = RegistrationInfoType_.c_children.copy()
    c_attributes = RegistrationInfoType_.c_attributes.copy()
    c_child_order = RegistrationInfoType_.c_child_order[:]
    c_cardinality = RegistrationInfoType_.c_cardinality.copy()


def registration_info_from_string(xml_string):
    return saml2.create_class_from_xml_string(RegistrationInfo, xml_string)


class Publishers(PublishersType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:dri:Publishers element"""

    c_tag = "Publishers"
    c_namespace = NAMESPACE
    c_children = PublishersType_.c_children.copy()
    c_attributes = PublishersType_.c_attributes.copy()
    c_child_order = PublishersType_.c_child_order[:]
    c_cardinality = PublishersType_.c_cardinality.copy()


def publishers_from_string(xml_string):
    return saml2.create_class_from_xml_string(Publishers, xml_string)


class DocumentInfoType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:dri:DocumentInfoType element"""

    c_tag = "DocumentInfoType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata:dri}CreationInstant"] = ("creation_instant", CreationInstant)
    c_cardinality["creation_instant"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata:dri}SerialNumber"] = ("serial_number", SerialNumber)
    c_cardinality["serial_number"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata:dri}UsagePolicy"] = ("usage_policy", UsagePolicy)
    c_cardinality["usage_policy"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata:dri}Publishers"] = ("publishers", Publishers)
    c_cardinality["publishers"] = {"min": 0, "max": 1}
    c_child_order.extend(["creation_instant", "serial_number", "usage_policy", "publishers"])

    def __init__(
        self,
        creation_instant=None,
        serial_number=None,
        usage_policy=None,
        publishers=None,
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
        self.creation_instant = creation_instant
        self.serial_number = serial_number
        self.usage_policy = usage_policy
        self.publishers = publishers


def document_info_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(DocumentInfoType_, xml_string)


class DocumentInfo(DocumentInfoType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:dri:DocumentInfo element"""

    c_tag = "DocumentInfo"
    c_namespace = NAMESPACE
    c_children = DocumentInfoType_.c_children.copy()
    c_attributes = DocumentInfoType_.c_attributes.copy()
    c_child_order = DocumentInfoType_.c_child_order[:]
    c_cardinality = DocumentInfoType_.c_cardinality.copy()


def document_info_from_string(xml_string):
    return saml2.create_class_from_xml_string(DocumentInfo, xml_string)


ELEMENT_FROM_STRING = {
    DocumentInfo.c_tag: document_info_from_string,
    DocumentInfoType_.c_tag: document_info_type__from_string,
    CreationInstant.c_tag: creation_instant_from_string,
    SerialNumber.c_tag: serial_number_from_string,
    UsagePolicy.c_tag: usage_policy_from_string,
    Publishers.c_tag: publishers_from_string,
    PublishersType_.c_tag: publishers_type__from_string,
    Publisher.c_tag: publisher_from_string,
    PublisherType_.c_tag: publisher_type__from_string,
    RegistrationInfo.c_tag: registration_info_from_string,
    RegistrationInfoType_.c_tag: registration_info_type__from_string,
    RegistrationAuthority.c_tag: registration_authority_from_string,
    RegistrationInstant.c_tag: registration_instant_from_string,
    RegistrationPolicy.c_tag: registration_policy_from_string,
}

ELEMENT_BY_TAG = {
    "DocumentInfo": DocumentInfo,
    "DocumentInfoType": DocumentInfoType_,
    "CreationInstant": CreationInstant,
    "SerialNumber": SerialNumber,
    "UsagePolicy": UsagePolicy,
    "Publishers": Publishers,
    "PublishersType": PublishersType_,
    "Publisher": Publisher,
    "PublisherType": PublisherType_,
    "RegistrationInfo": RegistrationInfo,
    "RegistrationInfoType": RegistrationInfoType_,
    "RegistrationAuthority": RegistrationAuthority,
    "RegistrationInstant": RegistrationInstant,
    "RegistrationPolicy": RegistrationPolicy,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)
