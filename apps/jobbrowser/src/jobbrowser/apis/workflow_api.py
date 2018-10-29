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

from jobbrowser.apis.base_api import Api, MockDjangoRequest, _extract_query_params, is_linkable, hdfs_link_js
from liboozie.oozie_api import get_oozie


LOG = logging.getLogger(__name__)


try:
  from oozie.forms import ParameterForm
  from oozie.conf import OOZIE_JOBS_COUNT, ENABLE_OOZIE_BACKEND_FILTERING
  from oozie.views.dashboard import get_oozie_job_log, list_oozie_workflow, manage_oozie_jobs, bulk_manage_oozie_jobs, has_dashboard_jobs_access, massaged_oozie_jobs_for_json, \
      has_job_edition_permission
  has_oozie_installed = True
except Exception, e:
  LOG.warn('Some applications are not enabled for Job Browser v2: %s' % e)
  has_oozie_installed = False


class WorkflowApi(Api):

  def apps(self, filters):
    oozie_api = get_oozie(self.user)

    kwargs = {'cnt': OOZIE_JOBS_COUNT.get(), 'filters': []}
    _filter_oozie_jobs(self.user, filters, kwargs)

    wf_list = oozie_api.get_workflows(**kwargs)

    return {
      'apps':[{
        'id': app['id'],
        'name': app['appName'],
        'status': app['status'],
        'apiStatus': self._api_status(app['status']),
        'type': 'workflow',
        'user': app['user'],
        'progress': app['progress'],
        'queue': app['group'],
        'duration': app['durationInMillis'],
        'submitted': app['startTimeInMillis'] * 1000,
        'canWrite': app['canEdit']
      } for app in massaged_oozie_jobs_for_json(wf_list.jobs, self.user)['jobs']],
      'total': wf_list.total
    }


  def app(self, appid):
    if '@' in appid:
      return WorkflowActionApi(self.user).app(appid)

    oozie_api = get_oozie(self.user)
    workflow = oozie_api.get_job(jobid=appid)

    common = {
        'id': workflow.id,
        'name': workflow.appName,
        'status': workflow.status,
        'apiStatus': self._api_status(workflow.status),
        'progress': workflow.get_progress(),
        'type': 'workflow',
        'user': workflow.user,
        'duration': workflow.durationTime,
        'submitted': workflow.submissionTime * 1000,
        'canWrite': has_job_edition_permission(workflow, self.user),
    }

    request = MockDjangoRequest(self.user)
    response = list_oozie_workflow(request, job_id=appid)
    common['properties'] = json.loads(response.content)
    common['properties']['xml'] = ''
    common['properties']['properties'] = ''
    common['properties']['coordinator_id'] = workflow.get_parent_job_id()
    common['properties']['bundle_id'] = workflow.conf_dict.get('oozie.bundle.id')
    common['properties']['parameters'] = self._get_variables(workflow)
    common['doc_url'] = common['properties'].get('doc_url')

    return common


  def action(self, app_ids, action):
    return _manage_oozie_job(self.user, action, app_ids)


  def logs(self, appid, app_type, log_name=None, is_embeddable=False):
    if '@' in appid:
      return WorkflowActionApi(self.user).logs(appid, app_type)

    request = MockDjangoRequest(self.user)
    data = get_oozie_job_log(request, job_id=appid)

    return {'logs': json.loads(data.content)['log']}


  def profile(self, appid, app_type, app_property, app_filters):
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
        'properties_display': [{'name': key, 'value': val, 'link': is_linkable(key, val) and hdfs_link_js(val)} for key, val in workflow.conf_dict.iteritems()],
      }

    return {}

  def _api_status(self, status):
    if status in ['PREP', 'RUNNING']:
      return 'RUNNING'
    elif status == 'SUSPENDED':
      return 'PAUSED'
    elif status == 'SUCCEEDED':
      return 'SUCCEEDED'
    else:
      return 'FAILED' # KILLED and FAILED

  def _get_variables(self, workflow):
    parameters = []

    for var, val in workflow.conf_dict.iteritems():
      if var not in ParameterForm.NON_PARAMETERS and var != 'oozie.use.system.libpath' or var == 'oozie.wf.application.path':
        link = ''
        if is_linkable(var, val):
          link = hdfs_link_js(val)
        if var == 'oozie.wf.application.path':
          var = _('Workspace')
        parameters.append({'name': var, 'value': val, 'link': link})

    return parameters


class WorkflowActionApi(Api):

  def app(self, appid):
    oozie_api = get_oozie(self.user)
    action = oozie_api.get_action(action_id=appid)

    common = action.to_json()

    common['action_type'] = common['type']
    common['type'] = 'workflow-action'
    common['properties'] = {}
    properties = action.to_json()
    properties.pop('toString')
    common['properties']['conf'] = properties.pop('conf')
    common['properties']['externalId'] = properties.get('externalId', '')
    common['properties']['externalChildIDs'] = properties.get('externalChildIDs') and properties.pop('externalChildIDs').split(',')
    common['properties']['properties'] = [{'name': key, 'value': val} for key, val in properties.iteritems()]

    common['properties']['workflow_id'] = appid.split('@', 1)[0]

    return common


  def logs(self, appid, app_type, log_name=None):
    return {'progress': 0, 'logs': ''}


def _manage_oozie_job(user, action, app_ids):
  if action == 'change' or action == 'ignore' or len(app_ids) == 1:
    request = MockDjangoRequest(user)
    response = manage_oozie_jobs(request, app_ids[0], action['action'])
  else:
    request = MockDjangoRequest(user, post={'job_ids': ' '.join(app_ids), 'action': action['action']})
    response = bulk_manage_oozie_jobs(request)

  result = json.loads(response.content)
  result['status'] = result.get('totalErrors', 0)
  result['message'] = _('%s action sent to %s jobs') % (action['action'], result.get('totalRequests', 1))
  return result


def _filter_oozie_jobs(user, filters, kwargs):
    text_filters = _extract_query_params(filters)

    if has_oozie_installed and not has_dashboard_jobs_access(user):
      kwargs['filters'].append(('user', user.username))
    elif 'username' in text_filters:
      kwargs['filters'].append(('user', text_filters['username']))

    if 'time' in filters:
      kwargs['filters'].extend([('startcreatedtime', '-%s%s' % (filters['time']['time_value'], filters['time']['time_unit'][:1]))])

    if has_oozie_installed and ENABLE_OOZIE_BACKEND_FILTERING.get() and text_filters.get('text'):
      kwargs['filters'].extend([('text', text_filters.get('text'))])

    if filters['pagination']:
      kwargs['offset'] = filters['pagination']['offset']
      kwargs['cnt'] = min(filters['pagination']['limit'], hasattr(OOZIE_JOBS_COUNT, 'get') and OOZIE_JOBS_COUNT.get())

    if filters.get('states'):
      states_filters = {'running': ['RUNNING', 'PREP', 'SUSPENDED'], 'completed': ['SUCCEEDED'], 'failed': ['FAILED', 'KILLED'],}
      for _state in filters.get('states'):
        for _status in states_filters[_state]:
          kwargs['filters'].extend([('status', _status)])
