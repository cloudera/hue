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
import posixpath
import re

from django.utils.translation import ugettext as _

from hadoop.fs.hadoopfs import Hdfs
from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)


def get_api(user, interface, cluster=None):
  from jobbrowser.apis.bundle_api import BundleApi
  from jobbrowser.apis.data_eng_api import DataEngClusterApi, DataEngJobApi
  from jobbrowser.apis.clusters import ClusterApi
  from jobbrowser.apis.data_warehouse import DataWarehouseClusterApi
  from jobbrowser.apis.livy_api import LivySessionsApi, LivyJobApi
  from jobbrowser.apis.job_api import JobApi
  from jobbrowser.apis.query_api import QueryApi
  from jobbrowser.apis.schedule_api import ScheduleApi
  from jobbrowser.apis.workflow_api import WorkflowApi

  if interface == 'jobs':
    return JobApi(user)
  elif interface == 'queries':
    return QueryApi(user, cluster=cluster)
  elif interface == 'workflows':
    return WorkflowApi(user)
  elif interface == 'schedules':
    return ScheduleApi(user)
  elif interface == 'bundles':
    return BundleApi(user)
  elif interface == 'engines':
    return ClusterApi(user)
  elif interface == 'dataeng-clusters':
    return DataEngClusterApi(user)
  elif interface == 'dataware-clusters':
    return DataWarehouseClusterApi(user)
  elif interface == 'dataware2-clusters':
    return DataWarehouseClusterApi(user, version=2)
  elif interface == 'dataeng-jobs':
    return DataEngJobApi(user)
  elif interface == 'livy-sessions':
    return LivySessionsApi(user)
  elif interface == 'livy-job':
    return LivyJobApi(user)
  elif interface == 'slas':
    return Api(user)
  else:
    raise PopupException(_('Interface %s is unknown') % interface)


class Api(object):

  def __init__(self, user):
    self.user = user
    self.request = None

  def apps(self, filters): return {'apps': [], 'total': 0}

  def app(self, appid): return {} # Also contains progress (0-100) and status [RUNNING, SUCCEEDED, PAUSED, FAILED]

  def action(self, app_ids, operation): return {}

  def logs(self, appid, app_type, log_name, is_embeddable=False): return {'progress': 0, 'logs': ''}

  def profile(self, appid, app_type, app_property, app_filters): return {} # Tasks, XML, counters...

  def _set_request(self, request):
    self.request = request


class MockDjangoRequest():

  def __init__(self, user, get=None, post=None, method='POST'):
    self.user = user
    self.jt = None
    self.GET = get if get is not None else {'format': 'json'}
    self.POST = post if post is not None else {}
    self.REQUEST = {}
    self.method = method


def _extract_query_params(filters):
  filter_params = {}

  for name, value in filters.iteritems():
    if name == 'text':
      filter_params['text'] = value
      user_filter = re.search('((user):([^ ]+))', value)
      if user_filter:
        filter_params['username'] = user_filter.group(3)
        filter_params['text'] = filter_params['text'].replace(user_filter.group(1), '').strip()
    else:
      filter_params[name] = value

  return filter_params


def is_linkable(name, path):
  return re.search('(dir|path|output|input)', name, re.I) or path.startswith('/') or path.startswith('hdfs://')


def hdfs_link_js(url):
  link = 'javascript:void(0)'

  if url:
    path = Hdfs.urlsplit(url)[2]
    if path:
      link = ('/filebrowser/view=%s' if path.startswith(posixpath.sep) else '/filebrowser/home_relative_view=/%s') % path

  return link
