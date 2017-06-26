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

import collections
import itertools
import json
import logging
import numbers
import re

from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.utils.translation import ugettext as _

from desktop.lib.i18n import smart_unicode, smart_str
from desktop.models import get_data_link

from dashboard.dashboard_api import get_engine


LOG = logging.getLogger(__name__)


class Collection2(object):

  def __init__(self, user, name='Default', data=None, document=None, engine='solr'):
    self.document = document

    if document is not None:
      self.data = json.loads(document.data)
    elif data is not None:
      self.data = json.loads(data)
    else:
      self.data = {
          'collection': self.get_default(user, name, engine),
          'layout': []
      }

  def get_json(self, user):
    return json.dumps(self.get_props(user))

  def get_props(self, user):
    props = self.data

    if self.document is not None:
      props['collection']['id'] = self.document.id
      props['collection']['label'] = self.document.name
      props['collection']['description'] = self.document.description

    # For backward compatibility
    if 'rows' not in props['collection']['template']:
      props['collection']['template']['rows'] = 25
    if 'showGrid' not in props['collection']['template']:
      props['collection']['template']['showGrid'] = True
    if 'showChart' not in props['collection']['template']:
      props['collection']['template']['showChart'] = False
    if 'chartSettings' not in props['collection']['template']:
      props['collection']['template']['chartSettings'] = {
        'chartType': 'bars',
        'chartSorting': 'none',
        'chartScatterGroup': None,
        'chartScatterSize': None,
        'chartScope': 'world',
        'chartX': None,
        'chartYSingle': None,
        'chartYMulti': [],
        'chartData': [],
        'chartMapLabel': None,
      }
    if 'enabled' not in props['collection']:
      props['collection']['enabled'] = True
    if 'engine' not in props['collection']:
      props['collection']['engine'] = 'solr'
    if 'leafletmap' not in props['collection']['template']:
      props['collection']['template']['leafletmap'] = {'latitudeField': None, 'longitudeField': None, 'labelField': None}
    if 'timeFilter' not in props['collection']:
      props['collection']['timeFilter'] = {
        'field': '',
        'type': 'rolling',
        'value': 'all',
        'from': '',
        'to': '',
        'truncate': True
      }
    if 'suggest' not in props['collection']:
      props['collection']['suggest'] = {'enabled': False, 'dictionary': ''}
    for field in props['collection']['template']['fieldsAttributes']:
      if 'type' not in field:
        field['type'] = 'string'
    if 'nested' not in props['collection']:
      props['collection']['nested'] = {
        'enabled': False,
        'schema': []
      }

    for facet in props['collection']['facets']:
      properties = facet['properties']
      if 'gap' in properties and not 'initial_gap' in properties:
        properties['initial_gap'] = properties['gap']
      if 'start' in properties and not 'initial_start' in properties:
        properties['initial_start'] = properties['start']
      if 'end' in properties and not 'initial_end' in properties:
        properties['initial_end'] = properties['end']
      if 'domain' not in properties:
        properties['domain'] = {'blockParent': [], 'blockChildren': []}

      if facet['widgetType'] == 'histogram-widget':
        if 'timelineChartType' not in properties:
          properties['timelineChartType'] = 'bar'
        if 'enableSelection' not in properties:
          properties['enableSelection'] = True
        if 'extraSeries' not in properties:
          properties['extraSeries'] = []

      if facet['widgetType'] == 'map-widget' and facet['type'] == 'field':
        facet['type'] = 'pivot'
        properties['facets'] = []
        properties['facets_form'] = {'field': '', 'mincount': 1, 'limit': 5}

    if 'qdefinitions' not in props['collection']:
      props['collection']['qdefinitions'] = []

    return props

  def get_default(self, user, name, engine='solr'):
    fields = self.fields_data(user, name, engine)
    id_field = [field['name'] for field in fields if field.get('isId')]

    if id_field:
      id_field = id_field[0]
    else:
      id_field = '' # Schemaless might not have an id

    TEMPLATE = {
      "extracode": escape("<style type=\"text/css\">\nem {\n  font-weight: bold;\n  background-color: yellow;\n}</style>\n\n<script>\n</script>"),
      "highlighting": [""],
      "properties": {"highlighting_enabled": True},
      "template": """
      <div class="row-fluid">
        <div class="row-fluid">
          <div class="span12">%s</div>
        </div>
        <br/>
      </div>""" % ' '.join(['{{%s}}' % field['name'] for field in fields]),
      "isGridLayout": True,
      "showFieldList": True,
      "showGrid": True,
      "showChart": False,
      "chartSettings" : {
        'chartType': 'bars',
        'chartSorting': 'none',
        'chartScatterGroup': None,
        'chartScatterSize': None,
        'chartScope': 'world',
        'chartX': None,
        'chartYSingle': None,
        'chartYMulti': [],
        'chartData': [],
        'chartMapLabel': None,
      },
      "fieldsAttributes": [self._make_gridlayout_header_field(field) for field in fields],
      "fieldsSelected": [],
      "leafletmap": {'latitudeField': None, 'longitudeField': None, 'labelField': None},
      "rows": 25,
    }

    FACETS = []

    return {
      'id': None,
      'name': name,
      'engine': engine,
      'label': name,
      'enabled': False,
      'template': TEMPLATE,
      'facets': FACETS,
      'fields': fields,
      'idField': id_field,
    }

  @classmethod
  def _make_field(cls, field, attributes):
    return {
        'name': str(escape(field)),
        'type': str(attributes.get('type', '')),
        'isId': attributes.get('required') and attributes.get('uniqueKey'),
        'isDynamic': 'dynamicBase' in attributes
    }

  @classmethod
  def _make_gridlayout_header_field(cls, field, isDynamic=False):
    return {'name': field['name'], 'type': field['type'], 'sort': {'direction': None}, 'isDynamic': isDynamic}

  @classmethod
  def _make_luke_from_schema_fields(cls, schema_fields):
    return dict([
        (f['name'], {
              'copySources': [],
              'type': f['type'],
              'required': True,
              'uniqueKey': f.get('uniqueKey'),
              'flags': u'%s-%s-----OF-----l' % ('I' if f['indexed'] else '-', 'S' if f['stored'] else '-'), u'copyDests': []
        })
        for f in schema_fields['fields']
    ])

  def get_absolute_url(self):
    return reverse('search:index') + '?collection=%s' % self.id

  def fields(self, user):
    return sorted([str(field.get('name', '')) for field in self.fields_data(user)])

  def fields_data(self, user, name, engine='solr'):
    api = get_engine(user, engine)
    try:
      schema_fields = api.fields(name)
      schema_fields = schema_fields['schema']['fields']
    except Exception, e:
      LOG.warn('/luke call did not succeed: %s' % e)
      fields = api.schema_fields(name)
      schema_fields = Collection2._make_luke_from_schema_fields(fields)

    return sorted([self._make_field(field, attributes) for field, attributes in schema_fields.iteritems()])

  def update_data(self, post_data):
    data_dict = self.data

    data_dict.update(post_data)

    self.data = data_dict

  @property
  def autocomplete(self):
    return self.data['autocomplete']

  @autocomplete.setter
  def autocomplete(self, autocomplete):
    properties_ = self.data
    properties_['autocomplete'] = autocomplete
    self.data = json.dumps(properties_)

  @classmethod
  def get_field_list(cls, collection):
    if collection['template']['fieldsSelected'] and collection['template']['isGridLayout']:
      fields = set(collection['template']['fieldsSelected'] + ([collection['idField']] if collection['idField'] else []))
      # Add field if needed
      if collection['template']['leafletmap'].get('latitudeField'):
        fields.add(collection['template']['leafletmap']['latitudeField'])
      if collection['template']['leafletmap'].get('longitudeField'):
        fields.add(collection['template']['leafletmap']['longitudeField'])
      if collection['template']['leafletmap'].get('labelField'):
        fields.add(collection['template']['leafletmap']['labelField'])
      return list(fields)
    else:
      return ['*']

