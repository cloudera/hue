# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import multiprocessing
import socket
import time
import ssl

import pytest

import thriftpy2

thriftpy2.install_import_hook()

from thriftpy2._compat import PY3  # noqa
from thriftpy2.rpc import make_server, client_context  # noqa
from thriftpy2.transport import TTransportException  # noqa
from thriftpy2.thrift import TApplicationException  # noqa


addressbook = thriftpy2.load(os.path.join(os.path.dirname(__file__),
                                          "addressbook.thrift"))
unix_sock = "/tmp/thriftpy_test.sock"
SSL_PORT = 50441


class Dispatcher(object):
    def __init__(self):
        self.ab = addressbook.AddressBook()
        self.ab.people = {}

    def ping(self):
        return True

    def hello(self, name):
        return "hello " + name

    def add(self, person):
        self.ab.people[person.name] = person
        return True

    def remove(self, name):
        try:
            self.ab.people.pop(name)
            return True
        except KeyError:
            raise addressbook.PersonNotExistsError(
                "{} not exists".format(name))

    def get(self, name):
        try:
            return self.ab.people[name]
        except KeyError:
            raise addressbook.PersonNotExistsError(
                "{} not exists".format(name))

    def book(self):
        return self.ab

    def get_phonenumbers(self, name, count):
        p = [self.ab.people[name].phones[0]] if name in self.ab.people else []
        return p * count

    def get_phones(self, name):
        phone_numbers = self.ab.people[name].phones
        return dict((p.type, p.number) for p in phone_numbers)

    def sleep(self, ms):
        time.sleep(ms / 1000.0)
        return True

    def close(self, ms):
        return


@pytest.fixture(scope="module")
def server(request):
    server = make_server(addressbook.AddressBookService, Dispatcher(),
                         unix_socket=unix_sock)
    ps = multiprocessing.Process(target=server.serve)
    ps.start()

    time.sleep(0.1)

    def fin():
        if ps.is_alive():
            ps.terminate()
        try:
            os.remove(unix_sock)
        except IOError:
            pass

    request.addfinalizer(fin)


@pytest.fixture(scope="module")
def ssl_server(request):
    ssl_server = make_server(addressbook.AddressBookService, Dispatcher(),
                             host='localhost', port=SSL_PORT,
                             certfile="ssl/server.pem")
    ps = multiprocessing.Process(target=ssl_server.serve)
    ps.start()

    time.sleep(0.1)

    def fin():
        if ps.is_alive():
            ps.terminate()
    request.addfinalizer(fin)


@pytest.fixture(scope="module")
def person():
    phone1 = addressbook.PhoneNumber()
    phone1.type = addressbook.PhoneType.MOBILE
    phone1.number = '555-1212'
    phone2 = addressbook.PhoneNumber()
    phone2.type = addressbook.PhoneType.HOME
    phone2.number = '555-1234'

    # empty struct
    phone3 = addressbook.PhoneNumber()

    alice = addressbook.Person()
    alice.name = "Alice"
    alice.phones = [phone1, phone2, phone3]
    alice.created_at = int(time.time())

    return alice


def client(timeout=3000):
    return client_context(addressbook.AddressBookService,
                          unix_socket=unix_sock, timeout=timeout)


def ssl_client(timeout=3000):
    return client_context(addressbook.AddressBookService,
                          host='localhost', port=SSL_PORT,
                          timeout=timeout,
                          cafile="ssl/CA.pem", certfile="ssl/client.crt",
                          keyfile="ssl/client.key")


def ssl_client_with_url(timeout=3000):
    return client_context(addressbook.AddressBookService,
                          url="thrift://localhost:{port}".format(
                              port=SSL_PORT),
                          timeout=timeout, cafile="ssl/CA.pem",
                          certfile="ssl/client.crt", keyfile="ssl/client.key")


def test_clients(ssl_server):
    with ssl_client() as c1, ssl_client_with_url() as c2:
        assert c1.hello("world") == c2.hello("world")


def test_void_api(server):
    with client() as c:
        assert c.ping() is None


def test_void_api_with_ssl(ssl_server):
    with ssl_client() as c:
        assert c.ping() is None


def test_string_api(server):
    with client() as c:
        assert c.hello("world") == "hello world"


def test_required_argument(server):
    with client() as c:
        assert c.hello("") == "hello "
        with pytest.raises(TApplicationException):
            c.hello()


def test_string_api_with_ssl(ssl_server):
    with ssl_client() as c:
        assert c.hello("world") == "hello world"


def test_huge_res(server):
    with client() as c:
        big_str = "world" * 100000
        assert c.hello(big_str) == "hello " + big_str


def test_huge_res_with_ssl(ssl_server):
    with ssl_client() as c:
        big_str = "world" * 100000
        assert c.hello(big_str) == "hello " + big_str


def test_tstruct_req(person):
    with client() as c:
        assert c.add(person) is True


def test_tstruct_req_with_ssl(person):
    with ssl_client() as c:
        assert c.add(person) is True


def test_tstruct_res(person):
    with client() as c:
        assert person == c.get("Alice")


def test_tstruct_res_with_ssl(person):
    with ssl_client() as c:
        assert person == c.get("Alice")


def test_complex_tstruct():
    with client() as c:
        assert len(c.get_phonenumbers("Alice", 0)) == 0
        assert len(c.get_phonenumbers("Alice", 1000)) == 1000


def test_complex_tstruct_with_ssl():
    with ssl_client() as c:
        assert len(c.get_phonenumbers("Alice", 0)) == 0
        assert len(c.get_phonenumbers("Alice", 1000)) == 1000


def test_exception():
    with pytest.raises(addressbook.PersonNotExistsError):
        with client() as c:
            c.remove("Bob")


def test_exception_iwth_ssl():
    with pytest.raises(addressbook.PersonNotExistsError):
        with ssl_client() as c:
            c.remove("Bob")


def test_client_timeout():
    with pytest.raises(socket.timeout):
        with client(timeout=500) as c:
            c.sleep(1000)


def test_client_socket_timeout():
    with pytest.raises(socket.timeout):
        with client_context(addressbook.AddressBookService,
                            unix_socket=unix_sock,
                            socket_timeout=500) as c:
            c.sleep(1000)


def test_client_connect_timeout():
    with pytest.raises(TTransportException):
        with client_context(addressbook.AddressBookService,
                            unix_socket='/tmp/test.sock',
                            connect_timeout=1000) as c:
            c.hello('test')


def test_ssl_client_timeout():
    # SSL socket timeout raises socket.timeout since Python 3.2.
    # http://bugs.python.org/issue10272
    with pytest.raises(socket.timeout if PY3 else ssl.SSLError):
        with ssl_client(timeout=500) as c:
            c.sleep(1000)


def test_close_method():
    with client() as c:
        c.tclose(1)
