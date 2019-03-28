# -*- coding: utf-8 -*-
"""
Definitions of types used by grants.
"""

import time
from oauth2.error import RedirectUriUnknown


class AccessToken(object):
    """
    An access token and associated data.
    """
    def __init__(self, client_id, grant_type, token, data={}, expires_at=None,
                 refresh_token=None, refresh_expires_at=None, scopes=[],
                 user_id=None):
        self.client_id = client_id
        self.grant_type = grant_type
        self.token = token
        self.data = data
        self.expires_at = expires_at
        self.refresh_token = refresh_token
        self.refresh_expires_at = refresh_expires_at
        self.scopes = scopes
        self.user_id = user_id

    @property
    def expires_in(self):
        """
        Returns the time until the token expires.

        :return: The remaining time until expiration in seconds or 0 if the
                 token has expired.
        """
        time_left = self.expires_at - int(time.time())

        if time_left > 0:
            return time_left
        return 0

    def is_expired(self):
        """
        Determines if the token has expired.

        :return: `True` if the token has expired. Otherwise `False`.
        """
        if self.expires_at is None:
            return False

        if self.expires_in > 0:
            return False

        return True


class AuthorizationCode(object):
    """
    Holds an authorization code and additional information.
    """
    def __init__(self, client_id, code, expires_at, redirect_uri, scopes,
                 data=None, user_id=None):
        self.client_id = client_id
        self.code = code
        self.data = data
        self.expires_at = expires_at
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.user_id = user_id

    def is_expired(self):
        if self.expires_at < int(time.time()):
            return True
        return False


class Client(object):
    """
    Representation of a client application.
    """
    def __init__(self, identifier, secret, authorized_grants=None,
                 authorized_response_types=None, redirect_uris=None):
        """
        :param identifier: The unique identifier of a client.
        :param secret: The secret the clients uses to authenticate.
        :param authorized_grants: A list of grants under which the client can
                                  request tokens.
                                  All grants are allowed if this value is set
                                  to `None` (default).
        :param authorized_response_types: A list of response types of which
                                          the client can request tokens.
                                          All response types are allowed if
                                          this value is set to `None`
                                          (default).
        :redirect_uris: A list of redirect uris this client can use.
        """
        self.authorized_grants = authorized_grants
        self.authorized_response_types = authorized_response_types
        self.identifier = identifier
        self.secret = secret

        if redirect_uris is None:
            self.redirect_uris = []
        else:
            self.redirect_uris = redirect_uris

        self._redirect_uri = None

    @property
    def redirect_uri(self):
        if self._redirect_uri is None:
            # redirect_uri is an optional param.
            # If not supplied, we use the first entry stored in db as default.
            return self.redirect_uris[0]
        return self._redirect_uri

    @redirect_uri.setter
    def redirect_uri(self, value):
        if value not in self.redirect_uris:
            raise RedirectUriUnknown
        self._redirect_uri = value

    def grant_type_supported(self, grant_type):
        """
        Checks if the Client is authorized receive tokens for the given grant.

        :param grant_type: The type of the grant.

        :return: Boolean
        """
        if self.authorized_grants is None:
            return True

        return grant_type in self.authorized_grants

    def response_type_supported(self, response_type):
        """
        Checks if the client is allowed to receive tokens for the given
        response type.

        :param response_type: The response type.

        :return: Boolean
        """
        if self.authorized_response_types is None:
            return True

        return response_type in self.authorized_response_types
