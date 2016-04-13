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

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.html import escape
from django.utils.translation import ugettext as _, ugettext_lazy as _t

from desktop.lib.i18n import smart_unicode, smart_str
from desktop.models import get_data_link

from libsolr.api import SolrApi

from search.conf import SOLR_URL


LOG = logging.getLogger(__name__)


# Deprecated
class Facet(models.Model):
  _ATTRIBUTES = ['properties', 'fields', 'ranges', 'dates', 'charts', 'order']

  enabled = models.BooleanField(default=True)
  data = models.TextField()

  def get_data(self):
    return json.loads(self.data)

  def update_from_post(self, post_data):
    data_dict = json.loads(self.data)

    for attr in Facet._ATTRIBUTES:
      if post_data.get(attr) is not None:
        data_dict[attr] = json.loads(post_data[attr])

    self.data = json.dumps(data_dict)


  def get_query_params(self):
    data_dict = json.loads(self.data)

    properties = data_dict.get('properties')

    params = (
      ('facet', properties.get('isEnabled') and 'true' or 'false'),
      ('facet.mincount', properties.get('mincount')),
      ('facet.limit', 100),
      ('facet.sort', properties.get('sort')),
    )

    if data_dict.get('charts'):
      for field_facet in data_dict['charts']:
        if field_facet['start'] and field_facet['end'] and field_facet['gap']:
          range_facets = tuple([
             ('facet.range', field_facet['field']),
             ('f.%s.facet.limit' % field_facet['field'], -1),
             ('f.%s.facet.range.start' % field_facet['field'], field_facet['start']),
             ('f.%s.facet.range.end' % field_facet['field'], field_facet['end']),
             ('f.%s.facet.range.gap' % field_facet['field'], field_facet['gap']),]
          )
          params += range_facets
        else:
          field_facets = tuple([
            ('facet.field', field_facet['field']),
            ('f.%s.facet.limit' % field_facet['field'], -1),
          ])
          params += field_facets

    if data_dict.get('ranges'):
      for field_facet in data_dict['ranges']:
        range_facets = tuple([
           ('facet.range', field_facet['field']),
           ('f.%s.facet.range.start' % field_facet['field'], field_facet['start']),
           ('f.%s.facet.range.end' % field_facet['field'], field_facet['end']),
           ('f.%s.facet.range.gap' % field_facet['field'], field_facet['gap']),]
        )
        params += range_facets

    if data_dict.get('dates'):
      for field_facet in data_dict['dates']:
        start = field_facet['start']
        end = field_facet['end']
        gap = field_facet['gap']

        date_facets = tuple([
           ('facet.date', field_facet['field']),
           ('f.%s.facet.date.start' % field_facet['field'], 'NOW-%(frequency)s%(unit)s/%(rounder)s' % {"frequency": start["frequency"], "unit": start["unit"], "rounder": gap["unit"]}),
           ('f.%s.facet.date.end' % field_facet['field'], 'NOW-%(frequency)s%(unit)s' % end),
           ('f.%s.facet.date.gap' % field_facet['field'], '+%(frequency)s%(unit)s' % gap),]
        )
        params += date_facets

    return params


# Deprecated
class Result(models.Model):
  _ATTRIBUTES = ['properties', 'template', 'highlighting', 'extracode']

  data = models.TextField()

  def update_from_post(self, post_data):
    data_dict = json.loads(self.data)

    for attr in Result._ATTRIBUTES:
      if post_data.get(attr) is not None:
        data_dict[attr] = json.loads(post_data[attr])

    self.data = json.dumps(data_dict)


  def get_template(self, with_highlighting=False):
    data_dict = json.loads(self.data)

    template = data_dict.get('template')
    if with_highlighting and data_dict.get('highlighting'):
      for field in data_dict.get('highlighting', []):
        template = re.sub('\{\{%s\}\}' % field, '{{{%s}}}' % field, template)

    return template

  def get_extracode(self):
    data_dict = json.loads(self.data)
    return data_dict.get('extracode')

  def get_highlighting(self):
    data_dict = json.loads(self.data)
    return json.dumps(data_dict.get('highlighting'))

  def get_properties(self):
    data_dict = json.loads(self.data)
    return json.dumps(data_dict.get('properties'))

  def get_query_params(self):
    data_dict = json.loads(self.data)

    params = ()

    if data_dict.get('highlighting'):
      params += (
        ('hl', data_dict.get('properties', {}).get('highlighting_enabled') and 'true' or 'false'),
        ('hl.fl', ','.join(data_dict.get('highlighting'))),
      )

    return params


