#
# Analogue of `processing.connection` which uses queues instead of sockets
#
# processing/dummy/connection.py
#
# Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'Client', 'Listener', 'Pipe' ]

from Queue import Queue


families = [None]
connections_are_picklable = True


class Listener(object):

    def __init__(self, address=None, family=None, backlog=1):
        self._backlog_queue = Queue(backlog)

    def accept(self):
        return Connection(*self._backlog_queue.get())

    def close(self):
        self._backlog_queue = None

    address = property(lambda self: self._backlog_queue)


def Client(address):
    _in, _out = Queue(), Queue()
    address.put((_out, _in))
    return Connection(_in, _out)


def Pipe(duplex=True):
    a, b = Queue(), Queue()
    return Connection(a, b), Connection(b, a)


class Connection(object):

    def __init__(self, _in, _out):
        self._out = _out
        self._in = _in
        self.send = self.sendbytes = self.sendBytes = _out.put
        self.recv = self.recvbytes = self.recvBytes = _in.get

    def poll(self, timeout=0.0):
        if not self._in.empty():
            return True
        if timeout <= 0.0:
            return False
        self._in.not_empty.acquire()
        self._in.not_empty.wait(timeout)
        self._in.not_empty.release()
        return not self._in.empty()

    def close(self):
        pass
