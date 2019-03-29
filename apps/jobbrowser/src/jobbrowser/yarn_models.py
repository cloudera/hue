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
import os
import re
import time
import urlparse

from lxml import html

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource
from desktop.lib.view_util import big_filesizeformat, format_duration_in_millis

from hadoop import cluster
from hadoop.yarn.clients import get_log_client

from itertools import izip

from jobbrowser.models import format_unixtime_ms


LOG = logging.getLogger(__name__)


class Application(object):

  def __init__(self, attrs, rm_api=None):
    self.api = rm_api
    for attr in attrs.keys():
      setattr(self, attr, attrs[attr])

    self._fixup()

  @property
  def logs_url(self):
    url = self.trackingUrl or ''
    if url and self.applicationType == 'SPARK':
      url = os.path.join(self.trackingUrl, 'executors')
    return url

  def _fixup(self):
    self.is_mr2 = True
    jobid = self.id
    self.yarnStatus = self.state
    if self.state in ('FINISHED', 'FAILED', 'KILLED'):
      setattr(self, 'status', self.finalStatus)
    else:
      setattr(self, 'status', self.state)
    setattr(self, 'jobId', jobid)
    setattr(self, 'jobId_short', re.sub('(application|job)_', '', self.jobId))
    setattr(self, 'jobName', self.name)
    setattr(self, 'applicationType', self.applicationType)
    setattr(self, 'is_retired', False)
    setattr(self, 'maps_percent_complete', self.progress)
    setattr(self, 'reduces_percent_complete', self.progress)
    setattr(self, 'queueName', self.queue)
    setattr(self, 'priority', '')
    if self.finishedTime == 0:
      finishTime = int(time.time() * 1000)
    else:
      finishTime = self.finishedTime
    if self.startedTime == 0:
      durationInMillis = None
    else:
      durationInMillis = finishTime - self.startedTime
    setattr(self, 'durationInMillis', durationInMillis)
    setattr(self, 'durationFormatted', durationInMillis and format_duration_in_millis(self.durationInMillis))
    setattr(self, 'startTimeMs', self.startedTime)
    setattr(self, 'startTimeFormatted', format_unixtime_ms(self.startedTime))
    setattr(self, 'finishTimeFormatted', format_unixtime_ms(finishTime))
    setattr(self, 'finishedMaps', None)
    setattr(self, 'desiredMaps', None)
    setattr(self, 'finishedReduces', None)
    setattr(self, 'desiredReduces', None)

    for attr in ['preemptedResourceVCores', 'vcoreSeconds', 'memorySeconds', 'diagnostics']:
      if not hasattr(self, attr):
        setattr(self, attr, 'N/A')

    if not hasattr(self, 'acls'):
      setattr(self, 'acls', {})

    # YARN returns a N/A url if it's not set.
    if not hasattr(self, 'trackingUrl') or self.trackingUrl == 'http://N/A':
      self.trackingUrl = None

  def kill(self):
    return self.api.kill(self.id)

  def filter_tasks(self, *args, **kwargs):
    return []


