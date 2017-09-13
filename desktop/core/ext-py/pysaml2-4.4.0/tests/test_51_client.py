#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import uuid
import six
from future.backports.urllib.parse import parse_qs
from future.backports.urllib.parse import urlencode
from future.backports.urllib.parse import urlparse

from saml2.argtree import add_path
from saml2.cert import OpenSSLWrapper
from saml2.xmldsig import SIG_RSA_SHA256
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import config
from saml2 import class_name
from saml2 import extension_elements_to_elements
from saml2 import saml
from saml2 import samlp
from saml2 import sigver
from saml2 import s_utils
from saml2.assertion import Assertion

from saml2.authn_context import INTERNETPROTOCOLPASSWORD
from saml2.client import Saml2Client
from saml2.config import SPConfig
from saml2.response import LogoutResponse
from saml2.saml import NAMEID_FORMAT_PERSISTENT, EncryptedAssertion, Advice
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.saml import NameID
from saml2.samlp import SessionIndex
from saml2.server import Server
from saml2.sigver import pre_encryption_part, make_temp, pre_encrypt_assertion
from saml2.sigver import rm_xmltag
from saml2.sigver import verify_redirect_signature
from saml2.s_utils import do_attribute_statement
from saml2.s_utils import factory
from saml2.time_util import in_a_while, a_while_ago

from fakeIDP import FakeIDP
from fakeIDP import unpack_form
from pathutils import full_path

AUTHN = {
    "class_ref": INTERNETPROTOCOLPASSWORD,
    "authn_auth": "http://www.example.com/login"
}


def generate_cert():
    sn = uuid.uuid4().urn
    cert_info = {
        "cn": "localhost",
        "country_code": "se",
        "state": "ac",
        "city": "Umea",
        "organization": "ITS",
        "organization_unit": "DIRG"
    }
    osw = OpenSSLWrapper()
    ca_cert_str = osw.read_str_from_file(
        full_path("root_cert/localhost.ca.crt"))
    ca_key_str = osw.read_str_from_file(
        full_path("root_cert/localhost.ca.key"))
    req_cert_str, req_key_str = osw.create_certificate(cert_info, request=True,
                                                       sn=sn, key_length=2048)
    cert_str = osw.create_cert_signed_certificate(ca_cert_str, ca_key_str,
                                                  req_cert_str)
    return cert_str, req_key_str


def add_subelement(xmldoc, node_name, subelem):
    s = xmldoc.find(node_name)
    if s > 0:
        x = xmldoc.rindex("<", 0, s)
        tag = xmldoc[x + 1:s - 1]
        c = s + len(node_name)
        spaces = ""
        while xmldoc[c] == " ":
            spaces += " "
            c += 1
        # Sometimes we get an xml header, sometimes we don't.
        subelem_str = str(subelem)
        if subelem_str[0:5].lower() == '<?xml':
            subelem_str = subelem_str.split("\n", 1)[1]
        xmldoc = xmldoc.replace(
            "<%s:%s%s/>" % (tag, node_name, spaces),
            "<%s:%s%s>%s</%s:%s>" % (tag, node_name, spaces, subelem_str, tag,
                                     node_name))

    return xmldoc


def for_me(condition, me):
    for restriction in condition.audience_restriction:
        audience = restriction.audience
        if audience.text.strip() == me:
            return True


def ava(attribute_statement):
    result = {}
    for attribute in attribute_statement.attribute:
        # Check name_format ??
        name = attribute.name.strip()
        result[name] = []
        for value in attribute.attribute_value:
            result[name].append(value.text.strip())
    return result


def _leq(l1, l2):
    return set(l1) == set(l2)


# def test_parse_3():
#     xml_response = open(XML_RESPONSE_FILE3).read()
#     response = samlp.response_from_string(xml_response)
#     client = Saml2Client({})
#     (ava, name_id, real_uri) = \
#             client.do_response(response, "xenosmilus.umdc.umu.se")
#     print(40*"=")
#     print(ava)
#     print(40*",")
#     print(name_id)
#     assert False

REQ1 = {"1.2.14": """<?xml version='1.0' encoding='UTF-8'?>
<ns0:AttributeQuery Destination="https://idp.example.com/idp/" ID="id1"
IssueInstant="%s" Version="2.0" xmlns:ns0="urn:oasis:names:tc:SAML:2
.0:protocol"><ns1:Issuer Format="urn:oasis:names:tc:SAML:2
.0:nameid-format:entity" xmlns:ns1="urn:oasis:names:tc:SAML:2
.0:assertion">urn:mace:example.com:saml:roland:sp</ns1:Issuer><ns1:Subject
xmlns:ns1="urn:oasis:names:tc:SAML:2.0:assertion"><ns1:NameID
Format="urn:oasis:names:tc:SAML:2
.0:nameid-format:persistent">E8042FB4-4D5B-48C3-8E14-8EDD852790DD</ns1:NameID
></ns1:Subject></ns0:AttributeQuery>""",
        "1.2.16": """<?xml version='1.0' encoding='UTF-8'?>
<ns0:AttributeQuery xmlns:ns0="urn:oasis:names:tc:SAML:2.0:protocol"
xmlns:ns1="urn:oasis:names:tc:SAML:2.0:assertion" Destination="https://idp
.example.com/idp/" ID="id1" IssueInstant="%s" Version="2.0"><ns1:Issuer
Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">urn:mace:example
.com:saml:roland:sp</ns1:Issuer><ns1:Subject><ns1:NameID
Format="urn:oasis:names:tc:SAML:2
.0:nameid-format:persistent">E8042FB4-4D5B-48C3-8E14-8EDD852790DD</ns1:NameID
></ns1:Subject></ns0:AttributeQuery>"""}

nid = NameID(name_qualifier="foo", format=NAMEID_FORMAT_TRANSIENT,
             text="123456")


def list_values2simpletons(_dict):
    return dict([(k, v[0]) for k, v in _dict.items()])


