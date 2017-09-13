from contextlib import closing
from saml2.authn_context import INTERNETPROTOCOLPASSWORD
from saml2.server import Server
from saml2.sigver import pre_encryption_part, ASSERT_XPATH, EncryptError
from saml2.sigver import CryptoBackendXmlSec1
from saml2.sigver import pre_encrypt_assertion
from pathutils import xmlsec_path
from pathutils import full_path

__author__ = 'roland'

TMPL_NO_HEADER = """<ns0:EncryptedData xmlns:ns0="http://www.w3.org/2001/04/xmlenc#" xmlns:ns1="http://www.w3.org/2000/09/xmldsig#" Id="ED" Type="http://www.w3.org/2001/04/xmlenc#Element"><ns0:EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#tripledes-cbc" /><ns1:KeyInfo><ns0:EncryptedKey Id="EK"><ns0:EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#rsa-1_5" /><ns1:KeyInfo><ns1:KeyName>my-rsa-key</ns1:KeyName></ns1:KeyInfo><ns0:CipherData><ns0:CipherValue /></ns0:CipherData></ns0:EncryptedKey></ns1:KeyInfo><ns0:CipherData><ns0:CipherValue /></ns0:CipherData></ns0:EncryptedData>"""
TMPL = "<?xml version='1.0' encoding='UTF-8'?>\n%s" % TMPL_NO_HEADER

IDENTITY = {"eduPersonAffiliation": ["staff", "member"],
            "surName": ["Jeter"], "givenName": ["Derek"],
            "mail": ["foo@gmail.com"],
            "title": ["shortstop"]}


AUTHN = {
    "class_ref": INTERNETPROTOCOLPASSWORD,
    "authn_auth": "http://www.example.com/login"
}


def test_pre_enc():
    tmpl = pre_encryption_part()
    print(tmpl)
    assert "%s" % tmpl in (TMPL_NO_HEADER, TMPL)


def test_reshuffle_response():
    with closing(Server("idp_conf")) as server:
        name_id = server.ident.transient_nameid(
            "urn:mace:example.com:saml:roland:sp", "id12")

        resp_ = server.create_authn_response(
            IDENTITY, "id12", "http://lingon.catalogix.se:8087/",
            "urn:mace:example.com:saml:roland:sp", name_id=name_id)

    resp2 = pre_encrypt_assertion(resp_)

    print(resp2)
    assert resp2.encrypted_assertion.extension_elements


def test_enc1():
    with closing(Server("idp_conf")) as server:
        name_id = server.ident.transient_nameid(
            "urn:mace:example.com:saml:roland:sp", "id12")

        resp_ = server.create_authn_response(
            IDENTITY, "id12", "http://lingon.catalogix.se:8087/",
            "urn:mace:example.com:saml:roland:sp", name_id=name_id)

    statement = pre_encrypt_assertion(resp_)

    tmpl = full_path("enc_tmpl.xml")
    # tmpl_file = open(tmpl, "w")
    # tmpl_file.write("%s" % pre_encryption_part())
    # tmpl_file.close()

    data = full_path("pre_enc.xml")
    # data_file = open(data, "w")
    # data_file.write("%s" % statement)
    # data_file.close()

    key_type = "des-192"
    com_list = [xmlsec_path, "encrypt", "--pubkey-cert-pem", full_path("pubkey.pem"),
                "--session-key", key_type, "--xml-data", data,
                "--node-xpath", ASSERT_XPATH]

    crypto = CryptoBackendXmlSec1(xmlsec_path)
    (_stdout, _stderr, output) = crypto._run_xmlsec(
        com_list, [tmpl], exception=EncryptError, validate_output=False)

    print(output)
    assert _stderr == ""
    assert _stdout == ""


def test_enc2():
    crypto = CryptoBackendXmlSec1(xmlsec_path)

    with closing(Server("idp_conf")) as server:
        name_id = server.ident.transient_nameid(
            "urn:mace:example.com:saml:roland:sp", "id12")

        resp_ = server.create_authn_response(
            IDENTITY, "id12", "http://lingon.catalogix.se:8087/",
            "urn:mace:example.com:saml:roland:sp", name_id=name_id)

    enc_resp = crypto.encrypt_assertion(resp_, full_path("pubkey.pem"),
                                        pre_encryption_part())

    print(enc_resp)
    assert enc_resp

if __name__ == "__main__":
    test_enc1()