class SparkJob(Application):

  def __init__(self, job, rm_api=None, hs_api=None):
    super(SparkJob, self).__init__(job, rm_api)
    self._resolve_tracking_url()
    if self.status not in ('NEW', 'SUBMITTED', 'ACCEPTED') and hs_api:
      self.history_server_api = hs_api
      self._get_metrics()

  @property
  def logs_url(self):
    log_links = self.history_server_api.get_executors_loglinks(self)
    return log_links['stdout'] if log_links and 'stdout' in log_links else ''

  @property
  def attempt_id(self):
    return self.trackingUrl.strip('/').split('/')[-1]

  def _resolve_tracking_url(self):
    resp = None
    try:
      self._client = HttpClient(self.trackingUrl, logger=LOG)
      self._root = Resource(self._client)
      yarn_cluster = cluster.get_cluster_conf_for_job_submission()
      self._security_enabled = yarn_cluster.SECURITY_ENABLED.get()
      if self._security_enabled:
        self._client.set_kerberos_auth()

      self._client.set_verify(yarn_cluster.SSL_CERT_CA_VERIFY.get())
      actual_url = self._execute(self._root.resolve_redirect_url)

      if actual_url.strip('/').split('/')[-1] == 'jobs':
        actual_url = actual_url.strip('/').replace('jobs', '')
      self.trackingUrl = actual_url
      LOG.debug("SparkJob tracking URL: %s" % self.trackingUrl)
    except Exception, e:
      LOG.warn("Failed to resolve Spark Job's actual tracking URL: %s" % e)
    finally:
      if resp is not None:
        resp.close()

  def _execute(self, function, *args, **kwargs):
    response = None
    try:
      response = function(*args, **kwargs)
    except Exception, e:
      LOG.warn('Spark resolve tracking URL returned a failed response: %s' % e)
    return response

  def _get_metrics(self):
    self.metrics = {}
    try:
      executors = self.history_server_api.executors(self)
      if executors:
        self.metrics['headers'] = [
          _('Executor Id'),
          _('Address'),
          _('RDD Blocks'),
          _('Storage Memory'),
          _('Disk Used'),
          _('Active Tasks'),
          _('Failed Tasks'),
          _('Complete Tasks'),
          _('Task Time'),
          _('Input'),
          _('Shuffle Read'),
          _('Shuffle Write'),
          _('Logs')]
        self.metrics['executors'] = []
        for e in executors:
          self.metrics['executors'].append([
            e.get('id', 'N/A'),
            e.get('hostPort', ''),
            e.get('rddBlocks', ''),
            '%s / %s' % (big_filesizeformat(e.get('memoryUsed', 0)), big_filesizeformat(e.get('maxMemory', 0))),
            big_filesizeformat(e.get('diskUsed', 0)),
            e.get('activeTasks', ''),
            e.get('failedTasks', ''),
            e.get('completedTasks', ''),
            format_duration_in_millis(e.get('totalDuration', 0)),
            big_filesizeformat(e.get('totalInputBytes', 0)),
            big_filesizeformat(e.get('totalShuffleRead', 0)),
            big_filesizeformat(e.get('totalShuffleWrite', 0)),
            e.get('executorLogs', '')
          ])
    except Exception, e:
      LOG.error('Failed to get Spark Job executors: %s' % e)
      # Prevent a nosedive. Don't create metrics if api changes or url is unreachable.

  def get_executors(self):
    executor_list = []
    if hasattr(self, 'metrics') and 'executors' in self.metrics:
      executors = self.metrics['executors']
      headers = ['executor_id', 'address', 'rdd_blocks', 'storage_memory', 'disk_used', 'active_tasks', 'failed_tasks',
                 'complete_tasks', 'task_time', 'input', 'shuffle_read', 'shuffle_write', 'logs']
      for executor in executors:
        executor_data = dict(izip(headers, executor))
        executor_data.update({'id': executor_data['executor_id'] + '_executor_' + self.jobId, 'type': 'SPARK_EXECUTOR'})
        executor_list.append(executor_data)
    return executor_list


