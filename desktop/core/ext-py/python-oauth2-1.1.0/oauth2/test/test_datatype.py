from oauth2.test import unittest
from mock import patch
from oauth2.datatype import AccessToken, Client
from oauth2.error import RedirectUriUnknown


def mock_time():
    return 1000


class AccessTokenTestCase(unittest.TestCase):
    @patch("time.time", mock_time)
    def test_expires_in_expired(self):
        access_token = AccessToken(client_id="abc",
                                   grant_type="client_credentials",
                                   token="def", expires_at=999)

        self.assertEqual(access_token.expires_in, 0)

    @patch("time.time", mock_time)
    def test_expires_in_not_expired(self):
        access_token = AccessToken(client_id="abc",
                                   grant_type="client_credentials",
                                   token="def", expires_at=1100)

        self.assertEqual(access_token.expires_in, 100)

    def test_is_expired_expired_at_not_set(self):
        access_token = AccessToken(client_id="abc",
                                   grant_type="client_credentials",
                                   token="def")

        self.assertFalse(access_token.is_expired())


class ClientTestCase(unittest.TestCase):
    def test_redirect_uri(self):
        client = Client(identifier="abc", secret="xyz",
                        redirect_uris=["http://callback"])

        self.assertEqual(client.redirect_uri, "http://callback")
        client.redirect_uri = "http://callback"
        self.assertEqual(client.redirect_uri, "http://callback")

        with self.assertRaises(RedirectUriUnknown):
            client.redirect_uri = "http://another.callback"

    def test_response_type_supported(self):
        client = Client(identifier="abc", secret="xyz",
                        authorized_grants=["test_grant"])

        self.assertTrue(client.grant_type_supported("test_grant"))
        self.assertFalse(client.grant_type_supported("unknown_grant"))

    def test_response_type_supported(self):
        client = Client(identifier="abc", secret="xyz",
                        authorized_response_types=["test_response_type"])

        self.assertTrue(client.response_type_supported("test_response_type"))
        self.assertFalse(client.response_type_supported("unknown"))
