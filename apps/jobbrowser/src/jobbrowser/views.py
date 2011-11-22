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
# Implements simple jobbrowser api
#
import re
import time
import logging
import string
from urllib import quote_plus

from desktop.lib.paginator import Paginator
from desktop.lib.django_util import render_json, MessageException, render
from desktop.lib.django_util import copy_query_dict
from django.http import HttpResponseRedirect

from desktop.log.access import access_warn, access_log_level
from desktop.views import register_status_bar_view
from hadoop.api.jobtracker.ttypes import ThriftJobPriority
from hadoop.api.jobtracker.ttypes import TaskTrackerNotFoundException

from jobbrowser.models import Job, JobLinkage, TaskList, Tracker, Cluster

##################################
## View end-points

__DEFAULT_OBJ_PER_PAGINATION = 10

def single_job(request, jobid):
  """
  We get here from /jobs/jobid
  """
  job = Job.from_id(jt=request.jt, jobid=jobid)

  def cmp_exec_time(foo, bar):
    return cmp(foo.execStartTimeMs, bar.execStartTimeMs)

  failed_tasks = job.filter_tasks(task_states=set(['failed']))
  failed_tasks.sort(cmp_exec_time)
  recent_tasks = job.filter_tasks(task_states=set(['running', 'succeeded']))
  recent_tasks.sort(cmp_exec_time, reverse=True)

  return render("job.mako", request, {
    'request': request,
    'job': job,
    'failed_tasks': failed_tasks[:5],
    'recent_tasks': recent_tasks[:5]
  })

def job_counters(request, jobid):
  """
  We get here from /jobs/jobid/counters
  """
  job = Job.from_id(jt=request.jt, jobid=jobid)
  return render("counters.html", request, {"counters":job.counters})

def jobs(request):
  """
  We get here from /jobs?filterargs
  """
  matching_jobs = sort_if_necessary(request, get_matching_jobs(request))
  state = request.GET.get('state', 'all')
  user = request.GET.get('user', '')
  text = request.GET.get('text', '')
  return render("jobs.mako", request, {
    'jobs':matching_jobs,
    'request': request,
    'state_filter': state,
    'user_filter': user,
    'text_filter': text,
    'filtered': not (state == 'all' and user == '' and text == '')
  })

def dock_jobs(request):
  username = request.user.username
  matching_jobs = get_job_count_by_state(request, username)
  return render("jobs_dock_info.mako", request, {
    'jobs':matching_jobs
  }, force_template=True)
register_status_bar_view(dock_jobs)


@access_log_level(logging.WARN)
def kill_job(request, jobid):
  """
  We get here from /jobs/jobid/kill
  """
  if request.method != "POST":
    raise Exception("kill_job may only be invoked with a POST (got a %s)" % request.method)
  job = Job.from_id(jt=request.jt, jobid=jobid)
  if job.user != request.user.username and not request.user.is_superuser:
    access_warn(request, 'Insufficient permission')
    raise MessageException("Permission denied.  User %s cannot delete user %s's job." %
                           (request.user.username, job.user))

  job.kill()
  cur_time = time.time()
  while time.time() - cur_time < 15:
    job = Job.from_id(jt=request.jt, jobid=jobid)

    if job.status not in ["RUNNING", "QUEUED"]:
      if request.REQUEST.get("next"):
        return HttpResponseRedirect(request.REQUEST.get("next"))
      else:
        raise MessageException("Job Killed")
    time.sleep(1)
    job = Job.from_id(jt=request.jt, jobid=jobid)

  raise Exception("Job did not appear as killed within 15 seconds")

def tasks(request, jobid):
  """
  We get here from /jobs/jobid/tasks?filterargs, with the options being:
    page=<n>            - Controls pagination. Defaults to 1.
    tasktype=<type>     - Type can be one of hadoop.job_tracker.VALID_TASK_TYPES
                          ("map", "reduce", "job_cleanup", "job_setup")
    taskstate=<state>   - State can be one of hadoop.job_tracker.VALID_TASK_STATES
                          ("succeeded", "failed", "running", "pending", "killed")
    tasktext=<text>     - Where <text> is a string matching info on the task
  """
  # Get the filter parameters
  ttypes = request.GET.get('tasktype')
  tstates = request.GET.get('taskstate')
  ttext = request.GET.get('tasktext')
  task_types = None
  if ttypes:
    task_types = set(ttypes.split(','))
  task_states = None
  if tstates:
    task_states = set(tstates.split(','))

  pagenum = int(request.GET.get('page', 1))
  if pagenum < 0:
    pagenum = 1

  # Fetch the list of tasks
  task_list = TaskList.select(request.jt,
                              jobid,
                              task_types,
                              task_states,
                              ttext,
                              __DEFAULT_OBJ_PER_PAGINATION,
                              __DEFAULT_OBJ_PER_PAGINATION * (pagenum - 1))

  paginator = Paginator(task_list, __DEFAULT_OBJ_PER_PAGINATION, total=task_list.numTotalTasks)
  page = paginator.page(pagenum)

  # We need to pass the parameters back to the template to generate links
  filter_params = copy_query_dict(
        request.GET, ('tasktype', 'taskstate', 'tasktext')).urlencode()

  return render("tasks.mako", request, {
    'request': request,
    'filter_params': filter_params,
    'jobid':jobid,
    'page': page,
    'tasktype': ttypes,
    'taskstate': tstates,
    'tasktext': ttext
  })


def single_task(request, jobid, taskid):
  """
  We get here from /jobs/jobid/tasks/taskid
  """
  job_link = JobLinkage(request.jt, jobid)
  task = job_link.get_task(taskid)

  return render("task.mako", request, {
    'task': task,
    'joblnk': job_link
  })

