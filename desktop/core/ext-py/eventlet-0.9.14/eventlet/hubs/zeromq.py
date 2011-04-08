from eventlet import patcher
from eventlet.green import zmq
from eventlet.hubs import _threadlocal
from eventlet.hubs.hub import BaseHub, READ, WRITE, noop
from eventlet.support import clear_sys_exc_info
import sys

time = patcher.original('time')
select = patcher.original('select')
sleep = time.sleep

EXC_MASK = zmq.POLLERR
READ_MASK = zmq.POLLIN
WRITE_MASK = zmq.POLLOUT

class Hub(BaseHub):
    def __init__(self, clock=time.time):
        BaseHub.__init__(self, clock)
        self.poll = zmq.Poller()

    def get_context(self, io_threads=1):
        """zmq's Context must be unique within a hub

        The zeromq API documentation states:
        All zmq sockets passed to the zmq_poll() function must share the same
        zmq context and must belong to the thread calling zmq_poll()

        As zmq_poll is what's eventually being called then we need to insure
        that all sockets that are going to be passed to zmq_poll (via
        hub.do_poll) are in the same context
        """
        try:
            return _threadlocal.context
        except AttributeError:
            _threadlocal.context = zmq._Context(io_threads)
            return _threadlocal.context

    def add(self, evtype, fileno, cb):
        listener = super(Hub, self).add(evtype, fileno, cb)
        self.register(fileno, new=True)
        return listener

    def remove(self, listener):
        super(Hub, self).remove(listener)
        self.register(listener.fileno)

    def register(self, fileno, new=False):
        mask = 0
        if self.listeners[READ].get(fileno):
            mask |= READ_MASK
        if self.listeners[WRITE].get(fileno):
            mask |= WRITE_MASK
        if mask:
            self.poll.register(fileno, mask)
        else:
            self.poll.unregister(fileno)

    def remove_descriptor(self, fileno):
        super(Hub, self).remove_descriptor(fileno)
        try:
            self.poll.unregister(fileno)
        except (KeyError, ValueError, IOError, OSError):
            # raised if we try to remove a fileno that was
            # already removed/invalid
            pass

    def do_poll(self, seconds):
        # zmq.Poller.poll expects milliseconds
        return self.poll.poll(seconds * 1000.0)

    def wait(self, seconds=None):
        readers = self.listeners[READ]
        writers = self.listeners[WRITE]

        if not readers and not writers:
            if seconds:
                sleep(seconds)
            return
        try:
            presult = self.do_poll(seconds)
        except zmq.ZMQError, e:
            # In the poll hub this part exists to special case some exceptions
            # from socket. There may be some error numbers that wider use of
            # this hub will throw up as needing special treatment so leaving
            # this block and this comment as a remineder
            raise
        SYSTEM_EXCEPTIONS = self.SYSTEM_EXCEPTIONS

        if self.debug_blocking:
            self.block_detect_pre()

        for fileno, event in presult:
            try:
                if event & READ_MASK:
                    readers.get(fileno, noop).cb(fileno)
                if event & WRITE_MASK:
                    writers.get(fileno, noop).cb(fileno)
                if event & EXC_MASK:
                    # zmq.POLLERR is returned for any error condition in the
                    # underlying fd (as passed through to poll/epoll)
                    readers.get(fileno, noop).cb(fileno)
                    writers.get(fileno, noop).cb(fileno)
            except SYSTEM_EXCEPTIONS:
                raise
            except:
                self.squelch_exception(fileno, sys.exc_info())
                clear_sys_exc_info()

        if self.debug_blocking:
            self.block_detect_post()
