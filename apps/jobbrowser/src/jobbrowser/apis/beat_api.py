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
import sys

from datetime import datetime

from dateutil import parser
from desktop.lib.scheduler.lib.beat import CeleryBeatApi

from jobbrowser.apis.base_api import Api

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _

LOG = logging.getLogger(__name__)


class BeatApi(Api):

  def apps(self, filters):
    api = CeleryBeatApi(user=self.user)

    tasks = api.list_tasks(self.user)

    return {
      'apps': [{
          'id': 'celery-beat-%(id)s' % app,
          'name': '%(name)s' % app,
          'status': self._massage_status(app),
          'apiStatus': self._api_status(self._massage_status(app)),
          'type': 'celery-beat',
          'user': app['description'], # No user id available yet
          'progress': 50,
          'queue': app['queue'],
          'canWrite': self.user.username == app['description'],
          'duration': ((datetime.now() - parser.parse(app['start_time']).replace(tzinfo=None)).seconds * 1000) if app['start_time'] else 1,
          'submitted': app.get('date_changed')
        } for app in tasks
      ],
      'total': len(tasks)
    }


  def app(self, appid):
    appid = appid.rsplit('-')[-1]
    api = CeleryBeatApi(user=self.user)

    app = api.list_task(appid)

    return {
      'id': 'celery-beat-%(id)s' % app,
      'name': '%(name)s' % app,
      'status': self._massage_status(app),
      'apiStatus': self._api_status(self._massage_status(app)),
      'type': 'celery-beat',
      'user': app['description'],
      'progress': 50,
      'queue': app['queue'],
      'duration': 1,
      'canWrite': self.user.username == app['description'],
      'submitted': app.get('date_changed'),
      'properties': {
      }
    }


  def action(self, app_ids, operation):
    api = CeleryBeatApi(user=self.user)

    operations = []
    actual_app_ids = [app_id.replace('celery-beat-', '') for app_id in app_ids]

    for app_id in actual_app_ids:
      try:
        api.action(app_id, operation['action'])
        operations.append(app_id)
      except Exception:
        LOG.exception('Could not stop job %s' % app_id)

    return {'kills': operations, 'status': len(app_ids) - len(operations), 'message': _('%s signal sent to %s') % (operation['action'], operations)}


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
    if status == 'RUNNING':
      return 'RUNNING'
    else:
      return 'PAUSED'


  def _massage_status(self, task):
    return 'RUNNING' if task['enabled'] else 'PAUSED'


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
