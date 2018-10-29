#!/usr/bin/env python
# -- coding: utf-8 --
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
import os
import time
import uuid

from tempfile import NamedTemporaryFile

from django.core.cache import cache
from django.utils.functional import wraps
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib import export_csvxls
from desktop.lib.i18n import smart_unicode
from desktop.lib.rest.http_client import RestException
from libsentry.sentry_site import get_hive_sentry_provider
from libsentry.privilege_checker import get_checker, MissingSentryPrivilegeException
from navoptapi.api_lib import ApiLib

from metadata.conf import OPTIMIZER, get_optimizer_url

from desktop.auth.backend import is_admin

LOG = logging.getLogger(__name__)


_JSON_CONTENT_TYPE = 'application/json'
OPTIMIZER_TENANT_ID_CACHE_KEY = 'navopt-tenant-id'


class NavOptException(Exception):
  def __init__(self, message=None):
    self.message = message or _('No error message, please check the logs.')

  def __str__(self):
    return str(self.message)

  def __unicode__(self):
    return smart_unicode(self.message)


def check_privileges(view_func):
  def decorate(*args, **kwargs):

    if OPTIMIZER.APPLY_SENTRY_PERMISSIONS.get():
      checker = get_checker(user=args[0].user)
      action = 'SELECT'
      objects = []

      if kwargs.get('db_tables'):
        for db_table in kwargs['db_tables']:
          objects.append({'server': get_hive_sentry_provider(), 'db': _get_table_name(db_table)['database'], 'table': _get_table_name(db_table)['table']})
      else:
        objects = [{'server': get_hive_sentry_provider()}]
        if kwargs.get('database_name'):
          objects[0]['db'] = kwargs['database_name']
        if kwargs.get('table_name'):
          objects[0]['table'] = kwargs['table_name']

      filtered = list(checker.filter_objects(objects, action))
      if len(filtered) != len(objects):
        raise MissingSentryPrivilegeException({'pre_filtering': objects, 'post_filtering': filtered, 'diff': len(objects) - len(filtered)})

    return view_func(*args, **kwargs)
  return wraps(view_func)(decorate)


