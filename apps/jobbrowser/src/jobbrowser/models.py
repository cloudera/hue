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

import datetime
import logging
import lxml.html
import re
import urllib2

from urlparse import urlparse, urlunparse

from desktop.lib.view_util import format_duration_in_millis
from desktop.lib import i18n
from hadoop import job_tracker
from hadoop import confparse
from hadoop.api.jobtracker.ttypes import JobNotFoundException

import hadoop.api.jobtracker.ttypes as ttypes
from desktop.lib.exceptions_renderable import PopupException

from django.utils.translation import ugettext as _


LOGGER = logging.getLogger(__name__)


def can_view_job(username, job):
  acl = get_acls(job).get('mapreduce.job.acl-view-job', '')
  return acl == '*' or username in acl.split(',')

def can_modify_job(username, job):
  acl = get_acls(job).get('mapreduce.job.acl-modify-job', '')
  return acl == '*' or username in acl.split(',')

def get_acls(job):
  if job.is_mr2:
    return job.acls
  else:
    return job.full_job_conf


class JobLinkage(object):
  """
  A thin representation of a job, without much of the details.
  Its purpose is to wrap a JobID to allow us to get further
  information from Hadoop, without instantiating a full Job object
  (which requires talking to Hadoop).
  """
  def __init__(self, jobtracker, jobid):
    """
    JobLinkage(jobtracker, jobid) -> JobLinkage
    The jobid is the jobid string (not the thrift jobid)
    """
    self._jobtracker = jobtracker
    self.jobId = jobid
    self.jobId_short = "_".join(jobid.split("_")[-2:])
    self.is_mr2 = False

  def get_task(self, task_id):
    """Retrieve a TaskInProgress from hadoop."""
    ttask = self._jobtracker.get_task(
                    self._jobtracker.thriftjobid_from_string(self.jobId),
                    self._jobtracker.thrifttaskid_from_string(task_id))
    return Task(ttask, self._jobtracker)

