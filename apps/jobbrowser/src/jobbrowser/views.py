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
import string
import time
import urllib2
import urlparse

from lxml import html
from urllib import quote_plus

from django.http import HttpResponseRedirect
from django.utils.functional import wraps
from django.utils.translation import ugettext as _
from django.urls import reverse

from desktop.auth.backend import is_admin
from desktop.lib.django_util import JsonResponse, render_json, render, copy_query_dict
from desktop.lib.exceptions import MessageException
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.json_utils import JSONEncoderForHTML
from desktop.lib.rest.http_client import RestException
from desktop.lib.rest.resource import Resource
from desktop.log.access import access_log_level
from desktop.views import register_status_bar_view

from hadoop import cluster
from hadoop.yarn.clients import get_log_client
from hadoop.yarn import resource_manager_api as resource_manager_api


LOG = logging.getLogger(__name__)


try:
  from beeswax.hive_site import hiveserver2_impersonation_enabled
except:
  LOG.warn('Hive is not enabled')
  def hiveserver2_impersonation_enabled(): return True

from jobbrowser.conf import LOG_OFFSET, SHARE_JOBS
from jobbrowser.api import get_api, ApplicationNotRunning, JobExpired
from jobbrowser.models import can_view_job, can_kill_job, LinkJobLogs
from jobbrowser.yarn_models import Application


LOG_OFFSET_BYTES = LOG_OFFSET.get()


def check_job_permission(view_func):
  """
  Ensure that the user has access to the job.
  Assumes that the wrapped function takes a 'jobid' param named 'job'.
  """
  def decorate(request, *args, **kwargs):
    jobid = kwargs['job']
    try:
      job = get_job(request, job_id=jobid)
    except ApplicationNotRunning, e:
      LOG.warn('Job %s has not yet been accepted by the RM, will poll for status.' % jobid)
      return job_not_assigned(request, jobid, request.path)

    if not SHARE_JOBS.get() and not is_admin(request.user) \
        and job.user != request.user.username and not can_view_job(request.user.username, job):
      raise PopupException(_("You don't have permission to access job %(id)s.") % {'id': jobid})
    kwargs['job'] = job
    return view_func(request, *args, **kwargs)

  return wraps(view_func)(decorate)


def get_job(request, job_id):
  try:
    job = get_api(request.user, request.jt).get_job(jobid=job_id)
  except ApplicationNotRunning, e:
    if e.job.get('state', '').lower() == 'accepted':
      rm_api = resource_manager_api.get_resource_manager(request.user)
      job = Application(e.job, rm_api)
    else:
      raise e  # Job has not yet been accepted by RM
  except JobExpired, e:
    raise PopupException(_('Job %s has expired.') % job_id, detail=_('Cannot be found on the History Server.'))
  except Exception, e:
    msg = 'Could not find job %s.'
    LOG.exception(msg % job_id)
    raise PopupException(_(msg) % job_id, detail=e)
  return job


def apps(request):
  return render('job_browser.mako', request, {
    'is_embeddable': request.GET.get('is_embeddable', False),
    'is_mini': request.GET.get('is_mini', False),
    'hiveserver2_impersonation_enabled': hiveserver2_impersonation_enabled()
  })


def job_not_assigned(request, jobid, path):
  if request.GET.get('format') == 'json':
    result = {'status': -1, 'message': ''}

    try:
      get_api(request.user, request.jt).get_job(jobid=jobid)
      result['status'] = 0
    except ApplicationNotRunning, e:
      result['status'] = 1
    except Exception, e:
      result['message'] = _('Error polling job %s: %s') % (jobid, e)

    return JsonResponse(result, encoder=JSONEncoderForHTML)
  else:
    return render('job_not_assigned.mako', request, {'jobid': jobid, 'path': path})


