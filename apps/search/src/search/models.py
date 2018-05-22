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

import json
import logging
import re

from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _t

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
        if 'enableSelection' not in properties:
          properties['enableSelection'] = True
        if 'extraSeries' not in properties:
          properties['extraSeries'] = []

      if facet['widgetType'] == 'heatmap-widget' and 'stacked' not in properties:
        properties['stacked'] = True

      if facet['widgetType'] == 'bar-widget' and 'stacked' not in properties:
        properties['stacked'] = False

      if facet['widgetType'] == 'map-widget' and facet['type'] == 'field':
        facet['type'] = 'pivot'
        properties['facets'] = []
        properties['facets_form'] = {'field': '', 'mincount': 0, 'limit': 5}

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
