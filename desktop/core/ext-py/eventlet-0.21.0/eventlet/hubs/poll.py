import errno
import sys

from eventlet import patcher
select = patcher.original('select')
time = patcher.original('time')

from eventlet.hubs.hub import BaseHub, READ, WRITE, noop
from eventlet.support import get_errno, clear_sys_exc_info

EXC_MASK = select.POLLERR | select.POLLHUP
READ_MASK = select.POLLIN | select.POLLPRI
WRITE_MASK = select.POLLOUT


class Hub(BaseHub):
    def __init__(self, clock=None):
        super(Hub, self).__init__(clock)
        self.poll = select.poll()
        # poll.modify is new to 2.6
        try:
            self.modify = self.poll.modify
        except AttributeError:
            self.modify = self.poll.register

    def add(self, evtype, fileno, cb, tb, mac):
        listener = super(Hub, self).add(evtype, fileno, cb, tb, mac)
        self.register(fileno, new=True)
        return listener

    def remove(self, listener):
        super(Hub, self).remove(listener)
        self.register(listener.fileno)

    def register(self, fileno, new=False):
        mask = 0
        if self.listeners[READ].get(fileno):
            mask |= READ_MASK | EXC_MASK
        if self.listeners[WRITE].get(fileno):
            mask |= WRITE_MASK | EXC_MASK
        try:
            if mask:
                if new:
                    self.poll.register(fileno, mask)
                else:
                    try:
                        self.modify(fileno, mask)
                    except (IOError, OSError):
                        self.poll.register(fileno, mask)
            else:
                try:
                    self.poll.unregister(fileno)
                except (KeyError, IOError, OSError):
                    # raised if we try to remove a fileno that was
                    # already removed/invalid
                    pass
        except ValueError:
            # fileno is bad, issue 74
            self.remove_descriptor(fileno)
            raise

    def remove_descriptor(self, fileno):
        super(Hub, self).remove_descriptor(fileno)
        try:
            self.poll.unregister(fileno)
        except (KeyError, ValueError, IOError, OSError):
            # raised if we try to remove a fileno that was
            # already removed/invalid
            pass

    def do_poll(self, seconds):
        # poll.poll expects integral milliseconds
        return self.poll.poll(int(seconds * 1000.0))

    def wait(self, seconds=None):
        readers = self.listeners[READ]
        writers = self.listeners[WRITE]

        if not readers and not writers:
            if seconds:
                time.sleep(seconds)
            return
        try:
            presult = self.do_poll(seconds)
        except (IOError, select.error) as e:
            if get_errno(e) == errno.EINTR:
                return
            raise
        SYSTEM_EXCEPTIONS = self.SYSTEM_EXCEPTIONS

        if self.debug_blocking:
            self.block_detect_pre()

        # Accumulate the listeners to call back to prior to
        # triggering any of them. This is to keep the set
        # of callbacks in sync with the events we've just
        # polled for. It prevents one handler from invalidating
        # another.
        callbacks = set()
        for fileno, event in presult:
            if event & READ_MASK:
                callbacks.add((readers.get(fileno, noop), fileno))
            if event & WRITE_MASK:
                callbacks.add((writers.get(fileno, noop), fileno))
            if event & select.POLLNVAL:
                self.remove_descriptor(fileno)
                continue
            if event & EXC_MASK:
                callbacks.add((readers.get(fileno, noop), fileno))
                callbacks.add((writers.get(fileno, noop), fileno))

        for listener, fileno in callbacks:
            try:
                listener.cb(fileno)
            except SYSTEM_EXCEPTIONS:
                raise
            except:
                self.squelch_exception(fileno, sys.exc_info())
                clear_sys_exc_info()

        if self.debug_blocking:
            self.block_detect_post()
