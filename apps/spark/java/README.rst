Welcome to Livy, the REST Spark Server
======================================

Livy is an open source REST interface for interacting with Spark from anywhere. It supports executing snippets of code or programs in a Spark context that runs locally or in YARN.

* Interactive Scala, Python and R shells
* Batch submissions in Scala, Java, Python
* Multi users can share the same server (impersonation support)
* Can be used for submitting jobs from anywhere with REST
* Does not require any code change to your programs

The code is currently incubating in Hue but hopefully will eventually graduate in its top
project. `Pull requests`_ are welcomed!

.. _Pull requests: https://github.com/cloudera/hue/pulls


Quick Start
===========

Livy is used for powering the Spark snippets of the `Hadoop Notebook`_ of `Hue 3.8`_, which you can see the
`implementation here`_.

See the API documentation below and some curl examples:

  * `Interactive shells`_
  * `Batch jobs`_
  * `Shared RDDs`_

.. _Interactive shells: http://gethue.com/how-to-use-the-livy-spark-rest-job-server-for-interactive-spark/
.. _Batch jobs: http://gethue.com/how-to-use-the-livy-spark-rest-job-server-api-for-sharing-spark-rdds-and-contexts/
.. _Shared RDDs: http://gethue.com/how-to-use-the-livy-spark-rest-job-server-api-for-submitting-batch-jar-python-and-streaming-spark-jobs/
.. _Hadoop Notebook: http://gethue.com/new-notebook-application-for-spark-sql/
.. _Hue 3.8: http://gethue.com/hue-3-8-with-an-oozie-editor-revamp-better-performances-improved-spark-ui-is-out/
.. _implementation here: https://github.com/cloudera/hue/blob/master/apps/spark/src/spark/job_server_api.py


Prerequisites
=============

To build/run Livy, you will need:

Debian/Ubuntu:
  * mvn (from ``maven`` package or maven3 tarball)
  * openjdk-7-jdk (or Oracle Java7 jdk)
  * spark 1.4+ from (from `Apache Spark tarball`_)
  * Python 2.6+
  * R 3.x

Redhat/CentOS:
  * mvn (from ``maven`` package or maven3 tarball)
  * java-1.7.0-openjdk (or Oracle Java7 jdk)
  * spark 1.4+ (from `Apache Spark tarball`_)
  * Python 2.6+
  * R 3.x

MacOS:
  * Xcode command line tools
  * Oracle's JDK 1.7+
  * Maven (Homebrew)
  * apache-spark 1.5 (Homebrew)
  * Python 2.6+
  * R 3.x



.. _Apache Spark Tarball: https://spark.apache.org/downloads.html


Building Livy
=============

Livy is currently built by the `Hue Build System`_, it can also be built on
it's own (aka without any other Hue dependency) with `Apache Maven`_. To
checkout and build Livy, run:

.. code:: shell

    % git clone git@github.com:cloudera/hue.git
    % cd hue
    % cd apps/spark/java
    % mvn -DskipTests clean package

By default Livy is built with the Cloudera distribution of Spark (currently
based off Spark 1.5.0), but it is simple to support other versions, such as
Spark 1.4.1, by compiling Livy with:

.. code:: shell

    % mvn -DskipTests -Dspark.version=1.4.1 clean package

.. _Hue Build System: https://github.com/cloudera/hue/#getting-started
.. _Apache Maven: http://maven.apache.org


Running Tests
=============

In order to run the Livy Tests, first follow the instructions in `Building
Livy`_. Then run:

.. code:: shell

    % export SPARK_HOME=/usr/lib/spark
    % export HADOOP_CONF_DIR=/etc/hadoop/conf
    % mvn test


Running Livy
============

In order to run Livy with local sessions, first export these variables:

.. code:: shell

   % export SPARK_HOME=/usr/lib/spark
   % export HADOOP_CONF_DIR=/etc/hadoop/conf

Then start the server with:

.. code:: shell

    % ./bin/livy-server

Or with YARN sessions by running:

.. code:: shell

   % env \
     LIVY_SERVER_JAVA_OPTS="-Dlivy.server.session.factory=yarn" \
     CLASSPATH=`hadoop classpath` \
     $LIVY_HOME/bin/livy-server


Livy Configuration
==================

The properties of the server can be modified by copying
`livy-defaults.conf.template`_ and renaming it ``conf/livy-defaults.conf``. The
Livy configuration directory can be placed in an alternative directory by defining
``LIVY_CONF_DIR``.

In particular the ``YARN mode`` (default is ``local`` process for development) can be set with:

.. code:: shell

    livy.server.session.factory = yarn

.. _livy-defaults.conf.template: https://github.com/cloudera/hue/blob/master/apps/spark/java/conf/livy-defaults.conf.template

Spark Configuration
===================

Livy's Spark sessions are configured through two mechanisms. First, is by way of the local
`Spark configuration`_. Create, or modify the Spark configuration files as directed, and point
Livy at this directory with:

.. code:: shell

    % env \
      SPARK_CONF_DIR=... \
      $LIVY_HOME/bin/livy-server

