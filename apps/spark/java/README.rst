Welcome to Livy, the REST Spark Server
======================================

Livy is an open source REST interface (in **Beta**) for interacting with a
remote Spark Shell running locally or from inside YARN.

* Interactive Spark Scala, Python shells
* Batch submissions in Scala, Java, Python
* Multi users can submit to the same server with their own credentials in YARN mode (impersonation support)
* Can be used for submitting jobs from anywhere with REST
* Does not require any code change to your programs


Livy is used for powering the `Spark Notebook`_ of `Hue 3.8`_, which you can see the
`implementation here`_.

.. _Spark Notebook: http://gethue.com/new-notebook-application-for-spark-sql/
.. _Hue 3.8: http://gethue.com/hue-3-8-with-an-oozie-editor-revamp-better-performances-improved-spark-ui-is-out/
.. _implementation here: https://github.com/cloudera/hue/blob/master/apps/spark/src/spark/job_server_api.py


Prerequisites
=============

To build Livy, you will need:

Debian/Ubuntu:
  * mvn (from ``maven`` package or maven3 tarball)
  * openjdk-7-jdk (or Oracle Java7 jdk)
  * spark 1.3 from (from `Apache Spark tarball`_)

Redhat/CentOS:
  * mvn (from ``maven`` package or maven3 tarball)
  * java-1.7.0-openjdk (or Oracle Java7 jdk)
  * spark 1.3 (from `Apache Spark tarball`_)
      
MacOS:
  * Xcode command line tools
  * Oracle's JDK 1.7+
  * Maven (Homebrew)
  * apache-spark (Homebrew)

.. _Apache Spark Tarball: https://spark.apache.org/downloads.html


Building Livy
=============

Livy is currently built by the `Hue Build System`_, it can also be built on
it's own (aka without any other Hue dependency) with `Apache Maven`_. To build,
run:

.. code:: shell

    % cd $HUE_HOME/apps/spark/java
    % mvn -DskipTests clean package

.. _Hue Build System: https://github.com/cloudera/hue/#getting-started
.. _Apache Maven: http://maven.apache.org


Running Tests
=============

In order to run the Livy Tests, first follow the instructions in `Building
Livy`_. Then run:

.. code:: shell

    % cd $HUE_HOME/apps/spark/java
    % mvn test


Running Livy
============

In order to run Livy with local sessions, start the server with:

.. code:: shell

    % ./bin/livy-server

Or with YARN sessions by running:

.. code:: shell

   % env \
     LIVY_SERVER_JAVA_OPTS="-Dlivy.server.session.factory=yarn" \
     CLASSPATH=`hadoop classpath` \
     ./bin/livy-server


Spark Example
=============

Now to see it in action by interacting with it in Python with the `Requests`_
library. By default livy runs on port 8998 (which can be changed with the
``livy_server_port config`` option). We’ll start off with a Spark session that
takes Scala code:

.. code:: python

    >>> import json, pprint, requests, textwrap
    >>> host = 'http://localhost:8998'
    >>> data = {'lang': 'spark'}
    >>> r = requests.post(host + '/sessions', data=json.dumps(data), headers=headers)
    >>> r.json()
    {u'state': u'starting', u'id': 0, u’kind’: u’spark’}

Once the session has completed starting up, it transitions to the idle state:

.. code:: python

    >>> session_url = host + r.headers['location']
    >>> r = requests.get(session_url, headers=headers)
    >>> r.json()
    {u'state': u'idle', u'id': 0, u’kind’: u’spark’}

Now we can execute Scala by passing in a simple JSON command:

.. code:: python

    >>> data = {'code': '1 + 1'}
    >>> r = requests.post(statements_url, data=json.dumps(data), headers=headers)
    >>> r.json()
    {u'output': None, u'state': u'running', u'id': 0}

If a statement takes longer than a few milliseconds to execute, Livy returns
early and provides a URL that can be polled until it is complete:

.. code:: python

    >>> statement_url = host + r.headers['location']
    >>> r = requests.get(statement_url, headers=headers)
    >>> pprint.pprint(r.json())
    [{u'id': 0,
      u'output': {u'data': {u'text/plain': u'res0: Int = 2'},
                  u'execution_count': 0,
                  u'status': u'ok'},
      u'state': u'available'}]

