# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys
import logging
import socket
import threading
import time

from os import path
from unittest import TestCase

import pytest
from tornado import ioloop

import thriftpy2
from thriftpy2.tornado import make_server
from thriftpy2.rpc import make_client
from thriftpy2.transport.framed import TFramedTransportFactory
from thriftpy2.protocol.binary import TBinaryProtocolFactory

try:
    import asyncio
except ImportError:
    asyncio = None

from thriftpy2._compat import CYTHON
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
        Person get(1: string name)
        """
        if name not in self.registry:
            raise addressbook.PersonNotExistsError()
        return self.registry[name]


class FramedTransportTestCase(TestCase):
    TRANSPORT_FACTORY = TFramedTransportFactory()
    PROTOCOL_FACTORY = TBinaryProtocolFactory()

    def mk_server(self):
        sock = self.server_sock = socket.socket(socket.AF_INET,
                                                socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 0))
        sock.setblocking(0)
        self.port = sock.getsockname()[-1]
        self.server_thread = threading.Thread(target=self.listen)
        self.server_thread.setDaemon(True)
        self.server_thread.start()

    def listen(self):
        self.server_sock.listen(128)
        if asyncio:
            # In Tornado 5.0+, the asyncio event loop will be used
            # automatically by default
            asyncio.set_event_loop(asyncio.new_event_loop())
        self.io_loop = ioloop.IOLoop.current()
        server = make_server(addressbook.AddressBookService,
                             Dispatcher(self.io_loop), io_loop=self.io_loop)
        server.add_socket(self.server_sock)
        self.io_loop.start()

    def mk_client(self):
        return make_client(addressbook.AddressBookService,
                           '127.0.0.1', self.port,
                           proto_factory=self.PROTOCOL_FACTORY,
                           trans_factory=self.TRANSPORT_FACTORY)

    def mk_client_with_url(self):
        return make_client(addressbook.AddressBookService,
                           proto_factory=self.PROTOCOL_FACTORY,
                           trans_factory=self.TRANSPORT_FACTORY,
                           url='thrift://127.0.0.1:{port}'.format(
                               port=self.port))

    def setUp(self):
        self.mk_server()
        time.sleep(0.1)
        self.client = self.mk_client()
        self.client_created_using_url = self.mk_client_with_url()

    def tearDown(self):
        self.io_loop.stop()

    @pytest.mark.skipif(sys.version_info[:2] == (2, 6), reason="not support")
    def test_make_client(self):
        linus = addressbook.Person('Linus Torvalds')
        success = self.client_created_using_url.add(linus)
        assert success
        success = self.client.add(linus)
        assert not success

    @pytest.mark.skipif(sys.version_info[:2] == (2, 6), reason="not support")
    def test_able_to_communicate(self):
        dennis = addressbook.Person(name='Dennis Ritchie')
        success = self.client.add(dennis)
        assert success
        success = self.client.add(dennis)
        assert not success

    @pytest.mark.skipif(sys.version_info[:2] == (2, 6), reason="not support")
    def test_zero_length_string(self):
        dennis = addressbook.Person(name='')
        success = self.client.add(dennis)
        assert success
        success = self.client.get(name='')
        assert success


if CYTHON:
    from thriftpy2.transport.framed import TCyFramedTransportFactory
    from thriftpy2.protocol.cybin import TCyBinaryProtocolFactory

    class CyFramedTransportTestCase(FramedTransportTestCase):
        PROTOCOL_FACTORY = TCyBinaryProtocolFactory()
        TRANSPORT_FACTORY = TCyFramedTransportFactory()
