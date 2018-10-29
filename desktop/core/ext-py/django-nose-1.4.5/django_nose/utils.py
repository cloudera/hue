# coding: utf-8
"""django-nose utility methods."""
from __future__ import unicode_literals


def process_tests(suite, process):
    """Find and process the suite with setup/teardown methods.

    Given a nested disaster of [Lazy]Suites, traverse to the first level
    that has setup or teardown, and do something to them.

    If we were to traverse all the way to the leaves (the Tests)
    indiscriminately and return them, when the runner later calls them, they'd
    run without reference to the suite that contained them, so they'd miss
    their class-, module-, and package-wide setup and teardown routines.

    The nested suites form basically a double-linked tree, and suites will call
    up to their containing suites to run their setups and teardowns, but it
    would be hubris to assume that something you saw fit to setup or teardown
    at the module level is less costly to repeat than DB fixtures. Also, those
    sorts of setups and teardowns are extremely rare in our code. Thus, we
    limit the granularity of bucketing to the first level that has setups or
    teardowns.

    :arg process: The thing to call once we get to a leaf or a test with setup
        or teardown
    """
    if (not hasattr(suite, '_tests') or
            (hasattr(suite, 'hasFixtures') and suite.hasFixtures())):
        # We hit a Test or something with setup, so do the thing. (Note that
        # "fixtures" here means setup or teardown routines, not Django
        # fixtures.)
        process(suite)
    else:
        for t in suite._tests:
            process_tests(t, process)


def is_subclass_at_all(cls, class_info):
    """Return whether ``cls`` is a subclass of ``class_info``.

    Even if ``cls`` is not a class, don't crash. Return False instead.

    """
    try:
        return issubclass(cls, class_info)
    except TypeError:
        return False


def uses_mysql(connection):
    """Return whether the connection represents a MySQL DB."""
    return 'mysql' in connection.settings_dict['ENGINE']
