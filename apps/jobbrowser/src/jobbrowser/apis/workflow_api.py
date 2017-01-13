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

from jobbrowser.apis.base_api import Api, MockDjangoRequest
from liboozie.oozie_api import get_oozie
from oozie.views.dashboard import list_oozie_workflow_action


LOG = logging.getLogger(__name__)


try:
  from oozie.conf import OOZIE_JOBS_COUNT
  from oozie.views.dashboard import get_oozie_job_log, list_oozie_workflow, manage_oozie_jobs, bulk_manage_oozie_jobs
except Exception, e:
  LOG.exception('Some applications are not enabled for Job Browser v2: %s' % e)


class WorkflowApi(Api):

  def apps(self):
    oozie_api = get_oozie(self.user)
    kwargs = {'cnt': OOZIE_JOBS_COUNT.get(), 'filters': []}
    wf_list = oozie_api.get_workflows(**kwargs)

    return [{
        'id': app.id,
        'name': app.appName,
        'status': app.status,
        'type': 'workflow',
        'user': app.user,
        'progress': 100,
        'duration': 10 * 3600,
        'submitted': 10 * 3600
    } for app in wf_list.jobs]


  def app(self, appid):
    if '@' in appid:
      return WorkflowActionApi(self.user).app(appid)

    oozie_api = get_oozie(self.user)
    workflow = oozie_api.get_job(jobid=appid)

    common = {'id': workflow.id, 'name': workflow.appName, 'status': workflow.status, 'type': 'workflow'}

    request = MockDjangoRequest(self.user)
    response = list_oozie_workflow(request, job_id=appid)
    common['properties'] = json.loads(response.content)
    common['properties']['xml'] = ''
    common['properties']['properties'] = ''

    return common


  def action(self, appid, action):
    if action == 'change' or action == 'ignore' or ',' not in appid:
      request = MockDjangoRequest(self.user)
      response = manage_oozie_jobs(request, appid, action['action'])
    else:
      request = MockDjangoRequest(self.user, post={'job_ids': appid, 'action': action['action']})
      response = bulk_manage_oozie_jobs(request)

    return json.loads(response.content)


  def logs(self, appid, app_type):
    if '@' in appid:
      return WorkflowActionApi(self.user).logs(appid, app_type)

    request = MockDjangoRequest(self.user)
    data = get_oozie_job_log(request, job_id=appid)

    return {'progress': 0, 'logs': {'default': json.loads(data.content)['log']}}


  def profile(self, appid, app_type, app_property):
    if '@' in appid:
      return WorkflowActionApi(self.self.user).profile(appid, app_type, app_property)

    if app_property == 'xml':
      oozie_api = get_oozie(self.user)
      workflow = oozie_api.get_job(jobid=appid)
      return {
        'xml': workflow.definition,
      }
    elif app_property == 'properties':
      oozie_api = get_oozie(self.user)
      workflow = oozie_api.get_job(jobid=appid)
      return {
        'properties': workflow.conf_dict,
      }

    return {}


class WorkflowActionApi(Api):

  def app(self, appid):
    oozie_api = get_oozie(self.user)
    action = oozie_api.get_action(action_id=appid)

    common = action.to_json()
    
    common['action_type'] = common['type']
    common['type'] = 'workflow-action'

    return common


  def logs(self, appid, app_type):
    return {'progress': 0, 'logs': {'default': ''}}