# Deprecated
class Sorting(models.Model):
  _ATTRIBUTES = ['properties', 'fields']

  data = models.TextField()

  def update_from_post(self, post_data):
    data_dict = json.loads(self.data)

    for attr in Sorting._ATTRIBUTES:
      if post_data.get(attr) is not None:
        data_dict[attr] = json.loads(post_data[attr])

    self.data = json.dumps(data_dict)


  def get_query_params(self, client_query=None):
    params = ()
    data_dict = json.loads(self.data)

    fields = []
    if data_dict.get('properties', {}).get('is_enabled') and 'true' or 'false':
      if client_query is not None and client_query.get('sort'):
        params += (
          ('sort', client_query.get('sort')),
        )
      elif data_dict.get('fields'):
        fields = []
        for field in data_dict.get('fields'):
          if field['include']:
            fields.append('%s %s' % (field['field'], field['asc'] and 'asc' or 'desc'))
        params += (
          ('sort', ','.join(fields)),
        )

    return params


# Deprecated
class CollectionManager(models.Manager):

  def create2(self, name, label, is_core_only=False, owner=None):
    facets = Facet.objects.create()
    result = Result.objects.create()
    sorting = Sorting.objects.create()

    collection = Collection.objects.create(
        name=name,
        label=label,
        owner=owner,
        enabled=False,
        cores=json.dumps({'version': 2}),
        is_core_only=is_core_only,
        facets=facets,
        result=result,
        sorting=sorting
    )

    return collection


