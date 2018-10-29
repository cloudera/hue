import array
import os
import shutil
import sys
import tempfile
import eventlet
from eventlet.green import socket
from eventlet.support import greendns
import tests


def test_create_connection_error():
    try:
        socket.create_connection(('192.0.2.1', 80), timeout=0.1)
    except (IOError, OSError):
        pass


def test_recv_type():
    # https://github.com/eventlet/eventlet/issues/245
    # socket recv returning multiple data types
    # For this test to work, client and server have to be in separate
    # processes or OS threads. Just running two greenthreads gives
    # false test pass.
    threading = eventlet.patcher.original('threading')
    addr = []

    def server():
        sock = eventlet.listen(('127.0.0.1', 0))
        addr[:] = sock.getsockname()
        eventlet.sleep(0.2)

    server_thread = threading.Thread(target=server)
    server_thread.start()
    eventlet.sleep(0.1)
    sock = eventlet.connect(tuple(addr))
    s = sock.recv(1)
    assert isinstance(s, bytes)


def test_recv_into_type():
    # make sure `_recv_loop` returns the correct value when `recv_meth` is of
    # foo_into type (fills a buffer and returns number of bytes, not the data)
    # Using threads like `test_recv_type` above.
    threading = eventlet.patcher.original('threading')
    addr = []

    def server():
        sock = eventlet.listen(('127.0.0.1', 0))
        addr[:] = sock.getsockname()
        eventlet.sleep(0.2)

    server_thread = threading.Thread(target=server)
    server_thread.start()
    eventlet.sleep(0.1)
    sock = eventlet.connect(tuple(addr))
    buf = array.array('B', b' ')
    res = sock.recv_into(buf, 1)
    assert isinstance(res, int)


def test_dns_methods_are_green():
    assert socket.gethostbyname is greendns.gethostbyname
    assert socket.gethostbyname_ex is greendns.gethostbyname_ex
    assert socket.getaddrinfo is greendns.getaddrinfo
    assert socket.getnameinfo is greendns.getnameinfo

    # https://github.com/eventlet/eventlet/pull/341
    # mock older dnspython in system packages
    mock_sys_pkg_dir = tempfile.mkdtemp('eventlet_test_dns_methods_are_green')
    try:
        with open(mock_sys_pkg_dir + '/dns.py', 'wb') as f:
            f.write(b'raise Exception("Your IP address string is so illegal ' +
                    b'it prevents installing packages.")\n')
        tests.run_isolated('socket_resolve_green.py', pythonpath_extend=[mock_sys_pkg_dir])
    finally:
        shutil.rmtree(mock_sys_pkg_dir)


def test_socket_api_family():
    # It was named family_or_realsock
    # https://github.com/eventlet/eventlet/issues/319
    socket.socket(family=socket.AF_INET)


def test_getaddrinfo_ipv6_scope():
    greendns.is_ipv6_addr('::1%2')
    if not socket.has_ipv6:
        return
    socket.getaddrinfo('::1%2', 80, socket.AF_INET6)


def test_error_is_timeout():
    s1, _ = socket.socketpair()
    s1.settimeout(0.01)
    try:
        s1.recv(1)
    except socket.error as e:
        tests.check_is_timeout(e)
    else:
        assert False, 'No timeout, socket.error was not raised'