def get_facet_field(category, field, facets):
  if category in ('nested', 'function'):
    id_pattern = '%(id)s'
  else:
    id_pattern = '%(field)s-%(id)s'

  facets = filter(lambda facet: facet['type'] == category and id_pattern % facet == field, facets)

  if facets:
    return facets[0]
  else:
    return None

def pairwise2(field, fq_filter, iterable):
  pairs = []
  selected_values = [f['value'] for f in fq_filter]
  a, b = itertools.tee(iterable)
  for element in a:
    pairs.append({
        'cat': field,
        'value': element,
        'count': next(a),
        'selected': element in selected_values,
        'exclude': all([f['exclude'] for f in fq_filter if f['value'] == element])
    })
  return pairs

def range_pair(field, cat, fq_filter, iterable, end, collection_facet):
  # e.g. counts":["0",17430,"1000",1949,"2000",671,"3000",404,"4000",243,"5000",165],"gap":1000,"start":0,"end":6000}
  pairs = []
  selected_values = [f['value'] for f in fq_filter]
  is_single_unit_gap = re.match('^[\+\-]?1[A-Za-z]*$', str(collection_facet['properties']['gap'])) is not None
  is_up = collection_facet['properties']['sort'] == 'asc'

  if collection_facet['properties']['sort'] == 'asc' and (collection_facet['type'] == 'range-up' or collection_facet['properties'].get('type') == 'range-up'):
    prev = None
    n = []
    for e in iterable:
      if prev is not None:
        n.append(e)
        n.append(prev)
        prev = None
      else:
        prev = e
    iterable = n
    iterable.reverse()

  a, to = itertools.tee(iterable)
  next(to, None)
  counts = iterable[1::2]
  total_counts = counts.pop(0) if collection_facet['properties']['sort'] == 'asc' else 0

  for element in a:
    next(to, None)
    to_value = next(to, end)
    count = next(a)

    pairs.append({
        'field': field, 'from': element, 'value': count, 'to': to_value, 'selected': element in selected_values,
        'exclude': all([f['exclude'] for f in fq_filter if f['value'] == element]),
        'is_single_unit_gap': is_single_unit_gap,
        'total_counts': total_counts,
        'is_up': is_up
    })
    total_counts += counts.pop(0) if counts else 0

  if collection_facet['properties']['sort'] == 'asc' and collection_facet['type'] != 'range-up' and collection_facet['properties'].get('type') != 'range-up':
    pairs.reverse()

  return pairs


