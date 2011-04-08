"""Listen on port 8888 and pretend to be an HTTP proxy.
It even works for some pages.

Demonstrates how to
 * plug in eventlet into a twisted application (join_reactor)
 * call green functions from places where blocking calls
   are not allowed (deferToGreenThread)
 * use eventlet.green package which provides [some of] the
   standard library modules that don't block other greenlets.
"""
import re
from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.protocols import basic

from eventlet.twistedutil import deferToGreenThread
from eventlet.twistedutil import join_reactor
from eventlet.green import httplib

class LineOnlyReceiver(basic.LineOnlyReceiver):

    def connectionMade(self):
        self.lines = []

    def lineReceived(self, line):
        if line:
            self.lines.append(line)
        elif self.lines:
            self.requestReceived(self.lines)
            self.lines = []

    def requestReceived(self, lines):
        request = re.match('^(\w+) http://(.*?)(/.*?) HTTP/1..$', lines[0])
        #print request.groups()
        method, host, path = request.groups()
        headers = dict(x.split(': ', 1) for x in lines[1:])
        def callback(result):
            self.transport.write(str(result))
            self.transport.loseConnection()
        def errback(err):
            err.printTraceback()
            self.transport.loseConnection()
        d = deferToGreenThread(http_request, method, host, path, headers=headers)
        d.addCallbacks(callback, errback)

def http_request(method, host, path, headers):
    conn = httplib.HTTPConnection(host)
    conn.request(method, path, headers=headers)
    response = conn.getresponse()
    body = response.read()
    print method, host, path, response.status, response.reason, len(body)
    return format_response(response, body)

def format_response(response, body):
    result = "HTTP/1.1 %s %s" % (response.status, response.reason)
    for k, v in response.getheaders():
        result += '\r\n%s: %s' % (k, v)
    if body:
        result += '\r\n\r\n'
        result += body
        result += '\r\n'
    return result

class MyFactory(Factory):
    protocol = LineOnlyReceiver

print __doc__
reactor.listenTCP(8888, MyFactory())
reactor.run()
