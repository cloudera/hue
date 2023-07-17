from eventlet import patcher
from eventlet.green import asyncore
from eventlet.green import asynchat
from eventlet.green import socket
from eventlet.green import thread
from eventlet.green import threading
from eventlet.green import time

patcher.inject(
    "test.test_asynchat",
    globals(),
    ('asyncore', asyncore),
    ('asynchat', asynchat),
    ('socket', socket),
    ('thread', thread),
    ('threading', threading),
    ('time', time))

if __name__ == "__main__":
    test_main()
