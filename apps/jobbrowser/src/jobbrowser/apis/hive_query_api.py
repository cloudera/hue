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
import sys

from datetime import datetime

from beeswax.models import QueryHistory
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.python_util import current_ms_from_utc
from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource
from notebook.models import _get_notebook_api, make_notebook, MockRequest

from jobbrowser.apis.base_api import Api

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)

class HiveQueryApi(Api):
  HEADERS = {'X-Requested-By': 'das'}

  def __init__(self, user, cluster=None):
    self.user = user
    self.cluster = cluster

  def apps(self, filters):
    # Removed Hive Querybrowser skeleton implementation, check git history if needed to add it back.
    pass

  def app(self, appid):
    # Removed Hive Querybrowser skeleton implementation, check git history if needed to add it back.
    pass

  def action(self, query_ids, action):
    message = {'actions': {}, 'status': 0}

    if action.get('action') == 'kill':
      for query_id in query_ids:
        action_details = {}

        try:
          self.kill_query(query_id)
          action_details['status'] = 0
          action_details['message'] = _('kill action performed')
        except Exception as ex:
          LOG.error(ex)
          message['status'] = -1
          action_details['status'] = -1
          action_details['message'] = _('kill action failed : %s' % str(ex))

        message['actions'][query_id] = action_details

    return message

  def kill_query(self, query_id):
    kill_sql = 'KILL QUERY "%s";' % query_id
    job = make_notebook(
        name=_('Kill query %s') % query_id,
        editor_type='hive',
        statement=kill_sql,
        status='ready',
        on_success_url='assist.db.refresh',
        is_task=False,
    )

    job.execute_and_wait(MockRequest(user=self.user))

  def logs(self, appid, app_type, log_name=None, is_embeddable=False):
    return {'logs': ''}

  def profile(self, appid, app_type, app_property, app_filters):
    message = {'message': '', 'status': 0}

    return message

  def _api_status(self, status):
    if status == 'SUCCESS':
      return 'SUCCEEDED'
    elif status == 'EXCEPTION':
      return 'FAILED'
    elif status == 'RUNNING':
      return 'RUNNING'
    else:
      return 'PAUSED'
