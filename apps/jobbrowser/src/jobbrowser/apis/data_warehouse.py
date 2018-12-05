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

from datetime import datetime
from dateutil import parser

from django.utils import timezone
from django.utils.translation import ugettext as _

from notebook.connectors.altus import AnalyticDbApi, DataWarehouse2Api

from jobbrowser.apis.base_api import Api



LOG = logging.getLogger(__name__)


RUNNING_STATES = ('QUEUED', 'RUNNING', 'SUBMITTING')


class DataWarehouseClusterApi(Api):

  def __init__(self, user, version=1):
    super(DataWarehouseClusterApi, self).__init__(user)

    self.version = version
    self.api = DataWarehouse2Api(self.user) if version == 2 else AnalyticDbApi(self.user) 


  def apps(self, filters):
    jobs = self.api.list_clusters()

    return {
      'apps': [{
        'id': app['crn'],
        'name': '%(clusterName)s' % app,
        'status': app['status'],
        'apiStatus': self._api_status(app['status']),
        'type': '%(instanceType)s' % app, #'Altus %(workersGroupSize)sX %(instanceType)s %(cdhVersion)s' % app,
        'user': app['clusterName'].split('-', 1)[0],
        'progress': app.get('progress', 100),
        'queue': 'group',
        'duration': ((datetime.now() - parser.parse(app['creationDate']).replace(tzinfo=None)).seconds * 1000) if app['creationDate'] else 0,
        'submitted': app['creationDate'],
        'canWrite': True
      } for app in sorted(jobs['clusters'], key=lambda a: a['creationDate'], reverse=True)],
      'total': len(jobs['clusters'])
    }


  def app(self, appid):
    handle = self.api.describe_cluster(cluster_id=appid)

    cluster = handle['cluster']

    common = {
        'id': cluster['crn'],
        'name': cluster['clusterName'],
        'status': cluster['status'],
        'apiStatus': self._api_status(cluster['status']),
        'progress': 50 if self._api_status(cluster['status']) == 'RUNNING' else 100,
        'duration': 10 * 3600,
        'submitted': cluster['creationDate'],
        'type': 'dataware2-cluster' if self.version == 2 else 'dataware-cluster',
        'canWrite': True
    }

    common['properties'] = {
      'properties': cluster
    }

    return common

  def action(self, appid, action):
    message = {'message': '', 'status': 0}

    if action.get('action') == 'kill':
      for _id in appid:
        result = self.api.delete_cluster(_id)
        if result.get('error'):
          message['message'] = result.get('error')
          message['status'] = -1
        elif result.get('contents') and message.get('status') != -1:
          message['message'] = result.get('contents')

    return message;


  def logs(self, appid, app_type, log_name=None, is_embeddable=False):
    return {'logs': ''}


  def profile(self, app_id, app_type, app_property, app_filters):
    return {}

  def _api_status(self, status):
    if status in ['CREATING', 'CREATED', 'ONLINE', 'SCALING_UP', 'SCALING_DOWN', 'STARTING']:
      return 'RUNNING'
    elif status == 'STOPPED':
      return 'PAUSED'
    elif status in ['ARCHIVING', 'COMPLETED', 'TERMINATING', 'TERMINATED']:
      return 'SUCCEEDED'
    else:
      return 'FAILED' # KILLED and FAILED
