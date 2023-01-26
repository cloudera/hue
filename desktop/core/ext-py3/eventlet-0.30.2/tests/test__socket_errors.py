import errno
import unittest
import socket as _original_sock
from eventlet.green import socket


class TestSocketErrors(unittest.TestCase):
    def test_connection_refused(self):
        # open and close a dummy server to find an unused port
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 0))
        server.listen(1)
        port = server.getsockname()[1]
        server.close()
        del server
        s = socket.socket()
        try:
            s.connect(('127.0.0.1', port))
            self.fail("Shouldn't have connected")
        except socket.error as ex:
            code, text = ex.args
            assert code == errno.ECONNREFUSED, 'Expected ECONNREFUSED, got {0} ({1})'.format(code, text)
            assert 'refused' in text.lower(), (code, text)

    def test_timeout_real_socket(self):
        """ Test underlying socket behavior to ensure correspondence
            between green sockets and the underlying socket module. """
        return self.test_timeout(socket=_original_sock)

    def test_timeout(self, socket=socket):
        """ Test that the socket timeout exception works correctly. """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 0))
        server.listen(1)
        port = server.getsockname()[1]

        s = socket.socket()

        s.connect(('127.0.0.1', port))

        cs, addr = server.accept()
        cs.settimeout(1)
        try:
            try:
                cs.recv(1024)
                self.fail("Should have timed out")
            except socket.timeout as ex:
                assert hasattr(ex, 'args')
                assert len(ex.args) == 1
                assert ex.args[0] == 'timed out'
        finally:
            s.close()
            cs.close()
            server.close()


def test_create_connection_refused():
    try:
        socket.create_connection(('127.0.0.1', 1))
        assert False, "Shouldn't have connected"
    except socket.error as ex:
        code, text = ex.args
        assert code == errno.ECONNREFUSED, 'Expected ECONNREFUSED, got {0} ({1})'.format(code, text)