# Deprecated see Collection2
class Collection(models.Model):
  """All the data is now saved into the properties field"""
  enabled = models.BooleanField(default=False) # Aka shared
  name = models.CharField(max_length=40, verbose_name=_t('Solr index name pointing to'))
  label = models.CharField(max_length=100, verbose_name=_t('Friendlier name in UI'))
  is_core_only = models.BooleanField(default=False)
  cores = models.TextField(default=json.dumps({}), verbose_name=_t('Collection with cores data'), help_text=_t('Solr json')) # Unused
  properties = models.TextField(
      default=json.dumps({}), verbose_name=_t('Properties'),
      help_text=_t('Hue properties (e.g. results by pages number)')
  )

  facets = models.ForeignKey(Facet)
  result = models.ForeignKey(Result)
  sorting = models.ForeignKey(Sorting)

  owner = models.ForeignKey(User, db_index=True, verbose_name=_t('Owner'), help_text=_t('User who created the job.'), default=None, null=True)

  _ATTRIBUTES = ['collection', 'layout', 'autocomplete']
  ICON = 'search/art/icon_search_48.png'

  objects = CollectionManager()

  def get_c(self, user):
    props = self.properties_dict

    if 'collection' not in props:
      props['collection'] = self.get_default(user)
      if self.cores != '{}': # Convert collections from < Hue 3.6
        try:
          self._import_hue_3_5_collections(props, user)
        except Exception, e:
          LOG.error('Could not import collection: %s' % e)

    if 'layout' not in props:
      props['layout'] = []

    if self.id:
      props['collection']['id'] = self.id
    if self.name:
      props['collection']['name'] = self.name
    if self.label:
      props['collection']['label'] = self.label
    if self.enabled is not None:
      props['collection']['enabled'] = self.enabled

    # For backward compatibility
    if 'rows' not in props['collection']['template']:
      props['collection']['template']['rows'] = 10
    if 'enabled' not in props['collection']:
      props['collection']['enabled'] = True
    if 'leafletmap' not in props['collection']['template']:
      props['collection']['template']['leafletmap'] = {'latitudeField': None, 'longitudeField': None, 'labelField': None}

    for facet in props['collection']['facets']:
      properties = facet['properties']
      if 'gap' in properties and not 'initial_gap' in properties:
        properties['initial_gap'] = properties['gap']
      if 'start' in properties and not 'initial_start' in properties:
        properties['initial_start'] = properties['start']
      if 'end' in properties and not 'initial_end' in properties:
        properties['initial_end'] = properties['end']

      if facet['widgetType'] == 'histogram-widget':
        if 'timelineChartType' not in properties:
          properties['timelineChartType'] = 'bar'
        if 'extraSeries' not in properties:
          properties['extraSeries'] = []

      if facet['widgetType'] == 'heatmap-widget' and 'stacked' not in properties:
        properties['stacked'] = True

      if facet['widgetType'] == 'bar-widget' and 'stacked' not in properties:
        properties['stacked'] = False

      if facet['widgetType'] == 'map-widget' and facet['type'] == 'field':
        facet['type'] = 'pivot'
        properties['facets'] = []
        properties['facets_form'] = {'field': '', 'mincount': 1, 'limit': 5}

    return json.dumps(props)

  def get_default(self, user):
    fields = self.fields_data(user)
    id_field = [field['name'] for field in fields if field.get('isId')]
    if id_field:
      id_field = id_field[0]

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
      "fieldsAttributes": [self._make_gridlayout_header_field(field) for field in fields],
      "fieldsSelected": [],
      "leafletmap": {'latitudeField': None, 'longitudeField': None, 'labelField': None},
      "rows": 10,
    }

    FACETS = []

    return {
      'id': self.id, 'name': self.name, 'label': self.label, 'enabled': self.enabled,
      'template': TEMPLATE, 'facets': FACETS,
      'fields': fields, 'idField': id_field,
    }

  @classmethod
  def _make_field(cls, field, attributes):
    return {
        'name': str(field),
        'type': str(attributes.get('type', '')),
        'isId': attributes.get('required') and attributes.get('uniqueKey'),
        'isDynamic': 'dynamicBase' in attributes
    }

  @classmethod
  def _make_gridlayout_header_field(cls, field, isDynamic=False):
    return {'name': field['name'], 'sort': {'direction': None}, 'isDynamic': isDynamic}

  def get_absolute_url(self):
    return reverse('search:index') + '?collection=%s' % self.id

  def fields(self, user):
    return sorted([str(field.get('name', '')) for field in self.fields_data(user)])

  def fields_data(self, user):
    schema_fields = SolrApi(SOLR_URL.get(), user).fields(self.name)
    schema_fields = schema_fields['schema']['fields']

    return sorted([self._make_field(field, attributes) for field, attributes in schema_fields.iteritems()])

  @property
  def properties_dict(self):
    if not self.properties:
      self.data = json.dumps({})
    properties_python = json.loads(self.properties)

    # Backward compatibility conversions
    if 'autocomplete' not in properties_python:
      properties_python['autocomplete'] = False
    if 'collection' in properties_python:
      if 'showFieldList' not in properties_python['collection']['template']:
        properties_python['collection']['template']['showFieldList'] = True

    return properties_python

  def update_properties(self, post_data):
    prop_dict = self.properties_dict

    for attr in Collection._ATTRIBUTES:
      if post_data.get(attr) is not None:
        prop_dict[attr] = post_data[attr]

    self.properties = json.dumps(prop_dict)

  @property
  def autocomplete(self):
    return self.properties_dict['autocomplete']

  @autocomplete.setter
  def autocomplete(self, autocomplete):
    properties_ = self.properties_dict
    properties_['autocomplete'] = autocomplete
    self.properties = json.dumps(properties_)

  @property
  def icon(self):
    if self.name == 'twitter_demo':
      return 'search/art/icon_twitter_48.png'
    elif self.name == 'yelp_demo':
      return 'search/art/icon_yelp_48.png'
    elif self.name == 'log_analytics_demo':
      return 'search/art/icon_logs_48.png'
    else:
      return 'search/art/icon_search_48.png'

  def _import_hue_3_5_collections(self, props, user):
    props['collection']['template']['template'] = self.result.get_template()
    props['collection']['template']['extracode'] = escape(self.result.get_extracode())
    props['collection']['template']['isGridLayout'] = False
    props['layout'] = [
          {"size":2,"rows":[{"widgets":[]}],"drops":["temp"],"klass":"card card-home card-column span2"},
          {"size":10,"rows":[{"widgets":[
              {"size":12,"name":"Grid Results","id":"52f07188-f30f-1296-2450-f77e02e1a5c0","widgetType":"html-resultset-widget",
               "properties":{},"offset":0,"isLoading":True,"klass":"card card-widget span12"}]
          }], "drops":["temp"],"klass":"card card-home card-column span10"}
     ]

    from search.views import _create_facet

    props['collection']['facets'] =[]
    facets = self.facets.get_data()

    for facet_id in facets['order']:
      for facet in facets['fields'] + facets['ranges']:
        if facet['uuid'] == facet_id:
          props['collection']['facets'].append(
              _create_facet({'name': self.name}, user, facet_id, facet['label'], facet['field'], 'facet-widget'))
          props['layout'][0]['rows'][0]['widgets'].append({
              "size":12,"name": facet['label'], "id":facet_id, "widgetType": "facet-widget",
              "properties":{},"offset":0,"isLoading":True,"klass":"card card-widget span12"
          })


