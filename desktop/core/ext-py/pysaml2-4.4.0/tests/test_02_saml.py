#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""Tests for saml2.saml"""

__author__ = 'roland.hedberg@adm.umu.se (Roland Hedberg)'

try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree

import saml2
import saml2_data
import ds_data

from saml2 import xmldsig as ds

from saml2 import saml

from py.test import raises

from saml2.saml import Issuer
from saml2.saml import Attribute
from saml2.saml import AttributeValue
from saml2.saml import NAMEID_FORMAT_EMAILADDRESS


class TestExtensionElement:
    def test_loadd(self):
        ava = {
            "attributes": {"attr": "loa", "info": "source"},
            "tag": "tag",
            "namespace": "urn:mace:example.com",
            "text": "free text"
        }

        ee = saml2.ExtensionElement(ava["tag"])
        ee.loadd(ava)

        del ava["tag"]
        print(ava)
        ee = saml2.ExtensionElement("")

        raises(KeyError, "ee.loadd(ava)")

        ava["tag"] = "foo"
        del ava["namespace"]

        ee = saml2.ExtensionElement("")
        raises(KeyError, "ee.loadd(ava)")

    def test_find_children(self):
        ava = {
            "attributes": {"attr": "loa", "info": "source"},
            "tag": "tag",
            "namespace": "urn:mace:example.com",
            "text": "free text",
            "children": [{
                             "attributes": {"foo": "bar", "special": "app"},
                             "tag": "tag2",
                             "namespace": "urn:mace:example.com",
                             "text": "Just a line"
                         },
                         {
                             "attributes": {"static": "attribute",
                                            "dynamic": "orgname"},
                             "tag": "tag3",
                             "namespace": "urn:mace:example.com",
                             "text": "Another line of text",
                             "children": [{
                                              "tag": "subtag",
                                              "namespace": "urn:mace:example.org",

                                              "text": "grandchild"
                                          }]
                         },
                         {
                             "attributes": {"entitlement": "xyz"},
                             "tag": "tag4",
                             "namespace": "urn:mace:example.org",
                             "text": "A comment"
                         }
            ]
        }

        ee = saml2.ExtensionElement(ava["tag"])
        ee.loadd(ava)

        c = ee.find_children(tag="tag")
        assert len(c) == 0
        c = ee.find_children(tag="tag2")
        assert len(c) == 1
        c = ee.find_children(tag="tag3")
        assert len(c) == 1
        # Grandchild
        gc = c[0].find_children(tag="subtag")
        assert len(gc) == 1
        # only do immediate children
        gc = ee.find_children(tag="subtag")
        assert len(gc) == 0

        c = ee.find_children(tag="tag2", namespace="urn:mace:example.com")
        assert len(c) == 1
        c = ee.find_children(tag="tag2", namespace="urn:mace:example.org")
        assert len(c) == 0
        c = ee.find_children(tag="subtag", namespace="urn:mace:example.org")
        assert len(c) == 0

        c = ee.find_children(namespace="urn:mace:example.com")
        assert len(c) == 2
        c = ee.find_children(namespace="urn:mace:example.org")
        assert len(c) == 1

        c = ee.find_children()
        assert len(c) == 3


class TestExtensionContainer:
    def test_find_extensions(self):
        avas = [{
                    "attributes": {"foo": "bar", "special": "app"},
                    "tag": "tag2",
                    "namespace": "urn:mace:example.com",
                    "text": "Just a line"
                },
                {
                    "attributes": {"static": "attribute", "dynamic": "orgname"},
                    "tag": "tag3",
                    "namespace": "urn:mace:example.com",
                    "text": "Another line of text",
                    "children": [{
                                     "tag": "subtag",
                                     "namespace": "urn:mace:example.org",
                                     "text": "grandchild"
                                 }]
                },
                {
                    "attributes": {"entitlement": "xyz"},
                    "tag": "tag4",
                    "namespace": "urn:mace:example.org",
                    "text": "A comment"
                }]

        ees = [saml2.ExtensionElement("").loadd(a) for a in avas]
        print(ees)
        ec = saml2.ExtensionContainer(extension_elements=ees)
        esl = ec.find_extensions(tag="tag2")
        assert len(esl) == 1
        esl = ec.find_extensions(tag="tag3")
        assert len(esl) == 1
        esl = ec.find_extensions(tag="tag4")
        assert len(esl) == 1
        esl = ec.find_extensions(tag="tag2", namespace="urn:mace:example.com")
        assert len(esl) == 1
        esl = ec.find_extensions(tag="tag2", namespace="urn:mace:example.org")
        assert len(esl) == 0
        esl = ec.find_extensions(namespace="urn:mace:example.com")
        assert len(esl) == 2
        esl = ec.find_extensions(namespace="urn:mace:example.org")
        assert len(esl) == 1
        esl = ec.find_extensions()
        assert len(esl) == 3

    def test_add_extension_elements(self):
        items = [saml.NameID(sp_name_qualifier="sp0", text="foo"),
                 saml.NameID(sp_name_qualifier="sp1", text="bar"),
                 saml.Audience(text="http://example.org")]

        ec = saml2.ExtensionContainer()
        ec.add_extension_elements(items)
        esl = ec.find_extensions(tag="NameID")
        assert len(esl) == 2
        esl = ec.find_extensions(tag="Audience")
        assert len(esl) == 1
        esl = ec.find_extensions(namespace=saml.NAMESPACE)
        assert len(esl) == 3
        esl = ec.find_extensions()
        assert len(esl) == 3

    def test_add_extension_attribute(self):
        ec = saml2.ExtensionContainer()
        ec.add_extension_attribute("foo", "bar")
        assert len(ec.extension_attributes) == 1
        assert list(ec.extension_attributes.keys())[0] == "foo"


