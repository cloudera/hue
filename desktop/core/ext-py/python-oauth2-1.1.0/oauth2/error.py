"""
Errors raised during the OAuth 2.0 flow.
"""


class AccessTokenNotFound(Exception):
    """
    Error indicating that an access token could not be read from the
    storage backend by an instance of :class:`oauth2.store.AccessTokenStore`.
    """
    pass


class AuthCodeNotFound(Exception):
    """
    Error indicating that an authorization code could not be read from the
    storage backend by an instance of :class:`oauth2.store.AuthCodeStore`.
    """
    pass


class ClientNotFoundError(Exception):
    """
    Error raised by an implementation of :class:`oauth2.store.ClientStore` if
    a client does not exists.
    """
    pass


class InvalidSiteAdapter(Exception):
    """
    Raised by :class:`oauth2.grant.SiteAdapterMixin` in case an invalid site
    adapter was passed to the instance.
    """
    pass


class UserIdentifierMissingError(Exception):
    """
    Indicates that the identifier of a user is missing when the use of unique
    access token is enabled.
    """
    pass


class OAuthBaseError(Exception):
    """
    Base class used by all OAuth 2.0 errors.

    :param error: Identifier of the error.
    :param error_uri: Set this to delivery an URL to your documentation that
                      describes the error. (optional)
    :param explanation: Short message that describes the error. (optional)
    """
    def __init__(self, error, error_uri=None, explanation=None):
        self.error = error
        self.error_uri = error_uri
        self.explanation = explanation

        super(OAuthBaseError, self).__init__()


class OAuthInvalidError(OAuthBaseError):
    """
    Indicates an error during validation of a request.
    """
    pass


class OAuthInvalidNoRedirectError(OAuthInvalidError):
    """
    Indicates an error during validation of a request.
    The provider will not inform the client about the error by redirecting to
    it. This behaviour is required by the Authorization Request step of the
    Authorization Code Grant and Implicit Grant.
    """
    pass


class UnsupportedGrantError(Exception):
    """
    Indicates that a requested grant is not supported by the server.
    """
    pass


class RedirectUriUnknown(Exception):
    """
    Indicates that a redirect_uri is not associated with a client.
    """
    pass


class UserNotAuthenticated(Exception):
    """
    Raised by a :class:`oauth2.web.SiteAdapter` if a user could not be
    authenticated.
    """
    pass
