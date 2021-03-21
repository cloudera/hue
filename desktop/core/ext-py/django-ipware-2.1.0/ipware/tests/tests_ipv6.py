# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpRequest
from django.test import TestCase
from ipware import get_client_ip


class IPv4TestCase(TestCase):
    """IP address Test"""

    def test_meta_none(self):
        request = HttpRequest()
        request.META = {}
        ip, routable = get_client_ip(request)
        self.assertIsNone(ip)
        self.assertFalse(routable)

    def test_meta_single(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True))

    def test_meta_multi(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb',
            'REMOTE_ADDR': '74dc::02bc',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True))

    def test_meta_multi_precedence_order(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '74dc::02be, 74dc::02bf',
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb',
            'REMOTE_ADDR': '74dc::02bc',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True))

    def test_meta_proxy_order_left_most(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb',
        }
        result = get_client_ip(request, proxy_order='left-most')
        self.assertEqual(result, ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True))

    def test_meta_proxy_order_right_most(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb',
        }
        result = get_client_ip(request, proxy_order='right-most')
        self.assertEqual(result, ("74dc::02bb", True))

    def test_meta_multi_precedence_private_first(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '2001:db8:, ::1',
            'X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb',
            'REMOTE_ADDR': '74dc::02bc',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True))

    def test_meta_multi_precedence_invalid_first(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': 'unknown, 2001:db8:, ::1',
            'X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb',
            'REMOTE_ADDR': '74dc::02bc',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True))

    def test_meta_error_only(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': 'unknown, 3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb',
        }
        result = get_client_ip(request)
        self.assertEqual(result, (None, False))

    def test_meta_error_first(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': 'unknown, 3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb',
            'X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True))

    def test_meta_singleton(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True))

    def test_meta_singleton_proxy_count(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
            'HTTP_X_REAL_IP': '74dc::02ba',
        }
        result = get_client_ip(request, proxy_count=1)
        self.assertEqual(result, (None, False))

    def test_meta_singleton_proxy_count_private(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '::1',
            'HTTP_X_REAL_IP': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        result = get_client_ip(request, proxy_count=1)
        self.assertEqual(result, (None, False))

    def test_meta_singleton_private_fallback(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '::1',
            'HTTP_X_REAL_IP': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True))

    def test_meta_proxy_trusted_ips(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb',
        }
        result = get_client_ip(request, proxy_trusted_ips=['74dc::02bb'])
        self.assertEqual(result, ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True))

    def test_meta_proxy_trusted_ips_proxy_count(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb',
        }
        result = get_client_ip(request, proxy_count=2, proxy_trusted_ips=['74dc::02bb'])
        self.assertEqual(result, ("3ffe:1900:4545:3:200:f8ff:fe21:67cf", True))

    def test_meta_proxy_trusted_ips_proxy_count_less_error(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02bb',
        }
        result = get_client_ip(request, proxy_count=2, proxy_trusted_ips=['74dc::02bb'])
        self.assertEqual(result, (None, False))

    def test_meta_proxy_trusted_ips_proxy_count_more_error(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb',
        }
        result = get_client_ip(request, proxy_count=1, proxy_trusted_ips=['74dc::02bb'])
        self.assertEqual(result, (None, False))

    def test_meta_proxy_trusted_ips_proxy_count_more_error_ignore_fallback(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba, 74dc::02bb',
            'HTTP_X_REAL_IP': '74dc::02bb',
        }
        result = get_client_ip(request, proxy_count=1, proxy_trusted_ips=['74dc::02bb'])
        self.assertEqual(result, (None, False))
