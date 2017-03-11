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

import base64
import binascii
import copy
import hashlib
import logging
import re
import StringIO
import struct

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.conf import USE_DEFAULT_CONFIGURATION
from desktop.lib.conf import BoundConfig
from desktop.lib.exceptions import StructuredException
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode, smart_str
from desktop.lib.rest.http_client import RestException
from desktop.models import DefaultConfiguration
from metadata.optimizer_client import OptimizerApi

from notebook.connectors.base import Api, QueryError, QueryExpired, OperationTimeout, OperationNotSupported, _get_snippet_name


LOG = logging.getLogger(__name__)


try:
  from beeswax import conf as beeswax_conf, data_export
  from beeswax.api import _autocomplete, _get_sample_data
  from beeswax.conf import CONFIG_WHITELIST as hive_settings, DOWNLOAD_ROW_LIMIT
  from beeswax.data_export import upload
  from beeswax.design import hql_query, strip_trailing_semicolon, split_statements
  from beeswax.models import QUERY_TYPES, HiveServerQueryHandle, HiveServerQueryHistory, QueryHistory, Session
  from beeswax.server import dbms
  from beeswax.server.dbms import get_query_server_config, QueryServerException
  from beeswax.views import parse_out_jobs
except ImportError, e:
  LOG.warn('Hive and HiveServer2 interfaces are not enabled')
  hive_settings = None

try:
  from impala import api   # Force checking if Impala is enabled
  from impala.conf import CONFIG_WHITELIST as impala_settings, SSL as impala_ssl_conf
  from impala.impala_flags import get_webserver_certificate_file
  from impala.server import get_api as get_impalad_api, ImpalaDaemonApiException
except ImportError, e:
  LOG.warn("Impala app is not enabled")
  impala_settings = None

try:
  from jobbrowser.views import get_job
except (AttributeError, ImportError), e:
  LOG.warn("Job Browser app is not enabled")


