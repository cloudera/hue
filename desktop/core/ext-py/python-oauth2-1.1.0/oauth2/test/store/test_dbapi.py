from functools import wraps
from mock import Mock, call
from oauth2.datatype import AccessToken, AuthorizationCode, Client
from oauth2.error import AccessTokenNotFound, ClientNotFoundError, \
    AuthCodeNotFound
from oauth2.store.dbapi.mysql import MysqlAccessTokenStore, MysqlAuthCodeStore, \
    MysqlClientStore
from oauth2.test import unittest


access_token_stores = [MysqlAccessTokenStore]

auth_code_stores = [MysqlAuthCodeStore]

client_stores = [MysqlClientStore]


class with_classes(object):
    def __init__(self, classes):
        self.classes = classes

    def __call__(self, func):
        @wraps(func)
        def wrapper(instance, *args, **kwargs):
            for klass in self.classes:
                func(instance, klass, *args, **kwargs)

        return wrapper


class StoreTestCase(unittest.TestCase):
    def _con_mock(self, cursor_mocks=None):
        connection_mock = Mock(spec=["close", "commit", "cursor"])

        if isinstance(cursor_mocks, list):
            connection_mock.cursor.side_effect = cursor_mocks

        return connection_mock

    def _cursor_mock(self):
        return Mock(spec=["close", "execute", "fetchone", "fetchall"])


