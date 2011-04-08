import warnings
warnings.warn("The proc module is deprecated!  Please use the greenthread " 
              "module, or any of the many other Eventlet cross-coroutine "
              "primitives, instead.",
               DeprecationWarning, stacklevel=2)

"""
This module provides means to spawn, kill and link coroutines. Linking means
subscribing to the coroutine's result, either in form of return value or
unhandled exception.

To create a linkable coroutine use spawn function provided by this module:

    >>> def demofunc(x, y):
    ...    return x / y
    >>> p = spawn(demofunc, 6, 2)

The return value of :func:`spawn` is an instance of :class:`Proc` class that
you can "link":

 * ``p.link(obj)`` - notify *obj* when the coroutine is finished

What "notify" means here depends on the type of *obj*: a callable is simply
called, an :class:`~eventlet.coros.Event` or a :class:`~eventlet.coros.queue`
is notified using ``send``/``send_exception`` methods and if *obj* is another
greenlet it's killed with :class:`LinkedExited` exception.

Here's an example:

>>> event = coros.Event()
>>> _ = p.link(event)
>>> event.wait()
3

Now, even though *p* is finished it's still possible to link it. In this
case the notification is performed immediatelly:

>>> try:
...     p.link()
... except LinkedCompleted:
...     print 'LinkedCompleted'
LinkedCompleted

(Without an argument, the link is created to the current greenlet)

There are also :meth:`~eventlet.proc.Source.link_value` and
:func:`link_exception` methods that only deliver a return value and an
unhandled exception respectively (plain :meth:`~eventlet.proc.Source.link`
delivers both).  Suppose we want to spawn a greenlet to do an important part of
the task; if it fails then there's no way to complete the task so the parent
must fail as well; :meth:`~eventlet.proc.Source.link_exception` is useful here:

>>> p = spawn(demofunc, 1, 0)
>>> _ = p.link_exception()
>>> try:
...     api.sleep(1)
... except LinkedFailed:
...     print 'LinkedFailed'
LinkedFailed

One application of linking is :func:`waitall` function: link to a bunch of
coroutines and wait for all them to complete. Such a function is provided by
this module.
"""
import sys
from eventlet import api, coros, hubs

__all__ = ['LinkedExited',
           'LinkedFailed',
           'LinkedCompleted',
           'LinkedKilled',
           'ProcExit',
           'Link',
           'waitall',
           'killall',
           'Source',
           'Proc',
           'spawn',
           'spawn_link',
           'spawn_link_value',
           'spawn_link_exception']


class LinkedExited(Exception):
    """Raised when a linked proc exits"""
    msg = "%r exited"

    def __init__(self, name=None, msg=None):
        self.name = name
        if msg is None:
            msg = self.msg % self.name
        Exception.__init__(self, msg)

class LinkedCompleted(LinkedExited):
    """Raised when a linked proc finishes the execution cleanly"""

    msg = "%r completed successfully"

class LinkedFailed(LinkedExited):
    """Raised when a linked proc dies because of unhandled exception"""
    msg = "%r failed with %s"

    def __init__(self, name, typ, value=None, tb=None):
        msg = self.msg % (name, typ.__name__)
        LinkedExited.__init__(self, name, msg)

class LinkedKilled(LinkedFailed):
    """Raised when a linked proc dies because of unhandled GreenletExit
    (i.e. it was killed)
    """
    msg = """%r was killed with %s"""

def getLinkedFailed(name, typ, value=None, tb=None):
    if issubclass(typ, api.GreenletExit):
        return LinkedKilled(name, typ, value, tb)
    return LinkedFailed(name, typ, value, tb)


class ProcExit(api.GreenletExit):
    """Raised when this proc is killed."""


class Link(object):
    """
    A link to a greenlet, triggered when the greenlet exits.
    """

    def __init__(self, listener):
        self.listener = listener

    def cancel(self):
        self.listener = None

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.cancel()

class LinkToEvent(Link):

    def __call__(self, source):
        if self.listener is None:
            return
        if source.has_value():
            self.listener.send(source.value)
        else:
            self.listener.send_exception(*source.exc_info())

