#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""Tests for saml2.md"""

__author__ = 'roland.hedberg@umu.se (Roland Hedberg)'

import unittest

try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree

import saml2
from saml2 import xmldsig as ds
from saml2 import saml
from saml2 import samlp
from saml2 import md
from saml2.extension import idpdisc
from saml2.extension import shibmd

from saml2 import extension_element_to_element
import md_data, ds_data


class TestEndpointType:
    def setup_class(self):
        self.endpoint = md.EndpointType_()

    def testAccessors(self):
        """Test for EndpointType accessors"""
        self.endpoint.binding = saml2.BINDING_HTTP_POST
        self.endpoint.location = "http://www.example.com/endpoint"
        self.endpoint.response_location = "http://www.example.com/response"
        print(self.endpoint.__class__.c_attributes.items())
        new_endpoint = md.endpoint_type__from_string(self.endpoint.to_string())
        assert new_endpoint.binding == saml2.BINDING_HTTP_POST
        assert new_endpoint.location == "http://www.example.com/endpoint"
        assert new_endpoint.response_location == \
               "http://www.example.com/response"

    def testUsingTestData(self):
        """Test for endpoint_type_from_string() using test data."""
        new_endpoint = md.endpoint_type__from_string(md_data.TEST_ENDPOINT)
        assert new_endpoint.binding == saml2.BINDING_HTTP_POST
        assert new_endpoint.location == "http://www.example.com/endpoint"
        assert new_endpoint.response_location == \
               "http://www.example.com/response"


class TestIndexedEndpointType:
    def setup_class(self):
        self.i_e = md.IndexedEndpointType_()

    def testAccessors(self):
        """Test for IndexedEndpointType accessors"""
        self.i_e.binding = saml2.BINDING_HTTP_POST
        self.i_e.location = "http://www.example.com/endpoint"
        self.i_e.response_location = "http://www.example.com/response"
        self.i_e.index = "1"
        self.i_e.is_default = "false"
        new_i_e = md.indexed_endpoint_type__from_string(self.i_e.to_string())
        assert new_i_e.binding == saml2.BINDING_HTTP_POST
        assert new_i_e.location == "http://www.example.com/endpoint"
        assert new_i_e.response_location == "http://www.example.com/response"
        assert new_i_e.index == "1"
        assert new_i_e.is_default == "false"

    def testUsingTestData(self):
        """Test for indexed_endpoint_type_from_string() using test data."""
        new_i_e = md.indexed_endpoint_type__from_string(
            md_data.TEST_INDEXED_ENDPOINT)
        assert new_i_e.binding == saml2.BINDING_HTTP_POST
        assert new_i_e.location == "http://www.example.com/endpoint"
        assert new_i_e.response_location == "http://www.example.com/response"
        assert new_i_e.index == "1"
        assert new_i_e.is_default == "false"


class TestExtensions:
    def setup_class(self):
        self.extensions = md.Extensions()

    def testAccessors(self):
        """Test for Extensions accessors"""
        self.extensions.extension_elements.append(
            saml2.extension_element_from_string(
                """<?xml version='1.0' encoding='UTF-8'?>
                <hoge>fuga</hoge>
                """))
        new_extensions = md.extensions_from_string(self.extensions.to_string())
        assert new_extensions.extension_elements[0].tag == "hoge"
        assert new_extensions.extension_elements[0].text.strip() == "fuga"


class TestOrganizationName:
    def setup_class(self):
        self.organization_name = md.OrganizationName()

    def testAccessors(self):
        """Test for OrganizationName accessors"""
        self.organization_name.lang = "en"
        self.organization_name.text = "SIOS Technology, Inc."
        new_organization_name = md.organization_name_from_string(
            self.organization_name.to_string())
        assert new_organization_name.lang == "en"
        assert new_organization_name.text.strip() == "SIOS Technology, Inc."

    def testUsingTestData(self):
        """Test for organization_name_from_string() using test data."""
        new_organization_name = md.organization_name_from_string(
            md_data.TEST_ORGANIZATION_NAME)
        print(new_organization_name.keyswv())
        assert new_organization_name.lang == "se"
        assert new_organization_name.text.strip() == "Catalogix"


class TestOrganizationDisplayName:
    def setup_class(self):
        self.od_name = md.OrganizationDisplayName()

    def testAccessors(self):
        """Test for OrganizationDisplayName accessors"""
        self.od_name.lang = "en"
        self.od_name.text = "SIOS"
        new_od_name = md.organization_display_name_from_string(
            self.od_name.to_string())
        assert new_od_name.lang == "en"
        assert new_od_name.text.strip() == "SIOS"

    def testUsingTestData(self):
        """Test for organization_display_name_from_string() using test data."""
        new_od_name = md.organization_display_name_from_string(
            md_data.TEST_ORGANIZATION_DISPLAY_NAME)
        assert new_od_name.lang == "se"
        assert new_od_name.text.strip() == "Catalogix"


class TestOrganizationURL:
    def setup_class(self):
        self.organization_url = md.OrganizationURL()

    def testAccessors(self):
        """Test for OrganizationURL accessors"""
        self.organization_url.lang = "ja"
        self.organization_url.text = "http://www.example.com/"
        print(self.organization_url.to_string())
        new_organization_url = md.organization_url_from_string(
            self.organization_url.to_string())
        assert new_organization_url.lang == "ja"
        assert new_organization_url.text.strip() == "http://www.example.com/"

    def testUsingTestData(self):
        """Test for organization_url_from_string() using test data."""
        new_organization_url = md.organization_url_from_string(
            md_data.TEST_ORGANIZATION_URL)
        assert new_organization_url.lang == "no"
        assert new_organization_url.text.strip() == "http://www.example.com/"


