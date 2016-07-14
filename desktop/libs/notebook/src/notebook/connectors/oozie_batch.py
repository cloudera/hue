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

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document2

from notebook.connectors.base import Api


LOG = logging.getLogger(__name__)


try:
  from oozie.models2 import Workflow, WorkflowBuilder
  from oozie.views.dashboard import check_job_access_permission, check_job_edition_permission
  from oozie.views.editor2 import _submit_workflow
except Exception, e:
  LOG.exception('Oozie application is not enabled: %s' % e)


class OozieApi(Api):

  def __init__(self, *args, **kwargs):
    Api.__init__(self, *args, **kwargs)

    self.fs = self.request.fs
    self.jt = self.request.jt

  def execute(self, notebook, snippet):
    # Get document from notebook
    if not notebook.get('uuid', ''):
      raise PopupException(_('Notebook is missing a uuid, please save the notebook before executing as a batch job.'))

    notebook_doc = Document2.objects.get_by_uuid(user=self.user, uuid=notebook['uuid'], perm_type='read')

    # Verify that the document is a valid Oozie batch type
    if not notebook_doc.type == 'query-hive':
      raise PopupException(_('Oozie batch submission only accepts Hive queries at this time.'))

    # Create a managed workflow from the notebook doc
    workflow_doc = WorkflowBuilder().create_workflow(document=notebook_doc, user=self.user, managed=True, name=_("Batch job for %s") % notebook_doc.name)
    workflow = Workflow(document=workflow_doc)

    # Submit workflow
    job_id = _submit_workflow(user=self.user, fs=self.fs, jt=self.jt, workflow=workflow, mapping=None)

    return {
      'id': job_id,
      'has_result_set': True,
    }

  def check_status(self, notebook, snippet):
    response = {}
    job_id = snippet['result']['handle']['id']
    oozie_job = check_job_access_permission(self.request, job_id)

    response['status'] = 'running' if oozie_job.is_running() else 'available'

    return response

  def fetch_result(self, notebook, snippet, rows, start_over):
    output = self.get_log(notebook, snippet)

    return {
        'data':  [[line] for line in output.split('\n')], # hdfs_link()
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
    status_resp = oozie_job.log

    return status_resp

  def progress(self, snippet, logs):
    job_id = snippet['result']['handle']['id']

    oozie_job = check_job_access_permission(self.request, job_id)
    return oozie_job.get_progress(),

  def close_statement(self, snippet):
    pass

  def close_session(self, session):
    pass
