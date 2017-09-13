#!/usr/bin/env python
import pytest

__author__ = 'rolandh'

import time
from saml2.cache import ToOld
from saml2.mdbcache import Cache
from saml2.time_util import in_a_while, str_to_time
from pytest import raises

SESSION_INFO_PATTERN = {"ava":{}, "came from":"", "not_on_or_after":0,
                    "issuer":"", "session_id":-1}

@pytest.mark.mongo
class TestMongoDBCache():
    def setup_class(self):
        try:
            self.cache = Cache()
            self.cache.clear()
        except Exception:
            self.cache = None

    def test_set_get_1(self):
        if self.cache is not None:
            not_on_or_after = str_to_time(in_a_while(days=1))
            session_info = SESSION_INFO_PATTERN.copy()
            session_info["ava"] = {"givenName":["Derek"]}
            # subject_id, entity_id, info, timestamp
            self.cache.set("1234", "abcd", session_info, not_on_or_after)

            info = self.cache.get("1234", "abcd")
            #{u'issuer': u'', u'came from': u'', u'ava': {u'givenName': [u'Derek']}, u'session_id': -1, u'not_on_or_after': 0}
            ava = info["ava"]
            print(ava)
            assert list(ava.keys()) == ["givenName"]
            assert ava["givenName"] == ["Derek"]

    def test_set_get_2(self):
        if self.cache is not None:
            not_on_or_after = str_to_time(in_a_while(seconds=1))
            session_info = SESSION_INFO_PATTERN.copy()
            session_info["ava"] = {"givenName":["Mariano"]}
            # subject_id, entity_id, info, timestamp
            self.cache.set("1235", "abcd", session_info,
                            not_on_or_after)
            time.sleep(2)

            raises(ToOld, 'self.cache.get("1235", "abcd")')
            info = self.cache.get("1235", "abcd", False)
            assert info != {}

    def test_remove(self):
        if self.cache is not None:
            self.cache.delete("1234")

            info = self.cache.get("1234", "abcd")
            print(info)
            assert info == {}

    def test_subjects(self):
        if self.cache is not None:
            slist = self.cache.subjects()
            assert len(slist) == 1
            assert slist == ["1235"]

    def test_identity(self):
        if self.cache is not None:
            not_on_or_after = str_to_time(in_a_while(days=1))
            session_info = SESSION_INFO_PATTERN.copy()
            session_info["ava"] = {"givenName":["Derek"]}
            self.cache.set("1234", "abcd", session_info, not_on_or_after)

            not_on_or_after = str_to_time(in_a_while(days=1))
            session_info = SESSION_INFO_PATTERN.copy()
            session_info["ava"] = {"mail":["Derek.Jeter@mlb.com"]}
            self.cache.set("1234", "xyzv", session_info, not_on_or_after)

            (ident, _) = self.cache.get_identity("1234")
            print(ident)
            assert len(ident.keys()) == 2
            assert "givenName" in ident.keys()
            assert "mail" in ident.keys()
            assert ident["mail"] == ["Derek.Jeter@mlb.com"]
            assert ident["givenName"] == ["Derek"]

    def test_remove_2(self):
        if self.cache is not None:
            self.cache.delete("1234")

            info = self.cache.get("1234", "xyzv")
            print(info)
            assert info == {}
