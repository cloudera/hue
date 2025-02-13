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

import sys
import json
import logging
from builtins import object

from django.utils.translation import gettext as _

from jobbrowser.apis.base_api import Api, MockDjangoRequest
from jobbrowser.apis.workflow_api import _filter_oozie_jobs, _manage_oozie_job
from liboozie.oozie_api import get_oozie
from liboozie.utils import format_time

LOG = logging.getLogger()


try:
  from oozie.conf import OOZIE_JOBS_COUNT
  from oozie.views.dashboard import get_oozie_job_log, has_job_edition_permission, list_oozie_coordinator, massaged_oozie_jobs_for_json
except Exception as e:
  LOG.warning('Some application are not enabled: %s' % e)


class ScheduleApi(Api):

  def apps(self, filters):
    oozie_api = get_oozie(self.user)
    kwargs = {'cnt': hasattr(OOZIE_JOBS_COUNT, 'get') and OOZIE_JOBS_COUNT.get(), 'filters': []}

    filters.pop('time')

    _filter_oozie_jobs(self.user, filters, kwargs)

    jobs = oozie_api.get_coordinators(**kwargs)

    return {
      'apps': [{
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

  def app(self, appid, offset=1, filters={}):
    oozie_api = get_oozie(self.user)
    coordinator = oozie_api.get_coordinator(jobid=appid)

    mock_get = MockGet()
    mock_get.update('offset', offset)

    """
      The Oozie job api supports one or more "status" parameters. The valid status values are:

      WAITING, READY, SUBMITTED, RUNNING, SUSPENDED, TIMEDOUT, SUCCEEDED, KILLED, FAILED, IGNORED, SKIPPED

      The job browser UI has a generic filter mechanism that is re-used across all different type of jobs, that
      parameter is called "states" and it only has three possible values: completed, running or failed

      Here we adapt this to fit the API requirements, "state" becomes "status" and the values are translated
      based on how it's been done historically (for instance list_oozie_coordinator.mako around line 725).
    """
    if 'states' in filters:
      statusFilters = []
      for stateFilter in filters.get('states'):
        if stateFilter == 'completed':
          statusFilters.append('SUCCEEDED')
        elif stateFilter == 'running':
          statusFilters.extend(['RUNNING', 'READY', 'SUBMITTED', 'SUSPENDED', 'WAITING'])
        elif stateFilter == 'failed':
          statusFilters.extend(['KILLED', 'FAILED', 'TIMEDOUT', 'SKIPPED'])
      mock_get.update('status', statusFilters)
    request = MockDjangoRequest(self.user, get=mock_get)
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
    'PREP': 'RUNNING',
    'RUNNING': 'RUNNING',
    'RUNNINGWITHERROR': 'RUNNING',
    'PREPSUSPENDED': 'PAUSED',
    'SUSPENDED': 'PAUSED',
    'SUSPENDEDWITHERROR': 'PAUSED',
    'PREPPAUSED': 'PAUSED',
    'PAUSED': 'PAUSED',
    'PAUSEDWITHERROR': 'PAUSED',
    'SUCCEEDED': 'SUCCEEDED',
    'DONEWITHERROR': 'FAILED',
    'KILLED': 'FAILED',
    'FAILED': 'FAILED',
  }

  def _api_status(self, status):
    return self._API_STATUSES.get(status, 'FAILED')

  _TASK_API_STATUSES = {
    'WAITING': 'RUNNING',
    'READY': 'RUNNING',
    'SUBMITTED': 'RUNNING',
    'RUNNING': 'RUNNING',
    'SUSPENDED': 'PAUSED',
    'SUCCEEDED': 'SUCCEEDED',
    'TIMEDOUT': 'FAILED',
    'KILLED': 'FAILED',
    'FAILED': 'FAILED',
    'IGNORED': 'FAILED',
    'SKIPPED': 'FAILED',
  }

  def _task_api_status(self, status):
    return self._TASK_API_STATUSES.get(status, 'FAILED')


class MockGet(object):
  _prop = None

  def __ini__(self, statuses):
    self.statuses = []

  @property
  def properties(self):
    if self._prop is None:
      self._prop = {}
    return self._prop

  def update(self, prop, value):
    if prop != 'format':
      self.properties.update({prop: value})

  def get(self, prop, default=None):
    if prop == 'format':
      return 'json'
    else:
      return self._prop.get(prop, default)

  def getlist(self, prop):
    return self._prop.get(prop)