def jobs(request):
  user = request.POST.get('user', request.user.username)
  state = request.POST.get('state')
  text = request.POST.get('text')
  retired = request.POST.get('retired')
  time_value = request.POST.get('time_value', 7)
  time_unit = request.POST.get('time_unit', 'days')

  if request.POST.get('format') == 'json':
    try:
      # Limit number of jobs to be 1000
      jobs = get_api(request.user, request.jt).get_jobs(
          user=request.user,
          username=user,
          state=state,
          text=text,
          retired=retired,
          limit=1000,
          time_value=int(time_value),
          time_unit=time_unit
      )
    except Exception, ex:
      ex_message = str(ex)
      if 'Connection refused' in ex_message or 'standby RM' in ex_message:
        raise PopupException(_('Resource Manager cannot be contacted or might be down.'))
      elif 'Could not connect to' in ex_message:
        raise PopupException(_('Job Tracker cannot be contacted or might be down.'))
      else:
        raise PopupException(ex)
    json_jobs = {
      'jobs': [massage_job_for_json(job, request) for job in jobs],
    }
    return JsonResponse(json_jobs, encoder=JSONEncoderForHTML)

  return render('jobs.mako', request, {
    'request': request,
    'state_filter': state,
    'user_filter': user,
    'text_filter': text,
    'retired': retired,
    'filtered': not (state == 'all' and user == '' and text == ''),
    'is_yarn': cluster.is_yarn(),
    'hiveserver2_impersonation_enabled': hiveserver2_impersonation_enabled()
  })


def massage_job_for_json(job, request=None, user=None):
  job = {
    'id': job.jobId,
    'shortId': job.jobId_short,
    'name': hasattr(job, 'jobName') and job.jobName or '',
    'status': job.status,
    'yarnStatus': hasattr(job, 'yarnStatus') and job.yarnStatus or '',
    'url': job.jobId and reverse('jobbrowser.views.single_job', kwargs={'job': job.jobId}) or '',
    'logs': job.jobId and reverse('jobbrowser.views.job_single_logs', kwargs={'job': job.jobId}) or '',
    'queueName': hasattr(job, 'queueName') and job.queueName or _('N/A'),
    'priority': hasattr(job, 'priority') and job.priority or _('N/A'),
    'user': job.user,
    'isRetired': job.is_retired,
    'isMR2': job.is_mr2,
    'progress': hasattr(job, 'progress') and job.progress or 0,
    'mapProgress': hasattr(job, 'mapProgress') and job.mapProgress or '',
    'reduceProgress': hasattr(job, 'reduceProgress') and job.reduceProgress or '',
    'setupProgress': hasattr(job, 'setupProgress') and job.setupProgress or '',
    'cleanupProgress': hasattr(job, 'cleanupProgress') and job.cleanupProgress or '',
    'desiredMaps': job.desiredMaps,
    'desiredReduces': job.desiredReduces,
    'applicationType': hasattr(job, 'applicationType') and job.applicationType or None,
    'type': hasattr(job, 'type') and job.type or None,
    'mapsPercentComplete': int(job.maps_percent_complete) if job.maps_percent_complete else '',
    'finishedMaps': job.finishedMaps,
    'finishedReduces': job.finishedReduces,
    'reducesPercentComplete': int(job.reduces_percent_complete) if job.reduces_percent_complete else '',
    'jobFile': hasattr(job, 'jobFile') and job.jobFile or '',
    'launchTimeMs': hasattr(job, 'launchTimeMs') and job.launchTimeMs or 0,
    'launchTimeFormatted': hasattr(job, 'launchTimeFormatted') and job.launchTimeFormatted or '',
    'startTimeMs': hasattr(job, 'startTimeMs') and job.startTimeMs or 0,
    'startTimeFormatted': hasattr(job, 'startTimeFormatted') and job.startTimeFormatted or '',
    'finishTimeMs': hasattr(job, 'finishTimeMs') and job.finishTimeMs or 0,
    'finishTimeFormatted': hasattr(job, 'finishTimeFormatted') and job.finishTimeFormatted or '',
    'durationFormatted': hasattr(job, 'durationFormatted') and job.durationFormatted or '',
    'durationMs': hasattr(job, 'durationInMillis') and job.durationInMillis or 0,
    'canKill': can_kill_job(job, request.user if request else user),
    'killUrl': job.jobId and reverse('kill_job', kwargs={'job': job.jobId}) or '',
    'diagnostics': hasattr(job, 'diagnostics') and job.diagnostics or '',
  }
  return job


