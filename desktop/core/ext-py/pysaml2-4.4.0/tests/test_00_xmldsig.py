#!/usr/bin/env python
#

"""Tests for xmldsig"""

__author__ = 'tmatsuo@example.com (Takashi MATSUO)'

import unittest
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import ds_data
import saml2.xmldsig as ds

class TestObject:

  def setup_class(self):
    self.object = ds.Object()

  def testAccessors(self):
    """Test for Object accessors"""
    self.object.id = "object_id"
    self.object.mime_type = "test/plain; charset=UTF-8"
    self.object.encoding = ds.ENCODING_BASE64
    new_object = ds.object_from_string(self.object.to_string())
    assert new_object.id == "object_id"
    assert new_object.mime_type == "test/plain; charset=UTF-8"
    assert new_object.encoding == ds.ENCODING_BASE64

  def testUsingTestData(self):
    """Test for object_from_string() using test data"""
    new_object = ds.object_from_string(ds_data.TEST_OBJECT)
    assert new_object.id == "object_id"
    assert new_object.encoding == ds.ENCODING_BASE64
    assert new_object.text.strip() == \
                 "V2VkIEp1biAgNCAxMjoxMTowMyBFRFQgMjAwMwo"
    

class TestMgmtData:

  def setup_class(self):
    self.mgmt_data = ds.MgmtData()

  def testAccessors(self):
    """Test for MgmtData accessors"""
    self.mgmt_data.text = "mgmt data"
    new_mgmt_data = ds.mgmt_data_from_string(self.mgmt_data.to_string())
    assert new_mgmt_data.text.strip() == "mgmt data"

  def testUsingTestData(self):
    """Test for mgmt_data_from_string() using test data"""
    new_mgmt_data = ds.mgmt_data_from_string(ds_data.TEST_MGMT_DATA)
    assert new_mgmt_data.text.strip() == "mgmt data"


class TestSPKISexp:

  def setup_class(self):
    self.spki_sexp = ds.SPKISexp()

  def testAccessors(self):
    """Test for SPKISexp accessors"""
    self.spki_sexp.text = "spki sexp"
    new_spki_sexp = ds.spki_sexp_from_string(self.spki_sexp.to_string())
    assert new_spki_sexp.text.strip() == "spki sexp"

  def testUsingTestData(self):
    """Test for spki_sexp_from_string() using test data"""
    new_spki_sexp = ds.spki_sexp_from_string(ds_data.TEST_SPKI_SEXP)
    assert new_spki_sexp.text.strip() == "spki sexp"


class TestSPKIData:

  def setup_class(self):
    self.spki_data = ds.SPKIData()

  def testAccessors(self):
    """Test for SPKIData accessors"""
    self.spki_data.spki_sexp.append(
      ds.spki_sexp_from_string(ds_data.TEST_SPKI_SEXP))
    new_spki_data = ds.spki_data_from_string(self.spki_data.to_string())
    assert new_spki_data.spki_sexp[0].text.strip() == "spki sexp"

  def testUsingTestData(self):
    """Test for spki_data_from_string() using test data"""
    new_spki_data = ds.spki_data_from_string(ds_data.TEST_SPKI_DATA)
    print(new_spki_data)
    assert new_spki_data.spki_sexp[0].text.strip() == "spki sexp"
    assert new_spki_data.spki_sexp[1].text.strip() == "spki sexp2"


class TestPGPData:

  def setup_class(self):
    self.pgp_data = ds.PGPData()

  def testAccessors(self):
    """Test for PGPData accessors"""
    self.pgp_data.pgp_key_id = ds.PGPKeyID(text="pgp key id")
    self.pgp_data.pgp_key_packet = ds.PGPKeyPacket(text="pgp key packet")
    new_pgp_data = ds.pgp_data_from_string(self.pgp_data.to_string())
    assert isinstance(new_pgp_data.pgp_key_id, ds.PGPKeyID)
    assert isinstance(new_pgp_data.pgp_key_packet, ds.PGPKeyPacket)
    assert new_pgp_data.pgp_key_id.text.strip() == "pgp key id"
    assert new_pgp_data.pgp_key_packet.text.strip() == "pgp key packet"

  def testUsingTestData(self):
    """Test for pgp_data_from_string() using test data"""
    new_pgp_data = ds.pgp_data_from_string(ds_data.TEST_PGP_DATA)
    assert isinstance(new_pgp_data.pgp_key_id, ds.PGPKeyID)
    assert isinstance(new_pgp_data.pgp_key_packet, ds.PGPKeyPacket)
    assert new_pgp_data.pgp_key_id.text.strip() == "pgp key id"
    assert new_pgp_data.pgp_key_packet.text.strip() == "pgp key packet"


