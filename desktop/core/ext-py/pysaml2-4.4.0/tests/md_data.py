#!/usr/bin/env python
#

"""Test data for md"""

__author__ = 'tmatsuo@example.com (Takashi MATSUO)'

TEST_ENDPOINT = """<?xml version="1.0" encoding="utf-8"?>
<EndpointType xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
"""

TEST_SINGLE_LOGOUT_SERVICE = """<?xml version="1.0" encoding="utf-8"?>
<SingleLogoutService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
"""


TEST_MANAGE_NAMEID_SERVICE = """<?xml version="1.0" encoding="utf-8"?>
<ManageNameIDService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
"""


TEST_SINGLE_SIGN_ON_SERVICE = """<?xml version="1.0" encoding="utf-8"?>
<SingleSignOnService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
"""


TEST_NAME_ID_MAPPING_SERVICE = """<?xml version="1.0" encoding="utf-8"?>
<NameIDMappingService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
"""


TEST_ASSERTION_ID_REQUEST_SERVICE = """<?xml version="1.0" encoding="utf-8"?>
<AssertionIDRequestService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
"""


TEST_INDEXED_ENDPOINT = """<?xml version="1.0" encoding="utf-8"?>
<IndexedEndpointType xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  index="1"
  isDefault="false"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
"""

TEST_ARTIFACT_RESOLUTION_SERVICE = """<?xml version="1.0" encoding="utf-8"?>
<ArtifactResolutionService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  index="1"
  isDefault="false"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
"""

TEST_ASSERTION_CONSUMER_SERVICE = """<?xml version="1.0" encoding="utf-8"?>
<AssertionConsumerService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  index="1"
  isDefault="false"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
"""

TEST_NAME_ID_FORMAT = """<?xml version="1.0" encoding="utf-8"?>
<NameIDFormat xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress
</NameIDFormat>
"""

TEST_ATTRIBUTE_PROFILE = """<?xml version="1.0" encoding="utf-8"?>
<AttributeProfile xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  urn:oasis:names:tc:SAML:2.0:profiles:attribute:basic
</AttributeProfile>
"""

TEST_ORGANIZATION_NAME = """<?xml version="1.0" encoding="utf-8"?>
<OrganizationName xmlns="urn:oasis:names:tc:SAML:2.0:metadata" 
    xml:lang="se">
  Catalogix
</OrganizationName>
"""

TEST_ORGANIZATION_DISPLAY_NAME = """<?xml version='1.0' encoding='UTF-8'?>
<ns0:OrganizationDisplayName xml:lang="se" xmlns:ns0="urn:oasis:names:tc:SAML:2.0:metadata">
Catalogix
</ns0:OrganizationDisplayName>
"""

TEST_ORGANIZATION_URL = """<?xml version="1.0" encoding="utf-8"?>
<OrganizationURL xmlns="urn:oasis:names:tc:SAML:2.0:metadata" 
    xml:lang="no">
  http://www.example.com/
</OrganizationURL>
"""

TEST_ORGANIZATION = """<?xml version="1.0" encoding="utf-8"?>
<Organization xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  <Extensions>
    <hoge xmlns="http://hoge.example.com/">hogehoge</hoge>
  </Extensions>
  <OrganizationName 
    xml:lang="se">
    Catalogix AB
  </OrganizationName>
  <OrganizationDisplayName xml:lang="no">
    Catalogix AS
  </OrganizationDisplayName>
  <OrganizationURL 
    xml:lang="en">
    http://www.example.com/
  </OrganizationURL>
</Organization>
"""

TEST_CONTACT_PERSON = """<?xml version="1.0" encoding="utf-8"?>
<ContactPerson xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  contactType="technical">
  <Extensions>
    <hoge xmlns="http://hoge.example.com/">hogehoge</hoge>
  </Extensions>
  <Company>SIOS Technology, Inc.</Company>
  <GivenName>Takashi</GivenName>
  <SurName>Matsuo</SurName>
  <EmailAddress>tmatsuo@example.com</EmailAddress>
  <EmailAddress>tmatsuo@shehas.net</EmailAddress>
  <TelephoneNumber>00-0000-0000</TelephoneNumber>
</ContactPerson>
"""

