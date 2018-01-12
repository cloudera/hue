"""
Django settings for testing django-nose.

Configuration is overriden by environment variables:

DATABASE_URL - See https://github.com/kennethreitz/dj-database-url
USE_SOUTH - Set to 1 to include South in INSTALLED_APPS
TEST_RUNNER - Dotted path of test runner to use (can also use --test-runner)
NOSE_PLUGINS - Comma-separated list of plugins to add
"""
from __future__ import print_function
from os import environ, path

import dj_database_url

BASE_DIR = path.dirname(path.dirname(__file__))


def rel_path(*subpaths):
    """Construct the full path given a relative path."""
    return path.join(BASE_DIR, *subpaths)


DATABASES = {
    'default':
        dj_database_url.config(
            default='sqlite:///' + rel_path('testapp.sqlite3'))
}

MIDDLEWARE_CLASSES = ()

INSTALLED_APPS = [
    'django_nose',
    'testapp',
]

raw_test_runner = environ.get('TEST_RUNNER')
if raw_test_runner:
    TEST_RUNNER = raw_test_runner
else:
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

raw_plugins = environ.get('NOSE_PLUGINS')
if raw_plugins:
    NOSE_PLUGINS = raw_plugins.split(',')

SECRET_KEY = 'ssshhhh'
