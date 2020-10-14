# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
import multiprocessing
import time

from os import path
from unittest import TestCase

import thriftpy2
from thriftpy2.rpc import client_context, make_server
from thriftpy2.transport.buffered import TBufferedTransportFactory
from thriftpy2.protocol.binary import TBinaryProtocolFactory

from thriftpy2._compat import CYTHON
logging.basicConfig(level=logging.INFO)

addressbook = thriftpy2.load(path.join(path.dirname(__file__),
                                       "addressbook.thrift"))


class Dispatcher(object):
    def __init__(self):
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


class BufferedTransportTestCase(TestCase):
    TRANSPORT_FACTORY = TBufferedTransportFactory()
    PROTOCOL_FACTORY = TBinaryProtocolFactory()

    PORT = 50001

    def mk_server(self):
        server = make_server(addressbook.AddressBookService, Dispatcher(),
                             host="localhost", port=self.PORT,
                             proto_factory=self.PROTOCOL_FACTORY,
                             trans_factory=self.TRANSPORT_FACTORY)
        p = multiprocessing.Process(target=server.serve)
        return p

    def client(self):
        return client_context(addressbook.AddressBookService,
                              host="localhost", port=self.PORT,
                              proto_factory=self.PROTOCOL_FACTORY,
                              trans_factory=self.TRANSPORT_FACTORY)

    def setUp(self):
        self.server = self.mk_server()
        self.server.start()
        time.sleep(0.1)

    def tearDown(self):
        if self.server.is_alive():
            self.server.terminate()

    def test_able_to_communicate(self):
        dennis = addressbook.Person(name='Dennis Ritchie')
        with self.client() as c:
            success = c.add(dennis)
            assert success

            success = c.add(dennis)
            assert not success

    def test_zero_length_string(self):
        dennis = addressbook.Person(name='')
        with self.client() as c:
            success = c.add(dennis)
            assert success
            success = c.get(name='')
            assert success


if CYTHON:
    from thriftpy2.transport.buffered import TCyBufferedTransportFactory
    from thriftpy2.protocol.cybin import TCyBinaryProtocolFactory

    class TCyBufferedTransportTestCase(BufferedTransportTestCase):
        TRANSPORT_FACTORY = TCyBufferedTransportFactory()
        PROTOCOL_FACTORY = TCyBinaryProtocolFactory()