class LinkToGreenlet(Link):

    def __call__(self, source):
        if source.has_value():
            self.listener.throw(LinkedCompleted(source.name))
        else:
            self.listener.throw(getLinkedFailed(source.name, *source.exc_info()))

class LinkToCallable(Link):

    def __call__(self, source):
        self.listener(source)


def waitall(lst, trap_errors=False, queue=None):
    if queue is None:
        queue = coros.queue()
    index = -1
    for (index, linkable) in enumerate(lst):
        linkable.link(decorate_send(queue, index))
    len = index + 1
    results = [None] * len
    count = 0
    while count < len:
        try:
            index, value = queue.wait()
        except Exception:
            if not trap_errors:
                raise
        else:
            results[index] = value
        count += 1
    return results


class decorate_send(object):

    def __init__(self, event, tag):
        self._event = event
        self._tag = tag

    def __repr__(self):
        params = (type(self).__name__, self._tag, self._event)
        return '<%s tag=%r event=%r>' % params

    def __getattr__(self, name):
        assert name != '_event'
        return getattr(self._event, name)

    def send(self, value):
        self._event.send((self._tag, value))


def killall(procs, *throw_args, **kwargs):
    if not throw_args:
        throw_args = (ProcExit, )
    wait = kwargs.pop('wait', False)
    if kwargs:
        raise TypeError('Invalid keyword argument for proc.killall(): %s' % ', '.join(kwargs.keys()))
    for g in procs:
        if not g.dead:
            hubs.get_hub().schedule_call_global(0, g.throw, *throw_args)
    if wait and api.getcurrent() is not hubs.get_hub().greenlet:
        api.sleep(0)


class NotUsed(object):

    def __str__(self):
        return '<Source instance does not hold a value or an exception>'

    __repr__ = __str__

_NOT_USED = NotUsed()


def spawn_greenlet(function, *args):
    """Create a new greenlet that will run ``function(*args)``.
    The current greenlet won't be unscheduled. Keyword arguments aren't
    supported (limitation of greenlet), use :func:`spawn` to work around that.
    """
    g = api.Greenlet(function)
    g.parent = hubs.get_hub().greenlet
    hubs.get_hub().schedule_call_global(0, g.switch, *args)
    return g


