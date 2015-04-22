#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
from contextlib import closing
from urlparse import parse_qs
from saml2.sigver import pre_encryption_part
from saml2.assertion import Policy
from saml2.authn_context import INTERNETPROTOCOLPASSWORD
from saml2.saml import NameID, NAMEID_FORMAT_TRANSIENT
from saml2.samlp import response_from_string

from saml2.server import Server
from saml2 import samlp
from saml2 import saml
from saml2 import client
from saml2 import config
from saml2 import class_name
from saml2 import extension_elements_to_elements
from saml2 import s_utils
from saml2 import sigver
from saml2 import time_util
from saml2.s_utils import OtherError
from saml2.s_utils import do_attribute_statement
from saml2.s_utils import factory
from saml2.soap import make_soap_enveloped_saml_thingy
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT

from py.test import raises

nid = NameID(name_qualifier="foo", format=NAMEID_FORMAT_TRANSIENT,
             text="123456")

AUTHN = {
    "class_ref": INTERNETPROTOCOLPASSWORD,
    "authn_auth": "http://www.example.com/login"
}


def _eq(l1, l2):
    return set(l1) == set(l2)


class TestServer1():
    def setup_class(self):
        self.server = Server("idp_conf")

        conf = config.SPConfig()
        conf.load_file("server_conf")
        self.client = client.Saml2Client(conf)

    def teardown_class(self):
        self.server.close()

    def test_issuer(self):
        issuer = self.server._issuer()
        assert isinstance(issuer, saml.Issuer)
        assert _eq(issuer.keyswv(), ["text", "format"])
        assert issuer.format == saml.NAMEID_FORMAT_ENTITY
        assert issuer.text == self.server.config.entityid

    def test_assertion(self):
        assertion = s_utils.assertion_factory(
            subject=factory(
                saml.Subject, text="_aaa",
                name_id=factory(saml.NameID,
                                format=saml.NAMEID_FORMAT_TRANSIENT)),
            attribute_statement=do_attribute_statement(
                {
                    ("", "", "surName"): ("Jeter", ""),
                    ("", "", "givenName"): ("Derek", ""),
                }
            ),
            issuer=self.server._issuer(),
        )

        assert _eq(assertion.keyswv(), ['attribute_statement', 'issuer', 'id',
                                        'subject', 'issue_instant', 'version'])
        assert assertion.version == "2.0"
        assert assertion.issuer.text == "urn:mace:example.com:saml:roland:idp"
        #
        assert assertion.attribute_statement
        attribute_statement = assertion.attribute_statement
        assert len(attribute_statement.attribute) == 2
        attr0 = attribute_statement.attribute[0]
        attr1 = attribute_statement.attribute[1]
        if attr0.attribute_value[0].text == "Derek":
            assert attr0.friendly_name == "givenName"
            assert attr1.friendly_name == "surName"
            assert attr1.attribute_value[0].text == "Jeter"
        else:
            assert attr1.friendly_name == "givenName"
            assert attr1.attribute_value[0].text == "Derek"
            assert attr0.friendly_name == "surName"
            assert attr0.attribute_value[0].text == "Jeter"
        # 
        subject = assertion.subject
        assert _eq(subject.keyswv(), ["text", "name_id"])
        assert subject.text == "_aaa"
        assert subject.name_id.format == saml.NAMEID_FORMAT_TRANSIENT

    def test_response(self):
        response = sigver.response_factory(
            in_response_to="_012345",
            destination="https:#www.example.com",
            status=s_utils.success_status_factory(),
            assertion=s_utils.assertion_factory(
                subject=factory(saml.Subject, text="_aaa",
                                name_id=saml.NAMEID_FORMAT_TRANSIENT),
                attribute_statement=do_attribute_statement(
                    {
                        ("", "", "surName"): ("Jeter", ""),
                        ("", "", "givenName"): ("Derek", ""),
                    }
                ),
                issuer=self.server._issuer(),
            ),
            issuer=self.server._issuer(),
        )

        print response.keyswv()
        assert _eq(response.keyswv(), ['destination', 'assertion', 'status',
                                       'in_response_to', 'issue_instant',
                                       'version', 'issuer', 'id'])
        assert response.version == "2.0"
        assert response.issuer.text == "urn:mace:example.com:saml:roland:idp"
        assert response.destination == "https:#www.example.com"
        assert response.in_response_to == "_012345"
        #
        status = response.status
        print status
        assert status.status_code.value == samlp.STATUS_SUCCESS

    def test_parse_faulty_request(self):
        req_id, authn_request = self.client.create_authn_request(
            destination="http://www.example.com", id="id1")

        # should raise an error because faulty spentityid
        binding = BINDING_HTTP_REDIRECT
        htargs = self.client.apply_binding(
            binding, "%s" % authn_request, "http://www.example.com", "abcd")
        _dict = parse_qs(htargs["headers"][0][1].split('?')[1])
        print _dict
        raises(OtherError, self.server.parse_authn_request,
               _dict["SAMLRequest"][0], binding)

    def test_parse_faulty_request_to_err_status(self):
        req_id, authn_request = self.client.create_authn_request(
            destination="http://www.example.com")

        binding = BINDING_HTTP_REDIRECT
        htargs = self.client.apply_binding(binding, "%s" % authn_request,
                                           "http://www.example.com", "abcd")
        _dict = parse_qs(htargs["headers"][0][1].split('?')[1])
        print _dict

        try:
            self.server.parse_authn_request(_dict["SAMLRequest"][0], binding)
            status = None
        except OtherError, oe:
            print oe.args
            status = s_utils.error_status_factory(oe)

        assert status
        print status
        assert _eq(status.keyswv(), ["status_code", "status_message"])
        assert status.status_message.text == 'Not destined for me!'
        status_code = status.status_code
        assert _eq(status_code.keyswv(), ["status_code", "value"])
        assert status_code.value == samlp.STATUS_RESPONDER
        assert status_code.status_code.value == samlp.STATUS_UNKNOWN_PRINCIPAL

    def test_parse_ok_request(self):
        req_id, authn_request = self.client.create_authn_request(
            message_id="id1", destination="http://localhost:8088/sso")

        print authn_request
        binding = BINDING_HTTP_REDIRECT
        htargs = self.client.apply_binding(binding, "%s" % authn_request,
                                           "http://www.example.com", "abcd")
        _dict = parse_qs(htargs["headers"][0][1].split('?')[1])
        print _dict

        req = self.server.parse_authn_request(_dict["SAMLRequest"][0], binding)
        # returns a dictionary
        print req
        resp_args = self.server.response_args(req.message, [BINDING_HTTP_POST])
        assert resp_args["destination"] == "http://lingon.catalogix.se:8087/"
        assert resp_args["in_response_to"] == "id1"
        name_id_policy = resp_args["name_id_policy"]
        assert _eq(name_id_policy.keyswv(), ["format", "allow_create"])
        assert name_id_policy.format == saml.NAMEID_FORMAT_TRANSIENT
        assert resp_args[
                   "sp_entity_id"] == "urn:mace:example.com:saml:roland:sp"

    def test_sso_response_with_identity(self):
        name_id = self.server.ident.transient_nameid(
            "urn:mace:example.com:saml:roland:sp", "id12")
        resp = self.server.create_authn_response(
            {
                "eduPersonEntitlement": "Short stop",
                "surName": "Jeter",
                "givenName": "Derek",
                "mail": "derek.jeter@nyy.mlb.com",
                "title": "The man"
            },
            "id12",  # in_response_to
            "http://localhost:8087/",  # destination
            "urn:mace:example.com:saml:roland:sp",  # sp_entity_id
            name_id=name_id,
            authn=AUTHN
        )

        print resp.keyswv()
        assert _eq(resp.keyswv(), ['status', 'destination', 'assertion',
                                   'in_response_to', 'issue_instant',
                                   'version', 'id', 'issuer'])
        assert resp.destination == "http://localhost:8087/"
        assert resp.in_response_to == "id12"
        assert resp.status
        assert resp.status.status_code.value == samlp.STATUS_SUCCESS
        assert resp.assertion
        assert resp.assertion
        assertion = resp.assertion
        print assertion
        assert assertion.authn_statement
        assert assertion.conditions
        assert assertion.attribute_statement
        attribute_statement = assertion.attribute_statement
        print attribute_statement
        assert len(attribute_statement[0].attribute) == 4
        # Pick out one attribute
        attr = None
        for attr in attribute_statement[0].attribute:
            if attr.friendly_name == "givenname":
                break
        assert len(attr.attribute_value) == 1
        assert attr.name == "urn:oid:2.5.4.42"
        assert attr.name_format == "urn:oasis:names:tc:SAML:2.0:attrname-format:uri"
        value = attr.attribute_value[0]
        assert value.text.strip() == "Derek"
        assert value.get_type() == "xs:string"
        assert assertion.subject
        assert assertion.subject.name_id
        assert assertion.subject.subject_confirmation
        confirmation = assertion.subject.subject_confirmation[0]
        print confirmation.keyswv()
        print confirmation.subject_confirmation_data
        assert confirmation.subject_confirmation_data.in_response_to == "id12"

    def test_sso_response_without_identity(self):
        resp = self.server.create_authn_response(
            {},
              "id12",  # in_response_to
              "http://localhost:8087/",  # consumer_url
              "urn:mace:example.com:saml:roland:sp",  # sp_entity_id
              userid="USER1",
              authn=AUTHN,
              release_policy=Policy(),
              best_effort=True
        )

        print resp.keyswv()
        assert _eq(resp.keyswv(), ['status', 'destination', 'in_response_to',
                                   'issue_instant', 'version', 'id', 'issuer',
                                   'assertion'])
        assert resp.destination == "http://localhost:8087/"
        assert resp.in_response_to == "id12"
        assert resp.status
        assert resp.status.status_code.value == samlp.STATUS_SUCCESS
        assert resp.issuer.text == "urn:mace:example.com:saml:roland:idp"
        assert not resp.assertion.attribute_statement

    def test_sso_response_specific_instant(self):
        _authn = AUTHN.copy()
        _authn["authn_instant"] = 1234567890

        resp = self.server.create_authn_response(
            {},
              "id12",  # in_response_to
              "http://localhost:8087/",  # consumer_url
              "urn:mace:example.com:saml:roland:sp",  # sp_entity_id
              userid="USER1",
              authn=_authn,
              best_effort=True
        )

        print resp.keyswv()
        assert _eq(resp.keyswv(), ['status', 'destination', 'in_response_to',
                                   'issue_instant', 'version', 'id', 'issuer',
                                   'assertion'])
        authn_statement = resp.assertion.authn_statement[0]
        assert authn_statement.authn_instant == '2009-02-13T23:31:30Z'

    def test_sso_failure_response(self):
        exc = s_utils.MissingValue("eduPersonAffiliation missing")
        resp = self.server.create_error_response(
            "id12", "http://localhost:8087/", exc)

        print resp.keyswv()
        assert _eq(resp.keyswv(), ['status', 'destination', 'in_response_to',
                                   'issue_instant', 'version', 'id', 'issuer'])
        assert resp.destination == "http://localhost:8087/"
        assert resp.in_response_to == "id12"
        assert resp.status
        print resp.status
        assert resp.status.status_code.value == samlp.STATUS_RESPONDER
        assert resp.status.status_code.status_code.value == \
               samlp.STATUS_REQUEST_UNSUPPORTED
        assert resp.status.status_message.text == \
               "eduPersonAffiliation missing"
        assert resp.issuer.text == "urn:mace:example.com:saml:roland:idp"
        assert not resp.assertion

    def test_authn_response_0(self):
        conf = config.SPConfig()
        conf.load_file("server_conf")
        self.client = client.Saml2Client(conf)

        ava = {"givenName": ["Derek"], "surName": ["Jeter"],
               "mail": ["derek@nyy.mlb.com"], "title": "The man"}

        npolicy = samlp.NameIDPolicy(format=saml.NAMEID_FORMAT_TRANSIENT,
                                     allow_create="true")
        resp_str = "%s" % self.server.create_authn_response(
            ava, "id1", "http://local:8087/",
            "urn:mace:example.com:saml:roland:sp", npolicy,
            "foba0001@example.com", authn=AUTHN)

        response = samlp.response_from_string(resp_str)
        print response.keyswv()
        assert _eq(response.keyswv(), ['status', 'destination', 'assertion',
                                       'in_response_to', 'issue_instant',
                                       'version', 'issuer', 'id'])
        print response.assertion[0].keyswv()
        assert len(response.assertion) == 1
        assert _eq(response.assertion[0].keyswv(), ['attribute_statement',
                                                    'issue_instant', 'version',
                                                    'subject', 'conditions',
                                                    'id', 'issuer',
                                                    'authn_statement'])
        assertion = response.assertion[0]
        assert len(assertion.attribute_statement) == 1
        astate = assertion.attribute_statement[0]
        print astate
        assert len(astate.attribute) == 4

    def test_signed_response(self):
        name_id = self.server.ident.transient_nameid(
            "urn:mace:example.com:saml:roland:sp", "id12")
        ava = {"givenName": ["Derek"], "surName": ["Jeter"],
               "mail": ["derek@nyy.mlb.com"], "title": "The man"}

        signed_resp = self.server.create_authn_response(
            ava,
            "id12",  # in_response_to
            "http://lingon.catalogix.se:8087/",  # consumer_url
            "urn:mace:example.com:saml:roland:sp",  # sp_entity_id
            name_id=name_id,
            sign_assertion=True
        )

        print signed_resp
        assert signed_resp

        sresponse = response_from_string(signed_resp)
        # It's the assertions that are signed not the response per se
        assert len(sresponse.assertion) == 1
        assertion = sresponse.assertion[0]

        # Since the reponse is created dynamically I don't know the signature
        # value. Just that there should be one
        assert assertion.signature.signature_value.text != ""

    def test_slo_http_post(self):
        soon = time_util.in_a_while(days=1)
        sinfo = {
            "name_id": nid,
            "issuer": "urn:mace:example.com:saml:roland:idp",
            "not_on_or_after": soon,
            "user": {
                "givenName": "Leo",
                "surName": "Laport",
            }
        }
        self.client.users.add_information_about_person(sinfo)

        req_id, logout_request = self.client.create_logout_request(
            destination="http://localhost:8088/slop", name_id=nid,
            issuer_entity_id="urn:mace:example.com:saml:roland:idp",
            reason="I'm tired of this")

        intermed = base64.b64encode("%s" % logout_request)

        #saml_soap = make_soap_enveloped_saml_thingy(logout_request)
        request = self.server.parse_logout_request(intermed, BINDING_HTTP_POST)
        assert request

    def test_slo_soap(self):
        soon = time_util.in_a_while(days=1)
        sinfo = {
            "name_id": nid,
            "issuer": "urn:mace:example.com:saml:roland:idp",
            "not_on_or_after": soon,
            "user": {
                "givenName": "Leo",
                "surName": "Laport",
            }
        }

        sp = client.Saml2Client(config_file="server_conf")
        sp.users.add_information_about_person(sinfo)

        req_id, logout_request = sp.create_logout_request(
            name_id=nid, destination="http://localhost:8088/slo",
            issuer_entity_id="urn:mace:example.com:saml:roland:idp",
            reason="I'm tired of this")

        #_ = s_utils.deflate_and_base64_encode("%s" % (logout_request,))

        saml_soap = make_soap_enveloped_saml_thingy(logout_request)
        self.server.ident.close()

        with closing(Server("idp_soap_conf")) as idp:
            request = idp.parse_logout_request(saml_soap)
            idp.ident.close()
            assert request

