"""
Every client that sends a request to obtain an access token needs to
authenticate with the provider.

The authentication of confidential clients can be handled in several ways,
some of which come bundled with this module.
"""

from base64 import b64decode
from oauth2.error import OAuthInvalidNoRedirectError, RedirectUriUnknown, \
    OAuthInvalidError, ClientNotFoundError


class ClientAuthenticator(object):
    """
    Handles authentication of a client both by its identifier as well as by
    its identifier and secret.

    :param client_store: The Client Store to retrieve a client from.
    :type client_store: oauth2.store.ClientStore
    :param source: A callable that returns a tuple
                   (<client_id>, <client_secret>)
    :type source: callable
    """
    def __init__(self, client_store, source):
        self.client_store = client_store
        self.source = source

    def by_identifier(self, request):
        """
        Authenticates a client by its identifier.

        :param request: The incoming request
        :type request: oauth2.web.Request

        :return: The identified client
        :rtype: oauth2.datatype.Client

        :raises: :class OAuthInvalidNoRedirectError:
        """
        client_id = request.get_param("client_id")

        if client_id is None:
            raise OAuthInvalidNoRedirectError(error="missing_client_id")

        try:
            client = self.client_store.fetch_by_client_id(client_id)
        except ClientNotFoundError:
            raise OAuthInvalidNoRedirectError(error="unknown_client")

        redirect_uri = request.get_param("redirect_uri")
        if redirect_uri is not None:
            try:
                client.redirect_uri = redirect_uri
            except RedirectUriUnknown:
                raise OAuthInvalidNoRedirectError(
                    error="invalid_redirect_uri")

        return client

    def by_identifier_secret(self, request):
        """
        Authenticates a client by its identifier and secret (aka password).

        :param request: The incoming request
        :type request: oauth2.web.Request

        :return: The identified client
        :rtype: oauth2.datatype.Client

        :raises OAuthInvalidError: If the client could not be found, is not
                                   allowed to to use the current grant or
                                   supplied invalid credentials
        """
        client_id, client_secret = self.source(request=request)

        try:
            client = self.client_store.fetch_by_client_id(client_id)
        except ClientNotFoundError:
            raise OAuthInvalidError(error="invalid_client",
                                    explanation="No client could be found")

        grant_type = request.post_param("grant_type")
        if client.grant_type_supported(grant_type) is False:
            raise OAuthInvalidError(error="unauthorized_client",
                                    explanation="The client is not allowed "
                                                "to use this grant type")

        if client.secret != client_secret:
            raise OAuthInvalidError(error="invalid_client",
                                    explanation="Invalid client credentials")

        return client


def request_body(request):
    """
    Extracts the credentials of a client from the
    *application/x-www-form-urlencoded* body of a request.

    Expects the client_id to be the value of the ``client_id`` parameter and
    the client_secret to be the value of the ``client_secret`` parameter.

    :param request: The incoming request
    :type request: oauth2.web.Request

    :return: A tuple in the format of `(<CLIENT ID>, <CLIENT SECRET>)`
    :rtype: tuple
    """
    client_id = request.post_param("client_id")
    if client_id is None:
        raise OAuthInvalidError(error="invalid_request",
                                explanation="Missing client identifier")

    client_secret = request.post_param("client_secret")
    if client_secret is None:
        raise OAuthInvalidError(error="invalid_request",
                                explanation="Missing client credentials")

    return client_id, client_secret


def http_basic_auth(request):
    """
    Extracts the credentials of a client using HTTP Basic Auth.

    Expects the ``client_id`` to be the username and the ``client_secret`` to
    be the password part of the Authorization header.

    :param request: The incoming request
    :type request: oauth2.web.Request

    :return: A tuple in the format of (<CLIENT ID>, <CLIENT SECRET>)`
    :rtype: tuple
    """
    auth_header = request.header("authorization")

    if auth_header is None:
        raise OAuthInvalidError(error="invalid_request",
                                explanation="Authorization header is missing")

    auth_parts = auth_header.strip().encode("latin1").split(None)

    if auth_parts[0].strip().lower() != b'basic':
        raise OAuthInvalidError(
            error="invalid_request",
            explanation="Provider supports basic authentication only")

    client_id, client_secret = b64decode(auth_parts[1]).split(b':', 1)

    return client_id.decode("latin1"), client_secret.decode("latin1")
