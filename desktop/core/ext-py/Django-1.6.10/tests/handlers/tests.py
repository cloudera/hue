# coding: utf-8

from __future__ import unicode_literals

from django.core.handlers.wsgi import WSGIHandler, WSGIRequest
from django.core.signals import request_started, request_finished
from django.db import close_old_connections, connection
from django.test import RequestFactory, TestCase, TransactionTestCase
from django.test.utils import override_settings
from django.utils.encoding import force_str
from django.utils import six


class HandlerTests(TestCase):

    def setUp(self):
        request_started.disconnect(close_old_connections)

    def tearDown(self):
        request_started.connect(close_old_connections)

    # Mangle settings so the handler will fail
    @override_settings(MIDDLEWARE_CLASSES=42)
    def test_lock_safety(self):
        """
        Tests for bug #11193 (errors inside middleware shouldn't leave
        the initLock locked).
        """
        # Try running the handler, it will fail in load_middleware
        handler = WSGIHandler()
        self.assertEqual(handler.initLock.locked(), False)
        with self.assertRaises(Exception):
            handler(None, None)
        self.assertEqual(handler.initLock.locked(), False)

    def test_bad_path_info(self):
        """Tests for bug #15672 ('request' referenced before assignment)"""
        environ = RequestFactory().get('/').environ
        environ['PATH_INFO'] = b'\xed' if six.PY2 else '\xed'
        handler = WSGIHandler()
        response = handler(environ, lambda *a, **k: None)
        self.assertEqual(response.status_code, 400)

    def test_non_ascii_query_string(self):
        """
        Test that non-ASCII query strings are properly decoded (#20530, #22996).
        """
        environ = RequestFactory().get('/').environ
        raw_query_strings = [
            b'want=caf%C3%A9', # This is the proper way to encode 'café'
            b'want=caf\xc3\xa9', # UA forgot to quote bytes
            b'want=caf%E9', # UA quoted, but not in UTF-8
            b'want=caf\xe9', # UA forgot to convert Latin-1 to UTF-8 and to quote (typical of MSIE)
        ]
        got = []
        for raw_query_string in raw_query_strings:
            if six.PY3:
                # Simulate http.server.BaseHTTPRequestHandler.parse_request handling of raw request
                environ['QUERY_STRING'] = str(raw_query_string, 'iso-8859-1')
            else:
                environ['QUERY_STRING'] = raw_query_string
            request = WSGIRequest(environ)
            got.append(request.GET['want'])
        if six.PY2:
            self.assertListEqual(got, ['café', 'café', 'caf\ufffd', 'caf\ufffd'])
        else:
            # On Python 3, %E9 is converted to the unicode replacement character by parse_qsl
            self.assertListEqual(got, ['café', 'café', 'caf\ufffd', 'café'])

    def test_non_ascii_cookie(self):
        """Test that non-ASCII cookies set in JavaScript are properly decoded (#20557)."""
        environ = RequestFactory().get('/').environ
        raw_cookie = 'want="café"'
        if six.PY3:
            raw_cookie = raw_cookie.encode('utf-8').decode('iso-8859-1')
        environ['HTTP_COOKIE'] = raw_cookie
        request = WSGIRequest(environ)
        # If would be nicer if request.COOKIES returned unicode values.
        # However the current cookie parser doesn't do this and fixing it is
        # much more work than fixing #20557. Feel free to remove force_str()!
        self.assertEqual(request.COOKIES['want'], force_str("café"))


class TransactionsPerRequestTests(TransactionTestCase):

    available_apps = []
    urls = 'handlers.urls'

    def test_no_transaction(self):
        response = self.client.get('/in_transaction/')
        self.assertContains(response, 'False')

    def test_auto_transaction(self):
        old_atomic_requests = connection.settings_dict['ATOMIC_REQUESTS']
        try:
            connection.settings_dict['ATOMIC_REQUESTS'] = True
            response = self.client.get('/in_transaction/')
        finally:
            connection.settings_dict['ATOMIC_REQUESTS'] = old_atomic_requests
        self.assertContains(response, 'True')

    def test_no_auto_transaction(self):
        old_atomic_requests = connection.settings_dict['ATOMIC_REQUESTS']
        try:
            connection.settings_dict['ATOMIC_REQUESTS'] = True
            response = self.client.get('/not_in_transaction/')
        finally:
            connection.settings_dict['ATOMIC_REQUESTS'] = old_atomic_requests
        self.assertContains(response, 'False')


class SignalsTests(TestCase):
    urls = 'handlers.urls'

    def setUp(self):
        self.signals = []
        request_started.connect(self.register_started)
        request_finished.connect(self.register_finished)

    def tearDown(self):
        request_started.disconnect(self.register_started)
        request_finished.disconnect(self.register_finished)

    def register_started(self, **kwargs):
        self.signals.append('started')

    def register_finished(self, **kwargs):
        self.signals.append('finished')

    def test_request_signals(self):
        response = self.client.get('/regular/')
        self.assertEqual(self.signals, ['started', 'finished'])
        self.assertEqual(response.content, b"regular content")

    def test_request_signals_streaming_response(self):
        response = self.client.get('/streaming/')
        self.assertEqual(self.signals, ['started'])
        self.assertEqual(b''.join(response.streaming_content), b"streaming content")
        self.assertEqual(self.signals, ['started', 'finished'])


class HandlerSuspiciousOpsTest(TestCase):
    urls = 'handlers.urls'

    def test_suspiciousop_in_view_returns_400(self):
        response = self.client.get('/suspicious/')
        self.assertEqual(response.status_code, 400)
