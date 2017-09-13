#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
from saml2.mdstore import MetadataStore, name

from saml2 import BINDING_HTTP_REDIRECT, BINDING_SOAP, BINDING_HTTP_POST
from saml2.config import SPConfig, IdPConfig, Config
from py.test import raises

from saml2 import root_logger

from pathutils import dotname, full_path
from saml2.sigver import security_context, CryptoBackendXMLSecurity

sp1 = {
    "entityid": "urn:mace:umu.se:saml:roland:sp",
    "service": {
        "sp": {
            "endpoints": {
                "assertion_consumer_service": [
                    "http://lingon.catalogix.se:8087/"],
            },
            "name": "test",
            "idp": {
                "urn:mace:example.com:saml:roland:idp": {
                    'single_sign_on_service':
                        {'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect':
                             'http://localhost:8088/sso/'}},
            }
        }
    },
    "key_file": full_path("test.key"),
    "cert_file": full_path("test.pem"),
    "metadata": [{
        "class": "saml2.mdstore.MetaDataFile",
        "metadata": [(full_path("metadata.xml"), ),
                  (full_path("urn-mace-swami.se-swamid-test-1.0-metadata.xml"), )],
    }],
    "virtual_organization": {
        "coip": {
            "nameid_format": "urn:oasis:names:tc:SAML:2.0:nameid-format:transient",
            "common_identifier": "eduPersonPrincipalName",
            "attribute_auth": [
                "https://coip-test.sunet.se/idp/shibboleth",
            ]
        }
    },
    "attribute_map_dir": full_path("attributemaps"),
    "only_use_keys_in_metadata": True,
    "xmlsec_path": ["/opt/local/bin"]
}

sp2 = {
    "entityid": "urn:mace:umu.se:saml:roland:sp",
    "name": "Rolands SP",
    "service": {
        "sp": {
            "endpoints": {
                "assertion_consumer_service": [
                    "http://lingon.catalogix.se:8087/"],
            },
            "required_attributes": ["surName", "givenName", "mail"],
            "optional_attributes": ["title"],
            "idp": {
                "": "https://example.com/saml2/idp/SSOService.php",
            },
            "authn_requests_signed": True,
            "logout_requests_signed": True,
        }
    },
    #"xmlsec_binary" : "/opt/local/bin/xmlsec1",
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
                "urn:mace:umu.se:saml:roland:sp": None
            },
        }
    },
    #"xmlsec_binary" : "/usr/local/bin/xmlsec1",
}

IDP2 = {
    "entityid": "urn:mace:umu.se:saml:roland:idp",
    "name": "Rolands IdP",
    "service": {
        "idp": {
            "endpoints": {
                "single_sign_on_service": ["http://localhost:8088/"],
                "single_logout_service": [
                    ("http://localhost:8088/", BINDING_HTTP_REDIRECT)],
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
                "urn:mace:umu.se:saml:roland:sp": None
            },
        }
    },
    #"xmlsec_binary" : "/usr/local/bin/xmlsec1",
}

