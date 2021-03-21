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
            'HTTP_X_FORWARDED_FOR': '177.139.233.139, 198.84.193.157, 198.84.193.158',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("177.139.233.139", True))

    def test_meta_multi(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '177.139.233.139, 198.84.193.157, 198.84.193.158',
            'REMOTE_ADDR': '177.139.233.133',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("177.139.233.139", True))

    def test_meta_multi_precedence_order(self):
        request = HttpRequest()
        request.META = {
            'X_FORWARDED_FOR': '177.139.233.138, 198.84.193.157, 198.84.193.158',
            'HTTP_X_FORWARDED_FOR': '177.139.233.139, 198.84.193.157, 198.84.193.158',
            'REMOTE_ADDR': '177.139.233.133',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("177.139.233.139", True))

    def test_meta_proxy_order_left_most(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '177.139.233.139, 198.84.193.157, 198.84.193.158',
        }
        result = get_client_ip(request, proxy_order='left-most')
        self.assertEqual(result, ("177.139.233.139", True))

    def test_meta_proxy_order_right_most(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '177.139.233.139, 198.84.193.157, 198.84.193.158',
        }
        result = get_client_ip(request, proxy_order='right-most')
        self.assertEqual(result, ("198.84.193.158", True))

    def test_meta_multi_precedence_private_first(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '10.0.0.0, 10.0.0.1, 10.0.0.2',
            'X_FORWARDED_FOR': '177.139.233.138, 198.84.193.157, 198.84.193.158',
            'REMOTE_ADDR': '177.139.233.133',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("177.139.233.138", True))

    def test_meta_multi_precedence_invalid_first(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': 'unknown, 10.0.0.1, 10.0.0.2',
            'X_FORWARDED_FOR': '177.139.233.138, 198.84.193.157, 198.84.193.158',
            'REMOTE_ADDR': '177.139.233.133',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("177.139.233.138", True))

    def test_meta_error_only(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': 'unknown, 177.139.233.139, 198.84.193.157, 198.84.193.158',
        }
        result = get_client_ip(request)
        self.assertEqual(result, (None, False))

    def test_meta_error_first(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': 'unknown, 177.139.233.139, 198.84.193.157, 198.84.193.158',
            'X_FORWARDED_FOR': '177.139.233.138, 198.84.193.157, 198.84.193.158',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("177.139.233.138", True))

    def test_meta_singleton(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '177.139.233.139',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("177.139.233.139", True))

    def test_meta_singleton_proxy_count(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '177.139.233.139',
        }
        result = get_client_ip(request, proxy_count=1)
        self.assertEqual(result, (None, False))

    def test_meta_singleton_proxy_count_private(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '10.0.0.0',
            'HTTP_X_REAL_IP': '177.139.233.139',
        }
        result = get_client_ip(request, proxy_count=1)
        self.assertEqual(result, (None, False))

    def test_meta_singleton_private_fallback(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '10.0.0.0',
            'HTTP_X_REAL_IP': '177.139.233.139',
        }
        result = get_client_ip(request)
        self.assertEqual(result, ("177.139.233.139", True))

    def test_meta_proxy_trusted_ips(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '177.139.233.139, 198.84.193.157, 198.84.193.158',
        }
        result = get_client_ip(request, proxy_trusted_ips=['198.84.193.158'])
        self.assertEqual(result, ("177.139.233.139", True))

    def test_meta_proxy_trusted_ips_proxy_count(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '177.139.233.139, 198.84.193.157, 198.84.193.158',
        }
        result = get_client_ip(request, proxy_count=2, proxy_trusted_ips=['198.84.193.158'])
        self.assertEqual(result, ("177.139.233.139", True))

    def test_meta_proxy_trusted_ips_proxy_count_less_error(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '177.139.233.139, 198.84.193.158',
        }
        result = get_client_ip(request, proxy_count=2, proxy_trusted_ips=['198.84.193.158'])
        self.assertEqual(result, (None, False))

    def test_meta_proxy_trusted_ips_proxy_count_more_error(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '177.139.233.139, 198.84.193.157, 198.84.193.158',
        }
        result = get_client_ip(request, proxy_count=1, proxy_trusted_ips=['198.84.193.158'])
        self.assertEqual(result, (None, False))

    def test_meta_proxy_trusted_ips_proxy_count_more_error_fallback(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '177.139.233.139, 198.84.193.157, 198.84.193.158',
            'HTTP_X_REAL_IP': '177.139.233.139',
        }
        result = get_client_ip(request, proxy_count=1, proxy_trusted_ips=['198.84.193.158'])
        self.assertEqual(result, (None, False))

    def test_best_matched_ip(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': '192.168.1.1',
            'REMOTE_ADDR': '177.31.233.133',
        }
        ip = get_client_ip(request)
        self.assertEqual(ip, ("177.31.233.133", True))

    def test_best_matched_ip_public(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': '177.31.233.122',
            'REMOTE_ADDR': '177.31.233.133',
        }
        ip = get_client_ip(request)
        self.assertEqual(ip, ("177.31.233.122", True))

    def test_best_matched_ip_private(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': '192.168.1.1',
            'REMOTE_ADDR': '127.0.0.1',
        }
        ip = get_client_ip(request)
        self.assertEqual(ip, ("192.168.1.1", False))

    def test_best_matched_ip_private_precedence(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': '127.0.0.1',
            'REMOTE_ADDR': '192.168.1.1',
        }
        ip = get_client_ip(request)
        self.assertEqual(ip, ("192.168.1.1", False))

    def test_100_low_range_public(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': '100.63.0.9',
        }
        ip = get_client_ip(request)
        self.assertEqual(ip, ("100.63.0.9", True))

    def test_100_block_private(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': '100.76.0.9',
        }
        ip = get_client_ip(request)
        self.assertEqual(ip, ("100.76.0.9", False))

    def test_100_high_range_public(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': '100.128.0.9',
        }
        ip = get_client_ip(request)
        self.assertEqual(ip, ("100.128.0.9", True))

    def test_request_header_order_specific(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': '192.168.1.1',
            'REMOTE_ADDR': '177.139.233.139',
            'HTTP_X_FORWARDED_FOR': '177.139.233.139, 198.84.193.157, 198.84.193.158',
        }
        ip = get_client_ip(request, request_header_order=['HTTP_X_FORWARDED_FOR'])
        self.assertEqual(ip, ("177.139.233.139", True))


    def test_request_header_order_multiple(self):
        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '177.139.233.139, 198.84.193.157, 198.84.193.158',
            'X_FORWARDED_FOR': '177.139.233.138, 198.84.193.157, 198.84.193.158',
            'REMOTE_ADDR': '177.139.233.133',
        }
        ip = get_client_ip(request, request_header_order=['X_FORWARDED_FOR', 'HTTP_X_FORWARDED_FOR'])
        self.assertEqual(ip, ("177.139.233.138", True))
