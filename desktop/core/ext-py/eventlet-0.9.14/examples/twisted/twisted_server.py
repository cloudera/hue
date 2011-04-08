"""Simple chat demo application.
Listen on port 8007 and re-send all the data received to other participants.

Demonstrates how to
 * plug in eventlet into a twisted application (join_reactor)
 * how to use SpawnFactory to start a new greenlet for each new request.
"""
from eventlet.twistedutil import join_reactor
from eventlet.twistedutil.protocol import SpawnFactory
from eventlet.twistedutil.protocols.basic import LineOnlyReceiverTransport

class Chat:

    def __init__(self):
        self.participants = []

    def handler(self, conn):
        peer = conn.getPeer()
        print 'new connection from %s' % (peer, )
        conn.write("Welcome! There're %s participants already\n" % (len(self.participants)))
        self.participants.append(conn)
        try:
            for line in conn:
                if line:
                    print 'received from %s: %s' % (peer, line)
                    for buddy in self.participants:
                        if buddy is not conn:
                            buddy.sendline('from %s: %s' % (peer, line))
        except Exception, ex:
            print peer, ex
        else:
            print peer, 'connection done'
        finally:
            conn.loseConnection()
            self.participants.remove(conn)

print __doc__
chat = Chat()
from twisted.internet import reactor
reactor.listenTCP(8007, SpawnFactory(chat.handler, LineOnlyReceiverTransport))
reactor.run()

