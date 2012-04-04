The short story
===============

Python-based tests:

  "build/env/bin/hue test all" runs all the tests.

You should be running that before you push.

Windmill-tests:

  build/env/bin/hue test windmill

runs all the windmill tests.  It uses port 8999.

  build/env/bin/hue runserver_plus
followed by
  build/env/bin/windmill -e test=core/src/desktop/windmilltests.py firefox http://localhost:8000/


Longer story
============

The ``test`` management command prepares the arguments (test app names)
and passes them to nose (django_nose.nose_runner). Nose will then magically
find all the tests to run.

Tests themselves should be named *_test.py.  These will be found
as long as they're in packages covered by django.  You can use the
unittest frameworks, or you can just name your method with
the word "test" at a word boundary, and nose will find it.
See apps/hello/src/hello/hello_test.py for an example.


Helpful command-line tricks
===========================

To run tests that do not depend on Hadoop, use:
  build/env/bin/hue test fast

To run all tests, use:
  build/env/bin/hue test all

To run only tests of a particular app, use:
  build/env/bin/hue test specific <app>
E.g.
  build/env/bin/hue test specific filebrowser

To run a specific test, use:
  build/env/bin/hue test specific <test_func>
E.g.
  build/env/bin/hue test specific useradmin.tests:test_user_admin

Start up pdb on test failures:
  build/env/bin/hue test <args> --pdb --pdb-failure -s


Special environment variables
=============================

DESKTOP_LOGLEVEL=<level>
  level can be DEBUG, INFO, WARN, ERROR, or CRITICAL

  When specified, the console logger is set to the given log level. A console
  logger is created if one is not defined.

DESKTOP_DEBUG
  A shorthand for DESKTOP_LOG_LEVEL=DEBUG. Also turns on output HTML
  validation.

DESKTOP_PROFILE
  Turn on Python profiling. The profile data is saved in a file. See the
  console output for the location of the file.

DESKTOP_LOG_DIR=<dir>
  Specify the HUE log directory. Defaults to ./log.

DESKTOP_DB_CONFIG=<db engine:db name:test db name:username:password:host:port>
  Specify alternate DB connection parameters for HUE to use. Useful for
  testing your changes against, for example, MySQL instead of sqlite. String
  is a colon-delimited list.


Writing tests that depend on Hadoop
===================================

Use pseudo_hdfs4.py!  You should tag such tests with "requires_hadoop", as follows:

  from nose.plugins.attrib import attr

  @attr('requires_hadoop')
  def your_test():
    ...


Hudson Configuration
====================

Because building Hadoop (for the tests that require it) is slow, we've
separated the Hudson builds into "fast" and "slow".  Both are run
via scripts/hudson.sh, which should be kept updated with the latest
and greatest in build technologies.

Headless Windmill
=================
Ideally, all you need to do is install xvfb and run "xvfb-run bin/hue test_windmill".
To debug, however, you'll need to be able to check out what's going on.  You can run
"xvfb-run bash", followed by "x11vnc", and then connect to your X via VNC from another
machine.  This lets you eavesdrop nicely.