class TestOrganization:
    def setup_class(self):
        self.organization = md.Organization()

    def testAccessors(self):
        """Test for Organization accessors"""
        self.organization.extensions = md.Extensions()
        self.organization.organization_name.append(
            md.organization_name_from_string(md_data.TEST_ORGANIZATION_NAME))
        self.organization.organization_display_name.append(
            md.organization_display_name_from_string(
                md_data.TEST_ORGANIZATION_DISPLAY_NAME))
        self.organization.organization_url.append(
            md.organization_url_from_string(md_data.TEST_ORGANIZATION_URL))
        new_organization = md.organization_from_string(
            self.organization.to_string())
        assert isinstance(new_organization.extensions, md.Extensions)
        assert isinstance(new_organization.organization_name[0],
                          md.OrganizationName)
        assert isinstance(new_organization.organization_display_name[0],
                          md.OrganizationDisplayName)
        assert isinstance(new_organization.organization_url[0],
                          md.OrganizationURL)
        assert new_organization.organization_name[0].text.strip() == "Catalogix"
        assert new_organization.organization_name[0].lang == "se"
        assert new_organization.organization_display_name[
                   0].text.strip() == "Catalogix"
        assert new_organization.organization_display_name[0].lang == "se"
        assert new_organization.organization_url[
                   0].text.strip() == "http://www.example.com/"
        assert new_organization.organization_url[0].lang == "no"

    def testUsingTestData(self):
        """Test for organization_from_string() using test data."""
        new_organization = md.organization_from_string(
            md_data.TEST_ORGANIZATION)
        assert isinstance(new_organization.extensions, md.Extensions)
        assert isinstance(new_organization.organization_name[0],
                          md.OrganizationName)
        assert isinstance(new_organization.organization_display_name[0],
                          md.OrganizationDisplayName)
        assert isinstance(new_organization.organization_url[0],
                          md.OrganizationURL)
        assert new_organization.organization_name[
                   0].text.strip() == "Catalogix AB"
        assert new_organization.organization_name[0].lang == "se"
        assert new_organization.organization_display_name[
                   0].text.strip() == "Catalogix AS"
        assert new_organization.organization_display_name[0].lang == "no"
        assert new_organization.organization_url[
                   0].text.strip() == "http://www.example.com/"
        assert new_organization.organization_url[0].lang == "en"


class TestContactPerson:
    def setup_class(self):
        self.contact_person = md.ContactPerson()

    def testAccessors(self):
        """Test for ContactPerson accessors"""
        self.contact_person.contact_type = "technical"
        self.contact_person.extensions = md.Extensions()
        self.contact_person.company = md.Company(text="SIOS Technology, Inc.")
        self.contact_person.given_name = md.GivenName(text="Takashi")
        self.contact_person.sur_name = md.SurName(text="Matsuo")
        self.contact_person.email_address.append(
            md.EmailAddress(text="tmatsuo@example.com"))
        self.contact_person.email_address.append(
            md.EmailAddress(text="tmatsuo@shehas.net"))
        self.contact_person.telephone_number.append(
            md.TelephoneNumber(text="00-0000-0000"))
        new_contact_person = md.contact_person_from_string(
            self.contact_person.to_string())
        assert new_contact_person.contact_type == "technical"
        assert isinstance(new_contact_person.extensions, md.Extensions)
        assert new_contact_person.company.text.strip() == "SIOS Technology, " \
                                                          "Inc."
        assert new_contact_person.given_name.text.strip() == "Takashi"
        assert new_contact_person.sur_name.text.strip() == "Matsuo"
        assert new_contact_person.email_address[
                   0].text.strip() == "tmatsuo@example.com"
        assert new_contact_person.email_address[
                   1].text.strip() == "tmatsuo@shehas.net"
        assert new_contact_person.telephone_number[
                   0].text.strip() == "00-0000-0000"

    def testUsingTestData(self):
        """Test for contact_person_from_string() using test data."""
        new_contact_person = md.contact_person_from_string(
            md_data.TEST_CONTACT_PERSON)
        assert new_contact_person.contact_type == "technical"
        assert isinstance(new_contact_person.extensions, md.Extensions)
        assert new_contact_person.company.text.strip() == "SIOS Technology, " \
                                                          "Inc."
        assert new_contact_person.given_name.text.strip() == "Takashi"
        assert new_contact_person.sur_name.text.strip() == "Matsuo"
        assert new_contact_person.email_address[
                   0].text.strip() == "tmatsuo@example.com"
        assert new_contact_person.email_address[
                   1].text.strip() == "tmatsuo@shehas.net"
        assert new_contact_person.telephone_number[
                   0].text.strip() == "00-0000-0000"


class TestAdditionalMetadataLocation:
    def setup_class(self):
        self.additional_metadata_location = md.AdditionalMetadataLocation()

    def testAccessors(self):
        """Test for AdditionalMetadataLocation accessors"""
        self.additional_metadata_location.namespace = (
            "http://www.example.com/namespace")
        self.additional_metadata_location.text = (
            "http://www.example.com/AdditionalMetadataLocation")
        new_additional_metadata_location = \
          md.additional_metadata_location_from_string(
            self.additional_metadata_location.to_string())
        assert new_additional_metadata_location.namespace == \
               "http://www.example.com/namespace"
        assert new_additional_metadata_location.text.strip() == \
               "http://www.example.com/AdditionalMetadataLocation"

    def testUsingTestData(self):
        """Test for additional_metadata_location_from_string() using test
        data."""
        new_additional_metadata_location = \
          md.additional_metadata_location_from_string(
            md_data.TEST_ADDITIONAL_METADATA_LOCATION)
        assert new_additional_metadata_location.namespace == \
               "http://www.example.com/namespace"
        assert new_additional_metadata_location.text.strip() == \
               "http://www.example.com/AdditionalMetadataLocation"


# class TestKeySize:
# 
#   def setup_class(self):
#     self.key_size = md.KeySize()
# 
#   def testAccessors(self):
#     """Test for KeySize accessors"""
#     self.key_size.text = "128"
#     new_key_size = md.key_size_from_string(self.key_size.to_string())
#     assert new_key_size.text.strip() == "128"
# 
#   def testUsingTestData(self):
#     """Test for key_size_from_string() using test data."""
#     new_key_size = md.key_size_from_string(md_data.TEST_KEY_SIZE)
#     assert new_key_size.text.strip() == "128"


# class TestOAEPparams:
# 
#   def setup_class(self):
#     self.oaep_params = md.OAEPparams()
# 
#   def testAccessors(self):
#     """Test for OAEPparams accessors"""
#     self.oaep_params.text = "9lWu3Q=="
#     new_oaep_params = md.oae_pparams_from_string(self.oaep_params.to_string())
#     assert new_oaep_params.text.strip() == "9lWu3Q=="
# 
#   def testUsingTestData(self):
#     """Test for oae_pparams_from_string() using test data."""
#     new_oaep_params = md.oae_pparams_from_string(md_data.TEST_OAEP_PARAMS)
#     assert new_oaep_params.text.strip() == "9lWu3Q=="


class TestEncryptionMethod:
    def setup_class(self):
        self.encryption_method = md.EncryptionMethod()

    def testAccessors(self):
        """Test for EncryptionMethod accessors"""
        self.encryption_method.algorithm = (
            "http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p")
        new_encryption_method = md.encryption_method_from_string(
            self.encryption_method.to_string())
        assert new_encryption_method.algorithm == \
               "http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p"

    def testUsingTestData(self):
        """Test for encryption_method_from_string() using test data."""
        new_encryption_method = md.encryption_method_from_string(
            md_data.TEST_ENCRYPTION_METHOD)
        assert new_encryption_method.algorithm == \
               "http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p"
        assert new_encryption_method.oae_pparams.text.strip() == "9lWu3Q=="


