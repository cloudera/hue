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

from __future__ import division
from future import standard_library
standard_library.install_aliases()
from builtins import next, object
import binascii
import copy
import json
import logging
import re
import struct
import sys

from django.urls import reverse

from desktop.auth.backend import is_admin
from desktop.conf import USE_DEFAULT_CONFIGURATION, has_connectors
from desktop.lib.conf import BoundConfig
from desktop.lib.exceptions import StructuredException
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode
from desktop.lib.paths import SAFE_CHARACTERS_URI_COMPONENTS
from desktop.lib.rest.http_client import RestException
from desktop.lib.thrift_util import unpack_guid, unpack_guid_base64
from desktop.models import DefaultConfiguration, Document2

from notebook.connectors.base import Api, QueryError, QueryExpired, OperationTimeout, OperationNotSupported, _get_snippet_name, Notebook, \
    get_interpreter, patch_snippet_for_connector

if sys.version_info[0] > 2:
  from urllib.parse import quote as urllib_quote, unquote as urllib_unquote
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
  from urllib import quote as urllib_quote, unquote as urllib_unquote

LOG = logging.getLogger()


try:
  from beeswax import conf as beeswax_conf, data_export
  from beeswax.api import _autocomplete, _get_sample_data
  from beeswax.conf import CONFIG_WHITELIST as hive_settings, DOWNLOAD_ROW_LIMIT, DOWNLOAD_BYTES_LIMIT, MAX_NUMBER_OF_SESSIONS, \
      has_session_pool, has_multiple_sessions, CLOSE_SESSIONS
  from beeswax.data_export import upload
  from beeswax.design import hql_query
  from beeswax.models import QUERY_TYPES, HiveServerQueryHandle, HiveServerQueryHistory, QueryHistory, Session
  from beeswax.server import dbms
  from beeswax.server.dbms import get_query_server_config, QueryServerException, reset_ha
  from beeswax.views import parse_out_jobs, parse_out_queries
except ImportError as e:
  LOG.warning('Hive and HiveServer2 interfaces are not enabled: %s' % e)
  hive_settings = None

try:
  from impala import api   # Force checking if Impala is enabled
  from impala.conf import CONFIG_WHITELIST as impala_settings
  from impala.server import get_api as get_impalad_api, ImpalaDaemonApiException, _get_impala_server_url
except ImportError as e:
  LOG.warning("Impala app is not enabled")
  impala_settings = None

try:
  from jobbrowser.apis.query_api import _get_api
  from jobbrowser.conf import ENABLE_QUERY_BROWSER, ENABLE_HIVE_QUERY_BROWSER
  from jobbrowser.views import get_job
  has_query_browser = ENABLE_QUERY_BROWSER.get()
  has_hive_query_browser = ENABLE_HIVE_QUERY_BROWSER.get()
  has_jobbrowser = True
except (AttributeError, ImportError, RuntimeError) as e:
  LOG.warning("Job Browser app is not enabled")
  has_jobbrowser = False
  has_query_browser = False
  has_hive_query_browser = False


DEFAULT_HIVE_ENGINE = 'mr'


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except StructuredException as e:
      message = force_unicode(str(e))
      if 'timed out' in message:
        raise OperationTimeout(e)
      elif 'Connection refused' in message or 'Name or service not known' in message or 'Could not connect to any' in message:
        reset_ha()
      else:
        raise QueryError(message)
    except QueryServerException as e:
      message = force_unicode(str(e))
      if 'Invalid query handle' in message or 'Invalid OperationHandle' in message:
        raise QueryExpired(e)
      else:
        raise QueryError(message)
  return decorator


def is_hive_enabled():
  return hive_settings is not None and type(hive_settings) == BoundConfig


def is_impala_enabled():
  return impala_settings is not None and type(impala_settings) == BoundConfig