class TestX509IssuerSerial:

  def setup_class(self):
    self.x509_issuer_serial = ds.X509IssuerSerialType_()

  def testAccessors(self):
    """Test for X509SerialNumber accessors"""
    self.x509_issuer_serial.x509_issuer_name = ds.X509IssuerName(
      text="issuer name")
    self.x509_issuer_serial.x509_serial_number = ds.X509SerialNumber(text="1")
    new_x509_issuer_serial = ds.x509_issuer_serial_type__from_string(
       self.x509_issuer_serial.to_string())
    assert new_x509_issuer_serial.x509_issuer_name.text.strip() == \
                 "issuer name"
    assert new_x509_issuer_serial.x509_serial_number.text.strip() == "1"

  def testUsingTestData(self):
    """Test for x509_issuer_serial_from_string() using test data"""
    new_x509_issuer_serial = ds.x509_issuer_serial_from_string(
      ds_data.TEST_X509_ISSUER_SERIAL)
    assert new_x509_issuer_serial.x509_issuer_name.text.strip() == \
                 "issuer name"
    assert new_x509_issuer_serial.x509_serial_number.text.strip() == "1"


class TestX509Data:

  def setup_class(self):
    self.x509_data = ds.X509Data()

  def testAccessors(self):
    """Test for X509Data accessors"""
    st = ds.x509_issuer_serial_from_string(ds_data.TEST_X509_ISSUER_SERIAL)
    print(st)
    self.x509_data.x509_issuer_serial= st
    self.x509_data.x509_ski = ds.X509SKI(text="x509 ski")
    self.x509_data.x509_subject_name = ds.X509SubjectName(
                                                text="x509 subject name")
    self.x509_data.x509_certificate = ds.X509Certificate(
                                                text="x509 certificate")
    self.x509_data.x509_crl = ds.X509CRL(text="x509 crl")
    
    new_x509_data = ds.x509_data_from_string(self.x509_data.to_string())
    print(new_x509_data.keyswv())
    print(new_x509_data.__dict__.keys())
    assert new_x509_data.x509_issuer_serial
    assert isinstance(new_x509_data.x509_issuer_serial, ds.X509IssuerSerial)
    assert new_x509_data.x509_ski.text.strip() == "x509 ski"
    assert isinstance(new_x509_data.x509_ski, ds.X509SKI)
    assert new_x509_data.x509_subject_name.text.strip() == \
                 "x509 subject name"
    assert isinstance(new_x509_data.x509_subject_name, ds.X509SubjectName)
    assert new_x509_data.x509_certificate.text.strip() == \
                 "x509 certificate"
    assert isinstance(new_x509_data.x509_certificate, ds.X509Certificate)
    assert new_x509_data.x509_crl.text.strip() == "x509 crl"
    assert isinstance(new_x509_data.x509_crl,ds.X509CRL)

  def testUsingTestData(self):
    """Test for x509_data_from_string() using test data"""
    new_x509_data = ds.x509_data_from_string(ds_data.TEST_X509_DATA)
    assert isinstance(new_x509_data.x509_issuer_serial, ds.X509IssuerSerial)
    assert new_x509_data.x509_ski.text.strip() == "x509 ski"
    assert isinstance(new_x509_data.x509_ski, ds.X509SKI)
    assert new_x509_data.x509_subject_name.text.strip() == \
                 "x509 subject name"
    assert isinstance(new_x509_data.x509_subject_name, ds.X509SubjectName)
    assert new_x509_data.x509_certificate.text.strip() == \
                 "x509 certificate"
    assert isinstance(new_x509_data.x509_certificate, ds.X509Certificate)
    assert new_x509_data.x509_crl.text.strip() == "x509 crl"
    assert isinstance(new_x509_data.x509_crl,ds.X509CRL)


