.. _basic_usage:

===========
Basic Usage
===========


Connection Handling
===================

To begin using Kazoo, a :class:`~kazoo.client.KazooClient` object must be
created and a connection established:

.. code-block:: python

    from kazoo.client import KazooClient

    zk = KazooClient(hosts='127.0.0.1:2181')
    zk.start()

By default, the client will connect to a local Zookeeper server on the default
port (2181). You should make sure Zookeeper is actually running there first,
or the ``start`` command will be waiting until its default timeout.

Once connected, the client will attempt to stay connected regardless of
intermittent connection loss or Zookeeper session expiration. The client can be
instructed to drop a connection by calling `stop`:

.. code-block:: python

    zk.stop()


Logging Setup
-------------

If logging is not setup for your application, you can get following message:

.. code-block:: python
    
    No handlers could be found for logger "kazoo.client"

To avoid this issue you can at the very minimum do the following:

.. code-block:: python
    
    import logging
    logging.basicConfig()

Read `Python's logging tutorial <https://docs.python.org/howto/logging.html>`_
for more details.


Listening for Connection Events
-------------------------------

It can be useful to know when the connection has been dropped, restored, or
when the Zookeeper session has expired. To simplify this process Kazoo uses a
state system and lets you register listener functions to be called when the
state changes.

.. code-block:: python

    from kazoo.client import KazooState

    def my_listener(state):
        if state == KazooState.LOST:
            # Register somewhere that the session was lost
        elif state == KazooState.SUSPENDED:
            # Handle being disconnected from Zookeeper
        else:
            # Handle being connected/reconnected to Zookeeper

    zk.add_listener(my_listener)

When using the :class:`kazoo.recipe.lock.Lock` or creating ephemeral nodes, its
highly recommended to add a state listener so that your program can properly
deal with connection interruptions or a Zookeeper session loss.

Understanding Kazoo States
--------------------------

The :class:`~kazoo.protocol.states.KazooState` object represents several states
the client transitions through. The current state of the client can always be
determined by viewing the :attr:`~kazoo.client.KazooClient.state` property. The
possible states are:

- LOST
- CONNECTED
- SUSPENDED

When a :class:`~kazoo.client.KazooClient` instance is first created, it is in
the `LOST` state. After a connection is established it transitions to the
`CONNECTED` state. If any connection issues come up or if it needs to connect
to a different Zookeeper cluster node, it will transition to `SUSPENDED` to let
you know that commands cannot currently be run. The connection will also be
lost if the Zookeeper node is no longer part of the quorum, resulting in a
`SUSPENDED` state.

Upon re-establishing a connection the client could transition to `LOST` if the
session has expired, or `CONNECTED` if the session is still valid.

.. note::

    These states should be monitored using a listener as described previously
    so that the client behaves properly depending on the state of the
    connection.

When a connection transitions to `SUSPENDED`, if the client is performing an
action that requires agreement with other systems (using the Lock recipe for
example), it should pause what it's doing. When the connection has been
re-established the client can continue depending on if the state is `LOST` or
transitions directly to `CONNECTED` again.

When a connection transitions to `LOST`, any ephemeral nodes that have been
created will be removed by Zookeeper. This affects all recipes that create
ephemeral nodes, such as the Lock recipe. Lock's will need to be re-acquired
after the state transitions to `CONNECTED` again. This transition occurs when
a session expires or when you stop the clients connection.

**Valid State Transitions**

- *LOST -> CONNECTED*

  New connection, or previously lost one becoming connected.
- *CONNECTED -> SUSPENDED*

  Connection loss to server occurred on a connection.
- *CONNECTED -> LOST*

  Only occurs if invalid authentication credentials are provided after the
  connection was established.
- *SUSPENDED -> LOST*

  Connection resumed to server, but then lost as the session was expired.
- *SUSPENDED -> CONNECTED*

  Connection that was lost has been restored.

Read-Only Connections
---------------------

.. versionadded:: 0.6

Zookeeper 3.4 and above `supports a read-only mode
<http://wiki.apache.org/hadoop/ZooKeeper/GSoCReadOnlyMode>`_. This mode
must be turned on for the servers in the Zookeeper cluster for the
client to utilize it. To use this mode with Kazoo, the
:class:`~kazoo.client.KazooClient` should be called with the
`read_only` option set to `True`. This will let the client connect to
a Zookeeper node that has gone read-only, and the client will continue
to scan for other nodes that are read-write.

.. code-block:: python

    from kazoo.client import KazooClient

    zk = KazooClient(hosts='127.0.0.1:2181', read_only=True)
    zk.start()

