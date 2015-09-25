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
import json

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from notebook.connectors.base import Api, QueryError


LOG = logging.getLogger(__name__)


try:
  from pig import api
  from pig.models import PigScript2, get_workflow_output, hdfs_link
  from oozie.views.dashboard import check_job_access_permission, check_job_edition_permission
except ImportError, e:
  LOG.exception('Pig application is not enabled')


class PigApi(Api):

  def execute(self, notebook, snippet):

    attrs = {
      'script': snippet['statement'],
      'name': snippet['properties'].get('name', 'Pig Snippet'),
      'parameters': snippet['properties'].get('parameters'),
      'resources': snippet['properties'].get('resources'),
      'hadoopProperties': snippet['properties'].get('hadoopProperties')
    }

    pig_script = PigScript2(attrs)

    params = json.dumps([])
    oozie_id = api.get(self.fs, self.jt, self.user).submit(pig_script, params)

    return {
      'id': oozie_id,
      'watchUrl': reverse('pig:watch', kwargs={'job_id': oozie_id}) + '?format=python'
    }

  def check_status(self, notebook, snippet):
    job_id = snippet['result']['handle']['id']
    request = MockRequest(self.user, self.fs, self.jt)

    oozie_workflow = check_job_access_permission(request, job_id)
    logs, workflow_actions, is_really_done = api.get(self.jt, self.jt, self.user).get_log(request, oozie_workflow)

    if is_really_done and not oozie_workflow.is_running():
      if oozie_workflow.status in ('KILLED', 'FAILED'):
        raise QueryError(_('The script failed to run and was stopped'))
      status = 'available'
    elif oozie_workflow.is_running():
      status = 'running'
    else:
      status = 'failed'

    return {
        'status': status
    }

  def fetch_result(self, notebook, snippet, rows, start_over):
    job_id = snippet['result']['handle']['id']

    oozie_workflow = check_job_access_permission(MockRequest(self.user, self.fs, self.jt), job_id)
    output = get_workflow_output(oozie_workflow, self.fs)

    return {
        'data':  [hdfs_link(output)],
        'meta': [{'name': 'Header', 'type': 'STRING_TYPE', 'comment': ''}],
        'type': 'text'
    }

  def cancel(self, notebook, snippet):
    job_id = snippet['result']['handle']['id']

    job = check_job_access_permission(self, job_id)
    check_job_edition_permission(job, self.user)

    api.get(self.fs, self.jt, self.user).stop(job_id)

    return {'status': 0}

  def get_log(self, notebook, snippet, startFrom=0, size=None):
    job_id = snippet['result']['handle']['id']
    request = MockRequest(self.user, self.fs, self.jt)

    oozie_workflow = check_job_access_permission(MockRequest(self.user, self.fs, self.jt), job_id)
    logs, workflow_actions, is_really_done = api.get(self.jt, self.jt, self.user).get_log(request, oozie_workflow)

    return logs

  def _progress(self, snippet, logs):
    job_id = snippet['result']['handle']['id']

    oozie_workflow = check_job_access_permission(MockRequest(self.user, self.fs, self.jt), job_id)
    return oozie_workflow.get_progress(),

  def close_statement(self, snippet):
    pass

  def close_session(self, session):
    pass

  def _get_jobs(self, log):
    return []


class MockRequest():

  def __init__(self, user, fs, jt):
    self.user = user
    self.fs = fs
    self.js = jt
