from eventlet import patcher
from eventlet.green import httplib
from eventlet.green import socket

patcher.inject(
    'test.test_httplib',
    globals(),
    ('httplib', httplib),
    ('socket', socket))

if __name__ == "__main__":
    test_main()