class TestTransform:

  def setup_class(self):
    self.transform = ds.Transform()

  def testAccessors(self):
    """Test for Transform accessors"""
    self.transform.x_path.append(ds.TransformType_XPath(text="xpath"))
    self.transform.algorithm = ds.TRANSFORM_ENVELOPED
    new_transform = ds.transform_from_string(self.transform.to_string())
    assert isinstance(new_transform.x_path[0], ds.TransformType_XPath)
    assert new_transform.x_path[0].text.strip() == "xpath"
    assert new_transform.algorithm == ds.TRANSFORM_ENVELOPED

  def testUsingTestData(self):
    """Test for transform_from_string() using test data"""
    new_transform = ds.transform_from_string(ds_data.TEST_TRANSFORM)
    assert isinstance(new_transform.x_path[0], ds.TransformType_XPath)
    assert new_transform.x_path[0].text.strip() == "xpath"
    assert new_transform.algorithm == ds.TRANSFORM_ENVELOPED


class TestTransforms:

  def setup_class(self):
    self.transforms = ds.Transforms()

  def testAccessors(self):
    """Test for Transforms accessors"""
    self.transforms.transform.append(
      ds.transform_from_string(ds_data.TEST_TRANSFORM))
    self.transforms.transform.append(
      ds.transform_from_string(ds_data.TEST_TRANSFORM))
    new_transforms = ds.transforms_from_string(self.transforms.to_string())
    assert isinstance(new_transforms.transform[0], ds.Transform)
    assert isinstance(new_transforms.transform[1], ds.Transform)
    assert new_transforms.transform[0].algorithm == \
                 ds.TRANSFORM_ENVELOPED
    assert new_transforms.transform[1].algorithm == \
                 ds.TRANSFORM_ENVELOPED
    assert new_transforms.transform[0].x_path[0].text.strip() == "xpath"
    assert new_transforms.transform[1].x_path[0].text.strip() == "xpath"
    
  def testUsingTestData(self):
    """Test for transform_from_string() using test data"""
    new_transforms = ds.transforms_from_string(ds_data.TEST_TRANSFORMS)
    assert isinstance(new_transforms.transform[0], ds.Transform)
    assert isinstance(new_transforms.transform[1], ds.Transform)
    assert new_transforms.transform[0].algorithm == \
                 ds.TRANSFORM_ENVELOPED
    assert new_transforms.transform[1].algorithm == \
                 ds.TRANSFORM_ENVELOPED
    assert new_transforms.transform[0].x_path[0].text.strip() == "xpath"
    assert new_transforms.transform[1].x_path[0].text.strip() == "xpath"


class TestRetrievalMethod:

  def setup_class(self):
    self.retrieval_method = ds.RetrievalMethod()

  def testAccessors(self):
    """Test for RetrievalMethod accessors"""
    self.retrieval_method.uri = "http://www.example.com/URI"
    self.retrieval_method.type = "http://www.example.com/Type"
    self.retrieval_method.transforms = ds.transforms_from_string(
      ds_data.TEST_TRANSFORMS)
    new_retrieval_method = ds.retrieval_method_from_string(
      self.retrieval_method.to_string())
    assert new_retrieval_method.uri == "http://www.example.com/URI"
    assert new_retrieval_method.type == "http://www.example.com/Type"
    assert isinstance(new_retrieval_method.transforms, ds.Transforms)
    
  def testUsingTestData(self):
    """Test for retrieval_method_from_string() using test data"""
    new_retrieval_method = ds.retrieval_method_from_string(
      ds_data.TEST_RETRIEVAL_METHOD)
    assert new_retrieval_method.uri == "http://www.example.com/URI"
    assert new_retrieval_method.type == "http://www.example.com/Type"
    assert isinstance(new_retrieval_method.transforms, ds.Transforms)


