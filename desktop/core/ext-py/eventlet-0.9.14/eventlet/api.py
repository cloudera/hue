import errno
import sys
import socket
import string
import linecache
import inspect
import warnings

from eventlet.support import greenlets as greenlet, BaseException
from eventlet import hubs
from eventlet import greenthread
from eventlet import debug
from eventlet import Timeout

__all__ = [
    'call_after', 'exc_after', 'getcurrent', 'get_default_hub', 'get_hub',
    'GreenletExit', 'kill', 'sleep', 'spawn', 'spew', 'switch',
    'ssl_listener', 'tcp_listener', 'trampoline',
    'unspew', 'use_hub', 'with_timeout', 'timeout']

warnings.warn("eventlet.api is deprecated!  Nearly everything in it has moved "
    "to the eventlet module.", DeprecationWarning, stacklevel=2)

def get_hub(*a, **kw):
    warnings.warn("eventlet.api.get_hub has moved to eventlet.hubs.get_hub",
        DeprecationWarning, stacklevel=2)
    return hubs.get_hub(*a, **kw)    
def get_default_hub(*a, **kw):
    warnings.warn("eventlet.api.get_default_hub has moved to"
        " eventlet.hubs.get_default_hub",
        DeprecationWarning, stacklevel=2)
    return hubs.get_default_hub(*a, **kw)
def use_hub(*a, **kw):
    warnings.warn("eventlet.api.use_hub has moved to eventlet.hubs.use_hub",
        DeprecationWarning, stacklevel=2)
    return hubs.use_hub(*a, **kw)
    

def switch(coro, result=None, exc=None):
    if exc is not None:
        return coro.throw(exc)
    return coro.switch(result)

Greenlet = greenlet.greenlet


def tcp_listener(address, backlog=50):
    """
    Listen on the given ``(ip, port)`` *address* with a TCP socket.  Returns a
    socket object on which one should call ``accept()`` to accept a connection
    on the newly bound socket.
    """
    warnings.warn("""eventlet.api.tcp_listener is deprecated.  Please use eventlet.listen instead.""",
        DeprecationWarning, stacklevel=2)

    from eventlet import greenio, util
    socket = greenio.GreenSocket(util.tcp_socket())
    util.socket_bind_and_listen(socket, address, backlog=backlog)
    return socket

def ssl_listener(address, certificate, private_key):
    """Listen on the given (ip, port) *address* with a TCP socket that
    can do SSL.  Primarily useful for unit tests, don't use in production.

    *certificate* and *private_key* should be the filenames of the appropriate
    certificate and private key files to use with the SSL socket.

    Returns a socket object on which one should call ``accept()`` to
    accept a connection on the newly bound socket.
    """
    warnings.warn("""eventlet.api.ssl_listener is deprecated.  Please use eventlet.wrap_ssl(eventlet.listen()) instead.""",
        DeprecationWarning, stacklevel=2)
    from eventlet import util
    import socket

    socket = util.wrap_ssl(socket.socket(), certificate, private_key, True)
    socket.bind(address)
    socket.listen(50)
    return socket

def connect_tcp(address, localaddr=None):
    """
    Create a TCP connection to address ``(host, port)`` and return the socket.
    Optionally, bind to localaddr ``(host, port)`` first.
    """
    warnings.warn("""eventlet.api.connect_tcp is deprecated.  Please use eventlet.connect instead.""",
        DeprecationWarning, stacklevel=2)
        
    from eventlet import greenio, util
    desc = greenio.GreenSocket(util.tcp_socket())
    if localaddr is not None:
        desc.bind(localaddr)
    desc.connect(address)
    return desc

TimeoutError = greenthread.TimeoutError

trampoline = hubs.trampoline

spawn = greenthread.spawn
spawn_n = greenthread.spawn_n


kill = greenthread.kill

call_after = greenthread.call_after
call_after_local = greenthread.call_after_local
call_after_global = greenthread.call_after_global


class _SilentException(BaseException):
    pass

class FakeTimer(object):
    def cancel(self):
        pass

class timeout(object):
    """Raise an exception in the block after timeout.
    
    Example::

     with timeout(10):
         urllib2.open('http://example.com')

    Assuming code block is yielding (i.e. gives up control to the hub),
    an exception provided in *exc* argument will be raised
    (:class:`~eventlet.api.TimeoutError` if *exc* is omitted)::
    
     try:
         with timeout(10, MySpecialError, error_arg_1):
             urllib2.open('http://example.com')
     except MySpecialError, e:
         print "special error received"


    When *exc* is ``None``, code block is interrupted silently.
    """

    def __init__(self, seconds, *throw_args):
        self.seconds = seconds
        if seconds is None:
            return
        if not throw_args:
            self.throw_args = (TimeoutError(), )
        elif throw_args == (None, ):
            self.throw_args = (_SilentException(), )
        else:
            self.throw_args = throw_args

    def __enter__(self):
        if self.seconds is None:
            self.timer = FakeTimer()
        else:
            self.timer = exc_after(self.seconds, *self.throw_args)
        return self.timer

    def __exit__(self, typ, value, tb):
        self.timer.cancel()
        if typ is _SilentException and value in self.throw_args:
            return True

with_timeout = greenthread.with_timeout

exc_after = greenthread.exc_after  
    
sleep = greenthread.sleep

getcurrent = greenlet.getcurrent
GreenletExit = greenlet.GreenletExit

spew = debug.spew
unspew = debug.unspew


def named(name):
    """Return an object given its name.

    The name uses a module-like syntax, eg::

      os.path.join

    or::

      mulib.mu.Resource
    """
    toimport = name
    obj = None
    import_err_strings = []
    while toimport:
        try:
            obj = __import__(toimport)
            break
        except ImportError, err:
            # print 'Import error on %s: %s' % (toimport, err)  # debugging spam
            import_err_strings.append(err.__str__())
            toimport = '.'.join(toimport.split('.')[:-1])
    if obj is None:
        raise ImportError('%s could not be imported.  Import errors: %r' % (name, import_err_strings))
    for seg in name.split('.')[1:]:
        try:
            obj = getattr(obj, seg)
        except AttributeError:
            dirobj = dir(obj)
            dirobj.sort()
            raise AttributeError('attribute %r missing from %r (%r) %r.  Import errors: %r' % (
                seg, obj, dirobj, name, import_err_strings))
    return obj

