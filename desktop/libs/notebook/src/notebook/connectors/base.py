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

from builtins import object
import json
import logging
import re
import time
import uuid

from django.utils.translation import ugettext as _
from django.utils.encoding import smart_str

from desktop.auth.backend import is_admin
from desktop.conf import TASK_SERVER, has_connectors
from desktop.lib import export_csvxls
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_unicode
from desktop.models import get_cluster_config
from metadata.optimizer.base import get_api as get_optimizer_api

from notebook.conf import get_ordered_interpreters
from notebook.sql_utils import get_current_statement


LOG = logging.getLogger(__name__)


class SessionExpired(Exception):
  pass

class QueryExpired(Exception):
  def __init__(self, message=None):
    super(QueryExpired, self).__init__()
    self.message = message

class AuthenticationRequired(Exception):
  def __init__(self, message=None):
    super(AuthenticationRequired, self).__init__()
    self.message = message

class OperationTimeout(Exception):
  def __str__(self):
    return 'OperationTimeout'

class OperationNotSupported(Exception):
  pass


class QueryError(Exception):
  def __init__(self, message, handle=None):
    super(QueryError, self).__init__(message)
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

  def get_str(self, from_oozie_action=False):
    return '\n\n\n'.join([
        'USE %s;\n\n%s' % (
          snippet['database'],
          snippet['statement_raw'] if from_oozie_action else Notebook.statement_with_variables(snippet)
        )
        for snippet in self.get_data()['snippets']
      ]
    )

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
        value = smart_str(variable['value'])
        return smart_str(p1) + smart_str(value if value is not None else variable['meta'].get('placeholder',''))

      return re.sub(
          "([^\\\\])\\$" + (
            "{(" if hasCurlyBracketParameters else "(") + variablesString + ")(=[^}]*)?" + ("}"
            if hasCurlyBracketParameters else ""
          ),
          replace,
          smart_str(statement_raw)
      )

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
    from notebook.api import _execute_notebook  # Cyclic dependency

    notebook_data = self.get_data()
    snippet = notebook_data['snippets'][0]
    snippet['wasBatchExecuted'] = batch

    return _execute_notebook(request, notebook_data, snippet)


  def execute_and_wait(self, request, timeout_sec=30.0, sleep_interval=1, include_results=False):
    """
    Run query and check status until it finishes or timeouts.

    Check status until it finishes or timeouts.
    """
    handle = self.execute(request, batch=False)

    if handle['status'] != 0:
      raise QueryError(e, message='SQL statement failed.', handle=handle)

    operation_id = handle['history_uuid']
    curr = time.time()
    end = curr + timeout_sec

    handle = self.check_status(request, operation_id=operation_id)

    while curr <= end:
      if handle['status'] == 0 and handle['query_status']['status'] not in ('waiting', 'running'):
        if include_results and handle['query_status']['status'] == 'available':
          handle.update(
            self.fetch_result_data(request.user, operation_id=operation_id)
          )
          # TODO: close
        return handle

      handle = self.check_status(request, operation_id=operation_id)
      time.sleep(sleep_interval)
      curr = time.time()

    # TODO
    # msg = "The query timed out after %(timeout)d seconds, canceled query." % {'timeout': timeout_sec}
    # LOG.warning(msg)
    # try:
    #   self.cancel_operation(handle)
    #   # get_api(request, snippet).cancel(notebook, snippet)
    # except Exception as e:
    #   msg = "Failed to cancel query."
    #   LOG.warning(msg)
    #   self.close_operation(handle)
    #   raise QueryServerException(e, message=msg)

    raise OperationTimeout()

  def check_status(self, request, operation_id):
    from notebook.api import _check_status

    return _check_status(request, operation_id=operation_id)

  def fetch_result_data(self, user, operation_id):
    from notebook.api import _fetch_result_data

    return _fetch_result_data(user, operation_id=operation_id, rows=100, start_over=False, nulls_only=True)


