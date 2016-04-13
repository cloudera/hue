===========
django-nose
===========

.. image:: https://travis-ci.org/django-nose/django-nose.png
  :target: https://travis-ci.org/django-nose/django-nose

Features
--------

* All the goodness of `nose`_ in your Django tests, like...

  * Testing just your apps by default, not all the standard ones that happen to
    be in ``INSTALLED_APPS``
  * Running the tests in one or more specific modules (or apps, or classes, or
    folders, or just running a specific test)
  * Obviating the need to import all your tests into ``tests/__init__.py``.
    This not only saves busy-work but also eliminates the possibility of
    accidentally shadowing test classes.
  * Taking advantage of all the useful `nose plugins`_
* Fixture bundling, an optional feature which speeds up your fixture-based
  tests by a factor of 4
* Reuse of previously created test DBs, cutting 10 seconds off startup time
* Hygienic TransactionTestCases, which can save you a DB flush per test
* Support for various databases. Tested with MySQL, PostgreSQL, and SQLite.
  Others should work as well.

.. _nose: http://somethingaboutorange.com/mrl/projects/nose/
.. _nose plugins: http://nose-plugins.jottit.com/


Installation
------------

You can get django-nose from PyPI with... ::

    pip install django-nose

The development version can be installed with... ::

    pip install -e git://github.com/django-nose/django-nose.git#egg=django-nose

Since django-nose extends Django's built-in test command, you should add it to
your ``INSTALLED_APPS`` in ``settings.py``::

    INSTALLED_APPS = (
        ...
        'django_nose',
        ...
    )

Then set ``TEST_RUNNER`` in ``settings.py``::

    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'


Use
---

The day-to-day use of django-nose is mostly transparent; just run ``./manage.py
test`` as usual.

See ``./manage.py help test`` for all the options nose provides, and look to
the `nose docs`_ for more help with nose.

.. _nose docs: http://somethingaboutorange.com/mrl/projects/nose/


Enabling Database Reuse
-----------------------

You can save several seconds at the beginning and end of your test suite by
reusing the test database from the last run. To do this, set the environment
variable ``REUSE_DB`` to 1::

    REUSE_DB=1 ./manage.py test

The one new wrinkle is that, whenever your DB schema changes, you should leave
the flag off the next time you run tests. This will cue the test runner to
reinitialize the test database.

Also, REUSE_DB is not compatible with TransactionTestCases that leave junk in
the DB, so be sure to make your TransactionTestCases hygienic (see below) if
you want to use it.


Enabling Fast Fixtures
----------------------

django-nose includes a fixture bundler which drastically speeds up your tests
by eliminating redundant setup of Django test fixtures. To use it...

