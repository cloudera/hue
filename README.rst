Welcome to the repository for Hue
=================================

.. note::
    This is the development-oriented readme. If you want to write notes for
    end users, please put them in ``dist/README``.

Hue is both a Web UI for Hadoop and a framework to create interactive Web
applications. It features:

      * FileBrowser for accessing HDFS
      * Job Designer for creating MapReduce/Streaming/Java jobs
      * Oozie App for submitting and scheduling workflows
      * JobBrowser for viewing MapReduce jobs
      * Beeswax application for executing Hive queries
      * A Pig/HBase shell

On top of that, a SDK is available for creating new apps integrated with Hadoop.

More documentation is available at http://cloudera.github.com/hue/.


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


Using and Installing Thrift
===========================
Right now, we check in the generated thrift code.
To generate the code, you'll need the thrift binary version 0.7.0.
Please download from http://thrift.apache.org/.

The modules using ``Thrift`` have some helper scripts like ``regenerate_thrift.sh``
for regenerating the code from the interfaces.


Profiling Hue Apps
==================
Hue has a profiling system built in, which can be used to analyze server-side
performance of applications.  To enable profiling::

    $ build/env/bin/hue runprofileserver

Then, access the page that you want to profile.  This will create files like
/tmp/useradmin.users.000072ms.2011-02-21T13:03:39.745851.prof.  The format for
the file names is /tmp/<app_module>.<page_url>.<time_taken>.<timestamp>.prof.

Hue uses the hotshot profiling library for instrumentation.  The documentation
for this library is located at: http://docs.python.org/library/hotshot.html.

You can use kcachegrind to view the profiled data graphically::

    $ hotshot2calltree /tmp/xyz.prof > /tmp/xyz.trace
    $ kcachegrind /tmp/xyz.trace

More generally, you can programmatically inspect a trace::

    #!/usr/bin/python
    import hotshot.stats
    import sys

    stats = hotshot.stats.load(sys.argv[1])
    stats.sort_stats('cumulative', 'calls')
    stats.print_stats(100)

This script takes in a .prof file, and orders function calls by the cumulative
time spent in that function, followed by the number of times the function was
called, and then prints out the top 100 time-wasters.  For information on the
other stats available, take a look at this website:
http://docs.python.org/library/profile.html#pstats.Stats


Internationalization
====================
How to update all the messages and compile them::

    $ make locales

How to update and compile the messages of one app::

    $ cd apps/beeswax
    $ make compile-locale

How to create a new locale for an app::

    $ cd $APP_ROOT/src/$APP_NAME/locale
    $ $HUE_ROOT/build/env/bin/pybabel init -D django -i en_US.pot -d . -l fr


License
=======
Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0