def get_interpreter(connector_type, user=None):
  interpreter = [
    interpreter for interpreter in get_ordered_interpreters(user) if connector_type == interpreter['type']
  ]

  if not interpreter:
    if connector_type == 'hbase': # TODO move to connectors
      interpreter = [{
        'name': 'hbase',
        'type': 'hbase',
        'interface': 'hbase',
        'options': {},
        'is_sql': False
      }]
    elif connector_type == 'kafka':
      interpreter = [{
        'name': 'kafka',
        'type': 'kafka',
        'interface': 'kafka',
        'options': {},
        'is_sql': False
      }]
    elif connector_type == 'solr':
      interpreter = [{
        'name': 'solr',
        'type': 'solr',
        'interface': 'solr',
        'options': {},
        'is_sql': False
      }]
    else:
      raise PopupException(_('Snippet type %s is not configured.') % connector_type)
  elif len(interpreter) > 1:
    raise PopupException(_('Snippet type %s matching more than one interpreter: %s') % (connector_type, len(interpreter)))

  return interpreter[0]


def patch_snippet_for_connector(snippet):
  """
  Connector backward compatibility switcher.
  # TODO Connector unification
  """
  if snippet.get('connector') and snippet['connector'].get('type'):
    snippet['type'] = snippet['connector']['type']  # To rename to 'id'
    snippet['dialect'] = snippet['connector']['dialect']
  else:
    snippet['dialect'] = snippet['type']


