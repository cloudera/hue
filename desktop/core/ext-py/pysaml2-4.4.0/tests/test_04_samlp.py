#!/usr/bin/env pythony
# -*- coding: utf-8 -*-
#

"""Tests for saml2.samlp"""

__author__ = 'roland.hedberg@adm.umu.se (Roland Hedberg)'

try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import saml2

import samlp_data

from saml2 import saml
from saml2 import samlp
from saml2 import xmldsig as ds


# class TestRequestAbstractType:
# 
#     def setup_class(self):
#         self.ar = samlp.RequestAbstractType_()
# 
#     def testAccessors(self):
#         """Test for RequestAbstractType accessors"""
#         self.ar.id = "request id"
#         self.ar.version = saml2.VERSION
#         self.ar.issue_instant = "2007-09-14T01:05:02Z"
#         self.ar.destination = "http://www.example.com/Destination"
#         self.ar.consent = saml.CONSENT_UNSPECIFIED
#         self.ar.issuer = saml.Issuer()
#         self.ar.signature = ds.Signature()
#         self.ar.extensions = samlp.Extensions()
# 
#         new_ar = samlp.request_abstract_type__from_string(self.ar.to_string())
#         assert new_ar.id == "request id"
#         assert new_ar.version == saml2.VERSION
#         assert new_ar.issue_instant == "2007-09-14T01:05:02Z"
#         assert new_ar.destination == "http://www.example.com/Destination"
#         assert new_ar.consent == saml.CONSENT_UNSPECIFIED
#         assert isinstance(new_ar.issuer, saml.Issuer)
#         assert isinstance(new_ar.signature, ds.Signature)
#         assert isinstance(new_ar.extensions, samlp.Extensions)
#         
#     def testUsingTestData(self):
#         """Test for request_abstract_type_from_string() using test data"""
#         # TODO:
#         pass

class TestStatusDetail:

    def setup_class(self):
        self.status_detail = samlp.StatusDetail()

    def testAccessors(self):
        """Test for StatusDetail accessors"""
        # TODO:
        pass
    

class TestStatusMessage:

    def setup_class(self):
        self.status_message = samlp.StatusMessage()

    def testAccessors(self):
        """Test for StatusMessage accessors"""
        # TODO:
        pass
    

class TestStatusCode:

    def setup_class(self):
        self.status_code = samlp.StatusCode()

    def testAccessors(self):
        """Test for StatusCode accessors"""
        self.status_code.value = samlp.STATUS_RESPONDER
        self.status_code.status_code = samlp.StatusCode(
            value=samlp.STATUS_REQUEST_DENIED)
        print(self.status_code.__dict__)
        new_status_code = samlp.status_code_from_string(self.status_code.to_string())
        assert new_status_code.value == samlp.STATUS_RESPONDER
        assert new_status_code.status_code.value == \
                                 samlp.STATUS_REQUEST_DENIED

    def testUsingTestData(self):
        """Test for status_code_from_string() using test data"""
        new_status_code = samlp.status_code_from_string(
            samlp_data.TEST_STATUS_CODE)
        assert new_status_code.value == samlp.STATUS_RESPONDER
        assert new_status_code.status_code.value == \
                                 samlp.STATUS_REQUEST_DENIED


class TestStatus:

    def setup_class(self):
        self.status = samlp.Status()

    def testAccessors(self):
        """Test for Status accessors"""
        self.status.status_code = samlp.StatusCode()
        self.status.status_message = samlp.StatusMessage()
        self.status.status_detail = samlp.StatusDetail()
        new_status = samlp.status_from_string(self.status.to_string())
        assert isinstance(new_status.status_code, samlp.StatusCode)
        assert isinstance(new_status.status_message, samlp.StatusMessage)
        assert isinstance(new_status.status_detail, samlp.StatusDetail)

    def testUsingTestData(self):
        """Test for status_from_string using test data"""
        new_status = samlp.status_from_string(samlp_data.TEST_STATUS)
        assert isinstance(new_status.status_code, samlp.StatusCode)
        assert isinstance(new_status.status_code.status_code,
                                                        samlp.StatusCode)
        assert isinstance(new_status.status_message, samlp.StatusMessage)
        assert isinstance(new_status.status_detail, samlp.StatusDetail)

