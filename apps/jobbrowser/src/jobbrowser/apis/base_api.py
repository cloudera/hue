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
import re

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)


def get_api(user, interface):
  from jobbrowser.apis.bundle_api import BundleApi
  from jobbrowser.apis.job_api import JobApi
  from jobbrowser.apis.schedule_api import ScheduleApi
  from jobbrowser.apis.slas_api import SlaApi
  from jobbrowser.apis.workflow_api import WorkflowApi

  if interface == 'jobs':
    return JobApi(user)
  elif interface == 'workflows':
    return WorkflowApi(user)
  elif interface == 'schedules':
    return ScheduleApi(user)
  elif interface == 'bundles':
    return BundleApi(user)
  elif interface == 'slas':
    return SlaApi(user)
  else:
    raise PopupException(_('Interface %s is unknown') % interface)


class Api(object):

  def __init__(self, user):
    self.user = user
    self.request = None

  def apps(self, filters): return []

  def app(self, appid): return {} # Also contains progress (0-100) and status [RUNNING, FINISHED, PAUSED]

  def action(self, appid, operation): return {}

  def logs(self, appid, app_type, log_name): return {'progress': 0, 'logs': ''}

  def profile(self, appid, app_type, app_property): return {} # Tasks, XML, counters...

  def _set_request(self, request):
    self.request = request


class MockDjangoRequest():

  def __init__(self, user, get=None, post=None):
    self.user = user
    self.jt = None
    self.GET = get if get is not None else {'format': 'json'}
    self.POST = post if post is not None else {}
    self.REQUEST = {}
    self.method = "POST"


def _extract_query_params(filters):
  filter_params = {}

  for name, value in filters.iteritems():
    if name == 'text':
      filter_params['text'] = value
      user_filter = re.search('((user):([^ ]+))', value)
      if user_filter:
        filter_params['username'] = user_filter.group(3)
        filter_params['text'] = filter_params['text'].replace(user_filter.group(1), '').strip()

  return filter_params
