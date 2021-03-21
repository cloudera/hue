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

            .. note::

                Up to version 2.6.1, requests could only be submitted
                in the CONNECTED state.  Requests submitted while
                SUSPENDED would immediately raise a
                :exc:`~kazoo.exceptions.SessionExpiredError`.  This
                was problematic, as sessions are usually recovered on
                reconnect.

                Kazoo now simply queues requests submitted in the
                SUSPENDED state, expecting a recovery.  This matches
                the behavior of the Java and C clients.

                Requests submitted in a LOST state still fail
                immediately with the corresponding exception.

                See:

                  * https://github.com/python-zk/kazoo/issues/374 and
                  * https://github.com/python-zk/kazoo/pull/570

    .. autoclass:: TransactionRequest
        :members:
        :member-order: bysource