class TestKeyDescriptor:
    def setup_class(self):
        self.key_descriptor = md.KeyDescriptor()

    def testAccessors(self):
        """Test for KeyDescriptor accessors"""

        self.key_descriptor.use = "signing"
        self.key_descriptor.key_info = ds.key_info_from_string(
            ds_data.TEST_KEY_INFO)
        self.key_descriptor.encryption_method.append(
            md.encryption_method_from_string(
                md_data.TEST_ENCRYPTION_METHOD))
        new_key_descriptor = md.key_descriptor_from_string(
            self.key_descriptor.to_string())
        assert new_key_descriptor.use == "signing"
        assert isinstance(new_key_descriptor.key_info, ds.KeyInfo)
        assert isinstance(new_key_descriptor.encryption_method[0],
                          md.EncryptionMethod)

    def testUsingTestData(self):
        """Test for key_descriptor_from_string() using test data."""
        new_key_descriptor = md.key_descriptor_from_string(
            md_data.TEST_KEY_DESCRIPTOR)
        assert new_key_descriptor.use == "signing"
        assert isinstance(new_key_descriptor.key_info, ds.KeyInfo)
        assert isinstance(new_key_descriptor.encryption_method[0],
                          md.EncryptionMethod)


class TestRoleDescriptor:
    def setup_class(self):
        self.role_descriptor = md.RoleDescriptor()

    def testAccessors(self):
        """Test for RoleDescriptor accessors"""
        self.role_descriptor.id = "ID"
        self.role_descriptor.valid_until = "2008-09-14T01:05:02Z"
        self.role_descriptor.cache_duration = "10:00:00:00"
        self.role_descriptor.protocol_support_enumeration = samlp.NAMESPACE
        self.role_descriptor.error_url = "http://www.example.com/errorURL"
        self.role_descriptor.signature = ds.Signature()
        self.role_descriptor.extensions = md.Extensions()
        self.role_descriptor.key_descriptor.append(
            md.key_descriptor_from_string(
                md_data.TEST_KEY_DESCRIPTOR))
        self.role_descriptor.organization = md.Organization()
        self.role_descriptor.contact_person.append(md.ContactPerson())

        new_role_descriptor = md.role_descriptor_from_string(
            self.role_descriptor.to_string())
        assert new_role_descriptor.id == "ID"
        assert new_role_descriptor.valid_until == "2008-09-14T01:05:02Z"
        assert new_role_descriptor.cache_duration == "10:00:00:00"
        assert new_role_descriptor.protocol_support_enumeration == \
               samlp.NAMESPACE
        assert new_role_descriptor.error_url == \
               "http://www.example.com/errorURL"
        assert isinstance(new_role_descriptor.signature, ds.Signature)
        assert isinstance(new_role_descriptor.extensions, md.Extensions)
        assert isinstance(new_role_descriptor.key_descriptor[0],
                          md.KeyDescriptor)
        assert isinstance(new_role_descriptor.organization, md.Organization)
        assert isinstance(new_role_descriptor.contact_person[0],
                          md.ContactPerson)

    def testUsingTestData(self):
        """Test for role_descriptor_from_string() using test data."""
        new_role_descriptor = md.role_descriptor_from_string(
            md_data.TEST_ROLE_DESCRIPTOR)
        assert new_role_descriptor.id == "ID"
        assert new_role_descriptor.valid_until == "2008-09-14T01:05:02Z"
        assert new_role_descriptor.cache_duration == "10:00:00:00"
        assert new_role_descriptor.protocol_support_enumeration == \
               samlp.NAMESPACE
        assert new_role_descriptor.error_url == \
               "http://www.example.com/errorURL"
        assert isinstance(new_role_descriptor.signature, ds.Signature)
        assert isinstance(new_role_descriptor.extensions, md.Extensions)
        assert isinstance(new_role_descriptor.key_descriptor[0],
                          md.KeyDescriptor)
        assert isinstance(new_role_descriptor.organization, md.Organization)
        assert isinstance(new_role_descriptor.contact_person[0],
                          md.ContactPerson)


# class TestSSODescriptor:
#   def setup_class(self):
#     self.sso_descriptor = md.SSODescriptorType_()
# 
#   def testAccessors(self):
#     """Test for SSODescriptorType accessors"""
#     self.sso_descriptor.id = "ID"
#     self.sso_descriptor.valid_until = "2008-09-14T01:05:02Z"
#     self.sso_descriptor.cache_duration = "10:00:00:00"
#     self.sso_descriptor.protocol_support_enumeration = samlp.NAMESPACE
#     self.sso_descriptor.error_url = "http://www.example.com/errorURL"
#     self.sso_descriptor.signature = ds.Signature()
#     self.sso_descriptor.extensions = md.Extensions()
#     self.sso_descriptor.key_descriptor.append(md.key_descriptor_from_string(
#       md_data.TEST_KEY_DESCRIPTOR))
#     self.sso_descriptor.organization = md.Organization()
#     self.sso_descriptor.contact_person.append(md.ContactPerson())
#     self.sso_descriptor.artifact_resolution_service.append(
#       md.ArtifactResolutionService())
#     self.sso_descriptor.single_logout_service.append(
#       md.SingleLogoutService())
#     self.sso_descriptor.manage_name_id_service.append(
#       md.ManageNameIDService())
#     self.sso_descriptor.name_id_format.append(
#       md.NameIDFormat())
# 
#     new_sso_descriptor = md.sso_descriptor_type__from_string(
#       self.sso_descriptor.to_string())
#     assert new_sso_descriptor.id == "ID"
#     assert new_sso_descriptor.valid_until == "2008-09-14T01:05:02Z"
#     assert new_sso_descriptor.cache_duration == "10:00:00:00"
#     assert new_sso_descriptor.protocol_support_enumeration == samlp.NAMESPACE
#     assert new_sso_descriptor.error_url == "http://www.example.com/errorURL"
#     assert isinstance(new_sso_descriptor.signature, ds.Signature)
#     assert isinstance(new_sso_descriptor.extensions, md.Extensions)
#     assert isinstance(new_sso_descriptor.key_descriptor[0],
#                             md.KeyDescriptor)
#     assert isinstance(new_sso_descriptor.organization, md.Organization)
#     assert isinstance(new_sso_descriptor.contact_person[0],
#                             md.ContactPerson)
#     assert isinstance(new_sso_descriptor.artifact_resolution_service[0],
#                             md.ArtifactResolutionService)
#     assert isinstance(new_sso_descriptor.single_logout_service[0],
#                             md.SingleLogoutService)
#     assert isinstance(new_sso_descriptor.manage_name_id_service[0],
#                             md.ManageNameIDService)
#     assert isinstance(new_sso_descriptor.name_id_format[0],
#                             md.NameIDFormat)
# 

