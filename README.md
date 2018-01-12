![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/hue_logo.png "Hue Logo")


Query. Explore. Repeat.
-----------------------

Hue is an open source Query Tool for browsing, querying and visualizing data with focus on SQL and Search: [gethue.com](http://gethue.com)

It features:

   * [Editors](http://gethue.com/sql-editor/) for Hive, Impala, Pig, MapReduce, Spark and any SQL like MySQL, Oracle, SparkSQL, Solr SQL, Phoenix and more.
   * [Dashboards](http://gethue.com/search-dashboards/) to dynamically interact and visualize data with Solr or SQL.
   * [Scheduler](http://gethue.com/scheduling/) of jobs and workflows.
   * [Browsers](http://gethue.com/browsers/) for Jobs, HDFS, S3 files, SQL Tables, Indexes, Git files, Sentry permissions, Sqoop and more.


![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/sql-editor.png "Hue Editor")

![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/dashboard.png "Hue Dashboard")


Who is using Hue
----------------
Thousands of companies and organizations use Hue to open-up and query their data in order to make smarter decisions. Just at Cloudera, Hue is heavily used by hundreds of customers executing millions of queries daily. Hue directly ships in Cloudera, Amazon, MapR, BigTop and is compatible with the other distributions.


Getting Started
---------------
Add the development packages, build and get the development server running:
```
git clone https://github.com/cloudera/hue.git
cd hue
make apps
build/env/bin/hue runserver
```
Now Hue should be running on [http://localhost:8000](http://localhost:8000) ! The configuration in development mode is ``desktop/conf/pseudo-distributed.ini``.

Explore the [latest documentation](http://cloudera.github.io/hue/latest/).


Docker
------
Start Hue in a single click with the [Docker Guide](https://github.com/cloudera/hue/tree/master/tools/docker) or the
[video blog post](http://gethue.com/getting-started-with-hue-in-2-minutes-with-docker/).


Prerequisites
-------------
You'll need these library development packages and tools installed on your system:

* Python 2.6.5 - 2.7

__Ubuntu:__

* sudo apt-get install git ant gcc g++ libffi-dev libkrb5-dev libmysqlclient-dev libsasl2-dev libsasl2-modules-gssapi-mit libsqlite3-dev libssl-dev libxml2-dev libxslt-dev make maven libldap2-dev python-dev python-setuptools libgmp3-dev

* Oracle's JDK [(read more here)](https://help.ubuntu.com/community/Java)
```
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java7-installer
```

* mvn (from ``maven`` package or maven3 tarball)
* openldap-dev / libldap2-dev
* libtidy-0.99-0 (for unit tests only)


__CentOS/RHEL:__

* sudo yum install ant asciidoc cyrus-sasl-devel cyrus-sasl-gssapi cyrus-sasl-plain gcc gcc-c++ krb5-devel libffi-devel libxml2-devel libxslt-devel make  mysql mysql-devel openldap-devel python-devel sqlite-devel gmp-devel

* Oracle's JDK [(read more here)](https://www.digitalocean.com/community/tutorials/how-to-install-java-on-centos-and-fedora)

* mvn (from [``apache-maven``](https://gist.github.com/sebsto/19b99f1fa1f32cae5d00) package or maven3 tarball)
* libtidy (for unit tests only)
* openssl-devel (for version 7+)


__MacOS:__

* Xcode command line tools
* Oracle's JDK 1.7+
* maven (Homebrew)
* mysql (Homebrew)
* gmp (Homebrew)
* openssl (Homebrew)
* Required for Mac OS X 10.11+ (El Capitan), after ``brew install openssl``, run: ``export LDFLAGS=-L/usr/local/opt/openssl/lib && export CPPFLAGS=-I/usr/local/opt/openssl/include``


Community
-----------
   * User group: http://groups.google.com/a/cloudera.org/group/hue-user
   * Jira: https://issues.cloudera.org/browse/HUE
   * Reviews: https://review.cloudera.org/dashboard/?view=to-group&group=hue (repo 'hue-rw')


License
-----------
Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
