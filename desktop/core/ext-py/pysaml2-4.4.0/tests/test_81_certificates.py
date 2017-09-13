from os import remove
import os
import time

__author__ = 'haho0032'
import unittest
from saml2.cert import OpenSSLWrapper


class TestGenerateCertificates(unittest.TestCase):
    def test_validate_with_root_cert(self):

        cert_info_ca = {
            "cn": "qwerty",
            "country_code": "qw",
            "state": "qwerty",
            "city": "qwerty",
            "organization": "qwerty",
            "organization_unit": "qwerty"
        }

        cert_info = {
            "cn": "asdfgh",
            "country_code": "as",
            "state": "asdfgh",
            "city": "asdfgh",
            "organization": "asdfgh",
            "organization_unit": "asdfg"
        }

        osw = OpenSSLWrapper()

        ca_cert, ca_key = osw.create_certificate(cert_info_ca, request=False,
                                                 write_to_file=True,
                                                 cert_dir=os.path.dirname(
                                                     os.path.abspath(
                                                         __file__)) + "/pki")

        req_cert_str, req_key_str = osw.create_certificate(cert_info,
                                                           request=True)

        ca_cert_str = osw.read_str_from_file(ca_cert)
        ca_key_str = osw.read_str_from_file(ca_key)

        cert_str = osw.create_cert_signed_certificate(ca_cert_str, ca_key_str,
                                                      req_cert_str)

        valid, mess = osw.verify(ca_cert_str, cert_str)
        self.assertTrue(valid)

        false_ca_cert, false_ca_key = osw.create_certificate(cert_info_ca,
                                                             request=False,
                                                             write_to_file=False)
        false_req_cert_str_1, false_req_key_str_1 = osw.create_certificate(
            cert_info_ca, request=True)
        false_cert_str_1 = osw.create_cert_signed_certificate(false_ca_cert,
                                                              false_ca_key,
                                                              false_req_cert_str_1)
        false_req_cert_str_2, false_req_key_str_2 = osw.create_certificate(
            cert_info, request=True)
        false_cert_str_2 = osw.create_cert_signed_certificate(false_ca_cert,
                                                              false_ca_key,
                                                              false_req_cert_str_2)

        valid, mess = osw.verify(false_ca_cert, cert_str)
        self.assertFalse(valid)
        valid, mess = osw.verify(false_ca_cert, false_cert_str_1)
        self.assertFalse(valid)
        valid, mess = osw.verify(ca_cert_str, false_cert_str_2)
        self.assertFalse(valid)

        if 'z' in cert_str:
            false_cert_str = cert_str.replace('z', 'x')
            valid, mess = osw.verify(ca_cert_str, false_cert_str)
            self.assertFalse(valid)

        remove(ca_cert)
        remove(ca_key)

    def test_validate_cert_chains(self):

        cert_info_ca = {
            "cn": "qwerty",
            "country_code": "qw",
            "state": "qwerty",
            "city": "qwerty",
            "organization": "qwerty",
            "organization_unit": "qwerty"
        }

        cert_intermediate_1_info = {
            "cn": "intermediate_1",
            "country_code": "as",
            "state": "asdfgh",
            "city": "asdfgh",
            "organization": "asdfgh",
            "organization_unit": "asdfg"
        }

        cert_intermediate_2_info = {
            "cn": "intermediate_2",
            "country_code": "as",
            "state": "asdfgh",
            "city": "asdfgh",
            "organization": "asdfgh",
            "organization_unit": "asdfg"
        }

        cert_client_cert_info = {
            "cn": "intermediate_1",
            "country_code": "as",
            "state": "asdfgh",
            "city": "asdfgh",
            "organization": "asdfgh",
            "organization_unit": "asdfg"
        }

        osw = OpenSSLWrapper()

        ca_cert_str, ca_key_str = osw.create_certificate(cert_info_ca,
                                                         request=False)

        req_cert_str, intermediate_1_key_str = osw.create_certificate(
            cert_intermediate_1_info, request=True)
        intermediate_cert_1_str = osw.create_cert_signed_certificate(
            ca_cert_str, ca_key_str, req_cert_str)

        req_cert_str, intermediate_2_key_str = osw.create_certificate(
            cert_intermediate_2_info, request=True)
        intermediate_cert_2_str = osw.create_cert_signed_certificate(
            intermediate_cert_1_str, intermediate_1_key_str,
            req_cert_str)

        req_cert_str, client_key_str = osw.create_certificate(
            cert_client_cert_info, request=True)
        client_cert_str = osw.create_cert_signed_certificate(
            intermediate_cert_2_str, intermediate_2_key_str,
            req_cert_str)

        cert_chain = [intermediate_cert_2_str, intermediate_cert_1_str,
                      ca_cert_str]

        valid, mess = osw.verify_chain(cert_chain, client_cert_str)
        self.assertTrue(valid)


    def test_validate_passphrase(self):

        cert_info_ca = {
            "cn": "qwerty",
            "country_code": "qw",
            "state": "qwerty",
            "city": "qwerty",
            "organization": "qwerty",
            "organization_unit": "qwerty"
        }

        cert_info = {
            "cn": "intermediate_1",
            "country_code": "as",
            "state": "asdfgh",
            "city": "asdfgh",
            "organization": "asdfgh",
            "organization_unit": "asdfg"
        }

        osw = OpenSSLWrapper()

        ca_cert_str, ca_key_str = osw.create_certificate(
            cert_info_ca, request=False,
            cipher_passphrase={"cipher": "blowfish", "passphrase": "qwerty"})

        req_cert_str, req_key_str = osw.create_certificate(cert_info,
                                                           request=True)
        cert_str = osw.create_cert_signed_certificate(ca_cert_str, ca_key_str,
                                                      req_cert_str,
                                                      passphrase=b"qwerty")

        valid = False
        try:
            cert_str = osw.create_cert_signed_certificate(
                ca_cert_str, ca_key_str, req_cert_str,
                passphrase="qwertyqwerty")
        except Exception:
            valid = True

        self.assertTrue(valid)

    def test_validate_expire(self):

        cert_info_ca = {
            "cn": "qwerty",
            "country_code": "qw",
            "state": "qwerty",
            "city": "qwerty",
            "organization": "qwerty",
            "organization_unit": "qwerty"
        }

        cert_info = {
            "cn": "intermediate_1",
            "country_code": "as",
            "state": "asdfgh",
            "city": "asdfgh",
            "organization": "asdfgh",
            "organization_unit": "asdfg"
        }

        osw = OpenSSLWrapper()

        ca_cert_str, ca_key_str = osw.create_certificate(cert_info_ca,
                                                         request=False)

        req_cert_str, req_key_str = osw.create_certificate(cert_info,
                                                           request=True)
        cert_str = osw.create_cert_signed_certificate(ca_cert_str, ca_key_str,
                                                      req_cert_str)

        valid, mess = osw.verify(ca_cert_str, cert_str)

        ca_cert_str, ca_key_str = osw.create_certificate(cert_info_ca,
                                                         request=False,
                                                         valid_from=1000,
                                                         valid_to=100000)
        req_cert_str, req_key_str = osw.create_certificate(cert_info,
                                                           request=True)
        cert_str = osw.create_cert_signed_certificate(ca_cert_str, ca_key_str,
                                                      req_cert_str)
        valid, mess = osw.verify(ca_cert_str, cert_str)
        self.assertFalse(valid)

        ca_cert_str, ca_key_str = osw.create_certificate(cert_info_ca,
                                                         request=False)
        req_cert_str, req_key_str = osw.create_certificate(cert_info,
                                                           request=True)
        cert_str = osw.create_cert_signed_certificate(ca_cert_str, ca_key_str,
                                                      req_cert_str,
                                                      valid_from=1000,
                                                      valid_to=100000)
        valid, mess = osw.verify(ca_cert_str, cert_str)
        self.assertFalse(valid)

        ca_cert_str, ca_key_str = osw.create_certificate(cert_info_ca,
                                                         request=False,
                                                         valid_from=0,
                                                         valid_to=1)
        req_cert_str, req_key_str = osw.create_certificate(cert_info,
                                                           request=True)
        cert_str = osw.create_cert_signed_certificate(ca_cert_str, ca_key_str,
                                                      req_cert_str)
        time.sleep(2)
        valid, mess = osw.verify(ca_cert_str, cert_str)
        self.assertFalse(valid)

        ca_cert_str, ca_key_str = osw.create_certificate(cert_info_ca,
                                                         request=False)
        req_cert_str, req_key_str = osw.create_certificate(cert_info,
                                                           request=True)
        cert_str = osw.create_cert_signed_certificate(ca_cert_str, ca_key_str,
                                                      req_cert_str,
                                                      valid_from=0, valid_to=1)
        time.sleep(2)
        valid, mess = osw.verify(ca_cert_str, cert_str)
        self.assertFalse(valid)
