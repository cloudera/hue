from mock import Mock, call, patch
import json
from oauth2.client_authenticator import ClientAuthenticator
from oauth2.compatibility import quote
from oauth2.test import unittest
from oauth2.web import Response, ResourceOwnerGrantSiteAdapter, \
    ImplicitGrantSiteAdapter, AuthorizationCodeGrantSiteAdapter
from oauth2.web.wsgi import Request
from oauth2.grant import ImplicitGrantHandler, AuthorizationCodeAuthHandler, \
    AuthRequestMixin, AuthorizationCodeTokenHandler, ImplicitGrant, \
    AuthorizationCodeGrant, ResourceOwnerGrantHandler, ResourceOwnerGrant, \
    Scope, RefreshToken, RefreshTokenHandler, ClientCredentialsGrant, \
    ClientCredentialsHandler, AuthorizeMixin, SiteAdapterMixin
from oauth2.store import ClientStore, AuthCodeStore, AccessTokenStore
from oauth2.error import OAuthInvalidError, UserNotAuthenticated, \
    AccessTokenNotFound, UserIdentifierMissingError, AuthCodeNotFound
from oauth2 import Provider
from oauth2.datatype import Client, AuthorizationCode, AccessToken
from oauth2.tokengenerator import TokenGenerator
from copy import copy


def mock_time():
    return 1000


class AuthorizationCodeGrantTestCase(unittest.TestCase):
    def test_create_auth_handler(self):
        """
        AuthorizationCodeGrant() should return a new instance of AuthorizationCodeAuthHandler on request
        """
        default_scope = "default_scope"
        method = "GET"
        scopes = ["first", "second"]
        path = "/auth"

        request_mock = Mock(spec=Request)
        request_mock.method = method
        request_mock.path = path
        request_mock.get_param.return_value = "code"

        scope_mock = Mock(Scope)

        server_mock = Mock()
        server_mock.authorize_path = path
        server_mock.auth_code_store = Mock()
        server_mock.client_authenticator = Mock()
        server_mock.token_generator = Mock()

        factory = AuthorizationCodeGrant(
            default_scope=default_scope,
            scopes=scopes,
            scope_class=scope_mock,
            site_adapter=Mock(spec=AuthorizationCodeGrantSiteAdapter)
        )
        result_class = factory(request_mock, server_mock)

        request_mock.get_param.assert_called_with("response_type")
        scope_mock.assert_called_with(default=default_scope, available=scopes)
        self.assertTrue(isinstance(result_class, AuthorizationCodeAuthHandler))

    def test_create_token_handler(self):
        path = "/token"

        request_mock = Mock(spec=Request)
        request_mock.method = "POST"
        request_mock.path = path
        request_mock.post_param.return_value = "authorization_code"

        server_mock = Mock()
        server_mock.authorize_path = "/auth"
        server_mock.token_path = path
        server_mock.access_token_store = Mock(spec=AccessTokenStore)
        server_mock.auth_code_store = Mock()
        server_mock.client_store = Mock()
        server_mock.token_generator = Mock()

        factory = AuthorizationCodeGrant(
            site_adapter=Mock(spec=AuthorizationCodeGrantSiteAdapter)
        )
        result_class = factory(request_mock, server_mock)

        request_mock.post_param.assert_called_with("grant_type")
        self.assertTrue(isinstance(result_class,
                                   AuthorizationCodeTokenHandler))

    def test_create_no_match(self):
        request_mock = Mock(spec=Request)
        request_mock.method = "POST"
        request_mock.get_param.return_value = "no-code"
        request_mock.post_param.return_value = "no-authorization_code"

        factory = AuthorizationCodeGrant(
            site_adapter=Mock(spec=AuthorizationCodeGrantSiteAdapter)
        )
        result_class = factory(request_mock, Mock())

        request_mock.post_param.assert_called_with("grant_type")
        self.assertEqual(result_class, None)


class AuthRequestMixinTestCase(unittest.TestCase):
    def test_read_validate_params_all_valid(self):
        """
        AuthRequestMixin.read_validate_params should parse all params correctly if they are valid
        """
        response_type = "code"
        state = "state"

        client = Client(identifier="abc", secret="xyz",
                        redirect_uris=["http://callback"],
                        authorized_response_types=["code"])

        request_mock = Mock(spec=Request)
        request_mock.get_param.side_effect = [response_type, state]

        scope_handler_mock = Mock(Scope)

        client_auth_mock = Mock(spec=ClientAuthenticator)
        client_auth_mock.by_identifier.return_value = client

        handler = AuthRequestMixin(client_authenticator=client_auth_mock,
                                   scope_handler=scope_handler_mock,
                                   token_generator=Mock())

        result = handler.read_validate_params(request_mock)

        request_mock.get_param.assert_has_calls([call("state")])
        scope_handler_mock.parse.assert_called_with(request_mock, "query")
        client_auth_mock.by_identifier.assert_called_with(request_mock)
        self.assertEqual(handler.state, state)
        self.assertTrue(result)


class AuthorizeMixinTestCase(unittest.TestCase):
    def test_authorize_user_denied_access(self):
        """
        AuthorizeMixin.authorize should raise an OAuthUserError if the user did not authorize the request
        """
        site_adapter_mock = Mock(spec=ImplicitGrantSiteAdapter)
        site_adapter_mock.user_has_denied_access.return_value = True

        auth_mixin = AuthorizeMixin(site_adapter=site_adapter_mock)
        with self.assertRaises(OAuthInvalidError):
            auth_mixin.authorize(Mock(spec=Request), Mock(spec=Response),
                                 environ={}, scopes=[])

    def test_authorize_dict_return(self):
        """
        AuthorizeMixin.authorize should return a tuple even if the SiteAdapter returns a dict
        """
        client_mock = Mock(spec=Client)

        test_data = {"test": "data"}

        site_adapter_mock = Mock(spec=ImplicitGrantSiteAdapter)
        site_adapter_mock.user_has_denied_access.return_value = False
        site_adapter_mock.authenticate.return_value = test_data

        auth_mixin = AuthorizeMixin(site_adapter=site_adapter_mock)
        auth_mixin.client = client_mock
        result = auth_mixin.authorize(Mock(spec=Request), Mock(spec=Response),
                                      environ={}, scopes=[])

        self.assertTrue(isinstance(result, tuple))
        self.assertDictEqual(result[0], test_data)
        self.assertIsNone(result[1])

    def test_authorize_tuple_return(self):
        """
        AuthorizeMixin.authorize should return the tuple returned by the SiteAdapter
        """
        client_mock = Mock(spec=Client)

        test_data = ({"test": "data"}, 123)

        site_adapter_mock = Mock(spec=ImplicitGrantSiteAdapter)
        site_adapter_mock.user_has_denied_access.return_value = False
        site_adapter_mock.authenticate.return_value = test_data

        auth_mixin = AuthorizeMixin(site_adapter=site_adapter_mock)
        auth_mixin.client = client_mock
        result = auth_mixin.authorize(Mock(spec=Request), Mock(spec=Response),
                                      environ={}, scopes=[])

        self.assertTrue(isinstance(result, tuple))
        self.assertDictEqual(result[0], test_data[0])
        self.assertEqual(result[1], test_data[1])

    def test_authorize_user_not_authenticated(self):
        client_mock = Mock(spec=Client)

        response_mock = Mock(spec=Response)

        site_adapter_mock = Mock(spec=ImplicitGrantSiteAdapter)
        site_adapter_mock.user_has_denied_access.return_value = False
        site_adapter_mock.authenticate.side_effect = UserNotAuthenticated
        site_adapter_mock.render_auth_page.return_value = response_mock

        auth_mixin = AuthorizeMixin(site_adapter=site_adapter_mock)
        auth_mixin.client = client_mock
        result = auth_mixin.authorize(Mock(spec=Request), response_mock,
                                      environ={}, scopes=[])

        self.assertEqual(result, response_mock)


