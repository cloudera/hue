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

class JdbcApiAthena(JdbcApi):

  def _createAssist(self, db):
    return AthenaAssist(db)

class AthenaAssist(Assist):

  def get_tables_full(self, database, table_names=[]):
    tables, description = query_and_fetch(self.db, "SELECT TABLE_NAME, null AS TABLE_COMMENT FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='%s'" % database)
    return [{"comment": table[1] and table[1].strip(), "type": "Table", "name": table[0] and table[0].strip()} for table in tables]

  def get_columns_full(self, database, table):
    columns, description = query_and_fetch(self.db, "SELECT COLUMN_NAME, DATA_TYPE, COMMENT AS COLUMN_COMMENT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='%s' AND TABLE_NAME='%s'" % (database, table))
    return [{"comment": col[2] and col[2].strip(), "type": col[1], "name": col[0] and col[0].strip()} for col in columns]
