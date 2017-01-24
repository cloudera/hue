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
from desktop.lib.rest.http_client import RestException
from navoptapi.api_lib import ApiLib

from metadata.conf import OPTIMIZER, get_optimizer_url


LOG = logging.getLogger(__name__)


_JSON_CONTENT_TYPE = 'application/json'



class OptimizerApiException(PopupException):
  pass


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


  def get_tenant(self, email=None):
    return self._api.call_api("getTenant", {"email" : email or self._email}).json()


  def create_tenant(self, group):
    return self._api.call_api('createTenant', {'userGroup' : group}).json()


  def authenticate(self):
    try:
      data = {
          'productName': self._product_name,
          'productSecret': self._product_secret,
      }
      return self._root.post('/api/authenticate', data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def delete_workload(self, token, email=None):
    try:
      data = {
          'email': email if email is not None else self._email,
          'token': token,
      }
      return self._root.post('/api/deleteWorkload', data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def upload(self, data, data_type='queries', source_platform='generic', workload_id=None):
    if data_type in ('table_stats', 'cols_stats'):
      data_suffix = '.log'
    else:
      data_suffix = '.csv'

    f_queries_path = NamedTemporaryFile(suffix=data_suffix)
    f_queries_path.close() # Reopened as real file below to work well with the command

    try:
      f_queries = open(f_queries_path.name, 'w+')

      try:
        content_generator = OptimizerDataAdapter(data, data_type=data_type)
        queries_csv = export_csvxls.create_generator(content_generator, 'csv')

        for row in queries_csv:
          f_queries.write(row)

      finally:
        f_queries.close()

      response = self._api.call_api('upload', {
          'tenant' : self._product_name,
          'fileLocation': f_queries.name,
          'sourcePlatform': source_platform,
          'colDelim': ',',
          'rowDelim': '\n',
          'headerFields': OptimizerApi.UPLOAD[data_type]['headerFields']
      })
      status = json.loads(response)
      status['count'] = len(data)
      return status

    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))
    finally:
      os.remove(f_queries_path.name)

  def upload_status(self, workload_id):
    return self._api.call_api('uploadStatus', {'tenant' : self._product_name, 'workloadId': workload_id}).json()


  def top_tables(self, workfloadId=None, database_name='default'):
    return self._api.call_api('getTopTables', {'tenant' : self._product_name, 'dbName': database_name.lower()}).json()


  def table_details(self, database_name, table_name):
    return self._api.call_api('getTablesDetail', {'tenant' : self._product_name, 'dbName': database_name.lower(), 'tableName': table_name.lower()}).json()


  def query_compatibility(self, source_platform, target_platform, query):
    return self._api.call_api('getQueryCompatible', {'tenant' : self._product_name, 'query': query, 'sourcePlatform': source_platform, 'targetPlatform': target_platform}).json()


  def query_risk(self, query):
    return self._api.call_api('getQueryRisk', {'tenant' : self._product_name, 'query': query}).json()


  def similar_queries(self, source_platform, query):
    return self._api.call_api('getSimilarQueries', {'tenant' : self._product_name, 'sourcePlatform': source_platform, 'query': query}).json()


  def top_filters(self, db_tables=None):
    args = {
      'tenant' : self._product_name
    }
    if db_tables:
      args['dbTableList'] = [db_table.lower() for db_table in db_tables]

    return self._api.call_api('getTopFilters', args).json()


  def top_aggs(self, db_tables=None):
    args = {
      'tenant' : self._product_name
    }
    if db_tables:
      args['dbTableList'] = [db_table.lower() for db_table in db_tables]

    return self._api.call_api('getTopAggs', args).json()


  def top_columns(self, db_tables=None):
    args = {
      'tenant' : self._product_name
    }
    if db_tables:
      args['dbTableList'] = [db_table.lower() for db_table in db_tables]

    return self._api.call_api('getTopColumns', args).json()


  def top_joins(self, db_tables=None):
    args = {
      'tenant' : self._product_name
    }
    if db_tables:
      args['dbTableList'] = [db_table.lower() for db_table in db_tables]

    return self._api.call_api('getTopJoins', args).json()


  def top_databases(self, db_tables=None):
    args = {
      'tenant' : self._product_name
    }

    return self._api.call_api('getTopDataBases', args).json()


  UPLOAD = {
    'queries': {
      'headers': ['SQL_ID', 'ELAPSED_TIME', 'SQL_FULLTEXT'],
      "colDelim": ",",
      "rowDelim": "\\n",
      "headerFields": [
          {
              "count": 0,
              "coltype": "SQL_ID",
              "use": True,
              "tag": "",
              "name": "SQL_ID"
          },
          {
              "count": 0,
              "coltype": "NONE",
              "use": True,
              "tag": "",
              "name": "ELAPSED_TIME"
          },
          {
              "count": 0,
              "coltype": "SQL_QUERY",
              "use": True,
              "tag": "",
              "name": "SQL_FULLTEXT"
          }
      ]
    },
    'table_stats': {
        'headers': ['TABLE_NAME', 'NUM_ROWS'],
        "colDelim": ",",
        "rowDelim": "\\n",
        "headerFields": [
            {
                "count": 0,
                "coltype": "NONE",
                "use": True,
                "tag": "",
                "name": "TABLE_NAME"
            },
            {
                "count": 0,
                "coltype": "NONE",
                "use": True,
                "tag": "",
                "name": "NUM_ROWS"
            }
        ]
    },
    'cols_stats': {
        'headers': ['table_name', 'column_name', 'data_type', 'num_distinct', 'num_nulls', 'avg_col_len'], # Lower case for some reason
        "colDelim": ",",
        "rowDelim": "\\n",
        "headerFields": [
            {
                "count": 0,
                "coltype": "NONE",
                "use": True,
                "tag": "",
                "name": "table_name"
            },
            {
                "count": 0,
                "coltype": "NONE",
                "use": True,
                "tag": "",
                "name": "column_name"
            },
            {
                "count": 0,
                "coltype": "NONE",
                "use": True,
                "tag": "",
                "name": "data_type"
            },
            {
                "count": 0,
                "coltype": "NONE",
                "use": True,
                "tag": "",
                "name": "num_distinct"
            },
            {
                "count": 0,
                "coltype": "NONE",
                "use": True,
                "tag": "",
                "name": "num_nulls"
            },
            {
                "count": 0,
                "coltype": "NONE",
                "use": True,
                "tag": "",
                "name": "avg_col_len"
            }
        ]
    }
  }


def OptimizerDataAdapter(data, data_type='queries'):
  headers = OptimizerApi.UPLOAD[data_type]['headers']

  if data_type in ('table_stats', 'cols_stats'):
    rows = data
  else:
    if data and len(data[0]) == 3:
      rows = data
    else:
      rows = ([str(uuid.uuid4()), 0.0, q] for q in data)

  yield headers, rows

