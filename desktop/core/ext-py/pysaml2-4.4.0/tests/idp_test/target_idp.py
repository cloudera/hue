#!/usr/bin/env python
from saml2.saml import NAME_FORMAT_URI

__author__ = 'rolandh'

import json
from saml2 import xmldsig as ds
from saml2.saml import NAME_FORMAT_UNSPECIFIED, NAME_FORMAT_URI, NAME_FORMAT_BASIC

BASE = "http://localhost:8088"

metadata = open("./idp/idp.xml").read()

info = {
    "entity_id": "%s/idp.xml" % BASE,
    "interaction": [
        {
            "matches": {
                "url": "%s/sso/redirect" % BASE,
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
                "url": "%s/sso/post" % BASE,
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
    # metadata source for the test target's EntityDescriptor:
    "metadata": metadata,
    "constraints": {
        # test if attribute name format matches the given value. Absence of this
        # option or the value NAME_FORMAT_UNSPECIFIED will match any format
        #"name_format": NAME_FORMAT_BASIC,
        #"name_format": NAME_FORMAT_UNSPECIFIED,
        "name_format": NAME_FORMAT_URI,
        # allowed for assertion & response:
        "signature_algorithm": [
            #ds.SIG_RSA_SHA1,  # you may need this for legacy deployments
            ds.SIG_RSA_SHA224,
            ds.SIG_RSA_SHA256,
            ds.SIG_RSA_SHA384,
            ds.SIG_RSA_SHA512,
        ],
        "digest_algorithm": [
            #ds.DIGEST_SHA1,   # you may need this for legacy deployments
            ds.DIGEST_SHA224,
            ds.DIGEST_SHA256,
            ds.DIGEST_SHA384,
            ds.DIGEST_SHA512,
            ds.DIGEST_RIPEMD160,
        ],
    }
}

print(json.dumps(info))