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

from django.http import Http404

from desktop.lib.django_util import JsonResponse
from librdbms import conf as librdbms_conf
from librdbms.server import dbms


def get_query_server_config_from_request(request):
  check_params = {
    'server_name': request.GET.get('server_type')
  }
  if 'host' in request.GET:
    check_params['server_host'] = request.GET.get('host')
  if 'port' in request.GET:
    check_params['server_port'] = request.GET.get('port')
  if 'username' in request.GET:
    check_params['username'] = request.GET.get('username')

  for alias in librdbms_conf.DATABASES:
    config = dbms.get_query_server_config(alias)
    if all([check_params[param] == config[param] for param in check_params]):
      return config

  return None


def autocomplete(request, database=None, table=None):
  response = {
    'status': 0,
    'errors': []
  }

  if 'server_type' not in request.GET:
    raise Http404()

  query_server = get_query_server_config_from_request(request)
  if database:
    query_server['name'] = database

  if not query_server:
    raise Http404()

  db = dbms.get(request.user, query_server)

  if database:
    response['databases'] = [database]
    if table:
      response['tables'] = [table]
      response['columns'] = db.get_columns(database, table)
    else:
      response['tables'] = db.get_tables(database)
  else:
    response['databases'] = db.get_databases()

  return JsonResponse(response)