class TestSAMLBase:
    def test_make_vals_dict(self):
        ava = {
            "sp_name_qualifier": "loa",
            "format": NAMEID_FORMAT_EMAILADDRESS,
            "text": "free text"
        }

        foo = saml2.make_vals(ava, Issuer, part=True)
        print(foo)
        assert foo.format == NAMEID_FORMAT_EMAILADDRESS
        assert foo.sp_name_qualifier == "loa"
        assert foo.text == "free text"

    def test_make_vals_str(self):
        ava = "free text"

        foo = saml2.make_vals(ava, Issuer, part=True)
        print(foo)
        assert foo.keyswv() == ["text"]
        assert foo.text == "free text"

    def test_make_vals_multi_dict(self):
        ava = ["foo", "bar", "lions", "saints"]

        raises(Exception,
               "saml2.make_vals(ava, AttributeValue, Attribute(), part=True)")

        attr = Attribute()
        saml2.make_vals(ava, AttributeValue, attr, prop="attribute_value")
        assert sorted(attr.keyswv()) == sorted(["name_format",
                                                "attribute_value"])
        assert len(attr.attribute_value) == 4

    def test_to_string_nspair(self):
        foo = saml2.make_vals("lions", AttributeValue, part=True)
        txt = foo.to_string().decode('utf-8')
        nsstr = foo.to_string({"saml": saml.NAMESPACE}).decode('utf-8')
        assert nsstr != txt
        print(txt)
        print(nsstr)
        assert "saml:AttributeValue" in nsstr
        assert "saml:AttributeValue" not in txt

    def test_set_text(self):
        av = AttributeValue()
        av.set_text(True)
        assert av.text == "true"
        av.set_text(False)
        assert av.text == "false"
        # can't change value to another type
        raises(AssertionError, "av.set_text(491)")

        av = AttributeValue()
        av.set_text(None)
        assert av.text == ""

    def test_make_vals_div(self):
        foo = saml2.make_vals(666, AttributeValue, part=True)
        assert foo.text == "666"

        foo = saml2.make_vals(True, AttributeValue, part=True)
        assert foo.text == "true"

        foo = saml2.make_vals(False, AttributeValue, part=True)
        assert foo.text == "false"


class TestNameID:
    def setup_class(self):
        self.name_id = saml.NameID()

    def testEmptyExtensionsList(self):
        """Test if NameID has empty extensions list"""
        assert isinstance(self.name_id.extension_elements, list)
        assert len(self.name_id.extension_elements) == 0

    def testFormatAttribute(self):
        """Test for Format attribute accessors"""
        self.name_id.format = saml.NAMEID_FORMAT_EMAILADDRESS
        assert self.name_id.format == saml.NAMEID_FORMAT_EMAILADDRESS
        assert len(self.name_id.extension_elements) == 0
        new_name_id = saml.name_id_from_string(self.name_id.to_string())
        assert len(new_name_id.extension_elements) == 0

        self.name_id.extension_elements.append(saml2.ExtensionElement(
            'foo', text='bar'))
        assert len(self.name_id.extension_elements) == 1
        assert self.name_id.format == saml.NAMEID_FORMAT_EMAILADDRESS

    def testNameIDText(self):
        """Test text value of NameID element"""
        self.name_id.text = "tmatsuo@example.com"
        assert self.name_id.text == "tmatsuo@example.com"

    def testSPProvidedID(self):
        """Test for SPProvidedID attribute accessors"""
        self.name_id.sp_provided_id = "provided id"
        assert self.name_id.sp_provided_id == "provided id"

    def testEmptyNameIDToAndFromStringMatch(self):
        """Test name_id_from_string() with empty NameID"""
        string_from_name_id = self.name_id.to_string()
        new_name_id = saml.name_id_from_string(string_from_name_id)
        string_from_new_name_id = new_name_id.to_string()
        assert string_from_name_id == string_from_new_name_id

    def testNameIDToAndFromStringMatch(self):
        """Test name_id_from_string() with data"""
        self.name_id.format = saml.NAMEID_FORMAT_EMAILADDRESS
        self.name_id.text = "tmatsuo@example.com"
        self.name_id.name_qualifier = "name_qualifier"
        self.name_id.sp_name_qualifier = "sp_name_qualifier"
        string_from_name_id = self.name_id.to_string()
        new_name_id = saml.name_id_from_string(string_from_name_id)
        assert new_name_id.name_qualifier == "name_qualifier"
        assert new_name_id.sp_name_qualifier == "sp_name_qualifier"
        string_from_new_name_id = new_name_id.to_string()
        assert string_from_name_id == string_from_new_name_id

    def testExtensionAttributes(self):
        """Test extension attributes"""
        self.name_id.extension_attributes['hoge'] = 'fuga'
        self.name_id.extension_attributes['moge'] = 'muga'
        assert self.name_id.extension_attributes['hoge'] == 'fuga'
        assert self.name_id.extension_attributes['moge'] == 'muga'
        new_name_id = saml.name_id_from_string(self.name_id.to_string())
        assert new_name_id.extension_attributes['hoge'] == 'fuga'
        assert new_name_id.extension_attributes['moge'] == 'muga'

    def testname_id_from_string(self):
        """Test name_id_from_string() using test data"""
        name_id = saml.name_id_from_string(saml2_data.TEST_NAME_ID)
        assert name_id.format == saml.NAMEID_FORMAT_EMAILADDRESS
        assert name_id.text.strip() == "tmatsuo@example.com"
        assert name_id.sp_provided_id == "sp provided id"


class TestIssuer:
    def setup_class(self):
        self.issuer = saml.Issuer()

    def testIssuerToAndFromString(self):
        """Test issuer_from_string()"""
        self.issuer.text = "http://www.example.com/test"
        self.issuer.name_qualifier = "name_qualifier"
        self.issuer.sp_name_qualifier = "sp_name_qualifier"
        new_issuer = saml.issuer_from_string(self.issuer.to_string())
        assert self.issuer.text == new_issuer.text
        assert self.issuer.name_qualifier == new_issuer.name_qualifier
        assert self.issuer.sp_name_qualifier == new_issuer.sp_name_qualifier
        assert self.issuer.extension_elements == new_issuer.extension_elements

    def testUsingTestData(self):
        """Test issuer_from_string() using test data"""
        issuer = saml.issuer_from_string(saml2_data.TEST_ISSUER)
        assert issuer.text.strip() == "http://www.example.com/test"
        new_issuer = saml.issuer_from_string(issuer.to_string())
        assert issuer.text == new_issuer.text
        assert issuer.extension_elements == new_issuer.extension_elements


