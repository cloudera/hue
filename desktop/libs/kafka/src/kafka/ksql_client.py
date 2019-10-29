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

from builtins import object
import logging
import json

from django.core.cache import cache
from django.utils.translation import ugettext as _

from desktop.lib.i18n import smart_unicode

from kafka.conf import KAFKA
from libzookeeper.conf import zkensemble


LOG = logging.getLogger(__name__)


class KSqlApiException(Exception):
  def __init__(self, message=None):
    self.message = message or _('No error message, please check the logs.')

  def __str__(self):
    return str(self.message)

  def __unicode__(self):
    return smart_unicode(self.message)


class KSqlApi(object):
  """
  https://pypi.org/project/ksql/

  pip install ksql
  """

  def __init__(self, user=None, security_enabled=False, ssl_cert_ca_verify=False):
    try:
      from ksql import KSQLAPI
    except ImportError:
      raise KSqlApiException('Module missing: pip install ksql')

    self._api_url = KAFKA.KSQL_API_URL.get().strip('/') if KAFKA.KSQL_API_URL.get() else ''

    self.user = user
    self.client = client = KSQLAPI(self._api_url)


  def show_tables(self):
    try:
      response = self._client.ksql('show tables')
      return json.loads(response)['tables']['tables']
    except RestException as e:
      raise KafkaApiException(e)


  def query(self, statement):
    result = []

    for line in self._client.query(statement):
      data_line = json.loads(line)
      result.append(data_line['row']['columns']) # TODO: streams, dataline['errorMessage']

    return result
