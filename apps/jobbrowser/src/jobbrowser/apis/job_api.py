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

from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from hadoop.yarn import resource_manager_api

from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions import MessageException
from desktop.lib.exceptions_renderable import PopupException
from jobbrowser.conf import MAX_JOB_FETCH, LOG_OFFSET
from jobbrowser.views import job_executor_logs, job_single_logs


LOG = logging.getLogger(__name__)
LOG_OFFSET_BYTES = LOG_OFFSET.get()


try:
  from jobbrowser.api import YarnApi as NativeYarnApi, ApplicationNotRunning, JobExpired
  from jobbrowser.apis.base_api import Api, MockDjangoRequest, _extract_query_params
  from jobbrowser.views import job_attempt_logs_json, kill_job, massage_job_for_json
  from jobbrowser.yarn_models import Application
except Exception, e:
  LOG.exception('Some application are not enabled: %s' % e)


class JobApi(Api):

  def __init__(self, user):
    self.user = user
    self.yarn_api = YarnApi(user)
    self.request = None

  def apps(self, filters):
    return self.yarn_api.apps(filters)

  def app(self, appid):
    return self._get_api(appid).app(appid)

  def action(self, app_ids, operation):
    return self._get_api(app_ids).action(operation, app_ids)

  def logs(self, appid, app_type, log_name, is_embeddable=False):
    return self._get_api(appid).logs(appid, app_type, log_name, is_embeddable)

  def profile(self, appid, app_type, app_property, app_filters):
    return self._get_api(appid).profile(appid, app_type, app_property, app_filters)

  def _get_api(self, appid):
    if type(appid) == list:
      return self.yarn_api
    elif appid.startswith('task_'):
      return YarnMapReduceTaskApi(self.user, appid)
    elif appid.startswith('attempt_'):
      return YarnMapReduceTaskAttemptApi(self.user, appid)
    elif appid.startswith('appattempt_'):
      return YarnAttemptApi(self.user, appid)
    elif appid.find('_executor_') > 0:
      return SparkExecutorApi(self.user, appid)
    else:
      return self.yarn_api # application_

  def _set_request(self, request):
    self.request = request


