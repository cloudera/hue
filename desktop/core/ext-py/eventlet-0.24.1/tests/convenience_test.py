import os
import warnings

import eventlet
from eventlet import convenience, debug
from eventlet.green import socket
import six
import tests
import tests.mock


certificate_file = os.path.join(os.path.dirname(__file__), 'test_server.crt')
private_key_file = os.path.join(os.path.dirname(__file__), 'test_server.key')


class TestServe(tests.LimitedTestCase):
    def setUp(self):
        super(TestServe, self).setUp()
        debug.hub_exceptions(False)

    def tearDown(self):
        super(TestServe, self).tearDown()
        debug.hub_exceptions(True)

    def test_exiting_server(self):
        # tests that the server closes the client sock on handle() exit
        def closer(sock, addr):
            pass

        l = eventlet.listen(('localhost', 0))
        gt = eventlet.spawn(eventlet.serve, l, closer)
        client = eventlet.connect(('localhost', l.getsockname()[1]))
        client.sendall(b'a')
        self.assertFalse(client.recv(100))
        gt.kill()

    def test_excepting_server(self):
        # tests that the server closes the client sock on handle() exception
        def crasher(sock, addr):
            sock.recv(1024)
            0 // 0

        l = eventlet.listen(('localhost', 0))
        gt = eventlet.spawn(eventlet.serve, l, crasher)
        client = eventlet.connect(('localhost', l.getsockname()[1]))
        client.sendall(b'a')
        self.assertRaises(ZeroDivisionError, gt.wait)
        self.assertFalse(client.recv(100))

    def test_excepting_server_already_closed(self):
        # same as above but with explicit clsoe before crash
        def crasher(sock, addr):
            sock.recv(1024)
            sock.close()
            0 // 0

        l = eventlet.listen(('localhost', 0))
        gt = eventlet.spawn(eventlet.serve, l, crasher)
        client = eventlet.connect(('localhost', l.getsockname()[1]))
        client.sendall(b'a')
        self.assertRaises(ZeroDivisionError, gt.wait)
        self.assertFalse(client.recv(100))

    def test_called_for_each_connection(self):
        hits = [0]

        def counter(sock, addr):
            hits[0] += 1
        l = eventlet.listen(('localhost', 0))
        gt = eventlet.spawn(eventlet.serve, l, counter)
        for i in six.moves.range(100):
            client = eventlet.connect(('localhost', l.getsockname()[1]))
            self.assertFalse(client.recv(100))
        gt.kill()
        self.assertEqual(100, hits[0])

    def test_blocking(self):
        l = eventlet.listen(('localhost', 0))
        x = eventlet.with_timeout(
            0.01,
            eventlet.serve, l, lambda c, a: None,
            timeout_value="timeout")
        self.assertEqual(x, "timeout")

    def test_raising_stopserve(self):
        def stopit(conn, addr):
            raise eventlet.StopServe()
        l = eventlet.listen(('localhost', 0))
        # connect to trigger a call to stopit
        gt = eventlet.spawn(eventlet.connect, ('localhost', l.getsockname()[1]))
        eventlet.serve(l, stopit)
        gt.wait()

    def test_concurrency(self):
        evt = eventlet.Event()

        def waiter(sock, addr):
            sock.sendall(b'hi')
            evt.wait()
        l = eventlet.listen(('localhost', 0))
        eventlet.spawn(eventlet.serve, l, waiter, 5)

        def test_client():
            c = eventlet.connect(('localhost', l.getsockname()[1]))
            # verify the client is connected by getting data
            self.assertEqual(b'hi', c.recv(2))
            return c
        [test_client() for i in range(5)]
        # very next client should not get anything
        x = eventlet.with_timeout(
            0.01,
            test_client,
            timeout_value="timed out")
        self.assertEqual(x, "timed out")

    @tests.skip_if_no_ssl
    def test_wrap_ssl(self):
        server = eventlet.wrap_ssl(
            eventlet.listen(('localhost', 0)),
            certfile=certificate_file, keyfile=private_key_file,
            server_side=True)
        port = server.getsockname()[1]

        def handle(sock, addr):
            sock.sendall(sock.recv(1024))
            raise eventlet.StopServe()

        eventlet.spawn(eventlet.serve, server, handle)
        client = eventlet.wrap_ssl(eventlet.connect(('localhost', port)))
        client.sendall(b"echo")
        self.assertEqual(b"echo", client.recv(1024))


def test_socket_reuse():
    # pick a free port with bind to 0 - without SO_REUSEPORT
    # then close it and try to bind to same port with SO_REUSEPORT
    # loop helps in case something else used the chosen port before second bind
    addr = None
    errors = []
    for _ in range(5):
        lsock1 = eventlet.listen(('localhost', 0))
        addr = lsock1.getsockname()
        lsock1.close()
        try:
            lsock1 = eventlet.listen(addr)
        except socket.error as e:
            errors.append(e)
            continue
        break
    else:
        assert False, errors

    if hasattr(socket, 'SO_REUSEPORT'):
        lsock2 = eventlet.listen(addr)
    else:
        try:
            lsock2 = eventlet.listen(addr)
            assert lsock2
            lsock2.close()
        except socket.error:
            pass

    lsock1.close()


def test_reuse_random_port_warning():
    with warnings.catch_warnings(record=True) as w:
        eventlet.listen(('localhost', 0), reuse_port=True).close()
        assert len(w) == 1
        assert issubclass(w[0].category, convenience.ReuseRandomPortWarning)


@tests.skip_unless(hasattr(socket, 'SO_REUSEPORT'))
def test_reuseport_oserror():
    # https://github.com/eventlet/eventlet/issues/380
    # https://github.com/eventlet/eventlet/issues/418
    err22 = OSError(22, 'Invalid argument')

    sock1 = eventlet.listen(('localhost', 0))
    addr = sock1.getsockname()
    sock1.close()

    original_socket_init = socket.socket.__init__

    def patched(self, *a, **kw):
        original_socket_init(self, *a, **kw)
        self.setsockopt = tests.mock.Mock(side_effect=err22)

    with warnings.catch_warnings(record=True) as w:
        try:
            socket.socket.__init__ = patched
            eventlet.listen(addr, reuse_addr=False, reuse_port=True).close()
        finally:
            socket.socket.__init__ = original_socket_init
        assert len(w) == 1
        assert issubclass(w[0].category, convenience.ReusePortUnavailableWarning)