class TestArtifactResolutionService:
    def setup_class(self):
        self.i_e = md.ArtifactResolutionService()

    def testAccessors(self):
        """Test for ArtifactResolutionService accessors"""
        self.i_e.binding = saml2.BINDING_HTTP_POST
        self.i_e.location = "http://www.example.com/endpoint"
        self.i_e.response_location = "http://www.example.com/response"
        self.i_e.index = "1"
        self.i_e.is_default = "false"
        new_i_e = md.artifact_resolution_service_from_string(
            self.i_e.to_string())
        assert new_i_e.binding == saml2.BINDING_HTTP_POST
        assert new_i_e.location == "http://www.example.com/endpoint"
        assert new_i_e.response_location == "http://www.example.com/response"
        assert new_i_e.index == "1"
        assert new_i_e.is_default == "false"

    def testUsingTestData(self):
        """Test for artifact_resolution_service_from_string() using test
        data."""
        new_i_e = md.artifact_resolution_service_from_string(
            md_data.TEST_ARTIFACT_RESOLUTION_SERVICE)
        assert new_i_e.binding == saml2.BINDING_HTTP_POST
        assert new_i_e.location == "http://www.example.com/endpoint"
        assert new_i_e.response_location == "http://www.example.com/response"
        assert new_i_e.index == "1"
        assert new_i_e.is_default == "false"


class TestSingleLogout:
    def setup_class(self):
        self.endpoint = md.SingleLogoutService()

    def testAccessors(self):
        """Test for SingleLogoutService accessors"""
        self.endpoint.binding = saml2.BINDING_HTTP_POST
        self.endpoint.location = "http://www.example.com/endpoint"
        self.endpoint.response_location = "http://www.example.com/response"
        new_endpoint = md.single_logout_service_from_string(
            self.endpoint.to_string())
        assert new_endpoint.binding == saml2.BINDING_HTTP_POST
        assert new_endpoint.location == "http://www.example.com/endpoint"
        assert new_endpoint.response_location == \
               "http://www.example.com/response"

    def testUsingTestData(self):
        """Test for single_logout_service_from_string() using test data."""
        new_endpoint = md.single_logout_service_from_string(
            md_data.TEST_SINGLE_LOGOUT_SERVICE)
        assert new_endpoint.binding == saml2.BINDING_HTTP_POST
        assert new_endpoint.location == "http://www.example.com/endpoint"
        assert new_endpoint.response_location == \
               "http://www.example.com/response"


class TestManageNameIDService:
    def setup_class(self):
        self.endpoint = md.ManageNameIDService()

    def testAccessors(self):
        """Test for ManageNameIDService accessors"""
        self.endpoint.binding = saml2.BINDING_HTTP_POST
        self.endpoint.location = "http://www.example.com/endpoint"
        self.endpoint.response_location = "http://www.example.com/response"
        new_endpoint = md.manage_name_id_service_from_string(
            self.endpoint.to_string())
        assert new_endpoint.binding == saml2.BINDING_HTTP_POST
        assert new_endpoint.location == "http://www.example.com/endpoint"
        assert new_endpoint.response_location == \
               "http://www.example.com/response"

    def testUsingTestData(self):
        """Test for manage_name_id_service_from_string() using test data."""
        new_endpoint = md.manage_name_id_service_from_string(
            md_data.TEST_MANAGE_NAMEID_SERVICE)
        assert new_endpoint.binding == saml2.BINDING_HTTP_POST
        assert new_endpoint.location == "http://www.example.com/endpoint"
        assert new_endpoint.response_location == \
               "http://www.example.com/response"


class TestNameIDFormat:
    def setup_class(self):
        self.name_id_format = md.NameIDFormat()

    def testAccessors(self):
        """Test for NameIDFormat accessors"""
        self.name_id_format.text = saml.NAMEID_FORMAT_EMAILADDRESS
        new_name_id_format = md.name_id_format_from_string(
            self.name_id_format.to_string())
        assert new_name_id_format.text.strip() == \
               saml.NAMEID_FORMAT_EMAILADDRESS

    def testUsingTestData(self):
        """Test for name_id_format_from_string() using test data."""
        new_name_id_format = md.name_id_format_from_string(
            md_data.TEST_NAME_ID_FORMAT)
        assert new_name_id_format.text.strip() == \
               saml.NAMEID_FORMAT_EMAILADDRESS


class TestSingleSignOnService:
    def setup_class(self):
        self.endpoint = md.SingleSignOnService()

    def testAccessors(self):
        """Test for SingelSignOnService accessors"""
        self.endpoint.binding = saml2.BINDING_HTTP_POST
        self.endpoint.location = "http://www.example.com/endpoint"
        self.endpoint.response_location = "http://www.example.com/response"
        new_endpoint = md.single_sign_on_service_from_string(
            self.endpoint.to_string())
        assert new_endpoint.binding == saml2.BINDING_HTTP_POST
        assert new_endpoint.location == "http://www.example.com/endpoint"
        assert new_endpoint.response_location == \
               "http://www.example.com/response"

    def testUsingTestData(self):
        """Test for SingelSignOn_service_from_string() using test data."""
        new_endpoint = md.single_sign_on_service_from_string(
            md_data.TEST_SINGLE_SIGN_ON_SERVICE)
        assert new_endpoint.binding == saml2.BINDING_HTTP_POST
        assert new_endpoint.location == "http://www.example.com/endpoint"
        assert new_endpoint.response_location == \
               "http://www.example.com/response"


class TestNameIDMappingService:
    def setup_class(self):
        self.endpoint = md.NameIDMappingService()

    def testAccessors(self):
        """Test for NameIDMappingService accessors"""
        self.endpoint.binding = saml2.BINDING_HTTP_POST
        self.endpoint.location = "http://www.example.com/endpoint"
        self.endpoint.response_location = "http://www.example.com/response"
        new_endpoint = md.name_id_mapping_service_from_string(
            self.endpoint.to_string())
        assert new_endpoint.binding == saml2.BINDING_HTTP_POST
        assert new_endpoint.location == "http://www.example.com/endpoint"
        assert new_endpoint.response_location == \
               "http://www.example.com/response"

    def testUsingTestData(self):
        """Test for name_id_mapping_service_from_string() using test data."""
        new_endpoint = md.name_id_mapping_service_from_string(
            md_data.TEST_NAME_ID_MAPPING_SERVICE)
        assert new_endpoint.binding == saml2.BINDING_HTTP_POST
        assert new_endpoint.location == "http://www.example.com/endpoint"
        assert new_endpoint.response_location == \
               "http://www.example.com/response"


