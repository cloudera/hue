from mock import Mock, call
from oauth2.datatype import AuthorizationCode, AccessToken
from oauth2.error import AuthCodeNotFound, AccessTokenNotFound
from oauth2.store.memcache import TokenStore
from oauth2.test import unittest

class MemcacheTokenStoreTestCase(unittest.TestCase):
    def setUp(self):
        self.cache_prefix = "test"

    def _generate_test_cache_key(self, key):
        return self.cache_prefix + "_" + key

    def test_fetch_by_code(self):
        code = "abc"
        saved_data = {"client_id": "myclient", "code": code,
                      "expires_at": 100, "redirect_uri": "http://localhost",
                      "scopes": ["foo_read", "foo_write"],
                      "data": {"name": "test"}}

        mc_mock = Mock(spec=["get"])
        mc_mock.get.return_value = saved_data

        store = TokenStore(mc=mc_mock, prefix=self.cache_prefix)

        auth_code = store.fetch_by_code(code)

        mc_mock.get.assert_called_with(self._generate_test_cache_key(code))
        self.assertEqual(auth_code.client_id, saved_data["client_id"])
        self.assertEqual(auth_code.code, saved_data["code"])
        self.assertEqual(auth_code.expires_at, saved_data["expires_at"])
        self.assertEqual(auth_code.redirect_uri, saved_data["redirect_uri"])
        self.assertEqual(auth_code.scopes, saved_data["scopes"])
        self.assertEqual(auth_code.data, saved_data["data"])

    def test_fetch_by_code_no_data(self):
        mc_mock = Mock(spec=["get"])
        mc_mock.get.return_value = None

        store = TokenStore(mc=mc_mock, prefix=self.cache_prefix)

        with self.assertRaises(AuthCodeNotFound):
            store.fetch_by_code("abc")

    def test_save_code(self):
        data = {"client_id": "myclient", "code": "abc", "expires_at": 100,
                 "redirect_uri": "http://localhost",
                 "scopes": ["foo_read", "foo_write"],
                 "data": {"name": "test"}, "user_id": 1}

        auth_code = AuthorizationCode(**data)

        cache_key = self._generate_test_cache_key(data["code"])

        mc_mock = Mock(spec=["set"])

        store = TokenStore(mc=mc_mock, prefix=self.cache_prefix)

        store.save_code(auth_code)

        mc_mock.set.assert_called_with(cache_key, data)

    def test_save_token(self):
        data = {"client_id": "myclient", "token": "xyz",
                "data": {"name": "test"}, "scopes": ["foo_read", "foo_write"],
                "expires_at": None, "refresh_token": "mno", 
                "refresh_expires_at": None,
                "grant_type": "authorization_code",
                "user_id": 123}

        access_token = AccessToken(**data)

        cache_key = self._generate_test_cache_key(access_token.token)
        refresh_token_key = self._generate_test_cache_key(access_token.refresh_token)
        unique_token_key = self._generate_test_cache_key(
            "{0}_{1}_{2}".format(access_token.client_id,
                                 access_token.grant_type,
                                 access_token.user_id)
        )

        mc_mock = Mock(spec=["set"])

        store = TokenStore(mc=mc_mock, prefix=self.cache_prefix)

        store.save_token(access_token)

        mc_mock.set.assert_has_calls([call(cache_key, data),
                                      call(unique_token_key, data),
                                      call(refresh_token_key, data)])

    def test_fetch_existing_token_of_user(self):
        data = {"client_id": "myclient", "token": "xyz",
                "data": {"name": "test"}, "scopes": ["foo_read", "foo_write"],
                "expires_at": None, "refresh_token": "mno",
                "grant_type": "authorization_code",
                "user_id": 123}

        mc_mock = Mock(spec=["get"])
        mc_mock.get.return_value = data

        store = TokenStore(mc=mc_mock, prefix=self.cache_prefix)

        access_token = store.fetch_existing_token_of_user(
            client_id="myclient",
            grant_type="authorization_code",
            user_id=123)

        self.assertTrue(isinstance(access_token, AccessToken))

    def test_fetch_existing_token_of_user_no_data(self):
        mc_mock = Mock(spec=["get"])
        mc_mock.get.return_value = None

        store = TokenStore(mc=mc_mock, prefix=self.cache_prefix)

        with self.assertRaises(AccessTokenNotFound):
            store.fetch_existing_token_of_user(client_id="myclient",
                                               grant_type="authorization_code",
                                               user_id=123)
