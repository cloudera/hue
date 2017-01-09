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

from liboozie.oozie_api import get_oozie
from notebook.connectors.oozie_batch import OozieApi

from jobbrowser.apis.base_api import Api
from oozie.views.dashboard import get_oozie_job_log


LOG = logging.getLogger(__name__)


try:
  from oozie.conf import OOZIE_JOBS_COUNT
  from oozie.views.dashboard import massaged_coordinator_actions_for_json
except Exception, e:
  LOG.exception('Some application are not enabled: %s' % e)


class ScheduleApi(Api):

  def apps(self):
    oozie_api = get_oozie(self.user)
    kwargs = {'cnt': OOZIE_JOBS_COUNT.get(), 'filters': []}
    wf_list = oozie_api.get_coordinators(**kwargs)

    return [{
        'id': app.id,
        'name': app.appName,
        'status': app.status,
        'type': 'coordinator',
        'user': app.user,
        'progress': 100,
        'duration': 10 * 3600,
        'submitted': 10 * 3600
    } for app in wf_list.jobs]

  def app(self, appid):
    oozie_api = get_oozie(self.user)
    coordinator = oozie_api.get_coordinator(jobid=appid)

    return {
        'id': coordinator.coordJobId,
        'name': coordinator.coordJobName,
        'status': coordinator.status,
        'actions': massaged_coordinator_actions_for_json(coordinator, None)
    }
