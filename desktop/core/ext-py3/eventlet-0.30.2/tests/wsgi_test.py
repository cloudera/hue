# coding: utf-8
import cgi
import collections
import errno
import os
import shutil
import signal
import socket
import sys
import tempfile
import traceback

import eventlet
from eventlet import debug
from eventlet import event
from eventlet import greenio
from eventlet import greenthread
from eventlet import support
from eventlet import tpool
from eventlet import wsgi
from eventlet.green import socket as greensocket
from eventlet.green import ssl
from eventlet.support import bytes_to_str
import six
from six.moves.urllib import parse
import tests


certificate_file = os.path.join(os.path.dirname(__file__), 'test_server.crt')
private_key_file = os.path.join(os.path.dirname(__file__), 'test_server.key')


HttpReadResult = collections.namedtuple(
    'HttpReadResult',
    'status headers_lower body headers_original')


def hello_world(env, start_response):
    if env['PATH_INFO'] == 'notexist':
        start_response('404 Not Found', [('Content-type', 'text/plain')])
        return [b"not found"]

    start_response('200 OK', [('Content-type', 'text/plain')])
    return [b"hello world"]


def chunked_app(env, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    yield b"this"
    yield b"is"
    yield b"chunked"


def chunked_fail_app(environ, start_response):
    """http://rhodesmill.org/brandon/2013/chunked-wsgi/
    """
    headers = [('Content-Type', 'text/plain')]
    start_response('200 OK', headers)

    # We start streaming data just fine.
    yield b"The dwarves of yore made mighty spells,"
    yield b"While hammers fell like ringing bells"

    # Then the back-end fails!
    try:
        1 / 0
    except Exception:
        start_response('500 Error', headers, sys.exc_info())
        return

    # So rest of the response data is not available.
    yield b"In places deep, where dark things sleep,"
    yield b"In hollow halls beneath the fells."


def big_chunks(env, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    line = b'a' * 8192
    for x in range(10):
        yield line


def use_write(env, start_response):
    if env['PATH_INFO'] == '/a':
        write = start_response('200 OK', [('Content-type', 'text/plain'),
                                          ('Content-Length', '5')])
        write(b'abcde')
    if env['PATH_INFO'] == '/b':
        write = start_response('200 OK', [('Content-type', 'text/plain')])
        write(b'abcde')
    return []


def chunked_post(env, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    if env['PATH_INFO'] == '/a':
        return [env['wsgi.input'].read()]
    elif env['PATH_INFO'] == '/b':
        return [x for x in iter(lambda: env['wsgi.input'].read(4096), b'')]
    elif env['PATH_INFO'] == '/c':
        return [x for x in iter(lambda: env['wsgi.input'].read(1), b'')]


def already_handled(env, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    return wsgi.ALREADY_HANDLED


class Site(object):
    def __init__(self):
        self.application = hello_world

    def __call__(self, env, start_response):
        return self.application(env, start_response)


class IterableApp(object):

    def __init__(self, send_start_response=False, return_val=wsgi.ALREADY_HANDLED):
        self.send_start_response = send_start_response
        self.return_val = return_val
        self.env = {}

    def __call__(self, env, start_response):
        self.env = env
        if self.send_start_response:
            start_response('200 OK', [('Content-type', 'text/plain')])
        return self.return_val


class IterableSite(Site):
    def __call__(self, env, start_response):
        it = self.application(env, start_response)
        for i in it:
            yield i


CONTENT_LENGTH = 'content-length'


def recvall(sock):
    result = b''
    while True:
        chunk = sock.recv(16 << 10)
        if chunk == b'':
            return result
        result += chunk


class ConnectionClosed(Exception):
    pass


def send_expect_close(sock, buf):
    # Some tests will induce behavior that causes the remote end to
    # close the connection before all of the data has been written.
    # With small kernel buffer sizes, this can cause an EPIPE error.
    # Since the test expects an early close, this can be ignored.
    try:
        sock.sendall(buf)
    except socket.error as exc:
        if support.get_errno(exc) != errno.EPIPE:
            raise


def read_http(sock):
    fd = sock.makefile('rb')
    try:
        response_line = bytes_to_str(fd.readline().rstrip(b'\r\n'))
    except socket.error as exc:
        # TODO find out whether 54 is ok here or not, I see it when running tests
        # on Python 3
        if support.get_errno(exc) in (10053, 54):
            raise ConnectionClosed
        raise
    if not response_line:
        raise ConnectionClosed(response_line)

    header_lines = []
    while True:
        line = fd.readline()
        if line == b'\r\n':
            break
        else:
            header_lines.append(line)

    headers_original = {}
    headers_lower = {}
    for x in header_lines:
        x = x.strip()
        if not x:
            continue
        key, value = bytes_to_str(x, encoding='latin1').split(':', 1)
        key = key.rstrip()
        value = value.lstrip()
        key_lower = key.lower()
        # FIXME: Duplicate headers are allowed as per HTTP RFC standard,
        # the client and/or intermediate proxies are supposed to treat them
        # as a single header with values concatenated using space (' ') delimiter.
        assert key_lower not in headers_lower, "header duplicated: {0}".format(key)
        headers_original[key] = value
        headers_lower[key_lower] = value

    content_length_str = headers_lower.get(CONTENT_LENGTH.lower(), '')
    if content_length_str:
        num = int(content_length_str)
        body = fd.read(num)
    else:
        # read until EOF
        body = fd.read()

    result = HttpReadResult(
        status=response_line,
        headers_lower=headers_lower,
        body=body,
        headers_original=headers_original)
    return result


class _TestBase(tests.LimitedTestCase):
    def setUp(self):
        super(_TestBase, self).setUp()
        self.site = Site()
        self.killer = None
        self.set_site()
        self.spawn_server()

    def tearDown(self):
        greenthread.kill(self.killer)
        eventlet.sleep(0)
        super(_TestBase, self).tearDown()

    def spawn_server(self, **kwargs):
        """Spawns a new wsgi server with the given arguments using
        :meth:`spawn_thread`.

        Sets `self.server_addr` to (host, port) tuple suitable for `socket.connect`.
        """
        self.logfile = six.StringIO()
        new_kwargs = dict(max_size=128,
                          log=self.logfile,
                          site=self.site)
        new_kwargs.update(kwargs)

        if 'sock' not in new_kwargs:
            new_kwargs['sock'] = eventlet.listen(('localhost', 0))

        self.server_addr = new_kwargs['sock'].getsockname()
        self.spawn_thread(wsgi.server, **new_kwargs)

    def spawn_thread(self, target, **kwargs):
        """Spawns a new greenthread using specified target and arguments.

        Kills any previously-running server and sets self.killer to the
        greenthread running the target.
        """
        eventlet.sleep(0)  # give previous server a chance to start
        if self.killer:
            greenthread.kill(self.killer)

        self.killer = eventlet.spawn(target, **kwargs)

    def set_site(self):
        raise NotImplementedError


class TestHttpd(_TestBase):
    def set_site(self):
        self.site = Site()

    def test_001_server(self):
        sock = eventlet.connect(self.server_addr)

        sock.sendall(b'GET / HTTP/1.0\r\nHost: localhost\r\n\r\n')
        result = recvall(sock)
        # The server responds with the maximum version it supports
        assert result.startswith(b'HTTP'), result
        assert result.endswith(b'hello world'), result

    def test_002_keepalive(self):
        sock = eventlet.connect(self.server_addr)

        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        read_http(sock)
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        read_http(sock)

    def test_004_close_keepalive(self):
        sock = eventlet.connect(self.server_addr)

        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        result1 = read_http(sock)
        assert result1.status == 'HTTP/1.1 200 OK'
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        result2 = read_http(sock)
        assert result2.status == 'HTTP/1.1 200 OK'
        assert result2.headers_lower['connection'] == 'close'
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        self.assertRaises(ConnectionClosed, read_http, sock)

    def test_006_reject_long_urls(self):
        sock = eventlet.connect(self.server_addr)
        path_parts = []
        for ii in range(3000):
            path_parts.append('path')
        path = '/'.join(path_parts)
        request = 'GET /%s HTTP/1.0\r\nHost: localhost\r\n\r\n' % path
        send_expect_close(sock, request.encode())
        fd = sock.makefile('rb')
        result = fd.readline()
        if result:
            # windows closes the socket before the data is flushed,
            # so we never get anything back
            status = result.split(b' ')[1]
            self.assertEqual(status, b'414')
        fd.close()

    def test_007_get_arg(self):
        # define a new handler that does a get_arg as well as a read_body
        def new_app(env, start_response):
            body = bytes_to_str(env['wsgi.input'].read())
            a = parse.parse_qs(body).get('a', [1])[0]
            start_response('200 OK', [('Content-type', 'text/plain')])
            return [six.b('a is %s, body is %s' % (a, body))]

        self.site.application = new_app
        sock = eventlet.connect(self.server_addr)
        request = b'\r\n'.join((
            b'POST / HTTP/1.0',
            b'Host: localhost',
            b'Content-Length: 3',
            b'',
            b'a=a'))
        sock.sendall(request)

        # send some junk after the actual request
        sock.sendall(b'01234567890123456789')
        result = read_http(sock)
        self.assertEqual(result.body, b'a is a, body is a=a')

    def test_008_correctresponse(self):
        sock = eventlet.connect(self.server_addr)

        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        result_200 = read_http(sock)
        sock.sendall(b'GET /notexist HTTP/1.1\r\nHost: localhost\r\n\r\n')
        read_http(sock)
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        result_test = read_http(sock)
        self.assertEqual(result_200.status, result_test.status)

    def test_009_chunked_response(self):
        self.site.application = chunked_app
        sock = eventlet.connect(self.server_addr)

        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        assert b'Transfer-Encoding: chunked' in recvall(sock)

    def test_010_no_chunked_http_1_0(self):
        self.site.application = chunked_app
        sock = eventlet.connect(self.server_addr)

        sock.sendall(b'GET / HTTP/1.0\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        assert b'Transfer-Encoding: chunked' not in recvall(sock)

    def test_011_multiple_chunks(self):
        self.site.application = big_chunks
        sock = eventlet.connect(self.server_addr)

        fd = sock.makefile('rwb')
        fd.write(b'GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        fd.flush()
        headers = b''
        while True:
            line = fd.readline()
            if line == b'\r\n':
                break
            else:
                headers += line
        assert b'Transfer-Encoding: chunked' in headers
        chunks = 0
        chunklen = int(fd.readline(), 16)
        while chunklen:
            chunks += 1
            fd.read(chunklen)
            fd.readline()  # CRLF
            chunklen = int(fd.readline(), 16)
        assert chunks > 1
        response = fd.read()
        # Require a CRLF to close the message body
        self.assertEqual(response, b'\r\n')

    def test_partial_writes_are_handled(self):
        # https://github.com/eventlet/eventlet/issues/295
        # Eventlet issue: "Python 3: wsgi doesn't handle correctly partial
        # write of socket send() when using writelines()".
        #
        # The bug was caused by the default writelines() implementaiton
        # (used by the wsgi module) which doesn't check if write()
        # successfully completed sending *all* data therefore data could be
        # lost and the client could be left hanging forever.
        #
        # Switching wsgi wfile to buffered mode fixes the issue.
        #
        # Related CPython issue: "Raw I/O writelines() broken",
        # http://bugs.python.org/issue26292
        #
        # Custom accept() and send() in order to simulate a connection that
        # only sends one byte at a time so that any code that doesn't handle
        # partial writes correctly has to fail.
        listen_socket = eventlet.listen(('localhost', 0))
        original_accept = listen_socket.accept

        def accept():
            connection, address = original_accept()
            original_send = connection.send

            def send(b, *args):
                b = b[:1]
                return original_send(b, *args)

            connection.send = send
            return connection, address

        listen_socket.accept = accept

        def application(env, start_response):
            # Sending content-length is important here so that the client knows
            # exactly how many bytes does it need to wait for.
            start_response('200 OK', [('Content-length', 3)])
            yield 'asd'

        self.spawn_server(sock=listen_socket)
        self.site.application = application
        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        # This would previously hang forever
        result = read_http(sock)
        assert result.body == b'asd'

    @tests.skip_if_no_ssl
    def test_012_ssl_server(self):
        def wsgi_app(environ, start_response):
            start_response('200 OK', {})
            return [environ['wsgi.input'].read()]

        certificate_file = os.path.join(os.path.dirname(__file__), 'test_server.crt')
        private_key_file = os.path.join(os.path.dirname(__file__), 'test_server.key')

        server_sock = eventlet.wrap_ssl(eventlet.listen(('localhost', 0)),
                                        certfile=certificate_file,
                                        keyfile=private_key_file,
                                        server_side=True)
        self.spawn_server(sock=server_sock, site=wsgi_app)

        sock = eventlet.connect(self.server_addr)
        sock = eventlet.wrap_ssl(sock)
        sock.write(
            b'POST /foo HTTP/1.1\r\nHost: localhost\r\n'
            b'Connection: close\r\nContent-length:3\r\n\r\nabc')
        result = recvall(sock)
        assert result.endswith(b'abc')

    @tests.skip_if_no_ssl
    def test_013_empty_return(self):
        def wsgi_app(environ, start_response):
            start_response("200 OK", [])
            return [b""]

        certificate_file = os.path.join(os.path.dirname(__file__), 'test_server.crt')
        private_key_file = os.path.join(os.path.dirname(__file__), 'test_server.key')
        server_sock = eventlet.wrap_ssl(eventlet.listen(('localhost', 0)),
                                        certfile=certificate_file,
                                        keyfile=private_key_file,
                                        server_side=True)
        self.spawn_server(sock=server_sock, site=wsgi_app)

        sock = eventlet.connect(('localhost', server_sock.getsockname()[1]))
        sock = eventlet.wrap_ssl(sock)
        sock.write(b'GET /foo HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        result = recvall(sock)
        assert result[-4:] == b'\r\n\r\n'

    def test_014_chunked_post(self):
        self.site.application = chunked_post
        sock = eventlet.connect(self.server_addr)
        fd = sock.makefile('rwb')
        fd.write('PUT /a HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n'
                 'Transfer-Encoding: chunked\r\n\r\n'
                 '2\r\noh\r\n4\r\n hai\r\n0\r\n\r\n'.encode())
        fd.flush()
        while True:
            if fd.readline() == b'\r\n':
                break
        response = fd.read()
        assert response == b'oh hai', 'invalid response %s' % response

        sock = eventlet.connect(self.server_addr)
        fd = sock.makefile('rwb')
        fd.write('PUT /b HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n'
                 'Transfer-Encoding: chunked\r\n\r\n'
                 '2\r\noh\r\n4\r\n hai\r\n0\r\n\r\n'.encode())
        fd.flush()
        while True:
            if fd.readline() == b'\r\n':
                break
        response = fd.read()
        assert response == b'oh hai', 'invalid response %s' % response

        sock = eventlet.connect(self.server_addr)
        fd = sock.makefile('rwb')
        fd.write('PUT /c HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n'
                 'Transfer-Encoding: chunked\r\n\r\n'
                 '2\r\noh\r\n4\r\n hai\r\n0\r\n\r\n'.encode())
        fd.flush()
        while True:
            if fd.readline() == b'\r\n':
                break
        response = fd.read(8192)
        assert response == b'oh hai', 'invalid response %s' % response

    def test_015_write(self):
        self.site.application = use_write
        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET /a HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        result1 = read_http(sock)
        assert 'content-length' in result1.headers_lower

        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET /b HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        result2 = read_http(sock)
        assert 'transfer-encoding' in result2.headers_lower
        assert result2.headers_lower['transfer-encoding'] == 'chunked'

    def test_016_repeated_content_length(self):
        """content-length header was being doubled up if it was set in
        start_response and could also be inferred from the iterator
        """
        def wsgi_app(environ, start_response):
            start_response('200 OK', [('Content-Length', '7')])
            return [b'testing']
        self.site.application = wsgi_app
        sock = eventlet.connect(self.server_addr)
        fd = sock.makefile('rwb')
        fd.write(b'GET /a HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        fd.flush()
        header_lines = []
        while True:
            line = fd.readline()
            if line == b'\r\n':
                break
            else:
                header_lines.append(line)
        self.assertEqual(1, len(
            [l for l in header_lines if l.lower().startswith(b'content-length')]))

    @tests.skip_if_no_ssl
    def test_017_ssl_zeroreturnerror(self):

        def server(sock, site, log):
            try:
                serv = wsgi.Server(sock, sock.getsockname(), site, log)
                client_socket, addr = sock.accept()
                serv.process_request([addr, client_socket, wsgi.STATE_IDLE])
                return True
            except Exception:
                traceback.print_exc()
                return False

        def wsgi_app(environ, start_response):
            start_response('200 OK', [])
            return [environ['wsgi.input'].read()]

        certificate_file = os.path.join(os.path.dirname(__file__), 'test_server.crt')
        private_key_file = os.path.join(os.path.dirname(__file__), 'test_server.key')

        sock = eventlet.wrap_ssl(
            eventlet.listen(('localhost', 0)),
            certfile=certificate_file, keyfile=private_key_file,
            server_side=True)
        server_coro = eventlet.spawn(server, sock, wsgi_app, self.logfile)

        client = eventlet.connect(('localhost', sock.getsockname()[1]))
        client = eventlet.wrap_ssl(client)
        client.write(b'X')  # non-empty payload so that SSL handshake occurs
        greenio.shutdown_safe(client)
        client.close()

        success = server_coro.wait()
        assert success

    def test_018_http_10_keepalive(self):
        # verify that if an http/1.0 client sends connection: keep-alive
        # that we don't close the connection
        sock = eventlet.connect(self.server_addr)

        sock.sendall(b'GET / HTTP/1.0\r\nHost: localhost\r\nConnection: keep-alive\r\n\r\n')
        result1 = read_http(sock)
        assert 'connection' in result1.headers_lower
        self.assertEqual('keep-alive', result1.headers_lower['connection'])

        # repeat request to verify connection is actually still open
        sock.sendall(b'GET / HTTP/1.0\r\nHost: localhost\r\nConnection: keep-alive\r\n\r\n')
        result2 = read_http(sock)
        assert 'connection' in result2.headers_lower
        self.assertEqual('keep-alive', result2.headers_lower['connection'])
        sock.close()

    def test_019_fieldstorage_compat(self):
        def use_fieldstorage(environ, start_response):
            cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
            start_response('200 OK', [('Content-type', 'text/plain')])
            return [b'hello!']

        self.site.application = use_fieldstorage
        sock = eventlet.connect(self.server_addr)

        sock.sendall(b'POST / HTTP/1.1\r\n'
                     b'Host: localhost\r\n'
                     b'Connection: close\r\n'
                     b'Transfer-Encoding: chunked\r\n\r\n'
                     b'2\r\noh\r\n'
                     b'4\r\n hai\r\n0\r\n\r\n')
        assert b'hello!' in recvall(sock)

    def test_020_x_forwarded_for(self):
        request_bytes = (
            b'GET / HTTP/1.1\r\nHost: localhost\r\n'
            + b'X-Forwarded-For: 1.2.3.4, 5.6.7.8\r\n\r\n'
        )

        sock = eventlet.connect(self.server_addr)
        sock.sendall(request_bytes)
        sock.recv(1024)
        sock.close()
        assert '1.2.3.4,5.6.7.8,127.0.0.1' in self.logfile.getvalue()

        # turning off the option should work too
        self.logfile = six.StringIO()
        self.spawn_server(log_x_forwarded_for=False)

        sock = eventlet.connect(self.server_addr)
        sock.sendall(request_bytes)
        sock.recv(1024)
        sock.close()
        assert '1.2.3.4' not in self.logfile.getvalue()
        assert '5.6.7.8' not in self.logfile.getvalue()
        assert '127.0.0.1' in self.logfile.getvalue()

    def test_socket_remains_open(self):
        greenthread.kill(self.killer)
        server_sock = eventlet.listen(('localhost', 0))
        server_sock_2 = server_sock.dup()
        self.spawn_server(sock=server_sock_2)
        # do a single req/response to verify it's up
        sock = eventlet.connect(server_sock.getsockname())
        sock.sendall(b'GET / HTTP/1.0\r\nHost: localhost\r\n\r\n')
        result = sock.recv(1024)
        assert result.startswith(b'HTTP'), result
        assert result.endswith(b'hello world'), result

        # shut down the server and verify the server_socket fd is still open,
        # but the actual socketobject passed in to wsgi.server is closed
        greenthread.kill(self.killer)
        eventlet.sleep(0)  # make the kill go through
        try:
            server_sock_2.accept()
            # shouldn't be able to use this one anymore
        except socket.error as exc:
            self.assertEqual(support.get_errno(exc), errno.EBADF)
        self.spawn_server(sock=server_sock)
        sock = eventlet.connect(server_sock.getsockname())
        sock.sendall(b'GET / HTTP/1.0\r\nHost: localhost\r\n\r\n')
        result = sock.recv(1024)
        assert result.startswith(b'HTTP'), result
        assert result.endswith(b'hello world'), result

    def test_021_environ_clobbering(self):
        def clobberin_time(environ, start_response):
            for environ_var in [
                    'wsgi.version', 'wsgi.url_scheme',
                    'wsgi.input', 'wsgi.errors', 'wsgi.multithread',
                    'wsgi.multiprocess', 'wsgi.run_once', 'REQUEST_METHOD',
                    'SCRIPT_NAME', 'RAW_PATH_INFO', 'PATH_INFO', 'QUERY_STRING',
                    'CONTENT_TYPE', 'CONTENT_LENGTH', 'SERVER_NAME', 'SERVER_PORT',
                    'SERVER_PROTOCOL']:
                environ[environ_var] = None
            start_response('200 OK', [('Content-type', 'text/plain')])
            return []
        self.site.application = clobberin_time
        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.1\r\n'
                     b'Host: localhost\r\n'
                     b'Connection: close\r\n'
                     b'\r\n\r\n')
        assert b'200 OK' in recvall(sock)

    def test_022_custom_pool(self):
        # just test that it accepts the parameter for now
        # TODO(waitall): test that it uses the pool and that you can waitall() to
        # ensure that all clients finished
        p = eventlet.GreenPool(5)
        self.spawn_server(custom_pool=p)

        # this stuff is copied from test_001_server, could be better factored
        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.0\r\nHost: localhost\r\n\r\n')
        result = recvall(sock)
        assert result.startswith(b'HTTP'), result
        assert result.endswith(b'hello world'), result

    def test_023_bad_content_length(self):
        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.0\r\nHost: localhost\r\nContent-length: argh\r\n\r\n')
        result = recvall(sock)
        assert result.startswith(b'HTTP'), result
        assert b'400 Bad Request' in result, result
        assert b'500' not in result, result

        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.0\r\nHost: localhost\r\nContent-length:\r\n\r\n')
        result = recvall(sock)
        assert result.startswith(b'HTTP'), result
        assert b'400 Bad Request' in result, result
        assert b'500' not in result, result

        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.0\r\nHost: localhost\r\nContent-length: \r\n\r\n')
        result = recvall(sock)
        assert result.startswith(b'HTTP'), result
        assert b'400 Bad Request' in result, result
        assert b'500' not in result, result

        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.0\r\nHost: localhost\r\nContent-length: -10\r\n\r\n')
        result = recvall(sock)
        assert result.startswith(b'HTTP'), result
        assert b'400 Bad Request' in result, result
        assert b'500' not in result, result

    def test_024_expect_100_continue(self):
        def wsgi_app(environ, start_response):
            if int(environ['CONTENT_LENGTH']) > 1024:
                start_response('417 Expectation Failed', [('Content-Length', '7')])
                return [b'failure']
            else:
                text = environ['wsgi.input'].read()
                start_response('200 OK', [('Content-Length', str(len(text)))])
                return [text]
        self.site.application = wsgi_app
        sock = eventlet.connect(self.server_addr)
        fd = sock.makefile('rwb')
        fd.write(b'PUT / HTTP/1.1\r\nHost: localhost\r\nContent-length: 1025\r\n'
                 b'Expect: 100-continue\r\n\r\n')
        fd.flush()
        result = read_http(sock)
        self.assertEqual(result.status, 'HTTP/1.1 417 Expectation Failed')
        self.assertEqual(result.body, b'failure')

        for expect_value in ('100-continue', '100-Continue'):
            fd.write(
                'PUT / HTTP/1.1\r\nHost: localhost\r\nContent-length: 7\r\n'
                'Expect: {}\r\n\r\ntesting'.format(expect_value).encode())
            fd.flush()
            header_lines = []
            while True:
                line = fd.readline()
                if line == b'\r\n':
                    break
                else:
                    header_lines.append(line)
            assert header_lines[0].startswith(b'HTTP/1.1 100 Continue')
            header_lines = []
            while True:
                line = fd.readline()
                if line == b'\r\n':
                    break
                else:
                    header_lines.append(line)
            assert header_lines[0].startswith(b'HTTP/1.1 200 OK')
            assert fd.read(7) == b'testing'
        fd.close()
        sock.close()

    def test_024a_expect_100_continue_with_headers(self):
        def wsgi_app(environ, start_response):
            if int(environ['CONTENT_LENGTH']) > 1024:
                start_response('417 Expectation Failed', [('Content-Length', '7')])
                return [b'failure']
            else:
                environ['wsgi.input'].set_hundred_continue_response_headers(
                    [('Hundred-Continue-Header-1', 'H1'),
                     ('Hundred-Continue-Header-2', 'H2'),
                     ('Hundred-Continue-Header-k', 'Hk')])
                text = environ['wsgi.input'].read()
                start_response('200 OK', [('Content-Length', str(len(text)))])
                return [text]
        self.site.application = wsgi_app
        sock = eventlet.connect(self.server_addr)
        fd = sock.makefile('rwb')
        fd.write(b'PUT / HTTP/1.1\r\nHost: localhost\r\nContent-length: 1025\r\n'
                 b'Expect: 100-continue\r\n\r\n')
        fd.flush()
        result = read_http(sock)
        self.assertEqual(result.status, 'HTTP/1.1 417 Expectation Failed')
        self.assertEqual(result.body, b'failure')
        fd.write(
            b'PUT / HTTP/1.1\r\nHost: localhost\r\nContent-length: 7\r\n'
            b'Expect: 100-continue\r\n\r\ntesting')
        fd.flush()
        header_lines = []
        while True:
            line = fd.readline()
            if line == b'\r\n':
                break
            else:
                header_lines.append(line.strip())
        assert header_lines[0].startswith(b'HTTP/1.1 100 Continue')
        headers = dict((k, v) for k, v in (h.split(b': ', 1) for h in header_lines[1:]))
        assert b'Hundred-Continue-Header-1' in headers
        assert b'Hundred-Continue-Header-2' in headers
        assert b'Hundred-Continue-Header-K' in headers
        self.assertEqual(b'H1', headers[b'Hundred-Continue-Header-1'])
        self.assertEqual(b'H2', headers[b'Hundred-Continue-Header-2'])
        self.assertEqual(b'Hk', headers[b'Hundred-Continue-Header-K'])
        header_lines = []
        while True:
            line = fd.readline()
            if line == b'\r\n':
                break
            else:
                header_lines.append(line)
        assert header_lines[0].startswith(b'HTTP/1.1 200 OK')
        self.assertEqual(fd.read(7), b'testing')
        fd.close()
        sock.close()

    def test_024b_expect_100_continue_with_headers_multiple_chunked(self):
        def wsgi_app(environ, start_response):
            environ['wsgi.input'].set_hundred_continue_response_headers(
                [('Hundred-Continue-Header-1', 'H1'),
                 ('Hundred-Continue-Header-2', 'H2')])
            text = environ['wsgi.input'].read()

            environ['wsgi.input'].set_hundred_continue_response_headers(
                [('Hundred-Continue-Header-3', 'H3')])
            environ['wsgi.input'].send_hundred_continue_response()

            text += environ['wsgi.input'].read()

            start_response('200 OK', [('Content-Length', str(len(text)))])
            return [text]
        self.site.application = wsgi_app
        sock = eventlet.connect(self.server_addr)
        fd = sock.makefile('rwb')
        fd.write(b'PUT /a HTTP/1.1\r\n'
                 b'Host: localhost\r\nConnection: close\r\n'
                 b'Transfer-Encoding: chunked\r\n'
                 b'Expect: 100-continue\r\n\r\n')
        fd.flush()

        # Expect 1st 100-continue response
        header_lines = []
        while True:
            line = fd.readline()
            if line == b'\r\n':
                break
            else:
                header_lines.append(line.strip())
        assert header_lines[0].startswith(b'HTTP/1.1 100 Continue')
        headers = dict((k, v) for k, v in (h.split(b': ', 1)
                                           for h in header_lines[1:]))
        assert b'Hundred-Continue-Header-1' in headers
        assert b'Hundred-Continue-Header-2' in headers
        self.assertEqual(b'H1', headers[b'Hundred-Continue-Header-1'])
        self.assertEqual(b'H2', headers[b'Hundred-Continue-Header-2'])

        # Send message 1
        fd.write(b'5\r\nfirst\r\n8\r\n message\r\n0\r\n\r\n')
        fd.flush()

        # Expect a 2nd 100-continue response
        header_lines = []
        while True:
            line = fd.readline()
            if line == b'\r\n':
                break
            else:
                header_lines.append(line.strip())
        assert header_lines[0].startswith(b'HTTP/1.1 100 Continue')
        headers = dict((k, v) for k, v in (h.split(b': ', 1)
                                           for h in header_lines[1:]))
        assert b'Hundred-Continue-Header-3' in headers
        self.assertEqual(b'H3', headers[b'Hundred-Continue-Header-3'])

        # Send message 2
        fd.write(b'8\r\n, second\r\n8\r\n message\r\n0\r\n\r\n')
        fd.flush()

        # Expect final 200-OK
        header_lines = []
        while True:
            line = fd.readline()
            if line == b'\r\n':
                break
            else:
                header_lines.append(line.strip())
        assert header_lines[0].startswith(b'HTTP/1.1 200 OK')

        self.assertEqual(fd.read(29), b'first message, second message')
        fd.close()
        sock.close()

    def test_024c_expect_100_continue_with_headers_multiple_nonchunked(self):
        def wsgi_app(environ, start_response):

            environ['wsgi.input'].set_hundred_continue_response_headers(
                [('Hundred-Continue-Header-1', 'H1'),
                 ('Hundred-Continue-Header-2', 'H2')])
            text = environ['wsgi.input'].read(13)

            environ['wsgi.input'].set_hundred_continue_response_headers(
                [('Hundred-Continue-Header-3', 'H3')])
            environ['wsgi.input'].send_hundred_continue_response()

            text += environ['wsgi.input'].read(16)

            start_response('200 OK', [('Content-Length', str(len(text)))])
            return [text]

        self.site.application = wsgi_app
        sock = eventlet.connect(self.server_addr)
        fd = sock.makefile('rwb')
        fd.write(b'PUT /a HTTP/1.1\r\n'
                 b'Host: localhost\r\nConnection: close\r\n'
                 b'Content-Length: 29\r\n'
                 b'Expect: 100-continue\r\n\r\n')
        fd.flush()

        # Expect 1st 100-continue response
        header_lines = []
        while True:
            line = fd.readline()
            if line == b'\r\n':
                break
            else:
                header_lines.append(line.strip())
        assert header_lines[0].startswith(b'HTTP/1.1 100 Continue')
        headers = dict((k, v) for k, v in (h.split(b': ', 1)
                                           for h in header_lines[1:]))
        assert b'Hundred-Continue-Header-1' in headers
        assert b'Hundred-Continue-Header-2' in headers
        self.assertEqual(b'H1', headers[b'Hundred-Continue-Header-1'])
        self.assertEqual(b'H2', headers[b'Hundred-Continue-Header-2'])

        # Send message 1
        fd.write(b'first message')
        fd.flush()

        # Expect a 2nd 100-continue response
        header_lines = []
        while True:
            line = fd.readline()
            if line == b'\r\n':
                break
            else:
                header_lines.append(line.strip())
        assert header_lines[0].startswith(b'HTTP/1.1 100 Continue')
        headers = dict((k, v) for k, v in (h.split(b': ', 1)
                                           for h in header_lines[1:]))
        assert b'Hundred-Continue-Header-3' in headers
        self.assertEqual(b'H3', headers[b'Hundred-Continue-Header-3'])

        # Send message 2
        fd.write(b', second message\r\n')
        fd.flush()

        # Expect final 200-OK
        header_lines = []
        while True:
            line = fd.readline()
            if line == b'\r\n':
                break
            else:
                header_lines.append(line.strip())
        assert header_lines[0].startswith(b'HTTP/1.1 200 OK')

        self.assertEqual(fd.read(29), b'first message, second message')
        fd.close()
        sock.close()

    def test_024d_expect_100_continue_with_eager_app_chunked(self):
        def wsgi_app(environ, start_response):
            # app knows it's going to do some time-intensive thing and doesn't
            # want clients to time out, so it's protocol says to:
            # * generally expect a successful status code,
            # * be prepared to eat some whitespace that will get dribbled out
            #   periodically, and
            # * parse the final status from the response body.
            environ['eventlet.minimum_write_chunk_size'] = 0
            start_response('202 Accepted', [])

            def resp_gen():
                yield b' '
                environ['wsgi.input'].read()
                yield b' '
                yield b'\n503 Service Unavailable\n\nOops!\n'

            return resp_gen()

        self.site.application = wsgi_app
        sock = eventlet.connect(self.server_addr)
        fd = sock.makefile('rwb')
        fd.write(b'PUT /a HTTP/1.1\r\n'
                 b'Host: localhost\r\nConnection: close\r\n'
                 b'Transfer-Encoding: chunked\r\n'
                 b'Expect: 100-continue\r\n\r\n')
        fd.flush()

        # Expect the optimistic response
        header_lines = []
        while True:
            line = fd.readline()
            if line == b'\r\n':
                break
            else:
                header_lines.append(line.strip())
        self.assertEqual(header_lines[0], b'HTTP/1.1 202 Accepted')

        def chunkify(data):
            return '{:x}'.format(len(data)).encode('ascii') + b'\r\n' + data + b'\r\n'

        def expect_chunk(data):
            expected = chunkify(data)
            self.assertEqual(expected, fd.read(len(expected)))

        # Can even see that initial whitespace
        expect_chunk(b' ')

        # Send message
        fd.write(chunkify(b'some data'))
        fd.write(chunkify(b''))  # end-of-message
        fd.flush()

        # Expect final response
        expect_chunk(b' ')
        expect_chunk(b'\n503 Service Unavailable\n\nOops!\n')
        expect_chunk(b'')  # end-of-message

        fd.close()
        sock.close()

    def test_025_accept_errors(self):
        debug.hub_exceptions(True)
        listener = greensocket.socket()
        listener.bind(('localhost', 0))
        # NOT calling listen, to trigger the error
        with tests.capture_stderr() as log:
            self.spawn_server(sock=listener)
            eventlet.sleep(0)  # need to enter server loop
            try:
                eventlet.connect(self.server_addr)
                self.fail("Didn't expect to connect")
            except socket.error as exc:
                self.assertEqual(support.get_errno(exc), errno.ECONNREFUSED)

        log_content = log.getvalue()
        assert 'Invalid argument' in log_content, log_content
        debug.hub_exceptions(False)

    def test_026_log_format(self):
        self.spawn_server(log_format="HI %(request_line)s HI")
        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET /yo! HTTP/1.1\r\nHost: localhost\r\n\r\n')
        sock.recv(1024)
        sock.close()
        assert '\nHI GET /yo! HTTP/1.1 HI\n' in self.logfile.getvalue(), self.logfile.getvalue()

    def test_close_chunked_with_1_0_client(self):
        # verify that if we return a generator from our app
        # and we're not speaking with a 1.1 client, that we
        # close the connection
        self.site.application = chunked_app
        sock = eventlet.connect(self.server_addr)

        sock.sendall(b'GET / HTTP/1.0\r\nHost: localhost\r\nConnection: keep-alive\r\n\r\n')

        result = read_http(sock)
        self.assertEqual(result.headers_lower['connection'], 'close')
        self.assertNotEqual(result.headers_lower.get('transfer-encoding'), 'chunked')
        self.assertEqual(result.body, b"thisischunked")

    def test_chunked_response_when_app_yields_empty_string(self):
        def empty_string_chunked_app(env, start_response):
            env['eventlet.minimum_write_chunk_size'] = 0  # no buffering
            start_response('200 OK', [('Content-type', 'text/plain')])
            return iter([b"stuff", b"", b"more stuff"])

        self.site.application = empty_string_chunked_app
        sock = eventlet.connect(self.server_addr)

        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')

        result = read_http(sock)
        self.assertEqual(result.headers_lower.get('transfer-encoding'), 'chunked')
        self.assertEqual(result.body, b"5\r\nstuff\r\na\r\nmore stuff\r\n0\r\n\r\n")

    def test_minimum_chunk_size_parameter_leaves_httpprotocol_class_member_intact(self):
        start_size = wsgi.HttpProtocol.minimum_chunk_size

        self.spawn_server(minimum_chunk_size=start_size * 2)
        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        read_http(sock)

        self.assertEqual(wsgi.HttpProtocol.minimum_chunk_size, start_size)
        sock.close()

    def test_error_in_chunked_closes_connection(self):
        # From http://rhodesmill.org/brandon/2013/chunked-wsgi/
        self.spawn_server(minimum_chunk_size=1)

        self.site.application = chunked_fail_app
        sock = eventlet.connect(self.server_addr)

        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')

        result = read_http(sock)
        self.assertEqual(result.status, 'HTTP/1.1 200 OK')
        self.assertEqual(result.headers_lower.get('transfer-encoding'), 'chunked')
        expected_body = (
            b'27\r\nThe dwarves of yore made mighty spells,\r\n'
            b'25\r\nWhile hammers fell like ringing bells\r\n')
        self.assertEqual(result.body, expected_body)

        # verify that socket is closed by server
        self.assertEqual(sock.recv(1), b'')

    def test_026_http_10_nokeepalive(self):
        # verify that if an http/1.0 client sends connection: keep-alive
        # and the server doesn't accept keep-alives, we close the connection
        self.spawn_server(keepalive=False)
        sock = eventlet.connect(self.server_addr)

        sock.sendall(b'GET / HTTP/1.0\r\nHost: localhost\r\nConnection: keep-alive\r\n\r\n')
        result = read_http(sock)
        self.assertEqual(result.headers_lower['connection'], 'close')

    def test_027_keepalive_chunked(self):
        self.site.application = chunked_post
        sock = eventlet.connect(self.server_addr)
        common_suffix = (
            b'Host: localhost\r\nTransfer-Encoding: chunked\r\n\r\n' +
            b'10\r\n0123456789abcdef\r\n0\r\n\r\n')
        sock.sendall(b'PUT /a HTTP/1.1\r\n' + common_suffix)
        read_http(sock)
        sock.sendall(b'PUT /b HTTP/1.1\r\n' + common_suffix)
        read_http(sock)
        sock.sendall(b'PUT /c HTTP/1.1\r\n' + common_suffix)
        read_http(sock)
        sock.sendall(b'PUT /a HTTP/1.1\r\n' + common_suffix)
        read_http(sock)
        sock.close()

    @tests.skip_if_no_ssl
    def test_028_ssl_handshake_errors(self):
        errored = [False]

        def server(sock):
            try:
                wsgi.server(sock=sock, site=hello_world, log=self.logfile)
                errored[0] = 'SSL handshake error caused wsgi.server to exit.'
            except greenthread.greenlet.GreenletExit:
                pass
            except Exception as e:
                errored[0] = 'SSL handshake error raised exception %s.' % e
                raise
        for data in ('', 'GET /non-ssl-request HTTP/1.0\r\n\r\n'):
            srv_sock = eventlet.wrap_ssl(
                eventlet.listen(('localhost', 0)),
                certfile=certificate_file, keyfile=private_key_file,
                server_side=True)
            addr = srv_sock.getsockname()
            g = eventlet.spawn_n(server, srv_sock)
            client = eventlet.connect(addr)
            if data:  # send non-ssl request
                client.sendall(data.encode())
            else:  # close sock prematurely
                client.close()
            eventlet.sleep(0)  # let context switch back to server
            assert not errored[0], errored[0]
            # make another request to ensure the server's still alive
            try:
                client = ssl.wrap_socket(eventlet.connect(addr))
                client.write(b'GET / HTTP/1.0\r\nHost: localhost\r\n\r\n')
                result = recvall(client)
                assert result.startswith(b'HTTP'), result
                assert result.endswith(b'hello world')
            except ImportError:
                pass  # TODO(openssl): should test with OpenSSL
            greenthread.kill(g)

    def test_029_posthooks(self):
        posthook1_count = [0]
        posthook2_count = [0]

        def posthook1(env, value, multiplier=1):
            self.assertEqual(env['local.test'], 'test_029_posthooks')
            posthook1_count[0] += value * multiplier

        def posthook2(env, value, divisor=1):
            self.assertEqual(env['local.test'], 'test_029_posthooks')
            posthook2_count[0] += value / divisor

        def one_posthook_app(env, start_response):
            env['local.test'] = 'test_029_posthooks'
            if 'eventlet.posthooks' not in env:
                start_response('500 eventlet.posthooks not supported',
                               [('Content-Type', 'text/plain')])
            else:
                env['eventlet.posthooks'].append(
                    (posthook1, (2,), {'multiplier': 3}))
                start_response('200 OK', [('Content-Type', 'text/plain')])
            yield b''
        self.site.application = one_posthook_app
        sock = eventlet.connect(self.server_addr)
        fp = sock.makefile('rwb')
        fp.write(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        fp.flush()
        self.assertEqual(fp.readline(), b'HTTP/1.1 200 OK\r\n')
        fp.close()
        sock.close()
        self.assertEqual(posthook1_count[0], 6)
        self.assertEqual(posthook2_count[0], 0)

        def two_posthook_app(env, start_response):
            env['local.test'] = 'test_029_posthooks'
            if 'eventlet.posthooks' not in env:
                start_response('500 eventlet.posthooks not supported',
                               [('Content-Type', 'text/plain')])
            else:
                env['eventlet.posthooks'].append(
                    (posthook1, (4,), {'multiplier': 5}))
                env['eventlet.posthooks'].append(
                    (posthook2, (100,), {'divisor': 4}))
                start_response('200 OK', [('Content-Type', 'text/plain')])
            yield b''
        self.site.application = two_posthook_app
        sock = eventlet.connect(self.server_addr)
        fp = sock.makefile('rwb')
        fp.write(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        fp.flush()
        self.assertEqual(fp.readline(), b'HTTP/1.1 200 OK\r\n')
        fp.close()
        sock.close()
        self.assertEqual(posthook1_count[0], 26)
        self.assertEqual(posthook2_count[0], 25)

    def test_030_reject_long_header_lines(self):
        sock = eventlet.connect(self.server_addr)
        request = 'GET / HTTP/1.0\r\nHost: localhost\r\nLong: %s\r\n\r\n' % \
            ('a' * 10000)
        send_expect_close(sock, request.encode())
        result = read_http(sock)
        self.assertEqual(result.status, 'HTTP/1.0 400 Header Line Too Long')

    def test_031_reject_large_headers(self):
        sock = eventlet.connect(self.server_addr)
        headers = ('Name: %s\r\n' % ('a' * 7000,)) * 20
        request = 'GET / HTTP/1.0\r\nHost: localhost\r\n%s\r\n\r\n' % headers
        send_expect_close(sock, request.encode())
        result = read_http(sock)
        self.assertEqual(result.status, 'HTTP/1.0 400 Headers Too Large')

    def test_032_wsgi_input_as_iterable(self):
        # https://bitbucket.org/eventlet/eventlet/issue/150
        # env['wsgi.input'] returns a single byte at a time
        # when used as an iterator
        g = [0]

        def echo_by_iterating(env, start_response):
            start_response('200 OK', [('Content-type', 'text/plain')])
            for chunk in env['wsgi.input']:
                g[0] += 1
                yield chunk

        self.site.application = echo_by_iterating
        upload_data = b'123456789abcdef' * 100
        request = (
            'POST / HTTP/1.0\r\n'
            'Host: localhost\r\n'
            'Content-Length: %i\r\n\r\n%s'
        ) % (len(upload_data), bytes_to_str(upload_data))
        sock = eventlet.connect(self.server_addr)
        sock.sendall(request.encode())
        result = read_http(sock)
        self.assertEqual(result.body, upload_data)
        self.assertEqual(g[0], 1)

    def test_zero_length_chunked_response(self):
        def zero_chunked_app(env, start_response):
            start_response('200 OK', [('Content-type', 'text/plain')])
            yield b""

        self.site.application = zero_chunked_app
        sock = eventlet.connect(self.server_addr)

        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        response = recvall(sock).split(b'\r\n')
        headers = []
        while True:
            h = response.pop(0)
            headers.append(h)
            if h == b'':
                break
        assert b'Transfer-Encoding: chunked' in b''.join(headers), headers
        # should only be one chunk of zero size with two blank lines
        # (one terminates the chunk, one terminates the body)
        self.assertEqual(response, [b'0', b'', b''])

    def test_configurable_url_length_limit(self):
        self.spawn_server(url_length_limit=20000)
        sock = eventlet.connect(self.server_addr)
        path = 'x' * 15000
        request = 'GET /%s HTTP/1.0\r\nHost: localhost\r\n\r\n' % path
        fd = sock.makefile('rwb')
        fd.write(request.encode())
        fd.flush()
        result = fd.readline()
        if result:
            # windows closes the socket before the data is flushed,
            # so we never get anything back
            status = result.split(b' ')[1]
            self.assertEqual(status, b'200')
        fd.close()

    def test_aborted_chunked_post(self):
        read_content = event.Event()
        blew_up = [False]

        def chunk_reader(env, start_response):
            try:
                content = env['wsgi.input'].read(1024)
            except IOError:
                blew_up[0] = True
                content = b'ok'
            read_content.send(content)
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [content]

        self.site.application = chunk_reader
        expected_body = 'a bunch of stuff'
        data = "\r\n".join(['PUT /somefile HTTP/1.0',
                            'Transfer-Encoding: chunked',
                            '',
                            'def',
                            expected_body])
        # start PUT-ing some chunked data but close prematurely
        sock = eventlet.connect(self.server_addr)
        sock.sendall(data.encode())
        sock.close()
        # the test passes if we successfully get here, and read all the data
        # in spite of the early close
        self.assertEqual(read_content.wait(), b'ok')
        assert blew_up[0]

    def test_aborted_chunked_post_between_chunks(self):
        read_content = event.Event()
        blew_up = [False]

        def chunk_reader(env, start_response):
            try:
                content = env['wsgi.input'].read(1024)
            except wsgi.ChunkReadError:
                blew_up[0] = True
                content = b'ok'
            except Exception as err:
                blew_up[0] = True
                content = b'wrong exception: ' + str(err).encode()
            read_content.send(content)
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [content]
        self.site.application = chunk_reader
        expected_body = 'A' * 0xdb
        data = "\r\n".join(['PUT /somefile HTTP/1.0',
                            'Transfer-Encoding: chunked',
                            '',
                            'db',
                            expected_body])
        # start PUT-ing some chunked data but close prematurely
        sock = eventlet.connect(self.server_addr)
        sock.sendall(data.encode())
        sock.close()
        # the test passes if we successfully get here, and read all the data
        # in spite of the early close
        self.assertEqual(read_content.wait(), b'ok')
        assert blew_up[0]

    def test_aborted_chunked_post_bad_chunks(self):
        read_content = event.Event()
        blew_up = [False]

        def chunk_reader(env, start_response):
            try:
                content = env['wsgi.input'].read(1024)
            except wsgi.ChunkReadError:
                blew_up[0] = True
                content = b'ok'
            except Exception as err:
                blew_up[0] = True
                content = b'wrong exception: ' + str(err).encode()
            read_content.send(content)
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [content]
        self.site.application = chunk_reader
        expected_body = 'look here is some data for you'
        data = "\r\n".join(['PUT /somefile HTTP/1.0',
                            'Transfer-Encoding: chunked',
                            '',
                            'cats',
                            expected_body])
        # start PUT-ing some garbage
        sock = eventlet.connect(self.server_addr)
        sock.sendall(data.encode())
        sock.close()
        # the test passes if we successfully get here, and read all the data
        # in spite of the early close
        self.assertEqual(read_content.wait(), b'ok')
        assert blew_up[0]

    def test_aborted_post_io_error(self):
        ran_post_req_hook = [False]

        def post_req_hook(env):
            ran_post_req_hook[0] = True

        def early_responder(env, start_response):
            env['eventlet.posthooks'] = [(post_req_hook, (), {})]
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return ['ok']

        self.site.application = early_responder
        data = "\r\n".join(['PUT /somefile HTTP/1.1',
                            'Transfer-Encoding: chunked',
                            '',
                            '20',
                            'not 32 bytes'])
        sock = eventlet.connect(self.server_addr)
        sock.sendall(data.encode())
        sock.close()
        # Give the server a chance to wrap things up
        eventlet.sleep(0.01)
        # Unexpected EOF shouldn't kill the server;
        # post-request processing should still happen
        assert ran_post_req_hook[0]

    def test_exceptions_close_connection(self):
        def wsgi_app(environ, start_response):
            raise RuntimeError("intentional error")
        self.site.application = wsgi_app
        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        result = read_http(sock)
        self.assertEqual(result.status, 'HTTP/1.1 500 Internal Server Error')
        self.assertEqual(result.headers_lower['connection'], 'close')
        assert 'transfer-encoding' not in result.headers_lower

    def test_unicode_with_only_ascii_characters_works(self):
        def wsgi_app(environ, start_response):
            start_response("200 OK", [])
            yield b"oh hai, "
            yield u"xxx"
        self.site.application = wsgi_app
        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        result = read_http(sock)
        assert b'xxx' in result.body

    def test_unicode_with_nonascii_characters_raises_error(self):
        def wsgi_app(environ, start_response):
            start_response("200 OK", [])
            yield b"oh hai, "
            yield u"xxx \u0230"
        self.site.application = wsgi_app
        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        result = read_http(sock)
        self.assertEqual(result.status, 'HTTP/1.1 500 Internal Server Error')
        self.assertEqual(result.headers_lower['connection'], 'close')

    def test_path_info_decoding(self):
        def wsgi_app(environ, start_response):
            start_response("200 OK", [])
            yield six.b("decoded: %s" % environ['PATH_INFO'])
            yield six.b("raw: %s" % environ['RAW_PATH_INFO'])
        self.site.application = wsgi_app
        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET /a*b@%40%233 HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        result = read_http(sock)
        assert result.status == 'HTTP/1.1 200 OK'
        assert b'decoded: /a*b@@#3' in result.body
        assert b'raw: /a*b@%40%233' in result.body

    def test_path_info_latin1(self):
        # https://github.com/eventlet/eventlet/issues/468
        g = []

        def wsgi_app(environ, start_response):
            g.append(environ['PATH_INFO'])
            start_response("200 OK", [])
            return b''

        self.site.application = wsgi_app
        sock = eventlet.connect(self.server_addr)
        # This is a properly-quoted request for the UTF-8 path /你好
        sock.sendall(b'GET /%E4%BD%A0%E5%A5%BD HTTP/1.1\r\nHost: localhost\r\n\r\n')
        result = read_http(sock)
        assert result.status == 'HTTP/1.1 200 OK'
        # Like above, but the octets are reversed before being quoted,
        # so the result should *not* be interpreted as UTF-8
        sock.sendall(b'GET /%BD%A5%E5%A0%BD%E4 HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        result = read_http(sock)
        assert result.status == 'HTTP/1.1 200 OK'

        # that was only preparation, actual tests below
        # Per PEP-0333 https://www.python.org/dev/peps/pep-0333/#unicode-issues
        # in all WSGI environment strings application must observe either bytes in latin-1 (ISO-8859-1)
        # or unicode code points \u0000..\u00ff
        msg = 'Expected PATH_INFO to be a native string, not {0}'.format(type(g[0]))
        assert isinstance(g[0], str), msg
        # Fortunately, WSGI strings have the same literal representation on both py2 and py3
        assert g[0] == '/\xe4\xbd\xa0\xe5\xa5\xbd'

        msg = 'Expected PATH_INFO to be a native string, not {0}'.format(type(g[1]))
        assert isinstance(g[1], str), msg
        assert g[1] == '/\xbd\xa5\xe5\xa0\xbd\xe4'

    @tests.skip_if_no_ipv6
    def test_ipv6(self):
        try:
            sock = eventlet.listen(('::1', 0), family=socket.AF_INET6)
        except (socket.gaierror, socket.error):  # probably no ipv6
            return
        log = six.StringIO()
        # first thing the server does is try to log the IP it's bound to

        def run_server():
            try:
                wsgi.server(sock=sock, log=log, site=Site())
            except ValueError:
                log.write(b'broken')

        self.spawn_thread(run_server)

        logval = log.getvalue()
        while not logval:
            eventlet.sleep(0.0)
            logval = log.getvalue()
        if 'broked' in logval:
            self.fail('WSGI server raised exception with ipv6 socket')

    def test_debug(self):
        self.spawn_server(debug=False)

        def crasher(env, start_response):
            raise RuntimeError("intentional crash")
        self.site.application = crasher

        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        result1 = read_http(sock)
        self.assertEqual(result1.status, 'HTTP/1.1 500 Internal Server Error')
        self.assertEqual(result1.body, b'')
        self.assertEqual(result1.headers_lower['connection'], 'close')
        assert 'transfer-encoding' not in result1.headers_lower

        # verify traceback when debugging enabled
        self.spawn_server(debug=True)
        self.site.application = crasher
        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        result2 = read_http(sock)
        self.assertEqual(result2.status, 'HTTP/1.1 500 Internal Server Error')
        assert b'intentional crash' in result2.body, result2.body
        assert b'RuntimeError' in result2.body, result2.body
        assert b'Traceback' in result2.body, result2.body
        self.assertEqual(result2.headers_lower['connection'], 'close')
        assert 'transfer-encoding' not in result2.headers_lower

    def test_client_disconnect(self):
        """Issue #95 Server must handle disconnect from client in the middle of response
        """
        def long_response(environ, start_response):
            start_response('200 OK', [('Content-Length', '9876')])
            yield b'a' * 9876

        server_sock = eventlet.listen(('localhost', 0))
        self.server_addr = server_sock.getsockname()
        server = wsgi.Server(server_sock, server_sock.getsockname(), long_response,
                             log=self.logfile)

        def make_request():
            sock = eventlet.connect(server_sock.getsockname())
            sock.send(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
            sock.close()

        request_thread = eventlet.spawn(make_request)
        client_sock, addr = server_sock.accept()
        # Next line must not raise IOError -32 Broken pipe
        server.process_request([addr, client_sock, wsgi.STATE_IDLE])
        request_thread.wait()
        server_sock.close()

    def test_server_connection_timeout_exception(self):
        self.reset_timeout(5)
        # Handle connection socket timeouts
        # https://bitbucket.org/eventlet/eventlet/issue/143/
        # Runs tests.wsgi_test_conntimeout in a separate process.
        tests.run_isolated('wsgi_connection_timeout.py')

    def test_server_socket_timeout(self):
        self.spawn_server(socket_timeout=0.1)
        sock = eventlet.connect(self.server_addr)
        sock.send(b'GET / HTTP/1.1\r\n')
        eventlet.sleep(0.1)
        try:
            read_http(sock)
            assert False, 'Expected ConnectionClosed exception'
        except ConnectionClosed:
            pass

    def test_header_name_capitalization(self):
        def wsgi_app(environ, start_response):
            start_response('200 oK', [
                ('sOMe-WEirD', 'cAsE'),
                ('wiTH-\xdf-LATIN1-\xff', 'chars'),
            ])
            return [b'']

        self.spawn_server(site=wsgi_app)

        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        result = read_http(sock)
        sock.close()
        self.assertEqual(result.status, 'HTTP/1.1 200 oK')
        self.assertIn('Some-Weird', result.headers_original)
        self.assertEqual(result.headers_original['Some-Weird'], 'cAsE')
        self.assertIn('With-\xdf-Latin1-\xff', result.headers_original)
        self.assertEqual(result.headers_original['With-\xdf-Latin1-\xff'], 'chars')

    def test_disable_header_name_capitalization(self):
        # Disable HTTP header name capitalization
        #
        # https://github.com/eventlet/eventlet/issues/80
        random_case_header = ('eTAg', 'TAg-VAluE')

        def wsgi_app(environ, start_response):
            start_response('200 oK', [random_case_header])
            return [b'']

        self.spawn_server(site=wsgi_app, capitalize_response_headers=False)

        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        result = read_http(sock)
        sock.close()
        self.assertEqual(result.status, 'HTTP/1.1 200 oK')
        self.assertEqual(result.headers_lower[random_case_header[0].lower()], random_case_header[1])
        self.assertEqual(result.headers_original[random_case_header[0]], random_case_header[1])

    def test_log_unix_address(self):
        def app(environ, start_response):
            start_response('200 OK', [])
            return ['\n{0}={1}\n'.format(k, v).encode() for k, v in environ.items()]

        tempdir = tempfile.mkdtemp('eventlet_test_log_unix_address')
        try:
            server_sock = eventlet.listen(tempdir + '/socket', socket.AF_UNIX)
            path = server_sock.getsockname()

            log = six.StringIO()
            self.spawn_server(site=app, sock=server_sock, log=log)
            eventlet.sleep(0)  # need to enter server loop
            assert 'http:' + path in log.getvalue()

            client_sock = eventlet.connect(path, family=socket.AF_UNIX)
            client_sock.sendall(b'GET / HTTP/1.0\r\nHost: localhost\r\n\r\n')
            result = read_http(client_sock)
            client_sock.close()
            assert '\nunix -' in log.getvalue()
        finally:
            shutil.rmtree(tempdir)

        assert result.status == 'HTTP/1.1 200 OK', repr(result) + log.getvalue()
        assert b'\nSERVER_NAME=unix\n' in result.body
        assert b'\nSERVER_PORT=\n' in result.body
        assert b'\nREMOTE_ADDR=unix\n' in result.body
        assert b'\nREMOTE_PORT=\n' in result.body

    def test_headers_raw(self):
        def app(environ, start_response):
            start_response('200 OK', [])
            return [b'\n'.join('{0}: {1}'.format(*kv).encode() for kv in environ['headers_raw'])]

        self.spawn_server(site=app)
        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\nx-ANY_k: one\r\nx-ANY_k: two\r\n\r\n')
        result = read_http(sock)
        sock.close()
        assert result.status == 'HTTP/1.1 200 OK'
        assert result.body == b'Host: localhost\nx-ANY_k: one\nx-ANY_k: two'

    def test_env_headers(self):
        def app(environ, start_response):
            start_response('200 OK', [])
            return ['{0}: {1}\n'.format(*kv).encode() for kv in sorted(environ.items())
                    if kv[0].startswith('HTTP_')]

        self.spawn_server(site=app)
        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\npath-info: foo\r\n'
                     b'x-ANY_k: one\r\nhttp-x-ANY_k: two\r\n\r\n')
        result = read_http(sock)
        sock.close()
        assert result.status == 'HTTP/1.1 200 OK', 'Received status {0!r}'.format(result.status)
        assert result.body == (b'HTTP_HOST: localhost\nHTTP_HTTP_X_ANY_K: two\n'
                               b'HTTP_PATH_INFO: foo\nHTTP_X_ANY_K: one\n')

    def test_env_header_stripping(self):
        def app(environ, start_response):
            start_response('200 OK', [])
            # On py3, headers get parsed as Latin-1, so send them back out as Latin-1, too
            return [line if isinstance(line, bytes) else line.encode('latin1')
                    for kv in sorted(environ.items())
                    if kv[0].startswith('HTTP_')
                    for line in ('{0}: {1}\n'.format(*kv),)]

        self.spawn_server(site=app)
        sock = eventlet.connect(self.server_addr)
        sock.sendall(
            b'GET / HTTP/1.1\r\n'
            b'Host: localhost\r\n'
            b'spaced:   o   u   t   \r\n'
            b'trailing: tab\t\r\n'
            b'trailing-nbsp: \xc2\xa0\r\n'
            b'null-set: \xe2\x88\x85\r\n\r\n')
        result = read_http(sock)
        sock.close()
        assert result.status == 'HTTP/1.1 200 OK', 'Received status {0!r}'.format(result.status)
        assert result.body == (
            b'HTTP_HOST: localhost\n'
            b'HTTP_NULL_SET: \xe2\x88\x85\n'
            b'HTTP_SPACED: o   u   t\n'
            b'HTTP_TRAILING: tab\n'
            b'HTTP_TRAILING_NBSP: \xc2\xa0\n')

    def test_log_disable(self):
        self.spawn_server(log_output=False)
        sock = eventlet.connect(self.server_addr)
        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\npath-info: foo\r\n'
                     b'x-ANY_k: one\r\nhttp-x-ANY_k: two\r\n\r\n')
        read_http(sock)
        sock.close()
        log_content = self.logfile.getvalue()
        assert log_content == ''

    def test_close_idle_connections(self):
        self.reset_timeout(2)
        pool = eventlet.GreenPool()
        self.spawn_server(custom_pool=pool)
        # https://github.com/eventlet/eventlet/issues/188
        sock = eventlet.connect(self.server_addr)

        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        result = read_http(sock)
        assert result.status == 'HTTP/1.1 200 OK', 'Received status {0!r}'.format(result.status)
        self.killer.kill(KeyboardInterrupt)
        try:
            with eventlet.Timeout(1):
                pool.waitall()
        except Exception:
            assert False, self.logfile.getvalue()


def read_headers(sock):
    fd = sock.makefile('rb')
    try:
        response_line = fd.readline()
    except socket.error as exc:
        if support.get_errno(exc) == 10053:
            raise ConnectionClosed
        raise
    if not response_line:
        raise ConnectionClosed

    header_lines = []
    while True:
        line = fd.readline()
        if line == b'\r\n':
            break
        else:
            header_lines.append(line)
    headers = dict()
    for x in header_lines:
        x = x.strip()
        if not x:
            continue
        key, value = x.split(b': ', 1)
        assert key.lower() not in headers, "%s header duplicated" % key
        headers[bytes_to_str(key.lower())] = bytes_to_str(value)
    return bytes_to_str(response_line), headers


class IterableAlreadyHandledTest(_TestBase):
    def set_site(self):
        self.site = IterableSite()

    def get_app(self):
        return IterableApp(True)

    def test_iterable_app_keeps_socket_open_unless_connection_close_sent(self):
        self.site.application = self.get_app()
        sock = eventlet.connect(self.server_addr)

        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        response_line, headers = read_headers(sock)
        self.assertEqual(response_line, 'HTTP/1.1 200 OK\r\n')
        assert 'connection' not in headers

        sock.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        result = read_http(sock)
        self.assertEqual(result.status, 'HTTP/1.1 200 OK')
        self.assertEqual(result.headers_lower.get('transfer-encoding'), 'chunked')
        self.assertEqual(result.body, b'0\r\n\r\n')  # Still coming back chunked


class ProxiedIterableAlreadyHandledTest(IterableAlreadyHandledTest):
    # same thing as the previous test but ensuring that it works with tpooled
    # results as well as regular ones
    @tests.skip_with_pyevent
    def get_app(self):
        return tpool.Proxy(super(ProxiedIterableAlreadyHandledTest, self).get_app())

    def tearDown(self):
        tpool.killall()
        super(ProxiedIterableAlreadyHandledTest, self).tearDown()


class TestChunkedInput(_TestBase):
    validator = None

    def application(self, env, start_response):
        input = env['wsgi.input']
        response = []

        pi = env["PATH_INFO"]

        if pi == "/short-read":
            d = input.read(10)
            response = [d]
        elif pi == "/lines":
            for x in input:
                response.append(x)
        elif pi == "/readline":
            response.extend(iter(input.readline, b''))
            response.append(('\nread %d lines' % len(response)).encode())
        elif pi == "/readlines":
            response.extend(input.readlines())
            response.append(('\nread %d lines' % len(response)).encode())
        elif pi == "/ping":
            input.read()
            response.append(b"pong")
        elif pi.startswith("/yield_spaces"):
            if pi.endswith('override_min'):
                env['eventlet.minimum_write_chunk_size'] = 1
            self.yield_next_space = False

            def response_iter():
                yield b' '
                num_sleeps = 0
                while not self.yield_next_space and num_sleeps < 200:
                    eventlet.sleep(.01)
                    num_sleeps += 1

                yield b' '

            start_response('200 OK',
                           [('Content-Type', 'text/plain'),
                            ('Content-Length', '2')])
            return response_iter()
        else:
            raise RuntimeError("bad path")

        start_response('200 OK', [('Content-Type', 'text/plain')])
        return response

    def connect(self):
        return eventlet.connect(self.server_addr)

    def set_site(self):
        self.site = Site()
        self.site.application = self.application

    def chunk_encode(self, chunks, dirt=""):
        b = ""
        for c in chunks:
            b += "%x%s\r\n%s\r\n" % (len(c), dirt, c)
        return b

    def body(self, dirt=""):
        return self.chunk_encode(["this", " is ", "chunked", "\nline",
                                  " 2", "\n", "line3", ""], dirt=dirt)

    def ping(self, fd):
        fd.sendall(b"GET /ping HTTP/1.1\r\n\r\n")
        self.assertEqual(read_http(fd).body, b"pong")

    def test_short_read_with_content_length(self):
        body = self.body()
        req = "POST /short-read HTTP/1.1\r\ntransfer-encoding: Chunked\r\n" \
              "Content-Length:1000\r\n\r\n" + body

        fd = self.connect()
        fd.sendall(req.encode())
        self.assertEqual(read_http(fd).body, b"this is ch")

        self.ping(fd)
        fd.close()

    def test_short_read_with_zero_content_length(self):
        body = self.body()
        req = "POST /short-read HTTP/1.1\r\ntransfer-encoding: Chunked\r\n" \
              "Content-Length:0\r\n\r\n" + body
        fd = self.connect()
        fd.sendall(req.encode())
        self.assertEqual(read_http(fd).body, b"this is ch")

        self.ping(fd)
        fd.close()

    def test_short_read(self):
        body = self.body()
        req = "POST /short-read HTTP/1.1\r\ntransfer-encoding: Chunked\r\n\r\n" + body

        fd = self.connect()
        fd.sendall(req.encode())
        self.assertEqual(read_http(fd).body, b"this is ch")

        self.ping(fd)
        fd.close()

    def test_dirt(self):
        body = self.body(dirt="; here is dirt\0bla")
        req = "POST /ping HTTP/1.1\r\ntransfer-encoding: Chunked\r\n\r\n" + body

        fd = self.connect()
        fd.sendall(req.encode())
        self.assertEqual(read_http(fd).body, b"pong")

        self.ping(fd)
        fd.close()

    def test_chunked_readline(self):
        body = self.body()
        req = "POST /lines HTTP/1.1\r\nContent-Length: %s\r\n" \
              "transfer-encoding: Chunked\r\n\r\n%s" % (len(body), body)

        fd = self.connect()
        fd.sendall(req.encode())
        self.assertEqual(read_http(fd).body, b'this is chunked\nline 2\nline3')
        fd.close()

    def test_chunked_readline_from_input(self):
        body = self.body()
        req = "POST /readline HTTP/1.1\r\nContent-Length: %s\r\n" \
              "transfer-encoding: Chunked\r\n\r\n%s" % (len(body), body)

        fd = self.connect()
        fd.sendall(req.encode())
        self.assertEqual(read_http(fd).body, b'this is chunked\nline 2\nline3\nread 3 lines')
        fd.close()

    def test_chunked_readlines_from_input(self):
        body = self.body()
        req = "POST /readlines HTTP/1.1\r\nContent-Length: %s\r\n" \
              "transfer-encoding: Chunked\r\n\r\n%s" % (len(body), body)

        fd = self.connect()
        fd.sendall(req.encode())
        self.assertEqual(read_http(fd).body, b'this is chunked\nline 2\nline3\nread 3 lines')
        fd.close()

    def test_chunked_readline_wsgi_override_minimum_chunk_size(self):

        fd = self.connect()
        fd.sendall(b"POST /yield_spaces/override_min HTTP/1.1\r\nContent-Length: 0\r\n\r\n")

        resp_so_far = b''
        with eventlet.Timeout(.1):
            while True:
                one_byte = fd.recv(1)
                resp_so_far += one_byte
                if resp_so_far.endswith(b'\r\n\r\n'):
                    break
            self.assertEqual(fd.recv(1), b' ')
        try:
            with eventlet.Timeout(.1):
                fd.recv(1)
        except eventlet.Timeout:
            pass
        else:
            assert False
        self.yield_next_space = True

        with eventlet.Timeout(.1):
            self.assertEqual(fd.recv(1), b' ')

    def test_chunked_readline_wsgi_not_override_minimum_chunk_size(self):

        fd = self.connect()
        fd.sendall(b"POST /yield_spaces HTTP/1.1\r\nContent-Length: 0\r\n\r\n")

        resp_so_far = b''
        try:
            with eventlet.Timeout(.1):
                while True:
                    one_byte = fd.recv(1)
                    resp_so_far += one_byte
                    if resp_so_far.endswith(b'\r\n\r\n'):
                        break
                self.assertEqual(fd.recv(1), b' ')
        except eventlet.Timeout:
            pass
        else:
            assert False

    def test_close_before_finished(self):
        got_signal = []

        def handler(*args):
            got_signal.append(1)
            raise KeyboardInterrupt()

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(1)

        try:
            body = '4\r\nthi'
            req = "POST /short-read HTTP/1.1\r\ntransfer-encoding: Chunked\r\n\r\n" + body

            fd = self.connect()
            fd.sendall(req.encode())
            fd.close()

            eventlet.sleep(0)

            # This is needed because on Python 3 GreenSocket.recv_into is called
            # rather than recv; recv_into right now (git 5ec3a3c) trampolines to
            # the hub *before* attempting to read anything from a file descriptor
            # therefore we need one extra context switch to let it notice closed
            # socket, die and leave the hub empty
            if six.PY3:
                eventlet.sleep(0)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, signal.SIG_DFL)

        assert not got_signal, "caught alarm signal. infinite loop detected."