# class TestStatusResponseType:
# 
#     def setup_class(self):
#         self.sr = samlp.StatusResponseType()
# 
#     def testAccessors(self):
#         """Test for StatusResponseType accessors"""
#         self.sr.id = "response id"
#         self.sr.in_response_to = "request id"
#         self.sr.version = saml2.VERSION
#         self.sr.issue_instant = "2007-09-14T01:05:02Z"
#         self.sr.destination = "http://www.example.com/Destination"
#         self.sr.consent = saml.CONSENT_UNSPECIFIED
#         self.sr.issuer = saml.Issuer()
#         self.sr.signature = ds.Signature()
#         self.sr.extensions = samlp.Extensions()
#         self.sr.status = samlp.Status()
# 
#         new_sr = samlp.status_response_type_from_string(self.sr.to_string())
#         assert new_sr.id == "response id"
#         assert new_sr.in_response_to == "request id"
#         assert new_sr.version == saml2.VERSION
#         assert new_sr.issue_instant == "2007-09-14T01:05:02Z"
#         assert new_sr.destination == "http://www.example.com/Destination"
#         assert new_sr.consent == saml.CONSENT_UNSPECIFIED
#         assert isinstance(new_sr.issuer, saml.Issuer)
#         assert isinstance(new_sr.signature, ds.Signature)
#         assert isinstance(new_sr.extensions, samlp.Extensions)
#         assert isinstance(new_sr.status, samlp.Status)
#         
#     def testUsingTestData(self):
#         """Test for status_response_from_string() using test data"""
#         # TODO:
#         pass


class TestResponse:

    def setup_class(self):
        self.response = samlp.Response()

    def testAccessors(self):
        """Test for Response accessors"""
        self.response.id = "response id"
        self.response.in_response_to = "request id"
        self.response.version = saml2.VERSION
        self.response.issue_instant = "2007-09-14T01:05:02Z"
        self.response.destination = "http://www.example.com/Destination"
        self.response.consent = saml.CONSENT_UNSPECIFIED
        self.response.issuer = saml.Issuer()
        self.response.signature = ds.Signature()
        self.response.extensions = samlp.Extensions()
        self.response.status = samlp.Status()
        self.response.assertion.append(saml.Assertion())
        self.response.encrypted_assertion.append(saml.EncryptedAssertion())

        new_response = samlp.response_from_string(self.response.to_string())
        assert new_response.id == "response id"
        assert new_response.in_response_to == "request id"
        assert new_response.version == saml2.VERSION
        assert new_response.issue_instant == "2007-09-14T01:05:02Z"
        assert new_response.destination == "http://www.example.com/Destination"
        assert new_response.consent == saml.CONSENT_UNSPECIFIED
        assert isinstance(new_response.issuer, saml.Issuer)
        assert isinstance(new_response.signature, ds.Signature)
        assert isinstance(new_response.extensions, samlp.Extensions)
        assert isinstance(new_response.status, samlp.Status)

        assert isinstance(new_response.assertion[0], saml.Assertion)
        assert isinstance(new_response.encrypted_assertion[0],
                                                        saml.EncryptedAssertion)

    def testUsingTestData(self):
        """Test for response_from_string() using test data"""
        # TODO:
        pass

class TestNameIDPolicy:

    def setup_class(self):
        self.name_id_policy = samlp.NameIDPolicy()

    def testAccessors(self):
        """Test for NameIDPolicy accessors"""
        self.name_id_policy.format = saml.NAMEID_FORMAT_EMAILADDRESS
        self.name_id_policy.sp_name_qualifier = saml.NAMEID_FORMAT_PERSISTENT
        self.name_id_policy.allow_create = 'false'

        new_name_id_policy = samlp.name_id_policy_from_string(
            self.name_id_policy.to_string())

        assert new_name_id_policy.format == saml.NAMEID_FORMAT_EMAILADDRESS
        assert new_name_id_policy.sp_name_qualifier == \
                                 saml.NAMEID_FORMAT_PERSISTENT
        assert new_name_id_policy.allow_create == 'false'

    def testUsingTestData(self):
        """Test for name_id_policy_from_string() using test data"""
        new_name_id_policy = samlp.name_id_policy_from_string(
            samlp_data.TEST_NAME_ID_POLICY)

        assert new_name_id_policy.format == saml.NAMEID_FORMAT_EMAILADDRESS
        assert new_name_id_policy.sp_name_qualifier == \
                                 saml.NAMEID_FORMAT_PERSISTENT
        assert new_name_id_policy.allow_create == 'false'


