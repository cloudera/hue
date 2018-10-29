
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

from django.core.management.base import BaseCommand
from django.core.exceptions import ImproperlyConfigured
from django.db import connections
from django.db.utils import OperationalError


LOG = logging.getLogger(__name__)


class Command(BaseCommand):

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

  def handle(self, *args, **options):
    self.stdout.write('Going to test accessing the database')

    try:
      db_conn = connections['default']
      db_conn.cursor()
    except ImproperlyConfigured, e:
      self.stderr.write('DB improperly configured: %s' % e)
      sys.exit(10)
    except OperationalError, e:
      self.stderr.write('Error accessing DB: %s' % e)
      error = str(e)

      # MySql
      if '2005' in error: # "Unknown MySQL server host 'laaaocalhost' (111)"
        sys.exit(5)
      elif '2002' in error: # Can't connect to local MySQL server through socket '/var/run/mysqld/mysqld.sock' (2)
        sys.exit(6)
      elif '1049' in error: # "Unknown database 'huea'"
        sys.exit(7)
      elif '1045' in error: # "Access denied for user 'root'@'localhost' (using password: YES)"
        sys.exit(8)
      else: # Any connection error that we can't make sense of
        sys.exit(4)
    except Exception, e:
      self.stderr.write('Error accessing DB: %s' % e)
      error = str(e)

      # Oracle
      # Note: we catch missing Oracle_cx module in manage_entry.py
      if 'ORA-12545' in error: # Connect failed because target host or object does not exist
        sys.exit(5)
      elif 'ORA-12541' in error: # TNS:no listener
        sys.exit(6)
      elif 'ORA-12505' in error: # TNS:listener does not currently know of SID given in connect descriptor
        sys.exit(7)
      elif 'ORA-01017' in error: # invalid username/password; logon denied
        sys.exit(8)
      elif 'ORA' in error: # Any connection error that we can't make sense of
        sys.exit(4)
      # PostGreSQL
      elif 'could not translate host name' in error: # could not translate host name "alocalhost" to address: Name or service not known
        sys.exit(5)
      elif 'could not connect to server' in error: # could not connect to server: Connection refused Is the server running on host "localhost" (127.0.0.1) and accepting TCP/IP connections on port 5432?
        sys.exit(6)
      elif 'does not exist' in error: # FATAL:  database "DB_NAMEaa" does not exist
        sys.exit(7)
      elif 'password authentication failed' in error: # password authentication failed for user "root"
        sys.exit(8)
      elif 'FATAL' in error:
        sys.exit(4)

      sys.exit(1)

    self.stdout.write('Database was accessed successfully')
