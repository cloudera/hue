#!/usr/bin/env python
#

"""Test data for saml2"""

__author__ = 'tmatsuo@example.com (Takashi MATSUO)'

TEST_STATUS_CODE = """<?xml version="1.0" encoding="utf-8"?>
<StatusCode xmlns="urn:oasis:names:tc:SAML:2.0:protocol"
  Value="urn:oasis:names:tc:SAML:2.0:status:Responder">
  <StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:RequestDenied" />
</StatusCode>
"""

TEST_STATUS = """<?xml version="1.0" encoding="utf-8"?>
<Status xmlns="urn:oasis:names:tc:SAML:2.0:protocol">
  <StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Responder">
    <StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:UnsupportedBinding" />
  </StatusCode>
  <StatusMessage>status message</StatusMessage>
  <StatusDetail><foo bar="bar" /></StatusDetail>
</Status>
"""

TEST_NAME_ID_POLICY = """<?xml version="1.0" encoding="utf-8"?>
<NameIDPolicy xmlns="urn:oasis:names:tc:SAML:2.0:protocol"
  Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
  SPNameQualifier="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"
  AllowCreate="false"
/>
"""

TEST_IDP_ENTRY = """<?xml version="1.0" encoding="utf-8"?>
<IDPEntry xmlns="urn:oasis:names:tc:SAML:2.0:protocol"
  ProviderID="http://www.example.com/provider"
  Name="the provider"
  Loc="http://www.example.com/Loc"
/>
"""

TEST_IDP_LIST = """<?xml version="1.0" encoding="utf-8"?>
<IDPList xmlns="urn:oasis:names:tc:SAML:2.0:protocol">
  <IDPEntry ProviderID="http://www.example.com/provider"
    Name="the provider"
    Loc="http://www.example.com/Loc" />
  <GetComplete>http://www.example.com/GetComplete</GetComplete>
</IDPList>
"""

TEST_SCOPING = """<?xml version="1.0" encoding="utf-8"?>
<Scoping xmlns="urn:oasis:names:tc:SAML:2.0:protocol" ProxyCount="1">
  <IDPList>
    <IDPEntry ProviderID="http://www.example.com/provider"
      Name="the provider"
      Loc="http://www.example.com/Loc" />
    <GetComplete>http://www.example.com/GetComplete</GetComplete>
  </IDPList>
  <RequesterID>http://www.example.com/RequesterID</RequesterID>
</Scoping>
"""

TEST_REQUESTED_AUTHN_CONTEXT = """<?xml version="1.0" encoding="utf-8"?>
<RequestedAuthnContext xmlns="urn:oasis:names:tc:SAML:2.0:protocol"
  Comparison="exact">
  <AuthnContextClassRef xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
    http://www.example.com/authnContextClassRef
  </AuthnContextClassRef>
  <AuthnContextDeclRef xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
    http://www.example.com/authnContextDeclRef
  </AuthnContextDeclRef>
</RequestedAuthnContext>
"""