A new attribute on :class:`~kazoo.protocol.states.KeeperState` has been
added, `CONNECTED_RO`. The connection states above are still valid,
however upon `CONNECTED`, you will need to check the clients non-
simplified state to see if the connection is `CONNECTED_RO`. For
example:

.. code-block:: python

    from kazoo.client import KazooState
    from kazoo.client import KeeperState

    @zk.add_listener
    def watch_for_ro(state):
        if state == KazooState.CONNECTED:
            if zk.client_state == KeeperState.CONNECTED_RO:
                print("Read only mode!")
            else:
                print("Read/Write mode!")

It's important to note that a `KazooState` is passed in to the listener
but the read-only information is only available by comparing the
non-simplified client state to the `KeeperState` object.

.. warning::

    A client using read-only mode should not use any of the recipes.


Zookeeper CRUD
==============

Zookeeper includes several functions for creating, reading, updating, and
deleting Zookeeper nodes (called znodes or nodes here). Kazoo adds several
convenience methods and a more Pythonic API.

Creating Nodes
--------------

Methods:

* :meth:`~kazoo.client.KazooClient.ensure_path`
* :meth:`~kazoo.client.KazooClient.create`

:meth:`~kazoo.client.KazooClient.ensure_path` will recursively create the node
and any nodes in the path necessary along the way, but can not set the data for
the node, only the ACL.

:meth:`~kazoo.client.KazooClient.create` creates a node and can set the data on
the node along with a watch function. It requires the path to it to exist
first, unless the `makepath` option is set to `True`.

.. code-block:: python

    # Ensure a path, create if necessary
    zk.ensure_path("/my/favorite")

    # Create a node with data
    zk.create("/my/favorite/node", b"a value")

Reading Data
------------

Methods:

* :meth:`~kazoo.client.KazooClient.exists`
* :meth:`~kazoo.client.KazooClient.get`
* :meth:`~kazoo.client.KazooClient.get_children`

:meth:`~kazoo.client.KazooClient.exists` checks to see if a node exists.

:meth:`~kazoo.client.KazooClient.get` fetches the data of the node along with
detailed node information in a :class:`~kazoo.protocol.states.ZnodeStat`
structure.

:meth:`~kazoo.client.KazooClient.get_children` gets a list of the children of
a given node.

.. code-block:: python

    # Determine if a node exists
    if zk.exists("/my/favorite"):
        # Do something

    # Print the version of a node and its data
    data, stat = zk.get("/my/favorite")
    print("Version: %s, data: %s" % (stat.version, data.decode("utf-8")))

    # List the children
    children = zk.get_children("/my/favorite")
    print("There are %s children with names %s" % (len(children), children))

Updating Data
-------------

Methods:

* :meth:`~kazoo.client.KazooClient.set`

:meth:`~kazoo.client.KazooClient.set` updates the data for a given node. A
version for the node can be supplied, which will be required to match before
updating the data, or a :exc:`~kazoo.exceptions.BadVersionError` will be
raised instead of updating.

.. code-block:: python

    zk.set("/my/favorite", b"some data")

Deleting Nodes
--------------

Methods:

* :meth:`~kazoo.client.KazooClient.delete`

:meth:`~kazoo.client.KazooClient.delete` deletes a node, and can optionally
recursively delete all children of the node as well. A version can be
supplied when deleting a node which will be required to match the version of
the node before deleting it or a :exc:`~kazoo.exceptions.BadVersionError`
will be raised instead of deleting.

.. code-block:: python

    zk.delete("/my/favorite/node", recursive=True)

.. _retrying_commands:

Retrying Commands
=================

Connections to Zookeeper may get interrupted if the Zookeeper server goes down
or becomes unreachable. By default, kazoo does not retry commands, so these
failures will result in an exception being raised. To assist with failures
kazoo comes with a :meth:`~kazoo.client.KazooClient.retry` helper that will
retry a function should one of the Zookeeper connection exceptions get raised.

Example:

.. code-block:: python

    result = zk.retry(zk.get, "/path/to/node")

Some commands may have unique behavior that doesn't warrant automatic retries
on a per command basis. For example, if one creates a node a connection might
be lost before the command returns successfully but the node actually got
created. This results in a :exc:`kazoo.exceptions.NodeExistsError` being
raised when it runs again. A similar unique situation arises when a node is
created with ephemeral and sequence options set,
`documented here on the Zookeeper site
<http://zookeeper.apache.org/doc/trunk/recipes.html#sc_recipes_errorHandlingNote>`_.

Since the :meth:`~kazoo.client.KazooClient.retry` method takes a function to
call and its arguments, a function that runs multiple Zookeeper commands could
be passed to it so that the entire function will be retried if the connection
is lost.

This snippet from the lock implementation shows how it uses retry to re-run the
function acquiring a lock, and checks to see if it was already created to
handle this condition:

