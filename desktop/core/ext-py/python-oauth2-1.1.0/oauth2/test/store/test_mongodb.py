from oauth2.test import unittest
from oauth2.store.mongodb import AccessTokenStore, AuthCodeStore, \
    ClientStore
from mock import Mock
from oauth2.datatype import AccessToken, AuthorizationCode, Client
from oauth2.error import AccessTokenNotFound, AuthCodeNotFound, \
    ClientNotFoundError


class MongodbAccessTokenStoreTestCase(unittest.TestCase):
    def setUp(self):
        self.access_token_data = {"client_id": "myclient",
                                  "grant_type": "authorization_code",
                                  "token": "xyz",
                                  "scopes": ["foo_read", "foo_write"],
                                  "data": {"name": "test"},
                                  "expires_at": 1000,
                                  "refresh_token": "abcd",
                                  "refresh_expires_at": 2000,
                                  "user_id": None}

    def test_fetch_by_refresh_token(self):
        refresh_token = "abcd"

        self.access_token_data["refresh_token"] = refresh_token

        collection_mock = Mock(spec=["find_one"])
        collection_mock.find_one.return_value = self.access_token_data

        store = AccessTokenStore(collection=collection_mock)
        token = store.fetch_by_refresh_token(refresh_token=refresh_token)

        collection_mock.find_one.assert_called_with(
            {"refresh_token": refresh_token})
        self.assertTrue(isinstance(token, AccessToken))
        self.assertDictEqual(token.__dict__, self.access_token_data)

    def test_fetch_by_refresh_token_no_data(self):
        collection_mock = Mock(spec=["find_one"])
        collection_mock.find_one.return_value = None

        store = AccessTokenStore(collection=collection_mock)

        with self.assertRaises(AccessTokenNotFound):
            store.fetch_by_refresh_token(refresh_token="abcd")

    def test_fetch_existing_token_of_user(self):
        test_data = {"client_id": "myclient",
                     "grant_type": "authorization_code",
                     "token": "xyz",
                     "scopes": ["foo_read", "foo_write"],
                     "data": {"name": "test"},
                     "expires_at": 1000,
                     "refresh_token": "abcd",
                     "refresh_expires_at": 2000,
                     "user_id": 123}

        collection_mock = Mock(spec=["find_one"])
        collection_mock.find_one.return_value = test_data

        store = AccessTokenStore(collection=collection_mock)

        token = store.fetch_existing_token_of_user(client_id="myclient",
                                                   grant_type="authorization_code",
                                                   user_id=123)

        self.assertTrue(isinstance(token, AccessToken))
        self.assertDictEqual(token.__dict__, test_data)
        collection_mock.find_one.assert_called_with({"client_id": "myclient",
                                                     "grant_type": "authorization_code",
                                                     "user_id": 123},
                                                    sort=[("expires_at", -1)])

    def test_fetch_existing_token_of_user_no_data(self):
        collection_mock = Mock(spec=["find_one"])
        collection_mock.find_one.return_value = None

        store = AccessTokenStore(collection=collection_mock)

        with self.assertRaises(AccessTokenNotFound):
            store.fetch_existing_token_of_user(client_id="myclient",
                                               grant_type="authorization_code",
                                               user_id=123)

    def test_save_token(self):
        access_token = AccessToken(**self.access_token_data)

        collection_mock = Mock(spec=["insert"])

        store = AccessTokenStore(collection=collection_mock)
        store.save_token(access_token)

        collection_mock.insert.assert_called_with(self.access_token_data)

class MongodbAuthCodeStoreTestCase(unittest.TestCase):
    def setUp(self):
        self.auth_code_data = {"client_id": "myclient", "expires_at": 1000,
                               "redirect_uri": "https://redirect",
                               "scopes": ["foo", "bar"], "data": {},
                               "user_id": None}

        self.collection_mock = Mock(spec=["find_one", "insert", "remove"])

    def test_fetch_by_code(self):
        code = "abcd"

        self.collection_mock.find_one.return_value = self.auth_code_data

        self.auth_code_data["code"] = "abcd"

        store = AuthCodeStore(collection=self.collection_mock)
        auth_code = store.fetch_by_code(code=code)

        self.collection_mock.find_one.assert_called_with({"code": "abcd"})
        self.assertTrue(isinstance(auth_code, AuthorizationCode))
        self.assertDictEqual(auth_code.__dict__, self.auth_code_data)

    def test_fetch_by_code_no_data(self):
        self.collection_mock.find_one.return_value = None

        store = AuthCodeStore(collection=self.collection_mock)

        with self.assertRaises(AuthCodeNotFound):
            store.fetch_by_code(code="abcd")

    def test_save_code(self):
        self.auth_code_data["code"] = "abcd"

        auth_code = AuthorizationCode(**self.auth_code_data)

        store = AuthCodeStore(collection=self.collection_mock)
        store.save_code(auth_code)

        self.collection_mock.insert.assert_called_with(self.auth_code_data)

class MongodbClientStoreTestCase(unittest.TestCase):
    def test_fetch_by_client_id(self):
        client_data = {"identifier": "testclient", "secret": "k#4g6",
                       "redirect_uris": ["https://redirect"],
                       "authorized_grants": []}

        collection_mock = Mock(spec=["find_one"])
        collection_mock.find_one.return_value = client_data

        store = ClientStore(collection=collection_mock)
        client = store.fetch_by_client_id(client_id=client_data["identifier"])

        collection_mock.find_one.assert_called_with({
            "identifier": client_data["identifier"]})
        self.assertTrue(isinstance(client, Client))
        self.assertEqual(client.identifier, client_data["identifier"])

    def test_fetch_by_client_id_no_data(self):
        collection_mock = Mock(spec=["find_one"])
        collection_mock.find_one.return_value = None

        store = ClientStore(collection=collection_mock)

        with self.assertRaises(ClientNotFoundError):
            store.fetch_by_client_id(client_id="testclient")
