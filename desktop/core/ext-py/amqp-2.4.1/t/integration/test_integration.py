from __future__ import absolute_import, unicode_literals

import socket
import pytest
from case import patch, call, Mock, ANY
import amqp
from amqp import spec, Connection, Channel, sasl, Message
from amqp.platform import pack
from amqp.exceptions import ConnectionError, \
    InvalidCommand, AccessRefused, PreconditionFailed, NotFound, ResourceLocked
from amqp.serialization import dumps, loads
from amqp.protocol import queue_declare_ok_t

connection_testdata = (
    (spec.Connection.Blocked, '_on_blocked'),
    (spec.Connection.Unblocked, '_on_unblocked'),
    (spec.Connection.Secure, '_on_secure'),
    (spec.Connection.CloseOk, '_on_close_ok'),
)

channel_testdata = (
    (spec.Basic.Ack, '_on_basic_ack'),
    (spec.Basic.Nack, '_on_basic_nack'),
    (spec.Basic.CancelOk, '_on_basic_cancel_ok'),
)

exchange_declare_error_testdata = (
    (
        503, "COMMAND_INVALID - "
        "unknown exchange type 'exchange-type'",
        InvalidCommand
    ),
    (
        403, "ACCESS_REFUSED - "
        "exchange name 'amq.foo' contains reserved prefix 'amq.*'",
        AccessRefused
    ),
    (
        406, "PRECONDITION_FAILED - "
        "inequivalent arg 'type' for exchange 'foo' in vhost '/':"
        "received 'direct' but current is 'fanout'",
        PreconditionFailed
    ),
)

queue_declare_error_testdata = (
    (
        403, "ACCESS_REFUSED - "
        "queue name 'amq.foo' contains reserved prefix 'amq.*",
        AccessRefused
    ),
    (
        404, "NOT_FOUND - "
        "no queue 'foo' in vhost '/'",
        NotFound
    ),
    (
        405, "RESOURCE_LOCKED - "
        "cannot obtain exclusive access to locked queue 'foo' in vhost '/'",
        ResourceLocked
    ),
)

CLIENT_PROPERTIES = {
    'product': 'py-amqp',
    'product_version': amqp.__version__,
    'capabilities': {
        'consumer_cancel_notify': True,
        'connection.blocked': True,
        'authentication_failure_close': True
    },
}

SERVER_PROPERTIES = {
    'capabilities': {
        'publisher_confirms': True,
        'exchange_exchange_bindings': True,
        'basic.nack': True,
        'consumer_cancel_notify': True,
        'connection.blocked': True,
        'consumer_priorities': True,
        'authentication_failure_close': True,
        'per_consumer_qos': True,
        'direct_reply_to': True
    },
    'cluster_name': 'rabbit@broker.com',
    'copyright': 'Copyright (C) 2007-2018 Pivotal Software, Inc.',
    'information': 'Licensed under the MPL.  See http://www.rabbitmq.com/',
    'platform': 'Erlang/OTP 20.3.8.9',
    'product': 'RabbitMQ',
    'version': '3.7.8'
}


def build_frame_type_1(method, channel=0, args=b'', arg_format=None):
    if len(args) > 0:
        args = dumps(arg_format, args)
    else:
        args = b''
    frame = (b''.join([pack('>HH', *method), args]))
    return 1, channel, frame


def build_frame_type_2(body_len, channel, properties):
    frame = (b''.join(
        [pack('>HxxQ', spec.Basic.CLASS_ID, body_len), properties])
    )
    return 2, channel, frame


def build_frame_type_3(channel, body):
    return 3, channel, body


class DataComparator(object):
    # Comparator used for asserting serialized data. It can be used
    # in cases when direct comparision of bytestream cannot be used
    # (mainly cases of Table type where order of items can vary)
    def __init__(self, argsig, items):
        self.argsig = argsig
        self.items = items

    def __eq__(self, other):
        values, offset = loads(self.argsig, other)
        return tuple(values) == tuple(self.items)


