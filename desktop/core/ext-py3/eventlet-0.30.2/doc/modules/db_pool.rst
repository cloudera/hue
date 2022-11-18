:mod:`db_pool` -- DBAPI 2 database connection pooling
========================================================

The db_pool module is useful for managing database connections.  It provides three primary benefits: cooperative yielding during database operations, concurrency limiting to a database host, and connection reuse.  db_pool is intended to be database-agnostic, compatible with any DB-API 2.0 database module.

*It has currently been tested and used with both MySQLdb and psycopg2.*

A ConnectionPool object represents a pool of connections open to a particular database.  The arguments to the constructor include the database-software-specific module, the host name, and the credentials required for authentication.  After construction, the ConnectionPool object decides when to create and sever connections with the target database.

>>> import MySQLdb
>>> cp = ConnectionPool(MySQLdb, host='localhost', user='root', passwd='')

Once you have this pool object, you connect to the database by calling :meth:`~eventlet.db_pool.ConnectionPool.get` on it:

>>> conn = cp.get()

This call may either create a new connection, or reuse an existing open connection, depending on whether it has one open already or not.  You can then use the connection object as normal.  When done, you must return the connection to the pool:

>>> conn = cp.get()
>>> try:
...     result = conn.cursor().execute('SELECT NOW()')
... finally:
...     cp.put(conn)

After you've returned a connection object to the pool, it becomes useless and will raise exceptions if any of its methods are called.

Constructor Arguments
----------------------

In addition to the database credentials, there are a bunch of keyword constructor arguments to the ConnectionPool that are useful.

* min_size, max_size : The normal Pool arguments.  max_size is the most important constructor argument -- it determines the number of concurrent connections can be open to the destination database.  min_size is not very useful.
* max_idle : Connections are only allowed to remain unused in the pool for a limited amount of time.  An asynchronous timer periodically wakes up and closes any connections in the pool that have been idle for longer than they are supposed to be.  Without this parameter, the pool would tend to have a 'high-water mark', where the number of connections open at a given time corresponds to the peak historical demand.  This number only has effect on the connections in the pool itself -- if you take a connection out of the pool, you can hold on to it for as long as you want.  If this is set to 0, every connection is closed upon its return to the pool.
* max_age : The lifespan of a connection.  This works much like max_idle, but the timer is measured from the connection's creation time, and is tracked throughout the connection's life.  This means that if you take a connection out of the pool and hold on to it for some lengthy operation that exceeds max_age, upon putting the connection back in to the pool, it will be closed.  Like max_idle, max_age will not close connections that are taken out of the pool, and, if set to 0, will cause every connection to be closed when put back in the pool.
* connect_timeout : How long to wait before raising an exception on connect().  If the database module's connect() method takes too long, it raises a ConnectTimeout exception from the get() method on the pool.

DatabaseConnector
-----------------

If you want to connect to multiple databases easily (and who doesn't), the DatabaseConnector is for you.  It's a pool of pools, containing a ConnectionPool for every host you connect to.

The constructor arguments are:

* module : database module, e.g. MySQLdb.  This is simply passed through to the ConnectionPool.
* credentials : A dictionary, or dictionary-alike, mapping hostname to connection-argument-dictionary.  This is used for the constructors of the ConnectionPool objects.  Example:

>>> dc = DatabaseConnector(MySQLdb,
...      {'db.internal.example.com': {'user': 'internal', 'passwd': 's33kr1t'},
...       'localhost': {'user': 'root', 'passwd': ''}})

If the credentials contain a host named 'default', then the value for 'default' is used whenever trying to connect to a host that has no explicit entry in the database.  This is useful if there is some pool of hosts that share arguments.

* conn_pool : The connection pool class to use.  Defaults to db_pool.ConnectionPool.

The rest of the arguments to the DatabaseConnector constructor are passed on to the ConnectionPool.

*Caveat: The DatabaseConnector is a bit unfinished, it only suits a subset of use cases.*

.. automodule:: eventlet.db_pool
	:members:
	:undoc-members:
