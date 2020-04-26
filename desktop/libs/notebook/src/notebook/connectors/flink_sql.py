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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.lib.i18n import force_unicode
from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest.resource import Resource

from notebook.connectors.base import Api, QueryError


LOG = logging.getLogger(__name__)
_JSON_CONTENT_TYPE = 'application/json'
_API_VERSION = 'v1'
SESSIONS = {}
SESSION_KEY = '%(username)s-%(connector_name)s'


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
    self.db = FlinkSqlClient(user=user, api_url=self.options['api_url'])


  @query_error_handler
  def create_session(self, lang=None, properties=None):
    # session = Session.objects.get_session(self.user, application=application)
    # reuse_session = session is not None
    # if not reuse_session:
    #   db = dbms.get(self.user, query_server=get_query_server_config(name=lang, connector=self.interpreter))
    #   session = db.open_session(self.user)


    # "session_name": "test",  # optional
    # "planner": "blink",  # required, "old"/"blink"
    # "execution_type": "streaming",  # required, "batch"/"streaming"
    # "properties": {  # optional
    #     "key": "value"
    # }

    session = self.db.create_session()

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
      SESSIONS[session_key] = self.create_session()

    try:
      self.db.session_heartbeat(session_id=SESSIONS[session_key]['id'])
    except Exception as e:
      if 'Session: %(id)s does not exist' % SESSIONS[session_key] in str(e):
        LOG.info('Session: %(id)s does not exist, opening a new one' % SESSIONS[session_key])
        SESSIONS[session_key] = self.create_session()
      else:
        raise e

    return SESSIONS[session_key]

  @query_error_handler
  def execute(self, notebook, snippet):
    session = self._get_session()
    session_id = session['id']

    resp = self.db.execute_statement(session_id=session_id, statement=snippet['statement'])

    if resp['statement_types'][0] == 'SELECT':
      job_id = resp['results'][0]['data'][0][0]

      i = 0
      import time
      status = 'running'
      while i < 10 and status == 'running':
        status = self.db.fetch_status(session_id, job_id)['status']
        i += 1
        time.sleep(1)

      resp = self.db.fetch_results(session_id, job_id)
      data, description = resp['results'][0]['data'], resp['results'][0]['columns']

      i = 1
      while i < 10 and resp.get('next_result_uri'):
        resp = self.db.fetch_results(session_id, job_id, i)
        i += 1
        if resp:
          data.extend(resp['results'][0]['data'])
    else:
      data, description = resp['results'][0]['data'], resp['results'][0]['columns']


    has_result_set = data is not None

    return {
      'sync': True,
      'has_result_set': has_result_set,
      'result': {
        'has_more': False,
        'data': data,
        'meta': [{
            'name': col['name'],
            'type': col['type'],
            'comment': ''
          }
          for col in description
        ] if has_result_set else [],
        'type': 'table'
      }
    }


  @query_error_handler
  def check_status(self, notebook, snippet):
    # resp = self.db.fetch_status(session_id, job_id)
    return {'status': 'expired'}

    if resp.get('status') == 'RUNNING':
      status = 'running'
    elif resp.get('status') == 'FINISHED':
      status = 'available'
    else:
      status = 'expired'

    return {'status': status}


  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None):
    response = {}

    try:
      if database is None:
        response['databases'] = self.show_databases()
      elif table is None:
        response['tables_meta'] = self.show_tables(database)
      elif column is None:
        columns = self.db.get_columns(table)
        response['columns'] = [col['name'] for col in columns]
        response['extended_columns'] = [{
            'comment': col.get('comment'),
            'name': col.get('name'),
            'type': str(col['schema'].get('type'))
          } for col in columns
        ]
      else:
        response = {}

    except Exception as e:
      LOG.warn('Autocomplete data fetching error: %s' % e)
      response['code'] = 500
      response['error'] = str(e)

    return response


  def show_databases(self):
    session = self._get_session()
    session_id = session['id']

    resp = self.db.execute_statement(session_id=session_id, statement='SHOW DATABASES')

    return [db[0] for db in resp['results'][0]['data']]


  def show_tables(self, database):
    session = self._get_session()
    session_id = session['id']

    resp = self.db.execute_statement(session_id=session_id, statement='USE %(database)s' % {'database': database})
    resp = self.db.execute_statement(session_id=session_id, statement='SHOW TABLES')

    return [table[0] for table in resp['results'][0]['data']]


  def close_session(self, session):
    session = self._get_session()
    self.db.close_session(session['id'])


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