class TestSubjectLocality:
    def setup_class(self):
        self.subject_locality = saml.SubjectLocality()

    def testAccessors(self):
        """Test for SubjectLocality accessors"""
        self.subject_locality.address = "127.0.0.1"
        self.subject_locality.dns_name = "localhost"
        assert self.subject_locality.address == "127.0.0.1"
        assert self.subject_locality.dns_name == "localhost"
        new_subject_locality = saml.subject_locality_from_string(
            self.subject_locality.to_string())
        assert new_subject_locality.address == "127.0.0.1"
        assert new_subject_locality.dns_name == "localhost"

    def testUsingTestData(self):
        """Test SubjectLocalityFromString() using test data"""

        subject_locality = saml.subject_locality_from_string(
            saml2_data.TEST_SUBJECT_LOCALITY)
        assert subject_locality.address == "127.0.0.1"
        assert subject_locality.dns_name == "localhost"

        new_subject_locality = saml.subject_locality_from_string(
            subject_locality.to_string())
        assert new_subject_locality.address == "127.0.0.1"
        assert new_subject_locality.dns_name == "localhost"
        assert subject_locality.to_string() == new_subject_locality.to_string()


class TestAuthnContextClassRef:
    def setup_class(self):
        self.authn_context_class_ref = saml.AuthnContextClassRef()
        self.text = "http://www.example.com/authnContextClassRef"

    def testAccessors(self):
        """Test for AuthnContextClassRef accessors"""
        self.authn_context_class_ref.text = self.text
        assert self.authn_context_class_ref.text == self.text
        new_authn_context_class_ref = saml.authn_context_class_ref_from_string(
            self.authn_context_class_ref.to_string())
        assert new_authn_context_class_ref.text == self.text
        assert self.authn_context_class_ref.to_string() == \
               new_authn_context_class_ref.to_string()

    def testUsingTestData(self):
        """Test authn_context_class_ref_from_string() using test data"""
        authn_context_class_ref = saml.authn_context_class_ref_from_string(
            saml2_data.TEST_AUTHN_CONTEXT_CLASS_REF)
        assert authn_context_class_ref.text.strip() == self.text


class TestAuthnContextDeclRef:
    def setup_class(self):
        self.authn_context_decl_ref = saml.AuthnContextDeclRef()
        self.ref = "http://www.example.com/authnContextDeclRef"

    def testAccessors(self):
        """Test for AuthnContextDeclRef accessors"""
        self.authn_context_decl_ref.text = self.ref
        assert self.authn_context_decl_ref.text == self.ref
        new_authn_context_decl_ref = saml.authn_context_decl_ref_from_string(
            self.authn_context_decl_ref.to_string())
        assert new_authn_context_decl_ref.text == self.ref
        assert self.authn_context_decl_ref.to_string() == \
               new_authn_context_decl_ref.to_string()

    def testUsingTestData(self):
        """Test authn_context_decl_ref_from_string() using test data"""
        authn_context_decl_ref = saml.authn_context_decl_ref_from_string(
            saml2_data.TEST_AUTHN_CONTEXT_DECL_REF)
        assert authn_context_decl_ref.text.strip() == self.ref


class TestAuthnContextDecl:
    def setup_class(self):
        self.authn_context_decl = saml.AuthnContextDecl()
        self.text = "http://www.example.com/authnContextDecl"

    def testAccessors(self):
        """Test for AuthnContextDecl accessors"""
        self.authn_context_decl.text = self.text
        assert self.authn_context_decl.text == self.text
        new_authn_context_decl = saml.authn_context_decl_from_string(
            self.authn_context_decl.to_string())
        assert new_authn_context_decl.text == self.text
        assert self.authn_context_decl.to_string() == \
               new_authn_context_decl.to_string()

    def testUsingTestData(self):
        """Test authn_context_decl_from_string() using test data"""
        authn_context_decl = saml.authn_context_decl_from_string(
            saml2_data.TEST_AUTHN_CONTEXT_DECL)
        assert authn_context_decl.text.strip() == self.text


class TestAuthenticatingAuthority:
    def setup_class(self):
        self.authenticating_authority = saml.AuthenticatingAuthority()
        self.text = "http://www.example.com/authenticatingAuthority"

    def testAccessors(self):
        """Test for AuthenticatingAuthority accessors"""
        self.authenticating_authority.text = self.text
        assert self.authenticating_authority.text == self.text
        new_authenticating_authority = saml.authenticating_authority_from_string(
            self.authenticating_authority.to_string())
        assert new_authenticating_authority.text == self.text
        assert self.authenticating_authority.to_string() == \
               new_authenticating_authority.to_string()

    def testUsingTestData(self):
        """Test authenticating_authority_from_string() using test data"""
        authenticating_authority = saml.authenticating_authority_from_string(
            saml2_data.TEST_AUTHENTICATING_AUTHORITY)
        assert authenticating_authority.text.strip() == self.text


class TestAuthnContext:
    def setup_class(self):
        self.authn_context = saml.AuthnContext()

    def testAccessors(self):
        """Test for AuthnContext accessors"""
        self.authn_context.authn_context_class_ref = \
            saml.authn_context_class_ref_from_string(
                saml2_data.TEST_AUTHN_CONTEXT_CLASS_REF)
        self.authn_context.authn_context_decl_ref = \
            saml.authn_context_decl_ref_from_string(
                saml2_data.TEST_AUTHN_CONTEXT_DECL_REF)
        self.authn_context.authn_context_decl = \
            saml.authn_context_decl_from_string(
                saml2_data.TEST_AUTHN_CONTEXT_DECL)
        self.authn_context.authenticating_authority.append(
            saml.authenticating_authority_from_string(
                saml2_data.TEST_AUTHENTICATING_AUTHORITY))
        assert self.authn_context.authn_context_class_ref.text.strip() == \
               "http://www.example.com/authnContextClassRef"
        assert self.authn_context.authn_context_decl_ref.text.strip() == \
               "http://www.example.com/authnContextDeclRef"
        assert self.authn_context.authn_context_decl.text.strip() == \
               "http://www.example.com/authnContextDecl"
        assert self.authn_context.authenticating_authority[0].text.strip() == \
               "http://www.example.com/authenticatingAuthority"
        new_authn_context = saml.authn_context_from_string(
            self.authn_context.to_string())
        assert self.authn_context.to_string() == new_authn_context.to_string()

    def testUsingTestData(self):
        """Test authn_context_from_string() using test data"""
        authn_context = saml.authn_context_from_string(
            saml2_data.TEST_AUTHN_CONTEXT)
        assert authn_context.authn_context_class_ref.text.strip() == \
               saml.AUTHN_PASSWORD


