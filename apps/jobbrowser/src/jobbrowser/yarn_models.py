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
import re
import time
import urlparse
import urllib2

from lxml import html

from django.utils.translation import ugettext as _

from desktop.lib.rest.resource import Resource
from desktop.lib.view_util import format_duration_in_millis

from hadoop.yarn.clients import get_log_client

from jobbrowser.models import format_unixtime_ms


LOGGER = logging.getLogger(__name__)


class Application(object):

  def __init__(self, attrs, rm_api=None):
    self.api = rm_api
    for attr in attrs.keys():
      setattr(self, attr, attrs[attr])

    self._fixup()

  def _fixup(self):
    self.is_mr2 = True
    jobid = self.id
    if self.state in ('FINISHED', 'FAILED', 'KILLED'):
      setattr(self, 'status', self.finalStatus)
    else:
      setattr(self, 'status', self.state)
    setattr(self, 'jobId', jobid)
    setattr(self, 'jobId_short', re.sub('(application|job)_', '', self.jobId))
    setattr(self, 'jobName', self.name)
    setattr(self, 'is_retired', False)
    setattr(self, 'maps_percent_complete', self.progress)
    setattr(self, 'reduces_percent_complete', self.progress)
    setattr(self, 'queueName', self.queue)
    setattr(self, 'priority', '')
    if self.finishedTime == 0:
      finishTime = int(time.time() * 1000)
    else:
      finishTime = self.finishedTime
    setattr(self, 'durationInMillis', finishTime - self.startedTime)
    setattr(self, 'startTimeMs', self.startedTime)
    setattr(self, 'startTimeFormatted',  format_unixtime_ms(self.startedTime))
    setattr(self, 'finishTimeFormatted',  format_unixtime_ms(finishTime))
    setattr(self, 'finishedMaps', None)
    setattr(self, 'desiredMaps', None)
    setattr(self, 'finishedReduces', None)
    setattr(self, 'desiredReduces', None)
    setattr(self, 'durationFormatted', format_duration_in_millis(self.durationInMillis))

    if not hasattr(self, 'acls'):
      setattr(self, 'acls', {})

  def kill(self):
    return self.api.kill(self.id)


class SparkJob(Application):

  def __init__(self, job):
    super(SparkJob, self).__init__(job)
    self._scrape()

  def _history_application_metrics(self, html_doc):
    metrics = []
    root = html.fromstring(html_doc)
    tables = root.findall('.//table')
    metrics_table = tables[2].findall('.//tr')
    for tr in metrics_table:
        header = tr.find('.//th')
        value = tr.findall('.//td')
        if value:
          header = header.text.strip().replace(':', '')
          value = value[0].text.strip()
          metrics.append({
            'header': header,
            'value': value
          })
    return metrics

  def _scrape(self):
    # XXX: we have to scrape the tracking URL directly because
    # spark jobs don't have a JSON api via YARN or app server
    # see YARN-1530, SPARK-1537 for progress on these apis
    self.scrapedData = {}
    try:
      res = urllib2.urlopen(self.trackingUrl)
      html_doc = res.read()
      if self.trackingUI == 'History':
        self.scrapedData['metrics'] = self._history_application_metrics(html_doc)
    except Exception, e:
      # Prevent a nosedive. Don't create metrics if api changes or url is unreachable.
      self.scrapedData['metrics'] = []


