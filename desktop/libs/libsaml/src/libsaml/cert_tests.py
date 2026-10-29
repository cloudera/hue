#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Tests for the certificate handling of the vendored pysaml2 (saml2.cert).

pyOpenSSL 26 removed X509Req, load_certificate_request and verify(), which the SAML signing code uses to create a
temporary signing certificate. These tests run that flow against the installed pyOpenSSL and cryptography.
"""

import pytest
from cryptography import x509
from cryptography.x509.oid import NameOID
from saml2.cert import CertificateError, OpenSSLWrapper, WrongInput

CA_INFO = {
  "cn": "ca.example.com",
  "country_code": "se",
  "state": "AC",
  "city": "Dorotea",
  "organization": "Company",
  "organization_unit": "Sales",
}
SERVICE_INFO = dict(CA_INFO, cn="service.example.com")


def common_name(pem):
  certificate = x509.load_pem_x509_certificate(pem if isinstance(pem, bytes) else pem.encode())
  return certificate.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value


class TestOpenSSLWrapper:
  def setup_method(self):
    self.wrapper = OpenSSLWrapper()
    self.ca_cert, self.ca_key = self.wrapper.create_certificate(CA_INFO, request=False, key_length=2048)

  def create_signed_certificate(self, **kwargs):
    request, _key = self.wrapper.create_certificate(SERVICE_INFO, request=True, key_length=2048)
    return self.wrapper.create_cert_signed_certificate(self.ca_cert.decode(), self.ca_key.decode(), request.decode(), **kwargs)

  def test_create_self_signed_certificate(self):
    assert common_name(self.ca_cert) == "ca.example.com"
    assert self.ca_key.startswith(b"-----BEGIN")

  def test_create_certificate_request(self):
    request, key = self.wrapper.create_certificate(SERVICE_INFO, request=True, key_length=2048)

    csr = x509.load_pem_x509_csr(request)
    assert csr.is_signature_valid
    assert csr.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == "service.example.com"
    assert csr.subject.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value == "se"
    assert key.startswith(b"-----BEGIN")

  def test_certificate_request_requires_a_two_letter_country_code(self):
    with pytest.raises(WrongInput):
      self.wrapper.create_certificate(dict(SERVICE_INFO, country_code="swe"), request=True)

  def test_unsupported_hash_algorithm_is_rejected(self):
    with pytest.raises(WrongInput):
      self.wrapper.create_certificate(SERVICE_INFO, request=True, hash_alg="nosuchhash")

  def test_encrypted_private_key(self):
    _cert, key = self.wrapper.create_certificate(
      CA_INFO, key_length=2048, cipher_passphrase={"cipher": "aes256", "passphrase": "secret"}
    )

    assert b"ENCRYPTED" in key

  def test_sign_certificate_request_with_ca(self):
    signed = self.create_signed_certificate()

    certificate = x509.load_pem_x509_certificate(signed.encode())
    assert common_name(signed) == "service.example.com"
    assert certificate.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == "ca.example.com"

  def test_sign_certificate_request_with_encrypted_ca_key(self):
    ca_cert, ca_key = self.wrapper.create_certificate(
      CA_INFO, key_length=2048, cipher_passphrase={"cipher": "aes256", "passphrase": "secret"}
    )
    request, _key = self.wrapper.create_certificate(SERVICE_INFO, request=True, key_length=2048)

    signed = self.wrapper.create_cert_signed_certificate(ca_cert.decode(), ca_key.decode(), request.decode(), passphrase="secret")

    assert common_name(signed) == "service.example.com"

  def test_verify_accepts_certificate_signed_by_ca(self):
    valid, _message = self.wrapper.verify(self.ca_cert.decode(), self.create_signed_certificate())

    assert valid

  def test_verify_rejects_certificate_signed_by_another_ca(self):
    other_ca_cert, _other_key = self.wrapper.create_certificate(dict(CA_INFO, cn="other.example.com"), key_length=2048)

    valid, message = self.wrapper.verify(other_ca_cert.decode(), self.create_signed_certificate())

    assert not valid
    assert "incorrectly signed" in message

  def test_verify_rejects_certificate_with_same_common_name_as_the_ca(self):
    request, _key = self.wrapper.create_certificate(CA_INFO, request=True, key_length=2048)
    signed = self.wrapper.create_cert_signed_certificate(self.ca_cert.decode(), self.ca_key.decode(), request.decode())

    valid, message = self.wrapper.verify(self.ca_cert.decode(), signed)

    assert not valid
    assert "CN may not be equal" in message

  def test_certificate_error_is_raised_when_the_key_cannot_be_dumped(self):
    with pytest.raises(CertificateError):
      self.wrapper.create_certificate(CA_INFO, key_length=2048, cipher_passphrase={"cipher": "nosuchcipher", "passphrase": "secret"})