class Job(object):

  def __init__(self, api, attrs):
    self.api = api
    self.is_mr2 = True
    for attr in attrs.keys():
      if attr == 'acls':
        # 'acls' are actually not available in the API
        LOG.warn('Not using attribute: %s' % attrs[attr])
      else:
        setattr(self, attr, attrs[attr])

    self._fixup()

    self.progress = None

    # Set MAPS/REDUCES completion percentage
    if hasattr(self, 'mapsTotal'):
      self.desiredMaps = self.mapsTotal
      if self.desiredMaps == 0:
        self.maps_percent_complete = 0
      else:
        self.maps_percent_complete = int(round(float(self.finishedMaps) / self.desiredMaps * 100))
      self.progress = self.maps_percent_complete

    if hasattr(self, 'reducesTotal'):
      self.desiredReduces = self.reducesTotal
      if self.desiredReduces == 0:
        self.reduces_percent_complete = 0
      else:
        self.reduces_percent_complete = int(round(float(self.finishedReduces) / self.desiredReduces * 100))

      if self.desiredReduces > 0:
        if self.progress is not None:
          self.progress = int((self.progress + self.reduces_percent_complete) / 2)
        else:
          self.progress = self.reduces_percent_complete


  def _fixup(self):
    jobid = self.id

    setattr(self, 'status', self.state)
    setattr(self, 'jobName', self.name)
    setattr(self, 'jobId', jobid)
    setattr(self, 'jobId_short', self.jobId.replace('job_', ''))
    setattr(self, 'is_retired', False)
    setattr(self, 'maps_percent_complete', None)
    setattr(self, 'reduces_percent_complete', None)

    if self.finishTime == 0:
      finishTime = int(time.time() * 1000)
    else:
      finishTime = self.finishTime
    if self.startTime == 0:
      durationInMillis = None
    else:
      durationInMillis = finishTime - self.startTime

    setattr(self, 'duration', durationInMillis)
    setattr(self, 'durationFormatted', self.duration and format_duration_in_millis(self.duration))
    setattr(self, 'finishTimeFormatted', format_unixtime_ms(self.finishTime))
    setattr(self, 'startTimeFormatted', format_unixtime_ms(self.startTime))
    setattr(self, 'finishedMaps', self.mapsCompleted)
    setattr(self, 'desiredMaps', 0)
    setattr(self, 'finishedReduces', self.reducesCompleted)
    setattr(self, 'desiredReduces', 0)
    setattr(self, 'applicationType', 'MR2')

  def kill(self):
    return self.api.kill(self.id)

  @property
  def counters(self):
    counters = self.api.counters(self.id)
    if counters:
      return counters['jobCounters']
    else:
      return None

  @property
  def acls(self):
    if not hasattr(self, '_acls'):
      self._acls = dict([(name, self.conf_keys[name]) for name in self.conf_keys if 'acl' in name])
    return self._acls

  @property
  def full_job_conf(self):
    if not hasattr(self, '_full_job_conf'):
      try:
        conf = self.api.conf(self.id)
        self._full_job_conf = conf['conf']
      except TypeError, e:
        LOG.exception('YARN API call failed to return all the data: %s' % conf)
    return self._full_job_conf

  @property
  def conf_keys(self):
    try:
      return dict([(line['name'], line['value']) for line in self.full_job_conf['property']])
    except Exception, e:
      LOG.error('Failed to parse conf_keys from YARN job configuration.')
      return None

  def get_task(self, task_id):
    json = self.api.task(self.id, task_id)['task']
    return Task(self, json)

  def filter_tasks(self, task_types=None, task_states=None, task_text=None):
    tasks = self.api.tasks(self.id).get('tasks', {})
    if tasks and tasks.get('task'):
      return [Task(self, task) for task in tasks.get('task', [])
              if (not task_types or task['type'].lower() in task_types) and
              (not task_states or task['state'].lower() in task_states) and
              (not task_text or task_text.lower() in str(task).lower())]
    else:
      return []

  @property
  def job_attempts(self):
    if not hasattr(self, '_job_attempts'):
      self._job_attempts = self.api.job_attempts(self.id)['jobAttempts']
    return self._job_attempts

