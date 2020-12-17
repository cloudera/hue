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
from builtins import filter

import logging
from logging import exception

from datetime import datetime
from django.utils.translation import ugettext as _

from beeswax.models import QueryHistory
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.python_util import current_ms_from_utc
from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource
from notebook.models import _get_notebook_api, make_notebook, MockRequest

from jobbrowser.apis.base_api import Api
from jobbrowser.conf import QUERY_STORE
from jobbrowser.models import HiveQuery


LOG = logging.getLogger(__name__)

class HiveQueryApi(Api):
  HEADERS = {'X-Requested-By': 'das'}

  def __init__(self, user, cluster=None):
    self.user = user
    self.cluster = cluster
    self.api = HiveQueryClient()

  def apps(self, filters):
    queries = self.api.get_queries(filters)

    apps = {
      "apps": {
        "queries": [{
            "details": None,
            "dags": [],
            "id": query.id,
            "queryId": query.query_id,
            "startTime": query.start_time,
            "query": query.query.replace('\r\n', ' ')[:60] + ('...' if len(query.query) > 60 else ''),
            "highlightedQuery": None,
            "endTime": query.end_time,
            "elapsedTime": query.elapsed_time,
            "status": query.status,
            "queueName": query.queue_name,
            "userId": query.user_id,
            "requestUser": query.request_user,
            "cpuTime": query.cpu_time,
            "physicalMemory": query.physical_memory,
            "virtualMemory": query.virtual_memory,
            "dataRead": query.data_read,
            "dataWritten": query.data_written,
            "operationId": query.operation_id,
            "clientIpAddress": query.client_ip_address,
            "hiveInstanceAddress": query.hive_instance_address,
            "hiveInstanceType": query.hive_instance_type,
            "sessionId": query.session_id,
            "logId": query.log_id,
            "threadId": query.thread_id,
            "executionMode": query.execution_mode,
            "tablesRead": query.tables_read,
            "tablesWritten": query.tables_written,
            "databasesUsed": query.databases_used,
            "domainId": query.domain_id,
            "llapAppId": query.llap_app_id,
            "usedCBO": query.used_cbo,
            "createdAt": query.created_at
          }
          for query in queries
        ],
        "meta": {
            "limit": filters['limit'],
            "offset": filters['offset'],
            "size": self.api.get_query_count(filters)
          }
      }
    }

    return apps

  def app(self, appid):
    query = self.api.get_query(query_id=appid)

    if not query:
      raise PopupException(_('Could not find query id %s' % appid))

    params = {
      'extended': 'true',
      'queryId': query.query_id
    }

    client = HttpClient(QUERY_STORE.SERVER_URL.get())
    resource = Resource(client)
    app = resource.get('api/hive/query', params=params, headers=self.HEADERS)

    return app

  def action(self, query_ids, action):
    message = {'actions': {}, 'status': 0}

    if action.get('action') == 'kill':
      for query_id in query_ids:
        action_details = {}

        try:
          request = MockRequest(user=self.user)
          self.kill_query(query_id, request)
          action_details['status'] = 0
          action_details['message'] = _('kill action performed')
        except Exception as ex:
          LOG.error(ex)
          message['status'] = -1
          action_details['status'] = -1
          action_details['message'] = _('kill action failed : %s' % str(ex))

        message['actions'][query_id] = action_details;

    return message

  def kill_query(self, query_id, request):
    kill_sql = 'KILL QUERY "%s";' % query_id
    job = make_notebook(
        name=_('Kill query %s') % query_id,
        editor_type='hive',
        statement=kill_sql,
        status='ready',
        on_success_url='assist.db.refresh',
        is_task=False,
    )

    job.execute_and_wait(request)

  def logs(self, appid, app_type, log_name=None, is_embeddable=False):
    return {'logs': ''}

  def profile(self, appid, app_type, app_property, app_filters):
    message = {'message': '', 'status': 0}

    return message;

  def _api_status(self, status):
    if status == 'SUCCESS':
      return 'SUCCEEDED'
    elif status == 'EXCEPTION':
      return 'FAILED'
    elif status == 'RUNNING':
      return 'RUNNING'
    else:
      return 'PAUSED'


class HiveQueryClient():

  def _get_all_queries(self):
    return HiveQuery.objects.using('query').order_by('-start_time')

  def _get_queries(self, filters):
    queries = self._get_all_queries()
    queries = queries.filter(start_time__gte=filters['startTime'], end_time__lte=filters['endTime'])
    if filters['text']:
      queries = queries.filter(query__icontains=filters['text'])

    for facet in filters['facets']:
      queries = queries.filter(**{facet['field']+'__in': facet['values']})

    return queries

  def get_query_count(self, filters):
    filtered_query_list = self._get_queries(filters)

    return len(filtered_query_list)

  def get_queries(self, filters):
    filtered_query_list = self._get_queries(filters)
    paginated_query_list = filtered_query_list[filters['offset']:filters['offset'] + filters['limit']]

    return paginated_query_list

  def get_query(self, query_id):
    return HiveQuery.objects.using('query').get(query_id=query_id)

  def get_query_analysis(self, query_id): pass

  # EXPLAIN with row count
  # CBO COST
  # VECTORIZATION?
