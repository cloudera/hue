#!/usr/bin/env python

from saml2 import attribute_converter, saml

from attribute_statement_data import *

from pathutils import full_path
from saml2.attribute_converter import AttributeConverterNOOP, from_local
from saml2.attribute_converter import AttributeConverter
from saml2.attribute_converter import to_local
from saml2.saml import attribute_from_string, name_id_from_string, NameID, NAMEID_FORMAT_PERSISTENT
from saml2.saml import attribute_statement_from_string


def _eq(l1, l2):
    return set(l1) == set(l2)


BASIC_NF = 'urn:oasis:names:tc:SAML:2.0:attrname-format:basic'
URI_NF = 'urn:oasis:names:tc:SAML:2.0:attrname-format:uri'
SAML1 = 'urn:mace:shibboleth:1.0:attributeNamespace:uri'


def test_default():
    acs = attribute_converter.ac_factory()
    assert acs


class TestAC():
    def setup_class(self):
        self.acs = attribute_converter.ac_factory(full_path("attributemaps"))

    def test_setup(self):
        print(self.acs)
        assert len(self.acs) == 3
        assert _eq([a.name_format for a in self.acs], [BASIC_NF, URI_NF, SAML1])

    def test_ava_fro_1(self):
        ats = saml.attribute_statement_from_string(STATEMENT1)
        # print(ats)
        ava = None

        for ac in self.acs:
            try:
                ava = ac.fro(ats)
            except attribute_converter.UnknownNameFormat:
                pass
            # break if we have something
            if ava:
                break
        print(ava.keys())
        assert _eq(ava.keys(), ['givenName', 'displayName', 'uid',
                                'eduPersonNickname', 'street',
                                'eduPersonScopedAffiliation',
                                'employeeType', 'eduPersonAffiliation',
                                'eduPersonPrincipalName', 'sn', 'postalCode',
                                'physicalDeliveryOfficeName', 'ou',
                                'eduPersonTargetedID', 'cn'])

    def test_ava_fro_2(self):
        ats = saml.attribute_statement_from_string(STATEMENT2)
        # print(ats)
        ava = {}
        for ac in self.acs:
            ava.update(ac.fro(ats))

        print(ava.keys())
        assert _eq(ava.keys(), ['eduPersonEntitlement', 'eduPersonAffiliation',
                                'uid', 'mail', 'givenName', 'sn'])

    def test_to_attrstat_1(self):
        ava = {"givenName": "Roland", "sn": "Hedberg"}

        statement = attribute_converter.from_local(self.acs, ava, BASIC_NF)

        assert statement is not None
        assert len(statement) == 2
        a0 = statement[0]
        a1 = statement[1]
        if a0.friendly_name == 'sn':
            assert a0.name == 'urn:mace:dir:attribute-def:sn'
            assert a0.name_format == BASIC_NF
            assert a1.friendly_name == "givenName"
            assert a1.name == 'urn:mace:dir:attribute-def:givenName'
            assert a1.name_format == BASIC_NF
        elif a0.friendly_name == 'givenName':
            assert a0.name == 'urn:mace:dir:attribute-def:givenName'
            assert a0.name_format == BASIC_NF
            assert a1.friendly_name == "sn"
            assert a1.name == 'urn:mace:dir:attribute-def:sn'
            assert a1.name_format == BASIC_NF
        else:
            assert False

    def test_to_attrstat_2(self):
        ava = {"givenName": "Roland", "surname": "Hedberg"}

        statement = attribute_converter.from_local(self.acs, ava, URI_NF)

        assert len(statement) == 2
        a0 = statement[0]
        a1 = statement[1]
        if a0.friendly_name == 'surname':
            assert a0.name == 'urn:oid:2.5.4.4'
            assert a0.name_format == URI_NF
            assert a1.friendly_name == "givenName"
            assert a1.name == 'urn:oid:2.5.4.42'
            assert a1.name_format == URI_NF
        elif a0.friendly_name == 'givenName':
            assert a0.name == 'urn:oid:2.5.4.42'
            assert a0.name_format == URI_NF
            assert a1.friendly_name == "surname"
            assert a1.name == 'urn:oid:2.5.4.4'
            assert a1.name_format == URI_NF
        else:
            print(a0.friendly_name)
            assert False

    def test_to_local_name(self):

        attr = [
            saml.Attribute(
                friendly_name="surName",
                name="urn:oid:2.5.4.4",
                name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"),
            saml.Attribute(
                friendly_name="efternamn",
                name="urn:oid:2.5.4.42",
                name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"),
            saml.Attribute(
                friendly_name="titel",
                name="urn:oid:2.5.4.12",
                name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")]

        lan = [attribute_converter.to_local_name(self.acs, a) for a in attr]

        assert _eq(lan, ['sn', 'givenName', 'title'])

    def test_to_local_name_from_unspecified(self):
        _xml = """<?xml version='1.0' encoding='UTF-8'?>
        <ns0:AttributeStatement xmlns:ns0="urn:oasis:names:tc:SAML:2.0:assertion">
<ns0:Attribute
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    Name="EmailAddress"
    NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified">
    <ns0:AttributeValue xsi:type="xs:string">foo@bar.com</ns0:AttributeValue>
</ns0:Attribute></ns0:AttributeStatement>"""

        attr = attribute_statement_from_string(_xml)
        ava = attribute_converter.to_local(self.acs, attr)

        assert _eq(list(ava.keys()), ['EmailAddress'])

    def test_to_local_name_from_basic(self):
        attr = [
            saml.Attribute(
                name="urn:mace:dir:attribute-def:eduPersonPrimaryOrgUnitDN",
                name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:basic")
        ]

        lan = [attribute_converter.to_local_name(self.acs, a) for a in attr]

        assert _eq(lan, ['eduPersonPrimaryOrgUnitDN'])

    def test_to_and_for(self):
        ava = {"givenName": "Roland", "surname": "Hedberg"}

        basic_ac = [a for a in self.acs if a.name_format == BASIC_NF][0]

        attr_state = saml.AttributeStatement(basic_ac.to_(ava))

        oava = basic_ac.fro(attr_state)

        assert _eq(ava.keys(), oava.keys())

    def test_unspecified_name_format(self):
        ats = saml.attribute_statement_from_string(STATEMENT4)
        ava = to_local(self.acs, ats)
        assert ava == {'user_id': ['bob'], 'NameID': ['bobsnameagain']}

    def test_mixed_attributes_1(self):
        ats = saml.attribute_statement_from_string(STATEMENT_MIXED)
        ava = to_local(self.acs, ats)
        assert ava == {'eduPersonAffiliation': ['staff'],
                       'givenName': ['Roland'], 'sn': ['Hedberg'],
                       'uid': ['demouser'], 'user_id': ['bob']}

        # Allow unknown
        ava = to_local(self.acs, ats, True)
        assert ava == {'eduPersonAffiliation': ['staff'],
                       'givenName': ['Roland'], 'sn': ['Hedberg'],
                       'swissEduPersonHomeOrganizationType': ['others'],
                       'uid': ['demouser'], 'urn:example:com:foo': ['Thing'],
                       'user_id': ['bob']}

    def test_adjust_with_only_from_defined(self):
        attr_conv = AttributeConverter()
        attr_conv._fro = {"id1": "name1", "id2": "name2"}
        attr_conv.adjust()
        assert attr_conv._to is not None

    def test_adjust_with_only_to_defined(self):
        attr_conv = AttributeConverter()
        attr_conv._to = {"id1": "name1", "id2": "name2"}
        attr_conv.adjust()
        assert attr_conv._fro is not None

    def test_adjust_with_no_mapping_defined(self):
        attr_conv = AttributeConverter()
        attr_conv.adjust()
        assert attr_conv._fro is None and attr_conv._to is None

    def test_from_local_nest_eduPersonTargetedID_in_NameID(self):
        ava = {"edupersontargetedid": ["test value1", "test value2"]}
        attributes = from_local(self.acs, ava, URI_NF)
        assert len(attributes) == 1
        assert len(attributes[0].attribute_value) == 2
        assert attributes[0].attribute_value[0].extension_elements[0].text == "test value1"
        assert attributes[0].attribute_value[1].extension_elements[0].text == "test value2"


def test_noop_attribute_conversion():
    ava = {"urn:oid:2.5.4.4": "Roland", "urn:oid:2.5.4.42": "Hedberg"}
    aconv = AttributeConverterNOOP(URI_NF)
    res = aconv.to_(ava)

    print(res)
    assert len(res) == 2
    for attr in res:
        assert len(attr.attribute_value) == 1
        if attr.name == "urn:oid:2.5.4.42":
            assert attr.name_format == URI_NF
            assert attr.attribute_value[0].text == "Hedberg"
        elif attr.name == "urn:oid:2.5.4.4":
            assert attr.name_format == URI_NF
            assert attr.attribute_value[0].text == "Roland"


ava = """<?xml version='1.0' encoding='UTF-8'?>
<ns0:Attribute xmlns:ns0="urn:oasis:names:tc:SAML:2.0:assertion"
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   FriendlyName="schacHomeOrganization" Name="urn:oid:1.3.6.1.4.1.25178.1.2.9"
   NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
   <ns0:AttributeValue xsi:nil="true" xsi:type="xs:string">
     uu.se
   </ns0:AttributeValue>
</ns0:Attribute>"""


def test_schac():
    attr = attribute_from_string(ava)
    acs = attribute_converter.ac_factory()
    for ac in acs:
        try:
            res = ac.ava_from(attr)
            assert res[0] == "schacHomeOrganization"
        except KeyError:
            pass


if __name__ == "__main__":
    t = TestAC()
    t.setup_class()
    t.test_to_local_name_from_unspecified()
