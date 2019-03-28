#!/usr/bin/env python
# -*- coding: utf-8 -*-


class AuthenticatingSiteAdapter(object):
    """
    Extended by site adapters that need to authenticate the user.
    """
    def authenticate(self, request, environ, scopes, client):
        """
        Authenticates a user and checks if she has authorized access.

        :param request: Incoming request data.
        :type request: oauth2.web.Request

        :param environ: Environment variables of the request.
        :type environ: dict

        :param scopes: A list of strings with each string being one requested
                       scope.
        :type scopes: list

        :param client: The client that initiated the authorization process
        :type client: oauth2.datatype.Client

        :return: A ``dict`` containing arbitrary data that will be passed to
                 the current storage adapter and saved with auth code and
                 access token. Return a tuple in the form
                 `(additional_data, user_id)` if you want to use
                 :doc:`unique_token`.
        :rtype: dict

        :raises oauth2.error.UserNotAuthenticated: If the user could not be
                                                   authenticated.
        """
        raise NotImplementedError


class UserFacingSiteAdapter(object):
    """
    Extended by site adapters that need to interact with the user.

    Display HTML or redirect the user agent to another page of your website
    where she can do something before being returned to the OAuth 2.0 server.
    """
    def render_auth_page(self, request, response, environ, scopes, client):
        """
        Defines how to display a confirmation page to the user.

        :param request: Incoming request data.
        :type request: oauth2.web.Request

        :param response: Response to return to a client.
        :type response: oauth2.web.Response

        :param environ: Environment variables of the request.
        :type environ: dict

        :param scopes: A list of strings with each string being one requested
                       scope.
        :type scopes: list

        :param client: The client that initiated the authorization process
        :type client: oauth2.datatype.Client

        :return: The response passed in as a parameter.
                 It can contain HTML or issue a redirect.
        :rtype: oauth2.web.Response
        """
        raise NotImplementedError

    def user_has_denied_access(self, request):
        """
        Checks if the user has denied access. This will lead to python-oauth2
        returning a "acess_denied" response to the requesting client app.

        :param request: Incoming request data.
        :type request: oauth2.web.Request

        :return: Return ``True`` if the user has denied access.
        :rtype: bool
        """
        raise NotImplementedError


class AuthorizationCodeGrantSiteAdapter(UserFacingSiteAdapter,
                                        AuthenticatingSiteAdapter):
    """
    Definition of a site adapter as required by
    :class:`oauth2.grant.AuthorizationCodeGrant`.
    """
    pass


class ImplicitGrantSiteAdapter(UserFacingSiteAdapter,
                               AuthenticatingSiteAdapter):
    """
    Definition of a site adapter as required by
    :class:`oauth2.grant.ImplicitGrant`.
    """
    pass


class ResourceOwnerGrantSiteAdapter(AuthenticatingSiteAdapter):
    """
    Definition of a site adapter as required by
    :class:`oauth2.grant.ResourceOwnerGrant`.
    """
    pass


class Request(object):
    """
    Base class defining the interface of a request.
    """
    @property
    def method(self):
        """
        Returns the HTTP method of the request.
        """
        raise NotImplementedError

    @property
    def path(self):
        """
        Returns the current path portion of the current uri.

        Used by some grants to determine which action to take.
        """
        raise NotImplementedError

    def get_param(self, name, default=None):
        """
        Retrieve a parameter from the query string of the request.
        """
        raise NotImplementedError

    def header(self, name, default=None):
        """
        Retrieve a header of the request.
        """
        raise NotImplementedError

    def post_param(self, name, default=None):
        """
        Retrieve a parameter from the body of the request.
        """
        raise NotImplementedError


class Response(object):
    """
    Contains data returned to the requesting user agent.
    """
    def __init__(self):
        self.status_code = 200
        self._headers = {"Content-Type": "text/html"}
        self.body = ""

    @property
    def headers(self):
        return self._headers

    def add_header(self, header, value):
        """
        Add a header to the response.
        """
        self._headers[header] = str(value)
