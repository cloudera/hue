"""This test checks that socket instances (not GreenSockets but underlying sockets)
are not leaked by the hub.
"""
import gc
import pprint
import sys
import weakref

import eventlet
from eventlet.green import socket


SOCKET_TIMEOUT = 0.1


def handle_request(s, raise_on_timeout):
    try:
        conn, address = s.accept()
    except socket.timeout:
        print('handle_request: server accept timeout')
        if raise_on_timeout:
            raise
        else:
            return
    print('handle_request: accepted')
    res = conn.recv(100)
    assert res == b'hello', repr(res)
    # print('handle_request: recvd %r' % res)
    res = conn.sendall(b'bye')
    # print('handle_request: sent %r' % res)
    # print('handle_request: conn refcount: %s' % sys.getrefcount(conn))


def make_request(addr):
    # print('make_request')
    s = eventlet.connect(addr)
    # print('make_request - connected')
    res = s.sendall(b'hello')
    # print('make_request - sent %s' % res)
    res = s.recv(100)
    assert res == b'bye', repr(res)
    # print('make_request - recvd %r' % res)


def run_interaction(run_client):
    s = eventlet.listen(('127.0.0.1', 0))
    s.settimeout(SOCKET_TIMEOUT)
    addr = s.getsockname()
    print('run_interaction: addr:', addr)
    eventlet.spawn(handle_request, s, run_client)
    if run_client:
        eventlet.spawn(make_request, addr)
    eventlet.sleep(0.1 + SOCKET_TIMEOUT)
    print('run_interaction: refcount(s.fd)', sys.getrefcount(s.fd))
    return weakref.ref(s.fd)


def run_and_check(run_client):
    w = run_interaction(run_client=run_client)
    # clear_sys_exc_info()
    gc.collect()
    fd = w()
    print('run_and_check: weakref fd:', fd)
    if fd:
        print(pprint.pformat(gc.get_referrers(fd)))
        for x in gc.get_referrers(fd):
            print(pprint.pformat(x))
            for y in gc.get_referrers(x):
                print('- {0}'.format(pprint.pformat(y)))
        raise AssertionError('server should be dead by now')


def test_clean_exit():
    run_and_check(True)
    run_and_check(True)


def test_timeout_exit():
    run_and_check(False)
    run_and_check(False)
