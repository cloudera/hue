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

import logging
import time

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode
from desktop.lib.rest.http_client import RestException

from spark.job_server_api import get_api as get_spark_api

from notebook.data_export import download as spark_download
from notebook.connectors.base import SessionExpired, _get_snippet_session, Api,\
  QueryError


LOG = logging.getLogger(__name__)


class SparkApi(Api):
  PROPERTIES = [
    {'name': 'jars', 'nice_name': _('Jars'), 'default': '', 'type': 'csv-hdfs-files', 'is_yarn': False},
    {'name': 'files', 'nice_name': _('Files'), 'default': '', 'type': 'csv-hdfs-files', 'is_yarn': False},
    {'name': 'pyFiles', 'nice_name': _('pyFiles'), 'default': '', 'type': 'csv-hdfs-files', 'is_yarn': False},

    {'name': 'driverMemory', 'nice_name': _('Driver Memory'), 'default': '1', 'type': 'jvm', 'is_yarn': False},

    {'name': 'driverCores', 'nice_name': _('Driver Cores'), 'default': '1', 'type': 'number', 'is_yarn': True},
    {'name': 'executorCores', 'nice_name': _('Executor Cores'), 'default': '1', 'type': 'number', 'is_yarn': True},
    {'name': 'queue', 'nice_name': _('Queue'), 'default': '1', 'type': 'string', 'is_yarn': True},
    {'name': 'archives', 'nice_name': _('Archives'), 'default': '', 'type': 'csv-hdfs-files', 'is_yarn': True},
    {'name': 'numExecutors', 'nice_name': _('Executors Numbers'), 'default': '1', 'type': 'number', 'is_yarn': True},
  ]

  def create_session(self, lang='scala', properties=None):
    properties = dict([(p['name'], p['value']) for p in properties]) if properties is not None else {}

    properties['kind'] = lang

    api = get_spark_api(self.user)

    response = api.create_session(**properties)

    status = api.get_session(response['id'])
    count = 0

    while status['state'] == 'starting' and count < 120:
      status = api.get_session(response['id'])
      count += 1
      time.sleep(1)

    if status['state'] != 'idle':
      info = '\n'.join(status['log']) if status['log'] else 'timeout'
      raise QueryError(_('The Spark session could not be created in the cluster: %s') % info)

    return {
        'type': lang,
        'id': response['id'],
        'properties': []
    }

  def execute(self, notebook, snippet):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)

    try:
      response = api.submit_statement(session['id'], snippet['statement'])
      return {
          'id': response['id'],
          'has_result_set': True,
      }
    except Exception, e:
      message = force_unicode(str(e)).lower()
      if 'session not found' in message or 'connection refused' in message or 'session is in state busy' in message:
        raise SessionExpired(e)
      else:
        raise e

  def check_status(self, notebook, snippet):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)
    cell = snippet['result']['handle']['id']

    try:
      response = api.fetch_data(session['id'], cell)
      return {
          'status': response['state'],
      }
    except Exception, e:
      message = force_unicode(str(e)).lower()
      if 'session not found' in message:
        raise SessionExpired(e)
      else:
        raise e

  def fetch_result(self, notebook, snippet, rows, start_over):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)
    cell = snippet['result']['handle']['id']

    try:
      response = api.fetch_data(session['id'], cell)
    except Exception, e:
      message = force_unicode(str(e)).lower()
      if 'session not found' in message:
        raise SessionExpired(e)
      else:
        raise e

    content = response['output']

    if content['status'] == 'ok':
      data = content['data']
      images = []

      try:
        table = data['application/vnd.livy.table.v1+json']
      except KeyError:
        try:
          images = [data['image/png']]
        except KeyError:
          images = []
        data = [[data['text/plain']]]
        meta = [{'name': 'Header', 'type': 'STRING_TYPE', 'comment': ''}]
        type = 'text'
      else:
        data = table['data']
        headers = table['headers']
        meta = [{'name': h['name'], 'type': h['type'], 'comment': ''} for h in headers]
        type = 'table'

      # Non start_over not supported
      if not start_over:
        data = []

      return {
          'data': data,
          'images': images,
          'meta': meta,
          'type': type
      }
    elif content['status'] == 'error':
      tb = content.get('traceback', None)

      if tb is None:
        msg = content.get('ename', 'unknown error')

        evalue = content.get('evalue')
        if evalue is not None:
          msg = '%s: %s' % (msg, evalue)
      else:
        msg = ''.join(tb)

      raise QueryError(msg)

  def download(self, notebook, snippet, format):
    try:
      api = get_spark_api(self.user)
      session = _get_snippet_session(notebook, snippet)
      cell = snippet['result']['handle']['id']

      return spark_download(api, session['id'], cell, format)
    except Exception, e:
      raise PopupException(e)

  def cancel(self, notebook, snippet):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)
    response = api.cancel(session['id'])

    return {'status': 0}

  def get_log(self, notebook, snippet, startFrom=0, size=None):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)

    return api.get_log(session['id'], startFrom=startFrom, size=size)

  def progress(self, snippet, logs):
    return 50

  def close_statement(self, snippet): # Individual statements cannot be closed
    pass

  def close_session(self, session):
    api = get_spark_api(self.user)

    if session['id'] is not None:
      try:
        api.close(session['id'])
        return {
          'session': session['id'],
          'status': 0
        }
      except RestException, e:
        if e.code == 404 or e.code == 500: # TODO remove the 500
          raise SessionExpired(e)
    else:
      return {'status': -1}

  def get_jobs(self, log):
    return []