class YarnV2Job(Job):
  def __init__(self, api, attrs):
    self.api = api
    for attr in attrs.keys():
      if attr == 'acls':
        # 'acls' are actually not available in the API
        LOG.warn('Not using attribute: %s' % attrs[attr])
      else:
        setattr(self, attr, attrs[attr])

    self._fixup()

  def _fixup(self):
    jobid = self.id

    if self.state in ('FINISHED', 'FAILED', 'KILLED'):
      setattr(self, 'status', self.finalStatus)
    else:
      setattr(self, 'status', self.state)
    setattr(self, 'type', self.applicationType)
    setattr(self, 'applicationType', 'YarnV2')
    setattr(self, 'jobName', self.name)
    setattr(self, 'jobId', jobid)
    setattr(self, 'jobId_short', self.jobId.replace('job_', ''))
    setattr(self, 'is_retired', False)
    setattr(self, 'is_mr2', True)
    setattr(self, 'maps_percent_complete', None)
    setattr(self, 'reduces_percent_complete', None)
    setattr(self, 'finishedMaps', 0)
    setattr(self, 'desiredMaps', 0)
    setattr(self, 'finishedReduces', 0)
    setattr(self, 'desiredReduces', 0)

    if self.finishedTime == 0:
      finishTime = int(time.time() * 1000)
    else:
      finishTime = self.finishedTime
    if self.startedTime == 0:
      durationInMillis = None
    else:
      durationInMillis = finishTime - self.startedTime

    setattr(self, 'duration', durationInMillis)
    setattr(self, 'durationInMillis', durationInMillis)
    setattr(self, 'durationFormatted', self.duration and format_duration_in_millis(self.duration))
    setattr(self, 'finishTimeFormatted', format_unixtime_ms(finishTime))
    setattr(self, 'startTimeFormatted', format_unixtime_ms(self.startedTime))
    setattr(self, 'startTimeMs', self.startTimeFormatted)
    setattr(self, 'startTime', self.startedTime)
    setattr(self, 'finishTime', finishTime)

    try:
      setattr(self, 'assignedContainerId', urlparse.urlsplit(self.amContainerLogs).path.split('/node/containerlogs/')[1].split('/')[0])
    except Exception:
      setattr(self, 'assignedContainerId', '')

  def get_task(self, task_id):
    task = YarnTask(self)
    task.taskId = None
    task.taskAttemptIds = [appAttempt['id'] for appAttempt in self.job_attempts['jobAttempt']]
    return task

  def filter_tasks(self, task_types=None, task_states=None, task_text=None):
    return [self.get_task(0)]

  @property
  def job_attempts(self):
    if not hasattr(self, '_job_attempts'):
      attempts = self.api.appattempts(self.id)['appAttempts']['appAttempt']
      self._job_attempts = {
        'jobAttempt': attempts
      }

    return self._job_attempts

# There's are tasks for Oozie workflow so we create a dummy one.
class YarnTask:
  def __init__(self, job):
    self.job = job

  def get_attempt(self, attempt_id):
    json = self.job.api.appattempts_attempt(self.job.id, attempt_id)
    return YarnV2Attempt(self, json)

class KilledJob(Job):

  def __init__(self, api, attrs):
    self._fixup()

    super(KilledJob, self).__init__(api, attrs)
    if not hasattr(self, 'finishTime'):
      setattr(self, 'finishTime', self.finishedTime)
    if not hasattr(self, 'startTime'):
      setattr(self, 'startTime', self.startedTime)
    self.progress = 100

    super(KilledJob, self)._fixup()

    setattr(self, 'jobId_short', self.jobId.replace('application_', ''))

  def _fixup(self):
    if not hasattr(self, 'mapsCompleted'):
      setattr(self, 'mapsCompleted', 0)
    if not hasattr(self, 'reducesCompleted'):
      setattr(self, 'reducesCompleted', 0)

  @property
  def counters(self):
    return {}

  @property
  def full_job_conf(self):
    return {'property': []}

  def filter_tasks(self, task_types=None, task_states=None, task_text=None):
    return []

  @property
  def job_attempts(self):
    return {'jobAttempt': []}


class Task:

  def __init__(self, job, attrs):
    self.job = job
    if attrs:
      for key, value in attrs.iteritems():
        setattr(self, key, value)
    self.is_mr2 = True

    self._fixup()

  def _fixup(self):
    setattr(self, 'jobId', self.job.jobId)
    setattr(self, 'taskId', self.id)
    setattr(self, 'taskId_short', self.id)
    setattr(self, 'taskType', self.type)
    setattr(self, 'execStartTimeMs', self.startTime)
    setattr(self, 'mostRecentState', self.state)
    setattr(self, 'execStartTimeFormatted', format_unixtime_ms(self.startTime))
    setattr(self, 'execFinishTimeFormatted', format_unixtime_ms(self.finishTime))
    setattr(self, 'startTimeFormatted', format_unixtime_ms(self.startTime))
    setattr(self, 'progress', self.progress)

  @property
  def attempts(self):
    # We can cache as we deal with history server
    if not hasattr(self, '_attempts'):
      task_attempts = self.job.api.task_attempts(self.job.id, self.id)['taskAttempts']
      if task_attempts:
        self._attempts = [Attempt(self, attempt) for attempt in task_attempts['taskAttempt']]
      else:
        self._attempts = []
    return self._attempts

  @property
  def taskAttemptIds(self):
    if not hasattr(self, '_taskAttemptIds'):
      self._taskAttemptIds = [attempt.id for attempt in self.attempts]
    return self._taskAttemptIds

  @property
  def counters(self):
    if not hasattr(self, '_counters'):
      self._counters = self.job.api.task_counters(self.jobId, self.id)['jobTaskCounters']
    return self._counters

  def get_attempt(self, attempt_id):
    json = self.job.api.task_attempt(self.jobId, self.id, attempt_id)['taskAttempt']
    return Attempt(self, json)


