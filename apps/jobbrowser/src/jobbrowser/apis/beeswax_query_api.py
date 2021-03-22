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
import sys

from datetime import datetime

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.python_util import current_ms_from_utc

from jobbrowser.apis.base_api import Api

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _

LOG = logging.getLogger(__name__)

try:
  from beeswax import query_history
except Exception as e:
  LOG.exception('Some application are not enabled: %s' % e)


class BeeswaxQueryApi(Api):

  def __init__(self, user, cluster=None):
    self.user=user
    self.cluster=cluster

  def apps(self, filters):
    filter_map = self._get_filter_map(filters)
    limit = filters.get('pagination', {'limit': 25}).get('limit')
    jobs = query_history.get_query_history(request_user=filter_map.get('effective_user'), start_date=filter_map.get('date'), start_time=filter_map.get('time'), query_id=filter_map.get('query_id'), status=filter_map.get('status'), limit=limit)

    current_time = current_ms_from_utc()
    apps = {
      'apps': [{
        'id': job[0],
        'name': job[5]['queryText'].replace('\r\n', ' ')[:60] + ('...' if len(job[5]) > 60 else '') if job[5] else '',
        'status': self._get_status(job),
        'apiStatus': self._api_status(self._get_status(job)),
        'type': job[2],
        'user': job[3],
        'queue': job[4],
        'progress': '100' if len(job[1]) >= 2 else '',
        'isRunning': len(job[1]) <= 1,
        'canWrite': False,
        'duration': job[1][-1] - job[1][0] if len(job[1]) > 1 else max(current_time - job[1][0], 0),
        'submitted': job[1][0],
        # Extra specific
        'rows_fetched': 0,
        'waiting': '',
        'waiting_time': 0,
        'properties': {
        'plan': {
            'stmt': job[5]['queryText'] if job[5] else '',
            'plan': job[5]['queryPlan'] if job[5] else '',
            'perf': job[6]
          }
        }
      } for job in jobs['data']],
      'total': 0
    }

    apps['total'] = len(apps['apps'])

    return apps

  def app(self, appid):
    jobs = query_history.get_query_by_id(self.user.get_username(), query_id=appid)

    current_time = current_ms_from_utc()
    if not jobs['data']:
      raise PopupException(_('Could not find query id %s' % appid))
    job = jobs['data'][0]
    app = {
      'id': job[0],
      'name': job[5]['queryText'].replace('\r\n', ' ')[:60] + ('...' if len(job[5]) > 60 else '') if job[5] else '',
      'status': self._get_status(job),
      'apiStatus': self._api_status(self._get_status(job)),
      'type': job[2],
      'user': job[3],
      'queue': job[4],
      'progress': '100' if len(job[1]) >= 2 else '',
      'isRunning': len(job[1]) <= 1,
      'canWrite': False,
      'duration': job[1][-1] - job[1][0] if len(job[1]) > 1 else max(current_time - job[1][0], 0),
      'submitted': job[1][0],
      # Extra specific
      'rows_fetched': 0,
      'waiting': '',
      'waiting_time': 0,
      'properties': {
        'plan': {
          'stmt': job[5]['queryText'] if job[5] else '',
          'plan': job[5]['queryPlan'] if job[5] else '',
          'perf': job[6]
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

  def profile_encoded(self, appid):
    message = {'message': '', 'status': 0}

    return message;

  def _get_status(self, job):
    return 'RUNNING' if len(job[1]) <= 1 else "FINISHED"

  def _api_status(self, status):
    if status == 'FINISHED':
      return 'SUCCEEDED'
    elif status == 'EXCEPTION':
      return 'FAILED'
    elif status == 'RUNNING':
      return 'RUNNING'
    else:
      return 'PAUSED'

  def _get_filter_map(self, filters):
    filter_map = {}
    if filters.get("text"):
      filter_names = {
        'user':'effective_user',
        'id':'query_id',
        'name':'state',
        'type':'stmt_type',
        'status':'status'
      }

      def make_lambda(name, value):
        return lambda app: app[name] == value

      for key, name in list(filter_names.items()):
          text_filter = re.search(r"\s*("+key+")\s*:([^ ]+)", filters.get("text"))
          if text_filter and text_filter.group(1) == key:
            filter_map[name] = text_filter.group(2).strip()

    if filters.get("time"):
      time_filter = filters.get("time")
      period_ms = self._time_in_ms(float(time_filter.get("time_value")), time_filter.get("time_unit")[0:1])
      ms_diff = current_ms_from_utc() - period_ms
      filter_map["date"] = datetime.strftime(datetime.fromtimestamp(ms_diff / 1000), "%Y-%m-%d")
      if time_filter.get("time_unit")[0:1] != 'd':
        filter_map["time"] = int(ms_diff)
    if filters.get("states"):
      if len(filters.get("states")) == 1:
        filter_map["status"] = filters.get("states")[0]

    return filter_map

  def _time_in_ms(self, time, period):
    if period == 'ns':
      return float(time) / 1000
    elif period == 'ms':
      return float(time)
    elif period == 's':
      return float(time) * 1000
    elif period == 'm':
      return float(time) * 60000 #1000*60
    elif period == 'h':
      return float(time) * 3600000 #1000*60*60
    elif period == 'd':
      return float(time) * 86400000  # 1000*60*60*24
    else:
      return float(time)