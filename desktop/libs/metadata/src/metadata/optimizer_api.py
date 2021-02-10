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

from builtins import object
import base64
import json
import logging
import struct

from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from desktop.auth.backend import is_admin
from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import force_unicode
from desktop.models import Document2
from libsentry.privilege_checker import MissingSentryPrivilegeException
from notebook.api import _get_statement
from notebook.models import Notebook

from metadata.optimizer.base import get_api
from metadata.optimizer.optimizer_client import NavOptException, _get_table_name, _clean_query
from metadata.conf import OPTIMIZER

LOG = logging.getLogger(__name__)


try:
  from beeswax.api import get_table_stats
  from beeswax.design import hql_query

  from metastore.views import _get_db
except ImportError as e:
  LOG.warn("Hive lib not enabled")


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    try:
      return view_fn(*args, **kwargs)
    except Http404 as e:
      raise e
    except NavOptException as e:
      LOG.exception(e)
      response = {
        'status': -1,
        'message': e.message
      }
    except MissingSentryPrivilegeException as e:
      LOG.exception(e)
      response = {
        'status': -1,
        'message': 'Missing privileges for %s' % force_unicode(str(e))
      }
    except Exception as e:
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

  interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
  cluster_id = request.POST.get('cluster_id')

  api = get_api(request.user, interface)

  data = api.get_tenant(cluster_id=cluster_id)

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

  interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
  database = request.POST.get('database', 'default')
  connector = json.loads(request.POST.get('connector', '{}'))
  limit = request.POST.get('len', 1000)

  api = get_api(request.user, interface)

  data = api.top_tables(database_name=database, page_size=limit, connector=connector)

  if OPTIMIZER.APPLY_SENTRY_PERMISSIONS.get():
    checker = get_checker(user=self.user)
    action = 'SELECT'

    def getkey(table):
      names = _get_table_name(table['name'])
      return {'server': get_hive_sentry_provider(), 'db': names['database'], 'table': names['table']}

    data['results'] = list(checker.filter_objects(data['results'], action, key=getkey))

  tables = [{
      'database': _get_table_name(table['name'])['database'],
      'name': _get_table_name(table['name'])['table'],
      'popularity': table['workloadPercent'],
      'column_count': table['columnCount'],
      'total': table['total'],
    }
    for table in data['results']
  ]

  response['top_tables'] = tables
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@error_handler
def table_details(request):
  response = {'status': -1}

  interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
  connector = json.loads(request.POST.get('connector', '{}'))
  database_name = request.POST.get('databaseName')
  table_name = request.POST.get('tableName')

  api = get_api(request.user, interface)

  data = api.table_details(database_name=database_name, table_name=table_name, connector=connector)

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

  interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
  connector = json.loads(request.POST.get('connector', '{}'))
  source_platform = request.POST.get('sourcePlatform')
  target_platform = request.POST.get('targetPlatform')
  query = request.POST.get('query')

  api = get_api(request.user, interface)

  data = api.query_compatibility(source_platform=source_platform, target_platform=target_platform, query=query, connector=connector)

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

  interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
  connector = json.loads(request.POST.get('connector', '{}'))
  query = json.loads(request.POST.get('query'))
  source_platform = request.POST.get('sourcePlatform')
  db_name = request.POST.get('dbName')

  api = get_api(request.user, interface)

  data = api.query_risk(query=query, source_platform=source_platform, db_name=db_name, connector=connector)

  if data:
    response['status'] = 0
    response['query_risk'] = data
  else:
    response['message'] = 'Optimizer: %s' % data

  return JsonResponse(response)


@require_POST
@error_handler
def predict(request):
  response = {'status': -1}

  interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
  connector = json.loads(request.POST.get('connector', '{}'))
  before_cursor = request.POST.get('beforeCursor', '')
  after_cursor = request.POST.get('afterCursor', '')

  api = get_api(request.user, interface)

  data = api.predict(before_cursor=before_cursor, after_cursor=after_cursor, connector=connector)

  if data:
    response['status'] = 0
    response['prediction'] = data['statement']
  else:
    response['message'] = 'Optimizer: %s' % data

  return JsonResponse(response)


@require_POST
@error_handler
def similar_queries(request):
  response = {'status': -1}

  interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
  connector = json.loads(request.POST.get('connector', '{}'))
  source_platform = request.POST.get('sourcePlatform')
  query = json.loads(request.POST.get('query'))

  api = get_api(request.user, interface)

  data = api.similar_queries(source_platform=source_platform, query=query, connector=connector)

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

  interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
  connector = json.loads(request.POST.get('connector', '{}'))
  db_tables = json.loads(request.POST.get('dbTables', '[]'))
  column_name = request.POST.get('columnName') # Unused

  api = get_api(request.user, interface)

  data = api.top_filters(db_tables=db_tables, connector=connector)

  if data:
    response['status'] = 0
    response['values'] = data['results']
  else:
    response['message'] = 'Optimizer: %s' % data

  if OPTIMIZER.APPLY_SENTRY_PERMISSIONS.get():
    filtered_filters = []
    for result in results['results']:
      cols = [_get_table_name(col['columnName']) for col in result["popularValues"][0]["group"]]
      if len(cols) == len(list(_secure_results(cols, self.user))):
        filtered_filters.append(result)
    results['results'] = filtered_filters

  return JsonResponse(response)


