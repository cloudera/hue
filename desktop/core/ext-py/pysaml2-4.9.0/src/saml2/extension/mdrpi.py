#!/usr/bin/env python

#
# Generated Mon Jun 27 09:54:22 2011 by parse_xsd.py version 0.4.
#

import saml2
from saml2 import SamlBase

from saml2 import md

NAMESPACE = 'urn:oasis:names:tc:SAML:metadata:rpi'


class RegistrationPolicy(md.LocalizedURIType_):
    """The urn:oasis:names:tc:SAML:metadata:rpi:RegistrationPolicy element """

    c_tag = 'RegistrationPolicy'
    c_namespace = NAMESPACE
    c_children = md.LocalizedURIType_.c_children.copy()
    c_attributes = md.LocalizedURIType_.c_attributes.copy()
    c_child_order = md.LocalizedURIType_.c_child_order[:]
    c_cardinality = md.LocalizedURIType_.c_cardinality.copy()


def registration_policy_from_string(xml_string):
    return saml2.create_class_from_xml_string(RegistrationPolicy, xml_string)


class UsagePolicy(md.LocalizedURIType_):
    """The urn:oasis:names:tc:SAML:metadata:rpi:UsagePolicy element """

    c_tag = 'UsagePolicy'
    c_namespace = NAMESPACE
    c_children = md.LocalizedURIType_.c_children.copy()
    c_attributes = md.LocalizedURIType_.c_attributes.copy()
    c_child_order = md.LocalizedURIType_.c_child_order[:]
    c_cardinality = md.LocalizedURIType_.c_cardinality.copy()


def usage_policy_from_string(xml_string):
    return saml2.create_class_from_xml_string(UsagePolicy, xml_string)


class PublicationType_(SamlBase):
    """The urn:oasis:names:tc:SAML:metadata:rpi:PublicationType element """

    c_tag = 'PublicationType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['publisher'] = ('publisher', 'string', True)
    c_attributes['creationInstant'] = ('creation_instant', 'dateTime', False)
    c_attributes['publicationId'] = ('publication_id', 'string', False)

    def __init__(self,
                 publisher=None,
                 creation_instant=None,
                 publication_id=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.publisher = publisher
        self.creation_instant = creation_instant
        self.publication_id = publication_id


def publication_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(PublicationType_, xml_string)


class RegistrationInfoType_(SamlBase):
    """The urn:oasis:names:tc:SAML:metadata:rpi:RegistrationInfoType element """

    c_tag = 'RegistrationInfoType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:metadata:rpi}RegistrationPolicy'] = (
    'registration_policy', [RegistrationPolicy])
    c_cardinality['registration_policy'] = {"min": 0}
    c_attributes['registrationAuthority'] = (
    'registration_authority', 'string', True)
    c_attributes['registrationInstant'] = (
    'registration_instant', 'dateTime', False)
    c_child_order.extend(['registration_policy'])

    def __init__(self,
                 registration_policy=None,
                 registration_authority=None,
                 registration_instant=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.registration_policy = registration_policy or []
        self.registration_authority = registration_authority
        self.registration_instant = registration_instant


def registration_info_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RegistrationInfoType_, xml_string)


