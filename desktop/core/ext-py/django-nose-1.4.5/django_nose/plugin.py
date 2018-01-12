# coding: utf-8
"""Included django-nose plugins."""
from __future__ import unicode_literals

import sys

from nose.plugins.base import Plugin
from nose.suite import ContextSuite

from django.test.testcases import TransactionTestCase, TestCase

from django_nose.testcases import FastFixtureTestCase
from django_nose.utils import process_tests, is_subclass_at_all


class AlwaysOnPlugin(Plugin):
    """A base plugin that takes no options and is always enabled."""

    def options(self, parser, env):
        """Avoid adding a ``--with`` option for this plugin.

        We don't have any options, and this plugin is always enabled, so we
        don't want to use superclass's ``options()`` method which would add a
        ``--with-*`` option.
        """

    def configure(self, *args, **kw_args):
        """Configure and enable this plugin."""
        super(AlwaysOnPlugin, self).configure(*args, **kw_args)
        self.enabled = True


class ResultPlugin(AlwaysOnPlugin):
    """Captures the TestResult object for later inspection.

    nose doesn't return the full test result object from any of its runner
    methods.  Pass an instance of this plugin to the TestProgram and use
    ``result`` after running the tests to get the TestResult object.
    """

    name = 'result'

    def finalize(self, result):
        """Finalize test run by capturing the result."""
        self.result = result


class DjangoSetUpPlugin(AlwaysOnPlugin):
    """Configures Django to set up and tear down the environment.

    This allows coverage to report on all code imported and used during the
    initialization of the test runner.
    """

    name = 'django setup'
    score = 150

    def __init__(self, runner):
        """Initialize the plugin with the test runner."""
        super(DjangoSetUpPlugin, self).__init__()
        self.runner = runner
        self.sys_stdout = sys.stdout

    def prepareTest(self, test):
        """Create the Django DB and model tables, and do other setup.

        This isn't done in begin() because that's too early--the DB has to be
        set up *after* the tests are imported so the model registry contains
        models defined in tests.py modules. Models are registered at
        declaration time by their metaclass.

        prepareTestRunner() might also have been a sane choice, except that, if
        some plugin returns something from it, none of the other ones get
        called. I'd rather not dink with scores if I don't have to.

        """
        # What is this stdout switcheroo for?
        sys_stdout = sys.stdout
        sys.stdout = self.sys_stdout

        self.runner.setup_test_environment()
        self.old_names = self.runner.setup_databases()

        sys.stdout = sys_stdout

    def finalize(self, result):
        """Finalize test run by cleaning up databases and environment."""
        self.runner.teardown_databases(self.old_names)
        self.runner.teardown_test_environment()


class Bucketer(object):
    """Collect tests into buckets with similar setup requirements."""

    def __init__(self):
        """Initialize the test buckets."""
        # { (frozenset(['users.json']), True):
        #      [ContextSuite(...), ContextSuite(...)] }
        self.buckets = {}

        # All the non-FastFixtureTestCase tests we saw, in the order they came
        # in:
        self.remainder = []

    def add(self, test):
        """Add test into an initialization bucket.

        Tests are bucketed according to its set of fixtures and the
        value of its exempt_from_fixture_bundling attr.
        """
        if is_subclass_at_all(test.context, FastFixtureTestCase):
            # We bucket even FFTCs that don't have any fixtures, but it
            # shouldn't matter.
            key = (frozenset(getattr(test.context, 'fixtures', [])),
                   getattr(test.context,
                           'exempt_from_fixture_bundling',
                           False))
            self.buckets.setdefault(key, []).append(test)
        else:
            self.remainder.append(test)