def augment_solr_response(response, collection, query):
  augmented = response
  augmented['normalized_facets'] = []
  NAME = '%(field)s-%(id)s'
  normalized_facets = []

  selected_values = dict([(fq['id'], fq['filter']) for fq in query['fqs']])

  if response and response.get('facet_counts'):
    for facet in collection['facets']:
      category = facet['type']

      if category == 'field' and response['facet_counts']['facet_fields']:
        name = NAME % facet
        collection_facet = get_facet_field(category, name, collection['facets'])
        counts = pairwise2(facet['field'], selected_values.get(facet['id'], []), response['facet_counts']['facet_fields'][name])
        if collection_facet['properties']['sort'] == 'asc':
          counts.reverse()
        facet = {
          'id': collection_facet['id'],
          'field': facet['field'],
          'type': category,
          'label': collection_facet['label'],
          'counts': counts,
        }
        normalized_facets.append(facet)
      elif (category == 'range' or category == 'range-up') and response['facet_counts']['facet_ranges']:
        name = NAME % facet
        collection_facet = get_facet_field(category, name, collection['facets'])
        counts = response['facet_counts']['facet_ranges'][name]['counts']
        end = response['facet_counts']['facet_ranges'][name]['end']
        counts = range_pair(facet['field'], name, selected_values.get(facet['id'], []), counts, end, collection_facet)
        facet = {
          'id': collection_facet['id'],
          'field': facet['field'],
          'type': category,
          'label': collection_facet['label'],
          'counts': counts,
          'extraSeries': []
        }
        normalized_facets.append(facet)
      elif category == 'query' and response['facet_counts']['facet_queries']:
        for name, value in response['facet_counts']['facet_queries'].iteritems():
          collection_facet = get_facet_field(category, name, collection['facets'])
          facet = {
            'id': collection_facet['id'],
            'query': name,
            'type': category,
            'label': name,
            'counts': value,
          }
          normalized_facets.append(facet)
      elif category == 'pivot':
        name = NAME % facet
        if 'facet_pivot' in response['facet_counts'] and name in response['facet_counts']['facet_pivot']:
          if facet['properties']['scope'] == 'stack':
            count = _augment_pivot_2d(name, facet['id'], response['facet_counts']['facet_pivot'][name], selected_values)
          else:
            count = response['facet_counts']['facet_pivot'][name]
            _augment_pivot_nd(facet['id'], count, selected_values)
        else:
          count = []
        facet = {
          'id': facet['id'],
          'field': name,
          'type': category,
          'label': name,
          'counts': count,
        }
        normalized_facets.append(facet)

  if response and response.get('facets'):
    for facet in collection['facets']:
      category = facet['type']
      name = facet['id'] # Nested facets can only have one name

      if category == 'function' and name in response['facets']:
        value = response['facets'][name]
        collection_facet = get_facet_field(category, name, collection['facets'])
        facet = {
          'id': collection_facet['id'],
          'query': name,
          'type': category,
          'label': name,
          'counts': value,
        }
        normalized_facets.append(facet)
      elif category == 'nested' and name in response['facets']:
        value = response['facets'][name]
        collection_facet = get_facet_field(category, name, collection['facets'])
        extraSeries = []
        counts = response['facets'][name]['buckets']

        cols = ['%(field)s' % facet, 'count(%(field)s)' % facet]
        last_x_col = 0
        last_xx_col = 0
        for i, f in enumerate(facet['properties']['facets']):
          if f['aggregate']['function'] == 'count':
            cols.append(f['field'])
            last_xx_col = last_x_col
            last_x_col = i + 2
          from libsolr.api import SolrApi
          cols.append(SolrApi._get_aggregate_function(f))
        rows = []

        # For dim in dimensions

        # Number or Date range
        if collection_facet['properties']['canRange'] and not facet['properties'].get('type') == 'field':
          dimension = 3 if collection_facet['properties']['isDate'] else 1
          # Single dimension or dimension 2 with analytics
          if not collection_facet['properties']['facets'] or collection_facet['properties']['facets'][0]['aggregate']['function'] != 'count' and len(collection_facet['properties']['facets']) == 1:
            column = 'count'
            if len(collection_facet['properties']['facets']) == 1:
              agg_keys = [key for key, value in counts[0].items() if key.lower().startswith('agg_')]
              legend = agg_keys[0].split(':', 2)[1]
              column = agg_keys[0]
            else:
              legend = facet['field'] # 'count(%s)' % legend
              agg_keys = [column]

            _augment_stats_2d(name, facet, counts, selected_values, agg_keys, rows)

            counts = [_v for _f in counts for _v in (_f['val'], _f[column])]
            counts = range_pair(facet['field'], name, selected_values.get(facet['id'], []), counts, 1, collection_facet)
          else:
            # Dimension 1 with counts and 2 with analytics
            agg_keys = [key for key, value in counts[0].items() if key.lower().startswith('agg_') or key.lower().startswith('dim_')]
            agg_keys.sort(key=lambda a: a[4:])

            if len(agg_keys) == 1 and agg_keys[0].lower().startswith('dim_'):
              agg_keys.insert(0, 'count')
            counts = _augment_stats_2d(name, facet, counts, selected_values, agg_keys, rows)

            _series = collections.defaultdict(list)

            for row in rows:
              for i, cell in enumerate(row):
                if i > last_x_col:
                  legend = cols[i]
                  if last_xx_col != last_x_col:
                    legend = '%s %s' % (cols[i], row[last_x_col])
                  _series[legend].append(row[last_xx_col])
                  _series[legend].append(cell)

            for _name, val in _series.iteritems():
              _c = range_pair(facet['field'], _name, selected_values.get(facet['id'], []), val, 1, collection_facet)
              extraSeries.append({'counts': _c, 'label': _name})
            counts = []
        elif collection_facet['properties'].get('isOldPivot'):
          facet_fields = [collection_facet['field']] + [f['field'] for f in collection_facet['properties'].get('facets', []) if f['aggregate']['function'] == 'count']

          column = 'count'
          agg_keys = [key for key, value in counts[0].items() if key.lower().startswith('agg_') or key.lower().startswith('dim_')]
          agg_keys.sort(key=lambda a: a[4:])

          if len(agg_keys) == 1 and agg_keys[0].lower().startswith('dim_'):
            agg_keys.insert(0, 'count')
          counts = _augment_stats_2d(name, facet, counts, selected_values, agg_keys, rows)

          #_convert_nested_to_augmented_pivot_nd(facet_fields, facet['id'], count, selected_values, dimension=2)
          dimension = len(facet_fields)
        elif not collection_facet['properties']['facets'] or (collection_facet['properties']['facets'][0]['aggregate']['function'] != 'count' and len(collection_facet['properties']['facets']) == 1):
          # Dimension 1 with 1 count or agg
          dimension = 1

          column = 'count'
          if len(collection_facet['properties']['facets']) == 1:
            agg_keys = [key for key, value in counts[0].items() if key.lower().startswith('agg_')]
            legend = agg_keys[0].split(':', 2)[1]
            column = agg_keys[0]
          else:
            legend = facet['field']
            agg_keys = [column]

          _augment_stats_2d(name, facet, counts, selected_values, agg_keys, rows)

          counts = [_v for _f in counts for _v in (_f['val'], _f[column])]
          counts = pairwise2(legend, selected_values.get(facet['id'], []), counts)
        else:
          # Dimension 2 with analytics or 1 with N aggregates
          dimension = 2
          agg_keys = [key for key, value in counts[0].items() if key.lower().startswith('agg_') or key.lower().startswith('dim_')]
          agg_keys.sort(key=lambda a: a[4:])

          if len(agg_keys) == 1 and agg_keys[0].lower().startswith('dim_'):
            agg_keys.insert(0, 'count')
          counts = _augment_stats_2d(name, facet, counts, selected_values, agg_keys, rows)
          actual_dimension = 1 + sum([_f['aggregate']['function'] == 'count' for _f in collection_facet['properties']['facets']])

          counts = filter(lambda a: len(a['fq_fields']) == actual_dimension, counts)

        num_bucket = response['facets'][name]['numBuckets'] if 'numBuckets' in response['facets'][name] else len(response['facets'][name])
        facet = {
          'id': collection_facet['id'],
          'field': facet['field'],
          'type': category,
          'label': collection_facet['label'],
          'counts': counts,
          'extraSeries': extraSeries,
          'dimension': dimension,
          'response': {'response': {'start': 0, 'numFound': num_bucket}}, # Todo * nested buckets + offsets
          'docs': [dict(zip(cols, row)) for row in rows],
          'fieldsAttributes': [Collection2._make_gridlayout_header_field({'name': col, 'type': 'aggr' if '(' in col else 'string'}) for col in cols]
        }

        normalized_facets.append(facet)

    # Remove unnecessary facet data
    if response:
      response.pop('facet_counts')
      response.pop('facets')

  augment_response(collection, query, response)

  if normalized_facets:
    augmented['normalized_facets'].extend(normalized_facets)

  return augmented