class AuthorizationCodeAuthHandlerTestCase(unittest.TestCase):
    def test_process(self):
        code = "abcd"
        environ = {"session": "data"}
        scopes = ["scope"]
        state = "my%state"
        redirect_uri = "https://callback"
        user_data = {"user_id": 789}

        location_uri = "%s?code=%s&state=%s" % (redirect_uri, code, quote(state))

        auth_code_store_mock = Mock(spec=AuthCodeStore)

        client = Client(identifier="abc", secret="xyz",
                        redirect_uris=[redirect_uri])

        response_mock = Mock(spec=Response)

        request_mock = Mock(spec=Request)

        scope_handler_mock = Mock(Scope)
        scope_handler_mock.scopes = scopes
        scope_handler_mock.send_back = False

        site_adapter_mock = Mock(spec=AuthorizationCodeGrantSiteAdapter)
        site_adapter_mock.authenticate.return_value = user_data
        site_adapter_mock.user_has_denied_access.return_value = False

        token_generator_mock = Mock(spec=["generate"])
        token_generator_mock.generate.return_value = code

        handler = AuthorizationCodeAuthHandler(
            auth_token_store=auth_code_store_mock,
            client_authenticator=Mock(), scope_handler=scope_handler_mock,
            site_adapter=site_adapter_mock,
            token_generator=token_generator_mock
        )

        handler.client = client
        handler.state = state
        response = handler.process(request_mock, response_mock, environ)

        token_generator_mock.generate.assert_called_with()
        site_adapter_mock.authenticate.assert_called_with(request_mock,
                                                          environ, scopes,
                                                          client)
        self.assertTrue(auth_code_store_mock.save_code.called)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.body, "")
        response_mock.add_header.assert_called_with("Location", location_uri)

    def test_process_not_confirmed(self):
        """
        AuthorizationCodeAuthHandler.process should call SiteAdapter.render_auth_page if the user could not be authenticated
        """
        environ = {"session": "data"}
        response_mock = Mock(spec=Response)
        scopes = ["scopes"]

        client_mock = Mock(spec=Client)

        request_mock = Mock(spec=Request)

        scope_handler_mock = Mock(Scope)
        scope_handler_mock.scopes = scopes

        site_adapter_mock = Mock(spec=AuthorizationCodeGrantSiteAdapter)
        site_adapter_mock.authenticate.side_effect = UserNotAuthenticated
        site_adapter_mock.render_auth_page.return_value = response_mock

        handler = AuthorizationCodeAuthHandler(
            auth_token_store=Mock(), client_authenticator=Mock(),
            scope_handler=scope_handler_mock, site_adapter=site_adapter_mock,
            token_generator=Mock()
        )
        handler.client = client_mock
        response = handler.process(request_mock, response_mock, environ)

        site_adapter_mock.render_auth_page.assert_called_with(request_mock,
                                                              response_mock,
                                                              environ,
                                                              scopes,
                                                              client_mock)
        self.assertEqual(response, response_mock)

    def test_redirect_oauth_error(self):
        error_identifier = "eid"
        redirect_uri = "https://callback"

        expected_redirect = "%s?error=%s" % (redirect_uri, error_identifier)

        error_mock = Mock(spec=OAuthInvalidError)
        error_mock.error = error_identifier

        response_mock = Mock(spec=Response)

        handler = AuthorizationCodeAuthHandler(
            auth_token_store=Mock(), client_authenticator=Mock(),
            scope_handler=Mock(), site_adapter=Mock(), token_generator=Mock())
        handler.client = Client(identifier="abc", secret="xyz",
                                redirect_uris=["https://callback"])
        result = handler.handle_error(error_mock, response_mock)

        response_mock.add_header.assert_called_with("Location",
                                                    expected_redirect)
        response_mock.status_code = 302
        response_mock.body = ""
        self.assertEqual(result, response_mock)