def massage_task_for_json(task):
  task = {
    'id': task.taskId,
    'shortId': task.taskId_short,
    'url': task.taskId and reverse('jobbrowser.views.single_task', kwargs={'job': task.jobId, 'taskid': task.taskId}) or '',
    'logs': task.taskAttemptIds and reverse('single_task_attempt_logs', kwargs={'job': task.jobId, 'taskid': task.taskId, 'attemptid': task.taskAttemptIds[-1]}) or '',
    'type': task.taskType
  }
  return task


def single_spark_job(request, job):
  if request.GET.get('format') == 'json':
    json_job = {
      'job': massage_job_for_json(job, request)
    }
    return JsonResponse(json_job, encoder=JSONEncoderForHTML)
  else:
    return render('job.mako', request, {
      'request': request,
      'job': job
    })

@check_job_permission
def single_job(request, job):
  def cmp_exec_time(task1, task2):
    return cmp(task1.execStartTimeMs, task2.execStartTimeMs)

  if job.applicationType == 'SPARK':
    return single_spark_job(request, job)

  failed_tasks = job.filter_tasks(task_states=('failed',))
  failed_tasks.sort(cmp_exec_time)
  recent_tasks = job.filter_tasks(task_states=('running', 'succeeded',))
  recent_tasks.sort(cmp_exec_time, reverse=True)

  if request.GET.get('format') == 'json':
    json_failed_tasks = [massage_task_for_json(task) for task in failed_tasks]
    json_recent_tasks = [massage_task_for_json(task) for task in recent_tasks]
    json_job = {
      'job': massage_job_for_json(job, request),
      'failedTasks': json_failed_tasks,
      'recentTasks': json_recent_tasks
    }
    return JsonResponse(json_job, encoder=JSONEncoderForHTML)

  return render('job.mako', request, {
    'request': request,
    'job': job,
    'failed_tasks': failed_tasks and failed_tasks[:5] or [],
    'recent_tasks': recent_tasks and recent_tasks[:5] or [],
  })


@check_job_permission
def job_counters(request, job):
  return render("counters.html", request, {"counters": job.counters})


@access_log_level(logging.WARN)
@check_job_permission
def kill_job(request, job):
  if request.method != "POST":
    raise Exception(_("kill_job may only be invoked with a POST (got a %(method)s).") % {'method': request.method})

  if not can_kill_job(job, request.user):
    raise PopupException(_("Kill operation is forbidden."))

  try:
    job.kill()
  except Exception, e:
    LOG.exception('Killing job')
    raise PopupException(e)

  cur_time = time.time()
  api = get_api(request.user, request.jt)

  while time.time() - cur_time < 15:
    try:
      job = api.get_job(jobid=job.jobId)
    except Exception, e:
      LOG.warn('Failed to get job with ID %s: %s' % (job.jobId, e))
    else:
      if job.status not in ["RUNNING", "QUEUED"]:
        if request.GET.get("next"):
          return HttpResponseRedirect(request.GET.get("next"))
        elif request.GET.get("format") == "json":
          return JsonResponse({'status': 0}, encoder=JSONEncoderForHTML)
        else:
          raise MessageException("Job Killed")
    time.sleep(1)

  raise Exception(_("Job did not appear as killed within 15 seconds."))

