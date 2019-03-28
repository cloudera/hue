# -*- coding: utf-8 -*-
import memcache

from oauth2.datatype import AccessToken, AuthorizationCode
from oauth2.error import AccessTokenNotFound, AuthCodeNotFound
from oauth2.store import AccessTokenStore, AuthCodeStore


class TokenStore(AccessTokenStore, AuthCodeStore):
    """
    Uses memcache to store access tokens and auth tokens.

    This Store supports ``python-memcached``. Arguments are passed to the
    underlying client implementation.

    Initialization by passing an object::

        # This example uses python-memcached
        import memcache

        # Somewhere in your application
        mc = memcache.Client(servers=['127.0.0.1:11211'], debug=0)
        # ...
        token_store = TokenStore(mc=mc)

    Initialization using ``python-memcached``::

        token_store = TokenStore(servers=['127.0.0.1:11211'], debug=0)

    """
    def __init__(self, mc=None, prefix="oauth2", *args, **kwargs):
        self.prefix = prefix

        if mc is not None:
            self.mc = mc
        else:
            self.mc = memcache.Client(*args, **kwargs)

    def fetch_by_code(self, code):
        """
        Returns data belonging to an authorization code from memcache or
        ``None`` if no data was found.

        See :class:`oauth2.store.AuthCodeStore`.

        """
        code_data = self.mc.get(self._generate_cache_key(code))

        if code_data is None:
            raise AuthCodeNotFound

        return AuthorizationCode(**code_data)

    def save_code(self, authorization_code):
        """
        Stores the data belonging to an authorization code token in memcache.

        See :class:`oauth2.store.AuthCodeStore`.

        """
        key = self._generate_cache_key(authorization_code.code)

        self.mc.set(key, {"client_id": authorization_code.client_id,
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
        self.mc.delete(self._generate_cache_key(code))

    def save_token(self, access_token):
        """
        Stores the access token and additional data in memcache.

        See :class:`oauth2.store.AccessTokenStore`.

        """
        key = self._generate_cache_key(access_token.token)
        self.mc.set(key, access_token.__dict__)

        unique_token_key = self._unique_token_key(access_token.client_id,
                                                  access_token.grant_type,
                                                  access_token.user_id)
        self.mc.set(self._generate_cache_key(unique_token_key),
                    access_token.__dict__)

        if access_token.refresh_token is not None:
            rft_key = self._generate_cache_key(access_token.refresh_token)
            self.mc.set(rft_key, access_token.__dict__)

    def delete_refresh_token(self, refresh_token):
        """
        Deletes a refresh token after use
        :param refresh_token: The refresh token to delete.
        """
        access_token = self.fetch_by_refresh_token(refresh_token)
        self.mc.delete(self._generate_cache_key(access_token.token))
        self.mc.delete(self._generate_cache_key(refresh_token))

    def fetch_by_refresh_token(self, refresh_token):
        token_data = self.mc.get(refresh_token)

        if token_data is None:
            raise AccessTokenNotFound

        return AccessToken(**token_data)

    def fetch_existing_token_of_user(self, client_id, grant_type, user_id):
        data = self.mc.get(self._unique_token_key(client_id, grant_type,
                                                  user_id))

        if data is None:
            raise AccessTokenNotFound

        return AccessToken(**data)

    def _unique_token_key(self, client_id, grant_type, user_id):
        return "{0}_{1}_{2}".format(client_id, grant_type, user_id)

    def _generate_cache_key(self, identifier):
        return self.prefix + "_" + identifier