class YarnApi(Api):
  """YARN, MR, Spark"""

  def apps(self, filters):
    filter_params = {
      'user': self.user,
      'username': '',
      'text': '',
      'state': 'all',
      'states': ''
    }

    filter_params.update(_extract_query_params(filters))

    if filters.get('states'):
      filter_params['states'] = filters['states']

    if 'time' in filters:
      filter_params['time_value'] = int(filters['time']['time_value'])
      filter_params['time_unit'] = filters['time']['time_unit']

    filter_params['limit'] = MAX_JOB_FETCH.get()

    jobs = NativeYarnApi(self.user).get_jobs(**filter_params)

    apps = [massage_job_for_json(job, user=self.user) for job in sorted(jobs, key=lambda job: job.jobId, reverse=True)]

    return {
      'apps': [{
        'id': app['id'],
        'name': app['name'],
        'type': app['applicationType'],
        'status': app['status'],
        'apiStatus': self._api_status(app['status']),
        'user': app['user'],
        'progress': app['progress'],
        'queue': app['queueName'],
        'duration': app['durationMs'],
        'submitted': app['startTimeMs'],
        'canWrite': app['canKill'],
      } for app in apps],
      'total': len(apps)
    }


  def app(self, appid):
    try:
      job = NativeYarnApi(self.user).get_job(jobid=appid)
    except ApplicationNotRunning, e:
      if e.job.get('state', '').lower() == 'accepted':
        rm_api = resource_manager_api.get_resource_manager(self.user)
        job = Application(e.job, rm_api)
      else:
        raise e  # Job has not yet been accepted by RM
    except JobExpired, e:
      raise PopupException(_('Job %s has expired.') % appid, detail=_('Cannot be found on the History Server.'))
    except Exception, e:
      msg = 'Could not find job %s.'
      LOG.exception(msg % appid)
      raise PopupException(_(msg) % appid, detail=e)


    app = massage_job_for_json(job, user=self.user)

    common = {
        'id': app['id'],
        'name': app['name'],
        'type': app['applicationType'],
        'status': app['status'],
        'apiStatus': self._api_status(app['status']),
        'user': app['user'],
        'progress': app['progress'],
        'duration': app['durationMs'],
        'submitted': app['startTimeMs'],
        'canWrite': app['canKill'],
    }

    if app['applicationType'] == 'MR2' or app['applicationType'] == 'MAPREDUCE':
      common['type'] = 'MAPREDUCE'

      if app['desiredMaps'] is None or app['finishedMaps'] is None:
        app['mapsPercentComplete'] = 100
      if app['desiredReduces'] is None or app['finishedReduces'] is None:
        app['reducesPercentComplete'] = 100

      common['properties'] = {
          'maps_percent_complete': app['mapsPercentComplete'] or 0,
          'reduces_percent_complete': app['reducesPercentComplete'] or 0,
          'finishedMaps': app['finishedMaps'] or 0,
          'finishedReduces': app['finishedReduces'] or 0,
          'desiredMaps': app['desiredMaps'] or 0,
          'desiredReduces': app['desiredReduces'] or 0,
          'durationFormatted': app['durationFormatted'],
          'startTimeFormatted': app['startTimeFormatted'],
          'diagnostics': app['diagnostics'] if app['diagnostics'] else '',
          'tasks': [],
          'metadata': [],
          'counters': []
      }
    elif app['applicationType'] == 'SPARK':
      app['logs'] = job.logs_url if hasattr(job, 'logs_url') else ''
      app['trackingUrl'] = job.trackingUrl if hasattr(job, 'trackingUrl') else ''
      common['type'] = 'SPARK'
      common['properties'] = {
        'metadata': [{'name': name, 'value': value} for name, value in app.iteritems() if name != "url" and name != "killUrl"],
        'executors': []
      }
      if hasattr(job, 'metrics'):
        common['metrics'] = job.metrics
    elif app['applicationType'] == 'YarnV2':
      common['applicationType'] = app.get('type')
      common['properties'] = {
        'startTime': job.startTime,
        'finishTime': job.finishTime,
        'elapsedTime': job.duration,
        'attempts': [],
        'diagnostics': job.diagnostics
      }

    return common


  def action(self, operation, app_ids):
    if operation['action'] == 'kill':
      kills = []
      for app_id in app_ids:
        try:
          response = kill_job(MockDjangoRequest(self.user), job=app_id)
          if isinstance(response, JsonResponse) and json.loads(response.content).get('status') == 0:
             kills.append(app_id)
        except MessageException:
          kills.append(app_id)
      return {'kills': kills, 'status': len(app_ids) - len(kills), 'message': _('Stop signal sent to %s') % kills}
    else:
      return {}


  def logs(self, appid, app_type, log_name, is_embeddable=False):
    logs = ''
    logs_list = []
    try:
      if app_type == 'YarnV2' or app_type == 'MAPREDUCE':
        if log_name == 'default':
          response = job_single_logs(MockDjangoRequest(self.user), job=appid)
          parseResponse = json.loads(response.content)
          logs = parseResponse.get('logs')
          logs_list = parseResponse.get('logsList')
          if logs and len(logs) == 4:
            if app_type == 'YarnV2' and logs[0]: #logs[0] is diagnostics
              logs = logs[0]
            else:
              logs = logs[1]
        else:
          response = job_attempt_logs_json(MockDjangoRequest(self.user), job=appid, name=log_name, is_embeddable=is_embeddable)
          logs = json.loads(response.content).get('log')
      elif app_type == 'SPARK':
        response = job_executor_logs(MockDjangoRequest(self.user), job=appid, name=log_name)
        logs = json.loads(response.content).get('log')
      else:
        logs = None
    except PopupException, e:
      LOG.warn('No task attempt found for logs: %s' % smart_str(e))
    return {'logs': logs, 'logsList': logs_list}


  def profile(self, appid, app_type, app_property, app_filters):
    if app_type == 'MAPREDUCE':
      if app_property == 'tasks':
        return {
          'task_list': YarnMapReduceTaskApi(self.user, appid).apps(app_filters)['apps'],
          'filter_text': ''
        }
      elif app_property == 'metadata':
        return NativeYarnApi(self.user).get_job(jobid=appid).full_job_conf
      elif app_property == 'counters':
        return NativeYarnApi(self.user).get_job(jobid=appid).counters
    elif app_type == 'SPARK':
      if app_property == 'executors':
        return {
          'executor_list': NativeYarnApi(self.user).get_job(jobid=appid).get_executors(),
          'filter_text': ''
        }
    elif app_type == 'YarnV2':
      if app_property == 'attempts':
        return {
          'task_list': NativeYarnApi(self.user).get_job(jobid=appid).job_attempts['jobAttempt'],
          'filter_text': ''
        }
    return {}

  def _api_status(self, status):
    if status in ['NEW', 'NEW_SAVING', 'SUBMITTED', 'ACCEPTED', 'RUNNING']:
      return 'RUNNING'
    elif status == 'SUCCEEDED':
      return 'SUCCEEDED'
    else:
      return 'FAILED' # FAILED, KILLED

