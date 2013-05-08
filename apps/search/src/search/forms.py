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


from django import forms
from search.models import Collection


class QueryForm(forms.Form):
  collection = forms.ChoiceField()

  query = forms.CharField(label='', max_length=256, required=False, initial='',
                          widget=forms.TextInput(attrs={'class': 'search-query input-xxlarge', 'placeholder': 'Search...'}))
  fq = forms.CharField(label='', max_length=256, required=False, initial='', widget=forms.HiddenInput(), help_text='Solr Filter query')
  sort = forms.CharField(label='', max_length=256, required=False, initial='', widget=forms.HiddenInput(), help_text='Solr sort')
  rows = forms.CharField(label='', required=False, initial='', widget=forms.HiddenInput(), help_text='Solr records per page')
  start = forms.CharField(label='', required=False, initial='', widget=forms.HiddenInput(), help_text='Solr start record')
  facets = forms.CharField(label='', required=False, initial='', widget=forms.HiddenInput(), help_text='Show hide facet search')

  def __init__(self, *args, **kwargs):
    super(QueryForm, self).__init__(*args, **kwargs)
    choices = [(core.name, core.label) for core in Collection.objects.filter(enabled=True)]
    initial_choice = self._initial_core(choices)
    self.fields['collection'] = forms.ChoiceField(choices=choices, initial=initial_choice, required=False, label='', widget=forms.Select(attrs={'class':'hide'}))

  def clean_collection(self):
    if self.cleaned_data.get('collection'):
      return self.cleaned_data['collection']
    else:
      return self._initial_core(self.fields['collection'].choices)


  def _initial_core(self, choices):
    return choices and choices[0][0] or None


class HighlightingForm(forms.Form):
  fields = forms.MultipleChoiceField(required=False)
  is_enabled = forms.BooleanField(label='Enabled', initial=True, required=False)

  def __init__(self, *args, **kwargs):
    fields = kwargs.pop('fields')
    super(HighlightingForm, self).__init__(*args, **kwargs)
    self.fields['fields'].choices = ((name, name) for name in fields)



class CollectionForm(forms.ModelForm):
  class Meta:
    model = Collection
    exclude = ('facets', 'result', 'sorting', 'properties')
