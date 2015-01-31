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

from desktop.lib.paginator import Paginator
from django.utils.functional import wraps
from hadoop import cluster
from hadoop.api.jobtracker.ttypes import ThriftJobPriority, TaskTrackerNotFoundException, ThriftJobState

import hadoop.yarn.history_server_api as history_server_api
import hadoop.yarn.mapreduce_api as mapreduce_api
import hadoop.yarn.resource_manager_api as resource_manager_api
import hadoop.yarn.node_manager_api as node_manager_api

from jobbrowser.conf import SHARE_JOBS
from jobbrowser.models import Job, JobLinkage, TaskList, Tracker
from jobbrowser.yarn_models import Application, Job as YarnJob, KilledJob as KilledYarnJob, Container
from jobbrowser.yarn_models import SparkJob
from hadoop.cluster import get_next_ha_mrcluster, get_next_ha_yarncluster
from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)

_DEFAULT_OBJ_PER_PAGINATION = 10


def get_api(user, jt):
  if cluster.is_yarn():
    return YarnApi(user)
  else:
    return JtApi(jt)


def jt_ha(funct):
  """
  Support JT plugin HA by trying other MR cluster.

  This modifies the cached JT and so will happen just once by failover.
  """
  def decorate(api, *args, **kwargs):
    try:
      return funct(api, *args, **kwargs)
    except Exception, ex:
      if 'Could not connect to' in str(ex):
        LOG.info('JobTracker not available, trying JT plugin HA: %s.' % ex)
        jt_ha = get_next_ha_mrcluster()
        if jt_ha is not None:
          if jt_ha[1].host == api.jt.host:
            raise ex
          config, api.jt = jt_ha
          return funct(api, *args, **kwargs)
      raise ex
  return wraps(funct)(decorate)


def rm_ha(funct):
  """
  Support RM HA by trying other RM API.
  """
  def decorate(api, *args, **kwargs):
    try:
      return funct(api, *args, **kwargs)
    except Exception, ex:
      ex_message = str(ex)
      if 'Connection refused' in ex_message or 'standby RM' in ex_message:
        LOG.info('Resource Manager not available, trying another RM: %s.' % ex)
        rm_ha = get_next_ha_yarncluster()
        if rm_ha is not None:
          if rm_ha[1].url == api.resource_manager_api.url:
            raise ex
          config, api.resource_manager_api = rm_ha
          return funct(api, *args, **kwargs)
      raise ex
  return wraps(funct)(decorate)


class JobBrowserApi(object):

  def paginate_task(self, task_list, pagenum):
    paginator = Paginator(task_list, _DEFAULT_OBJ_PER_PAGINATION)
    return paginator.page(pagenum)


class JtApi(JobBrowserApi):
  def __init__(self, jt):
    self.jt = jt

  @jt_ha
  def get_job_link(self, jobid):
    return JobLinkage(self.jt, jobid)

  @jt_ha
  def get_job(self, jobid):
    return Job.from_id(jt=self.jt, jobid=jobid)

  @jt_ha
  def get_jobs(self, user, **kwargs):
    """
    Returns an array of jobs where the returned
    jobs are matched by the provided filter arguments.

    If a filter argument is in kwargs it will supersede the same argument
    in the request object.

    Filter arguments may be jobid, pools, user, tasks, text and state.

    Filter by user ownership if check_permission is set to true.
    """
    jobfunc = {
       "completed" : (self.jt.completed_jobs, ThriftJobState.SUCCEEDED),
       # Succeeded and completed are synonyms here.
       "succeeded" : (self.jt.completed_jobs, ThriftJobState.SUCCEEDED),
       "running" : (self.jt.running_jobs, ThriftJobState.RUNNING),
       "failed" : (self.jt.failed_jobs, ThriftJobState.FAILED),
       "killed" : (self.jt.killed_jobs, ThriftJobState.KILLED),
       "all" : (self.jt.all_jobs, None),
       None : (self.jt.all_jobs, None)
    }

    selection = kwargs.pop('state')
    retired = kwargs.pop('retired')

    jobs = jobfunc[selection][0]().jobs

    if retired:
      jobs += self.jt.retired_jobs(jobfunc[selection][1]).jobs

    return self.filter_jobs(user, jobs, **kwargs)

  @jt_ha
  def filter_jobs(self, user, jobs, **kwargs):
    check_permission = not SHARE_JOBS.get() and not user.is_superuser

    return [Job.from_thriftjob(self.jt, j)
            for j in self._filter_jobs(jobs, **kwargs)
            if not check_permission or user.is_superuser or j.profile.user == user.username]

  def _filter_jobs(self, jobs, username=None, text=None):
    def predicate(job):
      """
      Return True if a ThriftJobInProgress structure matches the supplied filters.

      If a filter argument is None, everything matches it.
      """
      if username and username not in job.profile.user:
        return False

      if text:
        search = text.lower()
        # These fields are chosen to match those displayed by the JT UI
        saw_text = False
        for t in [job.profile.user,
                  job.profile.name,
                  job.jobID.asString,
                  job.profile.queueName,
                  job.priorityAsString
                  ]:
          if search in t.lower():
            saw_text = True
            break

        if not saw_text:
          return False

      return True

    return filter(predicate, jobs)

  @jt_ha
  def get_tasks(self, jobid, **filters):
    return TaskList.select(self.jt,
                           jobid,
                           filters['task_types'],
                           filters['task_states'],
                           filters['task_text'],
                           _DEFAULT_OBJ_PER_PAGINATION,
                           _DEFAULT_OBJ_PER_PAGINATION * (filters['pagenum'] - 1))

  @jt_ha
  def get_tracker(self, trackerid):
    return Tracker.from_name(self.jt, trackerid)


