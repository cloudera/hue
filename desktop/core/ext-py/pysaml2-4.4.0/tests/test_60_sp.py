#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
from saml2.authn_context import INTERNETPROTOCOLPASSWORD
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.samlp import NameIDPolicy
from saml2.s2repoze.plugins.sp import make_plugin
from saml2.server import Server

ENV1 = {'SERVER_SOFTWARE': 'CherryPy/3.1.2 WSGI Server',
        'SCRIPT_NAME': '',
        'ACTUAL_SERVER_PROTOCOL': 'HTTP/1.1',
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/krissms',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'QUERY_STRING': '',
        'REMOTE_ADDR': '127.0.0.1',
        'HTTP_USER_AGENT':
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_2; en-us) ',
        'HTTP_CONNECTION': 'keep-alive',
        'SERVER_NAME': 'lingon-catalogix-se-2.local',
        'REMOTE_PORT': '57309',
        'wsgi.url_scheme': 'http',
        'SERVER_PORT': '8087',
        'HTTP_HOST': '127.0.0.1:8087',
        'wsgi.multithread': True,
        'HTTP_ACCEPT':
            'application/xml,application/xhtml+xml,text/html;q=0.9,'
            'text/plain;q=0.8,image/png,*/*;q=0.5',
        'wsgi.version': (1, 0),
        'wsgi.run_once': False,
        'wsgi.multiprocess': False,
        'HTTP_ACCEPT_LANGUAGE': 'en-us',
        'HTTP_ACCEPT_ENCODING': 'gzip, deflate'}

trans_name_policy = NameIDPolicy(format=NAMEID_FORMAT_TRANSIENT,
                                 allow_create="true")

AUTHN = {
    "class_ref": INTERNETPROTOCOLPASSWORD,
    "authn_auth": "http://www.example.com/login"
}


class TestSP():
    def setup_class(self):
        self.sp = make_plugin("rem", saml_conf="server_conf")
        self.server = Server(config_file="idp_conf")

    def teardown_class(self):
        self.server.close()

    def test_setup(self):
        assert self.sp

    def test_identify(self):
        # Create a SAMLResponse
        ava = {"givenName": ["Derek"], "surName": ["Jeter"],
               "mail": ["derek@nyy.mlb.com"], "title": ["The man"]}

        resp_str = "%s" % self.server.create_authn_response(
            ava, "id1", "http://lingon.catalogix.se:8087/",
            "urn:mace:example.com:saml:roland:sp", trans_name_policy,
            "foba0001@example.com", authn=AUTHN)

        resp_str = base64.encodestring(resp_str.encode('utf-8'))
        self.sp.outstanding_queries = {"id1": "http://www.example.com/service"}
        session_info = self.sp._eval_authn_response(
            {}, {"SAMLResponse": [resp_str]})

        assert len(session_info) > 1
        assert session_info["came_from"] == 'http://www.example.com/service'
        assert session_info["ava"] == {'givenName': ['Derek'],
                                       'mail': ['derek@nyy.mlb.com'],
                                       'sn': ['Jeter'],
                                       'title': ['The man']}


if __name__ == "__main__":
    _sp = TestSP()
    _sp.setup_class()
    _sp.test_identify()