PDP = {
    "entityid": "http://example.org/pysaml2/pdp",
    "name": "Rolands PdP",
    "service": {
        "pdp": {
            "endpoints": {
                "authz_service": [("http://example.org/pysaml2/pdp/authz",
                                   BINDING_SOAP)],
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
    "contact_person": [{
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
                "assertion_consumer_service": [
                    "http://lingon.catalogix.se:8087/"],
            },
            "ecp": {
                "130.239.": "http://example.com/idp",
            }
        }
    },
    #"xmlsec_binary" : "/opt/local/bin/xmlsec1",
}

IDP_XMLSECURITY = {
    "entityid": "urn:mace:umu.se:saml:roland:idp",
    "name": "Rolands IdP",
    "service": {
        "idp": {
            "endpoints": {
                "single_sign_on_service": ["http://localhost:8088/"],
                "single_logout_service": [
                    ("http://localhost:8088/", BINDING_HTTP_REDIRECT)],
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
                "urn:mace:umu.se:saml:roland:sp": None
            },
        }
    },
    "key_file": "pkcs11:///usr/lunasa/lib/libCryptoki2_64.so:1/eduID dev SAML signing key?pin=123456",
    "crypto_backend": "XMLSecurity"
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
    assert list(c._sp_idp.values()) == [{'single_sign_on_service':
                                         {
                                             'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect':
                                             'http://localhost:8088/sso/'}}]

    assert c.only_use_keys_in_metadata


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
    assert list(c._sp_idp.values()) == [
        "https://example.com/saml2/idp/SSOService.php"]
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
        #"xmlsec_binary" : "/usr/local/bin/xmlsec1",
    }

    c = SPConfig().load(minimum)
    c.context = "sp"

    assert c is not None


def test_idp_1():
    c = IdPConfig().load(IDP1)
    c.context = "idp"

    print(c)
    assert c.endpoint("single_sign_on_service")[0] == 'http://localhost:8088/'

    attribute_restrictions = c.getattr("policy",
                                       "idp").get_attribute_restrictions("")
    assert attribute_restrictions["edupersonaffiliation"][0].match("staff")


def test_idp_2():
    c = IdPConfig().load(IDP2)
    c.context = "idp"

    print(c)
    assert c.endpoint("single_logout_service",
                      BINDING_SOAP) == []
    assert c.endpoint("single_logout_service",
                      BINDING_HTTP_REDIRECT) == ["http://localhost:8088/"]

    attribute_restrictions = c.getattr("policy",
                                       "idp").get_attribute_restrictions("")
    assert attribute_restrictions["edupersonaffiliation"][0].match("staff")


def test_wayf():
    c = SPConfig().load_file("server_conf")
    c.context = "sp"

    idps = c.metadata.with_descriptor("idpsso")
    ent = list(idps.values())[0]
    assert name(ent) == 'Example Co.'
    assert name(ent, "se") == 'Exempel AB'

    c.setup_logger()

    assert root_logger.level != logging.NOTSET
    assert root_logger.level == logging.INFO
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0],
                      logging.handlers.RotatingFileHandler)
    handler = root_logger.handlers[0]
    assert handler.backupCount == 5
    try:
        assert handler.maxBytes == 100000
    except AssertionError:
        assert handler.maxBytes == 500000
    assert handler.mode == "a"
    assert root_logger.name == "saml2"
    assert root_logger.level == 20


def test_conf_syslog():
    c = SPConfig().load_file("server_conf_syslog")
    c.context = "sp"

    # otherwise the logger setting is not changed
    root_logger.level = logging.NOTSET
    root_logger.handlers = []

    print(c.logger)
    c.setup_logger()

    assert root_logger.level != logging.NOTSET
    assert root_logger.level == logging.INFO
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0],
                      logging.handlers.SysLogHandler)
    handler = root_logger.handlers[0]
    print(handler.__dict__)
    assert handler.facility == "local3"
    assert handler.address == ('localhost', 514)
    if ((sys.version_info.major == 2 and sys.version_info.minor >= 7) or
        sys.version_info.major > 2):
        assert handler.socktype == 2
    else:
        pass
    assert root_logger.name == "saml2"
    assert root_logger.level == 20

#noinspection PyUnresolvedReferences
def test_3():
    cnf = Config()
    cnf.load_file(dotname("sp_1_conf"))
    assert cnf.entityid == "urn:mace:example.com:saml:roland:sp"
    assert cnf.debug == 1
    assert cnf.key_file == full_path("test.key")
    assert cnf.cert_file == full_path("test.pem")
    #assert cnf.xmlsec_binary ==  "/usr/local/bin/xmlsec1"
    assert cnf.accepted_time_diff == 60
    assert cnf.secret == "0123456789"
    assert cnf.metadata is not None
    assert cnf.attribute_converters is not None


def test_sp():
    cnf = SPConfig()
    cnf.load_file(dotname("sp_1_conf"))
    assert cnf.endpoint("assertion_consumer_service") == \
           ["http://lingon.catalogix.se:8087/"]


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
    assert cnf.endpoint("assertion_consumer_service") == \
           ["http://lingon.catalogix.se:8087/"]
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
    assert acs[0][
        "location"] == 'https://www.zimride.com/Shibboleth.sso/SAML2/POST'


def test_crypto_backend():
    idpc = IdPConfig()
    idpc.load(IDP_XMLSECURITY)

    assert idpc.crypto_backend == 'XMLSecurity'
    sec = security_context(idpc)
    assert isinstance(sec.crypto, CryptoBackendXMLSecurity)

if __name__ == "__main__":
    test_crypto_backend()
