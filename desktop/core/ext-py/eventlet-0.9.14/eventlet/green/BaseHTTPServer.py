from eventlet import patcher
from eventlet.green import socket
from eventlet.green import SocketServer

patcher.inject('BaseHTTPServer',
    globals(),
    ('socket', socket),
    ('SocketServer', SocketServer))

del patcher

if __name__ == '__main__':
    test()
