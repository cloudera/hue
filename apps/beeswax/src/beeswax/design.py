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

"""
The HQLdesign class can (de)serialize a design to/from a QueryDict.
"""

import json
import logging
import re
import urlparse

import django.http
from django import forms

from desktop.lib.django_forms import BaseSimpleFormSet, MultiForm
from desktop.lib.django_mako import render_to_string
from hadoop.cluster import get_hdfs


LOG = logging.getLogger(__name__)

SERIALIZATION_VERSION = '0.4.1'


def hql_query(hql, database='default', query_type=None):
  data_dict = json.loads('{"query": {"email_notify": false, "query": null, "type": 0, "is_parameterized": true, "database": "default"}, '
                               '"functions": [], "VERSION": "0.4.1", "file_resources": [], "settings": []}')
  if not (isinstance(hql, str) or isinstance(hql, unicode)):
    raise Exception('Requires a SQL text query of type <str>, <unicode> and not %s' % type(hql))

  data_dict['query']['query'] = strip_trailing_semicolon(hql)
  data_dict['query']['database'] = database
  if query_type:
    data_dict['query']['type'] = query_type
  hql_design = HQLdesign()
  hql_design._data_dict = data_dict

  return hql_design


class HQLdesign(object):
  """
  Represents an HQL design, with methods to perform (de)serialization.

  We support queries that aren't parameterized, in case users
  want to use "$" natively, but we leave that as an advanced
  option to turn off.
  """
  _QUERY_ATTRS = [ 'query', 'type', 'is_parameterized', 'email_notify', 'database' ]
  _SETTINGS_ATTRS = [ 'key', 'value' ]
  _FILE_RES_ATTRS = [ 'type', 'path' ]
  _FUNCTIONS_ATTRS = [ 'name', 'class_name' ]

  def __init__(self, form=None, query_type=None):
    """Initialize the design from a valid form data."""
    if form is not None:
      assert isinstance(form, MultiForm)
      self._data_dict = {
          'query': normalize_form_dict(form.query, HQLdesign._QUERY_ATTRS),
          'settings': normalize_formset_dict(form.settings, HQLdesign._SETTINGS_ATTRS),
          'file_resources': normalize_formset_dict(form.file_resources, HQLdesign._FILE_RES_ATTRS),
          'functions': normalize_formset_dict(form.functions, HQLdesign._FUNCTIONS_ATTRS)
      }
      if query_type is not None:
        self._data_dict['query']['type'] = query_type

  def dumps(self):
    """Returns the serialized form of the design in a string"""
    dic = self._data_dict.copy()
    dic['VERSION'] = SERIALIZATION_VERSION
    return json.dumps(dic)

  @property
  def hql_query(self):
    return self._data_dict['query']['query']

  @hql_query.setter
  def hql_query(self, query):
    self._data_dict['query']['query'] = query

  @property
  def query(self):
    return self._data_dict['query'].copy()

  @property
  def settings(self):
    return list(self._data_dict['settings'])

  @property
  def file_resources(self):
    return list(self._data_dict['file_resources'])

  @property
  def functions(self):
    return list(self._data_dict['functions'])

  def get_configuration_statements(self):
    configuration = []

    for f in self.file_resources:
      if not urlparse.urlsplit(f['path']).scheme:
        scheme = get_hdfs().fs_defaultfs
      else:
        scheme = ''
      configuration.append(render_to_string("hql_resource.mako", dict(type=f['type'], path=f['path'], scheme=scheme)))

    for f in self.functions:
      configuration.append(render_to_string("hql_function.mako", f))

    return configuration

  def get_query_dict(self):
    # We construct the mform to use its structure and prefix. We don't actually bind data to the forms.
    from beeswax.forms import QueryForm
    mform = QueryForm()
    mform.bind()

    res = django.http.QueryDict('', mutable=True)
    res.update(denormalize_form_dict(
                self._data_dict['query'], mform.query, HQLdesign._QUERY_ATTRS))
    res.update(denormalize_formset_dict(
                self._data_dict['settings'], mform.settings, HQLdesign._SETTINGS_ATTRS))
    res.update(denormalize_formset_dict(
                self._data_dict['file_resources'], mform.file_resources, HQLdesign._FILE_RES_ATTRS))
    res.update(denormalize_formset_dict(
                self._data_dict['functions'], mform.functions, HQLdesign._FUNCTIONS_ATTRS))
    return res

  @staticmethod
  def loads(data):
    """Returns an HQLdesign from the serialized form"""
    dic = json.loads(data)
    dic = dict(map(lambda k: (str(k), dic.get(k)), dic.keys()))
    if dic['VERSION'] != SERIALIZATION_VERSION:
      LOG.error('Design version mismatch. Found %s; expect %s' % (dic['VERSION'], SERIALIZATION_VERSION))

    # Convert to latest version
    del dic['VERSION']
    if 'type' not in dic['query'] or dic['query']['type'] is None:
      dic['query']['type'] = 0
    if 'database' not in dic['query']:
      dic['query']['database'] = 'default'

    design = HQLdesign()
    design._data_dict = dic
    return design

  def get_query(self):
    return self._data_dict["query"]

  @property
  def statement_count(self):
    return len(self.statements)

  def get_query_statement(self, n=0):
    return self.statements[n]

  @property
  def statements(self):
    hql_query = strip_trailing_semicolon(self.hql_query)
    return [strip_trailing_semicolon(statement.strip()) for statement in split_statements(hql_query)]

  def __eq__(self, other):
    return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

  def __ne__(self, other):
    return not self.__eq__(other)