class TestIDPEntry:

    def setup_class(self):
        self.idp_entry = samlp.IDPEntry()

    def testAccessors(self):
        """Test for IDPEntry accessors"""
        self.idp_entry.provider_id = "http://www.example.com/provider"
        self.idp_entry.name = "the provider"
        self.idp_entry.loc = "http://www.example.com/Loc"

        new_idp_entry = samlp.idp_entry_from_string(self.idp_entry.to_string())
        assert new_idp_entry.provider_id == "http://www.example.com/provider"
        assert new_idp_entry.name == "the provider"
        assert new_idp_entry.loc == "http://www.example.com/Loc"

    def testUsingTestData(self):
        """Test for idp_entry_from_string() using test data"""
        new_idp_entry = samlp.idp_entry_from_string(samlp_data.TEST_IDP_ENTRY)
        assert new_idp_entry.provider_id == "http://www.example.com/provider"
        assert new_idp_entry.name == "the provider"
        assert new_idp_entry.loc == "http://www.example.com/Loc"


class TestIDPList:

    def setup_class(self):
        self.idp_list = samlp.IDPList()

    def testAccessors(self):
        """Test for IDPList accessors"""
        self.idp_list.idp_entry.append(samlp.idp_entry_from_string(
            samlp_data.TEST_IDP_ENTRY))
        self.idp_list.get_complete = samlp.GetComplete(
            text="http://www.example.com/GetComplete")
        new_idp_list = samlp.idp_list_from_string(self.idp_list.to_string())
        assert isinstance(new_idp_list.idp_entry[0], samlp.IDPEntry)
        assert new_idp_list.get_complete.text.strip() == \
                                 "http://www.example.com/GetComplete"

    def testUsingTestData(self):
        """Test for idp_list_from_string() using test data"""
        new_idp_list = samlp.idp_list_from_string(samlp_data.TEST_IDP_LIST)
        assert isinstance(new_idp_list.idp_entry[0], samlp.IDPEntry)
        assert new_idp_list.get_complete.text.strip() == \
                                 "http://www.example.com/GetComplete"


class TestScoping:

    def setup_class(self):
        self.scoping = samlp.Scoping()

    def testAccessors(self):
        """Test for Scoping accessors"""

        self.scoping.proxy_count = "1"
        self.scoping.idp_list = samlp.IDPList()
        self.scoping.requester_id.append(samlp.RequesterID())

        new_scoping = samlp.scoping_from_string(self.scoping.to_string())

        assert new_scoping.proxy_count == "1"
        assert isinstance(new_scoping.idp_list, samlp.IDPList)
        assert isinstance(new_scoping.requester_id[0], samlp.RequesterID)

    def testUsingTestData(self):
        """Test for scoping_from_string() using test data"""
        new_scoping = samlp.scoping_from_string(samlp_data.TEST_SCOPING)

        assert new_scoping.proxy_count == "1"
        assert isinstance(new_scoping.idp_list, samlp.IDPList)
        assert isinstance(new_scoping.requester_id[0], samlp.RequesterID)


class TestRequestedAuthnContext:

    def setup_class(self):
        self.context = samlp.RequestedAuthnContext()

    def testAccessors(self):
        """Test for RequestedAuthnContext accessors"""

        self.context.authn_context_class_ref.append(saml.AuthnContextClassRef())
        self.context.authn_context_decl_ref.append(saml.AuthnContextDeclRef())
        self.context.comparison = "exact"

        new_context = samlp.requested_authn_context_from_string(
            self.context.to_string())

        assert isinstance(new_context.authn_context_class_ref[0],
                                                        saml.AuthnContextClassRef)
        assert isinstance(new_context.authn_context_decl_ref[0],
                                                        saml.AuthnContextDeclRef)
        assert new_context.comparison == "exact"

    def testUsingTestData(self):
        """Test for requested_authn_context_from_string() using test data"""
        new_context = samlp.requested_authn_context_from_string(
            samlp_data.TEST_REQUESTED_AUTHN_CONTEXT)

        assert isinstance(new_context.authn_context_class_ref[0],
                                                        saml.AuthnContextClassRef)
        assert isinstance(new_context.authn_context_decl_ref[0],
                                                        saml.AuthnContextDeclRef)
        assert new_context.comparison == "exact"


