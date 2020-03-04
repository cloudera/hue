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

from __future__ import absolute_import

import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.lib.i18n import force_unicode
from kafka.ksql_client import KSqlApi as KSqlClientApi

from notebook.connectors.base import Api, QueryError


LOG = logging.getLogger(__name__)


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except Exception as e:
      message = force_unicode(str(e))
      raise QueryError(message)
  return decorator


class KSqlApi(Api):

  def __init__(self, user, interpreter=None):
    Api.__init__(self, user, interpreter=interpreter)

    self.options = interpreter['options']

    self.db = KSqlClientApi(user=user, url=self.options['url'])


  @query_error_handler
  def execute(self, notebook, snippet):

    data, description = self.db.query(
        snippet['statement'],
        channel_name=snippet.get('editorWsChannel')
    )
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


  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None):
    response = {}

    try:
      if database is None:
        response['databases'] = ['tables', 'topics', 'streams']
      elif table is None:
        if database == 'tables':
          response['tables_meta'] = self.db.show_tables()
        elif database == 'topics':
          response['tables_meta'] = self.db.show_topics()
        elif database == 'streams':
          response['tables_meta'] = [
            {'name': t['name'], 'type': t['type'], 'comment': 'Topic: %(topic)s Format: %(format)s' % t}
            for t in self.db.show_streams()
          ]
      elif column is None:
        columns = self.db.get_columns(table)
        response['columns'] = [col['name'] for col in columns]
        response['extended_columns'] = [{
            'comment': col.get('comment'),
            'name': col.get('name'),
            'type': str(col['schema'].get('type'))
          } for col in columns
        ]
      else:
        response = {}

    except Exception as e:
      LOG.warn('Autocomplete data fetching error: %s' % e)
      response['code'] = 500
      response['error'] = e.message

    return response