def get_api(request, snippet):
  from notebook.connectors.oozie_batch import OozieApi

  if snippet.get('wasBatchExecuted') and not TASK_SERVER.ENABLED.get():
    return OozieApi(user=request.user, request=request)

  if snippet.get('type') == 'report':
    snippet['type'] = 'impala'

  patch_snippet_for_connector(snippet)

  connector_name = snippet['type']

  if has_connectors() and snippet.get('type') == 'hello' and is_admin(request.user):
    interpreter = snippet.get('interpreter')
  else:
    interpreter = get_interpreter(connector_type=connector_name, user=request.user)

  interface = interpreter['interface']

  if get_cluster_config(request.user)['has_computes']:
    compute = json.loads(request.POST.get('cluster', '""'))  # Via Catalog autocomplete API or Notebook create sessions.
    if compute == '""' or compute == 'undefined':
      compute = None
    if not compute and snippet.get('compute'):  # Via notebook.ko.js
      interpreter['compute'] = snippet['compute']

  LOG.debug('Selected interpreter %s interface=%s compute=%s' % (
    interpreter['type'],
    interface,
    interpreter.get('compute') and interpreter['compute']['name'])
  )

  if interface == 'hiveserver2' or interface == 'hms':
    from notebook.connectors.hiveserver2 import HS2Api
    return HS2Api(user=request.user, request=request, interpreter=interpreter)
  elif interface == 'oozie':
    return OozieApi(user=request.user, request=request)
  elif interface == 'livy':
    from notebook.connectors.spark_shell import SparkApi
    return SparkApi(request.user, interpreter=interpreter)
  elif interface == 'livy-batch':
    from notebook.connectors.spark_batch import SparkBatchApi
    return SparkBatchApi(request.user, interpreter=interpreter)
  elif interface == 'text' or interface == 'markdown':
    from notebook.connectors.text import TextApi
    return TextApi(request.user)
  elif interface == 'rdbms':
    from notebook.connectors.rdbms import RdbmsApi
    return RdbmsApi(request.user, interpreter=snippet['type'], query_server=snippet.get('query_server'))
  elif interface == 'jdbc':
    if interpreter['options'] and interpreter['options'].get('url', '').find('teradata') >= 0:
      from notebook.connectors.jdbc_teradata import JdbcApiTeradata
      return JdbcApiTeradata(request.user, interpreter=interpreter)
    if interpreter['options'] and interpreter['options'].get('url', '').find('awsathena') >= 0:
      from notebook.connectors.jdbc_athena import JdbcApiAthena
      return JdbcApiAthena(request.user, interpreter=interpreter)
    elif interpreter['options'] and interpreter['options'].get('url', '').find('presto') >= 0:
      from notebook.connectors.jdbc_presto import JdbcApiPresto
      return JdbcApiPresto(request.user, interpreter=interpreter)
    elif interpreter['options'] and interpreter['options'].get('url', '').find('clickhouse') >= 0:
      from notebook.connectors.jdbc_clickhouse import JdbcApiClickhouse
      return JdbcApiClickhouse(request.user, interpreter=interpreter)
    elif interpreter['options'] and interpreter['options'].get('url', '').find('vertica') >= 0:
      from notebook.connectors.jdbc_vertica import JdbcApiVertica
      return JdbcApiVertica(request.user, interpreter=interpreter)
    else:
      from notebook.connectors.jdbc import JdbcApi
      return JdbcApi(request.user, interpreter=interpreter)
  elif interface == 'teradata':
    from notebook.connectors.jdbc_teradata import JdbcApiTeradata
    return JdbcApiTeradata(request.user, interpreter=interpreter)
  elif interface == 'athena':
    from notebook.connectors.jdbc_athena import JdbcApiAthena
    return JdbcApiAthena(request.user, interpreter=interpreter)
  elif interface == 'presto':
    from notebook.connectors.jdbc_presto import JdbcApiPresto
    return JdbcApiPresto(request.user, interpreter=interpreter)
  elif interface == 'sqlalchemy':
    from notebook.connectors.sql_alchemy import SqlAlchemyApi
    return SqlAlchemyApi(request.user, interpreter=interpreter)
  elif interface == 'solr':
    from notebook.connectors.solr import SolrApi
    return SolrApi(request.user, interpreter=interpreter)
  elif interface == 'hbase':
    from notebook.connectors.hbase import HBaseApi
    return HBaseApi(request.user)
  elif interface == 'ksql':
    from notebook.connectors.ksql import KSqlApi
    return KSqlApi(request.user, interpreter=interpreter)
  elif interface == 'flink':
    from notebook.connectors.flink_sql import FlinkSqlApi
    return FlinkSqlApi(request.user, interpreter=interpreter)
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

  def __init__(self, user, interpreter=None, request=None, query_server=None):
    self.user = user
    self.interpreter = interpreter
    self.request = request
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

  def can_start_over(self, notebook, snippet):
    return False

  def fetch_result_size(self, notebook, snippet):
    raise OperationNotSupported()

  def download(self, notebook, snippet, file_format='csv'):
    from beeswax import data_export #TODO: Move to notebook?
    from beeswax import conf

    result_wrapper = ExecutionWrapper(self, notebook, snippet)

    max_rows = conf.DOWNLOAD_ROW_LIMIT.get()
    max_bytes = conf.DOWNLOAD_BYTES_LIMIT.get()

    content_generator = data_export.DataAdapter(result_wrapper, max_rows=max_rows, max_bytes=max_bytes)
    return export_csvxls.create_generator(content_generator, file_format)

  def get_log(self, notebook, snippet, startFrom=None, size=None):
    return 'No logs'

  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None, operation=None):
    return {}

  def progress(self, notebook, snippet, logs=None):
    return 50

  def get_jobs(self, notebook, snippet, logs):
    return []

  def get_sample_data(self, snippet, database=None, table=None, column=None, is_async=False, operation=None):
    raise NotImplementedError()

  def export_data_as_hdfs_file(self, snippet, target_file, overwrite):
    raise NotImplementedError()

  def export_data_as_table(self, notebook, snippet, destination, is_temporary=False, location=None):
    raise NotImplementedError()

  def export_large_data_to_hdfs(self, notebook, snippet, destination):
    raise NotImplementedError()

  def statement_risk(self, interface, notebook, snippet):
    response = self._get_current_statement(notebook, snippet)
    query = response['statement']

    client = get_optimizer_api(self.user, interface)
    patch_snippet_for_connector(snippet)

    return client.query_risk(query=query, source_platform=snippet['dialect'], db_name=snippet.get('database') or 'default')

  def statement_compatibility(self, interface, notebook, snippet, source_platform, target_platform):
    response = self._get_current_statement(notebook, snippet)
    query = response['statement']

    client = get_optimizer_api(self.user, interface)

    return client.query_compatibility(source_platform, target_platform, query)

  def statement_similarity(self, interface, notebook, snippet, source_platform):
    response = self._get_current_statement(notebook, snippet)
    query = response['statement']

    client = get_optimizer_api(self.user, interface)

    return client.similar_queries(source_platform, query)

  def describe(self, notebook, snippet, database=None, table=None, column=None):
    if column:
      response = self.describe_column(notebook, snippet, database=database, table=table, column=column)
    elif table:
      response = {
          'status': 0,
          'name': table or '',
          'partition_keys': [],
          'cols': [],
          'path_location': '',
          'hdfs_link': '',
          'comment': '',
          'is_view': False,
          'properties': [],
          'details': {'properties': {'table_type': ''}, 'stats': {}},
          'stats': []
      }
      describe_table = self.describe_table(notebook, snippet, database, table)
      response.update(describe_table)
    else:
      response = {
        'status': 0,
        'owner_name': '',
        'owner_type': '',
        'parameters': '',
        'hdfs_link': '',
        'message': ''
      }
      describe_database = self.describe_database(notebook, snippet, database)
      response.update(describe_database)
    return response

  def describe_column(self, notebook, snippet, database=None, table=None, column=None):
    return []

  def describe_table(self, notebook, snippet, database=None, table=None):
    response = {}
    autocomplete = self.autocomplete(snippet, database=database, table=table)
    response['cols'] = autocomplete['extended_columns'] if autocomplete and autocomplete.get('extended_columns') else [],
    return response

  def describe_database(self, notebook, snippet, database=None):
    return {}

  def close_statement(self, notebook, snippet): pass

  def _get_current_statement(self, notebook, snippet):
    should_close, resp = get_current_statement(snippet)
    if should_close:
      try:
        self.close_statement(notebook, snippet)  # Close all the time past multi queries
      except:
        LOG.warn('Could not close previous multiquery query')

    return resp

  def get_log_is_full_log(self, notebook, snippet):
    return True


