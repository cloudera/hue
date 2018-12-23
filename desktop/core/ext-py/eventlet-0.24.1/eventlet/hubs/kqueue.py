import os
import sys
from eventlet import patcher, support
import six
select = patcher.original('select')
time = patcher.original('time')

from eventlet.hubs.hub import BaseHub, READ, WRITE, noop


if getattr(select, 'kqueue', None) is None:
    raise ImportError('No kqueue implementation found in select module')


FILTERS = {READ: select.KQ_FILTER_READ,
           WRITE: select.KQ_FILTER_WRITE}


class Hub(BaseHub):
    MAX_EVENTS = 100

    def __init__(self, clock=None):
        super(Hub, self).__init__(clock)
        self._events = {}
        self._init_kqueue()

    def _init_kqueue(self):
        self.kqueue = select.kqueue()
        self._pid = os.getpid()

    def _reinit_kqueue(self):
        self.kqueue.close()
        self._init_kqueue()
        kqueue = self.kqueue
        events = [e for i in six.itervalues(self._events)
                  for e in six.itervalues(i)]
        kqueue.control(events, 0, 0)

    def _control(self, events, max_events, timeout):
        try:
            return self.kqueue.control(events, max_events, timeout)
        except (OSError, IOError):
            # have we forked?
            if os.getpid() != self._pid:
                self._reinit_kqueue()
                return self.kqueue.control(events, max_events, timeout)
            raise

    def add(self, evtype, fileno, cb, tb, mac):
        listener = super(Hub, self).add(evtype, fileno, cb, tb, mac)
        events = self._events.setdefault(fileno, {})
        if evtype not in events:
            try:
                event = select.kevent(fileno, FILTERS.get(evtype), select.KQ_EV_ADD)
                self._control([event], 0, 0)
                events[evtype] = event
            except ValueError:
                super(Hub, self).remove(listener)
                raise
        return listener

    def _delete_events(self, events):
        del_events = [
            select.kevent(e.ident, e.filter, select.KQ_EV_DELETE)
            for e in events
        ]
        self._control(del_events, 0, 0)

    def remove(self, listener):
        super(Hub, self).remove(listener)
        evtype = listener.evtype
        fileno = listener.fileno
        if not self.listeners[evtype].get(fileno):
            event = self._events[fileno].pop(evtype, None)
            if event is None:
                return
            try:
                self._delete_events((event,))
            except OSError:
                pass

    def remove_descriptor(self, fileno):
        super(Hub, self).remove_descriptor(fileno)
        try:
            events = self._events.pop(fileno).values()
            self._delete_events(events)
        except KeyError:
            pass
        except OSError:
            pass

    def wait(self, seconds=None):
        readers = self.listeners[READ]
        writers = self.listeners[WRITE]

        if not readers and not writers:
            if seconds:
                time.sleep(seconds)
            return
        result = self._control([], self.MAX_EVENTS, seconds)
        SYSTEM_EXCEPTIONS = self.SYSTEM_EXCEPTIONS
        for event in result:
            fileno = event.ident
            evfilt = event.filter
            try:
                if evfilt == FILTERS[READ]:
                    readers.get(fileno, noop).cb(fileno)
                if evfilt == FILTERS[WRITE]:
                    writers.get(fileno, noop).cb(fileno)
            except SYSTEM_EXCEPTIONS:
                raise
            except:
                self.squelch_exception(fileno, sys.exc_info())
                support.clear_sys_exc_info()
