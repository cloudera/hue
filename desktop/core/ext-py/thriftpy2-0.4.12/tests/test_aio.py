# -*- coding: utf-8 -*-
import os
import asyncio
# import uvloop
import threading
import random
from unittest.mock import patch

# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

import time

import pytest

import thriftpy2

from thriftpy2.contrib.aio.transport import (
    TAsyncBufferedTransportFactory,
    TAsyncFramedTransportFactory,
)
from thriftpy2.contrib.aio.protocol import (
    TAsyncBinaryProtocolFactory,
    TAsyncCompactProtocolFactory,
)
from thriftpy2.rpc import make_aio_server, make_aio_client
from thriftpy2.transport import TTransportException
from thriftpy2.thrift import TApplicationException

addressbook = thriftpy2.load(os.path.join(os.path.dirname(__file__),
                                          "addressbook.thrift"))


class Dispatcher:
    def __init__(self):
        self.ab = addressbook.AddressBook()
        self.ab.people = {}

    @asyncio.coroutine
    def ping(self):
        return True

    @asyncio.coroutine
    def hello(self, name):
        return "hello " + name

    @asyncio.coroutine
    def add(self, person):
        self.ab.people[person.name] = person
        return True

    @asyncio.coroutine
    def remove(self, name):
        if not name:
            # undeclared exception
            raise ValueError('name cannot be empty')
        try:
            self.ab.people.pop(name)
            return True
        except KeyError:
            raise addressbook.PersonNotExistsError(
                "{0} not exists".format(name))

    @asyncio.coroutine
    def get(self, name):
        try:
            return self.ab.people[name]
        except KeyError:
            raise addressbook.PersonNotExistsError(
                "{0} not exists".format(name))

    @asyncio.coroutine
    def book(self):
        return self.ab

    @asyncio.coroutine
    def get_phonenumbers(self, name, count):
        p = [self.ab.people[name].phones[0]] if name in self.ab.people else []
        return p * count

    @asyncio.coroutine
    def get_phones(self, name):
        phone_numbers = self.ab.people[name].phones
        return dict((p.type, p.number) for p in phone_numbers)

    @asyncio.coroutine
    def sleep(self, ms):
        yield from asyncio.sleep(ms / 1000.0)
        return True


def _create_person():
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


class _TestAIO:
    # Base test case for all async tests
    TRANSPORT_FACTORY = NotImplemented
    PROTOCOL_FACTORY = NotImplemented

    @classmethod
    def setup_class(cls):
        cls._start_server()
        cls.person = _create_person()

    @classmethod
    def teardown_class(cls):
        try:
            asyncio.get_event_loop().run_until_complete(cls.server.close())
        except:  # noqa Probably already closed earlier
            pass
        del cls.server
        del cls.person

    @classmethod
    def _start_server(cls):
        cls.server = make_aio_server(
            addressbook.AddressBookService,
            Dispatcher(),
            trans_factory=cls.TRANSPORT_FACTORY,
            proto_factory=cls.PROTOCOL_FACTORY,
            loop=asyncio.new_event_loop(),
            **cls.server_kwargs(),
        )
        st = threading.Thread(target=cls.server.serve)
        st.daemon = True
        st.start()
        time.sleep(0.1)

    @classmethod
    def server_kwargs(cls):
        name = cls.__name__.lower()
        return {'unix_socket': '/tmp/aio_thriftpy_test_{}.sock'.format(name)}

    @classmethod
    def client_kwargs(cls):
        return cls.server_kwargs()

    async def client(self, timeout: int = 3000000):
        return await make_aio_client(
            addressbook.AddressBookService,
            trans_factory=self.TRANSPORT_FACTORY,
            proto_factory=self.PROTOCOL_FACTORY,
            timeout=timeout,
            **self.client_kwargs(),
        )

    @pytest.mark.asyncio
    async def test_void_api(self):
        c = await self.client()
        assert await c.ping() is None
        c.close()

    @pytest.mark.asyncio
    async def test_string_api(self):
        c = await self.client()
        assert await c.hello("world") == "hello world"
        c.close()

    @pytest.mark.asyncio
    async def test_required_argument(self):
        c = await self.client()
        assert await c.hello("") == "hello "

        with pytest.raises(TApplicationException):
            await c.hello()
        c.close()

    @pytest.mark.asyncio
    async def test_huge_res(self):
        c = await self.client()
        big_str = "world" * 100000
        assert await c.hello(big_str) == "hello " + big_str
        c.close()

    @pytest.mark.asyncio
    async def test_tstruct_req(self):
        c = await self.client()
        assert await c.add(self.person) is True
        c.close()

    @pytest.mark.asyncio
    async def test_tstruct_res(self):
        c = await self.client()
        assert self.person == await c.get("Alice")
        c.close()

    @pytest.mark.asyncio
    async def test_complex_tstruct(self):
        c = await self.client()
        assert len(await c.get_phonenumbers("Alice", 0)) == 0
        assert len(await c.get_phonenumbers("Alice", 1000)) == 1000
        c.close()

    @pytest.mark.asyncio
    async def test_exception(self):
        c = await self.client()
        with pytest.raises(addressbook.PersonNotExistsError):
            await c.remove("Bob")
        c.close()

    @pytest.mark.asyncio
    async def test_undeclared_exception(self):
        c = await self.client()
        with pytest.raises(TTransportException):
            await c.remove('')
        c.close()

    @pytest.mark.asyncio
    async def test_client_socket_timeout(self):
        c = await self.client(timeout=500)
        with pytest.raises(asyncio.TimeoutError):
            await c.sleep(1000)
        c.close()


