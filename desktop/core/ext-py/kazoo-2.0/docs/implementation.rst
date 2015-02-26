.. _implementation_details:

======================
Implementation Details
======================

Up to version 0.3 kazoo used the Python bindings to the Zookeeper C library.
Unfortunately those bindings are fairly buggy and required a fair share of
weird workarounds to interface with the native OS thread used in those
bindings.

Starting with version 0.4 kazoo implements the entire Zookeeper wire protocol
itself in pure Python. Doing so removed the need for the workarounds and made
it much easier to implement the features missing in the C bindings.

Handlers
========

Both the Kazoo handlers run 3 separate queues to help alleviate deadlock issues
and ensure consistent execution order regardless of environment. The
:class:`~kazoo.handlers.gevent.SequentialGeventHandler` runs a separate
greenlet for each queue that processes the callbacks queued in order. The
:class:`~kazoo.handlers.threading.SequentialThreadingHandler` runs a separate
thread for each queue that processes the callbacks queued in order (thus the
naming scheme which notes they are sequential in anticipation that there could
be handlers shipped in the future which don't make this guarantee).

Callbacks are queued by type, the 3 types being:

1. Session events (State changes, registered listener functions)
2. Watch events (Watch callbacks, DataWatch, and ChildrenWatch functions)
3. Completion callbacks (Functions chained to
   :class:`~kazoo.interfaces.IAsyncResult` objects)

This ensures that calls can be made to Zookeeper from any callback **except for
a state listener** without worrying that critical session events will be
blocked.

.. warning::

    Its important to remember that if you write code that blocks in one of
    these functions then no queued functions of that type will be executed
    until the code stops blocking. If your code might block, it should run
    itself in a separate greenlet/thread so that the other callbacks can
    run.