TEST_AUTHN_REQUEST = """<?xml version="1.0" encoding="utf-8"?>
<AuthnRequest
  ID="request id"
  Version="2.0"
  IssueInstant="2007-09-14T01:05:02Z"
  Destination="http://www.example.com/Destination"
  Consent="urn:oasis:names:tc:SAML:2.0:consent:unspecified"
  ForceAuthn="true"
  IsPassive="true"
  AssertionConsumerServiceIndex="1"
  AssertionConsumerServiceURL="http://www.example.com/acs"
  ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  AttributeConsumingServiceIndex="2"
  ProviderName="provider name"
  xmlns="urn:oasis:names:tc:SAML:2.0:protocol">
  <Issuer xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
    http://www.example.com/test
  </Issuer>
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#" Id="id">
    <SignedInfo Id="id">
      <CanonicalizationMethod
        Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315#WithComments">
      </CanonicalizationMethod>
      <SignatureMethod
        Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1">
        <HMACOutputLength>8</HMACOutputLength>
      </SignatureMethod>
      <Reference Id="id" URI="http://www.example.com/URI"
        Type="http://www.example.com/Type">
        <Transforms>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature">
            <XPath>xpath</XPath>
          </Transform>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature">
            <XPath>xpath</XPath>
          </Transform>
        </Transforms>
        <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
        <DigestValue>digest value</DigestValue>
      </Reference>
    </SignedInfo>
    <SignatureValue Id="id">
      signature value
    </SignatureValue>
    <KeyInfo Id="id">
      <KeyName>
        key name
      </KeyName>
      <KeyValue>
        <DSAKeyValue>
          <P>p</P>
          <Q>q</Q>
          <G>g</G>
          <Y>y</Y>
          <J>j</J>
          <Seed>seed</Seed>
          <PgenCounter>pgen counter</PgenCounter>
        </DSAKeyValue>
      </KeyValue>
      <RetrievalMethod URI="http://www.example.com/URI"
        Type="http://www.example.com/Type">
        <Transforms>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature">
            <XPath>xpath</XPath>
          </Transform>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature">
            <XPath>xpath</XPath>
          </Transform>
        </Transforms>
      </RetrievalMethod>
      <X509Data>
        <X509IssuerSerial>
          <X509IssuerName>issuer name</X509IssuerName>
          <X509IssuerNumber>1</X509IssuerNumber>
        </X509IssuerSerial>
        <X509SKI>x509 ski</X509SKI>
        <X509SubjectName>x509 subject name</X509SubjectName>
        <X509Certificate>x509 certificate</X509Certificate>
        <X509CRL>x509 crl</X509CRL>
      </X509Data>
      <PGPData>
        <PGPKeyID>pgp key id</PGPKeyID>
        <PGPKeyPacket>pgp key packet</PGPKeyPacket>
      </PGPData>
      <MgmtData>
        mgmt data
      </MgmtData>
      <SPKIData>
        <SPKISexp>spki sexp</SPKISexp>
        <SPKISexp>spki sexp2</SPKISexp>
      </SPKIData>  
    </KeyInfo>
    <Object Id="object_id" Encoding="http://www.w3.org/2000/09/xmldsig#base64">
      V2VkIEp1biAgNCAxMjoxMTowMyBFRFQgMjAwMwo
    </Object>
  </Signature>
  <Extensions><test/></Extensions>
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
  <NameIDPolicy xmlns="urn:oasis:names:tc:SAML:2.0:protocol"
    Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
    SPNameQualifier="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"
    AllowCreate="false"/>
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
  <RequestedAuthnContext xmlns="urn:oasis:names:tc:SAML:2.0:protocol"
    Comparison="exact">
    <AuthnContextClassRef xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
      http://www.example.com/authnContextClassRef
    </AuthnContextClassRef>
    <AuthnContextDeclRef xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
      http://www.example.com/authnContextDeclRef
    </AuthnContextDeclRef>
  </RequestedAuthnContext>
  <Scoping xmlns="urn:oasis:names:tc:SAML:2.0:protocol" ProxyCount="1">
    <IDPList>
      <IDPEntry ProviderID="http://www.example.com/provider"
        Name="the provider"
        Loc="http://www.example.com/Loc" />
      <GetComplete>http://www.example.com/GetComplete</GetComplete>
    </IDPList>
    <RequesterID>http://www.example.com/RequesterID</RequesterID>
  </Scoping>
</AuthnRequest>
"""

TEST_LOGOUT_REQUEST = """<?xml version="1.0" encoding="utf-8"?>
<LogoutRequest
  ID="request id"
  Version="2.0"
  IssueInstant="2007-09-14T01:05:02Z"
  Destination="http://www.example.com/Destination"
  Consent="urn:oasis:names:tc:SAML:2.0:consent:unspecified"
  NotOnOrAfter="2007-10-14T01:05:02Z"
  Reason="http://www.example.com/Reason"
  xmlns="urn:oasis:names:tc:SAML:2.0:protocol">
  <Issuer xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
    http://www.example.com/test
  </Issuer>
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#" Id="id">
    <SignedInfo Id="id">
      <CanonicalizationMethod
        Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315#WithComments">
      </CanonicalizationMethod>
      <SignatureMethod
        Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1">
        <HMACOutputLength>8</HMACOutputLength>
      </SignatureMethod>
      <Reference Id="id" URI="http://www.example.com/URI"
        Type="http://www.example.com/Type">
        <Transforms>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature">
            <XPath>xpath</XPath>
          </Transform>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature">
            <XPath>xpath</XPath>
          </Transform>
        </Transforms>
        <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
        <DigestValue>digest value</DigestValue>
      </Reference>
    </SignedInfo>
    <SignatureValue Id="id">
      signature value
    </SignatureValue>
    <KeyInfo Id="id">
      <KeyName>
        key name
      </KeyName>
      <KeyValue>
        <DSAKeyValue>
          <P>p</P>
          <Q>q</Q>
          <G>g</G>
          <Y>y</Y>
          <J>j</J>
          <Seed>seed</Seed>
          <PgenCounter>pgen counter</PgenCounter>
        </DSAKeyValue>
      </KeyValue>
      <RetrievalMethod URI="http://www.example.com/URI"
        Type="http://www.example.com/Type">
        <Transforms>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature">
            <XPath>xpath</XPath>
          </Transform>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature">
            <XPath>xpath</XPath>
          </Transform>
        </Transforms>
      </RetrievalMethod>
      <X509Data>
        <X509IssuerSerial>
          <X509IssuerName>issuer name</X509IssuerName>
          <X509IssuerNumber>1</X509IssuerNumber>
        </X509IssuerSerial>
        <X509SKI>x509 ski</X509SKI>
        <X509SubjectName>x509 subject name</X509SubjectName>
        <X509Certificate>x509 certificate</X509Certificate>
        <X509CRL>x509 crl</X509CRL>
      </X509Data>
      <PGPData>
        <PGPKeyID>pgp key id</PGPKeyID>
        <PGPKeyPacket>pgp key packet</PGPKeyPacket>
      </PGPData>
      <MgmtData>
        mgmt data
      </MgmtData>
      <SPKIData>
        <SPKISexp>spki sexp</SPKISexp>
        <SPKISexp>spki sexp2</SPKISexp>
      </SPKIData>  
    </KeyInfo>
    <Object Id="object_id" Encoding="http://www.w3.org/2000/09/xmldsig#base64">
      V2VkIEp1biAgNCAxMjoxMTowMyBFRFQgMjAwMwo
    </Object>
  </Signature>
  <Extensions><test/></Extensions>
  <BaseID xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
    Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
    SPProvidedID="sp provided id">
    tmatsuo@example.com
  </BaseID>
  <NameID xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
    Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
    SPProvidedID="sp provided id">
    tmatsuo@example.com
  </NameID>
  <EncryptedID xmlns="urn:oasis:names:tc:SAML:2.0:assertion" />
  <SessionIndex>session index</SessionIndex>
</LogoutRequest>
"""

