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
import sys

from desktop.lib.i18n import force_unicode
from desktop.conf import has_channels
from kafka.ksql_client import KSqlApi as KSqlClientApi

from notebook.connectors.base import Api, QueryError

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger()


if has_channels():
  from notebook.consumer import _send_to_channel


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

    self.url = self.options['url']


  def _get_db(self):
    return KSqlClientApi(user=self.user, url=self.url)


  @query_error_handler
  def execute(self, notebook, snippet):
    channel_name = notebook.get('editorWsChannel')

    db = self._get_db()

    data, description = db.query(
        snippet['statement'],
        channel_name=channel_name
    )
    has_result_set = data is not None

    return {
      'sync': not (has_channels() and channel_name),
      'has_result_set': has_result_set,
      'result': {
          'has_more': False,
          'data': data if has_result_set else [],
          'meta': [{
              'name': col['name'],
              'type': col['type'],
              'comment': ''
            }
            for col in description
          ] if has_result_set else [],
        'type': 'table'
      }
    }


  @query_error_handler
  def check_status(self, notebook, snippet):
    return {'status': 'available'}


  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None, operation=None):
    response = {}

    db = self._get_db()

    if database is None:
      response['databases'] = ['tables', 'topics', 'streams']
    elif table is None:
      if database == 'tables':
        response['tables_meta'] = db.show_tables()
      elif database == 'topics':
        response['tables_meta'] = db.show_topics()
      elif database == 'streams':
        response['tables_meta'] = [{
            'name': t['name'],
            'type': t['type'],
            'comment': 'Topic: %(topic)s Format: %(format)s' % t
          }
          for t in db.show_streams()
        ]
    elif column is None:
      columns = db.get_columns(table)
      response['columns'] = [col['name'] for col in columns]
      response['extended_columns'] = [{
          'comment': col.get('comment'),
          'name': col.get('name'),
          'type': str(col['schema'].get('type'))
        }
        for col in columns
      ]

    return response

  @query_error_handler
  def get_sample_data(self, snippet, database=None, table=None, column=None, is_async=False, operation=None):
    notebook = {}

    snippet = {
      'statement': 'PRINT user_behavior FROM BEGINNING LIMIT 10'  # From beginning in case no new data is coming
    }
    sample = self.execute(notebook, snippet)['result']['data']

    # 'result': {'has_more': False, 'data':
    # [
    #    Key format --> JSON or SESSION(KAFKA_STRING) or HOPPING(KAFKA_STRING) or TUMBLING(KAFKA_STRING) or KAFKA_STRING
    #   ['Key format: ¯\\_(ツ)_/¯ - no data processed'],
    #   ['Value format: JSON or KAFKA_STRING']
    #   [
    #     'rowtime: 2020/10/22 05:25:10.639 Z, '
    #     'key: <null>, '
    #     'value: {"user_id": "952483", "item_id":"310884", "category_id": "4580532", "behavior": "pv", "ts": "2017-11-27 00:00:00"}'
    #   ]
    # ]
    # 'meta': [{'name': 'Row', 'type': 'STRING', 'comment': ''}], 'type': 'table'}

    response = {
      'status': 0,
      'result': {}
    }
    print(sample[2:12])
    print(sample[2:12][0])
    print(sample[2:12][0][0].rsplit(', value: ', 1))
    response['rows'] = [
      list(json.loads(row[0].rsplit(', value: ', 1)[1]).values())
      for row in sample[2:12]
    ]

    columns = json.loads(sample[2][0].rsplit(', value: ', 1)[1]).keys()

    response['full_headers'] = [{
        'name': col,
        'type': 'string',
        'comment': ''
      } for col in columns
    ]

    print(response)
    return response

  def fetch_result(self, notebook, snippet, rows, start_over):
    """Only called at the end of a live query."""
    return {
      'has_more': False,
      'data': [],
      'meta': []
    }