class HiveConfiguration(object):

  APP_NAME = 'hive'

  PROPERTIES = [{
      "multiple": True,
      "defaultValue": [],
      "value": [],
      "nice_name": _("Files"),
      "key": "files",
      "help_text": _("Add one or more files, jars, or archives to the list of resources."),
      "type": "hdfs-files"
    }, {
      "multiple": True,
      "defaultValue": [],
      "value": [],
      "nice_name": _("Functions"),
      "key": "functions",
      "help_text": _("Add one or more registered UDFs (requires function name and fully-qualified class name)."),
      "type": "functions"
    }, {
      "multiple": True,
      "defaultValue": [],
      "value": [],
      "nice_name": _("Settings"),
      "key": "settings",
      "help_text": _("Hive and Hadoop configuration properties."),
      "type": "settings",
      "options": [config.lower() for config in hive_settings.get()] if is_hive_enabled() and hasattr(hive_settings, 'get') else []
    }
  ]


class ImpalaConfiguration(object):

  APP_NAME = 'impala'

  PROPERTIES = [{
      "multiple": True,
      "defaultValue": [],
      "value": [],
      "nice_name": _("Settings"),
      "key": "settings",
      "help_text": _("Impala configuration properties."),
      "type": "settings",
      "options": [config.lower() for config in impala_settings.get()] if is_impala_enabled() else []
    }
  ]


