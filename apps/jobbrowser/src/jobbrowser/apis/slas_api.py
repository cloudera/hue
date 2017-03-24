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

from liboozie.oozie_api import get_oozie

from jobbrowser.apis.base_api import Api


LOG = logging.getLogger(__name__)


try:
  from oozie.views.dashboard import massaged_sla_for_json
except Exception, e:
  LOG.exception('Some application are not enabled: %s' % e)


class SlaApi(Api):

  def apps(self, filters):
    oozie_api = get_oozie(self.user,  api_version="v2")

    params = {}

    job_name = filters.POST.get('job_name')
 
    if re.match('.*-oozie-oozi-[WCB]', job_name):
      params['id'] = job_name
      params['parent_id'] = job_name
    else:
      params['app_name'] = job_name
 
#     if 'useDates' in request.POST:
#       if request.POST.get('start'):
#         params['nominal_start'] = request.POST.get('start')
#       if request.POST.get('end'):
#         params['nominal_end'] = request.POST.get('end')

    oozie_slas = oozie_api.get_oozie_slas(**params)



    massaged_slas = []
    for sla in oozie_slas:
      massaged_slas.append(massaged_sla_for_json(sla, request))

    return massaged_slas

#   configuration = oozie_api.get_configuration()
#   show_slas_hint = 'org.apache.oozie.sla.service.SLAService' not in configuration.get('oozie.services.ext', '')

    return [{
        'id': app.id,
        'name': app.appName,
        'status': app.status,
        'type': 'bundle',
        'user': app.user,
        'progress': 100,
        'duration': 10 * 3600,
        'submitted': 10 * 3600
    } for app in wf_list.jobs]

  def app(self, appid):
    oozie_api = get_oozie(self.user)
    bundle = oozie_api.get_bundle(jobid=appid)

    return {
        'id': bundle.bundleJobId,
        'name': bundle.bundleJobName,
        'status': bundle.status,
    }
