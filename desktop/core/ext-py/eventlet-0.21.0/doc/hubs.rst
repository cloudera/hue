.. _understanding_hubs:

Understanding Eventlet Hubs
===========================

A hub forms the basis of Eventlet's event loop, which dispatches I/O events and schedules greenthreads.  It is the existence of the hub that promotes coroutines (which can be tricky to program with) into greenthreads (which are easy).

Eventlet has multiple hub implementations, and when you start using it, it tries to select the best hub implementation for your system.  The hubs that it supports are (in order of preference):

**epolls**
    Requires Python 2.6 or the `python-epoll <http://pypi.python.org/pypi/python-epoll/1.0>`_ package, and Linux.  This is the fastest pure-Python hub.
**poll**
    On platforms that support it
**selects**
    Lowest-common-denominator, available everywhere.
**pyevent**
    This is a libevent-based backend and is thus the fastest.  It's disabled by default, because it does not support native threads, but you can enable it yourself if your use case doesn't require them.  (You have to install pyevent, too.)

If the selected hub is not ideal for the application, another can be selected.  You can make the selection either with the environment variable :ref:`EVENTLET_HUB <env_vars>`, or with use_hub.

.. function:: eventlet.hubs.use_hub(hub=None)

    Use this to control which hub Eventlet selects.  Call it with the name of the desired hub module.  Make sure to do this before the application starts doing any I/O!  Calling use_hub completely eliminates the old hub, and any file descriptors or timers that it had been managing will be forgotten.  Put the call as one of the first lines in the main module.::
    
        """ This is the main module """
        from eventlet import hubs
        hubs.use_hub("pyevent")
    
    Hubs are implemented as thread-local class instances.  :func:`eventlet.hubs.use_hub` only operates on the current thread.  When using multiple threads that each need their own hub, call :func:`eventlet.hubs.use_hub` at the beginning of each thread function that needs a specific hub.  In practice, it may not be necessary to specify a hub in each thread; it works to use one special hub for the main thread, and let other threads use the default hub; this hybrid hub configuration will work fine.
    
    It is also possible to use a third-party hub module in place of one of the built-in ones.  Simply pass the module itself to :func:`eventlet.hubs.use_hub`.  The task of writing such a hub is a little beyond the scope of this document, it's probably a good idea to simply inspect the code of the existing hubs to see how they work.::

         from eventlet import hubs    
         from mypackage import myhub
         hubs.use_hub(myhub)
    
    Supplying None as the argument to :func:`eventlet.hubs.use_hub` causes it to select the default hub.


How the Hubs Work
-----------------

The hub has a main greenlet, MAINLOOP.  When one of the running coroutines needs
to do some I/O, it registers a listener with the hub (so that the hub knows when to wake it up again), and then switches to MAINLOOP (via ``get_hub().switch()``).  If there are other coroutines that are ready to run, MAINLOOP switches to them, and when they complete or need to do more I/O, they switch back to the MAINLOOP.  In this manner, MAINLOOP ensures that every coroutine gets scheduled when it has some work to do.

MAINLOOP is launched only when the first I/O operation happens, and it is not the same greenlet that __main__ is running in.  This lazy launching is why it's not necessary to explicitly call a dispatch() method like other frameworks, which in turn means that code can start using Eventlet without needing to be substantially restructured.

More Hub-Related Functions
---------------------------

.. autofunction:: eventlet.hubs.get_hub
.. autofunction:: eventlet.hubs.get_default_hub
.. autofunction:: eventlet.hubs.trampoline

