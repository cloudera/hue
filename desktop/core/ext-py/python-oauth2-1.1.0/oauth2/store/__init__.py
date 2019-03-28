"""
Store adapters to persist and retrieve data during the OAuth 2.0 process or
for later use.
This module provides base classes that can be extended to implement your own
solution specific to your needs.
It also includes implementations for popular storage systems like memcache.
"""


class AccessTokenStore(object):
    """
    Base class for persisting an access token after it has been generated.

    Used by two-legged and three-legged authentication flows.
    """
    def save_token(self, access_token):
        """
        Stores an access token and additional data.

        :param access_token: An instance of :class:`oauth2.datatype.AccessToken`.

        """
        raise NotImplementedError

    def fetch_existing_token_of_user(self, client_id, grant_type, user_id):
        """
        Fetches an access token identified by its client id, type of grant and
        user id.

        This method must be implemented to make use of unique access tokens.

        :param client_id: Identifier of the client a token belongs to.
        :param grant_type: The type of the grant that created the token
        :param user_id: Identifier of the user a token belongs to.
        :return: An instance of :class:`oauth2.datatype.AccessToken`.
        :raises: :class:`oauth2.error.AccessTokenNotFound` if no data could be
                 retrieved.
        """
        raise NotImplementedError

    def fetch_by_refresh_token(self, refresh_token):
        """
        Fetches an access token from the store using its refresh token to
        identify it.

        :param refresh_token: A string containing the refresh token.
        :return: An instance of :class:`oauth2.datatype.AccessToken`.
        :raises: :class:`oauth2.error.AccessTokenNotFound` if no data could be retrieved for
                 given refresh_token.
        """
        raise NotImplementedError

    def delete_refresh_token(self, refresh_token):
        """
        Deletes an access token from the store using its refresh token to identify it.
        This invalidates both the access token and the refresh token.

        :param refresh_token: A string containing the refresh token.
        :return: None.
        :raises: :class:`oauth2.error.AccessTokenNotFound` if no data could be retrieved for
                 given refresh_token.
        """
        raise NotImplementedError


class AuthCodeStore(object):
    """
    Base class for persisting and retrieving an auth token during the
    Authorization Code Grant flow.
    """
    def fetch_by_code(self, code):
        """
        Returns an AuthorizationCode fetched from a storage.

        :param code: The authorization code.
        :return: An instance of :class:`oauth2.datatype.AuthorizationCode`.
        :raises: :class:`oauth2.error.AuthCodeNotFound` if no data could be retrieved for
                 given code.

        """
        raise NotImplementedError

    def save_code(self, authorization_code):
        """
        Stores the data belonging to an authorization code token.

        :param authorization_code: An instance of
                                   :class:`oauth2.datatype.AuthorizationCode`.
        """
        raise NotImplementedError

    def delete_code(self, code):
        """
        Deletes an authorization code after it's use per section 4.1.2.

        http://tools.ietf.org/html/rfc6749#section-4.1.2

        :param code: The authorization code.
        """
        raise NotImplementedError


class ClientStore(object):
    """
    Base class for handling OAuth2 clients.
    """
    def fetch_by_client_id(self, client_id):
        """
        Retrieve a client by its identifier.

        :param client_id: Identifier of a client app.
        :return: An instance of :class:`oauth2.datatype.Client`.
        :raises: :class:`oauth2.error.ClientNotFoundError` if no data could be retrieved for
                 given client_id.
        """
        raise NotImplementedError