class Source(object):
    """Maintain a set of links to the listeners. Delegate the sent value or
    the exception to all of them.

    To set up a link, use :meth:`link_value`, :meth:`link_exception` or
    :meth:`link` method. The latter establishes both "value" and "exception"
    link. It is possible to link to events, queues, greenlets and callables.

    >>> source = Source()
    >>> event = coros.Event()
    >>> _ = source.link(event)

    Once source's :meth:`send` or :meth:`send_exception` method is called, all
    the listeners with the right type of link will be notified ("right type"
    means that exceptions won't be delivered to "value" links and values won't
    be delivered to "exception" links). Once link has been fired it is removed.

    Notifying listeners is performed in the **mainloop** greenlet. Under the
    hood notifying a link means executing a callback, see :class:`Link` class
    for details. Notification *must not* attempt to switch to the hub, i.e.
    call any blocking functions.

    >>> source.send('hello')
    >>> event.wait()
    'hello'

    Any error happened while sending will be logged as a regular unhandled
    exception. This won't prevent other links from being fired.

    There 3 kinds of listeners supported:

     1. If *listener* is a greenlet (regardless if it's a raw greenlet or an
        extension like :class:`Proc`), a subclass of :class:`LinkedExited`
        exception is raised in it.

     2. If *listener* is something with send/send_exception methods (event,
        queue, :class:`Source` but not :class:`Proc`) the relevant method is
        called.

     3. If *listener* is a callable, it is called with 1 argument (the result)
        for "value" links and with 3 arguments ``(typ, value, tb)`` for
        "exception" links.
    """

    def __init__(self, name=None):
        self.name = name
        self._value_links = {}
        self._exception_links = {}
        self.value = _NOT_USED
        self._exc = None

    def _repr_helper(self):
        result = []
        result.append(repr(self.name))
        if self.value is not _NOT_USED:
            if self._exc is None:
                res = repr(self.value)
                if len(res)>50:
                    res = res[:50]+'...'
                result.append('result=%s' % res)
            else:
                result.append('raised=%s' % (self._exc, ))
        result.append('{%s:%s}' % (len(self._value_links), len(self._exception_links)))
        return result

    def __repr__(self):
        klass = type(self).__name__
        return '<%s at %s %s>' % (klass, hex(id(self)), ' '.join(self._repr_helper()))

    def ready(self):
        return self.value is not _NOT_USED

    def has_value(self):
        return self.value is not _NOT_USED and self._exc is None

    def has_exception(self):
        return self.value is not _NOT_USED and self._exc is not None

    def exc_info(self):
        if not self._exc:
            return (None, None, None)
        elif len(self._exc)==3:
            return self._exc
        elif len(self._exc)==1:
            if isinstance(self._exc[0], type):
                return self._exc[0], None, None
            else:
                return self._exc[0].__class__, self._exc[0], None
        elif len(self._exc)==2:
            return self._exc[0], self._exc[1], None
        else:
            return self._exc

    def link_value(self, listener=None, link=None):
        if self.ready() and self._exc is not None:
            return
        if listener is None:
            listener = api.getcurrent()
        if link is None:
            link = self.getLink(listener)
        if self.ready() and listener is api.getcurrent():
            link(self)
        else:
            self._value_links[listener] = link
            if self.value is not _NOT_USED:
                self._start_send()
        return link

    def link_exception(self, listener=None, link=None):
        if self.value is not _NOT_USED and self._exc is None:
            return
        if listener is None:
            listener = api.getcurrent()
        if link is None:
            link = self.getLink(listener)
        if self.ready() and listener is api.getcurrent():
            link(self)
        else:
            self._exception_links[listener] = link
            if self.value is not _NOT_USED:
                self._start_send_exception()
        return link

    def link(self, listener=None, link=None):
        if listener is None:
            listener = api.getcurrent()
        if link is None:
            link = self.getLink(listener)
        if self.ready() and listener is api.getcurrent():
            if self._exc is None:
                link(self)
            else:
                link(self)
        else:
            self._value_links[listener] = link
            self._exception_links[listener] = link
            if self.value is not _NOT_USED:
                if self._exc is None:
                    self._start_send()
                else:
                    self._start_send_exception()
        return link

    def unlink(self, listener=None):
        if listener is None:
            listener = api.getcurrent()
        self._value_links.pop(listener, None)
        self._exception_links.pop(listener, None)

    @staticmethod
    def getLink(listener):
        if hasattr(listener, 'throw'):
            return LinkToGreenlet(listener)
        if hasattr(listener, 'send'):
            return LinkToEvent(listener)
        elif hasattr(listener, '__call__'):
            return LinkToCallable(listener)
        else:
            raise TypeError("Don't know how to link to %r" % (listener, ))

    def send(self, value):
        assert not self.ready(), "%s has been fired already" % self
        self.value = value
        self._exc = None
        self._start_send()

    def _start_send(self):
        hubs.get_hub().schedule_call_global(0, self._do_send, self._value_links.items(), self._value_links)

    def send_exception(self, *throw_args):
        assert not self.ready(), "%s has been fired already" % self
        self.value = None
        self._exc = throw_args
        self._start_send_exception()

    def _start_send_exception(self):
        hubs.get_hub().schedule_call_global(0, self._do_send, self._exception_links.items(), self._exception_links)

    def _do_send(self, links, consult):
        while links:
            listener, link = links.pop()
            try:
                if listener in consult:
                    try:
                        link(self)
                    finally:
                        consult.pop(listener, None)
            except:
                hubs.get_hub().schedule_call_global(0, self._do_send, links, consult)
                raise

    def wait(self, timeout=None, *throw_args):
        """Wait until :meth:`send` or :meth:`send_exception` is called or
        *timeout* has expired. Return the argument of :meth:`send` or raise the
        argument of :meth:`send_exception`. If *timeout* has expired, ``None``
        is returned.

        The arguments, when provided, specify how many seconds to wait and what
        to do when *timeout* has expired. They are treated the same way as
        :func:`~eventlet.api.timeout` treats them.
        """
        if self.value is not _NOT_USED:
            if self._exc is None:
                return self.value
            else:
                api.getcurrent().throw(*self._exc)
        if timeout is not None:
            timer = api.timeout(timeout, *throw_args)
            timer.__enter__()
            if timeout==0:
                if timer.__exit__(None, None, None):
                    return
                else:
                    try:
                        api.getcurrent().throw(*timer.throw_args)
                    except:
                        if not timer.__exit__(*sys.exc_info()):
                            raise
                    return
            EXC = True
        try:
            try:
                waiter = Waiter()
                self.link(waiter)
                try:
                    return waiter.wait()
                finally:
                    self.unlink(waiter)
            except:
                EXC = False
                if timeout is None or not timer.__exit__(*sys.exc_info()):
                    raise
        finally:
            if timeout is not None and EXC:
                timer.__exit__(None, None, None)


