"""Basic twisted protocols converted to synchronous mode"""
import sys
from twisted.internet.protocol import Protocol as twistedProtocol
from twisted.internet.error import ConnectionDone
from twisted.internet.protocol import Factory, ClientFactory
from twisted.internet import main
from twisted.python import failure

from eventlet import greenthread
from eventlet import getcurrent
from eventlet.coros import Queue
from eventlet.event import Event as BaseEvent


class ValueQueue(Queue):
    """Queue that keeps the last item forever in the queue if it's an exception.
    Useful if you send an exception over queue only once, and once sent it must be always
    available.
    """

    def send(self, value=None, exc=None):
        if exc is not None or not self.has_error():
            Queue.send(self, value, exc)

    def wait(self):
        """The difference from Queue.wait: if there is an only item in the
        Queue and it is an exception, raise it, but keep it in the Queue, so
        that future calls to wait() will raise it again.
        """
        if self.has_error() and len(self.items)==1:
            # the last item, which is an exception, raise without emptying the Queue
            getcurrent().throw(*self.items[0][1])
        else:
            return Queue.wait(self)

    def has_error(self):
        return self.items and self.items[-1][1] is not None


class Event(BaseEvent):

    def send(self, value, exc=None):
        if self.ready():
            self.reset()
        return BaseEvent.send(self, value, exc)

    def send_exception(self, *throw_args):
        if self.ready():
            self.reset()
        return BaseEvent.send_exception(self, *throw_args)

class Producer2Event(object):

    # implements IPullProducer

    def __init__(self, event):
        self.event = event

    def resumeProducing(self):
        self.event.send(1)

    def stopProducing(self):
        del self.event


class GreenTransportBase(object):

    transportBufferSize = None

    def __init__(self, transportBufferSize=None):
        if transportBufferSize is not None:
            self.transportBufferSize = transportBufferSize
        self._queue = ValueQueue()
        self._write_event = Event()
        self._disconnected_event = Event()

    def build_protocol(self):
        return self.protocol_class(self)

    def _got_transport(self, transport):
        self._queue.send(transport)

    def _got_data(self, data):
        self._queue.send(data)

    def _connectionLost(self, reason):
        self._disconnected_event.send(reason.value)
        self._queue.send_exception(reason.value)
        self._write_event.send_exception(reason.value)

    def _wait(self):
        if self.disconnecting or self._disconnected_event.ready():
            if self._queue:
                return self._queue.wait()
            else:
                raise self._disconnected_event.wait()
        self.resumeProducing()
        try:
            return self._queue.wait()
        finally:
            self.pauseProducing()

    def write(self, data, wait=True):
        if self._disconnected_event.ready():
            raise self._disconnected_event.wait()
        if wait:
            self._write_event.reset()
            self.transport.write(data)
            self._write_event.wait()
        else:
            self.transport.write(data)

    def loseConnection(self, connDone=failure.Failure(main.CONNECTION_DONE), wait=True):
        self.transport.unregisterProducer()
        self.transport.loseConnection(connDone)
        if wait:
            self._disconnected_event.wait()

    def __getattr__(self, item):
        if item=='transport':
            raise AttributeError(item)
        if hasattr(self, 'transport'):
            try:
                return getattr(self.transport, item)
            except AttributeError:
                me = type(self).__name__
                trans = type(self.transport).__name__
                raise AttributeError("Neither %r nor %r has attribute %r" % (me, trans, item))
        else:
            raise AttributeError(item)

    def resumeProducing(self):
        self.paused -= 1
        if self.paused==0:
            self.transport.resumeProducing()

    def pauseProducing(self):
        self.paused += 1
        if self.paused==1:
            self.transport.pauseProducing()

    def _init_transport_producer(self):
        self.transport.pauseProducing()
        self.paused = 1

    def _init_transport(self):
        transport = self._queue.wait()
        self.transport = transport
        if self.transportBufferSize is not None:
            transport.bufferSize = self.transportBufferSize
        self._init_transport_producer()
        transport.registerProducer(Producer2Event(self._write_event), False)


class Protocol(twistedProtocol):

    def __init__(self, recepient):
        self._recepient = recepient

    def connectionMade(self):
        self._recepient._got_transport(self.transport)

    def dataReceived(self, data):
        self._recepient._got_data(data)

    def connectionLost(self, reason):
        self._recepient._connectionLost(reason)


class UnbufferedTransport(GreenTransportBase):
    """A very simple implementation of a green transport without an additional buffer"""

    protocol_class = Protocol

    def recv(self):
        """Receive a single chunk of undefined size.

        Return '' if connection was closed cleanly, raise the exception if it was closed
        in a non clean fashion. After that all successive calls return ''.
        """
        if self._disconnected_event.ready():
            return ''
        try:
            return self._wait()
        except ConnectionDone:
            return ''

    def read(self):
        """Read the data from the socket until the connection is closed cleanly.

        If connection was closed in a non-clean fashion, the appropriate exception
        is raised. In that case already received data is lost.
        Next time read() is called it returns ''.
        """
        result = ''
        while True:
            recvd = self.recv()
            if not recvd:
                break
            result += recvd
        return result

    # iterator protocol:

    def __iter__(self):
        return self

    def next(self):
        result = self.recv()
        if not result:
            raise StopIteration
        return result


