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
#
# Django-side implementation of the JobTracker plugin interface

from desktop.lib import thrift_util
from desktop.lib.conf import validate_port
from desktop.lib.exceptions import StructuredException
from desktop.lib.thrift_util import fixup_enums

from hadoop.api.jobtracker import Jobtracker
from hadoop.api.jobtracker.ttypes import ThriftJobID, ThriftTaskAttemptID, \
    ThriftTaskType, ThriftTaskPhase, ThriftTaskID, \
    ThriftTaskState, ThriftJobState, ThriftJobPriority, TaskNotFoundException, \
    JobTrackerState, JobNotFoundException, ThriftTaskQueryState
from hadoop.api.common.ttypes import RequestContext
from thrift.transport import TTransport

import threading

VALID_TASK_STATES = set(["succeeded", "failed", "running", "pending", "killed"])
VALID_TASK_TYPES = set(["map", "reduce", "job_cleanup", "job_setup"])

# timeout (seconds) for thrift calls to jobtracker
JT_THRIFT_TIMEOUT = 15

DEFAULT_USER = "webui"

def test_jt_configuration(cluster):
  """Test FS configuration. Returns list of (confvar, error)."""
  err = validate_port(cluster.JT_THRIFT_PORT)
  if err:
    return err

  try:
    jt = LiveJobTracker.from_conf(cluster)
    jt.runtime_info()
  except TTransport.TTransportException:
    msg = 'Failed to contact JobTracker plugin at %s:%s.' % \
          (cluster.HOST.get(), cluster.JT_THRIFT_PORT.get())
    return [ (cluster, msg) ]
  return []