class OptimizerApi(object):

  def __init__(self, user, api_url=None, auth_key=None, auth_key_secret=None, tenant_id=None):
    self.user = user
    self._api_url = (api_url or get_optimizer_url()).strip('/')
    self._auth_key = auth_key if auth_key else OPTIMIZER.AUTH_KEY_ID.get()
    self._auth_key_secret = auth_key_secret if auth_key_secret else (OPTIMIZER.AUTH_KEY_SECRET.get() and OPTIMIZER.AUTH_KEY_SECRET.get().replace('\\n', '\n'))

    self._api = ApiLib("navopt", self._api_url, self._auth_key, self._auth_key_secret)

    self._tenant_id = tenant_id if tenant_id else _get_tenant_id(self) # Aka "workload"


  def _call(self, *kwargs):
    start_time = time.time()

    resp = self._api.call_api(*kwargs)
    data = resp.json()

    if resp.headers.get('x-altus-request-id'):
      LOG.info('%s %s in %dms: %s' % (self.user, resp.headers['x-altus-request-id'], (time.time() - start_time) * 1000, kwargs))

    if data.get('code') == 'UNKNOWN':
      raise NavOptException(data.get('message'))
    elif data.get('errorMsg'):
      raise NavOptException(data.get('errorMsg'))
    else:
      return data


  def get_tenant(self, cluster_id='default'):
    return self._call('getTenant', {'clusterId' : cluster_id})


  def upload(self, data, data_type='queries', source_platform='generic', workload_id=None):
    if data_type in ('table_stats', 'cols_stats'):
      data_suffix = '.json'
      if data_type == 'table_stats':
        extra_parameters = {'fileType': 'TABLE_STATS'}
      else:
        extra_parameters = {'fileType': 'COLUMN_STATS'}
    else:
      data_suffix = '.csv'
      extra_parameters = {
          'fileType': 'QUERY',
          'colDelim': ',',
          'rowDelim': '\n',
          "headerFields": [
            {"count": 0, "name": "SQL_ID", "coltype": "SQL_ID", "use": True, "tag": ""},
            {"count": 0, "name": "ELAPSED_TIME", "coltype": "NONE", "use": True, "tag": ""},
            {"count": 0, "name": "SQL_FULLTEXT", "coltype": "SQL_QUERY", "use": True, "tag": ""},
            {"count": 0, "name": "DATABASE", "coltype": "NONE", "use": True, "tag": "DATABASE"}
          ],
      }

    f_queries_path = NamedTemporaryFile(suffix=data_suffix)
    f_queries_path.close() # Reopened as real file below to work well with the command

    try:
      f_queries = open(f_queries_path.name, 'w+')

      try:
        # Queries
        if data_suffix == '.csv':
          content_generator = OptimizerQueryDataAdapter(data)
          queries_csv = export_csvxls.create_generator(content_generator, 'csv')

          for row in queries_csv:
            f_queries.write(row)
            LOG.debug(row[:1000])
        else:
          # Table, column stats
          f_queries.write(json.dumps(data))
          LOG.debug(json.dumps(data[:10]))

      finally:
        f_queries.close()

      parameters = {
          'tenant' : self._tenant_id,
          'fileLocation': f_queries.name,
          'sourcePlatform': source_platform,
      }
      parameters.update(extra_parameters)
      response = self._api.call_api('upload', parameters)
      status = json.loads(response)

      status['count'] = len(data)
      return status

    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))
    finally:
      os.remove(f_queries_path.name)


  def upload_status(self, workload_id):
    return self._call('uploadStatus', {'tenant' : self._tenant_id, 'workloadId': workload_id})

  # Sentry permissions work bottom to top.
  # @check_privileges
  def top_tables(self, workfloadId=None, database_name='default', page_size=1000, startingToken=None):
    data = self._call('getTopTables', {'tenant' : self._tenant_id, 'dbName': database_name.lower(), 'pageSize': page_size, 'startingToken': startingToken})

    if OPTIMIZER.APPLY_SENTRY_PERMISSIONS.get():
      checker = get_checker(user=self.user)
      action = 'SELECT'

      def getkey(table):
        names = _get_table_name(table['name'])
        return {'server': get_hive_sentry_provider(), 'db': names['database'], 'table': names['table']}

      data['results'] = list(checker.filter_objects(data['results'], action, key=getkey))

    return data

  @check_privileges
  def table_details(self, database_name, table_name, page_size=100, startingToken=None):
    return self._call('getTablesDetail', {'tenant' : self._tenant_id, 'dbName': database_name.lower(), 'tableName': table_name.lower(), 'pageSize': page_size, 'startingToken': startingToken})


  def query_compatibility(self, source_platform, target_platform, query, page_size=100, startingToken=None):
    return self._call('getQueryCompatible', {'tenant' : self._tenant_id, 'query': query, 'sourcePlatform': source_platform, 'targetPlatform': target_platform, 'startingToken': startingToken})


  def query_risk(self, query, source_platform, db_name, page_size=100, startingToken=None):
    response = self._call('getQueryRisk', {
      'tenant' : self._tenant_id,
      'query': _clean_query(query),
      'dbName': db_name,
      'sourcePlatform': source_platform,
      'pageSize': page_size,
      'startingToken': startingToken
    })

    hints = response.get(source_platform + 'Risk', {})

    if hints and hints == [{"riskTables": [], "riskAnalysis": "", "riskId": 0, "risk": "low", "riskRecommendation": ""}]:
      hints = []

    return {
      'hints': hints,
      'noStats': response.get('noStats', []),
      'noDDL': response.get('noDDL', []),
    }

  def similar_queries(self, source_platform, query, page_size=100, startingToken=None):
    if is_admin(self.user):
      return self._call('getSimilarQueries', {'tenant' : self._tenant_id, 'sourcePlatform': source_platform, 'query': query, 'pageSize': page_size, 'startingToken': startingToken})
    else:
      raise PopupException(_('Call not supported'))


  @check_privileges
  def top_filters(self, db_tables=None, page_size=100, startingToken=None):
    args = {
      'tenant' : self._tenant_id,
      'pageSize': page_size,
      'startingToken': startingToken
    }
    if db_tables:
      args['dbTableList'] = [db_table.lower() for db_table in db_tables]

    results = self._call('getTopFilters', args)

    if OPTIMIZER.APPLY_SENTRY_PERMISSIONS.get():
      filtered_filters = []
      for result in results['results']:
        cols = [_get_table_name(col['columnName']) for col in result["popularValues"][0]["group"]]
        if len(cols) == len(list(_secure_results(cols, self.user))):
          filtered_filters.append(result)
      results['results'] = filtered_filters
    return results


  @check_privileges
  def top_aggs(self, db_tables=None, page_size=100, startingToken=None):
    args = {
      'tenant' : self._tenant_id,
      'pageSize': page_size,
      'startingToken': startingToken
    }
    if db_tables:
      args['dbTableList'] = [db_table.lower() for db_table in db_tables]

    results = self._call('getTopAggs', args)

    if OPTIMIZER.APPLY_SENTRY_PERMISSIONS.get():
      checker = get_checker(user=self.user)
      action = 'SELECT'

      def getkey(table):
        names = table['aggregateInfo'][0]
        names['server'] = get_hive_sentry_provider()
        return names

      results['results'] = list(checker.filter_objects(results['results'], action, key=getkey))

    return results


  @check_privileges
  def top_columns(self, db_tables=None, page_size=100, startingToken=None):
    args = {
      'tenant' : self._tenant_id,
      'pageSize': page_size,
      'startingToken': startingToken
    }
    if db_tables:
      args['dbTableList'] = [db_table.lower() for db_table in db_tables]

    results = self._call('getTopColumns', args)

    if OPTIMIZER.APPLY_SENTRY_PERMISSIONS.get():
      for section in ['orderbyColumns', 'selectColumns', 'filterColumns', 'joinColumns', 'groupbyColumns']:
        results[section] = list(_secure_results(results[section], self.user))
    return results


  @check_privileges
  def top_joins(self, db_tables=None, page_size=100, startingToken=None):
    args = {
      'tenant' : self._tenant_id,
      'pageSize': page_size,
      'startingToken': startingToken
    }
    if db_tables:
      args['dbTableList'] = [db_table.lower() for db_table in db_tables]

    results = self._call('getTopJoins', args)

    if OPTIMIZER.APPLY_SENTRY_PERMISSIONS.get():
      filtered_joins = []
      for result in results['results']:
        cols = [_get_table_name(col) for col in result["joinCols"][0]["columns"]]
        if len(cols) == len(list(_secure_results(cols, self.user))):
          filtered_joins.append(result)
      results['results'] = filtered_joins
    return results


  def top_databases(self, page_size=100, startingToken=None):
    args = {
      'tenant' : self._tenant_id,
      'pageSize': page_size,
      'startingToken': startingToken
    }

    data = self._call('getTopDatabases', args)

    if OPTIMIZER.APPLY_SENTRY_PERMISSIONS.get():
      data['results'] = list(_secure_results(data['results'], self.user))

    return data