That was a pretty simple example. More interesting is using Spark to estimate
PI. This is from the `Spark Examples`_:

.. code:: python

    >>> data = {
    ...   'code': textwrap.dedent("""\
    ...      val NUM_SAMPLES = 100000;
    ...      val count = sc.parallelize(1 to NUM_SAMPLES).map { i =>
    ...        val x = Math.random();
    ...        val y = Math.random();
    ...        if (x*x + y*y < 1) 1 else 0
    ...      }.reduce(_ + _);
    ...      println(\"Pi is roughly \" + 4.0 * count / NUM_SAMPLES)
    ...      """)
    ... }
    >>> r = requests.post(statements_url, data=json.dumps(data), headers=headers)
    >>> pprint.pprint(r.json())
    {u'id': 1,
     u'output': {u'data': {u'text/plain': u'Pi is roughly 3.14004\nNUM_SAMPLES: Int = 100000\ncount: Int = 78501'},
                 u'execution_count': 1,
                 u'status': u'ok'},
     u'state': u'available'}

Finally, lets close our session:

.. code:: python

    >>> session_url = 'http://localhost:8998/sessions/0'
    >>> requests.delete(session_url, headers=headers)
    <Response [204]>

.. _Requests: http://docs.python-requests.org/en/latest/
.. _Spark Examples: https://spark.apache.org/examples.html


PySpark Example
===============

pyspark has the exact same API, just with a different initial command:

.. code:: python

    >>> data = {'lang': 'pyspark'}
    >>> r = requests.post(host + '/sessions', data=json.dumps(data), headers=headers)
    >>> r.json()
    {u'id': 1, u'state': u'idle'}

The PI example from before then can be run as:

.. code:: python

    >>> data = {
    ...   'code': textwrap.dedent("""\
    ...     import random
    ...     NUM_SAMPLES = 100000
    ...     def sample(p):
    ...       x, y = random.random(), random.random()
    ...       return 1 if x*x + y*y < 1 else 0
    ...
    ...     count = sc.parallelize(xrange(0, NUM_SAMPLES)).map(sample) \
    ...               .reduce(lambda a, b: a + b)
    ...     print "Pi is roughly %f" % (4.0 * count / NUM_SAMPLES)
    ...     """)
    ... }
    >>> r = requests.post(statements_url, data=json.dumps(data), headers=headers)
    >>> pprint.pprint(r.json())
    {u'id': 12,
     u'output': {u'data': {u'text/plain': u'Pi is roughly 3.136000'},
                 u'execution_count': 12,
                 u'status': u'ok'},
     u'state': u'running'}



Community
=========

 * User group: http://groups.google.com/a/cloudera.org/group/hue-user
 * Jira: https://issues.cloudera.org/browse/HUE-2588
 * Reviews: https://review.cloudera.org/dashboard/?view=to-group&group=hue (repo 'hue-rw')


REST API
========

GET /batches
------------

Return all the active batch jobs.

Response Body
^^^^^^^^^^^^^

+---------+---------------+------+
| name    | description   | type |
+=========+===============+======+
| batches | `batch`_ list | list |
+---------+---------------+------+


POST /batches
-------------

Request Body
^^^^^^^^^^^^

+----------------+--------------------------------------------------+-----------------+
| name           | description                                      | type            |
+================+==================================================+=================+
| file           | archive holding the file                         | path (required) |
+----------------+--------------------------------------------------+-----------------+
| args           | command line arguments                           | list of strings |
+----------------+--------------------------------------------------+-----------------+
| className      | application's java/spark main class              | string          |
+----------------+--------------------------------------------------+-----------------+
| jars           | files to be placed on the java classpath         | list of paths   |
+----------------+--------------------------------------------------+-----------------+
| pyFiles        | files to be placed on the PYTHONPATH             | list of paths   |
+----------------+--------------------------------------------------+-----------------+
| files          | files to be placed in executor working directory | list of paths   |
+----------------+--------------------------------------------------+-----------------+
| driverMemory   | memory for driver                                | string          |
+----------------+--------------------------------------------------+-----------------+
| driverCores    | number of cores used by driver                   | int             |
+----------------+--------------------------------------------------+-----------------+
| executorMemory | memory for executor                              | string          |
+----------------+--------------------------------------------------+-----------------+
| executorCores  | number of cores used by executor                 | int             |
+----------------+--------------------------------------------------+-----------------+
| numExecutors   | number of executor                               | int             |
+----------------+--------------------------------------------------+-----------------+
| archives       |                                                  | list of paths   |
+----------------+--------------------------------------------------+-----------------+