class TestClient:
    def setup_class(self):
        self.server = Server("idp_conf")

        conf = config.SPConfig()
        conf.load_file("server_conf")
        self.client = Saml2Client(conf)

    def teardown_class(self):
        self.server.close()

    def test_create_attribute_query1(self):
        req_id, req = self.client.create_attribute_query(
            "https://idp.example.com/idp/",
            "E8042FB4-4D5B-48C3-8E14-8EDD852790DD",
            format=saml.NAMEID_FORMAT_PERSISTENT,
            message_id="id1")
        reqstr = "%s" % req.to_string().decode('utf-8')

        assert req.destination == "https://idp.example.com/idp/"
        assert req.id == "id1"
        assert req.version == "2.0"
        subject = req.subject
        name_id = subject.name_id
        assert name_id.format == saml.NAMEID_FORMAT_PERSISTENT
        assert name_id.text == "E8042FB4-4D5B-48C3-8E14-8EDD852790DD"
        issuer = req.issuer
        assert issuer.text == "urn:mace:example.com:saml:roland:sp"

        attrq = samlp.attribute_query_from_string(reqstr)

        print(attrq.keyswv())
        assert _leq(attrq.keyswv(), ['destination', 'subject', 'issue_instant',
                                     'version', 'id', 'issuer'])

        assert attrq.destination == req.destination
        assert attrq.id == req.id
        assert attrq.version == req.version
        assert attrq.issuer.text == issuer.text
        assert attrq.issue_instant == req.issue_instant
        assert attrq.subject.name_id.format == name_id.format
        assert attrq.subject.name_id.text == name_id.text

    def test_create_attribute_query2(self):
        req_id, req = self.client.create_attribute_query(
            "https://idp.example.com/idp/",
            "E8042FB4-4D5B-48C3-8E14-8EDD852790DD",
            attribute={
                ("urn:oid:2.5.4.42",
                 "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                 "givenName"): None,
                ("urn:oid:2.5.4.4",
                 "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                 "surname"): None,
                ("urn:oid:1.2.840.113549.1.9.1",
                 "urn:oasis:names:tc:SAML:2.0:attrname-format:uri"): None,
            },
            format=saml.NAMEID_FORMAT_PERSISTENT,
            message_id="id1")

        print(req.to_string())
        assert req.destination == "https://idp.example.com/idp/"
        assert req.id == "id1"
        assert req.version == "2.0"
        subject = req.subject
        name_id = subject.name_id
        assert name_id.format == saml.NAMEID_FORMAT_PERSISTENT
        assert name_id.text == "E8042FB4-4D5B-48C3-8E14-8EDD852790DD"
        assert len(req.attribute) == 3
        # one is givenName
        seen = []
        for attribute in req.attribute:
            if attribute.name == "urn:oid:2.5.4.42":
                assert attribute.name_format == saml.NAME_FORMAT_URI
                assert attribute.friendly_name == "givenName"
                seen.append("givenName")
            elif attribute.name == "urn:oid:2.5.4.4":
                assert attribute.name_format == saml.NAME_FORMAT_URI
                assert attribute.friendly_name == "surname"
                seen.append("surname")
            elif attribute.name == "urn:oid:1.2.840.113549.1.9.1":
                assert attribute.name_format == saml.NAME_FORMAT_URI
                if getattr(attribute, "friendly_name"):
                    assert False
                seen.append("email")
        assert _leq(seen, ["givenName", "surname", "email"])

    def test_create_attribute_query_3(self):
        req_id, req = self.client.create_attribute_query(
            "https://aai-demo-idp.switch.ch/idp/shibboleth",
            "_e7b68a04488f715cda642fbdd90099f5",
            format=saml.NAMEID_FORMAT_TRANSIENT,
            message_id="id1")

        assert isinstance(req, samlp.AttributeQuery)
        assert req.destination == "https://aai-demo-idp.switch" \
                                  ".ch/idp/shibboleth"
        assert req.id == "id1"
        assert req.version == "2.0"
        assert req.issue_instant
        assert req.issuer.text == "urn:mace:example.com:saml:roland:sp"
        nameid = req.subject.name_id
        assert nameid.format == saml.NAMEID_FORMAT_TRANSIENT
        assert nameid.text == "_e7b68a04488f715cda642fbdd90099f5"

    def test_create_auth_request_0(self):
        ar_str = "%s" % self.client.create_authn_request(
            "http://www.example.com/sso", message_id="id1")[1]

        ar = samlp.authn_request_from_string(ar_str)
        print(ar)
        assert ar.assertion_consumer_service_url == ("http://lingon.catalogix"
                                                     ".se:8087/")
        assert ar.destination == "http://www.example.com/sso"
        assert ar.protocol_binding == BINDING_HTTP_POST
        assert ar.version == "2.0"
        assert ar.provider_name == "urn:mace:example.com:saml:roland:sp"
        assert ar.issuer.text == "urn:mace:example.com:saml:roland:sp"
        nid_policy = ar.name_id_policy
        assert nid_policy.allow_create == "false"
        assert nid_policy.format == saml.NAMEID_FORMAT_TRANSIENT

    def test_create_auth_request_vo(self):
        assert list(self.client.config.vorg.keys()) == [
            "urn:mace:example.com:it:tek"]

        ar_str = "%s" % self.client.create_authn_request(
            "http://www.example.com/sso",
            "urn:mace:example.com:it:tek",  # vo
            nameid_format=NAMEID_FORMAT_PERSISTENT,
            message_id="666")[1]

        ar = samlp.authn_request_from_string(ar_str)
        print(ar)
        assert ar.id == "666"
        assert ar.assertion_consumer_service_url == "http://lingon.catalogix" \
                                                    ".se:8087/"
        assert ar.destination == "http://www.example.com/sso"
        assert ar.protocol_binding == BINDING_HTTP_POST
        assert ar.version == "2.0"
        assert ar.provider_name == "urn:mace:example.com:saml:roland:sp"
        assert ar.issuer.text == "urn:mace:example.com:saml:roland:sp"
        nid_policy = ar.name_id_policy
        assert nid_policy.allow_create == "false"
        assert nid_policy.format == saml.NAMEID_FORMAT_PERSISTENT
        assert nid_policy.sp_name_qualifier == "urn:mace:example.com:it:tek"

    def test_sign_auth_request_0(self):
        # print(self.client.config)

        req_id, areq = self.client.create_authn_request(
            "http://www.example.com/sso", sign=True, message_id="id1")

        ar_str = "%s" % areq
        ar = samlp.authn_request_from_string(ar_str)

        assert ar
        assert ar.signature
        assert ar.signature.signature_value
        signed_info = ar.signature.signed_info
        # print(signed_info)
        assert len(signed_info.reference) == 1
        assert signed_info.reference[0].uri == "#id1"
        assert signed_info.reference[0].digest_value
        print("------------------------------------------------")
        try:
            assert self.client.sec.correctly_signed_authn_request(
                ar_str, self.client.config.xmlsec_binary,
                self.client.config.metadata)
        except Exception:  # missing certificate
            self.client.sec.verify_signature(ar_str, node_name=class_name(ar))

    def test_create_logout_request(self):
        req_id, req = self.client.create_logout_request(
            "http://localhost:8088/slo", "urn:mace:example.com:saml:roland:idp",
            name_id=nid, reason="Tired", expire=in_a_while(minutes=15),
            session_indexes=["_foo"])

        assert req.destination == "http://localhost:8088/slo"
        assert req.reason == "Tired"
        assert req.version == "2.0"
        assert req.name_id == nid
        assert req.issuer.text == "urn:mace:example.com:saml:roland:sp"
        assert req.session_index == [SessionIndex("_foo")]

    def test_response_1(self):
        IDP = "urn:mace:example.com:saml:roland:idp"

        ava = {"givenName": ["Derek"], "surName": ["Jeter"],
               "mail": ["derek@nyy.mlb.com"], "title": ["The man"]}

        nameid_policy = samlp.NameIDPolicy(allow_create="false",
                                           format=saml.NAMEID_FORMAT_PERSISTENT)

        resp = self.server.create_authn_response(
            identity=ava,
            in_response_to="id1",
            destination="http://lingon.catalogix.se:8087/",
            sp_entity_id="urn:mace:example.com:saml:roland:sp",
            name_id_policy=nameid_policy,
            userid="foba0001@example.com",
            authn=AUTHN)

        resp_str = "%s" % resp

        resp_str = base64.encodestring(resp_str.encode('utf-8'))

        authn_response = self.client.parse_authn_request_response(
            resp_str, BINDING_HTTP_POST,
            {"id1": "http://foo.example.com/service"})

        assert authn_response is not None
        assert authn_response.issuer() == IDP
        assert authn_response.response.assertion[0].issuer.text == IDP
        session_info = authn_response.session_info()

        print(session_info)
        assert session_info["ava"] == {'mail': ['derek@nyy.mlb.com'],
                                       'givenName': ['Derek'],
                                       'sn': ['Jeter'],
                                       'title': ["The man"]}
        assert session_info["issuer"] == IDP
        assert session_info["came_from"] == "http://foo.example.com/service"
        response = samlp.response_from_string(authn_response.xmlstr)
        assert response.destination == "http://lingon.catalogix.se:8087/"
        assert "session_index" in session_info

        # One person in the cache
        assert len(self.client.users.subjects()) == 1
        subject_id = self.client.users.subjects()[0]
        print("||||", self.client.users.get_info_from(subject_id, IDP))
        # The information I have about the subject comes from one source
        assert self.client.users.issuers_of_info(subject_id) == [IDP]

        # --- authenticate another person

        ava = {"givenName": ["Alfonson"], "surName": ["Soriano"],
               "mail": ["alfonson@chc.mlb.com"], "title": ["outfielder"]}

        resp_str = "%s" % self.server.create_authn_response(
            identity=ava,
            in_response_to="id2",
            destination="http://lingon.catalogix.se:8087/",
            sp_entity_id="urn:mace:example.com:saml:roland:sp",
            name_id_policy=nameid_policy,
            userid="also0001@example.com",
            authn=AUTHN)

        resp_str = base64.encodestring(resp_str.encode('utf-8'))

        self.client.parse_authn_request_response(
            resp_str, BINDING_HTTP_POST,
            {"id2": "http://foo.example.com/service"})

        # Two persons in the cache
        assert len(self.client.users.subjects()) == 2
        issuers = [self.client.users.issuers_of_info(s) for s in
                   self.client.users.subjects()]
        # The information I have about the subjects comes from the same source
        print(issuers)
        assert issuers == [[IDP], [IDP]]

    def test_response_2(self):
        conf = config.SPConfig()
        conf.load_file("server_conf")
        _client = Saml2Client(conf)

        idp, ava, ava_verify, nameid_policy = self.setup_verify_authn_response()

        cert_str, cert_key_str = generate_cert()

        cert = \
            {
                "cert": cert_str,
                "key": cert_key_str
            }

        self.name_id = self.server.ident.transient_nameid(
            "urn:mace:example.com:saml:roland:sp", "id1")

        resp = self.server.create_authn_response(
            identity=ava,
            in_response_to="id1",
            destination="http://lingon.catalogix.se:8087/",
            sp_entity_id="urn:mace:example.com:saml:roland:sp",
            name_id=self.name_id,
            userid="foba0001@example.com",
            authn=AUTHN,
            sign_response=True,
            sign_assertion=True,
            encrypt_assertion=False,
            encrypt_assertion_self_contained=True,
            pefim=True,
            encrypt_cert_advice=cert_str
        )

        resp_str = "%s" % resp

        resp_str = base64.encodestring(resp_str.encode('utf-8'))

        authn_response = _client.parse_authn_request_response(
            resp_str, BINDING_HTTP_POST,
            {"id1": "http://foo.example.com/service"}, {"id1": cert})

        self.verify_authn_response(idp, authn_response, _client, ava_verify)

    def test_response_3(self):
        conf = config.SPConfig()
        conf.load_file("server_conf")
        _client = Saml2Client(conf)

        idp, ava, ava_verify, nameid_policy = self.setup_verify_authn_response()

        self.name_id = self.server.ident.transient_nameid(
            "urn:mace:example.com:saml:roland:sp", "id1")

        resp = self.server.create_authn_response(
            identity=ava,
            in_response_to="id1",
            destination="http://lingon.catalogix.se:8087/",
            sp_entity_id="urn:mace:example.com:saml:roland:sp",
            name_id=self.name_id,
            userid="foba0001@example.com",
            authn=AUTHN,
            sign_response=True,
            sign_assertion=True,
            encrypt_assertion=False,
            encrypt_assertion_self_contained=True,
            pefim=True,
        )

        resp_str = "%s" % resp

        resp_str = base64.encodestring(resp_str.encode('utf-8'))

        authn_response = _client.parse_authn_request_response(
            resp_str, BINDING_HTTP_POST,
            {"id1": "http://foo.example.com/service"})

        self.verify_authn_response(idp, authn_response, _client, ava_verify)

    def test_response_4(self):
        conf = config.SPConfig()
        conf.load_file("server_conf")
        _client = Saml2Client(conf)

        idp, ava, ava_verify, nameid_policy = self.setup_verify_authn_response()

        self.name_id = self.server.ident.transient_nameid(
            "urn:mace:example.com:saml:roland:sp", "id1")

        resp = self.server.create_authn_response(
            identity=ava,
            in_response_to="id1",
            destination="http://lingon.catalogix.se:8087/",
            sp_entity_id="urn:mace:example.com:saml:roland:sp",
            name_id=self.name_id,
            userid="foba0001@example.com",
            authn=AUTHN,
            sign_response=True,
            sign_assertion=True,
            encrypt_assertion=True,
            encrypt_assertion_self_contained=True,
            pefim=True,
        )

        resp_str = "%s" % resp

        resp_str = base64.encodestring(resp_str.encode('utf-8'))

        authn_response = _client.parse_authn_request_response(
            resp_str, BINDING_HTTP_POST,
            {"id1": "http://foo.example.com/service"})

        self.verify_authn_response(idp, authn_response, _client, ava_verify)

    def test_response_5(self):
        conf = config.SPConfig()
        conf.load_file("server_conf")
        _client = Saml2Client(conf)

        idp, ava, ava_verify, nameid_policy = self.setup_verify_authn_response()

        self.name_id = self.server.ident.transient_nameid(
            "urn:mace:example.com:saml:roland:sp", "id1")

        cert_str, cert_key_str = generate_cert()

        cert = \
            {
                "cert": cert_str,
                "key": cert_key_str
            }

        resp = self.server.create_authn_response(
            identity=ava,
            in_response_to="id1",
            destination="http://lingon.catalogix.se:8087/",
            sp_entity_id="urn:mace:example.com:saml:roland:sp",
            name_id=self.name_id,
            userid="foba0001@example.com",
            authn=AUTHN,
            sign_response=True,
            sign_assertion=True,
            encrypt_assertion=True,
            encrypt_assertion_self_contained=True,
            pefim=True,
            encrypt_cert_assertion=cert_str
        )

        resp_str = "%s" % resp

        resp_str = base64.encodestring(resp_str.encode('utf-8'))

        authn_response = _client.parse_authn_request_response(
            resp_str, BINDING_HTTP_POST,
            {"id1": "http://foo.example.com/service"}, {"id1": cert})

        self.verify_authn_response(idp, authn_response, _client, ava_verify)

    def test_response_6(self):
        conf = config.SPConfig()
        conf.load_file("server_conf")
        _client = Saml2Client(conf)

        idp, ava, ava_verify, nameid_policy = self.setup_verify_authn_response()

        self.name_id = self.server.ident.transient_nameid(
            "urn:mace:example.com:saml:roland:sp", "id1")

        cert_assertion_str, cert_key_assertion_str = generate_cert()

        cert_assertion = \
            {
                "cert": cert_assertion_str,
                "key": cert_key_assertion_str
            }

        cert_advice_str, cert_key_advice_str = generate_cert()

        cert_advice = \
            {
                "cert": cert_advice_str,
                "key": cert_key_advice_str
            }

        resp = self.server.create_authn_response(
            identity=ava,
            in_response_to="id1",
            destination="http://lingon.catalogix.se:8087/",
            sp_entity_id="urn:mace:example.com:saml:roland:sp",
            name_id=self.name_id,
            userid="foba0001@example.com",
            authn=AUTHN,
            sign_response=True,
            sign_assertion=True,
            encrypt_assertion=True,
            encrypt_assertion_self_contained=True,
            pefim=True,
            encrypt_cert_assertion=cert_assertion_str,
            encrypt_cert_advice=cert_advice_str
        )

        resp_str = "%s" % resp

        resp_str = base64.encodestring(resp_str.encode('utf-8'))

        authn_response = _client.parse_authn_request_response(
            resp_str, BINDING_HTTP_POST,
            {"id1": "http://foo.example.com/service"},
            {"id1": [cert_assertion, cert_advice]})

        self.verify_authn_response(idp, authn_response, _client, ava_verify)

    def test_response_7(self):
        conf = config.SPConfig()
        conf.load_file("server_conf")
        _client = Saml2Client(conf)

        idp, ava, ava_verify, nameid_policy = self.setup_verify_authn_response()

        self.name_id = self.server.ident.transient_nameid(
            "urn:mace:example.com:saml:roland:sp", "id1")

        resp = self.server.create_authn_response(
            identity=ava,
            in_response_to="id1",
            destination="http://lingon.catalogix.se:8087/",
            sp_entity_id="urn:mace:example.com:saml:roland:sp",
            name_id=self.name_id,
            userid="foba0001@example.com",
            authn=AUTHN,
            sign_response=True,
            sign_assertion=True,
            encrypt_assertion=True,
            encrypt_assertion_self_contained=True,
            encrypted_advice_attributes=True,
        )

        resp_str = "%s" % resp

        resp_str = base64.encodestring(resp_str.encode('utf-8'))

        authn_response = _client.parse_authn_request_response(
            resp_str, BINDING_HTTP_POST,
            {"id1": "http://foo.example.com/service"})

        self.verify_authn_response(idp, authn_response, _client, ava_verify)

    def test_response_8(self):
        conf = config.SPConfig()
        conf.load_file("server_conf")
        _client = Saml2Client(conf)

        idp, ava, ava_verify, nameid_policy = self.setup_verify_authn_response()

        self.name_id = self.server.ident.transient_nameid(
            "urn:mace:example.com:saml:roland:sp", "id1")

        cert_str, cert_key_str = generate_cert()

        cert = \
            {
                "cert": cert_str,
                "key": cert_key_str
            }

        resp = self.server.create_authn_response(
            identity=ava,
            in_response_to="id1",
            destination="http://lingon.catalogix.se:8087/",
            sp_entity_id="urn:mace:example.com:saml:roland:sp",
            name_id=self.name_id,
            userid="foba0001@example.com",
            authn=AUTHN,
            sign_response=True,
            sign_assertion=True,
            encrypt_assertion=True,
            encrypt_assertion_self_contained=True,
            encrypt_cert_assertion=cert_str
        )

        resp_str = "%s" % resp

        resp_str = base64.encodestring(resp_str.encode('utf-8'))

        authn_response = _client.parse_authn_request_response(
            resp_str, BINDING_HTTP_POST,
            {"id1": "http://foo.example.com/service"}, {"id1": cert})

        self.verify_authn_response(idp, authn_response, _client, ava_verify)

    def setup_verify_authn_response(self):
        idp = "urn:mace:example.com:saml:roland:idp"
        ava = {"givenName": ["Derek"], "surName": ["Jeter"],
               "mail": ["derek@nyy.mlb.com"], "title": ["The man"]}
        ava_verify = {'mail': ['derek@nyy.mlb.com'], 'givenName': ['Derek'],
                      'sn': ['Jeter'], 'title': ["The man"]}
        nameid_policy = samlp.NameIDPolicy(allow_create="false",
                                           format=saml.NAMEID_FORMAT_PERSISTENT)
        return idp, ava, ava_verify, nameid_policy

    def verify_authn_response(self, idp, authn_response, _client, ava_verify):
        assert authn_response is not None
        assert authn_response.issuer() == idp
        assert authn_response.assertion.issuer.text == idp
        session_info = authn_response.session_info()

        assert session_info["ava"] == ava_verify
        assert session_info["issuer"] == idp
        assert session_info["came_from"] == "http://foo.example.com/service"
        response = samlp.response_from_string(authn_response.xmlstr)
        assert response.destination == "http://lingon.catalogix.se:8087/"

        # One person in the cache
        assert len(_client.users.subjects()) == 1
        subject_id = _client.users.subjects()[0]
        # The information I have about the subject comes from one source
        assert _client.users.issuers_of_info(subject_id) == [idp]

    def test_init_values(self):
        entityid = self.client.config.entityid
        print(entityid)
        assert entityid == "urn:mace:example.com:saml:roland:sp"
        print(self.client.metadata.with_descriptor("idpsso"))
        location = self.client._sso_location()
        print(location)
        assert location == 'http://localhost:8088/sso'
        my_name = self.client._my_name()
        print(my_name)
        assert my_name == "urn:mace:example.com:saml:roland:sp"

    def test_sign_then_encrypt_assertion(self):
        # Begin with the IdPs side
        _sec = self.server.sec

        assertion = s_utils.assertion_factory(
            subject=factory(saml.Subject, text="_aaa",
                            name_id=factory(
                                saml.NameID,
                                format=saml.NAMEID_FORMAT_TRANSIENT)),
            attribute_statement=do_attribute_statement(
                {
                    ("", "", "surName"): ("Jeter", ""),
                    ("", "", "givenName"): ("Derek", ""),
                }
            ),
            issuer=self.server._issuer(),
        )

        assertion.signature = sigver.pre_signature_part(
            assertion.id, _sec.my_cert, 1)

        sigass = _sec.sign_statement(assertion, class_name(assertion),
                                     key_file=full_path("test.key"),
                                     node_id=assertion.id)
        # Create an Assertion instance from the signed assertion
        _ass = saml.assertion_from_string(sigass)

        response = sigver.response_factory(
            in_response_to="_012345",
            destination="https:#www.example.com",
            status=s_utils.success_status_factory(),
            issuer=self.server._issuer(),
            assertion=_ass
        )

        enctext = _sec.crypto.encrypt_assertion(response,
                                                self.client.sec.encryption_keypairs[
                                                    0]["cert_file"],
                                                pre_encryption_part())

        seresp = samlp.response_from_string(enctext)

        # Now over to the client side
        _csec = self.client.sec
        if seresp.encrypted_assertion:
            decr_text = _csec.decrypt(enctext)
            seresp = samlp.response_from_string(decr_text)
            resp_ass = []

            sign_cert_file = full_path("test.pem")
            for enc_ass in seresp.encrypted_assertion:
                assers = extension_elements_to_elements(
                    enc_ass.extension_elements, [saml, samlp])
                for ass in assers:
                    if ass.signature:
                        if not _csec.verify_signature("%s" % ass,
                                                      sign_cert_file,
                                                      node_name=class_name(
                                                          ass)):
                            continue
                    resp_ass.append(ass)

            seresp.assertion = resp_ass
            seresp.encrypted_assertion = None
            # print(_sresp)

        assert seresp.assertion

    def test_sign_then_encrypt_assertion2(self):
        # Begin with the IdPs side
        _sec = self.server.sec

        nameid_policy = samlp.NameIDPolicy(allow_create="false",
                                           format=saml.NAMEID_FORMAT_PERSISTENT)

        asser = Assertion({"givenName": "Derek", "surName": "Jeter"})
        farg = add_path(
            {},
            ['assertion', 'subject', 'subject_confirmation', 'method',
             saml.SCM_BEARER])
        add_path(
            farg['assertion']['subject']['subject_confirmation'],
            ['subject_confirmation_data', 'in_response_to',
             '_012345'])
        add_path(
            farg['assertion']['subject']['subject_confirmation'],
            ['subject_confirmation_data', 'recipient',
             "http://lingon.catalogix.se:8087/"])

        assertion = asser.construct(
            self.client.config.entityid,
            self.server.config.attribute_converters,
            self.server.config.getattr("policy", "idp"),
            name_id=factory(saml.NameID, format=saml.NAMEID_FORMAT_TRANSIENT),
            issuer=self.server._issuer(),
            authn_class=INTERNETPROTOCOLPASSWORD,
            authn_auth="http://www.example.com/login",
            farg=farg['assertion']
        )

        assertion.signature = sigver.pre_signature_part(
            assertion.id, _sec.my_cert, 1)

        sigass = _sec.sign_statement(assertion, class_name(assertion),
                                     key_file=self.client.sec.key_file,
                                     node_id=assertion.id)

        sigass = rm_xmltag(sigass)

        response = sigver.response_factory(
            in_response_to="_012345",
            destination="http://lingon.catalogix.se:8087/",
            status=s_utils.success_status_factory(),
            issuer=self.server._issuer(),
            encrypted_assertion=EncryptedAssertion()
        )

        xmldoc = "%s" % response
        # strangely enough I get different tags if I run this test separately
        # or as part of a bunch of tests.
        xmldoc = add_subelement(xmldoc, "EncryptedAssertion", sigass)

        enctext = _sec.crypto.encrypt_assertion(xmldoc,
                                                self.client.sec.encryption_keypairs[
                                                    1]["cert_file"],
                                                pre_encryption_part())

        # seresp = samlp.response_from_string(enctext)

        resp_str = base64.encodestring(enctext.encode('utf-8'))
        # Now over to the client side
        resp = self.client.parse_authn_request_response(
            resp_str, BINDING_HTTP_POST,
            {"_012345": "http://foo.example.com/service"})

        # assert resp.encrypted_assertion == []
        assert resp.assertion
        assert resp.ava == {'givenName': ['Derek'], 'sn': ['Jeter']}

    def test_sign_then_encrypt_assertion_advice_1(self):
        # Begin with the IdPs side
        _sec = self.server.sec

        nameid_policy = samlp.NameIDPolicy(allow_create="false",
                                           format=saml.NAMEID_FORMAT_PERSISTENT)

        asser = Assertion({"givenName": "Derek", "surName": "Jeter"})

        subject_confirmation_specs = {
            'recipient': "http://lingon.catalogix.se:8087/",
            'in_response_to': "_012345",
            'subject_confirmation_method': saml.SCM_BEARER
        }
        name_id = factory(saml.NameID, format=saml.NAMEID_FORMAT_TRANSIENT)

        farg = add_path(
            {},
            ['assertion', 'subject', 'subject_confirmation', 'method',
             saml.SCM_BEARER])
        add_path(
            farg['assertion']['subject']['subject_confirmation'],
            ['subject_confirmation_data', 'in_response_to',
             '_012345'])
        add_path(
            farg['assertion']['subject']['subject_confirmation'],
            ['subject_confirmation_data', 'recipient',
             "http://lingon.catalogix.se:8087/"])

        assertion = asser.construct(
            self.client.config.entityid,
            self.server.config.attribute_converters,
            self.server.config.getattr("policy", "idp"),
            issuer=self.server._issuer(),
            name_id=name_id,
            authn_class=INTERNETPROTOCOLPASSWORD,
            authn_auth="http://www.example.com/login",
            farg=farg['assertion'])

        a_asser = Assertion({"uid": "test01", "email": "test.testsson@test.se"})
        a_assertion = a_asser.construct(
            self.client.config.entityid,
            self.server.config.attribute_converters,
            self.server.config.getattr("policy", "idp"),
            issuer=self.server._issuer(),
            authn_class=INTERNETPROTOCOLPASSWORD,
            authn_auth="http://www.example.com/login",
            name_id=name_id,
            farg=farg['assertion'])

        a_assertion.signature = sigver.pre_signature_part(
            a_assertion.id, _sec.my_cert, 1)

        assertion.advice = Advice()

        assertion.advice.encrypted_assertion = []
        assertion.advice.encrypted_assertion.append(EncryptedAssertion())

        assertion.advice.encrypted_assertion[0].add_extension_element(
            a_assertion)

        response = sigver.response_factory(
            in_response_to="_012345",
            destination="http://lingon.catalogix.se:8087/",
            status=s_utils.success_status_factory(),
            issuer=self.server._issuer()
        )

        response.assertion.append(assertion)

        response = _sec.sign_statement("%s" % response, class_name(a_assertion),
                                       key_file=self.client.sec.key_file,
                                       node_id=a_assertion.id)

        # xmldoc = "%s" % response
        # strangely enough I get different tags if I run this test separately
        # or as part of a bunch of tests.
        # xmldoc = add_subelement(xmldoc, "EncryptedAssertion", sigass)

        node_xpath = ''.join(["/*[local-name()=\"%s\"]" % v for v in
                              ["Response", "Assertion", "Advice",
                               "EncryptedAssertion", "Assertion"]])

        enctext = _sec.crypto.encrypt_assertion(response,
                                                self.client.sec.encryption_keypairs[
                                                    0]["cert_file"],
                                                pre_encryption_part(),
                                                node_xpath=node_xpath)

        # seresp = samlp.response_from_string(enctext)

        resp_str = base64.encodestring(enctext.encode('utf-8'))
        # Now over to the client side
        resp = self.client.parse_authn_request_response(
            resp_str, BINDING_HTTP_POST,
            {"_012345": "http://foo.example.com/service"})

        # assert resp.encrypted_assertion == []
        assert resp.assertion
        assert resp.assertion.advice
        assert resp.assertion.advice.assertion
        assert resp.ava == \
               {'sn': ['Jeter'], 'givenName': ['Derek'], 'uid': ['test01'],
                'email': ['test.testsson@test.se']}

    def test_sign_then_encrypt_assertion_advice_2(self):
        # Begin with the IdPs side
        _sec = self.server.sec

        nameid_policy = samlp.NameIDPolicy(allow_create="false",
                                           format=saml.NAMEID_FORMAT_PERSISTENT)

        asser_1 = Assertion({"givenName": "Derek"})

        farg = add_path(
            {},
            ['assertion', 'subject', 'subject_confirmation', 'method',
             saml.SCM_BEARER])
        add_path(
            farg['assertion']['subject']['subject_confirmation'],
            ['subject_confirmation_data', 'in_response_to',
             '_012345'])
        add_path(
            farg['assertion']['subject']['subject_confirmation'],
            ['subject_confirmation_data', 'recipient',
             "http://lingon.catalogix.se:8087/"])
        name_id = factory(saml.NameID, format=saml.NAMEID_FORMAT_TRANSIENT)

        assertion_1 = asser_1.construct(
            self.client.config.entityid,
            self.server.config.attribute_converters,
            self.server.config.getattr("policy", "idp"),
            issuer=self.server._issuer(),
            authn_class=INTERNETPROTOCOLPASSWORD,
            authn_auth="http://www.example.com/login",
            name_id=name_id,
            farg=farg['assertion'])

        asser_2 = Assertion({"surName": "Jeter"})

        assertion_2 = asser_2.construct(
            self.client.config.entityid,
            self.server.config.attribute_converters,
            self.server.config.getattr("policy", "idp"),
            issuer=self.server._issuer(),
            authn_class=INTERNETPROTOCOLPASSWORD,
            authn_auth="http://www.example.com/login",
            name_id=name_id,
            farg=farg['assertion'])

        a_asser_1 = Assertion({"uid": "test01"})
        a_assertion_1 = a_asser_1.construct(
            self.client.config.entityid,
            self.server.config.attribute_converters,
            self.server.config.getattr("policy", "idp"),
            issuer=self.server._issuer(),
            authn_class=INTERNETPROTOCOLPASSWORD,
            authn_auth="http://www.example.com/login",
            name_id=name_id,
            farg=farg['assertion'])

        a_asser_2 = Assertion({"email": "test.testsson@test.se"})
        a_assertion_2 = a_asser_2.construct(
            self.client.config.entityid,
            self.server.config.attribute_converters,
            self.server.config.getattr("policy", "idp"),
            issuer=self.server._issuer(),
            authn_class=INTERNETPROTOCOLPASSWORD,
            authn_auth="http://www.example.com/login",
            name_id=name_id,
            farg=farg['assertion'])

        a_asser_3 = Assertion({"street": "street"})
        a_assertion_3 = a_asser_3.construct(
            self.client.config.entityid,
            self.server.config.attribute_converters,
            self.server.config.getattr("policy", "idp"),
            issuer=self.server._issuer(),
            authn_class=INTERNETPROTOCOLPASSWORD,
            authn_auth="http://www.example.com/login",
            name_id=name_id,
            farg=farg['assertion'])

        a_asser_4 = Assertion({"title": "title"})
        a_assertion_4 = a_asser_4.construct(
            self.client.config.entityid,
            self.server.config.attribute_converters,
            self.server.config.getattr("policy", "idp"),
            issuer=self.server._issuer(),
            authn_class=INTERNETPROTOCOLPASSWORD,
            authn_auth="http://www.example.com/login",
            name_id=name_id,
            farg=farg['assertion'])

        a_assertion_1.signature = sigver.pre_signature_part(
            a_assertion_1.id, _sec.my_cert, 1)

        a_assertion_2.signature = sigver.pre_signature_part(
            a_assertion_2.id, _sec.my_cert, 1)

        a_assertion_3.signature = sigver.pre_signature_part(
            a_assertion_3.id, _sec.my_cert, 1)

        a_assertion_4.signature = sigver.pre_signature_part(
            a_assertion_4.id, _sec.my_cert, 1)

        assertion_1.signature = sigver.pre_signature_part(assertion_1.id,
                                                          _sec.my_cert, 1)

        assertion_2.signature = sigver.pre_signature_part(assertion_2.id,
                                                          _sec.my_cert, 1)

        response = sigver.response_factory(
            in_response_to="_012345",
            destination="http://lingon.catalogix.se:8087/",
            status=s_utils.success_status_factory(),
            issuer=self.server._issuer()
        )

        response.assertion = assertion_1

        response.assertion.advice = Advice()

        response.assertion.advice.encrypted_assertion = []
        response.assertion.advice.encrypted_assertion.append(
            EncryptedAssertion())

        response.assertion.advice.encrypted_assertion[0].add_extension_element(
            a_assertion_1)

        advice_tag = response.assertion.advice._to_element_tree().tag
        assertion_tag = a_assertion_1._to_element_tree().tag
        response = \
            response.get_xml_string_with_self_contained_assertion_within_advice_encrypted_assertion(
                assertion_tag, advice_tag)

        response = _sec.sign_statement("%s" % response,
                                       class_name(a_assertion_1),
                                       key_file=self.server.sec.key_file,
                                       node_id=a_assertion_1.id)

        node_xpath = ''.join(["/*[local-name()=\"%s\"]" % v for v in
                              ["Response", "Assertion", "Advice",
                               "EncryptedAssertion", "Assertion"]])

        enctext = _sec.crypto.encrypt_assertion(response,
                                                self.client.sec.encryption_keypairs[
                                                    1]["cert_file"],
                                                pre_encryption_part(),
                                                node_xpath=node_xpath)

        response = samlp.response_from_string(enctext)

        response.assertion = response.assertion[0]

        response.assertion.advice.encrypted_assertion.append(
            EncryptedAssertion())
        response.assertion.advice.encrypted_assertion[1].add_extension_element(
            a_assertion_2)

        advice_tag = response.assertion.advice._to_element_tree().tag
        assertion_tag = a_assertion_2._to_element_tree().tag
        response = \
            response.get_xml_string_with_self_contained_assertion_within_advice_encrypted_assertion(
                assertion_tag, advice_tag)

        response = _sec.sign_statement("%s" % response,
                                       class_name(a_assertion_2),
                                       key_file=self.server.sec.key_file,
                                       node_id=a_assertion_2.id)

        node_xpath = ''.join(["/*[local-name()=\"%s\"]" % v for v in
                              ["Response", "Assertion", "Advice",
                               "EncryptedAssertion", "Assertion"]])

        enctext = _sec.crypto.encrypt_assertion(response,
                                                self.client.sec.encryption_keypairs[
                                                    0]["cert_file"],
                                                pre_encryption_part(),
                                                node_xpath=node_xpath)

        response = samlp.response_from_string(enctext)

        response.assertion = response.assertion[0]

        assertion_tag = response.assertion._to_element_tree().tag
        response = pre_encrypt_assertion(response)
        response = \
            response.get_xml_string_with_self_contained_assertion_within_encrypted_assertion(
            assertion_tag)

        response = _sec.sign_statement("%s" % response, class_name(assertion_1),
                                       key_file=self.server.sec.key_file,
                                       node_id=assertion_1.id)

        enctext = _sec.crypto.encrypt_assertion(response,
                                                self.client.sec.encryption_keypairs[
                                                    1]["cert_file"],
                                                pre_encryption_part())

        response = samlp.response_from_string(enctext)

        response.assertion = assertion_2

        response.assertion.advice = Advice()

        response.assertion.advice.encrypted_assertion = []
        response.assertion.advice.encrypted_assertion.append(
            EncryptedAssertion())

        response.assertion.advice.encrypted_assertion[0].add_extension_element(
            a_assertion_3)

        advice_tag = response.assertion.advice._to_element_tree().tag
        assertion_tag = a_assertion_3._to_element_tree().tag
        response = \
            response.get_xml_string_with_self_contained_assertion_within_advice_encrypted_assertion(
                assertion_tag, advice_tag)

        response = _sec.sign_statement("%s" % response,
                                       class_name(a_assertion_3),
                                       key_file=self.server.sec.key_file,
                                       node_id=a_assertion_3.id)

        node_xpath = ''.join(["/*[local-name()=\"%s\"]" % v for v in
                              ["Response", "Assertion", "Advice",
                               "EncryptedAssertion", "Assertion"]])

        enctext = _sec.crypto.encrypt_assertion(response,
                                                self.client.sec.encryption_keypairs[
                                                    0]["cert_file"],
                                                pre_encryption_part(),
                                                node_xpath=node_xpath)

        response = samlp.response_from_string(enctext)

        response.assertion = response.assertion[0]

        response.assertion.advice.encrypted_assertion.append(
            EncryptedAssertion())

        response.assertion.advice.encrypted_assertion[1].add_extension_element(
            a_assertion_4)

        advice_tag = response.assertion.advice._to_element_tree().tag
        assertion_tag = a_assertion_4._to_element_tree().tag
        response = \
            response.get_xml_string_with_self_contained_assertion_within_advice_encrypted_assertion(
                assertion_tag, advice_tag)

        response = _sec.sign_statement("%s" % response,
                                       class_name(a_assertion_4),
                                       key_file=self.server.sec.key_file,
                                       node_id=a_assertion_4.id)

        node_xpath = ''.join(["/*[local-name()=\"%s\"]" % v for v in
                              ["Response", "Assertion", "Advice",
                               "EncryptedAssertion", "Assertion"]])

        enctext = _sec.crypto.encrypt_assertion(response,
                                                self.client.sec.encryption_keypairs[
                                                    1]["cert_file"],
                                                pre_encryption_part(),
                                                node_xpath=node_xpath)

        response = samlp.response_from_string(enctext)

        response = _sec.sign_statement("%s" % response,
                                       class_name(response.assertion[0]),
                                       key_file=self.server.sec.key_file,
                                       node_id=response.assertion[0].id)

        response = samlp.response_from_string(response)

        # seresp = samlp.response_from_string(enctext)

        resp_str = base64.encodestring(str(response).encode('utf-8'))
        # Now over to the client side
        resp = self.client.parse_authn_request_response(
            resp_str, BINDING_HTTP_POST,
            {"_012345": "http://foo.example.com/service"})

        # assert resp.encrypted_assertion == []
        assert resp.assertion
        assert resp.assertion.advice
        assert resp.assertion.advice.assertion
        assert resp.ava == \
               {'street': ['street'], 'uid': ['test01'], 'title': ['title'],
                'givenName': ['Derek'], 'email':
                    ['test.testsson@test.se'], 'sn': ['Jeter']}

    def test_signed_redirect(self):

        msg_str = "%s" % self.client.create_authn_request(
            "http://localhost:8088/sso", message_id="id1")[1]

        info = self.client.apply_binding(
            BINDING_HTTP_REDIRECT, msg_str, destination="",
            relay_state="relay2", sigalg=SIG_RSA_SHA256)

        loc = info["headers"][0][1]
        qs = parse_qs(loc[1:])
        assert _leq(qs.keys(),
                    ['SigAlg', 'SAMLRequest', 'RelayState', 'Signature'])

        assert verify_redirect_signature(list_values2simpletons(qs),
                                         self.client.sec.sec_backend)

        res = self.server.parse_authn_request(qs["SAMLRequest"][0],
                                              BINDING_HTTP_REDIRECT)
        print(res)

    def test_do_logout_signed_redirect(self):
        conf = config.SPConfig()
        conf.load_file("sp_slo_redirect_conf")
        client = Saml2Client(conf)

        # information about the user from an IdP
        session_info = {
            "name_id": nid,
            "issuer": "urn:mace:example.com:saml:roland:idp",
            "not_on_or_after": in_a_while(minutes=15),
            "ava": {
                "givenName": "Anders",
                "surName": "Andersson",
                "mail": "anders.andersson@example.com"
            }
        }
        client.users.add_information_about_person(session_info)
        entity_ids = client.users.issuers_of_info(nid)
        assert entity_ids == ["urn:mace:example.com:saml:roland:idp"]

        resp = client.do_logout(nid, entity_ids, "Tired", in_a_while(minutes=5),
                                sign=True,
                                expected_binding=BINDING_HTTP_REDIRECT)

        assert list(resp.keys()) == entity_ids
        binding, info = resp[entity_ids[0]]
        assert binding == BINDING_HTTP_REDIRECT

        loc = info["headers"][0][1]
        _, _, _, _, qs, _ = urlparse(loc)
        qs = parse_qs(qs)
        assert _leq(qs.keys(),
                    ['SigAlg', 'SAMLRequest', 'RelayState', 'Signature'])

        assert verify_redirect_signature(list_values2simpletons(qs),
                                         client.sec.sec_backend)

        res = self.server.parse_logout_request(qs["SAMLRequest"][0],
                                               BINDING_HTTP_REDIRECT)
        print(res)

    def test_do_logout_post(self):
        # information about the user from an IdP
        session_info = {
            "name_id": nid,
            "issuer": "urn:mace:example.com:saml:roland:idp",
            "not_on_or_after": in_a_while(minutes=15),
            "ava": {
                "givenName": "Anders",
                "surName": "Andersson",
                "mail": "anders.andersson@example.com"
            },
            "session_index": SessionIndex("_foo")
        }
        self.client.users.add_information_about_person(session_info)
        entity_ids = self.client.users.issuers_of_info(nid)
        assert entity_ids == ["urn:mace:example.com:saml:roland:idp"]
        resp = self.client.do_logout(nid, entity_ids, "Tired",
                                     in_a_while(minutes=5), sign=True,
                                     expected_binding=BINDING_HTTP_POST)
        assert resp
        assert len(resp) == 1
        assert list(resp.keys()) == entity_ids
        binding, info = resp[entity_ids[0]]
        assert binding == BINDING_HTTP_POST

        _dic = unpack_form(info["data"][3])
        res = self.server.parse_logout_request(_dic["SAMLRequest"],
                                               BINDING_HTTP_POST)
        assert b'<ns0:SessionIndex>_foo</ns0:SessionIndex>' in res.xmlstr

    def test_do_logout_session_expired(self):
        # information about the user from an IdP
        session_info = {
            "name_id": nid,
            "issuer": "urn:mace:example.com:saml:roland:idp",
            "not_on_or_after": a_while_ago(minutes=15),
            "ava": {
                "givenName": "Anders",
                "surName": "Andersson",
                "mail": "anders.andersson@example.com"
            },
            "session_index": SessionIndex("_foo")
        }
        self.client.users.add_information_about_person(session_info)
        entity_ids = self.client.users.issuers_of_info(nid)
        assert entity_ids == ["urn:mace:example.com:saml:roland:idp"]
        resp = self.client.do_logout(nid, entity_ids, "Tired",
                                     in_a_while(minutes=5), sign=True,
                                     expected_binding=BINDING_HTTP_POST)
        assert resp
        assert len(resp) == 1
        assert list(resp.keys()) == entity_ids
        binding, info = resp[entity_ids[0]]
        assert binding == BINDING_HTTP_POST

        _dic = unpack_form(info["data"][3])
        res = self.server.parse_logout_request(_dic["SAMLRequest"],
                                               BINDING_HTTP_POST)
        assert b'<ns0:SessionIndex>_foo</ns0:SessionIndex>' in res.xmlstr


# Below can only be done with dummy Server
IDP = "urn:mace:example.com:saml:roland:idp"


class TestClientWithDummy():
    def setup_class(self):
        self.server = FakeIDP("idp_all_conf")

        conf = SPConfig()
        conf.load_file("servera_conf")
        self.client = Saml2Client(conf)

        self.client.send = self.server.receive

    def test_do_authn(self):
        binding = BINDING_HTTP_REDIRECT
        response_binding = BINDING_HTTP_POST
        sid, http_args = self.client.prepare_for_authenticate(
            IDP, "http://www.example.com/relay_state",
            binding=binding, response_binding=response_binding)

        assert isinstance(sid, six.string_types)
        assert len(http_args) == 4
        assert http_args["headers"][0][0] == "Location"
        assert http_args["data"] == []
        redirect_url = http_args["headers"][0][1]
        _, _, _, _, qs, _ = urlparse(redirect_url)
        qs_dict = parse_qs(qs)
        req = self.server.parse_authn_request(qs_dict["SAMLRequest"][0],
                                              binding)
        resp_args = self.server.response_args(req.message, [response_binding])
        assert resp_args["binding"] == response_binding

    def test_do_negotiated_authn(self):
        binding = BINDING_HTTP_REDIRECT
        response_binding = BINDING_HTTP_POST
        sid, auth_binding, http_args = \
            self.client.prepare_for_negotiated_authenticate(
            IDP, "http://www.example.com/relay_state",
            binding=binding, response_binding=response_binding)

        assert binding == auth_binding
        assert isinstance(sid, six.string_types)
        assert len(http_args) == 4
        assert http_args["headers"][0][0] == "Location"
        assert http_args["data"] == []
        redirect_url = http_args["headers"][0][1]
        _, _, _, _, qs, _ = urlparse(redirect_url)
        qs_dict = parse_qs(qs)
        req = self.server.parse_authn_request(qs_dict["SAMLRequest"][0],
                                              binding)
        resp_args = self.server.response_args(req.message, [response_binding])
        assert resp_args["binding"] == response_binding

    def test_do_attribute_query(self):
        response = self.client.do_attribute_query(
            IDP, "_e7b68a04488f715cda642fbdd90099f5",
            attribute={"eduPersonAffiliation": None},
            nameid_format=NAMEID_FORMAT_TRANSIENT)

    def test_logout_1(self):
        """ one IdP/AA logout from"""

        # information about the user from an IdP
        session_info = {
            "name_id": nid,
            "issuer": "urn:mace:example.com:saml:roland:idp",
            "not_on_or_after": in_a_while(minutes=15),
            "ava": {
                "givenName": "Anders",
                "surName": "Andersson",
                "mail": "anders.andersson@example.com"
            }
        }
        self.client.users.add_information_about_person(session_info)
        entity_ids = self.client.users.issuers_of_info(nid)
        assert entity_ids == ["urn:mace:example.com:saml:roland:idp"]
        resp = self.client.global_logout(nid, "Tired", in_a_while(minutes=5))
        print(resp)
        assert resp
        assert len(resp) == 1
        assert list(resp.keys()) == entity_ids
        response = resp[entity_ids[0]]
        assert isinstance(response, LogoutResponse)

    def test_post_sso(self):
        binding = BINDING_HTTP_POST
        response_binding = BINDING_HTTP_POST
        sid, http_args = self.client.prepare_for_authenticate(
            "urn:mace:example.com:saml:roland:idp", relay_state="really",
            binding=binding, response_binding=response_binding)
        _dic = unpack_form(http_args["data"][3])

        req = self.server.parse_authn_request(_dic["SAMLRequest"], binding)
        resp_args = self.server.response_args(req.message, [response_binding])
        assert resp_args["binding"] == response_binding

        # Normally a response would now be sent back to the users web client
        # Here I fake what the client will do
        # create the form post

        http_args["data"] = urlencode(_dic)
        http_args["method"] = "POST"
        http_args["dummy"] = _dic["SAMLRequest"]
        http_args["headers"] = [('Content-type',
                                 'application/x-www-form-urlencoded')]

        response = self.client.send(**http_args)
        print(response.text)
        _dic = unpack_form(response.text[3], "SAMLResponse")
        resp = self.client.parse_authn_request_response(_dic["SAMLResponse"],
                                                        BINDING_HTTP_POST,
                                                        {sid: "/"})
        ac = resp.assertion.authn_statement[0].authn_context
        assert ac.authenticating_authority[0].text == \
               'http://www.example.com/login'
        assert ac.authn_context_class_ref.text == INTERNETPROTOCOLPASSWORD

    def test_negotiated_post_sso(self):
        binding = BINDING_HTTP_POST
        response_binding = BINDING_HTTP_POST
        sid, auth_binding, http_args = self.client.prepare_for_negotiated_authenticate(
            "urn:mace:example.com:saml:roland:idp", relay_state="really",
            binding=binding, response_binding=response_binding)
        _dic = unpack_form(http_args["data"][3])

        assert binding == auth_binding

        req = self.server.parse_authn_request(_dic["SAMLRequest"], binding)
        resp_args = self.server.response_args(req.message, [response_binding])
        assert resp_args["binding"] == response_binding

        # Normally a response would now be sent back to the users web client
        # Here I fake what the client will do
        # create the form post

        http_args["data"] = urlencode(_dic)
        http_args["method"] = "POST"
        http_args["dummy"] = _dic["SAMLRequest"]
        http_args["headers"] = [('Content-type',
                                 'application/x-www-form-urlencoded')]

        response = self.client.send(**http_args)
        print(response.text)
        _dic = unpack_form(response.text[3], "SAMLResponse")
        resp = self.client.parse_authn_request_response(_dic["SAMLResponse"],
                                                        BINDING_HTTP_POST,
                                                        {sid: "/"})
        ac = resp.assertion.authn_statement[0].authn_context
        assert ac.authenticating_authority[0].text == \
               'http://www.example.com/login'
        assert ac.authn_context_class_ref.text == INTERNETPROTOCOLPASSWORD


# if __name__ == "__main__":
#     tc = TestClient()
#     tc.setup_class()
#     tc.test_response()

if __name__ == "__main__":
    tc = TestClient()
    tc.setup_class()
    tc.test_sign_then_encrypt_assertion()
