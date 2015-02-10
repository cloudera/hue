"""
Add extra options from the test runner to the ``test`` command, so that you can
browse all the nose options from the command line.
"""
from django.conf import settings
from django.test.utils import get_runner


if 'south' in settings.INSTALLED_APPS:
    from south.management.commands.test import Command
else:
    from django.core.management.commands.test import Command


# Django < 1.2 compatibility
test_runner = settings.TEST_RUNNER
if test_runner.endswith('run_tests') or test_runner.endswith('run_gis_tests'):
    import warnings
    warnings.warn(
        'Use `django_nose.NoseTestSuiteRunner` instead of `%s`' % test_runner,
        DeprecationWarning)


TestRunner = get_runner(settings)

if hasattr(TestRunner, 'options'):
    extra_options = TestRunner.options
else:
    extra_options = []


class Command(Command):
    option_list = Command.option_list + tuple(extra_options)
