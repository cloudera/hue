Welcome to the repository for Hue
=================================

.. note::
    This is the development-oriented readme. If you want to write notes for
    end users, please put them in ``dist/README``.

Hue is both a Web UI for Hadoop and a framework to create interactive Web
applications. It features:

      * FileBrowser for accessing HDFS
      * Job Designer for creating MapReduce/Streaming/Java jobs
      * Beeswax application for executing Hive queries
      * Impala App for executing Cloudera Impala queries
      * Oozie App for submitting and scheduling workflows
      * JobBrowser for viewing MapReduce jobs
      * A Pig/HBase/Sqoop2 shell

On top of that, a SDK is available for creating new apps integrated with Hadoop.

More user and developer documentation is available at http://cloudera.github.com/hue/.


Getting Started
===============
To build and get the core server running::

    $ git clone http://github.com/cloudera/hue.git
    $ cd hue
    $ make apps
    $ build/env/bin/hue runserver

If using the Beeswax application, start the daemon::

    $ build/env/bin/hue beeswax_server

Now Hue should be running on http://localhost:8000.

The configuration in development mode is ``desktop/conf/pseudo-distributed.ini``.


Note: to start all the servers in one command (but lose the automatic reloading after source modification)::

   $ build/env/bin/supervisor

To run the tests::

   $ build/env/bin/hue test all
   $ build/env/bin/hue test specific filebrowser
   $ build/env/bin/hue test specific jobbrowser.tests:test_get_path


Development Prerequisites
===========================
You'll need these library development packages and tools installed on
your system:

    Ubuntu:
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
      * mvn (from ``maven2`` package or tarball)
      * openldap-dev / libldap2-dev
      * python-dev
      * python-simplejson
      * python-setuptools

    CentOS:
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
      * mvn (from ``maven2`` package or tarball)
      * mysql
      * mysql-devel
      * openldap-devel
      * python-devel
      * python-simplejson
      * sqlite-devel

    MacOS (mac port):
      * liblxml
      * libxml2
      * libxslt
      * mysql5-devel
      * simplejson (easy_install)
      * sqlite3


File Layout
===========
The Hue "framework" is in ``desktop``. ``/core/`` contains the Web components and
``desktop/libs/`` the API for talking to Hadoop.
The installable apps live in ``apps/``.  Please place third-party dependencies in the app's ext-py/
directory.

The typical directory structure for inside an application includes:

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

For the URLs within your application, you should make your own ``urls.py``
which will be automatically rooted at ``/yourappname/`` in the global
namespace.  See ``apps/about/src/about/urls.py`` for an example.


Main Stack
==========

   * Python 2.4 - 2.7
   * Django 1.2 https://docs.djangoproject.com/en/1.2/
   * Mako
   * jQuery
   * Bootstrap


Community
=========
   * User group: http://groups.google.com/a/cloudera.org/group/hue-user
   * Jira: https://issues.cloudera.org/browse/HUE


License
=======
Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0


