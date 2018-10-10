import contextlib
import socket
import warnings

import eventlet
from eventlet import greenio
from eventlet.green import socket
try:
    from eventlet.green import ssl
except ImportError:
    __test__ = False
import six
import tests


def listen_ssl_socket(address=('localhost', 0), **kwargs):
    sock = ssl.wrap_socket(
        socket.socket(),
        tests.private_key_file,
        tests.certificate_file,
        server_side=True,
        **kwargs
    )
    sock.bind(address)
    sock.listen(50)
    return sock


class SSLTest(tests.LimitedTestCase):
    def setUp(self):
        # disabling socket.ssl warnings because we're testing it here
        warnings.filterwarnings(
            action='ignore',
            message='.*socket.ssl.*',
            category=DeprecationWarning)

        super(SSLTest, self).setUp()

    def test_duplex_response(self):
        def serve(listener):
            sock, addr = listener.accept()
            sock.recv(8192)
            sock.sendall(b'response')

        sock = listen_ssl_socket()

        server_coro = eventlet.spawn(serve, sock)

        client = ssl.wrap_socket(eventlet.connect(sock.getsockname()))
        client.sendall(b'line 1\r\nline 2\r\n\r\n')
        self.assertEqual(client.recv(8192), b'response')
        server_coro.wait()

    def test_ssl_close(self):
        def serve(listener):
            sock, addr = listener.accept()
            sock.recv(8192)
            try:
                self.assertEqual(b'', sock.recv(8192))
            except greenio.SSL.ZeroReturnError:
                pass

        sock = listen_ssl_socket()

        server_coro = eventlet.spawn(serve, sock)

        raw_client = eventlet.connect(sock.getsockname())
        client = ssl.wrap_socket(raw_client)
        client.sendall(b'X')
        greenio.shutdown_safe(client)
        client.close()
        server_coro.wait()

    def test_ssl_connect(self):
        def serve(listener):
            sock, addr = listener.accept()
            sock.recv(8192)
        sock = listen_ssl_socket()
        server_coro = eventlet.spawn(serve, sock)

        raw_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_client = ssl.wrap_socket(raw_client)
        ssl_client.connect(sock.getsockname())
        ssl_client.sendall(b'abc')
        greenio.shutdown_safe(ssl_client)
        ssl_client.close()
        server_coro.wait()

    def test_recv_after_ssl_connect(self):
        def serve(listener):
            sock, addr = listener.accept()
            sock.sendall(b'hjk')
        sock = listen_ssl_socket()
        server_coro = eventlet.spawn(serve, sock)

        raw_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_client = ssl.wrap_socket(raw_client)
        # Important: We need to call connect() on an SSL socket, not a plain one.
        # The bug was affecting that particular combination (create plain socket,
        # wrap, call connect() on the SSL socket and try to recv) on Python 3.5.
        ssl_client.connect(sock.getsockname())

        # The call to recv used to fail with:
        # Traceback (most recent call last):
        #   File "tests/ssl_test.py", line 99, in test_recv_after_ssl_connect
        #     self.assertEqual(ssl_client.recv(3), b'hjk')
        #   File "eventlet/green/ssl.py", line 194, in recv
        #     return self._base_recv(buflen, flags, into=False)
        #   File "eventlet/green/ssl.py", line 227, in _base_recv
        #     read = self.read(nbytes)
        #   File "eventlet/green/ssl.py", line 139, in read
        #     super(GreenSSLSocket, self).read, *args, **kwargs)
        #   File "eventlet/green/ssl.py", line 113, in _call_trampolining
        #     return func(*a, **kw)
        #   File "PYTHONLIB/python3.5/ssl.py", line 791, in read
        #     return self._sslobj.read(len, buffer)
        # TypeError: read() argument 2 must be read-write bytes-like object, not None
        self.assertEqual(ssl_client.recv(3), b'hjk')

        greenio.shutdown_safe(ssl_client)
        ssl_client.close()
        server_coro.wait()

    def test_ssl_unwrap(self):
        def serve():
            sock, addr = listener.accept()
            self.assertEqual(sock.recv(6), b'before')
            sock_ssl = ssl.wrap_socket(sock, tests.private_key_file, tests.certificate_file,
                                       server_side=True)
            sock_ssl.do_handshake()
            self.assertEqual(sock_ssl.recv(6), b'during')
            sock2 = sock_ssl.unwrap()
            self.assertEqual(sock2.recv(5), b'after')
            sock2.close()

        listener = eventlet.listen(('127.0.0.1', 0))
        server_coro = eventlet.spawn(serve)
        client = eventlet.connect(listener.getsockname())
        client.sendall(b'before')
        client_ssl = ssl.wrap_socket(client)
        client_ssl.do_handshake()
        client_ssl.sendall(b'during')
        client2 = client_ssl.unwrap()
        client2.sendall(b'after')
        server_coro.wait()

    def test_sendall_cpu_usage(self):
        """SSL socket.sendall() busy loop

        https://bitbucket.org/eventlet/eventlet/issue/134/greenssl-performance-issues

        Idea of this test is to check that GreenSSLSocket.sendall() does not busy loop
        retrying .send() calls, but instead trampolines until socket is writeable.

        BUFFER_SIZE and SENDALL_SIZE are magic numbers inferred through trial and error.
        """
        # Time limit resistant to busy loops
        self.set_alarm(1)

        stage_1 = eventlet.event.Event()
        BUFFER_SIZE = 1000
        SENDALL_SIZE = 100000

        def serve(listener):
            conn, _ = listener.accept()
            conn.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)
            self.assertEqual(conn.recv(8), b'request')
            conn.sendall(b'response')

            stage_1.wait()
            conn.sendall(b'x' * SENDALL_SIZE)

        server_sock = listen_ssl_socket()
        server_coro = eventlet.spawn(serve, server_sock)

        client_sock = eventlet.connect(server_sock.getsockname())
        client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
        client = ssl.wrap_socket(client_sock)
        client.sendall(b'request')
        self.assertEqual(client.recv(8), b'response')
        stage_1.send()

        tests.check_idle_cpu_usage(0.2, 0.1)
        server_coro.kill()

    def test_greensslobject(self):
        def serve(listener):
            sock, addr = listener.accept()
            sock.sendall(b'content')
            greenio.shutdown_safe(sock)
            sock.close()
        listener = listen_ssl_socket()
        eventlet.spawn(serve, listener)
        client = ssl.wrap_socket(eventlet.connect(listener.getsockname()))
        self.assertEqual(client.recv(1024), b'content')
        self.assertEqual(client.recv(1024), b'')

    def test_regression_gh_17(self):
        # https://github.com/eventlet/eventlet/issues/17
        # ssl wrapped but unconnected socket methods go special code path
        # test that path at least for syntax/typo errors
        sock = ssl.wrap_socket(socket.socket())
        sock.settimeout(0.01)
        try:
            sock.sendall(b'')
        except ssl.SSLError as e:
            assert 'timed out' in str(e)

    def test_no_handshake_block_accept_loop(self):
        listener = listen_ssl_socket()
        listener.settimeout(0.3)

        def serve(sock):
            try:
                name = sock.recv(8)
                sock.sendall(b'hello ' + name)
            except Exception:
                # ignore evil clients
                pass
            finally:
                greenio.shutdown_safe(sock)
                sock.close()

        def accept_loop():
            while True:
                try:
                    sock, _ = listener.accept()
                except socket.error:
                    return
                eventlet.spawn(serve, sock)

        loopt = eventlet.spawn(accept_loop)

        # evil no handshake
        evil = eventlet.connect(listener.getsockname())
        good = ssl.wrap_socket(eventlet.connect(listener.getsockname()))
        good.sendall(b'good')
        response = good.recv(16)
        good.close()
        assert response == b'hello good'
        evil.close()

        listener.close()
        loopt.wait()
        eventlet.sleep(0)

    def test_receiving_doesnt_block_if_there_is_already_decrypted_buffered_data(self):
        # Here's what could (and would) happen before the relevant bug was fixed (assuming method
        # M was trampolining unconditionally before actually reading):
        # 1. One side sends n bytes, leaves connection open (important)
        # 2. The other side uses method M to read m (where m < n) bytes, the underlying SSL
        #    implementation reads everything from the underlying socket, decrypts all n bytes,
        #    returns m of them and buffers n-m to be read later.
        # 3. The other side tries to read the remainder of the data (n-m bytes), this blocks
        #    because M trampolines uncoditionally and trampoline will hang because reading from
        #    the underlying socket would block. It would block because there's no data to be read
        #    and the connection is still open; leaving the connection open /mentioned in 1./ is
        #    important because otherwise trampoline would return immediately and the test would pass
        #    even with the bug still present in the code).
        #
        # The solution is to first request data from the underlying SSL implementation and only
        # trampoline if we actually need to read some data from the underlying socket.
        #
        # GreenSSLSocket.recv() wasn't broken but I've added code to test it as well for
        # completeness.
        content = b'xy'

        def recv(sock, expected):
            assert sock.recv(len(expected)) == expected

        def recv_into(sock, expected):
            buf = bytearray(len(expected))
            assert sock.recv_into(buf, len(expected)) == len(expected)
            assert buf == expected

        for read_function in [recv, recv_into]:
            print('Trying %s...' % (read_function,))
            listener = listen_ssl_socket()

            def accept(listener):
                sock, addr = listener.accept()
                sock.sendall(content)
                return sock

            accepter = eventlet.spawn(accept, listener)

            client_to_server = None
            try:
                client_to_server = ssl.wrap_socket(eventlet.connect(listener.getsockname()))
                for character in six.iterbytes(content):
                    character = six.int2byte(character)
                    print('We have %d already decrypted bytes pending, expecting: %s' % (
                        client_to_server.pending(), character))
                    read_function(client_to_server, character)
            finally:
                if client_to_server is not None:
                    client_to_server.close()
                server_to_client = accepter.wait()

                # Very important: we only want to close the socket *after* the other side has
                # read the data it wanted already, otherwise this would defeat the purpose of the
                # test (see the comment at the top of this test).
                server_to_client.close()

                listener.close()
