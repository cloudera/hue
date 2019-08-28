"""These tests use 3proxy software as http/socks4/socks5 proxy service.
The 3proxy binary is located in test/bin/3proxy
"""
from unittest import TestCase
import socket
import os
import signal
from subprocess import Popen
from threading import Thread
import threading

try:
    import urllib2 # py2
except ImportError:
    import urllib.request as urllib2 # py3
import psutil
import pytest

import sockshandler
import socks
from test.util import wait_for_socket

TEST_SERVER_HOST = 'localhost'
TEST_SERVER_HOST_IP = '127.0.0.1'
TEST_SERVER_PORT = 7777
PROXY_HOST_IP = '127.0.0.2'
HTTP_PROXY_PORT = 7776
SOCKS4_PROXY_PORT = 7775
SOCKS5_PROXY_PORT = 7774
# The 10.0.0.0 IP is used to emulate connection timeout errors
NON_ROUTABLE_IP = '10.0.0.0'


def proxy_thread():
    with open('3proxy.conf', 'w') as out:
        out.write('\n'.join((
            'allow *',
            'auth none',
            'proxy -a -n -p%d -e%s' % (HTTP_PROXY_PORT,
                                       PROXY_HOST_IP),
            'socks -p%d -e%s' % (SOCKS4_PROXY_PORT,
                                 PROXY_HOST_IP),
            'socks -p%d -e%s' % (SOCKS5_PROXY_PORT,
                                 PROXY_HOST_IP),
        )))
    cmd = 'test/bin/3proxy 3proxy.conf'
    server = Popen(cmd, shell=True)
    server.wait()


@pytest.fixture(scope='session', autouse=True)
def proxy_server():
    th = Thread(target=proxy_thread)
    th.daemon = True
    th.start()
    wait_for_socket('3proxy:http', PROXY_HOST_IP,
                    HTTP_PROXY_PORT)
    wait_for_socket('3proxy:socks4', PROXY_HOST_IP,
                    SOCKS4_PROXY_PORT)
    wait_for_socket('3proxy:socks5', PROXY_HOST_IP,
                    SOCKS5_PROXY_PORT)
    yield
    print('Active threads:')
    for th in threading.enumerate():
        print(' * %s' % th)

    parent = psutil.Process(os.getpid())
    print('Active child processes:')
    for child in parent.children(recursive=True):
        print(' * %s' % child)
        child.send_signal(signal.SIGINT)


class PySocksTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # import TestServer locally to avoid
        # pytest warning about skipped TestServer class
        from test_server import TestServer

        cls.test_server = TestServer(address=TEST_SERVER_HOST,
                                     port=TEST_SERVER_PORT,
                                     engine='subprocess')
        cls.test_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.test_server.stop()

    def setUp(self):
        self.test_server.reset()

    def build_http_request(self, host, port):
        if port == 80:
            port_fragment = ''
        else:
            port_fragment = ':%d' % port
        return (
            'GET / HTTP/1.1\r\n'
            'Host: %s%s\r\n'
            'User-Agent: PySocksTester\r\n'
            'Accept: text/html\r\n'
            '\r\n' % (host, port_fragment)
        ).encode()

    def assert_proxy_response(self, resp_data, content, address,
                              client_ip=None):
        status = resp_data.splitlines()[0]
        resp_body = resp_data.split(b'\r\n\r\n')[1]
        self.assertEqual(b'HTTP/1.1 200 OK', status)
        self.assertEqual('PySocksTester',
                         self.test_server.request['headers']['user-agent'])
        self.assertEqual('%s:%d' % address,
                         self.test_server.request['headers']['host'])
        self.assertEqual(content, resp_body)
        self.assertEqual(client_ip or PROXY_HOST_IP,
                         self.test_server.request['client_ip'])

    # 0/13
    def test_stdlib_socket(self):
        content = b'zzz'
        address = (TEST_SERVER_HOST, TEST_SERVER_PORT)
        self.test_server.response['data'] = content
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        sock.sendall(self.build_http_request(*address))
        data = sock.recv(2048)
        self.assert_proxy_response(data, content, address,
                                   client_ip=TEST_SERVER_HOST_IP)

    # 1/13
    def test_http_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (TEST_SERVER_HOST, TEST_SERVER_PORT)
        sock = socks.socksocket()
        sock.set_proxy(socks.HTTP, PROXY_HOST_IP, HTTP_PROXY_PORT)
        sock.connect(address)
        sock.sendall(self.build_http_request(*address))
        data = sock.recv(2048)
        self.assert_proxy_response(data, content, address)

    # 2/13
    def test_socks4_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (TEST_SERVER_HOST, TEST_SERVER_PORT)
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS4, PROXY_HOST_IP,
                       SOCKS4_PROXY_PORT)
        sock.connect(address)
        sock.sendall(self.build_http_request(*address))
        data = sock.recv(2048)
        self.assert_proxy_response(data, content, address)

    # 3/13
    def test_socks5_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (TEST_SERVER_HOST, TEST_SERVER_PORT)
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, PROXY_HOST_IP, SOCKS5_PROXY_PORT)
        sock.connect(address)
        sock.sendall(self.build_http_request(*address))
        data = sock.recv(2048)
        self.assert_proxy_response(data, content, address)

    # 3-1/13
    def test_urllib2_http_handler(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        opener = urllib2.build_opener(sockshandler.SocksiPyHandler(
            socks.HTTP, PROXY_HOST_IP, HTTP_PROXY_PORT))
        res = opener.open(self.test_server.get_url())
        body = res.read()
        self.assertTrue(self.test_server.request['headers']['user-agent']
                        .startswith('Python-urllib'))
        self.assertEqual('%s:%d' % (TEST_SERVER_HOST, TEST_SERVER_PORT),
                         self.test_server.request['headers']['host'])
        self.assertEqual(200, res.getcode())
        self.assertEqual(content, body)

    # 3-2/13
    def test_urllib2_socks4_handler(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        opener = urllib2.build_opener(sockshandler.SocksiPyHandler(
            socks.SOCKS4, PROXY_HOST_IP, SOCKS4_PROXY_PORT))
        res = opener.open(self.test_server.get_url())
        body = res.read()
        self.assertTrue(self.test_server.request['headers']['user-agent']
                        .startswith('Python-urllib'))
        self.assertEqual('%s:%d' % (TEST_SERVER_HOST, TEST_SERVER_PORT),
                         self.test_server.request['headers']['host'])
        self.assertEqual(200, res.getcode())
        self.assertEqual(content, body)

    # 3-3/13
    def test_urllib2_socks5_handler(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        opener = urllib2.build_opener(sockshandler.SocksiPyHandler(
            socks.SOCKS5, PROXY_HOST_IP, SOCKS5_PROXY_PORT))
        res = opener.open(self.test_server.get_url())
        body = res.read()
        self.assertTrue(self.test_server.request['headers']['user-agent']
                        .startswith('Python-urllib'))
        self.assertEqual('%s:%d' % (TEST_SERVER_HOST, TEST_SERVER_PORT),
                         self.test_server.request['headers']['host'])
        self.assertEqual(200, res.getcode())
        self.assertEqual(content, body)

    # 4/13
    def test_http_ip_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (TEST_SERVER_HOST_IP, TEST_SERVER_PORT)
        sock = socks.socksocket()
        sock.set_proxy(socks.HTTP, PROXY_HOST_IP, HTTP_PROXY_PORT)
        sock.connect(address)
        sock.sendall(self.build_http_request(*address))
        data = sock.recv(2048)
        self.assert_proxy_response(data, content, address)

    # 5/13
    def test_socks4_ip_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (TEST_SERVER_HOST_IP, TEST_SERVER_PORT)
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS4, PROXY_HOST_IP, SOCKS4_PROXY_PORT)
        sock.connect(address)
        sock.sendall(self.build_http_request(*address))
        data = sock.recv(2048)
        self.assert_proxy_response(data, content, address)

    # 6/13
    def test_socks5_ip_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (TEST_SERVER_HOST_IP, TEST_SERVER_PORT)
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, PROXY_HOST_IP, SOCKS5_PROXY_PORT)
        sock.connect(address)
        sock.sendall(self.build_http_request(*address))
        data = sock.recv(2048)
        self.assert_proxy_response(data, content, address)

    # 7/13
    def test_socks5_proxy_connect_timeout(self):
        """Test timeout during connecting to the proxy server"""
        sock = socks.socksocket()
        sock.settimeout(0.1)
        sock.set_proxy(socks.SOCKS5, NON_ROUTABLE_IP, SOCKS5_PROXY_PORT)
        address = (TEST_SERVER_HOST, TEST_SERVER_PORT)
        self.assertRaises(socks.ProxyConnectionError, sock.connect,
                          address)

        sock = socks.socksocket()
        sock.settimeout(0.1)
        sock.set_proxy(socks.SOCKS5, NON_ROUTABLE_IP, SOCKS5_PROXY_PORT)
        address = (TEST_SERVER_HOST, TEST_SERVER_PORT)
        try:
            sock.connect(address)
        except socks.ProxyConnectionError as ex:
            self.assertEqual(str(ex.socket_err), 'timed out')
        else:
            assert False

    # 8/13
    # TODO: imeplement server that accept connection slowly
    #def test_socks5_negotiation_timeout(self):
    #    """Test timeout during connection to to destination server"""
    #    sock = socks.socksocket()
    #    sock.settimeout(0.01)
    #    sock.set_proxy(socks.SOCKS5, PROXY_HOST_IP, SOCKS5_PROXY_PORT)
    #    address = (NON_ROUTABLE_IP, TEST_SERVER_PORT)
    #    self.assertRaises(socks.GeneralProxyError, sock.connect,
    #                      address)

    #    sock = socks.socksocket()
    #    sock.settimeout(0.1)
    #    sock.set_proxy(socks.SOCKS5, PROXY_HOST_IP, SOCKS5_PROXY_PORT)
    #    address = (NON_ROUTABLE_IP, TEST_SERVER_PORT)
    #    try:
    #        sock.connect(address)
    #    except socks.GeneralProxyError as ex:
    #        self.assertEqual(str(ex.socket_err), 'timed out')
    #    else:
    #        assert False

    # 8-1/13
    def test_socks5_read_timeout(self):
        """Test timeout during reading from the connected remote server"""
        self.test_server.response['sleep'] = 5

        sock = socks.socksocket()
        sock.settimeout(0.1)
        sock.set_proxy(socks.SOCKS5, PROXY_HOST_IP, SOCKS5_PROXY_PORT)
        address = (TEST_SERVER_HOST, TEST_SERVER_PORT)

        def func():
            sock.connect(address)
            sock.recv(1)

        self.assertRaises(socket.timeout, func)

    # 9/13
    def test_urllib2_http(self):
        original_socket = urllib2.socket.socket
        try:
            self.test_server.response['data'] = b'zzz'
            socks.set_default_proxy(socks.HTTP, PROXY_HOST_IP,
                                    HTTP_PROXY_PORT)
            socks.wrap_module(urllib2)
            address = (TEST_SERVER_HOST,
                       TEST_SERVER_PORT)
            url = 'http://%s:%d/' % address
            res = urllib2.urlopen(url)
            resp_body = res.read()
            self.assertEqual(200, res.getcode())
            self.assertEqual(b'zzz', resp_body)

            self.assertTrue(self.test_server
                            .request['headers']['user-agent']
                            .startswith('Python-urllib'))
            self.assertEqual('%s:%d' % address,
                             self.test_server.request['headers']['host'])
        finally:
            urllib2.socket.socket = original_socket

    # 10/13
    def test_urllib2_socks5(self):
        original_socket = urllib2.socket.socket
        try:
            self.test_server.response['data'] = b'zzz'
            socks.set_default_proxy(socks.SOCKS5, PROXY_HOST_IP,
                                    SOCKS5_PROXY_PORT)
            socks.wrap_module(urllib2)
            address = (TEST_SERVER_HOST,
                       TEST_SERVER_PORT)
            url = 'http://%s:%d/' % address
            res = urllib2.urlopen(url)
            resp_body = res.read()
            self.assertEqual(200, res.getcode())
            self.assertEqual(b'zzz', resp_body)

            self.assertTrue(self.test_server
                            .request['headers']['user-agent']
                            .startswith('Python-urllib'))
            self.assertEqual('%s:%d' % address,
                             self.test_server.request['headers']['host'])
        finally:
            urllib2.socket.socket = original_socket

    # 11/13
    def test_global_override_http(self):
        original_socket = socket.socket
        try:
            self.test_server.response['data'] = b'zzz'
            socks.set_default_proxy(socks.HTTP, PROXY_HOST_IP,
                                    HTTP_PROXY_PORT)
            socket.socket = socks.socksocket
            address = (TEST_SERVER_HOST,
                       TEST_SERVER_PORT)
            url = 'http://%s:%d/' % address
            res = urllib2.urlopen(url)
            resp_body = res.read()
            self.assertEqual(200, res.getcode())
            self.assertEqual(b'zzz', resp_body)

            self.assertTrue(self.test_server
                            .request['headers']['user-agent']
                            .startswith('Python-urllib'))
            self.assertEqual('%s:%d' % address,
                             self.test_server.request['headers']['host'])
        finally:
            socket.socket = original_socket

    # 12/13
    def test_global_override_socks5(self):
        original_socket = socket.socket
        try:
            self.test_server.response['data'] = b'zzz'
            socks.set_default_proxy(socks.SOCKS5, PROXY_HOST_IP,
                                    SOCKS5_PROXY_PORT)
            socket.socket = socks.socksocket
            address = (TEST_SERVER_HOST,
                       TEST_SERVER_PORT)
            url = 'http://%s:%d/' % address
            res = urllib2.urlopen(url)
            resp_body = res.read()
            self.assertEqual(200, res.getcode())
            self.assertEqual(b'zzz', resp_body)

            self.assertTrue(self.test_server
                            .request['headers']['user-agent']
                            .startswith('Python-urllib'))
            self.assertEqual('%s:%d' % address,
                             self.test_server.request['headers']['host'])
        finally:
            socket.socket = original_socket

    # 12/13
    def test_ipv6(self):
        sock = socks.socksocket()
        # (addr, scopeid, flowinfo, port)
        ipv6_tuple = ("::1", 1234, 0, 0)
        self.assertRaises(socket.error, sock.connect, ipv6_tuple)
