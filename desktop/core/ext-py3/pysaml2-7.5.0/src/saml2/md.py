#!/usr/bin/env python

#
# Generated Mon May  2 14:23:33 2011 by parse_xsd.py version 0.4.
#

import saml2
from saml2 import SamlBase
from saml2 import saml
from saml2 import xmldsig as ds
from saml2 import xmlenc as xenc


NAMESPACE = "urn:oasis:names:tc:SAML:2.0:metadata"


class EntityIDType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:entityIDType element"""

    c_tag = "entityIDType"
    c_namespace = NAMESPACE
    c_value_type = {"maxlen": "1024", "base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def entity_id_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(EntityIDType_, xml_string)


class LocalizedNameType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:localizedNameType element"""

    c_tag = "localizedNameType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["{http://www.w3.org/XML/1998/namespace}lang"] = ("lang", "string", True)

    def __init__(self, lang=None, text=None, extension_elements=None, extension_attributes=None):
        SamlBase.__init__(
            self, text=text, extension_elements=extension_elements, extension_attributes=extension_attributes
        )
        self.lang = lang


def localized_name_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(LocalizedNameType_, xml_string)


class LocalizedURIType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:localizedURIType element"""

    c_tag = "localizedURIType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["{http://www.w3.org/XML/1998/namespace}lang"] = ("lang", "anyURI", True)

    def __init__(self, lang=None, text=None, extension_elements=None, extension_attributes=None):
        SamlBase.__init__(
            self, text=text, extension_elements=extension_elements, extension_attributes=extension_attributes
        )
        self.lang = lang


def localized_uri_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(LocalizedURIType_, xml_string)


class ExtensionsType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:ExtensionsType element"""

    c_tag = "ExtensionsType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def extensions_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ExtensionsType_, xml_string)


class EndpointType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:EndpointType element"""

    c_tag = "EndpointType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["Binding"] = ("binding", "anyURI", True)
    c_attributes["Location"] = ("location", "anyURI", True)
    c_attributes["ResponseLocation"] = ("response_location", "anyURI", False)

    def __init__(
        self,
        binding=None,
        location=None,
        response_location=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self, text=text, extension_elements=extension_elements, extension_attributes=extension_attributes
        )
        self.binding = binding
        self.location = location
        self.response_location = response_location


def endpoint_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(EndpointType_, xml_string)


class IndexedEndpointType_(EndpointType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:IndexedEndpointType element"""

    c_tag = "IndexedEndpointType"
    c_namespace = NAMESPACE
    c_children = EndpointType_.c_children.copy()
    c_attributes = EndpointType_.c_attributes.copy()
    c_child_order = EndpointType_.c_child_order[:]
    c_cardinality = EndpointType_.c_cardinality.copy()
    c_attributes["index"] = ("index", "unsignedShort", True)
    c_attributes["isDefault"] = ("is_default", "boolean", False)

    def __init__(
        self,
        index=None,
        is_default=None,
        binding=None,
        location=None,
        response_location=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        EndpointType_.__init__(
            self,
            binding=binding,
            location=location,
            response_location=response_location,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.index = index
        self.is_default = is_default


def indexed_endpoint_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(IndexedEndpointType_, xml_string)


class OrganizationName(LocalizedNameType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:OrganizationName element"""

    c_tag = "OrganizationName"
    c_namespace = NAMESPACE
    c_children = LocalizedNameType_.c_children.copy()
    c_attributes = LocalizedNameType_.c_attributes.copy()
    c_child_order = LocalizedNameType_.c_child_order[:]
    c_cardinality = LocalizedNameType_.c_cardinality.copy()


def organization_name_from_string(xml_string):
    return saml2.create_class_from_xml_string(OrganizationName, xml_string)


class OrganizationDisplayName(LocalizedNameType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:OrganizationDisplayName
    element"""

    c_tag = "OrganizationDisplayName"
    c_namespace = NAMESPACE
    c_children = LocalizedNameType_.c_children.copy()
    c_attributes = LocalizedNameType_.c_attributes.copy()
    c_child_order = LocalizedNameType_.c_child_order[:]
    c_cardinality = LocalizedNameType_.c_cardinality.copy()


def organization_display_name_from_string(xml_string):
    return saml2.create_class_from_xml_string(OrganizationDisplayName, xml_string)


class OrganizationURL(LocalizedURIType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:OrganizationURL element"""

    c_tag = "OrganizationURL"
    c_namespace = NAMESPACE
    c_children = LocalizedURIType_.c_children.copy()
    c_attributes = LocalizedURIType_.c_attributes.copy()
    c_child_order = LocalizedURIType_.c_child_order[:]
    c_cardinality = LocalizedURIType_.c_cardinality.copy()


def organization_url_from_string(xml_string):
    return saml2.create_class_from_xml_string(OrganizationURL, xml_string)


class Company(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:Company element"""

    c_tag = "Company"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def company_from_string(xml_string):
    return saml2.create_class_from_xml_string(Company, xml_string)


class GivenName(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:GivenName element"""

    c_tag = "GivenName"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def given_name_from_string(xml_string):
    return saml2.create_class_from_xml_string(GivenName, xml_string)


class SurName(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:SurName element"""

    c_tag = "SurName"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def sur_name_from_string(xml_string):
    return saml2.create_class_from_xml_string(SurName, xml_string)


class EmailAddress(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:EmailAddress element"""

    c_tag = "EmailAddress"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def email_address_from_string(xml_string):
    return saml2.create_class_from_xml_string(EmailAddress, xml_string)


class TelephoneNumber(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:TelephoneNumber element"""

    c_tag = "TelephoneNumber"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def telephone_number_from_string(xml_string):
    return saml2.create_class_from_xml_string(TelephoneNumber, xml_string)


class ContactTypeType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:ContactTypeType element"""

    c_tag = "ContactTypeType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string", "enumeration": ["technical", "support", "administrative", "billing", "other"]}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def contact_type_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ContactTypeType_, xml_string)


class AdditionalMetadataLocationType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AdditionalMetadataLocationType
    element"""

    c_tag = "AdditionalMetadataLocationType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["namespace"] = ("namespace", "anyURI", True)

    def __init__(self, namespace=None, text=None, extension_elements=None, extension_attributes=None):
        SamlBase.__init__(
            self, text=text, extension_elements=extension_elements, extension_attributes=extension_attributes
        )
        self.namespace = namespace


def additional_metadata_location_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AdditionalMetadataLocationType_, xml_string)


class AnyURIListType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:anyURIListType element"""

    c_tag = "anyURIListType"
    c_namespace = NAMESPACE
    c_value_type = {"member": "anyURI", "base": "list"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def any_uri_list_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AnyURIListType_, xml_string)


class KeyTypes_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:KeyTypes element"""

    c_tag = "KeyTypes"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string", "enumeration": ["encryption", "signing"]}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def key_types__from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyTypes_, xml_string)


class EncryptionMethod(xenc.EncryptionMethodType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:EncryptionMethod element"""

    c_tag = "EncryptionMethod"
    c_namespace = NAMESPACE
    c_children = xenc.EncryptionMethodType_.c_children.copy()
    c_attributes = xenc.EncryptionMethodType_.c_attributes.copy()
    c_child_order = xenc.EncryptionMethodType_.c_child_order[:]
    c_cardinality = xenc.EncryptionMethodType_.c_cardinality.copy()


def encryption_method_from_string(xml_string):
    return saml2.create_class_from_xml_string(EncryptionMethod, xml_string)


class ArtifactResolutionService(IndexedEndpointType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:ArtifactResolutionService
    element"""

    c_tag = "ArtifactResolutionService"
    c_namespace = NAMESPACE
    c_children = IndexedEndpointType_.c_children.copy()
    c_attributes = IndexedEndpointType_.c_attributes.copy()
    c_child_order = IndexedEndpointType_.c_child_order[:]
    c_cardinality = IndexedEndpointType_.c_cardinality.copy()


def artifact_resolution_service_from_string(xml_string):
    return saml2.create_class_from_xml_string(ArtifactResolutionService, xml_string)


class SingleLogoutService(EndpointType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:SingleLogoutService element"""

    c_tag = "SingleLogoutService"
    c_namespace = NAMESPACE
    c_children = EndpointType_.c_children.copy()
    c_attributes = EndpointType_.c_attributes.copy()
    c_child_order = EndpointType_.c_child_order[:]
    c_cardinality = EndpointType_.c_cardinality.copy()


def single_logout_service_from_string(xml_string):
    return saml2.create_class_from_xml_string(SingleLogoutService, xml_string)


class ManageNameIDService(EndpointType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:ManageNameIDService element"""

    c_tag = "ManageNameIDService"
    c_namespace = NAMESPACE
    c_children = EndpointType_.c_children.copy()
    c_attributes = EndpointType_.c_attributes.copy()
    c_child_order = EndpointType_.c_child_order[:]
    c_cardinality = EndpointType_.c_cardinality.copy()


def manage_name_id_service_from_string(xml_string):
    return saml2.create_class_from_xml_string(ManageNameIDService, xml_string)


class NameIDFormat(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:NameIDFormat element"""

    c_tag = "NameIDFormat"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def name_id_format_from_string(xml_string):
    return saml2.create_class_from_xml_string(NameIDFormat, xml_string)


class SingleSignOnService(EndpointType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:SingleSignOnService element"""

    c_tag = "SingleSignOnService"
    c_namespace = NAMESPACE
    c_children = EndpointType_.c_children.copy()
    c_attributes = EndpointType_.c_attributes.copy()
    c_child_order = EndpointType_.c_child_order[:]
    c_cardinality = EndpointType_.c_cardinality.copy()


def single_sign_on_service_from_string(xml_string):
    return saml2.create_class_from_xml_string(SingleSignOnService, xml_string)


class NameIDMappingService(EndpointType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:NameIDMappingService element"""

    c_tag = "NameIDMappingService"
    c_namespace = NAMESPACE
    c_children = EndpointType_.c_children.copy()
    c_attributes = EndpointType_.c_attributes.copy()
    c_child_order = EndpointType_.c_child_order[:]
    c_cardinality = EndpointType_.c_cardinality.copy()


def name_id_mapping_service_from_string(xml_string):
    return saml2.create_class_from_xml_string(NameIDMappingService, xml_string)


class AssertionIDRequestService(EndpointType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AssertionIDRequestService
    element"""

    c_tag = "AssertionIDRequestService"
    c_namespace = NAMESPACE
    c_children = EndpointType_.c_children.copy()
    c_attributes = EndpointType_.c_attributes.copy()
    c_child_order = EndpointType_.c_child_order[:]
    c_cardinality = EndpointType_.c_cardinality.copy()


def assertion_id_request_service_from_string(xml_string):
    return saml2.create_class_from_xml_string(AssertionIDRequestService, xml_string)


class AttributeProfile(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AttributeProfile element"""

    c_tag = "AttributeProfile"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def attribute_profile_from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributeProfile, xml_string)


class AssertionConsumerService(IndexedEndpointType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AssertionConsumerService
    element"""

    c_tag = "AssertionConsumerService"
    c_namespace = NAMESPACE
    c_children = IndexedEndpointType_.c_children.copy()
    c_attributes = IndexedEndpointType_.c_attributes.copy()
    c_child_order = IndexedEndpointType_.c_child_order[:]
    c_cardinality = IndexedEndpointType_.c_cardinality.copy()


def assertion_consumer_service_from_string(xml_string):
    return saml2.create_class_from_xml_string(AssertionConsumerService, xml_string)


class ServiceName(LocalizedNameType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:ServiceName element"""

    c_tag = "ServiceName"
    c_namespace = NAMESPACE
    c_children = LocalizedNameType_.c_children.copy()
    c_attributes = LocalizedNameType_.c_attributes.copy()
    c_child_order = LocalizedNameType_.c_child_order[:]
    c_cardinality = LocalizedNameType_.c_cardinality.copy()


def service_name_from_string(xml_string):
    return saml2.create_class_from_xml_string(ServiceName, xml_string)


class ServiceDescription(LocalizedNameType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:ServiceDescription element"""

    c_tag = "ServiceDescription"
    c_namespace = NAMESPACE
    c_children = LocalizedNameType_.c_children.copy()
    c_attributes = LocalizedNameType_.c_attributes.copy()
    c_child_order = LocalizedNameType_.c_child_order[:]
    c_cardinality = LocalizedNameType_.c_cardinality.copy()


def service_description_from_string(xml_string):
    return saml2.create_class_from_xml_string(ServiceDescription, xml_string)


class RequestedAttributeType_(saml.AttributeType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:RequestedAttributeType
    element"""

    c_tag = "RequestedAttributeType"
    c_namespace = NAMESPACE
    c_children = saml.AttributeType_.c_children.copy()
    c_attributes = saml.AttributeType_.c_attributes.copy()
    c_child_order = saml.AttributeType_.c_child_order[:]
    c_cardinality = saml.AttributeType_.c_cardinality.copy()
    c_attributes["isRequired"] = ("is_required", "boolean", False)

    def __init__(
        self,
        is_required=None,
        friendly_name=None,
        name=None,
        name_format=None,
        attribute_value=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        saml.AttributeType_.__init__(
            self,
            friendly_name=friendly_name,
            name=name,
            name_format=name_format,
            attribute_value=attribute_value,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.is_required = is_required


def requested_attribute_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestedAttributeType_, xml_string)


class AuthnQueryService(EndpointType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AuthnQueryService element"""

    c_tag = "AuthnQueryService"
    c_namespace = NAMESPACE
    c_children = EndpointType_.c_children.copy()
    c_attributes = EndpointType_.c_attributes.copy()
    c_child_order = EndpointType_.c_child_order[:]
    c_cardinality = EndpointType_.c_cardinality.copy()


def authn_query_service_from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthnQueryService, xml_string)


class AuthzService(EndpointType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AuthzService element"""

    c_tag = "AuthzService"
    c_namespace = NAMESPACE
    c_children = EndpointType_.c_children.copy()
    c_attributes = EndpointType_.c_attributes.copy()
    c_child_order = EndpointType_.c_child_order[:]
    c_cardinality = EndpointType_.c_cardinality.copy()


def authz_service_from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthzService, xml_string)


class AttributeService(EndpointType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AttributeService element"""

    c_tag = "AttributeService"
    c_namespace = NAMESPACE
    c_children = EndpointType_.c_children.copy()
    c_attributes = EndpointType_.c_attributes.copy()
    c_child_order = EndpointType_.c_child_order[:]
    c_cardinality = EndpointType_.c_cardinality.copy()


def attribute_service_from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributeService, xml_string)


class AffiliateMember(EntityIDType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AffiliateMember element"""

    c_tag = "AffiliateMember"
    c_namespace = NAMESPACE
    c_children = EntityIDType_.c_children.copy()
    c_attributes = EntityIDType_.c_attributes.copy()
    c_child_order = EntityIDType_.c_child_order[:]
    c_cardinality = EntityIDType_.c_cardinality.copy()


def affiliate_member_from_string(xml_string):
    return saml2.create_class_from_xml_string(AffiliateMember, xml_string)


class Extensions(ExtensionsType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:Extensions element"""

    c_tag = "Extensions"
    c_namespace = NAMESPACE
    c_children = ExtensionsType_.c_children.copy()
    c_attributes = ExtensionsType_.c_attributes.copy()
    c_child_order = ExtensionsType_.c_child_order[:]
    c_cardinality = ExtensionsType_.c_cardinality.copy()


def extensions_from_string(xml_string):
    return saml2.create_class_from_xml_string(Extensions, xml_string)


class OrganizationType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:OrganizationType element"""

    c_tag = "OrganizationType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}Extensions"] = ("extensions", Extensions)
    c_cardinality["extensions"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}OrganizationName"] = ("organization_name", [OrganizationName])
    c_cardinality["organization_name"] = {"min": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}OrganizationDisplayName"] = (
        "organization_display_name",
        [OrganizationDisplayName],
    )
    c_cardinality["organization_display_name"] = {"min": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}OrganizationURL"] = ("organization_url", [OrganizationURL])
    c_cardinality["organization_url"] = {"min": 1}
    c_child_order.extend(["extensions", "organization_name", "organization_display_name", "organization_url"])

    def __init__(
        self,
        extensions=None,
        organization_name=None,
        organization_display_name=None,
        organization_url=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self, text=text, extension_elements=extension_elements, extension_attributes=extension_attributes
        )
        self.extensions = extensions
        self.organization_name = organization_name or []
        self.organization_display_name = organization_display_name or []
        self.organization_url = organization_url or []


def organization_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(OrganizationType_, xml_string)


class ContactType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:ContactType element"""

    c_tag = "ContactType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}Extensions"] = ("extensions", Extensions)
    c_cardinality["extensions"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}Company"] = ("company", Company)
    c_cardinality["company"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}GivenName"] = ("given_name", GivenName)
    c_cardinality["given_name"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}SurName"] = ("sur_name", SurName)
    c_cardinality["sur_name"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}EmailAddress"] = ("email_address", [EmailAddress])
    c_cardinality["email_address"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}TelephoneNumber"] = ("telephone_number", [TelephoneNumber])
    c_cardinality["telephone_number"] = {"min": 0}
    c_attributes["contactType"] = ("contact_type", ContactTypeType_, True)
    c_child_order.extend(["extensions", "company", "given_name", "sur_name", "email_address", "telephone_number"])

    def __init__(
        self,
        extensions=None,
        company=None,
        given_name=None,
        sur_name=None,
        email_address=None,
        telephone_number=None,
        contact_type=None,
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
        self.extensions = extensions
        self.company = company
        self.given_name = given_name
        self.sur_name = sur_name
        self.email_address = email_address or []
        self.telephone_number = telephone_number or []
        self.contact_type = contact_type


def contact_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ContactType_, xml_string)


class AdditionalMetadataLocation(AdditionalMetadataLocationType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AdditionalMetadataLocation
    element"""

    c_tag = "AdditionalMetadataLocation"
    c_namespace = NAMESPACE
    c_children = AdditionalMetadataLocationType_.c_children.copy()
    c_attributes = AdditionalMetadataLocationType_.c_attributes.copy()
    c_child_order = AdditionalMetadataLocationType_.c_child_order[:]
    c_cardinality = AdditionalMetadataLocationType_.c_cardinality.copy()


def additional_metadata_location_from_string(xml_string):
    return saml2.create_class_from_xml_string(AdditionalMetadataLocation, xml_string)


class KeyDescriptorType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:KeyDescriptorType element"""

    c_tag = "KeyDescriptorType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}KeyInfo"] = ("key_info", ds.KeyInfo)
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}EncryptionMethod"] = ("encryption_method", [EncryptionMethod])
    c_cardinality["encryption_method"] = {"min": 0}
    c_attributes["use"] = ("use", KeyTypes_, False)
    c_child_order.extend(["key_info", "encryption_method"])

    def __init__(
        self,
        key_info=None,
        encryption_method=None,
        use=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self, text=text, extension_elements=extension_elements, extension_attributes=extension_attributes
        )
        self.key_info = key_info
        self.encryption_method = encryption_method or []
        self.use = use


def key_descriptor_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyDescriptorType_, xml_string)


class RequestedAttribute(RequestedAttributeType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:RequestedAttribute element"""

    c_tag = "RequestedAttribute"
    c_namespace = NAMESPACE
    c_children = RequestedAttributeType_.c_children.copy()
    c_attributes = RequestedAttributeType_.c_attributes.copy()
    c_child_order = RequestedAttributeType_.c_child_order[:]
    c_cardinality = RequestedAttributeType_.c_cardinality.copy()


def requested_attribute_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestedAttribute, xml_string)


class Organization(OrganizationType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:Organization element"""

    c_tag = "Organization"
    c_namespace = NAMESPACE
    c_children = OrganizationType_.c_children.copy()
    c_attributes = OrganizationType_.c_attributes.copy()
    c_child_order = OrganizationType_.c_child_order[:]
    c_cardinality = OrganizationType_.c_cardinality.copy()


def organization_from_string(xml_string):
    return saml2.create_class_from_xml_string(Organization, xml_string)


class ContactPerson(ContactType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:ContactPerson element"""

    c_tag = "ContactPerson"
    c_namespace = NAMESPACE
    c_children = ContactType_.c_children.copy()
    c_attributes = ContactType_.c_attributes.copy()
    c_child_order = ContactType_.c_child_order[:]
    c_cardinality = ContactType_.c_cardinality.copy()


def contact_person_from_string(xml_string):
    return saml2.create_class_from_xml_string(ContactPerson, xml_string)


class KeyDescriptor(KeyDescriptorType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:KeyDescriptor element"""

    c_tag = "KeyDescriptor"
    c_namespace = NAMESPACE
    c_children = KeyDescriptorType_.c_children.copy()
    c_attributes = KeyDescriptorType_.c_attributes.copy()
    c_child_order = KeyDescriptorType_.c_child_order[:]
    c_cardinality = KeyDescriptorType_.c_cardinality.copy()


def key_descriptor_from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyDescriptor, xml_string)


class RoleDescriptorType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:RoleDescriptorType element"""

    c_tag = "RoleDescriptorType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}Signature"] = ("signature", ds.Signature)
    c_cardinality["signature"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}Extensions"] = ("extensions", Extensions)
    c_cardinality["extensions"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}KeyDescriptor"] = ("key_descriptor", [KeyDescriptor])
    c_cardinality["key_descriptor"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}Organization"] = ("organization", Organization)
    c_cardinality["organization"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}ContactPerson"] = ("contact_person", [ContactPerson])
    c_cardinality["contact_person"] = {"min": 0}
    c_attributes["ID"] = ("id", "ID", False)
    c_attributes["validUntil"] = ("valid_until", "dateTime", False)
    c_attributes["cacheDuration"] = ("cache_duration", "duration", False)
    c_attributes["protocolSupportEnumeration"] = ("protocol_support_enumeration", AnyURIListType_, True)
    c_attributes["errorURL"] = ("error_url", "anyURI", False)
    c_child_order.extend(["signature", "extensions", "key_descriptor", "organization", "contact_person"])

    def __init__(
        self,
        signature=None,
        extensions=None,
        key_descriptor=None,
        organization=None,
        contact_person=None,
        id=None,
        valid_until=None,
        cache_duration=None,
        protocol_support_enumeration=None,
        error_url=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self, text=text, extension_elements=extension_elements, extension_attributes=extension_attributes
        )
        self.signature = signature
        self.extensions = extensions
        self.key_descriptor = key_descriptor or []
        self.organization = organization
        self.contact_person = contact_person or []
        self.id = id
        self.valid_until = valid_until
        self.cache_duration = cache_duration
        self.protocol_support_enumeration = protocol_support_enumeration
        self.error_url = error_url


class SSODescriptorType_(RoleDescriptorType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:SSODescriptorType element"""

    c_tag = "SSODescriptorType"
    c_namespace = NAMESPACE
    c_children = RoleDescriptorType_.c_children.copy()
    c_attributes = RoleDescriptorType_.c_attributes.copy()
    c_child_order = RoleDescriptorType_.c_child_order[:]
    c_cardinality = RoleDescriptorType_.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}ArtifactResolutionService"] = (
        "artifact_resolution_service",
        [ArtifactResolutionService],
    )
    c_cardinality["artifact_resolution_service"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}SingleLogoutService"] = (
        "single_logout_service",
        [SingleLogoutService],
    )
    c_cardinality["single_logout_service"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}ManageNameIDService"] = (
        "manage_name_id_service",
        [ManageNameIDService],
    )
    c_cardinality["manage_name_id_service"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}NameIDFormat"] = ("name_id_format", [NameIDFormat])
    c_cardinality["name_id_format"] = {"min": 0}
    c_child_order.extend(
        ["artifact_resolution_service", "single_logout_service", "manage_name_id_service", "name_id_format"]
    )

    def __init__(
        self,
        artifact_resolution_service=None,
        single_logout_service=None,
        manage_name_id_service=None,
        name_id_format=None,
        signature=None,
        extensions=None,
        key_descriptor=None,
        organization=None,
        contact_person=None,
        id=None,
        valid_until=None,
        cache_duration=None,
        protocol_support_enumeration=None,
        error_url=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        RoleDescriptorType_.__init__(
            self,
            signature=signature,
            extensions=extensions,
            key_descriptor=key_descriptor,
            organization=organization,
            contact_person=contact_person,
            id=id,
            valid_until=valid_until,
            cache_duration=cache_duration,
            protocol_support_enumeration=protocol_support_enumeration,
            error_url=error_url,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.artifact_resolution_service = artifact_resolution_service or []
        self.single_logout_service = single_logout_service or []
        self.manage_name_id_service = manage_name_id_service or []
        self.name_id_format = name_id_format or []


class IDPSSODescriptorType_(SSODescriptorType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:IDPSSODescriptorType element"""

    c_tag = "IDPSSODescriptorType"
    c_namespace = NAMESPACE
    c_children = SSODescriptorType_.c_children.copy()
    c_attributes = SSODescriptorType_.c_attributes.copy()
    c_child_order = SSODescriptorType_.c_child_order[:]
    c_cardinality = SSODescriptorType_.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}SingleSignOnService"] = (
        "single_sign_on_service",
        [SingleSignOnService],
    )
    c_cardinality["single_sign_on_service"] = {"min": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}NameIDMappingService"] = (
        "name_id_mapping_service",
        [NameIDMappingService],
    )
    c_cardinality["name_id_mapping_service"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AssertionIDRequestService"] = (
        "assertion_id_request_service",
        [AssertionIDRequestService],
    )
    c_cardinality["assertion_id_request_service"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AttributeProfile"] = ("attribute_profile", [AttributeProfile])
    c_cardinality["attribute_profile"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:assertion}Attribute"] = ("attribute", [saml.Attribute])
    c_cardinality["attribute"] = {"min": 0}
    c_attributes["WantAuthnRequestsSigned"] = ("want_authn_requests_signed", "boolean", False)
    c_child_order.extend(
        [
            "single_sign_on_service",
            "name_id_mapping_service",
            "assertion_id_request_service",
            "attribute_profile",
            "attribute",
        ]
    )

    def __init__(
        self,
        single_sign_on_service=None,
        name_id_mapping_service=None,
        assertion_id_request_service=None,
        attribute_profile=None,
        attribute=None,
        want_authn_requests_signed=None,
        artifact_resolution_service=None,
        single_logout_service=None,
        manage_name_id_service=None,
        name_id_format=None,
        signature=None,
        extensions=None,
        key_descriptor=None,
        organization=None,
        contact_person=None,
        id=None,
        valid_until=None,
        cache_duration=None,
        protocol_support_enumeration=None,
        error_url=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
        want_authn_requests_only_with_valid_cert=None,
    ):
        SSODescriptorType_.__init__(
            self,
            artifact_resolution_service=artifact_resolution_service,
            single_logout_service=single_logout_service,
            manage_name_id_service=manage_name_id_service,
            name_id_format=name_id_format,
            signature=signature,
            extensions=extensions,
            key_descriptor=key_descriptor,
            organization=organization,
            contact_person=contact_person,
            id=id,
            valid_until=valid_until,
            cache_duration=cache_duration,
            protocol_support_enumeration=protocol_support_enumeration,
            error_url=error_url,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.single_sign_on_service = single_sign_on_service or []
        self.name_id_mapping_service = name_id_mapping_service or []
        self.assertion_id_request_service = assertion_id_request_service or []
        self.attribute_profile = attribute_profile or []
        self.attribute = attribute or []
        self.want_authn_requests_signed = want_authn_requests_signed
        self.want_authn_requests_only_with_valid_cert = want_authn_requests_only_with_valid_cert


def idpsso_descriptor_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(IDPSSODescriptorType_, xml_string)


class AttributeConsumingServiceType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AttributeConsumingServiceType
    element"""

    c_tag = "AttributeConsumingServiceType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}ServiceName"] = ("service_name", [ServiceName])
    c_cardinality["service_name"] = {"min": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}ServiceDescription"] = (
        "service_description",
        [ServiceDescription],
    )
    c_cardinality["service_description"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}RequestedAttribute"] = (
        "requested_attribute",
        [RequestedAttribute],
    )
    c_cardinality["requested_attribute"] = {"min": 1}
    c_attributes["index"] = ("index", "unsignedShort", True)
    c_attributes["isDefault"] = ("is_default", "boolean", False)
    c_child_order.extend(["service_name", "service_description", "requested_attribute"])

    def __init__(
        self,
        service_name=None,
        service_description=None,
        requested_attribute=None,
        index=None,
        is_default=None,
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
        self.service_name = service_name or []
        self.service_description = service_description or []
        self.requested_attribute = requested_attribute or []
        self.index = index
        self.is_default = is_default


def attribute_consuming_service_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributeConsumingServiceType_, xml_string)


class AuthnAuthorityDescriptorType_(RoleDescriptorType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AuthnAuthorityDescriptorType
    element"""

    c_tag = "AuthnAuthorityDescriptorType"
    c_namespace = NAMESPACE
    c_children = RoleDescriptorType_.c_children.copy()
    c_attributes = RoleDescriptorType_.c_attributes.copy()
    c_child_order = RoleDescriptorType_.c_child_order[:]
    c_cardinality = RoleDescriptorType_.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AuthnQueryService"] = ("authn_query_service", [AuthnQueryService])
    c_cardinality["authn_query_service"] = {"min": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AssertionIDRequestService"] = (
        "assertion_id_request_service",
        [AssertionIDRequestService],
    )
    c_cardinality["assertion_id_request_service"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}NameIDFormat"] = ("name_id_format", [NameIDFormat])
    c_cardinality["name_id_format"] = {"min": 0}
    c_child_order.extend(["authn_query_service", "assertion_id_request_service", "name_id_format"])

    def __init__(
        self,
        authn_query_service=None,
        assertion_id_request_service=None,
        name_id_format=None,
        signature=None,
        extensions=None,
        key_descriptor=None,
        organization=None,
        contact_person=None,
        id=None,
        valid_until=None,
        cache_duration=None,
        protocol_support_enumeration=None,
        error_url=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        RoleDescriptorType_.__init__(
            self,
            signature=signature,
            extensions=extensions,
            key_descriptor=key_descriptor,
            organization=organization,
            contact_person=contact_person,
            id=id,
            valid_until=valid_until,
            cache_duration=cache_duration,
            protocol_support_enumeration=protocol_support_enumeration,
            error_url=error_url,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.authn_query_service = authn_query_service or []
        self.assertion_id_request_service = assertion_id_request_service or []
        self.name_id_format = name_id_format or []


def authn_authority_descriptor_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthnAuthorityDescriptorType_, xml_string)


class PDPDescriptorType_(RoleDescriptorType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:PDPDescriptorType element"""

    c_tag = "PDPDescriptorType"
    c_namespace = NAMESPACE
    c_children = RoleDescriptorType_.c_children.copy()
    c_attributes = RoleDescriptorType_.c_attributes.copy()
    c_child_order = RoleDescriptorType_.c_child_order[:]
    c_cardinality = RoleDescriptorType_.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AuthzService"] = ("authz_service", [AuthzService])
    c_cardinality["authz_service"] = {"min": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AssertionIDRequestService"] = (
        "assertion_id_request_service",
        [AssertionIDRequestService],
    )
    c_cardinality["assertion_id_request_service"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}NameIDFormat"] = ("name_id_format", [NameIDFormat])
    c_cardinality["name_id_format"] = {"min": 0}
    c_child_order.extend(["authz_service", "assertion_id_request_service", "name_id_format"])

    def __init__(
        self,
        authz_service=None,
        assertion_id_request_service=None,
        name_id_format=None,
        signature=None,
        extensions=None,
        key_descriptor=None,
        organization=None,
        contact_person=None,
        id=None,
        valid_until=None,
        cache_duration=None,
        protocol_support_enumeration=None,
        error_url=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        RoleDescriptorType_.__init__(
            self,
            signature=signature,
            extensions=extensions,
            key_descriptor=key_descriptor,
            organization=organization,
            contact_person=contact_person,
            id=id,
            valid_until=valid_until,
            cache_duration=cache_duration,
            protocol_support_enumeration=protocol_support_enumeration,
            error_url=error_url,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.authz_service = authz_service or []
        self.assertion_id_request_service = assertion_id_request_service or []
        self.name_id_format = name_id_format or []


def pdp_descriptor_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(PDPDescriptorType_, xml_string)


class AttributeAuthorityDescriptorType_(RoleDescriptorType_):
    """The urn:oasis:names:tc:SAML:2
    .0:metadata:AttributeAuthorityDescriptorType element"""

    c_tag = "AttributeAuthorityDescriptorType"
    c_namespace = NAMESPACE
    c_children = RoleDescriptorType_.c_children.copy()
    c_attributes = RoleDescriptorType_.c_attributes.copy()
    c_child_order = RoleDescriptorType_.c_child_order[:]
    c_cardinality = RoleDescriptorType_.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AttributeService"] = ("attribute_service", [AttributeService])
    c_cardinality["attribute_service"] = {"min": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AssertionIDRequestService"] = (
        "assertion_id_request_service",
        [AssertionIDRequestService],
    )
    c_cardinality["assertion_id_request_service"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}NameIDFormat"] = ("name_id_format", [NameIDFormat])
    c_cardinality["name_id_format"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AttributeProfile"] = ("attribute_profile", [AttributeProfile])
    c_cardinality["attribute_profile"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:assertion}Attribute"] = ("attribute", [saml.Attribute])
    c_cardinality["attribute"] = {"min": 0}
    c_child_order.extend(
        ["attribute_service", "assertion_id_request_service", "name_id_format", "attribute_profile", "attribute"]
    )

    def __init__(
        self,
        attribute_service=None,
        assertion_id_request_service=None,
        name_id_format=None,
        attribute_profile=None,
        attribute=None,
        signature=None,
        extensions=None,
        key_descriptor=None,
        organization=None,
        contact_person=None,
        id=None,
        valid_until=None,
        cache_duration=None,
        protocol_support_enumeration=None,
        error_url=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        RoleDescriptorType_.__init__(
            self,
            signature=signature,
            extensions=extensions,
            key_descriptor=key_descriptor,
            organization=organization,
            contact_person=contact_person,
            id=id,
            valid_until=valid_until,
            cache_duration=cache_duration,
            protocol_support_enumeration=protocol_support_enumeration,
            error_url=error_url,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.attribute_service = attribute_service or []
        self.assertion_id_request_service = assertion_id_request_service or []
        self.name_id_format = name_id_format or []
        self.attribute_profile = attribute_profile or []
        self.attribute = attribute or []


def attribute_authority_descriptor_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributeAuthorityDescriptorType_, xml_string)


class AffiliationDescriptorType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AffiliationDescriptorType
    element"""

    c_tag = "AffiliationDescriptorType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}Signature"] = ("signature", ds.Signature)
    c_cardinality["signature"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}Extensions"] = ("extensions", Extensions)
    c_cardinality["extensions"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AffiliateMember"] = ("affiliate_member", [AffiliateMember])
    c_cardinality["affiliate_member"] = {"min": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}KeyDescriptor"] = ("key_descriptor", [KeyDescriptor])
    c_cardinality["key_descriptor"] = {"min": 0}
    c_attributes["affiliationOwnerID"] = ("affiliation_owner_id", EntityIDType_, True)
    c_attributes["validUntil"] = ("valid_until", "dateTime", False)
    c_attributes["cacheDuration"] = ("cache_duration", "duration", False)
    c_attributes["ID"] = ("id", "ID", False)
    c_child_order.extend(["signature", "extensions", "affiliate_member", "key_descriptor"])

    def __init__(
        self,
        signature=None,
        extensions=None,
        affiliate_member=None,
        key_descriptor=None,
        affiliation_owner_id=None,
        valid_until=None,
        cache_duration=None,
        id=None,
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
        self.signature = signature
        self.extensions = extensions
        self.affiliate_member = affiliate_member or []
        self.key_descriptor = key_descriptor or []
        self.affiliation_owner_id = affiliation_owner_id
        self.valid_until = valid_until
        self.cache_duration = cache_duration
        self.id = id


def affiliation_descriptor_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AffiliationDescriptorType_, xml_string)


class RoleDescriptor(RoleDescriptorType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:RoleDescriptor element"""

    c_tag = "RoleDescriptor"
    c_namespace = NAMESPACE
    c_children = RoleDescriptorType_.c_children.copy()
    c_attributes = RoleDescriptorType_.c_attributes.copy()
    c_child_order = RoleDescriptorType_.c_child_order[:]
    c_cardinality = RoleDescriptorType_.c_cardinality.copy()


def role_descriptor_from_string(xml_string):
    return saml2.create_class_from_xml_string(RoleDescriptor, xml_string)


class IDPSSODescriptor(IDPSSODescriptorType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:IDPSSODescriptor element"""

    c_tag = "IDPSSODescriptor"
    c_namespace = NAMESPACE
    c_children = IDPSSODescriptorType_.c_children.copy()
    c_attributes = IDPSSODescriptorType_.c_attributes.copy()
    c_child_order = IDPSSODescriptorType_.c_child_order[:]
    c_cardinality = IDPSSODescriptorType_.c_cardinality.copy()


def idpsso_descriptor_from_string(xml_string):
    return saml2.create_class_from_xml_string(IDPSSODescriptor, xml_string)


class AttributeConsumingService(AttributeConsumingServiceType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AttributeConsumingService
    element"""

    c_tag = "AttributeConsumingService"
    c_namespace = NAMESPACE
    c_children = AttributeConsumingServiceType_.c_children.copy()
    c_attributes = AttributeConsumingServiceType_.c_attributes.copy()
    c_child_order = AttributeConsumingServiceType_.c_child_order[:]
    c_cardinality = AttributeConsumingServiceType_.c_cardinality.copy()


def attribute_consuming_service_from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributeConsumingService, xml_string)


class AuthnAuthorityDescriptor(AuthnAuthorityDescriptorType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AuthnAuthorityDescriptor
    element"""

    c_tag = "AuthnAuthorityDescriptor"
    c_namespace = NAMESPACE
    c_children = AuthnAuthorityDescriptorType_.c_children.copy()
    c_attributes = AuthnAuthorityDescriptorType_.c_attributes.copy()
    c_child_order = AuthnAuthorityDescriptorType_.c_child_order[:]
    c_cardinality = AuthnAuthorityDescriptorType_.c_cardinality.copy()


def authn_authority_descriptor_from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthnAuthorityDescriptor, xml_string)


class PDPDescriptor(PDPDescriptorType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:PDPDescriptor element"""

    c_tag = "PDPDescriptor"
    c_namespace = NAMESPACE
    c_children = PDPDescriptorType_.c_children.copy()
    c_attributes = PDPDescriptorType_.c_attributes.copy()
    c_child_order = PDPDescriptorType_.c_child_order[:]
    c_cardinality = PDPDescriptorType_.c_cardinality.copy()


def pdp_descriptor_from_string(xml_string):
    return saml2.create_class_from_xml_string(PDPDescriptor, xml_string)


class AttributeAuthorityDescriptor(AttributeAuthorityDescriptorType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AttributeAuthorityDescriptor
    element"""

    c_tag = "AttributeAuthorityDescriptor"
    c_namespace = NAMESPACE
    c_children = AttributeAuthorityDescriptorType_.c_children.copy()
    c_attributes = AttributeAuthorityDescriptorType_.c_attributes.copy()
    c_child_order = AttributeAuthorityDescriptorType_.c_child_order[:]
    c_cardinality = AttributeAuthorityDescriptorType_.c_cardinality.copy()


def attribute_authority_descriptor_from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributeAuthorityDescriptor, xml_string)


class AffiliationDescriptor(AffiliationDescriptorType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:AffiliationDescriptor element"""

    c_tag = "AffiliationDescriptor"
    c_namespace = NAMESPACE
    c_children = AffiliationDescriptorType_.c_children.copy()
    c_attributes = AffiliationDescriptorType_.c_attributes.copy()
    c_child_order = AffiliationDescriptorType_.c_child_order[:]
    c_cardinality = AffiliationDescriptorType_.c_cardinality.copy()


def affiliation_descriptor_from_string(xml_string):
    return saml2.create_class_from_xml_string(AffiliationDescriptor, xml_string)


class SPSSODescriptorType_(SSODescriptorType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:SPSSODescriptorType element"""

    c_tag = "SPSSODescriptorType"
    c_namespace = NAMESPACE
    c_children = SSODescriptorType_.c_children.copy()
    c_attributes = SSODescriptorType_.c_attributes.copy()
    c_child_order = SSODescriptorType_.c_child_order[:]
    c_cardinality = SSODescriptorType_.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AssertionConsumerService"] = (
        "assertion_consumer_service",
        [AssertionConsumerService],
    )
    c_cardinality["assertion_consumer_service"] = {"min": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AttributeConsumingService"] = (
        "attribute_consuming_service",
        [AttributeConsumingService],
    )
    c_cardinality["attribute_consuming_service"] = {"min": 0}
    c_attributes["AuthnRequestsSigned"] = ("authn_requests_signed", "boolean", False)
    c_attributes["WantAssertionsSigned"] = ("want_assertions_signed", "boolean", False)
    c_child_order.extend(["assertion_consumer_service", "attribute_consuming_service"])

    def __init__(
        self,
        assertion_consumer_service=None,
        attribute_consuming_service=None,
        authn_requests_signed=None,
        want_assertions_signed=None,
        artifact_resolution_service=None,
        single_logout_service=None,
        manage_name_id_service=None,
        name_id_format=None,
        signature=None,
        extensions=None,
        key_descriptor=None,
        organization=None,
        contact_person=None,
        id=None,
        valid_until=None,
        cache_duration=None,
        protocol_support_enumeration=None,
        error_url=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SSODescriptorType_.__init__(
            self,
            artifact_resolution_service=artifact_resolution_service,
            single_logout_service=single_logout_service,
            manage_name_id_service=manage_name_id_service,
            name_id_format=name_id_format,
            signature=signature,
            extensions=extensions,
            key_descriptor=key_descriptor,
            organization=organization,
            contact_person=contact_person,
            id=id,
            valid_until=valid_until,
            cache_duration=cache_duration,
            protocol_support_enumeration=protocol_support_enumeration,
            error_url=error_url,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.assertion_consumer_service = assertion_consumer_service or []
        self.attribute_consuming_service = attribute_consuming_service or []
        self.authn_requests_signed = authn_requests_signed
        self.want_assertions_signed = want_assertions_signed


def spsso_descriptor_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SPSSODescriptorType_, xml_string)


class SPSSODescriptor(SPSSODescriptorType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:SPSSODescriptor element"""

    c_tag = "SPSSODescriptor"
    c_namespace = NAMESPACE
    c_children = SPSSODescriptorType_.c_children.copy()
    c_attributes = SPSSODescriptorType_.c_attributes.copy()
    c_child_order = SPSSODescriptorType_.c_child_order[:]
    c_cardinality = SPSSODescriptorType_.c_cardinality.copy()


def spsso_descriptor_from_string(xml_string):
    return saml2.create_class_from_xml_string(SPSSODescriptor, xml_string)


class EntityDescriptorType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:EntityDescriptorType element"""

    c_tag = "EntityDescriptorType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}Signature"] = ("signature", ds.Signature)
    c_cardinality["signature"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}Extensions"] = ("extensions", Extensions)
    c_cardinality["extensions"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptor"] = ("role_descriptor", [RoleDescriptor])
    c_cardinality["role_descriptor"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}IDPSSODescriptor"] = ("idpsso_descriptor", [IDPSSODescriptor])
    c_cardinality["idpsso_descriptor"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}SPSSODescriptor"] = ("spsso_descriptor", [SPSSODescriptor])
    c_cardinality["spsso_descriptor"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AuthnAuthorityDescriptor"] = (
        "authn_authority_descriptor",
        [AuthnAuthorityDescriptor],
    )
    c_cardinality["authn_authority_descriptor"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AttributeAuthorityDescriptor"] = (
        "attribute_authority_descriptor",
        [AttributeAuthorityDescriptor],
    )
    c_cardinality["attribute_authority_descriptor"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}PDPDescriptor"] = ("pdp_descriptor", [PDPDescriptor])
    c_cardinality["pdp_descriptor"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AffiliationDescriptor"] = (
        "affiliation_descriptor",
        AffiliationDescriptor,
    )
    c_cardinality["affiliation_descriptor"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}Organization"] = ("organization", Organization)
    c_cardinality["organization"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}ContactPerson"] = ("contact_person", [ContactPerson])
    c_cardinality["contact_person"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}AdditionalMetadataLocation"] = (
        "additional_metadata_location",
        [AdditionalMetadataLocation],
    )
    c_cardinality["additional_metadata_location"] = {"min": 0}
    c_attributes["entityID"] = ("entity_id", EntityIDType_, True)
    c_attributes["validUntil"] = ("valid_until", "dateTime", False)
    c_attributes["cacheDuration"] = ("cache_duration", "duration", False)
    c_attributes["ID"] = ("id", "ID", False)
    c_child_order.extend(
        [
            "signature",
            "extensions",
            "role_descriptor",
            "idpsso_descriptor",
            "spsso_descriptor",
            "authn_authority_descriptor",
            "attribute_authority_descriptor",
            "pdp_descriptor",
            "affiliation_descriptor",
            "organization",
            "contact_person",
            "additional_metadata_location",
        ]
    )

    def __init__(
        self,
        signature=None,
        extensions=None,
        role_descriptor=None,
        idpsso_descriptor=None,
        spsso_descriptor=None,
        authn_authority_descriptor=None,
        attribute_authority_descriptor=None,
        pdp_descriptor=None,
        affiliation_descriptor=None,
        organization=None,
        contact_person=None,
        additional_metadata_location=None,
        entity_id=None,
        valid_until=None,
        cache_duration=None,
        id=None,
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
        self.signature = signature
        self.extensions = extensions
        self.role_descriptor = role_descriptor or []
        self.idpsso_descriptor = idpsso_descriptor or []
        self.spsso_descriptor = spsso_descriptor or []
        self.authn_authority_descriptor = authn_authority_descriptor or []
        self.attribute_authority_descriptor = attribute_authority_descriptor or []
        self.pdp_descriptor = pdp_descriptor or []
        self.affiliation_descriptor = affiliation_descriptor
        self.organization = organization
        self.contact_person = contact_person or []
        self.additional_metadata_location = additional_metadata_location or []
        self.entity_id = entity_id
        self.valid_until = valid_until
        self.cache_duration = cache_duration
        self.id = id


def entity_descriptor_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(EntityDescriptorType_, xml_string)


class EntityDescriptor(EntityDescriptorType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:EntityDescriptor element"""

    c_tag = "EntityDescriptor"
    c_namespace = NAMESPACE
    c_children = EntityDescriptorType_.c_children.copy()
    c_attributes = EntityDescriptorType_.c_attributes.copy()
    c_child_order = EntityDescriptorType_.c_child_order[:]
    c_cardinality = EntityDescriptorType_.c_cardinality.copy()


def entity_descriptor_from_string(xml_string):
    return saml2.create_class_from_xml_string(EntityDescriptor, xml_string)


# ['EntitiesDescriptor', 'EntitiesDescriptorType']
class EntitiesDescriptorType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:metadata:EntitiesDescriptorType
    element"""

    c_tag = "EntitiesDescriptorType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}Signature"] = ("signature", ds.Signature)
    c_cardinality["signature"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}Extensions"] = ("extensions", Extensions)
    c_cardinality["extensions"] = {"min": 0, "max": 1}
    c_children["{urn:oasis:names:tc:SAML:2.0:metadata}EntityDescriptor"] = ("entity_descriptor", [EntityDescriptor])
    c_cardinality["entity_descriptor"] = {"min": 0}
    c_cardinality["entities_descriptor"] = {"min": 0}
    c_attributes["validUntil"] = ("valid_until", "dateTime", False)
    c_attributes["cacheDuration"] = ("cache_duration", "duration", False)
    c_attributes["ID"] = ("id", "ID", False)
    c_attributes["Name"] = ("name", "string", False)
    c_child_order.extend(["signature", "extensions", "entity_descriptor", "entities_descriptor"])

    def __init__(
        self,
        signature=None,
        extensions=None,
        entity_descriptor=None,
        entities_descriptor=None,
        valid_until=None,
        cache_duration=None,
        id=None,
        name=None,
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
        self.signature = signature
        self.extensions = extensions
        self.entity_descriptor = entity_descriptor or []
        self.entities_descriptor = entities_descriptor or []
        self.valid_until = valid_until
        self.cache_duration = cache_duration
        self.id = id
        self.name = name


def entities_descriptor_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(EntitiesDescriptorType_, xml_string)


class EntitiesDescriptor(EntitiesDescriptorType_):
    """The urn:oasis:names:tc:SAML:2.0:metadata:EntitiesDescriptor element"""

    c_tag = "EntitiesDescriptor"
    c_namespace = NAMESPACE
    c_children = EntitiesDescriptorType_.c_children.copy()
    c_attributes = EntitiesDescriptorType_.c_attributes.copy()
    c_child_order = EntitiesDescriptorType_.c_child_order[:]
    c_cardinality = EntitiesDescriptorType_.c_cardinality.copy()


def entities_descriptor_from_string(xml_string):
    return saml2.create_class_from_xml_string(EntitiesDescriptor, xml_string)


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
EntitiesDescriptorType_.c_children["{urn:oasis:names:tc:SAML:2.0:metadata}EntitiesDescriptor"] = (
    "entities_descriptor",
    [EntitiesDescriptor],
)
EntitiesDescriptor.c_children["{urn:oasis:names:tc:SAML:2.0:metadata}EntitiesDescriptor"] = (
    "entities_descriptor",
    [EntitiesDescriptor],
)
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

ELEMENT_FROM_STRING = {
    EntityIDType_.c_tag: entity_id_type__from_string,
    LocalizedNameType_.c_tag: localized_name_type__from_string,
    LocalizedURIType_.c_tag: localized_uri_type__from_string,
    Extensions.c_tag: extensions_from_string,
    ExtensionsType_.c_tag: extensions_type__from_string,
    EndpointType_.c_tag: endpoint_type__from_string,
    IndexedEndpointType_.c_tag: indexed_endpoint_type__from_string,
    EntitiesDescriptor.c_tag: entities_descriptor_from_string,
    EntitiesDescriptorType_.c_tag: entities_descriptor_type__from_string,
    EntityDescriptor.c_tag: entity_descriptor_from_string,
    EntityDescriptorType_.c_tag: entity_descriptor_type__from_string,
    Organization.c_tag: organization_from_string,
    OrganizationType_.c_tag: organization_type__from_string,
    OrganizationName.c_tag: organization_name_from_string,
    OrganizationDisplayName.c_tag: organization_display_name_from_string,
    OrganizationURL.c_tag: organization_url_from_string,
    ContactPerson.c_tag: contact_person_from_string,
    ContactType_.c_tag: contact_type__from_string,
    Company.c_tag: company_from_string,
    GivenName.c_tag: given_name_from_string,
    SurName.c_tag: sur_name_from_string,
    EmailAddress.c_tag: email_address_from_string,
    TelephoneNumber.c_tag: telephone_number_from_string,
    ContactTypeType_.c_tag: contact_type_type__from_string,
    AdditionalMetadataLocation.c_tag: additional_metadata_location_from_string,
    AdditionalMetadataLocationType_.c_tag: additional_metadata_location_type__from_string,
    RoleDescriptor.c_tag: role_descriptor_from_string,
    AnyURIListType_.c_tag: any_uri_list_type__from_string,
    KeyDescriptor.c_tag: key_descriptor_from_string,
    KeyDescriptorType_.c_tag: key_descriptor_type__from_string,
    KeyTypes_.c_tag: key_types__from_string,
    EncryptionMethod.c_tag: encryption_method_from_string,
    ArtifactResolutionService.c_tag: artifact_resolution_service_from_string,
    SingleLogoutService.c_tag: single_logout_service_from_string,
    ManageNameIDService.c_tag: manage_name_id_service_from_string,
    NameIDFormat.c_tag: name_id_format_from_string,
    IDPSSODescriptor.c_tag: idpsso_descriptor_from_string,
    IDPSSODescriptorType_.c_tag: idpsso_descriptor_type__from_string,
    SingleSignOnService.c_tag: single_sign_on_service_from_string,
    NameIDMappingService.c_tag: name_id_mapping_service_from_string,
    AssertionIDRequestService.c_tag: assertion_id_request_service_from_string,
    AttributeProfile.c_tag: attribute_profile_from_string,
    SPSSODescriptor.c_tag: spsso_descriptor_from_string,
    SPSSODescriptorType_.c_tag: spsso_descriptor_type__from_string,
    AssertionConsumerService.c_tag: assertion_consumer_service_from_string,
    AttributeConsumingService.c_tag: attribute_consuming_service_from_string,
    AttributeConsumingServiceType_.c_tag: attribute_consuming_service_type__from_string,
    ServiceName.c_tag: service_name_from_string,
    ServiceDescription.c_tag: service_description_from_string,
    RequestedAttribute.c_tag: requested_attribute_from_string,
    RequestedAttributeType_.c_tag: requested_attribute_type__from_string,
    AuthnAuthorityDescriptor.c_tag: authn_authority_descriptor_from_string,
    AuthnAuthorityDescriptorType_.c_tag: authn_authority_descriptor_type__from_string,
    AuthnQueryService.c_tag: authn_query_service_from_string,
    PDPDescriptor.c_tag: pdp_descriptor_from_string,
    PDPDescriptorType_.c_tag: pdp_descriptor_type__from_string,
    AuthzService.c_tag: authz_service_from_string,
    AttributeAuthorityDescriptor.c_tag: attribute_authority_descriptor_from_string,
    AttributeAuthorityDescriptorType_.c_tag: attribute_authority_descriptor_type__from_string,
    AttributeService.c_tag: attribute_service_from_string,
    AffiliationDescriptor.c_tag: affiliation_descriptor_from_string,
    AffiliationDescriptorType_.c_tag: affiliation_descriptor_type__from_string,
    AffiliateMember.c_tag: affiliate_member_from_string,
}

ELEMENT_BY_TAG = {
    "entityIDType": EntityIDType_,
    "localizedNameType": LocalizedNameType_,
    "localizedURIType": LocalizedURIType_,
    "Extensions": Extensions,
    "ExtensionsType": ExtensionsType_,
    "EndpointType": EndpointType_,
    "IndexedEndpointType": IndexedEndpointType_,
    "EntitiesDescriptor": EntitiesDescriptor,
    "EntitiesDescriptorType": EntitiesDescriptorType_,
    "EntityDescriptor": EntityDescriptor,
    "EntityDescriptorType": EntityDescriptorType_,
    "Organization": Organization,
    "OrganizationType": OrganizationType_,
    "OrganizationName": OrganizationName,
    "OrganizationDisplayName": OrganizationDisplayName,
    "OrganizationURL": OrganizationURL,
    "ContactPerson": ContactPerson,
    "ContactType": ContactType_,
    "Company": Company,
    "GivenName": GivenName,
    "SurName": SurName,
    "EmailAddress": EmailAddress,
    "TelephoneNumber": TelephoneNumber,
    "ContactTypeType": ContactTypeType_,
    "AdditionalMetadataLocation": AdditionalMetadataLocation,
    "AdditionalMetadataLocationType": AdditionalMetadataLocationType_,
    "RoleDescriptor": RoleDescriptor,
    "anyURIListType": AnyURIListType_,
    "KeyDescriptor": KeyDescriptor,
    "KeyDescriptorType": KeyDescriptorType_,
    "KeyTypes": KeyTypes_,
    "EncryptionMethod": EncryptionMethod,
    "ArtifactResolutionService": ArtifactResolutionService,
    "SingleLogoutService": SingleLogoutService,
    "ManageNameIDService": ManageNameIDService,
    "NameIDFormat": NameIDFormat,
    "IDPSSODescriptor": IDPSSODescriptor,
    "IDPSSODescriptorType": IDPSSODescriptorType_,
    "SingleSignOnService": SingleSignOnService,
    "NameIDMappingService": NameIDMappingService,
    "AssertionIDRequestService": AssertionIDRequestService,
    "AttributeProfile": AttributeProfile,
    "SPSSODescriptor": SPSSODescriptor,
    "SPSSODescriptorType": SPSSODescriptorType_,
    "AssertionConsumerService": AssertionConsumerService,
    "AttributeConsumingService": AttributeConsumingService,
    "AttributeConsumingServiceType": AttributeConsumingServiceType_,
    "ServiceName": ServiceName,
    "ServiceDescription": ServiceDescription,
    "RequestedAttribute": RequestedAttribute,
    "RequestedAttributeType": RequestedAttributeType_,
    "AuthnAuthorityDescriptor": AuthnAuthorityDescriptor,
    "AuthnAuthorityDescriptorType": AuthnAuthorityDescriptorType_,
    "AuthnQueryService": AuthnQueryService,
    "PDPDescriptor": PDPDescriptor,
    "PDPDescriptorType": PDPDescriptorType_,
    "AuthzService": AuthzService,
    "AttributeAuthorityDescriptor": AttributeAuthorityDescriptor,
    "AttributeAuthorityDescriptorType": AttributeAuthorityDescriptorType_,
    "AttributeService": AttributeService,
    "AffiliationDescriptor": AffiliationDescriptor,
    "AffiliationDescriptorType": AffiliationDescriptorType_,
    "AffiliateMember": AffiliateMember,
    "RoleDescriptorType": RoleDescriptorType_,
    "SSODescriptorType": SSODescriptorType_,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)
