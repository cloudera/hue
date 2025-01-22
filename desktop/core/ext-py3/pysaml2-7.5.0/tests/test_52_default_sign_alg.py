#!/usr/bin/env python
import os

from saml2 import client
from saml2 import config
from saml2.authn_context import INTERNETPROTOCOLPASSWORD
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.saml import NameID
from saml2.samlp import response_from_string
from saml2.server import Server
import saml2.xmldsig as ds


nid = NameID(name_qualifier="foo", format=NAMEID_FORMAT_TRANSIENT, text="123456")

AUTHN = {"class_ref": INTERNETPROTOCOLPASSWORD, "authn_auth": "http://www.example.com/login"}


def _eq(l1, l2):
    return set(l1) == set(l2)


BASEDIR = os.path.abspath(os.path.dirname(__file__))


def get_ava(assertion):
    ava = {}
    for statement in assertion.attribute_statement:
        for attr in statement.attribute:
            value = []
            for tmp_val in attr.attribute_value:
                value.append(tmp_val.text)
            key = attr.friendly_name
            if key is None or len(key) == 0:
                key = attr.text
            ava[key] = value
    return ava


class TestSignedResponse:
    def setup_class(self):
        self.server = Server("idp_conf")
        conf = config.SPConfig()
        conf.load_file("server_conf")
        self.client = client.Saml2Client(conf)
        self.name_id = self.server.ident.transient_nameid("urn:mace:example.com:saml:roland:sp", "id12")
        self.ava = {"givenName": ["Derek"], "surName": ["Jeter"], "mail": ["derek@nyy.mlb.com"], "title": "The man"}

    def teardown_class(self):
        self.server.close()

    def verify_assertion(self, assertion):
        assert assertion
        assert assertion[0].attribute_statement

        ava = ava = get_ava(assertion[0])

        assert ava == {
            "mail": ["derek@nyy.mlb.com"],
            "givenName": ["Derek"],
            "surName": ["Jeter"],
            "title": ["The man"],
        }

    def test_signed_response(self):
        print(ds.DefaultSignature().get_digest_alg())
        name_id = self.server.ident.transient_nameid("urn:mace:example.com:saml:roland:sp", "id12")
        ava = {"givenName": ["Derek"], "surName": ["Jeter"], "mail": ["derek@nyy.mlb.com"], "title": "The man"}

        signed_resp = self.server.create_authn_response(
            ava,
            "id12",  # in_response_to
            "http://lingon.catalogix.se:8087/",  # consumer_url
            "urn:mace:example.com:saml:roland:sp",  # sp_entity_id
            name_id=name_id,
            sign_assertion=True,
        )

        print(signed_resp)
        assert signed_resp

        sresponse = response_from_string(signed_resp)
        assert ds.SIG_RSA_SHA1 in str(sresponse), "Not correctly signed!"
        assert ds.DIGEST_SHA1 in str(sresponse), "Not correctly signed!"

    def test_signed_response_1(self):
        signed_resp = self.server.create_authn_response(
            self.ava,
            "id12",  # in_response_to
            "http://lingon.catalogix.se:8087/",  # consumer_url
            "urn:mace:example.com:saml:roland:sp",  # sp_entity_id
            name_id=self.name_id,
            sign_response=True,
            sign_assertion=True,
        )

        sresponse = response_from_string(signed_resp)
        assert ds.SIG_RSA_SHA1 in str(sresponse), "Not correctly signed!"
        assert ds.DIGEST_SHA1 in str(sresponse), "Not correctly signed!"
        valid = self.server.sec.verify_signature(
            signed_resp,
            self.server.config.cert_file,
            node_name="urn:oasis:names:tc:SAML:2.0:protocol:Response",
            node_id=sresponse.id,
        )
        assert valid
        assert ds.SIG_RSA_SHA1 in str(sresponse.assertion[0]), "Not correctly signed!"
        assert ds.DIGEST_SHA1 in str(sresponse.assertion[0]), "Not correctly signed!"
        valid = self.server.sec.verify_signature(
            signed_resp,
            self.server.config.cert_file,
            node_name="urn:oasis:names:tc:SAML:2.0:assertion:Assertion",
            node_id=sresponse.assertion[0].id,
        )
        assert valid

        self.verify_assertion(sresponse.assertion)

    def test_signed_response_2(self):
        signed_resp = self.server.create_authn_response(
            self.ava,
            "id12",  # in_response_to
            "http://lingon.catalogix.se:8087/",  # consumer_url
            "urn:mace:example.com:saml:roland:sp",  # sp_entity_id
            name_id=self.name_id,
            sign_response=True,
            sign_assertion=True,
            sign_alg=ds.SIG_RSA_SHA256,
            digest_alg=ds.DIGEST_SHA256,
        )

        sresponse = response_from_string(signed_resp)
        assert ds.SIG_RSA_SHA256 in str(sresponse), "Not correctly signed!"
        assert ds.DIGEST_SHA256 in str(sresponse), "Not correctly signed!"
        valid = self.server.sec.verify_signature(
            signed_resp,
            self.server.config.cert_file,
            node_name="urn:oasis:names:tc:SAML:2.0:protocol:Response",
            node_id=sresponse.id,
        )
        assert valid
        assert ds.SIG_RSA_SHA256 in str(sresponse.assertion[0]), "Not correctly signed!"
        assert ds.DIGEST_SHA256 in str(sresponse.assertion[0]), "Not correctly signed!"
        valid = self.server.sec.verify_signature(
            signed_resp,
            self.server.config.cert_file,
            node_name="urn:oasis:names:tc:SAML:2.0:assertion:Assertion",
            node_id=sresponse.assertion[0].id,
        )
        assert valid

        self.verify_assertion(sresponse.assertion)


if __name__ == "__main__":
    ts = TestSignedResponse()
    ts.setup_class()
    ts.test_signed_response()
    ts.test_signed_response_1()
    ts.test_signed_response_2()
