from collections import namedtuple, deque
import os
import threading
import time
import uuid
import struct
import sys

import pytest
import mock

from kazoo.exceptions import ConnectionLoss
from kazoo.protocol.serialization import (
    Connect,
    int_struct,
    write_string,
)
from kazoo.protocol.states import KazooState
from kazoo.protocol.connection import _CONNECTION_DROP
from kazoo.testing import KazooTestCase
from kazoo.tests.util import wait
from kazoo.tests.util import TRAVIS_ZK_VERSION


class Delete(namedtuple('Delete', 'path version')):
    type = 2

    def serialize(self):
        b = bytearray()
        b.extend(write_string(self.path))
        b.extend(int_struct.pack(self.version))
        return b

    @classmethod
    def deserialize(self, bytes, offset):
        raise ValueError("oh my")


class TestConnectionHandler(KazooTestCase):
    def test_bad_deserialization(self):
        async_object = self.client.handler.async_result()
        self.client._queue.append(
            (Delete(self.client.chroot, -1), async_object)
        )
        self.client._connection._write_sock.send(b'\0')

        with pytest.raises(ValueError):
            async_object.get()

    def test_with_bad_sessionid(self):
        ev = threading.Event()

        def expired(state):
            if state == KazooState.CONNECTED:
                ev.set()

        password = os.urandom(16)
        client = self._get_client(client_id=(82838284824, password))
        client.add_listener(expired)
        client.start()
        try:
            ev.wait(15)
            assert ev.is_set()
        finally:
            client.stop()

    def test_connection_read_timeout(self):
        client = self.client
        ev = threading.Event()
        path = "/" + uuid.uuid4().hex
        handler = client.handler
        _select = handler.select
        _socket = client._connection._socket

        def delayed_select(*args, **kwargs):
            result = _select(*args, **kwargs)
            if len(args[0]) == 1 and _socket in args[0]:
                # for any socket read, simulate a timeout
                return [], [], []
            return result

        def back(state):
            if state == KazooState.CONNECTED:
                ev.set()

        client.add_listener(back)
        client.create(path, b"1")
        try:
            handler.select = delayed_select
            with pytest.raises(ConnectionLoss):
                client.get(path)
        finally:
            handler.select = _select
        # the client reconnects automatically
        ev.wait(5)
        assert ev.is_set()
        assert client.get(path)[0] == b"1"

    def test_connection_write_timeout(self):
        client = self.client
        ev = threading.Event()
        path = "/" + uuid.uuid4().hex
        handler = client.handler
        _select = handler.select
        _socket = client._connection._socket

        def delayed_select(*args, **kwargs):
            result = _select(*args, **kwargs)
            if _socket in args[1]:
                # for any socket write, simulate a timeout
                return [], [], []
            return result

        def back(state):
            if state == KazooState.CONNECTED:
                ev.set()

        client.add_listener(back)

        try:
            handler.select = delayed_select
            with pytest.raises(ConnectionLoss):
                client.create(path)
        finally:
            handler.select = _select
        # the client reconnects automatically
        ev.wait(5)
        assert ev.is_set()
        assert client.exists(path) is None

    def test_connection_deserialize_fail(self):
        client = self.client
        ev = threading.Event()
        path = "/" + uuid.uuid4().hex
        handler = client.handler
        _select = handler.select
        _socket = client._connection._socket

        def delayed_select(*args, **kwargs):
            result = _select(*args, **kwargs)
            if _socket in args[1]:
                # for any socket write, simulate a timeout
                return [], [], []
            return result

        def back(state):
            if state == KazooState.CONNECTED:
                ev.set()

        client.add_listener(back)

        deserialize_ev = threading.Event()

        def bad_deserialize(_bytes, offset):
            deserialize_ev.set()
            raise struct.error()

        # force the connection to die but, on reconnect, cause the
        # server response to be non-deserializable. ensure that the client
        # continues to retry. This partially reproduces a rare bug seen
        # in production.

        with mock.patch.object(Connect, 'deserialize') as mock_deserialize:
            mock_deserialize.side_effect = bad_deserialize
            try:
                handler.select = delayed_select
                with pytest.raises(ConnectionLoss):
                    client.create(path)
            finally:
                handler.select = _select
            # the client reconnects automatically but the first attempt will
            # hit a deserialize failure. wait for that.
            deserialize_ev.wait(5)
            assert deserialize_ev.is_set()

        # this time should succeed
        ev.wait(5)
        assert ev.is_set()
        assert client.exists(path) is None

    def test_connection_close(self):
        with pytest.raises(Exception):
            self.client.close()
        self.client.stop()
        self.client.close()

        # should be able to restart
        self.client.start()

    def test_connection_sock(self):
        client = self.client
        read_sock = client._connection._read_sock
        write_sock = client._connection._write_sock

        assert read_sock is not None
        assert write_sock is not None

        # stop client and socket should not yet be closed
        client.stop()
        assert read_sock is not None
        assert write_sock is not None

        read_sock.getsockname()
        write_sock.getsockname()

        # close client, and sockets should be closed
        client.close()

        # Todo check socket closing

        # start client back up. should get a new, valid socket
        client.start()
        read_sock = client._connection._read_sock
        write_sock = client._connection._write_sock

        assert read_sock is not None
        assert write_sock is not None
        read_sock.getsockname()
        write_sock.getsockname()

    def test_dirty_sock(self):
        client = self.client
        read_sock = client._connection._read_sock
        write_sock = client._connection._write_sock

        # add a stray byte to the socket and ensure that doesn't
        # blow up client. simulates case where some error leaves
        # a byte in the socket which doesn't correspond to the
        # request queue.
        write_sock.send(b'\0')

        # eventually this byte should disappear from socket
        wait(lambda: client.handler.select([read_sock], [], [], 0)[0] == [])


