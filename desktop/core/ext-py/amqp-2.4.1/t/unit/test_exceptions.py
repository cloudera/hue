from __future__ import absolute_import, unicode_literals

from case import Mock
import pytest

import amqp.exceptions
from amqp.exceptions import AMQPError, error_for_code

AMQP_EXCEPTIONS = (
    'ConnectionError', 'ChannelError',
    'RecoverableConnectionError', 'IrrecoverableConnectionError',
    'RecoverableChannelError', 'IrrecoverableChannelError',
    'ConsumerCancelled', 'ContentTooLarge', 'NoConsumers',
    'ConnectionForced', 'InvalidPath', 'AccessRefused', 'NotFound',
    'ResourceLocked', 'PreconditionFailed', 'FrameError', 'FrameSyntaxError',
    'InvalidCommand', 'ChannelNotOpen', 'UnexpectedFrame', 'ResourceError',
    'NotAllowed', 'AMQPNotImplementedError', 'InternalError',
)


class test_AMQPError:

    def test_str(self):
        assert str(AMQPError()) == '<AMQPError: unknown error>'
        x = AMQPError(method_sig=(50, 60))
        assert str(x) == '(50, 60): (0) None'
        x = AMQPError('Test Exception')
        assert str(x) == 'Test Exception'

    @pytest.mark.parametrize("amqp_exception", AMQP_EXCEPTIONS)
    def test_str_subclass(self, amqp_exception):
        exp = '<{}: unknown error>'.format(amqp_exception)
        exception_class = getattr(amqp.exceptions, amqp_exception)
        assert str(exception_class()) == exp


class test_error_for_code:

    def test_unknown_error(self):
        default = Mock(name='default')
        x = error_for_code(2134214314, 't', 'm', default)
        default.assert_called_with('t', 'm', reply_code=2134214314)
        assert x is default()
