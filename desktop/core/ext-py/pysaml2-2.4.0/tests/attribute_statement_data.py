#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Testdata for attribute converters """

STATEMENT1 = """<?xml version="1.0" encoding="utf-8"?>
<ns1:AttributeStatement xmlns:ns1="urn:oasis:names:tc:SAML:2.0:assertion">
    <ns1:Attribute Name="urn:mace:dir:attribute-def:eduPersonPrincipalName"
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <ns1:AttributeValue>rohe0002@umu.se</ns1:AttributeValue>
    </ns1:Attribute>
    <ns1:Attribute Name="urn:mace:dir:attribute-def:eduPersonTargetedID"
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <ns1:AttributeValue>a139b2116ad1dd7b91c129a32a242fcc5fd9e821</ns1:AttributeValue>
    </ns1:Attribute>
    <ns1:Attribute Name="urn:mace:dir:attribute-def:displayName" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <ns1:AttributeValue>Hedberg, Roland</ns1:AttributeValue>
    </ns1:Attribute>
    <ns1:Attribute Name="urn:mace:dir:attribute-def:uid" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <ns1:AttributeValue>rohe0002</ns1:AttributeValue>
    </ns1:Attribute>
    <ns1:Attribute Name="urn:mace:dir:attribute-def:eduPersonNickname" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <ns1:AttributeValue>rohe0002</ns1:AttributeValue>
    </ns1:Attribute>
    <ns1:Attribute Name="urn:mace:dir:attribute-def:cn" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <ns1:AttributeValue>Roland Hedberg</ns1:AttributeValue>
    </ns1:Attribute>
    <ns1:Attribute Name="urn:mace:dir:attribute-def:eduPersonAffiliation" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <ns1:AttributeValue>member</ns1:AttributeValue>
        <ns1:AttributeValue>employee</ns1:AttributeValue>
        <ns1:AttributeValue>staff</ns1:AttributeValue>
    </ns1:Attribute>
    <ns1:Attribute Name="urn:mace:dir:attribute-def:street" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <ns1:AttributeValue>Umeå universitet</ns1:AttributeValue>
    </ns1:Attribute>
    <ns1:Attribute Name="urn:mace:dir:attribute-def:postalCode" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <ns1:AttributeValue>901 87</ns1:AttributeValue>
    </ns1:Attribute>
    <ns1:Attribute Name="urn:mace:dir:attribute-def:eduPersonScopedAffiliation" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <ns1:AttributeValue>employee@umu.se</ns1:AttributeValue>
        <ns1:AttributeValue>staff@umu.se</ns1:AttributeValue>
        <ns1:AttributeValue>member@umu.se</ns1:AttributeValue>
    </ns1:Attribute>
    <ns1:Attribute Name="urn:mace:dir:attribute-def:physicalDeliveryOfficeName" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <ns1:AttributeValue>Västra flygeln, plan 4</ns1:AttributeValue>
    </ns1:Attribute>
    <ns1:Attribute Name="urn:mace:dir:attribute-def:employeeType" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <ns1:AttributeValue>IT-arkitekt</ns1:AttributeValue>
        <ns1:AttributeValue>övrig/annan befattning</ns1:AttributeValue>
    </ns1:Attribute>
    <ns1:Attribute Name="urn:mace:dir:attribute-def:ou" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <ns1:AttributeValue>Ladokenheten</ns1:AttributeValue>
        <ns1:AttributeValue>IT-enheten</ns1:AttributeValue>
    </ns1:Attribute>
    <ns1:Attribute Name="urn:mace:dir:attribute-def:givenName" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <ns1:AttributeValue>Roland</ns1:AttributeValue>
    </ns1:Attribute>
    <ns1:Attribute Name="urn:mace:dir:attribute-def:sn" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <ns1:AttributeValue>Hedberg</ns1:AttributeValue>
    </ns1:Attribute>
</ns1:AttributeStatement>"""