class YarnApi(JobBrowserApi):
  """
  List all the jobs with Resource Manager API.
  Get running single job information with MapReduce API.
  Get finished single job information with History Server API.

  The trick is that we use appid when the job is running and jobid when it is finished.
  We also suppose that each app id has only one MR job id.
  e.g. job_1355791146953_0105, application_1355791146953_0105

  A better alternative might be to call the Resource Manager instead of relying on the type of job id.
  The perfect solution would be to have all this logic embedded
  """
  def __init__(self, user):
    self.user = user
    self.resource_manager_api = resource_manager_api.get_resource_manager()
    self.mapreduce_api = mapreduce_api.get_mapreduce_api()
    self.history_server_api = history_server_api.get_history_server_api()

  def get_job_link(self, job_id):
    return self.get_job(job_id)

  @rm_ha
  def get_jobs(self, user, **kwargs):
    state_filters = {'running': 'UNDEFINED', 'completed': 'SUCCEEDED', 'failed': 'FAILED', 'killed': 'KILLED', }
    filters = {}

    if kwargs['username']:
      filters['user'] = kwargs['username']
    if kwargs['state'] and kwargs['state'] != 'all':
      filters['finalStatus'] = state_filters[kwargs['state']]

    json = self.resource_manager_api.apps(**filters)
    if type(json) == str and 'This is standby RM' in json:
      raise Exception(json)

    if json['apps']:
      jobs = [Application(app) for app in json['apps']['app']]
    else:
      return []

    if kwargs['text']:
      text = kwargs['text'].lower()
      jobs = filter(lambda job:
                    text in job.name.lower() or
                    text in job.id.lower() or
                    text in job.user.lower() or
                    text in job.queue.lower(), jobs)

    return self.filter_jobs(user, jobs)

  def filter_jobs(self, user, jobs, **kwargs):
    check_permission = not SHARE_JOBS.get() and not user.is_superuser

    return filter(lambda job:
                  not check_permission or
                  user.is_superuser or
                  job.user == user.username, jobs)

  @rm_ha
  def get_job(self, jobid):
    try:
      # App id
      jobid = jobid.replace('job', 'application')
      job = self.resource_manager_api.app(jobid)['app']

      if job['state'] == 'ACCEPTED':
        raise ApplicationNotRunning(jobid, job)
      elif job['state'] == 'KILLED':
        return KilledYarnJob(self.resource_manager_api, job)

      if job.get('applicationType') == 'SPARK':
        job = YarnJob(job)
      elif job.get('applicationType') == 'MAPREDUCE':
        jobid = jobid.replace('application', 'job')

        if job['state'] in ('NEW', 'SUBMITTED', 'ACCEPTED', 'RUNNING'):
          json = self.mapreduce_api.job(self.user, jobid)
          job = YarnJob(self.mapreduce_api, json['job'])
        else:
          json = self.history_server_api.job(self.user, jobid)
          job = YarnJob(self.history_server_api, json['job'])
      else:
        job = Application(job, self.resource_manager_api)
    except ApplicationNotRunning, e:
      raise e
    except Exception, e:
      if 'NotFoundException' in str(e):
        raise JobExpired(jobid)
      else:
        raise PopupException('Job %s could not be found: %s' % (jobid, e), detail=e)

    return job

  def get_tasks(self, jobid, **filters):
    filters.pop('pagenum')
    return self.get_job(jobid).filter_tasks(**filters)

  def get_task(self, jobid, task_id):
    return self.get_job(jobid).task(task_id)

  def get_tracker(self, node_manager_http_address, container_id):
    api = node_manager_api.get_resource_manager_api('http://' + node_manager_http_address)
    return Container(api.container(container_id))


class ApplicationNotRunning(Exception):

  def __init__(self, application_id, job):
    self.application_id = application_id
    self.job = job


class JobExpired(Exception):

  def __init__(self, job):
    super(JobExpired, self).__init__('JobExpired: %s' %job)
    self.job = job
