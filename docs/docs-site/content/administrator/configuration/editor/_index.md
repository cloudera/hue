---
title: "Editor"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 2
---

The goal of the Editor is to open-up data to more users by making self service querying easy and productive.
It has one of the best SQL autocomplete and many [more features]({{% param baseURL %}}administrator/configuration/editor/).

It is available in Editor or Notebook. Dialects can be added to the main `[notebook]` section like this:

    [notebook]

      [[interpreters]]

        [[[hive]]]
          # The name of the snippet.
          name=Hive
          # The backend connection to use to communicate with the server.
          interface=hiveserver2

        [[[mysql]]]
          name = MySQL
          interface=sqlalchemy
          options='{"url": "mysql://root:root@localhost:3306/hue"}'

**Tip** Do not forget to uncomment the lines by removing the `#` and editing the sections at the correct levels.

## Editor

The editor supports some global settings.

### Downloads

Download and export options with limited scalability can be limited in the number of rows or bytes transferred using the following options respectively in your hue.ini:

        [beeswax]
        # A limit to the number of rows that can be downloaded from a query before it is truncated.
        # A value of -1 means there will be no limit.
        download_row_limit=-1

        # A limit to the number of bytes that can be downloaded from a query before it is truncated.
        # A value of -1 means there will be no limit.
        download_bytes_limit=-1

In addition, it is possible to disable the download and export feature in the editor, dashboard, as well as in the file browser with the following option in your hue.ini:

        [desktop]
        # Global setting to allow or disable end user downloads in all Hue.
        # e.g. Query result in Editors and Dashboards, file in File Browser...
        enable_download=false

The download feature in the file browser can be disabled separately with the following options in your hue.ini:

        [filebrowser]
        show_download_button=false

### Notebook

Enable the Notebook mode which supports multiple snippets of code.

      [notebook]
      show_notebooks=true

### External statements

Enable the selection of queries from files, saved queries into the editor or as snippet.

      [notebook]
      enable_external_statements=false

### Batch querying

This option currently only works with Hive and relies on Oozie until [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) gets done.

      [notebook]
      enable_batch_execute=true

### Assist Query Builder

Flag to enable a lightweight SQL query builder where tables and columns can be dragged & dropped from the left table assist. Not to be confused with the [Query Builder](../dashboard).

**Note** This feature is experimental.

      [notebook]
      enable_query_builder=true

### Query Analysis

Display an analysis panel post Impala queries executions with some hints and suggestions.

**Note** This feature is experimental.

      [notebook]
      enable_query_analysis=true

### Query Optimization

In the `[metadata]` section, Hue is supporting Cloudera Navigator Optimiser and soon other services. The goal is to provide recommendation on how to write better queries and get risk alerts on dangerous operations directly within the [editor]({{% param baseURL %}}user/editor/).

### One-click scheduling

Enable the creation of a coordinator for the current SQL query.