class AuthorizationCodeTokenHandlerTestCase(unittest.TestCase):
    def test_read_validate_params(self):
        client_id = "abc"
        client_secret = "t%gH"
        code = "defg"
        data = {"additional": "data"}
        redirect_uri = "http://callback"
        scopes = ["scope"]
        user_id = 123

        auth_code = Mock(AuthorizationCode)
        auth_code.code = code
        auth_code.data = data
        auth_code.is_expired.return_value = False
        auth_code.redirect_uri = redirect_uri
        auth_code.scopes = scopes
        auth_code.user_id = user_id

        auth_code_store_mock = Mock(spec=AuthCodeStore)
        auth_code_store_mock.fetch_by_code.return_value = auth_code

        client = Client(identifier=client_id, secret=client_secret,
                        redirect_uris=[redirect_uri])

        client_auth_mock = Mock(spec=ClientAuthenticator)
        client_auth_mock.by_identifier_secret.return_value = client

        request_mock = Mock(spec=Request)
        request_mock.post_param.side_effect = [code, redirect_uri]

        handler = AuthorizationCodeTokenHandler(
            access_token_store=Mock(spec=AccessTokenStore),
            auth_token_store=auth_code_store_mock,
            client_authenticator=client_auth_mock,
            token_generator=Mock())

        result = handler.read_validate_params(request_mock)

        request_mock.post_param.assert_has_calls([call("code"),
                                                  call("redirect_uri")])
        auth_code_store_mock.fetch_by_code.assert_called_with(code)
        self.assertEqual(handler.client, client)
        self.assertEqual(handler.code, code)
        self.assertEqual(handler.data, data)
        self.assertEqual(handler.redirect_uri, redirect_uri)
        self.assertEqual(handler.scopes, scopes)
        self.assertEqual(handler.user_id, user_id)
        self.assertTrue(result)

    def test_read_validate_params_missing_code(self):
        client_id = "abc"
        client_secret = "t%gH"
        code = None
        redirect_uri = "http://callback"

        client = Client(identifier=client_id, secret=client_secret,
                        redirect_uris=[redirect_uri])

        client_auth_mock = Mock(spec=ClientAuthenticator)
        client_auth_mock.by_identifier_secret.return_value = client

        request_mock = Mock(spec=Request)
        request_mock.post_param.side_effect = [code, redirect_uri]

        handler = AuthorizationCodeTokenHandler(
            access_token_store=Mock(spec=AccessTokenStore),
            auth_token_store=Mock(spec=AuthCodeStore),
            client_authenticator=client_auth_mock,
            token_generator=Mock())

        with self.assertRaises(OAuthInvalidError) as expected:
            handler.read_validate_params(request_mock)

        error = expected.exception

        self.assertEqual(error.error, "invalid_request")
        self.assertEqual(error.explanation,
                         "Missing required parameter in request")

    def test_read_validate_params_unknown_code(self):
        client_id = "abc"
        client_secret = "t%gH"
        code_expected = "defg"
        code_actual = "xyz"
        redirect_uri = "http://callback"

        auth_code_mock = Mock(AuthorizationCode)
        auth_code_mock.code = code_expected

        auth_code_store_mock = Mock(spec=AuthCodeStore)
        auth_code_store_mock.fetch_by_code.return_value = auth_code_mock

        client = Client(identifier=client_id, secret=client_secret,
                        redirect_uris=[redirect_uri])

        client_auth_mock = Mock(spec=ClientAuthenticator)
        client_auth_mock.by_identifier_secret.return_value = client

        request_mock = Mock(spec=Request)
        request_mock.post_param.side_effect = [code_actual, redirect_uri]

        handler = AuthorizationCodeTokenHandler(
            access_token_store=Mock(spec=AccessTokenStore),
            auth_token_store=auth_code_store_mock,
            client_authenticator=client_auth_mock,
            token_generator=Mock())

        with self.assertRaises(OAuthInvalidError) as expected:
            handler.read_validate_params(request_mock)

        error = expected.exception

        self.assertEqual(error.error, "invalid_grant")
        self.assertEqual(error.explanation,
                         "Invalid code parameter in request")

    def test_read_validate_params_no_auth_code_found(self):
        client_id = "abc"
        client_secret = "t%gH"
        code = "xyz"
        redirect_uri = "http://callback"

        auth_code_store_mock = Mock(spec=AuthCodeStore)
        auth_code_store_mock.fetch_by_code.side_effect = AuthCodeNotFound

        client = Client(identifier=client_id, secret=client_secret,
                        redirect_uris=[redirect_uri])

        client_auth_mock = Mock(spec=ClientAuthenticator)
        client_auth_mock.by_identifier_secret.return_value = client

        request_mock = Mock(spec=Request)
        request_mock.post_param.side_effect = [code, redirect_uri]

        handler = AuthorizationCodeTokenHandler(
            access_token_store=Mock(spec=AccessTokenStore),
            auth_token_store=auth_code_store_mock,
            client_authenticator=client_auth_mock,
            token_generator=Mock())

        with self.assertRaises(OAuthInvalidError) as expected:
            handler.read_validate_params(request_mock)

        error = expected.exception

        self.assertEqual(error.error, "invalid_request")
        self.assertEqual(error.explanation,
                         "Invalid authorization code parameter")

    def test_read_validate_params_wrong_redirect_uri_in_code_data(self):
        client_id = "abc"
        code = "xyz"
        redirect_uri_actual = "http://invalid-callback"
        redirect_uri_expected = "http://callback"

        auth_code_mock = Mock(AuthorizationCode)
        auth_code_mock.code = code
        auth_code_mock.redirect_uri = redirect_uri_actual

        auth_code_store_mock = Mock(spec=AuthCodeStore)
        auth_code_store_mock.fetch_by_code.return_value = auth_code_mock

        client = Client(identifier=client_id, secret="xyz",
                        redirect_uris=[redirect_uri_expected])

        client_auth_mock = Mock(spec=ClientAuthenticator)
        client_auth_mock.by_identifier_secret.return_value = client

        request_mock = Mock(spec=Request)
        request_mock.post_param.side_effect = [code, redirect_uri_expected]

        handler = AuthorizationCodeTokenHandler(
            access_token_store=Mock(spec=AccessTokenStore),
            auth_token_store=auth_code_store_mock,
            client_authenticator=client_auth_mock,
            token_generator=Mock())

        with self.assertRaises(OAuthInvalidError) as expected:
            handler.read_validate_params(request_mock)

        error = expected.exception

        self.assertEqual(error.error, "invalid_request")
        self.assertEqual(error.explanation, "Invalid redirect_uri parameter")

    def test_read_validate_params_token_expired(self):
        client_id = "abc"
        client_secret = "t%gH"
        code = "xyz"
        redirect_uri = "http://callback"

        auth_code_mock = Mock(AuthorizationCode)
        auth_code_mock.code = code
        auth_code_mock.redirect_uri = redirect_uri
        auth_code_mock.is_expired.return_value = True

        auth_code_store_mock = Mock(spec=AuthCodeStore)
        auth_code_store_mock.fetch_by_code.return_value = auth_code_mock

        client = Client(identifier=client_id, secret=client_secret,
                        redirect_uris=[redirect_uri])

        client_auth_mock = Mock(spec=ClientAuthenticator)
        client_auth_mock.by_identifier_secret.return_value = client

        request_mock = Mock(spec=Request)
        request_mock.post_param.side_effect = [code, redirect_uri]

        handler = AuthorizationCodeTokenHandler(
            access_token_store=Mock(spec=AccessTokenStore),
            auth_token_store=auth_code_store_mock,
            client_authenticator=client_auth_mock,
            token_generator=Mock())

        with self.assertRaises(OAuthInvalidError) as expected:
            handler.read_validate_params(request_mock)

        error = expected.exception

        self.assertEqual(error.error, "invalid_grant")
        self.assertEqual(error.explanation, "Authorization code has expired")

    def test_process_no_refresh_token(self):
        client_id = "efg"
        data = {"additional": "data"}
        scopes = ["scope:one", "scope:two"]
        token_data = {"access_token": "abcd", "token_type": "Bearer"}

        response_body = copy(token_data)
        response_body["scope"] = " ".join(scopes)

        access_token_store_mock = Mock(spec=AccessTokenStore)
        auth_code_store_mock = Mock(spec=AuthCodeStore)
        client_auth_mock = Mock(spec=ClientStore)

        token_generator_mock = Mock(spec=TokenGenerator)
        token_generator_mock.create_access_token_data.return_value = token_data

        response_mock = Mock(spec=Response)
        response_mock.body = None
        response_mock.status_code = None

        handler = AuthorizationCodeTokenHandler(
            access_token_store=access_token_store_mock,
            auth_token_store=auth_code_store_mock,
            client_authenticator=client_auth_mock,
            token_generator=token_generator_mock)
        handler.client = Client(identifier=client_id, secret="xyz")
        handler.data = data
        handler.scopes = scopes
        response = handler.process(Mock(spec=Request), response_mock, {})

        self.assertIsNotNone(auth_code_store_mock.delete_code.call_args)
        access_token, = access_token_store_mock.save_token.call_args[0]
        self.assertTrue(isinstance(access_token, AccessToken))
        self.assertEqual(access_token.data, data)
        self.assertEqual(access_token.grant_type, "authorization_code")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, json.dumps(token_data))
        response_mock.add_header.assert_has_calls([call("Content-Type",
                                                        "application/json"),
                                                   call("Cache-Control",
                                                        "no-store"),
                                                   call("Pragma", "no-cache")])

    @patch("time.time", mock_time)
    def test_process_with_refresh_token(self):
        token_data = {"access_token": "abcd", "token_type": "Bearer",
                      "refresh_token": "wxyz", "expires_in": 600}
        client_id = "efg"
        data = {"additional": "data"}
        scopes = ["scope"]

        access_token_store_mock = Mock(spec=AccessTokenStore)
        auth_code_store_mock = Mock(spec=AuthCodeStore)
        client_auth_mock = Mock(spec=ClientAuthenticator)

        token_generator_mock = Mock(spec=TokenGenerator)
        token_generator_mock.create_access_token_data.return_value = token_data
        token_generator_mock.refresh_expires_in = 10000

        response_mock = Mock(spec=Response)
        response_mock.body = None
        response_mock.status_code = None

        handler = AuthorizationCodeTokenHandler(
            access_token_store=access_token_store_mock,
            auth_token_store=auth_code_store_mock,
            client_authenticator=client_auth_mock,
            token_generator=token_generator_mock)
        handler.client = Client(identifier=client_id, secret="xyz")
        handler.data = data
        handler.scopes = scopes
        response = handler.process(Mock(spec=Request), response_mock, {})

        self.assertIsNotNone(auth_code_store_mock.delete_code.call_args)
        access_token, = access_token_store_mock.save_token.call_args[0]
        self.assertTrue(isinstance(access_token, AccessToken))
        self.assertEqual(access_token.data, data)
        self.assertEqual(access_token.grant_type, "authorization_code")
        self.assertEqual(access_token.expires_at, 1600)
        self.assertEqual(access_token.refresh_token,
                         token_data["refresh_token"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, json.dumps(token_data))
        response_mock.add_header.assert_has_calls([call("Content-Type",
                                                        "application/json"),
                                                   call("Cache-Control",
                                                        "no-store"),
                                                   call("Pragma", "no-cache")])

    @patch("time.time", mock_time)
    def test_process_with_unique_access_token(self):
        token_data = {"client_id": "myclient",
                      "grant_type": "authorization_code",
                      "token": "abc123", "data": {}, "expires_at": 1100,
                      "refresh_token": "def456", "scopes": ["foo", "bar"],
                      "user_id": 123}
        token = AccessToken(**token_data)
        expected_response_body = {"access_token": token_data["token"],
                                  "token_type": "Bearer",
                                  "refresh_token": token_data["refresh_token"],
                                  "expires_in": 100, "scope": "foo bar"}

        access_token_store_mock = Mock(spec=AccessTokenStore)
        access_token_store_mock.fetch_existing_token_of_user.return_value = token

        response = Response()

        handler = AuthorizationCodeTokenHandler(
            access_token_store=access_token_store_mock,
            auth_token_store=Mock(spec=AuthCodeStore),
            client_authenticator=Mock(spec=ClientAuthenticator),
            token_generator=Mock())
        handler.client = Client(identifier=token_data["client_id"],
                                secret="xyz")
        handler.data = {}
        handler.scopes = ["foo", "bar"]
        handler.unique_token = True
        handler.user_id = 123

        response = handler.process(request=Mock(spec=Request),
                                   response=response, environ={})
        self.assertDictEqual(json.loads(response.body),
                             expected_response_body)

    @patch("time.time", mock_time)
    def test_process_with_unique_access_token_not_found(self):
        token_data = {"access_token": "abc123", "token_type": "Bearer",
                      "refresh_token": "def456", "expires_in": 1000}
        expected_response_body = copy(token_data)
        expected_response_body["scope"] = "foo bar"

        response = Response()

        access_token_store_mock = Mock(spec=AccessTokenStore)
        access_token_store_mock.fetch_existing_token_of_user. \
            side_effect = AccessTokenNotFound

        token_generator_mock = Mock(spec=TokenGenerator)
        token_generator_mock.refresh_expires_in = 10000
        token_generator_mock.create_access_token_data. \
            return_value = token_data

        handler = AuthorizationCodeTokenHandler(
            access_token_store=access_token_store_mock,
            auth_token_store=Mock(spec=AuthCodeStore),
            client_authenticator=Mock(spec=ClientAuthenticator),
            token_generator=token_generator_mock)
        handler.client = Client(identifier="abc", secret="xyz")
        handler.unique_token = True
        handler.user_id = 123
        handler.scopes = ["foo", "bar"]

        response_result = handler.process(Mock(), response, {})
        self.assertDictEqual(expected_response_body,
                             json.loads(response_result.body))

    def test_process_with_unique_access_token_different_scope(self):
        access_token_data = {"client_id": "myclient",
                             "grant_type": "authorization_code",
                             "token": "xyz890", "data": {}, "expires_at": 1200,
                             "refresh_token": "mno789", "scopes": ["foo", "bar"],
                             "user_id": 123}
        access_token = AccessToken(**access_token_data)
        token_data = {"access_token": "abc123", "token_type": "Bearer",
                      "refresh_token": "def456", "expires_in": 1000}
        expected_response_body = copy(token_data)
        expected_response_body["scope"] = "bar baz"

        response = Response()

        access_token_store_mock = Mock(spec=AccessTokenStore)
        access_token_store_mock.fetch_existing_token_of_user.return_value = access_token

        token_generator_mock = Mock(spec=TokenGenerator)
        token_generator_mock.create_access_token_data.return_value = token_data
        token_generator_mock.refresh_expires_in = 10000

        handler = AuthorizationCodeTokenHandler(
            access_token_store=access_token_store_mock,
            auth_token_store=Mock(spec=AuthCodeStore),
            client_authenticator=Mock(spec=ClientAuthenticator),
            token_generator=token_generator_mock)
        handler.client = Client(identifier=access_token_data["client_id"],
                                secret="xyz")
        handler.data = {}
        handler.unique_token = True
        handler.user_id = 123
        handler.scopes = ["bar", "baz"]

        response_result = handler.process(Mock(), response, {})
        self.assertDictEqual(expected_response_body,
                             json.loads(response_result.body))

    @patch("time.time", mock_time)
    def test_process_with_unique_access_token_expired_token(self):
        access_token_data = {"client_id": "myclient",
                             "grant_type": "authorization_code",
                             "token": "xyz890", "data": {}, "expires_at": 300,
                             "refresh_token": "mno789", "scopes": ["foo", "bar"],
                             "user_id": 123}
        access_token = AccessToken(**access_token_data)
        token_data = {"access_token": "abc123", "token_type": "Bearer",
                      "refresh_token": "def456", "expires_in": 1000}
        expected_response_body = copy(token_data)
        expected_response_body["scope"] = "foo bar"

        response = Response()

        access_token_store_mock = Mock(spec=AccessTokenStore)
        access_token_store_mock.fetch_existing_token_of_user.return_value = access_token

        token_generator_mock = Mock(spec=TokenGenerator)
        token_generator_mock.create_access_token_data.return_value = token_data
        token_generator_mock.refresh_expires_in = 10000

        handler = AuthorizationCodeTokenHandler(
            access_token_store=access_token_store_mock,
            auth_token_store=Mock(spec=AuthCodeStore),
            client_authenticator=Mock(spec=ClientAuthenticator),
            token_generator=token_generator_mock)
        handler.client = Client(identifier=access_token_data["client_id"],
                                secret="xyz")
        handler.data = {}
        handler.unique_token = True
        handler.user_id = 123
        handler.scopes = ["foo", "bar"]

        response_result = handler.process(Mock(), response, {})
        self.assertDictEqual(expected_response_body,
                             json.loads(response_result.body))

    def test_process_with_unique_access_token_no_user_id(self):
        handler = AuthorizationCodeTokenHandler(
            access_token_store=Mock(spec=AccessTokenStore),
            auth_token_store=Mock(spec=AuthCodeStore),
            client_authenticator=Mock(spec=ClientAuthenticator),
            token_generator=Mock(spec=TokenGenerator))
        handler.client = Client(identifier="abc", secret="xyz")
        handler.unique_token = True
        handler.user_id = None

        with self.assertRaises(UserIdentifierMissingError):
            handler.process(Mock(), Mock(), {})


class ImplicitGrantTestCase(unittest.TestCase):
    def test_create_matching_response_type(self):
        path = "/auth"

        request_mock = Mock(spec=Request)
        request_mock.path = path
        request_mock.get_param.return_value = "token"

        token_generator_mock = Mock()

        server_mock = Mock()
        server_mock.authorize_path = path
        server_mock.client_authenticator = Mock()
        server_mock.token_generator = token_generator_mock

        factory = ImplicitGrant(site_adapter=ImplicitGrantSiteAdapter())
        result_class = factory(request_mock, server_mock)

        request_mock.get_param.assert_called_with("response_type")
        self.assertTrue(isinstance(result_class, ImplicitGrantHandler))

    def test_create_not_matching_response_type(self):
        request_mock = Mock(spec=Request)
        request_mock.get_param.return_value = "something"

        server_mock = Mock()

        factory = ImplicitGrant(site_adapter=ImplicitGrantSiteAdapter())
        result_class = factory(request_mock, server_mock)

        request_mock.get_param.assert_called_with("response_type")
        self.assertEqual(result_class, None)


class ImplicitGrantHandlerTestCase(unittest.TestCase):
    def test_process_redirect_with_token(self):
        environ = {"session": "data"}
        redirect_uri = "http://callback"
        scopes = ["scopes"]
        token = "tokencode"
        user_data = ({}, 1)

        access_token_store_mock = Mock(spec=AccessTokenStore)

        client = Client(identifier="abc", secret="xyz",
                        redirect_uris=[redirect_uri])

        request_mock = Mock(spec=Request)

        responseMock = Mock(spec=Response)

        scope_handler_mock = Mock(Scope)
        scope_handler_mock.scopes = scopes
        scope_handler_mock.send_back = False

        site_adapter_mock = Mock(spec=ImplicitGrantSiteAdapter)
        site_adapter_mock.authenticate.return_value = user_data

        token_generator_mock = Mock(spec=["generate"])
        token_generator_mock.generate.return_value = token

        redirect_uri_with_token = "%s#access_token=%s&token_type=bearer" % (redirect_uri, token)

        handler = ImplicitGrantHandler(
            access_token_store=access_token_store_mock,
            client_authenticator=Mock(), scope_handler=scope_handler_mock,
            site_adapter=site_adapter_mock,
            token_generator=token_generator_mock)
        handler.client = client
        result_response = handler.process(request_mock, responseMock, environ)

        site_adapter_mock.authenticate.assert_called_with(request_mock,
                                                          environ, scopes,
                                                          client)

        access_token, = access_token_store_mock.save_token.call_args[0]
        self.assertTrue(isinstance(access_token, AccessToken))
        self.assertEqual(access_token.grant_type, "implicit")

        responseMock.add_header.assert_called_with("Location",
                                                   redirect_uri_with_token)
        self.assertEqual(responseMock.status_code, 302)
        self.assertEqual(responseMock.content, "")
        self.assertEqual(result_response, responseMock)

    def test_process_redirect_with_state(self):
        """
        ImplicitGrantHandler should include the value of the "state" query parameter from request in redirect
        """
        redirect_uri = "http://callback"
        state = "XH%GFI"
        token = "tokencode"
        user_data = ({}, 1)

        expected_redirect_uri = "%s#access_token=%s&token_type=bearer&state=%s" % (redirect_uri, token, quote(state))

        response_mock = Mock(spec=Response)

        scope_handler_mock = Mock(Scope)
        scope_handler_mock.scopes = []
        scope_handler_mock.send_back = False

        site_adapter_mock = Mock(spec=ImplicitGrantSiteAdapter)
        site_adapter_mock.authenticate.return_value = user_data

        token_generator_mock = Mock(spec=["generate"])
        token_generator_mock.generate.return_value = token

        handler = ImplicitGrantHandler(
            access_token_store=Mock(AccessTokenStore),
            client_authenticator=Mock(), scope_handler=scope_handler_mock,
            site_adapter=site_adapter_mock,
            token_generator=token_generator_mock)
        handler.client = Client(identifier="abc", secret="xyz",
                                redirect_uris=[redirect_uri])
        handler.state = state

        result_response = handler.process(request=Mock(spec=Request),
                                          response=response_mock, environ={})

        response_mock.add_header.assert_called_with("Location",
                                                    expected_redirect_uri)
        self.assertEqual(response_mock.status_code, 302)
        self.assertEqual(response_mock.content, "")
        self.assertEqual(result_response, response_mock)

    def test_process_with_scope(self):
        client_id = "abc"
        redirect_uri = "http://callback"
        scopes = ["scope_read", "scope_write"]
        scopes_uri = "%20".join(scopes)
        state = "XHGFI"
        token = "tokencode"

        expected_redirect_uri = "%s#access_token=%s&token_type=bearer&state=%s&scope=%s" % (
            redirect_uri, token, state, scopes_uri)

        response_mock = Mock(spec=Response)

        scope_handler_mock = Mock(Scope)
        scope_handler_mock.scopes = scopes
        scope_handler_mock.send_back = True

        site_adapter_mock = Mock(spec=ImplicitGrantSiteAdapter)
        site_adapter_mock.authenticate.return_value = ({}, 1)

        token_generator_mock = Mock(spec=["generate"])
        token_generator_mock.generate.return_value = token

        handler = ImplicitGrantHandler(
            access_token_store=Mock(AccessTokenStore),
            client_authenticator=Mock(), scope_handler=scope_handler_mock,
            site_adapter=site_adapter_mock,
            token_generator=token_generator_mock)
        handler.client = Client(identifier="abc", secret="xyz",
                                redirect_uris=[redirect_uri])
        handler.state = state

        result_response = handler.process(request=Mock(spec=Request),
                                          response=response_mock, environ={})

        response_mock.add_header.assert_called_with("Location",
                                                    expected_redirect_uri)
        self.assertEqual(response_mock.status_code, 302)
        self.assertEqual(response_mock.content, "")
        self.assertEqual(result_response, response_mock)

    def test_process_unconfirmed(self):
        scopes = ["scopes"]
        environ = {"session": "data"}

        client_mock = Mock(spec=Client)

        request_mock = Mock(spec=Request)

        response_mock = Mock(spec=Response)

        scope_handler_mock = Mock(Scope)
        scope_handler_mock.scopes = scopes

        site_adapter_mock = Mock(spec=ImplicitGrantSiteAdapter)
        site_adapter_mock.authenticate.side_effect = UserNotAuthenticated
        site_adapter_mock.render_auth_page.return_value = response_mock

        handler = ImplicitGrantHandler(
            Mock(spec=AccessTokenStore), client_authenticator=Mock(),
            scope_handler=scope_handler_mock, site_adapter=site_adapter_mock,
            token_generator=Mock()
        )
        handler.client = client_mock
        result_response = handler.process(request_mock, response_mock, environ)

        site_adapter_mock.authenticate.assert_called_with(request_mock,
                                                          environ, scopes,
                                                          client_mock)
        site_adapter_mock.render_auth_page.assert_called_with(request_mock,
                                                              response_mock,
                                                              environ,
                                                              scopes,
                                                              client_mock)
        self.assertEqual(result_response, response_mock)

    def test_process_user_denied_access(self):
        request_mock = Mock(spec=Request)

        responseMock = Mock(spec=Response)

        scope_handler_mock = Mock(spec=Scope)
        scope_handler_mock.scopes = []

        site_adapter_mock = Mock(spec=ImplicitGrantSiteAdapter)
        site_adapter_mock.user_has_denied_access.return_value = True

        handler = ImplicitGrantHandler(
            Mock(spec=AccessTokenStore), client_authenticator=Mock(),
            scope_handler=scope_handler_mock, site_adapter=site_adapter_mock,
            token_generator=Mock()
        )

        with self.assertRaises(OAuthInvalidError) as expected:
            handler.process(request_mock, responseMock, {})

        e = expected.exception

        site_adapter_mock.user_has_denied_access.assert_called_with(
            request_mock
        )
        self.assertEqual(e.error, "access_denied")
        self.assertEqual(e.explanation, "Authorization denied by user")

    def test_redirect_oauth_error(self):
        error_code = "error_code"
        redirect_uri = "https://callback"
        expected_redirect_location = "%s#error=%s" % (redirect_uri, error_code)

        error_mock = Mock(spec=OAuthInvalidError)
        error_mock.error = error_code

        request_mock = Mock(spec=Request)

        response_mock = Mock(spec=Response)

        handler = ImplicitGrantHandler(
            Mock(spec=AccessTokenStore),
            client_authenticator=Mock(), scope_handler=Mock(Scope),
            site_adapter=Mock(), token_generator=Mock())
        handler.client = Client(identifier="abc", secret="xyz",
                                redirect_uris=[redirect_uri])
        altered_response = handler.handle_error(error_mock,
                                                response_mock)

        response_mock.add_header.assert_called_with(
            "Location",
            expected_redirect_location)
        self.assertEqual(altered_response.status_code, 302)
        self.assertEqual(altered_response.body, "")


class ResourceOwnerGrantTestCase(unittest.TestCase):
    def test_call(self):
        request_mock = Mock(Request)
        request_mock.post_param.return_value = "password"

        access_token_store_mock = Mock(AccessTokenStore)
        token_generator_mock = Mock()

        server_mock = Mock(Provider)
        server_mock.access_token_store = access_token_store_mock
        server_mock.client_authenticator = Mock(ClientAuthenticator)
        server_mock.token_generator = token_generator_mock

        factory = ResourceOwnerGrant(
            site_adapter=ResourceOwnerGrantSiteAdapter()
        )

        handler = factory(request_mock, server_mock)

        request_mock.post_param.assert_called_with("grant_type")
        self.assertTrue(isinstance(handler, ResourceOwnerGrantHandler))

    def test_call_no_resource_request(self):
        request_mock = Mock(Request)
        request_mock.post_param.return_value = "other"

        server_mock = Mock(Provider)

        factory = ResourceOwnerGrant(
            site_adapter=ResourceOwnerGrantSiteAdapter()
        )

        handler = factory(request_mock, server_mock)

        request_mock.post_param.assert_called_with("grant_type")
        self.assertEqual(handler, None)


class ResourceOwnerGrantHandlerTestCase(unittest.TestCase):
    def test_process(self):
        access_token = "0aef"
        client = Client(identifier="abc", secret="xyz")
        expected_response_body = {"access_token": access_token,
                                  "token_type": "Bearer"}
        scopes = ["scope"]
        token_data = {"access_token": access_token, "token_type": "Bearer"}
        user = {"id": 123}

        access_token_store_mock = Mock(AccessTokenStore)

        request_mock = Mock(Request)

        response_mock = Mock(Response)

        scope_handler_mock = Mock(Scope)
        scope_handler_mock.scopes = scopes
        scope_handler_mock.send_back = False

        site_adapter_mock = Mock(spec=ResourceOwnerGrantSiteAdapter)
        site_adapter_mock.authenticate.return_value = user

        token_generator_mock = Mock(spec=TokenGenerator)
        token_generator_mock.create_access_token_data.return_value = token_data

        handler = ResourceOwnerGrantHandler(
            access_token_store=access_token_store_mock,
            client_authenticator=Mock(ClientAuthenticator),
            scope_handler=scope_handler_mock,
            site_adapter=site_adapter_mock,
            token_generator=token_generator_mock)
        handler.client = client
        result = handler.process(request_mock, response_mock, {})

        site_adapter_mock.authenticate.assert_called_with(request_mock, {},
                                                          scopes, client)
        token_generator_mock.create_access_token_data.assert_called_with(ResourceOwnerGrant.grant_type)
        access_token, = access_token_store_mock.save_token.call_args[0]
        self.assertTrue(isinstance(access_token, AccessToken))
        self.assertEqual(access_token.grant_type,
                         ResourceOwnerGrant.grant_type)
        response_mock.add_header.assert_has_calls([call("Content-Type",
                                                        "application/json"),
                                                   call("Cache-Control",
                                                        "no-store"),
                                                   call("Pragma", "no-cache")])
        self.assertEqual(result.status_code, 200)
        self.assertEqual(json.loads(result.body), expected_response_body)
        self.assertEqual(result, response_mock)

    @patch("time.time", mock_time)
    def test_process_with_refresh_token(self):
        access_token = "0aef"
        client = Client(identifier="abc", secret="xyz")
        expected_response_body = {"access_token": access_token,
                                  "token_type": "Bearer",
                                  "refresh_token": "wxyz", "expires_in": 600}
        scopes = ["scope"]
        token_data = {"access_token": access_token, "token_type": "Bearer",
                      "refresh_token": "wxyz", "expires_in": 600}
        user = ({"test": "data"}, 123)

        access_token_store_mock = Mock(AccessTokenStore)

        request_mock = Mock(Request)

        response_mock = Mock(Response)

        scope_handler_mock = Mock(Scope)
        scope_handler_mock.scopes = scopes
        scope_handler_mock.send_back = False

        site_adapter_mock = Mock(spec=ResourceOwnerGrantSiteAdapter)
        site_adapter_mock.authenticate.return_value = user

        token_generator_mock = Mock(spec=TokenGenerator)
        token_generator_mock.create_access_token_data.return_value = token_data
        token_generator_mock.refresh_expires_in = 1200

        handler = ResourceOwnerGrantHandler(
            access_token_store=access_token_store_mock,
            client_authenticator=Mock(ClientAuthenticator),
            scope_handler=scope_handler_mock,
            site_adapter=site_adapter_mock,
            token_generator=token_generator_mock)
        handler.client = client
        result = handler.process(request_mock, response_mock, {})

        site_adapter_mock.authenticate.assert_called_with(request_mock, {},
                                                          scopes, client)
        token_generator_mock.create_access_token_data.assert_called_with(ResourceOwnerGrant.grant_type)
        access_token, = access_token_store_mock.save_token.call_args[0]
        self.assertTrue(isinstance(access_token, AccessToken))
        self.assertEqual(access_token.user_id, user[1])
        self.assertEqual(access_token.refresh_token, token_data["refresh_token"])
        self.assertEqual(access_token.expires_at, 1600)
        response_mock.add_header.assert_has_calls([call("Content-Type",
                                                        "application/json"),
                                                   call("Cache-Control",
                                                        "no-store"),
                                                   call("Pragma", "no-cache")])
        self.assertEqual(result.status_code, 200)
        self.assertEqual(json.loads(result.body), expected_response_body)
        self.assertEqual(result, response_mock)

    def test_process_redirect_with_scope(self):
        access_token = "0aef"
        scopes = ["scope_read", "scope_write"]
        expected_response_body = {"access_token": access_token,
                                  "token_type": "Bearer",
                                  "scope": " ".join(scopes)}
        token_data = {"access_token": access_token, "token_type": "Bearer"}

        response_mock = Mock(Response)

        site_adapter_mock = Mock(spec=ResourceOwnerGrantSiteAdapter)
        site_adapter_mock.authenticate.return_value = ({"test": "data"}, 123)

        scope_handler_mock = Mock(Scope)
        scope_handler_mock.scopes = scopes
        scope_handler_mock.send_back = True

        token_generator_mock = Mock(spec=TokenGenerator)
        token_generator_mock.create_access_token_data.return_value = token_data

        handler = ResourceOwnerGrantHandler(
            access_token_store=Mock(AccessTokenStore),
            client_authenticator=Mock(ClientAuthenticator),
            scope_handler=scope_handler_mock,
            site_adapter=site_adapter_mock,
            token_generator=token_generator_mock)
        handler.client = Client(identifier="abc", secret="xyz")
        result = handler.process(Mock(Request), response_mock, {})

        token_generator_mock.create_access_token_data.assert_called_with(ResourceOwnerGrant.grant_type)
        response_mock.add_header.assert_has_calls([call("Content-Type",
                                                        "application/json"),
                                                   call("Cache-Control",
                                                        "no-store"),
                                                   call("Pragma", "no-cache")])
        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(expected_response_body, json.loads(result.body))
        self.assertEqual(result, response_mock)

    def test_process_invalid_user(self):
        response_mock = Mock(Response)

        scope_handler_mock = Mock(Scope)
        scope_handler_mock.scopes = ["scopes"]
        scope_handler_mock.send_back = False

        site_adapter_mock = Mock(spec=ResourceOwnerGrantSiteAdapter)

        site_adapter_mock.authenticate.side_effect = UserNotAuthenticated

        handler = ResourceOwnerGrantHandler(
            access_token_store=Mock(AccessTokenStore),
            client_authenticator=Mock(ClientAuthenticator),
            scope_handler=scope_handler_mock,
            site_adapter=site_adapter_mock,
            token_generator=Mock(TokenGenerator))
        handler.client = Client(identifier="abc", secret="xyz")

        with self.assertRaises(OAuthInvalidError) as expected:
            handler.process(Mock(Request), response_mock, {})

        e = expected.exception

        self.assertEqual(e.error, "invalid_client")
        self.assertEqual(e.explanation,
                         ResourceOwnerGrantHandler.OWNER_NOT_AUTHENTICATED)

    def test_read_validate_params(self):
        password = "johnpw"
        username = "johndoe"

        client = Client(identifier="abcd", secret="xyz")

        client_auth_mock = Mock(ClientAuthenticator)
        client_auth_mock.by_identifier_secret.return_value = client

        request_mock = Mock(Request)
        request_mock.post_param.side_effect = [password, username]

        scope_handler_mock = Mock(Scope)

        handler = ResourceOwnerGrantHandler(
            access_token_store=Mock(AccessTokenStore),
            client_authenticator=client_auth_mock,
            scope_handler=scope_handler_mock,
            site_adapter=Mock(spec=ResourceOwnerGrantSiteAdapter),
            token_generator=Mock())
        result = handler.read_validate_params(request_mock)

        client_auth_mock.by_identifier_secret.assert_called_with(request_mock)
        scope_handler_mock.parse.assert_called_with(request=request_mock,
                                                    source="body")

        self.assertEqual(handler.client, client)
        self.assertEqual(handler.username, username)
        self.assertEqual(handler.password, password)
        self.assertTrue(result)

    def test_handle_error_owner_not_authenticated(self):
        error = OAuthInvalidError(
            error="invalid_client",
            explanation=ResourceOwnerGrantHandler.OWNER_NOT_AUTHENTICATED)

        response = Response()

        handler = ResourceOwnerGrantHandler(
            access_token_store=Mock(AccessTokenStore),
            client_authenticator=Mock(),
            scope_handler=Mock(),
            site_adapter=Mock(),
            token_generator=Mock())

        result = handler.handle_error(error, response)

        self.assertEqual(result.status_code, 401)


class ScopeTestCase(unittest.TestCase):
    def test_parse_scope_scope_present_in_query(self):
        """
        Scope.parse should return a list of requested scopes
        """
        expected_scopes = ["friends_read", "user_read"]

        request_mock = Mock(Request)
        request_mock.get_param.return_value = "friends_read user_read"

        scope = Scope(available=["user_read", "friends_write", "friends_read"])

        scope.parse(request=request_mock, source="query")

        request_mock.get_param.assert_called_with("scope")

        self.assertListEqual(expected_scopes, scope.scopes)
        self.assertFalse(scope.send_back)

    def test_parse_scope_scope_present_in_body(self):
        scope = Scope()

        request_mock = Mock(Request)
        request_mock.post_param.return_value = None

        scope.parse(request=request_mock, source="body")

        request_mock.post_param.assert_called_with("scope")

    def test_parse_scope_default_on_no_scope(self):
        """
        Scope.parse should return a list containing the default value if no scope present in request and default is set
        """
        expected_scopes = ["all"]

        request_mock = Mock(Request)
        request_mock.get_param.return_value = None

        scope = Scope(available=["user_read", "friends_write", "friends_read"],
                      default="all")

        scope.parse(request=request_mock, source="query")

        request_mock.get_param.assert_called_with("scope")

        self.assertListEqual(expected_scopes, scope.scopes)
        self.assertTrue(scope.send_back)

    def test_parse_scope_default_on_no_matching_scopes(self):
        """
        Scope.parse should return a list containing the default value if scope in request does not match and default is set
        """
        expected_scopes = ["all"]

        request_mock = Mock(Request)
        request_mock.get_param.return_value = "user_write"

        scope = Scope(available=["user_read", "friends_write", "friends_read"],
                      default="all")

        scope.parse(request=request_mock, source="query")

        request_mock.get_param.assert_called_with("scope")

        self.assertListEqual(expected_scopes, scope.scopes)
        self.assertTrue(scope.send_back)

    def test_parse_scope_no_value_on_no_scope_no_default(self):
        """
        Scope.parse should return an empty list if no scope is present in request and no default or scapes are defined
        """
        expected_scopes = []

        request_mock = Mock(Request)
        request_mock.get_param.return_value = None

        scope = Scope()

        scope.parse(request=request_mock, source="query")

        request_mock.get_param.assert_called_with("scope")

        self.assertEqual(expected_scopes, scope.scopes)
        self.assertFalse(scope.send_back)

    def test_parse_scope_exception_on_available_scopes_no_scope_given(self):
        """
        Scope.parse should throw an OAuthError if no scope is present in request but scopes are defined
        """
        request_mock = Mock(Request)
        request_mock.get_param.return_value = None

        scope = Scope(available=["user_read", "friends_write", "friends_read"])

        with self.assertRaises(OAuthInvalidError) as expected:
            scope.parse(request_mock, source="query")

        e = expected.exception

        self.assertEqual(e.error, "invalid_scope")

    def test_compare_scopes_equal(self):
        """
        Scope.compare should use the same scopes if new and old scopes do not differ
        """
        scope = Scope(available=["a", "b"])

        scope.scopes = ["a", "b"]

        result = scope.compare(["a", "b"])

        self.assertTrue(result)
        self.assertListEqual(scope.scopes, ["a", "b"])

    def test_compare_valid_scope_subset(self):
        """
        Scope.compare should set a new value for scopes attribute if the new scopes are a subset of the previously issued scopes
        """
        scope = Scope(available=["a", "b", "c"])

        scope.scopes = ["b", "c"]

        result = scope.compare(["a", "b", "c"])

        self.assertTrue(result)
        self.assertListEqual(scope.scopes, ["b", "c"])

    def test_compare_invalid_scope_requested(self):
        """
        Scope.compare should thow an error if a scope is requested that is not contained in the previous scopes.
        """
        scope = Scope(available=["a", "b", "c"])

        scope.scopes = ["b", "c"]

        with self.assertRaises(OAuthInvalidError) as expected:
            scope.compare(["a", "b"])

        e = expected.exception

        self.assertEqual(e.error, "invalid_scope")


class RefreshTokenTestCase(unittest.TestCase):
    def test_call(self):
        """
        RefreshToken should create a new instance of RefreshTokenHandler
        """
        path = "/token"
        expires_in = 600

        access_token_store_mock = Mock()
        client_auth_mock = Mock()
        scope_handler_mock = Mock()
        token_generator_mock = Mock()

        controller_mock = Mock(spec=Provider)
        controller_mock.token_path = path
        controller_mock.access_token_store = access_token_store_mock
        controller_mock.client_authenticator = client_auth_mock
        controller_mock.scope_handler = scope_handler_mock
        controller_mock.token_generator = token_generator_mock
        controller_mock.tokens_expire_in = expires_in

        request_mock = Mock(spec=Request)
        request_mock.path = path
        request_mock.post_param.return_value = "refresh_token"

        grant = RefreshToken(expires_in=0)

        grant_handler = grant(request_mock, controller_mock)

        request_mock.post_param.assert_called_with("grant_type")

        self.assertTrue(isinstance(grant_handler, RefreshTokenHandler))
        self.assertTrue(isinstance(grant_handler.scope_handler, Scope))
        self.assertEqual(access_token_store_mock,
                         grant_handler.access_token_store)
        self.assertEqual(client_auth_mock, grant_handler.client_authenticator)
        self.assertEqual(token_generator_mock, grant_handler.token_generator)

    def test_call_wrong_path(self):
        """
        RefreshToken should return 'None' if path in the request does not equal the token path
        """
        controller_mock = Mock(spec=Provider)
        controller_mock.token_path = "/token"

        request_mock = Mock(spec=Request)
        request_mock.path = "/authorize"

        grant = RefreshToken(expires_in=0)

        grant_handler = grant(request_mock, controller_mock)

        self.assertEqual(grant_handler, None)

    def test_call_other_grant_type(self):
        """
        RefreshToken should return 'None' if another grant type is requested
        """
        path = "/token"

        controller_mock = Mock(spec=Provider)
        controller_mock.token_path = path

        request_mock = Mock(spec=Request)
        request_mock.path = path
        request_mock.get_param.return_value = "authorization_code"

        grant = RefreshToken(expires_in=0)

        grant_handler = grant(request_mock, controller_mock)

        self.assertEqual(grant_handler, None)


class RefreshTokenHandlerTestCase(unittest.TestCase):
    @patch("time.time", mock_time)
    def test_process_no_reissue(self):
        client_id = "testclient"
        data = {"additional": "data"}
        expires_in = 600
        scopes = []
        token = "abcdefg"
        expected_response_body = {"access_token": token,
                                  "expires_in": expires_in,
                                  "token_type": "Bearer"}
        expected_headers = {"Content-Type": "application/json",
                            "Cache-Control": "no-store", "Pragma": "no-cache"}

        access_token_store_mock = Mock(spec=AccessTokenStore)

        response = Response()

        scope_handler_mock = Mock(spec=Scope)
        scope_handler_mock.scopes = scopes

        token_data = {"access_token": token, "expires_in": expires_in, "token_type": "Bearer", "refresh_token": "gafc"}
        token_generator_mock = Mock(spec=TokenGenerator)
        token_generator_mock.create_access_token_data.return_value = token_data
        token_generator_mock.refresh_expires_in = 1200

        handler = RefreshTokenHandler(
            access_token_store=access_token_store_mock,
            client_authenticator=Mock(spec=ClientAuthenticator),
            scope_handler=scope_handler_mock,
            token_generator=token_generator_mock)
        handler.client = Client(identifier=client_id, secret="xyz")
        handler.data = data
        handler.refresh_grant_type = 'test_grant_type'

        result = handler.process(request=Mock(spec=Request),
                                 response=response, environ={})

        access_token, = access_token_store_mock.save_token.call_args[0]
        self.assertEqual(access_token.client_id, client_id)
        self.assertEqual(access_token.grant_type, handler.refresh_grant_type)
        self.assertDictEqual(access_token.data, data)
        self.assertEqual(access_token.token, token)
        self.assertListEqual(access_token.scopes, scopes)
        self.assertEqual(access_token.expires_at, 1600)

        self.assertEqual(result, response)
        self.assertDictContainsSubset(expected_headers, result.headers)
        self.assertEqual(json.dumps(expected_response_body), result.body)

    @patch("time.time", mock_time)
    def test_process_with_reissue(self):
        client_id = "testclient"
        data = {"additional": "data"}
        expires_in = 600
        scopes = []
        token = "abcdefg"
        refresh_token = "cefg"
        expected_response_body = {"access_token": token,
                                  "expires_in": expires_in,
                                  "refresh_token": refresh_token,
                                  "token_type": "Bearer"}
        expected_headers = {"Content-Type": "application/json",
                            "Cache-Control": "no-store", "Pragma": "no-cache"}

        access_token_store_mock = Mock(spec=AccessTokenStore)

        response = Response()

        scope_handler_mock = Mock(spec=Scope)
        scope_handler_mock.scopes = scopes

        token_data = {"access_token": token, "expires_in": expires_in, "token_type": "Bearer",
                      "refresh_token": refresh_token}
        token_generator_mock = Mock(spec=TokenGenerator)
        token_generator_mock.create_access_token_data.return_value = token_data
        token_generator_mock.refresh_expires_in = 1200

        handler = RefreshTokenHandler(
            access_token_store=access_token_store_mock,
            client_authenticator=Mock(spec=ClientAuthenticator),
            scope_handler=scope_handler_mock,
            token_generator=token_generator_mock,
            reissue_refresh_tokens=True)
        handler.client = Client(identifier=client_id, secret="xyz")
        handler.data = data
        handler.refresh_grant_type = 'test_grant_type'

        result = handler.process(request=Mock(spec=Request),
                                 response=response, environ={})

        access_token, = access_token_store_mock.save_token.call_args[0]
        self.assertEqual(access_token.client_id, client_id)
        self.assertEqual(access_token.grant_type, handler.refresh_grant_type)
        self.assertDictEqual(access_token.data, data)
        self.assertEqual(access_token.token, token)
        self.assertListEqual(access_token.scopes, scopes)
        self.assertEqual(access_token.expires_at, 1600)

        self.assertEqual(result, response)
        self.assertDictContainsSubset(expected_headers, result.headers)
        self.assertDictEqual(expected_response_body, json.loads(result.body))

    @patch("time.time", mock_time)
    def test_read_validate_params(self):
        client_id = "client"
        client_secret = "secret"
        data = {"additional": "data"}
        original_token = "sd3f3j"
        refresh_token = "s74jf"
        scopes = []

        access_token = AccessToken(client_id=client_id, token=original_token,
                                   grant_type="test_grant_type",
                                   data=data, expires_at=1234, scopes=scopes,
                                   refresh_expires_at=0)

        access_token_store_mock = Mock(AccessTokenStore)
        access_token_store_mock.fetch_by_refresh_token.return_value = access_token

        client = Client(identifier=client_id, secret=client_secret,
                        redirect_uris=[])

        client_auth_mock = Mock(spec=ClientAuthenticator)
        client_auth_mock.by_identifier_secret.return_value = client

        request_mock = Mock(spec=Request)
        request_mock.post_param.side_effect = [refresh_token]

        token_generator_mock = Mock(expires_in={'test_grant_type': 600})
        token_generator_mock.refresh_expires_in = 0

        scope_handler_mock = Mock(spec=Scope)

        handler = RefreshTokenHandler(
            access_token_store=access_token_store_mock,
            client_authenticator=client_auth_mock,
            scope_handler=scope_handler_mock,
            token_generator=token_generator_mock)

        handler.read_validate_params(request=request_mock)

        request_mock.post_param.assert_called_with("refresh_token")
        access_token_store_mock.fetch_by_refresh_token.assert_called_with(refresh_token)
        client_auth_mock.by_identifier_secret.assert_called_with(request_mock)
        scope_handler_mock.parse.assert_called_with(request_mock, "body")
        scope_handler_mock.compare.assert_called_with(scopes)

        self.assertEqual(handler.client, client)
        self.assertEqual(handler.data, data)
        self.assertEqual(handler.refresh_token, refresh_token)

    def test_read_validate_params_no_refresh_token(self):
        request_mock = Mock(spec=Request)
        request_mock.post_param.return_value = None

        handler = RefreshTokenHandler(access_token_store=Mock(),
                                      client_authenticator=Mock(),
                                      scope_handler=Mock(),
                                      token_generator=Mock(expires_in=600))

        with self.assertRaises(OAuthInvalidError) as expected:
            handler.read_validate_params(request_mock)

        e = expected.exception

        self.assertEqual(e.error, "invalid_request")
        self.assertEqual(e.explanation,
                         "Missing refresh_token in request body")

    def test_read_validate_params_invalid_refresh_token(self):
        client_id = "abc"
        secret = "xyz"

        access_token_store_mock = Mock(spec=AccessTokenStore)
        access_token_store_mock.fetch_by_refresh_token.side_effect = AccessTokenNotFound

        request_mock = Mock(spec=Request)
        request_mock.post_param.side_effect = [client_id, secret, "uuu"]

        client = Client(identifier=client_id, secret=secret, redirect_uris=[])

        client_auth_mock = Mock(spec=ClientAuthenticator)
        client_auth_mock.by_identifier_secret.return_value = client

        handler = RefreshTokenHandler(access_token_store=access_token_store_mock,
                                      client_authenticator=client_auth_mock,
                                      scope_handler=Mock(),
                                      token_generator=Mock(expires_in=600))

        with self.assertRaises(OAuthInvalidError) as expected:
            handler.read_validate_params(request_mock)

        e = expected.exception

        self.assertEqual(e.error, "invalid_request")
        self.assertEqual(e.explanation, "Invalid refresh token")

    @patch("time.time", mock_time)
    def test_read_validate_params_expired_refresh_token(self):
        client_id = "abc"
        secret = "xyz"

        access_token_mock = Mock(spec=AccessToken)
        access_token_mock.grant_type = 'test_grant_type'
        access_token_mock.refresh_expires_at = 900

        access_token_store_mock = Mock(spec=AccessTokenStore)
        access_token_store_mock.fetch_by_refresh_token.return_value = access_token_mock

        request_mock = Mock(spec=Request)
        request_mock.post_param.side_effect = [client_id, secret, "uuu"]

        client = Client(identifier=client_id, secret=secret, redirect_uris=[])

        client_auth_mock = Mock(spec=ClientAuthenticator)
        client_auth_mock.by_identifier_secret.return_value = client

        handler = RefreshTokenHandler(
            access_token_store=access_token_store_mock,
            client_authenticator=client_auth_mock,
            scope_handler=Mock(),
            token_generator=Mock(expires_in={'test_grant_type': 600}))

        with self.assertRaises(OAuthInvalidError) as expected:
            handler.read_validate_params(request_mock)

        e = expected.exception

        self.assertEqual(e.error, "invalid_request")
        self.assertEqual(e.explanation, "Invalid refresh token")


class ClientCredentialsGrantTestCase(unittest.TestCase):
    def test_call(self):
        token_path = "token"

        request_mock = Mock(spec=Request)
        request_mock.path = token_path
        request_mock.post_param.return_value = "client_credentials"

        access_token_store_mock = Mock()
        client_auth_mock = Mock()
        token_generator_mock = Mock()

        scope_handler_mock = Mock(spec=Scope)

        server_mock = Mock()
        server_mock.token_path = token_path
        server_mock.access_token_store = access_token_store_mock
        server_mock.client_authenticator = client_auth_mock
        server_mock.scope_handler = scope_handler_mock
        server_mock.token_generator = token_generator_mock

        grant = ClientCredentialsGrant()
        handler = grant(request_mock, server_mock)

        request_mock.post_param.assert_called_with("grant_type")
        self.assertTrue(isinstance(handler, ClientCredentialsHandler))
        self.assertEqual(handler.access_token_store, access_token_store_mock)
        self.assertEqual(handler.client_authenticator, client_auth_mock)
        self.assertTrue(isinstance(handler.scope_handler, Scope))
        self.assertEqual(handler.token_generator, token_generator_mock)

    def test_call_wrong_request_path(self):
        request_mock = Mock(spec=Request)
        request_mock.path = "authorize"

        server_mock = Mock()
        server_mock.token_path = "token"

        grant = ClientCredentialsGrant()
        handler = grant(request_mock, server_mock)

        self.assertEqual(handler, None)

    def test_call_other_grant_type(self):
        token_path = "token"

        request_mock = Mock(spec=Request)
        request_mock.path = token_path
        request_mock.post_param.return_value = "other_grant"

        server_mock = Mock()
        server_mock.token_path = token_path

        grant = ClientCredentialsGrant()
        handler = grant(request_mock, server_mock)

        self.assertEqual(handler, None)


class ClientCredentialsHandlerTestCase(unittest.TestCase):
    def test_process(self):
        client_id = "abc"
        token = "abcd"

        expected_response_body = {"access_token": token,
                                  "token_type": "Bearer"}

        access_token_store_mock = Mock(spec=AccessTokenStore)

        response_mock = Mock(spec=Response)

        scope_handler_mock = Mock(spec=Scope)
        scope_handler_mock.send_back = False
        scope_handler_mock.scopes = []

        token_generator_mock = Mock(spec=TokenGenerator)
        token_generator_mock.generate.return_value = token
        token_generator_mock.expires_in = {}
        handler = ClientCredentialsHandler(
            access_token_store=access_token_store_mock,
            client_authenticator=Mock(),
            scope_handler=scope_handler_mock,
            token_generator=token_generator_mock)
        handler.client = Client(identifier=client_id, secret="xyz")
        result_response = handler.process(request=Mock(),
                                          response=response_mock, environ={})

        self.assertDictEqual(json.loads(result_response.body),
                             expected_response_body)

    @patch("time.time", mock_time)
    def test_process_with_refresh_token(self):
        client_id = "abc"
        expires_in = 600
        token = "abcd"
        scopes = ["foo", "bar"]

        expected_response_body = {"access_token": token,
                                  "expires_in": expires_in,
                                  "token_type": "Bearer",
                                  "scope": " ".join(scopes)}

        access_token_store_mock = Mock(spec=AccessTokenStore)

        response_mock = Mock(spec=Response)

        scope_handler_mock = Mock(spec=Scope)
        scope_handler_mock.send_back = True
        scope_handler_mock.scopes = scopes

        token_generator_mock = Mock(spec=TokenGenerator)
        token_generator_mock.generate.return_value = token
        token_generator_mock.expires_in = {ClientCredentialsGrant.grant_type: expires_in}

        handler = ClientCredentialsHandler(
            access_token_store=access_token_store_mock,
            client_authenticator=Mock(),
            scope_handler=scope_handler_mock,
            token_generator=token_generator_mock)
        handler.client = Client(identifier=client_id, secret="xyz")
        result_response = handler.process(request=Mock(),
                                          response=response_mock, environ={})

        access_token, = access_token_store_mock.save_token.call_args[0]
        self.assertTrue(isinstance(access_token, AccessToken))
        self.assertEqual(access_token.client_id, client_id)
        self.assertEqual(access_token.grant_type, "client_credentials")
        self.assertEqual(access_token.token, token)
        self.assertEqual(access_token.data, {})
        self.assertEqual(access_token.expires_at, expires_in + 1000)
        self.assertEqual(access_token.refresh_token, None)
        self.assertEqual(access_token.scopes, scopes)

        response_mock.add_header.assert_has_calls([call("Content-Type",
                                                        "application/json"),
                                                   call("Cache-Control",
                                                        "no-store"),
                                                   call("Pragma", "no-cache")])
        self.assertDictEqual(json.loads(result_response.body),
                             expected_response_body)

    def test_read_validate_params(self):
        client_id = "abc"
        client_secret = "xyz"

        client_auth_mock = Mock(spec=ClientAuthenticator)
        client_auth_mock.by_identifier_secret.return_value = Client(
            identifier=client_id,
            secret=client_secret,
            redirect_uris=[])

        scope_handler_mock = Mock(spec=Scope)

        request_mock = Mock(spec=Request)

        handler = ClientCredentialsHandler(
            access_token_store=Mock(),
            client_authenticator=client_auth_mock,
            scope_handler=scope_handler_mock,
            token_generator=Mock())
        handler.read_validate_params(request_mock)

        client_auth_mock.by_identifier_secret.assert_called_with(request_mock)
        scope_handler_mock.parse.assert_called_with(request=request_mock,
                                                    source="body")


if __name__ == "__main__":
    unittest.main()
