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
from builtins import filter

import logging
import re

from datetime import datetime
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.python_util import current_ms_from_utc

from jobbrowser.apis.base_api import Api
from jobbrowser.models import HiveQuery


LOG = logging.getLogger(__name__)


class HiveQueryApi(Api):

  def __init__(self, user, cluster=None):
    self.user = user
    self.cluster = cluster
    self.api = HiveQueryClient()

  def apps(self, filters):
    queries = self.api.get_queries(limit=100)

    apps = {
      'apps': [{
          'id': query.query_id,
          'name': query.query.replace('\r\n', ' ')[:60] + ('...' if len(query.query) > 60 else ''),
          'status': query.status,
          'apiStatus': self._api_status(query.status),
          'type': 'LLAP' if query.llap_app_id else 'Tez',
          'user': query.request_user,
          'queue': query.queue_name,
          'progress': '100',
          'isRunning': False,
          'canWrite': True,
          'duration': query.elapsed_time,
          'submitted': query.start_time,
        }
        for query in queries
      ],
      'total': self.api.get_query_count()
    }

    return apps

  def app(self, appid):
    query = self.api.get_query(query_id=appid)

    if not query:
      raise PopupException(_('Could not find query id %s' % appid))

    app = {
      'id': query.query_id,
      'name': query.query[:60] + ('...' if len(query.query) > 60 else ''),
      'status': query.status,
      'apiStatus': self._api_status(query.status),
      'type': 'hive-query',
      'user': query.request_user,
      'queue': query.queue_name,
      'progress': '100',
      'isRunning': False,
      'canWrite': True,
      'duration': query.elapsed_time,
      'submitted': query.start_time,
      'properties': {
        'plan': {
          'stmt': query.query,
          'plan': '''Explain
OPTIMIZED SQL: %(text_query)s
STAGE DEPENDENCIES:
Stage-0 is a root stage
STAGE PLANS:
Stage: Stage-0
Fetch Operator
limit: 100
Processor Tree:
TableScan
alias: business_unit
GatherStats: false
Select Operator
expressions: id (type: int), head (type: int), creator (type: string), created_date (type: date)
outputColumnNames: _col0, _col1, _col2, _col3
Limit
Number of rows: 100
ListSink
''' % {'text_query': query.query},
          'perf': ''
        }
      }
    }

    return app

  def action(self, appid, action):
    message = {'message': '', 'status': 0}

    return message;

  def logs(self, appid, app_type, log_name=None, is_embeddable=False):
    return {'logs': ''}

  def profile(self, appid, app_type, app_property, app_filters):
    message = {'message': '', 'status': 0}

    return message;

  def _api_status(self, status):
    if status == 'SUCCESS':
      return 'SUCCEEDED'
    elif status == 'EXCEPTION':
      return 'FAILED'
    elif status == 'RUNNING':
      return 'RUNNING'
    else:
      return 'PAUSED'


class HiveQueryClient():

  def get_query_count(self):
    return HiveQuery.objects.using('query').count()

  def get_queries(self, limit=100):
    return HiveQuery.objects.using('query').order_by('-id')[:limit]

  def get_query(self, query_id):
    return HiveQuery.objects.using('query').get(query_id=query_id)

  def get_query_analysis(self, query_id): pass

  # EXPLAIN with row count
  # CBO COST
  # VECTORIZATION?
