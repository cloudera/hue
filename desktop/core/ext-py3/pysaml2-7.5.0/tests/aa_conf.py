from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_SOAP
from saml2 import NAME_FORMAT_URI


BASE = "http://localhost:8089/"

from pathutils import full_path


CONFIG = {
    "service": {
        "aa": {
            "endpoints": {
                "attribute_service": [(f"{BASE}as", BINDING_HTTP_REDIRECT)],
                "single_logout_service": [(f"{BASE}slo", BINDING_SOAP)],
            },
            "release_policy": {
                "default": {
                    "lifetime": {"minutes": 15},
                    "attribute_restrictions": None,  # means all I have
                    "name_form": NAME_FORMAT_URI,
                },
            },
            "subject_data": full_path("aa.db"),
        }
    },
    "entityid": f"{BASE}aa",
    "name": "Rolands AA",
    "debug": 1,
    "key_file": full_path("test.key"),
    "cert_file": full_path("test.pem"),
    # "xmlsec_binary" : None,
    "metadata": {
        "local": [full_path("metadata.xml"), full_path("vo_metadata.xml")],
    },
    "attribute_map_dir": full_path("attributemaps"),
    "organization": {
        "name": "Exempel AB",
        "display_name": [("Exempel AB", "se"), ("Example Co.", "en")],
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
