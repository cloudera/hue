from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.protocols import basic

from xcaplib.green import XCAPClient

from eventlet.twistedutil import deferToGreenThread
from eventlet.twistedutil import join_reactor

class LineOnlyReceiver(basic.LineOnlyReceiver):

    def lineReceived(self, line):
        print 'received: %r' % line
        if not line:
            return
        app, context, node = (line + ' ').split(' ', 3) 
        context = {'u' : 'users', 'g': 'global'}.get(context, context)
        d = deferToGreenThread(client._get, app, node, globaltree=context=='global')
        def callback(result):
            self.transport.write(str(result))
        def errback(error):
            self.transport.write(error.getTraceback())
        d.addCallback(callback)
        d.addErrback(errback)

class MyFactory(Factory):
    protocol = LineOnlyReceiver

client = XCAPClient('https://xcap.sipthor.net/xcap-root', 'alice@example.com', '123')
reactor.listenTCP(8007, MyFactory())
reactor.run()