class AccessTokenStoreTestCase(StoreTestCase):
    @with_classes(access_token_stores)
    def test_delete_refresh_token(self, store_class):
        refresh_token = "xyz789"

        cursor_mock = self._cursor_mock()
        cursor_mock.lastrowid = None

        connection_mock = self._con_mock()
        connection_mock.cursor.return_value = cursor_mock

        store = store_class(connection=connection_mock)
        store.delete_refresh_token(refresh_token)

        cursor_mock.execute.assert_called_with(
            store_class.delete_refresh_token_query,
            (refresh_token,))

        self.assertEqual(cursor_mock.close.call_count, 1)

        self.assertEqual(connection_mock.commit.call_count, 1)

    @with_classes(access_token_stores)
    def test_fetch_by_refresh_token(self, store_class):
        refresh_token = "xyz789"
        access_token_row_id = 1
        token_data = {"client_id": "abc", "grant_type": "test_grant",
                      "token": "abc123", "data": {"test": "data"},
                      "expires_at": 1000, "refresh_token": refresh_token,
                      "refresh_expires_at": 2000, "scopes": ["foo", "bar"],
                      "user_id": 1}

        data_cursor = self._cursor_mock()
        data_cursor.fetchall.return_value = [("test", "data")]

        scope_cursor = self._cursor_mock()
        scope_cursor.fetchall.return_value = [("foo",), ("bar",)]

        token_cursor = self._cursor_mock()

        token_cursor.fetchone.return_value = (access_token_row_id,
                                              token_data["client_id"],
                                              token_data["grant_type"],
                                              token_data["token"],
                                              token_data["expires_at"],
                                              token_data["refresh_token"],
                                              token_data["refresh_expires_at"],
                                              token_data["user_id"])

        connection_mock = self._con_mock([token_cursor, scope_cursor,
                                          data_cursor])

        store = store_class(connection=connection_mock)
        access_token = store.fetch_by_refresh_token(refresh_token)

        self.assertTrue(isinstance(access_token, AccessToken))
        self.assertEqual(access_token.client_id, token_data["client_id"])
        self.assertEqual(access_token.grant_type, token_data["grant_type"])
        self.assertEqual(access_token.token, token_data["token"])
        self.assertDictEqual(access_token.data, token_data["data"])
        self.assertEqual(access_token.expires_at, token_data["expires_at"])
        self.assertEqual(access_token.refresh_token, refresh_token)
        self.assertEqual(access_token.refresh_expires_at,
                         token_data["refresh_expires_at"])
        self.assertListEqual(access_token.scopes, token_data["scopes"])
        self.assertEqual(access_token.user_id, token_data["user_id"])

        token_cursor.execute.\
            assert_called_with(store_class.fetch_by_refresh_token_query,
                               (refresh_token,))

        scope_cursor.execute.\
            assert_called_with(store_class.fetch_scopes_by_access_token_query,
                               (access_token_row_id,))

        data_cursor.execute.\
            assert_called_with(store_class.fetch_data_by_access_token_query,
                               (access_token_row_id,))

    @with_classes(access_token_stores)
    def test_fetch_by_refresh_token_data_not_found(self, store_class):
        cursor_mock = self._cursor_mock()
        cursor_mock.fetchone.return_value = None

        connection_mock = self._con_mock()
        connection_mock.cursor.return_value = cursor_mock

        with self.assertRaises(AccessTokenNotFound):
            store = store_class(connection_mock)
            store.fetch_by_refresh_token("def")

    @with_classes(access_token_stores)
    def test_fetch_existing_token_of_user(self, store_class):
        access_token_row_id = 1
        token_data = {"client_id": "abc", "grant_type": "test_grant",
                      "token": "abc123", "data": {"test": "data"},
                      "expires_at": 1000, "refresh_token": "xyz789",
                      "refresh_expires_at": 2000, "scopes": ["foo", "bar"],
                      "user_id": 1}

        data_cursor = self._cursor_mock()
        data_cursor.fetchall.return_value = [("test", "data")]

        scope_cursor = self._cursor_mock()
        scope_cursor.fetchall.return_value = [("foo",), ("bar",)]

        token_cursor = self._cursor_mock()
        token_cursor.fetchone.return_value = (access_token_row_id,
                                              token_data["client_id"],
                                              token_data["grant_type"],
                                              token_data["token"],
                                              token_data["expires_at"],
                                              token_data["refresh_token"],
                                              token_data["refresh_expires_at"],
                                              token_data["user_id"])

        connection_mock = self._con_mock([token_cursor, scope_cursor,
                                          data_cursor])

        store = store_class(connection=connection_mock)
        access_token = store.\
            fetch_existing_token_of_user(client_id=token_data["client_id"],
                                         grant_type=token_data["grant_type"],
                                         user_id=token_data["user_id"])

        self.assertTrue(isinstance(access_token, AccessToken))
        self.assertEqual(access_token.client_id, token_data["client_id"])
        self.assertEqual(access_token.grant_type, token_data["grant_type"])
        self.assertEqual(access_token.token, token_data["token"])
        self.assertDictEqual(access_token.data, token_data["data"])
        self.assertEqual(access_token.expires_at, token_data["expires_at"])
        self.assertEqual(access_token.refresh_token,
                         token_data["refresh_token"])
        self.assertEqual(access_token.refresh_expires_at,
                         token_data["refresh_expires_at"])
        self.assertListEqual(access_token.scopes, token_data["scopes"])
        self.assertEqual(access_token.user_id, token_data["user_id"])

        token_cursor.execute.\
            assert_called_with(store_class.fetch_existing_token_of_user_query,
                               (token_data["client_id"],
                                token_data["grant_type"],
                                token_data["user_id"]))

        scope_cursor.execute.\
            assert_called_with(store_class.fetch_scopes_by_access_token_query,
                               (access_token_row_id,))

        data_cursor.execute.\
            assert_called_with(store_class.fetch_data_by_access_token_query,
                               (access_token_row_id,))

    @with_classes(access_token_stores)
    def test_fetch_existing_token_of_user_no_token_found(self, store_class):
        cursor_mock = self._cursor_mock()
        cursor_mock.fetchone.return_value = None

        connection_mock = self._con_mock()
        connection_mock.cursor.return_value = cursor_mock

        store = store_class(connection=connection_mock)

        with self.assertRaises(AccessTokenNotFound):
            store.fetch_existing_token_of_user(client_id="abc",
                                               grant_type="test_grant",
                                               user_id=1)

    @with_classes(access_token_stores)
    def test_save_token(self, store_class):
        first_cursor = Mock(spec=["close", "execute"])
        first_cursor.lastrowid = 1

        second_cursor = Mock()
        third_cursor = Mock()
        fourth_cursor = Mock()

        connection_mock = Mock(spec=["commit", "cursor"])
        connection_mock.cursor.side_effect = [first_cursor, second_cursor,
                                              third_cursor, fourth_cursor]

        access_token = AccessToken(client_id="abc", grant_type="test",
                                   token="abc123", data={"test": "data"},
                                   expires_at=1000, refresh_token="xyz789",
                                   refresh_expires_at=2000,
                                   scopes=["foo", "bar"], user_id=1)

        store = store_class(connection=connection_mock)
        result = store.save_token(access_token)

        self.assertTrue(result)

        self.assertEqual(connection_mock.commit.call_count, 4)

        first_cursor.execute.\
            assert_called_with(store_class.create_access_token_query,
                               (access_token.client_id,
                                access_token.grant_type, access_token.token,
                                access_token.expires_at,
                                access_token.refresh_token,
                                access_token.refresh_expires_at,
                                access_token.user_id))
        first_cursor.close.assert_called_with()

        second_cursor.execute.\
            assert_called_with(store_class.create_data_query,
                               ("test", "data", 1))
        second_cursor.close.assert_called_with()

        third_cursor.execute.\
            assert_called_with(store_class.create_scope_query, ("foo", 1))
        third_cursor.close.assert_called_with()

        fourth_cursor.execute.\
            assert_called_with(store_class.create_scope_query, ("bar", 1))
        fourth_cursor.close.assert_called_with()