class TestAuthnRequest:

    def setup_class(self):
        self.ar = samlp.AuthnRequest()

    def testAccessors(self):
        """Test for AuthnRequest accessors"""
        self.ar.id = "request id"
        self.ar.version = saml2.VERSION
        self.ar.issue_instant = "2007-09-14T01:05:02Z"
        self.ar.destination = "http://www.example.com/Destination"
        self.ar.consent = saml.CONSENT_UNSPECIFIED
        self.ar.issuer = saml.Issuer()
        self.ar.signature = ds.Signature()
        self.ar.extensions = samlp.Extensions()

        self.ar.subject = saml.Subject()
        self.ar.name_id_policy = samlp.NameIDPolicy()
        self.ar.conditions = saml.Conditions()
        self.ar.requested_authn_context = samlp.RequestedAuthnContext()
        self.ar.scoping = samlp.Scoping()
        self.ar.force_authn = 'true'
        self.ar.is_passive = 'true'
        self.ar.assertion_consumer_service_index = "1"
        self.ar.assertion_consumer_service_url = "http://www.example.com/acs"
        self.ar.protocol_binding = saml2.BINDING_HTTP_POST
        self.ar.attribute_consuming_service_index = "2"
        self.ar.provider_name = "provider name"

        new_ar = samlp.authn_request_from_string(self.ar.to_string())
        assert new_ar.id == "request id"
        assert new_ar.version == saml2.VERSION
        assert new_ar.issue_instant == "2007-09-14T01:05:02Z"
        assert new_ar.destination == "http://www.example.com/Destination"
        assert new_ar.consent == saml.CONSENT_UNSPECIFIED
        assert isinstance(new_ar.issuer, saml.Issuer)
        assert isinstance(new_ar.signature, ds.Signature)
        assert isinstance(new_ar.extensions, samlp.Extensions)

        assert isinstance(new_ar.subject, saml.Subject)
        assert isinstance(new_ar.name_id_policy, samlp.NameIDPolicy)
        assert isinstance(new_ar.conditions, saml.Conditions)
        assert isinstance(new_ar.requested_authn_context,
                                                        samlp.RequestedAuthnContext)
        assert isinstance(new_ar.scoping, samlp.Scoping)
        assert new_ar.force_authn == 'true'
        assert new_ar.is_passive == 'true'
        assert new_ar.assertion_consumer_service_index == '1'
        assert new_ar.assertion_consumer_service_url == \
                                 'http://www.example.com/acs'
        assert new_ar.protocol_binding == saml2.BINDING_HTTP_POST
        assert new_ar.attribute_consuming_service_index == '2'
        assert new_ar.provider_name == "provider name"

    def testUsingTestData(self):
        """Test for authn_request_from_string() using test data"""
        new_ar = samlp.authn_request_from_string(samlp_data.TEST_AUTHN_REQUEST)
        assert new_ar.id == "request id"
        assert new_ar.version == saml2.VERSION
        assert new_ar.issue_instant == "2007-09-14T01:05:02Z"
        assert new_ar.destination == "http://www.example.com/Destination"
        assert new_ar.consent == saml.CONSENT_UNSPECIFIED
        assert isinstance(new_ar.issuer, saml.Issuer)
        assert isinstance(new_ar.signature, ds.Signature)
        assert isinstance(new_ar.extensions, samlp.Extensions)

        assert isinstance(new_ar.subject, saml.Subject)
        assert isinstance(new_ar.name_id_policy, samlp.NameIDPolicy)
        assert isinstance(new_ar.conditions, saml.Conditions)
        assert isinstance(new_ar.requested_authn_context,
                                                        samlp.RequestedAuthnContext)
        assert isinstance(new_ar.scoping, samlp.Scoping)
        assert new_ar.force_authn == 'true'
        assert new_ar.is_passive == 'true'
        assert new_ar.assertion_consumer_service_index == '1'
        assert new_ar.assertion_consumer_service_url == \
                                 'http://www.example.com/acs'
        assert new_ar.protocol_binding == saml2.BINDING_HTTP_POST
        assert new_ar.attribute_consuming_service_index == '2'
        assert new_ar.provider_name == "provider name"


