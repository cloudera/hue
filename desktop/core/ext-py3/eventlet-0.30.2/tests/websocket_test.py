import errno
import socket
import sys

import eventlet
from eventlet import event
from eventlet import greenio
from eventlet.green import httplib
import six
from eventlet.websocket import WebSocket, WebSocketWSGI

import tests
from tests import mock
import tests.wsgi_test


# demo app
def handle(ws):
    if ws.path == '/echo':
        while True:
            m = ws.wait()
            if m is None:
                break
            ws.send(m)
    elif ws.path == '/range':
        for i in range(10):
            ws.send("msg %d" % i)
            eventlet.sleep(0.01)
    elif ws.path == '/error':
        # some random socket error that we shouldn't normally get
        raise socket.error(errno.ENOTSOCK)
    else:
        ws.close()

wsapp = WebSocketWSGI(handle)


class TestWebSocket(tests.wsgi_test._TestBase):
    TEST_TIMEOUT = 5

    def set_site(self):
        self.site = wsapp

    def test_incorrect_headers(self):
        http = httplib.HTTPConnection(*self.server_addr)
        http.request("GET", "/echo")
        response = http.getresponse()
        assert response.status == 400

    def test_incomplete_headers_75(self):
        headers = dict(kv.split(': ') for kv in [
            "Upgrade: WebSocket",
            # NOTE: intentionally no connection header
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "WebSocket-Protocol: ws",
        ])
        http = httplib.HTTPConnection(*self.server_addr)
        http.request("GET", "/echo", headers=headers)
        resp = http.getresponse()

        self.assertEqual(resp.status, 400)
        self.assertEqual(resp.getheader('connection'), 'close')
        self.assertEqual(resp.read(), b'')

    def test_incomplete_headers_76(self):
        # First test: Missing Connection:
        headers = dict(kv.split(': ') for kv in [
            "Upgrade: WebSocket",
            # NOTE: intentionally no connection header
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Protocol: ws",
        ])
        http = httplib.HTTPConnection(*self.server_addr)
        http.request("GET", "/echo", headers=headers)
        resp = http.getresponse()

        self.assertEqual(resp.status, 400)
        self.assertEqual(resp.getheader('connection'), 'close')
        self.assertEqual(resp.read(), b'')

        # Now, miss off key2
        headers = dict(kv.split(': ') for kv in [
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Protocol: ws",
            "Sec-WebSocket-Key1: 4 @1  46546xW%0l 1 5",
            # NOTE: Intentionally no Key2 header
        ])
        http = httplib.HTTPConnection(*self.server_addr)
        http.request("GET", "/echo", headers=headers)
        resp = http.getresponse()

        self.assertEqual(resp.status, 400)
        self.assertEqual(resp.getheader('connection'), 'close')
        self.assertEqual(resp.read(), b'')

    def test_correct_upgrade_request_75(self):
        connect = [
            "GET /echo HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "WebSocket-Protocol: ws",
        ]
        sock = eventlet.connect(self.server_addr)

        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n'))
        result = sock.recv(1024)
        # The server responds the correct Websocket handshake
        self.assertEqual(result, six.b('\r\n'.join([
            'HTTP/1.1 101 Web Socket Protocol Handshake',
            'Upgrade: WebSocket',
            'Connection: Upgrade',
            'WebSocket-Origin: http://%s:%s' % self.server_addr,
            'WebSocket-Location: ws://%s:%s/echo\r\n\r\n' % self.server_addr,
        ])))

    def test_correct_upgrade_request_76(self):
        connect = [
            "GET /echo HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Protocol: ws",
            "Sec-WebSocket-Key1: 4 @1  46546xW%0l 1 5",
            "Sec-WebSocket-Key2: 12998 5 Y3 1  .P00",
        ]
        sock = eventlet.connect(self.server_addr)

        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n^n:ds[4U'))
        result = sock.recv(1024)
        # The server responds the correct Websocket handshake
        self.assertEqual(result, six.b('\r\n'.join([
            'HTTP/1.1 101 WebSocket Protocol Handshake',
            'Upgrade: WebSocket',
            'Connection: Upgrade',
            'Sec-WebSocket-Origin: http://%s:%s' % self.server_addr,
            'Sec-WebSocket-Protocol: ws',
            'Sec-WebSocket-Location: ws://%s:%s/echo\r\n\r\n8jKS\'y:G*Co,Wxa-' % self.server_addr,
        ])))

    def test_query_string(self):
        # verify that the query string comes out the other side unscathed
        connect = [
            "GET /echo?query_string HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Protocol: ws",
            "Sec-WebSocket-Key1: 4 @1  46546xW%0l 1 5",
            "Sec-WebSocket-Key2: 12998 5 Y3 1  .P00",
        ]
        sock = eventlet.connect(self.server_addr)

        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n^n:ds[4U'))
        result = sock.recv(1024)
        self.assertEqual(result, six.b('\r\n'.join([
            'HTTP/1.1 101 WebSocket Protocol Handshake',
            'Upgrade: WebSocket',
            'Connection: Upgrade',
            'Sec-WebSocket-Origin: http://%s:%s' % self.server_addr,
            'Sec-WebSocket-Protocol: ws',
            'Sec-WebSocket-Location: '
            'ws://%s:%s/echo?query_string\r\n\r\n8jKS\'y:G*Co,Wxa-' % self.server_addr,
        ])))

    def test_empty_query_string(self):
        # verify that a single trailing ? doesn't get nuked
        connect = [
            "GET /echo? HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Protocol: ws",
            "Sec-WebSocket-Key1: 4 @1  46546xW%0l 1 5",
            "Sec-WebSocket-Key2: 12998 5 Y3 1  .P00",
        ]
        sock = eventlet.connect(self.server_addr)

        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n^n:ds[4U'))
        result = sock.recv(1024)
        self.assertEqual(result, six.b('\r\n'.join([
            'HTTP/1.1 101 WebSocket Protocol Handshake',
            'Upgrade: WebSocket',
            'Connection: Upgrade',
            'Sec-WebSocket-Origin: http://%s:%s' % self.server_addr,
            'Sec-WebSocket-Protocol: ws',
            'Sec-WebSocket-Location: ws://%s:%s/echo?\r\n\r\n8jKS\'y:G*Co,Wxa-' % self.server_addr,
        ])))

    def test_sending_messages_to_websocket_75(self):
        connect = [
            "GET /echo HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "WebSocket-Protocol: ws",
        ]
        sock = eventlet.connect(self.server_addr)

        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n'))
        sock.recv(1024)
        sock.sendall(b'\x00hello\xFF')
        result = sock.recv(1024)
        self.assertEqual(result, b'\x00hello\xff')
        sock.sendall(b'\x00start')
        eventlet.sleep(0.001)
        sock.sendall(b' end\xff')
        result = sock.recv(1024)
        self.assertEqual(result, b'\x00start end\xff')
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        eventlet.sleep(0.01)

    def test_sending_messages_to_websocket_76(self):
        connect = [
            "GET /echo HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Protocol: ws",
            "Sec-WebSocket-Key1: 4 @1  46546xW%0l 1 5",
            "Sec-WebSocket-Key2: 12998 5 Y3 1  .P00",
        ]
        sock = eventlet.connect(self.server_addr)

        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n^n:ds[4U'))
        sock.recv(1024)
        sock.sendall(b'\x00hello\xFF')
        result = sock.recv(1024)
        self.assertEqual(result, b'\x00hello\xff')
        sock.sendall(b'\x00start')
        eventlet.sleep(0.001)
        sock.sendall(b' end\xff')
        result = sock.recv(1024)
        self.assertEqual(result, b'\x00start end\xff')
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        eventlet.sleep(0.01)

    def test_getting_messages_from_websocket_75(self):
        connect = [
            "GET /range HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "WebSocket-Protocol: ws",
        ]
        sock = eventlet.connect(self.server_addr)

        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n'))
        resp = sock.recv(1024)
        headers, result = resp.split(b'\r\n\r\n')
        msgs = [result.strip(b'\x00\xff')]
        cnt = 10
        while cnt:
            msgs.append(sock.recv(20).strip(b'\x00\xff'))
            cnt -= 1
        # Last item in msgs is an empty string
        self.assertEqual(msgs[:-1], [six.b('msg %d' % i) for i in range(10)])

    def test_getting_messages_from_websocket_76(self):
        connect = [
            "GET /range HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Protocol: ws",
            "Sec-WebSocket-Key1: 4 @1  46546xW%0l 1 5",
            "Sec-WebSocket-Key2: 12998 5 Y3 1  .P00",
        ]
        sock = eventlet.connect(self.server_addr)

        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n^n:ds[4U'))
        resp = sock.recv(1024)
        headers, result = resp.split(b'\r\n\r\n')
        msgs = [result[16:].strip(b'\x00\xff')]
        cnt = 10
        while cnt:
            msgs.append(sock.recv(20).strip(b'\x00\xff'))
            cnt -= 1
        # Last item in msgs is an empty string
        self.assertEqual(msgs[:-1], [six.b('msg %d' % i) for i in range(10)])

    def test_breaking_the_connection_75(self):
        error_detected = [False]
        done_with_request = event.Event()
        site = self.site

        def error_detector(environ, start_response):
            try:
                try:
                    return site(environ, start_response)
                except:
                    error_detected[0] = True
                    raise
            finally:
                done_with_request.send(True)
        self.site = error_detector
        self.spawn_server()
        connect = [
            "GET /range HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "WebSocket-Protocol: ws",
        ]
        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n'))
        sock.recv(1024)  # get the headers
        sock.close()  # close while the app is running
        done_with_request.wait()
        assert not error_detected[0]

    def test_breaking_the_connection_76(self):
        error_detected = [False]
        done_with_request = event.Event()
        site = self.site

        def error_detector(environ, start_response):
            try:
                try:
                    return site(environ, start_response)
                except:
                    error_detected[0] = True
                    raise
            finally:
                done_with_request.send(True)
        self.site = error_detector
        self.spawn_server()
        connect = [
            "GET /range HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Protocol: ws",
            "Sec-WebSocket-Key1: 4 @1  46546xW%0l 1 5",
            "Sec-WebSocket-Key2: 12998 5 Y3 1  .P00",
        ]
        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n^n:ds[4U'))
        sock.recv(1024)  # get the headers
        sock.close()  # close while the app is running
        done_with_request.wait()
        assert not error_detected[0]

    def test_client_closing_connection_76(self):
        error_detected = [False]
        done_with_request = event.Event()
        site = self.site

        def error_detector(environ, start_response):
            try:
                try:
                    return site(environ, start_response)
                except:
                    error_detected[0] = True
                    raise
            finally:
                done_with_request.send(True)
        self.site = error_detector
        self.spawn_server()
        connect = [
            "GET /echo HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Protocol: ws",
            "Sec-WebSocket-Key1: 4 @1  46546xW%0l 1 5",
            "Sec-WebSocket-Key2: 12998 5 Y3 1  .P00",
        ]
        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n^n:ds[4U'))
        sock.recv(1024)  # get the headers
        sock.sendall(b'\xff\x00')  # "Close the connection" packet.
        done_with_request.wait()
        assert not error_detected[0]

    def test_client_invalid_packet_76(self):
        error_detected = [False]
        done_with_request = event.Event()
        site = self.site

        def error_detector(environ, start_response):
            try:
                try:
                    return site(environ, start_response)
                except:
                    error_detected[0] = True
                    raise
            finally:
                done_with_request.send(True)
        self.site = error_detector
        self.spawn_server()
        connect = [
            "GET /echo HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Protocol: ws",
            "Sec-WebSocket-Key1: 4 @1  46546xW%0l 1 5",
            "Sec-WebSocket-Key2: 12998 5 Y3 1  .P00",
        ]
        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n^n:ds[4U'))
        sock.recv(1024)  # get the headers
        sock.sendall(b'\xef\x00')  # Weird packet.
        done_with_request.wait()
        assert error_detected[0]

    def test_server_closing_connect_76(self):
        connect = [
            "GET / HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Protocol: ws",
            "Sec-WebSocket-Key1: 4 @1  46546xW%0l 1 5",
            "Sec-WebSocket-Key2: 12998 5 Y3 1  .P00",
        ]
        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n^n:ds[4U'))
        resp = sock.recv(1024)
        headers, result = resp.split(b'\r\n\r\n')
        # The remote server should have immediately closed the connection.
        self.assertEqual(result[16:], b'\xff\x00')

    def test_app_socket_errors_75(self):
        error_detected = [False]
        done_with_request = event.Event()
        site = self.site

        def error_detector(environ, start_response):
            try:
                try:
                    return site(environ, start_response)
                except:
                    error_detected[0] = True
                    raise
            finally:
                done_with_request.send(True)
        self.site = error_detector
        self.spawn_server()
        connect = [
            "GET /error HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "WebSocket-Protocol: ws",
        ]
        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n'))
        sock.recv(1024)
        done_with_request.wait()
        assert error_detected[0]

    def test_app_socket_errors_76(self):
        error_detected = [False]
        done_with_request = event.Event()
        site = self.site

        def error_detector(environ, start_response):
            try:
                try:
                    return site(environ, start_response)
                except:
                    error_detected[0] = True
                    raise
            finally:
                done_with_request.send(True)
        self.site = error_detector
        self.spawn_server()
        connect = [
            "GET /error HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Protocol: ws",
            "Sec-WebSocket-Key1: 4 @1  46546xW%0l 1 5",
            "Sec-WebSocket-Key2: 12998 5 Y3 1  .P00",
        ]
        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n^n:ds[4U'))
        sock.recv(1024)
        done_with_request.wait()
        assert error_detected[0]

    def test_close_idle(self):
        pool = eventlet.GreenPool()
        # use log=stderr when test runner can capture it
        self.spawn_server(custom_pool=pool, log=sys.stdout)
        connect = (
            'GET /echo HTTP/1.1',
            'Upgrade: WebSocket',
            'Connection: Upgrade',
            'Host: %s:%s' % self.server_addr,
            'Origin: http://%s:%s' % self.server_addr,
            'Sec-WebSocket-Protocol: ws',
            'Sec-WebSocket-Key1: 4 @1  46546xW%0l 1 5',
            'Sec-WebSocket-Key2: 12998 5 Y3 1  .P00',
        )
        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n^n:ds[4U'))
        sock.recv(1024)
        sock.sendall(b'\x00hello\xff')
        result = sock.recv(1024)
        assert result, b'\x00hello\xff'
        self.killer.kill(KeyboardInterrupt)
        with eventlet.Timeout(1):
            pool.waitall()


class TestWebSocketSSL(tests.wsgi_test._TestBase):
    def set_site(self):
        self.site = wsapp

    @tests.skip_if_no_ssl
    def test_ssl_sending_messages(self):
        s = eventlet.wrap_ssl(eventlet.listen(('localhost', 0)),
                              certfile=tests.certificate_file,
                              keyfile=tests.private_key_file,
                              server_side=True)
        self.spawn_server(sock=s)
        connect = [
            "GET /echo HTTP/1.1",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Protocol: ws",
            "Sec-WebSocket-Key1: 4 @1  46546xW%0l 1 5",
            "Sec-WebSocket-Key2: 12998 5 Y3 1  .P00",
        ]
        sock = eventlet.wrap_ssl(eventlet.connect(self.server_addr))

        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n^n:ds[4U'))
        first_resp = b''
        while b'\r\n\r\n' not in first_resp:
            first_resp += sock.recv()
            print('resp now:')
            print(first_resp)
        # make sure it sets the wss: protocol on the location header
        loc_line = [x for x in first_resp.split(b"\r\n")
                    if x.lower().startswith(b'sec-websocket-location')][0]
        expect_wss = ('wss://%s:%s' % self.server_addr).encode()
        assert expect_wss in loc_line, "Expecting wss protocol in location: %s" % loc_line

        sock.sendall(b'\x00hello\xFF')
        result = sock.recv(1024)
        self.assertEqual(result, b'\x00hello\xff')
        sock.sendall(b'\x00start')
        eventlet.sleep(0.001)
        sock.sendall(b' end\xff')
        result = sock.recv(1024)
        self.assertEqual(result, b'\x00start end\xff')
        greenio.shutdown_safe(sock)
        sock.close()
        eventlet.sleep(0.01)


class TestWebSocketObject(tests.LimitedTestCase):

    def setUp(self):
        self.mock_socket = s = mock.Mock()
        self.environ = env = dict(HTTP_ORIGIN='http://localhost', HTTP_WEBSOCKET_PROTOCOL='ws',
                                  PATH_INFO='test')

        self.test_ws = WebSocket(s, env)
        super(TestWebSocketObject, self).setUp()

    def test_recieve(self):
        ws = self.test_ws
        ws.socket.recv.return_value = b'\x00hello\xFF'
        self.assertEqual(ws.wait(), 'hello')
        self.assertEqual(ws._buf, b'')
        self.assertEqual(len(ws._msgs), 0)
        ws.socket.recv.return_value = b''
        self.assertEqual(ws.wait(), None)
        self.assertEqual(ws._buf, b'')
        self.assertEqual(len(ws._msgs), 0)

    def test_send_to_ws(self):
        ws = self.test_ws
        ws.send(u'hello')
        assert ws.socket.sendall.called_with("\x00hello\xFF")
        ws.send(10)
        assert ws.socket.sendall.called_with("\x0010\xFF")

    def test_close_ws(self):
        ws = self.test_ws
        ws.close()
        assert ws.socket.shutdown.called_with(True)
