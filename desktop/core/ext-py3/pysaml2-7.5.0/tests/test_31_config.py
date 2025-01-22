#!/usr/bin/env python


from pathutils import dotname
from pathutils import full_path

from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_SOAP
from saml2.authn_context import PASSWORDPROTECTEDTRANSPORT as AUTHN_PASSWORD_PROTECTED
from saml2.authn_context import TIMESYNCTOKEN as AUTHN_TIME_SYNC_TOKEN
from saml2.config import Config
from saml2.config import IdPConfig
from saml2.config import SPConfig
from saml2.mdstore import MetadataStore
from saml2.mdstore import name
from saml2.sigver import CryptoBackendXMLSecurity
from saml2.sigver import security_context


sp1 = {
    "entityid": "urn:mace:umu.se:saml:roland:sp",
    "service": {
        "sp": {
            "endpoints": {
                "assertion_consumer_service": ["http://lingon.catalogix.se:8087/"],
            },
            "name": "test",
            "idp": {
                "urn:mace:example.com:saml:roland:idp": {
                    "single_sign_on_service": {
                        "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect": "http://localhost:8088/sso/"
                    }
                },
            },
            "requested_authn_context": {
                "authn_context_class_ref": [
                    AUTHN_PASSWORD_PROTECTED,
                    AUTHN_TIME_SYNC_TOKEN,
                ],
                "comparison": "exact",
            },
        }
    },
    "key_file": full_path("test.key"),
    "cert_file": full_path("test.pem"),
    "metadata": [
        {
            "class": "saml2.mdstore.MetaDataFile",
            "metadata": [(full_path("metadata.xml"),), (full_path("urn-mace-swami.se-swamid-test-1.0-metadata.xml"),)],
        }
    ],
    "virtual_organization": {
        "coip": {
            "nameid_format": "urn:oasis:names:tc:SAML:2.0:nameid-format:transient",
            "common_identifier": "eduPersonPrincipalName",
            "attribute_auth": [
                "https://coip-test.sunet.se/idp/shibboleth",
            ],
        }
    },
    "attribute_map_dir": full_path("attributemaps"),
    "only_use_keys_in_metadata": True,
    "xmlsec_path": ["/opt/local/bin"],
}

sp2 = {
    "entityid": "urn:mace:umu.se:saml:roland:sp",
    "name": "Rolands SP",
    "service": {
        "sp": {
            "endpoints": {
                "assertion_consumer_service": ["http://lingon.catalogix.se:8087/"],
            },
            "required_attributes": ["surName", "givenName", "mail"],
            "optional_attributes": ["title"],
            "idp": {
                "": "https://example.com/saml2/idp/SSOService.php",
            },
            "authn_requests_signed": True,
            "logout_requests_signed": True,
            "force_authn": True,
        }
    },
    # "xmlsec_binary" : "/opt/local/bin/xmlsec1",
}

IDP1 = {
    "entityid": "urn:mace:umu.se:saml:roland:idp",
    "name": "Rolands IdP",
    "service": {
        "idp": {
            "endpoints": {
                "single_sign_on_service": ["http://localhost:8088/"],
            },
            "policy": {
                "default": {
                    "attribute_restrictions": {
                        "givenName": None,
                        "surName": None,
                        "eduPersonAffiliation": ["(member|staff)"],
                        "mail": [".*@example.com"],
                    }
                },
                "urn:mace:umu.se:saml:roland:sp": None,
            },
            "error_url": "http://localhost:8080/error",
        }
    },
    # "xmlsec_binary" : "/usr/local/bin/xmlsec1",
}

IDP2 = {
    "entityid": "urn:mace:umu.se:saml:roland:idp",
    "name": "Rolands IdP",
    "service": {
        "idp": {
            "endpoints": {
                "single_sign_on_service": ["http://localhost:8088/"],
                "single_logout_service": [("http://localhost:8088/", BINDING_HTTP_REDIRECT)],
            },
            "policy": {
                "default": {
                    "attribute_restrictions": {
                        "givenName": None,
                        "surName": None,
                        "eduPersonAffiliation": ["(member|staff)"],
                        "mail": [".*@example.com"],
                    }
                },
                "urn:mace:umu.se:saml:roland:sp": None,
            },
        }
    },
    # "xmlsec_binary" : "/usr/local/bin/xmlsec1",
}

