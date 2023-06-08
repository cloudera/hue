#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from __future__ import absolute_import

import logging
import json
import os
import sys

import sqlflow
from sqlflow.rows import Rows

from desktop.lib.i18n import force_unicode

from notebook.connectors.base import Api, QueryError
from notebook.decorators import ssh_error_handler, rewrite_ssh_api_url
from notebook.models import escape_rows

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger()


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except Exception as e:
      message = force_unicode(str(e))
      raise QueryError(message)
  return decorator


class SqlFlowApi(Api):

  def __init__(self, user, interpreter=None):
    Api.__init__(self, user, interpreter=interpreter)

    self.options = interpreter['options']
    self.url = self.options['url']

    if self.options.get('has_ssh'):
      self.url = rewrite_ssh_api_url(self.url)['url']


  def _get_db(self):
    os.environ['SQLFLOW_DATASOURCE'] = self.interpreter['options']['datasource']
    return sqlflow.Client(server_url='172.18.1.3:50051')  # TODO Send as param instead of ENV


  @query_error_handler
  @ssh_error_handler
  def execute(self, notebook, snippet):
    db = self._get_db()

    statement = snippet['statement']
    statement = statement.replace('LIMIT 5000', '')

    result = self._execute(statement)

    has_result_set = len(result['data']) > 0

    return {
      'sync': True,
      'has_result_set': has_result_set,
      'result': {
          'has_more': False,
          'data': result['data'] if has_result_set else [],
          'meta': [{
              'name': col[0],
              'type': col[1],
              'comment': col[2]
            }
            for col in result['description']
          ]
          if has_result_set else [],
        'type': 'table'
      }
    }


  def _execute(self, statement):
    db = self._get_db()

    compound_message = db.execute(statement)

    data = []
    description = []

    if compound_message:
      for r in compound_message._messages:
        if isinstance(r[0], Rows):
          description = [(c, '', '') for c in r[0].column_names()]
          data.extend([r for r in r[0].rows()])
        else:
          description = ['']
          data.extend([r for r in r[0].rows()])
    else:
      # Need to grab from sqlflow.client logs
      pass

    return {
      'data': data,
      'description': description,
    }


  @query_error_handler
  def check_status(self, notebook, snippet):
    return {'status': 'available'}


  @query_error_handler
  @ssh_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None, operation=None):
    response = {}

    if database is None:
      response['databases'] = self._execute('SHOW DATABASES')['data']
    elif table is None:
      response['tables_meta'] = [
        {'name': t[0], 'type': '', 'comment': ''}
        for t in self._execute('SHOW TABLES in %s' % database)['data']
      ]
    elif column is None:
      columns = self._execute('DESCRIBE %s.%s' % (database, table))['data']
      response['columns'] = [col[0] for col in columns]
      response['extended_columns'] = [{
          'comment': col[2],
          'name': col[0],
          'type': col[1]
        }
        for col in columns
      ]

    return response

  @query_error_handler
  def get_sample_data(self, snippet, database=None, table=None, column=None, is_async=False, operation=None):
    result = self._execute('SELECT * FROM %s.%s LIMIT 10' % (database, table))

    response = {
      'status': 0,
    }

    response['rows'] = escape_rows(result['data'])

    response['full_headers'] = [{
        'name': col,
        'type': 'STRING_TYPE',
        'comment': ''
      }
      for col in result['description']
    ]

    return response


  def fetch_result(self, notebook, snippet, rows, start_over):
    """Only called at the end of a live query."""
    return {
      'has_more': False,
      'data': [],
      'meta': []
    }
