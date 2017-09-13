#!/usr/bin/env python
# -*- coding: utf-8 -*-
from saml2 import BINDING_SOAP, BINDING_URI
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_ARTIFACT
from saml2.saml import NAMEID_FORMAT_PERSISTENT
from saml2.saml import NAME_FORMAT_URI

from pathutils import full_path

BASE = "http://localhost:8088"

CONFIG = {
    "entityid": "%s/saml/idp" % BASE,
    "name": "Rolands IdP",
    "service": {
        "aa": {
            "endpoints": {
                "attribute_service": [
                    ("%s/aap" % BASE, BINDING_HTTP_POST),
                    ("%s/aas" % BASE, BINDING_SOAP)
                ]
            },
        },
        "aq": {
            "endpoints": {
                "authn_query_service": [
                    ("%s/aqs" % BASE, BINDING_SOAP)
                ]
            },
        },
        "idp": {
            "endpoints": {
                "single_sign_on_service": [
                    ("%s/sso/redirect" % BASE, BINDING_HTTP_REDIRECT),
                    ("%s/sso/post" % BASE, BINDING_HTTP_POST),
                    ("%s/sso/art" % BASE, BINDING_HTTP_ARTIFACT),
                    ("%s/sso/paos" % BASE, BINDING_SOAP)
                ],
                "single_logout_service": [
                    ("%s/slo/soap" % BASE, BINDING_SOAP),
                    ("%s/slo/post" % BASE, BINDING_HTTP_POST)
                ],
                "artifact_resolution_service": [
                    ("%s/ars" % BASE, BINDING_SOAP)
                ],
                "assertion_id_request_service": [
                    ("%s/airs" % BASE, BINDING_URI)
                ],
                "authn_query_service": [
                    ("%s/aqs" % BASE, BINDING_SOAP)
                ],
                "manage_name_id_service": [
                    ("%s/mni/soap" % BASE, BINDING_SOAP),
                    ("%s/mni/post" % BASE, BINDING_HTTP_POST),
                    ("%s/mni/redirect" % BASE, BINDING_HTTP_REDIRECT),
                    ("%s/mni/art" % BASE, BINDING_HTTP_ARTIFACT)
                ],
                "name_id_mapping_service": [
                    ("%s/nim/soap" % BASE, BINDING_SOAP),
                    ("%s/nim/post" % BASE, BINDING_HTTP_POST),
                    ("%s/nim/redirect" % BASE, BINDING_HTTP_REDIRECT),
                    ("%s/nim/art" % BASE, BINDING_HTTP_ARTIFACT)
                ]
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
                }
            },
            "subject_data": ("mongodb", "subject"),
            "session_storage": ("mongodb", "session")
        },
    },
    "debug": 1,
    "key_file": full_path("test.key"),
    "cert_file": full_path("test.pem"),
    #"xmlsec_binary": None,
    "xmlsec_path": ["/opt/local/bin", "usr/local/bin"],
    "metadata": [{
        "class": "saml2.mdstore.MetaDataFile",
        "metadata": [(full_path("servera.xml"), ),
                  (full_path("vo_metadata.xml"), )],
    }],
    "attribute_map_dir": full_path("attributemaps"),
    "organization": {
        "name": "Exempel AB",
        "display_name": [("Exempel ÄB", "se"), ("Example Co.", "en")],
        "url": "http://www.example.com/roland",
    },
    "contact_person": [
        {
            "given_name":"John",
            "sur_name": "Smith",
            "email_address": ["john.smith@example.com"],
            "contact_type": "technical",
        },
    ],
}

