from __future__ import absolute_import, unicode_literals

import socket
import warnings

import pytest
from case import ContextMock, Mock, call, patch

from amqp import Connection, spec
from amqp.connection import SSLError
from amqp.exceptions import ConnectionError, NotFound, ResourceError
from amqp.five import items
from amqp.sasl import AMQPLAIN, EXTERNAL, GSSAPI, PLAIN, SASL
from amqp.transport import TCPTransport


class test_Connection:

    @pytest.fixture(autouse=True)
    def setup_conn(self):
        self.frame_handler = Mock(name='frame_handler')
        self.frame_writer = Mock(name='frame_writer_cls')
        self.conn = Connection(
            frame_handler=self.frame_handler,
            frame_writer=self.frame_writer,
            authentication=AMQPLAIN('foo', 'bar'),
        )
        self.conn.Channel = Mock(name='Channel')
        self.conn.Transport = Mock(name='Transport')
        self.conn.transport = self.conn.Transport.return_value
        self.conn.send_method = Mock(name='send_method')
        self.conn.frame_writer = Mock(name='frame_writer')

    def test_sasl_authentication(self):
        authentication = SASL()
        self.conn = Connection(authentication=authentication)
        assert self.conn.authentication == (authentication,)

    def test_sasl_authentication_iterable(self):
        authentication = SASL()
        self.conn = Connection(authentication=(authentication,))
        assert self.conn.authentication == (authentication,)

    def test_gssapi(self):
        self.conn = Connection()
        assert isinstance(self.conn.authentication[0], GSSAPI)

    def test_external(self):
        self.conn = Connection()
        assert isinstance(self.conn.authentication[1], EXTERNAL)

    def test_amqplain(self):
        self.conn = Connection(userid='foo', password='bar')
        auth = self.conn.authentication[2]
        assert isinstance(auth, AMQPLAIN)
        assert auth.username == 'foo'
        assert auth.password == 'bar'

    def test_plain(self):
        self.conn = Connection(userid='foo', password='bar')
        auth = self.conn.authentication[3]
        assert isinstance(auth, PLAIN)
        assert auth.username == 'foo'
        assert auth.password == 'bar'

    def test_login_method_gssapi(self):
        try:
            self.conn = Connection(userid=None, password=None,
                                   login_method='GSSAPI')
        except NotImplementedError:
            pass
        else:
            auths = self.conn.authentication
            assert len(auths) == 1
            assert isinstance(auths[0], GSSAPI)

    def test_login_method_external(self):
        self.conn = Connection(userid=None, password=None,
                               login_method='EXTERNAL')
        auths = self.conn.authentication
        assert len(auths) == 1
        assert isinstance(auths[0], EXTERNAL)

    def test_login_method_amqplain(self):
        self.conn = Connection(login_method='AMQPLAIN')
        auths = self.conn.authentication
        assert len(auths) == 1
        assert isinstance(auths[0], AMQPLAIN)

    def test_login_method_plain(self):
        self.conn = Connection(login_method='PLAIN')
        auths = self.conn.authentication
        assert len(auths) == 1
        assert isinstance(auths[0], PLAIN)

    def test_enter_exit(self):
        self.conn.connect = Mock(name='connect')
        self.conn.close = Mock(name='close')
        with self.conn:
            self.conn.connect.assert_called_with()
        self.conn.close.assert_called_with()

    def test__enter__socket_error(self):
        # test when entering
        self.conn = Connection()
        self.conn.close = Mock(name='close')
        reached = False
        with patch('socket.socket', side_effect=socket.error):
            with pytest.raises(socket.error):
                with self.conn:
                    reached = True
        assert not reached and not self.conn.close.called
        assert self.conn._transport is None and not self.conn.connected

    def test__exit__socket_error(self):
        # test when exiting
        connection = self.conn
        transport = connection._transport
        transport.connected = True
        connection.send_method = Mock(name='send_method',
                                      side_effect=socket.error)
        reached = False
        with pytest.raises(socket.error):
            with connection:
                reached = True
        assert reached
        assert connection.send_method.called and transport.close.called
        assert self.conn._transport is None and not self.conn.connected

    def test_then(self):
        self.conn.on_open = Mock(name='on_open')
        on_success = Mock(name='on_success')
        on_error = Mock(name='on_error')
        self.conn.then(on_success, on_error)
        self.conn.on_open.then.assert_called_with(on_success, on_error)

    def test_connect(self):
        self.conn.transport.connected = False
        self.conn.drain_events = Mock(name='drain_events')

        def on_drain(*args, **kwargs):
            self.conn._handshake_complete = True
        self.conn.drain_events.side_effect = on_drain
        self.conn.connect()
        self.conn.Transport.assert_called_with(
            self.conn.host, self.conn.connect_timeout, self.conn.ssl,
            self.conn.read_timeout, self.conn.write_timeout,
            socket_settings=self.conn.socket_settings,
        )

    def test_connect__already_connected(self):
        callback = Mock(name='callback')
        self.conn.transport.connected = True
        assert self.conn.connect(callback) == callback.return_value
        callback.assert_called_with()

    def test_connect__socket_error(self):
        # check Transport.Connect error
        # socket.error derives from IOError
        # ssl.SSLError derives from socket.error
        self.conn = Connection()
        self.conn.Transport = Mock(name='Transport')
        transport = self.conn.Transport.return_value
        transport.connect.side_effect = IOError
        assert self.conn._transport is None and not self.conn.connected
        with pytest.raises(IOError):
            self.conn.connect()
        transport.connect.assert_called
        assert self.conn._transport is None and not self.conn.connected

    def test_on_start(self):
        self.conn._on_start(3, 4, {'foo': 'bar'}, b'x y z AMQPLAIN PLAIN',
                            'en_US en_GB')
        assert self.conn.version_major == 3
        assert self.conn.version_minor == 4
        assert self.conn.server_properties == {'foo': 'bar'}
        assert self.conn.mechanisms == [b'x', b'y', b'z',
                                        b'AMQPLAIN', b'PLAIN']
        assert self.conn.locales == ['en_US', 'en_GB']
        self.conn.send_method.assert_called_with(
            spec.Connection.StartOk, 'FsSs', (
                self.conn.client_properties, b'AMQPLAIN',
                self.conn.authentication[0].start(self.conn), self.conn.locale,
            ),
        )

    def test_on_start_string_mechanisms(self):
        self.conn._on_start(3, 4, {'foo': 'bar'}, 'x y z AMQPLAIN PLAIN',
                            'en_US en_GB')
        assert self.conn.version_major == 3
        assert self.conn.version_minor == 4
        assert self.conn.server_properties == {'foo': 'bar'}
        assert self.conn.mechanisms == [b'x', b'y', b'z',
                                        b'AMQPLAIN', b'PLAIN']
        assert self.conn.locales == ['en_US', 'en_GB']
        self.conn.send_method.assert_called_with(
            spec.Connection.StartOk, 'FsSs', (
                self.conn.client_properties, b'AMQPLAIN',
                self.conn.authentication[0].start(self.conn), self.conn.locale,
            ),
        )

    def test_missing_credentials(self):
        with pytest.raises(ValueError):
            self.conn = Connection(userid=None, password=None,
                                   login_method='AMQPLAIN')
        with pytest.raises(ValueError):
            self.conn = Connection(password=None, login_method='PLAIN')

    def test_invalid_method(self):
        with pytest.raises(ValueError):
            self.conn = Connection(login_method='any')

    def test_mechanism_mismatch(self):
        with pytest.raises(ConnectionError):
            self.conn._on_start(3, 4, {'foo': 'bar'}, b'x y z',
                                'en_US en_GB')

    def test_login_method_response(self):
        # An old way of doing things.:
        login_method, login_response = b'foo', b'bar'
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.conn = Connection(login_method=login_method,
                                   login_response=login_response)
            self.conn.send_method = Mock(name='send_method')
            self.conn._on_start(3, 4, {'foo': 'bar'}, login_method,
                                'en_US en_GB')
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)

        self.conn.send_method.assert_called_with(
            spec.Connection.StartOk, 'FsSs', (
                self.conn.client_properties, login_method,
                login_response, self.conn.locale,
            ),
        )

    def test_on_start__consumer_cancel_notify(self):
        self.conn._on_start(
            3, 4, {'capabilities': {'consumer_cancel_notify': 1}},
            b'AMQPLAIN', '',
        )
        cap = self.conn.client_properties['capabilities']
        assert cap['consumer_cancel_notify']

    def test_on_start__connection_blocked(self):
        self.conn._on_start(
            3, 4, {'capabilities': {'connection.blocked': 1}},
            b'AMQPLAIN', '',
        )
        cap = self.conn.client_properties['capabilities']
        assert cap['connection.blocked']

    def test_on_start__authentication_failure_close(self):
        self.conn._on_start(
            3, 4, {'capabilities': {'authentication_failure_close': 1}},
            b'AMQPLAIN', '',
        )
        cap = self.conn.client_properties['capabilities']
        assert cap['authentication_failure_close']

    def test_on_start__authentication_failure_close__disabled(self):
        self.conn._on_start(
            3, 4, {'capabilities': {}},
            b'AMQPLAIN', '',
        )
        assert 'capabilities' not in self.conn.client_properties

    def test_on_secure(self):
        self.conn._on_secure('vfz')

    def test_on_tune(self):
        self.conn.client_heartbeat = 16
        self.conn._on_tune(345, 16, 10)
        assert self.conn.channel_max == 345
        assert self.conn.frame_max == 16
        assert self.conn.server_heartbeat == 10
        assert self.conn.heartbeat == 10
        self.conn.send_method.assert_called_with(
            spec.Connection.TuneOk, 'BlB', (
                self.conn.channel_max, self.conn.frame_max,
                self.conn.heartbeat,
            ),
            callback=self.conn._on_tune_sent,
        )

    def test_on_tune__client_heartbeat_disabled(self):
        self.conn.client_heartbeat = 0
        self.conn._on_tune(345, 16, 10)
        assert self.conn.heartbeat == 0

    def test_on_tune_sent(self):
        self.conn._on_tune_sent()
        self.conn.send_method.assert_called_with(
            spec.Connection.Open, 'ssb', (self.conn.virtual_host, '', False),
        )

    def test_on_open_ok(self):
        self.conn.on_open = Mock(name='on_open')
        self.conn._on_open_ok()
        assert self.conn._handshake_complete
        self.conn.on_open.assert_called_with(self.conn)

    def test_connected(self):
        self.conn.transport.connected = False
        assert not self.conn.connected
        self.conn.transport.connected = True
        assert self.conn.connected
        self.conn.transport = None
        assert not self.conn.connected

    def test_collect(self):
        channels = self.conn.channels = {
            0: self.conn, 1: Mock(name='c1'), 2: Mock(name='c2'),
        }
        transport = self.conn.transport
        self.conn.collect()
        transport.close.assert_called_with()
        for i, channel in items(channels):
            if i:
                channel.collect.assert_called_with()
        assert self.conn._transport is None

    def test_collect__channel_raises_socket_error(self):
        self.conn.channels = self.conn.channels = {1: Mock(name='c1')}
        self.conn.channels[1].collect.side_effect = socket.error()
        self.conn.collect()

    def test_collect_no_transport(self):
        self.conn = Connection()
        self.conn.connect = Mock(name='connect')
        assert not self.conn.connected
        self.conn.collect()
        assert not self.conn.connect.called

    def test_collect_again(self):
        self.conn = Connection()
        self.conn.collect()
        self.conn.collect()

    def test_get_free_channel_id__raises_IndexError(self):
        self.conn._avail_channel_ids = []
        with pytest.raises(ResourceError):
            self.conn._get_free_channel_id()

    def test_claim_channel_id(self):
        self.conn._claim_channel_id(30)
        with pytest.raises(ConnectionError):
            self.conn._claim_channel_id(30)

    def test_channel(self):
        callback = Mock(name='callback')
        c = self.conn.channel(3, callback)
        self.conn.Channel.assert_called_with(self.conn, 3, on_open=callback)
        c2 = self.conn.channel(3, callback)
        assert c2 is c

    def test_is_alive(self):
        with pytest.raises(NotImplementedError):
            self.conn.is_alive()

    def test_drain_events(self):
        self.conn.blocking_read = Mock(name='blocking_read')
        self.conn.drain_events(30)
        self.conn.blocking_read.assert_called_with(30)

    def test_blocking_read__no_timeout(self):
        self.conn.on_inbound_frame = Mock(name='on_inbound_frame')
        self.conn.transport.having_timeout = ContextMock()
        ret = self.conn.blocking_read(None)
        self.conn.transport.read_frame.assert_called_with()
        self.conn.on_inbound_frame.assert_called_with(
            self.conn.transport.read_frame(),
        )
        assert ret is self.conn.on_inbound_frame()

    def test_blocking_read__timeout(self):
        self.conn.transport = TCPTransport('localhost:5672')
        sock = self.conn.transport.sock = Mock(name='sock')
        sock.gettimeout.return_value = 1
        self.conn.transport.read_frame = Mock(name='read_frame')
        self.conn.on_inbound_frame = Mock(name='on_inbound_frame')
        self.conn.blocking_read(3)
        sock.gettimeout.assert_called_with()
        sock.settimeout.assert_has_calls([call(3), call(1)])
        self.conn.transport.read_frame.assert_called_with()
        self.conn.on_inbound_frame.assert_called_with(
            self.conn.transport.read_frame(),
        )
        sock.gettimeout.return_value = 3
        self.conn.blocking_read(3)

    def test_blocking_read__SSLError(self):
        self.conn.on_inbound_frame = Mock(name='on_inbound_frame')
        self.conn.transport = TCPTransport('localhost:5672')
        sock = self.conn.transport.sock = Mock(name='sock')
        sock.gettimeout.return_value = 1
        self.conn.transport.read_frame = Mock(name='read_frame')
        self.conn.transport.read_frame.side_effect = SSLError(
            'operation timed out')
        with pytest.raises(socket.timeout):
            self.conn.blocking_read(3)
        self.conn.transport.read_frame.side_effect = SSLError(
            'The operation did not complete foo bar')
        with pytest.raises(socket.timeout):
            self.conn.blocking_read(3)
        self.conn.transport.read_frame.side_effect = SSLError(
            'oh noes')
        with pytest.raises(SSLError):
            self.conn.blocking_read(3)

    def test_on_inbound_method(self):
        self.conn.channels[1] = self.conn.channel(1)
        self.conn.on_inbound_method(1, (50, 60), 'payload', 'content')
        self.conn.channels[1].dispatch_method.assert_called_with(
            (50, 60), 'payload', 'content',
        )

    def test_close(self):
        self.conn.collect = Mock(name='collect')
        self.conn.close(reply_text='foo', method_sig=spec.Channel.Open)
        self.conn.send_method.assert_called_with(
            spec.Connection.Close, 'BsBB',
            (0, 'foo', spec.Channel.Open[0], spec.Channel.Open[1]),
            wait=spec.Connection.CloseOk,
        )

    def test_close__already_closed(self):
        self.conn.transport = None
        self.conn.close()

    def test_close__socket_error(self):
        self.conn.send_method = Mock(name='send_method',
                                     side_effect=socket.error)
        with pytest.raises(socket.error):
            self.conn.close()
        self.conn.send_method.assert_called()
        assert self.conn._transport is None and not self.conn.connected

    def test_on_close(self):
        self.conn._x_close_ok = Mock(name='_x_close_ok')
        with pytest.raises(NotFound):
            self.conn._on_close(404, 'bah not found', 50, 60)

    def test_x_close_ok(self):
        self.conn._x_close_ok()
        self.conn.send_method.assert_called_with(
            spec.Connection.CloseOk, callback=self.conn._on_close_ok,
        )

    def test_on_close_ok(self):
        self.conn.collect = Mock(name='collect')
        self.conn._on_close_ok()
        self.conn.collect.assert_called_with()

    def test_on_blocked(self):
        self.conn._on_blocked()
        self.conn.on_blocked = Mock(name='on_blocked')
        self.conn._on_blocked()
        self.conn.on_blocked.assert_called_with(
            'connection blocked, see broker logs')

    def test_on_unblocked(self):
        self.conn._on_unblocked()
        self.conn.on_unblocked = Mock(name='on_unblocked')
        self.conn._on_unblocked()
        self.conn.on_unblocked.assert_called_with()

    def test_send_heartbeat(self):
        self.conn.send_heartbeat()
        self.conn.frame_writer.assert_called_with(
            8, 0, None, None, None,
        )

    def test_heartbeat_tick__no_heartbeat(self):
        self.conn.heartbeat = 0
        self.conn.heartbeat_tick()

    def test_heartbeat_tick(self):
        self.conn.heartbeat = 3
        self.conn.heartbeat_tick()
        self.conn.bytes_sent = 3124
        self.conn.bytes_recv = 123
        self.conn.heartbeat_tick()
        self.conn.last_heartbeat_received -= 1000
        self.conn.last_heartbeat_sent -= 1000
        with pytest.raises(ConnectionError):
            self.conn.heartbeat_tick()

    def test_server_capabilities(self):
        self.conn.server_properties['capabilities'] = {'foo': 1}
        assert self.conn.server_capabilities == {'foo': 1}
