#!/usr/bin/env python
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_URI
from saml2.saml import NAME_FORMAT_URI
from saml2.saml import NAMEID_FORMAT_PERSISTENT
from saml2.saml import NAMEID_FORMAT_TRANSIENT


try:
    from saml2.sigver import get_xmlsec_binary
except ImportError:
    get_xmlsec_binary = None

if get_xmlsec_binary:
    xmlsec_path = get_xmlsec_binary(["/opt/local/bin"])
else:
    xmlsec_path = "/usr/bin/xmlsec1"

# BASE = "http://lingon.ladok.umu.se:8088"
# BASE = "http://lingon.catalogix.se:8088"
BASE = "http://localhost:8088"

CONFIG = {
    "entityid": f"{BASE}/idp.xml",
    "description": "My IDP",
    "service": {
        "idp": {
            "name": "Rolands IdP",
            "endpoints": {
                "single_sign_on_service": [
                    (f"{BASE}/sso/redirect", BINDING_HTTP_REDIRECT),
                    (f"{BASE}/sso/post", BINDING_HTTP_POST),
                ],
                "single_logout_service": [
                    (f"{BASE}/slo/post", BINDING_HTTP_POST),
                    (f"{BASE}/slo/redirect", BINDING_HTTP_REDIRECT),
                ],
                "assertion_id_request_service": [(f"{BASE}/airs", BINDING_URI)],
                "manage_name_id_service": [
                    (f"{BASE}/mni/post", BINDING_HTTP_POST),
                    (f"{BASE}/mni/redirect", BINDING_HTTP_REDIRECT),
                ],
            },
            "policy": {
                "default": {
                    "lifetime": {"minutes": 15},
                    "attribute_restrictions": None,  # means all I have
                    "name_form": NAME_FORMAT_URI,
                },
            },
            "subject_data": ("dict", None),
            "name_id_format": [NAMEID_FORMAT_TRANSIENT, NAMEID_FORMAT_PERSISTENT],
        },
    },
    "debug": 1,
    "key_file": "../keys/mykey.pem",
    "cert_file": "../keys/mycert.pem",
    "metadata": {},
    "organization": {
        "display_name": "Rolands Identiteter",
        "name": "Rolands Identiteter",
        "url": "http://www.example.com",
    },
    "contact_person": [
        {
            "contact_type": "technical",
            "given_name": "Roland",
            "sur_name": "Hedberg",
            "email_address": "technical@example.com",
        },
        {"contact_type": "support", "given_name": "Support", "email_address": "support@example.com"},
    ],
    # This database holds the map between a subjects local identifier and
    # the identifier returned to a SP
    "xmlsec_binary": xmlsec_path,
    "attribute_map_dir": "./attributemaps",
    "logger": {
        "rotating": {
            "filename": "idp.log",
            "maxBytes": 500000,
            "backupCount": 5,
        },
        "loglevel": "debug",
    },
}