class TestAssertionIDRequestService:
    def setup_class(self):
        self.endpoint = md.AssertionIDRequestService()

    def testAccessors(self):
        """Test for AssertionIDRequestService accessors"""
        self.endpoint.binding = saml2.BINDING_HTTP_POST
        self.endpoint.location = "http://www.example.com/endpoint"
        self.endpoint.response_location = "http://www.example.com/response"
        new_endpoint = md.assertion_id_request_service_from_string(
            self.endpoint.to_string())
        assert new_endpoint.binding == saml2.BINDING_HTTP_POST
        assert new_endpoint.location == "http://www.example.com/endpoint"
        assert new_endpoint.response_location == \
               "http://www.example.com/response"

    def testUsingTestData(self):
        """Test for assertion_id_request_service_from_string() using test
        data."""
        new_endpoint = md.assertion_id_request_service_from_string(
            md_data.TEST_ASSERTION_ID_REQUEST_SERVICE)
        assert new_endpoint.binding == saml2.BINDING_HTTP_POST
        assert new_endpoint.location == "http://www.example.com/endpoint"
        assert new_endpoint.response_location == \
               "http://www.example.com/response"


class TestAttributeProfile:
    def setup_class(self):
        self.attribute_profile = md.AttributeProfile()

    def testAccessors(self):
        """Test for AttributeProfile accessors"""
        self.attribute_profile.text = saml.PROFILE_ATTRIBUTE_BASIC
        new_attribute_profile = md.attribute_profile_from_string(
            self.attribute_profile.to_string())
        assert new_attribute_profile.text.strip() == \
               saml.PROFILE_ATTRIBUTE_BASIC

    def testUsingTestData(self):
        """Test for name_id_format_from_string() using test data."""
        new_attribute_profile = md.attribute_profile_from_string(
            md_data.TEST_ATTRIBUTE_PROFILE)
        assert new_attribute_profile.text.strip() == \
               saml.PROFILE_ATTRIBUTE_BASIC


class TestIDPSSODescriptor:
    def setup_class(self):
        self.idp_sso_descriptor = md.IDPSSODescriptor()

    def testAccessors(self):
        """Test for IDPSSODescriptor accessors"""
        self.idp_sso_descriptor.id = "ID"
        self.idp_sso_descriptor.valid_until = "2008-09-14T01:05:02Z"
        self.idp_sso_descriptor.cache_duration = "10:00:00:00"
        self.idp_sso_descriptor.protocol_support_enumeration = \
            samlp.NAMESPACE
        self.idp_sso_descriptor.error_url = "http://www.example.com/errorURL"
        self.idp_sso_descriptor.signature = ds.Signature()
        self.idp_sso_descriptor.extensions = md.Extensions()
        self.idp_sso_descriptor.key_descriptor.append(
            md.key_descriptor_from_string(
                md_data.TEST_KEY_DESCRIPTOR))
        self.idp_sso_descriptor.organization = md.Organization()
        self.idp_sso_descriptor.contact_person.append(md.ContactPerson())
        self.idp_sso_descriptor.artifact_resolution_service.append(
            md.ArtifactResolutionService())
        self.idp_sso_descriptor.single_logout_service.append(
            md.SingleLogoutService())
        self.idp_sso_descriptor.manage_name_id_service.append(
            md.ManageNameIDService())
        self.idp_sso_descriptor.name_id_format.append(
            md.NameIDFormat())
        self.idp_sso_descriptor.want_authn_requests_signed = 'true'
        self.idp_sso_descriptor.single_sign_on_service.append(
            md.SingleSignOnService())
        self.idp_sso_descriptor.name_id_mapping_service.append(
            md.NameIDMappingService())
        self.idp_sso_descriptor.assertion_id_request_service.append(
            md.AssertionIDRequestService())
        self.idp_sso_descriptor.attribute_profile.append(
            md.AttributeProfile())
        self.idp_sso_descriptor.attribute.append(saml.Attribute())

        new_idp_sso_descriptor = md.idpsso_descriptor_from_string(
            self.idp_sso_descriptor.to_string())
        assert new_idp_sso_descriptor.id == "ID"
        assert new_idp_sso_descriptor.valid_until == "2008-09-14T01:05:02Z"
        assert new_idp_sso_descriptor.cache_duration == "10:00:00:00"
        assert new_idp_sso_descriptor.protocol_support_enumeration == \
               samlp.NAMESPACE
        assert new_idp_sso_descriptor.error_url == \
               "http://www.example.com/errorURL"
        assert isinstance(new_idp_sso_descriptor.signature, ds.Signature)
        assert isinstance(new_idp_sso_descriptor.extensions, md.Extensions)
        assert isinstance(new_idp_sso_descriptor.key_descriptor[0],
                          md.KeyDescriptor)
        assert isinstance(new_idp_sso_descriptor.organization,
                          md.Organization)
        assert isinstance(new_idp_sso_descriptor.contact_person[0],
                          md.ContactPerson)
        assert isinstance(
            new_idp_sso_descriptor.artifact_resolution_service[0],
            md.ArtifactResolutionService)
        assert isinstance(new_idp_sso_descriptor.single_logout_service[0],
                          md.SingleLogoutService)
        assert isinstance(new_idp_sso_descriptor.manage_name_id_service[0],
                          md.ManageNameIDService)
        assert isinstance(new_idp_sso_descriptor.name_id_format[0],
                          md.NameIDFormat)
        assert new_idp_sso_descriptor.want_authn_requests_signed == "true"
        assert isinstance(new_idp_sso_descriptor.single_sign_on_service[0],
                          md.SingleSignOnService)
        assert isinstance(new_idp_sso_descriptor.name_id_mapping_service[0],
                          md.NameIDMappingService)
        assert isinstance(
            new_idp_sso_descriptor.assertion_id_request_service[0],
            md.AssertionIDRequestService)
        assert isinstance(new_idp_sso_descriptor.attribute_profile[0],
                          md.AttributeProfile)
        assert isinstance(new_idp_sso_descriptor.attribute[0],
                          saml.Attribute)

    def testUsingTestData(self):
        """Test for idpsso_descriptor_from_string() using test data."""
        new_idp_sso_descriptor = md.idpsso_descriptor_from_string(
            md_data.TEST_IDP_SSO_DESCRIPTOR)
        assert new_idp_sso_descriptor.id == "ID"
        assert new_idp_sso_descriptor.valid_until == "2008-09-14T01:05:02Z"
        assert new_idp_sso_descriptor.cache_duration == "10:00:00:00"
        assert new_idp_sso_descriptor.protocol_support_enumeration == \
               samlp.NAMESPACE
        assert new_idp_sso_descriptor.error_url == \
               "http://www.example.com/errorURL"
        assert isinstance(new_idp_sso_descriptor.signature, ds.Signature)
        assert isinstance(new_idp_sso_descriptor.extensions, md.Extensions)
        assert isinstance(new_idp_sso_descriptor.key_descriptor[0],
                          md.KeyDescriptor)
        assert isinstance(new_idp_sso_descriptor.organization,
                          md.Organization)
        assert isinstance(new_idp_sso_descriptor.contact_person[0],
                          md.ContactPerson)
        assert isinstance(
            new_idp_sso_descriptor.artifact_resolution_service[0],
            md.ArtifactResolutionService)
        assert isinstance(new_idp_sso_descriptor.single_logout_service[0],
                          md.SingleLogoutService)
        assert isinstance(new_idp_sso_descriptor.manage_name_id_service[0],
                          md.ManageNameIDService)
        assert isinstance(new_idp_sso_descriptor.name_id_format[0],
                          md.NameIDFormat)
        assert new_idp_sso_descriptor.want_authn_requests_signed == "true"
        assert isinstance(new_idp_sso_descriptor.single_sign_on_service[0],
                          md.SingleSignOnService)
        assert isinstance(new_idp_sso_descriptor.name_id_mapping_service[0],
                          md.NameIDMappingService)
        assert isinstance(
            new_idp_sso_descriptor.assertion_id_request_service[0],
            md.AssertionIDRequestService)
        assert isinstance(new_idp_sso_descriptor.attribute_profile[0],
                          md.AttributeProfile)
        assert isinstance(new_idp_sso_descriptor.attribute[0],
                          saml.Attribute)

    def testUsingScope(self):
        descriptor = md.IDPSSODescriptor()
        scope = shibmd.Scope()
        scope.text = "example.org"
        scope.regexp = "false"
        descriptor.extensions = md.Extensions()
        ext = saml2.element_to_extension_element(scope)
        descriptor.extensions.extension_elements.append(ext)
        exts = descriptor.extensions
        assert len(exts.extension_elements) == 1
        elem = exts.extension_elements[0]
        inst = saml2.extension_element_to_element(elem,
                                                  shibmd.ELEMENT_FROM_STRING,
                                                  namespace=shibmd.NAMESPACE)
        assert isinstance(inst, shibmd.Scope)
        assert inst.text == "example.org"
        assert inst.regexp == "false"


