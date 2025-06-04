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
import time
import logging
import textwrap
from urllib.parse import urlparse

import requests
from django.utils.translation import gettext as _
from trino.auth import BasicAuthentication
from trino.client import ClientSession, TrinoQuery, TrinoRequest
from trino.exceptions import TrinoConnectionError

from beeswax import conf, data_export
from desktop.auth.backend import rewrite_user
from desktop.conf import AUTH_PASSWORD as DEFAULT_AUTH_PASSWORD, AUTH_USERNAME as DEFAULT_AUTH_USERNAME
from desktop.lib import export_csvxls
from desktop.lib.conf import coerce_password_from_script
from desktop.lib.i18n import force_unicode
from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest.resource import Resource
from notebook.connectors.base import Api, ExecutionWrapper, QueryError, ResultWrapper

LOG = logging.getLogger()
SESSION_KEY = '%(username)s-%(interpreter_name)s'


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except RestException as e:
      try:
        message = force_unicode(json.loads(e.message)['errors'])
      except Exception as ex:
        message = ex.message
      message = force_unicode(message)
      raise QueryError(message)
    except Exception as e:
      message = force_unicode(str(e))
      raise QueryError(message)
  return decorator


class TrinoApi(Api):
  def __init__(self, user, interpreter=None):
    Api.__init__(self, user, interpreter=interpreter)
    self.options = interpreter['options']
    self.server_host, self.server_port, self.http_scheme = self.parse_api_url(self.options.get('url'))
    self.auth = None

    auth_username = self.options.get('auth_username', DEFAULT_AUTH_USERNAME.get())
    auth_password = self.options.get('auth_password', self.get_auth_password())

    if auth_username and auth_password:
      self.auth_username = auth_username
      self.auth_password = auth_password
      self.auth = BasicAuthentication(self.auth_username, self.auth_password)

    self.session_info = self.create_session()
    self.trino_session = ClientSession(self.user.username, properties=self.session_info['properties'])
    self.trino_request = TrinoRequest(
      host=self.server_host,
      port=self.server_port,
      client_session=self.trino_session,
      http_scheme=self.http_scheme,
      auth=self.auth
    )

  def get_auth_password(self):
    auth_password_script = self.options.get('auth_password_script')
    return (
        coerce_password_from_script(auth_password_script)
        if auth_password_script
        else DEFAULT_AUTH_PASSWORD.get()
    )

  def _format_identifier(self, identifier, is_db=False):
    # Remove any backticks
    identifier = identifier.replace('`', '')

    # Check if already formatted
    if not (identifier.startswith('"') and identifier.endswith('"')):
      # Check if it's a multi-part identifier (e.g., catalog.schema)
      if '.' in identifier and is_db:
        # Split and format each part separately
        identifier = '"{}"'.format('"."'.join(identifier.split('.')))
      else:
        # Format single-part identifier
        identifier = f'"{identifier}"'

    return identifier

  @query_error_handler
  def parse_api_url(self, api_url):
    parsed_url = urlparse(api_url)
    return parsed_url.hostname, parsed_url.port, parsed_url.scheme

  def _get_session_key(self):
    return SESSION_KEY % {
      'username': self.user.username if hasattr(self.user, 'username') else self.user,
      'interpreter_name': self.interpreter['name']
    }

  def _get_session_info_from_user(self):
    self.user = rewrite_user(self.user)
    session_key = self._get_session_key()

    if self.user.profile.data.get(session_key):
      return self.user.profile.data[session_key]

  def _set_session_info_to_user(self, session_info):
    self.user = rewrite_user(self.user)
    session_key = self._get_session_key()

    self.user.profile.update_data({session_key: session_info})
    self.user.profile.save()

  def _remove_session_info_from_user(self):
    self.user = rewrite_user(self.user)
    session_key = self._get_session_key()

    if self.user.profile.data.get(session_key):
      json_data = self.user.profile.data
      json_data.pop(session_key)
      self.user.profile.json_data = json.dumps(json_data)

    self.user.profile.save()

  @query_error_handler
  def create_session(self, lang=None, properties=None):
    properties = properties or self._get_session_info_from_user()

    new_session_info = {
        'type': lang,
        'id': None,
        'properties': properties if not None else []
    }

    return new_session_info

  @query_error_handler
  def execute(self, notebook, snippet):
    database = snippet['database']
    database = self._format_identifier(database, is_db=True)
    query_client = TrinoQuery(self.trino_request, 'USE ' + database)
    query_client.execute()

    current_statement = self._get_current_statement(notebook, snippet)
    statement = current_statement['statement']
    query_client = TrinoQuery(self.trino_request, statement)
    response = self.trino_request.post(query_client.query)
    status = self.trino_request.process(response)

    response = {
      'row_count': 0,
      'rows_remaining': 0,
      'next_uri': status.next_uri,
      'sync': None,
      'has_result_set': status.next_uri is not None,
      'guid': status.id,
      'result': {
        'has_more': status.id is not None,
        'data': status.rows,
        'meta': [{
            'name': col['name'],
            'type': col['type'],
            'comment': ''
          }
          for col in status.columns
        ]
        if status.columns else [],
        'type': 'table'
      }
    }
    response.update(current_statement)

    return response

  @query_error_handler
  def check_status(self, notebook, snippet):
    response = {}
    status = 'expired'
    next_uri = snippet['result']['handle']['next_uri']

    if next_uri is None:
      status = 'available'
    else:
      _response = self.trino_request.get(next_uri)
      _status = self.trino_request.process(_response)
      if _status.stats['state'] == 'QUEUED':
        status = 'waiting'
      elif _status.stats['state'] == 'RUNNING':
        status = 'available'  # need to verify
      else:
        status = 'available'

    response['status'] = status
    response['next_uri'] = _status.next_uri if status != 'available' else next_uri
    return response

  @query_error_handler
  def fetch_result(self, notebook, snippet, rows, start_over):
    data = []
    columns = []
    next_uri = snippet['result']['handle']['next_uri']
    row_count = snippet['result']['handle'].get('row_count', 0)
    rows_remaining = snippet['result']['handle'].get('rows_remaining', 0)
    status = False

    if row_count == 0:
      data = snippet['result']['handle']['result']['data']

    while next_uri:
      try:
        response = self.trino_request.get(next_uri)
      except requests.exceptions.RequestException as e:
        raise TrinoConnectionError("failed to fetch: {}".format(e))

      status = self.trino_request.process(response)
      data += status.rows
      columns = status.columns

      if rows_remaining:
        data = data[-rows_remaining:]  # Trim the data to only include the remaining rows
        rows_remaining = 0  # Reset rows_remaining since we've handled the trimming

      if len(data) > 100:
        rows_remaining = len(data) - 100  # no of rows remaining to fetch in the present uri
        break
      rows_remaining = 0

      next_uri = status.next_uri

    data = data[:100]

    properties = self.trino_session.properties
    self._set_session_info_to_user(properties)

    return {
      'row_count': len(data) + row_count,
      'rows_remaining': rows_remaining,
      'next_uri': next_uri,
      'has_more': bool(status.next_uri) if status else False,
      'data': data or [],
      'meta': [{
        'name': column['name'],
        'type': column['type'],
        'comment': ''
        } for column in columns] if status else [],
      'type': 'table'
    }

  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None, operation=None):
    response = {}

    if database is None:
      response['databases'] = self._show_databases()
    elif table is None:
      response['tables_meta'] = self._show_tables(database)
    elif column is None:
      columns = self._get_columns(database, table)
      response['columns'] = [col['name'] for col in columns]
      response['extended_columns'] = [{
        'comment': col.get('comment'),
        'name': col.get('name'),
        'type': col['type']
      }
        for col in columns
      ]

    return response

  @query_error_handler
  def get_sample_data(self, snippet, database=None, table=None, column=None, nested=False, is_async=False, operation=None):
    statement = self._get_select_query(database, table, column, operation)
    query_client = TrinoQuery(self.trino_request, statement)
    query_client.execute()

    response = {
      'status': 0,
      'rows': [],
      'full_headers': []
    }
    response['rows'] = query_client.result.rows
    response['full_headers'] = query_client.columns

    return response

  def _get_select_query(self, database, table, column=None, operation=None, limit=100):
    if operation == 'hello':
      statement = "SELECT 'Hello World!'"
    else:
      database = self._format_identifier(database, is_db=True)
      table = self._format_identifier(table)
      column = '%(column)s' % {'column': self._format_identifier(column)} if column else '*'
      statement = textwrap.dedent('''\
          SELECT %(column)s
          FROM %(database)s.%(table)s
          LIMIT %(limit)s
          ''' % {
        'database': database,
        'table': table,
        'column': column,
        'limit': limit,
      })

    return statement

  def close_statement(self, notebook, snippet):
    try:
      if snippet['result']['handle']['next_uri']:
        self.trino_request.delete(snippet['result']['handle']['next_uri'])
      else:
        return {'status': -1}  # missing operation ids
    except Exception as e:
      if 'does not exist in current session:' in str(e):
        return {'status': -1}  # skipped
      else:
        raise e

    return {'status': 0}

  def close_session(self, session):
    self._remove_session_info_from_user()

  def _show_databases(self):
    catalogs = self._show_catalogs()
    databases = []

    for catalog in catalogs:
      try:
        query_client = TrinoQuery(self.trino_request, 'SHOW SCHEMAS FROM ' + catalog)
        response = query_client.execute()
        databases += [f'{catalog}.{item}' for sublist in response.rows for item in sublist]
      except Exception as e:
        # Log the exception and continue with the next catalog
        LOG.error(f"Failed to fetch schemas from catalog {catalog}: {str(e)}")
        continue

    return databases

  @query_error_handler
  def _show_catalogs(self):
    query_client = TrinoQuery(self.trino_request, 'SHOW CATALOGS')
    response = query_client.execute()
    res = response.rows
    catalogs = [item for sublist in res for item in sublist]

    return catalogs

  @query_error_handler
  def _show_tables(self, database):
    database = self._format_identifier(database, is_db=True)
    query_client = TrinoQuery(self.trino_request, 'USE ' + database)
    query_client.execute()
    query_client = TrinoQuery(self.trino_request, 'SHOW TABLES')
    response = query_client.execute()
    tables = response.rows
    return [{
      'name': table[0],
      'type': 'table',
      'comment': '',
    }
      for table in tables
    ]

  @query_error_handler
  def _get_columns(self, database, table):
    database = self._format_identifier(database, is_db=True)
    query_client = TrinoQuery(self.trino_request, 'USE ' + database)
    query_client.execute()
    table = self._format_identifier(table)
    query_client = TrinoQuery(self.trino_request, 'DESCRIBE ' + table)
    response = query_client.execute()
    columns = response.rows

    return [{
      'name': col[0],
      'type': col[1],
      'comment': '',
    }
      for col in columns
    ]

  def get_log(self, notebook, snippet, startFrom=None, size=None):
    guid = snippet['result']['handle']['guid'] if snippet.get('result') and snippet['result'].get('handle') and \
      snippet['result']['handle'].get('guid') else None
    return f"query_id: {guid}"

  @query_error_handler
  def explain(self, notebook, snippet):
    statement = snippet['statement'].rstrip(';')
    explanation = ''

    if statement:
      try:
        database = snippet['database']
        database = self._format_identifier(database, is_db=True)
        TrinoQuery(self.trino_request, 'USE ' + database).execute()
        result = TrinoQuery(self.trino_request, 'EXPLAIN ' + statement).execute()
        explanation = result.rows
      except Exception as e:
        explanation = str(e)

    return {
      'status': 0,
      'explanation': explanation,
      'statement': statement
    }

  def download(self, notebook, snippet, file_format='csv'):
    result_wrapper = TrinoExecutionWrapper(self, notebook, snippet)

    max_rows = conf.DOWNLOAD_ROW_LIMIT.get()
    max_bytes = conf.DOWNLOAD_BYTES_LIMIT.get()

    content_generator = data_export.DataAdapter(result_wrapper, max_rows=max_rows, max_bytes=max_bytes)
    return export_csvxls.create_generator(content_generator, file_format)


