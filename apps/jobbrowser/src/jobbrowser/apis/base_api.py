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

from builtins import object
import logging
import posixpath
import re
import sys

from hadoop.fs.hadoopfs import Hdfs
from desktop.lib.exceptions_renderable import PopupException

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _

LOG = logging.getLogger(__name__)


def get_api(user, interface, cluster=None):

  if interface == 'jobs':
    from jobbrowser.apis.job_api import JobApi
    return JobApi(user)
  elif interface == 'queries-impala':
    from jobbrowser.apis.query_api import QueryApi
    return QueryApi(user, cluster=cluster)
  elif interface == 'queries-hive':
    from jobbrowser.apis.hive_query_api import HiveQueryApi
    return HiveQueryApi(user, cluster=cluster)
  elif interface == 'workflows':
    from jobbrowser.apis.workflow_api import WorkflowApi
    return WorkflowApi(user)
  elif interface == 'schedules':
    from jobbrowser.apis.schedule_api import ScheduleApi
    return ScheduleApi(user)
  elif interface == 'bundles':
    from jobbrowser.apis.bundle_api import BundleApi
    return BundleApi(user)
  elif interface == 'celery-beat':
    from jobbrowser.apis.beat_api import BeatApi
    return BeatApi(user)
  elif interface == 'schedule-hive':
    from jobbrowser.apis.schedule_hive import HiveScheduleApi
    return HiveScheduleApi(user)
  elif interface == 'history':
    from jobbrowser.apis.history import HistoryApi
    return HistoryApi(user)
  elif interface == 'engines':
    from jobbrowser.apis.clusters import ClusterApi
    return ClusterApi(user)
  elif interface == 'dataeng-clusters':
    from jobbrowser.apis.data_eng_api import DataEngClusterApi
    return DataEngClusterApi(user)
  elif interface == 'dataware-clusters':
    from jobbrowser.apis.data_warehouse import DataWarehouseClusterApi
    return DataWarehouseClusterApi(user)
  elif interface == 'dataware2-clusters':
    from jobbrowser.apis.data_warehouse import DataWarehouseClusterApi
    return DataWarehouseClusterApi(user, version=2)
  elif interface == 'dataeng-jobs':
    from jobbrowser.apis.data_eng_api import DataEngJobApi
    return DataEngJobApi(user)
  elif interface == 'livy-sessions':
    from jobbrowser.apis.livy_api import LivySessionsApi
    return LivySessionsApi(user)
  elif interface == 'livy-job':
    from jobbrowser.apis.livy_api import LivyJobApi
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


class MockDjangoRequest(object):

  def __init__(self, user, get=None, post=None, method='POST'):
    self.user = user
    self.jt = None
    self.GET = get if get is not None else {'format': 'json'}
    self.POST = post if post is not None else {}
    self.REQUEST = {}
    self.method = method


def _extract_query_params(filters):
  filter_params = {}

  for name, value in filters.items():
    if name == 'text':
      filter_params['text'] = value

      user_filter = re.search('((user):([^ ]+))', filter_params['text'])
      if user_filter:
        filter_params['username'] = user_filter.group(3)
        filter_params['text'] = filter_params['text'].replace(user_filter.group(1), '').strip()

      id_filter = re.search('((id):([^ ]+))', filter_params['text'])
      if id_filter:
        filter_params['id'] = id_filter.group(3)
        filter_params['text'] = filter_params['text'].replace(id_filter.group(1), '').strip()

      name_filter = re.search('((name):([^ ]+))', filter_params['text'])
      if name_filter:
        filter_params['name'] = name_filter.group(3)
        filter_params['text'] = filter_params['text'].replace(name_filter.group(1), '').strip()
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