class TestAssertionConsumerService:
    def setup_class(self):
        self.i_e = md.AssertionConsumerService()

    def testAccessors(self):
        """Test for AssertionConsumerService accessors"""
        self.i_e.binding = saml2.BINDING_HTTP_POST
        self.i_e.location = "http://www.example.com/endpoint"
        self.i_e.response_location = "http://www.example.com/response"
        self.i_e.index = "1"
        self.i_e.is_default = "false"
        new_i_e = md.assertion_consumer_service_from_string(
            self.i_e.to_string())
        assert new_i_e.binding == saml2.BINDING_HTTP_POST
        assert new_i_e.location == "http://www.example.com/endpoint"
        assert new_i_e.response_location == "http://www.example.com/response"
        assert new_i_e.index == "1"
        assert new_i_e.is_default == "false"

    def testUsingTestData(self):
        """Test for assertion_consumer_service_from_string() using test data."""
        new_i_e = md.assertion_consumer_service_from_string(
            md_data.TEST_ASSERTION_CONSUMER_SERVICE)
        assert new_i_e.binding == saml2.BINDING_HTTP_POST
        assert new_i_e.location == "http://www.example.com/endpoint"
        assert new_i_e.response_location == "http://www.example.com/response"
        assert new_i_e.index == "1"
        assert new_i_e.is_default == "false"


class TestRequestedAttribute:
    def setup_class(self):
        self.requested_attribute = md.RequestedAttribute()

    def testAccessors(self):
        """Test for RequestedAttribute accessors"""
        assert isinstance(self.requested_attribute, saml.AttributeType_)
        assert isinstance(self.requested_attribute, md.RequestedAttribute)
        assert self.requested_attribute.is_required is None
        self.requested_attribute.is_required = "true"
        new_requested_attribute = md.requested_attribute_from_string(
            self.requested_attribute.to_string())
        assert new_requested_attribute.is_required == "true"
        assert isinstance(new_requested_attribute, saml.AttributeType_)
        assert isinstance(new_requested_attribute, md.RequestedAttribute)

    def testUsingTestData(self):
        """Test for requested_attribute_from_string() using test data."""
        new_requested_attribute = md.requested_attribute_from_string(
            md_data.TEST_REQUESTED_ATTRIBUTE)
        assert new_requested_attribute.is_required == "true"
        assert isinstance(new_requested_attribute, saml.AttributeType_)
        assert isinstance(new_requested_attribute, md.RequestedAttribute)


class TestServiceName:
    def setup_class(self):
        self.service_name = md.ServiceName()

    def testAccessors(self):
        """Test for ServiceName accessors"""
        self.service_name.lang = "en"
        self.service_name.text = "SIOS mail"
        new_service_name = md.service_name_from_string(
            self.service_name.to_string())
        assert new_service_name.lang == "en"
        assert new_service_name.text.strip() == "SIOS mail"

    def testUsingTestData(self):
        """Test for organization_name_from_string() using test data."""
        new_service_name = md.service_name_from_string(
            md_data.TEST_SERVICE_NAME)
        assert new_service_name.lang == "en"
        assert new_service_name.text.strip() == "Catalogix Whois"


class TestServiceDescription:
    def setup_class(self):
        self.service_description = md.ServiceDescription()

    def testAccessors(self):
        """Test for ServiceDescription accessors"""
        self.service_description.lang = "en"
        self.service_description.text = "SIOS mail service"
        new_service_description = md.service_description_from_string(
            self.service_description.to_string())
        assert new_service_description.lang == "en"
        assert new_service_description.text.strip() == "SIOS mail service"

    def testUsingTestData(self):
        """Test for organization_name_from_string() using test data."""
        new_service_description = md.service_description_from_string(
            md_data.TEST_SERVICE_DESCRIPTION)
        assert new_service_description.lang == "en"
        assert new_service_description.text.strip() == "Catalogix Whois Service"