class TestAuthnStatement:
    def setup_class(self):
        self.authn_statem = saml.AuthnStatement()

    def testAccessors(self):
        """Test for AuthnStatement accessors"""
        self.authn_statem.authn_instant = "2007-08-31T01:05:02Z"
        self.authn_statem.session_not_on_or_after = "2007-09-14T01:05:02Z"
        self.authn_statem.session_index = "sessionindex"
        self.authn_statem.authn_context = saml.AuthnContext()
        self.authn_statem.authn_context.authn_context_class_ref = \
            saml.authn_context_class_ref_from_string(
                saml2_data.TEST_AUTHN_CONTEXT_CLASS_REF)
        self.authn_statem.authn_context.authn_context_decl_ref = \
            saml.authn_context_decl_ref_from_string(
                saml2_data.TEST_AUTHN_CONTEXT_DECL_REF)
        self.authn_statem.authn_context.authn_context_decl = \
            saml.authn_context_decl_from_string(
                saml2_data.TEST_AUTHN_CONTEXT_DECL)
        self.authn_statem.authn_context.authenticating_authority.append(
            saml.authenticating_authority_from_string(
                saml2_data.TEST_AUTHENTICATING_AUTHORITY))

        new_as = saml.authn_statement_from_string(self.authn_statem.to_string())
        assert new_as.authn_instant == "2007-08-31T01:05:02Z"
        assert new_as.session_index == "sessionindex"
        assert new_as.session_not_on_or_after == "2007-09-14T01:05:02Z"
        assert new_as.authn_context.authn_context_class_ref.text.strip() == \
               "http://www.example.com/authnContextClassRef"
        assert new_as.authn_context.authn_context_decl_ref.text.strip() == \
               "http://www.example.com/authnContextDeclRef"
        assert new_as.authn_context.authn_context_decl.text.strip() == \
               "http://www.example.com/authnContextDecl"
        assert new_as.authn_context.authenticating_authority[0].text.strip() \
               == "http://www.example.com/authenticatingAuthority"
        assert self.authn_statem.to_string() == new_as.to_string()

    def testUsingTestData(self):
        """Test authn_statement_from_string() using test data"""
        authn_statem = saml.authn_statement_from_string(
            saml2_data.TEST_AUTHN_STATEMENT)
        assert authn_statem.authn_instant == "2007-08-31T01:05:02Z"
        assert authn_statem.session_not_on_or_after == "2007-09-14T01:05:02Z"
        assert authn_statem.authn_context.authn_context_class_ref.text.strip() == \
               saml.AUTHN_PASSWORD


class TestAttributeValue:
    def setup_class(self):
        self.attribute_value = saml.AttributeValue()
        self.text = "value for test attribute"

    def testAccessors(self):
        """Test for AttributeValue accessors"""

        self.attribute_value.text = self.text
        new_attribute_value = saml.attribute_value_from_string(
            self.attribute_value.to_string())
        assert new_attribute_value.text.strip() == self.text

    def testUsingTestData(self):
        """Test attribute_value_from_string() using test data"""

        attribute_value = saml.attribute_value_from_string(
            saml2_data.TEST_ATTRIBUTE_VALUE)
        assert attribute_value.text.strip() == self.text


BASIC_STR_AV = """<?xml version="1.0" encoding="utf-8"?>
<Attribute xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic"
Name="FirstName">
<AttributeValue xsi:type="xs:string">By-Tor</AttributeValue>
</Attribute>"""

BASIC_INT_AV = """<?xml version="1.0" encoding="utf-8"?>
<Attribute xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic"
Name="age">
<AttributeValue xsi:type="xs:int">23</AttributeValue>
</Attribute>"""

BASIC_NOT_INT_AV = """<?xml version="1.0" encoding="utf-8"?>
<Attribute xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic"
Name="age">
<AttributeValue xsi:type="xs:int">foo</AttributeValue>
</Attribute>"""

BASIC_BOOLEAN_TRUE_AV = """<?xml version="1.0" encoding="utf-8"?>
<Attribute xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic"
Name="on-off">
<AttributeValue xsi:type="xs:boolean">true</AttributeValue>
</Attribute>"""

BASIC_BOOLEAN_FALSE_AV = """<?xml version="1.0" encoding="utf-8"?>
<Attribute xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic"
Name="on-off">
<AttributeValue xsi:type="xs:boolean">false</AttributeValue>
</Attribute>"""

BASIC_BASE64_AV = """<?xml version="1.0" encoding="utf-8"?>
<Attribute xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic"
Name="FirstName">
<AttributeValue 
xsi:type="xs:base64Binary">VU5JTkVUVA==</AttributeValue>
</Attribute>"""

X500_AV = """<?xml version="1.0" encoding="utf-8"?>
<Attribute xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
xmlns:x500="urn:oasis:names:tc:SAML:2.0:profiles:attribute:X500"
NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"
Name="urn:oid:2.5.4.42" FriendlyName="givenName">
<AttributeValue xsi:type="xs:string" x500:Encoding="LDAP">Steven
</AttributeValue>
</Attribute>"""

UUID_AV = """<?xml version="1.0" encoding="utf-8"?>
<Attribute xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"
Name="urn:uuid:6c9d0ec8-dd2d-11cc-abdd-080009353559"
FriendlyName="pre_auth_req">
<AttributeValue xsi:type="xs:integer">1</AttributeValue>
</Attribute>"""


