#!/usr/bin/env python

import time
import py
from saml2.saml import NameID, NAMEID_FORMAT_TRANSIENT
from saml2.cache import Cache
from saml2.time_util import in_a_while, str_to_time
from saml2.ident import code

SESSION_INFO_PATTERN = {"ava": {}, "came from": "", "not_on_or_after": 0,
                        "issuer": "", "session_id": -1}


def _eq(l1, l2):
    return set(l1) == set(l2)


def nid_eq(l1, l2):
    return _eq([code(c) for c in l1], [code(c) for c in l2])


nid = [
    NameID(name_qualifier="foo", format=NAMEID_FORMAT_TRANSIENT, text="1234"),
    NameID(name_qualifier="foo", format=NAMEID_FORMAT_TRANSIENT, text="9876"),
    NameID(name_qualifier="foo", format=NAMEID_FORMAT_TRANSIENT, text="1000")]


class TestClass:
    def setup_class(self):
        self.cache = Cache()

    def test_set(self):
        not_on_or_after = str_to_time(in_a_while(days=1))
        session_info = SESSION_INFO_PATTERN.copy()
        session_info["ava"] = {"givenName": ["Derek"]}
        self.cache.set(nid[0], "abcd", session_info, not_on_or_after)

        (ava, inactive) = self.cache.get_identity(nid[0])
        assert inactive == []
        assert list(ava.keys()) == ["givenName"]
        assert ava["givenName"] == ["Derek"]

    def test_add_ava_info(self):
        not_on_or_after = str_to_time(in_a_while(days=1))
        session_info = SESSION_INFO_PATTERN.copy()
        session_info["ava"] = {"surName": ["Jeter"]}
        self.cache.set(nid[0], "bcde", session_info, not_on_or_after)

        (ava, inactive) = self.cache.get_identity(nid[0])
        assert inactive == []
        assert _eq(ava.keys(), ["givenName", "surName"])
        assert ava["givenName"] == ["Derek"]
        assert ava["surName"] == ["Jeter"]

    def test_from_one_target_source(self):
        session_info = self.cache.get(nid[0], "bcde")
        ava = session_info["ava"]
        assert _eq(ava.keys(), ["surName"])
        assert ava["surName"] == ["Jeter"]
        session_info = self.cache.get(nid[0], "abcd")
        ava = session_info["ava"]
        assert _eq(ava.keys(), ["givenName"])
        assert ava["givenName"] == ["Derek"]

    def test_entities(self):
        assert _eq(self.cache.entities(nid[0]), ["abcd", "bcde"])
        py.test.raises(Exception, "self.cache.entities('6666')")

    def test_remove_info(self):
        self.cache.reset(nid[0], "bcde")
        assert self.cache.active(nid[0], "bcde") == False
        assert self.cache.active(nid[0], "abcd")

        (ava, inactive) = self.cache.get_identity(nid[0])
        assert inactive == ['bcde']
        assert _eq(ava.keys(), ["givenName"])
        assert ava["givenName"] == ["Derek"]

    def test_active(self):
        assert self.cache.active(nid[0], "bcde") == False
        assert self.cache.active(nid[0], "abcd")

    def test_subjects(self):
        assert nid_eq(self.cache.subjects(), [nid[0]])

    def test_second_subject(self):
        not_on_or_after = str_to_time(in_a_while(days=1))
        session_info = SESSION_INFO_PATTERN.copy()
        session_info["ava"] = {"givenName": ["Ichiro"],
                               "surName": ["Suzuki"]}
        self.cache.set(nid[1], "abcd", session_info,
                       not_on_or_after)

        (ava, inactive) = self.cache.get_identity(nid[1])
        assert inactive == []
        assert _eq(ava.keys(), ["givenName", "surName"])
        assert ava["givenName"] == ["Ichiro"]
        assert ava["surName"] == ["Suzuki"]
        assert nid_eq(self.cache.subjects(), [nid[0], nid[1]])

    def test_receivers(self):
        assert _eq(self.cache.receivers(nid[1]), ["abcd"])

        not_on_or_after = str_to_time(in_a_while(days=1))
        session_info = SESSION_INFO_PATTERN.copy()
        session_info["ava"] = {"givenName": ["Ichiro"],
                               "surName": ["Suzuki"]}
        self.cache.set(nid[1], "bcde", session_info,
                       not_on_or_after)

        assert _eq(self.cache.receivers(nid[1]), ["abcd", "bcde"])
        assert nid_eq(self.cache.subjects(), nid[0:2])

    def test_timeout(self):
        not_on_or_after = str_to_time(in_a_while(seconds=1))
        session_info = SESSION_INFO_PATTERN.copy()
        session_info["ava"] = {"givenName": ["Alex"],
                               "surName": ["Rodriguez"]}
        self.cache.set(nid[2], "bcde", session_info,
                       not_on_or_after)

        time.sleep(2)
        (ava, inactive) = self.cache.get_identity(nid[2])
        assert inactive == ["bcde"]
        assert ava == {}