The second mechanism is by white listing `Spark configuration`_ options that can be set by the user
creating a Spark session. This list can be created by copying
`spark-user-configurable-options.template`_ to ``spark-user-configurable-options`` and listing
the options the user may specify in the ``conf`` session field.

*warning*: Be careful before enabling options. Some options may allow a malicious user to
read files that are accessible by the Livy Server process user. Among other things, this might
allow a user to access the Livy TLS private key, Kerberos tickets, or more.

.. _Spark configuration: https://spark.apache.org/docs/latest/configuration.html
.. _spark-user-configurable-options.template: https://github.com/cloudera/hue/blob/master/apps/spark/java/conf/spark-user-configurable-options.template


Spark Example
=============

Now to see it in action by interacting with it in Python with the `Requests`_
library. By default livy runs on port 8998 (which can be changed with the
``livy_server_port config`` option). We’ll start off with a Spark session that
takes Scala code:

.. code:: shell
    % sudo pip install requests

.. code:: python

    >>> import json, pprint, requests, textwrap
    >>> host = 'http://localhost:8998'
    >>> data = {'kind': 'spark'}
    >>> headers = {'Content-Type': 'application/json'}
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

    >>> statements_url = session_url + '/statements'
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

    >>> data = {'kind': 'pyspark'}
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


SparkR Example
==============

SparkR also has the same API:

.. code:: python

    >>> data = {'kind': 'sparkR'}
    >>> r = requests.post(host + '/sessions', data=json.dumps(data), headers=headers)
    >>> r.json()
    {u'id': 1, u'state': u'idle'}

The PI example from before then can be run as:

