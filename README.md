![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/hue_logo.png "Hue Logo")


Welcome to the repository for Hue
-----------

Hue is an open source Web interface for analyzing data with any Apache Hadoop: [gethue.com](http://gethue.com)

![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/hue-screen.png "Hue Screenshot")

It features:

   * SQL Editors for Hive, Impala, MySql, PostGres, Sqlite and Oracle
   * Dynamic search dashboards for Solr
   * Spark Notebooks
   * Browsers for YARN, HDFS, Hive table Metastore, HBase, ZooKeeper
   * Pig Editor, Sqoop2, Oozie workflows Editors and Dashboards
   * Wizards to import data into Hadoop

On top of that, an SDK is available for creating new apps integrated with Hadoop.

More user and developer documentation is available at [gethue.com](http://gethue.com).


Getting Started
-----------
To build and get the development server running:
```
$ git clone https://github.com/cloudera/hue.git
$ cd hue
$ make apps
$ build/env/bin/hue runserver
```
Now Hue should be running on [http://localhost:8000](http://localhost:8000) !

The configuration in development mode is ``desktop/conf/pseudo-distributed.ini``.


Note: to start the production server (but lose the automatic reloading after source modification):
```
$ build/env/bin/supervisor
```
To run the tests:

Install the mini cluster (only once):
```
$ ./tools/jenkins/jenkins.sh slow
```

Run all the tests:
```
$ build/env/bin/hue test all
```

Or just some parts of the tests, e.g.:
```
$ build/env/bin/hue test specific impala
$ build/env/bin/hue test specific impala.tests:TestMockedImpala
$ build/env/bin/hue test specific impala.tests:TestMockedImpala.test_basic_flow
```


Development Prerequisites
-----------
You'll need these library development packages and tools installed on
your system:

__Ubuntu:__

* Oracle's JDK [(read more here)](https://help.ubuntu.com/community/Java)
* ant
* gcc
* g++
* libkrb5-dev
* libmysqlclient-dev
* libssl-dev
* libsasl2-dev
* libsasl2-modules-gssapi-mit
* libsqlite3-dev
* libtidy-0.99-0 (for unit tests only)
* libxml2-dev
* libxslt-dev
* make
* mvn (from ``maven`` package or maven3 tarball)
* openldap-dev / libldap2-dev
* python-dev
* python-setuptools
* libgmp3-dev
* libz-dev

__CentOS/RHEL:__

* Oracle's JDK [(read more here)](https://www.digitalocean.com/community/tutorials/how-to-install-java-on-centos-and-fedora)
* ant
* asciidoc
* cyrus-sasl-devel
* cyrus-sasl-gssapi
* gcc
* gcc-c++
* krb5-devel
* libtidy (for unit tests only)
* libxml2-devel
* libxslt-devel
* make
* mvn (from [``apache-maven``](https://gist.github.com/sebsto/19b99f1fa1f32cae5d00) package or maven3 tarball)
* mysql
* mysql-devel
* openldap-devel
* python-devel
* sqlite-devel
* openssl-devel (for version 7+)
* gmp-devel

__MacOS:__

* Xcode command line tools
* Oracle's JDK 1.7+
* maven (Homebrew)
* mysql (Homebrew)
* gmp (Homebrew)
* openssl (Homebrew)
* Required for Mac OS X 10.11+ (El Capitan), after ``brew install openssl``, run: ``export LDFLAGS=-L/usr/local/opt/openssl/lib && export CPPFLAGS=-I/usr/local/opt/openssl/include``


File Layout
-----------
The Hue "framework" is in ``desktop/core/`` and contains the Web components.
``desktop/libs/`` is the API for talking to various Hadoop services.
The installable apps live in ``apps/``.  Please place third-party dependencies in the app's ext-py/
directory.

The typical directory structure for inside an application includes:
```
  src/
    for Python/Django code
      models.py
      urls.py
      views.py
      forms.py
      settings.py

  conf/
    for configuration (``.ini``) files to be installed

  static/
    for static HTML/js resources and help doc

  templates/
    for data to be put through a template engine

  locales/
    for localizations in multiple languages
```

For the URLs within your application, you should make your own ``urls.py``
which will be automatically rooted at ``/yourappname/`` in the global
namespace.  See ``apps/about/src/about/urls.py`` for an example.


Main Stack
-----------
Hue would not be possible without:

   * Python 2.6.5 - 2.7
   * Django 1.6 (https://docs.djangoproject.com/en/1.6/)
   * Knockout.js (http://knockoutjs.com/)
   * jQuery (http://jquery.com/)
   * Bootstrap (http://getbootstrap.com/)


Community
-----------
   * User group: http://groups.google.com/a/cloudera.org/group/hue-user
   * Jira: https://issues.cloudera.org/browse/HUE
   * Reviews: https://review.cloudera.org/dashboard/?view=to-group&group=hue (repo 'hue-rw')


License
-----------
Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