class TestReorderer(AlwaysOnPlugin):
    """Reorder tests for various reasons."""

    name = 'django-nose-test-reorderer'

    def options(self, parser, env):
        """Add --with-fixture-bundling to options."""
        super(TestReorderer, self).options(parser, env)  # pointless
        parser.add_option('--with-fixture-bundling',
                          action='store_true',
                          dest='with_fixture_bundling',
                          default=env.get('NOSE_WITH_FIXTURE_BUNDLING', False),
                          help='Load a unique set of fixtures only once, even '
                               'across test classes. '
                               '[NOSE_WITH_FIXTURE_BUNDLING]')

    def configure(self, options, conf):
        """Configure plugin, reading the with_fixture_bundling option."""
        super(TestReorderer, self).configure(options, conf)
        self.should_bundle = options.with_fixture_bundling

    def _put_transaction_test_cases_last(self, test):
        """Reorder test suite so TransactionTestCase-based tests come last.

        Django has a weird design decision wherein TransactionTestCase doesn't
        clean up after itself. Instead, it resets the DB to a clean state only
        at the *beginning* of each test:
        https://docs.djangoproject.com/en/dev/topics/testing/?from=olddocs#
        django. test.TransactionTestCase. Thus, Django reorders tests so
        TransactionTestCases all come last. Here we do the same.

        "I think it's historical. We used to have doctests also, adding cleanup
        after each unit test wouldn't necessarily clean up after doctests, so
        you'd have to clean on entry to a test anyway." was once uttered on
        #django-dev.
        """
        def filthiness(test):
            """Return a score of how messy a test leaves the environment.

            Django's TransactionTestCase doesn't clean up the DB on teardown,
            but it's hard to guess whether subclasses (other than TestCase) do.
            We will assume they don't, unless they have a
            ``cleans_up_after_itself`` attr set to True. This is reasonable
            because the odd behavior of TransactionTestCase is documented, so
            subclasses should by default be assumed to preserve it.

            Thus, things will get these comparands (and run in this order):

            * 1: TestCase subclasses. These clean up after themselves.
            * 1: TransactionTestCase subclasses with
                 cleans_up_after_itself=True. These include
                 FastFixtureTestCases. If you're using the
                 FixtureBundlingPlugin, it will pull the FFTCs out, reorder
                 them, and run them first of all.
            * 2: TransactionTestCase subclasses. These leave a mess.
            * 2: Anything else (including doctests, I hope). These don't care
                 about the mess you left, because they don't hit the DB or, if
                 they do, are responsible for ensuring that it's clean (as per
                 https://docs.djangoproject.com/en/dev/topics/testing/?from=
                 olddocs#writing-doctests)

            """
            test_class = test.context
            if (is_subclass_at_all(test_class, TestCase) or
                (is_subclass_at_all(test_class, TransactionTestCase) and
                 getattr(test_class, 'cleans_up_after_itself', False))):
                return 1
            return 2

        flattened = []
        process_tests(test, flattened.append)
        flattened.sort(key=filthiness)
        return ContextSuite(flattened)

    def _bundle_fixtures(self, test):
        """Reorder tests to minimize fixture loading.

        I reorder FastFixtureTestCases so ones using identical sets
        of fixtures run adjacently. I then put attributes on them
        to advise them to not reload the fixtures for each class.

        This takes support.mozilla.com's suite from 123s down to 94s.

        FastFixtureTestCases are the only ones we care about, because
        nobody else, in practice, pays attention to the ``_fb`` advisory
        bits. We return those first, then any remaining tests in the
        order they were received.
        """
        def suite_sorted_by_fixtures(suite):
            """Flatten and sort a tree of Suites by fixture.

            Add ``_fb_should_setup_fixtures`` and
            ``_fb_should_teardown_fixtures`` attrs to each test class to advise
            it whether to set up or tear down (respectively) the fixtures.

            Return a Suite.

            """
            bucketer = Bucketer()
            process_tests(suite, bucketer.add)

            # Lay the bundles of common-fixture-having test classes end to end
            # in a single list so we can make a test suite out of them:
            flattened = []
            for (key, fixture_bundle) in bucketer.buckets.items():
                fixtures, is_exempt = key
                # Advise first and last test classes in each bundle to set up
                # and tear down fixtures and the rest not to:
                if fixtures and not is_exempt:
                    # Ones with fixtures are sure to be classes, which means
                    # they're sure to be ContextSuites with contexts.

                    # First class with this set of fixtures sets up:
                    first = fixture_bundle[0].context
                    first._fb_should_setup_fixtures = True

                    # Set all classes' 1..n should_setup to False:
                    for cls in fixture_bundle[1:]:
                        cls.context._fb_should_setup_fixtures = False

                    # Last class tears down:
                    last = fixture_bundle[-1].context
                    last._fb_should_teardown_fixtures = True

                    # Set all classes' 0..(n-1) should_teardown to False:
                    for cls in fixture_bundle[:-1]:
                        cls.context._fb_should_teardown_fixtures = False

                flattened.extend(fixture_bundle)
            flattened.extend(bucketer.remainder)

            return ContextSuite(flattened)

        return suite_sorted_by_fixtures(test)

    def prepareTest(self, test):
        """Reorder the tests."""
        test = self._put_transaction_test_cases_last(test)
        if self.should_bundle:
            test = self._bundle_fixtures(test)
        return test
