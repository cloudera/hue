"""Issue #143 - Socket timeouts in wsgi server not caught.
https://bitbucket.org/eventlet/eventlet/issue/143/

This file intentionally ignored by nose.
Caller process (tests.wsgi_test.TestWsgiConnTimeout) handles success / failure


Simulate server connection socket timeout without actually waiting.
Logs 'timed out' if server debug=True (similar to 'accepted' logging)

FAIL: if log (ie, _spawn_n_impl 'except:' catches timeout, logs TB)
NOTE: timeouts are NOT on server_sock, but on the conn sockets produced
by the socket.accept() call

server's socket.listen() sock - NaughtySocketAcceptWrap
    /  |  \
    |  |  |   (1 - many)
    V  V  V
server / client accept() conn - ExplodingConnectionWrap
    /  |  \
    |  |  |   (1 - many)
    V  V  V
connection makefile() file objects - ExplodingSocketFile <-- these raise
"""
import socket

import eventlet
from eventlet.support import six
import tests.wsgi_test


# no standard tests in this file, ignore
__test__ = False


TAG_BOOM = "=== ~* BOOM *~ ==="

output_buffer = []


class BufferLog(object):
    @staticmethod
    def write(s):
        output_buffer.append(s.rstrip())
        return len(s)


# This test might make you wince
class NaughtySocketAcceptWrap(object):
    # server's socket.accept(); patches resulting connection sockets

    def __init__(self, sock):
        self.sock = sock
        self.sock._really_accept = self.sock.accept
        self.sock.accept = self
        self.conn_reg = []

    def unwrap(self):
        self.sock.accept = self.sock._really_accept
        del self.sock._really_accept
        for conn_wrap in self.conn_reg:
            conn_wrap.unwrap()

    def arm(self):
        output_buffer.append("ca-click")
        for i in self.conn_reg:
            i.arm()

    def __call__(self):
        output_buffer.append(self.__class__.__name__ + ".__call__")
        conn, addr = self.sock._really_accept()
        self.conn_reg.append(ExplodingConnectionWrap(conn))
        return conn, addr


class ExplodingConnectionWrap(object):
    # new connection's socket.makefile
    # eventlet *tends* to use socket.makefile, not raw socket methods.
    # need to patch file operations

    def __init__(self, conn):
        self.conn = conn
        self.conn._really_makefile = self.conn.makefile
        self.conn.makefile = self
        self.armed = False
        self.file_reg = []

    def unwrap(self):
        self.conn.makefile = self.conn._really_makefile
        del self.conn._really_makefile

    def arm(self):
        output_buffer.append("tick")
        for i in self.file_reg:
            i.arm()

    def __call__(self, mode='r', bufsize=-1):
        output_buffer.append(self.__class__.__name__ + ".__call__")
        # file_obj = self.conn._really_makefile(*args, **kwargs)
        file_obj = ExplodingSocketFile(self.conn._sock, mode, bufsize)
        self.file_reg.append(file_obj)
        return file_obj


class ExplodingSocketFile(eventlet.greenio._fileobject):

    def __init__(self, sock, mode='rb', bufsize=-1, close=False):
        args = [bufsize, close] if six.PY2 else []
        super(self.__class__, self).__init__(sock, mode, *args)
        self.armed = False

    def arm(self):
        output_buffer.append("beep")
        self.armed = True

    def _fuse(self):
        if self.armed:
            output_buffer.append(TAG_BOOM)
            raise socket.timeout("timed out")

    def readline(self, *args, **kwargs):
        output_buffer.append(self.__class__.__name__ + ".readline")
        self._fuse()
        return super(self.__class__, self).readline(*args, **kwargs)


def step(debug):
    output_buffer[:] = []

    server_sock = eventlet.listen(('localhost', 0))
    server_addr = server_sock.getsockname()
    sock_wrap = NaughtySocketAcceptWrap(server_sock)

    eventlet.spawn_n(
        eventlet.wsgi.server,
        debug=debug,
        log=BufferLog,
        max_size=128,
        site=tests.wsgi_test.Site(),
        sock=server_sock,
    )

    try:
        # req #1 - normal
        sock1 = eventlet.connect(server_addr)
        sock1.settimeout(0.1)
        fd1 = sock1.makefile('rwb')
        fd1.write(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        fd1.flush()
        tests.wsgi_test.read_http(sock1)

        # let the server socket ops catch up, set bomb
        eventlet.sleep(0)
        output_buffer.append("arming...")
        sock_wrap.arm()

        # req #2 - old conn, post-arm - timeout
        fd1.write(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
        fd1.flush()
        try:
            tests.wsgi_test.read_http(sock1)
            assert False, 'Expected ConnectionClosed exception'
        except tests.wsgi_test.ConnectionClosed:
            pass

        fd1.close()
        sock1.close()
    finally:
        # reset streams, then output trapped tracebacks
        sock_wrap.unwrap()
    # check output asserts in tests.wsgi_test.TestHttpd
    # test_143_server_connection_timeout_exception

    return output_buffer[:]


def main():
    output_normal = step(debug=False)
    output_debug = step(debug=True)

    assert "timed out" in output_debug[-1], repr(output_debug)
    # if the BOOM check fails, it's because our timeout didn't happen
    # (if eventlet stops using file.readline() to read HTTP headers,
    # for instance)
    assert TAG_BOOM == output_debug[-2], repr(output_debug)
    assert TAG_BOOM == output_normal[-1], repr(output_normal)
    assert "Traceback" not in output_debug, repr(output_debug)
    assert "Traceback" not in output_normal, repr(output_normal)
    print("pass")

if __name__ == '__main__':
    main()
