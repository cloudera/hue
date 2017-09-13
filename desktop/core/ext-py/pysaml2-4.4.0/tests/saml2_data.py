#!/usr/bin/env python
#

"""Test data for saml2"""

__author__ = 'tmatsuo@example.com (Takashi MATSUO)'

TEST_NAME_ID = """<?xml version="1.0" encoding="utf-8"?>
<NameID xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
  Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
  SPProvidedID="sp provided id">
  tmatsuo@example.com
</NameID>
"""

TEST_ISSUER = """<?xml version="1.0" encoding="utf-8"?>
<Issuer xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
  http://www.example.com/test
</Issuer>
"""

TEST_SUBJECT_LOCALITY = """<?xml version="1.0" encoding="utf-8"?>
<SubjectLocality xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
  Address="127.0.0.1" DNSName="localhost"/>
"""

TEST_AUTHN_CONTEXT_CLASS_REF = """<?xml version="1.0" encoding="utf-8"?>
<AuthnContextClassRef xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
  http://www.example.com/authnContextClassRef
</AuthnContextClassRef>
"""

TEST_AUTHN_CONTEXT_DECL_REF = """<?xml version="1.0" encoding="utf-8"?>
<AuthnContextDeclRef xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
  http://www.example.com/authnContextDeclRef
</AuthnContextDeclRef>
"""

TEST_AUTHN_CONTEXT_DECL = """<?xml version="1.0" encoding="utf-8"?>
<AuthnContextDecl xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
  http://www.example.com/authnContextDecl
</AuthnContextDecl>
"""

TEST_AUTHENTICATING_AUTHORITY = """<?xml version="1.0" encoding="utf-8"?>
<AuthenticatingAuthority xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
  http://www.example.com/authenticatingAuthority
</AuthenticatingAuthority>
"""

TEST_AUTHN_CONTEXT = """<?xml version="1.0" encoding="utf-8"?>
<AuthnContext xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
  <AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:Password</AuthnContextClassRef>
</AuthnContext>
"""

TEST_AUTHN_STATEMENT = """<?xml version="1.0" encoding="utf-8"?>
<AuthnStatement xmlns="urn:oasis:names:tc:SAML:2.0:assertion" AuthnInstant="2007-08-31T01:05:02Z" SessionNotOnOrAfter="2007-09-14T01:05:02Z">
  <AuthnContext>
    <AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:Password</AuthnContextClassRef>
  </AuthnContext>
</AuthnStatement>
"""

TEST_ATTRIBUTE_VALUE = """<?xml version="1.0" encoding="utf-8"?>
<AttributeValue xmlns="urn:oasis:names:tc:SAML:2.0:assertion">value for test attribute</AttributeValue>
"""

TEST_ATTRIBUTE = """<?xml version="1.0" encoding="utf-8"?>
<Attribute Name="testAttribute"
  NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified"
  FriendlyName="test attribute"
  xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
  <AttributeValue >value1 of test attribute</AttributeValue>
  <AttributeValue >value2 of test attribute</AttributeValue>
</Attribute>
"""

TEST_ATTRIBUTE_STATEMENT = """<?xml version="1.0" encoding="utf-8"?>
<AttributeStatement xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
  <Attribute Name="testAttribute"
    NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified"
    FriendlyName="test attribute">
    <AttributeValue >value1 of test attribute</AttributeValue>
    <AttributeValue >value2 of test attribute</AttributeValue>
  </Attribute>
  <Attribute Name="http://www.example.com/testAttribute2"
    NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"
    FriendlyName="test attribute2">
    <AttributeValue >value1 of test attribute2</AttributeValue>
    <AttributeValue >value2 of test attribute2</AttributeValue>
  </Attribute>
</AttributeStatement>
"""

