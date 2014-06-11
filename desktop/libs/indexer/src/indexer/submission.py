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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.lib.view_util import format_duration_in_millis
from liboozie.oozie_api import get_oozie
from libsolr import conf as search_conf
from jobbrowser.views import job_single_logs
from oozie.models import Workflow, Shell, Ssh
from oozie.views.editor import _submit_workflow

import utils


LOG = logging.getLogger(__name__)


def get(fs, jt, user):
  return OozieApi(fs, jt, user)


class OozieApi(object):
  """
  Oozie submission.
  """
  WORKFLOW_NAME = 'libsolr-solrctl-script'
  RE_LOG_END = re.compile('(<<< Invocation of Pig command completed <<<|<<< Invocation of Main class completed <<<)')
  RE_LOG_START_RUNNING = re.compile('>>> Invoking Pig command line now >>>(.+?)(<<< Invocation of Pig command completed <<<|<<< Invocation of Main class completed)', re.M | re.DOTALL)
  RE_LOG_START_FINISHED = re.compile('(>>> Invoking Pig command line now >>>)', re.M | re.DOTALL)
  MAX_DASHBOARD_JOBS = 100

  def __init__(self, fs, jt, user):
    self.fs = fs
    self.jt = jt
    self.user = user

  def submit(self, name):
    workflow = None

    try:
      workflow = self._create_workflow(name)
      mapping = dict([(param['name'], param['value']) for param in workflow.get_parameters()])
      oozie_wf = _submit_workflow(self.user, self.fs, self.jt, workflow, mapping)
    finally:
      if workflow:
        workflow.delete(skip_trash=True)

    return oozie_wf

  def _create_workflow(self, name):
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.name = OozieApi.WORKFLOW_NAME
    workflow.is_history = True
    workflow.save()
    Workflow.objects.initialize(workflow, self.fs)

    solr_user = search_conf.SOLRCTL_USER.get()
    solr_host = search_conf.SOLRCTL_HOST.get()
    solr_config_path = os.path.join(search_conf.SOLRCTL_TMP_DIR.get(), 'hue_solr_config')

    rsync_action = Shell.objects.create(
      name='rsync-solr-config',
      workflow=workflow,
      node_type='shell',
      command='rsync -av %(config_path)s %(solr_user)s@%(solr_host)s:%(solr_config_path)s' % {
        'config_path': utils.get_config_template_path(),
        'solr_user': solr_user,
        'solr_host': solr_host,
        'solr_config_path': solr_config_path
      }
    )

    solrctl_action = Ssh.objects.create(
      name='solrctl-create-instance-dir',
      workflow=workflow,
      node_type='ssh',
      user=solr_user,
      host=solr_host,
      command='solrctl instancedir --create %s %s' % (name, solr_config_path)
    )

    rsync_action.add_node(solrctl_action)

    solrctl_action.add_node(workflow.end)

    start_link = workflow.start.get_link()
    start_link.child = rsync_action
    start_link.save()

    return workflow

  def stop(self, job_id):
    return get_oozie(self.user).job_control(job_id, 'kill')

  def get_jobs(self):
    kwargs = {'cnt': OozieApi.MAX_DASHBOARD_JOBS,}
    kwargs['user'] = self.user.username
    kwargs['name'] = OozieApi.WORKFLOW_NAME

    return get_oozie(self.user).get_workflows(**kwargs).jobs

  def get_log(self, request, oozie_workflow):
    logs = {}

    for action in oozie_workflow.get_working_actions():
      try:
        if action.externalId:
          data = job_single_logs(request, **{'job': action.externalId})
          if data:
            matched_logs = self._match_logs(data)
            logs[action.name] = self._make_links(matched_logs)
      except Exception, e:
        LOG.error('An error happen while watching the demo running: %(error)s' % {'error': e})

    workflow_actions = []

    # Shell and Ssh action
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

  def _match_logs(self, data):
    """Difficult to match multi lines of text"""
    logs = data['logs'][1]

    if OozieApi.RE_LOG_END.search(logs):
      return re.search(OozieApi.RE_LOG_START_RUNNING, logs).group(1).strip()
    else:
      group = re.search(OozieApi.RE_LOG_START_FINISHED, logs)
      i = logs.index(group.group(1)) + len(group.group(1))
      return logs[i:].strip()

  def massaged_jobs_for_json(self, request, oozie_jobs, hue_jobs):
    jobs = []
    hue_jobs = dict([(script.dict.get('job_id'), script) for script in hue_jobs if script.dict.get('job_id')])

    for job in oozie_jobs:
      if job.is_running():
        job = get_oozie(self.user).get_job(job.id)
        get_copy = request.GET.copy() # Hacky, would need to refactor JobBrowser get logs
        get_copy['format'] = 'python'
        request.GET = get_copy
        try:
          logs, workflow_action = self.get_log(request, job)
          progress = workflow_action[0]['progress']
        except Exception:
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


def get_progress(job, log):
  if job.status in ('SUCCEEDED', 'KILLED', 'FAILED'):
    return 100
  else:
    try:
      return int(re.findall("MapReduceLauncher  - (1?\d?\d)% complete", log)[-1])
    except:
      return 0


def format_time(st_time):
  if st_time is None:
    return '-'
  else:
    return time.strftime("%a, %d %b %Y %H:%M:%S", st_time)


def has_job_edition_permission(oozie_job, user):
  return user.is_superuser or oozie_job.user == user.username
