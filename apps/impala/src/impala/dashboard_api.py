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

from django.utils.html import escape

from beeswax.server.dbms import get_query_server_config
from beeswax.design import hql_query
from beeswax.server import dbms
from search.models import Collection2


LOG = logging.getLogger(__name__)


# To Split in Impala, DBMS..
# To inherit from DashboardApi
class SQLApi():

  def __init__(self, user):
    self.user = user

  def query(self, dashboard, query, facet=None):
    database, table = self._get_database_table_names(dashboard['name'])
    filters = []

    if query and query['qs'] == [{'q': '_root_:*'}]:
      return {'response': {'numFound': 0}}

    if facet:
      fields = [facet['field']] + [f['field'] for f in facet['properties']['facets']]
      fields = ['`%s`' % f for f in fields]

      hql = '''SELECT %(fields)s, COUNT(*)
      FROM %(database)s.%(table)s
      WHERE %(filters)s
      GROUP BY %(fields)s
      ORDER BY COUNT(*) DESC
      LIMIT %(limit)s''' % {
          'database': database,
          'table': table,
          'fields': ', '.join(fields),
          'filters': ' AND '.join(['%s IS NOT NULL' % f for f in fields]),
          'limit': 100
      }
    else:
      fields =  '*'
      hql = "SELECT %(fields)s FROM `%(database)s`.`%(table)s`" % {
          'database': database,
          'table': table,
          'fields': fields
      }
      if filters:
        hql += ' WHERE ' + filters
      hql += ' LIMIT 100'

#     sample = get_api(request, {'type': 'hive'}).get_sample_data({'type': 'hive'}, database=file_format['databaseName'], table=file_format['tableName'])
#     db = dbms.get(request.user)
#     table_metadata = db.get_table(database=file_format['databaseName'], table_name=file_format['tableName'])
#
#     format_ = {
#         "sample": sample['rows'][:4],
#         "columns": [
#             Field(col.name, HiveFormat.FIELD_TYPE_TRANSLATE.get(col.type, 'string')).to_dict()
#             for col in table_metadata.cols
#         ]
#     }

    query_server = get_query_server_config(name='impala') # To move to notebook API
    db = dbms.get(self.user, query_server=query_server)

    query = hql_query(hql)
    handle = db.execute_and_wait(query, timeout_sec=35.0)

    if handle:
      result = db.fetch(handle, rows=100)
      db.close(handle)

    if facet:
      return self._convert_impala_facet(result, facet)
    else:
      return self._convert_impala_results(result, dashboard, query)

  def datasets(self,  show_all=False):
    return ['sample_07', 'web_logs']

  def fields(self, dashboard):
    database, table = self._get_database_table_names(dashboard)

    db = dbms.get(self.user)
    table_metadata = db.get_table(database=database, table_name=table)
    return [{
        'name': str(escape(col.name)),
        'type': str(col.type),
        'isId': False, # TODO Kudu
        'isDynamic': False,
        'indexed': False,
        'stored': True
        # isNested
      } for col in table_metadata.cols
    ]

  def schema_fields(self, collection):
    return {'fields': self.fields(collection)}

  def luke(self, collection):
    fields = self.schema_fields(collection)
    return {'fields': Collection2._make_luke_from_schema_fields(fields)}

  def _get_database_table_names(self, name):
    if '.' in name:
      database, table_name = name.split('.', 1)
    else:
      database = 'default'
      table_name = name

    return database, table_name

  def _convert_impala_facet(self, result, facet):
    response = json.loads('''{
   "field":"cat",
   "fieldsAttributes":[],
   "response":{
      "response":{
         "start":0,
         "numFound":16
      }
   },
   "docs":[],
   "counts":[],
   "dimension":1,
   "type":"nested",
   "extraSeries":[
   ],
   "label":"cat"
}''')

    response['id'] = facet['id']

    cols = list(result.cols())
    rows = list(result.rows())

    response['fieldsAttributes'] = [{
         "sort":{
            "direction": None
         },
         "isDynamic": False,
         "type": column.type,
         "name": column.name
      } for column in result.data_table.cols()]


    response['docs'] = [dict((header, cell) for header, cell in zip(cols, row)) for row in rows]

    counts = []
    for row in rows:
      counts.append({
         "count": row[1],
         "exclude": True,
         "selected": False,
         "value": row[0]
      })
    response['counts'] = counts

    return {'normalized_facets': [response]}

  def _convert_impala_results(self, result, dashboard, query):
    cols = list(result.cols())

    docs = []
    for row in result.rows():
      docs.append(dict((header, cell) for header, cell in zip(cols, row)))

    response = json.loads('''{
   "highlighting":{
      "F8V7067-APL-KIT":{

      },
      "USD":{

      },
      "NOK":{

      },
      "GBP":{

      },
      "EUR":{

      }
   },
   "normalized_facets":[

   ],
   "responseHeader":{
      "status":0,
      "QTime":0,
      "params":{
         "rows":"5",
         "hl.fragsize":"1000",
         "hl.snippets":"5",
         "doAs":"romain",
         "q":"*:*",
         "start":"0",
         "wt":"json",
         "user.name":"hue",
         "hl":"true",
         "hl.fl":"*",
         "fl":"*"
      }
   },
   "response":{
      "start":0,
      "numFound":32,
      "docs":[]
   }
}''')

    response['response']['docs'] = docs
    response['response']['numFound'] = len(docs)

    return response
