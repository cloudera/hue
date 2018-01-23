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

from spark.job_server_api import get_api

from jobbrowser.apis.base_api import Api


LOG = logging.getLogger(__name__)


class LivySessionsApi(Api):

  def apps(self, filters):
    api = get_api(self.user)

    jobs = api.get_sessions()

    return {
      'apps': [{
        'id': 'livy-%(id)s' % app,
        'name': '%(kind)s %(id)s' % app,
        'status': app['state'],
        'apiStatus': self._api_status(app['state']),
        'type': 'livy-session',
        'user': app['owner'],
        'progress': 100,
        'queue': 'group',
        'duration': 1,
        'submitted': ''
      } for app in jobs['sessions']],
      'total': jobs['total']
    }


  def app(self, appid):
    appid = appid.rsplit('-')[-1]
    api = get_api(self.user)

    job = api.get_session(appid)

    return {
      'id': 'livy-%(id)s' % job,
      'name': '%(kind)s %(id)s' % job,
      'status': job['state'],
      'apiStatus': self._api_status(job['state']),
      'type': 'livy-session',
      'user': job['owner'],
      'progress': 100,
      'queue': 'group',
      'duration': 1,
      'submitted': '',
      'properties': {
        'statements': []
      }
    }


  def action(self, appid, action):
    return {}


  def logs(self, appid, app_type, log_name=None, is_embeddable=False):
    return {'logs': ''}


  def profile(self, appid, app_type, app_property, app_filters):
    appid = appid.rsplit('-')[-1]

    if app_property == 'properties':
      api = get_api(self.user)

      return api.get_statements(appid)
    else:
      return {}


  def _api_status(self, status):
    if status in ['CREATING', 'CREATED', 'TERMINATING']:
      return 'RUNNING'
    elif status in ['ARCHIVING', 'COMPLETED']:
      return 'SUCCEEDED'
    else:
      return 'FAILED' # KILLED and FAILED


class LivyJobApi(Api):

  def apps(self, filters):
    kwargs = {}

    api = get_api(self.user)

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
      'total': len(jobs)
    }

  def app(self, appid):
    handle = DataEng(self.user).describe_job(job_id=appid)

    job = handle['job']

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


  def logs(self, appid, app_type, log_name=None, is_embeddable=False):
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
