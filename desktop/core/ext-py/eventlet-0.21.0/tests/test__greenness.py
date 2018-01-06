"""Test than modules in eventlet.green package are indeed green.
To do that spawn a green server and then access it using a green socket.
If either operation blocked the whole script would block and timeout.
"""
import eventlet
from eventlet.green import BaseHTTPServer
from eventlet.support import six

if six.PY2:
    from eventlet.green.urllib2 import HTTPError, urlopen
else:
    from eventlet.green.urllib.request import urlopen
    from eventlet.green.urllib.error import HTTPError


class QuietHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *args, **kw):
        pass


def start_http_server():
    server_address = ('localhost', 0)
    httpd = BaseHTTPServer.HTTPServer(server_address, QuietHandler)
    sa = httpd.socket.getsockname()
    # print("Serving HTTP on", sa[0], "port", sa[1], "...")
    httpd.request_count = 0

    def serve():
        # increment the request_count before handling the request because
        # the send() for the response blocks (or at least appeared to be)
        httpd.request_count += 1
        httpd.handle_request()
    return eventlet.spawn(serve), httpd, sa[1]


def test_urllib():
    gthread, server, port = start_http_server()

    try:
        assert server.request_count == 0
        try:
            urlopen('http://127.0.0.1:{0}'.format(port))
            assert False, 'should not get there'
        except HTTPError as ex:
            assert ex.code == 501, repr(ex)
        assert server.request_count == 1
    finally:
        server.server_close()
        eventlet.kill(gthread)
