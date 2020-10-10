.. _async_usage:

==================
Asynchronous Usage
==================

The asynchronous Kazoo API relies on the
:class:`~kazoo.interfaces.IAsyncResult` object which is returned by all the
asynchronous methods. Callbacks can be added with the
:meth:`~kazoo.interfaces.IAsyncResult.rawlink` method which works in a
consistent manner whether threads or an asynchronous framework like gevent is
used.

Kazoo utilizes a pluggable :class:`~kazoo.interfaces.IHandler` interface which
abstracts the callback system to ensure it works consistently.

Connection Handling
===================

Creating a connection:

.. code-block:: python

    from kazoo.client import KazooClient
    from kazoo.handlers.gevent import SequentialGeventHandler

    zk = KazooClient(handler=SequentialGeventHandler())

    # returns immediately
    event = zk.start_async()

    # Wait for 30 seconds and see if we're connected
    event.wait(timeout=30)

    if not zk.connected:
        # Not connected, stop trying to connect
        zk.stop()
        raise Exception("Unable to connect.")

In this example, the `wait` method is used on the event object returned by the
:meth:`~kazoo.client.KazooClient.start_async` method. A timeout is **always**
used because its possible that we might never connect and that should be
handled gracefully.

The :class:`~kazoo.handlers.gevent.SequentialGeventHandler` is used when you
want to use gevent (and
:class:`~kazoo.handlers.eventlet.SequentialEventletHandler` when eventlet is
used). Kazoo doesn't rely on gevents/eventlet monkey patching and requires
that you pass in the appropriate handler, the default handler is
:class:`~kazoo.handlers.threading.SequentialThreadingHandler`.

Asynchronous Callbacks
======================

All kazoo `_async` methods except for
:meth:`~kazoo.client.KazooClient.start_async` return an
:class:`~kazoo.interfaces.IAsyncResult` instance. These instances allow
you to see when a result is ready, or chain one or more callback
functions to the result that will be called when it's ready.

The callback function will be passed the
:class:`~kazoo.interfaces.IAsyncResult` instance and should call the
:meth:`~kazoo.interfaces.IAsyncResult.get` method on it to retrieve
the value. This call could result in an exception being raised
if the asynchronous function encountered an error. It should be caught
and handled appropriately.

Example:

.. code-block:: python

    import sys

    from kazoo.exceptions import ConnectionLossException
    from kazoo.exceptions import NoAuthException

    def my_callback(async_obj):
        try:
            children = async_obj.get()
            do_something(children)
        except (ConnectionLossException, NoAuthException):
            sys.exit(1)

    # Both these statements return immediately, the second sets a callback
    # that will be run when get_children_async has its return value
    async_obj = zk.get_children_async("/some/node")
    async_obj.rawlink(my_callback)

Zookeeper CRUD
==============

The following CRUD methods all work the same as their synchronous counterparts
except that they return an :class:`~kazoo.interfaces.IAsyncResult` object.

Creating Method:

* :meth:`~kazoo.client.KazooClient.create_async`

Reading Methods:

* :meth:`~kazoo.client.KazooClient.exists_async`
* :meth:`~kazoo.client.KazooClient.get_async`
* :meth:`~kazoo.client.KazooClient.get_children_async`

Updating Methods:

* :meth:`~kazoo.client.KazooClient.set_async`

Deleting Methods:

* :meth:`~kazoo.client.KazooClient.delete_async`

The :meth:`~kazoo.client.KazooClient.ensure_path` has no asynchronous
counterpart at the moment nor can the
:meth:`~kazoo.client.KazooClient.delete_async` method do recursive deletes.
