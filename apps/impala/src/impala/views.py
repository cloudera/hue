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

## All the other views are inherited from Beeswax currently.

try:
  import json
except ImportError:
  import simplejson as json

from django.http import HttpResponse
from django.utils.translation import ugettext as _
from beeswax.views import install_examples as beeswax_install_examples
from impala import server


def refresh_catalog(request):
  response = {'status': -1, 'message': ''}

  if request.method != 'POST':
    response['message'] = _('A POST request is required.')
  else:
    try:
      db = server.get(request.user)
      res = db.resetCatalog()
      if res.status_code is None:
        status = 0
      else:
        status = res.status_code
      response = {'status': status, 'message': res.error_msgs}
    except Exception, e:
      response = {'message': str(e)}

  return HttpResponse(json.dumps(response), mimetype="application/json")


def install_examples(request):
  return beeswax_install_examples(request)
