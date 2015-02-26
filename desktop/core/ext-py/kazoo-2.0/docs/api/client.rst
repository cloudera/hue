.. _client_module:

:mod:`kazoo.client`
----------------------------

.. automodule:: kazoo.client

Public API
++++++++++

    .. autoclass:: KazooClient()
        :members:
        :member-order: bysource

        .. automethod:: __init__

        .. attribute:: handler

            The :class:`~kazoo.interfaces.IHandler` strategy used by this
            client. Gives access to appropriate synchronization objects.

        .. method:: retry(func, *args, **kwargs)

            Runs the given function with the provided arguments, retrying if it
            fails because the ZooKeeper connection is lost,
            see :ref:`retrying_commands`.

        .. attribute:: state

            A :class:`~kazoo.protocol.states.KazooState` attribute indicating
            the current higher-level connection state.

    .. autoclass:: TransactionRequest
        :members:
        :member-order: bysource
