#!/usr/bin/env python
# -- coding: utf-8 --
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

import logging

from django.core.cache import cache
from django.utils.translation import ugettext as _

from desktop.lib.rest.http_client import RestException, HttpClient
from desktop.lib.rest.resource import Resource
from desktop.lib.i18n import smart_unicode

from metadata.conf import PROMETHEUS


LOG = logging.getLogger(__name__)
VERSION = 'v1'


class PrometheusApiException(Exception):
  def __init__(self, message=None):
    self.message = message or _('No error message, please check the logs.')

  def __str__(self):
    return str(self.message)

  def __unicode__(self):
    return smart_unicode(self.message)


class PrometheusApi(object):

  def __init__(self, user=None, ssl_cert_ca_verify=False):
    self._api_url = '%s/%s' % (PROMETHEUS.API_URL.get().strip('/'), VERSION)

    self.user = user
    self._client = HttpClient(self._api_url, logger=LOG)

    self._client.set_verify(ssl_cert_ca_verify)
    self._root = Resource(self._client)


  def query(self, query):
    try:
      return self._root.get('query', {
        'query': query,
      })['data']
    except RestException, e:
      raise PrometheusApiException(e)

  def range_query(self, query, start, end, step):
    # e.g. /api/v1/query_range?query=up&start=2015-07-01T20:10:30.781Z&end=2015-07-01T20:11:00.781Z&step=15s
    try:
      return self._root.get('query_range', {
        'query': query,
        'start': start,
        'end': end,
        'step': step
      })['data']
    except RestException, e:
      raise PrometheusApiException(e)