class AuthCodeStoreTestCase(StoreTestCase):
    @with_classes(auth_code_stores)
    def test_delete_code(self, store_class):
        code = "abc123"

        cursor_mock = self._cursor_mock()
        cursor_mock.lastrowid = None

        connection_mock = self._con_mock([cursor_mock])

        store = store_class(connection=connection_mock)
        store.delete_code(code)

        cursor_mock.execute.\
            assert_called_with(store_class.delete_code_query, (code,))
        self.assertEqual(cursor_mock.close.call_count, 1)

    @with_classes(auth_code_stores)
    def test_fetch_by_code(self, store_class):
        code_data = {"client_id": "abc", "code": "abc123", "expires_at": 1000,
                     "redirect_uri": "http://localhost",
                     "scopes": ["foo", "bar"], "data": {"test": "data"},
                     "user_id": 1}
        id_in_db = 1

        code_cursor = Mock(spec=["execute", "close", "fetchone"])
        code_cursor.lastrowid = 1
        code_cursor.fetchone.return_value = (id_in_db, code_data["client_id"],
                                             code_data["code"],
                                             code_data["expires_at"],
                                             code_data["redirect_uri"],
                                             code_data["user_id"])

        data_cursor = Mock(spec=["execute", "close", "fetchall"])
        data_cursor.fetchall.return_value = [("test", "data")]

        scope_cursor = Mock(spec=["execute", "close", "fetchall"])
        scope_cursor.fetchall.return_value = [("foo",), ("bar",)]

        connection_mock = Mock(spec=["commit", "cursor"])
        connection_mock.cursor.side_effect = [code_cursor, data_cursor,
                                              scope_cursor]

        store = store_class(connection=connection_mock)
        auth_code = store.fetch_by_code("abc123")

        self.assertTrue(isinstance(auth_code, AuthorizationCode))

        self.assertEqual(auth_code.client_id, code_data["client_id"])
        self.assertEqual(auth_code.code, code_data["code"])
        self.assertEqual(auth_code.expires_at, code_data["expires_at"])
        self.assertEqual(auth_code.redirect_uri, code_data["redirect_uri"])
        self.assertEqual(auth_code.user_id, code_data["user_id"])
        self.assertListEqual(auth_code.scopes, code_data["scopes"])
        self.assertDictEqual(auth_code.data, code_data["data"])

        code_cursor.execute.assert_called_with(store_class.fetch_code_query,
                                               (code_data["code"],))
        code_cursor.close.assert_called_with()

        data_cursor.execute.assert_called_with(store_class.fetch_data_query,
                                               (id_in_db,))
        data_cursor.close.assert_called_with()

        scope_cursor.execute.\
            assert_called_with(store_class.fetch_scopes_query, (id_in_db,))

    @with_classes(auth_code_stores)
    def test_fetch_by_code_no_data_found(self, store_class):
        cursor_mock = Mock(spec=["execute", "close", "fetchone"])
        cursor_mock.fetchone.return_value = None

        connection_mock = Mock(spec=["cursor"])
        connection_mock.cursor.return_value = cursor_mock

        with self.assertRaises(AuthCodeNotFound):
            store = store_class(connection_mock)
            store.fetch_by_code("xyz789")

    @with_classes(auth_code_stores)
    def test_save_code(self, store_class):
        code_data = {"client_id": "abc", "code": "abc123", "expires_at": 1000,
                     "redirect_uri": "http://localhost",
                     "scopes": ["foo", "bar"], "data": {"test": "data"},
                     "user_id": 1}
        id_in_db = 1

        create_code_cursor = Mock(spec=["close", "execute"])
        create_code_cursor.lastrowid = id_in_db
        create_data_cursor = Mock(spec=["close", "execute"])
        create_data_cursor.lastrowid = 1
        create_first_scope_cursor = Mock(spec=["close", "execute"])
        create_first_scope_cursor.lastrowid = 1
        create_second_scope_cursor = Mock(spec=["close", "execute"])
        create_second_scope_cursor.lastrowid = 2

        connection_mock = Mock(spec=["commit", "cursor"])
        connection_mock.cursor.side_effect = [create_code_cursor,
                                              create_data_cursor,
                                              create_first_scope_cursor,
                                              create_second_scope_cursor]

        auth_code = AuthorizationCode(**code_data)

        store = store_class(connection=connection_mock)
        result = store.save_code(auth_code)

        self.assertTrue(result)

        create_code_cursor.execute.\
            assert_called_with(store_class.create_auth_code_query,
                               (code_data["client_id"], code_data["code"],
                                code_data["expires_at"],
                                code_data["redirect_uri"],
                                code_data["user_id"]))
        create_code_cursor.close.assert_called_with()

        create_data_cursor.execute.\
            assert_called_with(store_class.create_data_query,
                               ("test", "data", id_in_db))
        create_data_cursor.close.assert_called_with()

        create_first_scope_cursor.execute.\
            assert_called_with(store_class.create_scope_query,
                               ("foo", id_in_db))

        create_second_scope_cursor.execute.\
            assert_called_with(store_class.create_scope_query,
                               ("bar", id_in_db))

        self.assertEqual(connection_mock.commit.call_count, 4)


