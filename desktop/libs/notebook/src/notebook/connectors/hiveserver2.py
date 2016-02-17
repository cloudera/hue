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
import re

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode

from notebook.connectors.base import Api, QueryError, QueryExpired


LOG = logging.getLogger(__name__)


try:
  from beeswax import data_export
  from beeswax.api import _autocomplete
  from beeswax.design import hql_query, strip_trailing_semicolon, split_statements
  from beeswax import conf as beeswax_conf
  from beeswax.models import QUERY_TYPES, HiveServerQueryHandle, HiveServerQueryHistory, QueryHistory, Session
  from beeswax.server import dbms
  from beeswax.server.dbms import get_query_server_config, QueryServerException
  from beeswax.views import _parse_out_hadoop_jobs
except ImportError, e:
  LOG.exception('Hive and HiveServer2 interfaces are not enabled')


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except QueryServerException, e:
      message = force_unicode(str(e))
      if 'Invalid query handle' in message or 'Invalid OperationHandle' in message:
        raise QueryExpired(e)
      else:
        raise QueryError(message)
  return decorator


class HS2Api(Api):

  @query_error_handler
  def create_session(self, lang='hive', properties=None):
    application = 'beeswax' if lang == 'hive' else lang

    session = Session.objects.get_session(self.user, application=application)

    if session is None:
      session = dbms.get(self.user, query_server=get_query_server_config(name=lang)).open_session(self.user)

    return {
        'type': lang,
        'id': session.id,
        'properties': session.get_formatted_properties()
    }


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

    response = self._get_current_statement(db, snippet)

    query = self._prepare_hql_query(snippet, response.pop('statement'))

    try:
      db.use(query.database)
      handle = db.client.query(query)
    except QueryServerException, ex:
      raise QueryError(ex.message)

    # All good
    server_id, server_guid = handle.get()
    response.update({
      'secret': server_id,
      'guid': server_guid,
      'operation_type': handle.operation_type,
      'has_result_set': handle.has_result_set,
      'modified_row_count': handle.modified_row_count,
      'log_context': handle.log_context,
    })

    return response

  def _get_statements(self, hql_query):
    hql_query = strip_trailing_semicolon(hql_query)
    return [strip_trailing_semicolon(statement.strip()) for statement in split_statements(hql_query)]


  @query_error_handler
  def check_status(self, notebook, snippet):
    response = {}
    db = self._get_db(snippet)

    handle = self._get_handle(snippet)
    operation = db.get_operation_status(handle)
    status = HiveServerQueryHistory.STATE_MAP[operation.operationState]

    if status.index in (QueryHistory.STATE.failed.index, QueryHistory.STATE.expired.index):
      raise QueryError(operation.errorMessage)

    response['status'] = 'running' if status.index in (QueryHistory.STATE.running.index, QueryHistory.STATE.submitted.index) else 'available'

    return response


  @query_error_handler
  def fetch_result(self, notebook, snippet, rows, start_over):
    db = self._get_db(snippet)

    handle = self._get_handle(snippet)
    results = db.fetch(handle, start_over=start_over, rows=rows)

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
  def fetch_result_metadata(self):
    pass


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
      return data_export.download(handle, format, db)
    except Exception, e:
      LOG.exception('error downloading notebook')

      if not hasattr(e, 'message') or not e.message:
        message = e
      else:
        message = e.message
      raise PopupException(message, detail='')


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
      match = re.search('(\d+)% Complete', logs, re.MULTILINE)
      return int(match.group(1)) if match else 0
    else:
      return 50


  @query_error_handler
  def get_jobs(self, notebook, snippet, logs):
    job_ids = _parse_out_hadoop_jobs(logs)

    jobs = [{
      'name': job_id,
      'url': reverse('jobbrowser.views.single_job', kwargs={'job': job_id})
    } for job_id in job_ids]

    return jobs


  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None):
    db = self._get_db(snippet)
    return _autocomplete(db, database, table, column, nested)


  def _get_current_statement(self, db, snippet):
    # Multiquery, if not first statement or arrived to the last query
    statement_id = snippet['result']['handle'].get('statement_id', 0)
    statements_count = snippet['result']['handle'].get('statements_count', 1)

    if snippet['result']['handle'].get('has_more_statements'):
      try:
        handle = self._get_handle(snippet)
        db.close_operation(handle)  # Close all the time past multi queries
      except:
        LOG.warn('Could not close previous multiquery query')
      statement_id += 1
    else:
      statement_id = 0

    statements = self._get_statements(snippet['statement'])
    if statements_count != len(statements):
      statement_id = 0
    statement = statements[statement_id]

    return {
      'statement_id': statement_id,
      'statement': statement,
      'has_more_statements': statement_id < len(statements) - 1,
      'statements_count': len(statements)
    }


  def _prepare_hql_query(self, snippet, statement):
    settings = snippet['properties'].get('settings', None)
    file_resources = snippet['properties'].get('files', None)
    functions = snippet['properties'].get('functions', None)
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
    return db.get_select_star_query(database, table)


  def _get_handle(self, snippet):
    snippet['result']['handle']['secret'], snippet['result']['handle']['guid'] = HiveServerQueryHandle.get_decoded(snippet['result']['handle']['secret'], snippet['result']['handle']['guid'])
    snippet['result']['handle'].pop('statement_id')
    snippet['result']['handle'].pop('has_more_statements')
    snippet['result']['handle'].pop('statements_count')
    return HiveServerQueryHandle(**snippet['result']['handle'])


  def _get_db(self, snippet):
    if snippet['type'] == 'hive':
      name = 'beeswax'
    elif snippet['type'] == 'impala':
      name = 'impala'
    else:
      name = 'spark-sql'

    return dbms.get(self.user, query_server=get_query_server_config(name=name))
