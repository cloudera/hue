#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import closing

from saml2 import config
from saml2.authn_context import INTERNETPROTOCOLPASSWORD

from saml2.server import Server
from saml2.response import response_factory
from saml2.response import StatusResponse
from saml2.response import AuthnResponse
from saml2.sigver import SignatureError

from pathutils import full_path

FALSE_ASSERT_SIGNED = full_path("saml_false_signed.xml")

TIMESLACK = 62000000  # Roughly +- 24 month


def _eq(l1, l2):
    return set(l1) == set(l2)


IDENTITY = {"eduPersonAffiliation": ["staff", "member"],
            "surName": ["Jeter"], "givenName": ["Derek"],
            "mail": ["foo@gmail.com"],
            "title": ["shortstop"]}

AUTHN = {
    "class_ref": INTERNETPROTOCOLPASSWORD,
    "authn_auth": "http://www.example.com/login"
}


class TestResponse:
    def setup_class(self):
        with closing(Server("idp_conf")) as server:
            name_id = server.ident.transient_nameid(
                "urn:mace:example.com:saml:roland:sp", "id12")

            self._resp_ = server.create_authn_response(
                IDENTITY,
                "id12",  # in_response_to
                "http://lingon.catalogix.se:8087/",
                # consumer_url
                "urn:mace:example.com:saml:roland:sp",
                # sp_entity_id
                name_id=name_id)

            self._sign_resp_ = server.create_authn_response(
                IDENTITY,
                "id12",  # in_response_to
                "http://lingon.catalogix.se:8087/",  # consumer_url
                "urn:mace:example.com:saml:roland:sp",  # sp_entity_id
                name_id=name_id,
                sign_assertion=True)

            self._resp_authn = server.create_authn_response(
                IDENTITY,
                "id12",  # in_response_to
                "http://lingon.catalogix.se:8087/",  # consumer_url
                "urn:mace:example.com:saml:roland:sp",  # sp_entity_id
                name_id=name_id,
                authn=AUTHN)

            conf = config.SPConfig()
            conf.load_file("server_conf")
            self.conf = conf

    def test_1(self):
        xml_response = ("%s" % (self._resp_,))
        resp = response_factory(xml_response, self.conf,
                                return_addrs=[
                                    "http://lingon.catalogix.se:8087/"],
                                outstanding_queries={
                                    "id12": "http://localhost:8088/sso"},
                                timeslack=TIMESLACK, decode=False)

        assert isinstance(resp, StatusResponse)
        assert isinstance(resp, AuthnResponse)

    def test_2(self):
        xml_response = self._sign_resp_
        resp = response_factory(xml_response, self.conf,
                                return_addrs=[
                                    "http://lingon.catalogix.se:8087/"],
                                outstanding_queries={
                                    "id12": "http://localhost:8088/sso"},
                                timeslack=TIMESLACK, decode=False)

        assert isinstance(resp, StatusResponse)
        assert isinstance(resp, AuthnResponse)

    def test_false_sign(self):
        xml_response = open(FALSE_ASSERT_SIGNED).read()
        resp = response_factory(
            xml_response, self.conf,
            return_addrs=["http://lingon.catalogix.se:8087/"],
            outstanding_queries={
                "bahigehogffohiphlfmplepdpcohkhhmheppcdie":
                    "http://localhost:8088/sso"},
            timeslack=TIMESLACK, decode=False)

        assert isinstance(resp, StatusResponse)
        assert isinstance(resp, AuthnResponse)
        try:
            resp.verify()
        except SignatureError:
            pass
        else:
            assert False

    def test_other_response(self):
        xml_response = open(full_path("attribute_response.xml")).read()
        resp = response_factory(
            xml_response, self.conf,
            return_addrs=['https://myreviewroom.com/saml2/acs/'],
            outstanding_queries={'id-f4d370f3d03650f3ec0da694e2348bfe':
                                 "http://localhost:8088/sso"},
            timeslack=TIMESLACK, decode=False)

        assert isinstance(resp, StatusResponse)
        assert isinstance(resp, AuthnResponse)
        resp.sec.only_use_keys_in_metadata=False
        resp.parse_assertion()
        si = resp.session_info()
        assert si
        print(si["ava"])


if __name__ == "__main__":
    t = TestResponse()
    t.setup_class()
    t.test_false_sign()
