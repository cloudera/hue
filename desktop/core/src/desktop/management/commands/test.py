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
from django.core.management.base import BaseCommand
from django_nose import nose_runner

import south.management.commands.syncdb
import sys
import textwrap
import logging

from desktop import appmanager
from desktop.management.commands import test_windmill

class Command(BaseCommand):
  help = textwrap.dedent("""\
    Use the following arguments:

      all        Runs tests for all desktop applications and libraries
                 Additional arguments are passed to nose.

      fast       Runs the "fast" tests, namely those that don't start Hadoop.
              
      specific   Explicitly run specific tests using nose.
                 For example, to run all the filebrower tests or
                 to run a specific test function, use
                    test specific filebrowser
                    test specific useradmin.tests:test_user_admin
                 All additional arguments are passed directly to nose.

      windmill   Runs windmill tests

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
    south.management.commands.syncdb.patch_for_test_db_setup()

    if len(args) == 0:
      print self.help
      sys.exit(1)

    nose_args = None
    all_apps = [ app.module.__name__ for app in appmanager.DESKTOP_MODULES ]

    if args[0] == "all":
      nose_args = args + all_apps + ["-v"]
    elif args[0] == "fast":
      test_apps = [ app.module.__name__ for app in appmanager.DESKTOP_MODULES ]
      nose_args = args + all_apps + ["-v", "-a", "!requires_hadoop"]
    elif args[0] in ("specific", "nose"):
      nose_args = args + ['-v']
    elif args[0] == "windmill":
      args = args[1:]
      ret = test_windmill.Command().handle(*args)
    else:
      print self.help
      sys.exit(1)

    if nose_args:
      ret = nose_runner.run_tests_explicit(nose_args, interactive=True, verbosity=1)

    logging.info("Tests (%s) returned %s" % (' '.join(nose_args), ret))

    if not ret:
      sys.exit(1)