class Job(JobLinkage):
  """
  Creates a Job instance pulled from the job tracker Thrift interface.
  """

  def __getitem__(self, item):
    """
    For backwards-compatibility, resolve job["foo"] as job.foo
    """
    return getattr(self, item)

  @staticmethod
  def from_id(jt, jobid, is_finished=False):
    """
      Returns a Job instance given a job tracker interface and an id. The job tracker interface is typically
      located in request.jt.
    """
    try:
      thriftjob = jt.get_job(jt.thriftjobid_from_string(jobid))
    except JobNotFoundException:
      try:
        thriftjob = jt.get_retired_job(jt.thriftjobid_from_string(jobid))
      except JobNotFoundException, e:
        raise PopupException(_("Could not find job with id %(jobid)s.") % {'jobid': jobid}, detail=e)

    return Job(jt, thriftjob)

  @staticmethod
  def from_thriftjob(jt, thriftjob):
    """
      Returns a Job instance given a job tracker interface and a thriftjob object returned from that job tracker interface.
      The job tracker interface is typically located in request.jt
    """
    return Job(jt, thriftjob)

  def __init__(self, jt, thriftJob):
    """
    Returns a Job instance given a job tracker interface and a thriftjob object returned from that
    job tracker interface.  The job tracker interface is typically located in request.jt
    """
    JobLinkage.__init__(self, jt, thriftJob.jobID.asString)
    self.jt = jt
    self.job = thriftJob
    self.tasks = []
    if self.job.tasks is not None:
      self.tasks = TaskList.from_thriftTaskList(self.job.tasks, jt)

    self.task_map = dict( (task.taskId, task) for task in self.tasks )
    self._counters = None
    self._conf_keys = None
    self._full_job_conf = None
    self._init_attributes()
    self.is_retired = hasattr(thriftJob, 'is_retired')
    self.is_mr2 = False
    self.applicationType = 'MR2'

  @property
  def counters(self):
    if self.is_retired:
      self._counters = {}
    elif self._counters is None:
      rollups = self.jt.get_job_counter_rollups(self.job.jobID)
      # We get back a structure with counter lists for maps, reduces, and total
      # and we need to invert this

      def aggregate_counters(ctrs_from_jt, key, target):
        for group in ctrs_from_jt.groups:
          if group.name not in target:
            target[group.name] = {
              'name': group.name,
              'displayName': group.displayName,
              'counters': {}
              }
          agg_counters = target[group.name]['counters']
          for counter in group.counters.itervalues():
            if counter.name not in agg_counters:
              agg_counters[counter.name] = {
                'name': counter.name,
                'displayName': counter.displayName,
                }
            agg_counters[counter.name][key] = counter.value

      self._counters = {}
      aggregate_counters(rollups.mapCounters, "map", self._counters)
      aggregate_counters(rollups.reduceCounters, "reduce", self._counters)
      aggregate_counters(rollups.jobCounters, "total", self._counters)
    return self._counters

  @property
  def conf_keys(self):
    if self._conf_keys is None:
      self._initialize_conf_keys()
    return self._conf_keys

  @property
  def full_job_conf(self):
    if self._full_job_conf is None:
      self._initialize_conf_keys()
    return self._full_job_conf

  def _init_attributes(self):
    self.queueName = i18n.smart_unicode(self.job.profile.queueName)
    self.jobName = i18n.smart_unicode(self.job.profile.name)
    self.user = i18n.smart_unicode(self.job.profile.user)
    self.mapProgress = self.job.status.mapProgress
    self.reduceProgress = self.job.status.reduceProgress
    self.setupProgress = self.job.status.setupProgress
    self.cleanupProgress = self.job.status.cleanupProgress

    if self.job.desiredMaps == 0:
      maps_percent_complete = 0
    else:
      maps_percent_complete = int(round(float(self.job.finishedMaps) / self.job.desiredMaps * 100))

    self.desiredMaps = self.job.desiredMaps

    if self.job.desiredReduces == 0:
      reduces_percent_complete = 0
    else:
      reduces_percent_complete = int(round(float(self.job.finishedReduces) / self.job.desiredReduces * 100))

    self.desiredReduces = self.job.desiredReduces
    self.maps_percent_complete = maps_percent_complete
    self.finishedMaps = self.job.finishedMaps
    self.finishedReduces = self.job.finishedReduces
    self.reduces_percent_complete = reduces_percent_complete
    self.startTimeMs = self.job.startTime
    self.startTimeFormatted = format_unixtime_ms(self.job.startTime)
    self.launchTimeMs = self.job.launchTime
    self.launchTimeFormatted = format_unixtime_ms(self.job.launchTime)

    self.finishTimeMs = self.job.finishTime
    self.finishTimeFormatted = format_unixtime_ms(self.job.finishTime)
    self.status = self.job.status.runStateAsString
    self.priority = self.job.priorityAsString
    self.jobFile = self.job.profile.jobFile

    finishTime = self.job.finishTime
    if finishTime == 0:
      finishTime = datetime.datetime.now()
    else:
      finishTime = datetime.datetime.fromtimestamp(finishTime / 1000)
    self.duration = finishTime - datetime.datetime.fromtimestamp(self.job.startTime / 1000)

    diff = int(finishTime.strftime("%s")) * 1000 - self.startTimeMs
    self.durationFormatted = format_duration_in_millis(diff)
    self.durationInMillis = diff

  def kill(self):
    self.jt.kill_job(self.job.jobID)

  def get_task(self, id):
    try:
      return self.task_map[id]
    except:
      return JobLinkage.get_task(self, id)

  def filter_tasks(self, task_types=None, task_states=None, task_text=None):
    """
    Filters the tasks of the job.
    Pass in task_type and task_state as sets; None for "all".
    task_text is used to search in the state, mostRecentState, and the ID.
    """
    assert task_types is None or job_tracker.VALID_TASK_TYPES.issuperset(task_types)
    assert task_states is None or job_tracker.VALID_TASK_STATES.issuperset(task_states)

    def is_good_match(t):
      if task_types is not None:
        if t.task.taskID.taskTypeAsString.lower() not in task_types:
          return False

      if task_states is not None:
        if t.state.lower() not in task_states:
          return False

      if task_text is not None:
        tt_lower = task_text.lower()
        if tt_lower not in t.state.lower() and tt_lower not in t.mostRecentState.lower() and tt_lower not in t.task.taskID.asString.lower():
          return False

      return True

    return [ t for t in self.tasks if is_good_match(t) ]

  def _initialize_conf_keys(self):
    if self.is_retired:
      self._conf_keys = {}
      self._full_job_conf = {}
    else:
      conf_keys = [
        'mapred.mapper.class',
        'mapred.reducer.class',
        'mapred.input.format.class',
        'mapred.output.format.class',
        'mapred.input.dir',
        'mapred.output.dir',
        ]
      jobconf = get_jobconf(self.jt, self.jobId)
      self._full_job_conf = jobconf
      self._conf_keys = {}
      for k, v in jobconf.iteritems():
        if k in conf_keys:
          self._conf_keys[dots_to_camel_case(k)] = v


