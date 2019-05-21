#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Desktop-aware test runner.

Django's "test" command merely executes the test_runner,
so we circumvent it entirely and create our own.
"""
from django.conf import settings
from django.core.management.base import BaseCommand
from django.test.utils import get_runner
from django_nose import runner

#import south.management.commands
from django.utils import six
from django.utils.translation import deactivate
import sys
import textwrap
import logging

from desktop import appmanager
from desktop.lib import django_mako

if six.PY3:
    from types import SimpleNamespace
else:
    class SimpleNamespace(object):
        pass

class _TestState(object):
    pass


def setup_test_environment(debug=None):
    """
    Perform global pre-test setup, such as installing the instrumented template
    renderer and setting the email backend to the locmem email backend.
    """
    if hasattr(_TestState, 'saved_data'):
        # Executing this function twice would overwrite the saved values.
        raise RuntimeError(
            "setup_test_environment() was already called and can't be called "
            "again without first calling teardown_test_environment()."
        )

    if debug is None:
        debug = settings.DEBUG

    saved_data = SimpleNamespace()
    _TestState.saved_data = saved_data

    saved_data.allowed_hosts = settings.ALLOWED_HOSTS
    # Add the default host of the test client.
    settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver']

    saved_data.debug = settings.DEBUG
    settings.DEBUG = debug

    django_mako.render_to_string = django_mako.render_to_string_test

    deactivate()


def teardown_test_environment():
    """
    Perform any global post-test teardown, such as restoring the original
    template renderer and restoring the email sending functions.
    """
    saved_data = _TestState.saved_data

    settings.ALLOWED_HOSTS = saved_data.allowed_hosts
    settings.DEBUG = saved_data.debug
    django_mako.render_to_string = django_mako.render_to_string_normal

    del _TestState.saved_data


class Command(BaseCommand):
  help = textwrap.dedent("""\
    Use the following arguments:

      all           Runs tests for all desktop applications and libraries
                    Additional arguments are passed to nose.

      fast          Runs the "fast" tests, namely those that don't start Hadoop.

      specific      Explicitly run specific tests using nose.
                    For example, to run all the filebrower tests or
                    to run a specific test function, use
                       test specific filebrowser
                       test specific useradmin.tests:test_user_admin
                    All additional arguments are passed directly to nose.

      windmill      Runs windmill tests

      list_modules  List test modules for all desktop applications and libraries

    Common useful extra arguments for nose:
      --nologcapture
      --nocapture (-s)
      --pdb-failures
      --pdb
      --with-xunit
    """)

  def run_from_argv(self, argv):
    """
    Runs the tests.

    This management command is unusual in that it doesn't
    use Django's normal argument handling.  (If it did, this
    method would be callled handle().)  We do so to more
    easily pass arbitrary arguments to nose.
    """
    args = argv[2:] # First two are "desktop" and "test"

    # Patch South things in
    #south.management.commands.patch_for_test_db_setup()
    #south_logger = logging.getLogger('south')
    #south_logger.setLevel(logging.INFO)

    if len(args) == 0:
      print self.help
      sys.exit(1)

    nose_args = None
    all_apps = [ app.module.__name__ for app in appmanager.DESKTOP_MODULES ]

    if args[0] == "all":
      nose_args = args + all_apps
    elif args[0] == "fast":
      nose_args = args + all_apps + ["-a", "!requires_hadoop"]
    elif args[0] == "unit":
      nose_args = args + all_apps + ["-a", "!integration"]
    elif args[0] == "windmill":
      from desktop.management.commands import test_windmill
      args = args[1:]
      ret = test_windmill.Command().handle(*args)
    elif args[0] in ("specific", "nose"):
      nose_args = args
    elif args[0] == "list_modules":
      print '\n'.join(all_apps)
      sys.exit(0)
    else:
      print self.help
      sys.exit(1)

    if nose_args:
      TestRunner = get_runner(settings)
      test_runner = TestRunner(verbosity=1, interactive=False)
      nose_args.remove(args[0])
      ret = test_runner.run_tests(nose_args)

    logging.info("Tests (%s) returned %s" % (' '.join(nose_args), ret))

    if ret != 0:
      sys.exit(1)