TEST_LOGOUT_RESPONSE = """<?xml version="1.0" encoding="utf-8"?>
<LogoutResponse
  ID="response id"
  InResponseTo="request id"
  Version="2.0"
  IssueInstant="2007-09-14T01:05:02Z"
  Destination="http://www.example.com/Destination"
  Consent="urn:oasis:names:tc:SAML:2.0:consent:unspecified"
  xmlns="urn:oasis:names:tc:SAML:2.0:protocol">
  <Issuer xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
    http://www.example.com/test
  </Issuer>
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#" Id="id">
    <SignedInfo Id="id">
      <CanonicalizationMethod
        Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315#WithComments">
      </CanonicalizationMethod>
      <SignatureMethod
        Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1">
        <HMACOutputLength>8</HMACOutputLength>
      </SignatureMethod>
      <Reference Id="id" URI="http://www.example.com/URI"
        Type="http://www.example.com/Type">
        <Transforms>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature">
            <XPath>xpath</XPath>
          </Transform>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature">
            <XPath>xpath</XPath>
          </Transform>
        </Transforms>
        <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
        <DigestValue>digest value</DigestValue>
      </Reference>
    </SignedInfo>
    <SignatureValue Id="id">
      signature value
    </SignatureValue>
    <KeyInfo Id="id">
      <KeyName>
        key name
      </KeyName>
      <KeyValue>
        <DSAKeyValue>
          <P>p</P>
          <Q>q</Q>
          <G>g</G>
          <Y>y</Y>
          <J>j</J>
          <Seed>seed</Seed>
          <PgenCounter>pgen counter</PgenCounter>
        </DSAKeyValue>
      </KeyValue>
      <RetrievalMethod URI="http://www.example.com/URI"
        Type="http://www.example.com/Type">
        <Transforms>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature">
            <XPath>xpath</XPath>
          </Transform>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature">
            <XPath>xpath</XPath>
          </Transform>
        </Transforms>
      </RetrievalMethod>
      <X509Data>
        <X509IssuerSerial>
          <X509IssuerName>issuer name</X509IssuerName>
          <X509IssuerNumber>1</X509IssuerNumber>
        </X509IssuerSerial>
        <X509SKI>x509 ski</X509SKI>
        <X509SubjectName>x509 subject name</X509SubjectName>
        <X509Certificate>x509 certificate</X509Certificate>
        <X509CRL>x509 crl</X509CRL>
      </X509Data>
      <PGPData>
        <PGPKeyID>pgp key id</PGPKeyID>
        <PGPKeyPacket>pgp key packet</PGPKeyPacket>
      </PGPData>
      <MgmtData>
        mgmt data
      </MgmtData>
      <SPKIData>
        <SPKISexp>spki sexp</SPKISexp>
        <SPKISexp>spki sexp2</SPKISexp>
      </SPKIData>  
    </KeyInfo>
    <Object Id="object_id" Encoding="http://www.w3.org/2000/09/xmldsig#base64">
      V2VkIEp1biAgNCAxMjoxMTowMyBFRFQgMjAwMwo
    </Object>
  </Signature>
  <Extensions><test/></Extensions>
  <Status>
    <StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Responder">
      <StatusCode
        Value="urn:oasis:names:tc:SAML:2.0:status:UnsupportedBinding" />
    </StatusCode>
    <StatusMessage>status message</StatusMessage>
    <StatusDetail><foo bar="bar" /></StatusDetail>
  </Status>
</LogoutResponse>
"""