def augment_response(collection, query, response):
  # HTML escaping
  if not query.get('download'):
    id_field = collection.get('idField', '')

    for doc in response['response']['docs']:
      link = None
      if 'link-meta' in doc:
        meta = json.loads(doc['link-meta'])
        link = get_data_link(meta)
      elif 'link' in doc:
        meta = {'type': 'link', 'link': doc['link']}
        link = get_data_link(meta)

      for field, value in doc.iteritems():
        if isinstance(value, numbers.Number):
          escaped_value = value
        elif field == '_childDocuments_': # Nested documents
          escaped_value = value
        elif isinstance(value, list): # Multivalue field
          escaped_value = [smart_unicode(escape(val), errors='replace') for val in value]
        else:
          value = smart_unicode(value, errors='replace')
          escaped_value = escape(value)
        doc[field] = escaped_value

      doc['externalLink'] = link
      doc['details'] = []
      doc['hueId'] = smart_unicode(doc.get(id_field, ''))

  highlighted_fields = response.get('highlighting', {}).keys()
  if highlighted_fields and not query.get('download'):
    id_field = collection.get('idField')
    if id_field:
      for doc in response['response']['docs']:
        if id_field in doc and smart_unicode(doc[id_field]) in highlighted_fields:
          highlighting = response['highlighting'][smart_unicode(doc[id_field])]

          if highlighting:
            escaped_highlighting = {}
            for field, hls in highlighting.iteritems():
              _hls = [escape(smart_unicode(hl, errors='replace')).replace('&lt;em&gt;', '<em>').replace('&lt;/em&gt;', '</em>') for hl in hls]
              escaped_highlighting[field] = _hls[0] if len(_hls) == 1 else _hls

            doc.update(escaped_highlighting)
    else:
      response['warning'] = _("The Solr schema requires an id field for performing the result highlighting")


