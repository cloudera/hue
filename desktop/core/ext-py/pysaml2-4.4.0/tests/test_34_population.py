#!/usr/bin/env python
from saml2.ident import code
from saml2.saml import NAMEID_FORMAT_TRANSIENT, NameID

from saml2.population import Population
from saml2.time_util import in_a_while

IDP_ONE = "urn:mace:example.com:saml:one:idp"
IDP_OTHER = "urn:mace:example.com:saml:other:idp"

nid = NameID(name_qualifier="foo", format=NAMEID_FORMAT_TRANSIENT, 
             text="123456")

nida = NameID(name_qualifier="foo", format=NAMEID_FORMAT_TRANSIENT,
              text="abcdef")

cnid = code(nid)
cnida = code(nida)

def _eq(l1, l2):
    return set(l1) == set(l2)

class TestPopulationMemoryBased():
    def setup_class(self):
        self.population = Population()
        
    def test_add_person(self):
        session_info = {
            "name_id": nid,
            "issuer": IDP_ONE,
            "not_on_or_after": in_a_while(minutes=15),
            "ava": {
                "givenName": "Anders",
                "surName": "Andersson",
                "mail": "anders.andersson@example.com"
            }
        }
        self.population.add_information_about_person(session_info)
        
        issuers = self.population.issuers_of_info(nid)
        assert list(issuers) == [IDP_ONE]
        subjects = [code(c) for c in self.population.subjects()]
        assert subjects == [cnid]
        # Are any of the sources gone stale
        stales = self.population.stale_sources_for_person(nid)
        assert stales == []
        # are any of the possible sources not used or gone stale
        possible = [IDP_ONE, IDP_OTHER]
        stales = self.population.stale_sources_for_person(nid, possible)
        assert stales == [IDP_OTHER]

        (identity, stale) = self.population.get_identity(nid)
        assert stale == []
        assert identity == {'mail': 'anders.andersson@example.com', 
                            'givenName': 'Anders', 
                            'surName': 'Andersson'}

        info = self.population.get_info_from(nid, IDP_ONE)
        assert sorted(list(info.keys())) == sorted(["not_on_or_after",
                                                    "name_id", "ava"])
        assert info["name_id"] == nid
        assert info["ava"] == {'mail': 'anders.andersson@example.com', 
                                'givenName': 'Anders', 
                                'surName': 'Andersson'}

    def test_extend_person(self):
        session_info = {
            "name_id": nid,
            "issuer": IDP_OTHER,
            "not_on_or_after": in_a_while(minutes=15),
            "ava": {
                "eduPersonEntitlement": "Anka"
            }
        }
        
        self.population.add_information_about_person(session_info)
        
        issuers = self.population.issuers_of_info(nid)
        assert _eq(issuers, [IDP_ONE, IDP_OTHER])
        subjects = [code(c) for c in self.population.subjects()]
        assert subjects == [cnid]
        # Are any of the sources gone stale
        stales = self.population.stale_sources_for_person(nid)
        assert stales == []
        # are any of the possible sources not used or gone stale
        possible = [IDP_ONE, IDP_OTHER]
        stales = self.population.stale_sources_for_person(nid, possible)
        assert stales == []

        (identity, stale) = self.population.get_identity(nid)
        assert stale == []
        assert identity == {'mail': 'anders.andersson@example.com', 
                            'givenName': 'Anders', 
                            'surName': 'Andersson',
                            "eduPersonEntitlement": "Anka"}

        info = self.population.get_info_from(nid, IDP_OTHER)
        assert sorted(list(info.keys())) == sorted(["not_on_or_after",
                                                    "name_id", "ava"])
        assert info["name_id"] == nid
        assert info["ava"] == {"eduPersonEntitlement": "Anka"}
    
    def test_add_another_person(self):
        session_info = {
            "name_id": nida,
            "issuer": IDP_ONE,
            "not_on_or_after": in_a_while(minutes=15),
            "ava": {
                "givenName": "Bertil",
                "surName": "Bertilsson",
                "mail": "bertil.bertilsson@example.com"
            }
        }
        self.population.add_information_about_person(session_info)

        issuers = self.population.issuers_of_info(nida)
        assert list(issuers) == [IDP_ONE]
        subjects = [code(c) for c in self.population.subjects()]
        assert _eq(subjects, [cnid, cnida])
        
        stales = self.population.stale_sources_for_person(nida)
        assert stales == []
        # are any of the possible sources not used or gone stale
        possible = [IDP_ONE, IDP_OTHER]
        stales = self.population.stale_sources_for_person(nida, possible)
        assert stales == [IDP_OTHER]

        (identity, stale) = self.population.get_identity(nida)
        assert stale == []
        assert identity == {"givenName": "Bertil",
                            "surName": "Bertilsson",
                            "mail": "bertil.bertilsson@example.com"
                            }

        info = self.population.get_info_from(nida, IDP_ONE)
        assert sorted(list(info.keys())) == sorted(["not_on_or_after",
                                                    "name_id", "ava"])
        assert info["name_id"] == nida
        assert info["ava"] == {"givenName": "Bertil",
                                "surName": "Bertilsson",
                                "mail": "bertil.bertilsson@example.com"
                                }

    def test_modify_person(self):
        session_info = {
            "name_id": nid,
            "issuer": IDP_ONE,
            "not_on_or_after": in_a_while(minutes=15),
            "ava": {
                "givenName": "Arne",
                "surName": "Andersson",
                "mail": "arne.andersson@example.com"
            }
        }
        self.population.add_information_about_person(session_info)
        
        issuers = self.population.issuers_of_info(nid)
        assert _eq(issuers, [IDP_ONE, IDP_OTHER])
        subjects = [code(c) for c in self.population.subjects()]
        assert _eq(subjects, [cnid, cnida])
        # Are any of the sources gone stale
        stales = self.population.stale_sources_for_person(nid)
        assert stales == []
        # are any of the possible sources not used or gone stale
        possible = [IDP_ONE, IDP_OTHER]
        stales = self.population.stale_sources_for_person(nid, possible)
        assert stales == []

        (identity, stale) = self.population.get_identity(nid)
        assert stale == []
        assert identity == {'mail': 'arne.andersson@example.com', 
                            'givenName': 'Arne', 
                            'surName': 'Andersson',
                            "eduPersonEntitlement": "Anka"}

        info = self.population.get_info_from(nid, IDP_OTHER)
        assert sorted(list(info.keys())) == sorted(["not_on_or_after",
                                                    "name_id", "ava"])
        assert info["name_id"] == nid
        assert info["ava"] == {"eduPersonEntitlement": "Anka"}