class Waiter(object):

    def __init__(self):
        self.greenlet = None

    def send(self, value):
        """Wake up the greenlet that is calling wait() currently (if there is one).
        Can only be called from get_hub().greenlet.
        """
        assert api.getcurrent() is hubs.get_hub().greenlet
        if self.greenlet is not None:
            self.greenlet.switch(value)

    def send_exception(self, *throw_args):
        """Make greenlet calling wait() wake up (if there is a wait()).
        Can only be called from get_hub().greenlet.
        """
        assert api.getcurrent() is hubs.get_hub().greenlet
        if self.greenlet is not None:
            self.greenlet.throw(*throw_args)

    def wait(self):
        """Wait until send or send_exception is called. Return value passed
        into send() or raise exception passed into send_exception().
        """
        assert self.greenlet is None
        current = api.getcurrent()
        assert current is not hubs.get_hub().greenlet
        self.greenlet = current
        try:
            return hubs.get_hub().switch()
        finally:
            self.greenlet = None


class Proc(Source):
    """A linkable coroutine based on Source.
    Upon completion, delivers coroutine's result to the listeners.
    """

    def __init__(self, name=None):
        self.greenlet = None
        Source.__init__(self, name)

    def _repr_helper(self):
        if self.greenlet is not None and self.greenlet.dead:
            dead = '(dead)'
        else:
            dead = ''
        return ['%r%s' % (self.greenlet, dead)] + Source._repr_helper(self)

    def __repr__(self):
        klass = type(self).__name__
        return '<%s %s>' % (klass, ' '.join(self._repr_helper()))

    def __nonzero__(self):
        if self.ready():
            # with current _run this does not makes any difference
            # still, let keep it there
            return False
        # otherwise bool(proc) is the same as bool(greenlet)
        if self.greenlet is not None:
            return bool(self.greenlet)

    @property
    def dead(self):
        return self.ready() or self.greenlet.dead

    @classmethod
    def spawn(cls, function, *args, **kwargs):
        """Return a new :class:`Proc` instance that is scheduled to execute
        ``function(*args, **kwargs)`` upon the next hub iteration.
        """
        proc = cls()
        proc.run(function, *args, **kwargs)
        return proc

    def run(self, function, *args, **kwargs):
        """Create a new greenlet to execute ``function(*args, **kwargs)``.
        The created greenlet is scheduled to run upon the next hub iteration.
        """
        assert self.greenlet is None, "'run' can only be called once per instance"
        if self.name is None:
            self.name = str(function)
        self.greenlet = spawn_greenlet(self._run, function, args, kwargs)

    def _run(self, function, args, kwargs):
        """Internal top level function.
        Execute *function* and send its result to the listeners.
        """
        try:
            result = function(*args, **kwargs)
        except:
            self.send_exception(*sys.exc_info())
            raise # let mainloop log the exception
        else:
            self.send(result)

    def throw(self, *throw_args):
        """Used internally to raise the exception.

        Behaves exactly like greenlet's 'throw' with the exception that
        :class:`ProcExit` is raised by default. Do not use this function as it
        leaves the current greenlet unscheduled forever. Use :meth:`kill`
        method instead.
        """
        if not self.dead:
            if not throw_args:
                throw_args = (ProcExit, )
            self.greenlet.throw(*throw_args)

    def kill(self, *throw_args):
        """
        Raise an exception in the greenlet. Unschedule the current greenlet so
        that this :class:`Proc` can handle the exception (or die).

        The exception can be specified with *throw_args*. By default,
        :class:`ProcExit` is raised.
        """
        if not self.dead:
            if not throw_args:
                throw_args = (ProcExit, )
            hubs.get_hub().schedule_call_global(0, self.greenlet.throw, *throw_args)
            if api.getcurrent() is not hubs.get_hub().greenlet:
                api.sleep(0)

    # QQQ maybe Proc should not inherit from Source (because its send() and send_exception()
    # QQQ methods are for internal use only)


