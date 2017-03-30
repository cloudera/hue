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

from jobbrowser.apis.base_api import Api, MockDjangoRequest, _extract_query_params
from liboozie.oozie_api import get_oozie
from notebook.connectors.dataeng_batch import DataEng


LOG = logging.getLogger(__name__)


class DataEngClusterApi(Api):

  def apps(self, filters):
#     kwargs = {'cnt': OOZIE_JOBS_COUNT.get(), 'filters': []}
# 
#     text_filters = _extract_query_params(filters)
# 
#     if not has_dashboard_jobs_access(self.user):
#       kwargs['filters'].append(('user', self.user.username))
#     elif 'user' in text_filters:
#       kwargs['filters'].append(('user', text_filters['username']))
# 
#     if 'time' in filters:
#       kwargs['filters'].extend([('startcreatedtime', '-%s%s' % (filters['time']['time_value'], filters['time']['time_unit'][:1]))])
# 
#     if ENABLE_OOZIE_BACKEND_FILTERING.get() and text_filters.get('text'):
#       kwargs['filters'].extend([('text', text_filters.get('text'))])
# 
#     if filters.get('states'):
#       states_filters = {'running': ['RUNNING', 'PREP', 'SUSPENDED'], 'completed': ['SUCCEEDED'], 'failed': ['FAILED', 'KILLED'],}
#       for _state in filters.get('states'):
#         for _status in states_filters[_state]:
#           kwargs['filters'].extend([('status', _status)])

    api = DataEng(self.user)

    jobs = api.list_clusters()
    
    return [{
        'id': app['clusterName'],
        'name': '%(workersGroupSize)s %(instanceType)s %(cdhVersion)s' % app,
        'status': app['status'],
        'apiStatus': self._api_status(app['status']),
        'type': app['serviceType'],
        'user': app['clusterName'].split('-', 1)[0],
        'progress': 100,
        'duration': 10 * 3600,
        'submitted': app['creationDate']
    } for app in jobs['clusters']]


  def app(self, appid):
    oozie_api = get_oozie(self.user)
    workflow = oozie_api.get_job(jobid=appid)

    common = {
        'id': workflow.id,
        'name': workflow.appName,
        'status': workflow.status,
        'apiStatus': self._api_status(workflow.status),
        'progress': workflow.get_progress(),
        'type': 'workflow',
    }

    request = MockDjangoRequest(self.user)
    response = list_oozie_workflow(request, job_id=appid)
    common['properties'] = json.loads(response.content)
    common['properties']['xml'] = ''
    common['properties']['properties'] = ''
    common['properties']['coordinator_id'] = workflow.get_parent_job_id()
    common['properties']['bundle_id'] = workflow.conf_dict.get('oozie.bundle.id')

    return common


  def action(self, appid, action):
    if action == 'change' or action == 'ignore' or ',' not in appid:
      request = MockDjangoRequest(self.user)
      response = manage_oozie_jobs(request, appid, action['action'])
    else:
      request = MockDjangoRequest(self.user, post={'job_ids': appid, 'action': action['action']})
      response = bulk_manage_oozie_jobs(request)

    return json.loads(response.content)


  def logs(self, appid, app_type, log_name=None):
    request = MockDjangoRequest(self.user)
    data = get_oozie_job_log(request, job_id=appid)

    return {'logs': json.loads(data.content)['log']}


  def profile(self, appid, app_type, app_property):
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

  def _api_status(self, status):
    if status in ['CREATING', 'CREATED', 'TERMINATING']:
      return 'RUNNING'
    else:
      return 'FINISHED' # SUCCEEDED , KILLED and FAILED


class DataEngJobApi(Api):

  def apps(self, filters):
#     kwargs = {'cnt': OOZIE_JOBS_COUNT.get(), 'filters': []}
# 
#     text_filters = _extract_query_params(filters)
# 
#     if not has_dashboard_jobs_access(self.user):
#       kwargs['filters'].append(('user', self.user.username))
#     elif 'user' in text_filters:
#       kwargs['filters'].append(('user', text_filters['username']))
# 
#     if 'time' in filters:
#       kwargs['filters'].extend([('startcreatedtime', '-%s%s' % (filters['time']['time_value'], filters['time']['time_unit'][:1]))])
# 
#     if ENABLE_OOZIE_BACKEND_FILTERING.get() and text_filters.get('text'):
#       kwargs['filters'].extend([('text', text_filters.get('text'))])
# 
#     if filters.get('states'):
#       states_filters = {'running': ['RUNNING', 'PREP', 'SUSPENDED'], 'completed': ['SUCCEEDED'], 'failed': ['FAILED', 'KILLED'],}
#       for _state in filters.get('states'):
#         for _status in states_filters[_state]:
#           kwargs['filters'].extend([('status', _status)])

    api = DataEng(self.user)

    jobs = api.list_jobs()

    return [{
        'id': app.id,
        'name': app.appName,
        'status': app.status,
        'apiStatus': self._api_status(app.status),
        'type': 'workflow',
        'user': app.user,
        'progress': app.get_progress(),
        'duration': 10 * 3600,
        'submitted': 10 * 3600
    } for app in wf_list.jobs]


  def app(self, appid):
    oozie_api = get_oozie(self.user)
    workflow = oozie_api.get_job(jobid=appid)

    common = {
        'id': workflow.id,
        'name': workflow.appName,
        'status': workflow.status,
        'apiStatus': self._api_status(workflow.status),
        'progress': workflow.get_progress(),
        'type': 'workflow',
    }

    request = MockDjangoRequest(self.user)
    response = list_oozie_workflow(request, job_id=appid)
    common['properties'] = json.loads(response.content)
    common['properties']['xml'] = ''
    common['properties']['properties'] = ''
    common['properties']['coordinator_id'] = workflow.get_parent_job_id()
    common['properties']['bundle_id'] = workflow.conf_dict.get('oozie.bundle.id')

    return common


  def action(self, appid, action):
    if action == 'change' or action == 'ignore' or ',' not in appid:
      request = MockDjangoRequest(self.user)
      response = manage_oozie_jobs(request, appid, action['action'])
    else:
      request = MockDjangoRequest(self.user, post={'job_ids': appid, 'action': action['action']})
      response = bulk_manage_oozie_jobs(request)

    return json.loads(response.content)


  def logs(self, appid, app_type, log_name=None):
    request = MockDjangoRequest(self.user)
    data = get_oozie_job_log(request, job_id=appid)

    return {'logs': json.loads(data.content)['log']}


  def profile(self, appid, app_type, app_property):
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

  def _api_status(self, status):
    if status in ['PREP', 'RUNNING']:
      return 'RUNNING'
    elif status == 'SUSPENDED':
      return 'PAUSED'
    else:
      return 'FINISHED' # SUCCEEDED , KILLED and FAILED

