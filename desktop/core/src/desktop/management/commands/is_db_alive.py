
# adapted from django-extensions (http://code.google.com/p/django-command-extensions/)
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

import logging
import sys

from django.core.management.base import NoArgsCommand
from django.db import connections


LOG = logging.getLogger(__name__)


class Command(NoArgsCommand):

  help = """Check if Hue can is configured properly to use its database.

  sqlite
  DESKTOP_DB_CONFIG='django.db.backends.sqlite3:/DB/PATH:::::' ./build/env/bin/hue is_db_alive

  mysql
  DESKTOP_DB_CONFIG='django.db.backends.mysql:DB_NAME::root:root:localhost' ./build/env/bin/hue is_db_alive

  postgresql
  DESKTOP_DB_CONFIG='django.db.backends.postgresql_psycopg2:DB_NAME::root:root:localhost' ./build/env/bin/hue is_db_alive

  oracle
  DESKTOP_DB_CONFIG='django.db.backends.oracle:ORCL::root:password:oracle.hue.com:1521' ./build/env/bin/hue is_db_alive
  or
  DESKTOP_DB_CONFIG='django.db.backends.oracle:oracle.hue.com#1521/ORCL::root:password::' ./build/env/bin/hue is_db_alive

  Note:
  To switch to a non default port, append the port
  localhost --> localhost:3306


  Return non zero in case of failure

  e.g.
  $ DESKTOP_DB_CONFIG='django.db.backends.mysql:DB_NAME::root:root:localhost' ./build/env/bin/hue is_db_alive
    Going to test accessing the database
    Error accessing DB: (1049, "Unknown database 'DB_NAME'")

  $ DESKTOP_DB_CONFIG='django.db.backends.mysql:hue::root:root:localhost' ./build/env/bin/hue is_db_alive
    Going to test accessing the database
    Database was accessed successfully

  The command directly replace the database parameters in the settings.py, to never use the defaut Hue settings.
  """

  def handle_noargs(self, **options):
    self.stdout.write('Going to test accessing the database')

    try:
      db_conn = connections['default']
      db_conn.cursor()
    except Exception, e:
      self.stdout.write('Error accessing DB: %s' % e)
      sys.exit(-1)

    self.stdout.write('Database was accessed successfully')