def handshake(conn, transport_mock, server_properties=None):
    # Helper function simulating connection handshake with server
    if server_properties is None:
        server_properties = SERVER_PROPERTIES

    transport_mock().read_frame.side_effect = [
        build_frame_type_1(
            spec.Connection.Start, channel=0,
            args=(
                0, 9, server_properties, 'AMQPLAIN PLAIN', 'en_US'
            ),
            arg_format='ooFSS'
        ),
        build_frame_type_1(
            spec.Connection.Tune, channel=0,
            args=(2047, 131072, 60), arg_format='BlB'
        ),
        build_frame_type_1(
            spec.Connection.OpenOk, channel=0
        )
    ]
    conn.connect()
    transport_mock().read_frame.side_effect = None


def create_channel(channel_id, conn, transport_mock):
    transport_mock().read_frame.side_effect = [
        build_frame_type_1(
            spec.Channel.OpenOk,
            channel=channel_id,
            args=(1, False),
            arg_format='Lb'
        )
    ]
    ch = conn.channel(channel_id=channel_id)
    transport_mock().read_frame.side_effect = None
    return ch


class test_connection:
    # Integration tests. Tests verify the correctness of communication between
    # library and broker.
    # * tests mocks broker responses mocking return values of
    #   amqp.transport.Transport.read_frame() method
    # * tests asserts expected library responses to broker via calls of
    #   amqp.method_framing.frame_writer() function

    def test_connect(self):
        # Test checking connection handshake
        frame_writer_cls_mock = Mock()
        on_open_mock = Mock()
        frame_writer_mock = frame_writer_cls_mock()
        conn = Connection(
            frame_writer=frame_writer_cls_mock, on_open=on_open_mock
        )

        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            on_open_mock.assert_called_once_with(conn)
            security_mechanism = sasl.AMQPLAIN(
                'guest', 'guest'
            ).start(conn).decode('utf-8', 'surrogatepass')

            # Expected responses from client
            frame_writer_mock.assert_has_calls(
                [
                    call(
                        1, 0, spec.Connection.StartOk,
                        # Due Table type, we cannot compare bytestream directly
                        DataComparator(
                            'FsSs',
                            (
                                CLIENT_PROPERTIES, 'AMQPLAIN',
                                security_mechanism,
                                'en_US'
                            )
                        ),
                        None
                    ),
                    call(
                        1, 0, spec.Connection.TuneOk,
                        dumps(
                            'BlB',
                            (conn.channel_max, conn.frame_max, conn.heartbeat)
                        ),
                        None
                    ),
                    call(
                        1, 0, spec.Connection.Open,
                        dumps('ssb', (conn.virtual_host, '', False)),
                        None
                    )
                ]
            )
            assert conn.client_properties == CLIENT_PROPERTIES

    def test_connect_no_capabilities(self):
        # Test checking connection handshake with broker
        # not supporting capabilities
        frame_writer_cls_mock = Mock()
        on_open_mock = Mock()
        frame_writer_mock = frame_writer_cls_mock()
        conn = Connection(
            frame_writer=frame_writer_cls_mock, on_open=on_open_mock
        )

        with patch.object(conn, 'Transport') as transport_mock:
            server_properties = dict(SERVER_PROPERTIES)
            del server_properties['capabilities']
            client_properties = dict(CLIENT_PROPERTIES)
            del client_properties['capabilities']

            handshake(
                conn, transport_mock, server_properties=server_properties
            )
            on_open_mock.assert_called_once_with(conn)
            security_mechanism = sasl.AMQPLAIN(
                'guest', 'guest'
            ).start(conn).decode('utf-8', 'surrogatepass')

            # Expected responses from client
            frame_writer_mock.assert_has_calls(
                [
                    call(
                        1, 0, spec.Connection.StartOk,
                        # Due Table type, we cannot compare bytestream directly
                        DataComparator(
                            'FsSs',
                            (
                                client_properties, 'AMQPLAIN',
                                security_mechanism,
                                'en_US'
                            )
                        ),
                        None
                    ),
                    call(
                        1, 0, spec.Connection.TuneOk,
                        dumps(
                            'BlB',
                            (conn.channel_max, conn.frame_max, conn.heartbeat)
                        ),
                        None
                    ),
                    call(
                        1, 0, spec.Connection.Open,
                        dumps('ssb', (conn.virtual_host, '', False)),
                        None
                    )
                ]
            )
            assert conn.client_properties == client_properties

    def test_connect_missing_capabilities(self):
        # Test checking connection handshake with broker
        # supporting subset of capabilities
        frame_writer_cls_mock = Mock()
        on_open_mock = Mock()
        frame_writer_mock = frame_writer_cls_mock()
        conn = Connection(
            frame_writer=frame_writer_cls_mock, on_open=on_open_mock
        )

        with patch.object(conn, 'Transport') as transport_mock:
            server_properties = dict(SERVER_PROPERTIES)
            server_properties['capabilities'] = {
                # This capability is not supported by client
                'basic.nack': True,
                'consumer_cancel_notify': True,
                'connection.blocked': False,
                # server does not support 'authentication_failure_close'
                # which is supported by client
            }

            client_properties = dict(CLIENT_PROPERTIES)
            client_properties['capabilities'] = {
                'consumer_cancel_notify': True,
            }

            handshake(
                conn, transport_mock, server_properties=server_properties
            )
            on_open_mock.assert_called_once_with(conn)
            security_mechanism = sasl.AMQPLAIN(
                'guest', 'guest'
            ).start(conn).decode('utf-8', 'surrogatepass')

            # Expected responses from client
            frame_writer_mock.assert_has_calls(
                [
                    call(
                        1, 0, spec.Connection.StartOk,
                        # Due Table type, we cannot compare bytestream directly
                        DataComparator(
                            'FsSs',
                            (
                                client_properties, 'AMQPLAIN',
                                security_mechanism,
                                'en_US'
                            )
                        ),
                        None
                    ),
                    call(
                        1, 0, spec.Connection.TuneOk,
                        dumps(
                            'BlB',
                            (conn.channel_max, conn.frame_max, conn.heartbeat)
                        ),
                        None
                    ),
                    call(
                        1, 0, spec.Connection.Open,
                        dumps('ssb', (conn.virtual_host, '', False)),
                        None
                    )
                ]
            )
            assert conn.client_properties == client_properties

    def test_connection_close(self):
        # Test checking closing connection
        frame_writer_cls_mock = Mock()
        frame_writer_mock = frame_writer_cls_mock()
        conn = Connection(frame_writer=frame_writer_cls_mock)
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            frame_writer_mock.reset_mock()
            # Inject CloseOk response from broker
            transport_mock().read_frame.return_value = build_frame_type_1(
                spec.Connection.CloseOk
            )
            t = conn.transport
            conn.close()
            frame_writer_mock.assert_called_once_with(
                1, 0, spec.Connection.Close, dumps('BsBB', (0, '', 0, 0)), None
            )
            t.close.assert_called_once_with()

    def test_connection_closed_by_broker(self):
        # Test that library response correctly CloseOk when
        # close method is received and _on_close_ok() method is called.
        frame_writer_cls_mock = Mock()
        frame_writer_mock = frame_writer_cls_mock()
        with patch.object(Connection, '_on_close_ok') as callback_mock:
            conn = Connection(frame_writer=frame_writer_cls_mock)
            with patch.object(conn, 'Transport') as transport_mock:
                handshake(conn, transport_mock)
                frame_writer_mock.reset_mock()
                # Inject Close response from broker
                transport_mock().read_frame.return_value = build_frame_type_1(
                    spec.Connection.Close,
                    args=(1, False),
                    arg_format='Lb'
                )
                with pytest.raises(ConnectionError):
                    conn.drain_events(0)
                frame_writer_mock.assert_called_once_with(
                    1, 0, spec.Connection.CloseOk, '', None
                )
                callback_mock.assert_called_once_with()


