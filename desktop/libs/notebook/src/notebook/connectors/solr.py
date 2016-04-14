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

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode

from libsolr.api import SolrApi as NativeSolrApi

from notebook.connectors.base import Api, QueryError
from notebook.models import escape_rows


LOG = logging.getLogger(__name__)


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except Exception, e:
      message = force_unicode(str(e))
      raise QueryError(message)
  return decorator


class SolrApi(Api):

  def __init__(self, user, interpreter=None):
    Api.__init__(self, user, interpreter=interpreter)
    self.options = interpreter['options']

  @query_error_handler
  def execute(self, notebook, snippet):
    from search.conf import SOLR_URL

    api = NativeSolrApi(SOLR_URL.get(), self.user.username)

    collection = self.options.get('collection') or snippet.get('database')
    if not collection or collection == 'default':
      collection = api.collections2()[0]

    response = api.sql(collection, snippet['statement'])

    info = response['result-set']['docs'].pop(-1) # EOF, RESPONSE_TIME, EXCEPTION
    if info.get('EXCEPTION'):
      raise QueryError(info['EXCEPTION'])

    headers = []
    for row in response['result-set']['docs']:
      for col in row.keys():
        if col not in headers:
          headers.append(col)

    data = [[doc.get(col) for col in headers] for doc in response['result-set']['docs']]
    has_result_set = bool(data)

    return {
      'sync': True,
      'has_result_set': has_result_set,
      'modified_row_count': 0,
      'result': {
        'has_more': False,
        'data': data if has_result_set else [],
        'meta': [{
          'name': col,
          'type': '',
          'comment': ''
        } for col in headers] if has_result_set else [],
        'type': 'table'
      },
      'statement_id': 0,
      'has_more_statements': False,
      'statements_count': 1
    }


  @query_error_handler
  def check_status(self, notebook, snippet):
    return {'status': 'available'}


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
    from search.conf import SOLR_URL
    api = NativeSolrApi(SOLR_URL.get(), self.user.username)
    assist = Assist(self, self.user, api)
    response = {'status': -1}

    if database is None:
      response['databases'] = [self.options.get('collection') or snippet.get('database') or 'default']
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
    from search.conf import SOLR_URL
    db = NativeSolrApi(SOLR_URL.get(), self.user)

    assist = Assist(self, self.user, db)
    response = {'status': -1}

    sample_data = assist.get_sample_data(database, table, column)

    if sample_data:
      response['status'] = 0
      response['headers'] = sample_data['headers']
      response['rows'] = sample_data['rows']
    else:
      response['message'] = _('Failed to get sample data.')

    return response


class Assist():

  def __init__(self, api, user, db):
    self.api = api
    self.user = user
    self.db = db

  def get_databases(self):
    return self.options['collection'].get('collection') or ['default']

  def get_tables(self, database, table_names=[]):
    return self.db.collections2()

  def get_columns(self, database, table):
    return [{'name': field['name'], 'type': field['type'], 'comment': ''} for field in self.db.schema_fields(table)['fields']]

  def get_sample_data(self, database, table, column=None):
    if column is None:
      column = ', '.join([col['name'] for col in self.get_columns(database, table)])

    snippet = {
        'database': table,
        'statement': 'SELECT %s FROM %s LIMIT 250' % (column, table)
    }
    res = self.api.execute(None, snippet)

    response = {'status': -1}

    if res:
      response['status'] = 0
      response['headers'] = [col['name'] for col in res['result']['meta']]
      response['rows'] = escape_rows(res['result']['data'], nulls_only=True)
    else:
      response['message'] = _('Failed to get sample data.')

    return response