from pathutils import full_path
from pathutils import xmlsec_path

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
        }
    },
    "debug": 1,
    "key_file": full_path("test.key"),
    "cert_file": full_path("test.pem"),
    "encryption_keypairs": [{"key_file": full_path("test_1.key"), "cert_file": full_path("test_1.crt")},
                            {"key_file": full_path("test_2.key"), "cert_file": full_path("test_2.crt")}],
    "ca_certs": full_path("cacerts.txt"),
    "xmlsec_binary": xmlsec_path,
    "metadata": [{
        "class": "saml2.mdstore.MetaDataFile",
        "metadata": [(full_path("idp.xml"), ), (full_path("vo_metadata.xml"), )],
    }],
    "virtual_organization": {
        "urn:mace:example.com:it:tek": {
            "nameid_format": "urn:oid:1.3.6.1.4.1.1466.115.121.1.15-NameID",
            "common_identifier": "umuselin",
        }
    },
    "subject_data": "subject_data.db",
    "accepted_time_diff": 60,
    "attribute_map_dir": full_path("attributemaps"),
    "valid_for": 6,
    "organization": {
        "name": ("AB Exempel", "se"),
        "display_name": ("AB Exempel", "se"),
        "url": "http://www.example.org",
    },
    "contact_person": [{
                           "given_name": "Roland",
                           "sur_name": "Hedberg",
                           "telephone_number": "+46 70 100 0000",
                           "email_address": ["tech@eample.com",
                                             "tech@example.org"],
                           "contact_type": "technical"
                       },
    ],
    "logger": {
        "rotating": {
            "filename": full_path("sp.log"),
            "maxBytes": 100000,
            "backupCount": 5,
        },
        "loglevel": "info",
    }
}
