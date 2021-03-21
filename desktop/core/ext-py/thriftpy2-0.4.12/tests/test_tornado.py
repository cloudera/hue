# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys
from os import path
import logging
import socket

import pytest
from tornado import gen, testing

import thriftpy2
from thriftpy2.tornado import make_client
from thriftpy2.tornado import make_server
from thriftpy2.transport import TTransportException


logging.basicConfig(level=logging.INFO)

addressbook = thriftpy2.load(path.join(path.dirname(__file__),
                                       "addressbook.thrift"))


class Dispatcher(object):
    def __init__(self, io_loop):
        self.io_loop = io_loop
        self.registry = {}

    def add(self, person):
        """
        bool add(1: Person person);
        """
        if person.name in self.registry:
            return False
        self.registry[person.name] = person
        return True

    def get(self, name):
        """
        Person get(1: string name) throws (1: PersonNotExistsError not_exists);
        """
        if not name:
            # undeclared exception
            raise ValueError('name cannot be empty')
        if name not in self.registry:
            raise addressbook.PersonNotExistsError(
                'Person "{}" does not exist!'.format(name))
        return self.registry[name]

    @gen.coroutine
    def remove(self, name):
        """
        bool remove(1: string name) throws (1: PersonNotExistsError not_exists)
        """
        # delay action for later
        yield gen.Task(self.io_loop.add_callback)
        if not name:
            # undeclared exception
            raise ValueError('name cannot be empty')
        if name not in self.registry:
            raise addressbook.PersonNotExistsError(
                'Person "{}" does not exist!'.format(name))
        del self.registry[name]
        raise gen.Return(True)


class TornadoRPCTestCase(testing.AsyncTestCase):
    def mk_server(self):
        server = make_server(addressbook.AddressBookService,
                             Dispatcher(self.io_loop),
                             io_loop=self.io_loop)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))
        sock.setblocking(0)
        sock.listen(128)

        server.add_socket(sock)
        self.port = sock.getsockname()[-1]
        return server

    def mk_client(self):
        return make_client(addressbook.AddressBookService,
                           '127.0.0.1', self.port, io_loop=self.io_loop)

    def mk_client_with_url(self):
        return make_client(addressbook.AddressBookService,
                           io_loop=self.io_loop,
                           url='thrift://127.0.0.1:{port}'.format(
                               port=self.port))

    def setUp(self):
        super(TornadoRPCTestCase, self).setUp()
        self.server = self.mk_server()
        self.client = self.io_loop.run_sync(self.mk_client)
        self.client_with_url = self.io_loop.run_sync(self.mk_client_with_url)

    def tearDown(self):
        self.server.stop()
        self.client.close()
        self.client_with_url.close()
        super(TornadoRPCTestCase, self).tearDown()

    @testing.gen_test
    @pytest.mark.skipif(sys.version_info[:2] == (2, 6), reason="not support")
    def test_make_client(self):
        linus = addressbook.Person(name='Linus Torvalds')
        success = yield self.client_with_url.add(linus)
        assert success
        success = yield self.client.add(linus)
        assert not success

    @testing.gen_test
    @pytest.mark.skipif(sys.version_info[:2] == (2, 6), reason="not support")
    def test_synchronous_result(self):
        dennis = addressbook.Person(name='Dennis Ritchie')
        success = yield self.client.add(dennis)
        assert success
        success = yield self.client.add(dennis)
        assert not success
        person = yield self.client.get(dennis.name)
        assert person.name == dennis.name

    @testing.gen_test
    @pytest.mark.skipif(sys.version_info[:2] == (2, 6), reason="not support")
    def test_synchronous_exception(self):
        exc = None
        try:
            yield self.client.get('Brian Kernighan')
        except Exception as e:
            exc = e

        assert isinstance(exc, addressbook.PersonNotExistsError)

    @testing.gen_test
    @pytest.mark.skipif(sys.version_info[:2] == (2, 6), reason="not support")
    def test_synchronous_undeclared_exception(self):
        exc = None
        try:
            yield self.client.get('')
        except Exception as e:
            exc = e

        assert isinstance(exc, TTransportException)

    @testing.gen_test
    @pytest.mark.skipif(sys.version_info[:2] == (2, 6), reason="not support")
    def test_asynchronous_result(self):
        dennis = addressbook.Person(name='Dennis Ritchie')
        yield self.client.add(dennis)
        success = yield self.client.remove(dennis.name)
        assert success

    @testing.gen_test
    @pytest.mark.skipif(sys.version_info[:2] == (2, 6), reason="not support")
    def test_asynchronous_exception(self):
        exc = None
        try:
            yield self.client.remove('Brian Kernighan')
        except Exception as e:
            exc = e
        assert isinstance(exc, addressbook.PersonNotExistsError)

    @testing.gen_test
    @pytest.mark.skipif(sys.version_info[:2] == (2, 6), reason="not support")
    def test_asynchronous_undeclared_exception(self):
        exc = None
        try:
            yield self.client.remove('')
        except Exception as e:
            exc = e
        assert isinstance(exc, TTransportException)
