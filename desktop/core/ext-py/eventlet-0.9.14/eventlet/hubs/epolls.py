from eventlet import patcher
time = patcher.original('time')
select = patcher.original("select")
if hasattr(select, 'epoll'):
    epoll = select.epoll
else:
    try:
        # http://pypi.python.org/pypi/select26/
        from select26 import epoll
    except ImportError:
        try:
            import epoll as _epoll_mod
        except ImportError:
            raise ImportError(
                "No epoll implementation found in select module or PYTHONPATH")
        else:
            if hasattr(_epoll_mod, 'poll'):
                epoll = _epoll_mod.poll
            else:
                raise ImportError(
                    "You have an old, buggy epoll module in PYTHONPATH."
                    " Install http://pypi.python.org/pypi/python-epoll/"
                    " NOT http://pypi.python.org/pypi/pyepoll/. "
                    " easy_install pyepoll installs the wrong version.")

from eventlet.hubs.hub import BaseHub
from eventlet.hubs import poll
from eventlet.hubs.poll import READ, WRITE

# NOTE: we rely on the fact that the epoll flag constants
# are identical in value to the poll constants

class Hub(poll.Hub):
    def __init__(self, clock=time.time):
        BaseHub.__init__(self, clock)
        self.poll = epoll()
        try:
            # modify is required by select.epoll
            self.modify = self.poll.modify
        except AttributeError:
            self.modify = self.poll.register

    def add(self, evtype, fileno, cb):
        oldlisteners = bool(self.listeners[READ].get(fileno) or
                            self.listeners[WRITE].get(fileno))
        listener = BaseHub.add(self, evtype, fileno, cb)
        if not oldlisteners:
            # Means we've added a new listener
            self.register(fileno, new=True)
        else:
            self.register(fileno, new=False)
        return listener

    def do_poll(self, seconds):
        return self.poll.poll(seconds)