class TestAttributeConsumingService:
    def setup_class(self):
        self.attribute_consuming_service = md.AttributeConsumingService()

    def testAccessors(self):
        """Test for AttributeConsumingService accessors"""
        self.attribute_consuming_service.service_name.append(md.ServiceName())
        self.attribute_consuming_service.service_description.append(
            md.ServiceDescription())
        self.attribute_consuming_service.requested_attribute.append(
            md.RequestedAttribute())
        self.attribute_consuming_service.index = "1"
        self.attribute_consuming_service.is_default = "true"

        new_attribute_consuming_service = \
          md.attribute_consuming_service_from_string(
            self.attribute_consuming_service.to_string())
        assert new_attribute_consuming_service.index == "1"
        assert new_attribute_consuming_service.is_default == "true"
        assert isinstance(new_attribute_consuming_service.service_name[0],
                          md.ServiceName)
        assert isinstance(
            new_attribute_consuming_service.service_description[0],
            md.ServiceDescription)
        assert isinstance(
            new_attribute_consuming_service.requested_attribute[0],
            md.RequestedAttribute)

    def testUsingTestData(self):
        """Test for attribute_consuming_service_from_string() using test
        data."""
        new_attribute_consuming_service = \
          md.attribute_consuming_service_from_string(
            md_data.TEST_ATTRIBUTE_CONSUMING_SERVICE)
        assert new_attribute_consuming_service.index == "1"
        assert new_attribute_consuming_service.is_default == "true"
        assert isinstance(new_attribute_consuming_service.service_name[0],
                          md.ServiceName)
        assert isinstance(
            new_attribute_consuming_service.service_description[0],
            md.ServiceDescription)
        assert isinstance(
            new_attribute_consuming_service.requested_attribute[0],
            md.RequestedAttribute)


class TestSPSSODescriptor:
    def setup_class(self):
        self.sp_sso_descriptor = md.SPSSODescriptor()

    def testAccessors(self):
        """Test for SPSSODescriptor accessors"""
        self.sp_sso_descriptor.id = "ID"
        self.sp_sso_descriptor.valid_until = "2008-09-14T01:05:02Z"
        self.sp_sso_descriptor.cache_duration = "10:00:00:00"
        self.sp_sso_descriptor.protocol_support_enumeration = \
            samlp.NAMESPACE
        self.sp_sso_descriptor.error_url = "http://www.example.com/errorURL"
        self.sp_sso_descriptor.signature = ds.Signature()
        self.sp_sso_descriptor.extensions = md.Extensions()
        self.sp_sso_descriptor.key_descriptor.append(
            md.key_descriptor_from_string(
                md_data.TEST_KEY_DESCRIPTOR))
        self.sp_sso_descriptor.organization = md.Organization()
        self.sp_sso_descriptor.contact_person.append(md.ContactPerson())
        self.sp_sso_descriptor.artifact_resolution_service.append(
            md.ArtifactResolutionService())
        self.sp_sso_descriptor.single_logout_service.append(
            md.SingleLogoutService())
        self.sp_sso_descriptor.manage_name_id_service.append(
            md.ManageNameIDService())
        self.sp_sso_descriptor.name_id_format.append(
            md.NameIDFormat())
        self.sp_sso_descriptor.authn_requests_signed = "true"
        self.sp_sso_descriptor.want_assertions_signed = "true"
        self.sp_sso_descriptor.assertion_consumer_service.append(
            md.AssertionConsumerService())
        self.sp_sso_descriptor.attribute_consuming_service.append(
            md.AttributeConsumingService())

        print(self.sp_sso_descriptor)
        new_sp_sso_descriptor = md.spsso_descriptor_from_string(
            self.sp_sso_descriptor.to_string())
        print(new_sp_sso_descriptor)
        assert new_sp_sso_descriptor.id == "ID"
        assert new_sp_sso_descriptor.valid_until == "2008-09-14T01:05:02Z"
        assert new_sp_sso_descriptor.cache_duration == "10:00:00:00"
        assert new_sp_sso_descriptor.protocol_support_enumeration == \
               samlp.NAMESPACE
        assert new_sp_sso_descriptor.error_url == \
               "http://www.example.com/errorURL"
        assert isinstance(new_sp_sso_descriptor.signature, ds.Signature)
        assert isinstance(new_sp_sso_descriptor.extensions, md.Extensions)
        assert isinstance(new_sp_sso_descriptor.key_descriptor[0],
                          md.KeyDescriptor)
        assert isinstance(new_sp_sso_descriptor.organization,
                          md.Organization)
        assert isinstance(new_sp_sso_descriptor.contact_person[0],
                          md.ContactPerson)
        assert isinstance(
            new_sp_sso_descriptor.artifact_resolution_service[0],
            md.ArtifactResolutionService)
        assert isinstance(new_sp_sso_descriptor.single_logout_service[0],
                          md.SingleLogoutService)
        assert isinstance(new_sp_sso_descriptor.manage_name_id_service[0],
                          md.ManageNameIDService)
        assert isinstance(new_sp_sso_descriptor.name_id_format[0],
                          md.NameIDFormat)
        assert new_sp_sso_descriptor.authn_requests_signed == "true"
        assert new_sp_sso_descriptor.want_assertions_signed == "true"
        assert isinstance(
            new_sp_sso_descriptor.assertion_consumer_service[0],
            md.AssertionConsumerService)
        assert isinstance(
            new_sp_sso_descriptor.attribute_consuming_service[0],
            md.AttributeConsumingService)

    def testUsingTestData(self):
        """Test for spsso_descriptor_from_string() using test data."""
        new_sp_sso_descriptor = md.spsso_descriptor_from_string(
            md_data.TEST_SP_SSO_DESCRIPTOR)
        assert new_sp_sso_descriptor.id == "ID"
        assert new_sp_sso_descriptor.valid_until == "2008-09-14T01:05:02Z"
        assert new_sp_sso_descriptor.cache_duration == "10:00:00:00"
        assert new_sp_sso_descriptor.protocol_support_enumeration == \
               samlp.NAMESPACE
        assert new_sp_sso_descriptor.error_url == \
               "http://www.example.com/errorURL"
        assert isinstance(new_sp_sso_descriptor.signature, ds.Signature)
        assert isinstance(new_sp_sso_descriptor.extensions, md.Extensions)
        print(new_sp_sso_descriptor.extensions.__dict__)
        assert len(new_sp_sso_descriptor.extensions.extension_elements) == 2
        for eelem in new_sp_sso_descriptor.extensions.extension_elements:
            print("EE", eelem.__dict__)
            dp = extension_element_to_element(eelem,
                                              idpdisc.ELEMENT_FROM_STRING,
                                              idpdisc.NAMESPACE)
            print("DP", dp.c_tag, dp.c_namespace, dp.__dict__)
            assert isinstance(dp, idpdisc.DiscoveryResponse)
        assert isinstance(new_sp_sso_descriptor.key_descriptor[0],
                          md.KeyDescriptor)
        assert isinstance(new_sp_sso_descriptor.organization,
                          md.Organization)
        assert isinstance(new_sp_sso_descriptor.contact_person[0],
                          md.ContactPerson)
        assert isinstance(
            new_sp_sso_descriptor.artifact_resolution_service[0],
            md.ArtifactResolutionService)
        assert isinstance(new_sp_sso_descriptor.single_logout_service[0],
                          md.SingleLogoutService)
        assert isinstance(new_sp_sso_descriptor.manage_name_id_service[0],
                          md.ManageNameIDService)
        assert isinstance(new_sp_sso_descriptor.name_id_format[0],
                          md.NameIDFormat)
        assert new_sp_sso_descriptor.authn_requests_signed == "true"
        assert new_sp_sso_descriptor.want_assertions_signed == "true"
        assert isinstance(
            new_sp_sso_descriptor.assertion_consumer_service[0],
            md.AssertionConsumerService)
        assert isinstance(
            new_sp_sso_descriptor.attribute_consuming_service[0],
            md.AttributeConsumingService)


