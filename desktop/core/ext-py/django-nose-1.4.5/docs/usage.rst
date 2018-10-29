Usage
=====

The day-to-day use of django-nose is mostly transparent; just run ``./manage.py
test`` as usual.

See ``./manage.py help test`` for all the options nose provides, and look to
the `nose docs`_ for more help with nose.

.. _nose docs: https://nose.readthedocs.io/en/latest/

Enabling Database Reuse
-----------------------

.. warning:: There are several
   `open issues <https://github.com/django-nose/django-nose/milestones/Fix%20REUSE_DB=1>`_
   with this feature, including
   `reports of data loss <https://github.com/django-nose/django-nose/issues/76>`_.

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

.. warning:: There are several
   `known issues <https://github.com/django-nose/django-nose/milestones/Fix%20FastFixtureTestCase>`_
   with this feature.

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


Always Passing The Same Options
-------------------------------

To always set the same command line options you can use a `nose.cfg or
setup.cfg`_ (as usual) or you can specify them in settings.py like this::

    NOSE_ARGS = ['--failed', '--stop']

.. _nose.cfg or setup.cfg: https://nose.readthedocs.io/en/latest/usage.html#configuration


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

.. _make custom plugins: https://nose.readthedocs.io/en/latest/plugins.html#writing-plugins

