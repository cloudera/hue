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

from __future__ import absolute_import

import logging
import json
import posixpath
import sys

from desktop.lib.i18n import force_unicode
from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest.resource import Resource

from notebook.connectors.base import Api, QueryError

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger()
_JSON_CONTENT_TYPE = 'application/json'
_API_VERSION = 'v1'
SESSIONS = {}
SESSION_KEY = '%(username)s-%(connector_name)s'

n = 0


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except RestException as e:
      try:
        message = force_unicode(json.loads(e.message)['errors'])
      except:
        message = e.message
      message = force_unicode(message)
      raise QueryError(message)
    except Exception as e:
      message = force_unicode(str(e))
      raise QueryError(message)
  return decorator



class FlinkSqlApi(Api):

  def __init__(self, user, interpreter=None):
    Api.__init__(self, user, interpreter=interpreter)

    self.options = interpreter['options']
    api_url = self.options['url']

    self.db = FlinkSqlClient(user=user, api_url=api_url)


  @query_error_handler
  def create_session(self, lang=None, properties=None):
    session = self._get_session()

    response = {
      'type': lang,
      'id': session['session_id']
    }

    return response

  def _get_session(self):
    session_key = SESSION_KEY % {
      'username': self.user.username,
      'connector_name': self.interpreter['name']
    }

    if session_key not in SESSIONS:
      SESSIONS[session_key] = self.db.create_session()

    try:
      self.db.session_heartbeat(session_id=SESSIONS[session_key]['session_id'])
    except Exception as e:
      if 'Session: %(id)s does not exist' % SESSIONS[session_key] in str(e):
        LOG.warning('Session: %(id)s does not exist, opening a new one' % SESSIONS[session_key])
        SESSIONS[session_key] = self.db.create_session()
      else:
        raise e

    SESSIONS[session_key]['id'] = SESSIONS[session_key]['session_id']

    return SESSIONS[session_key]


  @query_error_handler
  def execute(self, notebook, snippet):
    global n
    n = 0
    session = self._get_session()
    session_id = session['id']
    job_id = None

    statement = snippet['statement'].strip().rstrip(';')

    resp = self.db.execute_statement(session_id=session_id, statement=statement)

    if resp['statement_types'][0] == 'SELECT':
      job_id = resp['results'][0]['data'][0][0]
      data, description = [], []
      # TODO: change_flags
    else:
      data, description = resp['results'][0]['data'], resp['results'][0]['columns']

    has_result_set = data is not None

    return {
      'sync': job_id is None,
      'has_result_set': has_result_set,
      'guid': job_id,
      'result': {
        'has_more': job_id is not None,
        'data': data if job_id is None else [],
        'meta': [{
            'name': col['name'],
            'type': col['type'],
            'comment': ''
          }
          for col in description
        ]
        if has_result_set else [],
        'type': 'table'
      }
    }


  @query_error_handler
  def check_status(self, notebook, snippet):
    global n
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
              status = 'streaming'
              response['result'] = self.fetch_result(notebook, snippet, n, False)
            elif resp.get('status') == 'FINISHED':
              status = 'available'
            elif resp.get('status') == 'FAILED':
              status = 'failed'
            elif resp.get('status') == 'CANCELED':
              status = 'expired'
          except Exception as e:
            if '%s does not exist in current session' % statement_id in str(e):
              LOG.warning('Job: %s does not exist' % statement_id)
            else:
              raise e

    response['status'] = status

    return response


  @query_error_handler
  def fetch_result(self, notebook, snippet, rows, start_over):
    global n
    session = self._get_session()
    statement_id = snippet['result']['handle']['guid']
    token = n #rows

    resp = self.db.fetch_results(session['id'], job_id=statement_id, token=token)

    next_result = resp.get('next_result_uri')
    if next_result:
      n = int(next_result.rsplit('/', 1)[-1])

    return {
        'has_more': bool(next_result),
        'data': resp and resp['results'][0]['data'] or [],  # No escaping...
        'meta': [{
            'name': column['name'],
            'type': column['type'],
            'comment': ''
          }
          for column in resp['results'][0]['columns'] if resp
        ],
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
  def get_sample_data(self, snippet, database=None, table=None, column=None, is_async=False, operation=None):
    if operation == 'hello':
      snippet['statement'] = "SELECT 'Hello World!'"

    notebook = {}
    sample = self.execute(notebook, snippet)

    response = {
      'status': 0,
      'result': {}
    }

    response['rows'] = sample['result']['data']
    response['full_headers'] = sample['result']['meta']

    return response


  def cancel(self, notebook, snippet):
    session = self._get_session()
    statement_id = snippet['result']['handle']['guid']

    try:
      if session and statement_id:
        self.db.close_statement(session_id=session['id'], job_id=statement_id)
      else:
        return {'status': -1} # missing operation ids
    except Exception as e:
      if 'does not exist in current session:' in str(e):
        return {'status': -1}  # skipped
      else:
        raise e

    return {'status': 0}


  def close_session(self, session):
    # Avoid closing session on page refresh or editor close for now
    pass
    # session = self._get_session()
    # self.db.close_session(session['id'])


  def _show_databases(self):
    session = self._get_session()
    session_id = session['id']

    resp = self.db.execute_statement(session_id=session_id, statement='SHOW DATABASES')

    return [db[0] for db in resp['results'][0]['data']]


  def _show_tables(self, database):
    session = self._get_session()
    session_id = session['id']

    resp = self.db.execute_statement(session_id=session_id, statement='USE %(database)s' % {'database': database})
    resp = self.db.execute_statement(session_id=session_id, statement='SHOW TABLES')

    return [table[0] for table in resp['results'][0]['data']]


  def _get_columns(self, database, table):
    session = self._get_session()
    session_id = session['id']

    resp = self.db.execute_statement(session_id=session_id, statement='USE %(database)s' % {'database': database})
    resp = self.db.execute_statement(session_id=session_id, statement='DESCRIBE %(table)s' % {'table': table})
    columns = resp['results'][0]['data']

    return [{
        'name': col[0],
        'type': col[1],  # Types to unify
        'comment': '',
      }
      for col in columns
    ]


class FlinkSqlClient():
  '''
  Implements https://github.com/ververica/flink-sql-gateway
  Could be a pip module or sqlalchemy dialect in the future.
  '''

  def __init__(self, user, api_url):
    self.user = user
    self._url = posixpath.join(api_url + '/' + _API_VERSION + '/')
    self._client = HttpClient(self._url, logger=LOG)
    self._root = Resource(self._client)

  def __str__(self):
    return "FlinkClient at %s" % (self._url,)

  def info(self):
    return self._root.get('info')

  def create_session(self, **properties):
    data = {
        "session_name": "test",  # optional
        "planner": "blink",  # required, "old"/"blink"
        "execution_type": "streaming",  # required, "batch"/"streaming"
        "properties": {  # optional
            "key": "value"
        }
    }
    data.update(properties)

    return self._root.post('sessions', data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)

  def session_heartbeat(self, session_id):
    return self._root.post('sessions/%(session_id)s/heartbeat' % {'session_id': session_id})

  def execute_statement(self, session_id, statement):
    data = {
        "statement": statement,  # required
        "execution_timeout": ""  # execution time limit in milliseconds, optional, but required for stream SELECT ?
    }

    return self._root.post(
        'sessions/%(session_id)s/statements' % {
        'session_id': session_id
      },
      data=json.dumps(data),
      contenttype=_JSON_CONTENT_TYPE
    )

  def fetch_status(self, session_id, job_id):
    return self._root.get(
      'sessions/%(session_id)s/jobs/%(job_id)s/status' % {
        'session_id': session_id,
        'job_id': job_id
      }
    )

  def fetch_results(self, session_id, job_id, token=0):
    return self._root.get(
      'sessions/%(session_id)s/jobs/%(job_id)s/result/%(token)s' % {
        'session_id': session_id,
        'job_id': job_id,
        'token': token
      }
    )

  def close_statement(self, session_id, job_id):
    return self._root.delete(
      'sessions/%(session_id)s/jobs/%(job_id)s' % {
        'session_id': session_id,
        'job_id': job_id,
      }
    )

  def close_session(self, session_id):
    return self._root.delete(
      'sessions/%(session_id)s' % {
        'session_id': session_id,
      }
    )