@check_job_permission
def job_executor_logs(request, job, attempt_index=0, name='syslog', offset=LOG_OFFSET_BYTES):
  response = {'status': -1}
  try:
    log = ''
    if job.status not in ('NEW', 'SUBMITTED', 'ACCEPTED'):
      log = job.history_server_api.download_executors_logs(request, job, name, offset)
    response['status'] = 0
    response['log'] = LinkJobLogs._make_hdfs_links(log)
  except Exception, e:
    response['log'] = _('Failed to retrieve executor log: %s' % e)

  return JsonResponse(response)


@check_job_permission
def job_attempt_logs(request, job, attempt_index=0):
  return render("job_attempt_logs.mako", request, {
    "attempt_index": attempt_index,
    "job": job,
    "log_offset": LOG_OFFSET_BYTES
  })


@check_job_permission
def job_attempt_logs_json(request, job, attempt_index=0, name='syslog', offset=LOG_OFFSET_BYTES, is_embeddable=False):
  """For async log retrieval as Yarn servers are very slow"""
  log_link = None
  response = {'status': -1}

  try:
    jt = get_api(request.user, request.jt)
    app = jt.get_application(job.jobId)

    if app['applicationType'] == 'MAPREDUCE':
      if app['finalStatus'] in ('SUCCEEDED', 'FAILED', 'KILLED'):
        attempt_index = int(attempt_index)
        if not job.job_attempts['jobAttempt']:
          response = {'status': 0, 'log': _('Job has no tasks')}
        else:
          attempt = job.job_attempts['jobAttempt'][attempt_index]

          log_link = attempt['logsLink']
          # Reformat log link to use YARN RM, replace node addr with node ID addr
          log_link = log_link.replace(attempt['nodeHttpAddress'], attempt['nodeId'])
      elif app['state'] == 'RUNNING':
        log_link = app['amContainerLogs']
    elif app.get('amContainerLogs'):
      log_link = app.get('amContainerLogs')
  except (KeyError, RestException), e:
    raise KeyError(_("Cannot find job attempt '%(id)s'.") % {'id': job.jobId}, e)
  except Exception, e:
    raise Exception(_("Failed to get application for job %s: %s") % (job.jobId, e))

  if log_link:
    link = '/%s/' % name
    params = {
      'doAs': request.user.username
    }
      
    if offset != 0:
      params['start'] = offset

    root = Resource(get_log_client(log_link), urlparse.urlsplit(log_link)[2], urlencode=False)
    api_resp = None

    try:
      api_resp = root.get(link, params=params)
      log = html.fromstring(api_resp, parser=html.HTMLParser()).xpath('/html/body/table/tbody/tr/td[2]')[0].text_content()

      response['status'] = 0
      response['log'] = LinkJobLogs._make_hdfs_links(log, is_embeddable)
    except Exception, e:
      response['log'] = _('Failed to retrieve log: %s' % e)
      try:
        debug_info = '\nLog Link: %s' % log_link
        if api_resp:
          debug_info += '\nHTML Response: %s' % response
        response['debug'] = debug_info
        LOG.error(debug_info)
      except:
        LOG.exception('failed to create debug info')

  return JsonResponse(response)


@check_job_permission
def job_single_logs(request, job, offset=LOG_OFFSET_BYTES):
  """
  Try to smartly detect the most useful task attempt (e.g. YarnV2, failed task) and get its MR logs.
  """
  def cmp_exec_time(task1, task2):
    return cmp(task1.execStartTimeMs, task2.execStartTimeMs)

  if job.applicationType == 'SPARK':
    return job.history_server_api.download_logs(job.app)

  task = None

  failed_tasks = job.filter_tasks(task_states=('failed',))
  failed_tasks.sort(cmp_exec_time)
  if failed_tasks:
    task = failed_tasks[0]
    if not task.taskAttemptIds and len(failed_tasks) > 1: # In some cases the last task ends up without any attempt
      task = failed_tasks[1]
  else:
    task_states = ['running', 'succeeded']
    if job.is_mr2:
      task_states.append('scheduled')
    recent_tasks = job.filter_tasks(task_states=task_states, task_types=('map', 'reduce',))
    recent_tasks.sort(cmp_exec_time, reverse=True)
    if recent_tasks:
      task = recent_tasks[0]

  if task is None or not task.taskAttemptIds:
    if request.GET.get('format') == 'link':
      params = {'job': job.jobId, 'offset': offset}
    else:
      raise PopupException(_("No tasks found for job %(id)s.") % {'id': job.jobId})
  else:
    params = {'job': job.jobId, 'taskid': task.taskId, 'attemptid': task.taskAttemptIds[-1], 'offset': offset}

  if request.GET.get('format') == 'link':
    return JsonResponse(params)
  else:
    return single_task_attempt_logs(request, **params)