class PublicationInfoType_(SamlBase):
    """The urn:oasis:names:tc:SAML:metadata:rpi:PublicationInfoType element """

    c_tag = 'PublicationInfoType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:metadata:rpi}UsagePolicy'] = (
    'usage_policy', [UsagePolicy])
    c_cardinality['usage_policy'] = {"min": 0}
    c_attributes['publisher'] = ('publisher', 'string', True)
    c_attributes['creationInstant'] = ('creation_instant', 'dateTime', False)
    c_attributes['publicationId'] = ('publication_id', 'string', False)
    c_child_order.extend(['usage_policy'])

    def __init__(self,
                 usage_policy=None,
                 publisher=None,
                 creation_instant=None,
                 publication_id=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.usage_policy = usage_policy or []
        self.publisher = publisher
        self.creation_instant = creation_instant
        self.publication_id = publication_id


def publication_info_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(PublicationInfoType_, xml_string)


class Publication(PublicationType_):
    """The urn:oasis:names:tc:SAML:metadata:rpi:Publication element """

    c_tag = 'Publication'
    c_namespace = NAMESPACE
    c_children = PublicationType_.c_children.copy()
    c_attributes = PublicationType_.c_attributes.copy()
    c_child_order = PublicationType_.c_child_order[:]
    c_cardinality = PublicationType_.c_cardinality.copy()


def publication_from_string(xml_string):
    return saml2.create_class_from_xml_string(Publication, xml_string)


class RegistrationInfo(RegistrationInfoType_):
    """The urn:oasis:names:tc:SAML:metadata:rpi:RegistrationInfo element """

    c_tag = 'RegistrationInfo'
    c_namespace = NAMESPACE
    c_children = RegistrationInfoType_.c_children.copy()
    c_attributes = RegistrationInfoType_.c_attributes.copy()
    c_child_order = RegistrationInfoType_.c_child_order[:]
    c_cardinality = RegistrationInfoType_.c_cardinality.copy()


def registration_info_from_string(xml_string):
    return saml2.create_class_from_xml_string(RegistrationInfo, xml_string)


class PublicationInfo(PublicationInfoType_):
    """The urn:oasis:names:tc:SAML:metadata:rpi:PublicationInfo element """

    c_tag = 'PublicationInfo'
    c_namespace = NAMESPACE
    c_children = PublicationInfoType_.c_children.copy()
    c_attributes = PublicationInfoType_.c_attributes.copy()
    c_child_order = PublicationInfoType_.c_child_order[:]
    c_cardinality = PublicationInfoType_.c_cardinality.copy()


def publication_info_from_string(xml_string):
    return saml2.create_class_from_xml_string(PublicationInfo, xml_string)


class PublicationPathType_(SamlBase):
    """The urn:oasis:names:tc:SAML:metadata:rpi:PublicationPathType element """

    c_tag = 'PublicationPathType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:metadata:rpi}Publication'] = (
    'publication', [Publication])
    c_cardinality['publication'] = {"min": 0}
    c_child_order.extend(['publication'])

    def __init__(self,
                 publication=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes)
        self.publication = publication or []


def publication_path_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(PublicationPathType_, xml_string)


class PublicationPath(PublicationPathType_):
    """The urn:oasis:names:tc:SAML:metadata:rpi:PublicationPath element """

    c_tag = 'PublicationPath'
    c_namespace = NAMESPACE
    c_children = PublicationPathType_.c_children.copy()
    c_attributes = PublicationPathType_.c_attributes.copy()
    c_child_order = PublicationPathType_.c_child_order[:]
    c_cardinality = PublicationPathType_.c_cardinality.copy()


def publication_path_from_string(xml_string):
    return saml2.create_class_from_xml_string(PublicationPath, xml_string)


ELEMENT_FROM_STRING = {
    RegistrationInfo.c_tag: registration_info_from_string,
    RegistrationInfoType_.c_tag: registration_info_type__from_string,
    RegistrationPolicy.c_tag: registration_policy_from_string,
    PublicationInfo.c_tag: publication_info_from_string,
    PublicationInfoType_.c_tag: publication_info_type__from_string,
    UsagePolicy.c_tag: usage_policy_from_string,
    PublicationPath.c_tag: publication_path_from_string,
    PublicationPathType_.c_tag: publication_path_type__from_string,
    Publication.c_tag: publication_from_string,
    PublicationType_.c_tag: publication_type__from_string,
}

ELEMENT_BY_TAG = {
    'RegistrationInfo': RegistrationInfo,
    'RegistrationInfoType': RegistrationInfoType_,
    'RegistrationPolicy': RegistrationPolicy,
    'PublicationInfo': PublicationInfo,
    'PublicationInfoType': PublicationInfoType_,
    'UsagePolicy': UsagePolicy,
    'PublicationPath': PublicationPath,
    'PublicationPathType': PublicationPathType_,
    'Publication': Publication,
    'PublicationType': PublicationType_,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)

