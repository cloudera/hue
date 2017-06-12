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
# limitations under the License.import logging

import logging

from librdbms.server import dbms

from notebook.connectors.base import Api
from notebook.connectors.rdbms import Assist




LOG = logging.getLogger(__name__)

class RdbmsIndexer():

  connect_credentials = {}
  db_name = None

  def __init__(self, connect_credentials, db_name):
    self.connect_credentials = connect_credentials
    self.db_name = db_name

  def guess_type(self):
    type = {}
    return type

  def guess_format(self):
    connect_credentials = {}
    return connect_credentials

  def get_sample_data(self, database=None, table=None, column=None):
    query_server = dbms.get_query_server_config(server=self.interpreter)
    db = dbms.get(self.connect_credentials['user_name'], query_server)

    database = self.db_name
    table = self.connect_credentials['table_name']
    column = self.connect_credentials['column_name']

    assist = Assist(db)
    response = {'status': -1}

    if database is None:
      response['databases'] = assist.get_databases()
    elif table is None:
      tables_meta = []
      for t in assist.get_tables(database):
        tables_meta.append({'name': t, 'type': 'Table', 'comment': ''})
      response['tables_meta'] = tables_meta
    elif column is None:
      columns = assist.get_columns(database, table)
      response['columns'] = [col['name'] for col in columns]
      response['extended_columns'] = columns
    else:
      columns = assist.get_columns(database, table)
      response['name'] = next((col['name'] for col in columns if column == col['name']), '')
      response['type'] = next((col['type'] for col in columns if column == col['name']), '')

    response['status'] = 0

    return response