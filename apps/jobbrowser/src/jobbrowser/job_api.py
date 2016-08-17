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
from jobbrowser.api import YarnApi as NativeYarnApi


LOG = logging.getLogger(__name__)



def get_api(user):
  pass



class Api():

  def __init__(self, user):
    self.user = user

  def apps(self): return []

  def app(self): return {}

  def kill(self): return {}

  def progress(self): return {'progress': 0}

  def tasks(self): return []

  def logs(self): return {'stderr': '', 'stdout': ''}

  def profile(self): return {}


# Job

class YarnApi(Api):

  def apps(self):
    jobs = NativeYarnApi(self.user).get_jobs(self.user, username=self.user.username, state='all', text='')
    return [{'id': app.jobId, 'status': app.status} for app in jobs]


class MapReduce2Api(Api):
  pass

class MapReduceHistoryServerApi(Api):
  pass


class SparkApi(Api):
  pass

class SparkHistoryServerApi(Api):
  pass


class ImpalaApi(Api):
  pass


# Batch

class BatchApi(Api):
  pass

# Schedule

class ScheduleApi(Api):
  pass


# History

class HueHistoryApi(Api):

  def apps(self): return []

