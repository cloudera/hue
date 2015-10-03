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
from librdbms.jdbc import Jdbc, query_and_fetch

from notebook.connectors.base import Api, QueryError


LOG = logging.getLogger(__name__)


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except Exception, e:
      message = force_unicode(str(e))
      if 'error occurred while trying to connect to the Java server' in message:
        raise QueryError(_('%s: is the DB Proxy server running?') % message)
      else:
        raise QueryError(message)
  return decorator


class JdbcApi(Api):

  def __init__(self, user, fs=None, jt=None, options=None):
    Api.__init__(self, user, fs=fs, jt=jt, options=options)

    self.db = Jdbc(self.options['driver'], self.options['url'], self.options['user'], self.options['password'])

  @query_error_handler
  def execute(self, notebook, snippet):
    data, description = query_and_fetch(self.db, snippet['statement'], 100)
    has_result_set = data is not None

    return {
      'sync': True,
      'has_result_set': has_result_set,
      'result': {
        'has_more': False,
        'data': data if has_result_set else [],
        'meta': [{
          'name': col[0],
          'type': col[1],
          'comment': ''
        } for col in description] if has_result_set else [],
        'type': 'table'
      }
    }

  @query_error_handler
  def check_status(self, notebook, snippet):
    return {'status': 'available'}

  def _fetch_result(self, cursor):
    return {}

  @query_error_handler
  def fetch_result_metadata(self):
    pass

  @query_error_handler
  def cancel(self, notebook, snippet):
    return {'status': 0}

  def download(self, notebook, snippet, format):
    raise PopupException('Downloading is not supported yet')

  def progress(self, snippet, logs):
    return 50

  @query_error_handler
  def close_statement(self, snippet):
    return {'status': -1}

  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None):
    assist = Assist(self.db)
    response = {'error': 0}

    try:
      if database is None:
        response['databases'] = assist.get_databases()
      elif table is None:
        response['tables'] = assist.get_tables(database)
      else:
        columns = assist.get_columns(database, table)
        response['columns'] = [col[0] for col in columns]
        response['extended_columns'] = [{
            'name': col[0],
            'type': col[1],
            'comment': col[5]
          } for col in columns
        ]
    except Exception, e:
      LOG.warn('Autocomplete data fetching error: %s' % e)
      response['code'] = -1
      response['error'] = e.message

    return response


class Assist():

  def __init__(self, db):
    self.db = db

  def get_databases(self):
    databases, description = query_and_fetch(self.db, 'SHOW DATABASES')
    return databases

  def get_tables(self, database, table_names=[]):
    tables, description = query_and_fetch(self.db, 'SHOW TABLES')
    return tables

  def get_columns(self, database, table):
    columns, description = query_and_fetch(self.db, 'SHOW COLUMNS FROM %s.%s' % (database, table))
    return columns
