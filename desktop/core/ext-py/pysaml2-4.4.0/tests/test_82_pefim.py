from saml2 import xmldsig as ds
from saml2 import config
from saml2 import extension_elements_to_elements
from saml2 import element_to_extension_element
from saml2 import saml
from saml2.client import Saml2Client
from saml2.extension import pefim
from saml2.extension.pefim import SPCertEnc
from saml2.samlp import Extensions
from saml2.samlp import authn_request_from_string
from saml2.sigver import read_cert_from_file
from pathutils import full_path

__author__ = 'roland'

conf = config.SPConfig()
conf.load_file("server_conf")
client = Saml2Client(conf)

# place a certificate in an authn request
cert = read_cert_from_file(full_path("test.pem"), "pem")

spcertenc = SPCertEnc(
    x509_data=ds.X509Data(
        x509_certificate=ds.X509Certificate(text=cert)))

extensions = Extensions(
    extension_elements=[element_to_extension_element(spcertenc)])

req_id, req = client.create_authn_request(
    "http://www.example.com/sso",
    "urn:mace:example.com:it:tek",
    nameid_format=saml.NAMEID_FORMAT_PERSISTENT,
    message_id="666",
    extensions=extensions)


print(req)

# Get a certificate from an authn request

xml = "%s" % req

parsed = authn_request_from_string(xml)

_elem = extension_elements_to_elements(parsed.extensions.extension_elements,
                                       [pefim, ds])

assert len(_elem) == 1
_spcertenc = _elem[0]
_cert = _spcertenc.key_info[0].x509_data[0].x509_certificate.text
assert cert == _cert
