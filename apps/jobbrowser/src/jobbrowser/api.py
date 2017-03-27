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

from datetime import datetime, timedelta
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.paginator import Paginator
from desktop.lib.rest.http_client import RestException

from hadoop import cluster
from hadoop.cluster import jt_ha, rm_ha
from hadoop.api.jobtracker.ttypes import ThriftJobPriority, TaskTrackerNotFoundException, ThriftJobState

import hadoop.yarn.history_server_api as history_server_api
import hadoop.yarn.mapreduce_api as mapreduce_api
import hadoop.yarn.node_manager_api as node_manager_api
import hadoop.yarn.resource_manager_api as resource_manager_api
import hadoop.yarn.spark_history_server_api as spark_history_server_api

from jobbrowser.conf import SHARE_JOBS
from jobbrowser.models import Job, JobLinkage, TaskList, Tracker
from jobbrowser.yarn_models import Application, Job as YarnJob, KilledJob as KilledYarnJob, Container, SparkJob


LOG = logging.getLogger(__name__)

_DEFAULT_OBJ_PER_PAGINATION = 10


def get_api(user, jt):
  if cluster.is_yarn():
    return YarnApi(user)
  else:
    return JtApi(jt)


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

    limit = kwargs.pop('limit', 10000)

    return [Job.from_thriftjob(self.jt, j)
            for j in self._filter_jobs(jobs, **kwargs)
            if not check_permission or user.is_superuser or j.profile.user == user.username][:limit]

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
    self.resource_manager_api = resource_manager_api.get_resource_manager(user.username)
    self.mapreduce_api = mapreduce_api.get_mapreduce_api(user.username)
    self.history_server_api = history_server_api.get_history_server_api(user.username)
    self.spark_history_server_api = spark_history_server_api.get_history_server_api()  # Spark HS does not support setuser

  def get_job_link(self, job_id):
    return self.get_job(job_id)

  @rm_ha
  def get_jobs(self, user, **kwargs):
    state_filters = {'running': 'UNDEFINED', 'completed': 'SUCCEEDED', 'failed': 'FAILED', 'killed': 'KILLED',}
    states_filters = {'running': 'NEW,NEW_SAVING,SUBMITTED,ACCEPTED,RUNNING', 'completed': 'FINISHED', 'failed': 'FAILED,KILLED',}
    filters = {}

    if kwargs['username']:
      filters['user'] = kwargs['username']
    if kwargs['state'] and kwargs['state'] != 'all':
      filters['finalStatus'] = state_filters[kwargs['state']]
    if kwargs.get('states'):
      filters['states'] = ','.join([states_filters[_s] for _s in kwargs['states']])
    if kwargs.get('limit'):
      filters['limit'] = kwargs['limit']
    if kwargs.get('time_value'):
      filters['startedTimeBegin'] = self._get_started_time_begin(kwargs.get('time_value'), kwargs.get('time_unit'))

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

  def _get_started_time_begin(self, time_value, time_unit):
    if time_unit == 'hours':
      start_date = datetime.utcnow() - timedelta(hours=time_value)
    elif time_unit == 'minutes':
      start_date = datetime.utcnow() - timedelta(minutes=time_value)
    else:
      start_date = datetime.utcnow() - timedelta(days=time_value)

    elapsed_time = start_date - datetime.utcfromtimestamp(0)
    return int(elapsed_time.days * 86400 + elapsed_time.seconds) * 1000

  def filter_jobs(self, user, jobs, **kwargs):
    check_permission = not SHARE_JOBS.get() and not user.is_superuser

    return filter(lambda job:
                  not check_permission or
                  user.is_superuser or
                  job.user == user.username, jobs)


  def _get_job_from_history_server(self, job_id):
    resp = self.history_server_api.job(self.user, job_id)
    return YarnJob(self.history_server_api, resp['job'])


  @rm_ha
  def get_job(self, jobid):
    job_id = jobid.replace('application', 'job')
    app_id = jobid.replace('job', 'application')

    try:
      app = self.resource_manager_api.app(app_id)['app']

      if app['finalStatus'] in ('SUCCEEDED', 'FAILED', 'KILLED'):
        if app['applicationType'] == 'SPARK':
          job = SparkJob(app, rm_api=self.resource_manager_api, hs_api=self.spark_history_server_api)
        elif app['state'] in ('KILLED', 'FAILED'):
          job = KilledYarnJob(self.resource_manager_api, app)
        else:  # Job succeeded, attempt to fetch from JHS
          job = self._get_job_from_history_server(job_id)
      else:
        if app['state'] == 'ACCEPTED':
          raise ApplicationNotRunning(app_id, app)
        # The MapReduce API only returns JSON when the application is in a RUNNING state
        elif app['state'] in ('NEW', 'SUBMITTED', 'RUNNING') and app['applicationType'] == 'MAPREDUCE':
          resp = self.mapreduce_api.job(self.user, job_id)
          if not isinstance(resp, dict):
            raise PopupException(_('Mapreduce Proxy API did not return JSON response, check if the job is running.'))
          job = YarnJob(self.mapreduce_api, resp['job'])
        else:
          job = Application(app, self.resource_manager_api)
    except RestException, e:
      if e.code == 404:  # Job not found in RM so attempt to find job in JHS
        job = self._get_job_from_history_server(job_id)
      else:
        raise JobExpired(app_id)
    except PopupException, e:
      if 'NotFoundException' in e.message:
        job = self._get_job_from_history_server(job_id)
      else:
        raise e
    except ApplicationNotRunning, e:
      raise e
    except Exception, e:
      raise PopupException('Job %s could not be found: %s' % (jobid, e), detail=e)

    return job

  def get_application(self, jobid):
    app = None
    app_id = jobid.replace('job', 'application')

    try:
      app = self.resource_manager_api.app(app_id)['app']
    except RestException, e:
      raise PopupException(_('Job %s could not be found in Resource Manager: %s') % (jobid, e), detail=e)
    except ApplicationNotRunning, e:
      raise PopupException(_('Application is not running: %s') % e, detail=e)
    except Exception, e:
      raise PopupException(_('Job %s could not be found: %s') % (jobid, e), detail=e)

    return app

  def get_tasks(self, jobid, **filters):
    filters.pop('pagenum')
    return self.get_job(jobid).filter_tasks(**filters)

  def get_task(self, jobid, task_id):
    return self.get_job(jobid).get_task(task_id)

  def get_tracker(self, node_manager_http_address, container_id):
    api = node_manager_api.get_node_manager_api('http://' + node_manager_http_address)
    return Container(api.container(container_id))


class ApplicationNotRunning(Exception):

  def __init__(self, application_id, job):
    self.application_id = application_id
    self.job = job


class JobExpired(Exception):

  def __init__(self, job):
    super(JobExpired, self).__init__('JobExpired: %s' %job)
    self.job = job