class MysqlClientStoreTestCase(StoreTestCase):
    @with_classes(client_stores)
    def test_fetch_by_client_id(self, store_class):
        client_id = 123
        client_data = {"identifier": "abc", "secret": "xyz",
                       "authorized_grants": ["authorization_code",
                                             "password"],
                       "authorized_response_types": ["code", "token"],
                       "redirect_uris": ["http://example.com",
                                         "http://www.example.com"]}

        client_cursor = Mock(spec=["close", "execute", "fetchone"])
        client_cursor.fetchone.return_value = (client_id,
                                               client_data["identifier"],
                                               client_data["secret"])
        redirect_uris_cursor = Mock(spec=["close", "execute", "fetchall"])
        redirect_uris_cursor.fetchall.return_value = [
            ("http://example.com",), ("http://www.example.com",)
        ]
        grants_cursor = Mock(spec=["close", "execute", "fetchall"])
        grants_cursor.fetchall.return_value = [("authorization_code",),
                                               ("password",)]
        response_types_cursor = Mock(spec=["close", "execute", "fetchall"])
        response_types_cursor.fetchall.return_value = [("code",), ("token",)]

        connection_mock = Mock(spec=["commit", "cursor"])

        connection_mock.cursor.side_effect = [client_cursor,
                                              grants_cursor,
                                              redirect_uris_cursor,
                                              response_types_cursor]

        store = store_class(connection=connection_mock)
        client = store.fetch_by_client_id(client_data["identifier"])

        self.assertTrue(isinstance(client, Client))
        self.assertEqual(client.identifier, client_data["identifier"])
        self.assertEqual(client.secret, client_data["secret"])
        self.assertListEqual(client.authorized_grants,
                             client_data["authorized_grants"])
        self.assertListEqual(client.authorized_response_types,
                             client_data["authorized_response_types"])
        self.assertListEqual(client.redirect_uris,
                             client_data["redirect_uris"])

        client_cursor.execute.\
            assert_called_with(store_class.fetch_client_query,
                               (client_data["identifier"],))
        redirect_uris_cursor.execute.\
            assert_called_with(store_class.fetch_redirect_uris_query,
                               (client_id,))
        grants_cursor.execute.\
            assert_called_with(store_class.fetch_grants_query, (client_id,))
        response_types_cursor.execute.\
            assert_called_with(store_class.fetch_response_types_query,
                               (client_id,))

    @with_classes(client_stores)
    def test_fetch_by_client_id_client_not_found(self, store_class):
        client_cursor_mock = Mock(spec=["close", "execute", "fetchone"])
        client_cursor_mock.fetchone.return_value = None

        connection_mock = Mock(spec=["cursor"])
        connection_mock.cursor.return_value = client_cursor_mock

        store = store_class(connection=connection_mock)

        with self.assertRaises(ClientNotFoundError):
            store.fetch_by_client_id("abc")
