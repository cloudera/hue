import sys
import traceback
import event
import types

from eventlet.support import greenlets as greenlet
import six
from eventlet.hubs.hub import BaseHub, READ, WRITE


class event_wrapper(object):

    def __init__(self, impl=None, seconds=None):
        self.impl = impl
        self.seconds = seconds

    def __repr__(self):
        if self.impl is not None:
            return repr(self.impl)
        else:
            return object.__repr__(self)

    def __str__(self):
        if self.impl is not None:
            return str(self.impl)
        else:
            return object.__str__(self)

    def cancel(self):
        if self.impl is not None:
            self.impl.delete()
            self.impl = None

    @property
    def pending(self):
        return bool(self.impl and self.impl.pending())


class Hub(BaseHub):

    SYSTEM_EXCEPTIONS = (KeyboardInterrupt, SystemExit)

    def __init__(self):
        super(Hub, self).__init__()
        event.init()

        self.signal_exc_info = None
        self.signal(
            2,
            lambda signalnum, frame: self.greenlet.parent.throw(KeyboardInterrupt))
        self.events_to_add = []

    def dispatch(self):
        loop = event.loop
        while True:
            for e in self.events_to_add:
                if e is not None and e.impl is not None and e.seconds is not None:
                    e.impl.add(e.seconds)
                    e.seconds = None
            self.events_to_add = []
            result = loop()

            if getattr(event, '__event_exc', None) is not None:
                # only have to do this because of bug in event.loop
                t = getattr(event, '__event_exc')
                setattr(event, '__event_exc', None)
                assert getattr(event, '__event_exc') is None
                six.reraise(t[0], t[1], t[2])

            if result != 0:
                return result

    def run(self):
        while True:
            try:
                self.dispatch()
            except greenlet.GreenletExit:
                break
            except self.SYSTEM_EXCEPTIONS:
                raise
            except:
                if self.signal_exc_info is not None:
                    self.schedule_call_global(
                        0, greenlet.getcurrent().parent.throw, *self.signal_exc_info)
                    self.signal_exc_info = None
                else:
                    self.squelch_timer_exception(None, sys.exc_info())

    def abort(self, wait=True):
        self.schedule_call_global(0, self.greenlet.throw, greenlet.GreenletExit)
        if wait:
            assert self.greenlet is not greenlet.getcurrent(
            ), "Can't abort with wait from inside the hub's greenlet."
            self.switch()

    def _getrunning(self):
        return bool(self.greenlet)

    def _setrunning(self, value):
        pass  # exists for compatibility with BaseHub
    running = property(_getrunning, _setrunning)

    def add(self, evtype, fileno, real_cb, real_tb, mac):
        # this is stupid: pyevent won't call a callback unless it's a function,
        # so we have to force it to be one here
        if isinstance(real_cb, types.BuiltinMethodType):
            def cb(_d):
                real_cb(_d)
        else:
            cb = real_cb

        if evtype is READ:
            evt = event.read(fileno, cb, fileno)
        elif evtype is WRITE:
            evt = event.write(fileno, cb, fileno)

        return super(Hub, self).add(evtype, fileno, evt, real_tb, mac)

    def signal(self, signalnum, handler):
        def wrapper():
            try:
                handler(signalnum, None)
            except:
                self.signal_exc_info = sys.exc_info()
                event.abort()
        return event_wrapper(event.signal(signalnum, wrapper))

    def remove(self, listener):
        super(Hub, self).remove(listener)
        listener.cb.delete()

    def remove_descriptor(self, fileno):
        for lcontainer in six.itervalues(self.listeners):
            listener = lcontainer.pop(fileno, None)
            if listener:
                try:
                    listener.cb.delete()
                except self.SYSTEM_EXCEPTIONS:
                    raise
                except:
                    traceback.print_exc()

    def schedule_call_local(self, seconds, cb, *args, **kwargs):
        current = greenlet.getcurrent()
        if current is self.greenlet:
            return self.schedule_call_global(seconds, cb, *args, **kwargs)
        event_impl = event.event(_scheduled_call_local, (cb, args, kwargs, current))
        wrapper = event_wrapper(event_impl, seconds=seconds)
        self.events_to_add.append(wrapper)
        return wrapper

    schedule_call = schedule_call_local

    def schedule_call_global(self, seconds, cb, *args, **kwargs):
        event_impl = event.event(_scheduled_call, (cb, args, kwargs))
        wrapper = event_wrapper(event_impl, seconds=seconds)
        self.events_to_add.append(wrapper)
        return wrapper

    def _version_info(self):
        baseversion = event.__version__
        return baseversion


def _scheduled_call(event_impl, handle, evtype, arg):
    cb, args, kwargs = arg
    try:
        cb(*args, **kwargs)
    finally:
        event_impl.delete()


def _scheduled_call_local(event_impl, handle, evtype, arg):
    cb, args, kwargs, caller_greenlet = arg
    try:
        if not caller_greenlet.dead:
            cb(*args, **kwargs)
    finally:
        event_impl.delete()
