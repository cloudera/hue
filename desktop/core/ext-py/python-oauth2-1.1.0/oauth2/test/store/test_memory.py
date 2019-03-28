from oauth2.datatype import AuthorizationCode, AccessToken
from oauth2.error import ClientNotFoundError, AuthCodeNotFound
from oauth2.store.memory import ClientStore, TokenStore
from oauth2.test import unittest

class MemoryClientStoreTestCase(unittest.TestCase):
    def test_add_client_and_fetch_by_client_id(self):
        expected_client_data = {"client_id": "abc", "client_secret": "xyz",
                                "redirect_uris": ["http://localhost"]}
        
        store = ClientStore()
        
        success = store.add_client(expected_client_data["client_id"],
                                   expected_client_data["client_secret"],
                                   expected_client_data["redirect_uris"])
        self.assertTrue(success)
        
        client = store.fetch_by_client_id("abc")
        
        self.assertEqual(client.identifier, expected_client_data["client_id"])
        self.assertEqual(client.secret, expected_client_data["client_secret"])
        self.assertEqual(client.redirect_uris, expected_client_data["redirect_uris"])
    
    def test_fetch_by_client_id_no_client(self):
        store = ClientStore()
        
        with self.assertRaises(ClientNotFoundError):
            store.fetch_by_client_id("abc")

class MemoryTokenStoreTestCase(unittest.TestCase):
    def setUp(self):
        self.access_token_data = {"client_id": "myclient",
                                  "token": "xyz",
                                  "scopes": ["foo_read", "foo_write"],
                                  "data": {"name": "test"},
                                  "grant_type": "authorization_code"}
        self.auth_code = AuthorizationCode("myclient", "abc", 100,
                                           "http://localhost",
                                           ["foo_read", "foo_write"],
                                           {"name": "test"})
        
        self.test_store = TokenStore()
    
    def test_fetch_by_code(self):
        with self.assertRaises(AuthCodeNotFound):
            self.test_store.fetch_by_code("unknown")
    
    def test_save_code_and_fetch_by_code(self):
        success = self.test_store.save_code(self.auth_code)
        self.assertTrue(success)
        
        result = self.test_store.fetch_by_code(self.auth_code.code)
        
        self.assertEqual(result, self.auth_code)
    
    def test_save_token_and_fetch_by_token(self):
        access_token = AccessToken(**self.access_token_data)
        
        success = self.test_store.save_token(access_token)
        self.assertTrue(success)
        
        result = self.test_store.fetch_by_token(access_token.token)
        
        self.assertEqual(result, access_token)