@check_job_permission
def tasks(request, job):
  """
  We get here from /jobs/job/tasks?filterargs, with the options being:
    page=<n>            - Controls pagination. Defaults to 1.
    tasktype=<type>     - Type can be one of hadoop.job_tracker.VALID_TASK_TYPES
                          ("map", "reduce", "job_cleanup", "job_setup")
    taskstate=<state>   - State can be one of hadoop.job_tracker.VALID_TASK_STATES
                          ("succeeded", "failed", "running", "pending", "killed")
    tasktext=<text>     - Where <text> is a string matching info on the task
  """
  ttypes = request.GET.get('tasktype')
  tstates = request.GET.get('taskstate')
  ttext = request.GET.get('tasktext')
  pagenum = int(request.GET.get('page', 1))
  pagenum = pagenum > 0 and pagenum or 1

  filters = {
    'task_types': ttypes and set(ttypes.split(',')) or None,
    'task_states': tstates and set(tstates.split(',')) or None,
    'task_text': ttext,
    'pagenum': pagenum,
  }

  jt = get_api(request.user, request.jt)

  task_list = jt.get_tasks(job.jobId, **filters)

  filter_params = copy_query_dict(request.GET, ('tasktype', 'taskstate', 'tasktext')).urlencode()

  return render("tasks.mako", request, {
    'request': request,
    'filter_params': filter_params,
    'job': job,
    'task_list': task_list,
    'tasktype': ttypes,
    'taskstate': tstates,
    'tasktext': ttext
  })


@check_job_permission
def single_task(request, job, taskid):
  jt = get_api(request.user, request.jt)

  job_link = jt.get_job_link(job.jobId)
  task = job_link.get_task(taskid)

  return render("task.mako", request, {
    'task': task,
    'joblnk': job_link
  })

@check_job_permission
def single_task_attempt(request, job, taskid, attemptid):
  jt = get_api(request.user, request.jt)

  job_link = jt.get_job_link(job.jobId)
  task = job_link.get_task(taskid)

  try:
    attempt = task.get_attempt(attemptid)
  except (KeyError, RestException), e:
    raise PopupException(_("Cannot find attempt '%(id)s' in task") % {'id': attemptid}, e)

  return render("attempt.mako", request, {
      "attempt": attempt,
      "taskid": taskid,
      "joblnk": job_link,
      "task": task
    })