class TestRSAKeyValue:

  def setup_class(self):
    self.rsa_key_value = ds.RSAKeyValue()

  def testAccessors(self):
    """Test for RSAKeyValue accessors"""
    self.rsa_key_value.modulus = ds.Modulus(text="modulus")
    self.rsa_key_value.exponent = ds.Exponent(text="exponent")
    new_rsa_key_value = ds.rsa_key_value_from_string(self.rsa_key_value.to_string())
    assert isinstance(new_rsa_key_value.modulus, ds.Modulus)
    assert isinstance(new_rsa_key_value.exponent, ds.Exponent)
    assert new_rsa_key_value.modulus.text.strip() == "modulus"
    assert new_rsa_key_value.exponent.text.strip() == "exponent"
    
  def testUsingTestData(self):
    """Test for rsa_key_value_from_string() using test data"""
    new_rsa_key_value = ds.rsa_key_value_from_string(
      ds_data.TEST_RSA_KEY_VALUE)
    assert isinstance(new_rsa_key_value.modulus, ds.Modulus)
    assert isinstance(new_rsa_key_value.exponent, ds.Exponent)
    assert new_rsa_key_value.modulus.text.strip() == "modulus"
    assert new_rsa_key_value.exponent.text.strip() == "exponent"


class TestDSAKeyValue:

  def setup_class(self):
    self.dsa_key_value = ds.DSAKeyValue()

  def testAccessors(self):
    """Test for DSAKeyValue accessors"""
    self.dsa_key_value.p = ds.P(text="p")
    self.dsa_key_value.q = ds.Q(text="q")
    self.dsa_key_value.g = ds.G(text="g")
    self.dsa_key_value.y = ds.Y(text="y")
    self.dsa_key_value.j = ds.J(text="j")
    self.dsa_key_value.seed = ds.Seed(text="seed")
    self.dsa_key_value.pgen_counter = ds.PgenCounter(text="pgen counter")
    new_dsa_key_value = ds.dsa_key_value_from_string(self.dsa_key_value.to_string())
    assert isinstance(new_dsa_key_value.p, ds.P)
    assert isinstance(new_dsa_key_value.q, ds.Q)
    assert isinstance(new_dsa_key_value.g, ds.G)
    assert isinstance(new_dsa_key_value.y, ds.Y)
    assert isinstance(new_dsa_key_value.j, ds.J)
    assert isinstance(new_dsa_key_value.seed, ds.Seed)
    assert isinstance(new_dsa_key_value.pgen_counter, ds.PgenCounter)
    assert new_dsa_key_value.p.text.strip() == "p"
    assert new_dsa_key_value.q.text.strip() == "q"
    assert new_dsa_key_value.g.text.strip() == "g"
    assert new_dsa_key_value.y.text.strip() == "y"
    assert new_dsa_key_value.j.text.strip() == "j"
    assert new_dsa_key_value.seed.text.strip() == "seed"
    assert new_dsa_key_value.pgen_counter.text.strip() == "pgen counter"
    
  def testUsingTestData(self):
    """Test for dsa_key_value_from_string() using test data"""
    new_dsa_key_value = ds.dsa_key_value_from_string(
      ds_data.TEST_DSA_KEY_VALUE)
    assert isinstance(new_dsa_key_value.p, ds.P)
    assert isinstance(new_dsa_key_value.q, ds.Q)
    assert isinstance(new_dsa_key_value.g, ds.G)
    assert isinstance(new_dsa_key_value.y, ds.Y)
    assert isinstance(new_dsa_key_value.j, ds.J)
    assert isinstance(new_dsa_key_value.seed, ds.Seed)
    assert isinstance(new_dsa_key_value.pgen_counter, ds.PgenCounter)
    assert new_dsa_key_value.p.text.strip() == "p"
    assert new_dsa_key_value.q.text.strip() == "q"
    assert new_dsa_key_value.g.text.strip() == "g"
    assert new_dsa_key_value.y.text.strip() == "y"
    assert new_dsa_key_value.j.text.strip() == "j"
    assert new_dsa_key_value.seed.text.strip() == "seed"
    assert new_dsa_key_value.pgen_counter.text.strip() == "pgen counter"


