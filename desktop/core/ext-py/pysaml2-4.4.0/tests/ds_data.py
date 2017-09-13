#!/usr/bin/env python
#

"""Test data for ds"""

__author__ = 'tmatsuo@example.com (Takashi MATSUO)'

TEST_OBJECT = """<?xml version="1.0" encoding="utf-8"?>
<Object Id="object_id" Encoding="http://www.w3.org/2000/09/xmldsig#base64"
  xmlns="http://www.w3.org/2000/09/xmldsig#">
  V2VkIEp1biAgNCAxMjoxMTowMyBFRFQgMjAwMwo
</Object>
"""

TEST_MGMT_DATA = """<?xml version="1.0" encoding="utf-8"?>
<MgmtData xmlns="http://www.w3.org/2000/09/xmldsig#">
  mgmt data
</MgmtData>
"""

TEST_SPKI_SEXP = """<?xml version="1.0" encoding="utf-8"?>
<SPKISexp xmlns="http://www.w3.org/2000/09/xmldsig#">
  spki sexp
</SPKISexp>
"""

TEST_SPKI_DATA = """<?xml version="1.0" encoding="utf-8"?>
<SPKIData xmlns="http://www.w3.org/2000/09/xmldsig#">
  <SPKISexp>spki sexp</SPKISexp>
  <SPKISexp>spki sexp2</SPKISexp>
</SPKIData>  
"""

TEST_PGP_DATA = """<?xml version="1.0" encoding="utf-8"?>
<PGPData xmlns="http://www.w3.org/2000/09/xmldsig#">
  <PGPKeyID>pgp key id</PGPKeyID>
  <PGPKeyPacket>pgp key packet</PGPKeyPacket>
</PGPData>
"""

TEST_X509_ISSUER_SERIAL = """<?xml version="1.0" encoding="utf-8"?>
<X509IssuerSerial xmlns="http://www.w3.org/2000/09/xmldsig#">
  <X509IssuerName>issuer name</X509IssuerName>
  <X509SerialNumber>1</X509SerialNumber>
</X509IssuerSerial>
"""

TEST_X509_DATA = """<?xml version="1.0" encoding="utf-8"?>
<X509Data xmlns="http://www.w3.org/2000/09/xmldsig#">
  <X509IssuerSerial>
    <X509IssuerName>issuer name</X509IssuerName>
    <X509IssuerNumber>1</X509IssuerNumber>
  </X509IssuerSerial>
  <X509SKI>x509 ski</X509SKI>
  <X509SubjectName>x509 subject name</X509SubjectName>
  <X509Certificate>x509 certificate</X509Certificate>
  <X509CRL>x509 crl</X509CRL>
</X509Data>
"""

TEST_TRANSFORM = """<?xml version="1.0" encoding="utf-8"?>
<Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"
  xmlns="http://www.w3.org/2000/09/xmldsig#">
  <XPath>xpath</XPath>
</Transform>
"""

TEST_TRANSFORMS = """<?xml version="1.0" encoding="utf-8"?>
<Transforms xmlns="http://www.w3.org/2000/09/xmldsig#">
  <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature">
    <XPath>xpath</XPath>
  </Transform>
  <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature">
    <XPath>xpath</XPath>
  </Transform>
</Transforms>
"""

TEST_RETRIEVAL_METHOD = """<?xml version="1.0" encoding="utf-8"?>
<RetrievalMethod xmlns="http://www.w3.org/2000/09/xmldsig#"
  URI="http://www.example.com/URI"
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
"""

TEST_RSA_KEY_VALUE = """<?xml version="1.0" encoding="utf-8"?>
<RSAKeyValue xmlns="http://www.w3.org/2000/09/xmldsig#">
  <Modulus>modulus</Modulus>
  <Exponent>exponent</Exponent>
</RSAKeyValue>
"""

TEST_DSA_KEY_VALUE = """<?xml version="1.0" encoding="utf-8"?>
<DSAKeyValue xmlns="http://www.w3.org/2000/09/xmldsig#">
  <P>p</P>
  <Q>q</Q>
  <G>g</G>
  <Y>y</Y>
  <J>j</J>
  <Seed>seed</Seed>
  <PgenCounter>pgen counter</PgenCounter>
</DSAKeyValue>
"""

TEST_KEY_VALUE1 = """<?xml version="1.0" encoding="utf-8"?>
<KeyValue xmlns="http://www.w3.org/2000/09/xmldsig#">
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
"""

TEST_KEY_VALUE2 = """<?xml version="1.0" encoding="utf-8"?>
<KeyValue xmlns="http://www.w3.org/2000/09/xmldsig#">
  <RSAKeyValue xmlns="http://www.w3.org/2000/09/xmldsig#">
    <Modulus>modulus</Modulus>
    <Exponent>exponent</Exponent>
  </RSAKeyValue>
</KeyValue>
"""

TEST_KEY_NAME = """<?xml version="1.0" encoding="utf-8"?>
<KeyName xmlns="http://www.w3.org/2000/09/xmldsig#">
  key name
</KeyName>
"""

TEST_KEY_INFO = """<?xml version="1.0" encoding="utf-8"?>
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
"""

TEST_DIGEST_VALUE = """<?xml version="1.0" encoding="utf-8"?>
<DigestValue xmlns="http://www.w3.org/2000/09/xmldsig#">
  digest value
</DigestValue>
"""

TEST_DIGEST_METHOD = """<?xml version="1.0" encoding="utf-8"?>
<DigestMethod xmlns="http://www.w3.org/2000/09/xmldsig#"
  Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
"""

TEST_REFERENCE = """<?xml version="1.0" encoding="utf-8"?>
<Reference xmlns="http://www.w3.org/2000/09/xmldsig#" Id="id"
  URI="http://www.example.com/URI"
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
"""

TEST_SIGNATURE_METHOD = """<?xml version="1.0" encoding="utf-8"?>
<SignatureMethod xmlns="http://www.w3.org/2000/09/xmldsig#"
  Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1">
  <HMACOutputLength>8</HMACOutputLength>
</SignatureMethod>
"""

TEST_CANONICALIZATION_METHOD = """<?xml version="1.0" encoding="utf-8"?>
<CanonicalizationMethod xmlns="http://www.w3.org/2000/09/xmldsig#"
  Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315#WithComments">
</CanonicalizationMethod>
"""

TEST_SIGNED_INFO = """<?xml version="1.0" encoding="utf-8"?>
<SignedInfo xmlns="http://www.w3.org/2000/09/xmldsig#" Id="id">
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
"""

TEST_SIGNATURE_VALUE = """<?xml version="1.0" encoding="utf-8"?>
<SignatureValue xmlns="http://www.w3.org/2000/09/xmldsig#" Id="id">
  signature value
</SignatureValue>
"""

TEST_SIGNATURE = """<?xml version="1.0" encoding="utf-8"?>
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
"""
