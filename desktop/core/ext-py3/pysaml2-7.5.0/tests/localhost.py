#!/usr/bin/env python
from saml2.saml import NAME_FORMAT_URI


__author__ = "rolandh"

import json


BASE = "http://localhost:8088"

metadata = open("idp_test/idp.xml").read()

info = {
    "entity_id": f"{BASE}/idp.xml",
    "interaction": [
        {
            "matches": {"url": f"{BASE}/login", "title": "IDP test login"},
            "page-type": "login",
            "control": {"type": "form", "set": {"login": "roland", "password": "dianakra"}},
        },
        {
            "matches": {"url": f"{BASE}/sso/redirect", "title": "SAML 2.0 POST"},
            "page-type": "other",
            "control": {"index": 0, "type": "form", "set": {}},
        },
        {
            "matches": {"url": f"{BASE}/sso/post", "title": "SAML 2.0 POST"},
            "page-type": "other",
            "control": {"index": 0, "type": "form", "set": {}},
        },
        {
            "matches": {"url": f"{BASE}/slo/post", "title": "SAML 2.0 POST"},
            "page-type": "other",
            "control": {"index": 0, "type": "form", "set": {}},
        },
    ],
    "metadata": metadata,
    "name_format": NAME_FORMAT_URI,
}

print(json.dumps(info))
