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
import sys

from django.core.cache import cache

from desktop.lib.i18n import smart_unicode
from desktop.lib.rest.http_client import RestException
from desktop.conf import has_channels

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _

if has_channels():
  from notebook.consumer import _send_to_channel


LOG = logging.getLogger()


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

  https://github.com/bryanyang0528/ksql-python/pull/60 fixes:
  - STREAMS requires a LIMIT currently or will hang or run forever
  - https://github.com/bryanyang0528/ksql-python/issues/57
  """

  def __init__(self, user=None, url=None, security_enabled=False, ssl_cert_ca_verify=False):
    try:
      from ksql import KSQLAPI
    except ImportError:
      raise KSqlApiException('Module missing: pip install ksql')

    self._api_url = url.strip('/')
    self.user = user

    self.client = client = KSQLAPI(self._api_url)


  def show_tables(self):
    try:
      response = self.client.ksql('SHOW TABLES')
      return response[0]['tables']
    except Exception as e:
      raise KSqlApiException(e)


  def show_topics(self):
    try:
      response = self.client.ksql('SHOW TOPICS')
      return response[0]['topics']
    except Exception as e:
      raise KSqlApiException(e)


  def show_streams(self):
    try:
      response = self.client.ksql('SHOW STREAMS')
      return response[0]['streams']
    except Exception as e:
      raise KSqlApiException(e)


  def get_columns(self, table):
    try:
      response = self.client.ksql('DESCRIBE %s' % table)
      return response[0]['sourceDescription']['fields']
    except Exception as e:
      raise KSqlApiException(e)


  def ksql(self, statement):
    response = self.client.ksql(statement)
    LOG.debug('ksqlDB response: %s' % response)
    return response[0] if response else {'@type': 'queries', 'queries': []}  # INSERTs return empty currently


  def query(self, statement, channel_name=None):
    data = []
    metadata = []

    is_select = statement.strip().lower().startswith('select')  # TODO via parser
    is_print = statement.strip().lower().startswith('print')

    if is_select or is_print:
      result = self.client.query(statement)

      metadata = [
        {'type': 'STRING', 'name': 'Row', 'comment': None}
      ]

      if has_channels() and channel_name:
        _send_to_channel(
            channel_name,
            message_type='task.progress',
            message_data={'status': 'running', 'query_id': 1}
        )

      try:
        for line in result:
          # columns = line.keys()
          # data.append([line[col] for col in columns])
          if 'finalMessage' in line:
            if has_channels() and channel_name:  # Send results via WS and empty results
              _send_to_channel(
                  channel_name,
                  message_type='task.result',
                  message_data={'status': 'finalMessage', 'query_id': 1}
              )
            break
          elif 'header' in line:
            continue
          else:
            line = line.strip()

          if is_select:
            try:
              data_line = json.loads(line)
            except ValueError as e:
              data_line = json.loads(line[:-1])  # Most probably record is not JSON
            if data_line.get('@type') == 'statement_error':
              raise KSqlApiException(data_line['message'])
            if data_line['row']:  # If limit not reached
              data.append(data_line['row']['columns'])
          else:
            data.append([line])

          if has_channels() and channel_name:  # Send results via WS and empty results
            _send_to_channel(
                channel_name,
                message_type='task.result',
                message_data={'data': data, 'meta': metadata, 'query_id': 1}
            )
            data = []  # TODO: special message when end of stream
      except RuntimeError as e:
        if 'generator raised StopIteration' in str(e):
          return data, metadata
        else:
          raise e
    else:
      data, metadata = self._decode_result(
        self.ksql(statement)
      )

      if has_channels() and channel_name:  # Send results via WS and empty results
        _send_to_channel(
            channel_name,
            message_type='task.result',
            message_data={'data': data, 'meta': metadata, 'query_id': 1}
        )
        data = []  # TODO: special message when end of stream

    return data, metadata


  def cancel(self, notebook, snippet):
    return {'status': -1}


  def _decode_result(self, result):
    columns = []
    data = []

    if result['@type'] == 'statement_error':
      raise KSqlApiException(result['message'])
    elif result['@type'] in ('kafka_topics', 'streams', 'tables', 'queries'):
      result_type = 'topics' if result['@type'] == 'kafka_topics' else result['@type']
      if result[result_type]:
        columns = result[result_type][0].keys()
        for line in result[result_type]:
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

    columns = [{'name': col, 'type': 'STRING'} for col in columns]

    return data, columns
