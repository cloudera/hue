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

try:
  import json
except ImportError:
  import simplejson as json
import logging
import re
import time

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from jobbrowser.views import job_single_logs
from desktop.lib.view_util import format_duration_in_millis
from oozie.models import Workflow, Pig
from oozie.views.editor import _submit_workflow
from liboozie.oozie_api import get_oozie

LOG = logging.getLogger(__name__)


def get(fs, user):
  return OozieApi(fs, user)


class OozieApi:
  """
  Oozie submission.
  """
  WORKFLOW_NAME = 'pig-app-hue-script'
  RE_LOG_END = re.compile('(<<< Invocation of Pig command completed <<<|<<< Invocation of Main class completed <<<)')
  RE_LOG_START_RUNNING = re.compile('>>> Invoking Pig command line now >>>\n\n\nRun pig script using PigRunner.run\(\) for Pig version [^\n]+?\n(.+?)(<<< Invocation of Pig command completed <<<|<<< Invocation of Main class completed)', re.M | re.DOTALL)
  RE_LOG_START_FINISHED = re.compile('(>>> Invoking Pig command line now >>>\n\n\nRun pig script using PigRunner.run\(\) for Pig version [^\n]+?)\n', re.M | re.DOTALL)
  MAX_DASHBOARD_JOBS = 100

  def __init__(self, fs, user):
    self.fs = fs
    self.user = user

  def submit(self, pig_script, params):
    mapping = {
      'oozie.use.system.libpath':  'true',
    }

    workflow = Workflow.objects.new_workflow(self.user)

    try:
      workflow.name = OozieApi.WORKFLOW_NAME
      workflow.is_history = True
      workflow.save()
      Workflow.objects.initialize(workflow, self.fs)

      script_path = workflow.deployment_dir + '/script.pig'
      self.fs.create(script_path, data=pig_script.dict['script'])

      pig_params = []
      for param in json.loads(params):
        pig_params.append({"type":"argument","value":"-param"})
        pig_params.append({"type":"argument","value":"%(name)s=%(value)s" % param})

      files = []
      archives = []

      for resource in pig_script.dict['resources']:
        if resource['type'] == 'file':
          files.append(resource['value'])
        if resource['type'] == 'archive':
          archives.append({"dummy": "", "name": resource['value']})

      action = Pig.objects.create(
          name='pig',
          script_path=script_path,
          workflow=workflow,
          node_type='pig',
          params=json.dumps(pig_params),
          files=json.dumps(files),
          archives=json.dumps(archives),
      )

      action.add_node(workflow.end)

      start_link = workflow.start.get_link()
      start_link.child = action
      start_link.save()

      oozie_wf = _submit_workflow(self.user, self.fs, workflow, mapping)
    finally:
      workflow.delete()

    return oozie_wf

  def stop(self, job_id):
    return get_oozie().job_control(job_id, 'kill')

  def get_jobs(self):
    kwargs = {'cnt': OozieApi.MAX_DASHBOARD_JOBS,}
    kwargs['user'] = self.user.username
    kwargs['name'] = OozieApi.WORKFLOW_NAME

    return get_oozie().get_workflows(**kwargs).jobs

  def get_log(self, request, oozie_workflow):
    logs = {}

    for action in oozie_workflow.get_working_actions():
      try:
        if action.externalId:
          log = job_single_logs(request, **{'job': action.externalId})
          if log:
            logs[action.name] = self._match_logs(log['logs'][1])
      except Exception, e:
        LOG.error('An error happen while watching the demo running: %(error)s' % {'error': e})

    workflow_actions = []

    # Only one Pig action
    for action in oozie_workflow.get_working_actions():
      progress = get_progress(oozie_workflow, logs.get(action.name, ''))
      appendable = {
        'name': action.name,
        'status': action.status,
        'logs': logs.get(action.name, ''),
        'progress': progress,
        'progressPercent': '%d%%' % progress,
        'absoluteUrl': oozie_workflow.get_absolute_url(),
      }
      workflow_actions.append(appendable)

    return logs, workflow_actions

  def _match_logs(self, logs):
    """Difficult to match multi lines of text"""
    if OozieApi.RE_LOG_END.search(logs):
      return re.search(OozieApi.RE_LOG_START_RUNNING, logs).group(1)
    else:
      group = re.search(OozieApi.RE_LOG_START_FINISHED, logs)
      i = logs.index(group.group(1)) + len(group.group(1))
      return logs[i:]

  def massaged_jobs_for_json(self, oozie_jobs, hue_jobs):
    jobs = []
    hue_jobs = dict([(script.dict.get('job_id'), script) for script in hue_jobs if script.dict.get('job_id')])

    for job in oozie_jobs:
      if job.is_running():
        job = get_oozie().get_job(job.id)

      hue_pig = hue_jobs.get(job.id) and hue_jobs.get(job.id) or None

      massaged_job = {
        'id': job.id,
        'lastModTime': hasattr(job, 'lastModTime') and job.lastModTime and format_time(job.lastModTime) or None,
        'kickoffTime': hasattr(job, 'kickoffTime') and job.kickoffTime or None,
        'timeOut': hasattr(job, 'timeOut') and job.timeOut or None,
        'endTime': job.endTime and format_time(job.endTime) or None,
        'status': job.status,
        'isRunning': job.is_running(),
        'duration': job.endTime and job.startTime and format_duration_in_millis(( time.mktime(job.endTime) - time.mktime(job.startTime) ) * 1000) or None,
        'appName': hue_pig and hue_pig.dict['name'] or _('Unsaved script'),
        'scriptId': hue_pig and hue_pig.id or -1,
        'progress': get_progress(job),
        'progressPercent': '%d%%' % get_progress(job),
        'user': job.user,
        'absoluteUrl': job.get_absolute_url(),
        'canEdit': has_job_edition_permission(job, self.user),
        'killUrl': reverse('oozie:manage_oozie_jobs', kwargs={'job_id':job.id, 'action':'kill'}),
        'watchUrl': reverse('pig:watch', kwargs={'job_id': job.id}) + '?format=python',
        'created': hasattr(job, 'createdTime') and job.createdTime and job.createdTime and ((job.type == 'Bundle' and job.createdTime) or format_time(job.createdTime)),
        'startTime': hasattr(job, 'startTime') and format_time(job.startTime) or None,
        'run': hasattr(job, 'run') and job.run or 0,
        'frequency': hasattr(job, 'frequency') and job.frequency or None,
        'timeUnit': hasattr(job, 'timeUnit') and job.timeUnit or None,
        }
      jobs.append(massaged_job)

    return jobs

def get_progress(job, log=None):
  if job.status in ('SUCCEEDED', 'KILLED', 'FAILED'):
    return 100
  elif log:
    try:
      return int(re.findall("MapReduceLauncher  - (1?\d?\d)% complete", log)[-1])
    except:
      return 0
  else:
    return 0


def format_time(st_time):
  if st_time is None:
    return '-'
  else:
    return time.strftime("%a, %d %b %Y %H:%M:%S", st_time)


def has_job_edition_permission(oozie_job, user):
  return user.is_superuser or oozie_job.user == user.username

