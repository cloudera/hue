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


## Main views are inherited from Beeswax.


import logging
import json

from desktop.lib.django_util import JsonResponse
from desktop.context_processors import get_app_name

from beeswax.server import dbms
from beeswax.server.dbms import get_query_server_config


LOG = logging.getLogger(__name__)


def refresh_tables(request):
  app_name = get_app_name(request)
  query_server = get_query_server_config(app_name)
  db = dbms.get(request.user, query_server=query_server)

  response = {'status': 0, 'message': ''}

  if request.method == "POST":
    try:
      database = json.loads(request.POST['database'])
      added = json.loads(request.POST['added'])
      removed = json.loads(request.POST['removed'])

      db.invalidate_tables(database, added + removed)
    except Exception, e:
      response['message'] = str(e)

  return JsonResponse(response)
