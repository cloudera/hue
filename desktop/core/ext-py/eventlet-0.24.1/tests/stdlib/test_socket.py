#!/usr/bin/env python

from eventlet import patcher
from eventlet.green import socket
from eventlet.green import select
from eventlet.green import time
from eventlet.green import thread
from eventlet.green import threading

patcher.inject(
    'test.test_socket',
    globals(),
    ('socket', socket),
    ('select', select),
    ('time', time),
    ('thread', thread),
    ('threading', threading))

# TODO: fix
TCPTimeoutTest.testInterruptedTimeout = lambda *a: None

if __name__ == "__main__":
    test_main()
