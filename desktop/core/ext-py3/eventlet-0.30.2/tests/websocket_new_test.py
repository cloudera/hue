import errno
import struct
import re

import eventlet
from eventlet import event
from eventlet import websocket
from eventlet.green import httplib
from eventlet.green import socket
import six

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


class TestWebSocketWithCompression(tests.wsgi_test._TestBase):
    TEST_TIMEOUT = 5

    def set_site(self):
        self.site = wsapp

    def setUp(self):
        super(TestWebSocketWithCompression, self).setUp()
        self.connect = '\r\n'.join([
            "GET /echo HTTP/1.1",
            "Upgrade: websocket",
            "Connection: upgrade",
            "Host: %s:%s" % self.server_addr,
            "Origin: http://%s:%s" % self.server_addr,
            "Sec-WebSocket-Version: 13",
            "Sec-WebSocket-Key: d9MXuOzlVQ0h+qRllvSCIg==",
            "Sec-WebSocket-Extensions: %s",
            '\r\n'
        ])
        self.handshake_re = re.compile(six.b('\r\n'.join([
            'HTTP/1.1 101 Switching Protocols',
            'Upgrade: websocket',
            'Connection: Upgrade',
            'Sec-WebSocket-Accept: ywSyWXCPNsDxLrQdQrn5RFNRfBU=',
            'Sec-WebSocket-Extensions: (.+)'
            '\r\n',
        ])))

    @staticmethod
    def get_deflated_reply(ws):
        msg = ws._recv_frame(None)
        msg.decompressor = None
        return msg.getvalue()

    def test_accept_basic_deflate_ext_13(self):
        for extension in [
            'permessage-deflate',
            'PeRMessAGe-dEFlaTe',
        ]:
            sock = eventlet.connect(self.server_addr)

            sock.sendall(six.b(self.connect % extension))
            result = sock.recv(1024)

            # The server responds the correct Websocket handshake
            # print('Extension offer: %r' % extension)
            match = re.match(self.handshake_re, result)
            assert match is not None
            assert len(match.groups()) == 1

    def test_accept_deflate_ext_context_takeover_13(self):
        for extension in [
            'permessage-deflate;CLient_No_conteXT_TAkeOver',
            'permessage-deflate;   SerVER_No_conteXT_TAkeOver',
            'permessage-deflate; server_no_context_takeover; client_no_context_takeover',
        ]:
            sock = eventlet.connect(self.server_addr)

            sock.sendall(six.b(self.connect % extension))
            result = sock.recv(1024)

            # The server responds the correct Websocket handshake
            # print('Extension offer: %r' % extension)
            match = re.match(self.handshake_re, result)
            assert match is not None
            assert len(match.groups()) == 1
            offered_ext_parts = (ex.strip().lower() for ex in extension.split(';'))
            accepted_ext_parts = match.groups()[0].decode().split('; ')
            assert all(oep in accepted_ext_parts for oep in offered_ext_parts)

    def test_accept_deflate_ext_window_max_bits_13(self):
        for extension_string, vals in [
            ('permessage-deflate; client_max_window_bits', [15]),
            ('permessage-deflate;   Server_Max_Window_Bits  =  11', [11]),
            ('permessage-deflate; server_max_window_bits; '
             'client_max_window_bits=9', [15, 9])
        ]:
            sock = eventlet.connect(self.server_addr)

            sock.sendall(six.b(self.connect % extension_string))
            result = sock.recv(1024)

            # The server responds the correct Websocket handshake
            # print('Extension offer: %r' % extension_string)
            match = re.match(self.handshake_re, result)
            assert match is not None
            assert len(match.groups()) == 1

            offered_parts = [part.strip().lower() for part in extension_string.split(';')]
            offered_parts_names = [part.split('=')[0].strip() for part in offered_parts]
            offered_parts_dict = dict(zip(offered_parts_names[1:], vals))

            accepted_ext_parts = match.groups()[0].decode().split('; ')
            assert accepted_ext_parts[0] == 'permessage-deflate'
            for param, val in (part.split('=') for part in accepted_ext_parts[1:]):
                assert int(val) == offered_parts_dict[param]

    def test_reject_max_window_bits_out_of_range_13(self):
        extension_string = ('permessage-deflate; client_max_window_bits=7,'
                            'permessage-deflate; server_max_window_bits=16, '
                            'permessage-deflate; client_max_window_bits=16; '
                            'server_max_window_bits=7, '
                            'permessage-deflate')
        sock = eventlet.connect(self.server_addr)

        sock.sendall(six.b(self.connect % extension_string))
        result = sock.recv(1024)

        # The server responds the correct Websocket handshake
        # print('Extension offer: %r' % extension_string)
        match = re.match(self.handshake_re, result)
        assert match.groups()[0] == b'permessage-deflate'

    def test_server_compress_with_context_takeover_13(self):
        extensions_string = 'permessage-deflate; client_no_context_takeover;'
        extensions = {'permessage-deflate': {
            'client_no_context_takeover': True,
            'server_no_context_takeover': False}}

        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b(self.connect % extensions_string))
        sock.recv(1024)
        ws = websocket.RFC6455WebSocket(sock, {}, client=True,
                                        extensions=extensions)

        # Deflated values taken from Section 7.2.3 of RFC 7692
        # https://tools.ietf.org/html/rfc7692#section-7.2.3
        ws.send(b'Hello')
        msg1 = self.get_deflated_reply(ws)
        assert msg1 == b'\xf2\x48\xcd\xc9\xc9\x07\x00'

        ws.send(b'Hello')
        msg2 = self.get_deflated_reply(ws)
        assert msg2 == b'\xf2\x00\x11\x00\x00'

        ws.close()
        eventlet.sleep(0.01)

    def test_server_compress_no_context_takeover_13(self):
        extensions_string = 'permessage-deflate; server_no_context_takeover;'
        extensions = {'permessage-deflate': {
            'client_no_context_takeover': False,
            'server_no_context_takeover': True}}

        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b(self.connect % extensions_string))
        sock.recv(1024)
        ws = websocket.RFC6455WebSocket(sock, {}, client=True,
                                        extensions=extensions)

        masked_msg1 = ws._pack_message(b'Hello', masked=True)
        ws._send(masked_msg1)
        masked_msg2 = ws._pack_message(b'Hello', masked=True)
        ws._send(masked_msg2)
        # Verify that client uses context takeover by checking
        # that the second message
        assert len(masked_msg2) < len(masked_msg1)

        # Verify that server drops context between messages
        # Deflated values taken from Section 7.2.3 of RFC 7692
        # https://tools.ietf.org/html/rfc7692#section-7.2.3
        reply_msg1 = self.get_deflated_reply(ws)
        assert reply_msg1 == b'\xf2\x48\xcd\xc9\xc9\x07\x00'
        reply_msg2 = self.get_deflated_reply(ws)
        assert reply_msg2 == b'\xf2\x48\xcd\xc9\xc9\x07\x00'

    def test_client_compress_with_context_takeover_13(self):
        extensions = {'permessage-deflate': {
            'client_no_context_takeover': False,
            'server_no_context_takeover': True}}
        ws = websocket.RFC6455WebSocket(None, {}, client=True,
                                        extensions=extensions)

        # Deflated values taken from Section 7.2.3 of RFC 7692
        # modified opcode to Binary instead of Text
        # https://tools.ietf.org/html/rfc7692#section-7.2.3
        packed_msg_1 = ws._pack_message(b'Hello', masked=False)
        assert packed_msg_1 == b'\xc2\x07\xf2\x48\xcd\xc9\xc9\x07\x00'
        packed_msg_2 = ws._pack_message(b'Hello', masked=False)
        assert packed_msg_2 == b'\xc2\x05\xf2\x00\x11\x00\x00'

        eventlet.sleep(0.01)

    def test_client_compress_no_context_takeover_13(self):
        extensions = {'permessage-deflate': {
            'client_no_context_takeover': True,
            'server_no_context_takeover': False}}
        ws = websocket.RFC6455WebSocket(None, {}, client=True,
                                        extensions=extensions)

        # Deflated values taken from Section 7.2.3 of RFC 7692
        # modified opcode to Binary instead of Text
        # https://tools.ietf.org/html/rfc7692#section-7.2.3
        packed_msg_1 = ws._pack_message(b'Hello', masked=False)
        assert packed_msg_1 == b'\xc2\x07\xf2\x48\xcd\xc9\xc9\x07\x00'
        packed_msg_2 = ws._pack_message(b'Hello', masked=False)
        assert packed_msg_2 == b'\xc2\x07\xf2\x48\xcd\xc9\xc9\x07\x00'

    def test_compressed_send_recv_13(self):
        extensions_string = 'permessage-deflate'
        extensions = {'permessage-deflate': {
            'client_no_context_takeover': False,
            'server_no_context_takeover': False}}

        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b(self.connect % extensions_string))
        sock.recv(1024)
        ws = websocket.RFC6455WebSocket(sock, {}, client=True, extensions=extensions)

        ws.send(b'hello')
        assert ws.wait() == b'hello'
        ws.send(b'hello world!')
        ws.send(u'hello world again!')
        assert ws.wait() == b'hello world!'
        assert ws.wait() == u'hello world again!'

        ws.close()
        eventlet.sleep(0.01)

    def test_send_uncompressed_msg_13(self):
        extensions_string = 'permessage-deflate'
        extensions = {'permessage-deflate': {
            'client_no_context_takeover': False,
            'server_no_context_takeover': False}}

        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b(self.connect % extensions_string))
        sock.recv(1024)

        # Send without using deflate, having rsv1 unset
        ws = websocket.RFC6455WebSocket(sock, {}, client=True)
        ws.send(b'Hello')

        # Adding extensions to recognise deflated response
        ws.extensions = extensions
        assert ws.wait() == b'Hello'

        ws.close()
        eventlet.sleep(0.01)

    def test_compressed_send_recv_client_no_context_13(self):
        extensions_string = 'permessage-deflate; client_no_context_takeover'
        extensions = {'permessage-deflate': {
            'client_no_context_takeover': True,
            'server_no_context_takeover': False}}

        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b(self.connect % extensions_string))
        sock.recv(1024)
        ws = websocket.RFC6455WebSocket(sock, {}, client=True, extensions=extensions)

        ws.send(b'hello')
        assert ws.wait() == b'hello'
        ws.send(b'hello world!')
        ws.send(u'hello world again!')
        assert ws.wait() == b'hello world!'
        assert ws.wait() == u'hello world again!'

        ws.close()
        eventlet.sleep(0.01)

    def test_compressed_send_recv_server_no_context_13(self):
        extensions_string = 'permessage-deflate; server_no_context_takeover'
        extensions = {'permessage-deflate': {
            'client_no_context_takeover': False,
            'server_no_context_takeover': False}}

        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b(self.connect % extensions_string))
        sock.recv(1024)
        ws = websocket.RFC6455WebSocket(sock, {}, client=True, extensions=extensions)

        ws.send(b'hello')
        assert ws.wait() == b'hello'
        ws.send(b'hello world!')
        ws.send(u'hello world again!')
        assert ws.wait() == b'hello world!'
        assert ws.wait() == u'hello world again!'

        ws.close()
        eventlet.sleep(0.01)

    def test_compressed_send_recv_both_no_context_13(self):
        extensions_string = ('permessage-deflate;'
                             ' server_no_context_takeover; client_no_context_takeover')
        extensions = {'permessage-deflate': {
            'client_no_context_takeover': True,
            'server_no_context_takeover': True}}

        sock = eventlet.connect(self.server_addr)
        sock.sendall(six.b(self.connect % extensions_string))
        sock.recv(1024)
        ws = websocket.RFC6455WebSocket(sock, {}, client=True, extensions=extensions)

        ws.send(b'hello')
        assert ws.wait() == b'hello'
        ws.send(b'hello world!')
        ws.send(u'hello world again!')
        assert ws.wait() == b'hello world!'
        assert ws.wait() == u'hello world again!'

        ws.close()
        eventlet.sleep(0.01)
