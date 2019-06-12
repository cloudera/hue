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
from notebook.connectors.base import get_api, OperationTimeout, Notebook

from dashboard.dashboard_api import DashboardApi
from dashboard.models import Collection2, augment_response
from desktop.models import Document2


LOG = logging.getLogger(__name__)

LIMIT = 100


class MockRequest():
  def __init__(self, user, cluster):
    self.user = user
    self.POST = {'cluster': cluster}


class SQLDashboardApi(DashboardApi):

  def __init__(self, user, engine, source='data', cluster='""'):
    super(SQLDashboardApi, self).__init__(user, cluster)
    self.engine = engine
    self.source = source
    self.async = engine == 'hive' or engine == 'impala'

  def query(self, dashboard, query, facet=None):
    if query['qs'] == [{'q': '_root_:*'}]:
      return {'response': {'numFound': 0}}

    filters = [q['q'] for q in query['qs'] if q['q']]
    filters.extend(self._get_fq(dashboard, query, facet))
    result_properties = {}

    timeFilter = self._get_time_filter_query(dashboard, query)
    if timeFilter:
      filters.append(timeFilter)

    if self.source == 'query':
      sql_from = '(%(query)s) t' % {'query': self._get_query(dashboard['name'])}
      database, table = '', ''
    else:
      database, table = self._get_database_table_names(dashboard['name'])
      sql_from = '`%(database)s`.`%(table)s`' % {
        'database': database,
        'table': table
      }

    if facet and facet['properties']['facets']:
      for i, _facet in enumerate(facet['properties']['facets']):
        _facet['position'] = i

      if facet['type'] == 'nested':
        fields_dimensions = [self._get_dimension_field(f)['name'] for f in self._get_dimension_fields(facet)]
        last_dimension_seen = False
        fields = []

        for f in reversed(facet['properties']['facets']):
          if f['aggregate']['function'] == 'count':
            if not last_dimension_seen:
              fields.insert(0, 'COUNT(*) AS %(field)s_%(position)s' % f)
              last_dimension_seen = True
            fields.insert(0, self._get_dimension_field(f)['name' if last_dimension_seen else 'select'])
          else:
            if not last_dimension_seen:
              fields.insert(0, self._get_aggregate_function(f) + 'AS %(field)s_%(position)s' % f)

        has_facet_mincount_greater_than_one = [f for f in facet['properties']['facets'] if f['mincount'] > 1]
        if has_facet_mincount_greater_than_one and self._supports_count_over():
          mincount_fields_name = []
          mincount_fields_operation = []
          mincount_where = []
          for f in facet['properties']['facets']:
            mincount_fields_name.append(f['field'])
            mincount_field_name = 'count__' + '_'.join(mincount_fields_name)
            mincount_fields_operation.append('COUNT(*) OVER (PARTITION BY %s) AS %s' % (', '.join(mincount_fields_name), mincount_field_name) )
            mincount_where.append('%s >= %s' % (mincount_field_name, str(f['mincount'])))
          sql_from = '''(SELECT * FROM (SELECT *, %(fields)s
          FROM %(sql_from)s) default
          WHERE %(where)s) default''' % {
            'fields': ', '.join(mincount_fields_operation),
            'sql_from': sql_from,
            'where': ' AND '.join(mincount_where)
          }

        order_by = ', '.join([self._get_dimension_field(f)['order_by'] for f in reversed(facet['properties']['facets']) if f['sort'] != 'default'])

        sql = '''SELECT %(fields)s
        FROM %(sql_from)s
        %(filters)s
        GROUP BY %(fields_dimensions)s
        %(order_by)s
        LIMIT %(limit)s''' % {
            'sql_from': sql_from,
            'fields': ', '.join(fields),
            'fields_dimensions': ', '.join(fields_dimensions),
            'order_by': 'ORDER BY %s' % order_by if order_by else '',
            'filters': self._convert_filters_to_where(filters),
            'limit': LIMIT
        }
      elif facet['type'] == 'function': # 1 dim only now
        aggregate_function = facet['properties']['facets'][0]['aggregate']['function']
        if (aggregate_function == 'percentile' or aggregate_function == 'median') and not self._supports_percentile() and self._supports_cume_dist():
          sql_from = '''
          (SELECT *
          FROM
          (
            SELECT %(field)s, cume_dist() OVER (ORDER BY %(field)s) * 100 AS cume_dist__%(field)s
            FROM %(sql_from)s
          ) DEFAULT
          WHERE cume_dist__%(field)s >= %(value)s) DEFAULT
          ''' % {
            'field': facet['properties']['facets'][0]['field'],
            'value': facet['properties']['facets'][0]['aggregate']['percentile'] if aggregate_function == 'percentile' else 50,
            'sql_from': sql_from,
          }

        sql = '''SELECT %(fields)s
        FROM %(sql_from)s
        %(filters)s''' % {
            'sql_from': sql_from,
            'fields': self._get_aggregate_function(facet['properties']['facets'][0]),
            'filters': self._convert_filters_to_where(filters),
        }
      elif facet['type'] == 'statement':
        doc = Document2.objects.get_by_uuid(user=self.user, uuid=facet['properties']['statementUuid'], perm_type='read')
        snippets = doc.data_dict.get('snippets', [])
        sql = snippets[0].get('statement', '')
        result_properties = facet['properties']['result']
    else:
      fields = Collection2.get_field_list(dashboard)
      order_by = ', '.join(['`%s` %s' % (f['name'], f['sort']['direction']) for f in dashboard['template']['fieldsAttributes'] if f['sort']['direction'] and f['name'] in fields])
      sql = '''
      SELECT %(fields)s
      FROM %(sql_from)s
      %(filters)s
      %(order_by)s
      %(limit)s''' % {
          'sql_from': sql_from,
          'fields': ', '.join(['`%s` as `%s`' % (f, f) if f != '*' else '*' for f in fields]),
          'filters': self._convert_filters_to_where(filters) if filters else '',
          'order_by': 'ORDER BY %s' % order_by if order_by else '',
          'limit': 'LIMIT %s' % dashboard['template']['rows'] or LIMIT
      }

    editor = make_notebook(
        name='Execute and watch',
        editor_type=dashboard['engine'],
        statement=sql,
        database=database,
        status='ready-execute',
        skip_historify=True,
        result_properties=result_properties
    )

    response = editor.execute(MockRequest(self.user, self.cluster))

    if 'handle' in response and response['handle'].get('sync'):
      response['result'] = self._convert_result(response['result'], dashboard, facet, query)

    return response

  def _supports_count_over(self):
    return True

  def fetch_result(self, dashboard, query, facet):
    notebook = {}
    snippet = facet['queryResult']

    start_over = True # TODO

    result = get_api(MockRequest(self.user, self.cluster), snippet).fetch_result(
        notebook,
        snippet,
        dashboard['template']['rows'],
        start_over=start_over
    )

    return self._convert_result(result, dashboard, facet, query)


  # This method currently behaves more like a static method
  def datasets(self, show_all=False):
    snippet = {'type': self.engine}

    # Ideally from left assist at some point instead
    databases = get_api(MockRequest(self.user, self.cluster), snippet).autocomplete(snippet)['databases']
    database = databases and 'default' not in databases and sorted(databases)[0] or 'default'

    return [
      database + '.' + table['name']
      for table in get_api(MockRequest(self.user, self.cluster), snippet).autocomplete(snippet, database=database)['tables_meta']
    ]


  # This method currently behaves more like a static method
  def fields(self, name):
    snippet = {'type': self.engine}

    if self.source == 'query':
      snippet['query'] = self._get_query(name)
      database, table = '', ''
    else:
      database, table = self._get_database_table_names(name)

    table_metadata = get_api(MockRequest(self.user, self.cluster), snippet).autocomplete(snippet, database, table)

    return {
      'schema': {
        'fields':
            dict([(col['name'], {
              'name': str(escape(col['name'])),
              'type': str(col['type']).lower(),
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


  def stats(self, dataset, fields, query, facet):
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

      if not isinstance(min_value, numbers.Number):
        min_value = min_value.replace(' ', 'T') + 'Z'
        max_value = max_value.replace(' ', 'T') + 'Z'

      return {
        'stats': {
          'stats_fields': {
            fields[0]: {
              'min': min_value,
              'max': max_value,
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

    request = MockRequest(self.user, self.cluster)
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
            api.close_statement(mock_notebook, snippet)
            break
          time.sleep(sleep_interval)
          curr = time.time()

        if curr > end:
          try:
            api.cancel_operation(snippet)
          except Exception, e:
            LOG.warning("Failed to cancel query: %s" % e)
            api.close_statement(mock_notebook, snippet)
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
    return [f for f in facet['properties']['facets'] if f['aggregate']['function'] == 'count']


  def _convert_filters_to_where(self, filters, alias=None):
    if alias:
      filters = [alias + '.' + filter for filter in filters]
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
              field_conditions = [self._get_field_condition_formatting(collection, facet, _f) % (_f, exclude, _val) for _f, _val in zip(fq['field'], value)]
              field_conditions = [condition for condition in field_conditions if condition]
              if field_conditions:
                f.append(' AND '.join(field_conditions))
            else:
              sql_condition = self._get_field_condition_formatting(collection, facet, fq['field'])
              if sql_condition:
                f.append(sql_condition % (fq['field'], exclude, value))
        if f:
          clauses.append(' OR '.join(f))
      elif fq['type'] == 'range':
        field = self._get_field(collection, fq['field'], facet=facet)
        if field:
          if self._is_date(field['type']):
            quote = "'"
          else:
            quote = ''
          clauses.append("`%(field)s` >= %(quote)s%(from)s%(quote)s AND `%(field)s` < %(quote)s%(to)s%(quote)s" % {
            'field': fq['field'],
            'to': fq['properties'][0]['to'],
            'from': fq['properties'][0]['from'],
            'quote': quote
          })
      elif fq['type'] == 'map':
        for direction in ['lat', 'lon']:
          field = self._get_field(collection, fq[direction], facet=facet)
          if field:
            if self._is_number(field['type']):
              quote = ''
            else:
              quote = "'"
            min_direction = min(fq['properties'][direction+'_sw'], fq['properties'][direction+'_ne'])
            max_direction = max(fq['properties'][direction+'_sw'], fq['properties'][direction+'_ne'])
            clauses.append("`%(field)s` >= %(quote)s%(from)s%(quote)s AND `%(field)s` < %(quote)s%(to)s%(quote)s" % {
              'field': fq[direction],
              'to': max_direction,
              'from': min_direction,
              'quote': quote
            })
    return clauses

  def _get_field_condition_formatting(self, table, facet, field_name):
    field = self._get_field(table, field_name, facet=facet)
    if field:
      return "`%s` %s %s" if self._is_number(field['type']) else "`%s` %s '%s'"
    else:
      return ''


  @classmethod
  def _get_aggregate_function(cls, facet):
    fields = []

    if facet['aggregate']['function'] == 'median':
      if cls._supports_median():
        facet['aggregate']['function'] = 'MEDIAN'
        fields.append(facet['field'])
      elif cls._supports_percentile():
        facet['aggregate']['function'] = 'PERCENTILE'
        fields.append('%s, 0.5' % facet['field'])
      elif cls._supports_cume_dist():
        facet['aggregate']['function'] = 'MIN'
        fields.append(facet['field'])
      else:
        fields.append(facet['field'])
    elif facet['aggregate']['function'] == 'unique':
      facet['aggregate']['function'] = 'COUNT'
      fields.append('distinct `%(field)s`' % facet)
    elif facet['aggregate']['function'] == 'percentile':
      if cls._supports_percentile():
        fields.append('%s, %s' % (facet['field'], cls._zero_to_one(float(facet['aggregate']['percentile']))))
      elif cls._supports_cume_dist():
        facet['aggregate']['function'] = 'MIN'
        fields.append(facet['field'])
      else:
        fields.append(facet['field'])
    else:
      fields.append(facet['field'])

    return '%s(%s) ' % (facet['aggregate']['function'], ','.join(fields))

  @classmethod
  def _zero_to_one(cls, value):
    if value < 0:
      return cls._zero_to_one(-1 * value)
    elif value <= 1:
      return value
    else:
      return value / 100

  @classmethod
  def _supports_cume_dist(self):
    return True

  @classmethod
  def _supports_median(self):
    return True

  @classmethod
  def _supports_ntile(self):
    return True

  @classmethod
  def _supports_percentile(self):
    return True

  def _get_dimension_field(self, facet):
    # facet salary --> cast(salary / 11000 as INT) * 10 AS salary_range_1
    # facet salary --> salary_range_2
    # facets --> Count DESC / salary_range_3 ASC

    if facet['canRange']:
      field_name = '%(field)s_range' % facet
      order_by = '`%(field)s_range_%(position)s` %(sort)s' % facet
      if facet['isDate']:
        field = '`%(field)s`' % facet

        slot = self._gap_to_units(facet['gap'])

        if slot['unit'] != 'SECOND':
          select = """
            trunc(%(field)s, '%(slot)s') AS `%(field_name)s_%(position)s`,
            trunc(%(field)s, '%(slot)s') + interval %(slot_interval)s AS `%(field_name)s_to_%(position)s`"""
        else:
          select = """
            %(field)s AS `%(field_name)s_%(position)s`,
            %(field)s + interval %(slot_interval)s AS `%(field_name)s_to_%(position)s`"""
        select = select % {
            'field': field,
            'slot': slot['sql_trunc'],
            'slot_interval': slot['sql_interval'],
            'field_name': field_name,
            'start': facet['start'],
            'end': facet['end'],
            'position': facet['position']
        }
      else:
        slot = facet['gap']
        select = """
        floor(floor((`%(field)s` - %(start)s) / %(slot)s) * %(slot)s) + %(start)s AS `%(field_name)s_%(position)s`""" % { # Beware: start might be not in sync with the UI
          'field': facet['field'],
          'slot': slot,
          'field_name': field_name,
          'start': facet['start'],
          'position': facet['position']
        }
    else:
      field_name = '%(field)s' % facet
      select = '%(field)s AS %(field)s_%(position)s' % facet
      order_by = '%(field)s_%(position)s %(sort)s' % facet

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
    elif duration['unit'] == 'DAY' and duration['coeff'] == 1:
      duration['sql_trunc'] = 'DD'
      duration['sql_interval'] = '1 DAY'
      duration['timedelta'] = timedelta(days=1)
    elif duration['unit'] == 'WEEK' or (duration['unit'] == 'DAY' and duration['coeff'] == 7):
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

    if not duration['sql_trunc']:
      LOG.warn('Duration %s not converted to SQL buckets.' % duration)

    return duration

  def _get_field(self, collection, name, facet=None):
    fields = collection['template']['fieldsAttributes'] or (facet and facet['template']['fieldsAttributes'])
    _field = [_f for _f in fields if _f['name'] == name]
    if _field:
      return _field[0]


  def _is_number(self, _type):
    return _type in ('int', 'long', 'bigint', 'float', 'INT_TYPE', 'DECIMAL_TYPE', 'DOUBLE_TYPE', 'FLOAT_TYPE', 'SMALLINT_TYPE', 'TINYINT_TYPE', 'BIGINT_TYPE')


  def _is_date(self, _type):
    return _type in ('timestamp','TIMESTAMP_TYPE')


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


  def _get_query(self, name):
    nb_doc = Document2.objects.document(user=self.user, doc_id=name)
    notebook = Notebook(document=nb_doc).get_data()
    snippet = notebook['snippets'][0]
    return snippet['statement'].strip(';')


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
    nested_facet = facet['properties']['facets'][0]

    response['field'] = nested_facet['field']
    response['label'] = nested_facet['field']

    cols = [col['name'] for col in result['meta']]
    rows = list(result['data']) # No escape_rows

    if nested_facet['canRange']:
      if nested_facet['isDate']:
        slot = self._gap_to_units(nested_facet['gap'])
        print augment_date_range_list(rows, nested_facet['start'], nested_facet['end'], slot['timedelta'], len(cols))
      else:
        rows = augment_number_range_list(rows, nested_facet['start'], nested_facet['end'], nested_facet['gap'], len(cols))

    response['fieldsAttributes'] = [{
         "sort": {
            "direction": nested_facet['sort']
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
        if nested_facet['isDate']:
          counts.append({
            "field": nested_facet['field'],
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
             "cat": nested_facet['field'],
             "count": row[-1],
             "exclude": False,
             "selected": row[0] in fq_fields,
             "value": row[0]
          })
    else: # Nested facets can have dimension > 2
      for row in rows:
        value_fields = [f['field'] for f in dimension_fields]  # e.g. SELECT `job`, cast(salary / 11000 as INT) * 10 AS salary_range, `gender`, COUNT(*), avg(salary)
        fq_values = row[:dimension]
        counts.append({
          "count": row[-1],
          "fq_values": fq_values,
          "selected": fq_values in fq_fields,
          "fq_fields": value_fields,
          "value": row[1] if dimension == 2 else ', '.join(str(x) for x in fq_values),
          "cat": row[0],
          "exclude": False
        })

    response['dimension'] = dimension
    response['counts'] = counts
    response['response']['response']['numFound'] = len(counts)

    return {'normalized_facets': [response]}


  def _convert_notebook_function_facet(self, result, facet, query):
    rows = list(result['data'])

    response = {"query": facet['id'], 'counts': {'percentage': 0, 'value': rows[0][0]}, "type": "function", "id": facet['id'], "label": facet['id']}

    return {'normalized_facets': [response]}


  def _convert_notebook_results(self, result, dashboard, query):
    cols = [col['name'] if self.source == 'data' else re.sub('^t\.', '', col['name']) for col in result['meta']]

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