.. code-block:: python

    # kazoo.recipe.lock snippet

    def acquire(self):
        """Acquire the mutex, blocking until it is obtained"""
        try:
            self.client.retry(self._inner_acquire)
            self.is_acquired = True
        except KazooException:
            # if we did ultimately fail, attempt to clean up
            self._best_effort_cleanup()
            self.cancelled = False
            raise

    def _inner_acquire(self):
        self.wake_event.clear()

        # make sure our election parent node exists
        if not self.assured_path:
            self.client.ensure_path(self.path)

        node = None
        if self.create_tried:
            node = self._find_node()
        else:
            self.create_tried = True

        if not node:
            node = self.client.create(self.create_path, self.data,
                ephemeral=True, sequence=True)
            # strip off path to node
            node = node[len(self.path) + 1:]

`create_tried` records whether it has tried to create the node already in the
event the connection is lost before the node name is returned.

Custom Retries
--------------

Sometimes you may wish to have specific retry policies for a command or
set of commands that differs from the
:meth:`~kazoo.client.KazooClient.retry` method. You can manually create
a :class:`~kazoo.retry.KazooRetry` instance with the specific retry
policy you prefer:

.. code-block:: python

    from kazoo.retry import KazooRetry

    kr = KazooRetry(max_tries=3, ignore_expire=False)
    result = kr(client.get, "/some/path")

This will retry the ``client.get`` command up to 3 times, and raise a
session expiration if it occurs. You can also make an instance with the
default behavior that ignores session expiration during a retry.

Watchers
========

Kazoo can set watch functions on a node that can be triggered either when the
node has changed or when the children of the node change. This change to the
node or children can also be the node or its children being deleted.

Watchers can be set in two different ways, the first is the style that
Zookeeper supports by default for one-time watch events. These watch functions
will be called once by kazoo, and do *not* receive session events, unlike the
native Zookeeper watches. Using this style requires the watch function to be
passed to one of these methods:

* :meth:`~kazoo.client.KazooClient.get`
* :meth:`~kazoo.client.KazooClient.get_children`
* :meth:`~kazoo.client.KazooClient.exists`

A watch function passed to :meth:`~kazoo.client.KazooClient.get` or
:meth:`~kazoo.client.KazooClient.exists` will be called when the data on the
node changes or the node itself is deleted. It will be passed a
:class:`~kazoo.protocol.states.WatchedEvent` instance.

.. code-block:: python

    def my_func(event):
        # check to see what the children are now

    # Call my_func when the children change
    children = zk.get_children("/my/favorite/node", watch=my_func)

Kazoo includes a higher level API that watches for data and children
modifications that's easier to use as it doesn't require re-setting the watch
every time the event is triggered. It also passes in the data and
:class:`~kazoo.protocol.states.ZnodeStat` when watching a node or the list of
children when watching a nodes children. Watch functions registered with this
API will be called immediately and every time there's a change, or until the
function returns False. If `allow_session_lost` is set to `True`, then the
function will no longer be called if the session is lost.

The following methods provide this functionality:

* :class:`~kazoo.recipe.watchers.ChildrenWatch`
* :class:`~kazoo.recipe.watchers.DataWatch`

These classes are available directly on the :class:`~kazoo.client.KazooClient`
instance and don't require the client object to be passed in when used in this
manner. The instance returned by instantiating either of the classes can be
called directly allowing them to be used as decorators:

.. code-block:: python

    @zk.ChildrenWatch("/my/favorite/node")
    def watch_children(children):
        print("Children are now: %s" % children)
    # Above function called immediately, and from then on

    @zk.DataWatch("/my/favorite")
    def watch_node(data, stat):
        print("Version: %s, data: %s" % (stat.version, data.decode("utf-8")))

Transactions
============

.. versionadded:: 0.6

Zookeeper 3.4 and above supports the sending of multiple commands at
once that will be committed as a single atomic unit. Either they will
all succeed or they will all fail. The result of a transaction will be
a list of the success/failure results for each command in the
transaction.

.. code-block:: python

    transaction = zk.transaction()
    transaction.check('/node/a', version=3)
    transaction.create('/node/b', b"a value")
    results = transaction.commit()

The :meth:`~kazoo.client.KazooClient.transaction` method returns a
:class:`~kazoo.client.TransactionRequest` instance. It's methods may be
called to queue commands to be completed in the transaction. When the
transaction is ready to be sent, the
:meth:`~kazoo.client.TransactionRequest.commit` method on it is called.

In the example above, there's a command not available unless a
transaction is being used, `check`. This can check nodes for a specific
version, which could be used to make the transaction fail if a node
doesn't match a version that it should be at. In this case the node
`/node/a` must be at version 3 or `/node/b` will not be created.
