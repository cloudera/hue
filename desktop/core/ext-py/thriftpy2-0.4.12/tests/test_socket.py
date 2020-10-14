# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import os
import socket
import sys

import pytest

from thriftpy2.transport import TTransportException
from thriftpy2.transport.socket import TSocket, TServerSocket


def _test_socket(server_socket, client_socket):
    server_socket.listen()
    client_socket.open()

    conn = server_socket.accept()

    buff = b"Hello World!"
    client_socket.write(buff)
    buff2 = conn.read(1024)
    conn.write(buff2)

    buff3 = client_socket.read(1024)

    assert buff == buff2 == buff3

    conn.close()
    client_socket.close()
    server_socket.close()


def test_inet_socket():
    server_socket = TServerSocket(host="127.0.0.1", port=12345)
    client_socket = TSocket(host="127.0.0.1", port=12345)

    _test_socket(server_socket, client_socket)


@pytest.mark.skipif(os.getenv('TRAVIS', '') == 'true',
                    reason='Travis CI dose not support IPv6')
def test_inet6_socket():
    server_socket = TServerSocket(host="::1", port=12345,
                                  socket_family=socket.AF_INET6)
    client_socket = TSocket(host="::1", port=12345,
                            socket_family=socket.AF_INET6)

    _test_socket(server_socket, client_socket)


@pytest.mark.skipif(
    sys.platform == 'darwin' and os.getuid() != 0,
    reason='os.mknod() requires super-user privileges on darwin')
def test_unix_domain_socket():
    sock_file = "/tmp/thriftpy_test.sock"

    # if socket file already exists, it will be removed
    if os.path.exists(sock_file):
        os.unlink(sock_file)
    os.mknod(sock_file)

    server_socket = TServerSocket(unix_socket=sock_file)
    client_socket = TSocket(unix_socket=sock_file)

    _test_socket(server_socket, client_socket)


def test_client_socket_timeout():
    server_socket = TServerSocket(host="localhost", port=12345,
                                  client_timeout=100)
    server_socket.listen()

    client_socket = TSocket(host="localhost", port=12345,
                            connect_timeout=10, socket_timeout=100)
    client_socket.open()

    conn = server_socket.accept()

    assert client_socket.sock.gettimeout() == 100 / 1000
    assert conn.sock.gettimeout() == 100 / 1000
    assert server_socket.sock.gettimeout() is None

    conn.close()
    client_socket.close()
    server_socket.close()


def test_client_socket_open():
    client_socket = TSocket(host="localhost", port=12345)
    with pytest.raises(TTransportException) as e:
        client_socket.open()
    assert e.value.message == "Could not connect to ('localhost', 12345)"
    assert not client_socket.is_open()

    server_socket = TServerSocket(host="localhost", port=12345)
    server_socket.listen()

    client_socket.open()
    assert client_socket.is_open()

    server_socket.close()
    client_socket.close()


def test_client_socket_close():
    server_socket = TServerSocket(host="localhost", port=12345)
    server_socket.listen()

    client_socket = TSocket(host="localhost", port=12345)
    client_socket.open()

    conn = server_socket.accept()
    client_socket.close()
    assert not client_socket.is_open()

    with pytest.raises(TTransportException) as e:
        conn.read(1024)
    assert "TSocket read 0 bytes" in e.value.message

    conn.write(b"world")

    conn.close()
    server_socket.close()


def test_server_socket_close():
    server_socket = TServerSocket(host="localhost", port=12345)
    server_socket.listen()

    client_socket = TSocket(host="localhost", port=12345, socket_timeout=100)
    client_socket.open()

    conn = server_socket.accept()
    server_socket.close()

    client_socket.write(b"Hello world")
    with pytest.raises(socket.timeout):
        client_socket.read(1024)

    conn.close()
    server_socket.close()


def test_client_socket_set_timeout():
    server_socket = TServerSocket(host="localhost", port=12345,
                                  client_timeout=100)
    server_socket.listen()

    client_socket = TSocket(host="localhost", port=12345, socket_timeout=100)
    client_socket.open()

    conn = server_socket.accept()

    assert client_socket.sock.gettimeout() == 100 / 1000
    assert conn.sock.gettimeout() == 100 / 1000
    assert conn.sock.gettimeout() == 100 / 1000

    client_socket.set_timeout(200)
    conn.set_timeout(200)
    assert client_socket.sock.gettimeout() == 200 / 1000
    assert conn.sock.gettimeout() == 200 / 1000

    conn.close()
    client_socket.close()
    server_socket.close()
