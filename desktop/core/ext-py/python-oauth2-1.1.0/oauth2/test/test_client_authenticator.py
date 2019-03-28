import base64
from base64 import b64encode
from oauth2.test import unittest
from mock import Mock
from oauth2.client_authenticator import ClientAuthenticator, http_basic_auth, \
    request_body
from oauth2.datatype import Client
from oauth2.error import OAuthInvalidNoRedirectError, ClientNotFoundError,\
    OAuthInvalidError
from oauth2.store import ClientStore
from oauth2.web.wsgi import Request


class ClientAuthenticatorTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client(identifier="abc", secret="xyz",
                             authorized_grants=["authorization_code"],
                             authorized_response_types=["code"],
                             redirect_uris=["http://callback"])
        self.client_store_mock = Mock(spec=ClientStore)

        self.source_mock = Mock()

        self.authenticator = ClientAuthenticator(
            client_store=self.client_store_mock,
            source=self.source_mock)

    def test_by_identifier(self):
        redirect_uri = "http://callback"

        self.client_store_mock.fetch_by_client_id.return_value = self.client

        request_mock = Mock(spec=Request)
        request_mock.get_param.side_effect = [self.client.identifier,
                                              redirect_uri]

        client = self.authenticator.by_identifier(request=request_mock)

        self.client_store_mock.fetch_by_client_id.\
            assert_called_with(self.client.identifier)
        self.assertEqual(client.redirect_uri, redirect_uri)

    def test_by_identifier_client_id_not_set(self):
        request_mock = Mock(spec=Request)
        request_mock.get_param.return_value = None

        with self.assertRaises(OAuthInvalidNoRedirectError) as expected:
            self.authenticator.by_identifier(request=request_mock)

        self.assertEqual(expected.exception.error, "missing_client_id")

    def test_by_identifier_unknown_client(self):
        request_mock = Mock(spec=Request)
        request_mock.get_param.return_value = "def"

        self.client_store_mock.fetch_by_client_id.\
            side_effect = ClientNotFoundError

        with self.assertRaises(OAuthInvalidNoRedirectError) as expected:
            self.authenticator.by_identifier(request=request_mock)

        self.assertEqual(expected.exception.error, "unknown_client")

    def test_by_identifier_unknown_redirect_uri(self):
        response_type = "code"
        unknown_redirect_uri = "http://unknown.com"

        request_mock = Mock(spec=Request)
        request_mock.get_param.side_effect = [self.client.identifier,
                                              response_type,
                                              unknown_redirect_uri]

        self.client_store_mock.fetch_by_client_id.return_value = self.client

        with self.assertRaises(OAuthInvalidNoRedirectError) as expected:
            self.authenticator.by_identifier(request=request_mock)

        self.assertEqual(expected.exception.error, "invalid_redirect_uri")

    def test_by_identifier_secret(self):
        client_id = "abc"
        client_secret = "xyz"
        grant_type = "authorization_code"

        request_mock = Mock(spec=Request)
        request_mock.post_param.return_value = grant_type

        self.source_mock.return_value = (client_id, client_secret)

        self.client_store_mock.fetch_by_client_id.return_value = self.client

        self.authenticator.by_identifier_secret(request=request_mock)
        self.client_store_mock.fetch_by_client_id.\
            assert_called_with(client_id)

    def test_by_identifier_secret_unknown_client(self):
        client_id = "def"
        client_secret = "uvw"

        self.source_mock.return_value = (client_id, client_secret)

        request_mock = Mock(spec=Request)

        self.client_store_mock.fetch_by_client_id.\
            side_effect = ClientNotFoundError

        with self.assertRaises(OAuthInvalidError) as expected:
            self.authenticator.by_identifier_secret(request_mock)

        self.assertEqual(expected.exception.error, "invalid_client")

    def test_by_identifier_secret_client_not_authorized(self):
        client_id = "abc"
        client_secret = "xyz"
        grant_type = "client_credentials"

        self.source_mock.return_value = (client_id, client_secret)

        request_mock = Mock(spec=Request)
        request_mock.post_param.return_value = grant_type

        self.client_store_mock.fetch_by_client_id.return_value = self.client

        with self.assertRaises(OAuthInvalidError) as expected:
            self.authenticator.by_identifier_secret(request_mock)

        self.assertEqual(expected.exception.error, "unauthorized_client")

    def test_by_identifier_secret_wrong_secret(self):
        client_id = "abc"
        client_secret = "uvw"
        grant_type = "authorization_code"

        self.source_mock.return_value = (client_id, client_secret)

        request_mock = Mock(spec=Request)
        request_mock.post_param.return_value = grant_type

        self.client_store_mock.fetch_by_client_id.return_value = self.client

        with self.assertRaises(OAuthInvalidError) as expected:
            self.authenticator.by_identifier_secret(request_mock)

        self.assertEqual(expected.exception.error, "invalid_client")


class RequestBodyTestCase(unittest.TestCase):
    def test_valid(self):
        client_id = "abc"
        client_secret = "secret"

        request_mock = Mock(spec=Request)
        request_mock.post_param.side_effect = [client_id, client_secret]

        result = request_body(request_mock)

        self.assertEqual(result[0], client_id)
        self.assertEqual(result[1], client_secret)

    def test_no_client_id(self):
        request_mock = Mock(spec=Request)
        request_mock.post_param.return_value = None

        with self.assertRaises(OAuthInvalidError) as expected:
            request_body(request_mock)

        self.assertEqual(expected.exception.error, "invalid_request")

    def test_no_client_secret(self):
        request_mock = Mock(spec=Request)
        request_mock.post_param.side_effect = ["abc", None]

        with self.assertRaises(OAuthInvalidError) as expected:
            request_body(request_mock)

        self.assertEqual(expected.exception.error, "invalid_request")


class HttpBasicAuthTestCase(unittest.TestCase):
    def test_valid(self):
        client_id = "testclient"
        client_secret = "secret"

        credentials = "{0}:{1}".format(client_id, client_secret)

        encoded = b64encode(credentials.encode("latin1"))

        request_mock = Mock(spec=Request)
        request_mock.header.return_value = "Basic {0}".\
            format(encoded.decode("latin1"))

        result_client_id, result_client_secret = http_basic_auth(request=request_mock)

        request_mock.header.assert_called_with("authorization")

        self.assertEqual(result_client_id, client_id)
        self.assertEqual(result_client_secret, client_secret)

    def test_header_not_present(self):
        request_mock = Mock(spec=Request)
        request_mock.header.return_value = None

        with self.assertRaises(OAuthInvalidError) as expected:
            http_basic_auth(request=request_mock)

        self.assertEqual(expected.exception.error, "invalid_request")

    def test_invalid_authorization_header(self):
        request_mock = Mock(spec=Request)
        request_mock.header.return_value = "some-data"

        with self.assertRaises(OAuthInvalidError) as expected:
            http_basic_auth(request=request_mock)

        self.assertEqual(expected.exception.error, "invalid_request")
