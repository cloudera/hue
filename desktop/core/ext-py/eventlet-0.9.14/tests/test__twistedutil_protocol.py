from tests import requires_twisted

import unittest
try:
    from twisted.internet import reactor
    from twisted.internet.error import ConnectionDone
    import eventlet.twistedutil.protocol as pr
    from eventlet.twistedutil.protocols.basic import LineOnlyReceiverTransport
except ImportError:
    # stub out some of the twisted dependencies so it at least imports
    class dummy(object):
        pass
    pr = dummy()
    pr.UnbufferedTransport = None
    pr.GreenTransport = None
    pr.GreenClientCreator = lambda *a, **k: None
    class reactor(object):
        pass
    
from eventlet import spawn, sleep, with_timeout, spawn_after
from eventlet.coros import Event

try:
    from eventlet.green import socket
except SyntaxError:
    socket = None

DELAY=0.01

if socket is not None:
    def setup_server_socket(self, delay=DELAY, port=0):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', port))
        port = s.getsockname()[1]
        s.listen(5)
        s.settimeout(delay*3)
        def serve():
            conn, addr = s.accept()
            conn.settimeout(delay+1)
            try:
                hello = conn.makefile().readline()[:-2]
            except socket.timeout:
                return
            conn.sendall('you said %s. ' % hello)
            sleep(delay)
            conn.sendall('BYE')
            sleep(delay)
            #conn.close()
        spawn(serve)
        return port

def setup_server_SpawnFactory(self, delay=DELAY, port=0):
    def handle(conn):
        port.stopListening()
        try:
            hello = conn.readline()
        except ConnectionDone:
            return
        conn.write('you said %s. ' % hello)
        sleep(delay)
        conn.write('BYE')
        sleep(delay)
        conn.loseConnection()
    port = reactor.listenTCP(0, pr.SpawnFactory(handle, LineOnlyReceiverTransport))
    return port.getHost().port

class TestCase(unittest.TestCase):
    transportBufferSize = None

    @property
    def connector(self):
        return pr.GreenClientCreator(reactor, self.gtransportClass, self.transportBufferSize)
    
    @requires_twisted
    def setUp(self):
        port = self.setup_server()
        self.conn = self.connector.connectTCP('127.0.0.1', port)
        if self.transportBufferSize is not None:
            self.assertEqual(self.transportBufferSize, self.conn.transport.bufferSize)

class TestUnbufferedTransport(TestCase):
    gtransportClass = pr.UnbufferedTransport
    setup_server = setup_server_SpawnFactory

    @requires_twisted
    def test_full_read(self):
        self.conn.write('hello\r\n')
        self.assertEqual(self.conn.read(), 'you said hello. BYE')
        self.assertEqual(self.conn.read(), '')
        self.assertEqual(self.conn.read(), '')

    @requires_twisted
    def test_iterator(self):
        self.conn.write('iterator\r\n')
        self.assertEqual('you said iterator. BYE', ''.join(self.conn))

class TestUnbufferedTransport_bufsize1(TestUnbufferedTransport):
    transportBufferSize = 1
    setup_server = setup_server_SpawnFactory

class TestGreenTransport(TestUnbufferedTransport):
    gtransportClass = pr.GreenTransport
    setup_server = setup_server_SpawnFactory

    @requires_twisted
    def test_read(self):
        self.conn.write('hello\r\n')
        self.assertEqual(self.conn.read(9), 'you said ')
        self.assertEqual(self.conn.read(999), 'hello. BYE')
        self.assertEqual(self.conn.read(9), '')
        self.assertEqual(self.conn.read(1), '')
        self.assertEqual(self.conn.recv(9), '')
        self.assertEqual(self.conn.recv(1), '')

    @requires_twisted
    def test_read2(self):
        self.conn.write('world\r\n')
        self.assertEqual(self.conn.read(), 'you said world. BYE')
        self.assertEqual(self.conn.read(), '')
        self.assertEqual(self.conn.recv(), '')

    @requires_twisted
    def test_iterator(self):
        self.conn.write('iterator\r\n')
        self.assertEqual('you said iterator. BYE', ''.join(self.conn))

    _tests = [x for x in locals().keys() if x.startswith('test_')]

    @requires_twisted
    def test_resume_producing(self):
        for test in self._tests:
            self.setUp()
            self.conn.resumeProducing()
            getattr(self, test)()

    @requires_twisted
    def test_pause_producing(self):
        self.conn.pauseProducing()
        self.conn.write('hi\r\n')
        result = with_timeout(DELAY*10, self.conn.read, timeout_value='timed out')
        self.assertEqual('timed out', result)

    @requires_twisted
    def test_pauseresume_producing(self):
        self.conn.pauseProducing()
        spawn_after(DELAY*5, self.conn.resumeProducing)
        self.conn.write('hi\r\n')
        result = with_timeout(DELAY*10, self.conn.read, timeout_value='timed out')
        self.assertEqual('you said hi. BYE', result)