class YarnAttemptApi(Api):

  def __init__(self, user, app_id):
    Api.__init__(self, user)
    start = 'appattempt_' if app_id.startswith('appattempt_') else 'attempt_'
    self.app_id = '_'.join(app_id.replace('task_', 'application_').replace(start, 'application_').split('_')[:3])
    self.task_id = '_'.join(app_id.replace(start, 'task_').split('_')[:5])
    self.attempt_id = app_id.split('_')[3]


  def apps(self):
    attempts = NativeYarnApi(self.user).get_task(jobid=self.app_id, task_id=self.task_id).attempts

    return {
      'apps': [self._massage_task(task) for task in attempts],
      'total': len(attempts)
    }


  def app(self, appid):
    task = NativeYarnApi(self.user).get_task(jobid=self.app_id, task_id=self.task_id).get_attempt(self.attempt_id)

    common = self._massage_task(task)
    common['properties'] = {
        'metadata': [],
        'counters': []
    }
    common['properties'].update(self._massage_task(task))

    return common


  def logs(self, appid, app_type, log_name, is_embeddable=False):
    if log_name == 'default':
      log_name = 'stdout'

    task = NativeYarnApi(self.user).get_task(jobid=self.app_id, task_id=self.task_id).get_attempt(self.attempt_id)
    stdout, stderr, syslog = task.get_task_log()

    return {'progress': 0, 'logs': syslog if log_name == 'syslog' else stderr if log_name == 'stderr' else stdout}


  def profile(self, appid, app_type, app_property, app_filters):
    if app_property == 'counters':
      return NativeYarnApi(self.user).get_task(jobid=self.app_id, task_id=self.task_id).get_attempt(self.attempt_id).counters

    return {}


  def _massage_task(self, task):
    return {
        #"elapsedMergeTime" : task.elapsedMergeTime,
        #"shuffleFinishTime" : task.shuffleFinishTime,
        'id': task.appAttemptId if hasattr(task, 'appAttemptId') else '',
        'appAttemptId': task.appAttemptId if hasattr(task, 'appAttemptId') else '',
        'blacklistedNodes': task.blacklistedNodes if hasattr(task, 'blacklistedNodes') else '',
        'containerId' : task.containerId if hasattr(task, 'containerId') else '',
        'diagnostics': task.diagnostics if hasattr(task, 'diagnostics') else '',
        "startTimeFormatted" : task.startTimeFormatted if hasattr(task, 'startTimeFormatted') else '',
        "startTime" : long(task.startTime) if hasattr(task, 'startTime') else '',
        "finishTime" : long(task.finishedTime) if hasattr(task, 'finishedTime') else '',
        "finishTimeFormatted" : task.finishTimeFormatted if hasattr(task, 'finishTimeFormatted') else '',
        "type" : task.type + '_ATTEMPT' if hasattr(task, 'type') else '',
        'nodesBlacklistedBySystem': task.nodesBlacklistedBySystem if hasattr(task, 'nodesBlacklistedBySystem') else '',
        'nodeId': task.nodeId if hasattr(task, 'nodeId') else '',
        'nodeHttpAddress': task.nodeHttpAddress if hasattr(task, 'nodeHttpAddress') else '',
        'logsLink': task.logsLink if hasattr(task, 'logsLink') else '',
        "app_id": self.app_id,
        "task_id": self.task_id,
        'duration' : task.duration if hasattr(task, 'duration') else '',
        'durationFormatted' : task.duration if hasattr(task, 'durationFormatted') else '',
        'state': task.status if hasattr(task, 'status') else ''
    }

