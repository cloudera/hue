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

from lxml import etree

try:
  import json
except ImportError:
  import simplejson as json

import logging

from django.db import models
from django.utils.translation import ugettext as _, ugettext_lazy as _t
from django.core.urlresolvers import reverse
from mako.template import Template

from search.api import SolrApi
from search.conf import SOLR_URL

LOG = logging.getLogger(__name__)


class RangeFacet(object): pass
class DateFacet(object): pass


class Facet(models.Model):
  _ATTRIBUTES = ['properties', 'fields', 'range', 'date']
  
  enabled = models.BooleanField(default=True)
  data = models.TextField()

  def update_from_post(self, post_data):
    data_dict = json.loads(self.data)

    if post_data.get('fields'):
      data_dict['fields'] = json.loads(post_data['fields'])

    if post_data.get('ranges'):
      data_dict['ranges'] = json.loads(post_data['ranges'])

    if post_data.get('dates'):
      data_dict['dates'] = json.loads(post_data['dates'])

    self.data = json.dumps(data_dict)


  def get_query_params(self):
    data_dict = json.loads(self.data)

    params = (
        ('facet', 'true'),
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
        range_facets = tuple([
                           ('facet.date', field_facet['field']),
                           ('f.%s.facet.date.start' % field_facet['field'], 'NOW/DAY-305DAYS'),
                           ('f.%s.facet.date.end' % field_facet['field'], 'NOW/DAY+1DAY'),
                           ('f.%s.facet.date.gap' % field_facet['field'], '+%sDAY' % field_facet['gap']),]
                        )
        params += range_facets
 
    return params


class Result(models.Model):
  _META_TEMPLATE_ATTRS = ['template', 'highlighted_fields', 'css']

  data = models.TextField()

  def update_from_post(self, post_data):
    data_dict = json.loads(self.data)

    if post_data.get('template'):
      data_dict['template'] = json.loads(post_data['template'])

    self.data = json.dumps(data_dict)


  def get_template(self):
    data_dict = json.loads(self.data)

    return data_dict.get('template')


  def render_result(self, result):
    return Template(self.get_template()).render(result=result)


class Sorting(models.Model):
  _META_TEMPLATE_ATTRS = ['fields']

  data = models.TextField()

  def update_from_post(self, post_data):
    data_dict = json.loads(self.data)

    if post_data.get('fields'):
      data_dict['fields'] = json.loads(post_data['fields'])

    self.data = json.dumps(data_dict)  


class Core(models.Model):
  enabled = models.BooleanField(default=True)
  name = models.CharField(max_length=40, unique=True, help_text=_t('Name of the Solr collection'))
  label = models.CharField(max_length=100)
  properties = models.TextField(default='[]', verbose_name=_t('Core properties'), help_text=_t('Properties (e.g. facets off, results by pages number)'))
  
  facets = models.ForeignKey(Facet)
  result = models.ForeignKey(Result)
  sorting = models.ForeignKey(Sorting)

  def get_query(self):
    return self.facets.get_query_params()

  def get_absolute_url(self):
    return reverse('search:admin_core_properties', kwargs={'core': self.name})

  @property
  def fields(self):
    solr_schema = SolrApi(SOLR_URL.get()).schema(self.name)
    schema = etree.fromstring(solr_schema)

    return [field.get('name') for fields in schema.iter('fields') for field in fields.iter('field')]


class Query(object): pass


def temp_fixture_hook():
  #Core.objects.all().delete()
  if not Core.objects.exists():
    facets = Facet.objects.create(data=json.dumps({
                 'ranges': [{"type":"range","field":"price","start":"1","end":"400","gap":"100"}],
                 'fields': [{"type":"field","field":"id"}],
                 'dates': [{"type":"date","field":"last_modified","start":"02-13-2013","end":"02-19-2013","gap":"1"}]
              }))
    result = Result.objects.create(data=json.dumps({'template': 'To customize!<br/>'}))
    sorting = Sorting.objects.create(data=json.dumps({'fields': [{"field":"id","label":"My id","asc":False}]}))

    Core.objects.create(name='collection1', label='Tweets', facets=facets, result=result, sorting=sorting)
    Core.objects.create(name='collection2', label='Zendesk Tickets', facets=facets, result=result, sorting=sorting)
