#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Classes for handling a HTTP request/response flow.

.. versionchanged:: 1.0.0
   Moved from package ``oauth2.web`` to ``oauth2.web.wsgi``.
"""

from oauth2.compatibility import parse_qs


class Request(object):
    """
    Contains data of the current HTTP request.
    """
    def __init__(self, env):
        """
        :param env: Wsgi environment
        """
        self.method = env["REQUEST_METHOD"]
        self.query_params = {}
        self.query_string = env["QUERY_STRING"]
        self.path = env["PATH_INFO"]
        self.post_params = {}
        self.env_raw = env

        for param, value in parse_qs(env["QUERY_STRING"]).items():
            self.query_params[param] = value[0]

        if (self.method == "POST"
            and env["CONTENT_TYPE"].startswith("application/x-www-form-urlencoded")):
            self.post_params = {}
            content = env['wsgi.input'].read(int(env['CONTENT_LENGTH']))
            post_params = parse_qs(content)

            for param, value in post_params.items():
                decoded_param = param.decode('utf-8')
                decoded_value = value[0].decode('utf-8')
                self.post_params[decoded_param] = decoded_value

    def get_param(self, name, default=None):
        """
        Returns a param of a GET request identified by its name.
        """
        try:
            return self.query_params[name]
        except KeyError:
            return default

    def post_param(self, name, default=None):
        """
        Returns a param of a POST request identified by its name.
        """
        try:
            return self.post_params[name]
        except KeyError:
            return default

    def header(self, name, default=None):
        """
        Returns the value of the HTTP header identified by `name`.
        """
        wsgi_header = "HTTP_{0}".format(name.upper())

        try:
            return self.env_raw[wsgi_header]
        except KeyError:
            return default


class Application(object):
    """
    Implements WSGI.

    .. versionchanged:: 1.0.0
       Renamed from ``Server`` to ``Application``.
    """
    HTTP_CODES = {200: "200 OK",
                  301: "301 Moved Permanently",
                  302: "302 Found",
                  400: "400 Bad Request",
                  401: "401 Unauthorized",
                  404: "404 Not Found"}

    def __init__(self, provider, authorize_uri="/authorize", env_vars=None,
                 request_class=Request, token_uri="/token"):
        self.authorize_uri = authorize_uri
        self.env_vars = env_vars
        self.request_class = request_class
        self.provider = provider
        self.token_uri = token_uri

        self.provider.authorize_path = authorize_uri
        self.provider.token_path = token_uri

    def __call__(self, env, start_response):
        environ = {}

        if (env["PATH_INFO"] != self.authorize_uri
            and env["PATH_INFO"] != self.token_uri):
            start_response("404 Not Found",
                           [('Content-type', 'text/html')])
            return [b"Not Found"]

        request = self.request_class(env)

        if isinstance(self.env_vars, list):
            for varname in self.env_vars:
                if varname in env:
                    environ[varname] = env[varname]

        response = self.provider.dispatch(request, environ)

        start_response(self.HTTP_CODES[response.status_code],
                       list(response.headers.items()))

        return [response.body.encode('utf-8')]
