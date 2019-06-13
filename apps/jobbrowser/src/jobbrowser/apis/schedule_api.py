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

from django.utils.translation import ugettext as _

from liboozie.oozie_api import get_oozie
from liboozie.utils import format_time

from jobbrowser.apis.base_api import Api, MockDjangoRequest
from jobbrowser.apis.workflow_api import _manage_oozie_job, _filter_oozie_jobs


LOG = logging.getLogger(__name__)


try:
  from oozie.conf import OOZIE_JOBS_COUNT
  from oozie.views.dashboard import list_oozie_coordinator, get_oozie_job_log, massaged_oozie_jobs_for_json, has_job_edition_permission
except Exception, e:
  LOG.warn('Some application are not enabled: %s' % e)


class ScheduleApi(Api):

  def apps(self, filters):
    oozie_api = get_oozie(self.user)
    kwargs = {'cnt': hasattr(OOZIE_JOBS_COUNT, 'get') and OOZIE_JOBS_COUNT.get(), 'filters': []}

    filters.pop('time')

    _filter_oozie_jobs(self.user, filters, kwargs)

    jobs = oozie_api.get_coordinators(**kwargs)

    return {
      'apps':[{
        'id': app['id'],
        'name': app['appName'],
        'status': app['status'],
        'apiStatus': self._api_status(app['status']),
        'type': 'schedule',
        'user': app['user'],
        'progress': app['progress'],
        'queue': app['group'],
        'duration': app['durationInMillis'],
        'submitted': app['lastActionInMillis'] * 1000,
        'canWrite': app['canEdit']
      } for app in massaged_oozie_jobs_for_json(jobs.jobs, self.user)['jobs']],
      'total': jobs.total
    }


  def app(self, appid):
    oozie_api = get_oozie(self.user)
    coordinator = oozie_api.get_coordinator(jobid=appid)

    request = MockDjangoRequest(self.user, get=MockGet())
    response = list_oozie_coordinator(request, job_id=appid)

    common = {
        'id': coordinator.coordJobId,
        'name': coordinator.coordJobName,
        'status': coordinator.status,
        'apiStatus': self._api_status(coordinator.status),
        'progress': coordinator.get_progress(),
        'type': 'schedule',
        'submitted': format_time(coordinator.startTime),
        'user': coordinator.user,
        'canWrite': has_job_edition_permission(coordinator, self.user),
    }
    common['properties'] = json.loads(response.content)
    for action in common['properties']['actions']:
      action['apiStatus'] = self._task_api_status(action['status'])
    common['properties']['tasks'] = common['properties']['actions']
    common['properties']['xml'] = ''
    common['properties']['properties'] = ''
    common['properties']['bundle_id'] = coordinator.conf_dict.get('oozie.bundle.id')
    common['doc_url'] = common['properties'].get('doc_url')

    return common


  def action(self, app_ids, action):
    return _manage_oozie_job(self.user, action, app_ids)


  def logs(self, appid, app_type, log_name=None, is_embeddable=False):
    request = MockDjangoRequest(self.user)
    data = get_oozie_job_log(request, job_id=appid)

    return {'logs': json.loads(data.content)['log']}


  def profile(self, appid, app_type, app_property, app_filters):
    if app_property == 'xml':
      oozie_api = get_oozie(self.user)
      coordinator = oozie_api.get_coordinator(jobid=appid)
      return {
        'xml': coordinator.definition,
      }
    elif app_property == 'properties':
      oozie_api = get_oozie(self.user)
      coordinator = oozie_api.get_coordinator(jobid=appid)
      return {
        'properties': coordinator.conf_dict,
      }
    elif app_property == 'tasks':
      coordinator = self.app(appid)
      return coordinator['properties']['tasks']

  _API_STATUSES = {
    'PREP':               'RUNNING',
    'RUNNING':            'RUNNING',
    'RUNNINGWITHERROR':   'RUNNING',
    'PREPSUSPENDED':      'PAUSED',
    'SUSPENDED':          'PAUSED',
    'SUSPENDEDWITHERROR': 'PAUSED',
    'PREPPAUSED':         'PAUSED',
    'PAUSED':             'PAUSED',
    'PAUSEDWITHERROR':    'PAUSED',
    'SUCCEEDED':          'SUCCEEDED',
    'DONEWITHERROR':      'FAILED',
    'KILLED':             'FAILED',
    'FAILED':             'FAILED',
  }

  def _api_status(self, status):
    return self._API_STATUSES.get(status, 'FAILED')

  _TASK_API_STATUSES = {
    'WAITING':   'RUNNING',
    'READY':     'RUNNING',
    'SUBMITTED': 'RUNNING',
    'RUNNING':   'RUNNING',
    'SUSPENDED': 'PAUSED',
    'SUCCEEDED': 'SUCCEEDED',
    'TIMEDOUT':  'FAILED',
    'KILLED':    'FAILED',
    'FAILED':    'FAILED',
    'IGNORED':   'FAILED',
    'SKIPPED':   'FAILED',
  }

  def _task_api_status(self, status):
    return self._TASK_API_STATUSES.get(status, 'FAILED')


class MockGet():
  def __ini__(self, statuses):
    self.statuses = []

  def get(self, prop, default=None):
    if prop == 'format':
      return 'json'
    else:
      return default

  def getlist(self, prop):
    return []
