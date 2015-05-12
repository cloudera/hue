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
    cursor = self.connection.cursor()
    cursor.execute('SELECT schema_name FROM information_schema.schemata')
    self.connection.commit()
    return [row[0] for row in cursor.fetchall()]


  def get_tables(self, database, table_names=[]):
    cursor = self.connection.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='%s'" % database)
    self.connection.commit()
    return [row[0] for row in cursor.fetchall()]


  def get_columns(self, database, table):
    cursor = self.connection.cursor()
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='%s' and table_name='%s'" % (database, table))
    self.connection.commit()
    return [row[0] for row in cursor.fetchall()]
