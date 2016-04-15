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

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode

from notebook.conf import get_interpreters


LOG = logging.getLogger(__name__)


class SessionExpired(Exception):
  pass

class QueryExpired(Exception):
  pass

class AuthenticationRequired(Exception):
  pass

class QueryError(Exception):
  def __init__(self, message, handle=None):
    self.message = message
    self.handle = handle

  def __str__(self):
    return force_unicode(str(self.message))


class Notebook(object):

  def __init__(self, document=None):
    self.document = None

    if document is not None:
      self.data = document.data
      self.document = document
    else:
      self.data = json.dumps({
          'name': 'My Notebook',
          'description': '',
          'type': 'notebook',
          'snippets': [],
      })

  def get_json(self):
    _data = self.get_data()

    return json.dumps(_data)

  def get_data(self):
    _data = json.loads(self.data)

    if self.document is not None:
      _data['id'] = self.document.id
      _data['is_history'] = self.document.is_history

    return _data

  def get_str(self):
    return '\n\n'.join([snippet['statement_raw'] for snippet in self.get_data()['snippets']])


def get_api(request, snippet):
  from notebook.connectors.hiveserver2 import HS2Api
  from notebook.connectors.jdbc import JdbcApi
  from notebook.connectors.rdbms import RdbmsApi
  from notebook.connectors.pig_batch import PigApi
  from notebook.connectors.solr import SolrApi
  from notebook.connectors.spark_shell import SparkApi
  from notebook.connectors.spark_batch import SparkBatchApi
  from notebook.connectors.text import TextApi

  interpreter = [interpreter for interpreter in get_interpreters(request.user) if interpreter['type'] == snippet['type']]
  if not interpreter:
    raise PopupException(_('Snippet type %(type)s is not configured in hue.ini') % snippet)
  interpreter = interpreter[0]
  interface = interpreter['interface']

  if interface == 'hiveserver2':
    return HS2Api(user=request.user, request=request)
  elif interface == 'livy':
    return SparkApi(request.user)
  elif interface == 'livy-batch':
    return SparkBatchApi(request.user)
  elif interface == 'text' or interface == 'markdown':
    return TextApi(request.user)
  elif interface == 'rdbms':
    return RdbmsApi(request.user, interpreter=snippet['type'])
  elif interface == 'jdbc':
    return JdbcApi(request.user, interpreter=interpreter)
  elif interface == 'solr':
    return SolrApi(request.user, interpreter=interpreter)
  elif interface == 'pig':
    return PigApi(user=request.user, request=request)
  else:
    raise PopupException(_('Notebook connector interface not recognized: %s') % interface)


def _get_snippet_session(notebook, snippet):
  session = [session for session in notebook['sessions'] if session['type'] == snippet['type']]
  if not session:
    raise SessionExpired()
  else:
    return session[0]


# Base API

class Api(object):

  def __init__(self, user, interpreter=None, request=None):
    self.user = user
    self.interpreter = interpreter
    self.request = request

  def create_session(self, lang, properties=None):
    return {
        'type': lang,
        'id': None,
        'properties': properties if not None else []
    }

  def close_session(self, session):
    pass

  def fetch_result(self, notebook, snippet, rows, start_over):
    pass

  def download(self, notebook, snippet, format):
    pass

  def get_log(self, notebook, snippet, startFrom=None, size=None):
    return 'No logs'

  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None):
    return {}

  def progress(self, snippet, logs=None):
    return 50

  def get_jobs(self, notebook, snippet, logs):
    return []

  def export_data_as_hdfs_file(self, snippet, target_file, overwrite): raise NotImplementedError()

  def export_data_as_table(self, notebook, snippet, destination): raise NotImplementedError()

  def export_large_data_to_hdfs(self, notebook, snippet, destination): raise NotImplementedError()
