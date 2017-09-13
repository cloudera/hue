#!/usr/bin/env python
import os

from saml2 import samlp
from saml2.saml import NAMEID_FORMAT_PERSISTENT, NAMEID_FORMAT_TRANSIENT
from saml2.config import IdPConfig
from saml2.ident import IdentDB
from saml2.assertion import Policy

def _eq(l1,l2):
    return set(l1) == set(l2)

CONFIG = IdPConfig().load({
    "entityid" :  "urn:mace:example.com:idp:2",
    "name" : "test",
    "service": {
        "idp": {
            "endpoints" : {
                "single_sign_on_service" : ["http://idp.example.org/"],
                },
            "policy": {
                "default": {
                    "lifetime": {"minutes":15},
                    "attribute_restrictions": None, # means all I have
                    "name_form": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                    "nameid_format": NAMEID_FORMAT_PERSISTENT
                }
            }
        }
    },
    "virtual_organization" : {
        "http://vo.example.org/biomed":{
            "nameid_format" : "urn:oid:2.16.756.1.2.5.1.1.1-NameID",
            "common_identifier": "uid",
        },
        "http://vo.example.org/design":{
            "nameid_format" : NAMEID_FORMAT_PERSISTENT,
            "common_identifier": "uid",
        }
    }
})

NAME_ID_POLICY_1 = """<?xml version="1.0" encoding="utf-8"?>
<NameIDPolicy xmlns="urn:oasis:names:tc:SAML:2.0:protocol"
  SPNameQualifier="http://vo.example.org/biomed"
/>
"""

NAME_ID_POLICY_2 = """<?xml version="1.0" encoding="utf-8"?>
<NameIDPolicy xmlns="urn:oasis:names:tc:SAML:2.0:protocol"
  SPNameQualifier="http://vo.example.org/design"
/>
"""


class TestIdentifier():
    def setup_class(self):
        try:
            os.remove("subject.db.db")
        except:
            pass
        self.id = IdentDB("subject.db", "example.com", "example")

    def test_persistent_1(self):
        policy = Policy({
            "default": {
                "name_form": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                "nameid_format": NAMEID_FORMAT_PERSISTENT,
                "attribute_restrictions": {
                    "surName": [".*berg"],
                }
            }
        })

        nameid = self.id.construct_nameid("foobar", policy,
                                          "urn:mace:example.com:sp:1")

        assert _eq(nameid.keyswv(), ['format', 'text', 'sp_name_qualifier',
                                     'name_qualifier'])
        assert nameid.sp_name_qualifier == "urn:mace:example.com:sp:1"
        assert nameid.format == NAMEID_FORMAT_PERSISTENT

        id = self.id.find_local_id(nameid)

        assert id == "foobar"

    def test_persistent_2(self):
        userid = 'foobar'
        nameid1 = self.id.persistent_nameid(userid, sp_name_qualifier="sp1",
                                            name_qualifier="name0")

        nameid2 = self.id.persistent_nameid(userid, sp_name_qualifier="sp1",
                                            name_qualifier="name0")

        # persistent NameIDs should be _persistent_ :-)
        assert nameid1 == nameid2

    def test_transient_1(self):
        policy = Policy({
            "default": {
                "name_form": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                "nameid_format": NAMEID_FORMAT_TRANSIENT,
                "attribute_restrictions": {
                    "surName": [".*berg"],
                }
            }
        })
        nameid = self.id.construct_nameid("foobar", policy,
                                          "urn:mace:example.com:sp:1")

        assert _eq(nameid.keyswv(), ['text', 'format', 'sp_name_qualifier',
                                     'name_qualifier'])
        assert nameid.format == NAMEID_FORMAT_TRANSIENT
        assert nameid.text != "foobar"

    def test_vo_1(self):
        policy = Policy({
            "default": {
                "name_form": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                "nameid_format": NAMEID_FORMAT_PERSISTENT,
                "attribute_restrictions": {
                    "surName": [".*berg"],
                }
            }
        })

        name_id_policy = samlp.name_id_policy_from_string(NAME_ID_POLICY_1)
        print(name_id_policy)
        nameid = self.id.construct_nameid("foobar", policy,
                                          'http://vo.example.org/biomed',
                                          name_id_policy)

        print(nameid)
        assert _eq(nameid.keyswv(), ['text', 'sp_name_qualifier', 'format',
                                     'name_qualifier'])
        assert nameid.sp_name_qualifier == 'http://vo.example.org/biomed'
        assert nameid.format == NAMEID_FORMAT_PERSISTENT
        # we want to *NOT* keep the user identifier in the nameid node
        assert nameid.text != "foobar"

    def test_vo_2(self):
        policy = Policy({
            "default": {
                "name_form": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                "nameid_format": NAMEID_FORMAT_PERSISTENT,
                "attribute_restrictions": {
                    "surName": [".*berg"],
                }
            }
        })

        name_id_policy = samlp.name_id_policy_from_string(NAME_ID_POLICY_2)

        nameid = self.id.construct_nameid("foobar", policy,
                                          'http://vo.example.org/design',
                                          name_id_policy)

        assert _eq(nameid.keyswv(), ['text', 'sp_name_qualifier', 'format',
                                     'name_qualifier'])
        assert nameid.sp_name_qualifier == 'http://vo.example.org/design'
        assert nameid.format == NAMEID_FORMAT_PERSISTENT
        assert nameid.text != "foobar01"


    def test_persistent_nameid(self):
        sp_id = "urn:mace:umu.se:sp"
        nameid = self.id.persistent_nameid("abcd0001", sp_id)
        remote_id = nameid.text.strip()
        print(remote_id)
        local = self.id.find_local_id(nameid)
        assert local == "abcd0001"

        # Always get the same
        nameid2 = self.id.persistent_nameid("abcd0001", sp_id)
        assert nameid.text.strip() == nameid2.text.strip()

    def test_transient_nameid(self):
        sp_id = "urn:mace:umu.se:sp"
        nameid = self.id.transient_nameid("abcd0001", sp_id)
        remote_id = nameid.text.strip()
        print(remote_id)
        local = self.id.find_local_id(nameid)
        assert local == "abcd0001"

        # Getting a new, means really getting a new !
        nameid2 = self.id.transient_nameid(sp_id, "abcd0001")
        assert nameid.text.strip() != nameid2.text.strip()

    def teardown_class(self):
        if os.path.exists("subject.db"):
            os.unlink("subject.db")

