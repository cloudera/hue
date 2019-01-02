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

from notebook.connectors.altus import DataWarehouse2Api

from jobbrowser.apis.base_api import Api



LOG = logging.getLogger(__name__)


RUNNING_STATES = ('QUEUED', 'RUNNING', 'SUBMITTING')


class ClusterApi(Api):

  def __init__(self, user, version=1):
    super(ClusterApi, self).__init__(user)

    self.version = version
    self.api = DataWarehouse2Api(self.user) 


  def apps(self, filters):
    #jobs = self.api.list_clusters()

    return {
      u'status': 0,
      u'total': 3,
      u'apps': [
        {u'status': u'ONLINE', u'name': u'Internal EDH', u'submitted': u'2018-10-04 08:34:39.128886', u'queue': u'group', u'user': u'jo0', u'canWrite': False, u'duration': 0, u'progress': u'100 / 100', u'type': u'GKE 100 nodes 100CPU 20TB', u'id': u'crn:altus:engine:k8s:12a0079b-1591-4ca0-b721-a446bda74e67:cluster:jo0/cbf7bbb1-f956-45e4-a269-d239efbc9996', u'apiStatus': u'RUNNING'},
        {u'status': u'ONLINE', u'name': u'gke_gcp-eng-dsdw_us-west2-b_impala-demo', u'submitted': u'2018-10-04 08:34:39.128881', u'queue': u'group', u'user': u'r0', u'canWrite': False, u'duration': 0, u'progress': u'4 / 4', u'type': u'GKE 4 nodes 16CPU 64GB', u'id': u'crn:altus:engine:k8s:12a0079b-1591-4ca0-b721-a446bda74e67:cluster:r0/0da5e627-ee33-45c5-9179-cc6b95008d2e', u'apiStatus': u'RUNNING'},
        {u'status': u'ONLINE', u'name': u'DW-fraud', u'submitted': u'2018-10-04 08:34:39.128881', u'queue': u'group', u'user': u'r0', u'canWrite': False, u'duration': 0, u'progress': u'50 / 50', u'type': u'OpenShift 50 nodes 30CPU 2TB', u'id': u'crn:altus:engine:k8s:12a0079b-1591-4ca0-b721-a446bda74e67:cluster:r0/0da5e627-ee33-45c5-9179-cc6b95008d2e', u'apiStatus': u'RUNNING'},
      ]
    }

    return {
      'apps': [{
        'id': app['crn'],
        'name': '%(clusterName)s' % app,
        'status': app['status'],
        'apiStatus': self._api_status(app['status']),
        'type': 'Altus %(workersGroupSize)sX %(instanceType)s %(cdhVersion)s' % app,
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

    cluster['workerAutoResize'] = False

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


  def profile(self, appid, app_type, app_property):
    return {}

  def _api_status(self, status):
    if status in ['CREATING', 'CREATED', 'ONLINE', 'SCALING_UP', 'SCALING_DOWN', 'STARTING']: # ONLINE ... are from K8s
      return 'RUNNING'
    elif status in ['ARCHIVING', 'COMPLETED', 'TERMINATING', 'STOPPED']:
      return 'SUCCEEDED'
    else:
      return 'FAILED' # KILLED and FAILED
