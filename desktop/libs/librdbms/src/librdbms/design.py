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

import django.http
from django.utils.translation import ugettext as _

from beeswax.design import normalize_form_dict, denormalize_form_dict, split_statements
from notebook.sql_utils import strip_trailing_semicolon

LOG = logging.getLogger(__name__)

SERIALIZATION_VERSION = "0.0.1"


class SQLdesign(object):
  """
  Represents an SQL design, with methods to perform (de)serialization.
  """
  _QUERY_ATTRS = [ 'query', 'type', 'database', 'server' ]

  def __init__(self, form=None, query_type=None):
    """Initialize the design from a valid form data."""
    if form is not None:
      self._data_dict = dict(query = normalize_form_dict(form, SQLdesign._QUERY_ATTRS))
      if query_type is not None:
        self._data_dict['query']['type'] = query_type

  def dumps(self):
    """Returns the serialized form of the design in a string"""
    dic = self._data_dict.copy()
    dic['VERSION'] = SERIALIZATION_VERSION
    return json.dumps(dic)

  @property
  def sql_query(self):
    return self._data_dict['query']['query']

  @property
  def query(self):
    return self._data_dict['query'].copy()

  @property
  def server(self):
    return self._data_dict['query']['server']

  @property
  def database(self):
    return self._data_dict['query']['database']

  def get_query_dict(self):
    # We construct the mform to use its structure and prefix. We don't actually bind data to the forms.
    from beeswax.forms import QueryForm
    mform = QueryForm()
    mform.bind()

    res = django.http.QueryDict('', mutable=True)
    res.update(denormalize_form_dict(
                self._data_dict['query'], mform.query, SQLdesign._QUERY_ATTRS))
    return res

  def get_query(self):
    return self._data_dict["query"]

  @property
  def statement_count(self):
    return len(self.statements)

  def get_query_statement(self, n=0):
    return self.statements[n]

  @property
  def statements(self):
    sql_query = strip_trailing_semicolon(self.sql_query)
    return [strip_trailing_semicolon(statement.strip()) for (start_row, start_col), (end_row, end_col), statement in split_statements(sql_query)]

  @staticmethod
  def loads(data):
    """Returns SQLdesign from the serialized form"""
    dic = json.loads(data)
    dic = dict(map(lambda k: (str(k), dic.get(k)), dic.keys()))
    if dic['VERSION'] != SERIALIZATION_VERSION:
      LOG.error('Design version mismatch. Found %s; expect %s' % (dic['VERSION'], SERIALIZATION_VERSION))

    # Convert to latest version
    del dic['VERSION']
    if 'type' not in dic['query'] or dic['query']['type'] is None:
      dic['query']['type'] = 0
    if 'server' not in dic['query']:
      raise RuntimeError(_('No server!'))
    if 'database' not in dic['query']:
      raise RuntimeError(_('No database!'))

    design = SQLdesign()
    design._data_dict = dic
    return design