from saml2.extension.idpdisc import BINDING_DISCO
from saml2 import BINDING_SOAP
from saml2 import BINDING_PAOS
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_HTTP_ARTIFACT
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.saml import NAMEID_FORMAT_PERSISTENT

from pathutils import full_path
from pathutils import xmlsec_path

BASE = "http://lingon.catalogix.se:8087"

CONFIG = {
    "entityid": "urn:mace:example.com:saml:roland:sp",
    "name": "urn:mace:example.com:saml:roland:sp",
    "description": "My own SP",
    "service": {
        "sp": {
            "endpoints": {
                "assertion_consumer_service": [
                    ("%s/" % BASE, BINDING_HTTP_POST),
                    ("%s/paos" % BASE, BINDING_PAOS),
                    ("%s/redirect" % BASE, BINDING_HTTP_REDIRECT)],
                "artifact_resolution_service": [
                    ("%s/ars" % BASE, BINDING_SOAP)
                ],
                "manage_name_id_service": [
                    ("%s/mni/soap" % BASE, BINDING_SOAP),
                    ("%s/mni/post" % BASE, BINDING_HTTP_POST),
                    ("%s/mni/redirect" % BASE, BINDING_HTTP_REDIRECT),
                    ("%s/mni/art" % BASE, BINDING_HTTP_ARTIFACT)
                ],
                "single_logout_service": [
                    ("%s/sls" % BASE, BINDING_SOAP)
                ],
                "discovery_response": [
                    ("%s/disco" % BASE, BINDING_DISCO)
                ]
            },
            "required_attributes": ["surName", "givenName", "mail"],
            "optional_attributes": ["title", "eduPersonAffiliation"],
            "idp": ["urn:mace:example.com:saml:roland:idp"],
            "name_id_format": [NAMEID_FORMAT_TRANSIENT,
                               NAMEID_FORMAT_PERSISTENT]
        }
    },
    "debug": 1,
    "key_file": full_path("test.key"),
    "cert_file": full_path("test.pem"),
    "ca_certs": full_path("cacerts.txt"),
    "xmlsec_binary": xmlsec_path,
    "metadata": [{
        "class": "saml2.mdstore.MetaDataFile",
        "metadata": [(full_path("idp_all.xml"), ), (full_path("vo_metadata.xml"), )],
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
    "entity_category": ["http://www.swamid.se/category/sfs-1993-1153",
                        #"http://www.swamid.se/category/research-and-education",
                        "http://www.swamid.se/category/hei-service"],
    #"valid_for": 6,
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
    "logger": {
        "rotating": {
            "filename": "sp.log",
            "maxBytes": 500000,
            "backupCount": 5,
        },
        "loglevel": "info",
    }
}
