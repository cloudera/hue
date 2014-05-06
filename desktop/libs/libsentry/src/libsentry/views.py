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

import json

from django.http import HttpResponse

from libsentry import conf
from libsentry.client import SentryClient


def roles(request):
  response = {
    'code': -1
  }

  try:
    client = SentryClient(conf.HOSTNAME.get(), conf.PORT.get(), request.user)
    response['roles'] = client.roles()
    response['code'] = 0
  except Exception, e:
    response['code'] = 1
    response['error'] = e.message

  return HttpResponse(json.dumps(response), mimetype="application/json", status=200)
