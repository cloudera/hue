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
import logging

from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import force_unicode
from desktop.models import Document2
from notebook.models import Notebook

from metadata.optimizer_client import OptimizerApi


LOG = logging.getLogger(__name__)


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    try:
      return view_fn(*args, **kwargs)
    except Http404, e:
      raise e
    except Exception, e:
      LOG.exception(e)
      response = {
        'status': -1,
        'message': force_unicode(str(e))
      }
    return JsonResponse(response, status=500)
  return decorator


@require_POST
@error_handler
def get_tenant(request):
  response = {'status': -1}

  email = request.POST.get('email')

  api = OptimizerApi()
  data = api.get_tenant(email=email)

  if data['status'] == 'success':
    response['status'] = 0
    response['data'] = data['tenant']
  else:
    response['message'] = 'Optimizer: %s' % data['details']

  return JsonResponse(response)


@require_POST
@error_handler
def top_tables(request):
  response = {'status': -1}

  database = request.POST.get('database', 'default')
  len = request.POST.get('len', 1000)

  api = OptimizerApi()
  data = api.top_tables(database_name=database)

  tables = [{
      'eid': table['eid'],
      'database': _get_table_name(table['name'])['database'],
      'name': _get_table_name(table['name'])['table'],
      'popularity': table['workloadPercent'],
      'column_count': table['columnCount'],
      'patternCount': table['patternCount'],
      'total': table['total'],
      'is_fact': table['type'] != 'Dimension'
      } for table in data['results']
  ]

  response['top_tables'] = tables
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@error_handler
def table_details(request):
  response = {'status': -1}

  database_name = request.POST.get('databaseName')
  table_name = request.POST.get('tableName')

  api = OptimizerApi()

  data = api.table_details(database_name=database_name, table_name=table_name)

  if data['status'] == 'success':
    response['status'] = 0
    response['details'] = data
  else:
    response['message'] = 'Optimizer: %s' % data['details']

  return JsonResponse(response)


@require_POST
@error_handler
def query_compatibility(request):
  response = {'status': -1}

  source_platform = request.POST.get('sourcePlatform')
  target_platform = request.POST.get('targetPlatform')
  query = request.POST.get('query')

  api = OptimizerApi()

  data = api.query_compatibility(source_platform=source_platform, target_platform=target_platform, query=query)

  if data['status'] == 'success':
    response['status'] = 0
    response['query_compatibility'] = data
  else:
    response['message'] = 'Optimizer: %s' % data

  return JsonResponse(response)


@require_POST
@error_handler
def query_risk(request):
  response = {'status': -1}

  query = json.loads(request.POST.get('query'))

  api = OptimizerApi()

  data = api.query_risk(query=query)

  if data['status'] == 'success':
    response['status'] = 0
    response['query_risk'] = data
  else:
    response['message'] = 'Optimizer: %s' % data

  return JsonResponse(response)


@require_POST
@error_handler
def similar_queries(request):
  response = {'status': -1}

  source_platform = request.POST.get('sourcePlatform')
  query = json.loads(request.POST.get('query'))

  api = OptimizerApi()

  data = api.similar_queries(source_platform=source_platform, query=query)

  if data['status'] == 'success':
    response['status'] = 0
    response['similar_queries'] = data
  else:
    response['message'] = 'Optimizer: %s' % data

  return JsonResponse(response)


@require_POST
@error_handler
def top_filters(request):
  response = {'status': -1}

  db_tables = json.loads(request.POST.get('dbTables'), '[]')
  column_name = request.POST.get('columnName') # Unsused

  api = OptimizerApi()
  data = api.top_filters(db_tables=db_tables)

  if data['status'] == 'success':
    response['status'] = 0
    response['values'] = data['results']
  else:
    response['message'] = 'Optimizer: %s' % data

  return JsonResponse(response)


@require_POST
@error_handler
def top_joins(request):
  response = {'status': -1}

  db_tables = json.loads(request.POST.get('dbTables'), '[]')

  api = OptimizerApi()
  data = api.top_joins(db_tables=db_tables)

  if data['status'] == 'success':
    response['status'] = 0
    response['values'] = data['results']
  else:
    response['message'] = 'Optimizer: %s' % data

  return JsonResponse(response)


@require_POST
@error_handler
def top_aggs(request):
  response = {'status': -1}

  db_tables = json.loads(request.POST.get('dbTables'), '[]')

  api = OptimizerApi()
  data = api.top_aggs(db_tables=db_tables)

  if data['status'] == 'success':
    response['status'] = 0
    response['values'] = data['results']
  else:
    response['message'] = 'Optimizer: %s' % data

  return JsonResponse(response)


@require_POST
@error_handler
def top_databases(request):
  response = {'status': -1}

  api = OptimizerApi()
  data = api.top_databases()

  if data['status'] == 'success':
    response['status'] = 0
    response['values'] = data['results']
  else:
    response['message'] = 'Optimizer: %s' % data

  return JsonResponse(response)


@require_POST
@error_handler
def top_columns(request):
  response = {'status': -1}

  db_tables = json.loads(request.POST.get('dbTables'), '[]')

  api = OptimizerApi()
  data = api.top_columns(db_tables=db_tables)

  if data['status'] == 'success':
    response['status'] = 0
    response['values'] = data
  else:
    response['message'] = 'Optimizer: %s' % data

  return JsonResponse(response)


@require_POST
@error_handler
def upload_history(request):
  response = {'status': -1}

  query_type = 'hive'

  queries = [
      (doc.uuid, 1000, Notebook(document=doc).get_data()['snippets'][0]['statement'])
      for doc in Document2.objects.get_history(doc_type='query-%s' % query_type, user=request.user)[:10]
  ]

  api = OptimizerApi()

  response['upload_history'] = api.upload(queries=queries, source_platform=query_type)
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@error_handler
def upload_status(request):
  response = {'status': -1}

  workload_id = request.POST.get('workloadId')

  api = OptimizerApi()

  response['upload_status'] = api.upload_status(workload_id=workload_id)
  response['status'] = 0

  return JsonResponse(response)


def _get_table_name(path):
  if '.' in path:
    database, table = path.split('.', 1)
  else:
    database, table = '', path

  return {'database': database, 'table': table}
