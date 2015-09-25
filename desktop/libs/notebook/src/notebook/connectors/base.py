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


class QueryError(Exception):
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return force_unicode(str(self.message))


class Notebook():

  def __init__(self, document=None):
    self.document = None

    if document is not None:
      self.data = document.data
      self.document = document
    else:
      self.data = json.dumps({
          'name': 'My Notebook',
          'description': '',
          'snippets': []
      })

  def get_json(self):
    _data = self.get_data()

    return json.dumps(_data)

  def get_data(self):
    _data = json.loads(self.data)

    if self.document is not None:
      _data['id'] = self.document.id

    return _data

  def get_str(self):
    return '\n\n'.join([snippet['statement_raw'] for snippet in self.get_data()['snippets']])


def get_api(user, snippet, fs, jt):
  from notebook.connectors.hiveserver2 import HS2Api
  from notebook.connectors.jdbc import JDBCApi
  from notebook.connectors.mysql import MySqlApi
  from notebook.connectors.pig_batch import PigApi
  from notebook.connectors.spark_shell import SparkApi
  from notebook.connectors.spark_batch import SparkBatchApi
  from notebook.connectors.text import TextApi


  interface = [interpreter for interpreter in get_interpreters() if interpreter['type'] == snippet['type']]
  if not interface:
    raise PopupException(_('Snippet type %(type)s is not configured in hue.ini') % snippet)
  interface = interface[0]['interface']

  if interface == 'hiveserver2':
    return HS2Api(user)
  elif interface == 'livy':
    return SparkApi(user)
  elif interface == 'livy-batch':
    return SparkBatchApi(user)
  elif interface == 'text':
    return TextApi(user)
  elif interface == 'mysql':
    return MySqlApi(user)
  elif interface == 'jdbc':
    return JDBCApi(user)
  elif interface == 'pig':
    return PigApi(user, fs, jt)
  else:
    raise PopupException(_('Notebook connector interface not recognized: %s') % interface)


def _get_snippet_session(notebook, snippet):
  return [session for session in notebook['sessions'] if session['type'] == snippet['type']][0]


# Base API

class Api(object):

  def __init__(self, user, fs=None, jt=None):
    self.user = user
    self.fs = fs
    self.jt = jt

  def create_session(self, lang, properties=None):
    return {
        'type': lang,
        'id': None,
        'properties': []
    }

  def close_session(self, session):
    pass

  def fetch_result(self, notebook, snippet, rows, start_over):
    pass

  def download(self, notebook, snippet, format):
    pass

  def get_log(self, notebook, snippet, startFrom=None, size=None):
    return 'No logs'