TEST_ADDITIONAL_METADATA_LOCATION = """<?xml version="1.0" encoding="utf-8"?>
<AdditionalMetadataLocation xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  namespace="http://www.example.com/namespace">
  http://www.example.com/AdditionalMetadataLocation
</AdditionalMetadataLocation>
"""

TEST_KEY_SIZE = """<?xml version="1.0" encoding="utf-8"?>
<KeySize xmlns="http://www.w3.org/2001/04/xmlenc#">128</KeySize>
"""

TEST_OAEP_PARAMS = """<?xml version="1.0" encoding="utf-8"?>
<OAEPparams xmlns="http://www.w3.org/2001/04/xmlenc#">
  9lWu3Q==
</OAEPparams>
"""

TEST_ENCRYPTION_METHOD = """<?xml version="1.0" encoding="utf-8"?>
<EncryptionMethod
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Algorithm="http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p">
  <OAEPparams xmlns="http://www.w3.org/2001/04/xmlenc#">
    9lWu3Q==
  </OAEPparams>
  <DigestMethod
    Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"
    xmlns="http://www.w3.org/2000/09/xmldsig#"/>
</EncryptionMethod>
"""

TEST_KEY_DESCRIPTOR = """<?xml version="1.0" encoding="utf-8"?>
<KeyDescriptor
  use="signing"
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  <KeyInfo xmlns="http://www.w3.org/2000/09/xmldsig#" Id="id">
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
  <EncryptionMethod
    xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
    Algorithm="http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p">
    <OAEPparams xmlns="http://www.w3.org/2001/04/xmlenc#">
      9lWu3Q==
    </OAEPparams>
    <DigestMethod
      Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"
      xmlns="http://www.w3.org/2000/09/xmldsig#"/>
  </EncryptionMethod>
</KeyDescriptor>
"""


TEST_ROLE_DESCRIPTOR = """<?xml version="1.0" encoding="utf-8"?>
<RoleDescriptor
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  ID="ID"
  validUntil="2008-09-14T01:05:02Z"
  cacheDuration="10:00:00:00"
  protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"
  errorURL="http://www.example.com/errorURL">
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
<Extensions>
  <foo xmlns="http://www.example.com/someNameSpace">bar</foo>
</Extensions>
<KeyDescriptor
  use="signing"
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  <KeyInfo xmlns="http://www.w3.org/2000/09/xmldsig#" Id="id">
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
  <EncryptionMethod
    xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
    Algorithm="http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p">
    <OAEPparams xmlns="http://www.w3.org/2001/04/xmlenc#">
      9lWu3Q==
    </OAEPparams>
    <DigestMethod
      Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"
      xmlns="http://www.w3.org/2000/09/xmldsig#"/>
  </EncryptionMethod>
</KeyDescriptor>
<Organization>
  <Extensions>
    <hoge xmlns="http://hoge.example.com/">hogehoge</hoge>
  </Extensions>
  <OrganizationName xml:lang="en">
    SIOS Technology, Inc.
  </OrganizationName>
  <OrganizationDisplayName xml:lang="en">
    SIOS
  </OrganizationDisplayName>
  <OrganizationURL xml:lang="ja">
    http://www.example.com/
  </OrganizationURL>
</Organization>
<ContactPerson contactType="technical">
  <Extensions>
    <hoge xmlns="http://hoge.example.com/">hogehoge</hoge>
  </Extensions>
  <Company>SIOS Technology, Inc.</Company>
  <GivenName>Takashi</GivenName>
  <SurName>Matsuo</SurName>
  <EmailAddress>tmatsuo@example.com</EmailAddress>
  <EmailAddress>tmatsuo@shehas.net</EmailAddress>
  <TelephoneNumber>00-0000-0000</TelephoneNumber>
</ContactPerson>
</RoleDescriptor>
"""