class TrinoExecutionWrapper(ExecutionWrapper):

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
      self.snippet['result']['handle']['row_count'] = result['row_count']
      self.snippet['result']['handle']['rows_remaining'] = result['rows_remaining']
      self.snippet['result']['handle']['next_uri'] = result['next_uri']

    return ResultWrapper(result.get('meta'), result.get('data'), result.get('has_more'))

  def _until_available(self):
    if self.snippet['result']['handle'].get('sync', False):
      return  # Request is already completed

    count = 0
    sleep_seconds = 1
    check_status_count = 0
    get_log_is_full_log = self.api.get_log_is_full_log(self.notebook, self.snippet)

    while True:
      response = self.api.check_status(self.notebook, self.snippet)
      old_uri = self.snippet['result']['handle']['next_uri']
      self.snippet['result']['handle']['next_uri'] = response['next_uri']
      if self.callback and hasattr(self.callback, 'on_status'):
        self.callback.on_status(response['status'])
      if self.callback and hasattr(self.callback, 'on_log'):
        log = self.api.get_log(self.notebook, self.snippet, startFrom=count)
        if get_log_is_full_log:
          log = log[count:]

        self.callback.on_log(log)
        count += len(log)

      if response['status'] not in ['waiting', 'running', 'submitted']:
        self.snippet['result']['handle']['next_uri'] = old_uri
        break
      check_status_count += 1
      if check_status_count > 5:
        sleep_seconds = 5
      elif check_status_count > 10:
        sleep_seconds = 10
      time.sleep(sleep_seconds)