class TestLogoutRequest:

    def setup_class(self):
        self.lr = samlp.LogoutRequest()

    def testAccessors(self):
        """Test for LogoutRequest accessors"""
        self.lr.id = "request id"
        self.lr.version = saml2.VERSION
        self.lr.issue_instant = "2007-09-14T01:05:02Z"
        self.lr.destination = "http://www.example.com/Destination"
        self.lr.consent = saml.CONSENT_UNSPECIFIED
        self.lr.issuer = saml.Issuer()
        self.lr.signature = ds.Signature()
        self.lr.extensions = samlp.Extensions()

        self.lr.not_on_or_after = "2007-10-14T01:05:02Z"
        self.lr.reason = "http://www.example.com/Reason"
        self.lr.base_id = saml.BaseID()
        self.lr.name_id = saml.NameID()
        self.lr.encrypted_id = saml.EncryptedID()
        self.lr.session_index = samlp.SessionIndex()

        new_lr = samlp.logout_request_from_string(self.lr.to_string())
        assert new_lr.id == "request id"
        assert new_lr.version == saml2.VERSION
        assert new_lr.issue_instant == "2007-09-14T01:05:02Z"
        assert new_lr.destination == "http://www.example.com/Destination"
        assert new_lr.consent == saml.CONSENT_UNSPECIFIED
        assert isinstance(new_lr.issuer, saml.Issuer)
        assert isinstance(new_lr.signature, ds.Signature)
        assert isinstance(new_lr.extensions, samlp.Extensions)
        assert new_lr.not_on_or_after == "2007-10-14T01:05:02Z"
        assert new_lr.reason == "http://www.example.com/Reason"
        assert isinstance(new_lr.base_id, saml.BaseID)
        assert isinstance(new_lr.name_id, saml.NameID)
        assert isinstance(new_lr.encrypted_id, saml.EncryptedID)
        assert isinstance(new_lr.session_index[0], samlp.SessionIndex)

    def testUsingTestData(self):
        """Test for logout_request_from_string() using test data"""
        new_lr = samlp.logout_request_from_string(samlp_data.TEST_LOGOUT_REQUEST)
        assert new_lr.id == "request id"
        assert new_lr.version == saml2.VERSION
        assert new_lr.issue_instant == "2007-09-14T01:05:02Z"
        assert new_lr.destination == "http://www.example.com/Destination"
        assert new_lr.consent == saml.CONSENT_UNSPECIFIED
        assert isinstance(new_lr.issuer, saml.Issuer)
        assert isinstance(new_lr.signature, ds.Signature)
        assert isinstance(new_lr.extensions, samlp.Extensions)
        assert new_lr.not_on_or_after == "2007-10-14T01:05:02Z"
        assert new_lr.reason == "http://www.example.com/Reason"
        assert isinstance(new_lr.base_id, saml.BaseID)
        assert isinstance(new_lr.name_id, saml.NameID)
        assert isinstance(new_lr.encrypted_id, saml.EncryptedID)
        assert isinstance(new_lr.session_index[0], samlp.SessionIndex)
        assert new_lr.session_index[0].text.strip() == "session index"


class TestLogoutResponse:
    
    def setup_class(self):
        self.lr = samlp.LogoutResponse()

    def testAccessors(self):
        """Test for LogoutResponse accessors"""
        self.lr.id = "response id"
        self.lr.in_response_to = "request id"
        self.lr.version = saml2.VERSION
        self.lr.issue_instant = "2007-09-14T01:05:02Z"
        self.lr.destination = "http://www.example.com/Destination"
        self.lr.consent = saml.CONSENT_UNSPECIFIED
        self.lr.issuer = saml.Issuer()
        self.lr.signature = ds.Signature()
        self.lr.extensions = samlp.Extensions()
        self.lr.status = samlp.Status()

        new_lr = samlp.logout_response_from_string(self.lr.to_string())
        assert new_lr.id == "response id"
        assert new_lr.in_response_to == "request id"
        assert new_lr.version == saml2.VERSION
        assert new_lr.issue_instant == "2007-09-14T01:05:02Z"
        assert new_lr.destination == "http://www.example.com/Destination"
        assert new_lr.consent == saml.CONSENT_UNSPECIFIED
        assert isinstance(new_lr.issuer, saml.Issuer)
        assert isinstance(new_lr.signature, ds.Signature)
        assert isinstance(new_lr.extensions, samlp.Extensions)
        assert isinstance(new_lr.status, samlp.Status)
        
    def testUsingTestData(self):
        """Test for logout_response_from_string() using test data"""
        new_lr = samlp.logout_response_from_string(
            samlp_data.TEST_LOGOUT_RESPONSE)
        assert new_lr.id == "response id"
        assert new_lr.in_response_to == "request id"
        assert new_lr.version == saml2.VERSION
        assert new_lr.issue_instant == "2007-09-14T01:05:02Z"
        assert new_lr.destination == "http://www.example.com/Destination"
        assert new_lr.consent == saml.CONSENT_UNSPECIFIED
        assert isinstance(new_lr.issuer, saml.Issuer)
        assert isinstance(new_lr.signature, ds.Signature)
        assert isinstance(new_lr.extensions, samlp.Extensions)
        assert isinstance(new_lr.status, samlp.Status)

