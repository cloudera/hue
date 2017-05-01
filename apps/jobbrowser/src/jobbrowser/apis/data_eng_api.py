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
import json

from datetime import datetime,  timedelta

from django.utils.translation import ugettext as _

from jobbrowser.apis.base_api import Api, MockDjangoRequest, _extract_query_params
from liboozie.oozie_api import get_oozie
from notebook.connectors.dataeng import DataEng, DATE_FORMAT


LOG = logging.getLogger(__name__)


class DataEngClusterApi(Api):

  def apps(self, filters):
#     kwargs = {'cnt': OOZIE_JOBS_COUNT.get(), 'filters': []}
#
#     text_filters = _extract_query_params(filters)
#
#     if not has_dashboard_jobs_access(self.user):
#       kwargs['filters'].append(('user', self.user.username))
#     elif 'user' in text_filters:
#       kwargs['filters'].append(('user', text_filters['username']))
#
#     if 'time' in filters:
#       kwargs['filters'].extend([('startcreatedtime', '-%s%s' % (filters['time']['time_value'], filters['time']['time_unit'][:1]))])
#
#     if ENABLE_OOZIE_BACKEND_FILTERING.get() and text_filters.get('text'):
#       kwargs['filters'].extend([('text', text_filters.get('text'))])
#
#     if filters.get('states'):
#       states_filters = {'running': ['RUNNING', 'PREP', 'SUSPENDED'], 'completed': ['SUCCEEDED'], 'failed': ['FAILED', 'KILLED'],}
#       for _state in filters.get('states'):
#         for _status in states_filters[_state]:
#           kwargs['filters'].extend([('status', _status)])

    api = DataEng(self.user)

    jobs = api.list_clusters()

    return {
      'apps': [{
        'id': app['clusterName'],
        'name': '%(workersGroupSize)s %(instanceType)s %(cdhVersion)s' % app,
        'status': app['status'],
        'apiStatus': self._api_status(app['status']),
        'type': app['serviceType'],
        'user': app['clusterName'].split('-', 1)[0],
        'progress': 100,
        'duration': 10 * 3600,
        'submitted': app['creationDate']
      } for app in jobs['clusters']],
      'total': None
    }


  def app(self, appid):
    return {}


  def action(self, appid, action):
    return {}


  def logs(self, appid, app_type, log_name=None):
    return {'logs': ''}


  def profile(self, appid, app_type, app_property):
    return {}

  def _api_status(self, status):
    if status in ['CREATING', 'CREATED', 'TERMINATING']:
      return 'RUNNING'
    elif status in ['ARCHIVING', 'COMPLETED']:
      return 'SUCCEEDED'
    else:
      return 'FAILED' # KILLED and FAILED


class DataEngJobApi(Api):

  def apps(self, filters):
    kwargs = {}
#
#     text_filters = _extract_query_params(filters)
#
#     if not has_dashboard_jobs_access(self.user):
#       kwargs['filters'].append(('user', self.user.username))
#     elif 'user' in text_filters:
#       kwargs['filters'].append(('user', text_filters['username']))
#
    if 'time' in filters:
      if filters['time']['time_unit'] == 'minutes':
        delta = timedelta(minutes=int(filters['time']['time_value']))
      elif filters['time']['time_unit'] == 'hours':
        delta = timedelta(hours=int(filters['time']['time_value']))
      else:
        delta = timedelta(days=int(filters['time']['time_value']))
      kwargs['creation_date_after'] = (datetime.today() - delta).strftime(DATE_FORMAT)

#     if ENABLE_OOZIE_BACKEND_FILTERING.get() and text_filters.get('text'):
#       kwargs['filters'].extend([('text', text_filters.get('text'))])
#
#     if filters.get('states'):
#       states_filters = {'running': ['RUNNING', 'PREP', 'SUSPENDED'], 'completed': ['SUCCEEDED'], 'failed': ['FAILED', 'KILLED'],}
#       for _state in filters.get('states'):
#         for _status in states_filters[_state]:
#           kwargs['filters'].extend([('status', _status)])

    api = DataEng(self.user)

    jobs = api.list_jobs(**kwargs)

    return {
      'apps': [{
        'id': app['jobId'],
        'name': app['creationDate'],
        'status': app['status'],
        'apiStatus': self._api_status(app['status']),
        'type': app['jobType'],
        'user': '',
        'progress': 100,
        'duration': 10 * 3600,
        'submitted': app['creationDate']
      } for app in jobs['jobs']],
      'total': None
    }

  def app(self, appid):
    handle = DataEng(self.user).describe_jobs(job_ids=[appid])

    job = handle['jobs'][0]

    common = {
        'id': job['jobId'],
        'name': job['jobId'],
        'status': job['status'],
        'apiStatus': self._api_status(job['status']),
        'progress': 50,
        'duration': 10 * 3600,
        'submitted': job['creationDate'],
        'type': 'dataeng-job-%s' % job['jobType'],
    }

    common['properties'] = {
      'properties': job
    }

    return common


  def action(self, appid, action):
    return {}


  def logs(self, appid, app_type, log_name=None):
    return {'logs': ''}


  def profile(self, appid, app_type, app_property):
    return {}

  def _api_status(self, status):
    if status in ['CREATING', 'CREATED', 'TERMINATING']:
      return 'RUNNING'
    elif status in ['COMPLETED']:
      return 'SUCCEEDED'
    else:
      return 'FAILED' # INTERRUPTED , KILLED, TERMINATED and FAILED