TEST_SUBJECT_CONFIRMATION_DATA = """<?xml version="1.0" encoding="utf-8"?>
<SubjectConfirmationData
  NotBefore="2007-08-31T01:05:02Z"
  NotOnOrAfter="2007-09-14T01:05:02Z"
  Recipient="recipient"
  InResponseTo="responseID"
  Address="127.0.0.1"
  xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
</SubjectConfirmationData>
"""

TEST_SUBJECT_CONFIRMATION = """<?xml version="1.0" encoding="utf-8"?>
<SubjectConfirmation
  Method="urn:oasis:names:tc:SAML:2.0:cm:bearer"
  xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
  <NameID xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
    Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
    SPProvidedID="sp provided id">
    tmatsuo@example.com
  </NameID>
  <SubjectConfirmationData
    NotBefore="2007-08-31T01:05:02Z"
    NotOnOrAfter="2007-09-14T01:05:02Z"
    Recipient="recipient"
    InResponseTo="responseID"
    Address="127.0.0.1">
  </SubjectConfirmationData>
</SubjectConfirmation>
"""

TEST_SUBJECT = """<?xml version="1.0" encoding="utf-8"?>
<Subject xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
  <NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
    SPProvidedID="sp provided id">
    tmatsuo@example.com
  </NameID>
  <SubjectConfirmation
    Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
    <NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
      SPProvidedID="sp provided id2">
      admin@example.com
    </NameID>
    <SubjectConfirmationData
      NotBefore="2007-08-31T01:05:02Z"
      NotOnOrAfter="2007-09-14T01:05:02Z"
      Recipient="recipient"
      InResponseTo="responseID"
      Address="127.0.0.1">
    </SubjectConfirmationData>
  </SubjectConfirmation>
</Subject>
"""

TEST_CONDITION = """<?xml version="1.0" encoding="utf-8"?>
<Condition xmlns="urn:oasis:names:tc:SAML:2.0:assertion" xsi:type="test" ExtendedAttribute="value" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
"""

TEST_AUDIENCE = """<?xml version="1.0" encoding="utf-8"?>
<Audience xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
  http://www.example.com/Audience
</Audience>
"""

TEST_AUDIENCE_RESTRICTION = """<?xml version="1.0" encoding="utf-8"?>
<AudienceRestriction xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
  <Audience>
    http://www.example.com/Audience
  </Audience>
</AudienceRestriction>
"""

TEST_ONE_TIME_USE = """<?xml version="1.0" encoding="utf-8"?>
<OneTimeUse xmlns="urn:oasis:names:tc:SAML:2.0:assertion"/>
"""

TEST_PROXY_RESTRICTION = """<?xml version="1.0" encoding="utf-8"?>
<ProxyRestriction xmlns="urn:oasis:names:tc:SAML:2.0:assertion" Count="2">
  <Audience>http://www.example.com/Audience</Audience>
</ProxyRestriction>
"""

TEST_CONDITIONS = """<?xml version="1.0" encoding="utf-8"?>
<Conditions
  xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
  NotBefore="2007-08-31T01:05:02Z"
  NotOnOrAfter="2007-09-14T01:05:02Z">
  <Condition
    xsi:type="test"
    ExtendedAttribute="value"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
  <AudienceRestriction>
    <Audience>
      http://www.example.com/Audience
    </Audience>
  </AudienceRestriction>
  <OneTimeUse />
  <ProxyRestriction  Count="2">
    <Audience>http://www.example.com/Audience</Audience>
  </ProxyRestriction>
</Conditions>
"""

TEST_ASSERTION_ID_REF = """<?xml version="1.0" encoding="utf-8"?>
<AssertionIDRef xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
  zzlieajngjbkjggjldmgindkckkolcblndbghlhm
</AssertionIDRef>
"""

TEST_ASSERTION_URI_REF = """<?xml version="1.0" encoding="utf-8"?>
<AssertionURIRef xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
  http://www.example.com/AssertionURIRef
</AssertionURIRef>
"""

TEST_ACTION = """<?xml version="1.0" encoding="utf-8"?>
<Action xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
  Namespace="http://www.example.com/Namespace"/>
"""