**Note** This feature is experimental until Task Server scheduler [HUE-8740](https://issues.cloudera.org/browse/HUE-8740).

      [notebook]
      enable_query_scheduling=true

### Credentials

When username or password are not specified in the connection URL, they will be prompted at connection time in the user browser.

Parameters are not saved at any time in the Hue database. The are currently not even cached in the Hue process. The clients serves these parameters
each time a query is sent.


## Connectors

Native connectors (via the `hiveserver2` interface) are recommended for Hive and Impala, otherwise SqlAlchemy is prefered. Read more about the [interfaces below](#interfaces).

### Impala

Support is native via a dedicated section.

    [impala]
      # Host of the Impala Server (one of the Impalad)
      server_host=localhost

      # Port of the Impala Server
      server_port=21050

Read more about [LDAP or PAM pass-through authentication](http://gethue.com/ldap-or-pam-pass-through-authentication-with-hive-or-impala/) and [High Availability](../external/).

### Hive

Support is native via a dedicated section.

    [beeswax]

      # Host where HiveServer2 is running.
      # If Kerberos security is enabled, use fully-qualified domain name (FQDN).
      hive_server_host=localhost

      # Port where HiveServer2 Thrift server runs on.
      hive_server_port=10000

Read more about [LDAP or PAM pass-through authentication](http://gethue.com/ldap-or-pam-pass-through-authentication-with-hive-or-impala/) and [High Availability](../external/).

**Tez**

Requires support for sending multiple queries when using Tez (instead of a maximum of just one at the time). You can turn it on with this setting:

    [beeswax]
    max_number_of_sessions=10

**Note** For historical reason, the name of the configuration section is `[beeswax]`.


### MySQL

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install mysqlclient

Then give Hue the information about the database source:

    [[[mysql]]]
       name = MySQL
       interface=sqlalchemy
       options='{"url": "mysql://root:root@localhost:3306/hue"}'
       ## mysql://${USER}:${PASSWORD}@localhost:3306/hue

Query string options are documented in the [SqlAlchemy MySQL documentation](https://docs.sqlalchemy.org/en/latest/dialects/mysql.html).

Alternative:

    [[[mysqljdbc]]]
       name=MySql JDBC
      interface=jdbc
       ## Specific options for connecting to the server.
       ## The JDBC connectors, e.g. mysql.jar, need to be in the CLASSPATH environment variable.
       ## If 'user' and 'password' are omitted, they will be prompted in the UI.
       options='{"url": "jdbc:mysql://localhost:3306/hue", "driver": "com.mysql.jdbc.Driver", "user": "root", "password": "root"}'
       ## options='{"url": "jdbc:mysql://localhost:3306/hue", "driver": "com.mysql.jdbc.Driver"}'

### Presto

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install pyhive

Then give Hue the information about the database source:

    [[[presto]]]
       name = Presto
       interface=sqlalchemy
       options='{"url": "presto://localhost:8080/hive/default"}'

Alternatives.

Direct interface:

    [[[presto]]]
      name=Presto SQL
      interface=presto
      ## Specific options for connecting to the Presto server.
      ## The JDBC driver presto-jdbc.jar need to be in the CLASSPATH environment variable.
      ## If 'user' and 'password' are omitted, they will be prompted in the UI.
      options='{"url": "jdbc:presto://localhost:8080/catalog/schema", "driver": "io.prestosql.jdbc.PrestoDriver", "user": "root", "password": "root"}'

JDBC:

The client driver is maintained by the Presto Team and can be downloaded here: https://prestosql.io/docs/current/installation/jdbc.html

    [[[presto]]]
    name=Presto JDBC
    interface=jdbc
    options='{"url": "jdbc:presto://localhost:8080/", "driver": "io.prestosql.jdbc.PrestoDriver"}'

### Oracle

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install cx_Oracle

Then give Hue the information about the database source:

    [[[oracle]]]
       name = Oracle
       interface=sqlalchemy
       options='{"url": "oracle://scott:tiger@dsn"}'

### PostgreSql

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install psycopg2
      or
      ./build/env/bin/pip install psycopg2-binary

Then give Hue the information about the database source:

    [[[postgresql]]]
       name = PostgreSql
       interface=sqlalchemy
       options='{"url": "postgresql+psycopg2://..."}'

Alternative:

First, in your hue.ini file, you will need to add the relevant database connection information under the librdbms section:

    [librdbms]
      [[databases]]
        [[[postgresql]]]
        nice_name=PostgreSQL
        name=music
        engine=postgresql_psycopg2
        port=5432
        user=hue
        password=hue
        options={}

Secondly, we need to add a new interpreter to the notebook app. This will allow the new database type to be registered as a snippet-type in the Notebook app. For query editors that use a Django-compatible database, the name in the brackets should match the database configuration name in the librdbms section (e.g. – postgresql). The interface will be set to rdbms. This tells Hue to use the librdbms driver and corresponding connection information to connect to the database. For example, with the above postgresql connection configuration in the librdbms section, we can add a PostgreSQL interpreter with the following notebook configuration:

    [notebook]
      [[interpreters]]
        [[[postgresql]]]
        name=PostgreSQL
        interface=rdbms

### AWS Athena

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install PyAthena

Then give Hue the information about the database source:

    [[[athena]]]
       name = AWS Athena
       interface=sqlalchemy
       options='{"url": "awsathena+rest://..."}'

### Apache Druid

First, make sure that Hue can talk to Druid via the pydruid SqlAlchemy connector. Either make sure it is in the global Python environment or install it in the Hue virtual environment.

      ./build/env/bin/pip install pydruid

**Note** Make sure the version is equal or more to 0.4.1 if not you will get a "Can't load plugin: sqlalchemy.dialects:druid".

In the hue.ini configuration file, now let's add the interpreter. Here 'druid-host.com' would be the machine where Druid is running.

      [notebook]
      [[interpreters]]
      [[[druid]]]
      name = Druid
      interface=sqlalchemy
      options='{"url": "druid://druid-host.com:8082/druid/v2/sql/"}'

### Teradata

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install sqlalchemy-teradata

Then give Hue the information about the database source:

    [[[teradata]]]
       name = Teradata
       interface=sqlalchemy
       options='{"url": "teradata://user:pw@host"}'

Alternative:

    [[[teradata]]]
      name=Teradata JDBC
      interface=jdbc
      options='{"url": "jdbc:teradata://sqoop-teradata-1400.sjc.cloudera.com/sqoop", "driver": "com.teradata.jdbc.TeraDriver", "user": "sqoop", "password": "sqoop"}'

### DB2

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install ibm_db_sa

(or via https://github.com/ibmdb/python-ibmdbsa/tree/master/ibm_db_sa)

Then give Hue the information about the database source:

    [[[db2]]]
       name = DB2
       interface=sqlalchemy
       options='{"url": "db2+ibm_db://user:pass@host[:port]/database"}'

Alternative:

    [[[db2]]]
      name=DB2 JDBC
      interface=jdbc
      options='{"url": "jdbc:db2://db2.vpc.cloudera.com:50000/SQOOP", "driver": "com.ibm.db2.jcc.DB2Driver", "user": "DB2INST1", "password": "cloudera"}'

### Spark SQL

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install pyhive

Then give Hue the information about the database source:

    [[[sparksql]]]
       name = SparkSql
       interface=sqlalchemy
       options='{"url": "hive://user:password@host:10000/database"}'

Alternatives:

Via [Apache Livy](https://livy.incubator.apache.org/):

    [[[sparksql]]]
      name=SparkSql
      interface=livy

    ...

    [spark]
      # The Livy Server URL.
      livy_server_url=http://localhost:8998

Via native HiveServer2 API:

    [[[sparksql]]]
      name=SparkSql
      interface=hiveserver2

### Kafka SQL

    [[[kafkasql]]]
      name=Kafka SQL
      interface=kafka

### MS SQLServer

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install pymssql

Then give Hue the information about the database source:

    [[[mssql]]]
       name = SQL Server
       interface=sqlalchemy
       options='{"url": "mssql+pymssql://<username>:<password>@<freetds_name>/?charset=utf8"}'

Alternative:

Microsoft’s SQL Server JDBC drivers can be downloaded from the official site: [Microsoft JDBC Driver](https://msdn.microsoft.com/en-us/sqlserver/aa937724.aspx)

    [[[sqlserver]]]
    name=SQLServer JDBC
    interface=jdbc
    options='{"url": "jdbc:microsoft:sqlserver://localhost:1433", "driver": "com.microsoft.jdbc.sqlserver.SQLServerDriver", "user": "admin": "password": "pass"}'

### Vertica

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install sqlalchemy-vertica-python

Then give Hue the information about the database source:

    [[[vertica]]]
       name = Vertica
       interface=sqlalchemy
       options='{"url": "vertica+vertica_python://user:pwd@host:port/database"}'

Alternative:

Vertica’s JDBC client drivers can be downloaded here: [Vertica JDBC Client Drivers](https://my.vertica.com/download/vertica/client-drivers/). Be sure to download the driver for the right version and OS.

    [[[vertica]]]
    name=Vertica JDBC
    interface=jdbc
    options='{"url": "jdbc:vertica://localhost:5433/example", "driver": "com.vertica.jdbc.Driver", "user": "admin", "password": "pass"}'

### Phoenix

The Phoenix JDBC client driver is bundled with the Phoenix binary and source release artifacts, which can be downloaded here: [Apache Phoenix Downloads](https://phoenix.apache.org/download.html). Be sure to use the Phoenix client driver that is compatible with your Phoenix server version.

    [[[phoenix]]]
    name=Phoenix JDBC
    interface=jdbc
    options='{"url": "jdbc:phoenix:localhost:2181/hbase", "driver": "org.apache.phoenix.jdbc.PhoenixDriver", "user": "", "password": ""}'

**Note**: Currently, the Phoenix JDBC connector for Hue only supports read-only operations (SELECT and EXPLAIN statements).

### AWS Redshift

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install sqlalchemy-redshift

Then give Hue the information about the database source:

    [[[redshift]]]
       name = Redshift
       interface=sqlalchemy
       options='{"url": "redshift+psycopg2://username@host.amazonaws.com:5439/database"}'

### Google BigQuery

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install pybigquery

From https://github.com/mxmzdlv/pybigquery.

Then give Hue the information about the database source:

    [[[bigquery]]]
       name = BigQuery
       interface=sqlalchemy
       options='{"url": "bigquery://project"}'

### Apache Drill

The dialect is available on https://github.com/JohnOmernik/sqlalchemy-drill

Then give Hue the information about the database source:

    [[[drill]]]
       name = Drill
       interface=sqlalchemy
       options='{"url": "drill+sadrill://..."}'
       ## To use Drill with SQLAlchemy you will need to craft a connection string in the format below:
       # drill+sadrill://<username>:<password>@<host>:<port>/<storage_plugin>?use_ssl=True
       ## To connect to Drill running on a local machine running in embedded mode you can use the following connection string.
       # drill+sadrill://localhost:8047/dfs?use_ssl=False

Alternative:

The [Drill JDBC driver](http://maprdocs.mapr.com/home/Hue/ConfigureHuewithDrill.html) can be used.

    [[[drill]]]
      name=Drill JDBC
      interface=jdbc
      ## Specific options for connecting to the server.
      ## The JDBC connectors, e.g. mysql.jar, need to be in the CLASSPATH environment variable.
      ## If 'user' and 'password' are omitted, they will be prompted in the UI.
      options='{"url": "<drill-jdbc-url>", "driver": "org.apache.drill.jdbc.Driver", "user": "admin", "password": "admin"}'</code>

### Sybase

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install sqlalchemy-teradata

Then give Hue the information about the database source:

    [[[teradata]]]
       name = Teradata
       interface=sqlalchemy
       options='{"url": "sybase+pysybase://<username>:<password>@<dsn>/[database name]"}'


### Hana

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install sqlalchemy-hana

(or via https://github.com/SAP/sqlalchemy-hana)

Then give Hue the information about the database source:

    [[[db2]]]
       name = DB2
       interface=sqlalchemy
       options='{"url": "hana://username:password@example.de:30015"}'

### Solr SQL

    [[[solr]]]
      name = Solr SQL
      interface=solr
      ## Name of the collection handler
      # options='{"collection": "default"}'

### Kylin

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install kylinpy

Then give Hue the information about the database source:

    [[[kylin]]]
       name = Kylin
       interface=sqlalchemy
       options='{"url": "kylin://..."}'

Alternative:

    [[[kylin]]]
     name=kylin JDBC
     interface=jdbc
     options='{"url": "jdbc:kylin://172.17.0.2:7070/learn_kylin", "driver": "org.apache.kylin.jdbc.Driver", "user": "ADMIN", "password": "KYLIN"}'

### Clickhouse

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install sqlalchemy-clickhouse

Then give Hue the information about the database source:

    [[[clickhouse]]]
       name = Clickhouse
       interface=sqlalchemy
       options='{"url": "clickhouse://..."}'

Alternative:

    [[[clickhouse]]]
      name=ClickHouse
      interface=jdbc
      ## Specific options for connecting to the ClickHouse server.
      ## The JDBC driver clickhouse-jdbc.jar and its related jars need to be in the CLASSPATH environment variable.
      options='{"url": "jdbc:clickhouse://localhost:8123", "driver": "ru.yandex.clickhouse.ClickHouseDriver", "user": "readonly", "password": ""}'

### Spark

This connector leverage the [Apache Livy REST Api](https://livy.incubator.apache.org/):

In the `[[interpreters]]` section:

      [[[pyspark]]]
            name=PySpark
            interface=livy

      [[[sql]]]
            name=SparkSql
            interface=livy

      [[[spark]]]
            name=Scala
            interface=livy

      [[[r]]]
            name=R
            interface=livy

In the `[spark]` section:

    [spark]
      # The Livy Server URL.
      livy_server_url=http://localhost:8998

And if using Cloudera distribution, make sure you have notebooks enabled:

    [desktop]
      app_blacklist=

    [notebook]
      show_notebooks=true

**YARN: Spark session could not be created**

If seeing an error similar to this with `primitiveMkdir`:

    The Spark session could not be created in the cluster: at org.apache.hadoop.io.retry.RetryInvocationHandler$Call.invokeMethod(RetryInvocationHandler.java:165)
    at org.apache.hadoop.io.retry.RetryInvocationHandler$Call.invoke(RetryInvocationHandler.java:157)
    at org.apache.hadoop.io.retry.RetryInvocationHandler$Call.invokeOnce(RetryInvocationHandler.java:95)
    at org.apache.hadoop.io.retry.RetryInvocationHandler.invoke(RetryInvocationHandler.java:359) at com.sun.proxy.$Proxy10.mkdirs(Unknown Source)
    at org.apache.hadoop.hdfs.DFSClient.primitiveMkdir(DFSClient.java:2333) ... 20 more
    19/05/13 12:27:07 INFO util.ShutdownHookManager: Shutdown hook called 19/05/13 12:27:07 INFO util.ShutdownHookManager:
    Deleting directory /tmp/spark-0d045154-77a0-4e12-94b2-2df18725a4ae YARN Diagnostics:

Does your logged-in user have a home dir on HDFS (i.e. `/user/bob`)? (you should see the full error in the Livy or YARN logs).

In Hue admin for you user, you can click the 'Create home' checkbox and save.

**CSRF**

Livy supports a configuration parameter in the Livy conf:

      livy.server.csrf-protection.enabled

...which is false by default. Upon trying to launch a Livy session from the notebook, Hue will pass along the connection error from Livy as a 400 response that the "Missing Required Header for CSRF protection". To enable it, add to the Hue config:

      [spark]
      # Whether Livy requires client to use csrf protection.
      ## csrf_enabled=false

### Pig

Pig is native to Hue and depends on the [Oozie service](../external/) to be configured:

    [[[pig]]]
      name=Pig
      interface=oozie

### Snowflake

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install snowflake-sqlalchemy

Then give Hue the information about the database source:

    [[[snowflake]]]
       name = Snowflake
       interface=sqlalchemy
       options='{"url": "snowflake://..."}'

### Sqlite

Just give Hue the information about the database source:

    [[[sqlite]]]
       name = Sqlite
       interface=sqlalchemy
       options='{"url": "sqlite://..."}'

### Greenplum

The dialect should be added to the Python system or Hue Python virtual environment:

      ./build/env/bin/pip install psycopg2

Then give Hue the information about the database source:

    [[[greenplum]]]
       name = Greenplum
       interface=sqlalchemy
       options='{"url": "postgresql+psycopg2://..."}'


## Interfaces

Several interfaces are possible and sometimes more than one works for a certain database. When available `HiveServer2` or `SqlAlchemy` are recommended as they are native.


### Sql Alchemy

SQL Alchemy is a robust [connector](https://docs.sqlalchemy.org/en/latest/core/engines.html#sqlalchemy.create_engine) that supports
many [SQL dialects](https://docs.sqlalchemy.org/en/latest/dialects) natively. This is the recommended connector for most of the databases.

The dialect should be added to the Python system or Hue Python virtual environment. For example for MySQL:

      ./build/env/bin/pip install mysqlclient

Then give Hue the information about the database source:

    [[[mysql]]]
       name = MySQL
       interface=sqlalchemy
       options='{"url": "mysql://root:root@localhost:3306/hue"}'

**Tip**

To offer more self service capabilities, parts of the URL can be parameterized and the information will be asked to the user.

Supported parameters are:

* USER
* PASSWORD

e.g.

      mysql://${USER}:${PASSWORD}@localhost:3306/hue

### HiveServer2

This is the interface that was created for Apache Hive and Apache Impala. The main advantages are that they provide asynchronous executions and so:

* non blocking submission
* progress reports
* non blocking result fetching

For example to point to Hive, first configure the `[beeswax]` section.

    [beeswax]
      # Host where HiveServer2 is running.
      hive_server_host=localhost

      # Port where HiveServer2 Thrift server runs on.
      hive_server_port=10000

Then make sure the `hive` interpreter is present in the `[[interpreters]]` list.

  [[interpreters]]

    [[[hive]]]
      name=Hive
      interface=hiveserver2

### Custom

A series of native connectors interacting with the editor have been developed and are listed in the [developer section]({{% param baseURL %}}developer/editor/).

### JDBC

**Note** This is an historical connector, SQLAlchemy should be prefered at this time.

Use the query editor with any JDBC database.

The “rdbms” interface works great for MySQL, PostgreSQL, SQLite, and Oracle, but for other JDBC-compatible databases Hue now finally supports a “jdbc” interface to integrate such databases with the new query editor!

Integrating an external JDBC database involves a 3-step process:

Download the compatible client driver JAR file for your specific OS and database. Usually you can find the driver files from the official database vendor site; for example, the MySQL JDBC connector for Mac OSX can be found here: https://dev.mysql.com/downloads/connector/j/. (NOTE: In the case of MySQL, the JDBC driver is platform independent, but some drivers are specific to certain OSes and versions so be sure to verify compatibility.)
Add the path to the driver JAR file to your Java CLASSPATH. Here, we set the CLASSPATH environment variable in our `.bash_profile` script.

    # MySQL
    export MYSQL_HOME=/Users/hue/Dev/mysql
    export CLASSPATH=$MYSQL_HOME/mysql-connector-java-5.1.38-bin.jar:$CLASSPATH

Add a new interpreter to the notebook app and supply the “name”, set “interface” to jdbc, and set “options” to a JSON object that contains the JDBC connection information. For example, we can connect a local MySQL database named “hue” running on `localhost` and port `8080` via JDBC with the following configuration:

    [notebook]
      [[interpreters]]
        [[[mysql]]]
        name=MySQL JDBC
        interface=jdbc
        options='{"url": "jdbc:mysql://localhost:3306/hue", "driver": "com.mysql.jdbc.Driver", "user": "root", "password": ""}'

Technically the JDBC is connecting to the database to query via a Java Proxy powered with Py4j. It will automatically
be started if any interpreter is using it.

    ## Main flag to override the automatic starting of the DBProxy server.
    enable_dbproxy_server=true

**Tip**: Testing JDBC Configurations
Before adding your interpreter’s JDBC configurations to hue.ini, verify that the JDBC driver and connection settings work in a SQL client like SQuirrel SQL.

**Tip**: Prompt for JDBC authentication
You can leave out the username and password in the JDBC options, and Hue will instead prompt the user for a username and password. This allows administrators to provide access to JDBC sources without granting all Hue users the same access.

### Django DB Connectors

**Note** This is an historical connector, SQLAlchemy should be prefered at this time.

Those rely on the `[dbms]` lib an dedicated Python libs.

First, in your hue.ini file, add the relevant database connection information under the `[librdbms]` section:

    [librdbms]
      [[databases]]
        [[[postgresql]]]
        nice_name=PostgreSQL
        name=music
        engine=postgresql_psycopg2
        port=5432
        user=hue
        password=hue
        options={}

Secondly, add a new interpreter to the notebook app. This will allow the new database type to be registered as a snippet-type in the Notebook app. For query editors that use a Django-compatible database, the name in the brackets should match the database configuration name in the librdbms section (e.g. – postgresql). The interface will be set to rdbms. This tells Hue to use the librdbms driver and corresponding connection information to connect to the database. For example, with the above postgresql connection configuration in the librdbms section, we can add a PostgreSQL interpreter with the following notebook configuration:

    [notebook]
      [[interpreters]]
        [[[postgresql]]]
        name=PostgreSQL
        interface=rdbms

After updating the configuration and restarting Hue, we can access the new PostgreSQL interpreter in the Notebook app:
