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
import sys

from datetime import datetime
from dateutil import parser

from desktop.models import Document2
from notebook.api import _get_statement
from notebook.models import Notebook

from jobbrowser.apis.base_api import Api
from jobbrowser.conf import MAX_JOB_FETCH

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


class HistoryApi(Api):

  def apps(self, filters):
    tasks = Document2.objects.get_history(user=self.user).order_by('-last_modified')[:MAX_JOB_FETCH.get()]
    apps = []

    for app in tasks:
      # Copied, Document class should have a get_history method (via method or inheritance)
      notebook = Notebook(document=app).get_data()
      is_notification_manager = False # Supposed SQL Editor query only right now
      if 'snippets' in notebook:
        statement = notebook['description'] if is_notification_manager else _get_statement(notebook)
        history = {
          'name': app.name,
          'id': app.id,
          'uuid': app.uuid,
          'type': app.type,
          'data': {
              'statement': statement[:1001] if statement else '',
              'lastExecuted': notebook['snippets'][0].get('lastExecuted', -1),
              'status':  notebook['snippets'][0]['status'],
              'parentSavedQueryUuid': notebook.get('parentSavedQueryUuid', '')
          } if notebook['snippets'] else {},
          'absoluteUrl': app.get_absolute_url(),
      }
      api_status = self._api_status(history)

      if filters.get('states') and api_status.lower() not in filters['states']:
        continue

      apps.append({
          'id': 'history-%010d' % history['id'],
          'name': history['data']['statement'],
          'status': history['data']['status'],
          'apiStatus': api_status,
          'type': 'history-%s' % history['type'],
          'user': self.user.username,
          'progress': 50,
          'queue': '',
          'canWrite': True,
          'duration': 1,
          'submitted': history['data']['lastExecuted']
        })

    return {
      'apps': apps,
      'total': len(tasks)
    }


  def app(self, appid):
    appid = appid.rsplit('-')[-1]

    app = Document2.objects.document(user=self.user, doc_id=appid)

    return {
      'id': 'history-%010d' % app.id,
      'name': app.name,
      'status': 'ready',
      'apiStatus': 'RUNNING',
      'type': 'history',
      'user': app.description,
      'progress': 50,
      'queue': '',
      'duration': 1,
      'canWrite': True,
      'submitted': 1,
      'properties': {
      }
    }


  def action(self, app_ids, operation):
    # Notebook API
    pass

  def logs(self, appid, app_type, log_name=None, is_embeddable=False):
    return {'logs': ''}


  def profile(self, appid, app_type, app_property, app_filters):
    appid = appid.rsplit('-')[-1]

    return {}


  def _api_status(self, task):
    if task['data']['status'] in ('expired', 'failed'):
      return 'FAILED'
    elif task['data']['status'] in ('available', 'canceled'):
      return 'SUCCEEDED'
    else:
      return 'RUNNING'