def _augment_pivot_2d(name, facet_id, counts, selected_values):
  values = set()

  for dimension in counts:
    for pivot in dimension['pivot']:
      values.add(pivot['value'])

  values = sorted(list(values))
  augmented = []

  for dimension in counts:
    count = {}
    pivot_field = ''
    for pivot in dimension['pivot']:
      count[pivot['value']] = pivot['count']
      pivot_field = pivot['field']
    for val in values:
      fq_values = [dimension['value'], val]
      fq_fields = [dimension['field'], pivot_field]
      fq_filter = selected_values.get(facet_id, [])
      _selected_values = [f['value'] for f in fq_filter]

      augmented.append({
          "count": count.get(val, 0),
          "value": val,
          "cat": dimension['value'],
          'selected': fq_values in _selected_values,
          'exclude': all([f['exclude'] for f in fq_filter if f['value'] == val]),
          'fq_fields': fq_fields,
          'fq_values': fq_values,
      })

  return augmented


def _augment_stats_2d(name, facet, counts, selected_values, agg_keys, rows):
  fq_fields = []
  fq_values = []
  fq_filter = []
  _selected_values = [f['value'] for f in selected_values.get(facet['id'], [])]
  _fields = [facet['field']] + [facet['field'] for facet in facet['properties']['facets']]

  return __augment_stats_2d(counts, facet['field'], fq_fields, fq_values, fq_filter, _selected_values, _fields, agg_keys, rows)


