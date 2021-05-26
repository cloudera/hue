---
title: "Editor"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 3
---

## Editor

The goal of the Editor is to open-up data to more users by making self service querying easy and productive.
It has one of the best SQL autocomplete and many [more features](/administrator/configuration/connectors/#databases).

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

The editor supports some global settings.

### Downloads

Download and export options with limited scalability by restricting the number of rows or bytes transferred using the following properties:

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

Flag to enable a lightweight SQL query builder where tables and columns can be dragged & dropped from the left table assist. Not to be confused with the [Query Builder](/user/querying/#dashboards).

**Note** This feature is deprecated.

      [notebook]
      enable_query_builder=true

### Query Analysis

Display an analysis panel post Impala queries executions with some hints and suggestions.

**Note** This feature is experimental.

      [notebook]
      enable_query_analysis=true

### Query Optimization

In the `[metadata]` section, Hue is supporting Cloudera Navigator Optimiser and soon other services. The goal is to provide recommendation on how to write better queries and get risk alerts on dangerous operations directly within the [editor](/user/querying/).

### One-click scheduling

Enable the creation of a coordinator for the current SQL query.

**Note** This feature is experimental until Task Server scheduler [HUE-8740](https://issues.cloudera.org/browse/HUE-8740).

      [notebook]
      enable_query_scheduling=true

### Credentials

When username or password are not specified in the connection URL, they will be prompted at connection time in the user browser.

Parameters are not saved at any time in the Hue database. The are currently not even cached in the Hue process. The clients serves these parameters
each time a query is sent.

## Dashboard

Manually typing SQL is not always the most efficient way to explore a dataset. Dashboards offer visual explorations without typing code.

They consist in 3 types:

* Interactive multi-widget querying of one source of data
* Query Builder (alpha)
* Multi-widget reporting (alpha)

### Solr Search

In the `[search]` section of the configuration file, you should
specify:

    [search]
      # URL of the Solr Server
      solr_url=http://solr-server.com:8983/solr/

### SQL

This application is getting improved via SQL Dashboards and Query Builder [HUE-3228](https://issues.cloudera.org/browse/HUE-3228).

      [dashboard]

      # Activate the Dashboard link in the menu.
      ## is_enabled=true

      # Activate the SQL Dashboard (beta).
      ## has_sql_enabled=false

      # Activate the Query Builder (beta).
      ## has_query_builder_enabled=false

      # Activate the static report layout (beta).
      ## has_report_enabled=false

      # Activate the new grid layout system.
      ## use_gridster=true

      # Activate the widget filter and comparison (beta).
      ## has_widget_filter=false

      # Activate the tree widget (to drill down fields as dimensions, alpha).
      ## has_tree_widget=false

      [[engines]]

      #  [[[solr]]]
      #  Requires Solr 6+
      ##  analytics=true
      ##  nesting=false

      #  [[[sql]]]
      ##  analytics=true
      ##  nesting=false

## Connectors

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

A series of native connectors (e.g. Livy, ksql...) interacting with the editor have been developed and are listed in the [developer section](/developer/development/#connectors).

### JDBC

**Note**: This is an historical connector, SQLAlchemy should be prefered at this time as it does not require a proxy and is fully secure.

Use the query editor with any JDBC database.

The “rdbms” interface works great for MySQL, PostgreSQL, SQLite, and Oracle, but for other JDBC-compatible databases Hue supports a “jdbc” interface to integrate such databases with the editor.

Integrating an external JDBC database involves a 3-step process:

Download the compatible client driver JAR file for your specific OS and database. Usually you can find the driver files from the official database vendor site; for example, the MySQL JDBC connector for Mac OSX can be found here: https://dev.mysql.com/downloads/connector/j/.

**Note**: In the case of MySQL, the JDBC driver is platform independent, but some drivers are specific to certain OSes and versions so be sure to verify compatibility.)
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

**Note**:
Hue needs to be compiled with the flag `BUILD_DB_PROXY=true` in order to come with the JDBC connector.

**Tip**: Testing JDBC Configurations
Before adding your interpreter's JDBC configurations to hue.ini, verify that the JDBC driver and connection settings work in a SQL client like SQuirrel SQL.

**Tip**: Prompt for JDBC authentication
You can leave out the username and password in the JDBC options, and Hue will instead prompt the user for a username and password. This allows administrators to provide access to JDBC sources without granting all Hue users the same access.
