from eventlet import patcher
from eventlet.green import socket
from eventlet.green import time

patcher.inject(
    'test.test_timeout',
    globals(),
    ('socket', socket),
    ('time', time))

# to get past the silly 'requires' check
from test import test_support
test_support.use_resources = ['network']

if __name__ == "__main__":
    test_main()