.. code:: python

    >>> data = {
    ...   'code': textwrap.dedent("""\
    ...      n <- 100000
    ...      piFunc <- function(elem) {
    ...        rands <- runif(n = 2, min = -1, max = 1)
    ...        val <- ifelse((rands[1]^2 + rands[2]^2) < 1, 1.0, 0.0)
    ...        val
    ...      }
    ...      piFuncVec <- function(elems) {
    ...        message(length(elems))
    ...        rands1 <- runif(n = length(elems), min = -1, max = 1)
    ...        rands2 <- runif(n = length(elems), min = -1, max = 1)
    ...        val <- ifelse((rands1^2 + rands2^2) < 1, 1.0, 0.0)
    ...        sum(val)
    ...      }
    ...      rdd <- parallelize(sc, 1:n, slices)
    ...      count <- reduce(lapplyPartition(rdd, piFuncVec), sum)
    ...      cat("Pi is roughly", 4.0 * count / n, "\n")
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
 * Umbrella Jira: https://issues.cloudera.org/browse/HUE-2588
 * Pull requests: https://github.com/cloudera/hue/pulls


REST API
========

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

Creates a new interative Scala, Python or R shell in the cluster.

Request Body
^^^^^^^^^^^^

+-------------------+--------------------------------------------------------------------------------+-----------------+
| name              | description                                                                    | type            |
+===================+================================================================================+=================+
| kind              | The session kind (required)                                                    | `session kind`_ |
+-------------------+--------------------------------------------------------------------------------+-----------------+
| proxyUser         | The user to impersonate that will run this session (e.g. bob)                  | string          |
+-------------------+--------------------------------------------------------------------------------+-----------------+
| jars              | Files to be placed on the java classpath                                       | list of paths   |
+-------------------+--------------------------------------------------------------------------------+-----------------+
| pyFiles           | Files to be placed on the PYTHONPATH                                           | list of paths   |
+-------------------+--------------------------------------------------------------------------------+-----------------+
| files             | Files to be placed in executor working directory                               | list of paths   |
+-------------------+--------------------------------------------------------------------------------+-----------------+
| driverMemory      | Memory for driver (e.g. 1000M, 2G)                                             | string          |
+-------------------+--------------------------------------------------------------------------------+-----------------+
| driverCores       | Number of cores used by driver (YARN mode only)                                | int             |
+-------------------+--------------------------------------------------------------------------------+-----------------+
| executorMemory    | Memory for executor (e.g. 1000M, 2G)                                           | string          |
+-------------------+--------------------------------------------------------------------------------+-----------------+
| executorCores     | Number of cores used by executor                                               | int             |
+-------------------+--------------------------------------------------------------------------------+-----------------+
| totalExecutorCores| number of cluster cores used by executor (Standalone mode only)                | int             |
+-------------------+--------------------------------------------------------------------------------+-----------------+
| numExecutors      | Number of executors (YARN mode only)                                           | int             |
+-------------------+--------------------------------------------------------------------------------+-----------------+
| archives          | Archives to be uncompressed in the executor working directory (YARN mode only) | list of paths   |
+-------------------+--------------------------------------------------------------------------------+-----------------+
| queue             | The YARN queue to submit too (YARN mode only)                                  | string          |
+-------------------+--------------------------------------------------------------------------------+-----------------+
| name              | Name of the application                                                        | string          |
+-------------------+--------------------------------------------------------------------------------+-----------------+
| conf              | Spark configuration property                                                   | Map of key=val  |
+-------------------+--------------------------------------------------------------------------------+-----------------+


Response Body
^^^^^^^^^^^^^

The created `Session`_.


GET /sessions/{sessionId}
-------------------------

Return the session information

Response
^^^^^^^^

The `Session`_.


DELETE /sessions/{sessionId}
----------------------------

Kill the `Session`_ job.


GET /sessions/{sessionId}/logs
------------------------------

Get the log lines from this session.

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

+------+-----------------------+-----------------+
| name | description           | type            |
+======+=======================+=================+
| id   | The session id        | int             |
+------+-----------------------+-----------------+
| from | offset                | int             |
+------+-----------------------+-----------------+
| size | total amount of lines | int             |
+------+-----------------------+-----------------+
| log  | The log lines         | list of strings |
+------+-----------------------+-----------------+


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

+----------------+---------------------------------------------------+-----------------+
| name           | description                                       | type            |
+================+===================================================+=================+
| proxyUser      | The user to impersonate that will execute the job | string          |
+----------------+---------------------------------------------------+-----------------+
| file           | Archive holding the file                          | path (required) |
+----------------+---------------------------------------------------+-----------------+
| args           | Command line arguments                            | list of strings |
+----------------+---------------------------------------------------+-----------------+
| className      | Application's java/spark main class               | string          |
+----------------+---------------------------------------------------+-----------------+
| jars           | Files to be placed on the java classpath          | list of paths   |
+----------------+---------------------------------------------------+-----------------+
| pyFiles        | Files to be placed on the PYTHONPATH              | list of paths   |
+----------------+---------------------------------------------------+-----------------+
| files          | Files to be placed in executor working directory  | list of paths   |
+----------------+---------------------------------------------------+-----------------+
| driverMemory   | Memory for driver (e.g. 1000M, 2G)                | string          |
+----------------+---------------------------------------------------+-----------------+
| driverCores    | Number of cores used by driver                    | int             |
+----------------+---------------------------------------------------+-----------------+
| executorMemory | Memory for executor (e.g. 1000M, 2G)              | string          |
+----------------+---------------------------------------------------+-----------------+
| executorCores  | Number of cores used by executor                  | int             |
+----------------+---------------------------------------------------+-----------------+
| numExecutors   | Number of executor                                | int             |
+----------------+---------------------------------------------------+-----------------+
| archives       | Archives to be uncompressed (YARN mode only)      | list of paths   |
+----------------+---------------------------------------------------+-----------------+
| queue          | The YARN queue to submit too (YARN mode only)     | string          |
+----------------+---------------------------------------------------+-----------------+
| name           | Name of the application                           | string          |
+----------------+---------------------------------------------------+-----------------+
| conf           | Spark configuration property                      | Map of key=val  |
+----------------+---------------------------------------------------+-----------------+


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
| id    | The batch id                | int             |
+-------+-----------------------------+-----------------+
| state | The state of the batch      | `batch`_ state  |
+-------+-----------------------------+-----------------+
| log   | The output of the batch job | list of strings |
+-------+-----------------------------+-----------------+


DELETE /batches/{batchId}
-------------------------

Kill the `Batch`_ job.


GET /batches/{batchId}/logs
---------------------------

Get the log lines from this batch.

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

+------+-----------------------+-----------------+
| name | description           | type            |
+======+=======================+=================+
| id   | The batch id          | int             |
+------+-----------------------+-----------------+
| from | offset                | int             |
+------+-----------------------+-----------------+
| size | total amount of lines | int             |
+------+-----------------------+-----------------+
| log  | The log lines         | list of strings |
+------+-----------------------+-----------------+


REST Objects
============

Session
-------

Sessions represent an interactive shell.

+----------------+--------------------------------------------------+----------------------------+
| name           | description                                      | type                       |
+================+==================================================+============================+
| id             | The session id                                   | int                        |
+----------------+--------------------------------------------------+----------------------------+
| kind           | session kind (spark, pyspark, or sparkr)         | `session kind`_ (required) |
+----------------+--------------------------------------------------+----------------------------+
| log            | The log lines                                    | list of strings            |
+----------------+--------------------------------------------------+----------------------------+
| state          | The session state                                | string                     |
+----------------+--------------------------------------------------+----------------------------+


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
| sparkr  | interactive R/spark session      |
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

Batch
-----

+----------------+--------------------------------------------------+----------------------------+
| name           | description                                      | type                       |
+================+==================================================+============================+
| id             | The session id                                   | int                        |
+----------------+--------------------------------------------------+----------------------------+
| kind           | session kind (spark, pyspark, or sparkr)         | `session kind`_ (required) |
+----------------+--------------------------------------------------+----------------------------+
| log            | The log lines                                    | list of strings            |
+----------------+--------------------------------------------------+----------------------------+
| state          | The session state                                | string                     |
+----------------+--------------------------------------------------+----------------------------+


License
=======

Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