class LiveJobTracker(object):
  """
  Connects to a JobTracker over our Thrift interface.
  At the moment, doesn't handle Thrift errors gracefully.

  In particular, if Thrift returns None for anything, this will throw.
  """

  def __init__(self, host,
               thrift_port,
               logical_name=None,
               security_enabled=False,
               kerberos_principal="mapred"):
    self.client = thrift_util.get_client(
      Jobtracker.Client, host, thrift_port,
      service_name="Hadoop MR JobTracker HUE Plugin",
      use_sasl=security_enabled,
      kerberos_principal=kerberos_principal,
      timeout_seconds=JT_THRIFT_TIMEOUT)
    self.host = host
    self.thrift_port = thrift_port
    self.logical_name = logical_name
    self.security_enabled = security_enabled
    # We allow a single LiveJobTracker to be used across multiple
    # threads by restricting the stateful components to a thread
    # thread-local.
    self.thread_local = threading.local()
    self.setuser(DEFAULT_USER)

  @classmethod
  def from_conf(cls, conf):
    return cls(
      conf.HOST.get(),
      conf.JT_THRIFT_PORT.get(),
      conf.LOGICAL_NAME.get(),
      security_enabled=conf.SECURITY_ENABLED.get(),
      kerberos_principal=conf.JT_KERBEROS_PRINCIPAL.get())

  def thriftjobid_from_string(self, jobid):
    """The jobid looks like this: job_201001301455_0001"""
    _, tid, jid = jobid.split("_")
    return ThriftJobID(tid, int(jid), jobid)

  def thriftattemptid_from_string(self, attemptid):
    """The attemptid looks like this: attempt_201001301455_0001_m_000007_0"""
    _, meat = attemptid.split('_', maxsplit=1)
    taskid, aid = meat.rsplit('_', maxsplit=1)
    return ThriftTaskAttemptID(self.thrifttaskid_from_string(taskid), int(aid))

  def thrifttaskid_from_string(self, taskid_str):
    """The taskid_str looks like this: task_201001301455_0001_m_000007"""
    TASK_TYPE_MAP = { "m" : ThriftTaskType.MAP,
                      "r" : ThriftTaskType.REDUCE }
    _, tracker, jid, tasktype, tid = taskid_str.split('_')
    return ThriftTaskID(ThriftJobID(tracker, int(jid)),
                        TASK_TYPE_MAP[tasktype],
                        int(tid))

  def _fixup_tasktracker(self, tracker):
    """
    Adds string representations of enums to a ThirftTaskTrackerStatus
    """
    if not tracker.taskReports:
      return tracker
    for tts in tracker.taskReports:
      fixup_enums(tts.taskID.taskID, {"taskType":ThriftTaskType})
      self._fixup_taskstatus(tts)


  def _fixup_taskstatus(self, taskstatus):
    """
    Adds string representations of enums to a ThriftTaskInProgress
    """
    fixup_enums(taskstatus, {"state":ThriftTaskState, "phase":ThriftTaskPhase})
    fixup_enums(taskstatus.taskID.taskID, {"taskType":ThriftTaskType})

  def _fixup_task_state(self, tip):
    """
    Determine overall state of a task.
    """
    if tip.complete:
      tip.state = "succeeded"
    elif tip.failed:
      if not tip.execStartTime:
        tip.state = "killed"
      else:
        tip.state = "failed"
    elif tip.execStartTime:
      tip.state = "running"
    else:
      tip.state = "pending"

    global VALID_TASK_STATES
    assert tip.state in VALID_TASK_STATES

  def _fixup_job(self, job):
    """
    Run through all the enums in a job and add their string variant
    """
    fixup_enums(job.status, {"runState":ThriftJobState, "priority":ThriftJobPriority})
    fixup_enums(job, {"priority":ThriftJobPriority})
    if job.tasks is not None:
      for tip in job.tasks.tasks:
        fixup_enums(tip.taskID, {"taskType":ThriftTaskType})
        self._fixup_task_state(tip)
        for taskstatus in tip.taskStatuses.values():
          self._fixup_taskstatus(taskstatus)

  def _fixup_task_in_progress(self, tip):
    fixup_enums(tip.taskID, {"taskType": ThriftTaskType})
    self._fixup_task_state(tip)
    for taskstatus in tip.taskStatuses.values():
      self._fixup_taskstatus(taskstatus)

  def _fixup_retired_job(self, job):
    job.is_retired = True

  def setuser(self, user):
    # Hadoop determines the groups the user belongs to on the server side.
    self.thread_local.request_context = RequestContext()
    if not self.thread_local.request_context.confOptions:
      self.thread_local.request_context.confOptions = {}
    self.thread_local.request_context.confOptions['effective_user'] = user
    self.thread_local.user = user

  @property
  def user(self):
    return self.thread_local.user

  @property
  def request_context(self):
    # Here for backwards-compatibility.
    return self.thread_local.request_context


  def queues(self):
    """
    Returns a ThriftJobQueueList
    """
    qs = self.client.getQueues(self.thread_local.request_context)
    return qs

  def cluster_status(self):
    """
    Returns a ThriftClusterStatus
    """
    cs = self.client.getClusterStatus(self.thread_local.request_context)
    fixup_enums(cs, {"state":JobTrackerState})
    return cs

  def runtime_info(self):
    """
    Returns a RuntimeInfo
    """
    return self.client.getRuntimeInfo(self.thread_local.request_context)

  def all_task_trackers(self):
    """
    Returns a ThriftTaskTrackerStatusList
    """
    tts = self.client.getAllTrackers(self.thread_local.request_context)
    for tracker in tts.trackers:
      self._fixup_tasktracker(tracker)
    return tts

  def active_trackers(self):
    """
    Returns a ThriftTaskTrackerStatusList
    """
    tts = self.client.getActiveTrackers(self.thread_local.request_context)
    for tracker in tts.trackers:
      self._fixup_tasktracker(tracker)
    return tts

  def blacklisted_trackers(self):
    """
    Returns a ThriftTaskTrackerStatusList
    """
    tts = self.client.getBlacklistedTrackers(self.thread_local.request_context)
    for tracker in tts.trackers:
      self._fixup_tasktracker(tracker)
    return tts

  def task_tracker(self, name):
    """
    Returns a ThriftTaskTrackerStatus or None
    """
    tracker = self.client.getTracker(self.thread_local.request_context, name)
    if not tracker:
      return None
    self._fixup_tasktracker(tracker)
    return tracker

  def get_job(self, jobid):
    """
    Returns a ThriftJobInProgress (including task info)
    """
    try:
      job = self.client.getJob(self.thread_local.request_context, jobid)
    except JobNotFoundException, e:
      raise StructuredException(code="JT_JOB_NOT_FOUND", message="Could not find job %s on JobTracker." % jobid.asString, data=jobid)
    self._fixup_job(job)
    return job

  def running_jobs(self):
    """
    Returns a ThriftJobList (does not include task info)
    """
    joblist = self.client.getRunningJobs(self.thread_local.request_context)
    for job in joblist.jobs:
      self._fixup_job(job)
    return joblist

  def completed_jobs(self):
    """
    Returns a ThriftJobList (does not include task info)
    """
    joblist = self.client.getCompletedJobs(self.thread_local.request_context)
    for job in joblist.jobs:
      self._fixup_job(job)
    return joblist

  def get_retired_job(self, jobid):
    """
    Returns a ThriftJobInProgress (does not include task info and most of the job information)
    """
    try:
      job = self.client.getRetiredJob(self.thread_local.request_context, jobid)
    except JobNotFoundException, e:
        raise StructuredException(code="JT_JOB_NOT_FOUND", message="Could not find job %s on JobTracker." % jobid.asString, data=jobid)
    self._fixup_job(job)
    self._fixup_retired_job(job)
    return job

  def retired_jobs(self, status=None):
    """
    Returns a ThriftJobStatusList (does not include task info and most of the job information)
    """
    joblist = self.client.getRetiredJobs(self.thread_local.request_context, status)
    for job in joblist.jobs:
      self._fixup_job(job)
      self._fixup_retired_job(job)
    return joblist

  def failed_jobs(self):
    """
    Returns a ThriftJobList (does not include task info)
    """
    joblist = self.client.getFailedJobs(self.thread_local.request_context)
    for job in joblist.jobs:
      self._fixup_job(job)
    return joblist

  def killed_jobs(self):
    """
    Returns a ThriftJobList (does not include task info)
    """
    joblist = self.client.getKilledJobs(self.thread_local.request_context)
    for job in joblist.jobs:
      self._fixup_job(job)
    return joblist

  def all_jobs(self):
    """
    Returns a ThriftJobList (does not include task info)
    """
    joblist = self.client.getAllJobs(self.thread_local.request_context)
    for job in joblist.jobs:
      self._fixup_job(job)
    return joblist

  def get_job_count_by_user(self, user):
    """
    Returns a ThriftUserJobCounts.
    """
    return self.client.getUserJobCounts(self.thread_local.request_context, user)

  def get_job_counters(self, jobid):
    """
    Returns a ThriftGroupList
    """
    return self.client.getJobCounters(self.thread_local.request_context, jobid)

  def get_job_counter_rollups(self, jobid):
    """
    Returns a ThriftGroupList
    """
    return self.client.getJobCounterRollups(self.thread_local.request_context, jobid)


  def get_task_list(self, jobid, task_types, task_states, task_text, count, offset):
    """
    Return a ThriftTaskInProgressList
    """
    # Translate task_states and task_types to their thrift variants
    ttask_types = [ ThriftTaskType._NAMES_TO_VALUES[x.upper()] for x in task_types ]
    ttask_states = [ ThriftTaskQueryState._NAMES_TO_VALUES[x.upper()] for x in task_states ]
    tip_list = self.client.getTaskList(
          self.thread_local.request_context, jobid, ttask_types, ttask_states, task_text, count, offset)

    for tip in tip_list.tasks:
      self._fixup_task_in_progress(tip)
    return tip_list

  def get_task(self, jobid, taskid):
    """Return a ThriftTaskInProgress"""
    try:
      tip = self.client.getTask(self.thread_local.request_context, taskid)
    except JobNotFoundException, e:
      raise StructuredException(code="JT_JOB_NOT_FOUND", message="Could not find job %s on JobTracker." % jobid.asString, data=jobid)
    except TaskNotFoundException, e:
      raise StructuredException(code="JT_TASK_NOT_FOUND", message="Could not find task %s on JobTracker." % taskid.asString, data=taskid)
    self._fixup_task_in_progress(tip)
    return tip

  def get_current_time(self):
    """
    Returns an integer timestamp
    """
    return self.client.getCurrentTime(self.thread_local.request_context)

  def get_job_xml(self, jobid):
    """
    Returns a string representation of the job XML
    """
    return self.client.getJobConfXML(self.thread_local.request_context, jobid)

  def kill_job(self, jobid):
    """
    Kill a job
    """
    return self.client.killJob(self.thread_local.request_context, jobid)

  def kill_task_attempt(self, attemptid):
    """
    Kill a task attempt
    """
    return self.client.killTaskAttempt(self.thread_local.request_context, attemptid)

  def set_job_priority(self, jobid, priority):
    """
    Set a job's priority
    """
    return self.client.setJobPriority(self.thread_local.request_context, jobid, priority)

  def get_delegation_token(self, principal):
    return self.client.getDelegationToken(self.thread_local.request_context, principal).delegationTokenBytes