class TestGreenTransport_bufsize1(TestGreenTransport):
    transportBufferSize = 1

# class TestGreenTransportError(TestCase):
#     setup_server = setup_server_SpawnFactory
#     gtransportClass = pr.GreenTransport
# 
#     def test_read_error(self):
#         self.conn.write('hello\r\n')
#         sleep(DELAY*1.5) # make sure the rest of data arrives
#         try:
#             1//0
#         except:
#             #self.conn.loseConnection(failure.Failure()) # does not work, why?
#             spawn(self.conn._queue.send_exception, *sys.exc_info())
#         self.assertEqual(self.conn.read(9), 'you said ')
#         self.assertEqual(self.conn.read(7), 'hello. ')
#         self.assertEqual(self.conn.read(9), 'BYE')
#         self.assertRaises(ZeroDivisionError, self.conn.read, 9)
#         self.assertEqual(self.conn.read(1), '')
#         self.assertEqual(self.conn.read(1), '')
# 
#     def test_recv_error(self):
#         self.conn.write('hello')
#         self.assertEqual('you said hello. ', self.conn.recv())
#         sleep(DELAY*1.5) # make sure the rest of data arrives
#         try:
#             1//0
#         except:
#             #self.conn.loseConnection(failure.Failure()) # does not work, why?
#             spawn(self.conn._queue.send_exception, *sys.exc_info())
#         self.assertEqual('BYE', self.conn.recv())
#         self.assertRaises(ZeroDivisionError, self.conn.recv, 9)
#         self.assertEqual('', self.conn.recv(1))
#         self.assertEqual('', self.conn.recv())
#

if socket is not None:

    class TestUnbufferedTransport_socketserver(TestUnbufferedTransport):
        setup_server = setup_server_socket

    class TestUnbufferedTransport_socketserver_bufsize1(TestUnbufferedTransport):
        transportBufferSize = 1
        setup_server = setup_server_socket

    class TestGreenTransport_socketserver(TestGreenTransport):
        setup_server = setup_server_socket

    class TestGreenTransport_socketserver_bufsize1(TestGreenTransport):
        transportBufferSize = 1
        setup_server = setup_server_socket


class TestTLSError(unittest.TestCase):
    @requires_twisted
    def test_server_connectionMade_never_called(self):
        # trigger case when protocol instance is created,
        # but it's connectionMade is never called
        from gnutls.interfaces.twisted import X509Credentials
        from gnutls.errors import GNUTLSError
        cred = X509Credentials(None, None)
        ev = Event()
        def handle(conn):
            ev.send("handle must not be called")
        s = reactor.listenTLS(0, pr.SpawnFactory(handle, LineOnlyReceiverTransport), cred)
        creator = pr.GreenClientCreator(reactor, LineOnlyReceiverTransport)
        try:
            conn = creator.connectTLS('127.0.0.1', s.getHost().port, cred)
        except GNUTLSError:
            pass
        assert ev.poll() is None, repr(ev.poll())
        
try:
    import gnutls.interfaces.twisted
except ImportError:
    del TestTLSError

@requires_twisted
def main():
    unittest.main()

if __name__=='__main__':
    main()