def _get_snippet_name(notebook, unique=False, table_format=False):
  name = (('%(name)s' + ('-%(id)s' if unique else '') if notebook.get('name') else '%(type)s-%(id)s') % notebook)
  if table_format:
    name = re.sub('[-|\s:]', '_', name)
  return name


class ExecutionWrapper(object):
  def __init__(self, api, notebook, snippet, callback=None):
    self.api = api
    self.notebook = notebook
    self.snippet = snippet
    self.callback = callback
    self.should_close = False

  def fetch(self, handle, start_over=None, rows=None):
    if start_over:
      if not self.snippet['result'].get('handle') \
          or not self.snippet['result']['handle'].get('guid') \
          or not self.api.can_start_over(self.notebook, self.snippet):
        start_over = False
        handle = self.api.execute(self.notebook, self.snippet)
        self.snippet['result']['handle'] = handle

        if self.callback and hasattr(self.callback, 'on_execute'):
          self.callback.on_execute(handle)

        self.should_close = True
        self._until_available()

    if self.snippet['result']['handle'].get('sync', False):
      result = self.snippet['result']['handle']['result']
    else:
      result = self.api.fetch_result(self.notebook, self.snippet, rows, start_over)

    return ResultWrapper(result.get('meta'), result.get('data'), result.get('has_more'))

  def _until_available(self):
    if self.snippet['result']['handle'].get('sync', False):
      return # Request is already completed

    count = 0
    sleep_seconds = 1
    check_status_count = 0
    get_log_is_full_log = self.api.get_log_is_full_log(self.notebook, self.snippet)

    while True:
      response = self.api.check_status(self.notebook, self.snippet)
      if self.callback and hasattr(self.callback, 'on_status'):
        self.callback.on_status(response['status'])
      if self.callback and hasattr(self.callback, 'on_log'):
        log = self.api.get_log(self.notebook, self.snippet, startFrom=count)
        if get_log_is_full_log:
          log = log[count:]

        self.callback.on_log(log)
        count += len(log)

      if response['status'] not in ['waiting', 'running', 'submitted']:
        break
      check_status_count += 1
      if check_status_count > 5:
        sleep_seconds = 5
      elif check_status_count > 10:
        sleep_seconds = 10
      time.sleep(sleep_seconds)

  def close(self, handle):
    if self.should_close:
      self.should_close = False
      self.api.close_statement(self.notebook, self.snippet)


class ResultWrapper(object):
  def __init__(self, cols, rows, has_more):
    self._cols = cols
    self._rows = rows
    self.has_more = has_more

  def full_cols(self):
    return self._cols

  def rows(self):
    return self._rows
