#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from mock import Mock

from oauth2.datatype import AccessToken
from oauth2.store.redisdb import TokenStore
from oauth2.test import unittest


class TokenStoreTestCase(unittest.TestCase):
    def test_delete_refresh_token(self):
        refresh_token_id = "def"
        access_token = AccessToken(client_id="abc", grant_type="token",
                                   token="xyz")

        redisdb_mock = Mock(spec=["delete", "get"])
        redisdb_mock.get.return_value = bytes(json.dumps(access_token.__dict__).encode('utf-8'))

        store = TokenStore(rs=redisdb_mock)
        store.delete_refresh_token(refresh_token_id)

        self.assertEqual(1, redisdb_mock.delete.call_count)
