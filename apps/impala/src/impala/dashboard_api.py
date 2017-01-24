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

from itertools import groupby

from django.utils.html import escape

from beeswax.server import dbms
from notebook.models import make_notebook
from notebook.connectors.base import get_api
from search.models import Collection2


LOG = logging.getLogger(__name__)

LIMIT = 100


class MockRequest():
  def __init__(self, user):
    self.user = user


# To Split in Impala, DBMS..
# To inherit from DashboardApi
class SQLApi():

  def __init__(self, user, engine):
    self.user = user
    self.engine = engine
    self.async = engine == 'hive' or engine == 'impala'

  def query(self, dashboard, query, facet=None):
    database, table = self._get_database_table_names(dashboard['name'])

    if query['qs'] == [{'q': '_root_:*'}]:
      return {'response': {'numFound': 0}}

    filters = [q['q'] for q in query['qs'] if q['q']]
    filters.extend(self._get_fq(dashboard, query, facet))

    if facet:
      if facet['type'] == 'nested':
        fields_dimensions = ['`%(field)s`' % f for f in self._get_dimension_fields(facet)]
        last_dimension_seen = False
        fields = []
        for f in reversed(facet['properties']['facets']):
          if f['aggregate']['function'] == 'count':
            if not last_dimension_seen:
              fields.insert(0, 'COUNT(*)')
              last_dimension_seen = True
            fields.insert(0, '`%(field)s`' % f)
          else:
            if not last_dimension_seen:
              fields.insert(0, self._get_aggregate_function(f))

        if not last_dimension_seen:
          fields.insert(0, 'COUNT(*)')
        fields.insert(0, '`%(field)s`' % facet)

        sql = '''SELECT %(fields)s
        FROM %(database)s.%(table)s
        %(filters)s
        GROUP BY %(fields_dimensions)s
        ORDER BY COUNT(*) DESC
        LIMIT %(limit)s''' % {
            'database': database,
            'table': table,
            'fields': ', '.join(fields),
            'fields_dimensions': ', '.join(fields_dimensions),
            'filters': self._convert_filters_to_where(filters),
            'limit': LIMIT
        }
      elif facet['type'] == 'function': # 1 dim only now
        sql = '''SELECT %(fields)s
        FROM %(database)s.%(table)s
        %(filters)s''' % {
            'database': database,
            'table': table,
            'fields': self._get_aggregate_function(facet),
            'filters': self._convert_filters_to_where(filters),
        }
    else:
      fields =  '*'
      sql = "SELECT %(fields)s FROM `%(database)s`.`%(table)s`" % {
          'database': database,
          'table': table,
          'fields': fields
      }
      if filters:
        sql += ' ' + self._convert_filters_to_where(filters)
      sql += ' LIMIT %s' % LIMIT


    editor = make_notebook(
        name='Execute and watch',
        editor_type=dashboard['engine'],
        statement=sql,
        database=database,
        status='ready-execute'
        # historify=False
    )

    response = editor.execute(MockRequest(self.user))

    if 'handle' in response and response['handle'].get('sync'):
      response['result'] = self._convert_result(response['result'], dashboard, facet, query)

    return response


  def fetch_result(self, dashboard, query, facet):
    notebook = {}
    snippet = facet['queryResult']

    start_over = True # TODO

    result = get_api(MockRequest(self.user), snippet).fetch_result(
        notebook,
        snippet,
        dashboard['template']['rows'],
        start_over=start_over
    )

    return self._convert_result(result, dashboard, facet, query)


  def datasets(self, show_all=False):
    # Implemented via Hive chooser
    return []


  def fields(self, dashboard):
    database, table = self._get_database_table_names(dashboard)
    snippet = {'type': self.engine}

    table_metadata = get_api(MockRequest(self.user), snippet).autocomplete(snippet, database, table)

    return [{
        'name': str(escape(col['name'])),
        'type': str(col['type']),
        'isId': False, # TODO Kudu
        'isDynamic': False,
        'indexed': False,
        'stored': True
        # isNested
      } for col in table_metadata['extended_columns']
    ]


  def schema_fields(self, collection):
    return {'fields': self.fields(collection)}


  def luke(self, collection):
    fields = self.schema_fields(collection)
    return {'fields': Collection2._make_luke_from_schema_fields(fields)}


  def _convert_result(self, result, dashboard, facet, query):
    if not facet.get('type'):
      return self._convert_notebook_results(result, dashboard, query)
    elif facet['type'] == 'function':
      return self._convert_notebook_function_facet(result, facet, query)
    else:
      return self._convert_notebook_facet(result, facet, query)


  def _get_dimension_fields(self, facet):
    return [facet] + [f for f in facet['properties']['facets'] if f['aggregate']['function'] == 'count']


  def _convert_filters_to_where(self, filters):
    return ('WHERE ' + ' AND '.join(filters)) if filters else ''


  def _get_fq(self, collection, query, facet=None):
    clauses = []

    # Facets should not filter themselves
    fqs = [fq for fq in query['fqs'] if not facet or facet['id'] != fq['id']]

    # Merge facets queries on same fields
    grouped_fqs = groupby(fqs, lambda x: (x['type'], x['field']))
    merged_fqs = []
    for key, group in grouped_fqs:
      field_fq = next(group)
      for fq in group:
        for f in fq['filter']:
            field_fq['filter'].append(f)
      merged_fqs.append(field_fq)

    for fq in merged_fqs:
      if fq['type'] == 'field':
        f = []
        for _filter in fq['filter']:
          exclude = '!=' if _filter['exclude'] else '='
          value = _filter['value']
          if value is not None:
            if isinstance(value, list):
              f.append(' AND '.join(["`%s` %s '%s'" % (_f, exclude, _val) for _f, _val in zip(fq['field'], value)]))
            else:
              f.append("%s %s '%s'" % (fq['field'], exclude, value))
        clauses.append(' OR '.join(f))

    return clauses

  @classmethod
  def _get_aggregate_function(cls, facet):
    if 'properties' in facet:
      f = facet['properties']['aggregate'] # Level 1 facet
    else:
      f = facet['aggregate']

    if not f['ops']:
      f['ops'] = [{'function': 'field', 'value': facet['field'], 'ops': []}]

    return cls.__get_aggregate_function(f)

  @classmethod
  def __get_aggregate_function(cls, f):
    if f['function'] == 'field':
      return f['value']
    else:
      fields = []
      for _f in f['ops']:
        fields.append(cls.__get_aggregate_function(_f))
      if f['function'] == 'median':
        f['function'] = 'percentile'
        fields.append('50')
      elif f['function'] == 'unique':
        f['function'] = 'count'
        fields[0] = 'distinct `%s`' % fields[0]
      elif f['function'] == 'percentiles':
        fields.extend(map(lambda a: str(a), [_p['value'] for _p in f['percentiles']]))
      return '%s(%s)' % (f['function'], ','.join(fields))

  def _get_database_table_names(self, name):
    if '.' in name:
      database, table_name = name.split('.', 1)
    else:
      database = 'default'
      table_name = name

    return database, table_name

  def _convert_notebook_facet(self, result, facet, query):
    response = json.loads('''{
   "fieldsAttributes":[],
   "response":{
      "response":{
         "start":0,
         "numFound":0
      }
   },
   "docs":[],
   "counts":[],
   "dimension":1,
   "type":"nested",
   "extraSeries":[
   ]
}''')

    response['id'] = facet['id']
    response['field'] = facet['field']
    response['label'] = facet['field']

    cols = [col['name'] for col in result['meta']]
    rows = list(result['data']) # escape_rows

    response['fieldsAttributes'] = [{
         "sort":{
            "direction": None
         },
         "isDynamic": False,
         "type": column['type'],
         "name": column['name']
      } for column in result['meta']]

    # Grid
    response['docs'] = [dict((header, cell) for header, cell in zip(cols, row)) for row in rows]

    fq_fields = [_f['value'] for fq in query['fqs'] for _f in fq['filter']] # type == 'field

    dimension_fields = self._get_dimension_fields(facet)
    dimension = len(dimension_fields)

    # Charts
    counts = []
    if dimension == 1:
      for row in rows:
        counts.append({
           "cat": facet['field'],
           "count": row[-1],
           "exclude": False,
           "selected": row[0] in fq_fields,
           "value": row[0]
        })
    elif dimension == 2:
      for row in rows:
        value_fields = [f['field'] for f in dimension_fields]
        fq_values = [row[0], row[1]]
        # SELECT `job`, `gender`, COUNT(*), avg(salary)
        # -->
        # SELECT `job`, avg(salary), `gender`, COUNT(*)
        counts.append({
            "count": row[-1],
            "fq_values": fq_values,
            "selected": fq_values in fq_fields,
            "fq_fields": value_fields,
            "value": row[1],
            "cat": row[0],
            "exclude": False
        })

    response['dimension'] = dimension
    response['counts'] = counts
    response['response']['response']['numFound'] = len(counts)

    return {'normalized_facets': [response]}


  def _convert_notebook_function_facet(self, result, facet, query):
    rows = list(result['data'])

    response = {"query": facet['id'], "counts": rows[0][0], "type": "function", "id": facet['id'], "label": facet['id']}

    return {'normalized_facets': [response]}


  def _convert_notebook_results(self, result, dashboard, query):
    cols = [col['name'] for col in result['meta']]

    docs = []
    for row in result['data']:
      docs.append(dict((header, cell) for header, cell in zip(cols, row)))

    response = json.loads('''{
   "highlighting":{
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
