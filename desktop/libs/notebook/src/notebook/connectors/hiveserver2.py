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

import binascii
import copy
import json
import logging
import re
import urllib

from django.urls import reverse
from django.utils.translation import ugettext as _

from desktop.auth.backend import is_admin
from desktop.conf import USE_DEFAULT_CONFIGURATION
from desktop.lib.conf import BoundConfig
from desktop.lib.exceptions import StructuredException
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode
from desktop.lib.paths import SAFE_CHARACTERS_URI_COMPONENTS
from desktop.lib.rest.http_client import RestException
from desktop.lib.thrift_util import unpack_guid, unpack_guid_base64
from desktop.models import DefaultConfiguration, Document2
from metadata.optimizer_client import OptimizerApi

from notebook.connectors.base import Api, QueryError, QueryExpired, OperationTimeout, OperationNotSupported, _get_snippet_name, Notebook

LOG = logging.getLogger(__name__)


try:
  from beeswax import conf as beeswax_conf, data_export
  from beeswax.api import _autocomplete, _get_sample_data
  from beeswax.conf import CONFIG_WHITELIST as hive_settings, DOWNLOAD_ROW_LIMIT, DOWNLOAD_BYTES_LIMIT
  from beeswax.data_export import upload
  from beeswax.design import hql_query
  from beeswax.models import QUERY_TYPES, HiveServerQueryHandle, HiveServerQueryHistory, QueryHistory, Session
  from beeswax.server import dbms
  from beeswax.server.dbms import get_query_server_config, QueryServerException
  from beeswax.views import parse_out_jobs
except ImportError, e:
  LOG.warn('Hive and HiveServer2 interfaces are not enabled: %s' % e)
  hive_settings = None

try:
  from impala import api   # Force checking if Impala is enabled
  from impala.dbms import _get_server_name
  from impala.conf import CONFIG_WHITELIST as impala_settings
  from impala.server import get_api as get_impalad_api, ImpalaDaemonApiException, _get_impala_server_url
except ImportError, e:
  LOG.warn("Impala app is not enabled")
  impala_settings = None

try:
  from jobbrowser.views import get_job
  from jobbrowser.conf import ENABLE_QUERY_BROWSER
  has_query_browser = ENABLE_QUERY_BROWSER.get()
