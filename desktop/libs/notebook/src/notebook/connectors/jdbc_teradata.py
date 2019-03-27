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


class JdbcApiTeradata(JdbcApi):

  def _createAssist(self, db):
    return TeradataAssist(db)


class TeradataAssist(Assist):

  def get_databases(self):
    dbs, description = query_and_fetch(self.db, 'SELECT DatabaseName FROM DBC.Databases ORDER BY DatabaseName')
    return [db[0] and db[0].strip() for db in dbs]

  def get_tables_full(self, database, table_names=[]):
    tables, description = query_and_fetch(self.db, "SELECT TableName, CommentString FROM dbc.tables WHERE tablekind = 'T' and databasename='%s' ORDER BY TableName" % database)
    return [{"comment": table[1] and table[1].strip(), "type": "Table", "name": table[0] and table[0].strip()} for table in tables]

  def get_columns_full(self, database, table):
    columns, description = query_and_fetch(self.db, "SELECT ColumnName, ColumnType, CommentString FROM DBC.Columns WHERE DatabaseName='%s' AND TableName='%s' ORDER BY ColumnName" % (database, table))
    return [{"comment": col[1] and col[1].strip(), "type": self._type_converter(col[1]), "name": col[0] and col[0].strip()} for col in columns]

  def get_sample_data(self, database, table, column=None):
    column = column or '*'
    return query_and_fetch(self.db, 'SELECT %s FROM %s.%s sample 100' % (column, database, table))

  def _type_converter(self, name):
    return {
        "I": "INT_TYPE",
        "I2": "SMALLINT_TYPE",
        "CF": "STRING_TYPE",
        "CV": "CHAR_TYPE",
        "DA": "DATE_TYPE",
      }.get(name, 'STRING_TYPE')
