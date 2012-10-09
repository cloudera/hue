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

import logging
import re
import simplejson

import django.http
from django import forms

from desktop.lib.django_forms import BaseSimpleFormSet, MultiForm
from desktop.lib.django_mako import render_to_string


LOG = logging.getLogger(__name__)

SERIALIZATION_VERSION = '0.4.0'


def hql_query(hql):
  data_dict = simplejson.loads('{"query": {"email_notify": null, "query": null, "type": null, "is_parameterized": null}, '
                               '"functions": [], "VERSION": "0.4.0", "file_resources": [], "settings": []}')
  if not (isinstance(hql, str) or isinstance(hql, unicode)):
    raise Exception('Requires a SQL text query of type <str>, <unicode> and not %s' % type(hql))

  data_dict['query']['query'] = _strip_trailing_semicolon(hql)
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
  _QUERY_ATTRS = [ 'query', 'type', 'is_parameterized', 'email_notify' ]
  _SETTINGS_ATTRS = [ 'key', 'value' ]
  _FILE_RES_ATTRS = [ 'type', 'path' ]
  _FUNCTIONS_ATTRS = [ 'name', 'class_name' ]

  def __init__(self, form=None):
    """Initialize the design from a valid form data."""
    if form is not None:
      assert isinstance(form, MultiForm)
      self._data_dict = dict(
          query = normalize_form_dict(form.query, HQLdesign._QUERY_ATTRS),
          settings = normalize_formset_dict(form.settings, HQLdesign._SETTINGS_ATTRS),
          file_resources = normalize_formset_dict(form.file_resources, HQLdesign._FILE_RES_ATTRS),
          functions = normalize_formset_dict(form.functions, HQLdesign._FUNCTIONS_ATTRS))

  def dumps(self):
    """Returns the serialized form of the design in a string"""
    dic = self._data_dict.copy()
    dic['VERSION'] = SERIALIZATION_VERSION
    return simplejson.dumps(dic)

  @property
  def hql_query(self):
    return self._data_dict['query']['query']

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

  def get_configuration(self):
    configuration = []

    for f in self.settings:
      configuration.append(render_to_string("hql_set.mako", f))

    for f in self.file_resources:
      configuration.append(render_to_string("hql_resource.mako", dict(type=f['type'], path=f['path'])))

    for f in self.functions:
      configuration.append(render_to_string("hql_function.mako", f))

    return configuration

  def get_query_dict(self):
    """get_query_dict() -> QueryDict"""
    # We construct the mform to use its structure and prefix. We don't actually bind
    # data to the forms.
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
    dic = simplejson.loads(data)
    if dic['VERSION'] != SERIALIZATION_VERSION:
      LOG.error('Design version mismatch. Found %s; expect %s' %
                (dic['VERSION'], SERIALIZATION_VERSION))
      return None
    del dic['VERSION']

    design = HQLdesign.__new__(HQLdesign)
    design._data_dict = dic
    return design

  def get_query(self):
    return self._data_dict["query"]

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
      res[form.add_prefix(attr)] = data_dict[attr]
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

  res[formset.management_form.add_prefix('next_form_id')] = str(len(data_dict_list))
  return res

  def __str__(self):
    return '%s: %s' % (self.__class__, self.query)


_SEMICOLON_WHITESPACE = re.compile(";\s*$")

def _strip_trailing_semicolon(query):
  """As a convenience, we remove trailing semicolons from queries."""
  s = _SEMICOLON_WHITESPACE.split(query, 2)
  if len(s) > 1:
    assert len(s) == 2
    assert s[1] == ''
  return s[0]
