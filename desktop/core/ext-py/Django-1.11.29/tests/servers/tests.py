# -*- encoding: utf-8 -*-
"""
Tests for django.core.servers.
"""
from __future__ import unicode_literals

import contextlib
import errno
import os
import socket

from django.test import LiveServerTestCase, override_settings
from django.utils._os import upath
from django.utils.http import urlencode
from django.utils.six import text_type
from django.utils.six.moves.urllib.error import HTTPError
from django.utils.six.moves.urllib.request import urlopen

from .models import Person

TEST_ROOT = os.path.dirname(upath(__file__))
TEST_SETTINGS = {
    'MEDIA_URL': '/media/',
    'MEDIA_ROOT': os.path.join(TEST_ROOT, 'media'),
    'STATIC_URL': '/static/',
    'STATIC_ROOT': os.path.join(TEST_ROOT, 'static'),
}


@override_settings(ROOT_URLCONF='servers.urls', **TEST_SETTINGS)
class LiveServerBase(LiveServerTestCase):

    available_apps = [
        'servers',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
    ]
    fixtures = ['testdata.json']

    def urlopen(self, url):
        return urlopen(self.live_server_url + url)


class LiveServerAddress(LiveServerBase):

    @classmethod
    def setUpClass(cls):
        super(LiveServerAddress, cls).setUpClass()
        # put it in a list to prevent descriptor lookups in test
        cls.live_server_url_test = [cls.live_server_url]

    def test_live_server_url_is_class_property(self):
        self.assertIsInstance(self.live_server_url_test[0], text_type)
        self.assertEqual(self.live_server_url_test[0], self.live_server_url)


class LiveServerViews(LiveServerBase):
    def test_404(self):
        with self.assertRaises(HTTPError) as err:
            self.urlopen('/')
        self.assertEqual(err.exception.code, 404, 'Expected 404 response')

    def test_view(self):
        with contextlib.closing(self.urlopen('/example_view/')) as f:
            self.assertEqual(f.read(), b'example view')

    def test_static_files(self):
        with contextlib.closing(self.urlopen('/static/example_static_file.txt')) as f:
            self.assertEqual(f.read().rstrip(b'\r\n'), b'example static file')

    def test_no_collectstatic_emulation(self):
        """
        LiveServerTestCase reports a 404 status code when HTTP client
        tries to access a static file that isn't explicitly put under
        STATIC_ROOT.
        """
        with self.assertRaises(HTTPError) as err:
            self.urlopen('/static/another_app/another_app_static_file.txt')
        self.assertEqual(err.exception.code, 404, 'Expected 404 response')

    def test_media_files(self):
        with contextlib.closing(self.urlopen('/media/example_media_file.txt')) as f:
            self.assertEqual(f.read().rstrip(b'\r\n'), b'example media file')

    def test_environ(self):
        with contextlib.closing(self.urlopen('/environ_view/?%s' % urlencode({'q': 'тест'}))) as f:
            self.assertIn(b"QUERY_STRING: 'q=%D1%82%D0%B5%D1%81%D1%82'", f.read())


class LiveServerDatabase(LiveServerBase):

    def test_fixtures_loaded(self):
        """
        Fixtures are properly loaded and visible to the live server thread.
        """
        with contextlib.closing(self.urlopen('/model_view/')) as f:
            self.assertEqual(f.read().splitlines(), [b'jane', b'robert'])

    def test_database_writes(self):
        """
        Data written to the database by a view can be read.
        """
        self.urlopen('/create_model_instance/')
        self.assertQuerysetEqual(
            Person.objects.all().order_by('pk'),
            ['jane', 'robert', 'emily'],
            lambda b: b.name
        )


class LiveServerPort(LiveServerBase):

    def test_port_bind(self):
        """
        Each LiveServerTestCase binds to a unique port or fails to start a
        server thread when run concurrently (#26011).
        """
        TestCase = type(str("TestCase"), (LiveServerBase,), {})
        try:
            TestCase.setUpClass()
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                # We're out of ports, LiveServerTestCase correctly fails with
                # a socket error.
                return
            # Unexpected error.
            raise
        try:
            # We've acquired a port, ensure our server threads acquired
            # different addresses.
            self.assertNotEqual(
                self.live_server_url, TestCase.live_server_url,
                "Acquired duplicate server addresses for server threads: %s" % self.live_server_url
            )
        finally:
            if hasattr(TestCase, 'server_thread'):
                TestCase.server_thread.terminate()

    def test_specified_port_bind(self):
        """LiveServerTestCase.port customizes the server's port."""
        TestCase = type(str('TestCase'), (LiveServerBase,), {})
        # Find an open port and tell TestCase to use it.
        s = socket.socket()
        s.bind(('', 0))
        TestCase.port = s.getsockname()[1]
        s.close()
        TestCase.setUpClass()
        try:
            self.assertEqual(
                TestCase.port, TestCase.server_thread.port,
                'Did not use specified port for LiveServerTestCase thread: %s' % TestCase.port
            )
        finally:
            if hasattr(TestCase, 'server_thread'):
                TestCase.server_thread.terminate()
