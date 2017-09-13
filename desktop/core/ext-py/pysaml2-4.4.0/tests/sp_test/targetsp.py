#!/usr/bin/env python
from saml2.saml import AUTHN_PASSWORD

__author__ = 'rolandh'

import json

BASE = "http://localhost:8087"
#BASE= "http://lingon.catalogix.se:8087"

metadata = open("./sp/sp.xml").read()

AUTHN = {"class_ref": AUTHN_PASSWORD,
         "authn_auth": "http://lingon.catalogix.se/login"}

info = {
    "start_page": BASE,
    "entity_id": "%s/sp.xml" % BASE,
    "result": {
        "matches": {
            "content": "<h2>Your identity are"
        },
    },
    "metadata": metadata,
    "args":
        {
            "AuthnResponse": {
                "sign_assertion": "always", # always, never
                "sign_response": "never", # always, never
                "sign_digest_alg": ds.DIGEST_SHA256,
                "sign_signature_alg": ds.SIG_RSA_SHA256,
                "authn": AUTHN
            }
        },
    # This is the set of attributes and values that are returned in the
    # SAML Assertion
    "identity": {
        "given_name": "Roland",
        "sn": "Hedberg"
    },
    # This is the value of the NameID that is return in the Subject in the
    # Assertion
    "userid": "roland",
    # regex pattern that must be contained in the resulting echo page to validate
    # that the SP returned the right page after Login.
    "echopageIdPattern": r"<title>SAML Echo Service</title>",
    # list of regex patterns that must be contained in the resulting echo page to validate
    # that the SP's echo page returns expected SAMLe response values (e.g. attribute values)
    "echopageContentPattern": [r"Given Name\s*</td>\s*<td>Roland</td>",
                               r"Userid\s*</td>\s*<td>roalnd</td>",
                               r"Surname\s*</td>\s*<td>Hedberg</td>",
                              ],
    "constraints": {
        "authnRequest_signature_required": True,
        # allowed for assertion & response signature:
        "signature_algorithm": [
            #ds.SIG_RSA_SHA1,  # you may need this for legacy deployments
            ds.SIG_RSA_SHA224,
            ds.SIG_RSA_SHA256,
            ds.SIG_RSA_SHA384,
            ds.SIG_RSA_SHA512,
        ],
        "digest_algorithm": [
            #ds.DIGEST_SHA1,   # you may need this for legacy deployments
            ds.DIGEST_SHA1,
            ds.DIGEST_SHA224,
            ds.DIGEST_SHA256,
            ds.DIGEST_SHA384,
            ds.DIGEST_SHA512,
            ds.DIGEST_RIPEMD160,
        ],
    },
}

print(json.dumps(info))