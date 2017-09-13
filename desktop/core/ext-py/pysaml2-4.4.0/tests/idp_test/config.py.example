from saml2 import BINDING_PAOS
from saml2 import BINDING_SOAP
from saml2 import BINDING_HTTP_ARTIFACT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2.sigver import get_xmlsec_binary
from saml2.extension.idpdisc import BINDING_DISCO
try:
    XMLSEC_BINARY = get_xmlsec_binary(["/opt/local/bin"])
except Exception:
    XMLSEC_BINARY = ""

BASE = "http://lingon.ladok.umu.se:8087"
#BASE = "http://localhost:8087"

CONFIG = {
    "entityid" : "%s/sp.xml" % BASE,
    "name" : "SAML2 test tool",
    "description": "Simplest possible",
    "service": {
        "sp": {
            "endpoints":{
                "assertion_consumer_service": [
                    ("%s/acs/post" % BASE, BINDING_HTTP_POST),
                    ("%s/acs/redirect" % BASE, BINDING_HTTP_REDIRECT),
                    ("%s/acs/artifact" % BASE, BINDING_HTTP_ARTIFACT),
                    #("%s/acs/soap" % BASE, BINDING_SOAP),
                    ("%s/ecp" % BASE, BINDING_PAOS)
                ],
                "single_logout_service": [
                    ("%s/sls" % BASE, BINDING_SOAP)
                ],
                "artifact_resolution_service":[
                    ("%s/ars" % BASE, BINDING_SOAP)
                ],
                "manage_name_id_service":[
                    ("%s/mni" % BASE, BINDING_HTTP_POST),
                    ("%s/mni" % BASE, BINDING_HTTP_REDIRECT),
                    ("%s/mni" % BASE, BINDING_SOAP),
                    ("%s/acs/artifact" % BASE, BINDING_HTTP_ARTIFACT)
                ],
                "discovery_response":[
                    ("%s/disco" % BASE, BINDING_DISCO)
                ]
            }
        }
    },
    "key_file" : "keys/mykey.pem",
    "cert_file" : "keys/mycert.pem",
    "xmlsec_binary" : XMLSEC_BINARY,
    "subject_data": "subject_data.db",
    "accepted_time_diff": 60,
    "attribute_map_dir" : "attributemaps",
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
    "secret": "0123456789",
    "only_use_keys_in_metadata": False
}

