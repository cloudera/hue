__author__ = 'haho0032'

import base64
import datetime
import dateutil.parser
import pytz
import six
from OpenSSL import crypto
from os.path import join
from os import remove

import saml2.cryptography.pki


class WrongInput(Exception):
    pass


class CertificateError(Exception):
    pass


class PayloadError(Exception):
    pass


class OpenSSLWrapper(object):
    def __init__(self):
        pass

    def create_certificate(self, cert_info, request=False, valid_from=0,
                           valid_to=315360000, sn=1, key_length=1024,
                           hash_alg="sha256", write_to_file=False, cert_dir="",
                           cipher_passphrase=None):
        """
        Can create certificate requests, to be signed later by another
        certificate with the method
        create_cert_signed_certificate. If request is True.

        Can also create self signed root certificates if request is False.
        This is default behaviour.

        :param cert_info:         Contains information about the certificate.
                                  Is a dictionary that must contain the keys:
                                  cn                = Common name. This part
                                  must match the host being authenticated
                                  country_code      = Two letter description
                                  of the country.
                                  state             = State
                                  city              = City
                                  organization      = Organization, can be a
                                  company name.
                                  organization_unit = A unit at the
                                  organization, can be a department.
                                  Example:
                                                    cert_info_ca = {
                                                        "cn": "company.com",
                                                        "country_code": "se",
                                                        "state": "AC",
                                                        "city": "Dorotea",
                                                        "organization":
                                                        "Company",
                                                        "organization_unit":
                                                        "Sales"
                                                    }
        :param request:           True if this is a request for certificate,
                                  that should be signed.
                                  False if this is a self signed certificate,
                                  root certificate.
        :param valid_from:        When the certificate starts to be valid.
                                  Amount of seconds from when the
                                  certificate is generated.
        :param valid_to:          How long the certificate will be valid from
                                  when it is generated.
                                  The value is in seconds. Default is
                                  315360000 seconds, a.k.a 10 years.
        :param sn:                Serial number for the certificate. Default
                                  is 1.
        :param key_length:        Length of the key to be generated. Defaults
                                  to 1024.
        :param hash_alg:          Hash algorithm to use for the key. Default
                                  is sha256.
        :param write_to_file:     True if you want to write the certificate
                                  to a file. The method will then return
                                  a tuple with path to certificate file and
                                  path to key file.
                                  False if you want to get the result as
                                  strings. The method will then return a tuple
                                  with the certificate string and the key as
                                  string.
                                  WILL OVERWRITE ALL EXISTING FILES WITHOUT
                                  ASKING!
        :param cert_dir:          Where to save the files if write_to_file is
                                  true.
        :param cipher_passphrase  A dictionary with cipher and passphrase.
        Example::
                {"cipher": "blowfish", "passphrase": "qwerty"}

        :return:                  string representation of certificate,
                                  string representation of private key
                                  if write_to_file parameter is False otherwise
                                  path to certificate file, path to private
                                  key file
        """
        cn = cert_info["cn"]

        c_f = None
        k_f = None

        if write_to_file:
            cert_file = "%s.crt" % cn
            key_file = "%s.key" % cn
            try:
                remove(cert_file)
            except:
                pass
            try:
                remove(key_file)
            except:
                pass
            c_f = join(cert_dir, cert_file)
            k_f = join(cert_dir, key_file)


        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, key_length)

        # create a self-signed cert
        cert = crypto.X509()

        if request:
            cert = crypto.X509Req()

        if (len(cert_info["country_code"]) != 2):
            raise WrongInput("Country code must be two letters!")
        cert.get_subject().C = cert_info["country_code"]
        cert.get_subject().ST = cert_info["state"]
        cert.get_subject().L = cert_info["city"]
        cert.get_subject().O = cert_info["organization"]
        cert.get_subject().OU = cert_info["organization_unit"]
        cert.get_subject().CN = cn
        if not request:
            cert.set_serial_number(sn)
            cert.gmtime_adj_notBefore(valid_from)  #Valid before present time
            cert.gmtime_adj_notAfter(valid_to)  #3 650 days
            cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, hash_alg)

        try:
            if request:
                tmp_cert = crypto.dump_certificate_request(crypto.FILETYPE_PEM,
                                                           cert)
            else:
                tmp_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
            tmp_key = None
            if cipher_passphrase is not None:
                passphrase = cipher_passphrase["passphrase"]
                if isinstance(cipher_passphrase["passphrase"],
                              six.string_types):
                    passphrase = passphrase.encode('utf-8')
                tmp_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, k,
                                                 cipher_passphrase["cipher"],
                                                 passphrase)
            else:
                tmp_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, k)
            if write_to_file:
                with open(c_f, 'wt') as fc:
                    fc.write(tmp_cert.decode('utf-8'))
                with open(k_f, 'wt') as fk:
                    fk.write(tmp_key.decode('utf-8'))
                return c_f, k_f
            return tmp_cert, tmp_key
        except Exception as ex:
            raise CertificateError("Certificate cannot be generated.", ex)

    def write_str_to_file(self, file, str_data):
        with open(file, 'wt') as f:
            f.write(str_data)

    def read_str_from_file(self, file, type="pem"):
        with open(file, 'rb') as f:
            str_data = f.read()

        if type == "pem":
            return str_data

        if type in ["der", "cer", "crt"]:
            return base64.b64encode(str(str_data))


    def create_cert_signed_certificate(self, sign_cert_str, sign_key_str,
                                       request_cert_str, hash_alg="sha256",
                                       valid_from=0, valid_to=315360000, sn=1,
                                       passphrase=None):

        """
        Will sign a certificate request with a give certificate.
        :param sign_cert_str:     This certificate will be used to sign with.
                                  Must be a string representation of
                                  the certificate. If you only have a file
                                  use the method read_str_from_file to
                                  get a string representation.
        :param sign_key_str:        This is the key for the ca_cert_str
                                  represented as a string.
                                  If you only have a file use the method
                                  read_str_from_file to get a string
                                  representation.
        :param request_cert_str:  This is the prepared certificate to be
                                  signed. Must be a string representation of
                                  the requested certificate. If you only have
                                  a file use the method read_str_from_file
                                  to get a string representation.
        :param hash_alg:          Hash algorithm to use for the key. Default
                                  is sha256.
        :param valid_from:        When the certificate starts to be valid.
                                  Amount of seconds from when the
                                  certificate is generated.
        :param valid_to:          How long the certificate will be valid from
                                  when it is generated.
                                  The value is in seconds. Default is
                                  315360000 seconds, a.k.a 10 years.
        :param sn:                Serial number for the certificate. Default
                                  is 1.
        :param passphrase:        Password for the private key in sign_key_str.
        :return:                  String representation of the signed
                                  certificate.
        """
        ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, sign_cert_str)
        ca_key = None
        if passphrase is not None:
            ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, sign_key_str,
                                            passphrase)
        else:
            ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, sign_key_str)
        req_cert = crypto.load_certificate_request(crypto.FILETYPE_PEM,
                                                   request_cert_str)

        cert = crypto.X509()
        cert.set_subject(req_cert.get_subject())
        cert.set_serial_number(sn)
        cert.gmtime_adj_notBefore(valid_from)
        cert.gmtime_adj_notAfter(valid_to)
        cert.set_issuer(ca_cert.get_subject())
        cert.set_pubkey(req_cert.get_pubkey())
        cert.sign(ca_key, hash_alg)

        cert_dump = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
        if isinstance(cert_dump, six.string_types):
            return cert_dump
        return cert_dump.decode('utf-8')

    def verify_chain(self, cert_chain_str_list, cert_str):
        """

        :param cert_chain_str_list: Must be a list of certificate strings,
        where the first certificate to be validate
        is in the beginning and the root certificate is last.
        :param cert_str: The certificate to be validated.
        :return:
        """
        for tmp_cert_str in cert_chain_str_list:
            valid, message = self.verify(tmp_cert_str, cert_str)
            if not valid:
                return False, message
            else:
                cert_str = tmp_cert_str
            return (True,
                    "Signed certificate is valid and correctly signed by CA "
                    "certificate.")

    def certificate_not_valid_yet(self, cert):
        starts_to_be_valid = dateutil.parser.parse(cert.get_notBefore())
        now = pytz.UTC.localize(datetime.datetime.utcnow())
        if starts_to_be_valid < now:
            return False
        return True


    def verify(self, signing_cert_str, cert_str):
        """
        Verifies if a certificate is valid and signed by a given certificate.

        :param signing_cert_str: This certificate will be used to verify the
                                  signature. Must be a string representation
                                 of the certificate. If you only have a file
                                 use the method read_str_from_file to
                                 get a string representation.
        :param cert_str:         This certificate will be verified if it is
                                  correct. Must be a string representation
                                 of the certificate. If you only have a file
                                 use the method read_str_from_file to
                                 get a string representation.
        :return:                 Valid, Message
                                 Valid = True if the certificate is valid,
                                 otherwise false.
                                 Message = Why the validation failed.
        """
        try:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM,
                                              signing_cert_str)
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_str)

            if self.certificate_not_valid_yet(ca_cert):
                return False, "CA certificate is not valid yet."

            if ca_cert.has_expired() == 1:
                return False, "CA certificate is expired."

            if cert.has_expired() == 1:
                return False, "The signed certificate is expired."

            if self.certificate_not_valid_yet(cert):
                return False, "The signed certificate is not valid yet."

            if ca_cert.get_subject().CN == cert.get_subject().CN:
                return False, ("CN may not be equal for CA certificate and the "
                               "signed certificate.")

            cert_algorithm = cert.get_signature_algorithm()
            if six.PY3:
                cert_algorithm = cert_algorithm.decode('ascii')
                cert_str = cert_str.encode('ascii')

            cert_crypto = saml2.cryptography.pki.load_pem_x509_certificate(
                    cert_str)

            try:
                crypto.verify(ca_cert, cert_crypto.signature,
                              cert_crypto.tbs_certificate_bytes,
                              cert_algorithm)
                return True, "Signed certificate is valid and correctly signed by CA certificate."
            except crypto.Error as e:
                return False, "Certificate is incorrectly signed."
        except Exception as e:
            return False, "Certificate is not valid for an unknown reason. %s" % str(e)
