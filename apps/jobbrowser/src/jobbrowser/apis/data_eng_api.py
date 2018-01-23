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

from datetime import datetime,  timedelta

from django.utils.translation import ugettext as _

from desktop.models import Cluster, DATAENG
from notebook.connectors.dataeng import DataEng, DATE_FORMAT

from jobbrowser.apis.base_api import Api


LOG = logging.getLogger(__name__)


class DataEngClusterApi(Api):

  def apps(self, filters):
    api = DataEng(self.user)

    jobs = api.list_clusters()

    return {
      'apps': [{
        'id': app['crn'],
        'name': '%(clusterName)s' % app,
        'status': app['status'],
        'apiStatus': self._api_status(app['status']),
        'type': '%(serviceType)s %(workersGroupSize)s %(instanceType)s %(cdhVersion)s' % app,
        'user': app['clusterName'].split('-', 1)[0],
        'progress': 100,
        'queue': 'group',
        'duration': 1,
        'submitted': app['creationDate']
      } for app in jobs['clusters']],
      'total': len(jobs)
    }


  def app(self, appid):
    return {}


  def action(self, appid, action):
    return {}


  def logs(self, appid, app_type, log_name=None, is_embeddable=False):
    return {'logs': ''}


  def profile(self, appid, app_type, app_property):
    return {}

  def _api_status(self, status):
    if status in ['CREATING', 'CREATED', 'TERMINATING']:
      return 'RUNNING'
    elif status in ['ARCHIVING', 'COMPLETED']:
      return 'SUCCEEDED'
    else:
      return 'FAILED' # KILLED and FAILED


class DataEngJobApi(Api):

  def apps(self, filters):
    kwargs = {}

    if 'time' in filters:
      if filters['time']['time_unit'] == 'minutes':
        delta = timedelta(minutes=int(filters['time']['time_value']))
      elif filters['time']['time_unit'] == 'hours':
        delta = timedelta(hours=int(filters['time']['time_value']))
      else:
        delta = timedelta(days=int(filters['time']['time_value']))
      kwargs['creation_date_after'] = (datetime.today() - delta).strftime(DATE_FORMAT)

    # Could also come from filters
    cluster = Cluster(self.user)
    if cluster.get_type() == DATAENG:
      kwargs['cluster_crn'] = cluster.get_id()

    api = DataEng(self.user)

    jobs = api.list_jobs(**kwargs)

    return {
      'apps': [{
        'id': app['jobId'],
        'name': app['creationDate'],
        'status': app['status'],
        'apiStatus': self._api_status(app['status']),
        'type': app['jobType'],
        'user': '',
        'progress': 100,
        'duration': 10 * 3600,
        'submitted': app['creationDate']
      } for app in jobs['jobs']],
      'total': len(jobs)
    }

  def app(self, appid):
    handle = DataEng(self.user).describe_job(job_id=appid)

    job = handle['job']

    common = {
        'id': job['jobId'],
        'name': job['jobId'],
        'status': job['status'],
        'apiStatus': self._api_status(job['status']),
        'progress': 50,
        'duration': 10 * 3600,
        'submitted': job['creationDate'],
        'type': 'dataeng-job-%s' % job['jobType'],
    }

    common['properties'] = {
      'properties': job
    }

    return common


  def action(self, appid, action):
    return {}


  def logs(self, appid, app_type, log_name=None, is_embeddable=False):
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
