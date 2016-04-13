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

try:
    import psycopg2 as Database
except ImportError, e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Error loading psycopg2 module: %s" % e)

from librdbms.server.rdbms_base_lib import BaseRDBMSDataTable, BaseRDBMSResult, BaseRDMSClient


LOG = logging.getLogger(__name__)


class DataTable(BaseRDBMSDataTable): pass


class Result(BaseRDBMSResult): pass


class PostgreSQLClient(BaseRDMSClient):
  """Same API as Beeswax"""

  data_table_cls = DataTable
  result_cls = Result

  def __init__(self, *args, **kwargs):
    super(PostgreSQLClient, self).__init__(*args, **kwargs)
    self.connection = Database.connect(**self._conn_params)


  @property
  def _conn_params(self):
    params = {
      'user': self.query_server['username'],
      'password': self.query_server['password'],
      'host': self.query_server['server_host'],
      'port': self.query_server['server_port'] == 0 and 5432 or self.query_server['server_port'],
      'database': self.query_server['name']
    }

    if self.query_server['options']:
      params.update(self.query_server['options'])
      # handle transaction commits manually.
      if 'autocommit' in params:
        del params['autocommit']

    return params


  def use(self, database):
    # No op since postgresql requires a new connection per database
    pass


  def execute_statement(self, statement):
    cursor = self.connection.cursor()
    cursor.execute(statement)
    self.connection.commit()
    if cursor.description:
      columns = [column[0] for column in cursor.description]
    else:
      columns = []
    return self.data_table_cls(cursor, columns)


  def get_databases(self):
    # List all the schemas in the database
    try:
      cursor = self.connection.cursor()
      cursor.execute('SELECT nspname from pg_catalog.pg_namespace')
      self.connection.commit()
      return [row[0] for row in cursor.fetchall()]
    except Exception:
      LOG.exception('Failed to select nspname from pg_catalog.pg_namespace')
      return [self._conn_params['database']]


  def get_tables(self, database, table_names=[]):
    cursor = self.connection.cursor()
    query = "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = '%s'" % database
    if table_names:
      clause = ' OR '.join(["tablename LIKE '%%%(table)s%%'" % {'table': table} for table in table_names])
      query += ' AND (%s)' % clause
    cursor.execute(query)
    self.connection.commit()
    return [row[0] for row in cursor.fetchall()]


  def get_columns(self, database, table, names_only=True):
    cursor = self.connection.cursor()
    query = """
      SELECT
          a.attname as "name",
          pg_catalog.format_type(a.atttypid, a.atttypmod) as "datatype"
      FROM
          pg_catalog.pg_attribute a
      WHERE
          a.attnum > 0
          AND NOT a.attisdropped
          AND a.attrelid = (
              SELECT c.oid
              FROM pg_catalog.pg_class c
                  LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
              WHERE c.relname ~ '^(%(table)s)$'
                  AND n.nspname = '%(database)s'
                  AND pg_catalog.pg_table_is_visible(c.oid)
          )
    """ % {'table': table, 'database': database}

    cursor.execute(query)
    self.connection.commit()
    if names_only:
      columns = [row[0] for row in cursor.fetchall()]
    else:
      columns = [dict(name=row[0], type=row[1], comment='') for row in cursor.fetchall()]
    return columns

  def get_sample_data(self, database, table, column=None, limit=100):
    column = '"%s"' % column if column else '*'
    statement = 'SELECT %s FROM "%s"."%s" LIMIT %d' % (column, database, table, limit)
    return self.execute_statement(statement)
