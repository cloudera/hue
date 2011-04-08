import cgi
from eventlet import greenthread
import eventlet
import errno
import os
import socket
import sys
from tests import skipped, LimitedTestCase, skip_with_pyevent
from unittest import main

from eventlet import greenio
from eventlet import event
from eventlet.green import socket as greensocket
from eventlet import wsgi
from eventlet.support import get_errno

from tests import find_command

httplib = eventlet.import_patched('httplib')

certificate_file = os.path.join(os.path.dirname(__file__), 'test_server.crt')
private_key_file = os.path.join(os.path.dirname(__file__), 'test_server.key')

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


def hello_world(env, start_response):
    if env['PATH_INFO'] == 'notexist':
        start_response('404 Not Found', [('Content-type', 'text/plain')])
        return ["not found"]

    start_response('200 OK', [('Content-type', 'text/plain')])
    return ["hello world"]


def chunked_app(env, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    yield "this"
    yield "is"
    yield "chunked"


def big_chunks(env, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    line = 'a' * 8192
    for x in range(10):
        yield line

def use_write(env, start_response):
    if env['PATH_INFO'] == '/a':
        write = start_response('200 OK', [('Content-type', 'text/plain'),
                                          ('Content-Length', '5')])
        write('abcde')
    if env['PATH_INFO'] == '/b':
        write = start_response('200 OK', [('Content-type', 'text/plain')])
        write('abcde')
    return []

def chunked_post(env, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    if env['PATH_INFO'] == '/a':
        return [env['wsgi.input'].read()]
    elif env['PATH_INFO'] == '/b':
        return [x for x in iter(lambda: env['wsgi.input'].read(4096), '')]
    elif env['PATH_INFO'] == '/c':
        return [x for x in iter(lambda: env['wsgi.input'].read(1), '')]

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


"""
HTTP/1.1 200 OK
Date: foo
Content-length: 11

hello world
"""

class ConnectionClosed(Exception):
    pass


def read_http(sock):
    fd = sock.makefile()
    try:
        response_line = fd.readline()
    except socket.error, exc:
        if get_errno(exc) == 10053:
            raise ConnectionClosed
        raise
    if not response_line:
        raise ConnectionClosed
    
    header_lines = []
    while True:
        line = fd.readline()
        if line == '\r\n':
            break
        else:
            header_lines.append(line)
    headers = dict()
    for x in header_lines:
        x = x.strip()
        if not x:
            continue
        key, value = x.split(': ', 1)
        assert key.lower() not in headers, "%s header duplicated" % key
        headers[key.lower()] = value

    if CONTENT_LENGTH in headers:
        num = int(headers[CONTENT_LENGTH])
        body = fd.read(num)
    else:
        # read until EOF
        body = fd.read()

    return response_line, headers, body

class _TestBase(LimitedTestCase):
    def setUp(self):
        super(_TestBase, self).setUp()
        self.logfile = StringIO()
        self.site = Site()
        self.killer = None
        self.set_site()
        self.spawn_server()

    def tearDown(self):
        greenthread.kill(self.killer)
        eventlet.sleep(0)
        super(_TestBase, self).tearDown()

    def spawn_server(self, **kwargs):
        """Spawns a new wsgi server with the given arguments.
        Sets self.port to the port of the server, and self.killer is the greenlet
        running it.

        Kills any previously-running server."""
        eventlet.sleep(0) # give previous server a chance to start
        if self.killer:
            greenthread.kill(self.killer)
            eventlet.sleep(0) # give killer a chance to kill

        new_kwargs = dict(max_size=128,
                          log=self.logfile,
                          site=self.site)
        new_kwargs.update(kwargs)

        if 'sock' not in new_kwargs:
            new_kwargs['sock'] = eventlet.listen(('localhost', 0))

        self.port = new_kwargs['sock'].getsockname()[1]
        self.killer = eventlet.spawn_n(
            wsgi.server,
            **new_kwargs)

    def set_site(self):
        raise NotImplementedError

class TestHttpd(_TestBase):
    def set_site(self):
        self.site = Site()

    def test_001_server(self):
        sock = eventlet.connect(
            ('localhost', self.port))

        fd = sock.makefile('rw')
        fd.write('GET / HTTP/1.0\r\nHost: localhost\r\n\r\n')
        fd.flush()
        result = fd.read()
        fd.close()
        ## The server responds with the maximum version it supports
        self.assert_(result.startswith('HTTP'), result)
        self.assert_(result.endswith('hello world'))

    def test_002_keepalive(self):
        sock = eventlet.connect(
            ('localhost', self.port))

        fd = sock.makefile('w')
        fd.write('GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        fd.flush()
        read_http(sock)
        fd.write('GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        fd.flush()
        read_http(sock)
        fd.close()

    def test_003_passing_non_int_to_read(self):
        # This should go in greenio_test
        sock = eventlet.connect(
            ('localhost', self.port))

        fd = sock.makefile('rw')
        fd.write('GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        fd.flush()
        cancel = eventlet.Timeout(1, RuntimeError)
        self.assertRaises(TypeError, fd.read, "This shouldn't work")
        cancel.cancel()
        fd.close()

    def test_004_close_keepalive(self):
        sock = eventlet.connect(
            ('localhost', self.port))

        fd = sock.makefile('w')
        fd.write('GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        fd.flush()
        read_http(sock)
        fd.write('GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        fd.flush()
        read_http(sock)
        fd.write('GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        fd.flush()
        self.assertRaises(ConnectionClosed, read_http, sock)
        fd.close()

    @skipped
    def test_005_run_apachebench(self):
        url = 'http://localhost:12346/'
        # ab is apachebench
        from eventlet.green import subprocess
        subprocess.call([find_command('ab'),
                         '-c','64','-n','1024', '-k', url],
                        stdout=subprocess.PIPE)

    def test_006_reject_long_urls(self):
        sock = eventlet.connect(
            ('localhost', self.port))
        path_parts = []
        for ii in range(3000):
            path_parts.append('path')
        path = '/'.join(path_parts)
        request = 'GET /%s HTTP/1.0\r\nHost: localhost\r\n\r\n' % path
        fd = sock.makefile('rw')
        fd.write(request)
        fd.flush()
        result = fd.readline()
        if result:
            # windows closes the socket before the data is flushed,
            # so we never get anything back
            status = result.split(' ')[1]
            self.assertEqual(status, '414')
        fd.close()

    def test_007_get_arg(self):
        # define a new handler that does a get_arg as well as a read_body
        def new_app(env, start_response):
            body = env['wsgi.input'].read()
            a = cgi.parse_qs(body).get('a', [1])[0]
            start_response('200 OK', [('Content-type', 'text/plain')])
            return ['a is %s, body is %s' % (a, body)]

        self.site.application = new_app
        sock = eventlet.connect(
            ('localhost', self.port))
        request = '\r\n'.join((
            'POST / HTTP/1.0',
            'Host: localhost',
            'Content-Length: 3',
            '',
            'a=a'))
        fd = sock.makefile('w')
        fd.write(request)
        fd.flush()

        # send some junk after the actual request
        fd.write('01234567890123456789')
        reqline, headers, body = read_http(sock)
        self.assertEqual(body, 'a is a, body is a=a')
        fd.close()

    def test_008_correctresponse(self):
        sock = eventlet.connect(
            ('localhost', self.port))

        fd = sock.makefile('w')
        fd.write('GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        fd.flush()
        response_line_200,_,_ = read_http(sock)
        fd.write('GET /notexist HTTP/1.1\r\nHost: localhost\r\n\r\n')
        fd.flush()
        response_line_404,_,_ = read_http(sock)
        fd.write('GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        fd.flush()
        response_line_test,_,_ = read_http(sock)
        self.assertEqual(response_line_200,response_line_test)
        fd.close()

    def test_009_chunked_response(self):
        self.site.application = chunked_app
        sock = eventlet.connect(
            ('localhost', self.port))

        fd = sock.makefile('rw')
        fd.write('GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        fd.flush()
        self.assert_('Transfer-Encoding: chunked' in fd.read())

    def test_010_no_chunked_http_1_0(self):
        self.site.application = chunked_app
        sock = eventlet.connect(
            ('localhost', self.port))

        fd = sock.makefile('rw')
        fd.write('GET / HTTP/1.0\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        fd.flush()
        self.assert_('Transfer-Encoding: chunked' not in fd.read())

    def test_011_multiple_chunks(self):
        self.site.application = big_chunks
        sock = eventlet.connect(
            ('localhost', self.port))

        fd = sock.makefile('rw')
        fd.write('GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        fd.flush()
        headers = ''
        while True:
            line = fd.readline()
            if line == '\r\n':
                break
            else:
                headers += line
        self.assert_('Transfer-Encoding: chunked' in headers)
        chunks = 0
        chunklen = int(fd.readline(), 16)
        while chunklen:
            chunks += 1
            chunk = fd.read(chunklen)
            fd.readline()  # CRLF
            chunklen = int(fd.readline(), 16)
        self.assert_(chunks > 1)
        response = fd.read()
        # Require a CRLF to close the message body
        self.assertEqual(response, '\r\n')

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
    
        sock = eventlet.connect(('localhost', self.port))
        sock = eventlet.wrap_ssl(sock)
        sock.write('POST /foo HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\nContent-length:3\r\n\r\nabc')
        result = sock.read(8192)
        self.assertEquals(result[-3:], 'abc')
        
    def test_013_empty_return(self):
        def wsgi_app(environ, start_response):
            start_response("200 OK", [])
            return [""]

        certificate_file = os.path.join(os.path.dirname(__file__), 'test_server.crt')
        private_key_file = os.path.join(os.path.dirname(__file__), 'test_server.key')
        server_sock = eventlet.wrap_ssl(eventlet.listen(('localhost', 0)), 
                                        certfile=certificate_file, 
                                        keyfile=private_key_file,
                                        server_side=True)
        self.spawn_server(sock=server_sock, site=wsgi_app)

        sock = eventlet.connect(('localhost', server_sock.getsockname()[1]))
        sock = eventlet.wrap_ssl(sock)
        sock.write('GET /foo HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        result = sock.read(8192)
        self.assertEquals(result[-4:], '\r\n\r\n')

    def test_014_chunked_post(self):
        self.site.application = chunked_post
        sock = eventlet.connect(('localhost', self.port))
        fd = sock.makefile('rw')
        fd.write('PUT /a HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n'
                 'Transfer-Encoding: chunked\r\n\r\n'
                 '2\r\noh\r\n4\r\n hai\r\n0\r\n\r\n')
        fd.flush()
        while True:
            if fd.readline() == '\r\n':
                break
        response = fd.read()
        self.assert_(response == 'oh hai', 'invalid response %s' % response)

        sock = eventlet.connect(('localhost', self.port))
        fd = sock.makefile('rw')
        fd.write('PUT /b HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n'
                 'Transfer-Encoding: chunked\r\n\r\n'
                 '2\r\noh\r\n4\r\n hai\r\n0\r\n\r\n')
        fd.flush()
        while True:
            if fd.readline() == '\r\n':
                break
        response = fd.read()
        self.assert_(response == 'oh hai', 'invalid response %s' % response)

        sock = eventlet.connect(('localhost', self.port))
        fd = sock.makefile('rw')
        fd.write('PUT /c HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n'
                 'Transfer-Encoding: chunked\r\n\r\n'
                 '2\r\noh\r\n4\r\n hai\r\n0\r\n\r\n')
        fd.flush()
        while True:
            if fd.readline() == '\r\n':
                break
        response = fd.read(8192)
        self.assert_(response == 'oh hai', 'invalid response %s' % response)

    def test_015_write(self):
        self.site.application = use_write
        sock = eventlet.connect(('localhost', self.port))
        fd = sock.makefile('w')
        fd.write('GET /a HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        fd.flush()
        response_line, headers, body = read_http(sock)
        self.assert_('content-length' in headers)

        sock = eventlet.connect(('localhost', self.port))
        fd = sock.makefile('w')
        fd.write('GET /b HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        fd.flush()
        response_line, headers, body = read_http(sock)
        self.assert_('transfer-encoding' in headers)
        self.assert_(headers['transfer-encoding'] == 'chunked')

    def test_016_repeated_content_length(self):
        """
        content-length header was being doubled up if it was set in
        start_response and could also be inferred from the iterator
        """
        def wsgi_app(environ, start_response):
            start_response('200 OK', [('Content-Length', '7')])
            return ['testing']
        self.site.application = wsgi_app
        sock = eventlet.connect(('localhost', self.port))
        fd = sock.makefile('rw')
        fd.write('GET /a HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        fd.flush()
        header_lines = []
        while True:
            line = fd.readline()
            if line == '\r\n':
                break
            else:
                header_lines.append(line)
        self.assertEquals(1, len([l for l in header_lines
                if l.lower().startswith('content-length')]))

    def test_017_ssl_zeroreturnerror(self):

        def server(sock, site, log):
            try:
                serv = wsgi.Server(sock, sock.getsockname(), site, log)
                client_socket = sock.accept()
                serv.process_request(client_socket)
                return True
            except:
                import traceback
                traceback.print_exc()
                return False

        def wsgi_app(environ, start_response):
            start_response('200 OK', [])
            return [environ['wsgi.input'].read()]

        certificate_file = os.path.join(os.path.dirname(__file__), 'test_server.crt')
        private_key_file = os.path.join(os.path.dirname(__file__), 'test_server.key')

        sock = eventlet.wrap_ssl(eventlet.listen(('localhost', 0)), 
                                        certfile=certificate_file, 
                                        keyfile=private_key_file,
                                        server_side=True)
        server_coro = eventlet.spawn(server, sock, wsgi_app, self.logfile)

        client = eventlet.connect(('localhost', sock.getsockname()[1]))
        client = eventlet.wrap_ssl(client)
        client.write('X') # non-empty payload so that SSL handshake occurs
        greenio.shutdown_safe(client)
        client.close()

        success = server_coro.wait()
        self.assert_(success)
        
    def test_018_http_10_keepalive(self):
        # verify that if an http/1.0 client sends connection: keep-alive
        # that we don't close the connection
        sock = eventlet.connect(
            ('localhost', self.port))

        fd = sock.makefile('w')
        fd.write('GET / HTTP/1.0\r\nHost: localhost\r\nConnection: keep-alive\r\n\r\n')
        fd.flush()
        
        response_line, headers, body = read_http(sock)
        self.assert_('connection' in headers)
        self.assertEqual('keep-alive', headers['connection'])
        # repeat request to verify connection is actually still open
        fd.write('GET / HTTP/1.0\r\nHost: localhost\r\nConnection: keep-alive\r\n\r\n')
        fd.flush()
        response_line, headers, body = read_http(sock)
        self.assert_('connection' in headers)
        self.assertEqual('keep-alive', headers['connection'])
                     
    def test_019_fieldstorage_compat(self):
        def use_fieldstorage(environ, start_response):
            import cgi
            fs = cgi.FieldStorage(fp=environ['wsgi.input'],
                                  environ=environ)
            start_response('200 OK', [('Content-type', 'text/plain')])
            return ['hello!']
                             
        self.site.application = use_fieldstorage
        sock = eventlet.connect(
            ('localhost', self.port))

        fd = sock.makefile('rw')
        fd.write('POST / HTTP/1.1\r\n'
                 'Host: localhost\r\n'
                 'Connection: close\r\n'
                 'Transfer-Encoding: chunked\r\n\r\n'
                 '2\r\noh\r\n'
                 '4\r\n hai\r\n0\r\n\r\n')
        fd.flush()
        self.assert_('hello!' in fd.read())

    def test_020_x_forwarded_for(self):
        sock = eventlet.connect(('localhost', self.port))
        sock.sendall('GET / HTTP/1.1\r\nHost: localhost\r\nX-Forwarded-For: 1.2.3.4, 5.6.7.8\r\n\r\n')
        sock.recv(1024)
        sock.close()
        self.assert_('1.2.3.4,5.6.7.8,127.0.0.1' in self.logfile.getvalue())
        
        # turning off the option should work too
        self.logfile = StringIO()
        self.spawn_server(log_x_forwarded_for=False)
            
        sock = eventlet.connect(('localhost', self.port))
        sock.sendall('GET / HTTP/1.1\r\nHost: localhost\r\nX-Forwarded-For: 1.2.3.4, 5.6.7.8\r\n\r\n')
        sock.recv(1024)
        sock.close()
        self.assert_('1.2.3.4' not in self.logfile.getvalue())
        self.assert_('5.6.7.8' not in self.logfile.getvalue())        
        self.assert_('127.0.0.1' in self.logfile.getvalue())

    def test_socket_remains_open(self):
        greenthread.kill(self.killer)
        server_sock = eventlet.listen(('localhost', 0))
        server_sock_2 = server_sock.dup()
        self.spawn_server(sock=server_sock_2)
        # do a single req/response to verify it's up
        sock = eventlet.connect(('localhost', self.port))
        fd = sock.makefile('rw')
        fd.write('GET / HTTP/1.0\r\nHost: localhost\r\n\r\n')
        fd.flush()
        result = fd.read(1024)
        fd.close()
        self.assert_(result.startswith('HTTP'), result)
        self.assert_(result.endswith('hello world'))

        # shut down the server and verify the server_socket fd is still open,
        # but the actual socketobject passed in to wsgi.server is closed
        greenthread.kill(self.killer)
        eventlet.sleep(0) # make the kill go through
        try:
            server_sock_2.accept()
            # shouldn't be able to use this one anymore
        except socket.error, exc:
            self.assertEqual(get_errno(exc), errno.EBADF)
        self.spawn_server(sock=server_sock)
        sock = eventlet.connect(('localhost', self.port))
        fd = sock.makefile('rw')
        fd.write('GET / HTTP/1.0\r\nHost: localhost\r\n\r\n')
        fd.flush()
        result = fd.read(1024)
        fd.close()
        self.assert_(result.startswith('HTTP'), result)
        self.assert_(result.endswith('hello world'))

    def test_021_environ_clobbering(self):
        def clobberin_time(environ, start_response):
            for environ_var in ['wsgi.version', 'wsgi.url_scheme',
                'wsgi.input', 'wsgi.errors', 'wsgi.multithread',
                'wsgi.multiprocess', 'wsgi.run_once', 'REQUEST_METHOD',
                'SCRIPT_NAME', 'PATH_INFO', 'QUERY_STRING', 'CONTENT_TYPE',
                'CONTENT_LENGTH', 'SERVER_NAME', 'SERVER_PORT', 
                'SERVER_PROTOCOL']:
                environ[environ_var] = None
            start_response('200 OK', [('Content-type', 'text/plain')])
            return []
        self.site.application = clobberin_time
        sock = eventlet.connect(('localhost', self.port))
        fd = sock.makefile('rw')
        fd.write('GET / HTTP/1.1\r\n'
                 'Host: localhost\r\n'
                 'Connection: close\r\n'
                 '\r\n\r\n')
        fd.flush()
        self.assert_('200 OK' in fd.read())

    def test_022_custom_pool(self):
        # just test that it accepts the parameter for now
        # TODO: test that it uses the pool and that you can waitall() to
        # ensure that all clients finished
        from eventlet import greenpool
        p = greenpool.GreenPool(5)
        self.spawn_server(custom_pool=p)
            
        # this stuff is copied from test_001_server, could be better factored
        sock = eventlet.connect(
            ('localhost', self.port))
        fd = sock.makefile('rw')
        fd.write('GET / HTTP/1.0\r\nHost: localhost\r\n\r\n')
        fd.flush()
        result = fd.read()
        fd.close()
        self.assert_(result.startswith('HTTP'), result)
        self.assert_(result.endswith('hello world'))

    def test_023_bad_content_length(self):
        sock = eventlet.connect(
            ('localhost', self.port))
        fd = sock.makefile('rw')
        fd.write('GET / HTTP/1.0\r\nHost: localhost\r\nContent-length: argh\r\n\r\n')
        fd.flush()
        result = fd.read()
        fd.close()
        self.assert_(result.startswith('HTTP'), result)
        self.assert_('400 Bad Request' in result)
        self.assert_('500' not in result)

    def test_024_expect_100_continue(self):
        def wsgi_app(environ, start_response):
            if int(environ['CONTENT_LENGTH']) > 1024:
                start_response('417 Expectation Failed', [('Content-Length', '7')])
                return ['failure']
            else:
                text = environ['wsgi.input'].read()
                start_response('200 OK', [('Content-Length', str(len(text)))])
                return [text]
        self.site.application = wsgi_app
        sock = eventlet.connect(('localhost', self.port))
        fd = sock.makefile('rw')
        fd.write('PUT / HTTP/1.1\r\nHost: localhost\r\nContent-length: 1025\r\nExpect: 100-continue\r\n\r\n')
        fd.flush()
        response_line, headers, body = read_http(sock)
        self.assert_(response_line.startswith('HTTP/1.1 417 Expectation Failed'))
        self.assertEquals(body, 'failure')
        fd.write('PUT / HTTP/1.1\r\nHost: localhost\r\nContent-length: 7\r\nExpect: 100-continue\r\n\r\ntesting')
        fd.flush()
        header_lines = []
        while True:
            line = fd.readline()
            if line == '\r\n':
                break
            else:
                header_lines.append(line)
        self.assert_(header_lines[0].startswith('HTTP/1.1 100 Continue'))
        header_lines = []
        while True:
            line = fd.readline()
            if line == '\r\n':
                break
            else:
                header_lines.append(line)
        self.assert_(header_lines[0].startswith('HTTP/1.1 200 OK'))
        self.assertEquals(fd.read(7), 'testing')
        fd.close()

    def test_025_accept_errors(self):
        from eventlet import debug
        debug.hub_exceptions(True)
        listener = greensocket.socket()
        listener.bind(('localhost', 0))
        # NOT calling listen, to trigger the error
        self.logfile = StringIO()
        self.spawn_server(sock=listener)
        old_stderr = sys.stderr
        try:
            sys.stderr = self.logfile
            eventlet.sleep(0) # need to enter server loop
            try:
                eventlet.connect(('localhost', self.port))
                self.fail("Didn't expect to connect")
            except socket.error, exc:
                self.assertEquals(get_errno(exc), errno.ECONNREFUSED)

            self.assert_('Invalid argument' in self.logfile.getvalue(),
                self.logfile.getvalue())
        finally:
            sys.stderr = old_stderr
        debug.hub_exceptions(False)

    def test_026_log_format(self):
        self.spawn_server(log_format="HI %(request_line)s HI")
        sock = eventlet.connect(('localhost', self.port))
        sock.sendall('GET /yo! HTTP/1.1\r\nHost: localhost\r\n\r\n')
        sock.recv(1024)
        sock.close()
        self.assert_('\nHI GET /yo! HTTP/1.1 HI\n' in self.logfile.getvalue(), self.logfile.getvalue())

    def test_close_chunked_with_1_0_client(self):
        # verify that if we return a generator from our app
        # and we're not speaking with a 1.1 client, that we 
        # close the connection
        self.site.application = chunked_app
        sock = eventlet.connect(('localhost', self.port))

        sock.sendall('GET / HTTP/1.0\r\nHost: localhost\r\nConnection: keep-alive\r\n\r\n')
        
        response_line, headers, body = read_http(sock)
        self.assertEqual(headers['connection'], 'close')
        self.assertNotEqual(headers.get('transfer-encoding'), 'chunked')
        self.assertEquals(body, "thisischunked")
        
    def test_026_http_10_nokeepalive(self):
        # verify that if an http/1.0 client sends connection: keep-alive
        # and the server doesn't accept keep-alives, we close the connection
        self.spawn_server(keepalive=False)
        sock = eventlet.connect(
            ('localhost', self.port))

        sock.sendall('GET / HTTP/1.0\r\nHost: localhost\r\nConnection: keep-alive\r\n\r\n')
        response_line, headers, body = read_http(sock)
        self.assertEqual(headers['connection'], 'close')

    def test_027_keepalive_chunked(self):
        self.site.application = chunked_post
        sock = eventlet.connect(('localhost', self.port))
        fd = sock.makefile('w')
        fd.write('PUT /a HTTP/1.1\r\nHost: localhost\r\nTransfer-Encoding: chunked\r\n\r\n10\r\n0123456789abcdef\r\n0\r\n\r\n')
        fd.flush()
        read_http(sock)
        fd.write('PUT /b HTTP/1.1\r\nHost: localhost\r\nTransfer-Encoding: chunked\r\n\r\n10\r\n0123456789abcdef\r\n0\r\n\r\n')
        fd.flush()
        read_http(sock)
        fd.write('PUT /c HTTP/1.1\r\nHost: localhost\r\nTransfer-Encoding: chunked\r\n\r\n10\r\n0123456789abcdef\r\n0\r\n\r\n')
        fd.flush()
        read_http(sock)
        fd.write('PUT /a HTTP/1.1\r\nHost: localhost\r\nTransfer-Encoding: chunked\r\n\r\n10\r\n0123456789abcdef\r\n0\r\n\r\n')
        fd.flush()
        read_http(sock)

    def test_028_ssl_handshake_errors(self):
        errored = [False]
        def server(sock):
            try:
                wsgi.server(sock=sock, site=hello_world, log=self.logfile)
                errored[0] = 'SSL handshake error caused wsgi.server to exit.'
            except greenthread.greenlet.GreenletExit:
                pass
            except Exception, e:
                errored[0] = 'SSL handshake error raised exception %s.' % e
        for data in ('', 'GET /non-ssl-request HTTP/1.0\r\n\r\n'):
            srv_sock = eventlet.wrap_ssl(eventlet.listen(('localhost', 0)), 
                                        certfile=certificate_file, 
                                        keyfile=private_key_file,
                                        server_side=True)
            port = srv_sock.getsockname()[1]
            g = eventlet.spawn_n(server, srv_sock)
            client = eventlet.connect(('localhost', port))
            if data: # send non-ssl request
                client.sendall(data) 
            else: # close sock prematurely
                client.close()
            eventlet.sleep(0) # let context switch back to server
            self.assert_(not errored[0], errored[0])
            # make another request to ensure the server's still alive
            try:
                from eventlet.green import ssl
                client = ssl.wrap_socket(eventlet.connect(('localhost', port)))
                client.write('GET / HTTP/1.0\r\nHost: localhost\r\n\r\n')
                result = client.read()
                self.assert_(result.startswith('HTTP'), result)
                self.assert_(result.endswith('hello world'))
            except ImportError:
                pass # TODO: should test with OpenSSL
            greenthread.kill(g)

    def test_029_posthooks(self):
        posthook1_count = [0]
        posthook2_count = [0]
        def posthook1(env, value, multiplier=1):
            self.assertEquals(env['local.test'], 'test_029_posthooks')
            posthook1_count[0] += value * multiplier
        def posthook2(env, value, divisor=1):
            self.assertEquals(env['local.test'], 'test_029_posthooks')
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
            yield ''
        self.site.application = one_posthook_app
        sock = eventlet.connect(('localhost', self.port))
        fp = sock.makefile('rw')
        fp.write('GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        fp.flush()
        self.assertEquals(fp.readline(), 'HTTP/1.1 200 OK\r\n')
        fp.close()
        sock.close()
        self.assertEquals(posthook1_count[0], 6)
        self.assertEquals(posthook2_count[0], 0)

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
            yield ''
        self.site.application = two_posthook_app
        sock = eventlet.connect(('localhost', self.port))
        fp = sock.makefile('rw')
        fp.write('GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        fp.flush()
        self.assertEquals(fp.readline(), 'HTTP/1.1 200 OK\r\n')
        fp.close()
        sock.close()
        self.assertEquals(posthook1_count[0], 26)
        self.assertEquals(posthook2_count[0], 25)

    def test_zero_length_chunked_response(self):
        def zero_chunked_app(env, start_response):
            start_response('200 OK', [('Content-type', 'text/plain')])
            yield ""

        self.site.application = zero_chunked_app
        sock = eventlet.connect(
            ('localhost', self.port))

        fd = sock.makefile('rw')
        fd.write('GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        fd.flush()
        response = fd.read().split('\r\n')
        headers = []
        while True:
            h = response.pop(0)
            headers.append(h)
            if h == '':
                break
        self.assert_('Transfer-Encoding: chunked' in ''.join(headers))
        # should only be one chunk of zero size with two blank lines
        # (one terminates the chunk, one terminates the body)
        self.assertEqual(response, ['0', '', ''])

    def test_aborted_chunked_post(self):
        read_content = event.Event()
        blew_up = [False]
        def chunk_reader(env, start_response):
            try:
                content = env['wsgi.input'].read(1024)
            except IOError:
                blew_up[0] = True
                content = 'ok'
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
        sock = eventlet.connect(('127.0.0.1', self.port))
        sock.sendall(data)
        sock.close()
        # the test passes if we successfully get here, and read all the data
        # in spite of the early close
        self.assertEqual(read_content.wait(), 'ok')
        self.assert_(blew_up[0])

    def test_exceptions_close_connection(self):
        def wsgi_app(environ, start_response):
            raise RuntimeError("intentional error")
        self.site.application = wsgi_app
        sock = eventlet.connect(('localhost', self.port))
        fd = sock.makefile('rw')
        fd.write('GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        fd.flush()
        response_line, headers, body = read_http(sock)
        self.assert_(response_line.startswith('HTTP/1.1 500 Internal Server Error'))
        self.assertEqual(headers['connection'], 'close')
        self.assert_('transfer-encoding' not in headers)

    def test_unicode_raises_error(self):
        def wsgi_app(environ, start_response):
            start_response("200 OK", [])
            yield u"oh hai"
            yield u"non-encodable unicode: \u0230"
        self.site.application = wsgi_app
        sock = eventlet.connect(('localhost', self.port))
        fd = sock.makefile('rw')
        fd.write('GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        fd.flush()
        response_line, headers, body = read_http(sock)
        self.assert_(response_line.startswith('HTTP/1.1 500 Internal Server Error'))
        self.assertEqual(headers['connection'], 'close')
        self.assert_('unicode' in body)

def read_headers(sock):
    fd = sock.makefile()
    try:
        response_line = fd.readline()
    except socket.error, exc:
        if get_errno(exc) == 10053:
            raise ConnectionClosed
        raise
    if not response_line:
        raise ConnectionClosed

    header_lines = []
    while True:
        line = fd.readline()
        if line == '\r\n':
            break
        else:
            header_lines.append(line)
    headers = dict()
    for x in header_lines:
        x = x.strip()
        if not x:
            continue
        key, value = x.split(': ', 1)
        assert key.lower() not in headers, "%s header duplicated" % key
        headers[key.lower()] = value
    return response_line, headers

class IterableAlreadyHandledTest(_TestBase):
    def set_site(self):
        self.site = IterableSite()

    def get_app(self):
        return IterableApp(True)

    def test_iterable_app_keeps_socket_open_unless_connection_close_sent(self):
        self.site.application = self.get_app()
        sock = eventlet.connect(
            ('localhost', self.port))

        fd = sock.makefile('rw')
        fd.write('GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')

        fd.flush()
        response_line, headers = read_headers(sock)
        self.assertEqual(response_line, 'HTTP/1.1 200 OK\r\n')
        self.assert_('connection' not in headers)
        fd.write('GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        fd.flush()
        response_line, headers, body = read_http(sock)
        self.assertEqual(response_line, 'HTTP/1.1 200 OK\r\n')
        self.assertEqual(headers.get('transfer-encoding'), 'chunked')
        self.assertEqual(body, '0\r\n\r\n') # Still coming back chunked

class ProxiedIterableAlreadyHandledTest(IterableAlreadyHandledTest):
    # same thing as the previous test but ensuring that it works with tpooled
    # results as well as regular ones
    @skip_with_pyevent
    def get_app(self):
        from eventlet import tpool
        return tpool.Proxy(super(ProxiedIterableAlreadyHandledTest, self).get_app())

    def tearDown(self):
        from eventlet import tpool
        tpool.killall()
        super(ProxiedIterableAlreadyHandledTest, self).tearDown()

class TestChunkedInput(_TestBase):
    dirt = ""
    validator = None
    def application(self, env, start_response):
        input = env['wsgi.input']
        response = []

        pi = env["PATH_INFO"]

        if pi=="/short-read":
            d=input.read(10)
            response = [d]
        elif pi=="/lines":
            for x in input:
                response.append(x)
        elif pi=="/ping":
            input.read()
            response.append("pong")
        else:
            raise RuntimeError("bad path")

        start_response('200 OK', [('Content-Type', 'text/plain')])
        return response

    def connect(self):
        return eventlet.connect(('localhost', self.port))

    def set_site(self):
        self.site = Site()
        self.site.application = self.application

    def chunk_encode(self, chunks, dirt=None):
        if dirt is None:
            dirt = self.dirt

        b = ""
        for c in chunks:
            b += "%x%s\r\n%s\r\n" % (len(c), dirt, c)
        return b

    def body(self, dirt=None):
        return self.chunk_encode(["this", " is ", "chunked", "\nline", " 2", "\n", "line3", ""], dirt=dirt)

    def ping(self, fd):
        fd.sendall("GET /ping HTTP/1.1\r\n\r\n")
        self.assertEquals(read_http(fd)[-1], "pong")

    def test_short_read_with_content_length(self):
        body = self.body()
        req = "POST /short-read HTTP/1.1\r\ntransfer-encoding: Chunked\r\nContent-Length:1000\r\n\r\n" + body

        fd = self.connect()
        fd.sendall(req)
        self.assertEquals(read_http(fd)[-1], "this is ch")

        self.ping(fd)

    def test_short_read_with_zero_content_length(self):
        body = self.body()
        req = "POST /short-read HTTP/1.1\r\ntransfer-encoding: Chunked\r\nContent-Length:0\r\n\r\n" + body
        fd = self.connect()
        fd.sendall(req)
        self.assertEquals(read_http(fd)[-1], "this is ch")

        self.ping(fd)

    def test_short_read(self):
        body = self.body()
        req = "POST /short-read HTTP/1.1\r\ntransfer-encoding: Chunked\r\n\r\n" + body

        fd = self.connect()
        fd.sendall(req)
        self.assertEquals(read_http(fd)[-1], "this is ch")

        self.ping(fd)

    def test_dirt(self):
        body = self.body(dirt="; here is dirt\0bla")
        req = "POST /ping HTTP/1.1\r\ntransfer-encoding: Chunked\r\n\r\n" + body

        fd = self.connect()
        fd.sendall(req)
        self.assertEquals(read_http(fd)[-1], "pong")

        self.ping(fd)

    def test_chunked_readline(self):
        body = self.body()
        req = "POST /lines HTTP/1.1\r\nContent-Length: %s\r\ntransfer-encoding: Chunked\r\n\r\n%s" % (len(body), body)

        fd = self.connect()
        fd.sendall(req)
        self.assertEquals(read_http(fd)[-1], 'this is chunked\nline 2\nline3')

    def test_close_before_finished(self):
        import signal

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
            fd.sendall(req)
            fd.close()
            eventlet.sleep(0.0)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, signal.SIG_DFL)

        assert not got_signal, "caught alarm signal. infinite loop detected."

    def test_ipv6(self):
        try:
            sock = eventlet.listen(('::1', 0), family=socket.AF_INET6)
        except (socket.gaierror, socket.error):  # probably no ipv6
            return
        log = StringIO()
        # first thing the server does is try to log the IP it's bound to
        def run_server():
            try:
                server = wsgi.server(sock=sock, log=log, site=Site())
            except ValueError:
                log.write('broked')
        eventlet.spawn_n(run_server)
        logval = log.getvalue()
        while not logval:
            eventlet.sleep(0.0)
            logval = log.getvalue()
        if 'broked' in logval:
            self.fail('WSGI server raised exception with ipv6 socket')


if __name__ == '__main__':
    main()