class TaskList(object):
  @staticmethod
  def select(jt, jobid, task_types, task_states, text, count, offset):
    """
    select(jt, jobid, task_types, task_states, text, count, offset) -> TaskList

    Retrieve a TaskList from Hadoop according to the given criteria.
    task_types is a set of job_tracker.VALID_TASK_TYPES. A value to None means everything.
    task_states is a set of job_tracker.VALID_TASK_STATES. A value to None means everything.
    """
    assert task_types is None or job_tracker.VALID_TASK_TYPES.issuperset(task_types)
    assert task_states is None or job_tracker.VALID_TASK_STATES.issuperset(task_states)

    if task_types is None:
      task_types = job_tracker.VALID_TASK_TYPES
    if task_states is None:
      task_states = job_tracker.VALID_TASK_STATES

    tjobid = jt.thriftjobid_from_string(jobid)
    thrift_list = jt.get_task_list(tjobid, task_types, task_states, text, count, offset)
    return TaskList.from_thriftTaskList(thrift_list, jt)

  @staticmethod
  def from_thriftTaskList(thrift_task_list, jobtracker):
    """TaskList.from_thriftTaskList(thrift_task_list, jobtracker) -> TaskList
    """
    if thrift_task_list is None:
      return None
    return TaskList(thrift_task_list, jobtracker)

  def __init__(self, tasklist, jobtracker):
    self.__tasklist = tasklist                  # The thrift task list
    self.__jt = jobtracker
    self.__init_attributes()

  def __init_attributes(self):
    self.__tasksSoFar = [ Task(t, self.__jt) for t in self.__tasklist.tasks ]
    self.__nTotalTasks = self.__tasklist.numTotalTasks

  def __iter__(self):
    return self.__tasksSoFar.__iter__()

  def __len__(self):
    return len(self.__tasksSoFar)

  def __getitem__(self, key):
    return self.__tasksSoFar[key]

  @property
  def tasks(self):
    return self.__tasksSoFar

  @property
  def numTotalTasks(self):
    return self.__nTotalTasks


class Task(object):

  def __getitem__(self, item):
    """
    For backwards-compatibility, resolve job["foo"] as job.foo
    """
    return getattr(self, item)

  def __init__(self, task, jt):
    self.task = task
    self.jt = jt
    self._init_attributes()

    self.attempt_map = {}
    for id, attempt in self.task.taskStatuses.iteritems():
      ta = TaskAttempt(attempt, task=self)
      self.attempt_map[id] = ta

  @property
  def attempts(self):
    return self.attempt_map.values()

  def _init_attributes(self):
    self.taskType = self.task.taskID.taskTypeAsString
    self.taskId = self.task.taskID.asString
    self.taskId_short = "_".join(self.taskId.split("_")[-2:])
    self.startTimeMs = self.task.startTime
    self.startTimeFormatted = format_unixtime_ms(self.task.startTime)
    self.execStartTimeMs = self.task.execStartTime
    self.execStartTimeFormatted = format_unixtime_ms(self.task.execStartTime)
    self.execFinishTimeMs = self.task.execFinishTime
    self.execFinishTimeFormatted = format_unixtime_ms(self.task.execFinishTime)
    self.state = self.task.state
    assert self.state in job_tracker.VALID_TASK_STATES
    self.progress = self.task.progress
    self.taskId = self.task.taskID.asString
    self.jobId = self.task.taskID.jobID.asString
    self.taskAttemptIds = self.task.taskStatuses.keys()
    self.mostRecentState = self.task.mostRecentState
    self.diagnosticMap = self.task.taskDiagnosticData
    self.counters = self.task.counters
    self.failed = self.task.failed
    self.complete = self.task.complete
    self.is_mr2 = False

  def get_attempt(self, id):
    """
    Returns a TaskAttempt for a given id.
    """
    return self.attempt_map[id]


