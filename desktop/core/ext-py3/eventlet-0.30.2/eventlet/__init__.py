import os
import sys
import warnings

if sys.version_info < (3, 5):
    warnings.warn(
        "Support for your Python version is deprecated and will be removed in the future",
        DeprecationWarning,
    )

version_info = (0, 30, 2)
__version__ = '.'.join(map(str, version_info))
# This is to make Debian packaging easier, it ignores import
# errors of greenlet so that the packager can still at least
# access the version.  Also this makes easy_install a little quieter
if os.environ.get('EVENTLET_IMPORT_VERSION_ONLY') != '1':
    from eventlet import convenience
    from eventlet import event
    from eventlet import greenpool
    from eventlet import greenthread
    from eventlet import patcher
    from eventlet import queue
    from eventlet import semaphore
    from eventlet import support
    from eventlet import timeout
    import greenlet
    # Force monotonic library search as early as possible.
    # Helpful when CPython < 3.5 on Linux blocked in `os.waitpid(-1)` before first use of hub.
    # Example: gunicorn
    # https://github.com/eventlet/eventlet/issues/401#issuecomment-327500352
    try:
        import monotonic
        del monotonic
    except ImportError:
        pass

    connect = convenience.connect
    listen = convenience.listen
    serve = convenience.serve
    StopServe = convenience.StopServe
    wrap_ssl = convenience.wrap_ssl

    Event = event.Event

    GreenPool = greenpool.GreenPool
    GreenPile = greenpool.GreenPile

    sleep = greenthread.sleep
    spawn = greenthread.spawn
    spawn_n = greenthread.spawn_n
    spawn_after = greenthread.spawn_after
    kill = greenthread.kill

    import_patched = patcher.import_patched
    monkey_patch = patcher.monkey_patch

    Queue = queue.Queue

    Semaphore = semaphore.Semaphore
    CappedSemaphore = semaphore.CappedSemaphore
    BoundedSemaphore = semaphore.BoundedSemaphore

    Timeout = timeout.Timeout
    with_timeout = timeout.with_timeout
    wrap_is_timeout = timeout.wrap_is_timeout
    is_timeout = timeout.is_timeout

    getcurrent = greenlet.greenlet.getcurrent

    # deprecated
    TimeoutError, exc_after, call_after_global = (
        support.wrap_deprecated(old, new)(fun) for old, new, fun in (
            ('TimeoutError', 'Timeout', Timeout),
            ('exc_after', 'greenthread.exc_after', greenthread.exc_after),
            ('call_after_global', 'greenthread.call_after_global', greenthread.call_after_global),
        ))

del os
