"""Example for GreenTransport and GreenClientCreator.

In this example reactor is started implicitly upon the first
use of a blocking function.
"""
from twisted.internet import ssl
from twisted.internet.error import ConnectionClosed
from eventlet.twistedutil.protocol import GreenClientCreator
from eventlet.twistedutil.protocols.basic import LineOnlyReceiverTransport
from twisted.internet import reactor

# read from TCP connection
conn = GreenClientCreator(reactor).connectTCP('www.google.com', 80)
conn.write('GET / HTTP/1.0\r\n\r\n')
conn.loseWriteConnection()
print conn.read()

# read from SSL connection line by line
conn = GreenClientCreator(reactor, LineOnlyReceiverTransport).connectSSL('sf.net', 443, ssl.ClientContextFactory())
conn.write('GET / HTTP/1.0\r\n\r\n')
try:
    for num, line in enumerate(conn):
        print '%3s %r' % (num, line)
except ConnectionClosed, ex:
    print ex

