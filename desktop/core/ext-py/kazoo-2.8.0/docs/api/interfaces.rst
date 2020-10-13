.. _interfaces_module:

:mod:`kazoo.interfaces`
----------------------------

.. automodule:: kazoo.interfaces

Public API
++++++++++

:class:`IHandler` implementations should be created by the developer to be
passed into :class:`~kazoo.client.KazooClient` during instantiation for the
preferred callback handling.

If the developer needs to use objects implementing the :class:`IAsyncResult`
interface, the :meth:`IHandler.async_result` method must be used instead of
instantiating one directly.

    .. autoclass:: IHandler
     :members:

Private API
+++++++++++

The :class:`IAsyncResult` documents the proper implementation for providing
a value that results from a Zookeeper completion callback. Since the
:class:`~kazoo.client.KazooClient` returns an :class:`IAsyncResult` object
instead of taking a completion callback for async functions, developers
wishing to have their own callback called should use the
:meth:`IAsyncResult.rawlink` method.

  .. autoclass:: IAsyncResult
     :members:
