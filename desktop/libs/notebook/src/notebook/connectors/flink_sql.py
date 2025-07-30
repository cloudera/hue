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
import posixpath
import re
import time

from desktop.auth.backend import rewrite_user
from desktop.lib.i18n import force_unicode
from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest.resource import Resource
from notebook.connectors.base import Api, QueryError

LOG = logging.getLogger()

_JSON_CONTENT_TYPE = 'application/json'
_API_VERSION = 'v3'
SESSION_KEY = '%(username)s-%(connector_name)s'
OPERATION_TOKEN = '%(username)s-%(connector_name)s' + '-operation-token'
DEFAULT_CATALOG_PARAM = "default_catalog"
DEFAULT_DATABASE_PARAM = "default_database"


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except RestException as e:
      try:
        message = force_unicode(json.loads(e.message)['errors'])
      except Exception:
        message = e.message
      message = force_unicode(message)
      raise QueryError(parse_error(message))
    except Exception as e:
      message = force_unicode(str(e))
      raise QueryError(message)

  return decorator


def parse_error(error):
  lines = re.split(r'\\n', error)
  caused_by = [line for line in lines if 'Caused by:' in line]

  if len(caused_by) == 0:
    return error
  elif len(caused_by) >= 1:
    return caused_by[-1]


class FlinkSqlApi(Api):

  def __init__(self, user, interpreter=None):
    Api.__init__(self, user, interpreter=interpreter)

    self.options = interpreter['options']
    api_url = self.options['url']
    self.default_catalog = self.options.get(DEFAULT_CATALOG_PARAM)
    self.default_database = self.options.get(DEFAULT_DATABASE_PARAM)

    self.db = FlinkSqlClient(user=user, api_url=api_url)

  @query_error_handler
  def create_session(self, lang=None, properties=None):
    LOG.info("Creating session for %s.", lang)
    session = self._get_session()

    response = {
      'type': lang,
      'id': session['id']
    }
    return response

  def _get_session_key(self):
    return SESSION_KEY % {
      'username': self.user.username if hasattr(self.user, 'username') else self.user,
      'connector_name': self.interpreter['name']
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
    operation_token_key = self._get_operation_token_key()

    if self.user.profile.data.get(session_key):
      json_data = self.user.profile.data
      json_data.pop(session_key)
      json_data.pop(operation_token_key)
      self.user.profile.json_data = json.dumps(json_data)

    self.user.profile.save()

  def _get_operation_token_key(self):
    return OPERATION_TOKEN % {
      'username': self.user.username if hasattr(self.user, 'username') else self.user,
      'connector_name': self.interpreter['name']
    }

  def _get_operation_token_info_from_user(self, operation_handle):
    self.user = rewrite_user(self.user)
    operation_token_key = self._get_operation_token_key()

    if self.user.profile.data.get(operation_token_key):
      return self.user.profile.data[operation_token_key][operation_handle]

  def _set_operation_token_info_to_user(self, operation_handle, token):
    self.user = rewrite_user(self.user)
    operation_token_key = self._get_operation_token_key()

    json_data = self.user.profile.data

    if self.user.profile.data.get(operation_token_key) is None:
      json_data[operation_token_key] = {}

    json_data[operation_token_key][operation_handle] = token
    self.user.profile.update_data(json_data)

    self.user.profile.save()

  def _remove_operation_token_info_from_user(self, operation_handle):
    self.user = rewrite_user(self.user)
    operation_token_key = self._get_operation_token_key()

    if self.user.profile.data.get(operation_token_key):
      json_data = self.user.profile.data
      json_data[operation_token_key].pop(operation_handle)
      self.user.profile.json_data = json.dumps(json_data)

    self.user.profile.save()

  def _get_session(self):
    session = self._get_session_info_from_user()

    if not session:
      session = self._create_session()
    try:
      self.db.session_heartbeat(session_handle=session['id'])
    except Exception as e:
      if "Session '%(sessionHandle)s' does not exist" % session in str(e):
        LOG.warning('Session %(sessionHandle)s does not exist, opening a new one' % session)
        session = self._create_session()
      else:
        raise e

    self._set_session_info_to_user(session)

    return session

  def _create_session(self):
    session = self.db.create_session()
    session['id'] = session['sessionHandle']
    session['flink_version'] = self.db.info().get('version')

    if self.default_database:
      self._use_database(session, self.default_catalog, self.default_database)
    elif self.default_catalog:
      self._use_catalog(session, self.default_catalog)
    return session

  @query_error_handler
  def execute(self, notebook, snippet):
    session = self._get_session()
    session_handle = session['id']

    statement = snippet['statement'].strip().rstrip(';')

    # TODO: Operations such as add, alter, create, drop, use, load, unload can be executed using simple path via
    # /sessions/:session_handle/configure-session
    operation_handle = self.db.execute_statement(session_handle=session_handle, statement=statement)
    self._set_operation_token_info_to_user(operation_handle['operationHandle'], 0)

    return {
      'has_result_set': True,
      'guid': operation_handle['operationHandle'],
    }

  def _is_sync_statement(self, statement):
    return bool(re.match(r'^(add|alter|create|drop|load|unload|use)\b', statement, re.IGNORECASE))

  @query_error_handler
  def check_status(self, notebook, snippet):
    response = {}
    session = self._get_session()

    status = 'expired'

    if snippet.get('result'):
      statement_id = snippet['result']['handle']['guid']
      if session:
        if not statement_id:  # Sync result
          status = 'available'
        else:
          try:
            resp = self.db.fetch_status(session['id'], statement_id)
            if resp.get('status') == 'RUNNING':
              status = 'running'
            elif resp.get('status') == 'FINISHED':
              status = 'available'
            elif resp.get('status') == 'CANCELED':
              status = 'expired'
            elif resp.get('status') == 'CLOSED':
              status = 'closed'
            elif resp.get('status') == 'ERROR':
              status = 'error'
              self._remove_operation_token_info_from_user(statement_id)
              result_resp = self.db.fetch_results(session['id'], statement_id, 0)
              raise QueryError(parse_error(result_resp['errors'][-1]))

          except Exception as e:
            if 'Can not find the submitted operation in the OperationManager with the %s' % statement_id in str(e):
              LOG.warning('Operation Handle: %s does not exist' % statement_id)
            else:
              raise e

    response['status'] = status
    return response

  @query_error_handler
  def fetch_result(self, notebook, snippet, rows, start_over):
    session = self._get_session()
    statement_id = snippet['result']['handle']['guid']

    token = self._get_operation_token_info_from_user(statement_id)

    # Is race condition between cancel and fetch possible?
    resp = self.db.fetch_results(session['id'], operation_handle=statement_id, token=token)

    if resp['resultType'] == 'EOS':
      next_result = None
    else:
      next_result = resp.get('nextResultUri') if resp else None

    if next_result:
      # nextResultUri format:
      #   /sessions/:session_handle/operations/:operation_handle/result/:token?rowFormat=JSON
      # Step 1: Drop URL query part ("?rowFormat=JSON")
      url_path = next_result.rsplit('?', 1)[0]
      # Step 2: Extract "token" from URL path
      n = int(url_path.rsplit('/', 1)[-1])
      self._set_operation_token_info_to_user(statement_id, n)

    data = [db['fields'] for db in resp['results']['data'] if resp and resp['results'] and resp['results']['data']]

    if not bool(next_result):
      # This will not be required if close_statement one will start working
      self._remove_operation_token_info_from_user(statement_id)

    return {
      'has_more': bool(next_result),
      'data': data,  # No escaping...
      'meta': [{
        'name': column['name'],
        'type': column['logicalType']['type'],
        'comment': column['comment']
      }
        for column in resp['results']['columns'] if resp
      ],
      'type': 'table'
    }

  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None, operation=None):
    response = {}

    if operation == 'functions':
      response['functions'] = self._show_functions(database)
    elif operation == 'function':
      # When function signature is requested the following call is executed:
      # autocomplete(db=<function_name>, table=None, col=None, nested=None, op=function)
      response['function'] = self._show_function(database)
    elif database is None:
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
  def get_sample_data(self, snippet, database=None, table=None, column=None, nested=None, is_async=False,
                      operation=None):
    if operation == 'hello':
      snippet['statement'] = "SELECT 'Hello World!'"
    else:
      snippet['statement'] = "SELECT * FROM `%(database)s`.`%(table)s` LIMIT 25;" % {
        'database': database,
        'table': table
      }

    session = self._get_session()
    session_id = session['id']
    operation_handle = self.db.execute_statement(session_handle=session_id, statement=snippet['statement'])
    statement_id = operation_handle['operationHandle']

    resp = self.db.fetch_results(session_id, statement_id, 0)
    while resp['resultType'] == 'NOT_READY':
      time.sleep(0.1)
      resp = self.db.fetch_results(session_id, statement_id, 0)

    sample = [db['fields'] for db in resp['results']['data'] if resp and resp['results'] and resp['results']['data']]
    n = 0

    while resp['resultType'] != 'EOS':
      resp = self.db.fetch_results(session_id, statement_id, n)
      if resp['resultType'] == 'PAYLOAD':
        n = n + 1
      sample += [db['fields'] for db in resp['results']['data'] if resp and resp['results'] and resp['results']['data']]
      time.sleep(1)
      if len(sample) > 0:
        break

    return {
      'status': 0,
      'result': {
        'handle': {
          'guid': statement_id
        }
      },
      'rows': sample,
      'full_headers': [
        {
          'name': column['name'],
          'type': column['logicalType']['type'],
          'comment': column['comment']
        }
        for column in resp['results']['columns'] if resp
      ]
    }

  @query_error_handler
  def cancel(self, notebook, snippet):
    session = self._get_session()
    operation_handle = snippet['result']['handle']['guid']

    try:
      self.db.close_statement(session['id'], operation_handle)
    except Exception as e:
      message = force_unicode(str(e)).lower()
      LOG.debug(message)

    return {'status': 0}

  @query_error_handler
  def close_statement(self, notebook, snippet):
    session = self._get_session()
    statement_id = snippet['result']['handle']['guid']

    try:
      if session and statement_id:
        self.db.close_statement(session_handle=session['id'], operation_handle=statement_id)
        # self._remove_operation_token_info_from_user(statement_id)     ## Needs to check why Hue db not getting updated
      else:
        return {'status': -1}  # missing operation ids
    except Exception as e:
      if 'does not exist in current session:' in str(e):
        return {'status': -1}  # skipped
      else:
        raise e

    return {'status': 0}

  def close_session(self, session):
    if self._get_session_info_from_user():
      self._remove_session_info_from_user()
      self.db.close_session(session['id'])

    return {
      'status': 0,
      'session': session['id']
    }

  def _check_status_and_fetch_result(self, session_handle, operation_handle):
    resp = self.db.fetch_results(session_handle, operation_handle, 0)

    while resp['resultType'] == 'NOT_READY':
      resp = self.db.fetch_results(session_handle, operation_handle, 0)

    data = [i['fields'] for i in resp['results']['data'] if resp and resp['results'] and resp['results']['data']]
    return data

  def _show_databases(self):
    session = self._get_session()
    session_handle = session['id']

    operation_handle = self.db.execute_statement(session_handle=session_handle, statement='SHOW DATABASES')
    db_list = self._check_status_and_fetch_result(session_handle, operation_handle['operationHandle'])

    return [db[0] for db in db_list]

  def _show_tables(self, database):
    session = self._get_session()
    session_handle = session['id']

    operation_handle = self.db.execute_statement(session_handle=session_handle,
                                                 statement='SHOW TABLES IN `%(database)s`' % {'database': database})
    table_list = self._check_status_and_fetch_result(session_handle, operation_handle['operationHandle'])

    return [{
      'name': table[0],
      'type': 'Table',
      'comment': '',
    }
      for table in table_list
    ]

  def _get_columns(self, database, table):
    session = self._get_session()
    session_handle = session['id']

    operation_handle = self.db.execute_statement(
      session_handle=session_handle,
      statement='DESCRIBE `%(database)s`.`%(table)s`' % {'database': database, 'table': table})
    column_list = self._check_status_and_fetch_result(session_handle, operation_handle['operationHandle'])

    return [{
      'name': col[0],
      'type': col[1],  # Types to unify
      'comment': '',
    }
      for col in column_list
    ]

  def _show_functions(self, database):
    session = self._get_session()
    statement = 'SHOW FUNCTIONS IN `%(database)s`' % {'database': database} if database else 'SHOW FUNCTIONS'
    operation_handle = self.db.execute_statement(session['id'], statement)
    function_list = self._check_status_and_fetch_result(session['id'], operation_handle['operationHandle'])
    return [{'name': function[0]} for function in function_list]

  def _show_function(self, function_name):
    session = self._get_session()
    if session.get('flink_version') and session['flink_version'].startswith('2.'):
      # Describe function is available as of Flink 2.0.
      operation_handle = self.db.execute_statement(
        session_handle=session['id'],
        statement='DESCRIBE FUNCTION EXTENDED %(function_name)s' % {'function_name': function_name})
      properties = dict(self._check_status_and_fetch_result(session['id'], operation_handle['operationHandle']))

      return {
        'name': function_name,
        'signature': properties.get('signature'),
      }
    else:
      return {'name': function_name}

  def _use_catalog(self, session, catalog):
    self.db.configure_session(session['id'], "USE CATALOG `%s`" % catalog)

  def _use_database(self, session, catalog, database):
    if catalog:
      self.db.configure_session(session['id'], "USE `%(catalog)s`.`%(database)s`" % {'catalog': catalog,
                                                                                     'database': database})
    else:
      self.db.configure_session(session['id'], "USE `%(database)s`" % {'database': database})


