from eventlet import patcher

from eventlet.green import BaseHTTPServer
from eventlet.green import threading
from eventlet.green import socket
from eventlet.green import urllib2

patcher.inject(
    'test.test_urllib2_localnet',
    globals(),
    ('BaseHTTPServer', BaseHTTPServer),
    ('threading', threading),
    ('socket', socket),
    ('urllib2', urllib2))

if __name__ == "__main__":
    test_main()
