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
import numbers
import re
import time

from datetime import datetime, timedelta
from itertools import groupby

from django.utils.html import escape

from notebook.models import make_notebook
from notebook.connectors.base import get_api, OperationTimeout

from dashboard.models import Collection2, augment_response


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

    timeFilter = self._get_time_filter_query(dashboard, query)
    if timeFilter:
      filters.append(timeFilter)

    if facet:
      if facet['type'] == 'nested':
        fields_dimensions = [self._get_dimension_field(f)['name'] for f in self._get_dimension_fields(facet)]
        last_dimension_seen = False
        fields = []
        for f in reversed(facet['properties']['facets']):
          if f['aggregate']['function'] == 'count':
            if not last_dimension_seen:
              fields.insert(0, 'COUNT(*) AS Count')
              last_dimension_seen = True
            fields.insert(0, self._get_dimension_field(f)['select'])
          else:
            if not last_dimension_seen:
              fields.insert(0, self._get_aggregate_function(f))

        if not last_dimension_seen:
          fields.insert(0, 'COUNT(*) as Count')
        fields.insert(0, self._get_dimension_field(facet)['select'])

        sql = '''SELECT %(fields)s
        FROM %(database)s.%(table)s
        %(filters)s
        GROUP BY %(fields_dimensions)s
        ORDER BY %(order_by)s
        LIMIT %(limit)s''' % {
            'database': database,
            'table': table,
            'fields': ', '.join(fields),
            'fields_dimensions': ', '.join(fields_dimensions),
            'order_by': ', '.join([self._get_dimension_field(f)['order_by'] for f in self._get_dimension_fields(facet)]),
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
      fields = Collection2.get_field_list(dashboard)
      sql = "SELECT %(fields)s FROM `%(database)s`.`%(table)s`" % {
          'database': database,
          'table': table,
          'fields': ', '.join(['`%s`' % f if f != '*' else '*' for f in fields])
      }
      if filters:
        sql += ' ' + self._convert_filters_to_where(filters)
      sql += ' LIMIT %s' % LIMIT

    editor = make_notebook(
        name='Execute and watch',
        editor_type=dashboard['engine'],
        statement=sql,
        database=database,
        status='ready-execute',
        skip_historify=True
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

    return {
      'schema': {
        'fields':
            dict([(col['name'], {
              'name': str(escape(col['name'])),
              'type': str(col['type']),
              'uniqueKey': col.get('primary_key') == 'true',
              # 'dynamicBase': False,
              'indexed': False,
              'stored': True,
              'required': col.get('primary_key') == 'true'
          })
          for col in table_metadata['extended_columns']]
        )
      }
    }


  def schema_fields(self, collection):
    return {
      'fields': [f for f in self.fields(collection)['schema']['fields'].itervalues()]
    }


  def luke(self, collection):
    fields = self.schema_fields(collection)
    return {'fields': Collection2._make_luke_from_schema_fields(fields)}


  def stats(self, dataset, fields):
    database, table = self._get_database_table_names(dataset)

    # TODO: check column stats to go faster

    sql = "SELECT MIN(`%(field)s`), MAX(`%(field)s`) FROM `%(database)s`.`%(table)s`" % {
      'field': fields[0],
      'database': database,
      'table': table
    }

    result = self._sync_execute(sql, database)

    if result:
      stats = list(result['data'])
      min_value, max_value = stats[0]
      maybe_is_big_int_date = isinstance(min_value, (int, long))

      if not isinstance(min_value, numbers.Number):
        min_value = min_value.replace(' ', 'T') + 'Z'
        max_value = max_value.replace(' ', 'T') + 'Z'

      return {
        'stats': {
          'stats_fields': {
            fields[0]: {
              'min': min_value,
              'max': max_value,
              'min_date_if_bigint': datetime.fromtimestamp(min_value).strftime('%Y-%m-%dT%H:%M:%SZ') if maybe_is_big_int_date else min_value,
              'max_date_if_bigint': datetime.fromtimestamp(max_value).strftime('%Y-%m-%dT%H:%M:%SZ') if maybe_is_big_int_date else max_value,
              'maybe_is_big_int_date': maybe_is_big_int_date
            }
          }
        }
      }


  def get(self, dashboard, doc_id):
    database, table = self._get_database_table_names(dashboard['name'])
    field = self._get_field(dashboard, dashboard['idField'])
    quotes = '' if self._is_number(field['type']) else "'"

    sql = "SELECT * FROM `%(database)s`.`%(table)s` WHERE `%(idField)s` = %(quotes)s%(doc_id)s%(quotes)s" % {
      'database': database,
      'table': table,
      'idField': dashboard['idField'], # Only 1 PK currently,
      'doc_id': doc_id,
      'quotes': quotes
    }

    result = self._sync_execute(sql, database)

    if result:
      cols = [col['name'] for col in result['meta']]
      rows = list(result['data']) # No escape_rows
      doc_data = dict([(header, cell) for row in rows for header, cell in zip(cols, row)])
    else:
      doc_data = {}

    return {
      "doc": doc_data
    }

  def _sync_execute(self, sql, database):
    editor = make_notebook(
        name='Execute and watch',
        editor_type=self.engine,
        statement=sql,
        database=database,
        status='ready-execute',
        skip_historify=True
        # async=False
    )

    request = MockRequest(self.user)
    mock_notebook = {}
    snippet = {'type': self.engine}
    response = editor.execute(request)


    if 'handle' in response:
      snippet['result'] = response

      if response['handle'].get('sync'):
        result = response['result']
      else:
        timeout_sec = 20 # To move to Notebook API
        sleep_interval = 0.5
        curr = time.time()
        end = curr + timeout_sec

        api = get_api(request, snippet)

        while curr <= end:
          status = api.check_status(mock_notebook, snippet)
          if status['status'] == 'available':
            result = api.fetch_result(mock_notebook, snippet, rows=10, start_over=True)
            api.close_statement(snippet)
            break
          time.sleep(sleep_interval)
          curr = time.time()

        if curr > end:
          try:
            api.cancel_operation(snippet)
          except Exception, e:
            LOG.warning("Failed to cancel query: %s" % e)
            api.close_statement(snippet)
          raise OperationTimeout(e)

    return result

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
      field = self._get_field(collection, fq['field'])
      if fq['type'] == 'field':
        f = []
        if self._is_number(field['type']):
          sql_condition = "`%s` %s %s"
        else:
          sql_condition = "`%s` %s '%s'"
        for _filter in fq['filter']:
          exclude = '!=' if _filter['exclude'] else '='
          value = _filter['value']
          if value is not None:
            if isinstance(value, list):
              f.append(' AND '.join([sql_condition % (_f, exclude, _val) for _f, _val in zip(fq['field'], value)]))
            else:
              f.append(sql_condition % (fq['field'], exclude, value))
        clauses.append(' OR '.join(f))
      elif fq['type'] == 'range':
        if self._is_date(field['type']):
          quote = "'"
        else:
          quote = ''
          if  any([c['properties'].get('isBigIntDate') for c in collection['facets'] if c['field'] == fq['field']]):
            fq['properties'][0]['from'] = "unix_timestamp('%(from)s')" % fq['properties'][0]
            fq['properties'][0]['to'] = "unix_timestamp('%(to)s')" % fq['properties'][0]
        clauses.append("`%(field)s` >= %(quote)s%(from)s%(quote)s AND `%(field)s` < %(quote)s%(to)s%(quote)s" % {
          'field': fq['field'],
          'to': fq['properties'][0]['to'],
          'from': fq['properties'][0]['from'],
          'quote': quote
        })

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


  def _get_dimension_field(self, facet):
    # facet salary --> cast(salary / 11000 as INT) * 10 AS salary_range
    # facet salary --> salary_range
    # facets --> Count DESC   |   salary_range ASC
    if facet['properties']['canRange']:
      field_name = '%(field)s_range' % facet
      order_by = '`%(field)s_range` ASC' % facet
      if facet['properties']['isDate']:
        if facet['properties']['isBigIntDate']:
          field = 'cast(`%(field)s` AS timestamp)' % facet
        else:
          field = '`%(field)s`' % facet

        slot = self._gap_to_units(facet['properties']['gap'])

        if slot['unit'] != 'SECOND':
          select = """
            trunc(%(field)s, '%(slot)s') AS `%(field_name)s`,
            trunc(%(field)s, '%(slot)s') + interval %(slot_interval)s AS `%(field_name)s_to`""" 
        else:
          select = """
            %(field)s AS `%(field_name)s`,
            %(field)s + interval %(slot_interval)s AS `%(field_name)s_to`"""
        select = select % {
            'field': field,
            'slot': slot['sql_trunc'],
            'slot_interval': slot['sql_interval'],
            'field_name': field_name,
            'start': facet['properties']['start'],
            'end': facet['properties']['end'],
        }
      else:
        slot = facet['properties']['gap']
        select = """
        floor(floor((`%(field)s` - %(start)s) / %(slot)s) * %(slot)s) + %(start)s AS `%(field_name)s`""" % { # Beware: start might be not in sync with the UI
          'field': facet['field'],
          'slot': slot,
          'field_name': field_name,
          'start': facet['properties']['start']
        }
    else:
      field_name = '%(field)s' % facet
      select = field_name
      order_by = 'Count DESC'

    return {
      'name': '`%s`' % field_name,
      'select': select,
      'order_by': order_by
    }


  def _gap_to_units(self, gap):
    skip, coeff, unit = re.split('(\d+)', gap.strip('+')) # e.g. +1HOURS
    duration = {
      'coeff': int(coeff),
      'unit': unit.rstrip('S'),
      'sql_trunc': None,
      'sql_interval': '1 SECOND',
      'timedelta': timedelta(seconds=1) # TODO: switch to dateutil.relativedelta or create a SELECT INTERVAL + N query to get all the buckets
    }

    if duration['unit'] == 'MINUTE':
      duration['sql_trunc'] = 'MI'
      duration['sql_interval'] = '1 MINUTE'
      duration['timedelta'] = timedelta(seconds=60)
    elif duration['unit'] == 'HOUR':
      duration['sql_trunc'] = 'HH'
      duration['sql_interval'] = '1 HOUR'
      duration['timedelta'] = timedelta(seconds=60 * 60)
    elif duration['unit'] == 'DAY'  and duration['coeff'] == 1:
      duration['sql_trunc'] = 'DD'
      duration['sql_interval'] = '1 DAY'
      duration['timedelta'] = timedelta(days=1)
    elif duration['unit'] == 'WEEK':
      duration['sql_trunc'] = 'WW'
      duration['sql_interval'] = '1 WEEK'
      duration['timedelta'] = timedelta(days=7)
    elif duration['unit'] == 'MONTH' and duration['coeff'] == 1:
      duration['sql_trunc'] = 'MM'
      duration['sql_interval'] = '1 MONTH'
      duration['timedelta'] = timedelta(days=30)
    elif duration['unit'] == 'MONTH':
      duration['sql_trunc'] = 'Q'
      duration['sql_interval'] = '4 MONTH'
      duration['timedelta'] = timedelta(days=30 * 3)
    elif duration['unit'] == 'YEAR':
      duration['sql_trunc'] = 'YY'
      duration['sql_interval'] = '1 YEAR'
      duration['timedelta'] = timedelta(days=365)

    return duration

  def _get_field(self, collection, name):
    _field = [_f for _f in collection['template']['fieldsAttributes'] if _f['name'] == name]
    if _field:
      return _field[0]


  def _is_number(self, _type):
    return _type in ('int', 'long', 'bigint', 'float')


  def _is_date(self, _type):
    return _type in ('timestamp',)


  def _get_time_filter_range(self, collection, query):
    props = {}

    time_field = collection['timeFilter'].get('field')

    if time_field and (collection['timeFilter']['value'] != 'all' or collection['timeFilter']['type'] == 'fixed'):
      props = {
        'field': collection['timeFilter']['field'],
      }
      # fqs overrides main time filter
#       fq_time_ids = [fq['id'] for fq in query['fqs'] if fq['field'] == time_field]
#       if fq_time_ids:
#         return {}
#         props['time_filter_overrides'] = fq_time_ids
#         props['time_field'] = time_field

      if collection['timeFilter']['type'] == 'rolling':
        duration = self._gap_to_units(collection['timeFilter']['value'])

        props['from'] = "now() - interval %(coeff)s %(unit)s" % duration
        props['to'] = 'now()' # TODO +/- Proper Tz of user

        if any([c['properties'].get('isBigIntDate') for c in collection['facets'] if c['field'] == time_field]):
          props['from'] = 'unix_timestamp(%(from)s)' % props
          props['to'] = 'unix_timestamp(%(to)s)' % props

      elif collection['timeFilter']['type'] == 'fixed':
        props['from'] = collection['timeFilter'].get('from', 'now() - interval 7 DAY')
        props['to'] = collection['timeFilter'].get('to', 'now()')

    return props


  def _get_time_filter_query(self, collection, query):
    props = self._get_time_filter_range(collection, query)

    if props:
      return "(`%(field)s` >= %(from)s AND `%(field)s` <= %(to)s)" %  props
    else:
      return {}


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
    rows = list(result['data']) # No escape_rows

    if facet['properties']['canRange']:
      if facet['properties']['isDate']:
        slot = self._gap_to_units(facet['properties']['gap'])
        print augment_date_range_list(rows, facet['properties']['start'], facet['properties']['end'], slot['timedelta'], len(cols))
      else:
        rows = augment_number_range_list(rows, facet['properties']['start'], facet['properties']['end'], facet['properties']['gap'], len(cols))

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

    fq_fields = [_f['value'] for fq in query['fqs'] for _f in fq['filter']]

    dimension_fields = self._get_dimension_fields(facet)
    dimension = len(dimension_fields)

    # Charts
    counts = []
    if dimension == 1:
      for row in rows:
        if facet['properties']['isDate']:
          counts.append({
            "field": facet['field'],
            "total_counts": row[-1],
            "is_single_unit_gap": True,
            "from": row[0].replace(' ', 'T') + 'Z',
            "is_up": False,
            "to": row[1].replace(' ', 'T') + 'Z',
            "exclude": False,
            "selected": (row[0].replace(' ', 'T') + 'Z') in fq_fields,
            "value": row[-1]
          })
        else:
          counts.append({
             "cat": facet['field'],
             "count": row[-1],
             "exclude": False,
             "selected": row[0] in fq_fields,
             "value": row[0]
          })
    elif dimension == 2:
      for row in rows:
        value_fields = [f['field'] for f in dimension_fields] # e.g. SELECT `job`, cast(salary / 11000 as INT) * 10 AS salary_range, `gender`, COUNT(*), avg(salary)
        fq_values = [row[0], row[1]]
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

    augment_response(dashboard, query, response)

    return response


def augment_date_range_list(source_rows, start, end, delta, nb_cols):
  start_ts = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ')
  end_ts = datetime.strptime(end, '%Y-%m-%dT%H:%M:%SZ')

  current = start_ts
  indexed_rows = dict([(row[0], row) for row in source_rows])
  augmented = []

  while current <= end_ts:
    if str(current) in indexed_rows:
      augmented.append(indexed_rows[str(current)])
    else:
      augmented.append([str(current), str(current + delta)] + [0] * (nb_cols - 2))
    current += delta

  return augmented


def augment_number_range_list(source_rows, start, end, delta, nb_cols):
  current = start
  indexed_rows = dict([(row[0], row) for row in source_rows])
  augmented = []

  while current <= end:
    if current in indexed_rows:
      augmented.append(indexed_rows[current])
    else:
      augmented.append([current] + [0] * (nb_cols - 1))
    current += delta

  return augmented
