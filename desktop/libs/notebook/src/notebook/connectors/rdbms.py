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

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode

from librdbms.server import dbms

from notebook.connectors.base import Api, QueryError, QueryExpired


LOG = logging.getLogger(__name__)


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except Exception, e:
      message = force_unicode(str(e))
      if 'Invalid query handle' in message or 'Invalid OperationHandle' in message:
        raise QueryExpired(e)
      else:
        raise QueryError(message)
  return decorator


class RdbmsApi(Api):

  @query_error_handler
  def execute(self, notebook, snippet):
    query_server = dbms.get_query_server_config(server=self.interpreter)
    db = dbms.get(self.user, query_server)

    db.use(snippet['database']) # TODO: only do the use on the first statement in a multi query
    table = db.execute_statement(snippet['statement'])  # TODO: execute statement stub in Rdbms

    data = list(table.rows())
    has_result_set = data is not None
    print table.columns
    print table.columns_description
    return {
      'sync': True,
      'has_result_set': has_result_set,
      'modified_row_count': 0,
      'result': {
        'has_more': False,
        'data': data if has_result_set else [],
        'meta': [{
          'name': col['name'],
          'type': col.get('type', ''),
          'comment': ''
        } for col in table.columns_description] if has_result_set else [],
        'type': 'table'
      }
    }


  @query_error_handler
  def check_status(self, notebook, snippet):
    return {'status': 'expired'}


  @query_error_handler
  def fetch_result(self, notebook, snippet, rows, start_over):
    return {
      'has_more': False,
      'data': [],
      'meta': [],
      'type': 'table'
    }


  @query_error_handler
  def fetch_result_metadata(self):
    pass


  @query_error_handler
  def cancel(self, notebook, snippet):
    return {'status': 0}


  @query_error_handler
  def get_log(self, notebook, snippet, startFrom=None, size=None):
    return 'No logs'


  def download(self, notebook, snippet, format):
    raise PopupException('Downloading is not supported yet')


  @query_error_handler
  def close_statement(self, snippet):
    return {'status': -1}


  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None):
    query_server = dbms.get_query_server_config(server=self.interpreter)
    db = dbms.get(self.user, query_server)

    assist = Assist(db)
    response = {'status': -1}

    if database is None:
      response['databases'] = assist.get_databases()
    elif table is None:
      tables_meta = []
      for t in assist.get_tables(database):
        tables_meta.append({'name': t, 'type': 'Table', 'comment': ''})
      response['tables_meta'] = tables_meta
    else:
      columns = assist.get_columns(database, table)
      response['columns'] = [col['name'] for col in columns]
      response['extended_columns'] = columns

    response['status'] = 0
    return response


  @query_error_handler
  def get_sample_data(self, snippet, database=None, table=None, column=None):
    query_server = dbms.get_query_server_config(server=self.interpreter)
    db = dbms.get(self.user, query_server)

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

  @query_error_handler
  def get_select_star_query(self, snippet, database, table):
    return "SELECT * FROM `%s`.`%s` LIMIT 1000" % (database, table)


class Assist():

  def __init__(self, db):
    self.db = db

  def get_databases(self):
    return self.db.get_databases()

  def get_tables(self, database, table_names=[]):
    self.db.use(database)
    return self.db.get_tables(database, table_names)

  def get_columns(self, database, table):
    return self.db.get_columns(database, table, names_only=False)

  def get_sample_data(self, database, table, column=None):
    return self.db.get_sample_data(database, table, column)
