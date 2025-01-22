from pathutils import full_path
from pathutils import xmlsec_path

from saml2 import BINDING_HTTP_ARTIFACT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_PAOS
from saml2 import BINDING_SOAP
from saml2.authn_context import PASSWORDPROTECTEDTRANSPORT as AUTHN_PASSWORD_PROTECTED
from saml2.authn_context import TIMESYNCTOKEN as AUTHN_TIME_SYNC_TOKEN
from saml2.extension.idpdisc import BINDING_DISCO
from saml2.saml import NAMEID_FORMAT_PERSISTENT
from saml2.saml import NAMEID_FORMAT_TRANSIENT


BASE = "http://lingon.catalogix.se:8087"

CONFIG = {
    "entityid": "urn:mace:example.com:saml:roland:sp",
    "name": "urn:mace:example.com:saml:roland:sp",
    "description": "My own SP",
    "service": {
        "sp": {
            "endpoints": {
                "assertion_consumer_service": [
                    (f"{BASE}/", BINDING_HTTP_POST),
                    (f"{BASE}/paos", BINDING_PAOS),
                    (f"{BASE}/redirect", BINDING_HTTP_REDIRECT),
                ],
                "artifact_resolution_service": [(f"{BASE}/ars", BINDING_SOAP)],
                "manage_name_id_service": [
                    (f"{BASE}/mni/soap", BINDING_SOAP),
                    (f"{BASE}/mni/post", BINDING_HTTP_POST),
                    (f"{BASE}/mni/redirect", BINDING_HTTP_REDIRECT),
                    (f"{BASE}/mni/art", BINDING_HTTP_ARTIFACT),
                ],
                "single_logout_service": [(f"{BASE}/sls", BINDING_SOAP)],
                "discovery_response": [(f"{BASE}/disco", BINDING_DISCO)],
            },
            "required_attributes": ["surName", "givenName", "mail"],
            "optional_attributes": ["title", "eduPersonAffiliation"],
            "idp": ["urn:mace:example.com:saml:roland:idp"],
            "name_id_format": [
                NAMEID_FORMAT_TRANSIENT,
                NAMEID_FORMAT_PERSISTENT,
            ],
            "requested_authn_context": {
                "authn_context_class_ref": [
                    AUTHN_PASSWORD_PROTECTED,
                    AUTHN_TIME_SYNC_TOKEN,
                ],
                "comparison": "exact",
            },
        }
    },
    "debug": 1,
    "key_file": full_path("test.key"),
    "cert_file": full_path("test.pem"),
    "ca_certs": full_path("cacerts.txt"),
    "xmlsec_binary": xmlsec_path,
    "metadata": [
        {
            "class": "saml2.mdstore.MetaDataFile",
            "metadata": [(full_path("idp_all.xml"),), (full_path("vo_metadata.xml"),)],
        }
    ],
    "virtual_organization": {
        "urn:mace:example.com:it:tek": {
            "nameid_format": "urn:oid:1.3.6.1.4.1.1466.115.121.1.15-NameID",
            "common_identifier": "umuselin",
        }
    },
    "subject_data": "subject_data.db",
    "accepted_time_diff": 60,
    "attribute_map_dir": full_path("attributemaps"),
    "entity_category": [
        "http://www.swamid.se/category/sfs-1993-1153",
        # "http://www.swamid.se/category/research-and-education",
        "http://www.swamid.se/category/hei-service",
    ],
    # "valid_for": 6,
    "organization": {
        "name": ("AB Exempel", "se"),
        "display_name": ("AB Exempel", "se"),
        "url": "http://www.example.org",
    },
    "contact_person": [
        {
            "given_name": "Roland",
            "sur_name": "Hedberg",
            "telephone_number": "+46 70 100 0000",
            "email_address": ["tech@eample.com", "tech@example.org"],
            "contact_type": "technical",
        },
    ],
    "logger": {
        "rotating": {
            "filename": "sp.log",
            "maxBytes": 500000,
            "backupCount": 5,
        },
        "loglevel": "info",
    },
}