def single_task_attempt(request, jobid, taskid, attemptid):
  """
  We get here from /jobs/jobid/tasks/taskid/attempts/attemptid
  """
  job_link = JobLinkage(request.jt, jobid)
  task = job_link.get_task(taskid)
  try:
    attempt = task.get_attempt(attemptid)
  except KeyError:
    raise KeyError("Cannot find attempt '%s' in task" % (attemptid,))

  try:
    # Add a diagnostic log
    diagnostic_log = ", ".join(task.diagnosticMap[attempt.attemptId])
    logs = [ diagnostic_log ]
    # Add remaining logs
    logs += [ section.strip() for section in attempt.get_task_log() ]
  except TaskTrackerNotFoundException:
    # Four entries,
    # for diagnostic, stdout, stderr and syslog
    logs = [ "Failed to retrieve log. TaskTracker not found." ] * 4
  return render("attempt.mako", request,
    {
      "attempt":attempt,
      "taskid":taskid,
      "joblnk": job_link,
      "task": task,
      "logs": logs
    })

def task_attempt_counters(request, jobid, taskid, attemptid):
  """
  We get here from /jobs/jobid/tasks/taskid/attempts/attemptid/counters
  (phew!)
  """
  job_link = JobLinkage(request.jt, jobid)
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
  """
  ret = request.jt.kill_task_attempt(request.jt.thriftattemptid_from_string(attemptid))
  return render_json({})

def trackers(request):
  """
  We get here from /trackers
  """
  trackers = sort_if_necessary(request, get_tasktrackers(request))

  return render("tasktrackers.mako", request, {'trackers':trackers})

def single_tracker(request, trackerid):
  """
  We get here from /trackers/trackerid
  """
  tracker = Tracker.from_name(request.jt, trackerid)
  return render("tasktracker.mako", request, {'tracker':tracker})

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

def set_job_priority(request, jobid):
  """
  We get here from /jobs/jobid/setpriority?priority=PRIORITY
  """
  priority = request.GET.get("priority")
  jid = request.jt.thriftjobid_from_string(jobid)
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


def sort_if_necessary(request, items):
  if request.GET.get("sortkey"):
    items.sort(key=lambda x: getattr(x, request.GET.get("sortkey")), reverse=request.GET.has_key("sortrev"))
  return items

def get_state_link(request, option=None, val='',
                    VALID_OPTIONS = ("state", "user", "text", "taskstate")):
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


def _filter_jobs_by_req(joblist, request, **kwargs):
  """
  Unpacks filter arguments from the request object and optional
  keyword arguments, and supplies the resulting filter to _filter_jobs.
  """
  args = {}
  for x in ["jobid_exact", "jobid_substr", "pools", "user", "tasks", "text"]:
    if x in kwargs:
      args[x] = kwargs[x]
    else:
      args[x] = request.GET.get(x)
  return _filter_jobs(joblist, **args)


def _filter_jobs(jobs, jobid_exact=None, jobid_substr=None, pools=None, user=None, tasks=None, text=None):
  # TODO(henry): this naive version can be replaced with something
  # more flexible. (i.e. use getattr with a dict of values, check
  # the type and do the right kind of test)
  """
  Return the set in jobs that match the supplied parameters (any of which may be
  None). If jobid is supplied will only return exact id matches if exactid = True.

  All other parameters are substring matched.
  """
  def predicate(job):
    """
    Return True if a ThriftJobInProgress structure matches the supplied filters.

    If a filter argument is None, everything matches it.
    """
    if jobid_exact and jobid_exact != job.jobID.asString:
      return False
    if jobid_substr and jobid_substr not in job.jobID.asString:
      return False
    if pools and pools not in job.profile.queueName:
      return False
    if user and user not in job.profile.user:
      return False
    if tasks and not True: # TODO: figure out what Nutron wants to happen here
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

##################################
## Task trackers

def get_tasktrackers(request):
  """
  Return a ThriftTaskTrackerStatusList object containing all task trackers
  """
  return [ Tracker(tracker) for tracker in request.jt.all_task_trackers().trackers]


##################################
## Jobs

def get_single_job(request, jobid):
  """
  Returns the job which matches jobid.
  """
  return Job.from_id(jt=request.jt, jobid=jobid)


def get_matching_jobs(request, **kwargs):
  """
  Returns an array of jobs where the returned
  jobs are matched by the provided filter arguments.

  If a filter argument is in kwargs it will supersede the same argument
  in the request object.

  Filter arguments may be jobid, pools, user, tasks, text and state.
  """
  jobfunc = {"completed" : request.jt.completed_jobs,
             # Succeeded and completed are synonyms here.
             "succeeded" : request.jt.completed_jobs,
             "running" : request.jt.running_jobs,
             "failed" : request.jt.failed_jobs,
             "killed" : request.jt.killed_jobs,
             "all" : request.jt.all_jobs}
  if 'state' in kwargs:
    selection = kwargs['state']
  else:
    selection = request.GET.get("state", "all")

  joblist = jobfunc[selection]().jobs

  return [Job.from_thriftjob(request.jt, j)
          for j in _filter_jobs_by_req(joblist, request, **kwargs) ]


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


##################################
## JobBrowser views

def jobbrowser(request):
  """
  jobbrowser.jsp - a - like.
  """
  # TODO(bc): Is this view even reachable?
  def check_job_state(state):
    return lambda job: job.status == state

  status = request.jt.cluster_status()
  alljobs = get_matching_jobs(request)
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
