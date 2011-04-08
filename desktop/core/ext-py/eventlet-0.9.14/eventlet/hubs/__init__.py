import sys
import os
from eventlet.support import greenlets as greenlet
from eventlet import patcher

__all__ = ["use_hub", "get_hub", "get_default_hub", "trampoline"]

threading = patcher.original('threading')
_threadlocal = threading.local()

def get_default_hub():
    """Select the default hub implementation based on what multiplexing
    libraries are installed.  The order that the hubs are tried is:
    
    * twistedr
    * epoll
    * poll
    * select
    
    It won't automatically select the pyevent hub, because it's not 
    python-thread-safe.
    
    .. include:: ../../doc/common.txt
    .. note :: |internal|
    """    
    
    # pyevent hub disabled for now because it is not thread-safe
    #try:
    #    import eventlet.hubs.pyevent
    #    return eventlet.hubs.pyevent
    #except:
    #    pass

    select = patcher.original('select')
    try:
        import eventlet.hubs.epolls
        return eventlet.hubs.epolls
    except ImportError:
        if hasattr(select, 'poll'):
            import eventlet.hubs.poll
            return eventlet.hubs.poll
        else:
            import eventlet.hubs.selects
            return eventlet.hubs.selects


def use_hub(mod=None):
    """Use the module *mod*, containing a class called Hub, as the
    event hub. Usually not required; the default hub is usually fine.  
    
    Mod can be an actual module, a string, or None.  If *mod* is a module,
    it uses it directly.   If *mod* is a string, use_hub tries to import 
    `eventlet.hubs.mod` and use that as the hub module.  If *mod* is None, 
    use_hub uses the default hub.  Only call use_hub during application 
    initialization,  because it resets the hub's state and any existing 
    timers or listeners will never be resumed.
    """
    if mod is None:
        mod = os.environ.get('EVENTLET_HUB', None)
    if mod is None:
        mod = get_default_hub()
    if hasattr(_threadlocal, 'hub'):
        del _threadlocal.hub
    if isinstance(mod, str):
        assert mod.strip(), "Need to specify a hub"
        mod = __import__('eventlet.hubs.' + mod, globals(), locals(), ['Hub'])
    if hasattr(mod, 'Hub'):
        _threadlocal.Hub = mod.Hub
    else:
        _threadlocal.Hub = mod

def get_hub():
    """Get the current event hub singleton object.
    
    .. note :: |internal|
    """
    try:
        hub = _threadlocal.hub
    except AttributeError:
        try:
            _threadlocal.Hub
        except AttributeError:
            use_hub()
        hub = _threadlocal.hub = _threadlocal.Hub()
    return hub

from eventlet import timeout
def trampoline(fd, read=None, write=None, timeout=None, 
               timeout_exc=timeout.Timeout):
    """Suspend the current coroutine until the given socket object or file
    descriptor is ready to *read*, ready to *write*, or the specified
    *timeout* elapses, depending on arguments specified.

    To wait for *fd* to be ready to read, pass *read* ``=True``; ready to
    write, pass *write* ``=True``. To specify a timeout, pass the *timeout*
    argument in seconds.

    If the specified *timeout* elapses before the socket is ready to read or
    write, *timeout_exc* will be raised instead of ``trampoline()``
    returning normally.
    
    .. note :: |internal|
    """
    t = None
    hub = get_hub()
    current = greenlet.getcurrent()
    assert hub.greenlet is not current, 'do not call blocking functions from the mainloop'
    assert not (read and write), 'not allowed to trampoline for reading and writing'
    try:
        fileno = fd.fileno()
    except AttributeError:
        fileno = fd
    if timeout is not None:
        t = hub.schedule_call_global(timeout, current.throw, timeout_exc)
    try:
        if read:
            listener = hub.add(hub.READ, fileno, current.switch)
        elif write:
            listener = hub.add(hub.WRITE, fileno, current.switch)
        try:
            return hub.switch()
        finally:
            hub.remove(listener)
    finally:
        if t is not None:
            t.cancel()
