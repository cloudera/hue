"""
Django test runner that invokes nose.

Usage:
    ./manage.py test DJANGO_ARGS -- NOSE_ARGS

The 'test' argument, and any other args before '--', will not be passed
to nose, allowing django args and nose args to coexist.

You can use

    NOSE_ARGS = ['list', 'of', 'args']

in settings.py for arguments that you always want passed to nose.
"""
import sys

from django.conf import settings
from django.db import connection
from django.test import utils

import nose

SETUP_ENV = 'setup_test_environment'
TEARDOWN_ENV = 'teardown_test_environment'


def get_test_enviroment_functions():
    """The functions setup_test_environment and teardown_test_environment in
    <appname>.tests modules will be automatically called before and after
    running the tests.
    """
    setup_funcs = []
    teardown_funcs = []
    for app_name in settings.INSTALLED_APPS:
        mod = __import__(app_name, None, None, ['tests'])
        if hasattr(mod, 'tests'):
            if hasattr(mod.tests, SETUP_ENV):
                setup_funcs.append(getattr(mod.tests, SETUP_ENV))
            if hasattr(mod.tests, TEARDOWN_ENV):
                teardown_funcs.append(getattr(mod.tests, TEARDOWN_ENV))
    return setup_funcs, teardown_funcs


def setup_test_environment(setup_funcs):
    utils.setup_test_environment()
    for func in setup_funcs:
        func()


def teardown_test_environment(teardown_funcs):
    utils.teardown_test_environment()
    for func in teardown_funcs:
        func()


def run_tests_explicit(nose_args, verbosity=1, interactive=True):
    """Setup django and run nose with given arguments."""
    setup_funcs, teardown_funcs = get_test_enviroment_functions()
    # Prepare django for testing.
    setup_test_environment(setup_funcs)
    old_db_name = settings.DATABASE_NAME
    connection.creation.create_test_db(verbosity, autoclobber=not interactive)

    # Pretend it's a production environment.
    settings.DEBUG = False

    ret = nose.run(argv=nose_args)

    # Clean up django.
    connection.creation.destroy_test_db(old_db_name, verbosity)
    teardown_test_environment(teardown_funcs)

    return ret

def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    """Calculates nose arguments and runs tests."""
    nose_argv = ['nosetests']
    if hasattr(settings, 'NOSE_ARGS'):
        nose_argv.extend(settings.NOSE_ARGS)

    # Everything after '--' is passed to nose.
    if '--' in sys.argv:
        hyphen_pos = sys.argv.index('--')
        nose_argv.extend(sys.argv[hyphen_pos + 1:])

    if verbosity >= 1:
        print ' '.join(nose_argv)

    return run_tests_explicit(nose_argv, verbosity, interactive)