# Clear one dimension
def __augment_stats_2d(counts, label, fq_fields, fq_values, fq_filter, _selected_values, _fields, agg_keys, rows):
  augmented = []

  for bucket in counts: # For each dimension, go through each bucket and pick up the counts or aggregates, then go recursively in the next dimension
    val = bucket['val']
    count = bucket['count']
    dim_row = [val]

    _fq_fields = fq_fields + _fields[0:1]
    _fq_values = fq_values + [val]

    for agg_key in agg_keys:
      if agg_key == 'count':
        dim_row.append(count)
        augmented.append(_get_augmented(count, val, label, _fq_values, _fq_fields, fq_filter, _selected_values))
      elif agg_key.startswith('agg_'):
        label = fq_values[0] if len(_fq_fields) >= 2 else agg_key.split(':', 2)[1]
        if agg_keys.index(agg_key) == 0: # One count by dimension
          dim_row.append(count)
        dim_row.append(bucket[agg_key])
        augmented.append(_get_augmented(bucket[agg_key], val, label, _fq_values, _fq_fields, fq_filter, _selected_values))
      else:
        augmented.append(_get_augmented(count, val, label, _fq_values, _fq_fields, fq_filter, _selected_values)) # Needed?

        # Go rec
        _agg_keys = [key for key, value in bucket[agg_key]['buckets'][0].items() if key.lower().startswith('agg_') or key.lower().startswith('dim_')]
        _agg_keys.sort(key=lambda a: a[4:])

        if not _agg_keys or len(_agg_keys) == 1 and _agg_keys[0].lower().startswith('dim_'):
          _agg_keys.insert(0, 'count')
        next_dim = []
        new_rows = []
        augmented += __augment_stats_2d(bucket[agg_key]['buckets'], val, _fq_fields, _fq_values, fq_filter, _selected_values, _fields[1:], _agg_keys, next_dim)
        for row in next_dim:
          new_rows.append(dim_row + row)
        dim_row = new_rows

    if dim_row and type(dim_row[0]) == list:
      rows.extend(dim_row)
    else:
      rows.append(dim_row)

  return augmented


