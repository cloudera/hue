
<link rel="stylesheet" href="../css/bootplus.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>
<link rel="stylesheet" href="../css/font-awesome.min.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>
<link rel="stylesheet" href="../css/docbook.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>

<div class="row-fluid doc-title">
  <h1><a href=../index.html>Doc</a> > Hue Administration Guide</h1>
</div>


<div class="row-fluid">
  <div class="span3">

[TOC]

  </div>
  <div class="span9">

# Installation

The following instructions describe how to install the Hue tarball on a
multi-node cluster. You need to also install Hadoop and its satellite components
(Oozie, Hive...) and update some Hadoop configuration files before running Hue.


Hue consists of a web service that runs on a special node in your cluster.
Choose one node where you want to run Hue. This guide refers to that node as
the _Hue Server_. For optimal performance, this should be one of the nodes
within your cluster, though it can be a remote node as long as there are no
overly restrictive firewalls. For small clusters of less than 10 nodes,
you can use your existing master node as the Hue Server.

You can download the Hue tarball here:
[https://github.com/cloudera/hue/releases](https://github.com/cloudera/hue/releases)

## Dependencies

Hue employs some Python modules which use native code and requires
certain development libraries be installed on your system. To install from the
tarball, you'll need these library development packages and tools installed on your system:

* Python 2.7
* Python 3 (not available yet [HUE-8737](https://issues.cloudera.org/browse/HUE-8737))
* [MySQL InnoDB or PostgreSQL or Oracle](https://www.cloudera.com/documentation/enterprise/latest/topics/hue_dbs_0.html)
* Java (but only for the JDBC proxy, should be removed when [SQL Alchemy](https://issues.cloudera.org/browse/HUE-8740) is mature)

### Ubuntu

    sudo apt-get install git ant gcc g++ libffi-dev libkrb5-dev libmysqlclient-dev libsasl2-dev libsasl2-modules-gssapi-mit libsqlite3-dev libssl-dev libxml2-dev libxslt-dev make maven libldap2-dev python-dev python-setuptools libgmp3-dev nodejs npm

**Install Oracle JDK**

    sudo add-apt-repository ppa:webupd8team/java
    sudo apt-get update
    sudo apt-get install oracle-java8-installer

### CentOS/RHEL

    sudo yum install ant asciidoc cyrus-sasl-devel cyrus-sasl-gssapi cyrus-sasl-plain gcc gcc-c++ krb5-devel libffi-devel libxml2-devel libxslt-devel make  mysql mysql-devel openldap-devel python-devel sqlite-devel gmp-devel

* [Oracle JDK](https://www.digitalocean.com/community/tutorials/how-to-install-java-on-centos-and-fedora)
* mvn (from [``apache-maven``](https://gist.github.com/sebsto/19b99f1fa1f32cae5d00) package or maven3 tarball)
* libtidy (for unit tests only)
* openssl-devel (for version 7+)

#### Centos/Oracle/RedHat 6.x

Installing Python 2.7:

##### CentOS 6.8/6.9 OS

Check your OS Version:

    cat /etc/redhat-release

Make sure "/etc/redhat-release" contains "CentOS 6.8 or 6.9" version. These instructions are tested on CentOS 6.8 and 6.9 versions only. It may or may not work on previous CentOS 6 series OS.

    yum install -y centos-release-SCL
    yum install -y scl-utils
    yum install -y python27

##### RedHat 6.8/6.9 OS

Check your OS Version

    cat /etc/redhat-release

Make sure `/etc/redhat-release` contains "RedHat 6.8 or 6.9" version. These instructions are tested on RedHat 6.8 and 6.9 versions only. It may or may not work on previous RedHat 6 series OS.

    wget http://mirror.infra.cloudera.com/centos/6/extras/x86_64/Packages/centos-release-scl-rh-2-3.el6.centos.noarch.rpm
    rpm -ivh centos-release-scl-rh-2-3.el6.centos.noarch.rpm
    yum install -y scl-utils
    yum install -y python27

##### Oracle 6.8/6.9 OS

Check your OS Version

    cat /etc/redhat-release

Make sure `/etc/redhat-release` contains "Oracle 6.8 or 6.9" version. These instructions are tested on Oracle 6.8 and 6.9 versions only. It may or may not work on previous Oracle 6 series OS.

    wget -O /etc/yum.repos.d/public-yum-ol6.repo http://yum.oracle.com/public-yum-ol6.repo

Set the value of the enabled parameter for the software_collections repository to 1: for file `/etc/yum.repos.d/public-yum-ol6.repo`

    [ol6_software_collections]
    name=Software Collection Library release 3.0 packages for Oracle Linux 6 (x86_64)
    baseurl=http://yum.oracle.com/repo/OracleLinux/OL6/SoftwareCollections/x86_64/
    gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-oracle
    gpgcheck=1
    enabled=1

for more details, refer to this link: [https://docs.oracle.com/cd/E37670_01/E59096/html/section_e3v_nbl_cr.html](https://docs.oracle.com/cd/E37670_01/E59096/html/section_e3v_nbl_cr.html)

    yum install -y scl-utils
    yum install -y python27

### MacOS

* Xcode command line tools
* [Homebrew](https://brew.sh)
* [Oracle Instant Client](http://www.oracle.com/technetwork/database/database-technologies/instant-client/downloads/index.html)

1. Install Dependencies via Homebrew
    brew install mysql maven gmp openssl libffi && brew cask install java8

2. Install Xcode command line tools
    sudo xcode-select --install

3. Fix openssl errors
Required for MacOS 10.11+
    export LDFLAGS=-L/usr/local/opt/openssl/lib && export CPPFLAGS=-I/usr/local/opt/openssl/include


### Oracle Client lib

Download both instantclient-basic and instantclient-sdk of the same version (11.2.0.4.0 for this example) and on your ~/.bash_profile, add

    export ORACLE_HOME=/usr/local/share/oracle
    export VERSION=11.2.0.4.0
    export ARCH=x86_64
    export DYLD_LIBRARY_PATH=$ORACLE_HOME
    export LD_LIBRARY_PATH=$ORACLE_HOME

and then

    source ~/.bash_profile
    sudo mkdir -p $ORACLE_HOME
    sudo chmod 775 $ORACLE_HOME

then unzip the content of both downloaded zip files into the newly created $ORACLE_HOME in a way that the 'sdk' folder is at the same level with the other files and then

    ln -s libclntsh.dylib.11.1 libclntsh.dylib
    ln -s libocci.dylib.11.1 libocci.dylib

and finally

    cd sdk
    unzip ottclasses.zip


## Install

Configure `$PREFIX` with the path where you want to install Hue by running:

    PREFIX=/usr/share make install
    cd /usr/share/hue

You can install Hue anywhere on your system, and run Hue as a non-root user.

It is a good practice to create a new user for Hue and either install Hue in
that user's home directory, or in a directory within `/usr/share`.

## Docker

Alternatively to building Hue into an image, the [Hue Docker Guide](https://github.com/cloudera/hue/tree/testing/tools/docker) is available.

## Starting the server

After your cluster is running with the plugins enabled, you can start Hue on
your Hue Server by running:

    build/env/bin/supervisor

This will start several subprocesses, corresponding to the different Hue
components. Your Hue installation is now running.


# Connectors

The source of truth sits in the main [hue.ini](https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini).
It consists in several [ini sections](https://en.wikipedia.org/wiki/INI_file#Sections). Lines needs to be uncommented to be active.

Hue is using Hadoop `impersonation` to be able to communicate properly with certain services. This is described in the following [Service Configuration]("#services-pre-configurations).

## Editor

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

The Presto JDBC client driver is maintained by the Presto Team and can be downloaded here: https://prestosql.io/docs/current/installation/jdbc.html

    [[[presto]]]
    name=Presto JDBC
    interface=jdbc
    options='{"url": "jdbc:presto://localhost:8080/", "driver": "io.prestosql.jdbc.PrestoDriver"}'

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

## Files and Object Store

### HDFS

Hue supports one HDFS cluster. That cluster should be defined
under the `[[[default]]]` sub-section.

    fs_defaultfs::
      This is the equivalence of `fs.defaultFS` (aka `fs.default.name`) in
      Hadoop configuration.

    webhdfs_url::
      You can also set this to be the HttpFS url. The default value is the HTTP
      port on the NameNode.

    hadoop_conf_dir::
      This is the configuration directory of the HDFS, typically
      `/etc/hadoop/conf`.

### S3

Hue's filebrowser can now allow users to explore, manage, and upload data in an S3 account, in addition to HDFS.

Read more about it in the [S3 User Documentation](../user-guide/user-guide.html#s3).

In order to add an S3 account to Hue, you'll need to configure Hue with valid S3 credentials, including the access key ID and secret access key: [AWSCredentials](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html)

These keys can securely stored in a script that outputs the actual access key and secret key to stdout to be read by Hue (this is similar to how Hue reads password scripts). In order to use script files, add the following section to your hue.ini configuration file:


    [aws]
    [[aws_accounts]]
    [[[default]]]
    access_key_id_script=/path/to/access_key_script
    secret_access_key_script= /path/to/secret_key_script
    allow_environment_credentials=false
    region=us-east-1


Alternatively (but not recommended for production or secure environments), you can set the access_key_id and secret_access_key values to the plain-text values of your keys:

    [aws]
    [[aws_accounts]]
    [[[default]]]
    access_key_id=s3accesskeyid
    secret_access_key=s3secretaccesskey
    allow_environment_credentials=false
    region=us-east-1

The region should be set to the AWS region corresponding to the S3 account. By default, this region will be set to 'us-east-1'.


**Using Ceph**
New end points have been added in [HUE-5420](https://issues.cloudera.org/browse/HUE-5420)


### ADLS

Hue's file browser can now allow users to explore, manage, and upload data in an ADLS, in addition to HDFS and S3.

Read more about it in the [ADLS User Documentation](../user-guide/user-guide.html#adls).

In order to add an ADLS account to Hue, you'll need to configure Hue with valid ADLS credentials, including the client ID, client secret and tenant ID.
These keys can securely stored in a script that outputs the actual access key and secret key to stdout to be read by Hue (this is similar to how Hue reads password scripts). In order to use script files, add the following section to your hue.ini configuration file:

    [adls]
    [[azure_accounts]]
    [[[default]]]
    client_id_script=/path/to/client_id_script.sh
    client_secret_script=/path/to/client_secret_script.sh
    tenant_id_script=/path/to/tenant_id_script.sh

    [[adls_clusters]]
    [[[default]]]
    fs_defaultfs=adl://<account_name>.azuredatalakestore.net
    webhdfs_url=https://<account_name>.azuredatalakestore.net

Alternatively (but not recommended for production or secure environments), you can set the client_secret value in plain-text:

    [adls]
    [[azure_account]]
    [[[default]]]
    client_id=adlsclientid
    client_secret=adlsclientsecret
    tenant_id=adlstenantid

    [[adls_clusters]]
    [[[default]]]
    fs_defaultfs=adl://<account_name>.azuredatalakestore.net
    webhdfs_url=https://<account_name>.azuredatalakestore.net


## YARN Cluster

Hue supports one or two Yarn clusters (two for HA). These clusters should be defined
under the `[[[default]]]` and `[[[ha]]]` sub-sections.

    resourcemanager_host:
      The host running the ResourceManager.

    resourcemanager_port:
      The port for the ResourceManager REST service.

    logical_name:
      NameNode logical name.

    submit_to:
      To enable the section, set to True.

## Oozie

In the `[liboozie]` section of the configuration file, you should
specify:

    oozie_url:
      The URL of the Oozie service. It is the same as the `OOZIE_URL`
      environment variable for Oozie.


## Solr

In the `[search]` section of the configuration file, you should
specify:

    solr_url:
      The URL of the Solr service.


## HBase

In the `[hbase]` section of the configuration file, you should
specify:

    hbase_clusters:
      Comma-separated list of HBase Thrift servers for clusters in the format of "(name|host:port)".

# Services pre-configuration

## Hive SQL

Hue's Hive SQL Editor application helps you use Hive to query your data.
It depends on a Hive Server 2 running in the cluster. Please read
this section to ensure a proper integration.

Your Hive data is stored in HDFS, normally under `/user/hive/warehouse`
(or any path you specify as `hive.metastore.warehouse.dir` in your
`hive-site.xml`).  Make sure this location exists and is writable by
the users whom you expect to be creating tables.  `/tmp` (on the local file
system) must be world-writable (1777), as Hive makes extensive use of it.

<div class="note">
  In `hue.ini`, modify `hive_conf_dir` to point to the
  directory containing `hive-site.xml`.
</div>

## Hive and Impala High Availability (HA)

HiveServer2 and Impala support High Availability through a “load balancer”.
One caveat is that Hue's underlying Thrift libraries reuse TCP connections in a
pool, a single user session may not have the same Impala or Hive TCP connection.
If a TCP connection is balanced away from the previously selected  HiveServer2
or Impalad instance, the user session and its queries can be lost and trigger
the “Results have expired” or “Invalid session Id” errors.

To prevent sessions from being lost, you need configure the load balancer with
“source” algorithm to ensure each Hue instance sends all traffic to a single
HiveServer2/Impalad instance. Yes, this is not true load balancing, but a
configuration for failover High Availability. HiveSever2 or Impala coordinators
already distribute the work across the cluster so this is not an issue.

To enable an optimal load distribution that works for everybody, you can create
multiple profiles in our load balancer, per port for Hue clients and non-Hue
clients like Hive or Impala. You can configure non-Hue clients to distribute loads
with “roundrobin” or “leastconn” and configure Hue clients with “source”
(source IP Persistence) on dedicated ports, for example, 10015 for Hive beeline
commands, 10016 for Hue, 21051 for Hue-Impala interactions while 25003 for Impala shell.

You can configure the HaProxy to have two different ports associated with
different load balancing algorithms. Here is a sample configuration (haproxy.cfg)
for Hive and Impala HA on a secure cluster.

    frontend hiveserver2_front
    bind *:10015 ssl crt /path/to/cert_key.pem
    mode tcp
    option tcplog
    default_backend hiveserver2
    backend hiveserver2
        balance                     roundrobin
        mode                        tcp
        server hs2_1 host-2.com:10000 ssl ca-file /path/to/truststore.pem check
        server hs2_2 host-3.com:10000 ssl ca-file /path/to/truststore.pem check
        server hs2_3 host-1.com:10000 ssl ca-file /path/to/truststore.pem check

    frontend  hivejdbc_front
        bind                        *:10016 ssl crt /path/to/cert_key.pem
        mode                        tcp
        option                      tcplog
        stick                       match src
        stick-table type ip size 200k expire 30m
        default_backend             hivejdbc
    backend hivejdbc
        balance                     source
        mode                        tcp
        server hs2_1 host-2.com:10000 ssl ca-file /path/to/truststore.pem check
        server hs2_2 host-3.com:10000 ssl ca-file /path/to/truststore.pem check
        server hs2_3 host-1.com:10000 ssl ca-file /path/to/truststore.pem check

And here is an example for impala HA configuration on a secure cluster.

    frontend  impala_front
        bind                        *:25003 ssl crt /path/to/cert_key.pem
        mode                        tcp
        option                      tcplog
        default_backend             impala
    backend impala
        balance                     leastconn
        mode                        tcp
        server impalad1 host-3.com:21000 ssl ca-file /path/to/truststore.pem check
        server impalad2 host-2.com:21000 ssl ca-file /path/to/truststore.pem check
        server impalad3 host-4.com:21000 ssl ca-file /path/to/truststore.pem check

    frontend  impalajdbc_front
        bind                        *:21051 ssl crt /path/to/cert_key.pem
        mode                        tcp
        option                      tcplog
        stick                       match src
        stick-table type ip size 200k expire 30m
        default_backend             impalajdbc
    backend impalajdbc
        balance                     source
        mode                        tcp
        server impalad1 host-3.com:21050 ssl ca-file /path/to/truststore.pem check
        server impalad2 host-2.com:21050 ssl ca-file /path/to/truststore.pem check
        server impalad3 host-4.com:21050 ssl ca-file /path/to/truststore.pem check

Note: “check” is required at end of each line to ensure HaProxy can detect any
unreachable Impalad/HiveServer2 server, so HA failover can be successful. Without
 TCP check, you may hit the “TSocket reads 0 byte” error when the
Impalad/HiveServer2 server Hue tries to connect is down.

After editing the /etc/haproxy/haproxy.cfg file, run following commands to
restart HaProxy service and check the service restarts successfully.

    service haproxy restart
    service haproxy status

Also we need add following blocks into hue.ini.

    [impala]
    server_port=21051

    [beeswax]
    hive_server_port=10016

Read more about it in the [How to optimally configure your Analytic Database for
High Availability with Hue and other SQL clients](http://gethue.com/how-to-opti
mally-configure-your-analytic-database-for-high-availability-with-hue-and-other-sql-clients) post.

## Hadoop HDFS

You need to enable WebHdfs or run an HttpFS server. To turn on WebHDFS,
add this to your `hdfs-site.xml` and *restart* your HDFS cluster.
Depending on your setup, your `hdfs-site.xml` might be in `/etc/hadoop/conf`.

    <property>
      <name>dfs.webhdfs.enabled</name>
      <value>true</value>
    </property>

You also need to add this to `core-site.xml`.

    <property>
      <name>hadoop.proxyuser.hue.hosts</name>
      <value>*</value>
    </property>
    <property>
      <name>hadoop.proxyuser.hue.groups</name>
      <value>*</value>
    </property>

If you place your Hue Server outside the Hadoop cluster, you can run
an HttpFS server to provide Hue access to HDFS. The HttpFS service requires
only one port to be opened to the cluster.

Also add this in `httpfs-site.xml` which might be in `/etc/hadoop-httpfs/conf`.

    <property>
      <name>httpfs.proxyuser.hue.hosts</name>
      <value>*</value>
    </property>
    <property>
      <name>httpfs.proxyuser.hue.groups</name>
      <value>*</value>
    </property>


## Oozie

Hue submits MapReduce jobs to Oozie as the logged in user. You need to
configure Oozie to accept the `hue` user to be a proxyuser. Specify this in
your `oozie-site.xml` (even in a non-secure cluster), and restart Oozie:

    <property>
        <name>oozie.service.ProxyUserService.proxyuser.hue.hosts</name>
        <value>*</value>
    </property>
    <property>
        <name>oozie.service.ProxyUserService.proxyuser.hue.groups</name>
        <value>*</value>
    </property>

## Firewall

Hue currently requires that the machines within your cluster can connect to
each other freely over TCP. The machines outside your cluster must be able to
open TCP port 8888 on the Hue Server (or the configured Hue web HTTP port)
to interact with the system.

# Configuration

## Reference Architecture

A recommended setup consists in:

* 2 Hues and 1 Load Balancer
* Databases: MySQL InnoDB, PostgreSQL, Oracle
* Authentication: [LDAP or Username/Passord](#user-management)

### Monitoring

Performing a `GET /desktop/debug/is_alive` will return a 200 response if running.


### Load Balancers

Hue is often run with:

* Cherrypy with Httpd
* [Apache mod Python](http://gethue.com/how-to-run-hue-with-the-apache-server/)
* [NGINX](http://gethue.com/using-nginx-to-speed-up-hue-3-8-0/)

### Task Server

The task server is currently a work in progress to outsource all the blocking or resource intensive operations
outside of the API server. Follow (HUE-8738)[https://issues.cloudera.org/browse/HUE-8738) for more information
on when first usable task will be released.

Until then, here is how to try the task server service.

Make sure you have Rabbit MQ installed and running.

    sudo apt-get install rabbitmq-server -y


In hue.ini, telling the API server that the Task Server is available:

    [desktop]
    [[task_server]]
    enabled=true

Starting the Task server:

    ./build/env/bin/hue runcelery worker --concurrency=1

Starting the Task server in a Cloudera Manager environment:

    ./build/env/bin/hue runcelery worker --concurrency=1 --cm-managed

Running a test tasks:

    ./build/env/bin/hue shell

    from desktop.celery import debug_task

    debug_task.delay()
    debug_task.delay().get() # Works if result backend is setup and task_server is true in the hue.ini

Starting the Task Scheduler server:

    ./build/env/bin/celery -A core beat -l info

or when Django Celery Beat is enabled:

    ./build/env/bin/celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

### Proxy

A Web proxy lets you centralize all the access to a certain URL and prettify the address (e.g. ec2-54-247-321-151.compute-1.amazonaws.com --> demo.gethue.com).

Here is one way to do it with [Apache](http://gethue.com/i-put-a-proxy-on-hue/).

## Quick Start Wizard

The Quick Start wizard allows you to perform the following Hue setup
operations by clicking the tab of each step or sequentially by clicking
Next in each screen:

1.  **Check Configuration** validates your Hue configuration. It will
    note any potential misconfiguration and provide hints as to how to
    fix them. You can edit the configuration file described in the next
    section or use Cloudera Manager, if installed, to manage your
    changes.
2.  **Examples** contains links to install examples into the Hive,
    Impala, MapReduce, Spark, Oozie, Solr Dashboard and Pig Editor applications.
3.  **Users** contains a link to the User Admin application to create or
    import users and a checkbox to enable and disable collection of
    usage information.

## Configuration

Displays a list of the installed Hue applications and their
configuration. The location of the folder containing the Hue
configuration files is shown at the top of the page. Hue configuration
settings are in the hue.ini configuration file.

Click the tabs under **Configuration Sections and Variables** to see the
settings configured for each application. For information on configuring
these settings, see Hue Configuration in the Hue installation manual.


Hue ships with a default configuration that will work for
pseudo-distributed clusters.  If you are running on a real cluster, you must
make a few changes to the `hue.ini` configuration file (`/etc/hue/hue.ini` when installed from the
package version) or `pseudo-distributed.ini` in `desktop/conf` when in development mode).
The following sections describe the key configuration options you must make to configure Hue.


<div class="note">
To list all available configuration options, run:

    $ /usr/share/hue/build/env/bin/hue config_help | less

This commands outlines the various sections and options in the configuration,
and provides help and information on the default values.
</div>


<div class="note">
To view the current configuration from within Hue, open:

    http://<hue>/hue/dump_config
</div>

<div class="note">
Hue loads and merges all of the files with extension `.ini`
located in the `/etc/hue` directory.  Files that are alphabetically later
take precedence.
</div>


### Web Server Configuration

These configuration variables are under the `[desktop]` section in
the `hue.ini` configuration file.

### Specifying the HTTP port

Hue uses CherryPy web server.  You can use the following options to
change the IP address and port that the web server listens on.
The default setting is port 8888 on all configured IP addresses.

    # Webserver listens on this address and port
    http_host=0.0.0.0
    http_port=8888

[Gunicorn](https://gunicorn.org/) support is planned to come in via [HUE-8739](https://issues.cloudera.org/browse/HUE-8739).

### Specifying the Secret Key

For security, you should also specify the secret key that is used for secure
hashing in the session store. Enter a long series of random characters
(30 to 60 characters is recommended).

    secret_key=jFE93j;2[290-eiw.KEiwN2s3['d;/.q[eIW^y#e=+Iei*@Mn<qW5o

NOTE: If you don't specify a secret key, your session cookies will not be
secure. Hue will run but it will also display error messages telling you to
set the secret key.

### Disabling some apps

In the Hue ini configuration file, in the [desktop] section, you can enter the names of the app to hide:

<pre>
[desktop]
# Comma separated list of apps to not load at server startup.
app_blacklist=beeswax,impala,security,filebrowser,jobbrowser,rdbms,jobsub,pig,hbase,sqoop,zookeeper,metastore,spark,oozie,indexer
</pre>

[Read more about it here](http://gethue.com/mini-how-to-disabling-some-apps-from-showing-up/).

### Authentication

By default, the first user who logs in to Hue can choose any
username and password and becomes an administrator automatically.  This
user can create other user and administrator accounts. User information is
stored in the Django database in the Django backend.

The authentication system is pluggable. For more information, see the [SDK Documentation](../sdk/sdk.html).

List of some of the possible authentications:
#### Username / Password
#### LDAP
#### SAML

[Read more about it](http://gethue.com/updated-saml-2-0-support/).

#### OpenId Connect
#### Multiple Authentication Backends

For example, to enable Hue to first attempt LDAP directory lookup before falling back to the database-backed user model, we can update the hue.ini configuration file or Hue safety valve in Cloudera Manager with a list containing first the LdapBackend followed by either the ModelBackend or custom AllowFirstUserDjangoBackend (permits first login and relies on user model for all subsequent authentication):

<pre>
[desktop]
  [[auth]]
  backend=desktop.auth.backend.LdapBackend,desktop.auth.backend.AllowFirstUserDjangoBackend
</pre>

This tells Hue to first check against the configured LDAP directory service, and if the username is not found in the directory, then attempt to authenticate the user with the Django user manager.

[Read more about it here](http://gethue.com/configuring-hue-multiple-authentication-backends-and-ldap/).

### Reset a password

**Programmatically**

When a Hue administrator loses their password, a more programmatic approach is required to secure the administrator again. Hue comes with a wrapper around the python interpreter called the “shell” command. It loads all the libraries required to work with Hue at a programmatic level. To start the Hue shell, type the following command from the Hue installation root.

Then:

    cd /usr/lib/hue (or /opt/cloudera/parcels/CDH-XXXXX/share/hue if using parcels and CM)
    build/env/bin/hue shell

The following is a small script, that can be executed within the Hue shell, to change the password for a user named “example”:

    from django.contrib.auth.models import User
    user = User.objects.get(username='example')
    user.set_password('some password')
    user.save()

The script can also be invoked in the shell by using input redirection (assuming the script is in a file named script.py):

    build/env/bin/hue shell < script.py

How to make a certain user a Hue admin

    build/env/bin/hue  shell

Then set these properties to true:

    from django.contrib.auth.models import User

    a = User.objects.get(username='hdfs')
    a.is_staff = True
    a.is_superuser = True
    a.set_password('my_secret')
    a.save()

** Via a command**

Go on the Hue machine, then in the Hue home directory and either type:

To change the password of the currently logged in Unix user:

    build/env/bin/hue changepassword

If you don't remember the admin username, create a new Hue admin (you will then also be able to login and could change the password of another user in Hue):

    build/env/bin/hue createsuperuser


[Read more about it here](http://gethue.com/password-management-in-hue/).

<div class="note">
Above works with the `AllowFirstUserBackend`, it might be different if another backend is used.
</div>

### Change your maps look and feel

The properties we need to tweak are leaflet_tile_layer and leaflet_tile_layer_attribution, that can be configured in the hue.ini file:

<pre>
[desktop]
leaflet_tile_layer=https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}
leaflet_tile_layer_attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
</pre>

[Read more about it here](http://gethue.com/change-your-maps-look-and-feel/).

### Configure a Proxy

We explained how to run Hue with NGINX serving the static files or under Apache. If you use another proxy, you might need to set these options:

<pre>
  [desktop]
  # Enable X-Forwarded-Host header if the load balancer requires it.
  use_x_forwarded_host=false

  # Support for HTTPS termination at the load-balancer level with SECURE_PROXY_SSL_HEADER.
  secure_proxy_ssl_header=false
</pre>

### Configuring SSL

You can configure Hue to serve over HTTPS.

1. Configure Hue to use your private key by adding the following
options to the `hue.ini` configuration file:

    ssl_certificate=/path/to/certificate
    ssl_private_key=/path/to/key

2. Ideally, you would have an appropriate key signed by a Certificate Authority.
If you're just testing, you can create a self-signed key using the `openssl`
command that may be installed on your system:

Create a key:

    openssl genrsa 1024 > host.key

Create a self-signed certificate:

    openssl req -new -x509 -nodes -sha1 -key host.key > host.cert


<div class="note">
Self-signed Certificates and File Uploads

To upload files using the Hue File Browser over HTTPS requires
using a proper SSL Certificate.  Self-signed certificates don't
work.
</div>

Note: The security vulnerability SWEET32 is also called Birthday attacks against TLS ciphers with 64bit block size and it is assigned CVE-2016-2183. This is due to legacy block ciphers
having block size of 64 bits are vulnerable to a practical collision attack when used in CBC mode.

DES/3DES are the only ciphers has block size of 64-bit. One way to config Hue not to use them:
<pre>
  [desktop]
  ssl_cipher_list=DEFAULT:!DES:!3DES
</pre>

### SASL

When getting a bigger result set from Hive/Impala or bigger files like images from HBase, the response requires to increase
the buffer size of SASL lib for thrift sasl communication.

<pre>
  [desktop]
  # This property specifies the maximum size of the receive buffer in bytes in thrift sasl communication,
  # default value is 2097152 (2 MB), which equals to (2 * 1024 * 1024)
  sasl_max_buffer=2097152
</pre>

### User Admin Configuration
In the `[useradmin]` section of the configuration file, you can
_optionally_ specify the following:

default_user_group::
  The name of a default group that is suggested when creating a
  user manually. If the LdapBackend or PamBackend are configured
  for doing user authentication, new users will automatically be
  members of the default group.


### Banner
You can add a custom banner to the Hue Web UI by applying HTML directly to the property, banner_top_html. For example:

    banner_top_html=<H4>My company's custom Hue Web UI banner</H4>

### Splash Screen
You can customize a splash screen on the login page by applying HTML directly to the property, login_splash_html. For example:

    [desktop]
    [[custom]]
    login_splash_html=WARNING: You are required to have authorization before you proceed.


### Custom Logo

There is also the possibility to change the logo for further personalization.

    [desktop]
    [[custom]]
    # SVG code to replace the default Hue logo in the top bar and sign in screen
    # e.g. <image xlink:href="/static/desktop/art/hue-logo-mini-white.png" x="0" y="0" height="40" width="160" />
    logo_svg=

You can go crazy and write there any SVG code you want. Please keep in mind your SVG should be designed to fit in a 160×40 pixels space. To have the same ‘hearts logo' you can see above, you can type this code

    [desktop]
    [[custom]]
    logo_svg='<g><path stroke="null" id="svg_1" d="m44.41215,11.43463c-4.05017,-10.71473 -17.19753,-5.90773 -18.41353,-0.5567c-1.672,-5.70253 -14.497,-9.95663 -18.411,0.5643c-4.35797,11.71793 16.891,22.23443 18.41163,23.95773c1.5181,-1.36927 22.7696,-12.43803 18.4129,-23.96533z" fill="#ffffff"/> <path stroke="null" id="svg_2" d="m98.41246,10.43463c-4.05016,-10.71473 -17.19753,-5.90773 -18.41353,-0.5567c-1.672,-5.70253 -14.497,-9.95663 -18.411,0.5643c-4.35796,11.71793 16.891,22.23443 18.41164,23.95773c1.5181,-1.36927 22.76959,-12.43803 18.41289,-23.96533z" fill="#FF5A79"/> <path stroke="null" id="svg_3" d="m154.41215,11.43463c-4.05016,-10.71473 -17.19753,-5.90773 -18.41353,-0.5567c-1.672,-5.70253 -14.497,-9.95663 -18.411,0.5643c-4.35796,11.71793 16.891,22.23443 18.41164,23.95773c1.5181,-1.36927 22.76959,-12.43803 18.41289,-23.96533z" fill="#ffffff"/> </g>'

Read more about it in [Hue with a custom logo](http://gethue.com/hue-with-a-custom-logo/) post.


### Storing passwords in file script

This [article details how to store passwords in a script](http://gethue.com/storing-passwords-in-script-rather-than-hue-ini-files/) launched from the OS rather than have clear text passwords in the hue*.ini files.

Some passwords go in Hue ini configuration file making them easily visible to Hue admin user or by users of cluster management software. You can use the password_script feature to prevent passwords from being visible.

### Idle session timeout

Hue now offers a new property, idle_session_timeout, that can be configured in the hue.ini file:

<pre>
[desktop]
[[auth]]
idle_session_timeout=600
</pre>

When idle_session_timeout is set, users will automatically be logged out after N (e.g. – 600) seconds of inactivity and be prompted to login again:

[Read more about it here](http://gethue.com/introducing-the-new-login-modal-and-idle-session-timeout/).

### Auditing

Read more about [Auditing User Administration Operations with Hue and Cloudera Navigator](http://gethue.com/auditing-user-administration-operations-with-hue-and-cloudera-navigator-2/).


# Administration

Now that you've installed and started Hue, you can feel free to skip ahead
to the <<usage,Using Hue>> section. Administrators may want to refer to this
section for more details about managing and operating a Hue installation.


## Configuration Validation

Hue can detect certain invalid configuration.

To view the configuration of a running Hue instance, navigate to
`http://myserver:8888/hue/dump_config`, also accessible through the About
application.


## Server Logs

Displays the Hue Server log and allows you to download the log to your
local system in a zip file.

## Threads

Read more on the [Threads and Metrics pages
 blog post](http://gethue.com/easier-administration-of-hue-with-the-new-threads-and-metrics-pages/)

Threads page can be very helpful in debugging purposes. It includes a daemonic thread and the thread objects serving concurrent requests. The host name, thread name identifier and current stack frame of each are displayed. Those are useful when Hue “hangs”, sometimes in case of a request too CPU intensive. There is also a REST API to get the dump of Threads using 'desktop/debug/threads'

## Metrics

Read more on the [Threads and Metrics pages
 blog post](http://gethue.com/easier-administration-of-hue-with-the-new-threads-and-metrics-pages/)

Hue uses the **PyFormance** Python library to collect the metrics. These metrics are represented as gauge, counters, meter, rate of events over time, histogram, statistical distribution of values. A REST API endpoint '/desktop/metrics/' to get all the metrics dump as json is also exposed

The below metrics of most concern to us are displayed on the page:

- requests.active
- requests.exceptions
- requests.response-time
- threads.daemon
- threads.total
- users
- users.active

One of the most useful ones are the percentiles of response time of requests and the count of active users.
Admins can either filter a particular property in all the metrics or select a particular metric for all properties


## User management

The User Admin application lets a superuser add, delete, and manage Hue
users and groups, and configure group permissions. Superusers can add
users and groups individually, or import them from an LDAP directory.
Group permissions define the Hue applications visible to group members
when they log into Hue and the application features available to them.

Click the **User Admin** icon in the top right navigation bar under your username.

### LDAP

[LDAP or PAM pass-through authentication with Hive or Impala and Impersonation
](http://gethue.com/ldap-or-pam-pass-through-authentication-with-hive-or-impala/).


### Users

The User Admin application provides two levels of user privileges:
superusers and users.

-   Superusers — The first user who logs into Hue after its initial
    installation becomes the first superuser. Superusers have
    permissions to perform administrative functions:
    -   Add and delete users
    -   Add and delete groups
    -   Assign permissions to groups
    -   Change a user into a superuser
    -   Import users and groups from an LDAP server

-   Users can change their name, e-mail address, and password and log
    in to Hue and run Hue applications, subject to the permissions
    provided by the Hue groups to which they belong.

#### Adding a User

1.  In the **User Admin** page, click **Add User**.
2.  In the **Credentials** screen, add required information about the
    user. Once you provide the required information you can click the
    wizard step tabs to set other information.

 <table>
<tr><td>Username</td><td>  A user name that contains only letters, numbers, and underscores;
    blank spaces are not allowed and the name cannot begin with a
    number. The user name is used to log into Hue and in file
    permissions and job submissions. This is a required field.
</td></tr>
<tr><td>Password and Password confirmation</td><td>    A password for the user. This is a required field.</td></tr>
<tr><td>Create home directory</td><td>   Indicate whether to create a directory named /user/username in HDFS.
    For non-superusers, the user and group of the directory are
    username. For superusers, the user and group are username and
    supergroup.</td></tr></table>



3.  Click **Add User** to save the information you specified and close
    the **Add User** wizard or click **Next**.
4.  In the **Names and Groups** screen, add optional information.

<table>
<tr><td>First name and Last name</td><td> The user's first and last name.
</td></tr>
<tr><td>E-mail address</td><td>The user's e-mail address. The e-mail address is used by the Job
    Designer and Beeswax applications to send users an e-mail message
    after certain actions have occurred. The Job Designer sends an
    e-mail message after a job has completed. Beeswax sends a message
    after a query has completed. If an e-mail address is not specified,
    the application will not attempt to email the user.</td></tr>
<tr><td>Groups</td><td> The groups to which the user belongs. By default, a user is assigned
    to the **default** group, which allows access to all applications.
    See [Permissions](#permissions).</td></tr></table>


5.  Click **Add User** to save the information you specified and close
    the **Add User** wizard or click **Next**.
6.  In the **Advanced** screen, add status information.

<table>
<tr><td>Active</td><td> Indicate that the user is enabled and allowed to log in. Default: checked.</td></tr>
<tr><td>Superuser status</td><td> Assign superuser privileges to the user.</td></tr></table>

7.  Click **Add User** to save the information you specified and close
    the **Add User** wizard.

#### Deleting a User

1.  Check the checkbox next to the user name and click **Delete**.
2.  Click **Yes** to confirm.

#### Editing a User

1.  Click the user you want to edit in the **Hue Users** list.
2.  Make the changes to the user and then click **Update user**.

#### Importing Users from an LDAP Directory

**Note**:

Importing users from an LDAP directory does not import any password
information. You must add passwords manually in order for a user to log
in.

To add a user from an external LDAP directory:

1.  Click **Add/sync LDAP user**.
2.  Specify the user properties:

<table>
<tr><td>Username</td><td>The user name.</td></tr>
<tr><td>Distinguished name</td><td>Indicate that Hue should use a full distinguished name for the user.
    This imports the user's first and last name, username, and email,
    but does not store the user password.</td></tr>
    <tr><td>Create home directory</td><td> Indicate that Hue should create a home directory for the user in
    HDFS.</td></tr></table>


3.  Click **Add/sync user**.

    If the user already exists in the User Admin, the user information
    in User Admin is synced with what is currently in the LDAP
    directory.

#### Syncing Users and Groups with an LDAP Directory

You can sync the Hue user database with the current state of the LDAP
directory using the **Sync LDAP users/groups** function. This updates
the user and group information for the already imported users and
groups. It does not import any new users or groups.

1.  Click **Sync LDAP users/groups**.
2.  The **Create Home Directories** checkbox creates home directories in
    HDFS for existing imported members that don't have home directories.
3.  In the **Sync LDAP users and groups** dialog, click **Sync** to
    perform the sync.

### Groups

Superusers can add and delete groups, configure group permissions, and
assign users to group memberships.

#### Adding a Group

You can add groups, and delete the groups you've added. You can also
import groups from an LDAP directory.

1.  In the **User Admin** window, click **Groups** and then click **Add
    Group**.
2.  Specify the group properties:

<table>
<tr><td>Name</td><td> The name of the group. Group names can only be letters, numbers, and
    underscores; blank spaces are not allowed.</td></tr>
<tr><td>Members</td><td>The users in the group. Check user names or check Select all.</td></tr>
    <tr><td>Permissions</td><td>The applications the users in the group can access. Check
    application names or check Select all.</td></tr></table>

3.  Click **Add group**.

#### Adding Users to a Group

1.  In the **User Admin** window, click **Groups**.
2.  Click the group.
3.  To add users to the group, check the names in the list provided or
    check **Select All**.
4.  Click **Update group**.

#### Deleting a Group

1.  Click **Groups**.
2.  Check the checkbox next to the group and click **Delete**.
3.  Click **Yes** to confirm.

#### Limit users can login only if they are belong to one of listed LDAP groups

    [desktop]
    [[ldap]]
    login_groups=ldap_grp1,ldap_grp2,ldap_grp3

#### Importing Groups from an LDAP Directory

1.  From the **Groups** tab, click **Add/sync LDAP group**.
2.  Specify the group properties:

<table>
<tr><td>Name</td><td> The name of the group.</td></tr>
<tr><td>Distinguished name</td><td> Indicate that Hue should use a full distinguished name for the
    group.</td></tr>
    <tr><td>Import new members</td><td>  Indicate that Hue should import the members of the group.</td></tr>
        <tr><td>Import new members from all subgroups</td><td>
    Indicate that Hue should import the members of the subgroups.</td></tr>
            <tr><td>Create home directories</td><td> Indicate that Hue should create home directories in HDFS for the
    imported members.</td></tr>
</table>

3.  Click **Add/sync group**.

<a id="permissions"></a>
Permissions
-----------

Permissions for Hue applications are granted to groups, with users
gaining permissions based on their group membership. Group permissions
define the Hue applications visible to group members when they log into
Hue and the application features available to them.

1.  Click **Permissions**.
2.  Click the application for which you want to assign permissions.
3.  Check the checkboxes next to the groups you want to have permission
    for the application. Check **Select all** to select all groups.
4.  Click **Update permission**. The new groups will appear in the
    Groups column in the **Hue Permissions** list.

[Read more about it here](http://gethue.com/how-to-manage-permissions-in-hue/).

## Process Hierarchy

A script called `supervisor` manages all Hue processes. The supervisor is a
watchdog process -- its only purpose is to spawn and monitor other processes.
A standard Hue installation starts and monitors the following processes:

* `runcpserver` - a web server based on CherryPy that provides the core web
functionality of Hue

If you have installed other applications into your Hue instance, you may see
other daemons running under the supervisor as well.

You can see the supervised processes running in the output of `ps -f -u hue`:

    UID        PID  PPID  C STIME TTY          TIME CMD
    hue       8685  8679  0 Aug05 ?        00:01:39 /usr/share/hue/build/env/bin/python /usr/share/hue/build/env/bin/desktop runcpserver

Note that the supervisor automatically restarts these processes if they fail for
any reason. If the processes fail repeatedly within a short time, the supervisor
itself shuts down.

## Logging

The Hue logs are found in `/var/log/hue`, or in a `logs` directory under your
Hue installation root. Inside the log directory you can find:

* An `access.log` file, which contains a log for all requests against the Hue
web server.
* A `supervisor.log` file, which contains log information for the supervisor
process.
* A `supervisor.out` file, which contains the stdout and stderr for the
supervisor process.
* A `.log` file for each supervised process described above, which contains
the logs for that process.
* A `.out` file for each supervised process described above, which contains
the stdout and stderr for that process.

If users on your cluster have problems running Hue, you can often find error
messages in these log files. If you are unable to start Hue from the init
script, the `supervisor.log` log file can often contain clues.

### Viewing Recent Log Messages

In addition to logging `INFO` level messages to the `logs` directory, the Hue
web server keeps a small buffer of log messages at all levels in memory. You can
view these logs by visiting `http://myserver:8888/hue/logs`. The `DEBUG` level
messages shown can sometimes be helpful in troubleshooting issues.

## Troubleshooting

To troubleshoot why Hue is slow or consuming high memory, admin can enable instrumentation by setting the `instrumentation` flag to True.
 <pre>
[desktop]
instrumentation=true
</pre>
 If `django_debug_mode` is enabled, instrumentation is automatically enabled. This flag appends the response time and the total peak memory used since Hue started for every logged request.

### Instrumentation enabled

<pre>
[17/Apr/2018 15:18:43 -0700] access       INFO     127.0.0.1 admin - "POST /jobbrowser/jobs/ HTTP/1.1" `returned in 97ms (mem: 135mb)`
</pre>

### Instrumentation not enabled

<pre>
[23/Apr/2018 10:59:01 -0700] INFO     127.0.0.1 admin - "POST /jobbrowser/jobs/ HTTP/1.1" returned in 88ms
</pre>

## Database

Hue requires a SQL database to store small amounts of data, including user
account information as well as history of job submissions and Hive queries.
By default, Hue is configured to use the embedded database SQLite for this
purpose, and should require no configuration or management by the administrator.
However, MySQL is the recommended database to use. This section contains
instructions for configuring Hue to access MySQL and other databases.

### Inspecting the Database

The default SQLite database used by Hue is located in: `/usr/share/hue/desktop/desktop.db`.
You can inspect this database from the command line using the `sqlite3`
program or typing `/usr/share/hue/build/env/bin/hue dbshell'. For example:

    sqlite3 /usr/share/hue/desktop/desktop.db
    SQLite version 3.6.22
    Enter ".help" for instructions
    Enter SQL statements terminated with a ";"
    sqlite> select username from auth_user;
    admin
    test
    sample
    sqlite>

It is strongly recommended that you avoid making any modifications to the
database directly using SQLite, though this trick can be useful for management
or troubleshooting.

### Backing up the Database

If you use the default SQLite database, then copy the `desktop.db` file to
another node for backup. It is recommended that you back it up on a regular
schedule, and also that you back it up before any upgrade to a new version of
Hue.

### Configuring to Access Another Database

Although SQLite is the default database type, some advanced users may prefer
to have Hue access an alternate database type. Note that if you elect to
configure Hue to use an external database, upgrades may require more manual
steps in the future.

The following instructions are for MySQL, though you can also configure Hue to
work with other common databases such as PostgreSQL and Oracle.

<div class="note">
Note that Hue has only been tested with SQLite and MySQL database backends.
</div>


### Configuring to Store Data in MySQL

To configure Hue to store data in MySQL:

1. Create a new database in MySQL and grant privileges to a Hue user to manage
   this database.

    <pre>
    mysql> create database hue;
    Query OK, 1 row affected (0.01 sec)
    mysql> grant all on hue.* to 'hue'@'localhost' identified by 'secretpassword';
    Query OK, 0 rows affected (0.00 sec)
    </pre>

2. Shut down Hue if it is running.

3. To migrate your existing data to MySQL, use the following command to dump the
   existing database data to a text file. Note that using the ".json" extension
   is required.

    <pre>
    /usr/share/hue/build/env/bin/hue dumpdata > $some-temporary-file.json
    </pre>

4. Open the `hue.ini` file in a text editor. Directly below the
   `[[database]]` line, add the following options (and modify accordingly for
   your MySQL setup):

    <pre>
    host=localhost
    port=3306
    engine=mysql
    user=hue
    password=secretpassword
    name=hue
    </pre>

5. As the Hue user, configure Hue to load the existing data and create the
   necessary database tables:

    <pre>
    /usr/share/hue/build/env/bin/hue syncdb --noinput
    mysql -uhue -psecretpassword -e "DELETE FROM hue.django_content_type;"
    /usr/share/hue/build/env/bin/hue loaddata $temporary-file-containing-dumped-data.json
    </pre>

Your system is now configured and you can start the Hue server as normal.

# Using Hue

After installation, you can use Hue by navigating to `http://myserver:8888/`.

The [user guide](../user-guide/user-guide.html) will help users go through the various installed applications.

## Supported Browsers

The two latest LTS versions of each browsers:

* Edge
* Safari
* Chrome
* Firefox

## Troubleshooting the tarball Installation

Q: I moved my Hue installation from one directory to another and now Hue no
longer functions correctly.

A: Due to the use of absolute paths by some Python packages, you must run a
series of commands if you move your Hue installation. In the new location, run:

    rm app.reg
    rm -r build
    make apps


Q: Why does "make install" compile other pieces of software?

A: In order to ensure that Hue is stable on a variety of distributions and
architectures, it installs a Python virtual environment which includes its
dependencies. This ensures that the software can depend on specific versions
of various Python libraries and you don't have to be concerned about missing
software components.


## Feedback

Your feedback is welcome. The best way to send feedback is to join the
https://groups.google.com/a/cloudera.org/group/hue-user[mailing list], and
send e-mail, to mailto:hue-user@cloudera.org[hue-user@cloudera.org].

## Reporting Bugs

If you find that something doesn't work, it'll often be helpful to include logs
from your server. Please include the
logs as a zip (or cut and paste the ones that look relevant) and send those with
your bug reports.

   </div>
</div>


<div class="row-fluid footer">
  Documentation improvements? Feel free to <a href="https://github.com/cloudera/hue/blob/master/docs/user-guide/user-guide.md">edit this page on GitHub </a> and send a pull request!
</div>


<script src="../js/jquery.min.js"></script>
<script src="../js/jquery.treed.js"></script>
<script src="../js/jquery.highlight.js"></script>
<script src="../js/hue-docs.js"></script>


<script async src="https://www.googletagmanager.com/gtag/js?id=UA-37637545-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-37637545-1');
</script>
