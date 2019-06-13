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
import os
import re
import urlparse

import django.http
from django import forms
from django.forms import ValidationError
from django.utils.translation import ugettext as _

from notebook.sql_utils import split_statements, strip_trailing_semicolon
from desktop.lib.django_forms import BaseSimpleFormSet, MultiForm
from hadoop.cluster import get_hdfs


LOG = logging.getLogger(__name__)

SERIALIZATION_VERSION = '0.4.1'


def hql_query(hql, database='default', query_type=None, settings=None, file_resources=None, functions=None):
  data_dict = HQLdesign.get_default_data_dict()

  if not (isinstance(hql, str) or isinstance(hql, unicode)):
    raise Exception('Requires a SQL text query of type <str>, <unicode> and not %s' % type(hql))

  data_dict['query']['query'] = strip_trailing_semicolon(hql)
  data_dict['query']['database'] = database

  if query_type:
    data_dict['query']['type'] = query_type

  if settings is not None and HQLdesign.validate_properties('settings', settings, HQLdesign._SETTINGS_ATTRS):
    data_dict['settings'] = settings

  if file_resources is not None and HQLdesign.validate_properties('file resources', file_resources, HQLdesign._FILE_RES_ATTRS):
    data_dict['file_resources'] = file_resources

  if functions is not None and HQLdesign.validate_properties('functions', functions, HQLdesign._FUNCTIONS_ATTRS):
    data_dict['functions'] = functions

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

  @property
  def database(self):
    return self._data_dict['query']['database']

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
    return list(self._data_dict.get('settings', []))

  @property
  def file_resources(self):
    return list(self._data_dict.get('file_resources', []))

  @property
  def functions(self):
    return list(self._data_dict.get('functions', []))

  @property
  def statement_count(self):
    return len(self.statements)

  @property
  def statements(self):
    hql_query = strip_trailing_semicolon(self.hql_query)
    return [strip_trailing_semicolon(statement) for (start_row, start_col), (end_row, end_col), statement in split_statements(hql_query)]

  @staticmethod
  def get_default_data_dict():
    return {
      'query': {
        'email_notify': False,
        'query': None,
        'type': 0,
        'is_parameterized': True,
        'database': 'default'
      },
      'functions': [],
      'VERSION': SERIALIZATION_VERSION,
      'file_resources': [],
      'settings': []
    }

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

  @staticmethod
  def validate_properties(property_type, properties, req_attr_list):
    """
    :param property_type: 'Settings', 'File Resources', or 'Functions'
    :param properties: list of properties as dict
    :param req_attr_list: list of attributes that are required keys for each dict item
    """
    if isinstance(properties, list) and all(isinstance(item, dict) for item in properties):
      for item in properties:
        if not all(attr in item for attr in req_attr_list):
          raise ValidationError(_("Invalid %s, missing required attributes: %s.") % (property_type, ', '.join(req_attr_list)))
    else:
      raise ValidationError(_('Invalid settings, expected list of dict items.'))
    return True

  def dumps(self):
    """Returns the serialized form of the design in a string"""
    dic = self._data_dict.copy()
    dic['VERSION'] = SERIALIZATION_VERSION
    return json.dumps(dic)

  def get_configuration_statements(self):
    configuration = []

    for f in self.file_resources:
      if not urlparse.urlsplit(f['path']).scheme:
        scheme = get_hdfs().fs_defaultfs
      else:
        scheme = ''
      configuration.append('ADD %(type)s %(scheme)s%(path)s' %
                           {'type': f['type'].upper(), 'path': f['path'], 'scheme': scheme})

    for f in self.functions:
      configuration.append("CREATE TEMPORARY FUNCTION %(name)s AS '%(class_name)s'" %
                           {'name': f['name'], 'class_name': f['class_name']})

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

  def get_query(self):
    return self._data_dict["query"]

  def get_query_statement(self, n=0):
    return self.statements[n]

  def __eq__(self, other):
    return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

  def __ne__(self, other):
    return not self.__eq__(other)


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