class TestConnectionDrop(KazooTestCase):
    def test_connection_dropped(self):
        ev = threading.Event()

        def back(state):
            if state == KazooState.CONNECTED:
                ev.set()

        # create a node with a large value and stop the ZK node
        path = "/" + uuid.uuid4().hex
        self.client.create(path)
        self.client.add_listener(back)
        result = self.client.set_async(path, b'a' * 1000 * 1024)
        self.client._call(_CONNECTION_DROP, None)

        with pytest.raises(ConnectionLoss):
            result.get()
        # we have a working connection to a new node
        ev.wait(30)
        assert ev.is_set()


class TestReadOnlyMode(KazooTestCase):
    def setUp(self):
        self.setup_zookeeper(read_only=True)
        skip = False
        if TRAVIS_ZK_VERSION and TRAVIS_ZK_VERSION < (3, 4):
            skip = True
        elif TRAVIS_ZK_VERSION and TRAVIS_ZK_VERSION >= (3, 4):
            skip = False
        else:
            ver = self.client.server_version()
            if ver[1] < 4:
                skip = True
        if skip:
            pytest.skip("Must use Zookeeper 3.4 or above")

    def tearDown(self):
        self.client.stop()

    def test_read_only(self):
        from kazoo.exceptions import NotReadOnlyCallError
        from kazoo.protocol.states import KeeperState

        client = self.client
        states = []
        ev = threading.Event()

        @client.add_listener
        def listen(state):
            states.append(state)
            if client.client_state == KeeperState.CONNECTED_RO:
                ev.set()

        try:
            self.cluster[1].stop()
            self.cluster[2].stop()
            ev.wait(6)
            assert ev.is_set()
            assert client.client_state == KeeperState.CONNECTED_RO

            # Test read only command
            assert client.get_children('/') == []

            # Test error with write command
            with pytest.raises(NotReadOnlyCallError):
                client.create('/fred')

            # Wait for a ping
            time.sleep(15)
        finally:
            client.remove_listener(listen)
            self.cluster[1].run()
            self.cluster[2].run()


class TestUnorderedXids(KazooTestCase):
    def setUp(self):
        super(TestUnorderedXids, self).setUp()

        self.connection = self.client._connection
        self.connection_routine = self.connection._connection_routine

        self._pending = self.client._pending
        self.client._pending = _naughty_deque()

    def tearDown(self):
        self.client._pending = self._pending
        super(TestUnorderedXids, self).tearDown()

    def _get_client(self, **kwargs):
        # overrides for patching zk_loop
        c = KazooTestCase._get_client(self, **kwargs)
        self._zk_loop = c._connection.zk_loop
        self._zk_loop_errors = []
        c._connection.zk_loop = self._zk_loop_func
        return c

    def _zk_loop_func(self, *args, **kwargs):
        # patched zk_loop which will catch and collect all RuntimeError
        try:
            self._zk_loop(*args, **kwargs)
        except RuntimeError as e:
            self._zk_loop_errors.append(e)

    def test_xids_mismatch(self):
        from kazoo.protocol.states import KeeperState

        ev = threading.Event()
        error_stack = []

        @self.client.add_listener
        def listen(state):
            if self.client.client_state == KeeperState.CLOSED:
                ev.set()

        def log_exception(*args):
            error_stack.append((args, sys.exc_info()))

        self.connection.logger.exception = log_exception

        ev.clear()
        with pytest.raises(RuntimeError):
            self.client.get_children('/')

        ev.wait()
        assert self.client.connected is False
        assert self.client.state == 'LOST'
        assert self.client.client_state == KeeperState.CLOSED

        args, exc_info = error_stack[-1]
        assert args == ('Unhandled exception in connection loop',)
        assert exc_info[0] == RuntimeError

        self.client.handler.sleep_func(0.2)
        assert not self.connection_routine.is_alive()
        assert len(self._zk_loop_errors) == 1
        assert self._zk_loop_errors[0] == exc_info[1]


class _naughty_deque(deque):
    def append(self, s):
        request, async_object, xid = s
        return deque.append(self, (request, async_object, xid + 1))  # +1s