Response Body
^^^^^^^^^^^^^

The created `Batch`_ object.


GET /batches/{batchId}
----------------------

Request Parameters
^^^^^^^^^^^^^^^^^^

+------+-----------------------------+------+
| name | description                 | type |
+======+=============================+======+
| from | offset                      | int  |
+------+-----------------------------+------+
| size | amount of batches to return | int  |
+------+-----------------------------+------+

Response Body
^^^^^^^^^^^^^

+-------+-----------------------------+-----------------+
| name  | description                 | type            |
+=======+=============================+=================+
| id    | `batch`_ list               | list            |
+-------+-----------------------------+-----------------+
| state | The state of the batch      | `batch`_ state  |
+-------+-----------------------------+-----------------+
| lines | The output of the batch job | list of strings |
+-------+-----------------------------+-----------------+


DELETE /batches/{batchId}
-------------------------

Kill the `Batch`_ job.


GET /sessions
-------------

Returns all the active interactive sessions.

Response Body
^^^^^^^^^^^^^

+----------+-----------------+------+
| name     | description     | type |
+==========+=================+======+
| sessions | `session`_ list | list |
+----------+-----------------+------+


POST /sessions
--------------

Request Body
^^^^^^^^^^^^

+------+--------------+----------------------------+
| name | description  | type                       |
+======+==============+============================+
| lang | session kind | `session kind`_ (required) |
+------+--------------+----------------------------+

Response Body
^^^^^^^^^^^^^

The created `Session`_.


GET /sessions/{sessionId}
-------------------------

Return the session information

Response
^^^^^^^^

The `Session`_.


DELETE /sessions/{batchId}
-------------------------

Kill the `Session`_ job.


GET /sessions/{sessionId}/statements
------------------------------------

Return all the statements in a session.

Response Body
^^^^^^^^^^^^^

+------------+-------------------+------+
| name       | description       | type |
+============+===================+======+
| statements | `statement`_ list | list |
+------------+-------------------+------+


POST /sessions/{sessionId}/statements
-------------------------------------

Execute a statement in a session.

Request Body
^^^^^^^^^^^^

+------+---------------------+--------+
| name | description         | type   |
+======+=====================+========+
| code | The code to execute | string |
+------+---------------------+--------+

Response Body
^^^^^^^^^^^^^

The `statement`_ object.


REST Objects
============

Batch
-----

+----------------+--------------------------------------------------------------------------------+-----------------+
| name           | description                                                                    | type            |
+================+================================================================================+=================+
| file           | archive holding the file                                                       | path (required) |
+----------------+--------------------------------------------------------------------------------+-----------------+
| args           | command line arguments                                                         | list of strings |
+----------------+--------------------------------------------------------------------------------+-----------------+
| className      | application's java/spark main class                                            | string          |
+----------------+--------------------------------------------------------------------------------+-----------------+
| jars           | files to be placed on the java classpath                                       | list of paths   |
+----------------+--------------------------------------------------------------------------------+-----------------+
| pyFiles        | files to be placed on the PYTHONPATH                                           | list of paths   |
+----------------+--------------------------------------------------------------------------------+-----------------+
| files          | files to be placed in executor working directory                               | list of paths   |
+----------------+--------------------------------------------------------------------------------+-----------------+
| driverMemory   | memory for driver                                                              | string          |
+----------------+--------------------------------------------------------------------------------+-----------------+
| driverCores    | number of cores used by driver (YARN mode only)                                | int             |
+----------------+--------------------------------------------------------------------------------+-----------------+
| executorMemory | memory for executor                                                            | string          |
+----------------+--------------------------------------------------------------------------------+-----------------+
| executorCores  | number of cores used by executor                                               | int             |
+----------------+--------------------------------------------------------------------------------+-----------------+
| numExecutors   | number of executors (YARN mode only)                                           | int             |
+----------------+--------------------------------------------------------------------------------+-----------------+
| archives       | Archives to be uncompressed in the executor working directory (YARN mode only) | list of paths   |
+----------------+--------------------------------------------------------------------------------+-----------------+