class TestAttribute:
    def setup_class(self):
        self.attribute = saml.Attribute()
        self.text = ["value of test attribute",
                     "value1 of test attribute",
                     "value2 of test attribute"]

    def testAccessors(self):
        """Test for Attribute accessors"""
        self.attribute.name = "testAttribute"
        self.attribute.name_format = saml.NAME_FORMAT_URI
        self.attribute.friendly_name = "test attribute"
        self.attribute.attribute_value.append(saml.AttributeValue())
        self.attribute.attribute_value[0].text = self.text[0]

        new_attribute = saml.attribute_from_string(self.attribute.to_string())
        assert new_attribute.name == "testAttribute"
        assert new_attribute.name_format == saml.NAME_FORMAT_URI
        assert new_attribute.friendly_name == "test attribute"
        assert new_attribute.attribute_value[0].text.strip() == self.text[0]

    def testUsingTestData(self):
        """Test attribute_from_string() using test data"""
        attribute = saml.attribute_from_string(saml2_data.TEST_ATTRIBUTE)
        assert attribute.name == "testAttribute"
        assert attribute.name_format == saml.NAME_FORMAT_UNSPECIFIED
        assert attribute.friendly_name == "test attribute"
        assert attribute.attribute_value[0].text.strip() == self.text[1]
        assert attribute.attribute_value[1].text.strip() == self.text[2]
        # test again
        attribute = saml.attribute_from_string(attribute.to_string())
        assert attribute.name == "testAttribute"
        assert attribute.name_format == saml.NAME_FORMAT_UNSPECIFIED
        assert attribute.friendly_name == "test attribute"
        assert attribute.attribute_value[0].text.strip() == self.text[1]
        assert attribute.attribute_value[1].text.strip() == self.text[2]

    def test_basic_str(self):
        attribute = saml.attribute_from_string(BASIC_STR_AV)
        print(attribute)
        assert attribute.attribute_value[0].text.strip() == "By-Tor"

    def test_basic_int(self):
        attribute = saml.attribute_from_string(BASIC_INT_AV)
        print(attribute)
        assert attribute.attribute_value[0].text == "23"

    def test_basic_base64(self):
        attribute = saml.attribute_from_string(BASIC_BASE64_AV)
        print(attribute)
        assert attribute.attribute_value[0].text == "VU5JTkVUVA=="
        assert attribute.attribute_value[0].get_type() == "xs:base64Binary"

    def test_basic_boolean_true(self):
        attribute = saml.attribute_from_string(BASIC_BOOLEAN_TRUE_AV)
        print(attribute)
        assert attribute.attribute_value[0].text.lower() == "true"

    def test_basic_boolean_false(self):
        attribute = saml.attribute_from_string(BASIC_BOOLEAN_FALSE_AV)
        print(attribute)
        assert attribute.attribute_value[0].text.lower() == "false"


class TestAttributeStatement:
    def setup_class(self):
        self.attr_statem = saml.AttributeStatement()
        self.text = ["value of test attribute",
                     "value1 of test attribute",
                     "value2 of test attribute",
                     "value1 of test attribute2",
                     "value2 of test attribute2", ]

    def testAccessors(self):
        """Test for Attribute accessors"""
        self.attr_statem.attribute.append(saml.Attribute())
        self.attr_statem.attribute.append(saml.Attribute())
        self.attr_statem.attribute[0].name = "testAttribute"
        self.attr_statem.attribute[0].name_format = saml.NAME_FORMAT_URI
        self.attr_statem.attribute[0].friendly_name = "test attribute"
        self.attr_statem.attribute[0].attribute_value.append(
            saml.AttributeValue())
        self.attr_statem.attribute[0].attribute_value[0].text = self.text[0]

        self.attr_statem.attribute[1].name = "testAttribute2"
        self.attr_statem.attribute[1].name_format = saml.NAME_FORMAT_UNSPECIFIED
        self.attr_statem.attribute[1].friendly_name = self.text[2]
        self.attr_statem.attribute[1].attribute_value.append(
            saml.AttributeValue())
        self.attr_statem.attribute[1].attribute_value[0].text = self.text[2]

        new_as = saml.attribute_statement_from_string(
            self.attr_statem.to_string())
        assert new_as.attribute[0].name == "testAttribute"
        assert new_as.attribute[0].name_format == saml.NAME_FORMAT_URI
        assert new_as.attribute[0].friendly_name == "test attribute"
        assert new_as.attribute[0].attribute_value[0].text.strip() == self.text[
            0]
        assert new_as.attribute[1].name == "testAttribute2"
        assert new_as.attribute[1].name_format == saml.NAME_FORMAT_UNSPECIFIED
        assert new_as.attribute[1].friendly_name == "value2 of test attribute"
        assert new_as.attribute[1].attribute_value[0].text.strip() == self.text[
            2]

    def testUsingTestData(self):
        """Test attribute_statement_from_string() using test data"""
        attr_statem = saml.attribute_statement_from_string( \
            saml2_data.TEST_ATTRIBUTE_STATEMENT)
        assert attr_statem.attribute[0].name == "testAttribute"
        assert attr_statem.attribute[
                   0].name_format == saml.NAME_FORMAT_UNSPECIFIED
        assert attr_statem.attribute[0].friendly_name == "test attribute"
        assert attr_statem.attribute[0].attribute_value[0].text.strip() == \
               self.text[1]
        assert attr_statem.attribute[0].attribute_value[1].text.strip() == \
               self.text[2]
        assert attr_statem.attribute[
                   1].name == "http://www.example.com/testAttribute2"
        assert attr_statem.attribute[1].name_format == saml.NAME_FORMAT_URI
        assert attr_statem.attribute[1].friendly_name == "test attribute2"
        assert attr_statem.attribute[1].attribute_value[0].text.strip() == \
               self.text[3]
        assert attr_statem.attribute[1].attribute_value[1].text.strip() == \
               self.text[4]

        # test again
        attr_statem2 = saml.attribute_statement_from_string(
            attr_statem.to_string())
        assert attr_statem2.attribute[0].name == "testAttribute"
        assert attr_statem2.attribute[
                   0].name_format == saml.NAME_FORMAT_UNSPECIFIED
        assert attr_statem2.attribute[0].friendly_name == "test attribute"
        assert attr_statem2.attribute[0].attribute_value[0].text.strip() == \
               self.text[1]
        assert attr_statem2.attribute[0].attribute_value[1].text.strip() == \
               self.text[2]
        assert attr_statem2.attribute[
                   1].name == "http://www.example.com/testAttribute2"
        assert attr_statem2.attribute[1].name_format == saml.NAME_FORMAT_URI
        assert attr_statem2.attribute[1].friendly_name == "test attribute2"
        assert attr_statem2.attribute[1].attribute_value[0].text.strip() == \
               self.text[3]
        assert attr_statem2.attribute[1].attribute_value[1].text.strip() == \
               self.text[4]


