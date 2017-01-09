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
  from jobbrowser.apis.batch_api import BatchApi
  from jobbrowser.apis.job_api import YarnApi
  from jobbrowser.apis.schedule_api import ScheduleApi

  if interface == 'batches':
    return BatchApi(user)
  elif interface == 'schedules':
    return ScheduleApi(user)
  elif interface == 'apps':
    return YarnApi(user)
  else:
    raise PopupException(_('Interface %s is unknown') % interface)


class Api():

  def __init__(self, user):
    self.user = user

  def apps(self): return []

  def app(self, appid): return {}

  def kill(self): return {}

  def progress(self): return {'progress': 0}

  def tasks(self): return []

  def logs(self): return {'stderr': '', 'stdout': ''}

  def profile(self): return {}