class TaskAttempt(object):

  def __getitem__(self, item):
    """
    For backwards-compatibility, resolve task["foo"] as task.foo.
    """
    return getattr(self, item)

  def __init__(self, task_attempt, task):
    assert task_attempt is not None
    self.task_attempt = task_attempt
    self.task = task
    self._init_attributes();

  def _init_attributes(self):
    self.taskType = self.task_attempt.taskID.taskID.taskTypeAsString
    self.attemptId = self.task_attempt.taskID.asString
    self.attemptId_short = "_".join(self.attemptId.split("_")[-2:])
    self.startTimeMs = self.task_attempt.startTime
    self.startTimeFormatted = format_unixtime_ms(self.task_attempt.startTime)
    self.finishTimeMs = self.task_attempt.finishTime
    self.finishTimeFormatted = format_unixtime_ms(self.task_attempt.finishTime)
    self.state = self.task_attempt.stateAsString.lower()
    self.taskTrackerId = self.task_attempt.taskTracker
    self.phase = self.task_attempt.phaseAsString
    self.progress = self.task_attempt.progress
    self.outputSize = self.task_attempt.outputSize
    self.shuffleFinishTimeMs = self.task_attempt.shuffleFinishTime
    self.shuffleFinishTimeFormatted = format_unixtime_ms(self.task_attempt.shuffleFinishTime)
    self.sortFinishTimeMs = self.task_attempt.sortFinishTime
    self.sortFinishTimeFormatted = format_unixtime_ms(self.task_attempt.sortFinishTime)
    self.mapFinishTimeMs = self.task_attempt.mapFinishTime # DO NOT USE, NOT VALID IN 0.20
    self.mapFinishTimeFormatted = format_unixtime_ms(self.task_attempt.mapFinishTime)
    self.counters = self.task_attempt.counters
    self.is_mr2 = False

  def get_tracker(self):
    try:
      tracker = Tracker.from_name(self.task.jt, self.taskTrackerId)
      return tracker
    except ttypes.TaskTrackerNotFoundException, e:
      LOGGER.warn("Tracker %s not found: %s" % (self.taskTrackerId, e))
      if LOGGER.isEnabledFor(logging.DEBUG):
        all_trackers = self.task.jt.all_task_trackers()
        for t in all_trackers.trackers:
          LOGGER.debug("Available tracker: %s" % (t.trackerName,))
      raise ttypes.TaskTrackerNotFoundException(
                          _("Cannot look up TaskTracker %(id)s.") % {'id': self.taskTrackerId})

  def get_task_log(self):
    """
    get_task_log(task_id) -> (stdout_text, stderr_text, syslog_text)

    Retrieve the task log from the TaskTracker, at this url:
      http://<tracker_host>:<port>/tasklog?taskid=<attempt_id>
    Optional query string:
      &filter=<source>  : where <source> is 'syslog', 'stdout', or 'stderr'.
      &start=<offset>   : specify the start offset of the log section, when using a filter.
      &end=<offset>     : specify the end offset of the log section, when using a filter.
    """
    tracker = self.get_tracker()
    url = urlunparse(('http',
                      '%s:%s' % (tracker.host, tracker.httpPort),
                      'tasklog',
                      None,
                      'attemptid=%s' % (self.attemptId,),
                      None))
    LOGGER.info('Retrieving %s' % (url,))
    try:
      data = urllib2.urlopen(url)
    except urllib2.URLError:
      raise urllib2.URLError(_("Cannot retrieve logs from TaskTracker %(id)s.") % {'id': self.taskTrackerId})

    et = lxml.html.parse(data)
    log_sections = et.findall('body/pre')
    logs = [section.text or '' for section in log_sections]
    if len(logs) < 3:
      LOGGER.warn('Error parsing task attempt log for %s at "%s". Found %d (not 3) log sections' %
                  (self.attemptId, url, len(log_sections)))
      err = _("Hue encountered an error while retrieving logs from '%s'.") % (url,)
      logs += [err] * (3 - len(logs))
    return logs


