#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. warning::

   Tornado support is currently experimental.

Use Tornado to serve token requests:

.. literalinclude:: examples/tornado_server.py
"""

from __future__ import absolute_import

from tornado.web import RequestHandler


class Request(object):
    def __init__(self, handler):
        """
        :param handler: Handler of the current request
        :type handler: :class:`tornado.web.RequestHandler`
        """
        self.handler = handler

    @property
    def method(self):
        return self.handler.request.method

    @property
    def path(self):
        return self.handler.request.path

    @property
    def query_string(self):
        return self.handler.request.query

    def get_param(self, name, default=None):
        return self.handler.get_query_argument(name=name, default=default)

    def header(self, name, default=None):
        return self.handler.request.headers[name]

    def post_param(self, name, default=None):
        return self.handler.get_body_argument(name=name, default=default)


class OAuth2Handler(RequestHandler):
    def initialize(self, provider):
        """
        :type provider: :class:`oauth2.Provider`
        """
        self.provider = provider

    def get(self):
        response = self._dispatch_request()

        self._map_response(response)

    def post(self):
        response = self._dispatch_request()

        self._map_response(response)

    def _dispatch_request(self):
        return self.provider.dispatch(request=Request(handler=self),
                                      environ=dict())

    def _map_response(self, response):
        for name, value in list(response.headers.items()):
            self.set_header(name, value)

        self.set_status(response.status_code)
        self.write(response.body)
