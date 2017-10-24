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
import time
from datetime import datetime

from django.utils.translation import ugettext as _

from jobbrowser.apis.base_api import Api

LOG = logging.getLogger(__name__)


try:
  from beeswax.models import Session
  from impala.server import get_api as get_impalad_api, _get_impala_server_url
except Exception, e:
  LOG.exception('Some application are not enabled: %s' % e)

def _get_api(user):
  session = Session.objects.get_session(user, application='impala')
  server_url = _get_impala_server_url(session)
  return get_impalad_api(user=user, url=server_url)

class QueryApi(Api):

  def __init__(self, user, impala_api=None):
    if impala_api:
      self.api = impala_api
    else:
      self.api = _get_api(user)

  def apps(self, filters):
    kwargs = {}

    jobs = self.api.get_queries(**kwargs)

    filter_list = self._get_filter_list(filters)
    jobs_iter = itertools.chain(jobs['in_flight_queries'], jobs['completed_queries'])
    jobs_iter_filtered = self._n_filter(filter_list, jobs_iter)

    return {
      'apps': sorted([{
        'id': job['query_id'],
        'name': job['stmt'][:100] + ('...' if len(job['stmt']) > 100 else ''),
        'status': job['state'],
        'apiStatus': self._api_status(job['state']),
        'type': job['stmt_type'],
        'user': job['effective_user'],
        'queue': job['resource_pool'],
        'progress': job['progress'],
        'canWrite': job in jobs['in_flight_queries'],
        'duration': self._time_in_ms_groups(re.search(r"\s*(([\d.]*)([a-z]*))(([\d.]*)([a-z]*))?(([\d.]*)([a-z]*))?", job['duration'], re.MULTILINE).groups()),
        'submitted': job['start_time'],
        # Extra specific
        'rows_fetched': job['rows_fetched'],
        'waiting': job['waiting'],
        'waiting_time': job['waiting_time']
      } for job in jobs_iter_filtered], key=lambda job: job.get('submitted'), reverse=True),
      'total': jobs['num_in_flight_queries'] + jobs['num_executing_queries'] + jobs['num_waiting_queries']
    }

  def _time_in_ms_groups(self, groups):
    time = 0
    for x in range(0, len(groups), 3):
      if groups[x+1]:
        time += self._time_in_ms(groups[x+1], groups[x+2])
    return time

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

  def app(self, appid):
    query = self.api.get_query_profile(query_id=appid)
    if query.get('error'):
      return {
        'status': -1,
        'message': query.get('error')
      }

    user = re.search(r"^\s*User:\s?([^\n\r]*)$", query['profile'], re.MULTILINE).group(1)
    status = re.search(r"^\s*Query State:\s?([^\n\r]*)$", query['profile'], re.MULTILINE).group(1)
    stmt = re.search(r"^\s*Sql Statement:\s?([^\n\r]*)", query['profile'], re.MULTILINE).group(1)
    partitions = re.findall(r"partitions=\s*(\d)+\s*\/\s*(\d)+", query['profile'])
    end_time = re.search(r"^\s*End Time:\s?([^\n\r]*)$", query['profile'], re.MULTILINE).group(1)
    submitted = re.search(r"^\s*Start Time:\s?([^\n\r]*)$", query['profile'], re.MULTILINE).group(1)

    progress = 0
    if end_time:
      progress = 100
    elif partitions:
      for partition in partitions:
        progress += float(partition[0]) / float(partition[1])
      progress /= len(partitions)
      progress *= 100

    if end_time:
      end_time_ms = int(time.mktime(datetime.strptime(end_time[:26], '%Y-%m-%d %H:%M:%S.%f').timetuple()))*1000
      start_time_ms = int(time.mktime(datetime.strptime(submitted[:26], '%Y-%m-%d %H:%M:%S.%f').timetuple()))*1000
      duration_ms = end_time_ms - start_time_ms
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
    message = {'message': '', 'status': 0}

    if action.get('action') == 'kill':

      for _id in appid:
        result = self.api.kill(_id)
        if result.get('error'):
          message['message'] = result.get('error')
          message['status'] = -1
        elif result.get('contents') and message.get('status') != -1:
          message['message'] = result.get('contents')

    return message;


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
    return self.api.get_query_memory(query_id=appid);

  def _query(self, appid):
    return self.api.get_query(query_id=appid)

  def _query_profile(self, appid):
    return self.api.get_query_profile(query_id=appid)

  def _api_status_filter(self, status):
    if status in ['RUNNING', 'CREATED']:
      return 'RUNNING'
    elif status in ['FINISHED']:
      return 'COMPLETED'
    else:
      return 'FAILED'

  def _api_status(self, status):
    if status in ['RUNNING', 'CREATED']:
      return 'RUNNING'
    elif status in ['FINISHED']:
      return 'SUCCEEDED'
    else:
      return 'FAILED'

  def _get_filter_list(self, filters):
    filter_list = []
    if filters.get("text"):
      filter_names = {
        'user':'effective_user',
        'id':'query_id',
        'name':'state',
        'type':'stmt_type',
        'status':'status'
      }

      def makeLambda(name, value):
        return lambda app: app[name] == value

      for key, name in filter_names.items():
          text_filter = re.search(r"\s*("+key+")\s*:([^ ]+)", filters.get("text"))
          if text_filter and text_filter.group(1) == key:
            filter_list.append(makeLambda(name, text_filter.group(2).strip()))
    if filters.get("time"):
      time_filter = filters.get("time")
      period_ms = self._time_in_ms(float(time_filter.get("time_value")), time_filter.get("time_unit")[0:1])
      current_ms = time.time() * 1000.0
      filter_list.append(lambda app: current_ms - (time.mktime(datetime.strptime(app['start_time'][:26], '%Y-%m-%d %H:%M:%S.%f').timetuple()) * 1000) < period_ms)
    if filters.get("states"):
      filter_list.append(lambda app: self._api_status_filter(app['state']).lower() in filters.get("states"))

    return filter_list

  def _n_filter(self, filters, tuples):
    for f in filters:
      tuples = filter(f, tuples)
    return tuples