"""
Read or write data from or to local memory.

Though not very valuable in a production setup, these store adapters are great
for testing purposes.
"""

from oauth2.store import AccessTokenStore, AuthCodeStore, ClientStore
from oauth2.error import AccessTokenNotFound, AuthCodeNotFound, \
                         ClientNotFoundError
from oauth2.datatype import Client


class ClientStore(ClientStore):
    """
    Stores clients in memory.
    """
    def __init__(self):
        self.clients = {}

    def add_client(self, client_id, client_secret, redirect_uris,
                   authorized_grants=None, authorized_response_types=None):
        """
        Add a client app.

        :param client_id: Identifier of the client app.
        :param client_secret: Secret the client app uses for authentication
                              against the OAuth 2.0 provider.
        :param redirect_uris: A ``list`` of URIs to redirect to.

        """
        self.clients[client_id] = Client(
            identifier=client_id,
            secret=client_secret,
            redirect_uris=redirect_uris,
            authorized_grants=authorized_grants,
            authorized_response_types=authorized_response_types)

        return True

    def fetch_by_client_id(self, client_id):
        """
        Retrieve a client by its identifier.

        :param client_id: Identifier of a client app.
        :return: An instance of :class:`oauth2.Client`.
        :raises: ClientNotFoundError

        """
        if client_id not in self.clients:
            raise ClientNotFoundError

        return self.clients[client_id]


class TokenStore(AccessTokenStore, AuthCodeStore):
    """
    Stores tokens in memory.

    Useful for testing purposes or APIs with a very limited set of clients.
    Use memcache or redis as storage to be able to scale.
    """
    def __init__(self):
        self.access_tokens = {}
        self.auth_codes = {}
        self.refresh_tokens = {}
        self.unique_token_identifier = {}

    def fetch_by_code(self, code):
        """
        Returns an AuthorizationCode.

        :param code: The authorization code.
        :return: An instance of :class:`oauth2.datatype.AuthorizationCode`.
        :raises: :class:`AuthCodeNotFound` if no data could be retrieved for
                 given code.

        """
        if code not in self.auth_codes:
            raise AuthCodeNotFound

        return self.auth_codes[code]

    def save_code(self, authorization_code):
        """
        Stores the data belonging to an authorization code token.

        :param authorization_code: An instance of
                                   :class:`oauth2.datatype.AuthorizationCode`.

        """
        self.auth_codes[authorization_code.code] = authorization_code

        return True

    def save_token(self, access_token):
        """
        Stores an access token and additional data in memory.

        :param access_token: An instance of :class:`oauth2.datatype.AccessToken`.
        """
        self.access_tokens[access_token.token] = access_token

        unique_token_key = self._unique_token_key(access_token.client_id,
                                                  access_token.grant_type,
                                                  access_token.user_id)

        self.unique_token_identifier[unique_token_key] = access_token.token

        if access_token.refresh_token is not None:
            self.refresh_tokens[access_token.refresh_token] = access_token

        return True

    def delete_code(self, code):
        """
        Deletes an authorization code after use
        :param code: The authorization code.
        """
        if code in self.auth_codes:
            del self.auth_codes[code]

    def delete_refresh_token(self, refresh_token):
        """
        Deletes a refresh token after use
        :param refresh_token: The refresh_token.
        """
        if refresh_token in self.refresh_tokens:
            del self.refresh_tokens[refresh_token]

    def fetch_by_refresh_token(self, refresh_token):
        """
        Find an access token by its refresh token.

        :param refresh_token: The refresh token that was assigned to an
                              ``AccessToken``.
        :return: The :class:`oauth2.datatype.AccessToken`.
        :raises: :class:`oauth2.error.AccessTokenNotFound`
        """
        if refresh_token not in self.refresh_tokens:
            raise AccessTokenNotFound

        return self.refresh_tokens[refresh_token]

    def fetch_by_token(self, token):
        """
        Returns data associated with an access token or ``None`` if no data
        was found.

        Useful for cases like validation where the access token needs to be
        read again.

        :param token: A access token code.
        :return: An instance of :class:`oauth2.datatype.AccessToken`.
        """
        if token not in self.access_tokens:
            raise AccessTokenNotFound

        return self.access_tokens[token]

    def fetch_existing_token_of_user(self, client_id, grant_type, user_id):
        try:
            key = self._unique_token_key(client_id, grant_type, user_id)
            token = self.unique_token_identifier[key]
        except KeyError:
            raise AccessTokenNotFound

        return self.fetch_by_token(token)

    def _unique_token_key(self, client_id, grant_type, user_id):
        return "{0}_{1}_{2}".format(client_id, grant_type, user_id)
