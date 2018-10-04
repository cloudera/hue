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
import json

from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import force_unicode

from metadata.workload_analytics_client import WorkfloadAnalyticsClient


LOG = logging.getLogger(__name__)


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    try:
      return view_fn(*args, **kwargs)
    except Exception, e:
      LOG.exception(e)
      response = {
        'status': -1,
        'message': force_unicode(e)
      }
    return JsonResponse(response, status=500)
  return decorator


@require_POST
@error_handler
def get_impala_query(request):
  response = {'status': -1}

  cluster = json.loads(request.POST.get('cluster'))
  query_id = json.loads(request.POST.get('query_id'))

  client = WorkfloadAnalyticsClient(request.user)
  data = client.get_impala_query(cluster=cluster, query_id=query_id)

  if data:
    response['status'] = 0
    response['data'] = data
  else:
    response['message'] = 'Workload Analytics: %s' % data['details']

  return JsonResponse(response)


@require_POST
@error_handler
def get_cluster_id(request):
  response = {'status': -1}

  crn = json.loads(request.POST.get('crn'))

  client = WorkfloadAnalyticsClient(request.user)
  data = client.list_uploads()

  if data:
    env = [_env for _env in data['environments'] if _env['crn'] == crn]
    if not env:
      response['message'] = 'Workload Analytics: %s environment not found' % crn
    else:
      response['status'] = 0
      response['data'] = env[0]
  else:
    response['message'] = 'Workload Analytics: %s' % data['details']

  return JsonResponse(response)


@require_POST
@error_handler
def get_environment(request):
  response = {'status': -1}

  crn = json.loads(request.POST.get('crn'))

  client = WorkfloadAnalyticsClient(request.user)
  data = client.list_environments()

  if data:
    env = [_env for _env in data['environments'] if _env['crn'] == crn]
    if not env:
      response['message'] = 'Workload Analytics: %s environment not found' % crn
    else:
      response['status'] = 0
      response['data'] = env[0]
  else:
    response['message'] = 'Workload Analytics: %s' % data['details']

  return JsonResponse(response)


@require_POST
@error_handler
def get_operation_execution_details(request):
  response = {'status': -1}

  operation_id = json.loads(request.POST.get('operation_id'))

  client = WorkfloadAnalyticsClient(request.user)
  data = client.get_operation_execution_details(operation_id=operation_id)

  if data:
    response['status'] = 0
    response['data'] = data
  else:
    response['message'] = 'Workload Analytics: %s' % data['details']

  return JsonResponse(response)