@check_job_permission
def single_task_attempt_logs(request, job, taskid, attemptid, offset=LOG_OFFSET_BYTES):
  jt = get_api(request.user, request.jt)

  job_link = jt.get_job_link(job.jobId)
  task = job_link.get_task(taskid)

  try:
    attempt = task.get_attempt(attemptid)
  except (KeyError, RestException), e:
    raise KeyError(_("Cannot find attempt '%(id)s' in task") % {'id': attemptid}, e)

  first_log_tab = 0

  try:
    # Add a diagnostic log
    if hasattr(task, 'job') and hasattr(task.job, 'diagnostics'):
      diagnostic_log = task.job.diagnostics
    elif job_link.is_mr2:
      diagnostic_log = attempt.diagnostics
    else:
      diagnostic_log =  ", ".join(task.diagnosticMap[attempt.attemptId])
    logs = [diagnostic_log]
    # Add remaining logs
    logs += [section.strip() for section in attempt.get_task_log(offset=offset)]
    log_tab = [i for i, log in enumerate(logs) if log]
    if log_tab:
      first_log_tab = log_tab[0]
  except urllib2.URLError:
    logs = [_("Failed to retrieve log. TaskTracker not ready.")] * 4

  context = {
      "attempt": attempt,
      "taskid": taskid,
      "joblnk": job_link,
      "task": task,
      "logs": logs,
      "logs_list": attempt.get_log_list(),
      "first_log_tab": first_log_tab,
  }

  if request.GET.get('format') == 'python':
    return context
  else:
    context['logs'] = [LinkJobLogs._make_links(log) for i, log in enumerate(logs)]

  if request.GET.get('format') == 'json':
    response = {
      "logs": context['logs'],
      "logsList": context['logs_list'],
      "isRunning": job.status.lower() in ('running', 'pending', 'prep')
    }
    return JsonResponse(response)
  else:
    return render("attempt_logs.mako", request, context)

@check_job_permission
def task_attempt_counters(request, job, taskid, attemptid):
  """
  We get here from /jobs/jobid/tasks/taskid/attempts/attemptid/counters
  (phew!)
  """
  job_link = JobLinkage(request.jt, job.jobId)
  task = job_link.get_task(taskid)
  attempt = task.get_attempt(attemptid)
  counters = {}
  if attempt:
    counters = attempt.counters
  return render("counters.html", request, {'counters':counters})

@access_log_level(logging.WARN)
def kill_task_attempt(request, attemptid):
  """
  We get here from /jobs/jobid/tasks/taskid/attempts/attemptid/kill
  TODO: security
  """
  ret = request.jt.kill_task_attempt(request.jt.thriftattemptid_from_string(attemptid))
  return render_json({})

def trackers(request):
  """
  We get here from /trackers
  """
  trackers = get_tasktrackers(request)

  return render("tasktrackers.mako", request, {'trackers':trackers})

def single_tracker(request, trackerid):
  jt = get_api(request.user, request.jt)

  try:
    tracker = jt.get_tracker(trackerid)
  except Exception, e:
    raise PopupException(_('The tracker could not be contacted.'), detail=e)
  return render("tasktracker.mako", request, {'tracker':tracker})

def container(request, node_manager_http_address, containerid):
  jt = get_api(request.user, request.jt)

  try:
    tracker = jt.get_tracker(node_manager_http_address, containerid)
  except Exception, e:
    # TODO: add a redirect of some kind
    raise PopupException(_('The container disappears as soon as the job finishes.'), detail=e)
  return render("container.mako", request, {'tracker':tracker})


def clusterstatus(request):
  """
  We get here from /clusterstatus
  """
  return render("clusterstatus.html", request, Cluster(request.jt))

def queues(request):
  """
  We get here from /queues
  """
  return render("queues.html", request, { "queuelist" : request.jt.queues()})

@check_job_permission
def set_job_priority(request, job):
  """
  We get here from /jobs/job/setpriority?priority=PRIORITY
  """
  priority = request.GET.get("priority")
  jid = request.jt.thriftjobid_from_string(job.jobId)
  request.jt.set_job_priority(jid, ThriftJobPriority._NAMES_TO_VALUES[priority])
  return render_json({})

CONF_VARIABLE_REGEX = r"\$\{(.+)\}"