TEST_SSO_DESCRIPTOR = """<?xml version="1.0" encoding="utf-8"?>
<SSODescriptorType
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  ID="ID"
  validUntil="2008-09-14T01:05:02Z"
  cacheDuration="10:00:00:00"
  protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"
  errorURL="http://www.example.com/errorURL">
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
<Extensions>
  <foo xmlns="http://www.example.com/someNameSpace">bar</foo>
</Extensions>
<KeyDescriptor
  use="signing"
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  <KeyInfo xmlns="http://www.w3.org/2000/09/xmldsig#" Id="id">
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
  <EncryptionMethod
    xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
    Algorithm="http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p">
    <OAEPparams xmlns="http://www.w3.org/2001/04/xmlenc#">
      9lWu3Q==
    </OAEPparams>
    <DigestMethod
      Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"
      xmlns="http://www.w3.org/2000/09/xmldsig#"/>
  </EncryptionMethod>
</KeyDescriptor>
<Organization>
  <Extensions>
    <hoge xmlns="http://hoge.example.com/">hogehoge</hoge>
  </Extensions>
  <OrganizationName xml:lang="en">
    SIOS Technology, Inc.
  </OrganizationName>
  <OrganizationDisplayName xml:lang="en">
    SIOS
  </OrganizationDisplayName>
  <OrganizationURL xml:lang="ja">
    http://www.example.com/
  </OrganizationURL>
</Organization>
<ContactPerson contactType="technical">
  <Extensions>
    <hoge xmlns="http://hoge.example.com/">hogehoge</hoge>
  </Extensions>
  <Company>SIOS Technology, Inc.</Company>
  <GivenName>Takashi</GivenName>
  <SurName>Matsuo</SurName>
  <EmailAddress>tmatsuo@example.com</EmailAddress>
  <EmailAddress>tmatsuo@shehas.net</EmailAddress>
  <TelephoneNumber>00-0000-0000</TelephoneNumber>
</ContactPerson>
<ArtifactResolutionService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  index="1"
  isDefault="false"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
<SingleLogoutService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
<ManageNameIDService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
<NameIDFormat xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress
</NameIDFormat>
</SSODescriptorType>
"""


TEST_IDP_SSO_DESCRIPTOR = """<?xml version="1.0" encoding="utf-8"?>
<IDPSSODescriptor
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  ID="ID"
  validUntil="2008-09-14T01:05:02Z"
  cacheDuration="10:00:00:00"
  protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"
  errorURL="http://www.example.com/errorURL"
  WantAuthnRequestsSigned="true">
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
<Extensions>
  <foo xmlns="http://www.example.com/someNameSpace">bar</foo>
</Extensions>
<KeyDescriptor
  use="signing"
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  <KeyInfo xmlns="http://www.w3.org/2000/09/xmldsig#" Id="id">
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
  <EncryptionMethod
    xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
    Algorithm="http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p">
    <OAEPparams xmlns="http://www.w3.org/2001/04/xmlenc#">
      9lWu3Q==
    </OAEPparams>
    <DigestMethod
      Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"
      xmlns="http://www.w3.org/2000/09/xmldsig#"/>
  </EncryptionMethod>
</KeyDescriptor>
<Organization>
  <Extensions>
    <hoge xmlns="http://hoge.example.com/">hogehoge</hoge>
  </Extensions>
  <OrganizationName xml:lang="en">
    SIOS Technology, Inc.
  </OrganizationName>
  <OrganizationDisplayName xml:lang="en">
    SIOS
  </OrganizationDisplayName>
  <OrganizationURL xml:lang="ja">
    http://www.example.com/
  </OrganizationURL>
</Organization>
<ContactPerson contactType="technical">
  <Extensions>
    <hoge xmlns="http://hoge.example.com/">hogehoge</hoge>
  </Extensions>
  <Company>SIOS Technology, Inc.</Company>
  <GivenName>Takashi</GivenName>
  <SurName>Matsuo</SurName>
  <EmailAddress>tmatsuo@example.com</EmailAddress>
  <EmailAddress>tmatsuo@shehas.net</EmailAddress>
  <TelephoneNumber>00-0000-0000</TelephoneNumber>
</ContactPerson>
<ArtifactResolutionService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  index="1"
  isDefault="false"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
<SingleLogoutService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
<ManageNameIDService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
<NameIDFormat xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress
</NameIDFormat>
<SingleSignOnService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
<NameIDMappingService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
<AssertionIDRequestService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
<AttributeProfile xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  urn:oasis:names:tc:SAML:2.0:profiles:attribute:basic
</AttributeProfile>
<Attribute Name="testAttribute"
  NameFormat="urn:oasis:names:tc:SAML:2.0:attrnam-format:unspecified"
  FriendlyName="test attribute"
  xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
  <AttributeValue >value1 of test attribute</AttributeValue>
  <AttributeValue >value2 of test attribute</AttributeValue>
</Attribute>
</IDPSSODescriptor>
"""