#------------------------------------------------------------------------

IDENTITY = {"eduPersonAffiliation": ["staff", "member"],
            "surName": ["Jeter"], "givenName": ["Derek"],
            "mail": ["foo@gmail.com"], "title": "The man"}


class TestServer2():
    def setup_class(self):
        self.server = Server("restrictive_idp_conf")

    def teardown_class(self):
        self.server.close()

    def test_do_attribute_reponse(self):
        aa_policy = self.server.config.getattr("policy", "idp")
        print aa_policy.__dict__
        response = self.server.create_attribute_response(
            IDENTITY.copy(), "aaa", "http://example.com/sp/",
            "urn:mace:example.com:sp:1")

        assert response is not None
        assert response.destination == "http://example.com/sp/"
        assert response.in_response_to == "aaa"
        assert response.version == "2.0"
        assert response.issuer.text == "urn:mace:example.com:saml:roland:idpr"
        assert response.status.status_code.value == samlp.STATUS_SUCCESS
        assert response.assertion
        assertion = response.assertion
        assert assertion.version == "2.0"
        subject = assertion.subject
        #assert subject.name_id.format == saml.NAMEID_FORMAT_TRANSIENT
        assert subject.subject_confirmation
        subject_conf = subject.subject_confirmation[0]
        assert subject_conf.subject_confirmation_data.in_response_to == "aaa"