def make_substitutions(conf):
  """
  Substitute occurences of ${foo} with conf[foo], recursively, in all the values
  of the conf dict.

  Note that the Java code may also substitute Java properties in, which
  this code does not have.
  """
  r = re.compile(CONF_VARIABLE_REGEX)
  def sub(s, depth=0):
    # Malformed / malicious confs could make this loop infinitely
    if depth > 100:
      logging.warn("Max recursion depth exceeded when substituting jobconf value: %s" % s)
      return s
    m = r.search(s)
    if m:
      for g in [g for g in m.groups() if g in conf]:
        substr = "${%s}" % g
        s = s.replace(substr, sub(conf[g], depth+1))
    return s

  for k, v in conf.items():
    conf[k] = sub(v)
  return conf

##################################
## Helper functions

def get_shorter_id(hadoop_job_id):
  return "_".join(hadoop_job_id.split("_")[-2:])


def format_counter_name(s):
  """
  Makes counter/config names human readable:
  FOOBAR_BAZ -> "Foobar Baz"
  foo_barBaz -> "Foo Bar Baz"
  """
  def splitCamels(s):
    """ Convert "fooBar" to "foo bar" """
    return re.sub(r'[a-z][A-Z]',
                  lambda x: x.group(0)[0] + " " + x.group(0)[1].lower(),
                  s)

  return string.capwords(re.sub('_', ' ', splitCamels(s)).lower())


def get_state_link(request, option=None, val='', VALID_OPTIONS = ("state", "user", "text", "taskstate")):
  """
    constructs the query string for the state of the current query for the jobs page.
    pass in the request, and an optional option/value pair; these are used for creating
    links to turn on the filter, while preserving the other present settings.
  """
  states = []
  val = quote_plus(val)

  assert option is None or option in VALID_OPTIONS

  states = dict()
  for o in VALID_OPTIONS:
    if o in request.GET:
      states[o] = request.GET[o]
  if option is not None:
    states[option] = val

  return "&".join([ "%s=%s" % (key, quote_plus(value)) for key, value in states.iteritems() ])


## All Unused below

# DEAD?
def dock_jobs(request):
  username = request.user.username
  matching_jobs = get_job_count_by_state(request, username)
  return render("jobs_dock_info.mako", request, {
    'jobs': matching_jobs
  }, force_template=True)
register_status_bar_view(dock_jobs)


def get_tasktrackers(request):
  """
  Return a ThriftTaskTrackerStatusList object containing all task trackers
  """
  return [ Tracker(tracker) for tracker in request.jt.all_task_trackers().trackers]


def get_single_job(request, jobid):
  """
  Returns the job which matches jobid.
  """
  return Job.from_id(jt=request.jt, jobid=jobid)


def get_job_count_by_state(request, username):
  """
  Returns the number of comlpeted, running, and failed jobs for a user.
  """
  res = {
    'completed': 0,
    'running': 0,
    'failed': 0,
    'killed': 0,
    'all': 0
  }

  jobcounts = request.jt.get_job_count_by_user(username)
  res['completed'] = jobcounts.nSucceeded
  res['running'] = jobcounts.nPrep + jobcounts.nRunning
  res['failed'] = jobcounts.nFailed
  res['killed'] = jobcounts.nKilled
  res['all'] = res['completed'] + res['running'] + res['failed'] + res['killed']
  return res


def jobbrowser(request):
  """
  jobbrowser.jsp - a - like.
  """
  # TODO(bc): Is this view even reachable?
  def check_job_state(state):
    return lambda job: job.status == state

  status = request.jt.cluster_status()
  alljobs = [] #get_matching_jobs(request)
  runningjobs = filter(check_job_state('RUNNING'), alljobs)
  completedjobs = filter(check_job_state('COMPLETED'), alljobs)
  failedjobs = filter(check_job_state('FAILED'), alljobs)
  killedjobs = filter(check_job_state('KILLED'), alljobs)
  jobqueues = request.jt.queues()

  return render("jobbrowser.html", request, {
      "clusterstatus" : status,
      "queues" : jobqueues,
      "alljobs" : alljobs,
      "runningjobs" : runningjobs,
      "failedjobs" : failedjobs,
      "killedjobs" : killedjobs,
      "completedjobs" : completedjobs
  })
