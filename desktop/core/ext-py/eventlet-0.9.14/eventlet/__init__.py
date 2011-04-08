version_info = (0, 9, 14)
__version__ = ".".join(map(str, version_info))

try:
    from eventlet import greenthread
    from eventlet import greenpool
    from eventlet import queue
    from eventlet import timeout
    from eventlet import patcher
    from eventlet import convenience
    import greenlet

    sleep = greenthread.sleep
    spawn = greenthread.spawn
    spawn_n = greenthread.spawn_n
    spawn_after = greenthread.spawn_after
    kill = greenthread.kill
    
    Timeout = timeout.Timeout
    with_timeout = timeout.with_timeout
    
    GreenPool = greenpool.GreenPool
    GreenPile = greenpool.GreenPile
    
    Queue = queue.Queue
    
    import_patched = patcher.import_patched
    monkey_patch = patcher.monkey_patch
    
    connect = convenience.connect
    listen = convenience.listen
    serve = convenience.serve
    StopServe = convenience.StopServe
    wrap_ssl = convenience.wrap_ssl

    getcurrent = greenlet.greenlet.getcurrent
    
    # deprecated    
    TimeoutError = timeout.Timeout
    exc_after = greenthread.exc_after
    call_after_global = greenthread.call_after_global
except ImportError, e:
    # This is to make Debian packaging easier, it ignores import
    # errors of greenlet so that the packager can still at least
    # access the version.  Also this makes easy_install a little quieter
    if 'greenlet' not in str(e):
        # any other exception should be printed
        import traceback
        traceback.print_exc()
