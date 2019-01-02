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
import time

from django.urls import reverse
from django.utils.translation import ugettext as _

from desktop.lib.i18n import smart_str
from desktop.lib.view_util import format_duration_in_millis
from liboozie.oozie_api import get_oozie
from oozie.models import Workflow, Pig
from oozie.views.api import get_log as get_workflow_logs
from oozie.views.editor import _submit_workflow
from desktop.auth.backend import is_admin


LOG = logging.getLogger(__name__)


def get(fs, jt, user):
  return OozieApi(fs, jt, user)


class OozieApi(object):
  """
  Oozie submission.
  """

  WORKFLOW_NAME = 'pig-app-hue-script'
  LOG_START_PATTERN = '(Pig script \[(?:[\w.-]+)\] content:.+)'
  LOG_END_PATTERN = '(&lt;&lt;&lt; Invocation of Pig command completed &lt;&lt;&lt;|' \
                    '&lt;&lt;&lt; Invocation of Main class completed &lt;&lt;&lt;|' \
                    '<<< Invocation of Pig command completed <<<|' \
                    '<<< Invocation of Main class completed <<<)'
  MAX_DASHBOARD_JOBS = 100


  def __init__(self, fs, jt, user):
    self.oozie_api = get_oozie(user)
    self.fs = fs
    self.jt = jt
    self.user = user


  def submit(self, pig_script, params):
    workflow = None

    try:
      workflow = self._create_workflow(pig_script, params)
      mapping = dict([(param['name'], param['value']) for param in workflow.get_parameters()])
      oozie_wf = _submit_workflow(self.user, self.fs, self.jt, workflow, mapping)
    finally:
      if workflow:
        workflow.delete(skip_trash=True)

    return oozie_wf


  def _create_workflow(self, pig_script, params):
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.schema_version = 'uri:oozie:workflow:0.5'
    workflow.name = OozieApi.WORKFLOW_NAME
    workflow.is_history = True
    if pig_script.use_hcatalog:
      workflow.add_parameter("oozie.action.sharelib.for.pig", "pig,hcatalog,hive")
    workflow.save()
    Workflow.objects.initialize(workflow, self.fs)

    script_path = workflow.deployment_dir + '/script.pig'
    if self.fs: # For testing, difficult to mock
      self.fs.do_as_user(self.user.username, self.fs.create, script_path, data=smart_str(pig_script.dict['script']))

    files = []
    archives = []

    popup_params = json.loads(params)
    popup_params_names = [param['name'] for param in popup_params]
    pig_params = self._build_parameters(popup_params)

    if pig_script.isV2:
      pig_params += [{"type": "argument", "value": param} for param in pig_script.dict['parameters']]

      job_properties = [{"name": prop.split('=', 1)[0], "value": prop.split('=', 1)[1]} for prop in pig_script.dict['hadoopProperties']]

      for resource in pig_script.dict['resources']:
        if resource.endswith('.zip') or resource.endswith('.tgz') or resource.endswith('.tar') or resource.endswith('.gz'):
          archives.append({"dummy": "", "name": resource})
        else:
          files.append(resource)

    else:
      script_params = [param for param in pig_script.dict['parameters'] if param['name'] not in popup_params_names]

      pig_params += self._build_parameters(script_params)

      job_properties = [{"name": prop['name'], "value": prop['value']} for prop in pig_script.dict['hadoopProperties']]

      for resource in pig_script.dict['resources']:
        if resource['type'] == 'file':
          files.append(resource['value'])
        if resource['type'] == 'archive':
          archives.append({"dummy": "", "name": resource['value']})

    action = Pig.objects.create(
        name='pig-5760',
        script_path=script_path,
        workflow=workflow,
        node_type='pig',
        params=json.dumps(pig_params),
        files=json.dumps(files),
        archives=json.dumps(archives),
        job_properties=json.dumps(job_properties)
    )

    credentials = []
    if pig_script.use_hcatalog and self.oozie_api.security_enabled:
      credentials.append({'name': 'hcat', 'value': True})
    if pig_script.use_hbase and self.oozie_api.security_enabled:
      credentials.append({'name': 'hbase', 'value': True})
    if credentials:
      action.credentials = credentials # Note, action.credentials is a @setter here
      action.save()

    action.add_node(workflow.end)

    start_link = workflow.start.get_link()
    start_link.child = action
    start_link.save()

    return workflow


  def _build_parameters(self, params):
    pig_params = []

    for param in params:
      if param['name'].startswith('-'):
        pig_params.append({"type": "argument", "value": "%(name)s" % param})
        if param['value']:
          pig_params.append({"type": "argument", "value": "%(value)s" % param})
      else:
        # Simpler way and backward compatibility for parameters
        pig_params.append({"type": "argument", "value": "-param"})
        pig_params.append({"type": "argument", "value": "%(name)s=%(value)s" % param})

    return pig_params


  def stop(self, job_id):
    return self.oozie_api.job_control(job_id, 'kill')


  def get_jobs(self):
    kwargs = {'cnt': OozieApi.MAX_DASHBOARD_JOBS,}
    kwargs['filters'] = [
        ('user', self.user.username),
        ('name', OozieApi.WORKFLOW_NAME)
    ]

    return self.oozie_api.get_workflows(**kwargs).jobs


  def get_log(self, request, oozie_workflow, make_links=True):
    return get_workflow_logs(request, oozie_workflow, make_links=make_links, log_start_pattern=self.LOG_START_PATTERN,
                             log_end_pattern=self.LOG_END_PATTERN)


  def massaged_jobs_for_json(self, request, oozie_jobs, hue_jobs):
    jobs = []
    hue_jobs = dict([(script.dict.get('job_id'), script) for script in hue_jobs if script.dict.get('job_id')])

    for job in oozie_jobs:
      if job.is_running():
        job = self.oozie_api.get_job(job.id)
        get_copy = request.GET.copy() # Hacky, would need to refactor JobBrowser get logs
        get_copy['format'] = 'python'
        request.GET = get_copy
        try:
          logs, workflow_action, is_really_done = self.get_log(request, job)
          progress = workflow_action[0]['progress']
        except:
          LOG.exception('failed to get progress')
          progress = 0
      else:
        progress = 100

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
        'scriptContent': hue_pig and hue_pig.dict['script'] or '',
        'progress': progress,
        'progressPercent': '%d%%' % progress,
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


def format_time(st_time):
  if st_time is None:
    return '-'
  else:
    return time.strftime("%a, %d %b %Y %H:%M:%S", st_time)


def has_job_edition_permission(oozie_job, user):
  return is_admin(user) or oozie_job.user == user.username

