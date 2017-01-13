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

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)


def get_api(user, interface):
  from jobbrowser.apis.bundle_api import BundleApi
  from jobbrowser.apis.job_api import JobApi
  from jobbrowser.apis.schedule_api import ScheduleApi
  from jobbrowser.apis.workflow_api import WorkflowApi

  if interface == 'apps':
    return JobApi(user)
  elif interface == 'workflows':
    return WorkflowApi(user)
  elif interface == 'schedules':
    return ScheduleApi(user)
  elif interface == 'bundles':
    return BundleApi(user)
  else:
    raise PopupException(_('Interface %s is unknown') % interface)


class Api(object):

  def __init__(self, user):
    self.user = user
    self.request = None

  def apps(self): return []

  def app(self, appid): return {}

  def action(self, appid, operation): return {}

  def status(self, appid): return {'status': 'RUNNING'}

  def logs(self, appid, app_type): return {'progress': 0, 'logs': {'default': ''}}

  def profile(self, appid, app_type, app_property): return {} # Tasks, XML, counters...

  def _set_request(self, request):
    self.request = request


class MockDjangoRequest():

  def __init__(self, user, get=None, post=None):
    self.user = user
    self.jt = None
    self.GET = get if get is not None else {'format': 'json'}
    self.POST = post if post is not None else {}
    self.method = "POST"
