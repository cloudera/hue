from __future__ import absolute_import, unicode_literals

import pytest
from case import Mock, patch
from vine import promise

from amqp.abstract_channel import AbstractChannel
from amqp.exceptions import AMQPNotImplementedError, RecoverableConnectionError
from amqp.serialization import dumps


class test_AbstractChannel:

    class Channel(AbstractChannel):

        def _setup_listeners(self):
            pass

    @pytest.fixture(autouse=True)
    def setup_conn(self):
        self.conn = Mock(name='connection')
        self.conn.channels = {}
        self.channel_id = 1
        self.c = self.Channel(self.conn, self.channel_id)
        self.method = Mock(name='method')
        self.content = Mock(name='content')
        self.content.content_encoding = 'utf-8'
        self.c._METHODS = {(50, 61): self.method}

    def test_enter_exit(self):
        self.c.close = Mock(name='close')
        with self.c:
            pass
        self.c.close.assert_called_with()

    def test_send_method(self):
        self.c.send_method((50, 60), 'iB', (30, 0))
        self.conn.frame_writer.assert_called_with(
            1, self.channel_id, (50, 60), dumps('iB', (30, 0)), None,
        )

    def test_send_method__callback(self):
        callback = Mock(name='callback')
        p = promise(callback)
        self.c.send_method((50, 60), 'iB', (30, 0), callback=p)
        callback.assert_called_with()

    def test_send_method__wait(self):
        self.c.wait = Mock(name='wait')
        self.c.send_method((50, 60), 'iB', (30, 0), wait=(50, 61))
        self.c.wait.assert_called_with((50, 61), returns_tuple=False)

    def test_send_method__no_connection(self):
        self.c.connection = None
        with pytest.raises(RecoverableConnectionError):
            self.c.send_method((50, 60))

    def test_send_method__connection_dropped(self):
        self.c.connection.frame_writer.side_effect = StopIteration
        with pytest.raises(RecoverableConnectionError):
            self.c.send_method((50, 60))

    def test_close(self):
        with pytest.raises(NotImplementedError):
            self.c.close()

    def test_wait(self):
        with patch('amqp.abstract_channel.ensure_promise') as ensure_promise:
            p = ensure_promise.return_value
            p.ready = False

            def on_drain(*args, **kwargs):
                p.ready = True
            self.conn.drain_events.side_effect = on_drain

            p.value = (1,), {'arg': 2}
            self.c.wait((50, 61), timeout=1)
            self.conn.drain_events.assert_called_with(timeout=1)

            prev = self.c._pending[(50, 61)] = Mock(name='p2')
            p.value = None
            self.c.wait([(50, 61)])
            assert self.c._pending[(50, 61)] is prev

    def test_dispatch_method__content_encoding(self):
        self.c.auto_decode = True
        self.method.args = None
        self.c.dispatch_method((50, 61), 'payload', self.content)
        self.content.body.decode.side_effect = KeyError()
        self.c.dispatch_method((50, 61), 'payload', self.content)

    def test_dispatch_method__unknown_method(self):
        with pytest.raises(AMQPNotImplementedError):
            self.c.dispatch_method((100, 131), 'payload', self.content)

    def test_dispatch_method__one_shot(self):
        self.method.args = None
        p = self.c._pending[(50, 61)] = Mock(name='oneshot')
        self.c.dispatch_method((50, 61), 'payload', self.content)
        p.assert_called_with((50, 61), self.content)

    def test_dispatch_method__one_shot_no_content(self):
        self.method.args = None
        self.method.content = None
        p = self.c._pending[(50, 61)] = Mock(name='oneshot')
        self.c.dispatch_method((50, 61), 'payload', self.content)
        p.assert_called_with((50, 61))
        assert not self.c._pending

    def test_dispatch_method__listeners(self):
        with patch('amqp.abstract_channel.loads') as loads:
            loads.return_value = [1, 2, 3], 'foo'
            p = self.c._callbacks[(50, 61)] = Mock(name='p')
            self.c.dispatch_method((50, 61), 'payload', self.content)
            p.assert_called_with(1, 2, 3, self.content)

    def test_dispatch_method__listeners_and_one_shot(self):
        with patch('amqp.abstract_channel.loads') as loads:
            loads.return_value = [1, 2, 3], 'foo'
            p1 = self.c._callbacks[(50, 61)] = Mock(name='p')
            p2 = self.c._pending[(50, 61)] = Mock(name='oneshot')
            self.c.dispatch_method((50, 61), 'payload', self.content)
            p1.assert_called_with(1, 2, 3, self.content)
            p2.assert_called_with((50, 61), 1, 2, 3, self.content)
            assert not self.c._pending
            assert self.c._callbacks[(50, 61)]