class TestSubjectConfirmationData:
    def setup_class(self):
        self.scd = saml.SubjectConfirmationData()

    def testAccessors(self):
        """Test for SubjectConfirmationData accessors"""

        self.scd.not_before = "2007-08-31T01:05:02Z"
        self.scd.not_on_or_after = "2007-09-14T01:05:02Z"
        self.scd.recipient = "recipient"
        self.scd.in_response_to = "responseID"
        self.scd.address = "127.0.0.1"
        new_scd = saml.subject_confirmation_data_from_string(
            self.scd.to_string())
        assert new_scd.not_before == "2007-08-31T01:05:02Z"
        assert new_scd.not_on_or_after == "2007-09-14T01:05:02Z"
        assert new_scd.recipient == "recipient"
        assert new_scd.in_response_to == "responseID"
        assert new_scd.address == "127.0.0.1"

    def testUsingTestData(self):
        """Test subject_confirmation_data_from_string() using test data"""

        scd = saml.subject_confirmation_data_from_string(
            saml2_data.TEST_SUBJECT_CONFIRMATION_DATA)
        assert scd.not_before == "2007-08-31T01:05:02Z"
        assert scd.not_on_or_after == "2007-09-14T01:05:02Z"
        assert scd.recipient == "recipient"
        assert scd.in_response_to == "responseID"
        assert scd.address == "127.0.0.1"


class TestSubjectConfirmation:
    def setup_class(self):
        self.sc = saml.SubjectConfirmation()

    def testAccessors(self):
        """Test for SubjectConfirmation accessors"""
        self.sc.name_id = saml.name_id_from_string(saml2_data.TEST_NAME_ID)
        self.sc.method = saml.SCM_BEARER
        self.sc.subject_confirmation_data = saml.subject_confirmation_data_from_string(
            saml2_data.TEST_SUBJECT_CONFIRMATION_DATA)
        new_sc = saml.subject_confirmation_from_string(self.sc.to_string())
        assert new_sc.name_id.sp_provided_id == "sp provided id"
        assert new_sc.method == saml.SCM_BEARER
        assert new_sc.subject_confirmation_data.not_before == \
               "2007-08-31T01:05:02Z"
        assert new_sc.subject_confirmation_data.not_on_or_after == \
               "2007-09-14T01:05:02Z"
        assert new_sc.subject_confirmation_data.recipient == "recipient"
        assert new_sc.subject_confirmation_data.in_response_to == "responseID"
        assert new_sc.subject_confirmation_data.address == "127.0.0.1"

    def testUsingTestData(self):
        """Test subject_confirmation_from_string() using test data"""

        sc = saml.subject_confirmation_from_string(
            saml2_data.TEST_SUBJECT_CONFIRMATION)
        assert sc.name_id.sp_provided_id == "sp provided id"
        assert sc.method == saml.SCM_BEARER
        assert sc.subject_confirmation_data.not_before == "2007-08-31T01:05:02Z"
        assert sc.subject_confirmation_data.not_on_or_after == "2007-09-14T01:05:02Z"
        assert sc.subject_confirmation_data.recipient == "recipient"
        assert sc.subject_confirmation_data.in_response_to == "responseID"
        assert sc.subject_confirmation_data.address == "127.0.0.1"

    def testVerify(self):
        """Test SubjectConfirmation verify"""

        sc = saml.subject_confirmation_from_string(
            saml2_data.TEST_SUBJECT_CONFIRMATION)
        assert sc.verify()


class TestSubject:
    def setup_class(self):
        self.subject = saml.Subject()

    def testAccessors(self):
        """Test for Subject accessors"""
        self.subject.name_id = saml.name_id_from_string(saml2_data.TEST_NAME_ID)
        self.subject.subject_confirmation.append(
            saml.subject_confirmation_from_string(
                saml2_data.TEST_SUBJECT_CONFIRMATION))
        new_subject = saml.subject_from_string(self.subject.to_string())
        assert new_subject.name_id.sp_provided_id == "sp provided id"
        assert new_subject.name_id.text.strip() == "tmatsuo@example.com"
        assert new_subject.name_id.format == saml.NAMEID_FORMAT_EMAILADDRESS
        assert isinstance(new_subject.subject_confirmation[0],
                          saml.SubjectConfirmation)

    def testUsingTestData(self):
        """Test for subject_from_string() using test data."""

        subject = saml.subject_from_string(saml2_data.TEST_SUBJECT)
        assert subject.name_id.sp_provided_id == "sp provided id"
        assert subject.name_id.text.strip() == "tmatsuo@example.com"
        assert subject.name_id.format == saml.NAMEID_FORMAT_EMAILADDRESS
        assert isinstance(subject.subject_confirmation[0],
                          saml.SubjectConfirmation)


class TestCondition:
    def setup_class(self):
        self.condition = saml.Condition()
        self.name = "{%s}type" % saml.XSI_NAMESPACE

    def testAccessors(self):
        """Test for Condition accessors."""
        self.condition.extension_attributes[self.name] = "test"
        self.condition.extension_attributes['ExtendedAttribute'] = "value"
        new_condition = saml.condition_from_string(self.condition.to_string())
        assert new_condition.extension_attributes[self.name] == "test"
        assert new_condition.extension_attributes[
                   "ExtendedAttribute"] == "value"

    def testUsingTestData(self):
        """Test for condition_from_string() using test data."""
        condition = saml.condition_from_string(saml2_data.TEST_CONDITION)
        assert condition.extension_attributes[self.name] == "test"
        assert condition.extension_attributes["ExtendedAttribute"] == "value"


class TestAudience:
    def setup_class(self):
        self.audience = saml.Audience()

    def testAccessors(self):
        """Test for Audience accessors"""

        self.audience.text = "http://www.example.com/Audience"
        new_audience = saml.audience_from_string(self.audience.to_string())
        assert new_audience.text.strip() == "http://www.example.com/Audience"

    def testUsingTestData(self):
        """Test audience_from_string using test data"""

        audience = saml.audience_from_string(saml2_data.TEST_AUDIENCE)
        assert audience.text.strip() == "http://www.example.com/Audience"


