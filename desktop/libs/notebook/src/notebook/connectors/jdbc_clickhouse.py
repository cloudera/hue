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

from librdbms.jdbc import query_and_fetch

from notebook.connectors.jdbc import JdbcApi
from notebook.connectors.jdbc import Assist
class JdbcApiClickhouse(JdbcApi):

  def _createAssist(self, db):
    return ClickhouseAssist(db)

class ClickhouseAssist(Assist):

  def get_databases(self):
    dbs, description = query_and_fetch(self.db, 'SHOW DATABASES')
    return [db[0] and db[0].strip() for db in dbs]

  def get_tables_full(self, database, table_names=[]):
    tables, description = query_and_fetch(self.db, "SELECT name, '' FROM system.tables WHERE database='%s'" % database)
    return [{"comment": table[1] and table[1].strip(), "type": "Table", "name": table[0] and table[0].strip()} for table in tables]

  def get_columns_full(self, database, table):
    columns, description = query_and_fetch(self.db, "SELECT name, type, '' FROM system.columns WHERE database='%s' AND table = '%s'" % (database, table))
    return [{"comment": col[2] and col[2].strip(), "type": col[1], "name": col[0] and col[0].strip()} for col in columns]

  def get_sample_data(self, database, table, column=None):
    column = column or '*'
    return query_and_fetch(self.db, 'SELECT %s FROM %s.%s limit 100' % (column, database, table))