def split_statements(hql):
  """
  Just check if the semicolon is between two non escaped quotes,
  meaning it is inside a string or a real separator.
  """
  statements = []
  current = ''
  prev = ''
  between_quotes = None

  for c in hql:
    current += c
    if c in ('"', "'") and prev != '\\':
      if between_quotes == c:
        between_quotes = None
      elif between_quotes is None:
        between_quotes = c
    elif c == ';':
      if between_quotes is None:
        statements.append(current)
        current = ''
    prev = c

  if current and current != ';':
    statements.append(current)

  return statements


def normalize_form_dict(form, attr_list):
  """
  normalize_form_dict(form, attr_list) -> A dictionary of (attr, value)

  Each attr is a field name. And the value is obtained by looking up the form's data dict.
  """
  assert isinstance(form, forms.Form)
  res = { }
  for attr in attr_list:
    res[attr] = form.cleaned_data.get(attr)
  return res


def normalize_formset_dict(formset, attr_list):
  """
  normalize_formset_dict(formset, attr_list) -> A list of dictionary of (attr, value)
  """
  assert isinstance(formset, BaseSimpleFormSet)
  res = [ ]
  for form in formset.forms:
    res.append(normalize_form_dict(form, attr_list))
  return res


def denormalize_form_dict(data_dict, form, attr_list):
  """
  denormalize_form_dict(data_dict, form, attr_list) -> A QueryDict with the attributes set
  """
  assert isinstance(form, forms.Form)
  res = django.http.QueryDict('', mutable=True)
  for attr in attr_list:
    try:
      res[str(form.add_prefix(attr))] = data_dict[attr]
    except KeyError:
      pass
  return res


def denormalize_formset_dict(data_dict_list, formset, attr_list):
  """
  denormalize_formset_dict(data_dict, form, attr_list) -> A QueryDict with the attributes set
  """
  assert isinstance(formset, BaseSimpleFormSet)
  res = django.http.QueryDict('', mutable=True)
  for i, data_dict in enumerate(data_dict_list):
    prefix = formset.make_prefix(i)
    form = formset.form(prefix=prefix)
    res.update(denormalize_form_dict(data_dict, form, attr_list))
    res[prefix + '-_exists'] = 'True'

  res[str(formset.management_form.add_prefix('next_form_id'))] = str(len(data_dict_list))
  return res

  def __str__(self):
    return '%s: %s' % (self.__class__, self.query)


_SEMICOLON_WHITESPACE = re.compile(";\s*$")

def strip_trailing_semicolon(query):
  """As a convenience, we remove trailing semicolons from queries."""
  s = _SEMICOLON_WHITESPACE.split(query, 2)
  if len(s) > 1:
    assert len(s) == 2
    assert s[1] == ''
  return s[0]
