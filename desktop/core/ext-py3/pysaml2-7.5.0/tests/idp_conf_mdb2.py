#!/usr/bin/env python
from pathutils import full_path

from saml2 import BINDING_HTTP_ARTIFACT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_SOAP
from saml2 import BINDING_URI
from saml2.saml import NAME_FORMAT_URI
from saml2.saml import NAMEID_FORMAT_PERSISTENT


BASE = "http://localhost:8089"

CONFIG = {
    "entityid": f"{BASE}/saml/idp2",
    "name": "Rolands 2nd IdP",
    "service": {
        "aa": {
            "endpoints": {"attribute_service": [(f"{BASE}/aap", BINDING_HTTP_POST), (f"{BASE}/aas", BINDING_SOAP)]},
        },
        "aq": {
            "endpoints": {"authn_query_service": [(f"{BASE}/aqs", BINDING_SOAP)]},
        },
        "idp": {
            "endpoints": {
                "single_sign_on_service": [
                    (f"{BASE}/sso/redirect", BINDING_HTTP_REDIRECT),
                    (f"{BASE}/sso/post", BINDING_HTTP_POST),
                    (f"{BASE}/sso/art", BINDING_HTTP_ARTIFACT),
                    (f"{BASE}/sso/paos", BINDING_SOAP),
                ],
                "single_logout_service": [
                    (f"{BASE}/slo/soap", BINDING_SOAP),
                    (f"{BASE}/slo/post", BINDING_HTTP_POST),
                ],
                "artifact_resolution_service": [(f"{BASE}/ars", BINDING_SOAP)],
                "assertion_id_request_service": [(f"{BASE}/airs", BINDING_URI)],
                "authn_query_service": [(f"{BASE}/aqs", BINDING_SOAP)],
                "manage_name_id_service": [
                    (f"{BASE}/mni/soap", BINDING_SOAP),
                    (f"{BASE}/mni/post", BINDING_HTTP_POST),
                    (f"{BASE}/mni/redirect", BINDING_HTTP_REDIRECT),
                    (f"{BASE}/mni/art", BINDING_HTTP_ARTIFACT),
                ],
                "name_id_mapping_service": [
                    (f"{BASE}/nim/soap", BINDING_SOAP),
                    (f"{BASE}/nim/post", BINDING_HTTP_POST),
                    (f"{BASE}/nim/redirect", BINDING_HTTP_REDIRECT),
                    (f"{BASE}/nim/art", BINDING_HTTP_ARTIFACT),
                ],
            },
            "policy": {
                "default": {
                    "lifetime": {"minutes": 15},
                    "attribute_restrictions": None,  # means all I have
                    "name_form": NAME_FORMAT_URI,
                },
                "urn:mace:example.com:saml:roland:sp": {
                    "lifetime": {"minutes": 5},
                    "nameid_format": NAMEID_FORMAT_PERSISTENT,
                    # "attribute_restrictions":{
                    #     "givenName": None,
                    #     "surName": None,
                    # }
                },
            },
            "subject_data": ("mongodb", "subject"),
            "session_storage": ("mongodb", "session"),
        },
    },
    "debug": 1,
    "key_file": full_path("test.key"),
    "cert_file": full_path("test.pem"),
    "xmlsec_binary": None,
    "metadata": {
        "local": [full_path("servera.xml"), full_path("vo_metadata.xml")],
    },
    "attribute_map_dir": full_path("attributemaps"),
    "organization": {
        "name": "Exempel AB",
        "display_name": [("Exempel ÄB", "se"), ("Example Co.", "en")],
        "url": "http://www.example.com/roland",
    },
    "contact_person": [
        {
            "given_name": "John",
            "sur_name": "Smith",
            "email_address": ["john.smith@example.com"],
            "contact_type": "technical",
        },
    ],
}
