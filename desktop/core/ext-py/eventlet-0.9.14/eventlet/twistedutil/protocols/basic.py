from twisted.protocols import basic
from twisted.internet.error import ConnectionDone
from eventlet.twistedutil.protocol import GreenTransportBase


class LineOnlyReceiver(basic.LineOnlyReceiver):

    def __init__(self, recepient):
        self._recepient = recepient

    def connectionMade(self):
        self._recepient._got_transport(self.transport)

    def connectionLost(self, reason):
        self._recepient._connectionLost(reason)

    def lineReceived(self, line):
        self._recepient._got_data(line)


class LineOnlyReceiverTransport(GreenTransportBase):

    protocol_class = LineOnlyReceiver

    def readline(self):
        return self._wait()

    def sendline(self, line):
        self.protocol.sendLine(line)

    # iterator protocol:

    def __iter__(self):
        return self

    def next(self):
        try:
            return self.readline()
        except ConnectionDone:
            raise StopIteration

