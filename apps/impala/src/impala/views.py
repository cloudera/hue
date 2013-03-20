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
from desktop.lib.exceptions_renderable import PopupException

from impala import server


def refresh_catalog(request):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  try:
    db = server.get(request.user)
    res = db.resetCatalog()
    response = {'status': res.status_code, 'data': res.error_msgs}
  except Exception, e:
    response = {'status': -1, 'data': str(e)}

  return HttpResponse(json.dumps(response), mimetype="application/json")
