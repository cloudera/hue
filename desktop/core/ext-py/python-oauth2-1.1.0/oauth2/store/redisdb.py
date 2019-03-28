# -*- coding: utf-8 -*-
import redis
import json

from oauth2.datatype import AccessToken, AuthorizationCode, Client
from oauth2.error import AccessTokenNotFound, AuthCodeNotFound, \
    ClientNotFoundError
from oauth2.store import AccessTokenStore, AuthCodeStore, ClientStore


class RedisStore(object):
    """
    Uses redis to store access tokens and auth tokens.

    This Store supports ``redis``. Arguments are passed to the
    underlying client implementation.

    Initialization::

        import redisdb

        token_store = TokenStore(host="127.0.0.1",
            port=6379,
            db=0
        )

    """
    def __init__(self, rs=None, prefix="oauth2", *args, **kwargs):
        self.prefix = prefix

        if rs is not None:
            self.rs = rs
        else:
            self.rs = redis.StrictRedis(*args, **kwargs)

    def delete(self, name):
        cache_key = self._generate_cache_key(name)

        self.rs.delete(cache_key)

    def write(self, name, data):
        cache_key = self._generate_cache_key(name)

        self.rs.set(cache_key, json.dumps(data))

    def read(self, name):
        cache_key = self._generate_cache_key(name)

        data = self.rs.get(cache_key)

        if data is None:
            return None

        return json.loads(data.decode("utf-8"))

    def _generate_cache_key(self, identifier):
        return self.prefix + "_" + identifier


class TokenStore(AccessTokenStore, AuthCodeStore, RedisStore):
    def fetch_by_code(self, code):
        """
        Returns data belonging to an authorization code from redis or
        ``None`` if no data was found.

        See :class:`oauth2.store.AuthCodeStore`.

        """
        code_data = self.read(code)

        if code_data is None:
            raise AuthCodeNotFound

        return AuthorizationCode(**code_data)

    def save_code(self, authorization_code):
        """
        Stores the data belonging to an authorization code token in redis.

        See :class:`oauth2.store.AuthCodeStore`.

        """
        self.write(authorization_code.code,
                   {"client_id": authorization_code.client_id,
                    "code": authorization_code.code,
                    "expires_at": authorization_code.expires_at,
                    "redirect_uri": authorization_code.redirect_uri,
                    "scopes": authorization_code.scopes,
                    "data": authorization_code.data,
                    "user_id": authorization_code.user_id})

    def delete_code(self, code):
        """
        Deletes an authorization code after use
        :param code: The authorization code.
        """
        self.delete(code)

    def save_token(self, access_token):
        """
        Stores the access token and additional data in redis.

        See :class:`oauth2.store.AccessTokenStore`.

        """
        self.write(access_token.token, access_token.__dict__)

        unique_token_key = self._unique_token_key(access_token.client_id,
                                                  access_token.grant_type,
                                                  access_token.user_id)
        self.write(unique_token_key, access_token.__dict__)

        if access_token.refresh_token is not None:
            self.write(access_token.refresh_token, access_token.__dict__)

    def delete_refresh_token(self, refresh_token):
        """
        Deletes a refresh token after use
        :param refresh_token: The refresh token to delete.
        """
        access_token = self.fetch_by_refresh_token(refresh_token)

        self.delete(access_token.token)

    def fetch_by_refresh_token(self, refresh_token):
        token_data = self.read(refresh_token)

        if token_data is None:
            raise AccessTokenNotFound

        return AccessToken(**token_data)

    def fetch_existing_token_of_user(self, client_id, grant_type, user_id):
        unique_token_key = self._unique_token_key(client_id=client_id,
                                                  grant_type=grant_type,
                                                  user_id=user_id)
        token_data = self.read(unique_token_key)

        if token_data is None:
            raise AccessTokenNotFound

        return AccessToken(**token_data)

    def _unique_token_key(self, client_id, grant_type, user_id):
        return "{0}_{1}_{2}".format(client_id, grant_type, user_id)


class ClientStore(ClientStore, RedisStore):
    def add_client(self, client_id, client_secret, redirect_uris,
                   authorized_grants=None, authorized_response_types=None):
        """
        Add a client app.

        :param client_id: Identifier of the client app.
        :param client_secret: Secret the client app uses for authentication
                              against the OAuth 2.0 provider.
        :param redirect_uris: A ``list`` of URIs to redirect to.

        """
        self.write(client_id,
                   {"identifier": client_id,
                    "secret": client_secret,
                    "redirect_uris": redirect_uris,
                    "authorized_grants": authorized_grants,
                    "authorized_response_types": authorized_response_types})

        return True

    def fetch_by_client_id(self, client_id):
        client_data = self.read(client_id)

        if client_data is None:
            raise ClientNotFoundError

        return Client(identifier=client_data["identifier"],
                      secret=client_data["secret"],
                      redirect_uris=client_data["redirect_uris"],
                      authorized_grants=client_data["authorized_grants"],
                      authorized_response_types=client_data["authorized_response_types"])
