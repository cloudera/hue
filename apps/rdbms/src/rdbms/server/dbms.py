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

from desktop.lib.i18n import smart_str
from beeswax.models import QueryHistory
from rdbms.conf import RDBMS


LOG = logging.getLogger(__name__)


def force_dict_to_strings(dictionary):
  if not dictionary:
    return dictionary

  new_dict = {}
  for k in dictionary:
    new_key = smart_str(k)
    if isinstance(dictionary[k], basestring):
      # Strings should not be unicode.
      new_dict[new_key] = smart_str(dictionary[k])
    elif isinstance(dictionary[k], dict):
      # Recursively force dicts to strings.
      new_dict[new_key] = force_dict_to_strings(dictionary[k])
    else:
      # Normal objects, or other literals, should not be converted.
      new_dict[new_key] = dictionary[k]

  return new_dict


def get(user, query_server=None):
  if query_server is None:
    query_server = get_query_server_config()

  if query_server['server_name'] == 'mysql':
    from rdbms.server.mysql_lib import MySQLClient

    return Rdbms(MySQLClient(query_server, user), QueryHistory.SERVER_TYPE[2][0])
  elif query_server['server_name'] in ('postgresql', 'postgresql_psycopg2'):
    from rdbms.server.postgresql_lib import PostgreSQLClient

    return Rdbms(PostgreSQLClient(query_server, user), QueryHistory.SERVER_TYPE[2][0])
  elif query_server['server_name'] in ('sqlite', 'sqlite3'):
    from rdbms.server.sqlite_lib import SQLiteClient

    return Rdbms(SQLiteClient(query_server, user), QueryHistory.SERVER_TYPE[2][0])
  elif query_server['server_name'] == 'oracle':
    from rdbms.server.oracle_lib import OracleClient

    return Rdbms(OracleClient(query_server, user), QueryHistory.SERVER_TYPE[2][0])


def get_query_server_config(server=None):
  if not server or server not in RDBMS:
    keys = RDBMS.keys()
    name = keys and keys[0] or None
  else:
    name = server

  if name:
    query_server = {
      'server_name': RDBMS[name].ENGINE.get().split('.')[-1],
      'server_host': RDBMS[name].HOST.get(),
      'server_port': RDBMS[name].PORT.get(),
      'username': RDBMS[name].USER.get(),
      'password': RDBMS[name].PASSWORD.get(),
      'options': force_dict_to_strings(RDBMS[name].OPTIONS.get()),
      'alias': name
    }

    if RDBMS[name].NAME.get():
      query_server['name'] = RDBMS[name].NAME.get()
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

  def get_tables(self, database):
    return self.client.get_tables(database)

  def get_table(self, database, table_name):
    return self.client.get_table(database, table_name)

  def get_columns(self, database, table_name):
    return self.client.get_columns(database, table_name)

  def execute_query(self, query, design):
    sql_query = query.sql_query
    query_history = QueryHistory.build(
      owner=self.client.user,
      query=sql_query,
      server_host='%(server_host)s' % self.client.query_server,
      server_port='%(server_port)d' % self.client.query_server,
      server_name='%(server_name)s' % self.client.query_server,
      server_type=self.server_type,
      last_state=QueryHistory.STATE.available.index,
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