def _logout_request(conf_file):
    conf = config.SPConfig()
    conf.load_file(conf_file)
    sp = client.Saml2Client(conf)

    soon = time_util.in_a_while(days=1)
    sinfo = {
        "name_id": nid,
        "issuer": "urn:mace:example.com:saml:roland:idp",
        "not_on_or_after": soon,
        "user": {
            "givenName": "Leo",
            "surName": "Laport",
        }
    }
    sp.users.add_information_about_person(sinfo)

    return sp.create_logout_request(
        name_id=nid,
        destination="http://localhost:8088/slo",
        issuer_entity_id="urn:mace:example.com:saml:roland:idp",
        reason="I'm tired of this")


class TestServerLogout():
    def test_1(self):
        with closing(Server("idp_slo_redirect_conf")) as server:
            req_id, request = _logout_request("sp_slo_redirect_conf")
            print request
            bindings = [BINDING_HTTP_REDIRECT]
            response = server.create_logout_response(request, bindings)
            binding, destination = server.pick_binding("single_logout_service",
                                                       bindings, "spsso",
                                                       request)

            http_args = server.apply_binding(binding, "%s" % response, destination,
                                             "relay_state", response=True)

            assert len(http_args) == 4
            assert http_args["headers"][0][0] == "Location"
            assert http_args["data"] == []


if __name__ == "__main__":
    ts = TestServer1()
    ts.setup_class()
