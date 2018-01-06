from eventlet import patcher
from eventlet.green import select
from eventlet.green import socket
from eventlet.green import time

patcher.inject(
    "asyncore",
    globals(),
    ('select', select),
    ('socket', socket),
    ('time', time))

del patcher