class Job(object):

  def __init__(self, api, attrs):
    self.api = api
    self.is_mr2 = True
    for attr in attrs.keys():
      if attr == 'acls':
        # 'acls' are actually not available in the API
        LOGGER.warn('Not using attribute: %s' % attrs[attr])
      else:
        setattr(self, attr, attrs[attr])

    self._fixup()

  def _fixup(self):
    jobid = self.id

    setattr(self, 'status', self.state)
    setattr(self, 'jobId', jobid)
    setattr(self, 'jobId_short', self.jobId.replace('job_', ''))
    setattr(self, 'is_retired', False)
    setattr(self, 'maps_percent_complete', None)
    setattr(self, 'reduces_percent_complete', None)
    setattr(self, 'duration', self.finishTime - self.startTime)
    setattr(self, 'durationFormatted', format_duration_in_millis(self.duration))
    setattr(self, 'finishTimeFormatted', format_unixtime_ms(self.finishTime))
    setattr(self, 'startTimeFormatted', format_unixtime_ms(self.startTime))
    setattr(self, 'finishedMaps', self.mapsCompleted)
    setattr(self, 'desiredMaps', None)
    setattr(self, 'finishedReduces', self.reducesCompleted)
    setattr(self, 'desiredReduces', None)
    setattr(self, 'applicationType', None)

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
      self._full_job_conf = self.api.conf(self.id)['conf']
    return self._full_job_conf

  @property
  def conf_keys(self):
    return dict([(line['name'], line['value']) for line in self.full_job_conf['property']])

  def get_task(self, task_id):
    json = self.api.task(self.id, task_id)['task']
    return Task(self, json)

  def filter_tasks(self, task_types=None, task_states=None, task_text=None):
    return [Task(self, task) for task in self.api.tasks(self.id).get('tasks', {}).get('task', [])
          if (not task_types or task['type'].lower() in task_types) and
             (not task_states or task['state'].lower() in task_states)]

  @property
  def job_attempts(self):
    if not hasattr(self, '_job_attempts'):
      self._job_attempts = self.api.job_attempts(self.id)['jobAttempts']
    return self._job_attempts


class KilledJob(Job):

  def __init__(self, api, attrs):
    self._fixup()

    super(KilledJob, self).__init__(api, attrs)
    if not hasattr(self, 'finishTime'):
      setattr(self, 'finishTime', self.finishedTime)
    if not hasattr(self, 'startTime'):
      setattr(self, 'startTime', self.startedTime)

    super(KilledJob, self)._fixup()

    setattr(self, 'jobId_short', self.jobId.replace('application_', ''))

  def _fixup(self):
    if not hasattr(self, 'mapsCompleted'):
      setattr(self, 'mapsCompleted', 1)
    if not hasattr(self, 'reducesCompleted'):
      setattr(self, 'reducesCompleted', 1)

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
    setattr(self, 'progress', self.progress / 100)

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
    setattr(self, 'progress', self.progress / 100)
    if not hasattr(self, 'diagnostics'):
      self.diagnostics = ''
    if not hasattr(self, 'assignedContainerId'):
      setattr(self, 'assignedContainerId', '')

  @property
  def counters(self):
    if not hasattr(self, '_counters'):
      self._counters = self.task.job.api.task_attempt_counters(self.task.jobId, self.task.id, self.id)['jobCounters']
    return self._counters

  def get_task_log(self, offset=0):
    logs = []
    attempt = self.task.job.job_attempts['jobAttempt'][-1]
    log_link = attempt['logsLink']
    # Get MR task logs
    if self.assignedContainerId:
      log_link = log_link.replace(attempt['containerId'], self.assignedContainerId)
    if hasattr(self, 'nodeHttpAddress'):
      log_link = log_link.replace(attempt['nodeHttpAddress'].split(':')[0], self.nodeHttpAddress.split(':')[0])

    for name in ('stdout', 'stderr', 'syslog'):
      link = '/%s/' % name
      params = {}
      if int(offset) >= 0:
        params['start'] = offset

      try:
        log_link = re.sub('job_[^/]+', self.id, log_link)
        root = Resource(get_log_client(log_link), urlparse.urlsplit(log_link)[2], urlencode=False)
        response = root.get(link, params=params)
        log = html.fromstring(response).xpath('/html/body/table/tbody/tr/td[2]')[0].text_content()
      except Exception, e:
        log = _('Failed to retrieve log: %s') % e

      logs.append(log)

    return logs + [''] * (3 - len(logs))


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

