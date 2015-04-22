#!/usr/bin/env python
# -*- coding: utf-8 -*-
from contextlib import closing
from saml2.authn_context import INTERNETPROTOCOLPASSWORD

from saml2.server import Server
from saml2.response import authn_response
from saml2.config import config_factory

from pathutils import dotname, full_path

XML_RESPONSE_FILE = full_path("saml_signed.xml")
XML_RESPONSE_FILE2 = full_path("saml2_response.xml")


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


class TestAuthnResponse:
    def setup_class(self):
        with closing(Server(dotname("idp_conf"))) as server:
            name_id = server.ident.transient_nameid(
                                "urn:mace:example.com:saml:roland:sp","id12")

            self._resp_ = server.create_authn_response(
                                IDENTITY,
                                "id12",                       # in_response_to
                                "http://lingon.catalogix.se:8087/",   # consumer_url
                                "urn:mace:example.com:saml:roland:sp", # sp_entity_id
                                name_id=name_id,
                                authn=AUTHN)

            self._sign_resp_ = server.create_authn_response(
                                IDENTITY,
                                "id12",                       # in_response_to
                                "http://lingon.catalogix.se:8087/",   # consumer_url
                                "urn:mace:example.com:saml:roland:sp", # sp_entity_id
                                name_id=name_id, sign_assertion=True,
                                authn=AUTHN)

            self._resp_authn = server.create_authn_response(
                                IDENTITY,
                                "id12",                       # in_response_to
                                "http://lingon.catalogix.se:8087/",   # consumer_url
                                "urn:mace:example.com:saml:roland:sp", # sp_entity_id
                                name_id=name_id,
                                authn=AUTHN)

            self.conf = config_factory("sp", dotname("server_conf"))
            self.conf.only_use_keys_in_metadata = False
            self.ar = authn_response(self.conf, "http://lingon.catalogix.se:8087/")
    
    def test_verify_1(self):
        xml_response = "%s" % (self._resp_,)
        print xml_response
        self.ar.outstanding_queries = {"id12": "http://localhost:8088/sso"}
        self.ar.timeslack = 10000
        self.ar.loads(xml_response, decode=False)
        self.ar.verify()
        
        print self.ar.__dict__
        assert self.ar.came_from == 'http://localhost:8088/sso'
        assert self.ar.session_id() == "id12"
        assert self.ar.ava["givenName"] == IDENTITY["givenName"]
        assert self.ar.name_id
        assert self.ar.issuer() == 'urn:mace:example.com:saml:roland:idp'
    
    def test_verify_signed_1(self):
        xml_response = self._sign_resp_
        print xml_response
        
        self.ar.outstanding_queries = {"id12": "http://localhost:8088/sso"}
        self.ar.timeslack = 10000
        self.ar.loads(xml_response, decode=False)
        self.ar.verify()
        
        print self.ar.__dict__
        assert self.ar.came_from == 'http://localhost:8088/sso'
        assert self.ar.session_id() == "id12"
        assert self.ar.ava["sn"] == IDENTITY["surName"]
        assert self.ar.issuer() == 'urn:mace:example.com:saml:roland:idp'
        assert self.ar.name_id

    def test_parse_2(self):
        xml_response = open(XML_RESPONSE_FILE).read()
        ID = "bahigehogffohiphlfmplepdpcohkhhmheppcdie"
        self.ar.outstanding_queries = {ID: "http://localhost:8088/foo"}    
        self.ar.return_addr = "http://xenosmilus.umdc.umu.se:8087/login"
        self.ar.entity_id = "xenosmilus.umdc.umu.se"
        # roughly a year, should create the response on the fly
        self.ar.timeslack = 315360000 # indecent long time
        self.ar.loads(xml_response, decode=False)
        self.ar.verify()
        
        print self.ar.__dict__
        assert self.ar.came_from == 'http://localhost:8088/foo'
        assert self.ar.session_id() == ID
        assert self.ar.name_id

    def test_verify_w_authn(self):
        xml_response = "%s" % (self._resp_authn,)
        self.ar.outstanding_queries = {"id12": "http://localhost:8088/sso"}
        self.ar.return_addr = "http://lingon.catalogix.se:8087/"
        self.ar.entity_id = "urn:mace:example.com:saml:roland:sp"
        self.ar.timeslack = 10000
        self.ar.loads(xml_response, decode=False)
        self.ar.verify()

        print self.ar.assertion
        assert len(self.ar.assertion.authn_statement) == 1
        authn_info = self.ar.authn_info()
        assert len(authn_info) == 1
        assert authn_info[0][0] == INTERNETPROTOCOLPASSWORD
        assert authn_info[0][1] == ["http://www.example.com/login"]
        session_info = self.ar.session_info()
        assert session_info["authn_info"] == authn_info

if __name__ == "__main__":
    t = TestAuthnResponse()
    t.setup_class()
    t.test_verify_1()