class TestKeyValue:

  def setup_class(self):
    self.key_value = ds.KeyValue()

  def testAccessors(self):
    """Test for KeyValue accessors"""
    self.key_value.dsa_key_value = ds.dsa_key_value_from_string(
      ds_data.TEST_DSA_KEY_VALUE)
    new_key_value = ds.key_value_from_string(self.key_value.to_string())
    assert isinstance(new_key_value.dsa_key_value, ds.DSAKeyValue)
    self.key_value.dsa_key_value = None
    self.key_value.rsa_key_value = ds.rsa_key_value_from_string(
      ds_data.TEST_RSA_KEY_VALUE)
    new_key_value = ds.key_value_from_string(self.key_value.to_string())
    assert isinstance(new_key_value.rsa_key_value, ds.RSAKeyValue)
    
  def testUsingTestData(self):
    """Test for key_value_from_string() using test data"""
    new_key_value = ds.key_value_from_string(ds_data.TEST_KEY_VALUE1)
    assert isinstance(new_key_value.dsa_key_value, ds.DSAKeyValue)
    self.key_value.dsa_key_value = None
    self.key_value.rsa_key_value = ds.rsa_key_value_from_string(
      ds_data.TEST_RSA_KEY_VALUE)
    new_key_value = ds.key_value_from_string(ds_data.TEST_KEY_VALUE2)
    assert isinstance(new_key_value.rsa_key_value, ds.RSAKeyValue)


class TestKeyName:

  def setup_class(self):
    self.key_name = ds.KeyName()

  def testAccessors(self):
    """Test for KeyName accessors"""
    self.key_name.text = "key name"
    new_key_name = ds.key_name_from_string(self.key_name.to_string())
    assert new_key_name.text.strip() == "key name"
    
  def testUsingTestData(self):
    """Test for key_name_from_string() using test data"""
    new_key_name = ds.key_name_from_string(ds_data.TEST_KEY_NAME)
    assert new_key_name.text.strip() == "key name"


class TestKeyInfo:
  def setup_class(self):
    self.key_info = ds.KeyInfo()

  def testAccessors(self):
    """Test for KeyInfo accessors"""
    self.key_info.key_name.append(
      ds.key_name_from_string(ds_data.TEST_KEY_NAME))
    self.key_info.key_value.append(
      ds.key_value_from_string(ds_data.TEST_KEY_VALUE1))
    self.key_info.retrieval_method.append(
      ds.retrieval_method_from_string(ds_data.TEST_RETRIEVAL_METHOD))
    self.key_info.x509_data.append(
      ds.x509_data_from_string(ds_data.TEST_X509_DATA))
    self.key_info.pgp_data.append(
      ds.pgp_data_from_string(ds_data.TEST_PGP_DATA))
    self.key_info.spki_data.append(
      ds.spki_data_from_string(ds_data.TEST_SPKI_DATA))
    self.key_info.mgmt_data.append(
      ds.mgmt_data_from_string(ds_data.TEST_MGMT_DATA))
    self.key_info.id = "id"
    new_key_info = ds.key_info_from_string(self.key_info.to_string())

    assert isinstance(new_key_info.key_name[0], ds.KeyName)
    assert isinstance(new_key_info.key_value[0], ds.KeyValue)
    assert isinstance(new_key_info.retrieval_method[0],
                            ds.RetrievalMethod)
    assert isinstance(new_key_info.x509_data[0], ds.X509Data)
    assert isinstance(new_key_info.pgp_data[0], ds.PGPData)
    assert isinstance(new_key_info.spki_data[0], ds.SPKIData)
    assert isinstance(new_key_info.mgmt_data[0], ds.MgmtData)
    assert new_key_info.id == "id"
    
  def testUsingTestData(self):
    """Test for key_info_from_string() using test data"""
    new_key_info = ds.key_info_from_string(ds_data.TEST_KEY_INFO)
    assert isinstance(new_key_info.key_name[0], ds.KeyName)
    assert isinstance(new_key_info.key_value[0], ds.KeyValue)
    assert isinstance(new_key_info.retrieval_method[0],
                            ds.RetrievalMethod)
    assert isinstance(new_key_info.x509_data[0], ds.X509Data)
    assert isinstance(new_key_info.pgp_data[0], ds.PGPData)
    assert isinstance(new_key_info.spki_data[0], ds.SPKIData)
    assert isinstance(new_key_info.mgmt_data[0], ds.MgmtData)
    assert new_key_info.id == "id"
  

