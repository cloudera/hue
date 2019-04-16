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

from django.urls import reverse
from django.http import QueryDict
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document2

from notebook.connectors.base import Api, QueryError


LOG = logging.getLogger(__name__)


try:
  from oozie.models2 import Workflow, WorkflowBuilder
  from oozie.views.api import get_log as get_workflow_logs
  from oozie.views.dashboard import check_job_access_permission, check_job_edition_permission
  from oozie.views.editor2 import _submit_workflow
except Exception, e:
  LOG.exception('Oozie application is not enabled: %s' % e)


class OozieApi(Api):

  LOG_START_PATTERN = '(>>> Invoking Main class now >>>.+)'
  LOG_END_PATTERN = '<<< Invocation of Main class completed <<<'
  RESULTS_PATTERN = "(?P<results>>>> Invoking Beeline command line now >>>.+<<< Invocation of Beeline command completed <<<)"
  RESULTS_PATTERN_GENERIC = "(?P<results>>>> Invoking Main class now >>>.+<<< Invocation of Main class completed <<<)"
  RESULTS_PATTERN_MAPREDUCE = "(?P<results>.+)"
  RESULTS_PATTERN_PIG = "(?P<results>>>> Invoking Pig command line now >>>.+<<< Invocation of Pig command completed <<<)"
  BATCH_JOB_PREFIX = 'Batch'
  SCHEDULE_JOB_PREFIX = 'Schedule'

  def __init__(self, *args, **kwargs):
    Api.__init__(self, *args, **kwargs)

    self.fs = self.request.fs
    self.jt = self.request.jt


  def execute(self, notebook, snippet):
    # Get document from notebook
    if not notebook.get('uuid', ''):
      raise PopupException(_('Notebook is missing a uuid, please save the notebook before executing as a batch job.'))

    if notebook['type'] == 'notebook' or notebook['type'] == 'query-java':
      # Convert notebook to workflow
      workflow_doc = WorkflowBuilder().create_notebook_workflow(notebook=notebook, user=self.user, managed=True, name=_("%s for %s") % (OozieApi.BATCH_JOB_PREFIX, notebook['name'] or notebook['type']))
      workflow = Workflow(document=workflow_doc, user=self.user)
    else:
      notebook_doc = Document2.objects.get_by_uuid(user=self.user, uuid=notebook['uuid'], perm_type='read')
      # Create a managed workflow from the notebook doc
      workflow_doc = WorkflowBuilder().create_workflow(document=notebook_doc, user=self.user, managed=True, name=_("Batch job for %s") % (notebook_doc.name or notebook_doc.type))
      workflow = Workflow(document=workflow_doc, user=self.user)

    # Submit workflow
    job_id = _submit_workflow(user=self.user, fs=self.fs, jt=self.jt, workflow=workflow, mapping=None)

    return {
      'id': job_id,
      'has_result_set': True,
    }


  def check_status(self, notebook, snippet):
    response = {'status': 'running'}

    job_id = snippet['result']['handle']['id']
    oozie_job = check_job_access_permission(self.request, job_id)

    if oozie_job.is_running():
      return response
    elif oozie_job.status in ('KILLED', 'FAILED'):
      raise QueryError(_('Job was %s') % oozie_job.status)
    else:
      # Check if job results are actually available, since YARN takes a while to move logs to JHS,
      log_output = self.get_log(notebook, snippet)
      if log_output:
        results = self._get_results(log_output, snippet['type'])
        if results:
          response['status'] = 'available'
        else:
          LOG.warn('No log result could be matched for %s' % job_id)
      else:
        response['status'] = 'failed'

    return response


  def fetch_result(self, notebook, snippet, rows, start_over):
    log_output = self.get_log(notebook, snippet)
    results = self._get_results(log_output, snippet['type'])

    return {
        'data':  [[line] for line in results.split('\n')],  # hdfs_link()
        'meta': [{'name': 'Header', 'type': 'STRING_TYPE', 'comment': ''}],
        'type': 'table',
        'has_more': False,
    }


  def cancel(self, notebook, snippet):
    job_id = snippet['result']['handle']['id']

    job = check_job_access_permission(self, job_id)
    oozie_job = check_job_edition_permission(job, self.user)

    oozie_job.kill()

    return {'status': 0}


  def get_log(self, notebook, snippet, startFrom=0, size=None):
    job_id = snippet['result']['handle']['id']

    oozie_job = check_job_access_permission(self.request, job_id)
    logs = self._get_log_output(oozie_job)

    return logs if logs else oozie_job.log


  def progress(self, notebook, snippet, logs=None):
    job_id = snippet['result']['handle']['id']

    oozie_job = check_job_access_permission(self.request, job_id)
    return oozie_job.get_progress()


  def get_jobs(self, notebook, snippet, logs):
    jobs = []
    job_id = snippet['result']['handle']['id']

    oozie_job = check_job_access_permission(self.request, job_id)
    actions = oozie_job.get_working_actions()
    for action in actions:
      if action.externalId is not None:
        jobs.append({
          'name': action.externalId,
          'url': reverse('jobbrowser.views.single_job', kwargs={'job': action.externalId}),
          'started': action.startTime is not None,
          'finished': action.endTime is not None
        })
    return jobs


  def close_statement(self, notebook, snippet):
    pass


  def close_session(self, session):
    pass


  def _get_log_output(self, oozie_workflow):
    log_output = ''
    q = self.request.GET.copy()
    q['format'] = 'python'  # Hack for triggering the good section in single_task_attempt_logs
    self.request.GET = q

    attempts = 0
    max_attempts = 10
    logs_found = False
    while not logs_found and attempts < max_attempts:
      logs, workflow_actions, is_really_done = get_workflow_logs(self.request, oozie_workflow, make_links=False,
                                                                 log_start_pattern=self.LOG_START_PATTERN,
                                                                 log_end_pattern=self.LOG_END_PATTERN)
      if logs:
        log_output = logs.values()[0]
        if log_output.startswith('Unable to locate'):
          LOG.debug('Failed to get job attempt logs, possibly due to YARN archiving job to JHS. Will sleep and try again.')
          time.sleep(2.0)
        else:
          logs_found = True

      attempts += 1
    return log_output


  def _get_results(self, log_output, action_type):
    results = ''

    if action_type == 'hive':
      pattern = self.RESULTS_PATTERN
    elif action_type == 'pig':
      pattern = self.RESULTS_PATTERN_PIG
    elif action_type == 'mapreduce':
      pattern = self.RESULTS_PATTERN_MAPREDUCE
    else:
      pattern = self.RESULTS_PATTERN_GENERIC

    re_results = re.compile(pattern, re.M | re.DOTALL)
    if re_results.search(log_output):
      results = re.search(re_results, log_output).group('results').strip()

    return results