class HS2Api(Api):

  @staticmethod
  def get_properties(lang='hive'):
    return ImpalaConfiguration.PROPERTIES if lang == 'impala' else HiveConfiguration.PROPERTIES


  @query_error_handler
  def create_session(self, lang='hive', properties=None):
    application = 'beeswax' if lang == 'hive' or lang == 'llap' else lang

    uses_session_pool = has_session_pool()
    uses_multiple_sessions = has_multiple_sessions()

    if lang == 'impala':
      uses_session_pool = False
      uses_multiple_sessions = False

    try:
      if uses_session_pool:
        session = Session.objects.get_tez_session(self.user, application, MAX_NUMBER_OF_SESSIONS.get())
      elif not uses_multiple_sessions:
        session = Session.objects.get_session(self.user, application=application)
      else:
        session = None
    except Exception as e:
      if 'Connection refused' in str(e) or 'Name or service not known' in str(e):
        LOG.exception('Connection being refused or service is not available in either session or in multiple sessions'
                      '- HA failover')
        reset_ha()

    reuse_session = session is not None
    if not reuse_session:
      db = dbms.get(self.user, query_server=get_query_server_config(name=lang, connector=self.interpreter))
      try:
        session = db.open_session(self.user)
      except Exception as e:
        if 'Connection refused' in str(e) or 'Name or service not known' in str(e):
          LOG.exception('Connection being refused or service is not available in reuse session - HA failover')
          reset_ha()

    response = {
      'type': lang,
      'id': session.id
    }

    if not properties:
      config = None
      if USE_DEFAULT_CONFIGURATION.get():
        config = DefaultConfiguration.objects.get_configuration_for_user(app=lang, user=self.user)

      if config is not None:
        properties = config.properties_list
      else:
        properties = self.get_properties(lang)

    response['properties'] = properties
    response['configuration'] = json.loads(session.properties)
    response['reuse_session'] = reuse_session
    response['session_id'] = ''

    try:
      decoded_guid = session.get_handle().sessionId.guid
      response['session_id'] = unpack_guid(decoded_guid)
    except Exception as e:
      LOG.warning('Failed to decode session handle: %s' % e)

    if lang == 'impala' and session:
      http_addr = _get_impala_server_url(session)
      response['http_addr'] = http_addr

    return response


  @query_error_handler
  def close_session(self, session):
    app_name = session.get('type')
    session_id = session.get('id')
    source_method = session.get("sourceMethod")

    if not session_id:
      session = Session.objects.get_session(self.user, application=app_name)
      decoded_guid = session.get_handle().sessionId.guid
      session_decoded_id = unpack_guid(decoded_guid)
      if source_method == "dt_logout":
        LOG.debug("Closing Impala session id %s on logout for user %s" % (session_decoded_id, self.user.username))

    query_server = get_query_server_config(name=app_name)

    response = {'status': -1, 'message': ''}
    session_record = None

    try:
      filters = {'id': session_id, 'application': query_server['server_name']}
      if not is_admin(self.user):
        filters['owner'] = self.user
      session_record = Session.objects.get(**filters)
    except Session.DoesNotExist:
      response['message'] = _('Session does not exist or you do not have permissions to close the session.')

    if session_record:
      session_record = dbms.get(self.user, query_server).close_session(session_record)
      response['status'] = 0
      response['message'] = _('Session successfully closed.')
      response['session'] = {'id': session_id, 'application': session_record.application, 'status': session_record.status_code}

    return response


  def close_session_idle(self, notebook, session):
    idle = True
    response = {'result': []}
    for snippet in [_s for _s in notebook['snippets'] if _s['type'] == session['type']]:
      try:
        if snippet['status'] != 'running':
          response['result'].append(self.close_statement(notebook, snippet))
        else:
          idle = False
          LOG.info('Not closing SQL snippet as still running.')
      except QueryExpired:
        pass
      except Exception as e:
        LOG.exception('Error closing statement %s' % str(e))

    close_sessions = CLOSE_SESSIONS.get()

    if session['type'] == 'impala':
      close_sessions = False

    try:
      if idle and close_sessions:
        response['result'].append(self.close_session(session))
    except QueryExpired:
      pass
    except Exception as e:
      LOG.exception('Error closing statement %s' % str(e))

    return response['result']

  @query_error_handler
  def execute(self, notebook, snippet):
    db = self._get_db(snippet, interpreter=self.interpreter)

    statement = self._get_current_statement(notebook, snippet)
    session = self._get_session(notebook, snippet['type'])

    query = self._prepare_hql_query(snippet, statement['statement'], session)
    _session = self._get_session_by_id(notebook, snippet['type'])

    try:
      if statement.get('statement_id') == 0: # TODO: move this to client
        if query.database and not statement['statement'].lower().startswith('set'):
          result = db.use(query.database, session=_session)
          if result.session:
            _session = result.session
      handle = db.client.query(query, session=_session)
    except QueryServerException as ex:
      raise QueryError(ex.message, handle=statement)

    # All good
    server_id, server_guid = handle.get()
    if sys.version_info[0] > 2:
      server_id = server_id.decode('utf-8')
      server_guid = server_guid.decode('utf-8')

    response = {
      'secret': server_id,
      'guid': server_guid,
      'operation_type': handle.operation_type,
      'has_result_set': handle.has_result_set,
      'modified_row_count': handle.modified_row_count,
      'log_context': handle.log_context,
      'session_guid': handle.session_guid,
      'session_id': handle.session_id,
      'session_type': snippet['type']
    }
    response.update(statement)

    return response


  @query_error_handler
  def check_status(self, notebook, snippet):
    response = {}
    db = self._get_db(snippet, interpreter=self.interpreter)

    handle = self._get_handle(snippet)
    operation = db.get_operation_status(handle)
    status = HiveServerQueryHistory.STATE_MAP[operation.operationState]

    if status.value in (QueryHistory.STATE.failed.value, QueryHistory.STATE.expired.value):
      if operation.errorMessage and 'transition from CANCELED to ERROR' in operation.errorMessage:  # Hive case on canceled query
        raise QueryExpired()
      elif operation.errorMessage and re.search(
          'Cannot validate serde: org.apache.hive.hcatalog.data.JsonSerDe', str(operation.errorMessage)
          ):
        raise QueryError(message=operation.errorMessage + _('. Is hive-hcatalog-core.jar registered?'))
      else:
        raise QueryError(operation.errorMessage)

    response['status'] = 'running' if status.value in (
        QueryHistory.STATE.running.value, QueryHistory.STATE.submitted.value
      ) else 'available'
    if operation.hasResultSet is not None:
      response['has_result_set'] = operation.hasResultSet  # HIVE-12442 - With LLAP hasResultSet can change after get_operation_status

    return response


  @query_error_handler
  def fetch_result(self, notebook, snippet, rows, start_over):
    db = self._get_db(snippet, interpreter=self.interpreter)

    handle = self._get_handle(snippet)
    try:
      results = db.fetch(handle, start_over=start_over, rows=rows)
    except QueryServerException as ex:
      if re.search('(client inactivity)|(Invalid query handle)', str(ex)) and ex.message:
        raise QueryExpired(message=ex.message)
      else:
        raise QueryError(ex)

    # No escaping...
    return {
        'has_more': results.has_more,
        'data': results.rows(),
        'meta': [{
            'name': column.name,
            'type': column.type,
            'comment': column.comment
          } for column in results.data_table.cols()
        ],
        'type': 'table'
    }


  @query_error_handler
  def fetch_result_size(self, notebook, snippet):
    resp = {
      'rows': None,
      'size': None,
      'message': ''
    }

    if snippet.get('status') != 'available':
      raise QueryError(_('Result status is not available'))

    if has_connectors():
      # TODO: Add dialect to snippet and update fetchResultSize() in notebook.ko
      interpreter = get_interpreter(connector_type=snippet['type'])
      snippet_dialect = interpreter['dialect']
    else:
      snippet_dialect = snippet['type']

    if snippet_dialect not in ('hive', 'impala'):
      raise OperationNotSupported(_('Cannot fetch result metadata for snippet type: %s') % snippet_dialect)

    if snippet_dialect == 'hive':
      resp['rows'], resp['size'], resp['message'] = self._get_hive_result_size(notebook, snippet)
    else:
      resp['rows'], resp['size'], resp['message'] = self._get_impala_result_size(notebook, snippet)

    return resp


  @query_error_handler
  def cancel(self, notebook, snippet):
    db = self._get_db(snippet, interpreter=self.interpreter)

    handle = self._get_handle(snippet)
    db.cancel_operation(handle)
    return {'status': 0}


  @query_error_handler
  def get_log(self, notebook, snippet, startFrom=None, size=None):
    db = self._get_db(snippet, interpreter=self.interpreter)

    handle = self._get_handle(snippet)
    return db.get_log(handle, start_over=startFrom == 0)


  @query_error_handler
  def close_statement(self, notebook, snippet):
    db = self._get_db(snippet, interpreter=self.interpreter)

    try:
      handle = self._get_handle(snippet)
      db.close_operation(handle)
    except Exception as e:
      if 'no valid handle' in str(e):
        return {'status': -1}  # skipped
      else:
        raise e
    return {'status': 0}


  def can_start_over(self, notebook, snippet):
    try:
      db = self._get_db(snippet, interpreter=self.interpreter)
      handle = self._get_handle(snippet)
      # Test handle to verify if still valid
      db.fetch(handle, start_over=True, rows=1)
      can_start_over = True
    except Exception as e:
      raise e
    return can_start_over


  @query_error_handler
  def progress(self, notebook, snippet, logs=''):
    patch_snippet_for_connector(snippet)

    if snippet['dialect'] == 'hive':
      match = re.search('Total jobs = (\d+)', logs, re.MULTILINE)
      total = int(match.group(1)) if match else 1

      started = logs.count('Starting Job')
      ended = logs.count('Ended Job')

      progress = int((started + ended) * 100 / (total * 2))
      return max(progress, 5)  # Return 5% progress as a minimum
    elif snippet['dialect'] == 'impala':
      match = re.findall('(\d+)% Complete', logs, re.MULTILINE)
      # Retrieve the last reported progress percentage if it exists
      return int(match[-1]) if match and isinstance(match, list) else 0
    else:
      return 50


  @query_error_handler
  def get_jobs(self, notebook, snippet, logs):
    jobs = []

    patch_snippet_for_connector(snippet)

    if snippet['dialect'] == 'hive':
      engine = self._get_hive_execution_engine(notebook, snippet)
      jobs_with_state = parse_out_jobs(logs, engine=engine, with_state=True)
      queries_with_state = parse_out_queries(logs, engine=engine, with_state=True)

      jobs = [{
          'name': job.get('job_id', ''),
          'url': reverse('jobbrowser:jobbrowser.views.single_job', kwargs={'job': job.get('job_id', '')}) if has_jobbrowser else '',
          'started': job.get('started', False),
          'finished': job.get('finished', False)
        }
        for job in jobs_with_state
      ]
      if has_hive_query_browser:
        jobs += [{
            'name': job.get('job_id', ''),
            'url': 'api/job/queries-hive/',
            'started': job.get('started', False),
            'finished': job.get('finished', False)
          }
          for job in queries_with_state
        ]
    elif snippet['dialect'] == 'impala' and has_query_browser:
      guid = snippet['result']['handle']['guid']
      if isinstance(guid, str):
        guid = guid.encode('utf-8')
      query_id = unpack_guid_base64(guid)
      progress = min(
          self.progress(notebook, snippet, logs), 99
        ) if snippet['status'] != 'available' and snippet['status'] != 'success' else 100
      jobs = [{
        'name': query_id,
        'url': '/hue/jobbrowser#!id=%s' % query_id,
        'started': True,
        'finished': False,
        'percentJob': progress
      }]

    return jobs


  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None, operation=None):
    db = self._get_db(snippet, interpreter=self.interpreter)
    query = None

    if snippet.get('query'):
      query = snippet.get('query')
    elif snippet.get('source') == 'query':
      document = Document2.objects.get(id=database)
      document.can_read_or_exception(self.user)
      notebook = Notebook(document=document).get_data()
      snippet = notebook['snippets'][0]
      query = self._get_current_statement(notebook, snippet)['statement']
      database, table = '', ''

    resp = _autocomplete(db, database, table, column, nested, query=query, cluster=self.interpreter, operation=operation)

    if resp.get('error'):
      resp['message'] = resp.pop('error')
      if 'Read timed out' in resp['message']:
        raise QueryExpired(resp['message'])

    return resp


  @query_error_handler
  def get_sample_data(self, snippet, database=None, table=None, column=None, is_async=False, operation=None):
    try:
      db = self._get_db(snippet, is_async=is_async, interpreter=self.interpreter)
      return _get_sample_data(db, database, table, column, is_async, operation=operation, cluster=self.interpreter)
    except QueryServerException as ex:
      raise QueryError(ex.message)


  @query_error_handler
  def explain(self, notebook, snippet):
    db = self._get_db(snippet, interpreter=self.interpreter)
    response = self._get_current_statement(notebook, snippet)
    session = self._get_session(notebook, snippet['type'])

    statement = response.pop('statement')
    explanation = ''

    query = self._prepare_hql_query(snippet, statement, session)

    if statement:
      try:
        db.use(query.database)

        explanation = db.explain(query).textual
        statement = query.get_query_statement(0)
      except QueryServerException as ex:
        explanation = str(ex.message)

    return {
      'status': 0,
      'explanation': explanation,
      'statement': statement,
    }


  @query_error_handler
  def export_data_as_hdfs_file(self, snippet, target_file, overwrite):
    db = self._get_db(snippet, interpreter=self.interpreter)

    handle = self._get_handle(snippet)
    max_rows = DOWNLOAD_ROW_LIMIT.get()
    max_bytes = DOWNLOAD_BYTES_LIMIT.get()

    upload(target_file, handle, self.request.user, db, self.request.fs, max_rows=max_rows, max_bytes=max_bytes)

    return '/filebrowser/view=%s' % urllib_quote(
        urllib_quote(target_file.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)
    ) # Quote twice, because of issue in the routing on client


  def export_data_as_table(self, notebook, snippet, destination, is_temporary=False, location=None):
    db = self._get_db(snippet, interpreter=self.interpreter)

    response = self._get_current_statement(notebook, snippet)
    session = self._get_session(notebook, snippet['type'])
    query = self._prepare_hql_query(snippet, response.pop('statement'), session)

    if 'select' not in query.hql_query.strip().lower():
      raise PopupException(_('Only SELECT statements can be saved. Provided statement: %(query)s') % {'query': query.hql_query})

    database = snippet.get('database') or 'default'
    table = destination

    if '.' in table:
      database, table = table.split('.', 1)

    db.use(query.database)

    hql = 'CREATE %sTABLE `%s`.`%s` %sAS %s' % (
        'TEMPORARY ' if is_temporary else '', database, table, "LOCATION '%s' " % location if location else '', query.hql_query
    )
    success_url = reverse('metastore:describe_table', kwargs={'database': database, 'table': table})

    return hql, success_url


  def export_large_data_to_hdfs(self, notebook, snippet, destination):
    response = self._get_current_statement(notebook, snippet)
    session = self._get_session(notebook, snippet['type'])
    query = self._prepare_hql_query(snippet, response.pop('statement'), session)

    if 'select' not in query.hql_query.strip().lower():
      raise PopupException(_('Only SELECT statements can be saved. Provided statement: %(query)s') % {'query': query.hql_query})

    hql = '''
DROP TABLE IF EXISTS `%(table)s`;

CREATE EXTERNAL TABLE `%(table)s` ROW FORMAT DELIMITED
     FIELDS TERMINATED BY '\\t'
     ESCAPED BY '\\\\'
     LINES TERMINATED BY '\\n'
     STORED AS TEXTFILE LOCATION '%(location)s'
     AS
%(hql)s;

DROP TABLE IF EXISTS `%(table)s`;
    ''' % {
      'table': _get_snippet_name(notebook, unique=True, table_format=True),
      'location': self.request.fs.netnormpath(destination),
      'hql': query.hql_query
    }
    success_url = '/filebrowser/view=%s' % urllib_quote(destination.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)

    return hql, success_url


  def upgrade_properties(self, lang='hive', properties=None):
    upgraded_properties = copy.deepcopy(self.get_properties(lang))

    # Check that current properties is a list of dictionary objects with 'key' and 'value' keys
    if not isinstance(properties, list) or \
      not all(isinstance(prop, dict) for prop in properties) or \
      not all('key' in prop for prop in properties) or not all('value' in prop for prop in properties):
      LOG.warning('Current properties are not formatted correctly, will replace with defaults.')
      return upgraded_properties

    valid_props_dict = dict((prop["key"], prop) for prop in upgraded_properties)
    curr_props_dict = dict((prop['key'], prop) for prop in properties)

    # Upgrade based on valid properties as needed
    if set(valid_props_dict.keys()) != set(curr_props_dict.keys()):
      settings = next((prop for prop in upgraded_properties if prop['key'] == 'settings'), None)
      if settings is not None and isinstance(properties, list):
        settings['value'] = properties
    else:  # No upgrade needed so return existing properties
      upgraded_properties = properties

    return upgraded_properties


  def _get_session(self, notebook, type='hive'):
    session = next((session for session in notebook['sessions'] if session['type'] == type), None)
    return session

  def _get_session_by_id(self, notebook, type='hive'):
    session = self._get_session(notebook, type)
    if session:
      session_id = session.get('id')
      if session_id:
        filters = {'id': session_id, 'application': 'beeswax' if type == 'hive' or type == 'llap' else type}
        if not is_admin(self.user):
          filters['owner'] = self.user
        return Session.objects.get(**filters)


  def _get_hive_execution_engine(self, notebook, snippet):
    # Get hive.execution.engine from snippet properties, if none, then get from session
    properties = snippet['properties']
    settings = properties.get('settings', [])

    if not settings:
      session = self._get_session(notebook, 'hive')
      if not session:
        LOG.warning('Cannot get jobs, failed to find active HS2 session for user: %s' % self.user.username)
      elif session.get('configuration') and session['configuration'].get('hive.execution.engine'):
        return session['configuration'].get('hive.execution.engine')
      else:
        properties = session['properties']
        settings = next((prop['value'] for prop in properties if prop['key'] == 'settings'), None)

    if settings:
      engine = next((setting['value'] for setting in settings if setting['key'] == 'hive.execution.engine'), DEFAULT_HIVE_ENGINE)
    else:
      engine = DEFAULT_HIVE_ENGINE

    return engine


  def _prepare_hql_query(self, snippet, statement, session):
    settings = snippet['properties'].get('settings', None)
    file_resources = snippet['properties'].get('files', None)
    functions = snippet['properties'].get('functions', None)
    properties = session['properties'] if session else []

    # Get properties from session if not defined in snippet
    if not settings:
      settings = next((prop['value'] for prop in properties if prop['key'] == 'settings'), None)

    if not file_resources:
      file_resources = next((prop['value'] for prop in properties if prop['key'] == 'files'), None)

    if not functions:
      functions = next((prop['value'] for prop in properties if prop['key'] == 'functions'), None)

    database = snippet.get('database') or 'default'
    query_type = QUERY_TYPES[4] if 'dialect' in snippet and snippet['dialect'] == 'hplsql' else QUERY_TYPES[0]

    return hql_query(
      statement,
      query_type=query_type,
      settings=settings,
      file_resources=file_resources,
      functions=functions,
      database=database
    )


  def get_browse_query(self, snippet, database, table, partition_spec=None):
    db = self._get_db(snippet, interpreter=self.interpreter)
    table = db.get_table(database, table)
    if table.is_impala_only:
      snippet['type'] = 'impala'
      db = self._get_db(snippet, interpreter=self.interpreter)

    if partition_spec is not None:
      decoded_spec = urllib_unquote(partition_spec)
      return db.get_partition(database, table.name, decoded_spec, generate_ddl_only=True)
    else:
      return db.get_select_star_query(database, table, limit=100)


  def _get_handle(self, snippet):
    try:
      handle = snippet['result']['handle'].copy()
      handle['secret'], handle['guid'] = HiveServerQueryHandle.get_decoded(handle['secret'], handle['guid'])
    except KeyError:
      raise Exception('Operation has no valid handle attached')
    except binascii.Error:
      LOG.warning('Handle already base 64 decoded')

    for key in list(handle.keys()):
      if key not in ('log_context', 'secret', 'has_result_set', 'operation_type', 'modified_row_count', 'guid'):
        handle.pop(key)

    return HiveServerQueryHandle(**handle)


  def _get_db(self, snippet, is_async=False, interpreter=None):
    if interpreter and interpreter.get('dialect'):
      dialect = interpreter['dialect']
    else:
      dialect = snippet['type']  # Backward compatibility without connectors

    if not is_async and dialect == 'hive':
      name = 'beeswax'
    elif dialect == 'hive':
      name = 'hive'
    elif dialect == 'llap':
      name = 'llap'
    elif dialect == 'impala':
      name = 'impala'
    elif dialect == 'hplsql':
      name = 'hplsql'
    else:
      name = 'sparksql'

    # Note: name is not used if interpreter is present
    return dbms.get(self.user, query_server=get_query_server_config(name=name, connector=interpreter))


  def _parse_job_counters(self, job_id):
    # Attempt to fetch total records from the job's Hive counter
    total_records, total_size = None, None
    job = get_job(self.request, job_id=job_id)

    if not job or not job.counters:
      raise PopupException(_('Failed to get job details or job does not contain counters data.'))

    counter_groups = job.counters.get('counterGroup')  # Returns list of counter groups with 'counterGroupName' and 'counter'
    if counter_groups:
      # Extract totalCounterValue from HIVE counter group
      hive_counters = next((group for group in counter_groups if group.get('counterGroupName', '').upper() == 'HIVE'), None)
      if hive_counters:
        total_records = next(
          (counter.get('totalCounterValue') for counter in hive_counters['counter'] if counter['name'] == 'RECORDS_OUT_0'),
          None
        )
      else:
        LOG.info("No HIVE counter group found for job: %s" % job_id)

      # Extract totalCounterValue from FileSystemCounter counter group
      fs_counters = next(
          (group for group in counter_groups if group.get('counterGroupName') == 'org.apache.hadoop.mapreduce.FileSystemCounter'),
          None
        )
      if fs_counters:
        total_size = next(
          (counter.get('totalCounterValue') for counter in fs_counters['counter'] if counter['name'] == 'HDFS_BYTES_WRITTEN'),
          None
        )
      else:
        LOG.info("No FileSystemCounter counter group found for job: %s" % job_id)

    return total_records, total_size


  def _get_hive_result_size(self, notebook, snippet):
    total_records, total_size, msg = None, None, None
    engine = self._get_hive_execution_engine(notebook, snippet).lower()
    logs = self.get_log(notebook, snippet, startFrom=0)

    if engine == 'mr':
      jobs = self.get_jobs(notebook, snippet, logs)
      if jobs:
        last_job_id = jobs[-1].get('name')
        LOG.info("Hive query executed %d jobs, last job is: %s" % (len(jobs), last_job_id))
        total_records, total_size = self._parse_job_counters(job_id=last_job_id)
      else:
        msg = _('Hive query did not execute any jobs.')
    elif engine == 'spark':
      total_records_re = "RECORDS_OUT_0: (?P<total_records>\d+)"
      total_size_re = "Spark Job\[[a-z0-9-]+\] Metrics[A-Za-z0-9:\s]+ResultSize: (?P<total_size>\d+)"
      total_records_match = re.search(total_records_re, logs, re.MULTILINE)
      total_size_match = re.search(total_size_re, logs, re.MULTILINE)

      if total_records_match:
        total_records = int(total_records_match.group('total_records'))
      if total_size_match:
        total_size = int(total_size_match.group('total_size'))

    return total_records, total_size, msg


  def _get_impala_result_size(self, notebook, snippet):
    total_records_match = None
    total_records, total_size, msg = None, None, None

    query_id = self._get_impala_query_id(snippet)
    server_url = _get_api(self.user, snippet)._url

    if query_id:
      LOG.debug("Attempting to get Impala query profile at server_url %s for query ID: %s" % (server_url, query_id))

      fragment = self._get_impala_query_profile(server_url, query_id=query_id)
      total_records_re = \
          "Coordinator Fragment F\d\d.+?RowsReturned: \d+(?:.\d+[KMB])? \((?P<total_records>\d+)\).*?(Averaged Fragment F\d\d)"
      total_records_match = re.search(total_records_re, fragment, re.MULTILINE | re.DOTALL)

    if total_records_match:
      total_records = int(total_records_match.group('total_records'))
      query_plan = self._get_impala_profile_plan(query_id, fragment)
      if query_plan:
        LOG.debug('Query plan for Impala query %s: %s' % (query_id, query_plan))
      else:
        LOG.info('Query plan for Impala query %s not found.' % query_id)

    return total_records, total_size, msg


  def _get_impala_query_id(self, snippet):
    guid = None
    if 'result' in snippet and 'handle' in snippet['result'] and 'guid' in snippet['result']['handle']:
      try:
        guid = unpack_guid_base64(snippet['result']['handle']['guid'])
      except Exception as e:
        LOG.warning('Failed to decode operation handle guid: %s' % e)
    else:
      LOG.warning('Snippet does not contain a valid result handle, cannot extract Impala query ID.')
    return guid


  def _get_impala_query_profile(self, server_url, query_id):
    api = get_impalad_api(user=self.user, url=server_url)

    try:
      query_profile = api.get_query_profile(query_id)
      profile = query_profile.get('profile')
    except (RestException, ImpalaDaemonApiException) as e:
      raise PopupException(_("Failed to get query profile from Impala Daemon server: %s") % e)

    if not profile:
      raise PopupException(_("Could not find profile in query profile response from Impala Daemon Server."))

    return profile


  def _get_impala_profile_plan(self, query_id, profile):
    query_plan_re = "Query \(id=%(query_id)s\):.+?Execution Profile %(query_id)s" % {'query_id': query_id}
    query_plan_match = re.search(query_plan_re, profile, re.MULTILINE | re.DOTALL)
    return query_plan_match.group() if query_plan_match else None


  def describe_column(self, notebook, snippet, database=None, table=None, column=None):
    db = self._get_db(snippet, interpreter=self.interpreter)
    return db.get_table_columns_stats(database, table, column)


  def describe_table(self, notebook, snippet, database=None, table=None):
    db = self._get_db(snippet, interpreter=self.interpreter)
    tb = db.get_table(database, table)

    return {
      'status': 0,
      'name': tb.name,
      'partition_keys': [{'name': part.name, 'type': part.type} for part in tb.partition_keys],
      'primary_keys': [{'name': pk.name} for pk in tb.primary_keys],
      'cols': [{'name': col.name, 'type': col.type, 'comment': col.comment} for col in tb.cols],
      'path_location': tb.path_location,
      'hdfs_link': tb.hdfs_link,
      'comment': tb.comment,
      'is_view': tb.is_view,
      'properties': tb.properties,
      'details': tb.details,
      'stats': tb.stats
    }

  def describe_database(self, notebook, snippet, database=None):
    db = self._get_db(snippet, interpreter=self.interpreter)
    return db.get_database(database)

  def get_log_is_full_log(self, notebook, snippet):
    return snippet['type'] != 'hive' and snippet['type'] != 'impala'
