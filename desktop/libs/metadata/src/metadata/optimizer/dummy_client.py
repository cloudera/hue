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

from builtins import object
import json
import logging
import os
import time
import uuid

from tempfile import NamedTemporaryFile

from django.core.cache import cache
from django.utils.functional import wraps
from django.utils.translation import ugettext as _

from desktop.auth.backend import is_admin
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib import export_csvxls
from desktop.lib.i18n import smart_unicode
from desktop.lib.rest.http_client import RestException
from libsentry.sentry_site import get_hive_sentry_provider
from libsentry.privilege_checker import get_checker, MissingSentryPrivilegeException

from metadata.conf import OPTIMIZER, get_optimizer_url
from metadata.optimizer.base import Api


LOG = logging.getLogger(__name__)

_JSON_CONTENT_TYPE = 'application/json'


class DummyClient(Api):

  def __init__(self, user, api_url=None, auth_key=None, auth_key_secret=None, tenant_id=None):
    self.user = user
    self._api_url = (api_url or get_optimizer_url()).strip('/')
    self._auth_key = auth_key if auth_key else OPTIMIZER.AUTH_KEY_ID.get()
    self._auth_key_secret = auth_key_secret if auth_key_secret else (OPTIMIZER.AUTH_KEY_SECRET.get() and OPTIMIZER.AUTH_KEY_SECRET.get().replace('\\n', '\n'))

    self._api = None

    self._tenant_id = tenant_id


  def get_tenant(self, cluster_id='default'):
    pass


  def upload(self, data, data_type='queries', source_platform='generic', workload_id=None):
    pass


  def upload_status(self, workload_id):
    pass

  # Sentry permissions work bottom to top.
  # @check_privileges
  def top_tables(self, workfloadId=None, database_name='default', page_size=1000, startingToken=None):
    data = {'results': []}

    return data

  @check_privileges
  def table_details(self, database_name, table_name, page_size=100, startingToken=None):
    return {}


  def query_compatibility(self, source_platform, target_platform, query, page_size=100, startingToken=None):
    return {}


  def query_risk(self, query, source_platform, db_name, page_size=100, startingToken=None):
    return {
      'hints': hints,
      'noStats': response.get('noStats', []),
      'noDDL': response.get('noDDL', []),
    }

  def similar_queries(self, source_platform, query, page_size=100, startingToken=None):
    raise PopupException(_('Call not supported'))


  @check_privileges
  def top_filters(self, db_tables=None, page_size=100, startingToken=None):
    results = {'result': []}

    return results


  @check_privileges
  def top_aggs(self, db_tables=None, page_size=100, startingToken=None):
    results = {'result': []}

    return results


  @check_privileges
  def top_columns(self, db_tables=None, page_size=100, startingToken=None):
    results = {'results': []}

    return results


  @check_privileges
  def top_joins(self, db_tables=None, page_size=100, startingToken=None):
    results = {'results': []}

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