TEST_REQUESTED_ATTRIBUTE = """<?xml version="1.0" encoding="utf-8"?>
<RequestedAttribute Name="testAttribute"
  NameFormat="urn:oasis:names:tc:SAML:2.0:attrnam-format:unspecified"
  FriendlyName="test attribute"
  isRequired="true"
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  <AttributeValue xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
    value1 of test attribute
  </AttributeValue>
  <AttributeValue xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
    value2 of test attribute
  </AttributeValue>
</RequestedAttribute>
"""

TEST_SERVICE_NAME = """<?xml version="1.0" encoding="utf-8"?>
<ServiceName xmlns="urn:oasis:names:tc:SAML:2.0:metadata" 
    xml:lang="en">
  Catalogix Whois
</ServiceName>
"""

TEST_SERVICE_DESCRIPTION = """<?xml version="1.0" encoding="utf-8"?>
<ServiceDescription xmlns="urn:oasis:names:tc:SAML:2.0:metadata" 
    xml:lang="en">
Catalogix Whois Service
</ServiceDescription>
"""

TEST_ATTRIBUTE_CONSUMING_SERVICE = """<?xml version="1.0" encoding="utf-8"?>
<AttributeConsumingService
  index="1"
  isDefault="true"
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
<ServiceName xml:lang="en">SIOS mail</ServiceName>
<ServiceDescription  xml:lang="en">SIOS mail service</ServiceDescription>
<RequestedAttribute Name="testAttribute"
  NameFormat="urn:oasis:names:tc:SAML:2.0:attrnam-format:unspecified"
  FriendlyName="test attribute"
  isRequired="true">
  <AttributeValue xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
    value1 of test attribute
  </AttributeValue>
  <AttributeValue xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
    value2 of test attribute
  </AttributeValue>
</RequestedAttribute>
</AttributeConsumingService>
"""