DEFAULT_HIVE_ENGINE = 'mr'


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except StructuredException, e:
      message = force_unicode(str(e))
      if 'timed out' in message:
        raise OperationTimeout(e)
      else:
        raise QueryError(message)
    except QueryServerException, e:
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
    application = 'beeswax' if lang == 'hive' else lang

    session = Session.objects.get_session(self.user, application=application)

    if session is None:
      session = dbms.get(self.user, query_server=get_query_server_config(name=lang)).open_session(self.user)

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

    if lang == 'impala':
      http_addr = self._get_impala_server_url(session)
      response['http_addr'] = http_addr

    return response


  @query_error_handler
  def close_session(self, session):
    app_name = session.get('type')
    session_id = session.get('id')

    query_server = get_query_server_config(name=app_name)

    response = {'status': -1, 'message': ''}

    try:
      filters = {'id': session_id, 'application': query_server['server_name']}
      if not self.user.is_superuser:
        filters['owner'] = self.user
      session = Session.objects.get(**filters)
    except Session.DoesNotExist:
      response['message'] = _('Session does not exist or you do not have permissions to close the session.')

    if session:
      session = dbms.get(self.user, query_server).close_session(session)
      response['status'] = 0
      response['message'] = _('Session successfully closed.')
      response['session'] = {'id': session_id, 'application': session.application, 'status': session.status_code}

    return response


  @query_error_handler
  def execute(self, notebook, snippet):
    db = self._get_db(snippet)

    statement = self._get_current_statement(db, snippet)
    session = self._get_session(notebook, snippet['type'])

    query = self._prepare_hql_query(snippet, statement['statement'], session)

    try:
      if statement.get('statement_id') == 0:
        if query.database:
          db.use(query.database)
      handle = db.client.query(query, withMultipleSession=True)
    except QueryServerException, ex:
      raise QueryError(ex.message, handle=statement)

    # All good
    server_id, server_guid = handle.get()
    response = {
      'secret': server_id,
      'guid': server_guid,
      'operation_type': handle.operation_type,
      'has_result_set': handle.has_result_set,
      'modified_row_count': handle.modified_row_count,
      'log_context': handle.log_context,
      'session_guid': handle.session_guid
    }
    response.update(statement)

    return response


  @query_error_handler
  def check_status(self, notebook, snippet):
    response = {}
    db = self._get_db(snippet)

    handle = self._get_handle(snippet)
    operation = db.get_operation_status(handle)
    status = HiveServerQueryHistory.STATE_MAP[operation.operationState]

    if status.index in (QueryHistory.STATE.failed.index, QueryHistory.STATE.expired.index):
      if operation.errorMessage and 'transition from CANCELED to ERROR' in operation.errorMessage: # Hive case on canceled query
        raise QueryExpired()
      elif  operation.errorMessage and re.search('Cannot validate serde: org.apache.hive.hcatalog.data.JsonSerDe', str(operation.errorMessage)):
        raise QueryError(message=operation.errorMessage + _('. Is hive-hcatalog-core.jar registered?'))
      else:
        raise QueryError(operation.errorMessage)

    response['status'] = 'running' if status.index in (QueryHistory.STATE.running.index, QueryHistory.STATE.submitted.index) else 'available'

    return response


  @query_error_handler
  def fetch_result(self, notebook, snippet, rows, start_over):
    db = self._get_db(snippet)

    handle = self._get_handle(snippet)
    try:
      results = db.fetch(handle, start_over=start_over, rows=rows)
    except QueryServerException, ex:
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
        } for column in results.data_table.cols()],
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

    if snippet['type'] not in ('hive', 'impala'):
      raise OperationNotSupported(_('Cannot fetch result metadata for snippet type: %s') % snippet['type'])

    if snippet['type'] == 'hive':
      resp['rows'], resp['size'], resp['message'] = self._get_hive_result_size(notebook, snippet)
    else:
      resp['rows'], resp['size'], resp['message'] = self._get_impala_result_size(notebook, snippet)

    return resp


  @query_error_handler
  def cancel(self, notebook, snippet):
    db = self._get_db(snippet)

    handle = self._get_handle(snippet)
    db.cancel_operation(handle)
    return {'status': 0}


  @query_error_handler
  def get_log(self, notebook, snippet, startFrom=None, size=None):
    db = self._get_db(snippet)

    handle = self._get_handle(snippet)
    return db.get_log(handle, start_over=startFrom == 0)


  @query_error_handler
  def close_statement(self, snippet):
    if snippet['type'] == 'impala':
      from impala import conf as impala_conf

    if (snippet['type'] == 'hive' and beeswax_conf.CLOSE_QUERIES.get()) or (snippet['type'] == 'impala' and impala_conf.CLOSE_QUERIES.get()):
      db = self._get_db(snippet)

      handle = self._get_handle(snippet)
      db.close_operation(handle)
      return {'status': 0}
    else:
      return {'status': -1}  # skipped


  @query_error_handler
  def download(self, notebook, snippet, format):
    try:
      db = self._get_db(snippet)
      handle = self._get_handle(snippet)
      # Test handle to verify if still valid
      db.fetch(handle, start_over=True, rows=1)

      file_name = _get_snippet_name(notebook)

      return data_export.download(handle, format, db, id=snippet['id'], file_name=file_name)
    except Exception, e:
      title = 'The query result cannot be downloaded.'
      LOG.exception(title)

      if hasattr(e, 'message') and e.message:
        if 'generic failure: Unable to find a callback: 32775' in e.message:
          message = e.message + " " + _("Increase the sasl_max_buffer value in hue.ini")
        elif 'query result cache exceeded its limit' in e.message:
          message = e.message.replace("Restarting the fetch is not possible.", _("Please execute the query again."))
        else:
          message = e.message
      else:
        message = e
      raise PopupException(_(title), detail=message)


  @query_error_handler
  def progress(self, snippet, logs):
    if snippet['type'] == 'hive':
      match = re.search('Total jobs = (\d+)', logs, re.MULTILINE)
      total = int(match.group(1)) if match else 1

      started = logs.count('Starting Job')
      ended = logs.count('Ended Job')

      progress = int((started + ended) * 100 / (total * 2))
      return max(progress, 5)  # Return 5% progress as a minimum
    elif snippet['type'] == 'impala':
      match = re.findall('(\d+)% Complete', logs, re.MULTILINE)
      # Retrieve the last reported progress percentage if it exists
      return int(match[-1]) if match and isinstance(match, list) else 0
    else:
      return 50


  @query_error_handler
  def get_jobs(self, notebook, snippet, logs):
    jobs = []

    if snippet['type'] == 'hive':
      engine = self._get_hive_execution_engine(notebook, snippet)
      jobs_with_state = parse_out_jobs(logs, engine=engine, with_state=True)

      jobs = [{
        'name': job.get('job_id', ''),
        'url': reverse('jobbrowser.views.single_job', kwargs={'job': job.get('job_id', '')}),
        'started': job.get('started', False),
        'finished': job.get('finished', False)
      } for job in jobs_with_state]

    return jobs


  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None):
    db = self._get_db(snippet)
    return _autocomplete(db, database, table, column, nested)


  @query_error_handler
  def get_sample_data(self, snippet, database=None, table=None, column=None):
    try:
      db = self._get_db(snippet)
      return _get_sample_data(db, database, table, column)
    except QueryServerException, ex:
      raise QueryError(ex.message)


  @query_error_handler
  def explain(self, notebook, snippet):
    db = self._get_db(snippet)
    response = self._get_current_statement(db, snippet)
    session = self._get_session(notebook, snippet['type'])

    query = self._prepare_hql_query(snippet, response.pop('statement'), session)

    try:
      db.use(query.database)

      explanation = db.explain(query)
    except QueryServerException, ex:
      raise QueryError(ex.message)

    return {
      'status': 0,
      'explanation': explanation.textual,
      'statement': query.get_query_statement(0),
    }


  @query_error_handler
  def export_data_as_hdfs_file(self, snippet, target_file, overwrite):
    db = self._get_db(snippet)

    handle = self._get_handle(snippet)
    max_rows = DOWNLOAD_ROW_LIMIT.get()

    upload(target_file, handle, self.request.user, db, self.request.fs, max_rows=max_rows)

    return '/filebrowser/view=%s' % target_file


  def export_data_as_table(self, notebook, snippet, destination, is_temporary=False, location=None):
    db = self._get_db(snippet)

    response = self._get_current_statement(db, snippet)
    session = self._get_session(notebook, snippet['type'])
    query = self._prepare_hql_query(snippet, response.pop('statement'), session)

    if 'select' not in query.hql_query.strip().lower():
      raise PopupException(_('Only SELECT statements can be saved. Provided statement: %(query)s') % {'query': query.hql_query})

    database = snippet.get('database') or 'default'
    table = destination

    if '.' in table:
      database, table = table.split('.', 1)

    db.use(query.database)

    hql = 'CREATE %sTABLE `%s`.`%s` %sAS %s' % ('TEMPORARY ' if is_temporary else '', database, table, "LOCATION '%s' " % location if location else '', query.hql_query)
    success_url = reverse('metastore:describe_table', kwargs={'database': database, 'table': table})

    return hql, success_url


  def export_large_data_to_hdfs(self, notebook, snippet, destination):
    db = self._get_db(snippet)

    response = self._get_current_statement(db, snippet)
    session = self._get_session(notebook, snippet['type'])
    query = self._prepare_hql_query(snippet, response.pop('statement'), session)

    if 'select' not in query.hql_query.strip().lower():
      raise PopupException(_('Only SELECT statements can be saved. Provided statement: %(query)s') % {'query': query.hql_query})

    hql = '''
DROP TABLE IF EXISTS `%(table)s`;

CREATE TABLE `%(table)s` ROW FORMAT DELIMITED
     FIELDS TERMINATED BY '\\t'
     ESCAPED BY '\\\\'
     LINES TERMINATED BY '\\n'
     STORED AS TEXTFILE LOCATION '%(location)s'
     AS
%(hql)s;

ALTER TABLE `%(table)s` SET TBLPROPERTIES('EXTERNAL'='TRUE');

DROP TABLE IF EXISTS `%(table)s`;
    ''' % {
      'table': _get_snippet_name(notebook, unique=True, table_format=True),
      'location': destination,
      'hql': query.hql_query
    }
    success_url = '/filebrowser/view=%s' % destination

    return hql, success_url


  def statement_risk(self, notebook, snippet):
    db = self._get_db(snippet)

    response = self._get_current_statement(db, snippet)
    query = response['statement']

    api = OptimizerApi()

    data = api.query_risk(query=query)
    data = data.get(snippet['type'] + 'Risk', {})

    return {
      'risk': data.get('risk'),
      'riskAnalysis': data.get('riskAnalysis'),
      'riskRecommendation': data.get('riskRecommendation')
    }


  def statement_compatibility(self, notebook, snippet, source_platform, target_platform):
    db = self._get_db(snippet)

    response = self._get_current_statement(db, snippet)
    query = response['statement']

    api = OptimizerApi()

    return api.query_compatibility(source_platform, target_platform, query)


  def statement_similarity(self, notebook, snippet, source_platform):
    db = self._get_db(snippet)

    response = self._get_current_statement(db, snippet)
    query = response['statement']

    api = OptimizerApi()

    return api.similar_queries(source_platform, query)


  def upgrade_properties(self, lang='hive', properties=None):
    upgraded_properties = copy.deepcopy(self.get_properties(lang))

    # Check that current properties is a list of dictionary objects with 'key' and 'value' keys
    if not isinstance(properties, list) or \
      not all(isinstance(prop, dict) for prop in properties) or \
      not all('key' in prop for prop in properties) or not all('value' in prop for prop in properties):
      LOG.warn('Current properties are not formatted correctly, will replace with defaults.')
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


  def _get_hive_execution_engine(self, notebook, snippet):
    # Get hive.execution.engine from snippet properties, if none, then get from session
    properties = snippet['properties']
    settings = properties.get('settings', [])

    if not settings:
      session = self._get_session(notebook, 'hive')
      if not session:
        LOG.warn('Cannot get jobs, failed to find active HS2 session for user: %s' % self.user.username)
      else:
        properties = session['properties']
        settings = next((prop['value'] for prop in properties if prop['key'] == 'settings'), None)

    if settings:
      engine = next((setting['value'] for setting in settings if setting['key'] == 'hive.execution.engine'), DEFAULT_HIVE_ENGINE)
    else:
      engine = DEFAULT_HIVE_ENGINE

    return engine


  def _get_statements(self, hql_query):
    hql_query = strip_trailing_semicolon(hql_query)
    hql_query_sio = StringIO.StringIO(hql_query)

    statements = []
    for (start_row, start_col), (end_row, end_col), statement in split_statements(hql_query_sio.read()):
      statements.append({
        'start': {
          'row': start_row,
          'column': start_col
        },
        'end': {
          'row': end_row,
          'column': end_col
        },
        'statement': strip_trailing_semicolon(statement.rstrip())
      })
    return statements


  def _get_current_statement(self, db, snippet):
    # Multiquery, if not first statement or arrived to the last query
    statement_id = snippet['result']['handle'].get('statement_id', 0)
    statements_count = snippet['result']['handle'].get('statements_count', 1)

    statements = self._get_statements(snippet['statement'])

    statement_id = min(statement_id, len(statements) - 1) # In case of removal of statements
    previous_statement_hash = self.__compute_statement_hash(statements[statement_id]['statement'])
    non_edited_statement = previous_statement_hash == snippet['result']['handle'].get('previous_statement_hash') or not snippet['result']['handle'].get('previous_statement_hash')

    if snippet['result']['handle'].get('has_more_statements'):
      try:
        handle = self._get_handle(snippet)
        db.close_operation(handle)  # Close all the time past multi queries
      except:
        LOG.warn('Could not close previous multiquery query')

      if non_edited_statement:
        statement_id += 1
    else:
      if non_edited_statement:
        statement_id = 0

    if statements_count != len(statements):
      statement_id = min(statement_id, len(statements) - 1)

    resp = {
      'statement_id': statement_id,
      'has_more_statements': statement_id < len(statements) - 1,
      'statements_count': len(statements),
      'previous_statement_hash': self.__compute_statement_hash(statements[statement_id]['statement'])
    }

    resp.update(statements[statement_id])
    return resp


  def __compute_statement_hash(self, statement):
    return hashlib.sha224(smart_str(statement)).hexdigest()


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

    return hql_query(
      statement,
      query_type=QUERY_TYPES[0],
      settings=settings,
      file_resources=file_resources,
      functions=functions,
      database=database
    )


  def get_select_star_query(self, snippet, database, table):
    db = self._get_db(snippet)
    table = db.get_table(database, table)
    if table.is_impala_only:
      snippet['type'] = 'impala'
      db = self._get_db(snippet)

    return db.get_select_star_query(database, table, limit=100)


  def _get_handle(self, snippet):
    try:
      snippet['result']['handle']['secret'], snippet['result']['handle']['guid'] = HiveServerQueryHandle.get_decoded(snippet['result']['handle']['secret'], snippet['result']['handle']['guid'])
    except KeyError:
      raise Exception('Operation has no valid handle attached')
    except binascii.Error:
      LOG.warn('Handle already base 64 decoded')

    for key in snippet['result']['handle'].keys():
      if key not in ('log_context', 'secret', 'has_result_set', 'operation_type', 'modified_row_count', 'guid'):
        snippet['result']['handle'].pop(key)

    return HiveServerQueryHandle(**snippet['result']['handle'])


  def _get_db(self, snippet):
    if snippet['type'] == 'hive':
      name = 'beeswax'
    elif snippet['type'] == 'impala':
      name = 'impala'
    else:
      name = 'sparksql'

    return dbms.get(self.user, query_server=get_query_server_config(name=name))


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
        total_records = next((counter.get('totalCounterValue') for counter in hive_counters['counter'] if counter['name'] == 'RECORDS_OUT_0'), None)
      else:
        LOG.info("No HIVE counter group found for job: %s" % job_id)

      # Extract totalCounterValue from FileSystemCounter counter group
      fs_counters = next((group for group in counter_groups if group.get('counterGroupName') == 'org.apache.hadoop.mapreduce.FileSystemCounter'), None)
      if fs_counters:
        total_size = next((counter.get('totalCounterValue') for counter in fs_counters['counter'] if counter['name'] == 'HDFS_BYTES_WRITTEN'), None)
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
    session = Session.objects.get_session(self.user, application='impala')
    protocol = 'https' if get_webserver_certificate_file() else 'http'
    server_url = '%s://%s' % (protocol, self._get_impala_server_url(session))
    if query_id:
      LOG.info("Attempting to get Impala query profile at server_url %s for query ID: %s" % (server_url, query_id))

      fragment = self._get_impala_query_profile(server_url, query_id=query_id)
      total_records_re = "Coordinator Fragment F\d\d.+?RowsReturned: \d+(?:.\d+[KMB])? \((?P<total_records>\d+)\).*?(Averaged Fragment F\d\d)"
      total_records_match = re.search(total_records_re, fragment, re.MULTILINE | re.DOTALL)

    if total_records_match:
      total_records = int(total_records_match.group('total_records'))

    return total_records, total_size, msg


  def _get_impala_query_id(self, snippet):
    guid = None
    if 'result' in snippet and 'handle' in snippet['result'] and 'guid' in snippet['result']['handle']:
      try:
        decoded_guid = base64.decodestring(snippet['result']['handle']['guid'])
        guid = "%x:%x" % struct.unpack(b"QQ", decoded_guid)
      except Exception, e:
        LOG.warn('Failed to decode operation handle guid: %s' % e)
    else:
      LOG.warn('Snippet does not contain a valid result handle, cannot extract Impala query ID.')
    return guid


  def _get_impala_server_url(self, session):
    impala_settings = session.get_formatted_properties()
    http_addr = next((setting['value'] for setting in impala_settings if setting['key'].lower() == 'http_addr'), None)
    return http_addr


  def _get_impala_query_profile(self, server_url, query_id):
    api = get_impalad_api(user=self.user, url=server_url)

    try:
      query_profile = api.get_query_profile(query_id)
      profile = query_profile.get('profile')
    except (RestException, ImpalaDaemonApiException), e:
      raise PopupException(_("Failed to get query profile from Impala Daemon server: %s") % e)

    if not profile:
      raise PopupException(_("Could not find profile in query profile response from Impala Daemon Server."))

    return profile