class Collection2(object):

  def __init__(self, user, name='Default', data=None, document=None):
    self.document = document

    if document is not None:
      self.data = json.loads(document.data)
    elif data is not None:
      self.data = json.loads(data)
    else:
      self.data = {
          'collection': self.get_default(user, name),
          'layout': []
      }

  def get_json(self, user):
    props = self.data

    if self.document is not None:
      props['collection']['id'] = self.document.id
      props['collection']['label'] = self.document.name
      props['collection']['description'] = self.document.description

    # For backward compatibility
    if 'rows' not in props['collection']['template']:
      props['collection']['template']['rows'] = 10
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
    if 'leafletmap' not in props['collection']['template']:
      props['collection']['template']['leafletmap'] = {'latitudeField': None, 'longitudeField': None, 'labelField': None}
    if 'timeFilter' not in props['collection']:
      props['collection']['timeFilter'] = {
        'field': '',
        'type': 'rolling',
        'value': 'all',
        'from': '',
        'to': 'NOW',
        'truncate': True
      }
    if 'suggest' not in props['collection']:
      props['collection']['suggest'] = {'enabled': False, 'dictionary': ''}
    for field in props['collection']['template']['fieldsAttributes']:
      if 'type' not in field:
        field['type'] = 'string'

    for facet in props['collection']['facets']:
      properties = facet['properties']
      if 'gap' in properties and not 'initial_gap' in properties:
        properties['initial_gap'] = properties['gap']
      if 'start' in properties and not 'initial_start' in properties:
        properties['initial_start'] = properties['start']
      if 'end' in properties and not 'initial_end' in properties:
        properties['initial_end'] = properties['end']

      if facet['widgetType'] == 'histogram-widget':
        if 'timelineChartType' not in properties:
          properties['timelineChartType'] = 'bar'
        if 'extraSeries' not in properties:
          properties['extraSeries'] = []

      if facet['widgetType'] == 'map-widget' and facet['type'] == 'field':
        facet['type'] = 'pivot'
        properties['facets'] = []
        properties['facets_form'] = {'field': '', 'mincount': 1, 'limit': 5}

    if 'qdefinitions' not in props['collection']:
      props['collection']['qdefinitions'] = []

    return json.dumps(props)

  def get_default(self, user, name):
    fields = self.fields_data(user, name)
    id_field = [field['name'] for field in fields if field.get('isId')]
    if id_field:
      id_field = id_field[0]

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
      "rows": 10,
    }

    FACETS = []

    return {
      'id': None,
      'name': name,
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
        'name': str(field),
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
        for f in schema_fields['fields']])

  def get_absolute_url(self):
    return reverse('search:index') + '?collection=%s' % self.id

  def fields(self, user):
    return sorted([str(field.get('name', '')) for field in self.fields_data(user)])

  def fields_data(self, user, name):
    api = SolrApi(SOLR_URL.get(), user)
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

  if collection_facet['properties']['sort'] == 'asc' and collection_facet['type'] == 'range-up':
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

  if collection_facet['properties']['sort'] == 'asc' and collection_facet['type'] != 'range-up':
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

        # Date range
        if collection_facet['properties']['isDate']:
          dimension = 3
          # Single dimension or dimension 2 with analytics
          if not collection_facet['properties']['facets'] or collection_facet['properties']['facets'][0]['aggregate'] not in ('count', 'unique'):
            counts = [_v for _f in counts for _v in (_f['val'], _f['d2'] if 'd2' in _f else _f['count'])]
            counts = range_pair(facet['field'], name, selected_values.get(facet['id'], []), counts, 1, collection_facet)
          else:
            # Dimension 1 with counts and 2 with analytics
            _series = collections.defaultdict(list)
            for f in counts:
              for bucket in (f['d2']['buckets'] if 'd2' in f else []):
                _series[bucket['val']].append(f['val'])
                _series[bucket['val']].append(bucket['d2'] if 'd2' in bucket else bucket['count'])
            for name, val in _series.iteritems():
              _c = range_pair(facet['field'], name, selected_values.get(facet['id'], []), val, 1, collection_facet)
              extraSeries.append({'counts': _c, 'label': name})
            counts = []
        elif not collection_facet['properties']['facets'] or collection_facet['properties']['facets'][0]['aggregate'] not in ('count', 'unique'):
          # Single dimension or dimension 2 with analytics
          dimension = 1
          counts = [_v for _f in counts for _v in (_f['val'], _f['d2'] if 'd2' in _f else _f['count'])]
          counts = pairwise2(facet['field'], selected_values.get(facet['id'], []), counts)
        else:
          # Dimension 1 with counts and 2 with analytics
          dimension = 2
          counts = _augment_stats_2d(name, facet, counts, selected_values)

        if collection_facet['properties']['sort'] == 'asc':
          counts.reverse()

        facet = {
          'id': collection_facet['id'],
          'field': facet['field'],
          'type': category,
          'label': collection_facet['label'],
          'counts': counts,
          'extraSeries': extraSeries,
          'dimension': dimension
        }

        normalized_facets.append(facet)

    # Remove unnecessary facet data
    if response:
      response.pop('facet_counts')
      response.pop('facets')

  # HTML escaping
  if not query.get('download'):
    id_field = collection.get('idField', '')
    for doc in response['response']['docs']:
      for field, value in doc.iteritems():
        if isinstance(value, numbers.Number):
          escaped_value = value
        elif isinstance(value, list): # Multivalue field
          escaped_value = [smart_unicode(val, errors='replace') for val in value]
        else:
          value = smart_unicode(value, errors='replace')
          escaped_value = escape(value)
        doc[field] = escaped_value

      link = None
      if 'link-meta' in doc:
        meta = json.loads(doc['link-meta'])
        link = get_data_link(meta)

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


  if normalized_facets:
    augmented['normalized_facets'].extend(normalized_facets)

  return augmented


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