class test_channel:
    # Integration tests. Tests verify the correctness of communication between
    # library and broker.
    # * tests mocks broker responses mocking return values of
    #   amqp.transport.Transport.read_frame() method
    # * tests asserts expected library responses to broker via calls of
    #   amqp.method_framing.frame_writer() function

    @pytest.mark.parametrize("method, callback", connection_testdata)
    def test_connection_methods(self, method, callback):
        # Test verifying that proper Connection callback is called when
        # given method arrived from Broker.
        with patch.object(Connection, callback) as callback_mock:
            conn = Connection()
            with patch.object(conn, 'Transport') as transport_mock:
                handshake(conn, transport_mock)
                # Inject desired method
                transport_mock().read_frame.return_value = build_frame_type_1(
                    method, channel=0, args=(1, False), arg_format='Lb'
                )
                conn.drain_events(0)
                callback_mock.assert_called_once()

    def test_channel_open_close(self):
        # Test checking opening and closing channel
        frame_writer_cls_mock = Mock()
        conn = Connection(frame_writer=frame_writer_cls_mock)
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)

            channel_id = 1
            transport_mock().read_frame.side_effect = [
                # Inject Open Handshake
                build_frame_type_1(
                    spec.Channel.OpenOk,
                    channel=channel_id,
                    args=(1, False),
                    arg_format='Lb'
                ),
                # Inject close method
                build_frame_type_1(
                    spec.Channel.CloseOk,
                    channel=channel_id
                )
            ]

            frame_writer_mock = frame_writer_cls_mock()
            frame_writer_mock.reset_mock()

            on_open_mock = Mock()
            ch = conn.channel(channel_id=channel_id, callback=on_open_mock)
            on_open_mock.assert_called_once_with(ch)
            assert ch.is_open is True

            ch.close()
            frame_writer_mock.assert_has_calls(
                [
                    call(
                        1, 1, spec.Channel.Open, dumps('s', ('',)),
                        None
                    ),
                    call(
                        1, 1, spec.Channel.Close, dumps('BsBB', (0, '', 0, 0)),
                        None
                    )
                ]
            )
            assert ch.is_open is False

    def test_received_channel_Close_during_connection_close(self):
        # This test verifies that library handles correctly closing channel
        # during closing of connection:
        # 1. User requests closing connection - client sends Connection.Close
        # 2. Broker requests closing Channel - client receives Channel.Close
        # 3. Broker sends Connection.CloseOk
        # see GitHub issue #218
        conn = Connection()
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            channel_id = 1
            create_channel(channel_id, conn, transport_mock)
            # Replies sent by broker
            transport_mock().read_frame.side_effect = [
                # Inject close methods
                build_frame_type_1(
                    spec.Channel.Close,
                    channel=channel_id,
                    args=(1, False),
                    arg_format='Lb'
                ),
                build_frame_type_1(
                    spec.Connection.CloseOk
                )
            ]
            conn.close()

    @pytest.mark.parametrize("method, callback", channel_testdata)
    def test_channel_methods(self, method, callback):
        # Test verifying that proper Channel callback is called when
        # given method arrived from Broker
        with patch.object(Channel, callback) as callback_mock:
            conn = Connection()
            with patch.object(conn, 'Transport') as transport_mock:
                handshake(conn, transport_mock)
                create_channel(1, conn, transport_mock)

                # Inject desired method
                transport_mock().read_frame.return_value = build_frame_type_1(
                    method,
                    channel=1,
                    args=(1, False),
                    arg_format='Lb'
                )
                conn.drain_events(0)
                callback_mock.assert_called_once()

    def test_basic_publish(self):
        # Test verifing publishing message.
        frame_writer_cls_mock = Mock()
        conn = Connection(frame_writer=frame_writer_cls_mock)
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            ch = create_channel(1, conn, transport_mock)

            frame_writer_mock = frame_writer_cls_mock()
            frame_writer_mock.reset_mock()
            msg = Message('test')
            # we need to mock socket timeout due checks in
            # Channel._basic_publish
            transport_mock().read_frame.side_effect = socket.timeout
            ch.basic_publish(msg)
            frame_writer_mock.assert_called_once_with(
                1, 1, spec.Basic.Publish,
                dumps('Bssbb', (0, '', '', False, False)), msg
            )

    def test_consume_no_consumer_tag(self):
        # Test verifing starting consuming without specified consumer_tag
        callback_mock = Mock()
        frame_writer_cls_mock = Mock()
        conn = Connection(frame_writer=frame_writer_cls_mock)
        consumer_tag = 'amq.ctag-PCmzXGkhCw_v0Zq7jXyvkg'
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            ch = create_channel(1, conn, transport_mock)

            # Inject ConsumeOk response from Broker
            transport_mock().read_frame.return_value = build_frame_type_1(
                spec.Basic.ConsumeOk,
                channel=1,
                args=(consumer_tag,),
                arg_format='s'
            )
            frame_writer_mock = frame_writer_cls_mock()
            frame_writer_mock.reset_mock()
            ret = ch.basic_consume('my_queue', callback=callback_mock)
            frame_writer_mock.assert_called_once_with(
                1, 1, spec.Basic.Consume,
                dumps(
                    'BssbbbbF',
                    (0, 'my_queue', '', False, False, False, False, None)
                ),
                None
            )
            assert ch.callbacks[consumer_tag] == callback_mock
            assert ret == 'amq.ctag-PCmzXGkhCw_v0Zq7jXyvkg'

    def test_consume_with_consumer_tag(self):
        # Test verifing starting consuming with specified consumer_tag
        callback_mock = Mock()
        frame_writer_cls_mock = Mock()
        conn = Connection(frame_writer=frame_writer_cls_mock)
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            ch = create_channel(1, conn, transport_mock)

            # Inject ConcumeOk response from Broker
            transport_mock().read_frame.return_value = build_frame_type_1(
                spec.Basic.ConsumeOk,
                channel=1,
                args=('my_tag',),
                arg_format='s'
            )
            frame_writer_mock = frame_writer_cls_mock()
            frame_writer_mock.reset_mock()
            ret = ch.basic_consume(
                'my_queue', callback=callback_mock, consumer_tag='my_tag'
            )
            frame_writer_mock.assert_called_once_with(
                1, 1, spec.Basic.Consume,
                dumps(
                    'BssbbbbF',
                    (
                        0, 'my_queue', 'my_tag',
                        False, False, False, False, None
                    )
                ),
                None
            )
            assert ch.callbacks['my_tag'] == callback_mock
            assert ret == 'my_tag'

    def test_queue_declare(self):
        # Test verifying declaring queue
        frame_writer_cls_mock = Mock()
        conn = Connection(frame_writer=frame_writer_cls_mock)
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            ch = create_channel(1, conn, transport_mock)
            transport_mock().read_frame.return_value = build_frame_type_1(
                spec.Queue.DeclareOk,
                channel=1,
                arg_format='sll',
                args=('foo', 1, 2)
            )
            frame_writer_mock = frame_writer_cls_mock()
            frame_writer_mock.reset_mock()
            ret = ch.queue_declare('foo')
            assert ret == queue_declare_ok_t(
                queue='foo', message_count=1, consumer_count=2
            )
            frame_writer_mock.assert_called_once_with(
                1, 1, spec.Queue.Declare,
                dumps(
                    'BsbbbbbF',
                    (
                        0,
                        # queue, passive, durable, exclusive,
                        'foo', False, False, False,
                        # auto_delete, nowait, arguments
                        True, False, None
                    )
                ),
                None
            )

    @pytest.mark.parametrize(
        "reply_code, reply_text, exception", queue_declare_error_testdata)
    def test_queue_declare_error(self, reply_code, reply_text, exception):
        # Test verifying wrong declaring exchange
        frame_writer_cls_mock = Mock()
        conn = Connection(frame_writer=frame_writer_cls_mock)
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            ch = create_channel(1, conn, transport_mock)
            transport_mock().read_frame.return_value = build_frame_type_1(
                spec.Connection.Close,
                args=(reply_code, reply_text) + spec.Exchange.Declare,
                arg_format='BsBB'
            )
            frame_writer_mock = frame_writer_cls_mock()
            frame_writer_mock.reset_mock()
            with pytest.raises(exception) as excinfo:
                ch.queue_declare('foo')
            assert excinfo.value.code == reply_code
            assert excinfo.value.message == reply_text
            assert excinfo.value.method == 'Exchange.declare'
            assert excinfo.value.method_name == 'Exchange.declare'
            assert excinfo.value.method_sig == spec.Exchange.Declare
            # Client is sending to broker:
            # 1. Exchange Declare
            # 2. Connection.CloseOk as reply to received Connecton.Close
            frame_writer_calls = [
                call(
                    1, 1, spec.Queue.Declare,
                    dumps(
                        'BsbbbbbF',
                        (
                            0,
                            # queue, passive, durable, exclusive,
                            'foo', False, False, False,
                            # auto_delete, nowait, arguments
                            True, False, None
                        )
                    ),
                    None
                ),
                call(
                    1, 0, spec.Connection.CloseOk,
                    '',
                    None
                ),
            ]
            frame_writer_mock.assert_has_calls(frame_writer_calls)

    def test_queue_delete(self):
        # Test verifying deleting queue
        frame_writer_cls_mock = Mock()
        conn = Connection(frame_writer=frame_writer_cls_mock)
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            ch = create_channel(1, conn, transport_mock)
            transport_mock().read_frame.return_value = build_frame_type_1(
                spec.Queue.DeleteOk,
                channel=1,
                arg_format='l',
                args=(5,)
            )
            frame_writer_mock = frame_writer_cls_mock()
            frame_writer_mock.reset_mock()
            msg_count = ch.queue_delete('foo')
            assert msg_count == 5
            frame_writer_mock.assert_called_once_with(
                1, 1, spec.Queue.Delete,
                dumps(
                    'Bsbbb',
                    # queue, if_unused, if_empty, nowait
                    (0, 'foo', False, False, False)
                ),
                None
            )

    def test_queue_purge(self):
        # Test verifying purging queue
        frame_writer_cls_mock = Mock()
        conn = Connection(frame_writer=frame_writer_cls_mock)
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            ch = create_channel(1, conn, transport_mock)
            transport_mock().read_frame.return_value = build_frame_type_1(
                spec.Queue.PurgeOk,
                channel=1,
                arg_format='l',
                args=(4,)
            )
            frame_writer_mock = frame_writer_cls_mock()
            frame_writer_mock.reset_mock()
            msg_count = ch.queue_purge('foo')
            assert msg_count == 4
            frame_writer_mock.assert_called_once_with(
                1, 1, spec.Queue.Purge,
                dumps(
                    'Bsb',
                    # queue, nowait
                    (0, 'foo', False)
                ),
                None
            )

    def test_basic_deliver(self):
        # Test checking delivering single message
        callback_mock = Mock()
        frame_writer_cls_mock = Mock()
        conn = Connection(frame_writer=frame_writer_cls_mock)
        consumer_tag = 'amq.ctag-PCmzXGkhCw_v0Zq7jXyvkg'
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            ch = create_channel(1, conn, transport_mock)

            # Inject ConsumeOk response from Broker
            transport_mock().read_frame.side_effect = [
                # Inject Consume-ok response
                build_frame_type_1(
                    spec.Basic.ConsumeOk,
                    channel=1,
                    args=(consumer_tag,),
                    arg_format='s'
                ),
                # Inject basic-deliver response
                build_frame_type_1(
                    spec.Basic.Deliver,
                    channel=1,
                    arg_format='sLbss',
                    args=(
                        # consumer-tag, delivery-tag, redelivered,
                        consumer_tag, 1, False,
                        # exchange-name, routing-key
                        'foo_exchange', 'routing-key'
                    )
                ),
                build_frame_type_2(
                    channel=1,
                    body_len=12,
                    properties=b'0\x00\x00\x00\x00\x00\x01'
                ),
                build_frame_type_3(
                    channel=1,
                    body=b'Hello World!'
                ),
            ]
            frame_writer_mock = frame_writer_cls_mock()
            frame_writer_mock.reset_mock()
            ch.basic_consume('my_queue', callback=callback_mock)
            conn.drain_events()
            callback_mock.assert_called_once_with(ANY)
            msg = callback_mock.call_args[0][0]
            assert isinstance(msg, Message)
            assert msg.body_size == 12
            assert msg.body == b'Hello World!'
            assert msg.frame_method == spec.Basic.Deliver
            assert msg.delivery_tag == 1
            assert msg.ready is True
            assert msg.delivery_info == {
                'consumer_tag': 'amq.ctag-PCmzXGkhCw_v0Zq7jXyvkg',
                'delivery_tag': 1,
                'redelivered': False,
                'exchange': 'foo_exchange',
                'routing_key': 'routing-key'
            }
            assert msg.properties == {
                'application_headers': {}, 'delivery_mode': 1
            }

    def test_queue_get(self):
        # Test verifying getting message from queue
        frame_writer_cls_mock = Mock()
        conn = Connection(frame_writer=frame_writer_cls_mock)
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            ch = create_channel(1, conn, transport_mock)
            transport_mock().read_frame.side_effect = [
                build_frame_type_1(
                    spec.Basic.GetOk,
                    channel=1,
                    arg_format='Lbssl',
                    args=(
                        # delivery_tag, redelivered, exchange_name
                        1, False, 'foo_exchange',
                        # routing_key, message_count
                        'routing_key', 1
                    )
                ),
                build_frame_type_2(
                    channel=1,
                    body_len=12,
                    properties=b'0\x00\x00\x00\x00\x00\x01'
                ),
                build_frame_type_3(
                    channel=1,
                    body=b'Hello World!'
                )
            ]
            frame_writer_mock = frame_writer_cls_mock()
            frame_writer_mock.reset_mock()
            msg = ch.basic_get('foo')
            assert msg.body_size == 12
            assert msg.body == b'Hello World!'
            assert msg.frame_method == spec.Basic.GetOk
            assert msg.delivery_tag == 1
            assert msg.ready is True
            assert msg.delivery_info == {
                'delivery_tag': 1, 'redelivered': False,
                'exchange': 'foo_exchange',
                'routing_key': 'routing_key', 'message_count': 1
            }
            assert msg.properties == {
                'application_headers': {}, 'delivery_mode': 1
            }
            frame_writer_mock.assert_called_once_with(
                1, 1, spec.Basic.Get,
                dumps(
                    'Bsb',
                    # queue, nowait
                    (0, 'foo', False)
                ),
                None
            )

    def test_queue_get_empty(self):
        # Test verifying getting message from empty queue
        frame_writer_cls_mock = Mock()
        conn = Connection(frame_writer=frame_writer_cls_mock)
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            ch = create_channel(1, conn, transport_mock)
            transport_mock().read_frame.return_value = build_frame_type_1(
                spec.Basic.GetEmpty,
                channel=1,
                arg_format='s',
                args=('s')
            )
            frame_writer_mock = frame_writer_cls_mock()
            frame_writer_mock.reset_mock()
            ret = ch.basic_get('foo')
            assert ret is None
            frame_writer_mock.assert_called_once_with(
                1, 1, spec.Basic.Get,
                dumps(
                    'Bsb',
                    # queue, nowait
                    (0, 'foo', False)
                ),
                None
            )

    def test_exchange_declare(self):
        # Test verifying declaring exchange
        frame_writer_cls_mock = Mock()
        conn = Connection(frame_writer=frame_writer_cls_mock)
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            ch = create_channel(1, conn, transport_mock)
            transport_mock().read_frame.return_value = build_frame_type_1(
                spec.Exchange.DeclareOk,
                channel=1
            )
            frame_writer_mock = frame_writer_cls_mock()
            frame_writer_mock.reset_mock()
            ret = ch.exchange_declare('foo', 'fanout')
            assert ret is None
            frame_writer_mock.assert_called_once_with(
                1, 1, spec.Exchange.Declare,
                dumps(
                    'BssbbbbbF',
                    (
                        0,
                        # exchange, type, passive, durable,
                        'foo', 'fanout', False, False,
                        # auto_delete, internal, nowait, arguments
                        True, False, False, None
                    )
                ),
                None
            )

    @pytest.mark.parametrize(
        "reply_code, reply_text, exception", exchange_declare_error_testdata)
    def test_exchange_declare_error(self, reply_code, reply_text, exception):
        # Test verifying wrong declaring exchange
        frame_writer_cls_mock = Mock()
        conn = Connection(frame_writer=frame_writer_cls_mock)
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            ch = create_channel(1, conn, transport_mock)
            transport_mock().read_frame.return_value = build_frame_type_1(
                spec.Connection.Close,
                args=(reply_code, reply_text) + spec.Exchange.Declare,
                arg_format='BsBB'
            )
            frame_writer_mock = frame_writer_cls_mock()
            frame_writer_mock.reset_mock()
            with pytest.raises(exception) as excinfo:
                ch.exchange_declare('exchange', 'exchange-type')
            assert excinfo.value.code == reply_code
            assert excinfo.value.message == reply_text
            assert excinfo.value.method == 'Exchange.declare'
            assert excinfo.value.method_name == 'Exchange.declare'
            assert excinfo.value.method_sig == spec.Exchange.Declare
            # Client is sending to broker:
            # 1. Exchange Declare
            # 2. Connection.CloseOk as reply to received Connecton.Close
            frame_writer_calls = [
                call(
                    1, 1, spec.Exchange.Declare,
                    dumps(
                        'BssbbbbbF',
                        (
                            0,
                            # exchange, type, passive, durable,
                            'exchange', 'exchange-type', False, False,
                            # auto_delete, internal, nowait, arguments
                            True, False, False, None
                        )
                    ),
                    None
                ),
                call(
                    1, 0, spec.Connection.CloseOk,
                    '',
                    None
                ),
            ]
            frame_writer_mock.assert_has_calls(frame_writer_calls)

    def test_exchange_delete(self):
        # Test verifying declaring exchange
        frame_writer_cls_mock = Mock()
        conn = Connection(frame_writer=frame_writer_cls_mock)
        with patch.object(conn, 'Transport') as transport_mock:
            handshake(conn, transport_mock)
            ch = create_channel(1, conn, transport_mock)
            transport_mock().read_frame.return_value = build_frame_type_1(
                spec.Exchange.DeleteOk,
                channel=1
            )
            frame_writer_mock = frame_writer_cls_mock()
            frame_writer_mock.reset_mock()
            ret = ch.exchange_delete('foo')
            assert ret == ()
            frame_writer_mock.assert_called_once_with(
                1, 1, spec.Exchange.Delete,
                dumps(
                    'Bsbb',
                    (
                        0,
                        # exchange, if-unused, no-wait
                        'foo', False, False
                    )
                ),
                None
            )