Session
-------

Sessions represent an interactive shell.

+----------------+--------------------------------------------------------------------------------+------------------+
| name           | description                                                                    | type             |
+================+================================================================================+==================+
| id             | The session id                                                                 | string           |
+----------------+--------------------------------------------------------------------------------+------------------+
| state          | The state of the session                                                       | `session state`_ |
+----------------+--------------------------------------------------------------------------------+------------------+
| kind           | The session kind                                                               | `session kind`_  |
+----------------+--------------------------------------------------------------------------------+------------------+
| proxyUser      | The user running this session                                                  | optional string  |
+----------------+--------------------------------------------------------------------------------+------------------+
| jars           | files to be placed on the java classpath                                       | list of paths    |
+----------------+--------------------------------------------------------------------------------+------------------+
| pyFiles        | files to be placed on the PYTHONPATH                                           | list of paths    |
+----------------+--------------------------------------------------------------------------------+------------------+
| files          | files to be placed in executor working directory                               | list of paths    |
+----------------+--------------------------------------------------------------------------------+------------------+
| driverMemory   | memory for driver                                                              | string           |
+----------------+--------------------------------------------------------------------------------+------------------+
| driverCores    | number of cores used by driver (YARN mode only)                                | int              |
+----------------+--------------------------------------------------------------------------------+------------------+
| executorMemory | memory for executor                                                            | string           |
+----------------+--------------------------------------------------------------------------------+------------------+
| executorCores  | number of cores used by executor                                               | int              |
+----------------+--------------------------------------------------------------------------------+------------------+
| numExecutors   | number of executors (YARN mode only)                                           | int              |
+----------------+--------------------------------------------------------------------------------+------------------+
| archives       | Archives to be uncompressed in the executor working directory (YARN mode only) | list of paths    |
+----------------+--------------------------------------------------------------------------------+------------------+

Session State
^^^^^^^^^^^^^

+-------------+----------------------------------+
| name        | description                      |
+=============+==================================+
| not_started | session has not been started     |
+-------------+----------------------------------+
| starting    | session is starting              |
+-------------+----------------------------------+
| idle        | session is waiting for input     |
+-------------+----------------------------------+
| busy        | session is executing a statement |
+-------------+----------------------------------+
| error       | session errored out              |
+-------------+----------------------------------+
| dead        | session has exited               |
+-------------+----------------------------------+

Session Kind
^^^^^^^^^^^^

+---------+----------------------------------+
| name    | description                      |
+=========+==================================+
| spark   | interactive scala/spark session  |
+---------+----------------------------------+
| pyspark | interactive python/spark session |
+---------+----------------------------------+

Statement
---------

Statements represent the result of an execution statement.

+--------+----------------------+---------------------+
| name   | description          | type                |
+========+======================+=====================+
| id     | The statement id     | integer             |
+--------+----------------------+---------------------+
| state  | The execution state  | `statement state`_  |
+--------+----------------------+---------------------+
| output | The execution output | `statement output`_ |
+--------+----------------------+---------------------+

Statement State
^^^^^^^^^^^^^^^

+-----------+----------------------------------+
| name      | description                      |
+===========+==================================+
| running   | Statement is currently executing |
+-----------+----------------------------------+
| available | Statement has a ready response   |
+-----------+----------------------------------+
| error     | Statement failed                 |
+-----------+----------------------------------+

Statement Output
^^^^^^^^^^^^^^^^

+-----------------+-------------------+----------------------------------+
| name            | description       | type                             |
+=================+===================+==================================+
| status          | execution status  | string                           |
+-----------------+-------------------+----------------------------------+
| execution_count | a monotomically   | integer                          |
|                 | increasing number |                                  |
+-----------------+-------------------+----------------------------------+
| data            | statement output  | an object mapping a mime type to |
|                 |                   | the result. If the mime type is  |
|                 |                   | ``application/json``, the value  |
|                 |                   | will be a JSON value             |
+-----------------+-------------------+----------------------------------+


License
=======

Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