class Attempt:

  def __init__(self, task, attrs):
    self.task = task
    if attrs:
      for key, value in attrs.iteritems():
        setattr(self, key, value)
    self.is_mr2 = True
    self._fixup()

  def _fixup(self):
    setattr(self, 'attemptId', self.id)
    setattr(self, 'attemptId_short', self.id)
    setattr(self, 'taskTrackerId', getattr(self, 'assignedContainerId', None))
    setattr(self, 'startTimeFormatted', format_unixtime_ms(self.startTime))
    setattr(self, 'finishTimeFormatted', format_unixtime_ms(self.finishTime))
    setattr(self, 'outputSize', None)
    setattr(self, 'phase', None)
    setattr(self, 'shuffleFinishTimeFormatted', None)
    setattr(self, 'sortFinishTimeFormatted', None)
    setattr(self, 'mapFinishTimeFormatted', None)
    if not hasattr(self, 'diagnostics'):
      self.diagnostics = ''
    if not hasattr(self, 'assignedContainerId'):
      setattr(self, 'assignedContainerId', '')

  @property
  def counters(self):
    if not hasattr(self, '_counters'):
      self._counters = self.task.job.api.task_attempt_counters(self.task.jobId, self.task.id, self.id)['jobTaskAttemptCounters']
    return self._counters

  def get_log_link(self):
    attempt = self.task.job.job_attempts['jobAttempt'][-1]
    log_link = attempt['logsLink']
    if not log_link:
      return log_link, None

    # Generate actual task log link from logsLink url
    if self.task.job.status in ('NEW', 'SUBMITTED', 'RUNNING'):
      logs_path = '/node/containerlogs/'
      node_url, tracking_path = log_link.split(logs_path)
      container_id, user = tracking_path.strip('/').split('/')

      # Replace log path tokens with actual container properties if available
      if hasattr(self, 'nodeHttpAddress') and 'nodeId' in attempt:
        node_url = '%s://%s' % (node_url.split('://')[0], self.nodeHttpAddress)
      container_id = self.assignedContainerId if hasattr(self, 'assignedContainerId') else container_id

      log_link = '%(node_url)s/%(logs_path)s/%(container)s/%(user)s' % {
        'node_url': node_url,
        'logs_path': logs_path.strip('/'),
        'container': container_id,
        'user': user
      }
    else:  # Completed jobs
      if '/node/containerlogs/' in log_link:
        # Applications that use NodeManager API instead of JobHistory API, like new "Oozie Launcher",
        # have `logsLink` URL pointed to NodeManager even for completed jobs
        logs_path = '/node/containerlogs/'

        yarn_cluster = cluster.get_cluster_conf_for_job_submission()
        root_url = yarn_cluster.HISTORY_SERVER_API_URL.get()

        tracking_path = log_link.split(logs_path)[1]
        container_id, user = tracking_path.strip('/').split('/')

        node_url = self.nodeId
        attempt_id = self.id
      else:
        logs_path = '/jobhistory/logs/'
        root_url, tracking_path = log_link.split(logs_path)
        node_url, container_id, attempt_id, user = tracking_path.strip('/').split('/')

        # Replace log path tokens with actual attempt properties if available
        if hasattr(self, 'nodeHttpAddress') and 'nodeId' in attempt:
          node_url = '%s:%s' % (self.nodeHttpAddress.split(':')[0], attempt['nodeId'].split(':')[1])
        container_id = self.assignedContainerId if hasattr(self, 'assignedContainerId') else container_id
        attempt_id = self.attemptId if hasattr(self, 'attemptId') else attempt_id

      log_link = '%(root_url)s/jobhistory/logs/%(node)s/%(container)s/%(attempt)s/%(user)s' % {
        'root_url': root_url,
        'node': node_url,
        'container': container_id,
        'attempt': attempt_id,
        'user': user
      }

    return log_link, user

  def get_log_list(self):
    log_link, user = self.get_log_link()
    if not log_link:
      return []
    params = {
      'doAs': user
    }
    log_link = re.sub('job_[^/]+', str(self.id), log_link)
    root = Resource(get_log_client(log_link), urlparse.urlsplit(log_link)[2], urlencode=False)
    response = root.get('/', params=params)
    links = html.fromstring(response, parser=html.HTMLParser()).xpath('/html/body/table/tbody/tr/td[2]//a/@href')
    parsed_links = map(lambda x: urlparse.urlsplit(x), links)
    return map(lambda x: x and len(x) >= 2 and x[2].split('/')[-2] or '', parsed_links)

  def get_task_log(self, offset=0):
    logs = []

    log_link, user = self.get_log_link()
    if not log_link:
      return ['', '', '']

    for name in ('stdout', 'stderr', 'syslog'):
      link = '/%s/' % name
      if self.type == 'Oozie Launcher' and not self.task.job.status == 'FINISHED': # Yarn currently dumps with 500 error with doas in running state
        params = {}
      else:
        params = {
          'doAs': user
        }

      if int(offset) != 0:
        params['start'] = offset
      else:
        params['start'] = 0

      response = None
      try:
        log_link = re.sub('job_[^/]+', str(self.id), log_link)
        root = Resource(get_log_client(log_link), urlparse.urlsplit(log_link)[2], urlencode=False)
        response = root.get(link, params=params)
        log = html.fromstring(response, parser=html.HTMLParser()).xpath('/html/body/table/tbody/tr/td[2]')[0].text_content()
      except Exception, e:
        log = _('Failed to retrieve log: %s' % e)
        try:
          debug_info = '\nLog Link: %s' % log_link
          if response:
            debug_info += '\nHTML Response: %s' % response
          LOG.error(debug_info)
        except:
          LOG.exception('failed to build debug info')

      logs.append(log)

    return logs + [''] * (3 - len(logs))