class Tracker(object):

  def __getitem__(self, item):
    """
    For backwards-compatibility, resolve job["foo"] as job.foo.
    """
    return getattr(self, item)

  @staticmethod
  def from_name(jt, trackername):
    return Tracker(jt.task_tracker(trackername))

  def __init__(self, thrifttracker):
    self.tracker = thrifttracker
    self._init_attributes();

  def _init_attributes(self):
    self.trackerId = self.tracker.trackerName
    self.httpPort = self.tracker.httpPort
    self.host = self.tracker.host
    self.lastSeenMs = self.tracker.lastSeen
    self.lastSeenFormatted = format_unixtime_ms(self.tracker.lastSeen)
    self.totalVirtualMemory = self.tracker.totalVirtualMemory
    self.totalPhysicalMemory = self.tracker.totalPhysicalMemory
    self.availableSpace = self.tracker.availableSpace
    self.failureCount = self.tracker.failureCount
    self.mapCount = self.tracker.mapCount
    self.reduceCount = self.tracker.reduceCount
    self.maxMapTasks = self.tracker.maxMapTasks
    self.maxReduceTasks = self.tracker.maxReduceTasks
    self.taskReports = self.tracker.taskReports
    self.is_mr2 = False


class Cluster(object):

  def __getitem__(self, item):
    """
    For backwards-compatibility, resolve job["foo"] as job.foo
    """
    return getattr(self, item)

  def __init__(self, jt):
    self.status = jt.cluster_status()
    self._init_attributes();

  def _init_attributes(self):
    self.mapTasksInProgress = self.status.mapTasks
    self.reduceTasksInProgress = self.status.reduceTasks
    self.maxMapTasks = self.status.maxMapTasks
    self.maxReduceTasks = self.status.maxReduceTasks
    self.usedHeapMemory = self.status.usedMemory
    self.maxHeapMemory = self.status.maxMemory
    self.clusterStartTimeMs = self.status.startTime
    self.clusterStartTimeFormatted = format_unixtime_ms(self.status.startTime)
    self.identifier = self.status.identifier
    self.taskTrackerExpiryInterval = self.status.taskTrackerExpiryInterval
    self.totalJobSubmissions = self.status.totalSubmissions
    self.state = self.status.stateAsString
    self.numActiveTrackers = self.status.numActiveTrackers
    self.activeTrackerNames = self.status.activeTrackerNames
    self.numBlackListedTrackers = self.status.numBlacklistedTrackers
    self.blacklistedTrackerNames = self.status.blacklistedTrackerNames
    self.hostname = self.status.hostname
    self.httpPort = self.status.httpPort


def get_jobconf(jt, jobid):
  """
  Returns a dict representation of the jobconf for the job corresponding
  to jobid. filter_keys is an optional list of configuration keys to filter on.
  """
  jid = jt.thriftjobid_from_string(jobid)
  # This will throw if the the jobconf can't be found
  xml_data = jt.get_job_xml(jid)
  return confparse.ConfParse(xml_data)

def format_unixtime_ms(unixtime):
  """
  Format a unix timestamp in ms to a human readable string
  """
  if unixtime:
    return str(datetime.datetime.fromtimestamp(unixtime/1000).strftime("%x %X %Z"))
  else:
    return ""

DOTS = re.compile("\.([a-z])")
def dots_to_camel_case(dots):
  """
  Takes a string delimited with periods and returns a camel-case string.
  Example: dots_to_camel_case("foo.bar.baz") //returns fooBarBaz
  """
  def return_upper(match):
    return match.groups()[0].upper()
  return str(DOTS.sub(return_upper, dots))

def get_path(hdfs_url):
  """
  Returns the path component of an HDFS url.
  """
  # urlparse is lame, and only "uses_netloc" for a certain
  # set of protocols.  So we replace hdfs with gopher:
  if hdfs_url.startswith("hdfs://"):
    gopher_url = "gopher://" + hdfs_url[7:]
    path = urlparse(gopher_url)[2] # path
    return path
  else:
    return hdfs_url
