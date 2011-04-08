"""Test than modules in eventlet.green package are indeed green.
To do that spawn a green server and then access it using a green socket.
If either operation blocked the whole script would block and timeout.
"""
import unittest
from eventlet.green import urllib2, BaseHTTPServer
from eventlet import spawn, kill

class QuietHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    def log_message(self, *args, **kw):
        pass

def start_http_server():
    server_address = ('localhost', 0)
    httpd = BaseHTTPServer.HTTPServer(server_address, QuietHandler)
    sa = httpd.socket.getsockname()
    #print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.request_count = 0
    def serve():
        # increment the request_count before handling the request because
        # the send() for the response blocks (or at least appeared to be)
        httpd.request_count += 1
        httpd.handle_request()
    return spawn(serve), httpd, sa[1]

class TestGreenness(unittest.TestCase):

    def setUp(self):
        self.gthread, self.server,self.port = start_http_server()
        #print 'Spawned the server'

    def tearDown(self):
        self.server.server_close()
        kill(self.gthread)

    def test_urllib2(self):
        self.assertEqual(self.server.request_count, 0)
        try:
            urllib2.urlopen('http://127.0.0.1:%s' % self.port)
            assert False, 'should not get there'
        except urllib2.HTTPError, ex:
            assert ex.code == 501, repr(ex)
        self.assertEqual(self.server.request_count, 1)

if __name__ == '__main__':
    unittest.main()
