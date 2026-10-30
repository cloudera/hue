---
title: "Editor"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 3
---

## Editor

The goal of the Editor is to open up data to more users by making self-service querying easy and productive.
It has one of the best SQL autocompletes and many [more features](/administrator/configuration/connectors/#databases).

The Editor is available in the Editor and Notebook apps. You add dialects to the main `[notebook]` section like this:

```ini
[notebook]
  [[interpreters]]

    [[[hive]]]
      # The name of the snippet.
      name=Hive
      # The backend connection to use to communicate with the server.
      interface=hiveserver2

    [[[mysql]]]
      name=MySQL
      interface=sqlalchemy
      options='{"url": "mysql://root:root@localhost:3306/hue"}'
```

> **Tip**: Remember to uncomment the lines by removing the `#`, and to edit the sections at the correct levels.

The Editor supports some global settings.

### Downloads

You can limit the scalability cost of downloads and exports by restricting the number of rows or bytes transferred:

```ini
[beeswax]
  # A limit to the number of rows that can be downloaded from a query before it is truncated.
  # A value of -1 means there is no limit.
  download_row_limit=-1

  # A limit to the number of bytes that can be downloaded from a query before it is truncated.
  # A value of -1 means there is no limit.
  download_bytes_limit=-1
```

You can also disable the download and export feature in the Editor, the Dashboard, and the File Browser:

```ini
[desktop]
  # Global setting to allow or disable end user downloads in all Hue.
  # e.g. Query result in Editors and Dashboards, file in File Browser...
  enable_download=false
```

You can disable the download feature of the File Browser separately:

```ini
[filebrowser]
  show_download_button=false
```

### Notebook

Enable the Notebook mode, which supports multiple snippets of code:

```ini
[notebook]
  show_notebooks=true
```

### External statements

Enable the selection of queries from files or saved queries, into the Editor or as a snippet:

```ini
[notebook]
  enable_external_statements=false
```

### Batch querying

This option only works with Hive and relies on Oozie.

```ini
[notebook]
  enable_batch_execute=true
```

### Assist query builder

This flag enables a lightweight SQL query builder. You can drag and drop tables and columns from the left table assist into it. Do not confuse it with the dashboards described in the [Dashboard section](/user/querying/#dashboard).

> **Note**: This feature is deprecated.

```ini
[notebook]
  enable_query_builder=true
```

### Query analysis

Show an analysis panel with hints and suggestions after an Impala query runs.

> **Note**: This feature is experimental.

```ini
[notebook]
  enable_query_analysis=true
```

### Query optimization

In the `[metadata]` section, Hue supports Cloudera Navigator Optimizer, and other services might follow. It gives recommendations on how to write better queries and shows risk alerts on dangerous operations directly in the [Editor](/user/querying/).

### One-click scheduling

Enable the creation of a coordinator for the current SQL query. This feature requires the Oozie app.

> **Note**: This feature is experimental.

```ini
[notebook]
  enable_query_scheduling=true
```

### Credentials

When the connection URL does not contain a username or password, Hue prompts the user for them in the browser when connecting.

Hue does not save these parameters in its database, and it does not cache them in the Hue process. The client sends them each time it submits a query.

## Dashboard

Typing SQL is not always the most efficient way to explore a dataset. Dashboards offer visual exploration without typing code.

Hue supports these types:

* Interactive multi-widget querying of one source of data
* Multi-widget reporting (alpha)

### Solr search

In the `[search]` section of the configuration file, specify the URL of the Solr server:

```ini
[search]
  # URL of the Solr server
  solr_url=http://solr-server.com:8983/solr/
```

### SQL

The SQL Dashboard is configured in the `[dashboard]` section:

```ini
[dashboard]
  # Activate the Dashboard link in the menu.
  ## is_enabled=true

  # Activate the SQL Dashboard (beta).
  ## has_sql_enabled=false

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
```

## Connectors

Several interfaces are possible, and sometimes more than one works for a given database. When available, `HiveServer2` or `SqlAlchemy` are recommended because they are native.

### SQLAlchemy

SQLAlchemy is a robust [connector](https://docs.sqlalchemy.org/en/latest/core/engines.html#sqlalchemy.create_engine) that natively supports many [SQL dialects](https://docs.sqlalchemy.org/en/latest/dialects). It is the recommended connector for most databases.

Install the dialect in the Python system or in the Hue Python virtual environment. For example, for MySQL:

```bash
./build/env/bin/pip install mysqlclient
```

Then give Hue the information about the database:

```ini
[[[mysql]]]
  name=MySQL
  interface=sqlalchemy
  options='{"url": "mysql://root:root@localhost:3306/hue"}'
```

> **Tip**: To offer more self-service, you can parameterize parts of the URL. Hue then asks the user for the values. The supported parameters are `USER` and `PASSWORD`. For example:
>
> ```text
> mysql://${USER}:${PASSWORD}@localhost:3306/hue
> ```

### HiveServer2

This is the interface created for Apache Hive and Apache Impala. Its main advantages are asynchronous executions, which give you:

* Non-blocking submission
* Progress reports
* Non-blocking result fetching

For example, to point to Hive, first configure the `[beeswax]` section:

```ini
[beeswax]
  # Host where HiveServer2 is running.
  hive_server_host=localhost

  # Port where the HiveServer2 Thrift server runs.
  hive_server_port=10000
```

Then make sure the `hive` interpreter is in the `[[interpreters]]` list:

```ini
[notebook]
  [[interpreters]]
    [[[hive]]]
      name=Hive
      interface=hiveserver2
```

### Custom

Hue provides a series of native connectors (for example Livy and ksqlDB) that interact with the Editor. They are listed in the [developer section](/developer/development/#connectors).

### JDBC

> **Note**: This is a historical connector. Prefer SQLAlchemy, because it does not require a proxy and is fully secure.

Use the Editor with any JDBC database.

The `rdbms` interface works well for MySQL, PostgreSQL, SQLite, and Oracle. For other JDBC-compatible databases, Hue supports a `jdbc` interface.

To integrate an external JDBC database:

1. Download the compatible client driver JAR file for your OS and database. You can usually find the driver files on the database vendor's site.

   > **Note**: The MySQL JDBC driver is platform independent, but some drivers are specific to certain operating systems and versions. Check compatibility.

2. Add the path to the driver JAR file to your Java `CLASSPATH`. For example, set the `CLASSPATH` environment variable in your `.bash_profile`:

   ```bash
   # MySQL
   export MYSQL_HOME=/Users/hue/Dev/mysql
   export CLASSPATH=$MYSQL_HOME/mysql-connector-java-5.1.38-bin.jar:$CLASSPATH
   ```

3. Add a new interpreter to the Notebook app. Set `name`, set `interface` to `jdbc`, and set `options` to a JSON object with the JDBC connection information. For example, to connect to a local MySQL database named `hue` that runs on `localhost` and port `3306`:

   ```ini
   [notebook]
     [[interpreters]]
       [[[mysql]]]
         name=MySQL JDBC
         interface=jdbc
         options='{"url": "jdbc:mysql://localhost:3306/hue", "driver": "com.mysql.jdbc.Driver", "user": "root", "password": ""}'
   ```

Under the hood, Hue connects to the database through a Java proxy powered by Py4j. Hue starts the proxy automatically if any interpreter uses it. You can override this behavior:

```ini
[notebook]
  # Main flag to override the automatic starting of the DBProxy server.
  enable_dbproxy_server=true
```

> **Note**: Compile Hue with the `BUILD_DB_PROXY=true` flag to get the JDBC connector.

> **Tip**: Before you add the JDBC configuration to `hue.ini`, check that the JDBC driver and connection settings work in a SQL client such as SQuirreL SQL.

> **Tip**: You can leave the username and password out of the JDBC options. Hue then prompts the user for them. This lets administrators give access to JDBC sources without granting every Hue user the same access.