class TestAudienceRestriction:
    def setup_class(self):
        self.audience_restriction = saml.AudienceRestriction()

    def testAccessors(self):
        """Test for AudienceRestriction accessors"""

        self.audience_restriction.audience = \
            saml.audience_from_string(saml2_data.TEST_AUDIENCE)
        new_audience = saml.audience_restriction_from_string(
            self.audience_restriction.to_string())
        assert self.audience_restriction.audience.text.strip() == \
               "http://www.example.com/Audience"

    def testUsingTestData(self):
        """Test audience_restriction_from_string using test data"""

        audience_restriction = saml.audience_restriction_from_string(
            saml2_data.TEST_AUDIENCE_RESTRICTION)
        assert audience_restriction.audience[0].text.strip() == \
               "http://www.example.com/Audience"


class TestOneTimeUse:
    def setup_class(self):
        self.one_time_use = saml.OneTimeUse()

    def testAccessors(self):
        """Test for OneTimeUse accessors"""
        assert isinstance(self.one_time_use, saml.OneTimeUse)
        assert isinstance(self.one_time_use, saml.ConditionAbstractType_)

    def testUsingTestData(self):
        """Test one_time_use_from_string() using test data"""
        one_time_use = saml.one_time_use_from_string(
            saml2_data.TEST_ONE_TIME_USE)
        assert isinstance(one_time_use, saml.OneTimeUse)
        assert isinstance(one_time_use, saml.ConditionAbstractType_)


class TestProxyRestriction:
    def setup_class(self):
        self.proxy_restriction = saml.ProxyRestriction()

    def testAccessors(self):
        """Test for ProxyRestriction accessors"""

        assert isinstance(self.proxy_restriction, saml.ConditionAbstractType_)
        self.proxy_restriction.count = "2"
        self.proxy_restriction.audience.append(saml.audience_from_string(
            saml2_data.TEST_AUDIENCE))
        new_proxy_restriction = saml.proxy_restriction_from_string(
            self.proxy_restriction.to_string())
        assert new_proxy_restriction.count == "2"
        assert new_proxy_restriction.audience[0].text.strip() == \
               "http://www.example.com/Audience"

    def testUsingTestData(self):
        """Test proxy_restriction_from_string() using test data"""

        proxy_restriction = saml.proxy_restriction_from_string(
            saml2_data.TEST_PROXY_RESTRICTION)
        assert proxy_restriction.count == "2"
        assert proxy_restriction.audience[0].text.strip() == \
               "http://www.example.com/Audience"


class TestConditions:
    def setup_class(self):
        self.conditions = saml.Conditions()

    def testAccessors(self):
        """Test for Conditions accessors"""
        self.conditions.not_before = "2007-08-31T01:05:02Z"
        self.conditions.not_on_or_after = "2007-09-14T01:05:02Z"
        self.conditions.condition.append(saml.Condition())
        self.conditions.audience_restriction.append(saml.AudienceRestriction())
        self.conditions.one_time_use.append(saml.OneTimeUse())
        self.conditions.proxy_restriction.append(saml.ProxyRestriction())
        new_conditions = saml.conditions_from_string(
            self.conditions.to_string())
        assert new_conditions.not_before == "2007-08-31T01:05:02Z"
        assert new_conditions.not_on_or_after == "2007-09-14T01:05:02Z"
        assert isinstance(new_conditions.condition[0], saml.Condition)
        assert isinstance(new_conditions.audience_restriction[0],
                          saml.AudienceRestriction)
        assert isinstance(new_conditions.one_time_use[0],
                          saml.OneTimeUse)
        assert isinstance(new_conditions.proxy_restriction[0],
                          saml.ProxyRestriction)

    def testUsingTestData(self):
        """Test conditions_from_string() using test data"""
        new_conditions = saml.conditions_from_string(saml2_data.TEST_CONDITIONS)
        assert new_conditions.not_before == "2007-08-31T01:05:02Z"
        assert new_conditions.not_on_or_after == "2007-09-14T01:05:02Z"
        assert isinstance(new_conditions.condition[0], saml.Condition)
        assert isinstance(new_conditions.audience_restriction[0],
                          saml.AudienceRestriction)
        assert isinstance(new_conditions.one_time_use[0],
                          saml.OneTimeUse)
        assert isinstance(new_conditions.proxy_restriction[0],
                          saml.ProxyRestriction)


class TestAssertionIDRef:
    def setup_class(self):
        self.assertion_id_ref = saml.AssertionIDRef()

    def testAccessors(self):
        """Test for AssertionIDRef accessors"""
        self.assertion_id_ref.text = "zzlieajngjbkjggjldmgindkckkolcblndbghlhm"
        new_assertion_id_ref = saml.assertion_id_ref_from_string(
            self.assertion_id_ref.to_string())
        assert new_assertion_id_ref.text == \
               "zzlieajngjbkjggjldmgindkckkolcblndbghlhm"

    def testUsingTestData(self):
        """Test assertion_id_ref_from_string() using test data"""
        new_assertion_id_ref = saml.assertion_id_ref_from_string(
            saml2_data.TEST_ASSERTION_ID_REF)
        assert new_assertion_id_ref.text.strip() == \
               "zzlieajngjbkjggjldmgindkckkolcblndbghlhm"


class TestAssertionURIRef:
    def setup_class(self):
        self.assertion_uri_ref = saml.AssertionURIRef()

    def testAccessors(self):
        """Test for AssertionURIRef accessors"""
        self.assertion_uri_ref.text = "http://www.example.com/AssertionURIRef"
        new_assertion_uri_ref = saml.assertion_uri_ref_from_string(
            self.assertion_uri_ref.to_string())
        assert new_assertion_uri_ref.text == \
               "http://www.example.com/AssertionURIRef"

    def testUsingTestData(self):
        """Test assertion_uri_ref_from_string() using test data"""
        new_assertion_uri_ref = saml.assertion_uri_ref_from_string(
            saml2_data.TEST_ASSERTION_URI_REF)
        assert new_assertion_uri_ref.text.strip() == \
               "http://www.example.com/AssertionURIRef"


