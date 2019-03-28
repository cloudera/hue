import json
from mock import Mock
from oauth2.error import OAuthInvalidNoRedirectError, OAuthInvalidError
from oauth2.test import unittest
from oauth2 import Provider
from oauth2.store import ClientStore
from oauth2.web import Response, AuthorizationCodeGrantSiteAdapter, \
    ResourceOwnerGrantSiteAdapter
from oauth2.web.wsgi import Request
from oauth2.grant import RefreshToken, AuthorizationCodeGrant, GrantHandler, \
    ResourceOwnerGrant


class ProviderTestCase(unittest.TestCase):
    def setUp(self):
        self.client_store_mock = Mock(spec=ClientStore)
        self.token_generator_mock = Mock()

        self.response_mock = Mock(spec=Response)
        self.response_mock.body = ""
        response_class_mock = Mock(return_value=self.response_mock)

        self.token_generator_mock.expires_in = {}
        self.token_generator_mock.refresh_expires_in = 0

        self.auth_server = Provider(access_token_store=Mock(),
                                    auth_code_store=Mock(),
                                    client_store=self.client_store_mock,
                                    token_generator=self.token_generator_mock,
                                    response_class=response_class_mock)

    def test_add_grant_set_expire_time(self):
        """
        Provider.add_grant() should set the expiration time on the instance of TokenGenerator
        """
        self.auth_server.add_grant(
            AuthorizationCodeGrant(
                expires_in=400,
                site_adapter=Mock(spec=AuthorizationCodeGrantSiteAdapter)
            )
        )
        self.auth_server.add_grant(
            ResourceOwnerGrant(
                expires_in=500,
                site_adapter=Mock(spec=ResourceOwnerGrantSiteAdapter)
            )
        )
        self.auth_server.add_grant(RefreshToken(expires_in=1200))

        self.assertEqual(self.token_generator_mock.expires_in[AuthorizationCodeGrant.grant_type], 400)
        self.assertEqual(self.token_generator_mock.expires_in[ResourceOwnerGrant.grant_type], 500)
        self.assertEqual(self.token_generator_mock.refresh_expires_in, 1200)

    def test_dispatch(self):
        environ = {"session": "data"}
        process_result = "response"

        request_mock = Mock(spec=Request)

        grant_handler_mock = Mock(spec=["process", "read_validate_params"])
        grant_handler_mock.process.return_value = process_result

        grant_factory_mock = Mock(return_value=grant_handler_mock)

        self.auth_server.site_adapter = Mock(
            spec=AuthorizationCodeGrantSiteAdapter
        )
        self.auth_server.add_grant(grant_factory_mock)
        result = self.auth_server.dispatch(request_mock, environ)

        grant_factory_mock.assert_called_with(request_mock, self.auth_server)
        grant_handler_mock.read_validate_params.\
            assert_called_with(request_mock)
        grant_handler_mock.process.assert_called_with(request_mock,
                                                      self.response_mock,
                                                      environ)
        self.assertEqual(result, process_result)

    def test_dispatch_no_grant_type_found(self):
        error_body = {
            "error": "unsupported_response_type",
            "error_description": "Grant not supported"
        }

        request_mock = Mock(spec=Request)

        result = self.auth_server.dispatch(request_mock, {})

        self.response_mock.add_header.assert_called_with("Content-Type",
                                                         "application/json")
        self.assertEqual(self.response_mock.status_code, 400)
        self.assertEqual(self.response_mock.body, json.dumps(error_body))
        self.assertEqual(result, self.response_mock)

    def test_dispatch_no_client_found(self):
        request_mock = Mock(spec=Request)

        grant_handler_mock = Mock(spec=GrantHandler)
        grant_handler_mock.process.side_effect = OAuthInvalidNoRedirectError(
            error="")

        grant_factory_mock = Mock(return_value=grant_handler_mock)

        self.auth_server.add_grant(grant_factory_mock)
        self.auth_server.dispatch(request_mock, {})

        self.response_mock.add_header.assert_called_with("Content-Type",
                                                         "application/json")
        self.assertEqual(self.response_mock.status_code, 400)
        self.assertEqual(json.loads(self.response_mock.body)["error"], "invalid_redirect_uri")

    def test_dispatch_general_exception(self):
        request_mock = Mock(spec=Request)

        grant_handler_mock = Mock(spec=GrantHandler)
        grant_handler_mock.process.side_effect = KeyError

        grant_factory_mock = Mock(return_value=grant_handler_mock)

        self.auth_server.add_grant(grant_factory_mock)
        self.auth_server.dispatch(request_mock, {})

        self.assertTrue(grant_handler_mock.handle_error.called)
