Phoenix database adapter for Python
===================================

``phoenixdb`` is a Python library for accessing 
`Apache Phoenix <http://phoenix.apache.org/>`_
using the
`remote query server <http://phoenix.apache.org/server.html>`_.
This library implements the
standard `DB API 2.0 <https://www.python.org/dev/peps/pep-0249/>`_ interface and a
subset of `SQLAlchemy <https://www.sqlalchemy.org/>`_, either of which should be familiar
to most Python programmers.

Installation
------------

The source code is part of the phoenix-queryserver source distribution.
You can download it from <https://phoenix.apache.org/>, or get the latest development version
from <https://github.com/apache/phoenix-queryserver>

Extract the archive and then install it manually::

    cd /path/to/phoenix-queryserver-x.y.z/python/phoenixdb
    python setup.py install

Usage
-----

The library implements the standard DB API 2.0 interface, so it can be
used the same way you would use any other SQL database from Python, for example::

    import phoenixdb
    import phoenixdb.cursor

    database_url = 'http://localhost:8765/'
    conn = phoenixdb.connect(database_url, autocommit=True)

    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR)")
    cursor.execute("UPSERT INTO users VALUES (?, ?)", (1, 'admin'))
    cursor.execute("SELECT * FROM users")
    print(cursor.fetchall())

    cursor = conn.cursor(cursor_factory=phoenixdb.cursor.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id=1")
    print(cursor.fetchone()['USERNAME'])


Setting up a development environment
------------------------------------

If you want to quickly try out the included examples, you can set up a
local `virtualenv <https://virtualenv.pypa.io/en/latest/>`_ with all the
necessary requirements::

    virtualenv e
    source e/bin/activate
    pip install -r requirements.txt
    python setup.py develop

You can start a Phoenix QueryServer instance on http://localhost:8765 for testing by running
the following command in the phoenix-queryserver directory::

    mvn clean verify -am -pl phoenix-queryserver-it -Dtest=foo \
    -Dit.test=QueryServerBasicsIT\#startLocalPQS \
    -Ddo.not.randomize.pqs.port=true -Dstart.unsecure.pqs=true

You can start a secure (https+kerberos) Phoenix QueryServer instance on https://localhost:8765
for testing by running the following command in the phoenix-queryserver directory::

    mvn clean verify -am -pl phoenix-queryserver-it -Dtest=foo \
    -Dit.test=SecureQueryServerPhoenixDBIT\#startLocalPQS \
    -Ddo.not.randomize.pqs.port=true -Dstart.secure.pqs=true

this will also create a shell script in phoenix-queryserver-it/target/krb_setup.sh, that you can use to set
up the environment for the tests.

If you want to use the library without installing the phoenixdb library, you can use
the `PYTHONPATH` environment variable to point to the library directly::

    cd $PHOENIX_HOME/python
    python setup.py build
    cd ~/my_project
    PYTHONPATH=$PHOENIX_HOME/build/lib python my_app.py

Don't forget to run flake8 on your changes.

Running the test suite
----------------------

The library comes with a test suite for testing Python DB API 2.0 compliance and
various Phoenix-specific features. In order to run the test suite, you need a
working Phoenix database and set the ``PHOENIXDB_TEST_DB_URL`` environment variable::

    export PHOENIXDB_TEST_DB_URL='http://localhost:8765/'
    nosetests

If you use a secure PQS server, you can set the connection parameters via the following environment
variables:

- PHOENIXDB_TEST_DB_TRUSTSTORE
- PHOENIXDB_TEST_DB_AUTHENTICATION
- PHOENIXDB_TEST_DB_AVATICA_USER
- PHOENIXDB_TEST_DB_AVATICA_PASSWORD

Similarly, tox can be used to run the test suite against multiple Python versions::

    pyenv install 3.5.5
    pyenv install 3.6.4
    pyenv install 2.7.14
    pyenv global 2.7.14 3.5.5 3.6.4
    PHOENIXDB_TEST_DB_URL='http://localhost:8765' tox

You can use tox and docker to run the tests on all supported python versions without installing the
environments locally::

    docker build -t toxtest .
    docker run --rm  -v `pwd`:/src toxtest

You can also run the test suite from maven as part of the Java build by setting the 
run.full.python.testsuite property. You DO NOT need to set the PHOENIXDB_* enviroment variables,
maven will set them up for you. The output of the test run will be saved in
phoenix-queryserver/phoenix-queryserver-it/target/python-stdout.log and python-stderr.log::

    mvn clean verify -Drun.full.python.testsuite=true

Known issues
------------

- TIME and DATE columns in Phoenix are stored as full timestamps with a millisecond accuracy,
  but the remote protocol only exposes the time (hour/minute/second) or date (year/month/day)
  parts of the columns. (`CALCITE-797 <https://issues.apache.org/jira/browse/CALCITE-797>`_, `CALCITE-798 <https://issues.apache.org/jira/browse/CALCITE-798>`_)
- TIMESTAMP columns in Phoenix are stored with a nanosecond accuracy, but the remote protocol truncates them to milliseconds. (`CALCITE-796 <https://issues.apache.org/jira/browse/CALCITE-796>`_)


SQLAlchemy feature support
--------------------------

SQLAlchemy has a wide breadth of API, ranging from basic SQL commands to object-relational mapping support.

Today, python-phoenixdb only supports the following subset of the complete SQLAlchemy API:

- `Textual SQL <https://docs.sqlalchemy.org/en/13/core/tutorial.html#using-textual-sql>`_

All other API should be considered not implemented.