STATEMENT2 = """<?xml version="1.0" encoding="utf-8"?>
<saml2:AttributeStatement xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion">
    <saml2:Attribute FriendlyName="uid" Name="urn:oid:0.9.2342.19200300.100.1.1" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml2:AttributeValue xmlns:xs="http://www.w3.org/2001/XMLSchema" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
            xsi:type="xs:string">demouser</saml2:AttributeValue>
    </saml2:Attribute>
    <saml2:Attribute FriendlyName="surname"
        Name="urn:oid:2.5.4.4" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml2:AttributeValue 
            xmlns:xs="http://www.w3.org/2001/XMLSchema" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
            xsi:type="xs:string">SWITCHaai</saml2:AttributeValue>
    </saml2:Attribute>
    <saml2:Attribute FriendlyName="givenName" 
        Name="urn:oid:2.5.4.42" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml2:AttributeValue 
            xmlns:xs="http://www.w3.org/2001/XMLSchema" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
            xsi:type="xs:string">Demouser</saml2:AttributeValue>
    </saml2:Attribute>
    <saml2:Attribute FriendlyName="eduPersonAffiliation" 
        Name="urn:oid:1.3.6.1.4.1.5923.1.1.1.1" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml2:AttributeValue 
            xmlns:xs="http://www.w3.org/2001/XMLSchema" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
            xsi:type="xs:string">staff</saml2:AttributeValue>
    </saml2:Attribute>
    <saml2:Attribute FriendlyName="eduPersonEntitlement" 
        Name="urn:oid:1.3.6.1.4.1.5923.1.1.1.7" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml2:AttributeValue 
            xmlns:xs="http://www.w3.org/2001/XMLSchema" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
            xsi:type="xs:string">http://example.org/res/99999</saml2:AttributeValue>
        <saml2:AttributeValue 
            xmlns:xs="http://www.w3.org/2001/XMLSchema" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
            xsi:type="xs:string">http://publisher-xy.com/e-journals</saml2:AttributeValue>
    </saml2:Attribute>
    <saml2:Attribute FriendlyName="mail" 
        Name="urn:oid:0.9.2342.19200300.100.1.3" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml2:AttributeValue 
            xmlns:xs="http://www.w3.org/2001/XMLSchema" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
            xsi:type="xs:string">demouser@example.org</saml2:AttributeValue>
    </saml2:Attribute>
</saml2:AttributeStatement>"""

STATEMENT3 = """<?xml version='1.0' encoding='UTF-8'?>
<ns0:AttributeStatement xmlns:ns0="urn:oasis:names:tc:SAML:2.0:assertion">
    <ns0:Attribute Name="umuselin">
        <ns0:AttributeValue>1234567890</ns0:AttributeValue>
    </ns0:Attribute>
    <ns0:Attribute Name="edupersonaffiliation">
        <ns0:AttributeValue>staff</ns0:AttributeValue>
    </ns0:Attribute>
    <ns0:Attribute FriendlyName="surname" Name="urn:oid:2.5.4.4" 
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <ns0:AttributeValue>Hedberg</ns0:AttributeValue>
    </ns0:Attribute>
    <ns0:Attribute Name="uid">
        <ns0:AttributeValue>roland</ns0:AttributeValue>
    </ns0:Attribute>
    <ns0:Attribute Name="givenname">
        <ns0:AttributeValue>Roland</ns0:AttributeValue>
    </ns0:Attribute>
</ns0:AttributeStatement>"""

STATEMENT4 = """<?xml version='1.0' encoding='UTF-8'?>
<ns0:AttributeStatement xmlns:ns0="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <ns0:Attribute Name="user_id" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified">
        <ns0:AttributeValue xsi:type="xs:string">bob</ns0:AttributeValue>
    </ns0:Attribute>
    <ns0:Attribute Name="NameID" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified">
        <ns0:AttributeValue xsi:type="xs:string">bobsnameagain</ns0:AttributeValue>
    </ns0:Attribute>
</ns0:AttributeStatement>"""

STATEMENT_MIXED = """<?xml version="1.0" encoding="utf-8"?>
<saml2:AttributeStatement xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion">
    <saml2:Attribute FriendlyName="uid" Name="urn:oid:0.9.2342.19200300.100.1.1"
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml2:AttributeValue xmlns:xs="http://www.w3.org/2001/XMLSchema"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:type="xs:string">demouser</saml2:AttributeValue>
    </saml2:Attribute>
    <saml2:Attribute FriendlyName="swissEduPersonHomeOrganizationType"
        Name="urn:oid:2.16.756.1.2.5.1.1.5"
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml2:AttributeValue
            xmlns:xs="http://www.w3.org/2001/XMLSchema"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:type="xs:string">others</saml2:AttributeValue>
    </saml2:Attribute>
    <saml2:Attribute Name="urn:mace:dir:attribute-def:givenName"
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <saml2:AttributeValue>Roland</saml2:AttributeValue>
    </saml2:Attribute>
    <saml2:Attribute Name="urn:mace:dir:attribute-def:sn"
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
        <saml2:AttributeValue>Hedberg</saml2:AttributeValue>
    </saml2:Attribute>
    <saml2:Attribute FriendlyName="eduPersonAffiliation"
        Name="urn:oid:1.3.6.1.4.1.5923.1.1.1.1"
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml2:AttributeValue
            xmlns:xs="http://www.w3.org/2001/XMLSchema"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:type="xs:string">staff</saml2:AttributeValue>
    </saml2:Attribute>
    <saml2:Attribute Name="urn:example:com:foo"
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:example">
        <saml2:AttributeValue>Thing</saml2:AttributeValue>
    </saml2:Attribute>
    <saml2:Attribute Name="user_id"
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified">
        <saml2:AttributeValue>bob</saml2:AttributeValue>
    </saml2:Attribute>
</saml2:AttributeStatement>"""
