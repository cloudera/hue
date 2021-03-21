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

import logging

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException

from metadata.optimizer.base import Api


LOG = logging.getLogger(__name__)


class DummyClient(Api):

  def __init__(self, user, api_url=None, auth_key=None, auth_key_secret=None, tenant_id=None):
    self.user = user


  def get_tenant(self, cluster_id='default'):
    pass


  def upload(self, data, data_type='queries', source_platform='generic', workload_id=None):
    pass


  def upload_status(self, workload_id):
    pass


  def top_tables(self, workfloadId=None, database_name='default', page_size=1000, startingToken=None, connector=None):
    data = {
      'results': [{
          "database": "default",
          "name": "sample_07",
          "workloadPercent": 42,
          "columnCount": 4,
          "total": 6
        }, {
          "database": "default",
          "name": "sample_08",
          "workloadPercent": 21,
          "columnCount": 4,
          "total": 3
        }, {
          "database": "default",
          "name": "web_logs",
          "workloadPercent": 21,
          "columnCount": 1,
          "total": 3
        }, {
          "database": "default",
          "name": "customers",
          "workloadPercent": 7,
          "columnCount": 44,
          "total": 1
        }
      ]
    }

    return data


  def table_details(self, database_name, table_name, page_size=100, startingToken=None, connector=None):
    return {}


  def query_compatibility(self, source_platform, target_platform, query, page_size=100, startingToken=None, connector=None):
    return {}


  def query_risk(self, query, source_platform, db_name, page_size=100, startingToken=None, connector=None):
    hints = []
    response = {}

    return {
      'hints': hints,
      'noStats': response.get('noStats', []),
      'noDDL': response.get('noDDL', []),
    }


  def predict(self, query, source_platform, connector):
    hints = []
    response = {}

    return {
      'hints': hints,
    }


  def similar_queries(self, source_platform, query, page_size=100, startingToken=None, connector=None):
    raise PopupException(_('Call not supported'))


  def top_filters(self, db_tables=None, page_size=100, startingToken=None, connector=None):
    results = {'results': []}

    return results


  def top_aggs(self, db_tables=None, page_size=100, startingToken=None, connector=None):
    results = {'results': []}

    return results


  def top_columns(self, db_tables=None, page_size=100, startingToken=None, connector=None):
    results = {
      'selectColumns': [{
        "dbName": 'default',
        "tableName": 'sample_07',
        "columnName": 'description',
        "columnCount": 2,
        "groupbyCol": 0,
        "selectCol": 2,
        "filterCol": 0,
        "joinCol": 0,
        "orderbyCol": 0,
        "workloadPercent": 100,
      }
    ]}

    return results


  def top_joins(self, db_tables=None, page_size=100, startingToken=None, connector=None):
    results = {'results': []}

    return results


  def top_databases(self, page_size=100, startingToken=None, connector=None):
    results = {'results': []}

    return results