@require_POST
@error_handler
def top_joins(request):
  response = {'status': -1}

  interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
  connector = json.loads(request.POST.get('connector', '{}'))
  db_tables = json.loads(request.POST.get('dbTables', '[]'))

  api = get_api(request.user, interface)

  data = api.top_joins(db_tables=db_tables, connector=connector)

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

  interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
  connector = json.loads(request.POST.get('connector', '{}'))
  db_tables = json.loads(request.POST.get('dbTables', '[]'))

  api = get_api(request.user, interface)

  data = api.top_aggs(db_tables=db_tables, connector=connector)

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

  interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
  connector = json.loads(request.POST.get('connector', '{}'))

  api = get_api(request.user, interface)

  data = api.top_databases(connector=connector)

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

  interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
  connector = json.loads(request.POST.get('connector', '{}'))
  db_tables = json.loads(request.POST.get('dbTables', '[]'))

  api = get_api(request.user, interface)

  data = api.top_columns(db_tables=db_tables, connector=connector)

  if data:
    response['status'] = 0
    response['values'] = data
  else:
    response['message'] = 'Optimizer: %s' % data

  return JsonResponse(response)


def _convert_queries(queries_data):
  queries = []

  for query_data in queries_data:
    try:
      snippet = query_data['snippets'][0]
      if 'guid' in snippet['result']['handle']: # Not failed query
        guid = snippet['result']['handle']['guid']
        if isinstance(guid, str):
          guid = guid.encode('utf-8')
        # unpack_guid uses '%016x:%016x' while optmizer api uses '%s:%s'.
        original_query_id = '%s:%s' % struct.unpack(b"QQ", base64.decodestring(guid))
        execution_time = snippet['result']['executionTime'] * 100 if snippet['status'] in ('available', 'expired') else -1
        statement = _clean_query(_get_statement(query_data))
        queries.append((original_query_id, execution_time, statement, snippet.get('database', 'default').strip()))
    except Exception as e:
      LOG.warning('Skipping upload of %s: %s' % (query_data['uuid'], e))

  return queries


@require_POST
@error_handler
def upload_history(request):
  response = {'status': -1}

  if is_admin(request.user):
    interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
    api = get_api(request.user, interface)
    histories = []
    upload_stats = {}

    if request.POST.get('sourcePlatform'):
      n = min(request.POST.get('n', OPTIMIZER.QUERY_HISTORY_UPLOAD_LIMIT.get()))
      source_platform = request.POST.get('sourcePlatform', 'hive')
      histories = [(source_platform, Document2.objects.get_history(doc_type='query-%s' % source_platform, user=request.user)[:n])]

    elif OPTIMIZER.QUERY_HISTORY_UPLOAD_LIMIT.get() > 0:
      histories = [
        (
          source_platform,
          Document2.objects.filter(
            type='query-%s' % source_platform, is_history=True, is_managed=False, is_trashed=False
          ).order_by('-last_modified')[:OPTIMIZER.QUERY_HISTORY_UPLOAD_LIMIT.get()]
        )
        for source_platform in ['hive', 'impala']
      ]

    for source_platform, history in histories:
      queries = _convert_queries([Notebook(document=doc).get_data() for doc in history])
      upload_stats[source_platform] = api.upload(data=queries, data_type='queries', source_platform=source_platform)

    response['upload_history'] = upload_stats
    response['status'] = 0
  else:
    response['message'] = _('Query history upload requires Admin privileges or feature is disabled.')

  return JsonResponse(response)