class TestDigestValue:

  def setup_class(self):
    self.digest_value = ds.DigestValue()

  def testAccessors(self):
    """Test for DigestValue accessors"""
    self.digest_value.text = "digest value"
    new_digest_value = ds.digest_value_from_string(self.digest_value.to_string())
    assert new_digest_value.text.strip() == "digest value"
    
  def testUsingTestData(self):
    """Test for digest_value_from_string() using test data"""
    new_digest_value = ds.digest_value_from_string(ds_data.TEST_DIGEST_VALUE)
    assert new_digest_value.text.strip() == "digest value"


class TestDigestMethod:

  def setup_class(self):
    self.digest_method = ds.DigestMethod()

  def testAccessors(self):
    """Test for DigestMethod accessors"""
    self.digest_method.algorithm = ds.DIGEST_SHA1
    new_digest_method = ds.digest_method_from_string(
      self.digest_method.to_string())
    assert new_digest_method.algorithm == ds.DIGEST_SHA1
    
  def testUsingTestData(self):
    """Test for digest_method_from_string() using test data"""
    new_digest_method = ds.digest_method_from_string(
      ds_data.TEST_DIGEST_METHOD)
    assert new_digest_method.algorithm == ds.DIGEST_SHA1


class TestReference:

  def setup_class(self):
    self.reference = ds.Reference()

  def testAccessors(self):
    """Test for Reference accessors"""
    self.reference.transforms = ds.transforms_from_string(
      ds_data.TEST_TRANSFORMS)
    self.reference.digest_method = ds.digest_method_from_string(
      ds_data.TEST_DIGEST_METHOD)
    self.reference.digest_value = ds.digest_value_from_string(
      ds_data.TEST_DIGEST_VALUE)
    self.reference.id = "id"
    self.reference.uri = "http://www.example.com/URI"
    self.reference.type = "http://www.example.com/Type"
    new_reference = ds.reference_from_string(self.reference.to_string())
    assert isinstance(new_reference.transforms, ds.Transforms)
    assert isinstance(new_reference.digest_method, ds.DigestMethod)
    assert isinstance(new_reference.digest_value, ds.DigestValue)
    assert new_reference.id == "id"
    assert new_reference.uri == "http://www.example.com/URI"
    assert new_reference.type == "http://www.example.com/Type"
    
  def testUsingTestData(self):
    """Test for reference_from_string() using test data"""
    new_reference = ds.reference_from_string(ds_data.TEST_REFERENCE)
    assert isinstance(new_reference.transforms, ds.Transforms)
    assert isinstance(new_reference.digest_method, ds.DigestMethod)
    assert isinstance(new_reference.digest_value, ds.DigestValue)
    assert new_reference.id == "id"
    assert new_reference.uri == "http://www.example.com/URI"
    assert new_reference.type == "http://www.example.com/Type"


class TestSignatureMethod:

  def setup_class(self):
    self.signature_method = ds.SignatureMethod()

  def testAccessors(self):
    """Test for SignatureMethod accessors"""
    self.signature_method.algorithm = ds.SIG_RSA_SHA1
    self.signature_method.hmac_output_length = ds.HMACOutputLength(text="8")
    new_signature_method = ds.signature_method_from_string(
      self.signature_method.to_string())
    assert isinstance(new_signature_method.hmac_output_length,
                      ds.HMACOutputLength)
    assert new_signature_method.hmac_output_length.text.strip() == "8"
    assert new_signature_method.algorithm == ds.SIG_RSA_SHA1
    
  def testUsingTestData(self):
    """Test for signature_method_from_string() using test data"""
    new_signature_method = ds.signature_method_from_string(
                        ds_data.TEST_SIGNATURE_METHOD)
    assert isinstance(new_signature_method.hmac_output_length,
                      ds.HMACOutputLength)
    assert new_signature_method.hmac_output_length.text.strip() == "8"
    assert new_signature_method.algorithm == ds.SIG_RSA_SHA1


