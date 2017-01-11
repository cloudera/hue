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

import json
import logging

from django.utils.translation import ugettext as _

from jobbrowser.apis.base_api import Api, MockDjangoRequest
from jobbrowser.views import job_attempt_logs_json, tasks


LOG = logging.getLogger(__name__)


try:
  from jobbrowser.api import YarnApi as NativeYarnApi
except Exception, e:
  LOG.exception('Some application are not enabled: %s' % e)


class JobApi(Api):

  def __init__(self, user):
    self.user = user
    self.yarn_api = YarnApi(user) # TODO: actually long term move job aggregations to the frontend instead probably
    self.impala_api = ImpalaApi(user)
    self.request = None

  def apps(self):
    jobs = self.yarn_api.apps()
    # += Impala
    # += Sqoop2
    return jobs

  def app(self, appid):
    return self._get_api(appid).app(appid)

  def logs(self, appid, app_type):
    return self._get_api(appid).logs(appid, app_type)

  def profile(self, appid, app_type, app_property):
    return self._get_api(appid).profile(appid, app_type, app_property)

  def _get_api(self, appid):
    if appid.startswith('task_'):
      return YarnMapReduceTaskApi(self.user, appid)
    else:
      return self.yarn_api # application_

  def _set_request(self, request):
    self.request = request


class YarnApi(Api):
  """YARN, MR, Spark"""

  def apps(self):
    jobs = NativeYarnApi(self.user).get_jobs(self.user, username=self.user.username, state='all', text='')
    return [{
        'id': app.jobId,
        'name': app.name,
        'type': app.applicationType,
        'status': app.status,
        'user': self.user.username,
        'progress': 100,
        'duration': 10 * 3600,
        'submitted': 10 * 3600
    } for app in jobs]


  def app(self, appid):
    app = NativeYarnApi(self.user).get_job(jobid=appid)

    common = {
        'id': app.jobId,
        'name': app.name,
        'type': app.applicationType,
        'status': app.status,
        'user': self.user.username,
        'progress': 100,
        'duration': 10 * 3600,
        'submitted': 10 * 3600
    }

    if app.applicationType == 'MR2':
      common['type'] = 'MAPREDUCE'
      common['duration'] = app.duration
      common['durationFormatted'] = app.durationFormatted

      common['properties'] = {
          'maps_percent_complete': app.maps_percent_complete,
          'reduces_percent_complete': app.reduces_percent_complete,
          'finishedMaps': app.finishedMaps,
          'finishedReduces': app.finishedReduces,
          'desiredMaps': app.desiredMaps,
          'desiredReduces': app.desiredReduces,
          'tasks': []
      }
    return common


  def logs(self, appid, app_type):
    if app_type == 'MAPREDUCE':
      response = job_attempt_logs_json(MockDjangoRequest(self.user), job=appid)
      logs = json.loads(response.content)['log']
    else:
      logs = None
    return {'progress': 0, 'logs': {'default': logs}}


  def profile(self, appid, app_type, app_property):
    if app_type == 'MAPREDUCE':
      if app_property == 'tasks':
        return {
          'task_list': YarnMapReduceTaskApi(self.user, appid).apps(),
        }

    return {}


class YarnMapReduceTaskApi(Api):

  def __init__(self, user, app_id):
    Api.__init__(self, user)
    self.app_id = '_'.join(app_id.replace('task_', 'application_').split('_')[:3])


  def apps(self):
    return [self._massage_task(task) for task in NativeYarnApi(self.user).get_tasks(jobid=self.app_id, pagenum=1)]

  def app(self, appid):
    task = NativeYarnApi(self.user).get_task(jobid=self.app_id, task_id=appid)

    common = self._massage_task(task)
    common['properties'] = {
    }

    return common


  def logs(self, appid, app_type):
    if app_type == 'MAPREDUCE':
      response = job_attempt_logs_json(MockDjangoRequest(self.user), job=appid)
      logs = json.loads(response.content)['log']
    else:
      logs = None
    return {'progress': 0, 'logs': {'default': logs}}


  def profile(self, appid, app_type, app_property):
    if app_property == 'task_attemps':
      response = tasks(self.request, job=appid)
      return json.loads(response.content)

    return {}

  def _massage_task(self, task):
    return {
        'id': task.id,
        'type': task.type,
        'elapsedTime': task.elapsedTime,
        'progress': task.progress,
        'state': task.state,
        'startTime': task.startTime,
        'successfulAttempt': task.successfulAttempt,
        'finishTime': task.finishTime
    }


class YarnAtsApi(Api):
  pass


class ImpalaApi(Api):
  pass


class Sqoop2Api(Api):
  pass
