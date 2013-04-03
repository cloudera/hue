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

try:
  import json
except ImportError:
  import simplejson as json
  
from datetime import datetime
from lxml import etree
import re
import logging

from django.db import models
from django.utils.translation import ugettext as _, ugettext_lazy as _t
from django.core.urlresolvers import reverse
from mako.template import Template

from search.api import SolrApi
from search.conf import SOLR_URL

LOG = logging.getLogger(__name__)



class Facet(models.Model):
  _ATTRIBUTES = ['properties', 'fields', 'ranges', 'dates']

  enabled = models.BooleanField(default=True)
  data = models.TextField()

  def update_from_post(self, post_data):
    data_dict = json.loads(self.data)
    
    for attr in Sorting._META_TEMPLATE_ATTRS:
      if post_data.get(attr):
        data_dict[attr] = json.loads(post_data[attr])

    self.data = json.dumps(data_dict)


  def get_query_params(self):
    data_dict = json.loads(self.data)

    params = (
        ('facet', data_dict.get('properties', {}).get('is_enabled') and 'true' or 'false'),
        ('facet.limit', 10),
        ('facet.mincount', 1),
        ('facet.sort', 'count'),
    )

    if data_dict.get('fields'):
      field_facets = tuple([('facet.field', field_facet['field']) for field_facet in data_dict['fields']])
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
        start = datetime.strptime(field_facet['start'], '%m-%d-%Y') - datetime.now()
        end = datetime.strptime(field_facet['end'], '%m-%d-%Y') - datetime.now()
        range_facets = tuple([
                           ('facet.date', field_facet['field']),
                           ('f.%s.facet.date.start' % field_facet['field'], 'NOW/DAY%sDAYS' % start.days),
                           ('f.%s.facet.date.end' % field_facet['field'], 'NOW/DAY%sDAY' % end.days),
                           ('f.%s.facet.date.gap' % field_facet['field'], '+%sDAY' % field_facet['gap']),]
                        )
        params += range_facets

    return params


class Result(models.Model):
  _META_TEMPLATE_ATTRS = ['properties', 'template', 'highlighting']

  data = models.TextField()

  def update_from_post(self, post_data):
    data_dict = json.loads(self.data)

    for attr in Result._META_TEMPLATE_ATTRS:
      if post_data.get(attr):
        data_dict[attr] = json.loads(post_data[attr])

    self.data = json.dumps(data_dict)


  def get_template(self, with_highlighting=False):
    data_dict = json.loads(self.data)

    template = data_dict.get('template')
    if with_highlighting:
      for field in data_dict.get('highlighting', []):
        template = re.sub('\{\{%s\}\}' % field, '{{{%s}}}' % field, template)

    return template

  def get_query_params(self):
    data_dict = json.loads(self.data)

    params = ()

    if data_dict.get('highlighting'):
      params += (
        ('hl', data_dict.get('properties', {}).get('highlighting_enabled') and 'true' or 'false'),
        ('hl.fl', ','.join(data_dict.get('highlighting'))),
      )

    return params


class Sorting(models.Model):
  _META_TEMPLATE_ATTRS = ['properties', 'fields']

  data = models.TextField()

  def update_from_post(self, post_data):
    data_dict = json.loads(self.data)

    for attr in Sorting._META_TEMPLATE_ATTRS:
      if post_data.get(attr):
        data_dict[attr] = json.loads(post_data[attr])

    self.data = json.dumps(data_dict)


  def get_query_params(self):
    data_dict = json.loads(self.data)

    params = ()

    if data_dict.get('properties', {}).get('is_enabled') and 'true' or 'false':
      if data_dict.get('fields'):
        fields = ['%s %s' % (field['field'], field['asc'] and 'asc' or 'desc') for field in data_dict.get('fields')]
        params += (
          ('sort', ','.join(fields)),
        )

    return params


  def get_query(self):
    ('sort', solr_query['sort']),


class CoreManager(models.Manager):
  def get_or_create(self, name):
    try:
      return self.get(name=name)
    except Core.DoesNotExist:
      facets = Facet.objects.create(data=json.dumps({
                   'properties': {'is_enabled': False},
                   'ranges': [],
                   'fields': [],
                   'dates': []
                }))
      result = Result.objects.create(data=json.dumps({
                  'template': """
<div class="row-fluid">
  <div class="span1"><img src="http://twitter.com/api/users/profile_image/{{user_screen_name}}" style="margin:10px"></div>
  <div class="span9">
    <h5>{{user_name}}</h5>
    {{text}}
    <br>
    <a href="/filebrowser/view/{{file_path}}">
      {{file_name}} {{content_type}} {{file_length}}{{#file_length}} bytes{{/file_length}}
    </a>
    {{#file_path}}
    <a href="/filebrowser/download{{file_path}}?disposition=inline">
      Download
    </a>
    {{/file_path}}
  </div>
  <div class="span2"><br><a class="btn" href="https://twitter.com/{{user_screen_name}}/status/{{id}}" target="_blank" title="Open in Twitter">
    <i class="icon-twitter"></i></a>
  </div>
</div>
                  """,
                  'highlighting': [],
                  'properties': {'highlighting_enabled': False},
              }))
      sorting = Sorting.objects.create(data=json.dumps({'properties': {'is_enabled': False}, 'fields': []}))

      return Core.objects.create(name=name, label=name, facets=facets, result=result, sorting=sorting)


class Core(models.Model):
  enabled = models.BooleanField(default=True)
  name = models.CharField(max_length=40, unique=True, verbose_name=_t('Solr collection'))
  label = models.CharField(max_length=100)
  # solr_address?
  # results by pages number, autocomplete off...
  properties = models.TextField(default='[]', verbose_name=_t('Core properties'), help_text=_t('Properties (e.g. facets off, results by pages number)'))
  facets = models.ForeignKey(Facet)
  result = models.ForeignKey(Result)
  sorting = models.ForeignKey(Sorting)

  objects = CoreManager()

  def get_query(self):
    return self.facets.get_query_params() + self.result.get_query_params() + self.sorting.get_query_params()

  def get_absolute_url(self):
    return reverse('search:admin_core', kwargs={'core': self.name})

  @property
  def fields(self):
    return ['score'] + sorted([field.get('name') for field in self.fields_data])

  @property
  def fields_data(self):
    solr_schema = SolrApi(SOLR_URL.get()).schema(self.name)
    schema = etree.fromstring(solr_schema)

    return sorted([{'name': field.get('name'),'type': field.get('type')}
                   for fields in schema.iter('fields') for field in fields.iter('field')])