class TestAction:
    def setup_class(self):
        self.action = saml.Action()

    def testAccessors(self):
        """Test for Action accessors"""
        self.action.namespace = "http://www.example.com/Namespace"
        new_action = saml.action_from_string(self.action.to_string())
        assert new_action.namespace == "http://www.example.com/Namespace"

    def testUsingTestData(self):
        """Test action_from_string() using test data"""
        new_action = saml.action_from_string(saml2_data.TEST_ACTION)
        assert new_action.namespace == "http://www.example.com/Namespace"


class TestEvidence:
    def setup_class(self):
        self.evidence = saml.Evidence()

    def testAccessors(self):
        """Test for Evidence accessors"""
        self.evidence.assertion_id_ref.append(saml.AssertionIDRef())
        self.evidence.assertion_uri_ref.append(saml.AssertionURIRef())
        self.evidence.assertion.append(saml.Assertion())
        self.evidence.encrypted_assertion.append(saml.EncryptedAssertion())
        new_evidence = saml.evidence_from_string(self.evidence.to_string())
        print(new_evidence)
        assert self.evidence.to_string() == new_evidence.to_string()
        assert isinstance(new_evidence.assertion_id_ref[0],
                          saml.AssertionIDRef)
        assert isinstance(new_evidence.assertion_uri_ref[0],
                          saml.AssertionURIRef)
        assert len(new_evidence.assertion) == 1
        assert isinstance(new_evidence.assertion[0], saml.Assertion)
        assert len(new_evidence.encrypted_assertion) == 1
        assert isinstance(new_evidence.encrypted_assertion[0],
                          saml.EncryptedAssertion)

    def testUsingTestData(self):
        """Test evidence_from_string() using test data"""
        # TODO:
        pass


class TestAuthzDecisionStatement:
    def setup_class(self):
        self.authz_decision_statement = saml.AuthzDecisionStatement()

    def testAccessors(self):
        """Test for AuthzDecisionStatement accessors"""
        self.authz_decision_statement.resource = "http://www.example.com/Resource"
        self.authz_decision_statement.decision = saml.DECISION_TYPE_PERMIT
        self.authz_decision_statement.action.append(saml.Action())
        self.authz_decision_statement.evidence = saml.Evidence()
        new_authz_decision_statement = saml.authz_decision_statement_from_string(
            self.authz_decision_statement.to_string())
        assert self.authz_decision_statement.to_string() == \
               new_authz_decision_statement.to_string()
        assert new_authz_decision_statement.resource == \
               "http://www.example.com/Resource"
        assert new_authz_decision_statement.decision == \
               saml.DECISION_TYPE_PERMIT
        assert isinstance(new_authz_decision_statement.action[0],
                          saml.Action)
        assert isinstance(new_authz_decision_statement.evidence,
                          saml.Evidence)


    def testUsingTestData(self):
        """Test authz_decision_statement_from_string() using test data"""
        # TODO:
        pass


class TestAdvice:
    def setup_class(self):
        self.advice = saml.Advice()

    def testAccessors(self):
        """Test for Advice accessors"""
        self.advice.assertion_id_ref.append(saml.AssertionIDRef())
        self.advice.assertion_uri_ref.append(saml.AssertionURIRef())
        self.advice.assertion.append(saml.Assertion())
        self.advice.encrypted_assertion.append(saml.EncryptedAssertion())
        new_advice = saml.advice_from_string(self.advice.to_string())
        assert self.advice.to_string() == new_advice.to_string()
        assert isinstance(new_advice.assertion_id_ref[0],
                          saml.AssertionIDRef)
        assert isinstance(new_advice.assertion_uri_ref[0],
                          saml.AssertionURIRef)
        assert isinstance(new_advice.assertion[0], saml.Assertion)
        assert isinstance(new_advice.encrypted_assertion[0],
                          saml.EncryptedAssertion)

    def testUsingTestData(self):
        """Test advice_from_string() using test data"""
        # TODO:
        pass


class TestAssertion:
    def setup_class(self):
        self.assertion = saml.Assertion()

    def testAccessors(self):
        """Test for Assertion accessors"""
        self.assertion.id = "assertion id"
        self.assertion.version = saml2.VERSION
        self.assertion.issue_instant = "2007-08-31T01:05:02Z"
        self.assertion.issuer = saml.issuer_from_string(saml2_data.TEST_ISSUER)
        self.assertion.signature = ds.signature_from_string(
            ds_data.TEST_SIGNATURE)
        self.assertion.subject = saml.subject_from_string(
            saml2_data.TEST_SUBJECT)
        self.assertion.conditions = saml.conditions_from_string(
            saml2_data.TEST_CONDITIONS)
        self.assertion.advice = saml.Advice()
        self.assertion.statement.append(saml.Statement())
        self.assertion.authn_statement.append(saml.authn_statement_from_string(
            saml2_data.TEST_AUTHN_STATEMENT))
        self.assertion.authz_decision_statement.append(
            saml.AuthzDecisionStatement())
        self.assertion.attribute_statement.append(
            saml.attribute_statement_from_string(
                saml2_data.TEST_ATTRIBUTE_STATEMENT))

        new_assertion = saml.assertion_from_string(self.assertion.to_string())
        assert new_assertion.id == "assertion id"
        assert new_assertion.version == saml2.VERSION
        assert new_assertion.issue_instant == "2007-08-31T01:05:02Z"
        assert isinstance(new_assertion.issuer, saml.Issuer)
        assert isinstance(new_assertion.signature, ds.Signature)
        assert isinstance(new_assertion.subject, saml.Subject)
        assert isinstance(new_assertion.conditions, saml.Conditions)
        assert isinstance(new_assertion.advice, saml.Advice)
        assert isinstance(new_assertion.statement[0], saml.Statement)
        assert isinstance(new_assertion.authn_statement[0],
                          saml.AuthnStatement)
        assert isinstance(new_assertion.authz_decision_statement[0],
                          saml.AuthzDecisionStatement)
        assert isinstance(new_assertion.attribute_statement[0],
                          saml.AttributeStatement)


    def testUsingTestData(self):
        """Test assertion_from_string() using test data"""
        # TODO
        pass

if __name__ == "__main__":
    t = TestSAMLBase()
    t.test_make_vals_multi_dict()
