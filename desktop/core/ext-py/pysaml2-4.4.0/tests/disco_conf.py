from saml2.extension.idpdisc import BINDING_DISCO

from pathutils import full_path
from pathutils import xmlsec_path

BASE = "http://localhost:8088"

CONFIG = {
    "entityid": "%s/disco.xml" % BASE,
    "name": "Rolands Discoserver",
    "service": {
        "ds": {
            "endpoints": {
                "disco_service": [
                    ("%s/disco" % BASE, BINDING_DISCO),
                ]
            },
        },
    },
    "debug": 1,
    "xmlsec_binary": xmlsec_path,
    "metadata": [{
        "class": "saml2.mdstore.MetaDataFile",
        "metadata": [(full_path("servera.xml"), )],
    }],
}