@require_POST
@error_handler
def upload_query(request):
  response = {'status': -1}

  interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
  source_platform = request.POST.get('sourcePlatform', 'default')
  query_id = request.POST.get('query_id')

  if OPTIMIZER.AUTO_UPLOAD_QUERIES.get() and source_platform in ('hive', 'impala') and query_id:
    try:
      doc = Document2.objects.document(request.user, doc_id=query_id)

      query_data = Notebook(document=doc).get_data()
      queries = _convert_queries([query_data])
      source_platform = query_data['snippets'][0]['type']

      api = get_api(request.user, interface)

      response['query_upload'] = api.upload(data=queries, data_type='queries', source_platform=source_platform)
    except Document2.DoesNotExist:
      response['query_upload'] = _('Skipped as task query')
  else:
    response['query_upload'] = _('Skipped')
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@error_handler
def upload_table_stats(request):
  response = {'status': -1}

  interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
  db_tables = json.loads(request.POST.get('db_tables', '[]'))
  source_platform = json.loads(request.POST.get('sourcePlatform', '"hive"'))
  with_ddl = json.loads(request.POST.get('with_ddl', 'false'))
  with_table_stats = json.loads(request.POST.get('with_table', 'false'))
  with_columns_stats = json.loads(request.POST.get('with_columns', 'false'))

  table_ddls = []
  table_stats = []
  column_stats = []

  if not OPTIMIZER.AUTO_UPLOAD_DDL.get():
    with_ddl = False

  if not OPTIMIZER.AUTO_UPLOAD_STATS.get():
    with_table_stats = with_columns_stats = False


  for db_table in db_tables:
    path = _get_table_name(db_table)

    try:
      if with_ddl:
        db = _get_db(request.user, source_type=source_platform)
        query = hql_query('SHOW CREATE TABLE `%(database)s`.`%(table)s`' % path)
        handle = db.execute_and_wait(query, timeout_sec=5.0)

        if handle:
          result = db.fetch(handle, rows=5000)
          db.close(handle)
          table_ddls.append((0, 0, ' '.join([row[0] for row in result.rows()]), path['database']))

      if with_table_stats:
        mock_request = MockRequest(user=request.user, source_platform=source_platform)
        full_table_stats = json.loads(get_table_stats(mock_request, database=path['database'], table=path['table']).content)
        stats = dict((stat['data_type'], stat['comment']) for stat in full_table_stats['stats'])

        table_stats.append({
          'table_name': '%(database)s.%(table)s' % path, # DB Prefix
          'num_rows': stats.get('numRows', -1),
          'last_modified_time': stats.get('transient_lastDdlTime', -1),
          'total_size': stats.get('totalSize', -1),
          'raw_data_size': stats.get('rawDataSize', -1),
          'num_files': stats.get('numFiles', -1),
          'num_partitions': stats.get('numPartitions', -1),
          # bytes_cached
          # cache_replication
          # format
        })

      if with_columns_stats:
        if source_platform == 'impala':
          colum_stats = json.loads(
            get_table_stats(mock_request, database=path['database'], table=path['table'], column=-1).content
          )['stats']
        else:
          colum_stats = [
              json.loads(get_table_stats(mock_request, database=path['database'], table=path['table'], column=col).content)['stats']
              for col in full_table_stats['columns'][:25]
          ]

        raw_column_stats = [
          dict([
            (key, val if val is not None else '')
              for col_stat in col for key, val in col_stat.items()
            ]
          )
          for col in colum_stats
        ]

        for col_stats in raw_column_stats:
          column_stats.append({
            'table_name': '%(database)s.%(table)s' % path, # DB Prefix
            'column_name': col_stats['col_name'],
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
    except Exception as e:
      LOG.exception('Skipping upload of %s: %s' % (db_table, e))

  api = get_api(request.user, interface)

  response['status'] = 0

  if table_stats:
    response['upload_table_stats'] = api.upload(data=table_stats, data_type='table_stats', source_platform=source_platform)
    response['upload_table_stats_status'] = 0 if response['upload_table_stats']['status']['state'] in (
      'WAITING', 'FINISHED', 'IN_PROGRESS') else -1
    response['status'] = response['upload_table_stats_status']
  if column_stats:
    response['upload_cols_stats'] = api.upload(data=column_stats, data_type='cols_stats', source_platform=source_platform)
    response['upload_cols_stats_status'] = response['status'] if response['upload_cols_stats']['status']['state'] in (
      'WAITING', 'FINISHED', 'IN_PROGRESS') else -1
    if response['upload_cols_stats_status'] != 0:
      response['status'] = response['upload_cols_stats_status']
  if table_ddls:
    response['upload_table_ddl'] = api.upload(data=table_ddls, data_type='queries', source_platform=source_platform)
    response['upload_table_ddl_status'] = response['status'] if response['upload_table_ddl']['status']['state'] in (
      'WAITING', 'FINISHED', 'IN_PROGRESS') else -1
    if response['upload_table_ddl_status'] != 0:
      response['status'] = response['upload_table_ddl_status']

  return JsonResponse(response)


@require_POST
@error_handler
def upload_status(request):
  response = {'status': -1}

  interface = request.POST.get('interface', OPTIMIZER.INTERFACE.get())
  workload_id = request.POST.get('workloadId')

  api = get_api(request.user, interface)

  response['upload_status'] = api.upload_status(workload_id=workload_id)
  response['status'] = 0

  return JsonResponse(response)


class MockRequest(object):

  def __init__(self, user, source_platform):
    self.user = user
    self.path = '/%s/' % source_platform if source_platform != 'hive' else 'beeswax'
