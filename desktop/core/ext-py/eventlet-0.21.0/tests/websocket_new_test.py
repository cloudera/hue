import errno
import struct

import eventlet
from eventlet import event
from eventlet import websocket
from eventlet.green import httplib
from eventlet.green import socket
from eventlet.support import six

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

wsapp = websocket.WebSocketWSGI(handle)


class TestWebSocket(tests.wsgi_test._TestBase):
    TEST_TIMEOUT = 5

    def set_site(self):
        self.site = wsapp

    def test_incomplete_headers_13(self):
        headers = dict(kv.split(': ') for kv in [
            "Upgrade: websocket",
            # NOTE: intentionally no connection header
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Version: 13",
        ])
        http = httplib.HTTPConnection(*self.server_addr)
        http.request("GET", "/echo", headers=headers)
        resp = http.getresponse()

        self.assertEqual(resp.status, 400)
        self.assertEqual(resp.getheader('connection'), 'close')
        self.assertEqual(resp.read(), b'')

        # Now, miss off key
        headers = dict(kv.split(': ') for kv in [
            "Upgrade: websocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Version: 13",
        ])
        http = httplib.HTTPConnection(*self.server_addr)
        http.request("GET", "/echo", headers=headers)
        resp = http.getresponse()

        self.assertEqual(resp.status, 400)
        self.assertEqual(resp.getheader('connection'), 'close')
        self.assertEqual(resp.read(), b'')

        # No Upgrade now
        headers = dict(kv.split(': ') for kv in [
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Version: 13",
        ])
        http = httplib.HTTPConnection(*self.server_addr)
        http.request("GET", "/echo", headers=headers)
        resp = http.getresponse()

        self.assertEqual(resp.status, 400)
        self.assertEqual(resp.getheader('connection'), 'close')
        self.assertEqual(resp.read(), b'')

    def test_correct_upgrade_request_13(self):
        for http_connection in ['Upgrade', 'UpGrAdE', 'keep-alive, Upgrade']:
            connect = [
                "GET /echo HTTP/1.1",
                "Upgrade: websocket",
                "Connection: %s" % http_connection,
                "Host: %s:%s" % self.server_addr,
                "Origin: http://%s:%s" % self.server_addr,
                "Sec-WebSocket-Version: 13",
                "Sec-WebSocket-Key: d9MXuOzlVQ0h+qRllvSCIg==",
            ]
            sock = eventlet.connect(self.server_addr)

            sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n'))
            result = sock.recv(1024)
            # The server responds the correct Websocket handshake
            print('Connection string: %r' % http_connection)
            self.assertEqual(result, six.b('\r\n'.join([
                'HTTP/1.1 101 Switching Protocols',
                'Upgrade: websocket',
                'Connection: Upgrade',
                'Sec-WebSocket-Accept: ywSyWXCPNsDxLrQdQrn5RFNRfBU=\r\n\r\n',
            ])))

    def test_send_recv_13(self):
        connect = [
            "GET /echo HTTP/1.1",
            "Upgrade: websocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Version: 13",
            "Sec-WebSocket-Key: d9MXuOzlVQ0h+qRllvSCIg==",
        ]
        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n'))
        sock.recv(1024)
        ws = websocket.RFC6455WebSocket(sock, {}, client=True)
        ws.send(b'hello')
        assert ws.wait() == b'hello'
        ws.send(b'hello world!\x01')
        ws.send(u'hello world again!')
        assert ws.wait() == b'hello world!\x01'
        assert ws.wait() == u'hello world again!'
        ws.close()
        eventlet.sleep(0.01)

    def test_breaking_the_connection_13(self):
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
            "Upgrade: websocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Version: 13",
            "Sec-WebSocket-Key: d9MXuOzlVQ0h+qRllvSCIg==",
        ]
        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n'))
        sock.recv(1024)  # get the headers
        sock.close()  # close while the app is running
        done_with_request.wait()
        assert not error_detected[0]

    def test_client_closing_connection_13(self):
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
            "Upgrade: websocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Version: 13",
            "Sec-WebSocket-Key: d9MXuOzlVQ0h+qRllvSCIg==",
        ]
        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n'))
        sock.recv(1024)  # get the headers
        closeframe = struct.pack('!BBIH', 1 << 7 | 8, 1 << 7 | 2, 0, 1000)
        sock.sendall(closeframe)  # "Close the connection" packet.
        done_with_request.wait()
        assert not error_detected[0]

    def test_client_invalid_packet_13(self):
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
            "Upgrade: websocket",
            "Connection: Upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Version: 13",
            "Sec-WebSocket-Key: d9MXuOzlVQ0h+qRllvSCIg==",
        ]
        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b('\r\n'.join(connect) + '\r\n\r\n'))
        sock.recv(1024)  # get the headers
        sock.sendall(b'\x07\xff')  # Weird packet.
        done_with_request.wait()
        assert not error_detected[0]
