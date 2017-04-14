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
import uuid

from tempfile import NamedTemporaryFile
from urlparse import urlparse

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib import export_csvxls
from desktop.lib.i18n import smart_unicode
from desktop.lib.rest.http_client import RestException
from navoptapi.api_lib import ApiLib

from metadata.conf import OPTIMIZER, get_optimizer_url


LOG = logging.getLogger(__name__)


_JSON_CONTENT_TYPE = 'application/json'


class NavOptException(Exception):
  def __init__(self, message=None):
    self.message = message or _('No error message, please check the logs.')

  def __unicode__(self):
    return smart_unicode(self.message)


class OptimizerApi(object):

  def __init__(self, api_url=None, product_name=None, product_secret=None, ssl_cert_ca_verify=OPTIMIZER.SSL_CERT_CA_VERIFY.get(), product_auth_secret=None):
    self._api_url = (api_url or get_optimizer_url()).strip('/')
    self._email = OPTIMIZER.EMAIL.get()
    self._email_password = OPTIMIZER.EMAIL_PASSWORD.get()
    self._product_secret = product_secret if product_secret else OPTIMIZER.PRODUCT_SECRET.get()
    self._product_auth_secret = product_auth_secret if product_auth_secret else (OPTIMIZER.PRODUCT_AUTH_SECRET.get() and OPTIMIZER.PRODUCT_AUTH_SECRET.get().replace('\\n', '\n'))

    self._api = ApiLib("navopt", urlparse(self._api_url).hostname, self._product_secret, self._product_auth_secret)

    self._product_name = product_name if product_name else (OPTIMIZER.PRODUCT_NAME.get() or self.get_tenant()['tenant']) # Aka "workload"

  def _authenticate(self, force=False):
    if self._token is None or force:
      self._token = self.authenticate()['token']

    return self._token

  def _call(self, *kwargs):
    data = self._api.call_api(*kwargs).json()

    if data.get('code') == 'UNKNOWN':
      raise NavOptException(data.get('message'))
    else:
      return data

  def get_tenant(self, email=None):
    return self._call("getTenant", {"email" : email or self._email})


  def create_tenant(self, group):
    return self._call('createTenant', {'userGroup' : group})


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
            LOG.debug(row)
        else:
          # Table, column stats
          f_queries.write(json.dumps(data))
          LOG.debug(json.dumps(data))

      finally:
        f_queries.close()

      parameters = {
          'tenant' : self._product_name,
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
    return self._call('uploadStatus', {'tenant' : self._product_name, 'workloadId': workload_id})


  def top_tables(self, workfloadId=None, database_name='default', page_size=1000, startingToken=None):
    return self._call('getTopTables', {'tenant' : self._product_name, 'dbName': database_name.lower(), 'pageSize': page_size, startingToken: None})


  def table_details(self, database_name, table_name, page_size=100, startingToken=None):
    return self._call('getTablesDetail', {'tenant' : self._product_name, 'dbName': database_name.lower(), 'tableName': table_name.lower(), 'pageSize': page_size, startingToken: None})


  def query_compatibility(self, source_platform, target_platform, query, page_size=100, startingToken=None):
    return self._call('getQueryCompatible', {'tenant' : self._product_name, 'query': query, 'sourcePlatform': source_platform, 'targetPlatform': target_platform, })


  def query_risk(self, query, source_platform, page_size=100, startingToken=None):
    response = self._call('getQueryRisk', {'tenant' : self._product_name, 'query': query, 'sourcePlatform': source_platform, 'pageSize': page_size, startingToken: None})
    data = response.get(source_platform + 'Risk', {})

    if data and data == [{u'riskAnalysis': u'', u'risk': u'low', u'riskRecommendation': u''}]:
      data = []

    return data


  def similar_queries(self, source_platform, query, page_size=100, startingToken=None):
    return self._call('getSimilarQueries', {'tenant' : self._product_name, 'sourcePlatform': source_platform, 'query': query, 'pageSize': page_size, startingToken: None})


  def top_filters(self, db_tables=None, page_size=100, startingToken=None):
    args = {
      'tenant' : self._product_name,
      'pageSize': page_size,
      'startingToken': None
    }
    if db_tables:
      args['dbTableList'] = [db_table.lower() for db_table in db_tables]

    return self._call('getTopFilters', args)


  def top_aggs(self, db_tables=None, page_size=100, startingToken=None):
    args = {
      'tenant' : self._product_name,
      'pageSize': page_size,
      'startingToken': None
    }
    if db_tables:
      args['dbTableList'] = [db_table.lower() for db_table in db_tables]

    return self._call('getTopAggs', args)


  def top_columns(self, db_tables=None, page_size=100, startingToken=None):
    args = {
      'tenant' : self._product_name,
      'pageSize': page_size,
      'startingToken': None
    }
    if db_tables:
      args['dbTableList'] = [db_table.lower() for db_table in db_tables]

    return self._call('getTopColumns', args)


  def top_joins(self, db_tables=None, page_size=100, startingToken=None):
    args = {
      'tenant' : self._product_name,
      'pageSize': page_size,
      'startingToken': None
    }
    if db_tables:
      args['dbTableList'] = [db_table.lower() for db_table in db_tables]

    return self._call('getTopJoins', args)


  def top_databases(self, page_size=100, startingToken=None):
    args = {
      'tenant' : self._product_name,
      'pageSize': page_size,
      'startingToken': None
    }

    return self._call('getTopDatabases', args)


def OptimizerQueryDataAdapter(data):
  headers = ['SQL_ID', 'ELAPSED_TIME', 'SQL_FULLTEXT', 'DATABASE']

  if data and len(data[0]) == 4:
    rows = data
  else:
    rows = ([str(uuid.uuid4()), 0.0, q, 'default'] for q in data)

  yield headers, rows
