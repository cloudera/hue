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

import itertools
import logging
import re

from django.utils.translation import ugettext as _

from jobbrowser.apis.base_api import Api

LOG = logging.getLogger(__name__)


try:
  from beeswax.models import Session
  from impala.server import get_api as get_impalad_api, _get_impala_server_url
except Exception, e:
  LOG.exception('Some application are not enabled: %s' % e)


class QueryApi(Api):

  def __init__(self, user):
    self.user = user
    session = Session.objects.get_session(self.user, application='impala')
    self.server_url = _get_impala_server_url(session)

  def apps(self, filters):
    kwargs = {}

    api = get_impalad_api(user=self.user, url=self.server_url)

    jobs = api.get_queries(**kwargs)

    return {
      'apps': [{
        'id': app['query_id'],
        'name': app['stmt'][:100] + ('...' if len(app['stmt']) > 100 else ''),
        'status': app['state'],
        'apiStatus': self._api_status(app['state']),
        'type': app['stmt_type'],
        'user': app['effective_user'],
        'queue': app['resource_pool'],
        'progress': app['progress'],
        'duration': 0, # app['duration'],
        'submitted': app['start_time'],
        # Extra specific
        'rows_fetched': app['rows_fetched'],
        'waiting': app['waiting'],
        'waiting_time': app['waiting_time']
      } for app in itertools.chain(jobs['in_flight_queries'], jobs['completed_queries'])],
      'total': jobs['num_in_flight_queries'] + jobs['num_executing_queries'] + jobs['num_waiting_queries']
    }

  def time_in_ms(self, time, period):
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
    else:
      return float(time)

  def app(self, appid):
    api = get_impalad_api(user=self.user, url=self.server_url)

    query = api.get_query_profile(query_id=appid)
    user = re.search(r"^\s*User:\s*(.*)$", query['profile'], re.MULTILINE).group(1)
    status = re.search(r"^\s*Query State:\s*(.*)$", query['profile'], re.MULTILINE).group(1)
    stmt = re.search(r"^\s*Sql Statement:\s*(.*)$", query['profile'], re.MULTILINE).group(1)
    partitions = re.findall(r"partitions=\s*(\d)+\s*\/\s*(\d)+", query['profile'])
    end_time = re.search(r"^\s*End Time:\s*(.*)$", query['profile'], re.MULTILINE).group(1)
    duration_1 = re.search(r"\s*Rows available:\s([\d.]*)(\w*)", query['profile'], re.MULTILINE)
    duration_2 = re.search(r"\s*Request finished:\s([\d.]*)(\w*)", query['profile'], re.MULTILINE)
    duration_3 = re.search(r"\s*Query Timeline:\s([\d.]*)(\w*)", query['profile'], re.MULTILINE)
    submitted = re.search(r"^\s*Start Time:\s*(.*)$", query['profile'], re.MULTILINE).group(1)

    progress = 0
    if end_time:
      progress = 100
    elif partitions:
      for partition in partitions:
        progress += float(partition[0]) / float(partition[1])
      progress /= len(partitions)
      progress *= 100

    duration = duration_1 or duration_2 or duration_3
    if duration:
      duration_ms = self.time_in_ms(duration.group(1), duration.group(2))
    else:
      duration_ms = 0

    common = {
        'id': appid,
        'name': stmt,
        'status': status,
        'apiStatus': self._api_status(status),
        'user': user,
        'progress': progress,
        'duration': duration_ms,
        'submitted': submitted,
        'type': 'queries'
    }

    common['properties'] = {
      'memory': '',
      'profile': '',
      'plan': ''
    }

    return common


  def action(self, appid, action):
    return {}


  def logs(self, appid, app_type, log_name=None):
    return {'logs': ''}

  def profile(self, appid, app_type, app_property, app_filters):
    if app_property == 'memory':
      return self._memory(appid, app_type, app_property, app_filters)
    elif app_property == 'profile':
      return self._query_profile(appid)
    else:
      return self._query(appid)

  def _memory(self, appid, app_type, app_property, app_filters):
    api = get_impalad_api(user=self.user, url=self.server_url)
    return api.get_query_memory(query_id=appid);

  def _query(self, appid):
    api = get_impalad_api(user=self.user, url=self.server_url)
    return api.get_query(query_id=appid)

  def _query_profile(self, appid):
    api = get_impalad_api(user=self.user, url=self.server_url)
    return api.get_query_profile(query_id=appid)

  def _api_status(self, status):
    if status in ['RUNNING', 'CREATED']:
      return 'RUNNING'
    elif status in ['FINISHED']:
      return 'SUCCEEDED'
    else:
      return 'FAILED' # INTERRUPTED , KILLED, TERMINATED and FAILED
