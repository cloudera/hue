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
import sys
import json

from desktop.lib.exceptions_renderable import PopupException
from django.db.models import Count
from desktop.models import SqlParserSuggestions
from metadata.optimizer.base import Api

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


class OptimizerParserClient(Api):
    # retriving the data from the database 
    def top_tables(self, workfloadId=None, database_name='default', page_size=1000, startingToken=None, connector=None):
            result_top_tables = SqlParserSuggestions.objects.filter(database=database_name).values('database' , 'table_name').annotate(usage_count=Count('*')).order_by('-usage_count').values('database' , 'table_name', 'usage_count')[:4]
      
            data = {
                'results': [{
                    "database": "default",
                    "name": "sample_07",
                    "workloadPercent": 6,
                    "columnCount": 4,
                    "total": 6
                    }, {
                    "database": "default",
                    "name": "sample_08",
                    "workloadPercent": 5,
                    "columnCount": 4,
                    "total": 3
                    }, {
                    "database": "default",
                    "name": "web_logs",
                    "workloadPercent": 4,
                    "columnCount": 1,
                    "total": 3
                    }, {
                    "database": "default",
                    "name": "customers",
                    "workloadPercent": 3,
                    "columnCount": 44,
                    "total": 1
                    }
                ]
            }

            i=0
            for d in data['results']:
                d['database'] = result_top_tables[i]['database']
                d['name'] = result_top_tables[i]['table_name']
                i = i+1

            return data
    
    def top_columns(self, db_tables=None, page_size=100, startingToken=None, connector=None, database_name='default'):
      db_tables = ' '.join(map(str, db_tables))
      db_table_only = db_tables.split(".")[1]
      result_top_columns = SqlParserSuggestions.objects.filter(database=database_name, table_name = db_table_only).values('database', 'table_name', 'column_name').annotate(usage_count=Count('*')).order_by('-usage_count')[:4]

      results = { 
        'selectColumns': [{
            "dbName": 'default',
            "tableName": 'sample_07',
            "columnName": 'description',
            "columnCount": 6,
            "groupbyCol": 0,
            "selectCol": 6,
            "filterCol": 0,
            "joinCol": 0,
            "orderbyCol": 0,
            "workloadPercent": 100,
          }, {
            "dbName": 'default',
            "tableName": 'sample_07',
            "columnName": 'description',
            "columnCount": 5,
            "groupbyCol": 0,
            "selectCol": 5,
            "filterCol": 0,
            "joinCol": 0,
            "orderbyCol": 0,
            "workloadPercent": 100,
          }, {
          "dbName": 'default',
            "tableName": 'sample_07',
            "columnName": 'description',
            "columnCount": 4,
            "groupbyCol": 0,
            "selectCol": 4,
            "filterCol": 0,
            "joinCol": 0,
            "orderbyCol": 0,
            "workloadPercent": 100,
          }, {
            "dbName": 'default',
            "tableName": 'sample_07',
            "columnName": 'description',
            "columnCount": 3,
            "groupbyCol": 0,
            "selectCol": 4,
            "filterCol": 0,
            "joinCol": 0,
            "orderbyCol": 0,
            "workloadPercent": 100,
          }
        ]
    }
        
      j=0
      for r in results['selectColumns']:
          r['dbName'] = result_top_columns[j]['database']
          r['tableName'] = result_top_columns[j]['table_name']
          r['columnName'] = result_top_columns[j]['column_name']
          j = j+1

      return results
    

    def top_joins(self, db_tables=None, connector=None, database_name='default'):
      db_tables = ' '.join(map(str, db_tables))
      db_table_only = db_tables.split(".")[1]
      result_top_joins = SqlParserSuggestions.objects.filter(database=database_name, table_name=db_table_only).values('database', 'table_name', 'table_name_1', 'column_name', 'column_name_1').annotate(usage_count=Count('*')).order_by('-usage_count')[:2]
      print('result_top_joins: ', result_top_joins)

      key = {
          'results': [{
            "totalTableCount": 10,
            "totalQueryCount": 50, 
            "joinType": 'JOIN',
            "tables": ['sample_07', 'sample_08'],
            "joinCols": [{ 'columns': ['code', 'code'] }],
            "relativePopularity": 15,
            "popularity": 250
          },{
            "totalTableCount": 10,
            "totalQueryCount": 10, 
            "joinType": 'JOIN',
            "tables": ['sample_07', 't1'],
            "joinCols": [{ 'columns': ['code', 't11'] }],
            "relativePopularity": 15,
            "popularity": 250
          }
        ]
      }
      
      j=0
      for r in key['results']:
        r['totalQueryCount'] = result_top_joins[j]['usage_count']
        r['tables'][0] = result_top_joins[j]['table_name']
        r['tables'][1] = result_top_joins[j]['table_name_1']
        r['joinCols'][0]['columns'][0] = result_top_joins[j]['column_name']
        r['joinCols'][0]['columns'][1] = result_top_joins[j]['column_name_1']
        j=j+1
              
      return key