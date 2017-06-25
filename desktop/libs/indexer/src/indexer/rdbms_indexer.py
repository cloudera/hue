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
# limitations under the License.import logging

import logging

from librdbms.server import dbms
from notebook.connectors.rdbms import Assist


LOG = logging.getLogger(__name__)


class RdbmsIndexer():

  def __init__(self, user, db_conf_name):
    self.user = user
    self.db_conf_name = db_conf_name

  def guess_type(self):
    return {}

  def guess_format(self):
    return {}

  def get_sample_data(self, database=None, table=None, column=None):
    query_server = dbms.get_query_server_config(server=self.db_conf_name)
    db = dbms.get(self.user, query_server=query_server)

    assist = Assist(db)
    response = {'status': -1}
    sample_data = assist.get_sample_data(database, table, column)

    if sample_data:
      response['status'] = 0
      response['headers'] = sample_data.columns
      response['rows'] = list(sample_data.rows())
    else:
      response['message'] = _('Failed to get sample data.')

    return response

  def get_databases(self):
    query_server = dbms.get_query_server_config(server=self.db_conf_name)
    db = dbms.get(self.user, query_server=query_server)
    assist = Assist(db)
    response = {'status': -1}
    sample_data = assist.get_databases()

    if sample_data:
      response['status'] = 0
      response['data'] = sample_data
    else:
      response['message'] = _('Failed to get sample data.')

    return response

  def get_tables(self, database=None):
    query_server = dbms.get_query_server_config(server=self.db_conf_name)
    db = dbms.get(self.user, query_server=query_server)
    assist = Assist(db)
    response = {'status': -1}
    sample_data = assist.get_tables(database)

    if sample_data:
      response['status'] = 0
      response['data'] = sample_data
    else:
      response['message'] = _('Failed to get sample data.')

    return response

  def get_columns(self, database=None, table=None):
    query_server = dbms.get_query_server_config(server=self.db_conf_name)
    db = dbms.get(self.user, query_server=query_server)

    assist = Assist(db)
    response = {'status': -1}
    sample_data = assist.get_columns(database, table)

    if sample_data:
      response = sample_data
    else:
      response['message'] = _('Failed to get sample data.')

    return response