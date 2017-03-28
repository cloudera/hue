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

import base64
import json
import logging
import struct

from django.http import Http404
from django.views.decorators.http import require_POST

from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import force_unicode
from desktop.models import Document2
from libsentry.privilege_checker import PrivilegeChecker
from notebook.models import Notebook

from metadata.conf import NAVIGATOR
from metadata.optimizer_client import OptimizerApi

LOG = logging.getLogger(__name__)


try:
  from beeswax.api import get_table_stats
  from beeswax.design import hql_query
  from beeswax.server import dbms
except ImportError, e:
  LOG.warn("Hive lib not enabled")


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

  if data:
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

  if NAVIGATOR.APPLY_SENTRY_PERMISSIONS.get():
    checker = PrivilegeChecker(user=request.user)
    action = 'SELECT'

    for table in tables:
      paths = _get_table_name(table['name'])
      table.update({u'db': paths['database'], u'table': paths['table'], u'column': None, u'server': u'server1'})
    tables = list(checker.filter_objects(tables, action)) #, getkey=getkey)

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

  if data:
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

  if data:
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

  if data:
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

  if data:
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

  if data:
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

  if data:
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

  if data:
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

  if data:
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

  if data:
    response['status'] = 0
    response['values'] = data
  else:
    response['message'] = 'Optimizer: %s' % data

  return JsonResponse(response)


@require_POST
@error_handler
def upload_history(request):
  response = {'status': -1}

  n = request.POST.get('n')
  source_platform = request.POST.get('sourcePlatform', 'hive')

  history = Document2.objects.get_history(doc_type='query-%s' % source_platform, user=request.user)
  if n:
    history = history[:n]

  queries = []
  for doc in history:
    query_data = Notebook(document=doc).get_data()

    try:
      original_query_id = '%s:%s' % struct.unpack(b"QQ", base64.decodestring(query_data['snippets'][0]['result']['handle']['guid']))
      execution_time = query_data['snippets'][0]['result']['executionTime'] * 100

      queries.append((original_query_id, execution_time, query_data['snippets'][0]['statement'], query_data['snippets'][0].get('database', 'default')))
    except Exception, e:
      LOG.warning('Skipping upload of %s: %s' % (doc, e))

  api = OptimizerApi()

  response['upload_history'] = api.upload(data=queries, data_type='queries', source_platform=source_platform)
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@error_handler
def upload_table_stats(request):
  response = {'status': -1}

  db_tables = json.loads(request.POST.get('db_tables'), '[]')
  source_platform = request.POST.get('sourcePlatform', 'hive')
  with_columns = json.loads(request.POST.get('with_columns', 'false'))
  with_ddl = json.loads(request.POST.get('with_ddl', 'false'))

  table_stats = []
  column_stats = []
  table_ddls = []

  for db_table in db_tables:
    path = _get_table_name(db_table['name'])

    try:
      if with_ddl:
        db = dbms.get(request.user)
        query = hql_query('SHOW CREATE TABLE `%(database)s`.`%(table)s`' % path)
        handle = db.execute_and_wait(query, timeout_sec=5.0)

        if handle:
          result = db.fetch(handle, rows=5000)
          db.close(handle)
          table_ddls.append((0, 0, '\n'.join([row[0] for row in result.rows()])))

      full_table_stats = json.loads(get_table_stats(request, database=path['database'], table=path['table']).content)
      stats = dict((stat['data_type'], stat['comment']) for stat in full_table_stats['stats'])

      table_stats.append({
        'table_name': db_table,
        'num_rows':  stats.get('numRows', -1),
        'last_modified_time':  stats.get('transient_lastDdlTime', -1),
        'total_size':  stats.get('totalSize', -1),
        'raw_data_size':  stats.get('rawDataSize', -1),
        'num_files':  stats.get('numFiles', -1),
        # bytes_cached
        # cache_replication
        # format
      })

      if with_columns:
        for col in full_table_stats['columns']:
          col_stats = json.loads(get_table_stats(request, database=path['database'], table=path['table'], column=col).content)['stats']
          col_stats = dict([(key, val) for col_stat in col_stats for key, val in col_stat.iteritems()])

          column_stats.append({
            'table_name': db_table,
            'column_name': col,
            'data_type': col_stats['data_type'],
            "num_distinct": int(col_stats.get('distinct_count')) if col_stats.get('distinct_count') != '' else -1,
            "num_nulls": int(col_stats['num_nulls']) if col_stats['num_nulls'] != '' else -1,
            "avg_col_len": int(float(col_stats['avg_col_len'])) if col_stats['avg_col_len'] != '' else -1,
            "max_size": int(float(col_stats['max_col_len'])) if col_stats['max_col_len'] != '' else -1,
            "min": col_stats['min'] if col_stats.get('min', '') != '' else -1,
            "max": col_stats['max'] if col_stats.get('max', '') != '' else -1,
            "num_trues": col_stats['num_trues'] if col_stats.get('num_trues', '') != '' else -1,
            "num_falses": col_stats['num_falses'] if col_stats.get('num_falses', '') != '' else -1,
          })
    except Exception, e:
      LOG.exception('Skipping upload of %s: %s' % (db_table, e))

  api = OptimizerApi()

  response['upload_table_stats'] = api.upload(data=table_stats, data_type='table_stats', source_platform=source_platform)
  response['status'] = 0 if response['upload_table_stats']['status']['state'] in ('WAITING', 'FINISHED', 'IN_PROGRESS') else -1
  if column_stats:
    response['upload_cols_stats'] = api.upload(data=column_stats, data_type='cols_stats', source_platform=source_platform)
    response['status'] = response['status'] if response['upload_cols_stats']['status']['state'] in ('WAITING', 'FINISHED', 'IN_PROGRESS') else -1
  if table_ddls:
    response['upload_table_ddl'] = api.upload(data=table_ddls, data_type='queries', source_platform=source_platform)

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
    database, table = 'default', path

  return {'database': database, 'table': table}
