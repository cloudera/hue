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
from desktop.lib.scheduler.lib.hive import HiveSchedulerApi

from jobbrowser.apis.base_api import Api

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _

LOG = logging.getLogger()


class HiveScheduleApi(Api):

  def apps(self, filters):
    api = HiveSchedulerApi(user=self.user)

    tasks = api.list_tasks(self.user)

    return {
      'apps': [{
          'id': 'schedule-hive-%(scheduled_query_id)s' % app,
          'name': '%(schedule_name)s' % app,
          'status': self._massage_status(app),
          'apiStatus': self._api_status(self._massage_status(app)),
          'type': 'schedule-hive',
          'user': app['user'],
          'progress': 50,
          'queue': app['cluster_namespace'],
          'canWrite': self.user.username == app['user'],
          'duration': 1,
          'submitted': app['enabled']
        } for app in tasks
      ],
      'total': len(tasks)
    }


  def app(self, appid):
    appid = appid.rsplit('-')[-1]
    api = HiveSchedulerApi(user=self.user)

    app = api.list_task(appid)

    return {
        'id': 'schedule-hive-%(scheduled_query_id)s' % app,
        'name': '%(schedule_name)s' % app,
        'status': self._massage_status(app),
        'apiStatus': self._api_status(self._massage_status(app)),
        'type': 'schedule-hive',
        'user': app['user'],
        'progress': 50,
        'queue': app['cluster_namespace'],
        'duration': 1,
        'canWrite': self.user.username == app['user'],
        'submitted': app['enabled'],
        'properties': {
            'query': app['query'],
            'tasks': []
        }
    }


  def action(self, app_ids, operation):
    api = HiveSchedulerApi(user=self.user)

    operations = []
    actual_app_ids = [app_id.rsplit('-')[-1] for app_id in app_ids]

    for app_id in actual_app_ids:
      try:
        api.action(app_id, operation['action'])
        operations.append(app_id)
      except Exception:
        LOG.exception('Could not stop job %s' % app_id)

    return {
        'kills': operations,
        'status': len(app_ids) - len(operations),
        'message': _('%s signal sent to %s') % (operation['action'], operations)
    }


  def logs(self, appid, app_type, log_name=None, is_embeddable=False):
    return {'logs': ''}


  def profile(self, appid, app_type, app_property, app_filters):
    appid = appid.rsplit('-')[-1]

    if app_property == 'tasks':
      api = HiveSchedulerApi(user=self.user)

      return [
        {
          'status': task['state'],
          'title': task['executor_query_id'],
        }
        for task in api.list_executed_tasks(appid)
      ]
    else:
      return {}


  def _api_status(self, status):
    if status == 'RUNNING':
      return 'RUNNING'
    else:
      return 'PAUSED'


  def _massage_status(self, task):
    return 'RUNNING' if task['enabled'] else 'PAUSED'