TEST_SP_SSO_DESCRIPTOR = """<?xml version="1.0" encoding="utf-8"?>
<SPSSODescriptor
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  ID="ID"
  validUntil="2008-09-14T01:05:02Z"
  cacheDuration="10:00:00:00"
  protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"
  errorURL="http://www.example.com/errorURL"
  AuthnRequestsSigned="true"
  WantAssertionsSigned="true">
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
<Extensions>
  <idpdisc:DiscoveryResponse 
    xmlns:idpdisc="urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol"
    index="1"
    Binding="urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol"
    Location="http://geneva.rutgers.edu/Shibboleth.sso/DS"/>
  <idpdisc:DiscoveryResponse 
    xmlns:idpdisc="urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol"
    index="2" 
    Binding="urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol"
    Location="https://geneva.rutgers.edu/Shibboleth.sso/DS"/>
</Extensions>
<KeyDescriptor
  use="signing"
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  <KeyInfo xmlns="http://www.w3.org/2000/09/xmldsig#" Id="id">
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
  <EncryptionMethod
    xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
    Algorithm="http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p">
    <OAEPparams xmlns="http://www.w3.org/2001/04/xmlenc#">
      9lWu3Q==
    </OAEPparams>
    <DigestMethod
      Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"
      xmlns="http://www.w3.org/2000/09/xmldsig#"/>
  </EncryptionMethod>
</KeyDescriptor>
<Organization>
  <Extensions>
    <hoge xmlns="http://hoge.example.com/">hogehoge</hoge>
  </Extensions>
  <OrganizationName xml:lang="en">
    SIOS Technology, Inc.
  </OrganizationName>
  <OrganizationDisplayName xml:lang="en">
    SIOS
  </OrganizationDisplayName>
  <OrganizationURL xml:lang="ja">
    http://www.example.com/
  </OrganizationURL>
</Organization>
<ContactPerson contactType="technical">
  <Extensions>
    <hoge xmlns="http://hoge.example.com/">hogehoge</hoge>
  </Extensions>
  <Company>SIOS Technology, Inc.</Company>
  <GivenName>Takashi</GivenName>
  <SurName>Matsuo</SurName>
  <EmailAddress>tmatsuo@example.com</EmailAddress>
  <EmailAddress>tmatsuo@shehas.net</EmailAddress>
  <TelephoneNumber>00-0000-0000</TelephoneNumber>
</ContactPerson>
<ArtifactResolutionService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  index="1"
  isDefault="false"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
<SingleLogoutService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
<ManageNameIDService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
<NameIDFormat xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
  urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress
</NameIDFormat>
<AssertionConsumerService xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  index="1"
  isDefault="false"
  Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
  Location="http://www.example.com/endpoint"
  ResponseLocation = "http://www.example.com/response"
/>
<AttributeConsumingService
  index="1"
  isDefault="true"
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
<ServiceName xml:lang="en">SIOS mail</ServiceName>
<ServiceDescription  xml:lang="en">SIOS mail service</ServiceDescription>
<RequestedAttribute Name="testAttribute"
  NameFormat="urn:oasis:names:tc:SAML:2.0:attrnam-format:unspecified"
  FriendlyName="test attribute"
  isRequired="true">
  <AttributeValue xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
    value1 of test attribute
  </AttributeValue>
  <AttributeValue xmlns="urn:oasis:names:tc:SAML:2.0:assertion">
    value2 of test attribute
  </AttributeValue>
</RequestedAttribute>
</AttributeConsumingService>
</SPSSODescriptor>
"""

TEST_ENTITY_DESCRIPTOR = """<?xml version="1.0" encoding="utf-8"?>
<EntityDescriptor
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  entityID="entityID"
  ID="ID"
  validUntil="2008-09-14T01:05:02Z"
  cacheDuration="10:00:00:00">
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
<Extensions>
  <foo xmlns="http://www.example.com/someNameSpace">bar</foo>
</Extensions>
<RoleDescriptor/>
<IDPSSODescriptor/>
<SPSSODescriptor/>
<Organization>
  <Extensions>
    <hoge xmlns="http://hoge.example.com/">hogehoge</hoge>
  </Extensions>
  <OrganizationName xml:lang="en">
    SIOS Technology, Inc.
  </OrganizationName>
  <OrganizationDisplayName xml:lang="en">
    SIOS
  </OrganizationDisplayName>
  <OrganizationURL xml:lang="ja">
    http://www.example.com/
  </OrganizationURL>
</Organization>
<ContactPerson contactType="technical">
  <Extensions>
    <hoge xmlns="http://hoge.example.com/">hogehoge</hoge>
  </Extensions>
  <Company>SIOS Technology, Inc.</Company>
  <GivenName>Takashi</GivenName>
  <SurName>Matsuo</SurName>
  <EmailAddress>tmatsuo@example.com</EmailAddress>
  <EmailAddress>tmatsuo@shehas.net</EmailAddress>
  <TelephoneNumber>00-0000-0000</TelephoneNumber>
</ContactPerson>
<AdditionalMetadataLocation xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  namespace="http://www.example.com/namespace">
  http://www.example.com/AdditionalMetadataLocation
</AdditionalMetadataLocation>
</EntityDescriptor>
"""

TEST_ENTITIES_DESCRIPTOR = """<?xml version="1.0" encoding="utf-8"?>
<EntitiesDescriptor
  xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
  Name="name"
  ID="ID"
  validUntil="2008-09-14T01:05:02Z"
  cacheDuration="10:00:00:00">
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
<Extensions>
  <foo xmlns="http://www.example.com/someNameSpace">bar</foo>
</Extensions>
<EntityDescriptor/>
<EntitiesDescriptor/>
</EntitiesDescriptor>
"""
