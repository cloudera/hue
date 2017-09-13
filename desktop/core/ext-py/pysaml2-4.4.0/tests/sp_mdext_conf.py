from pathutils import full_path, xmlsec_path

CONFIG = {
    "entityid": "urn:mace:example.com:saml:roland:sp",
    "name": "urn:mace:example.com:saml:roland:sp",
    "description": "My own SP",
    "service": {
        "sp": {
            "endpoints": {
                "assertion_consumer_service": [
                    "http://lingon.catalogix.se:8087/"],
            },
            "required_attributes": ["surName", "givenName", "mail"],
            "optional_attributes": ["title"],
            "idp": ["urn:mace:example.com:saml:roland:idp"],
            "extensions": {
                "mdui": {
                    "UIInfo": {
                        "display_name": {"text": "NORDUnet", "lang": "en"},
                        "description": {
                            "text": "The NORDUnet A/S Identity Provider ..",
                            "lang": "en"},
                        "logo": {
                            "text": "https://www.nordu"
                                    ".net/resources/NORDUnet2.jpg",
                            "lang": "en", "height": 46, "width": 203}
                    },
                    "DiscoHints": {
                        "domain_hint": {"text": "nordu.net"}
                    }
                },
                "shibmd": {
                    "Scope": {"regexp": "false", "text": "nordu.net"}
                },
            }
        }
    },
    "debug": 1,
    "key_file": full_path("test.key"),
    "cert_file": full_path("test.pem"),
    "xmlsec_binary": xmlsec_path,
    "metadata": {
        "local": [full_path("idp_2.xml")],
    },
    "virtual_organization": {
        "urn:mace:example.com:it:tek": {
            "nameid_format": "urn:oid:1.3.6.1.4.1.1466.115.121.1.15-NameID",
            "common_identifier": "umuselin",
        }
    },
    "subject_data": full_path("subject_data.db"),
    "accepted_time_diff": 60,
    "attribute_map_dir": full_path("attributemaps"),
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
            "contact_type": "technical"
        },
    ],
    "secret": "0123456789",
    "only_use_keys_in_metadata": True,
}
