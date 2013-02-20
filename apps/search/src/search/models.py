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
  _ATTRIBUTES = ['properties', 'fields', 'range', 'date'] # Metadata of the data, only 'fields' used currently
  enabled = models.BooleanField(default=True)
  data = models.TextField()

  def dumps(self):
    pass

  def loads(self, json):
    pass

  def update_from_post(self, post_data):
    data_dict = json.loads(self.data)

    if 'fields' in post_data and post_data['fields']:
      data_dict['fields'] = json.loads(post_data['fields'])

    self.data = json.dumps(data_dict)

  def get_query_params(self):
    data_dict = json.loads(self.data)

    params = (
        ('facet', 'true'),
        ('facet.limit', 10),
        ('facet.mincount', 1),
        ('facet.sort', 'count'),
    )

    if 'fields' in data_dict and data_dict['fields']:
      field_facets = tuple([('facet.field', field_facet) for field_facet in data_dict['fields']])
      params += field_facets

    return params

# e.g.
#                ('facet.range', 'retweet_count'),
#                ('f.retweet_count.facet.range.start', '0'),
#                ('f.retweet_count.facet.range.end', '100'),
#                ('f.retweet_count.facet.range.gap', '10'),
#
#                ('facet.date', 'created_at'),
#                ('facet.date.start', 'NOW/DAY-305DAYS'),
#                ('facet.date.end', 'NOW/DAY+1DAY'),
#                ('facet.date.gap', '+1DAY'),


class Result(models.Model):
  _META_TEMPLATE_ATTRS = ['template', 'highlighted_fields', 'css']

  def __init__(self, *args, **kwargs):
    super(Result, self).__init__(*args, **kwargs)
    self._data_dict = []

  data = models.TextField()

  def gen_template(self):
    return """
      <tr>
        <td style="word-wrap: break-word;">
          <div class="content">
            <div class="text">
              ${ result.get('id', '')  | n,unicode }
            </div>
          </div>
        </td>
      </tr>"""

  def gen_result(self, result):
    return Template(self.gen_template()).render(result=result)


class Sorting(models.Model): pass


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
    facets = Facet.objects.create(data=json.dumps({'fields': ['id']}))
    result = Result.objects.create()
    sorting = Sorting.objects.create()

    Core.objects.create(name='collection1', label='Tweets', facets=facets, result=result, sorting=sorting)
    Core.objects.create(name='collection2', label='Zendesk Tickets', facets=facets, result=result, sorting=sorting)