def OptimizerQueryDataAdapter(data):
  headers = ['SQL_ID', 'ELAPSED_TIME', 'SQL_FULLTEXT', 'DATABASE']

  if data and len(data[0]) == 4:
    rows = data
  else:
    rows = ([str(uuid.uuid4()), 0.0, q, 'default'] for q in data)

  yield headers, rows


def _get_table_name(path):
  column = None

  if path.count('.') == 1:
    database, table = path.split('.', 1)
  elif path.count('.') == 2:
    database, table, column = path.split('.', 2)
  else:
    database, table = 'default', path

  name = {'database': database, 'table': table}
  if column:
    name['column'] = column
  return name


def _secure_results(results, user, action='SELECT'):
    if OPTIMIZER.APPLY_SENTRY_PERMISSIONS.get():
      checker = get_checker(user=user)

      def getkey(result):
        key = {'server': get_hive_sentry_provider()}

        if 'dbName' in result:
          key['db'] = result['dbName']
        elif 'database' in result:
          key['db'] = result['database']
        if 'tableName' in result:
          key['table'] = result['tableName']
        elif 'table' in result:
          key['table'] = result['table']
        if 'columnName' in result:
          key['column'] = result['columnName']
        elif 'column' in result:
          key['column'] = result['column']

        return key

      return checker.filter_objects(results, action, key=getkey)
    else:
      return results


def _clean_query(query):
  return ' '.join([line for line in query.strip().splitlines() if not line.strip().startswith('--')])


def _get_tenant_id(api):
  tenant_id = OPTIMIZER.TENANT_ID.get() or cache.get(OPTIMIZER_TENANT_ID_CACHE_KEY)
  if not tenant_id:
    tenant = api.get_tenant(cluster_id=OPTIMIZER.CLUSTER_ID.get())
    if tenant.get('tenant'):
      tenant_id = tenant['tenant']
    else:
      raise PopupException(_('Could not get tenant id from cluster id %s: %s') % (OPTIMIZER.CLUSTER_ID.get(), tenant))
    cache.set(OPTIMIZER_TENANT_ID_CACHE_KEY, tenant_id, 60 * 60 * 24 * 30)
  return tenant_id