def _get_augmented(count, val, label, fq_values, fq_fields, fq_filter, _selected_values):
  return {
      "count": count,
      "value": val,
      "cat": label,
      'selected': fq_values in _selected_values,
      'exclude': all([f['exclude'] for f in fq_filter if f['value'] == val]),
      'fq_fields': fq_fields,
      'fq_values': fq_values
  }


def _augment_pivot_nd(facet_id, counts, selected_values, fields='', values=''):
  for c in counts:
    fq_fields = (fields if fields else []) + [c['field']]
    fq_values = (values if values else []) + [smart_str(c['value'])]

    if 'pivot' in c:
      _augment_pivot_nd(facet_id, c['pivot'], selected_values, fq_fields, fq_values)

    fq_filter = selected_values.get(facet_id, [])
    _selected_values = [f['value'] for f in fq_filter]
    c['selected'] = fq_values in _selected_values
    c['exclude'] = False
    c['fq_fields'] = fq_fields
    c['fq_values'] = fq_values


def _convert_nested_to_augmented_pivot_nd(facet_fields, facet_id, counts, selected_values, fields='', values='', dimension=2):
  for c in counts['buckets']:
    c['field'] = facet_fields[0]
    fq_fields = (fields if fields else []) + [c['field']]
    fq_values = (values if values else []) + [smart_str(c['val'])]
    c['value'] = c.pop('val')
    bucket = 'd%s' % dimension

    if bucket in c:
      next_dimension = facet_fields[1:]
      if next_dimension:
        _convert_nested_to_augmented_pivot_nd(next_dimension, facet_id, c[bucket], selected_values, fq_fields, fq_values, dimension=dimension+1)
        c['pivot'] = c.pop(bucket)['buckets']
      else:
        c['count'] = c.pop(bucket)

    fq_filter = selected_values.get(facet_id, [])
    _selected_values = [f['value'] for f in fq_filter]
    c['selected'] = fq_values in _selected_values
    c['exclude'] = False
    c['fq_fields'] = fq_fields
    c['fq_values'] = fq_values


def augment_solr_exception(response, collection):
  response.update(
  {
    "facet_counts": {
    },
    "highlighting": {
    },
    "normalized_facets": [
      {
        "field": facet['field'],
        "counts": [],
        "type": facet['type'],
        "label": facet['label']
      }
      for facet in collection['facets']
    ],
    "responseHeader": {
      "status": -1,
      "QTime": 0,
      "params": {
      }
    },
    "response": {
      "start": 0,
      "numFound": 0,
      "docs": [
      ]
    }
  })
