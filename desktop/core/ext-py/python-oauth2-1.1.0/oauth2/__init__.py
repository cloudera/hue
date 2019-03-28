"""
=============
python-oauth2
=============

python-oauth2 is a framework that aims at making it easy to provide
authentication via `OAuth 2.0 <http://tools.ietf.org/html/rfc6749>`_ within
an application stack.

Usage
=====

Example:

.. literalinclude:: examples/base_server.py

Installation
============

python-oauth2 is available on
`PyPI <http://pypi.python.org/pypi/python-oauth2/>`_::

    pip install python-oauth2

"""

import json
from oauth2.client_authenticator import ClientAuthenticator, request_body
from oauth2.error import OAuthInvalidError, \
    ClientNotFoundError, OAuthInvalidNoRedirectError, UnsupportedGrantError
from oauth2.log import app_log
from oauth2.web import Response
from oauth2.tokengenerator import Uuid4
from oauth2.grant import Scope, AuthorizationCodeGrant, ImplicitGrant, \
    ClientCredentialsGrant, ResourceOwnerGrant, RefreshToken

VERSION = "1.1.0"


class Provider(object):
    """
    Endpoint of requests to the OAuth 2.0 provider.

    :param access_token_store: An object that implements methods defined
                               by :class:`oauth2.store.AccessTokenStore`.
    :type access_token_store: oauth2.store.AccessTokenStore
    :param auth_code_store: An object that implements methods defined by
                            :class:`oauth2.store.AuthCodeStore`.
    :type auth_code_store: oauth2.store.AuthCodeStore
    :param client_store: An object that implements methods defined by
                         :class:`oauth2.store.ClientStore`.
    :type client_store: oauth2.store.ClientStore
    :param token_generator: Object to generate unique tokens.
    :type token_generator: oauth2.tokengenerator.TokenGenerator
    :param client_authentication_source: A callable which when executed,
                                         authenticates a client.
                                         See :mod:`oauth2.client_authenticator`.
    :type client_authentication_source: callable
    :param response_class: Class of the response object.
                           Defaults to :class:`oauth2.web.Response`.
    :type response_class: oauth2.web.Response

    .. versionchanged:: 1.0.0
       Removed parameter ``site_adapter``.
    """
    authorize_path = "/authorize"
    token_path = "/token"

    def __init__(self, access_token_store, auth_code_store, client_store,
                 token_generator, client_authentication_source=request_body,
                 response_class=Response):
        self.grant_types = []
        self._input_handler = None

        self.access_token_store = access_token_store
        self.auth_code_store = auth_code_store
        self.client_authenticator = ClientAuthenticator(
            client_store=client_store,
            source=client_authentication_source)
        self.response_class = response_class
        self.token_generator = token_generator

    def add_grant(self, grant):
        """
        Adds a Grant that the provider should support.

        :param grant: An instance of a class that extends
                      :class:`oauth2.grant.GrantHandlerFactory`
        :type grant: oauth2.grant.GrantHandlerFactory
        """
        if hasattr(grant, "expires_in"):
            self.token_generator.expires_in[grant.grant_type] = grant.expires_in

        if hasattr(grant, "refresh_expires_in"):
            self.token_generator.refresh_expires_in = grant.refresh_expires_in

        self.grant_types.append(grant)

    def dispatch(self, request, environ):
        """
        Checks which Grant supports the current request and dispatches to it.

        :param request: The incoming request.
        :type request: :class:`oauth2.web.Request`
        :param environ: Dict containing variables of the environment.
        :type environ: dict

        :return: An instance of ``oauth2.web.Response``.
        """
        try:
            grant_type = self._determine_grant_type(request)

            response = self.response_class()

            grant_type.read_validate_params(request)

            return grant_type.process(request, response, environ)
        except OAuthInvalidNoRedirectError:
            response = self.response_class()
            response.add_header("Content-Type", "application/json")
            response.status_code = 400
            response.body = json.dumps({
                "error": "invalid_redirect_uri",
                "error_description": "Invalid redirect URI"
            })

            return response
        except OAuthInvalidError as err:
            response = self.response_class()
            return grant_type.handle_error(error=err, response=response)
        except UnsupportedGrantError:
            response = self.response_class()
            response.add_header("Content-Type", "application/json")
            response.status_code = 400
            response.body = json.dumps({
                "error": "unsupported_response_type",
                "error_description": "Grant not supported"
            })

            return response
        except:
            app_log.error("Uncaught Exception", exc_info=True)
            response = self.response_class()
            return grant_type.handle_error(
                error=OAuthInvalidError(error="server_error",
                                        explanation="Internal server error"),
                response=response)

    def enable_unique_tokens(self):
        """
        Enable the use of unique access tokens on all grant types that support
        this option.
        """
        for grant_type in self.grant_types:
            if hasattr(grant_type, "unique_token"):
                grant_type.unique_token = True

    @property
    def scope_separator(self, separator):
        """
        Sets the separator of values in the scope query parameter.
        Defaults to " " (whitespace).

        The following code makes the Provider use "," instead of " "::

            provider = Provider()

            provider.scope_separator = ","

        Now the scope parameter in the request of a client can look like this:
        `scope=foo,bar`.
        """
        Scope.separator = separator

    def _determine_grant_type(self, request):
        for grant in self.grant_types:
            grant_handler = grant(request, self)
            if grant_handler is not None:
                return grant_handler

        raise UnsupportedGrantError
