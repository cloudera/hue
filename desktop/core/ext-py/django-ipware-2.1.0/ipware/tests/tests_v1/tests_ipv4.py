# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpRequest
from django.test import TestCase
from ipware.ip import get_ip
from ipware.ip import get_real_ip
from ipware.ip import get_trusted_ip


class IPv4TestCase(TestCase):
    """IP address Test"""

    def test_meta_none(self):
        request = HttpRequest()
        request.META = {
        }
        ip = get_real_ip(request)
        self.assertIsNone(ip)

    def test_http_x_forwarded_for_multiple(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '192.168.255.182, 10.0.0.0, 127.0.0.1, 198.84.193.157, 177.139.233.139',
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "198.84.193.157")

    def test_http_x_forwarded_for_multiple_left_most_ip(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '192.168.255.182, 198.84.193.157, 10.0.0.0, 127.0.0.1, 177.139.233.139',
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "198.84.193.157")

    def test_http_x_forwarded_for_multiple_right_most_ip(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '192.168.255.182, 198.84.193.157, 10.0.0.0, 127.0.0.1, 177.139.233.139',
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request, right_most_proxy=True)
        self.assertEqual(ip, "177.139.233.139")

    def test_http_x_forwarded_for_multiple_right_most_ip_private(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '192.168.255.182, 198.84.193.157, 10.0.0.0, 127.0.0.1, 177.139.233.139',
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request, right_most_proxy=True)
        self.assertEqual(ip, "177.139.233.139")

    def test_http_x_forwarded_for_multiple_bad_address(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': 'unknown, 192.168.255.182, 10.0.0.0, 127.0.0.1, 198.84.193.157, 177.139.233.139',
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "198.84.193.157")

    def test_http_x_forwarded_for_singleton(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '177.139.233.139',
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "177.139.233.139")

    def test_http_x_forwarded_for_singleton_private_address(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '192.168.255.182',
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "177.139.233.132")

    def test_bad_http_x_forwarded_for_fallback_on_x_real_ip(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': 'unknown 177.139.233.139',
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "177.139.233.132")

    def test_empty_http_x_forwarded_for_fallback_on_x_real_ip(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '177.139.233.132',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "177.139.233.132")

    def test_empty_http_x_forwarded_for_empty_x_real_ip_fallback_on_remote_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "177.139.233.133")

    def test_empty_http_x_forwarded_for_private_x_real_ip_fallback_on_remote_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '192.168.255.182',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "177.139.233.133")

    def test_private_http_x_forward_for_ip_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '127.0.0.1',
            'HTTP_X_REAL_IP': '',
            'REMOTE_ADDR': '',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, None)

    def test_private_remote_addr_for_ip_addr(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '',
            'REMOTE_ADDR': '127.0.0.1',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, None)

    def test_missing_x_forwarded(self):
        request = HttpRequest()
        request.META = {
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "177.139.233.133")

    def test_missing_x_forwarded_missing_real_ip(self):
        request = HttpRequest()
        request.META = {
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "177.139.233.133")

    def test_best_matched_real_ip(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': '127.0.0.1',
            'REMOTE_ADDR': '177.31.233.133',
        }
        ip = get_ip(request)
        self.assertEqual(ip, "177.31.233.133")

    def test_best_matched_private_ip(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': '127.0.0.1',
            'REMOTE_ADDR': '192.31.233.133',
        }
        ip = get_ip(request)
        self.assertEqual(ip, "192.31.233.133")

    def test_best_matched_private_ip_2(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': '192.31.233.133',
            'REMOTE_ADDR': '127.0.0.1',
        }
        ip = get_ip(request)
        self.assertEqual(ip, "192.31.233.133")

    def test_x_forwarded_for_multiple(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '192.168.255.182, 10.0.0.0, 127.0.0.1, 198.84.193.157, 177.139.233.139',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "198.84.193.157")

    def test_x_forwarded_for_multiple_left_most_ip(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '192.168.255.182, 198.84.193.157, 10.0.0.0, 127.0.0.1, 177.139.233.139',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "198.84.193.157")

    def test_x_forwarded_for_multiple_right_most_ip(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '192.168.255.182, 198.84.193.157, 10.0.0.0, 127.0.0.1, 177.139.233.139',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request, right_most_proxy=True)
        self.assertEqual(ip, "177.139.233.139")

    def test_x_forwarded_for_multiple_right_most_ip_private(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '192.168.255.182, 198.84.193.157, 10.0.0.0, 127.0.0.1, 177.139.233.139',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request, right_most_proxy=True)
        self.assertEqual(ip, "177.139.233.139")

    def test_x_forwarded_for_multiple_bad_address(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': 'unknown, 192.168.255.182, 10.0.0.0, 127.0.0.1, 198.84.193.157, 177.139.233.139',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "198.84.193.157")

    def test_x_forwarded_for_singleton(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '177.139.233.139',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "177.139.233.139")

    def test_x_forwarded_for_singleton_private_address(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '192.168.255.182',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "177.139.233.133")

    def test_bad_x_forwarded_for_fallback_on_x_real_ip(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': 'unknown 177.139.233.139',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "177.139.233.133")

    def test_empty_x_forwarded_for_fallback_on_x_real_ip(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "177.139.233.133")

    def test_empty_x_forwarded_for_empty_x_real_ip_fallback_on_remote_addr(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "177.139.233.133")

    def test_empty_x_forwarded_for_private_x_real_ip_fallback_on_remote_addr(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "177.139.233.133")

    def test_private_x_forward_for_ip_addr(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '127.0.0.1',
            'REMOTE_ADDR': '',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, None)

    def test_x_forwarded_for_singleton_hyphen_as_delimiter(self):
        request = HttpRequest()
        request.META = {
            'X-FORWARDED-FOR': '177.139.233.139',
            'REMOTE-ADDR': '177.139.233.133',
        }
        ip = get_real_ip(request)
        self.assertEqual(ip, "177.139.233.139")


class IPv4TrustedProxiesTestCase(TestCase):
    """Trusted Proxies - IP address Test"""

    def test_meta_none(self):
        request = HttpRequest()
        request.META = {
        }
        ip = get_trusted_ip(request)
        self.assertIsNone(ip)

    def test_http_x_forwarded_for_conf_settings(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '198.84.193.157, 177.139.200.139, 177.139.233.100',
        }
        ip = get_trusted_ip(request)
        self.assertEqual(ip, "198.84.193.157")

    def test_http_x_forwarded_for_no_proxy(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '198.84.193.157, 177.139.200.139, 177.139.233.139',
        }
        ip = get_trusted_ip(request, trusted_proxies=[])
        self.assertIsNone(ip)

    def test_http_x_forwarded_for_single_proxy(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '198.84.193.157, 177.139.200.139, 177.139.233.139',
        }
        ip = get_trusted_ip(request, trusted_proxies=['177.139.233.139'])
        self.assertEqual(ip, "198.84.193.157")

    def test_http_x_forwarded_for_single_proxy_with_right_most(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '177.139.233.139, 177.139.200.139, 198.84.193.157',
        }
        ip = get_trusted_ip(request, right_most_proxy=True, trusted_proxies=['177.139.233.139'])
        self.assertEqual(ip, "198.84.193.157")

    def test_http_x_forwarded_for_multi_proxy(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '198.84.193.157, 177.139.200.139, 177.139.233.139',
        }
        ip = get_trusted_ip(request, trusted_proxies=['177.139.233.138', '177.139.233.139'])
        self.assertEqual(ip, "198.84.193.157")

    def test_http_x_forwarded_for_all_proxies_in_subnet(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '198.84.193.157, 177.139.200.139, 177.139.233.139',
        }
        ip = get_trusted_ip(request, trusted_proxies=['177.139.233'])
        self.assertEqual(ip, "198.84.193.157")

    def test_http_x_forwarded_for_all_proxies_in_subnet_2(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '198.84.193.157, 177.139.200.139, 177.139.233.139',
        }
        ip = get_trusted_ip(request, trusted_proxies=['177.139'])
        self.assertEqual(ip, "198.84.193.157")

    def test_x_forwarded_for_single_proxy(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '198.84.193.157, 177.139.200.139, 177.139.233.139',
        }
        ip = get_trusted_ip(request, trusted_proxies=['177.139.233.139'])
        self.assertEqual(ip, "198.84.193.157")

    def test_x_forwarded_for_single_proxy_hyphens(self):
        request = HttpRequest()
        request.META = {
            'X-FORWARDED-FOR': '198.84.193.157, 177.139.200.139, 177.139.233.139',
        }
        ip = get_trusted_ip(request, trusted_proxies=['177.139.233.139'])
        self.assertEqual(ip, "198.84.193.157")

    def test_http_x_forwarded_for_and_x_forward_for_single_proxy(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '198.84.193.156, 177.139.200.139, 177.139.233.139',
            'X_FORWARDED_FOR': '198.84.193.157, 177.139.200.139, 177.139.233.139',
        }
        ip = get_trusted_ip(request, trusted_proxies=['177.139.233.139'])
        self.assertEqual(ip, "198.84.193.156")
