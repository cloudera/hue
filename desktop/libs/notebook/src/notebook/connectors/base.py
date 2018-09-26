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
    return '\n\n\n'.join(['USE %s;\n\n%s' % (snippet['database'], Notebook.statement_with_variables(snippet)) for snippet in self.get_data()['snippets']])

  @staticmethod
  def statement_with_variables(snippet):
    statement_raw = snippet['statement_raw']
    hasCurlyBracketParameters = snippet['type'] != 'pig'
    variables = {}
    for variable in snippet['variables']:
      variables[variable['name']] = variable

    if variables:
      variables_names = []
      for variable in snippet['variables']:
        variables_names.append(variable['name'])
      variablesString = '|'.join(variables_names)

      def replace(match):
        p1 = match.group(1)
        p2 = match.group(2)
        variable = variables[p2]
        value = variable['value']
        return p1 + (value if value is not None else variable['meta'].get('placeholder',''))
        
      return re.sub("([^\\\\])\\$" + ("{(" if hasCurlyBracketParameters else "(") + variablesString + ")(=[^}]*)?" + ("}" if hasCurlyBracketParameters else ""), replace, statement_raw)
      
    return statement_raw

  def add_hive_snippet(self, database, sql):
    _data = json.loads(self.data)

    _data['snippets'].append(self._make_snippet({
       'status': 'running',
       'statement_raw': sql,
       'statement': sql,
       'type': 'hive',
       'properties': {
            'files': [],
            'functions': [],
            'settings': [],
       },
       'database': database,
    }))
    self._add_session(_data, 'hive')

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

  def add_sqoop_snippet(self, statement, arguments, files):
    _data = json.loads(self.data)

    _data['snippets'].append(self._make_snippet({
        u'type': u'sqoop1',
        u'status': u'running',
        u'properties':  {
          u'files': files,
          u'arguments': arguments,
          u'archives': [],
          u'statement': statement
        }
    }))
    self._add_session(_data, 'java')

    self.data = json.dumps(_data)

  def add_spark_snippet(self, clazz, jars, arguments, files):
    _data = json.loads(self.data)

    _data['snippets'].append(self._make_snippet({
        u'type': u'spark',
        u'status': u'running',
        u'properties':  {
          u'files': files,
          u'class': clazz,
          u'app_jar': jars,
          u'arguments': arguments,
          u'archives': [],
          u'spark_opts': ''
        }
    }))
    self._add_session(_data, 'spark')

    self.data = json.dumps(_data)

  def add_shell_snippet(self, shell_command, arguments=None, archives=None, files=None, env_var=None, last_executed=None, capture_output=True):
    _data = json.loads(self.data)

    if arguments is None:
      arguments = []
    if archives is None:
      archives = []
    if files is None:
      files = []
    if env_var is None:
      env_var = []

    _data['snippets'].append(self._make_snippet({
        u'type': u'shell',
        u'status': u'running',
        u'properties':  {
          u'files': files,
          u'shell_command': shell_command,
          u'arguments': arguments,
          u'archives': archives,
          u'env_var': env_var,
          u'command_path': shell_command,
          u'capture_output': capture_output
        },
        u'lastExecuted': last_executed
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
         'variables': [],
         'lastExecuted': _snippet.get('lastExecuted'),
         'capture_output': _snippet.get('capture_output', True)
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
  from notebook.connectors.oozie_batch import OozieApi

  if snippet.get('wasBatchExecuted'):
    return OozieApi(user=request.user, request=request)

  if snippet['type'] == 'report':
    snippet['type'] = 'impala'

  interpreter = [interpreter for interpreter in get_ordered_interpreters(request.user) if interpreter['type'] == snippet['type']]
  if not interpreter:
    if snippet['type'] == 'hbase':
      interpreter = [{
        'name': 'hbase',
        'type': 'hbase',
        'interface': 'hbase',
        'options': {},
        'is_sql': False
      }]
    elif snippet['type'] == 'kafka':
      interpreter = [{
        'name': 'kafka',
        'type': 'kafka',
        'interface': 'kafka',
        'options': {},
        'is_sql': False
      }]
    elif snippet['type'] == 'solr':
      interpreter = [{
        'name': 'solr',
        'type': 'solr',
        'interface': 'solr',
        'options': {},
        'is_sql': False
      }]
    elif snippet['type'] == 'custom':
      interpreter = [{
        'name': snippet['name'],
        'type': snippet['type'],
        'interface': snippet['interface'],
        'options': snippet.get('options', {}),
        'is_sql': False
      }]
    else:
      raise PopupException(_('Snippet type %(type)s is not configured in hue.ini') % snippet)

  interpreter = interpreter[0]
  interface = interpreter['interface']

  # Multi cluster
  cluster = json.loads(request.POST.get('cluster', '""')) # Via Catalog autocomplete API
  if cluster == 'undefined':
    cluster = None
  if not cluster and snippet.get('compute'): # Via notebook.ko.js
    cluster = snippet['compute']

  cluster_name = cluster.get('id') if cluster else None

  if cluster and 'altus:dataware:k8s' in cluster_name:
    interface = 'hiveserver2'
  elif cluster and 'crn:altus:dataware:' in cluster_name:
    interface = 'altus-adb'
  elif cluster and 'crn:altus:dataeng:' in cluster_name:
    interface = 'dataeng'

  LOG.info('Selected cluster %s %s interface %s' % (cluster_name, cluster, interface))

  if interface == 'hiveserver2':
    from notebook.connectors.hiveserver2 import HS2Api
    return HS2Api(user=request.user, request=request, cluster=cluster)
  elif interface == 'oozie':
    return OozieApi(user=request.user, request=request)
  elif interface == 'livy':
    from notebook.connectors.spark_shell import SparkApi
    return SparkApi(request.user)
  elif interface == 'livy-batch':
    from notebook.connectors.spark_batch import SparkBatchApi
    return SparkBatchApi(request.user)
  elif interface == 'text' or interface == 'markdown':
    from notebook.connectors.text import TextApi
    return TextApi(request.user)
  elif interface == 'rdbms':
    from notebook.connectors.rdbms import RdbmsApi
    return RdbmsApi(request.user, interpreter=snippet['type'], query_server=snippet.get('query_server'))
  elif interface == 'altus-adb':
    from notebook.connectors.altus_adb import AltusAdbApi
    return AltusAdbApi(user=request.user, cluster_name=cluster_name, request=request)
  elif interface == 'dataeng':
    from notebook.connectors.dataeng import DataEngApi
    return DataEngApi(user=request.user, request=request, cluster_name=cluster_name)
  elif interface == 'jdbc':
    if not interpreter['options'] or interpreter['options'].get('url', '').find('teradata') < 0:
      from notebook.connectors.jdbc import JdbcApi
      return JdbcApi(request.user, interpreter=interpreter)
    else:
      from notebook.connectors.jdbc_teradata import JdbcApiTeradata
      return JdbcApiTeradata(request.user, interpreter=interpreter)
  elif interface == 'teradata':
    from notebook.connectors.jdbc import JdbcApiTeradata
    return JdbcApiTeradata(request.user, interpreter=interpreter)
  elif interface == 'sqlalchemy':
    from notebook.connectors.sqlalchemyapi import SqlAlchemyApi
    return SqlAlchemyApi(request.user, interpreter=interpreter)
  elif interface == 'solr':
    from notebook.connectors.solr import SolrApi
    return SolrApi(request.user, interpreter=interpreter)
  elif interface == 'hbase':
    from notebook.connectors.hbase import HBaseApi
    return HBaseApi(request.user)
  elif interface == 'kafka':
    from notebook.connectors.kafka import KafkaApi
    return KafkaApi(request.user)
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

  def __init__(self, user, interpreter=None, request=None, cluster=None, query_server=None):
    self.user = user
    self.interpreter = interpreter
    self.request = request
    self.cluster = cluster
    self.query_server = query_server

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
    raise OperationNotSupported()

  def download(self, notebook, snippet, format, user_agent=None):
    pass

  def get_log(self, notebook, snippet, startFrom=None, size=None):
    return 'No logs'

  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None):
    return {}

  def progress(self, snippet, logs=None):
    return 50

  def get_jobs(self, notebook, snippet, logs):
    return []

  def get_sample_data(self, snippet, database=None, table=None, column=None, async=False, operation=None): raise NotImplementedError()

  def export_data_as_hdfs_file(self, snippet, target_file, overwrite): raise NotImplementedError()

  def export_data_as_table(self, notebook, snippet, destination, is_temporary=False, location=None): raise NotImplementedError()

  def export_large_data_to_hdfs(self, notebook, snippet, destination): raise NotImplementedError()

  def statement_risk(self, notebook, snippet): raise NotImplementedError()

  def statement_compatibility(self, notebook, snippet, source_platform, target_platform): raise NotImplementedError()

  def statement_similarity(self, notebook, snippet, source_platform, target_platform): raise NotImplementedError()


def _get_snippet_name(notebook, unique=False, table_format=False):
  name = (('%(name)s' + ('-%(id)s' if unique else '') if notebook.get('name') else '%(type)s-%(id)s') % notebook)
  if table_format:
    name = re.sub('[-|\s:]', '_', name)
  return name
