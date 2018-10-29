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

import logging

from desktop.lib.python_util import force_dict_to_strings

from librdbms.conf import DATABASES, get_database_password


LOG = logging.getLogger(__name__)

MYSQL = 'mysql'
POSTGRESQL = 'postgresql'
SQLITE = 'sqlite'
ORACLE = 'oracle'


def get(user, query_server=None):
  if query_server is None:
    query_server = get_query_server_config()

  if query_server['server_name'] == 'mysql':
    from librdbms.server.mysql_lib import MySQLClient

    return Rdbms(MySQLClient(query_server, user), MYSQL)
  elif query_server['server_name'] in ('postgresql', 'postgresql_psycopg2'):
    from librdbms.server.postgresql_lib import PostgreSQLClient

    return Rdbms(PostgreSQLClient(query_server, user), POSTGRESQL)
  elif query_server['server_name'] in ('sqlite', 'sqlite3'):
    from librdbms.server.sqlite_lib import SQLiteClient

    return Rdbms(SQLiteClient(query_server, user), SQLITE)
  elif query_server['server_name'] == 'oracle':
    from librdbms.server.oracle_lib import OracleClient

    return Rdbms(OracleClient(query_server, user), ORACLE)


def get_query_server_config(server=None):
  if not server or server not in DATABASES:
    keys = DATABASES.keys()
    name = keys and keys[0] or None
  else:
    name = server

  if name:
    query_server = {
      'server_name': DATABASES[name].ENGINE.get().split('.')[-1],
      'server_host': DATABASES[name].HOST.get(),
      'server_port': DATABASES[name].PORT.get(),
      'username': DATABASES[name].USER.get(),
      'password': get_database_password(name),
      'options': force_dict_to_strings(DATABASES[name].OPTIONS.get()),
      'alias': name
    }

    if DATABASES[name].NAME.get():
      query_server['name'] = DATABASES[name].NAME.get()
  else:
    query_server = {}

  LOG.debug("Query Server: %s" % query_server)

  return query_server


class Rdbms(object):
  def __init__(self, client, server_type):
    self.client = client
    self.server_type = server_type

  def get_databases(self):
    return self.client.get_databases()

  def get_tables(self, database, table_names=None):
    return self.client.get_tables(database)

  def get_table(self, database, table_name):
    return self.client.get_table(database, table_name)

  def get_columns(self, database, table_name, names_only=True):
    return self.client.get_columns(database, table_name, names_only)

  def get_sample_data(self, database, table_name, column=None, limit=100):
    return self.client.get_sample_data(database, table_name, column, limit)

  def execute_statement(self, statement):
    return self.client.execute_statement(statement)

  def execute_query(self, query, design):
    from beeswax.models import QueryHistory

    sql_query = query.sql_query
    query_history = QueryHistory.build(
      owner=self.client.user,
      query=sql_query,
      server_host='%(server_host)s' % self.client.query_server,
      server_port='%(server_port)d' % self.client.query_server,
      server_name='%(server_name)s' % self.client.query_server,
      server_type=self.server_type,
      last_state=QueryHistory.STATE.available.value,
      design=design,
      notify=False,
      query_type=query.query['type'],
      statement_number=0
    )
    query_history.save()

    LOG.debug("Updated QueryHistory id %s user %s statement_number: %s" % (query_history.id, self.client.user, query_history.statement_number))

    return query_history

  def explain(self, statement):
    return self.client.explain(statement)

  def use(self, database):
    self.client.use(database)

  def execute_and_wait(self, query, timeout_sec=30.0):
    """
    Run query

    Simply run query irrespective of timeout.
    Timeout exists to comply with interface.
    """

    return self.client.query(query)