except (AttributeError, ImportError), e:
  LOG.warn("Job Browser app is not enabled")
  has_query_browser = False


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

    reuse_session = session is not None
    if not reuse_session:
      session = dbms.get(self.user, query_server=get_query_server_config(name=lang, cluster=self.cluster)).open_session(self.user)

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
    except Exception, e:
      LOG.warn('Failed to decode session handle: %s' % e)

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

    try:
      filters = {'id': session_id, 'application': query_server['server_name']}
      if not is_admin(self.user):
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
    db = self._get_db(snippet, cluster=self.cluster)

    statement = self._get_current_statement(notebook, snippet)
    session = self._get_session(notebook, snippet['type'])

    query = self._prepare_hql_query(snippet, statement['statement'], session)

    try:
      if statement.get('statement_id') == 0:
        if query.database and not statement['statement'].lower().startswith('set'):
          db.use(query.database)
      handle = db.client.query(query, with_multiple_session=True)
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
    db = self._get_db(snippet, cluster=self.cluster)

    handle = self._get_handle(snippet)
    operation = db.get_operation_status(handle)
    status = HiveServerQueryHistory.STATE_MAP[operation.operationState]

    if status.value in (QueryHistory.STATE.failed.value, QueryHistory.STATE.expired.value):
      if operation.errorMessage and 'transition from CANCELED to ERROR' in operation.errorMessage: # Hive case on canceled query
        raise QueryExpired()
      elif  operation.errorMessage and re.search('Cannot validate serde: org.apache.hive.hcatalog.data.JsonSerDe', str(operation.errorMessage)):
        raise QueryError(message=operation.errorMessage + _('. Is hive-hcatalog-core.jar registered?'))
      else:
        raise QueryError(operation.errorMessage)

    response['status'] = 'running' if status.value in (QueryHistory.STATE.running.value, QueryHistory.STATE.submitted.value) else 'available'

    return response


  @query_error_handler
  def fetch_result(self, notebook, snippet, rows, start_over):
    db = self._get_db(snippet, cluster=self.cluster)

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
    db = self._get_db(snippet, cluster=self.cluster)

    handle = self._get_handle(snippet)
    db.cancel_operation(handle)
    return {'status': 0}


  @query_error_handler
  def get_log(self, notebook, snippet, startFrom=None, size=None):
    db = self._get_db(snippet, cluster=self.cluster)

    handle = self._get_handle(snippet)
    return db.get_log(handle, start_over=startFrom == 0)


  @query_error_handler
  def close_statement(self, notebook, snippet):
    if snippet['type'] == 'impala':
      from impala import conf as impala_conf

    if (snippet['type'] == 'hive' and beeswax_conf.CLOSE_QUERIES.get()) or (snippet['type'] == 'impala' and impala_conf.CLOSE_QUERIES.get()):
      db = self._get_db(snippet, cluster=self.cluster)

      try:
        handle = self._get_handle(snippet)
        db.close_operation(handle)
      except Exception, e:
        if 'no valid handle' in str(e):
          return {'status': -1}  # skipped
        else:
          raise e
      return {'status': 0}
    else:
      return {'status': -1}  # skipped


  def can_start_over(self, notebook, snippet):
    try:
      db = self._get_db(snippet, cluster=self.cluster)
      handle = self._get_handle(snippet)
      # Test handle to verify if still valid
      db.fetch(handle, start_over=True, rows=1)
      can_start_over = True
    except Exception as e:
      raise e
    return can_start_over


  @query_error_handler
  def progress(self, notebook, snippet, logs=''):
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
    elif snippet['type'] == 'impala' and has_query_browser:
      query_id = unpack_guid_base64(snippet['result']['handle']['guid'])
      progress = min(self.progress(notebook, snippet, logs), 99) if snippet['status'] != 'available' and snippet['status'] != 'success' else 100
      jobs = [{
        'name': query_id,
        'url': '/hue/jobbrowser#!id=%s' % query_id,
        'started': True,
        'finished': False,
        'percentJob': progress
      }]

    return jobs


  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None):
    db = self._get_db(snippet, cluster=self.cluster)
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

    return _autocomplete(db, database, table, column, nested, query=query, cluster=self.cluster)


  @query_error_handler
  def get_sample_data(self, snippet, database=None, table=None, column=None, async=False, operation=None):
    try:
      db = self._get_db(snippet, async, cluster=self.cluster)
      return _get_sample_data(db, database, table, column, async, operation=operation, cluster=self.cluster)
    except QueryServerException, ex:
      raise QueryError(ex.message)


  @query_error_handler
  def explain(self, notebook, snippet):
    db = self._get_db(snippet, cluster=self.cluster)
    response = self._get_current_statement(notebook, snippet)
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
    db = self._get_db(snippet, cluster=self.cluster)

    handle = self._get_handle(snippet)
    max_rows = DOWNLOAD_ROW_LIMIT.get()
    max_bytes = DOWNLOAD_BYTES_LIMIT.get()

    upload(target_file, handle, self.request.user, db, self.request.fs, max_rows=max_rows, max_bytes=max_bytes)

    return '/filebrowser/view=%s' % urllib.quote(urllib.quote(target_file.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)) # Quote twice, because of issue in the routing on client


  def export_data_as_table(self, notebook, snippet, destination, is_temporary=False, location=None):
    db = self._get_db(snippet, cluster=self.cluster)

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

    hql = 'CREATE %sTABLE `%s`.`%s` %sAS %s' % ('TEMPORARY ' if is_temporary else '', database, table, "LOCATION '%s' " % location if location else '', query.hql_query)
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
      'location': self.request.fs.netnormpath(destination),
      'hql': query.hql_query
    }
    success_url = '/filebrowser/view=%s' % urllib.quote(destination.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)

    return hql, success_url


  def statement_risk(self, notebook, snippet):
    response = self._get_current_statement(notebook, snippet)
    query = response['statement']

    api = OptimizerApi(self.user)

    return api.query_risk(query=query, source_platform=snippet['type'], db_name=snippet.get('database') or 'default')


  def statement_compatibility(self, notebook, snippet, source_platform, target_platform):
    response = self._get_current_statement(notebook, snippet)
    query = response['statement']

    api = OptimizerApi(self.user)

    return api.query_compatibility(source_platform, target_platform, query)


  def statement_similarity(self, notebook, snippet, source_platform):
    response = self._get_current_statement(notebook, snippet)
    query = response['statement']

    api = OptimizerApi(self.user)

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

    return hql_query(
      statement,
      query_type=QUERY_TYPES[0],
      settings=settings,
      file_resources=file_resources,
      functions=functions,
      database=database
    )


  def get_browse_query(self, snippet, database, table, partition_spec=None):
    db = self._get_db(snippet, cluster=self.cluster)
    table = db.get_table(database, table)
    if table.is_impala_only:
      snippet['type'] = 'impala'
      db = self._get_db(snippet, cluster=self.cluster)

    if partition_spec is not None:
      decoded_spec = urllib.unquote(partition_spec)
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
      LOG.warn('Handle already base 64 decoded')

    for key in handle.keys():
      if key not in ('log_context', 'secret', 'has_result_set', 'operation_type', 'modified_row_count', 'guid'):
        handle.pop(key)

    return HiveServerQueryHandle(**handle)


  def _get_db(self, snippet, async=False, cluster=None):
    if not async and snippet['type'] == 'hive':
      name = 'beeswax'
    elif snippet['type'] == 'hive':
      name = 'hive'
    elif snippet['type'] == 'impala':
      name = 'impala'
    elif self.interface == 'hms':
      name = 'hms'
    elif self.interface.startswith('hiveserver2-'):
      name = self.interface.replace('hiveserver2-', '')
    else:
      name = 'sparksql' # Backward compatibility until HUE-8758

    return dbms.get(self.user, query_server=get_query_server_config(name=name, cluster=cluster))


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
    application = _get_server_name(snippet.get('compute', {}))
    session = Session.objects.get_session(self.user, application=application)

    server_url = _get_impala_server_url(session)
    if query_id:
      LOG.debug("Attempting to get Impala query profile at server_url %s for query ID: %s" % (server_url, query_id))

      fragment = self._get_impala_query_profile(server_url, query_id=query_id)
      total_records_re = "Coordinator Fragment F\d\d.+?RowsReturned: \d+(?:.\d+[KMB])? \((?P<total_records>\d+)\).*?(Averaged Fragment F\d\d)"
      total_records_match = re.search(total_records_re, fragment, re.MULTILINE | re.DOTALL)

    if total_records_match:
      total_records = int(total_records_match.group('total_records'))
      query_plan = self._get_impala_profile_plan(query_id, fragment)
      if query_plan:
        LOG.info('Query plan for Impala query %s: %s' % (query_id, query_plan))
      else:
        LOG.info('Query plan for Impala query %s not found.' % query_id)

    return total_records, total_size, msg


  def _get_impala_query_id(self, snippet):
    guid = None
    if 'result' in snippet and 'handle' in snippet['result'] and 'guid' in snippet['result']['handle']:
      try:
        guid = unpack_guid_base64(snippet['result']['handle']['guid'])
      except Exception, e:
        LOG.warn('Failed to decode operation handle guid: %s' % e)
    else:
      LOG.warn('Snippet does not contain a valid result handle, cannot extract Impala query ID.')
    return guid


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


  def _get_impala_profile_plan(self, query_id, profile):
    query_plan_re = "Query \(id=%(query_id)s\):.+?Execution Profile %(query_id)s" % {'query_id': query_id}
    query_plan_match = re.search(query_plan_re, profile, re.MULTILINE | re.DOTALL)
    return query_plan_match.group() if query_plan_match else None


  def describe_column(self, notebook, snippet, database=None, table=None, column=None):
    db = self._get_db(snippet, self.cluster)
    return db.get_table_columns_stats(database, table, column)


  def describe_table(self, notebook, snippet, database=None, table=None):
    db = self._get_db(snippet, self.cluster)
    tb = db.get_table(database, table)
    return {
      'status': 0,
      'name': tb.name,
      'partition_keys': [{'name': part.name, 'type': part.type} for part in tb.partition_keys],
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
    db = self._get_db(snippet, self.cluster)
    return db.get_database(database)

  def get_log_is_full_log(self, notebook, snippet):
    return snippet['type'] != 'hive' and snippet['type'] != 'impala'
