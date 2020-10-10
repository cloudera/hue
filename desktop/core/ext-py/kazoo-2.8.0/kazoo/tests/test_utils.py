import unittest

from mock import patch
import pytest

try:
    from kazoo.handlers.eventlet import green_socket as socket

    EVENTLET_HANDLER_AVAILABLE = True
except ImportError:
    EVENTLET_HANDLER_AVAILABLE = False


class TestCreateTCPConnection(unittest.TestCase):
    def test_timeout_arg(self):
        from kazoo.handlers import utils
        from kazoo.handlers.utils import create_tcp_connection, socket, time

        with patch.object(socket, 'create_connection') as create_connection:
            with patch.object(utils, '_set_default_tcpsock_options'):
                # Ensure a gap between calls to time.time() does not result in
                # create_connection being called with a negative timeout
                # argument.
                with patch.object(time, 'time', side_effect=range(10)):
                    create_tcp_connection(socket, ('127.0.0.1', 2181),
                                          timeout=1.5)

                for call_args in create_connection.call_args_list:
                    timeout = call_args[0][1]
                    assert timeout >= 0, 'socket timeout must be nonnegative'

    def test_timeout_arg_eventlet(self):
        if not EVENTLET_HANDLER_AVAILABLE:
            pytest.skip('eventlet handler not available.')

        from kazoo.handlers import utils
        from kazoo.handlers.utils import create_tcp_connection, time

        with patch.object(socket, 'create_connection') as create_connection:
            with patch.object(utils, '_set_default_tcpsock_options'):
                # Ensure a gap between calls to time.time() does not result in
                # create_connection being called with a negative timeout
                # argument.
                with patch.object(time, 'time', side_effect=range(10)):
                    create_tcp_connection(socket, ('127.0.0.1', 2181),
                                          timeout=1.5)

                for call_args in create_connection.call_args_list:
                    timeout = call_args[0][1]
                    assert timeout >= 0, 'socket timeout must be nonnegative'

    def test_slow_connect(self):
        # Currently, create_tcp_connection will raise a socket timeout if it
        # takes longer than the specified "timeout" to create a connection.
        # In the future, "timeout" might affect only the created socket and not
        # the time it takes to create it.
        from kazoo.handlers.utils import create_tcp_connection, socket, time

        # Simulate a second passing between calls to check the current time.
        with patch.object(time, 'time', side_effect=range(10)):
            with pytest.raises(socket.error):
                create_tcp_connection(socket, ('127.0.0.1', 2181), timeout=0.5)

    def test_negative_timeout(self):
        from kazoo.handlers.utils import create_tcp_connection, socket

        with pytest.raises(socket.error):
            create_tcp_connection(socket, ('127.0.0.1', 2181), timeout=-1)

    def test_zero_timeout(self):
        # Rather than pass '0' through as a timeout to
        # socket.create_connection, create_tcp_connection should raise
        # socket.error. This is because the socket library treats '0' as an
        # indicator to create a non-blocking socket.
        from kazoo.handlers.utils import create_tcp_connection, socket, time

        # Simulate no time passing between calls to check the current time.
        with patch.object(time, 'time', return_value=time.time()):
            with pytest.raises(socket.error):
                create_tcp_connection(socket, ('127.0.0.1', 2181), timeout=0)
