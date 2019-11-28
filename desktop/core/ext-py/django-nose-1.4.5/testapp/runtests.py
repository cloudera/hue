#!/usr/bin/env python
"""Configure enough Django to run the test suite."""
import sys

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3'}},
        INSTALLED_APPS=['django_nose'],
        MIDDLEWARE_CLASSES=[],
    )


def runtests(*test_labels):
    """Run the selected tests, or all tests if none selected."""
    from django_nose import NoseTestSuiteRunner
    runner = NoseTestSuiteRunner(verbosity=1, interactive=True)
    failures = runner.run_tests(test_labels)
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