PDP = {
    "entityid": "http://example.org/pysaml2/pdp",
    "name": "Rolands PdP",
    "service": {
        "pdp": {
            "endpoints": {
                "authz_service": [("http://example.org/pysaml2/pdp/authz", BINDING_SOAP)],
            },
        }
    },
    "key_file": full_path("test.key"),
    "cert_file": full_path("test.pem"),
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

ECP_SP = {
    "entityid": "urn:mace:umu.se:saml:roland:ecpsp",
    "name": "Rolands ECP_SP",
    "service": {
        "sp": {
            "endpoints": {
                "assertion_consumer_service": ["http://lingon.catalogix.se:8087/"],
            },
            "ecp": {
                "130.239.": "http://example.com/idp",
            },
        }
    },
    # "xmlsec_binary" : "/opt/local/bin/xmlsec1",
}

IDP_XMLSECURITY = {
    "entityid": "urn:mace:umu.se:saml:roland:idp",
    "name": "Rolands IdP",
    "service": {
        "idp": {
            "endpoints": {
                "single_sign_on_service": ["http://localhost:8088/"],
                "single_logout_service": [("http://localhost:8088/", BINDING_HTTP_REDIRECT)],
            },
            "policy": {
                "default": {
                    "attribute_restrictions": {
                        "givenName": None,
                        "surName": None,
                        "eduPersonAffiliation": ["(member|staff)"],
                        "mail": [".*@example.com"],
                    }
                },
                "urn:mace:umu.se:saml:roland:sp": None,
            },
        }
    },
    "key_file": "pkcs11:///usr/lunasa/lib/libCryptoki2_64.so:1/eduID dev SAML signing key?pin=123456",
    "crypto_backend": "XMLSecurity",
}


def _eq(l1, l2):
    return set(l1) == set(l2)


def test_1():
    c = SPConfig().load(sp1)
    c.context = "sp"
    print(c)
    assert c._sp_endpoints
    assert c._sp_name
    assert c._sp_idp
    md = c.metadata
    assert isinstance(md, MetadataStore)

    assert len(c._sp_idp) == 1
    assert list(c._sp_idp.keys()) == ["urn:mace:example.com:saml:roland:idp"]
    assert list(c._sp_idp.values()) == [
        {
            "single_sign_on_service": {
                "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect": ("http://localhost:8088/sso/")
            }
        }
    ]

    assert c.only_use_keys_in_metadata
    assert type(c.getattr("requested_authn_context")) is dict
    assert c.getattr("requested_authn_context").get("authn_context_class_ref") == [
        AUTHN_PASSWORD_PROTECTED,
        AUTHN_TIME_SYNC_TOKEN,
    ]
    assert c.getattr("requested_authn_context").get("comparison") == "exact"


def test_2():
    c = SPConfig().load(sp2)
    c.context = "sp"

    print(c)
    assert c._sp_endpoints
    assert c.getattr("endpoints", "sp")
    assert c._sp_idp
    assert c._sp_optional_attributes
    assert c.name
    assert c._sp_required_attributes

    assert len(c._sp_idp) == 1
    assert list(c._sp_idp.keys()) == [""]
    assert list(c._sp_idp.values()) == ["https://example.com/saml2/idp/SSOService.php"]
    assert c.only_use_keys_in_metadata is True


def test_minimum():
    minimum = {
        "entityid": "urn:mace:example.com:saml:roland:sp",
        "service": {
            "sp": {
                "endpoints": {
                    "assertion_consumer_service": ["http://sp.example.org/"],
                },
                "name": "test",
                "idp": {
                    "": "https://example.com/idp/SSOService.php",
                },
            }
        },
        # "xmlsec_binary" : "/usr/local/bin/xmlsec1",
    }

    c = SPConfig().load(minimum)
    c.context = "sp"

    assert c is not None


def test_idp_1():
    c = IdPConfig().load(IDP1)
    c.context = "idp"

    print(c)
    assert c.endpoint("single_sign_on_service")[0] == "http://localhost:8088/"

    attribute_restrictions = c.getattr("policy", "idp").get_attribute_restrictions("")
    assert attribute_restrictions["edupersonaffiliation"][0].match("staff")

    error_url = c.getattr("error_url", "idp")
    assert error_url == "http://localhost:8080/error"


def test_idp_2():
    c = IdPConfig().load(IDP2)
    c.context = "idp"

    print(c)
    assert c.endpoint("single_logout_service", BINDING_SOAP) == []
    assert c.endpoint("single_logout_service", BINDING_HTTP_REDIRECT) == ["http://localhost:8088/"]

    attribute_restrictions = c.getattr("policy", "idp").get_attribute_restrictions("")
    assert attribute_restrictions["edupersonaffiliation"][0].match("staff")


def test_wayf():
    c = SPConfig().load_file("server_conf")
    c.context = "sp"

    idps = c.metadata.with_descriptor("idpsso")
    ent = list(idps.values())[0]
    assert name(ent) == "Example Co."
    assert name(ent, "se") == "Exempel AB"


def test_conf_syslog():
    c = SPConfig().load_file("server_conf_syslog")
    c.context = "sp"


def test_3():
    cnf = Config()
    cnf.load_file(dotname("sp_1_conf"))
    assert cnf.entityid == "urn:mace:example.com:saml:roland:sp"
    assert cnf.debug == 1
    assert cnf.key_file == full_path("test.key")
    assert cnf.cert_file == full_path("test.pem")
    # assert cnf.xmlsec_binary ==  "/usr/local/bin/xmlsec1"
    assert cnf.accepted_time_diff == 60
    assert cnf.secret == "0123456789"
    assert cnf.metadata is not None
    assert cnf.attribute_converters is not None
    assert cnf.http_client_timeout == 10


def test_sp():
    cnf = SPConfig()
    cnf.load_file(dotname("sp_1_conf"))
    assert cnf.endpoint("assertion_consumer_service") == ["http://lingon.catalogix.se:8087/"]


def test_dual():
    cnf = Config().load_file(dotname("idp_sp_conf"))

    spe = cnf.getattr("endpoints", "sp")
    idpe = cnf.getattr("endpoints", "idp")
    assert spe
    assert idpe
    assert spe != idpe


def test_ecp():
    cnf = SPConfig()
    cnf.load(ECP_SP)
    assert cnf.endpoint("assertion_consumer_service") == ["http://lingon.catalogix.se:8087/"]
    eid = cnf.ecp_endpoint("130.239.16.3")
    assert eid == "http://example.com/idp"
    eid = cnf.ecp_endpoint("130.238.20.20")
    assert eid is None


def test_assertion_consumer_service():
    c = IdPConfig()
    c.load_file(dotname("idp_conf"))
    c.context = "idp"

    c.metadata.load("local", full_path("InCommon-metadata.xml"))

    entity_id = "https://www.zimride.com/shibboleth"
    acs = c.metadata.assertion_consumer_service(entity_id)
    assert len(acs) == 1
    assert acs[0]["location"] == "https://www.zimride.com/Shibboleth.sso/SAML2/POST"


def test_crypto_backend():
    idpc = IdPConfig()
    idpc.load(IDP_XMLSECURITY)

    assert idpc.crypto_backend == "XMLSecurity"
    sec = security_context(idpc)
    assert isinstance(sec.crypto, CryptoBackendXMLSecurity)


def test_unset_force_authn():
    cnf = SPConfig().load(sp1)
    assert bool(cnf.getattr("force_authn", "sp")) == False


def test_set_force_authn():
    cnf = SPConfig().load(sp2)
    assert bool(cnf.getattr("force_authn", "sp")) == True


if __name__ == "__main__":
    test_crypto_backend()