class GreenTransport(GreenTransportBase):

    protocol_class = Protocol
    _buffer = ''
    _error = None

    def read(self, size=-1):
        """Read size bytes or until EOF"""
        if not self._disconnected_event.ready():
            try:
                while len(self._buffer) < size or size < 0:
                    self._buffer += self._wait()
            except ConnectionDone:
                pass
            except:
                if not self._disconnected_event.has_exception():
                    raise
        if size>=0:
            result, self._buffer = self._buffer[:size], self._buffer[size:]
        else:
            result, self._buffer = self._buffer, ''
        if not result and self._disconnected_event.has_exception():
            try:
                self._disconnected_event.wait()
            except ConnectionDone:
                pass
        return result

    def recv(self, buflen=None):
        """Receive a single chunk of undefined size but no bigger than buflen"""
        if not self._disconnected_event.ready():
            self.resumeProducing()
            try:
                try:
                    recvd = self._wait()
                    #print 'received %r' % recvd
                    self._buffer += recvd
                except ConnectionDone:
                    pass
                except:
                    if not self._disconnected_event.has_exception():
                        raise
            finally:
                self.pauseProducing()
        if buflen is None:
            result, self._buffer = self._buffer, ''
        else:
            result, self._buffer = self._buffer[:buflen], self._buffer[buflen:]
        if not result and self._disconnected_event.has_exception():
            try:
                self._disconnected_event.wait()
            except ConnectionDone:
                pass
        return result

    # iterator protocol:

    def __iter__(self):
        return self

    def next(self):
        res = self.recv()
        if not res:
            raise StopIteration
        return res


class GreenInstanceFactory(ClientFactory):

    def __init__(self, instance, event):
        self.instance = instance
        self.event = event

    def buildProtocol(self, addr):
        return self.instance

    def clientConnectionFailed(self, connector, reason):
        self.event.send_exception(reason.type, reason.value, reason.tb)


class GreenClientCreator(object):
    """Connect to a remote host and return a connected green transport instance.
    """

    gtransport_class = GreenTransport

    def __init__(self, reactor=None, gtransport_class=None, *args, **kwargs):
        if reactor is None:
            from twisted.internet import reactor
        self.reactor = reactor
        if gtransport_class is not None:
            self.gtransport_class = gtransport_class
        self.args = args
        self.kwargs = kwargs

    def _make_transport_and_factory(self):
        gtransport = self.gtransport_class(*self.args, **self.kwargs)
        protocol = gtransport.build_protocol()
        factory = GreenInstanceFactory(protocol, gtransport._queue)
        return gtransport, factory

    def connectTCP(self, host, port, *args, **kwargs):
        gtransport, factory = self._make_transport_and_factory()
        self.reactor.connectTCP(host, port, factory, *args, **kwargs)
        gtransport._init_transport()
        return gtransport

    def connectSSL(self, host, port, *args, **kwargs):
        gtransport, factory = self._make_transport_and_factory()
        self.reactor.connectSSL(host, port, factory, *args, **kwargs)
        gtransport._init_transport()
        return gtransport

    def connectTLS(self, host, port, *args, **kwargs):
        gtransport, factory = self._make_transport_and_factory()
        self.reactor.connectTLS(host, port, factory, *args, **kwargs)
        gtransport._init_transport()
        return gtransport

    def connectUNIX(self, address, *args, **kwargs):
        gtransport, factory = self._make_transport_and_factory()
        self.reactor.connectUNIX(address, factory, *args, **kwargs)
        gtransport._init_transport()
        return gtransport

    def connectSRV(self, service, domain, *args, **kwargs):
        SRVConnector = kwargs.pop('ConnectorClass', None)
        if SRVConnector is None:
            from twisted.names.srvconnect import SRVConnector
        gtransport, factory = self._make_transport_and_factory()
        c = SRVConnector(self.reactor, service, domain, factory, *args, **kwargs)
        c.connect()
        gtransport._init_transport()
        return gtransport


class SimpleSpawnFactory(Factory):
    """Factory that spawns a new greenlet for each incoming connection.

    For an incoming connection a new greenlet is created using the provided
    callback as a function and a connected green transport instance as an
    argument.
    """

    gtransport_class = GreenTransport

    def __init__(self, handler, gtransport_class=None, *args, **kwargs):
        if callable(handler):
            self.handler = handler
        else:
            self.handler = handler.send
        if hasattr(handler, 'send_exception'):
            self.exc_handler = handler.send_exception
        if gtransport_class is not None:
            self.gtransport_class = gtransport_class
        self.args = args
        self.kwargs = kwargs

    def exc_handler(self, *args):
        pass

    def buildProtocol(self, addr):
        gtransport = self.gtransport_class(*self.args, **self.kwargs)
        protocol = gtransport.build_protocol()
        protocol.factory = self
        self._do_spawn(gtransport, protocol)
        return protocol

    def _do_spawn(self, gtransport, protocol):
        greenthread.spawn(self._run_handler, gtransport, protocol)

    def _run_handler(self, gtransport, protocol):
        try:
            gtransport._init_transport()
        except Exception:
            self.exc_handler(*sys.exc_info())
        else:
            self.handler(gtransport)


class SpawnFactory(SimpleSpawnFactory):
    """An extension to SimpleSpawnFactory that provides some control over
    the greenlets it has spawned.
    """

    def __init__(self, handler, gtransport_class=None, *args, **kwargs):
        self.greenlets = set()
        SimpleSpawnFactory.__init__(self, handler, gtransport_class, *args, **kwargs)

    def _do_spawn(self, gtransport, protocol):
        g = greenthread.spawn(self._run_handler, gtransport, protocol)
        self.greenlets.add(g)
        g.link(lambda *_: self.greenlets.remove(g))

    def waitall(self):
        results = []
        for g in self.greenlets:
            results.append(g.wait())
        return results

