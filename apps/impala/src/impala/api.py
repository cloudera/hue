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

from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from desktop.lib.django_util import JsonResponse

from beeswax.api import error_handler
from beeswax.models import Session
from beeswax.server import dbms as beeswax_dbms
from beeswax.views import authorized_get_query_history

from impala import dbms


LOG = logging.getLogger(__name__)


@require_POST
@error_handler
def invalidate(request):
  query_server = dbms.get_query_server_config()
  db = beeswax_dbms.get(request.user, query_server=query_server)

  response = {'status': 0, 'message': ''}

  database = request.POST.get('database', None)
  flush_all = request.POST.get('flush_all', 'false').lower() == 'true'

  db.invalidate(database=database, flush_all=flush_all)
  response['message'] = _('Successfully invalidated metadata')

  return JsonResponse(response)



@require_POST
@error_handler
def refresh_table(request, database, table):
  query_server = dbms.get_query_server_config()
  db = beeswax_dbms.get(request.user, query_server=query_server)

  response = {'status': 0, 'message': ''}

  db.refresh_table(database, table)
  response['message'] = _('Successfully refreshed metadata for `%s`.`%s`') % (database, table)

  return JsonResponse(response)


@require_POST
@error_handler
def get_exec_summary(request, query_history_id):
  query_server = dbms.get_query_server_config()
  db = beeswax_dbms.get(request.user, query_server=query_server)

  response = {'status': -1}
  query_history = authorized_get_query_history(request, query_history_id, must_exist=True)

  if query_history is None:
    response['message'] = _('get_exec_summary requires a valid query_history_id')
  else:
    session = Session.objects.get_session(request.user, query_server['server_name'])
    operation_handle = query_history.get_handle().get_rpc_handle()
    session_handle = session.get_handle()
    summary = db.get_exec_summary(operation_handle, session_handle)
    response['status'] = 0
    response['summary'] = summary

  return JsonResponse(response)


@require_POST
@error_handler
def get_runtime_profile(request, query_history_id):
  query_server = dbms.get_query_server_config()
  db = beeswax_dbms.get(request.user, query_server=query_server)

  response = {'status': -1}
  query_history = authorized_get_query_history(request, query_history_id, must_exist=True)

  if query_history is None:
    response['message'] = _('get_runtime_profile requires a valid query_history_id')
  else:
    session = Session.objects.get_session(request.user, query_server['server_name'])
    operation_handle = query_history.get_handle().get_rpc_handle()
    session_handle = session.get_handle()
    profile = db.get_runtime_profile(operation_handle, session_handle)
    response['status'] = 0
    response['profile'] = profile

  return JsonResponse(response)