1. Subclass ``django_nose.FastFixtureTestCase`` instead of
   ``django.test.TestCase``. (I like to import it ``as TestCase`` in my
   project's ``tests/__init__.py`` and then import it from there into my actual
   tests. Then it's easy to sub the base class in and out.) This alone will
   cause fixtures to load once per class rather than once per test.
2. Activate fixture bundling by passing the ``--with-fixture-bundling`` option
   to ``./manage.py test``. This loads each unique set of fixtures only once,
   even across class, module, and app boundaries.

How Fixture Bundling Works
~~~~~~~~~~~~~~~~~~~~~~~~~~

The fixture bundler reorders your test classes so that ones with identical sets
of fixtures run adjacently. It then advises the first of each series to load
the fixtures once for all of them (and the remaining ones not to bother). It
also advises the last to tear them down. Depending on the size and repetition
of your fixtures, you can expect a 25% to 50% speed increase.

Incidentally, the author prefers to avoid Django fixtures, as they encourage
irrelevant coupling between tests and make tests harder to comprehend and
modify. For future tests, it is better to use the "model maker" pattern,
creating DB objects programmatically. This way, tests avoid setup they don't
need, and there is a clearer tie between a test and the exact state it
requires. The fixture bundler is intended to make existing tests, which have
already committed to fixtures, more tolerable.

Troubleshooting
~~~~~~~~~~~~~~~

If using ``--with-fixture-bundling`` causes test failures, it likely indicates
an order dependency between some of your tests. Here are the most frequent
sources of state leakage we have encountered:

* Locale activation, which is maintained in a threadlocal variable. Be sure to
  reset your locale selection between tests.
* memcached contents. Be sure to flush between tests. Many test superclasses do
  this automatically.

It's also possible that you have ``post_save`` signal handlers which create
additional database rows while loading the fixtures. ``FastFixtureTestCase``
isn't yet smart enough to notice this and clean up after it, so you'll have to
go back to plain old ``TestCase`` for now.

Exempting A Class From Bundling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In some unusual cases, it is desirable to exempt a test class from fixture
bundling, forcing it to set up and tear down its fixtures at the class
boundaries. For example, we might have a ``TestCase`` subclass which sets up
some state outside the DB in ``setUpClass`` and tears it down in
``tearDownClass``, and it might not be possible to adapt those routines to heed
the advice of the fixture bundler. In such a case, simply set the
``exempt_from_fixture_bundling`` attribute of the test class to ``True``.


Speedy Hygienic TransactionTestCases
------------------------------------

Unlike the stock Django test runner, django-nose lets you write custom
TransactionTestCase subclasses which expect to start with an unmarred DB,
saving an entire DB flush per test.

Background
~~~~~~~~~~

The default Django TransactionTestCase class `can leave the DB in an unclean
state`_ when it's done. To compensate, TransactionTestCase does a
time-consuming flush of the DB *before* each test to ensure it begins with a
clean slate. Django's stock test runner then runs TransactionTestCases last so
they don't wreck the environment for better-behaved tests. django-nose
replicates this behavior.

Escaping the Grime
~~~~~~~~~~~~~~~~~~

Some people, however, have made subclasses of TransactionTestCase that clean up
after themselves (and can do so efficiently, since they know what they've
changed). Like TestCase, these may assume they start with a clean DB. However,
any TransactionTestCases that run before them and leave a mess could cause them
to fail spuriously.

django-nose offers to fix this. If you include a special attribute on your
well-behaved TransactionTestCase... ::

    class MyNiceTestCase(TransactionTestCase):
        cleans_up_after_itself = True

...django-nose will run it before any of those nasty, trash-spewing test cases.
You can thus enjoy a big speed boost any time you make a TransactionTestCase
clean up after itself: skipping a whole DB flush before every test. With a
large schema, this can save minutes of IO.

django-nose's own FastFixtureTestCase uses this feature, even though it
ultimately acts more like a TestCase than a TransactionTestCase.

.. _can leave the DB in an unclean state: https://docs.djangoproject.com/en/1.4/topics/testing/#django.test.TransactionTestCase


Test-Only Models
----------------

If you have a model that is used only by tests (for example, to test an
abstract model base class), you can put it in any file that's imported in the
course of loading tests. For example, if the tests that need it are in
``test_models.py``, you can put the model in there, too. django-nose will make
sure its DB table gets created.


Assertions
----------

``django-nose.tools`` provides pep8 versions of Django's TestCase asserts
and some of its own as functions. ::

   assert_redirects(response, expected_url, status_code=302, target_status_code=200, host=None, msg_prefix='')

   assert_contains(response, text, count=None, status_code=200, msg_prefix='')
   assert_not_contains(response, text, count=None, status_code=200, msg_prefix='')

   assert_form_error(response, form, field, errors, msg_prefix='')

   assert_template_used(response, template_name, msg_prefix='')
   assert_template_not_used(response, template_name, msg_prefix='')

   assert_queryset_equal(qs, values, transform=repr)

   assert_num_queries(num, func=None, *args, **kwargs)

   assert_code(response, status_code, msg_prefix='')

   assert_ok(response, msg_prefix='')

   assert_mail_count(count, msg=None)


Using With South
----------------

`South`_ installs its own test command that turns off migrations during
testing. Make sure that django-nose comes *after* ``south`` in
``INSTALLED_APPS`` so that django_nose's test command is used.

.. _South: http://south.aeracode.org/


Always Passing The Same Options
-------------------------------

To always set the same command line options you can use a `nose.cfg or
setup.cfg`_ (as usual) or you can specify them in settings.py like this::

    NOSE_ARGS = ['--failed', '--stop']

.. _nose.cfg or setup.cfg: http://somethingaboutorange.com/mrl/projects/nose/0.11.2/usage.html#configuration


Custom Plugins
--------------

If you need to `make custom plugins`_, you can define each plugin class
somewhere within your app and load them from settings.py like this::

    NOSE_PLUGINS = [
        'yourapp.tests.plugins.SystematicDysfunctioner',
        # ...
    ]

Just like middleware or anything else, each string must be a dot-separated,
importable path to an actual class. Each plugin class will be instantiated and
added to the Nose test runner.

.. _make custom plugins: http://somethingaboutorange.com/mrl/projects/nose/0.11.2/plugins.html#writing-plugins


Older Versions of Django
------------------------
Upgrading from Django <= 1.3 to Django 1.4
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In versions of Django < 1.4 the project folder was in fact a python package as
well (note the __init__.py in your project root). In Django 1.4, there is no
such file and thus the project is not a python module.

**When you upgrade your Django project to the Django 1.4 layout, you need to
remove the __init__.py file in the root of your project (and move any python
files that reside there other than the manage.py) otherwise you will get a
`ImportError: No module named urls` exception.**

This happens because Nose will intelligently try to populate your sys.path, and
in this particular case includes your parent directory if your project has a
__init__.py file (see: https://github.com/nose-devs/nose/blob/release_1.1.2/nose/importer.py#L134).

This means that even though you have set up your directory structure properly and
set your `ROOT_URLCONF='my_project.urls'` to match the new structure, when running
django-nose's test runner it will try to find your urls.py file in `'my_project.my_project.urls'`.


Upgrading from Django < 1.2
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Django 1.2 switches to a `class-based test runner`_. To use django-nose
with Django 1.2, change your ``TEST_RUNNER`` from ``django_nose.run_tests`` to
``django_nose.NoseTestSuiteRunner``.

``django_nose.run_tests`` will continue to work in Django 1.2 but will raise a
warning. In Django 1.3, it will stop working.

If you were using ``django_nose.run_gis_tests``, you should also switch to
``django_nose.NoseTestSuiteRunner`` and use one of the `spatial backends`_ in
your ``DATABASES`` settings.

.. _class-based test runner: http://docs.djangoproject.com/en/dev/releases/1.2/#function-based-test-runners
.. _spatial backends: http://docs.djangoproject.com/en/dev/ref/contrib/gis/db-api/#id1

Django 1.1
~~~~~~~~~~

If you want to use django-nose with Django 1.1, use
https://github.com/django-nose/django-nose/tree/django-1.1 or
http://pypi.python.org/pypi/django-nose/0.0.3.

Django 1.0
~~~~~~~~~~

django-nose does not support Django 1.0.


Recent Version History
----------------------

1.3 (2014-12-05)
  * Django 1.6 and 1.7 support (conrado, co3k, Nepherhotep, mbertheau)
  * Python 3.3 and 3.4 testing and support (frewsxcv, jsocol)

1.2 (2013-07-23)
  * Python 3 support (melinath and jonashaag)
  * Django 1.5 compat (fabiosantoscode)

1.1 (2012-05-19)
  * Django TransactionTestCases don't clean up after themselves; they leave
    junk in the DB and clean it up only on ``_pre_setup``. Thus, Django makes
    sure these tests run last. Now django-nose does, too. This means one fewer
    source of failures on existing projects. (Erik Rose)
  * Add support for hygienic TransactionTestCases. (Erik Rose)
  * Support models that are used only for tests. Just put them in any file
    imported in the course of loading tests. No more crazy hacks necessary.
    (Erik Rose)
  * Make the fixture bundler more conservative, fixing some conceivable
    situations in which fixtures would not appear as intended if a
    TransactionTestCase found its way into the middle of a bundle. (Erik Rose)
  * Fix an error that would surface when using SQLAlchemy with connection
    pooling. (Roger Hu)
  * Gracefully ignore the new ``--liveserver`` option introduced in Django 1.4;
    don't let it through to nose. (Adam DePue)

1.0 (2012-03-12)
  * New fixture-bundling plugin for avoiding needless fixture setup (Erik Rose)
  * Moved FastFixtureTestCase in from test-utils, so now all the
    fixture-bundling stuff is in one library. (Erik Rose)
  * Added the REUSE_DB setting for faster startup and shutdown. (Erik Rose)
  * Fixed a crash when printing options with certain verbosities. (Daniel Abel)
  * Broke hard dependency on MySQL. Support PostgreSQL. (Roger Hu)
  * Support SQLite, both memory- and disk-based. (Roger Hu and Erik Rose)
  * Nail down versions of the package requirements. (Daniel Mizyrycki)

0.1.3 (2010-04-15)
  * Even better coverage support (rozza)
  * README fixes (carljm and ionelmc)
  * optparse OptionGroups are handled better (outofculture)
  * nose plugins are loaded before listing options

See more in changelog.txt.