class FlinkSqlClient:
  """
  Implements https://nightlies.apache.org/flink/flink-docs-master/docs/dev/table/sql-gateway/rest/.
  Could be a pip module or sqlalchemy dialect in the future.
  """

  def __init__(self, user, api_url):
    self.user = user
    self._url = posixpath.join(api_url.rstrip('/') + '/' + _API_VERSION + '/')
    self._client = HttpClient(self._url, logger=LOG)
    self._root = Resource(self._client)

  def __str__(self):
    return "FlinkClient at %s" % (self._url,)

  def info(self):
    return self._root.get('info')

  def create_session(self, **properties):
    data = {
      "sessionName": self.user.username + "-flink-sql",
    }
    data.update(properties)
    return self._root.post('sessions', data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)

  def close_session(self, session_handle):
    return self._root.delete('sessions/%(session_handle)s' % {'session_handle': session_handle})

  def get_session_conf(self, session_handle):
    return self._root.get('sessions/%(session_handle)s' % {'session_handle': session_handle})

  def session_heartbeat(self, session_handle):
    return self._root.post('sessions/%(session_handle)s/heartbeat' % {'session_handle': session_handle})

  def configure_session(self, session_handle, statement):
    data = {
      "statement": statement,
    }
    json_data = json.dumps(data)

    path = 'sessions/%(session_handle)s/configure-session' % {'session_handle': session_handle}
    self._root.post(path, data=json_data, contenttype=_JSON_CONTENT_TYPE)

  def execute_statement(self, session_handle, statement):
    data = {
      "statement": statement,
    }
    json_data = json.dumps(data)

    path = 'sessions/%(session_handle)s/statements' % {'session_handle': session_handle}
    return self._root.post(path, data=json_data, contenttype=_JSON_CONTENT_TYPE)

  def fetch_status(self, session_handle, operation_handle):
    return self._root.get(
      'sessions/%(session_handle)s/operations/%(operation_handle)s/status' % {
        'session_handle': session_handle,
        'operation_handle': operation_handle,
      }
    )

  def fetch_results(self, session_handle, operation_handle, token=0):
    return self._root.get(
      'sessions/%(session_handle)s/operations/%(operation_handle)s/result/%(token)s' % {
        'session_handle': session_handle,
        'operation_handle': operation_handle,
        'token': token
      })

  def close_statement(self, session_handle, operation_handle):
    return self._root.delete(
      'sessions/%(session_handle)s/operations/%(operation_handle)s/close' % {
        'session_handle': session_handle,
        'operation_handle': operation_handle,
      }
    )

  def cancel(self, session_handle, operation_handle):
    return self._root.post(
      'sessions/%(session_handle)s/operations/%(operation_handle)s/cancel' % {
        'session_handle': session_handle,
        'operation_handle': operation_handle
      }
    )
