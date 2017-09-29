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

import itertools
import logging

from django.utils.translation import ugettext as _

from jobbrowser.apis.base_api import Api

LOG = logging.getLogger(__name__)


try:
  from beeswax.models import Session
  from impala.server import get_api as get_impalad_api, _get_impala_server_url
except Exception, e:
  LOG.exception('Some application are not enabled: %s' % e)


class QueryApi(Api):

  def __init__(self, user):
    self.user = user
    session = Session.objects.get_session(self.user, application='impala')
    self.server_url = _get_impala_server_url(session)

  def apps(self, filters):
    kwargs = {}

    api = get_impalad_api(user=self.user, url=self.server_url)

    jobs = api.get_queries(**kwargs)

    return {
      'apps': [{
        'id': app['query_id'],
        'name': app['stmt'][:100] + ('...' if len(app['stmt']) > 100 else ''),
        'status': app['state'],
        'apiStatus': self._api_status(app['state']),
        'type': app['stmt_type'],
        'user': app['effective_user'],
        'queue': app['resource_pool'],
        'progress': app['progress'],
        'duration': 0, # app['duration'],
        'submitted': app['start_time'],
        # Extra specific
        'rows_fetched': app['rows_fetched'],
        'waiting': app['waiting'],
        'waiting_time': app['waiting_time']
      } for app in itertools.chain(jobs['in_flight_queries'], jobs['completed_queries'])],
      'total': jobs['num_in_flight_queries'] + jobs['num_executing_queries'] + jobs['num_waiting_queries']
    }

  def app(self, appid):
    api = get_impalad_api(user=self.user, url=self.server_url)

    query = api.get_query(query_id=appid)

    common = {
        'id': appid,
        'name': query['stmt'][:100] + ('...' if len(query['stmt']) > 100 else ''),
        'status': query['status'],
        'apiStatus': self._api_status(query['status']),
        'progress': 50,
        'duration': 10 * 3600,
        'submitted': 0,
        'type': 'NA',
    }

    common['properties'] = {
      'properties': query
    }

    return common


  def action(self, appid, action):
    return {}


  def logs(self, appid, app_type, log_name=None):
    return {'logs': ''}


  def profile(self, appid, app_type, app_property):
    return {}

  def _api_status(self, status):
    if status in ['CREATING', 'CREATED', 'TERMINATING']:
      return 'RUNNING'
    elif status in ['COMPLETED']:
      return 'SUCCEEDED'
    else:
      return 'FAILED' # INTERRUPTED , KILLED, TERMINATED and FAILED