spawn = Proc.spawn

def spawn_link(function, *args, **kwargs):
    p = spawn(function, *args, **kwargs)
    p.link()
    return p

def spawn_link_value(function, *args, **kwargs):
    p = spawn(function, *args, **kwargs)
    p.link_value()
    return p

def spawn_link_exception(function, *args, **kwargs):
    p = spawn(function, *args, **kwargs)
    p.link_exception()
    return p



class wrap_errors(object):
    """Helper to make function return an exception, rather than raise it.

    Because every exception that is unhandled by greenlet will be logged by the hub,
    it is desirable to prevent non-error exceptions from leaving a greenlet.
    This can done with simple try/except construct:

    def func1(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (A, B, C), ex:
            return ex

    wrap_errors provides a shortcut to write that in one line:

    func1 = wrap_errors((A, B, C), func)

    It also preserves __str__ and __repr__ of the original function.
    """

    def __init__(self, errors, func):
        """Make a new function from `func', such that it catches `errors' (an
        Exception subclass, or a tuple of Exception subclasses) and return
        it as a value.
        """
        self.errors = errors
        self.func = func

    def __call__(self, *args, **kwargs):
        try:
            return self.func(*args, **kwargs)
        except self.errors, ex:
            return ex

    def __str__(self):
        return str(self.func)

    def __repr__(self):
        return repr(self.func)

    def __getattr__(self, item):
        return getattr(self.func, item)


class RunningProcSet(object):
    """
    Maintain a set of :class:`Proc` s that are still running, that is,
    automatically remove a proc when it's finished. Provide a way to wait/kill
    all of them
    """

    def __init__(self, *args):
        self.procs = set(*args)
        if args:
            for p in self.args[0]:
                p.link(lambda p: self.procs.discard(p))

    def __len__(self):
        return len(self.procs)

    def __contains__(self, item):
        if isinstance(item, api.Greenlet):
            # special case for "api.getcurrent() in running_proc_set" to work
            for x in self.procs:
                if x.greenlet == item:
                    return True
        else:
            return item in self.procs

    def __iter__(self):
        return iter(self.procs)

    def add(self, p):
        self.procs.add(p)
        p.link(lambda p: self.procs.discard(p))

    def spawn(self, func, *args, **kwargs):
        p = spawn(func, *args, **kwargs)
        self.add(p)
        return p

    def waitall(self, trap_errors=False):
        while self.procs:
            waitall(self.procs, trap_errors=trap_errors)

    def killall(self, *throw_args, **kwargs):
        return killall(self.procs, *throw_args, **kwargs)


class Pool(object):

    linkable_class = Proc

    def __init__(self, limit):
        self.semaphore = coros.Semaphore(limit)

    def allocate(self):
        self.semaphore.acquire()
        g = self.linkable_class()
        g.link(lambda *_args: self.semaphore.release())
        return g