class YarnV2Attempt(Attempt):
  def __init__(self, task, attrs):
    self.task = task
    if attrs:
      for key, value in attrs.iteritems():
        setattr(self, key, value)
    self.is_mr2 = True
    self._fixup()

  def _fixup(self):
    if not hasattr(self, 'diagnostics'):
      self.diagnostics = ''
    setattr(self, 'type', 'YarnV2')
    if self.finishedTime == 0:
      finishTime = int(time.time() * 1000)
    else:
      finishTime = self.finishedTime
    if self.startTime == 0:
      durationInMillis = None
    else:
      durationInMillis = finishTime - self.startTime

    setattr(self, 'duration', durationInMillis)
    setattr(self, 'durationInMillis', durationInMillis)
    setattr(self, 'durationFormatted', self.duration and format_duration_in_millis(self.duration))
    setattr(self, 'finishTimeFormatted', format_unixtime_ms(finishTime))
    setattr(self, 'startTimeFormatted', format_unixtime_ms(self.startTime))
    setattr(self, 'status', 'RUNNING' if self.finishedTime == 0 else 'SUCCEEDED')
    setattr(self, 'properties', {})

class Container:

  def __init__(self, attrs):
    if attrs:
      for key, value in attrs['container'].iteritems():
        setattr(self, key, value)
    self.is_mr2 = True

    self._fixup()

  def _fixup(self):
    setattr(self, 'trackerId', self.id)
    setattr(self, 'httpPort', self.nodeId.split(':')[1])
    setattr(self, 'host', self.nodeId.split(':')[0])
    setattr(self, 'lastSeenMs', None)
    setattr(self, 'lastSeenFormatted', '')
    setattr(self, 'totalVirtualMemory', None)
    setattr(self, 'totalPhysicalMemory', self.totalMemoryNeededMB)
    setattr(self, 'availableSpace', None)
    setattr(self, 'failureCount', None)
    setattr(self, 'mapCount', None)
    setattr(self, 'reduceCount', None)
    setattr(self, 'maxMapTasks', None)
    setattr(self, 'maxReduceTasks', None)
    setattr(self, 'taskReports', None)

