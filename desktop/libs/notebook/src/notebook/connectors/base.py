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
import re
import uuid

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_unicode

from notebook.conf import get_ordered_interpreters


LOG = logging.getLogger(__name__)


class SessionExpired(Exception):
  pass

class QueryExpired(Exception):
  def __init__(self, message=None):
    super(QueryExpired, self).__init__()
    self.message = message

class AuthenticationRequired(Exception):
  pass

class OperationTimeout(Exception):
  pass

class OperationNotSupported(Exception):
  pass


class QueryError(Exception):
  def __init__(self, message, handle=None):
    self.message = message or _('No error message, please check the logs.')
    self.handle = handle
    self.extra = {}

  def __unicode__(self):
    return smart_unicode(self.message)


class Notebook(object):

  def __init__(self, document=None, **options):
    self.document = None

    if document is not None:
      self.data = document.data
      self.document = document
    else:
      _data = {
          'name': 'My Notebook',
          'uuid': str(uuid.uuid4()),
          'description': '',
          'type': 'notebook',
          'isSaved': False,
          'isManaged': False, # Aka isTask
          'skipHistorify': False,
          'sessions': [],
          'snippets': [],
      }
      _data.update(options)
      self.data = json.dumps(_data)

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
    return '\n\n\n'.join(['USE %s;\n\n%s' % (snippet['database'], snippet['statement_raw']) for snippet in self.get_data()['snippets']])

  def add_hive_snippet(self, database, sql):
    _data = json.loads(self.data)

    _data['snippets'].append(self._make_snippet({
       'status': 'running',
       'statement_raw': sql,
       'statement': sql,
       'type': 'query-hive',
       'properties': {
            'files': [],
            'functions': [],
            'settings': [],
       },
       'database': database,
    }))
    self._add_session(_data, 'query-hive')

    self.data = json.dumps(_data)

  def add_java_snippet(self, clazz, app_jar, arguments, files):
    _data = json.loads(self.data)

    _data['snippets'].append(self._make_snippet({
        u'type': u'java',
        u'status': u'running',
        u'properties':  {
          u'files': files,
          u'class': clazz,
          u'app_jar': app_jar,
          u'arguments': arguments,
          u'archives': [],
        }
    }))
    self._add_session(_data, 'java')

    self.data = json.dumps(_data)

  def add_shell_snippet(self, shell_command, arguments, archives, files, env_var):
    _data = json.loads(self.data)

    _data['snippets'].append(self._make_snippet({
        u'type': u'shell',
        u'status': u'running',
        u'properties':  {
          u'files': files,
          u'shell_command': shell_command,
          u'arguments': arguments,
          u'archives': archives,
          u'env_var': env_var,
          'command_path': shell_command,
        }
    }))
    self._add_session(_data, 'shell')

    self.data = json.dumps(_data)

  def _make_snippet(self, _snippet):
    return {
         'status': _snippet.get('status', 'ready'),
         'id': str(uuid.uuid4()),
         'statement_raw': _snippet.get('statement', ''),
         'statement': _snippet.get('statement', ''),
         'type': _snippet.get('type'),
         'properties': _snippet['properties'],
         'name': _snippet.get('name', '%(type)s snippet' % _snippet),
         'database': _snippet.get('database'),
         'result': {},
         'variables': []
    }

  def _add_session(self, data, snippet_type):
    from notebook.connectors.hiveserver2 import HS2Api # Cyclic dependency

    if snippet_type not in [_s['type'] for _s in data['sessions']]:
      data['sessions'].append({
         'type': snippet_type,
         'properties': HS2Api.get_properties(snippet_type),
         'id': None
      }
    )

  def execute(self, request, batch=False):
    from notebook.api import _execute_notebook # Cyclic dependency

    notebook_data = self.get_data()
    snippet = notebook_data['snippets'][0]
    snippet['wasBatchExecuted'] = batch

    return _execute_notebook(request, notebook_data, snippet)


def get_api(request, snippet):
  from notebook.connectors.hiveserver2 import HS2Api
  from notebook.connectors.jdbc import JdbcApi
  from notebook.connectors.rdbms import RdbmsApi
  from notebook.connectors.oozie_batch import OozieApi
  from notebook.connectors.solr import SolrApi
  from notebook.connectors.spark_shell import SparkApi
  from notebook.connectors.spark_batch import SparkBatchApi
  from notebook.connectors.text import TextApi

  if snippet.get('wasBatchExecuted'):
    return OozieApi(user=request.user, request=request)

  interpreter = [interpreter for interpreter in get_ordered_interpreters(request.user) if interpreter['type'] == snippet['type']]
  if not interpreter:
    raise PopupException(_('Snippet type %(type)s is not configured in hue.ini') % snippet)
  interpreter = interpreter[0]
  interface = interpreter['interface']

  if interface == 'hiveserver2':
    return HS2Api(user=request.user, request=request)
  elif interface == 'oozie':
    return OozieApi(user=request.user, request=request)
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
    return OozieApi(user=request.user, request=request) # Backward compatibility until Hue 4
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

  def fetch_result_size(self, notebook, snippet):
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

  def export_data_as_table(self, notebook, snippet, destination, is_temporary=False, location=None): raise NotImplementedError()

  def export_large_data_to_hdfs(self, notebook, snippet, destination): raise NotImplementedError()

  def statement_risk(self, notebook, snippet): raise NotImplementedError()

  def statement_compatibility(self, notebook, snippet, source_platform, target_platform): raise NotImplementedError()

  def statement_similarity(self, notebook, snippet, source_platform, target_platform): raise NotImplementedError()


def _get_snippet_name(notebook, unique=False, table_format=False):
  name = (('%(name)s' + ('%(id)s' if unique else '') if notebook.get('name') else '%(type)s-%(id)s') % notebook)
  if table_format:
    name = re.sub('-|\s', '_', name)
  return name
