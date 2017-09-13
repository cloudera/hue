#!/usr/bin/env python
from saml2.saml import NAME_FORMAT_URI

__author__ = 'rolandh'

import json

BASE = "http://localhost:8088"

metadata = open("idp_test/idp.xml").read()

info = {
    "entity_id": "%s/idp.xml" % BASE,
    "interaction": [
        {
            "matches": {
                "url": "%s/login" % BASE,
                "title": 'IDP test login'
            },
            "page-type": "login",
            "control": {
                "type": "form",
                "set": {"login": "roland", "password": "dianakra"}
            }
        },
        {
            "matches": {
                "url": "%s/sso/redirect" % BASE,
                "title": "SAML 2.0 POST"
            },
            "page-type": "other",
            "control": {
                "index": 0,
                "type": "form",
                "set": {}
            }
        },
        {
            "matches": {
                "url": "%s/sso/post" % BASE,
                "title": "SAML 2.0 POST"
            },
            "page-type": "other",
            "control": {
                "index": 0,
                "type": "form",
                "set": {}
            }
        },
        {
            "matches": {
                "url": "%s/slo/post" % BASE,
                "title": "SAML 2.0 POST"
            },
            "page-type": "other",
            "control": {
                "index": 0,
                "type": "form",
                "set": {}
            }
        }
    ],
    "metadata": metadata,
    "name_format": NAME_FORMAT_URI
}

print(json.dumps(info))
