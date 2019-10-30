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
from desktop.lib.rest.http_client import RestException

from kafka.conf import KAFKA


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
      response = self.client.ksql('SHOW TABLES')
      return response[0]['tables']
    except Exception as e:
      raise KSqlApiException(e)


  def ksql(self, statement):
    response = self.client.ksql(statement)
    print(response)
    return response[0]


  def query(self, statement):
    data = []
    metadata = []

    if statement.strip().lower().startswith('select') or statement.strip().lower().startswith('print'):
      # STREAMS requires a LIMIT currently or will hang without https://github.com/bryanyang0528/ksql-python/pull/60
      result = self.client.query(statement)
      for line in ''.join(list(result)).split('\n'):
        # Until https://github.com/bryanyang0528/ksql-python/issues/57
        # columns = line.keys()
        # data.append([line[col] for col in columns])
        data.append([line])
        # TODO: WS to plug-in
      metadata = [['Row', 'STRING']]
    else:
      data, metadata = self._decode_result(
        self.ksql(statement)
      )

    return data, metadata


  def _decode_result(self, result):
    columns = []
    data = []

    if result['@type'] == 'statement_error':
      raise KSqlApiException(result['message'])
    elif result['@type'] == 'kafka_topics':
      columns = result['topics'][0].keys()
      for line in result['topics']:
        row = []
        for column in columns:
          row.append(
            json.dumps(line[column])
          )
        data.append(row)
    elif result['@type'] == 'sourceDescription':
      columns = ['name', 'description']
      for key in result['sourceDescription']:
        if key == 'fields':
          data.append(['', ''])
          data.append(['Fields:', ''])
          for field in result['sourceDescription'][key]:
            data.append([field['name'], field['schema']['type']])
          data.append(['', ''])
        else:
          data.append([key, result['sourceDescription'][key]])
    elif result['@type'] == 'currentStatus':
      data.append([result['commandStatus']['status']])
      data.append([result['commandStatus']['message']])

    columns = [[col, 'STRING'] for col in columns]

    return data, columns