class SSLServerMixin:

    @classmethod
    def setup_class(cls):
        cls.port = random.randint(55000, 56000)
        super().setup_class()

    @classmethod
    def server_kwargs(cls):
        return {
            'host': 'localhost',
            'port': cls.port,
            'certfile': "ssl/server.pem",
            'keyfile': "ssl/server.key",
        }

    @classmethod
    def client_kwargs(cls):
        kw = cls.server_kwargs()
        kw['cafile'] = "ssl/CA.pem"
        return kw

    async def client_with_url(self, timeout: int = 3000):
        kw = self.client_kwargs()
        kw['url'] = "thrift://{}:{}".format(kw.pop('host'), kw.pop('port'))
        return await make_aio_client(
            addressbook.AddressBookService,
            trans_factory=self.TRANSPORT_FACTORY,
            proto_factory=self.PROTOCOL_FACTORY,
            timeout=timeout,
            **kw,
        )

    @pytest.mark.asyncio
    async def test_clients(self):
        c1 = await self.client()
        c2 = await self.client_with_url()
        assert await c1.hello("world") == await c2.hello("world")
        c1.close()
        c2.close()


class TestAIOBufferedBinary(_TestAIO):
    TRANSPORT_FACTORY = TAsyncBufferedTransportFactory()
    PROTOCOL_FACTORY = TAsyncBinaryProtocolFactory()


class TestAIOBufferedCompact(_TestAIO):
    TRANSPORT_FACTORY = TAsyncBufferedTransportFactory()
    PROTOCOL_FACTORY = TAsyncCompactProtocolFactory()


class TestAIOFramedBinary(_TestAIO):
    TRANSPORT_FACTORY = TAsyncFramedTransportFactory()
    PROTOCOL_FACTORY = TAsyncBinaryProtocolFactory()


class TestAIOFramedCompact(_TestAIO):
    TRANSPORT_FACTORY = TAsyncFramedTransportFactory()
    PROTOCOL_FACTORY = TAsyncCompactProtocolFactory()


class TestAIOBufferedBinarySSL(SSLServerMixin, TestAIOBufferedBinary):
    pass


class TestAIOBufferedCompactSSL(SSLServerMixin, TestAIOBufferedCompact):
    pass


class TestAIOFramedBinarySSL(SSLServerMixin, TestAIOFramedBinary):
    pass


class TestAIOFramedCompactSSL(SSLServerMixin, TestAIOFramedCompact):
    pass


@pytest.mark.asyncio
async def test_client_connect_timeout():
    with pytest.raises(TTransportException):
        c = await make_aio_client(
            addressbook.AddressBookService,
            unix_socket='/tmp/test.sock',
            connect_timeout=1000
        )
        await c.hello('test')


class TestDeprecatedTimeoutKwarg:
    """
    Replace TAsyncSocket with a Mock object that raises a RuntimeError
    when called. This allows us to check that timeout vs. socket_timeout
    arguments are properly handled without actually creating the client.

    This class should be removed when the socket_timeout argument is removed.
    """
    def setup(self):
        # Create and apply a fresh patch for each test.
        self.async_sock = patch(
            'thriftpy2.contrib.aio.rpc.TAsyncSocket',
            side_effect=RuntimeError,
        ).__enter__()

    def teardown_(self):
        self.async_sock.__exit__()  # Clean up patch

    @pytest.mark.asyncio
    async def test_no_timeout_given(self):
        await self._make_client()
        assert self._given_timeout() == 3000  # Default value

    @pytest.mark.asyncio
    async def test_timeout_given(self):
        await self._make_client(timeout=1234)
        assert self._given_timeout() == 1234

    @pytest.mark.asyncio
    async def test_socket_timeout_given(self):
        await self._make_client(warning=DeprecationWarning, socket_timeout=555)
        assert self._given_timeout() == 555

    @staticmethod
    async def _make_client(warning=None, **kwargs):
        """
        Helper method to create the client and check that the proper warning
        is emitted (if any) and that the patch is properly applied by
        consuming the RuntimeError.
        """
        with pytest.warns(warning),\
                pytest.raises(RuntimeError):  # Consume error
            await make_aio_client(addressbook.AddressBookService, **kwargs)

    def _given_timeout(self):
        """Get the timeout provided to TAsyncSocket."""
        try:
            self.async_sock.assert_called_once()
        except AttributeError:  # Python 3.5
            assert self.async_sock.call_count == 1
        _args, kwargs = self.async_sock.call_args
        return kwargs['socket_timeout']
