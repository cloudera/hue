import errno
from eventlet.support import get_errno
from eventlet import patcher
select = patcher.original('select')
if not hasattr(select, 'epoll'):
    # TODO: remove mention of python-epoll on 2019-01
    raise ImportError('No epoll implementation found in select module.'
                      ' python-epoll (or similar) package support was removed,'
                      ' please open issue on https://github.com/eventlet/eventlet/'
                      ' if you must use epoll outside stdlib.')
epoll = select.epoll

from eventlet.hubs.hub import BaseHub
from eventlet.hubs import poll
from eventlet.hubs.poll import READ, WRITE

# NOTE: we rely on the fact that the epoll flag constants
# are identical in value to the poll constants


class Hub(poll.Hub):
    def __init__(self, clock=None):
        BaseHub.__init__(self, clock)
        self.poll = epoll()

    def add(self, evtype, fileno, cb, tb, mac):
        oldlisteners = bool(self.listeners[READ].get(fileno) or
                            self.listeners[WRITE].get(fileno))
        listener = BaseHub.add(self, evtype, fileno, cb, tb, mac)
        try:
            if not oldlisteners:
                # Means we've added a new listener
                self.register(fileno, new=True)
            else:
                self.register(fileno, new=False)
        except IOError as ex:    # ignore EEXIST, #80
            if get_errno(ex) != errno.EEXIST:
                raise
        return listener

    def do_poll(self, seconds):
        return self.poll.poll(seconds)
