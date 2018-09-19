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

from liboozie.oozie_api import get_oozie

from jobbrowser.apis.base_api import Api, MockDjangoRequest
from jobbrowser.apis.workflow_api import _manage_oozie_job, _filter_oozie_jobs
from jobbrowser.apis.schedule_api import MockGet


LOG = logging.getLogger(__name__)


try:
  from oozie.conf import OOZIE_JOBS_COUNT
  from oozie.views.dashboard import get_oozie_job_log, massaged_oozie_jobs_for_json, list_oozie_bundle
except Exception, e:
  LOG.exception('Some application are not enabled: %s' % e)


class BundleApi(Api):

  def apps(self, filters):
    oozie_api = get_oozie(self.user)

    kwargs = {'cnt': OOZIE_JOBS_COUNT.get(), 'filters': []}

    filters.pop('time')

    _filter_oozie_jobs(self.user, filters, kwargs)

    jobs = oozie_api.get_bundles(**kwargs)

    return {
      'apps':[{
        'id': app['id'],
        'name': app['appName'],
        'status': app['status'],
        'apiStatus': self._api_status(app['status']),
        'type': 'bundle',
        'user': app['user'],
        'progress': app['progress'],
        'queue': app['group'],
        'duration': app['durationInMillis'],
        'submitted': app['kickoffTimeInMillis'] * 1000,
        'canWrite': app['canEdit']
      } for app in massaged_oozie_jobs_for_json(jobs.jobs, self.user)['jobs']],
      'total': jobs.total
    }


  def app(self, appid):
    request = MockDjangoRequest(self.user, get=MockGet())
    response = list_oozie_bundle(request, job_id=appid)
    bundle = json.loads(response.content)

    common = {
        'id': bundle['id'],
        'name': bundle['name'],
        'status': bundle['status'],
        'apiStatus': self._api_status(bundle['status']),
        'progress': bundle['progress'],
        'type': 'bundle',
        'user': bundle['user'],
        'submitted': bundle['submitted'],
        'canWrite': bundle['canEdit'],
        'properties': {}
    }
    common['properties']['actions'] = bundle['actions']
    common['properties']['xml'] = ''
    common['properties']['properties'] = ''
    common['doc_url'] = bundle.get('doc_url')

    return common


  def action(self, app_ids, action):
    return _manage_oozie_job(self.user, action, app_ids)


  def logs(self, appid, app_type, log_name=None, is_embeddable=False):
    request = MockDjangoRequest(self.user)
    data = get_oozie_job_log(request, job_id=appid)

    return {'logs': json.loads(data.content)['log']}


  def profile(self, appid, app_type, app_property, app_filters):
    if app_property == 'xml':
      oozie_api = get_oozie(self.user)
      workflow = oozie_api.get_bundle(jobid=appid)
      return {
        'xml': workflow.definition,
      }
    elif app_property == 'properties':
      oozie_api = get_oozie(self.user)
      workflow = oozie_api.get_bundle(jobid=appid)
      return {
        'properties': workflow.conf_dict,
      }

  def _api_status(self, status):
    if status in ['PREP', 'RUNNING', 'RUNNINGWITHERROR']:
      return 'RUNNING'
    elif status in ['PREPSUSPENDED', 'SUSPENDED', 'SUSPENDEDWITHERROR', 'PREPPAUSED', 'PAUSED', 'PAUSEDWITHERROR']:
      return 'PAUSED'
    elif status == 'SUCCEEDED':
      return 'SUCCEEDED'
    else:
      return 'FAILED' # DONEWITHERROR, KILLED, FAILED

