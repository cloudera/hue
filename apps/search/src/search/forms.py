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


import math

from django import forms
from django.utils.translation import ugettext as _
from search.models import Collection
from search_controller import SearchController


class QueryForm(forms.Form):
  collection = forms.ChoiceField() # Aka collection_id

  query = forms.CharField(label='', max_length=256, required=False, initial='',
                          widget=forms.TextInput(attrs={'class': 'search-query input-xxlarge', 'data-bind': 'value: q'}))
  fq = forms.CharField(label='', max_length=256, required=False, initial='', widget=forms.HiddenInput(), help_text='Solr Filter query')
  sort = forms.CharField(label='', max_length=256, required=False, initial='', widget=forms.HiddenInput(), help_text='Solr sort')
  rows = forms.CharField(label='', required=False, initial='', widget=forms.HiddenInput(), help_text='Solr records per page')
  start = forms.CharField(label='', required=False, initial='', widget=forms.HiddenInput(), help_text='Solr start record')
  facets = forms.CharField(label='', required=False, initial='', widget=forms.HiddenInput(), help_text='Show hide facet search')

  def __init__(self, *args, **kwargs):
    self.initial_collection = kwargs.pop('initial_collection')
    super(QueryForm, self).__init__(*args, **kwargs)
    choices = [(core.id, core.label) for core in Collection.objects.filter(enabled=True)]
    # Beware: initial not working, set in the js
    self.fields['collection'] = forms.ChoiceField(choices=choices, initial=self.initial_collection, required=False, label='', widget=forms.Select(attrs={'class':'hide'}))

  def clean_collection(self):
    if self.cleaned_data.get('collection'):
      return self.cleaned_data['collection']
    else:
      return self.initial_collection

  @property
  def solr_query_dict(self):
    solr_query = {}

    if self.is_valid():
      solr_query['q'] = self.cleaned_data['query'].encode('utf8')
      solr_query['fq'] = self.cleaned_data['fq']
      if self.cleaned_data['sort']:
        solr_query['sort'] = self.cleaned_data['sort']
      solr_query['rows'] = self.cleaned_data['rows'] or 15
      solr_query['start'] = self.cleaned_data['start'] or 0
      solr_query['facets'] = self.cleaned_data['facets'] or 1
      solr_query['current_page'] = int(math.ceil((float(solr_query['start']) + 1) / float(solr_query['rows'])))
      solr_query['total_pages'] = 0
      solr_query['search_time'] = 0
      solr_query['collection'] = Collection.objects.get(id=self.cleaned_data['collection']).name
    
    return solr_query


class HighlightingForm(forms.Form):
  fields = forms.MultipleChoiceField(required=False)
  is_enabled = forms.BooleanField(label='Enabled', initial=True, required=False)

  def __init__(self, *args, **kwargs):
    fields = kwargs.pop('fields')
    super(HighlightingForm, self).__init__(*args, **kwargs)
    self.fields['fields'].choices = ((name, name) for name in fields)



class CollectionForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user', None)
    super(CollectionForm, self).__init__(*args, **kwargs)

  class Meta:
    model = Collection
    exclude = ('facets', 'result', 'sorting', 'properties', 'cores')

  def clean_name(self):
    searcher = SearchController(self.user)
    name = self.cleaned_data['name']
    if not searcher.is_collection(name) and not searcher.is_core(name):
      raise forms.ValidationError(_('No live Solr collection or core by the name %s.') % name)
    return name
