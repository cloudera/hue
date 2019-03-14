---
title: "Hue"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 1
---

The goal of the Editor is to open-up data to more users by making self service querying easy and productive.

It is available in Editor or Notebook mode and focuses on SQL. Dialects can be added to the main `[notebook]` section like this:

    [notebook]

      [[interpreters]]

        [[[hive]]]
          # The name of the snippet.
          name=Hive
          # The backend connection to use to communicate with the server.
          interface=hiveserver2

        [[[mysqlalche]]]
          name = MySQL alchemy
          interface=sqlalchemy
          options='{"url": "mysql://root:root@localhost:3306/hue"}'


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


### Impala

    [impala]
      # Host of the Impala Server (one of the Impalad)
      ## server_host=localhost

      # Port of the Impala Server
      ## server_port=21050

[LDAP or PAM pass-through authentication with Hive or Impala and Impersonation
](http://gethue.com/ldap-or-pam-pass-through-authentication-with-hive-or-impala/).

### Hive

    [beeswax]

      # Host where HiveServer2 is running.
      # If Kerberos security is enabled, use fully-qualified domain name (FQDN).
      ## hive_server_host=localhost

      # Port where HiveServer2 Thrift server runs on.
      ## hive_server_port=10000

**Tez**

Requires support for sending multiple queries when using Tez (instead of a maximum of just one at the time). You can turn it on with this setting:

    [beeswax]
    max_number_of_sessions=10


### MySQL

Recommended way:

    [[[mysql]]]
       name = MySQL Alchemy
       interface=sqlalchemy
       ## https://docs.sqlalchemy.org/en/latest/core/engines.html#sqlalchemy.create_engine
       ## https://docs.sqlalchemy.org/en/latest/dialects/mysql.html
       options='{"url": "mysql://root:root@localhost:3306/hue"}'

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

Direct interface:

    [[[presto]]]
      name=Presto SQL
      interface=presto
      ## Specific options for connecting to the Presto server.
      ## The JDBC driver presto-jdbc.jar need to be in the CLASSPATH environment variable.
      ## If 'user' and 'password' are omitted, they will be prompted in the UI.
      options='{"url": "jdbc:presto://localhost:8080/catalog/schema", "driver": "io.prestosql.jdbc.PrestoDriver", "user": "root", "password": "root"}'

The Presto JDBC client driver is maintained by the Presto Team and can be downloaded here: https://prestodb.io/docs/current/installation/jdbc.html

    [[[presto]]]
    name=Presto JDBC
    interface=jdbc
    options='{"url": "jdbc:presto://localhost:8080/", "driver": "com.facebook.presto.jdbc.PrestoDriver"}'

### Oracle

### PostgreSQL

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

Same as Presto.

### Teradata

    [[[teradata]]]
      name=Teradata JDBC
      interface=jdbc
      options='{"url": "jdbc:teradata://sqoop-teradata-1400.sjc.cloudera.com/sqoop", "driver": "com.teradata.jdbc.TeraDriver", "user": "sqoop", "password": "sqoop"}'

### DB2

    [[[db2]]]
      name=DB2 JDBC
      interface=jdbc
      options='{"url": "jdbc:db2://db2.vpc.cloudera.com:50000/SQOOP", "driver": "com.ibm.db2.jcc.DB2Driver", "user": "DB2INST1", "password": "cloudera"}'

### Spark SQL

Via [Apache Livy](https://livy.incubator.apache.org/) (recommended):

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

### SQLServer

Microsoft’s SQL Server JDBC drivers can be downloaded from the official site: [Microsoft JDBC Driver](https://msdn.microsoft.com/en-us/sqlserver/aa937724.aspx)

    [[[sqlserver]]]
    name=SQLServer JDBC
    interface=jdbc
    options='{"url": "jdbc:microsoft:sqlserver://localhost:1433", "driver": "com.microsoft.jdbc.sqlserver.SQLServerDriver", "user": "admin": "password": "pass"}'

### Vertica

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

### Redshift

### BigQuery

### Drill

The [Drill JDBC driver](http://maprdocs.mapr.com/home/Hue/ConfigureHuewithDrill.html) can be used.

    [[[drill]]]
      name=Drill JDBC
      interface=jdbc
      ## Specific options for connecting to the server.
      ## The JDBC connectors, e.g. mysql.jar, need to be in the CLASSPATH environment variable.
      ## If 'user' and 'password' are omitted, they will be prompted in the UI.
      options='{"url": "<drill-jdbc-url>", "driver": "org.apache.drill.jdbc.Driver", "user": "admin", "password": "admin"}'</code>

### Solr SQL

    [[[solr]]]
      name = Solr SQL
      interface=solr
      ## Name of the collection handler
      # options='{"collection": "default"}'

### Kylin

    [[[kylin]]]
     name=kylin JDBC
     interface=jdbc
     options='{"url": "jdbc:kylin://172.17.0.2:7070/learn_kylin", "driver": "org.apache.kylin.jdbc.Driver", "user": "ADMIN", "password": "KYLIN"}'

### Clickhouse

    [[[clickhouse]]]
      name=ClickHouse
      interface=jdbc
      ## Specific options for connecting to the ClickHouse server.
      ## The JDBC driver clickhouse-jdbc.jar and its related jars need to be in the CLASSPATH environment variable.
      options='{"url": "jdbc:clickhouse://localhost:8123", "driver": "ru.yandex.clickhouse.ClickHouseDriver", "user": "readonly", "password": ""}'

### SQL Alchemy
SQL Alchemy is a robust [connector](https://docs.sqlalchemy.org/en/latest/core/engines.html#sqlalchemy.create_engine) that supports
many [SQL dialects](https://docs.sqlalchemy.org/en/latest/dialects/mysql.html).

    [[[mysql]]]
       name = MySQL Alchemy
       interface=sqlalchemy
       options='{"url": "mysql://root:root@localhost:3306/hue"}'

### Django DB Connectors
Those rely on the `[dbms]` lib an dedicated Python libs.

Note, SQL Alchemy should be prefered.

Hue’s query editor can easily be configured to work with any database backend that [Django](https://docs.djangoproject.com/en/1.9/topics/install/#database-installation) supports, including PostgreSQL, MySQL, Oracle and SQLite. Some of you may note that these are the same backends supported by Hue’s DBQuery app and in fact, adding a new query editor for these databases starts with the same configuration step.

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

After updating the configuration and restarting Hue, we can access the new PostgreSQL interpreter in the Notebook app:

### JDBC
Use the query editor with any JDBC database.

Note, SQL Alchemy should be prefered.

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


### Spark

    [[[pyspark]]]
      name=PySpark
      interface=livy

    [[[sparksql]]]
      name=SparkSql
      interface=livy

    [[[spark]]]
      name=Scala
      interface=livy

    [[[r]]]
        name=R
        interface=livy

    ...

    [spark]
      # The Livy Server URL.
      livy_server_url=http://localhost:8998

### Pig

    [[[pig]]]
      name=Pig
      interface=oozie
