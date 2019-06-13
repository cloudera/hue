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
Django management command that invokes windmill tests,
after appropriate setup.
"""
import sys
import time
from optparse import make_option

from windmill.authoring import djangotest

from django.core.management.base import BaseCommand

import logging

LOG = logging.getLogger(__name__)

DEFAULT_PORT=8999

class ServerContainer(object):
  """
  This monkey-patch of djangotest's ServerContainer allows a custom port number.
  """
  port = DEFAULT_PORT

  def start_test_server(self):
    djangotest.start_test_server(self, "127.0.0.1", self.port)

  stop_test_server = djangotest.stop_test_server

class Command(BaseCommand):
  """Runs windmill tests."""

  def add_arguments(self, parser):
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, dest='port',
        help='Port number to use for server.')

  def setup_test_db(self):
    """
    Windmill only sets up the db if it's in-memory, but it ought to do it always.
    We have to adapt a bit for South as well.
    """
    # South:
    import south.management.commands
    south.management.commands.patch_for_test_db_setup()

    # Create the test database
    from django.db import connection
    connection.creation.create_test_db(0)

  def start_helper_servers(self):
    """
    Starts Hadoop daemons.

    This currently doesn't start app-specific
    other servers.
    """
    pass

  def stop_helper_servers(self):
    self.cluster.shutdown()

  def handle(self, *args, **options):
    """
    This is a rewrite of windmill.management.commands.test_windmill
    that uses nose instead of functest.
    """
    from windmill.bin import admin_lib
    from windmill.conf import global_settings
    import nose

    self.port = options['port']

    # Setup DB
    self.setup_test_db()

    # Start a servers (django web server & Hadoop)
    server_container = ServerContainer()
    server_container.start_test_server()
    LOG.info("Server running on %d" % server_container.server_thread.port)
    self.start_helper_servers()


    # Configure windmill
    global_settings.TEST_URL = 'http://127.0.0.1:%d' % server_container.server_thread.port
    # For now, we only handle Firefox.
    global_settings.START_FIREFOX = True
    admin_lib.configure_global_settings(logging_on=False)

    # Start windmill proxy server
    windmill_obj = admin_lib.setup()

    # Run tests with nose
    nose_args = self.find_modules()
    LOG.info("Testing modules: " + repr(nose_args))
    if "--" in sys.argv:
      nose_args.extend(sys.argv[sys.argv.index("--") + 1:])
    res = nose.run(argv=nose_args)

    # Stop servers
    self.stop_helper_servers()
    server_container.stop_test_server()

    # Stop windmill
    admin_lib.teardown(windmill_obj)
    time.sleep(0.25)

    if res:
      sys.exit(0)
    else:
      sys.exit(1)

  def find_modules(self):
    """Find modules ending in windmilltests within installed apps."""
    import django.conf
    names = []
    for app in django.conf.settings.INSTALLED_APPS:
      name = app + "." + "windmilltests"
      try:
        __import__(name)
        names.append(name)
      except ImportError:
        pass
    return names