class TestCanonicalizationMethod:

  def setup_class(self):
    self.canonicalization_method = ds.CanonicalizationMethod()

  def testAccessors(self):
    """Test for CanonicalizationMethod accessors"""
    self.canonicalization_method.algorithm = ds.C14N_WITH_C
    new_canonicalization_method = ds.canonicalization_method_from_string(
      self.canonicalization_method.to_string())
    assert new_canonicalization_method.algorithm == ds.C14N_WITH_C
    
  def testUsingTestData(self):
    """Test for canonicalization_method_from_string() using test data"""
    new_canonicalization_method = ds.canonicalization_method_from_string(
      ds_data.TEST_CANONICALIZATION_METHOD)
    assert new_canonicalization_method.algorithm == ds.C14N_WITH_C


class TestSignedInfo:

  def setup_class(self):
    self.si = ds.SignedInfo()

  def testAccessors(self):
    """Test for SignedInfo accessors"""
    self.si.id = "id"
    self.si.canonicalization_method = ds.canonicalization_method_from_string(
      ds_data.TEST_CANONICALIZATION_METHOD)
    self.si.signature_method = ds.signature_method_from_string(
      ds_data.TEST_SIGNATURE_METHOD)
    self.si.reference.append(ds.reference_from_string(
      ds_data.TEST_REFERENCE))
    new_si = ds.signed_info_from_string(self.si.to_string())
    assert new_si.id == "id"
    assert isinstance(new_si.canonicalization_method,
                            ds.CanonicalizationMethod)
    assert isinstance(new_si.signature_method, ds.SignatureMethod)
    assert isinstance(new_si.reference[0], ds.Reference)
    
  def testUsingTestData(self):
    """Test for signed_info_from_string() using test data"""
    new_si = ds.signed_info_from_string(ds_data.TEST_SIGNED_INFO)
    assert new_si.id == "id"
    assert isinstance(new_si.canonicalization_method,
                            ds.CanonicalizationMethod)
    assert isinstance(new_si.signature_method, ds.SignatureMethod)
    assert isinstance(new_si.reference[0], ds.Reference)

class TestSignatureValue:

  def setup_class(self):
    self.signature_value = ds.SignatureValue()

  def testAccessors(self):
    """Test for SignatureValue accessors"""
    self.signature_value.id = "id"
    self.signature_value.text = "signature value"
    new_signature_value = ds.signature_value_from_string(
      self.signature_value.to_string())
    assert new_signature_value.id == "id"
    assert new_signature_value.text.strip() == "signature value"
    
  def testUsingTestData(self):
    """Test for signature_value_from_string() using test data"""
    new_signature_value = ds.signature_value_from_string(
      ds_data.TEST_SIGNATURE_VALUE)
    assert new_signature_value.id == "id"
    assert new_signature_value.text.strip() == "signature value"


class TestSignature:

  def setup_class(self):
    self.signature = ds.Signature()

  def testAccessors(self):
    """Test for Signature accessors"""
    self.signature.id = "id"
    self.signature.signed_info = ds.signed_info_from_string(
      ds_data.TEST_SIGNED_INFO)
    self.signature.signature_value = ds.signature_value_from_string(
      ds_data.TEST_SIGNATURE_VALUE)
    self.signature.key_info = ds.key_info_from_string(ds_data.TEST_KEY_INFO)
    self.signature.object.append(ds.object_from_string(ds_data.TEST_OBJECT))

    new_signature = ds.signature_from_string(self.signature.to_string())
    assert new_signature.id == "id"
    assert isinstance(new_signature.signed_info, ds.SignedInfo)
    assert isinstance(new_signature.signature_value, ds.SignatureValue)
    assert isinstance(new_signature.key_info, ds.KeyInfo)
    assert isinstance(new_signature.object[0], ds.Object)
    
  def testUsingTestData(self):
    """Test for signature_value_from_string() using test data"""
    new_signature = ds.signature_from_string(ds_data.TEST_SIGNATURE)
    assert new_signature.id == "id"
    assert isinstance(new_signature.signed_info, ds.SignedInfo)
    assert isinstance(new_signature.signature_value, ds.SignatureValue)
    assert isinstance(new_signature.key_info, ds.KeyInfo)
    assert isinstance(new_signature.object[0], ds.Object)


if __name__ == '__main__':
  unittest.main()
