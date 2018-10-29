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

from librdbms.design import SQLdesign


LOG = logging.getLogger(__name__)


class BaseRDBMSDataTable(object):
  def __init__(self, cursor, columns, fetch_size=1000):
    self.cursor = cursor
    if columns and isinstance(columns[0], dict): # Backward compatible for API without column metadata
      self.columns_description = columns
      self.columns = [col['name'] for col in columns]
    else:
      self.columns_description = [{'name': col} for col in columns]
      self.columns = columns
    self.next = None
    self.startRowOffset = 0
    self.fetchSize = 1000

  @property
  def ready(self):
    return True

  @property
  def has_more(self):
    if not self.next:
      self.next = list(self.cursor.fetchmany(self.fetchSize))
    return bool(self.next)

  def cols(self):
    return self.columns

  def rows(self):
    while self.has_more:
      yield self.next.pop(0)



class BaseRDBMSResult(object):
  def __init__(self, data_table):
    self.data_table = data_table
    self.rows = data_table.rows
    self.has_more = data_table.has_more
    self.start_row = data_table.startRowOffset
    self.columns = data_table.columns
    self.ready = True


class BaseRDMSClient(object):
  """Same API as Beeswax"""

  data_table_cls = None
  result_cls = None

  def __init__(self, query_server, user):
    self.user = user
    self.query_server = query_server


  def create_result(self, datatable):
    return self.result_cls(datatable)


  def query(self, query, statement=0):
    return self.execute_statement(query.get_query_statement(statement))


  def explain(self, query):
    if isinstance(query, SQLdesign):
      # Backward compatibility with rdbms app
      q = query.get_query_statement(0)
    else:
      q = query

    if q.upper().startswith('EXPLAIN'):
      return self.execute_statement(q)
    else:
      return self.execute_statement('EXPLAIN ' + q)