class YarnMapReduceTaskApi(Api):

  def __init__(self, user, app_id):
    Api.__init__(self, user)
    self.app_id = '_'.join(app_id.replace('task_', 'application_').split('_')[:3])


  def apps(self, filters):
    filter_params = {
      'task_types': None,
      'task_states': None,
      'task_text': None,
      'jobid': self.app_id,
      'pagenum': 1
    }

    filters = _extract_query_params(filters)

    if filters.get('text'):
      filter_params['task_text'] = filters['text']

    if filters.get('states'):
      task_states = []
      if 'completed' in filters['states']:
        task_states.append('succeeded')
      if 'running' in filters['states']:
        task_states.extend(['running', 'pending'])
      if 'failed' in filters['states']:
        task_states.extend(['running', 'killed'])
      filter_params['task_states'] = task_states

    if filters.get('types') and len(filters.get('types')) == 1:
      filter_params['task_types'] = filters['types'][0]

    tasks = NativeYarnApi(self.user).get_tasks(**filter_params)

    return {
      'apps': [self._massage_task(task) for task in tasks],
      'total': len(tasks)
    }


  def app(self, appid):
    task = NativeYarnApi(self.user).get_task(jobid=self.app_id, task_id=appid)

    common = self._massage_task(task)
    common['properties'] = {
      'attempts': [],
      'metadata': [],
      'counters': []
    }
    common['properties'].update(self._massage_task(task))

    return common


  def logs(self, appid, app_type, log_name, is_embeddable=False):
    if log_name == 'default':
      log_name = 'stdout'

    try:
      response = job_attempt_logs_json(MockDjangoRequest(self.user), job=self.app_id, name=log_name, is_embeddable=is_embeddable)
      logs = json.loads(response.content)['log']
    except PopupException, e:
      LOG.warn('No task attempt found for default logs: %s' % e)
      logs = ''
    return {'progress': 0, 'logs': logs}


  def profile(self, appid, app_type, app_property, app_filters):
    if app_property == 'attempts':
      return {
          'task_list': YarnMapReduceTaskAttemptApi(self.user, appid).apps()['apps'],
      }
    elif app_property == 'counters':
      return NativeYarnApi(self.user).get_task(jobid=self.app_id, task_id=appid).counters

    return {}

  def _massage_task(self, task):
    return {
        'id': task.id,
        "app_id": self.app_id,
        'type': task.type,
        'elapsedTime': task.elapsedTime,
        'progress': task.progress,
        'state': task.state,
        'startTime': task.startTime,
        'successfulAttempt': task.successfulAttempt,
        'finishTime': task.finishTime,
        'apiStatus': self._api_status(task.state),
    }

  def _api_status(self, status):
    if status in ['NEW', 'SUBMITTED', 'ACCEPTED', 'RUNNING']:
      return 'RUNNING'
    elif status == 'SUCCEEDED':
      return 'SUCCEEDED'
    else:
      return 'FAILED' # FAILED, KILLED


