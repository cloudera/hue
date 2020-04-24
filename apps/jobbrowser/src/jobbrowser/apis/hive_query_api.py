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


LOG = logging.getLogger(__name__)


class HiveQueryApi(Api):

  def __init__(self, user, cluster=None):
    self.user=user
    self.cluster=cluster

  def apps(self, filters):
    jobs = []

    apps = {
      'apps': [],
      'total': 0
    }

    apps['total'] = len(apps['apps'])

    return apps

  def app(self, appid):
    sql_query = 'SELECT * FROM default.business_unit LIMIT 100'

    job = HiveQueryClient().get_query_analysis(sql_query=sql_query)

    if not job:
      raise PopupException(_('Could not find query id %s' % appid))

    app = {
      'id': job['id'],
      'name': sql_query[:60] + ('...' if len(sql_query) > 60 else ''),
      'status': self._get_status(job),
      'apiStatus': self._api_status(self._get_status(job)),
      'type': 'hive-query',
      'user': self.user.username,
      'queue': 'queue',
      'progress': '100',
      'isRunning': False,
      'canWrite': False,
      'duration': 1,
      'submitted': 1,
      'properties': {
        'plan': {
          'stmt': sql_query,
          'plan': '''Explain
OPTIMIZED SQL: SELECT `id`, `head`, `creator`, `created_date`
FROM `default`.`business_unit`
LIMIT 100
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
''', #.replace('\n', ' '),
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

  def _get_status(self, job):
    return 'RUNNING' if job['status'] != 'FINISHED' else "FINISHED"

  def _api_status(self, status):
    if status == 'FINISHED':
      return 'SUCCEEDED'
    elif status == 'EXCEPTION':
      return 'FAILED'
    elif status == 'RUNNING':
      return 'RUNNING'
    else:
      return 'PAUSED'


class HiveQueryClient():

  def get_query_analysis(self, sql_query):
    return {
      'id': 'dev_20200417220345_3cf5e2a4-a3c9-4056-8bf7-76fb8a75f360',
      'queryText': sql_query,
      'status': 'FINISHED'
    }

  # EXPLAIN with row count
  # CBO COST
  # VECTORIZATION?
