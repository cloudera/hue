from eventlet import patcher
from eventlet.green import socket
from eventlet.green import SocketServer
from eventlet.support import six

patcher.inject(
    'BaseHTTPServer' if six.PY2 else 'http.server',
    globals(),
    ('socket', socket),
    ('SocketServer', SocketServer),
    ('socketserver', SocketServer))

del patcher

if __name__ == '__main__':
    test()
