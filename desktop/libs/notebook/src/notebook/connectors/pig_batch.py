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

from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.utils.translation import ugettext as _

from notebook.connectors.base import Api, QueryError


LOG = logging.getLogger(__name__)


try:
  from pig import api
  from pig.models import PigScript2, get_workflow_output, hdfs_link
  from oozie.views.dashboard import check_job_access_permission, check_job_edition_permission
except Exception, e:
  LOG.exception('Pig application is not enabled: %s' % e)


class PigApi(Api):

  def __init__(self, *args, **kwargs):
    Api.__init__(self, *args, **kwargs)

    self.fs = self.request.fs
    self.jt = self.request.jt

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
      'watchUrl': reverse('pig:watch', kwargs={'job_id': oozie_id}) + '?format=python',
      'has_result_set': True,
    }

  def check_status(self, notebook, snippet):
    job_id = snippet['result']['handle']['id']

    oozie_workflow = check_job_access_permission(self.request, job_id)
    logs, workflow_actions, is_really_done = self._get_output(oozie_workflow)

    if is_really_done and not oozie_workflow.is_running():
      if oozie_workflow.status in ('KILLED', 'FAILED'):
        raise QueryError(_('The script failed to run and was stopped'))
      if logs:
        status = 'available'
      else:
        status = 'running' # Tricky case when the logs are being moved by YARN at job completion
    elif oozie_workflow.is_running():
      status = 'running'
    else:
      status = 'failed'

    return {
        'status': status
    }

  def _get_output(self, oozie_workflow):
    q = QueryDict(self.request.GET, mutable=True)
    q['format'] = 'python' # Hack for triggering the good section in single_task_attempt_logs
    self.request.GET = q

    logs, workflow_actions, is_really_done = api.get(self.fs, self.jt, self.user).get_log(self.request, oozie_workflow)

    return logs, workflow_actions, is_really_done

  def fetch_result(self, notebook, snippet, rows, start_over):
    job_id = snippet['result']['handle']['id']

    oozie_workflow = check_job_access_permission(self.request, job_id)
    logs, workflow_actions, is_really_done = self._get_output(oozie_workflow)

    output = logs.get('pig', _('No result'))

    return {
        'data':  [[line] for line in output.split('\n')], # hdfs_link()
        'meta': [{'name': 'Header', 'type': 'STRING_TYPE', 'comment': ''}],
        'type': 'table',
        'has_more': False,
    }

  def cancel(self, notebook, snippet):
    job_id = snippet['result']['handle']['id']

    job = check_job_access_permission(self, job_id)
    check_job_edition_permission(job, self.user)

    api.get(self.fs, self.jt, self.user).stop(job_id)

    return {'status': 0}

  def get_log(self, notebook, snippet, startFrom=0, size=None):
    job_id = snippet['result']['handle']['id']

    oozie_workflow = check_job_access_permission(self.request, job_id)
    logs, workflow_actions, is_really_done = self._get_output(oozie_workflow)

    return logs.get('pig', _('No result'))

  def progress(self, snippet, logs):
    job_id = snippet['result']['handle']['id']

    oozie_workflow = check_job_access_permission(self.request, job_id)
    return oozie_workflow.get_progress(),

  def close_statement(self, snippet):
    pass

  def close_session(self, session):
    pass
