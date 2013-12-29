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

import django.http
from django.utils.translation import ugettext as _

from beeswax.design import normalize_form_dict, denormalize_form_dict


LOG = logging.getLogger(__name__)

SERIALIZATION_VERSION = "1.0"


class SparkDesign(object):
  _QUERY_ATTRS = ['type', 'appName', 'classPath', 'autoContext', 'context', 'params']

  def __init__(self, form=None, query_type=None):
    if form is not None:
      self._data_dict = {'query': normalize_form_dict(form, SparkDesign._QUERY_ATTRS)}
      if query_type is not None:
        self._data_dict['query']['type'] = query_type

  def dumps(self):
    """Returns the serialized form of the design in a string"""
    dic = self._data_dict.copy()
    dic['VERSION'] = SERIALIZATION_VERSION
    return json.dumps(dic)

  @property
  def query(self):
    return self._data_dict['query'].copy()

  @property
  def appName(self):
    return self._data_dict['query']['appName']

  @property
  def classPath(self):
    return self._data_dict['query']['classPath']

  @property
  def autoContext(self):
    return self._data_dict['query']['autoContext']

  @property
  def context(self):
    return self._data_dict['query']['context']

  @property
  def params(self):
    return self._data_dict['query']['params']

  def get_query_dict(self):
    # We construct the form to use its structure and prefix. We don't actually bind data to the forms.
    from beeswax.forms import QueryForm
    mform = QueryForm()
    mform.bind()

    res = django.http.QueryDict('', mutable=True)
    res.update(denormalize_form_dict(self._data_dict['query'], mform.query, SparkDesign._QUERY_ATTRS))
    return res

  @staticmethod
  def loads(data):
    if data:
      dic = json.loads(data)
      dic = dict(map(lambda k: (str(k), dic.get(k)), dic.keys()))
    else:
      dic = {
          'VERSION': SERIALIZATION_VERSION,
          'query': {
              'type': 3, 'appName': '', 'classPath': 'spark.jobserver.WordCountExample', 'autoContext': True, 'context': '',
              'params': json.dumps([])
          }
      }

    if dic['VERSION'] != SERIALIZATION_VERSION:
      LOG.error('Design version mismatch. Found %s; expect %s' % (dic['VERSION'], SERIALIZATION_VERSION))

    # Convert to latest version
    del dic['VERSION']
    if 'type' not in dic['query'] or dic['query']['type'] is None:
      dic['query']['type'] = 0
    if 'appName' not in dic['query']:
      dic['query']['appName'] = ''
    if 'classPath' not in dic['query']:
      dic['query']['classPath'] = ''
    if 'autoContext' not in dic['query']:
      dic['query']['autoContext'] = True
    if 'context' not in dic['query']:
      dic['query']['context'] = ''
    if 'params' not in dic['query']:
      dic['query']['params'] = json.dumps([])

    design = SparkDesign()
    design._data_dict = dic
    return design