class TestEntityDescriptor:
    def setup_class(self):
        self.entity_descriptor = md.EntityDescriptor()

    def testAccessors(self):
        """Test for RoleDescriptor accessors"""
        self.entity_descriptor.id = "ID"
        self.entity_descriptor.entity_id = "entityID"
        self.entity_descriptor.valid_until = "2008-09-14T01:05:02Z"
        self.entity_descriptor.cache_duration = "10:00:00:00"

        self.entity_descriptor.signature = ds.Signature()
        self.entity_descriptor.extensions = md.Extensions()
        self.entity_descriptor.role_descriptor.append(md.RoleDescriptor())
        self.entity_descriptor.idpsso_descriptor.append(md.IDPSSODescriptor())
        self.entity_descriptor.spsso_descriptor.append(md.SPSSODescriptor())
        self.entity_descriptor.organization = md.Organization()
        self.entity_descriptor.contact_person.append(md.ContactPerson())
        self.entity_descriptor.additional_metadata_location.append(
            md.AdditionalMetadataLocation())

        new_entity_descriptor = md.entity_descriptor_from_string(
            self.entity_descriptor.to_string())
        assert new_entity_descriptor.id == "ID"
        assert new_entity_descriptor.entity_id == "entityID"
        assert new_entity_descriptor.valid_until == "2008-09-14T01:05:02Z"
        assert new_entity_descriptor.cache_duration == "10:00:00:00"
        assert isinstance(new_entity_descriptor.signature, ds.Signature)
        assert isinstance(new_entity_descriptor.extensions, md.Extensions)
        assert isinstance(new_entity_descriptor.role_descriptor[0],
                          md.RoleDescriptor)
        assert isinstance(new_entity_descriptor.idpsso_descriptor[0],
                          md.IDPSSODescriptor)
        assert isinstance(new_entity_descriptor.spsso_descriptor[0],
                          md.SPSSODescriptor)
        assert isinstance(new_entity_descriptor.organization,
                          md.Organization)
        assert isinstance(new_entity_descriptor.contact_person[0],
                          md.ContactPerson)
        assert isinstance(
            new_entity_descriptor.additional_metadata_location[0],
            md.AdditionalMetadataLocation)

    def testUsingTestData(self):
        """Test for entity_descriptor_from_string() using test data."""
        new_entity_descriptor = md.entity_descriptor_from_string(
            md_data.TEST_ENTITY_DESCRIPTOR)
        assert new_entity_descriptor.id == "ID"
        assert new_entity_descriptor.entity_id == "entityID"
        assert new_entity_descriptor.valid_until == "2008-09-14T01:05:02Z"
        assert new_entity_descriptor.cache_duration == "10:00:00:00"
        assert isinstance(new_entity_descriptor.signature, ds.Signature)
        assert isinstance(new_entity_descriptor.extensions, md.Extensions)
        assert isinstance(new_entity_descriptor.role_descriptor[0],
                          md.RoleDescriptor)
        assert isinstance(new_entity_descriptor.idpsso_descriptor[0],
                          md.IDPSSODescriptor)
        assert isinstance(new_entity_descriptor.spsso_descriptor[0],
                          md.SPSSODescriptor)
        assert isinstance(new_entity_descriptor.organization,
                          md.Organization)
        assert isinstance(new_entity_descriptor.contact_person[0],
                          md.ContactPerson)
        assert isinstance(new_entity_descriptor.additional_metadata_location[0],
                          md.AdditionalMetadataLocation)


class TestEntitiesDescriptor:
    def setup_class(self):
        self.entities_descriptor = md.EntitiesDescriptor()

    def testAccessors(self):
        """Test for EntitiesDescriptor accessors"""
        self.entities_descriptor.id = "ID"
        self.entities_descriptor.name = "name"
        self.entities_descriptor.valid_until = "2008-09-14T01:05:02Z"
        self.entities_descriptor.cache_duration = "10:00:00:00"

        self.entities_descriptor.signature = ds.Signature()
        self.entities_descriptor.extensions = md.Extensions()
        self.entities_descriptor.entity_descriptor.append(md.EntityDescriptor())
        self.entities_descriptor.entities_descriptor.append(
            md.EntitiesDescriptor())

        new_entities_descriptor = md.entities_descriptor_from_string(
            self.entities_descriptor.to_string())
        assert new_entities_descriptor.id == "ID"
        assert new_entities_descriptor.name == "name"
        assert new_entities_descriptor.valid_until == "2008-09-14T01:05:02Z"
        assert new_entities_descriptor.cache_duration == "10:00:00:00"
        assert isinstance(new_entities_descriptor.signature, ds.Signature)
        assert isinstance(new_entities_descriptor.extensions, md.Extensions)
        assert isinstance(new_entities_descriptor.entity_descriptor[0],
                          md.EntityDescriptor)
        assert isinstance(new_entities_descriptor.entities_descriptor[0],
                          md.EntitiesDescriptor)

    def testUsingTestData(self):
        """Test for entities_descriptor_from_string() using test data."""
        new_entities_descriptor = md.entities_descriptor_from_string(
            md_data.TEST_ENTITIES_DESCRIPTOR)
        assert new_entities_descriptor.id == "ID"
        assert new_entities_descriptor.name == "name"
        assert new_entities_descriptor.valid_until == "2008-09-14T01:05:02Z"
        assert new_entities_descriptor.cache_duration == "10:00:00:00"
        assert isinstance(new_entities_descriptor.signature, ds.Signature)
        assert isinstance(new_entities_descriptor.extensions, md.Extensions)
        assert isinstance(new_entities_descriptor.entity_descriptor[0],
                          md.EntityDescriptor)
        assert isinstance(new_entities_descriptor.entities_descriptor[0],
                          md.EntitiesDescriptor)


if __name__ == "__main__":
    c = TestIDPSSODescriptor()
    c.setup_class()
    c.testAccessors()