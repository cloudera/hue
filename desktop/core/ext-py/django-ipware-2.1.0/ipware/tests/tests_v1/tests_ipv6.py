# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpRequest
from django.test import TestCase
from django.test import override_settings
from ipware.ip import get_ip
from ipware.ip import get_real_ip
from ipware.ip import get_trusted_ip


class IPv6TestCase(TestCase):
    """IP address Test"""

    def test_http_x_forwarded_for_multiple(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba',
            'HTTP_X_REAL_IP': '74dc::02ba',
            'REMOTE_ADDR': '74dc::02ba',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "3ffe:1900:4545:3:200:f8ff:fe21:67cf")

    def test_http_x_forwarded_for_multiple_bad_address(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': 'unknown, ::1/128, 74dc::02ba',
            'HTTP_X_REAL_IP': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
            'REMOTE_ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")

    def test_http_x_forwarded_for_singleton(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '74dc::02ba',
            'HTTP_X_REAL_IP': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
            'REMOTE_ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")

    def test_http_x_forwarded_for_singleton_private_address(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '::1/128',
            'HTTP_X_REAL_IP': '74dc::02ba',
            'REMOTE_ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")

    def test_bad_http_x_forwarded_for_fallback_on_x_real_ip(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': 'unknown ::1/128',
            'HTTP_X_REAL_IP': '74dc::02ba',
            'REMOTE_ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")

    def test_empty_http_x_forwarded_for_fallback_on_x_real_ip(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '74dc::02ba',
            'REMOTE_ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")

    def test_empty_http_x_forwarded_for_empty_x_real_ip_fallback_on_remote_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '',
            'REMOTE_ADDR': '74dc::02ba',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")

    def test_empty_http_x_forwarded_for_private_x_real_ip_fallback_on_remote_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '::1/128',
            'REMOTE_ADDR': '74dc::02ba',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")

    def test_private_http_x_forward_for_ip_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '::1/128',
            'HTTP_X_REAL_IP': '',
            'REMOTE_ADDR': '',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, None)

    def test_private_real_ip_for_ip_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '::1/128',
            'REMOTE_ADDR': '',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, None)

    def test_private_remote_addr_for_ip_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '',
            'REMOTE_ADDR': '::1/128',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, None)

    def test_missing_x_forwarded(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': '74dc::02ba',
            'REMOTE_ADDR': '74dc::02ba',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")

    def test_missing_x_forwarded_missing_real_ip(self):
        request = HttpRequest()
        request.META = {
            'REMOTE_ADDR': '74dc::02ba',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")

    def test_missing_x_forwarded_missing_real_ip_mix_case(self):
        request = HttpRequest()
        request.META = {
            'REMOTE_ADDR': '74DC::02BA',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")

    def test_private_remote_address(self):
        request = HttpRequest()
        request.META = {
            'REMOTE_ADDR': 'fe80::02ba',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, None)

    def test_best_matched_real_ip(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': '::1',
            'REMOTE_ADDR': 'fe80::02ba',
        }
        ip = get_ip(request)
        self.assertEqual(ip, "fe80::02ba")

    def test_x_forwarded_for_multiple(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba',
            'REMOTE_ADDR': '74dc::02ba',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "3ffe:1900:4545:3:200:f8ff:fe21:67cf")

    def test_x_forwarded_for_multiple_bad_address(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': 'unknown, ::1/128, 74dc::02ba',
            'REMOTE_ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")

    def test_x_forwarded_for_singleton(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '74dc::02ba',
            'REMOTE_ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")

    def test_x_forwarded_for_singleton_private_address(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '::1/128',
            'HTTP_X_REAL_IP': '74dc::02ba',
            'REMOTE_ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")

    def test_bad_x_forwarded_for_fallback_on_x_real_ip(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': 'unknown ::1/128',
            'REMOTE_ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "3ffe:1900:4545:3:200:f8ff:fe21:67cf")

    def test_empty_x_forwarded_for_fallback_on_x_real_ip(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '',
            'REMOTE_ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "3ffe:1900:4545:3:200:f8ff:fe21:67cf")

    def test_empty_x_forwarded_for_empty_x_real_ip_fallback_on_remote_addr(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '',
            'REMOTE_ADDR': '74dc::02ba',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")

    def test_empty_x_forwarded_for_private_x_real_ip_fallback_on_remote_addr(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '',
            'REMOTE_ADDR': '74dc::02ba',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")

    def test_private_x_forward_for_ip_addr(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '::1/128',
            'REMOTE_ADDR': '',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, None)

    def test_x_forwarded_for_singleton_hyphen_as_delimiter(self):
        request = HttpRequest()
        request.META = {
            'X-FORWARDED-FOR': '74dc::02ba',
            'REMOTE-ADDR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "74dc::02ba")


class IPv6TrustedProxiesTestCase(TestCase):
    """Trusted Proxies - IP address Test"""

    def test_http_x_forwarded_for_no_proxy(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba',
        }
        ip = get_trusted_ip(request, trusted_proxies=[])
        self.assertIsNone(ip)

    def test_http_x_forwarded_for_single_proxy(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '3ffe:1900:4545:3:200:f8ff:fe21:67cf, 74dc::02ba',
        }
        ip = get_trusted_ip(request, trusted_proxies=['74dc::02ba'])
        self.assertEqual(ip, "3ffe:1900:4545:3:200:f8ff:fe21:67cf")