class YarnMapReduceTaskAttemptApi(Api):

  def __init__(self, user, app_id):
    Api.__init__(self, user)
    start = 'appattempt_' if app_id.startswith('appattempt_') else 'attempt_'
    self.app_id = '_'.join(app_id.replace('task_', 'application_').replace(start, 'application_').split('_')[:3])
    self.task_id = '_'.join(app_id.replace(start, 'task_').split('_')[:5])
    self.attempt_id = app_id


  def apps(self):
    attempts = NativeYarnApi(self.user).get_task(jobid=self.app_id, task_id=self.task_id).attempts

    return {
      'apps': [self._massage_task(task) for task in attempts],
      'total': len(attempts)
    }


  def app(self, appid):
    task = NativeYarnApi(self.user).get_task(jobid=self.app_id, task_id=self.task_id).get_attempt(self.attempt_id)

    common = self._massage_task(task)
    common['properties'] = {
        'metadata': [],
        'counters': []
    }
    common['properties'].update(self._massage_task(task))

    return common


  def logs(self, appid, app_type, log_name, is_embeddable=False):
    if log_name == 'default':
      log_name = 'stdout'

    task = NativeYarnApi(self.user).get_task(jobid=self.app_id, task_id=self.task_id).get_attempt(self.attempt_id)
    stdout, stderr, syslog = task.get_task_log()

    return {'progress': 0, 'logs': syslog if log_name == 'syslog' else stderr if log_name == 'stderr' else stdout}


  def profile(self, appid, app_type, app_property, app_filters):
    if app_property == 'counters':
      return NativeYarnApi(self.user).get_task(jobid=self.app_id, task_id=self.task_id).get_attempt(self.attempt_id).counters

    return {}


  def _api_status(self, status):
    if status in ['NEW', 'SUBMITTED', 'ACCEPTED', 'RUNNING']:
      return 'RUNNING'
    elif status == 'SUCCEEDED':
      return 'SUCCEEDED'
    else:
      return 'FAILED' # FAILED, KILLED


  def _massage_task(self, task):
    return {
        #"elapsedMergeTime" : task.elapsedMergeTime,
        #"shuffleFinishTime" : task.shuffleFinishTime,
        "assignedContainerId" : task.assignedContainerId if hasattr(task, 'assignedContainerId') else task.amContainerId if hasattr(task, 'amContainerId') else '',
        "progress" : task.progress if hasattr(task, 'progress') else '',
        "elapsedTime" : task.elapsedTime if hasattr(task, 'elapsedTime') else '',
        "state" : task.state if hasattr(task, 'state') else task.appAttemptState if hasattr(task, 'appAttemptState') else '',
        #"elapsedShuffleTime" : task.elapsedShuffleTime,
        #"mergeFinishTime" : task.mergeFinishTime,
        "rack" : task.rack if hasattr(task, 'rack') else '',
        #"elapsedReduceTime" : task.elapsedReduceTime,
        "nodeHttpAddress" : task.nodeHttpAddress if hasattr(task, 'nodeHttpAddress') else '',
        "type" : task.type + '_ATTEMPT' if hasattr(task, 'type') else '',
        "startTime" : task.startTime if hasattr(task, 'startTime') else '',
        "id" : task.id if hasattr(task, 'id') else task.appAttemptId if hasattr(task, 'appAttemptId') else '',
        "finishTime" : task.finishTime if hasattr(task, 'finishTime') else long(task.finishedTime) if hasattr(task, 'finishedTime') else '',
        "app_id": self.app_id,
        "task_id": self.task_id,
        'apiStatus': self._api_status(task.state) if hasattr(task, 'state') else self._api_status(task.appAttemptState) if hasattr(task, 'appAttemptState') else '',
        'host': task.host if hasattr(task, 'host') else '',
        'rpcPort': task.rpcPort if hasattr(task, 'rpcPort') else '',
        'diagnosticsInfo': task.diagnosticsInfo if hasattr(task, 'diagnosticsInfo') else ''
    }


class YarnAtsApi(Api):
  pass


class SparkExecutorApi(Api):

  def __init__(self, user, app_id):
    Api.__init__(self, user)
    self.app_executor_id = app_id
    self.executor_id, self.app_id = app_id.split('_executor_')
    job = NativeYarnApi(self.user).get_job(jobid=self.app_id)
    if job:
      executors = job.get_executors()
      self._executors = [executor for executor in executors if executor['executor_id'] == self.executor_id]
      self.history_server_api = job.history_server_api

  def set_for_test(self, hs_api):
    self.history_server_api = hs_api

  def app(self, appid):
    common = {}

    if self._executors and self._executors[0]:
      common = self._massage_executor(self._executors[0])
      common['properties'] = {
          'metadata': [],
          'counters': []
      }
      common['properties'].update(self._massage_executor(self._executors[0]))

    return common

  def _massage_executor(self, executor):
    return {
       "app_id": self.app_id,
       "type": 'SPARK_EXECUTOR',
       "id": self.app_executor_id,
       "executor_id": executor['executor_id'],
       "address": executor['address'],
       "rdd_blocks": executor['rdd_blocks'],
       "storage_memory": executor['storage_memory'],
       "disk_used": executor['disk_used'],
       "active_tasks": executor['active_tasks'],
       "failed_tasks": executor['failed_tasks'],
       "complete_tasks": executor['complete_tasks'],
       "task_time": executor['task_time'],
       "input": executor['input'],
       "shuffle_read": executor['shuffle_read'],
       "shuffle_write": executor['shuffle_write'],
       "logs": executor['logs']
    }

  def logs(self, appid, app_type, log_name, is_embeddable=False):
    log = ""

    if self._executors and self._executors[0]:
      log = self.history_server_api.download_executor_logs(self.user, self._executors[0], log_name, LOG_OFFSET_BYTES)
    return {
       "logs": log
    }