def _augment_stats_2d(name, facet, counts, selected_values):
  fq_fields = []
  fq_values = []
  fq_filter = []
  _selected_values = [f['value'] for f in selected_values.get(facet['id'], [])]
  _fields = [facet['field']] + [facet['field'] for facet in facet['properties']['facets']]

  return __augment_stats_2d(counts, facet['field'], fq_fields, fq_values, fq_filter, _selected_values, _fields)


def __augment_stats_2d(counts, label, fq_fields, fq_values, fq_filter, _selected_values, _fields):
  augmented = []

  for bucket in counts:
    val = bucket['val']
    count = bucket['count']

    _fq_fields = fq_fields + _fields[0:1]
    _fq_values = fq_values + [val]

    if 'd2' in bucket:
      if type(bucket['d2']) == dict:
        augmented += __augment_stats_2d(bucket['d2']['buckets'], val, _fq_fields, _fq_values, fq_filter, _selected_values, _fields[1:])
      else:
        augmented.append(_get_augmented(bucket['d2'], val, label, _fq_values, _fq_fields, fq_filter, _selected_values))
    else:
      augmented.append(_get_augmented(count, val, label, _fq_values, _fq_fields, fq_filter, _selected_values))

  return augmented


def _get_augmented(count, val, label, fq_values, fq_fields, fq_filter, _selected_values):
  return {
      "count": count,
      "value": val,
      "cat": label,
      'selected': fq_values in _selected_values,
      'exclude': all([f['exclude'] for f in fq_filter if f['value'] == val]),
      'fq_fields': fq_fields,
      'fq_values': fq_values,
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
