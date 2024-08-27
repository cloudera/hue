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
import sys
from urllib.parse import urlparse

from beeswax import conf, data_export
from desktop.lib import export_csvxls
from desktop.lib.i18n import force_unicode, smart_str
from django.utils.translation import gettext as _
from notebook.connectors.base import (Api, AuthenticationRequired,
                                      ExecutionWrapper, QueryError,
                                      ResultWrapper)
from trino.auth import BasicAuthentication
from trino.dbapi import connect

LOG = logging.getLogger()

API_CACHE = {}


def query_and_fetch(db, statement, n=None):
  data = None
  try:
    db.connect()
    curs = db.cursor()

    try:
      if curs.execute(statement):
        data = curs.fetchall()
      meta = curs.description
      return data, meta
    finally:
      curs.close()
  except Exception as e:
    message = force_unicode(smart_str(e))
    if 'Access denied' in message:
      raise AuthenticationRequired()
    raise
  finally:
    db.close()


def query_and_fetch_support_use(db, statement, use_statement, n=None):
    data = None
    try:
        db.connect()
        curs = db.cursor()
        try:
            curs.execute(use_statement)
            print(statement)
            queries = split_sql_statements(statement)
            for query in queries:
                curs.execute(query)
                if query == queries[-1]:
                    data = curs.fetchmany(n)
            meta = curs.description
            return data, meta
        finally:
            curs.close()
    except Exception as e:
        message = force_unicode(smart_str(e))
        if 'Access denied' in message:
            raise AuthenticationRequired()
        raise
    finally:
        db.close()


def split_sql_statements(statement):
    """
    Splits SQL statements by semicolons, ignoring semicolons inside quotes.
    """
    statements = []
    current_statement = []
    in_quotes = False
    quote_char = ''

    for char in statement:
        if char in ('"', "'"):
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif in_quotes and char == quote_char:
                in_quotes = False
                quote_char = ''

        if char == ';' and not in_quotes:
            # End of a statement
            statements.append(''.join(current_statement).strip())
            current_statement = []
        else:
            current_statement.append(char)

    # Append the last statement if exists
    if current_statement:
        statements.append(''.join(current_statement).strip())

    return statements


# Cache one JDBC connection by user for not saving user credentials
def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except AuthenticationRequired as e:
      raise e
    except Exception as e:
      message = force_unicode(smart_str(e))
      if 'error occurred while trying to connect to the Java server' in message:
        raise QueryError(_('%s: is the DB Proxy server running?') % message).with_traceback(sys.exc_info()[2])
      elif 'Access denied' in message:
        raise AuthenticationRequired('').with_traceback(sys.exc_info()[2])
      else:
        raise QueryError(message).with_traceback(sys.exc_info()[2])

  return decorator


class PythonApiTrino(Api):

  def __init__(self, user, interpreter=None):
    global API_CACHE
    Api.__init__(self, user, interpreter=interpreter)
    self.db = None
    self.options = interpreter['options']
    self.session_user = user.username
    self.server_host, self.server_port, self.http_scheme = self.parse_api_url(self.options['url'])

    if self.cache_key in API_CACHE:
      self.db = API_CACHE[self.cache_key]
    elif 'auth_password' in self.options:
      username = self.options.get('auth_user') or user.username
      self.db = API_CACHE[self.cache_key] = TrinPythonClientWrapper(
        self.server_host,
        username,
        self.options['auth_password'],
        self.server_port,
        self.http_scheme,
        user.username)

  def create_session(self, lang=None, properties=None):
    global API_CACHE
    props = super(PythonApiTrino, self).create_session(lang, properties)

    properties = dict([(p['name'], p['value']) for p in properties]) if properties is not None else {}
    props['properties'] = {}  # We don't store passwords

    if self.db is None or not self.db.test_connection(throw_exception='auth_password' not in properties):
      if 'auth_password' in properties:
        user = self.options.get('auth_user')
        props['properties'] = {'auth_user': user}
        self.db = API_CACHE[self.cache_key] = TrinPythonClientWrapper(
          self.options['url'],
          user,
          properties.pop('auth_password'),
          self.server_port,
          self.http_scheme,
          self.session_user)

        self.db.test_connection(throw_exception=True)

    if self.db is None:
      raise AuthenticationRequired()

    return props

  @property
  def cache_key(self):
    return '%s-%s' % (self.interpreter['name'], self.session_user)

  def download(self, notebook, snippet, file_format='csv'):
    result_wrapper = TrinoPythonExecutionWrapper(self, notebook, snippet)

    max_rows = conf.DOWNLOAD_ROW_LIMIT.get()
    max_bytes = conf.DOWNLOAD_BYTES_LIMIT.get()

    content_generator = data_export.DataAdapter(result_wrapper, max_rows=max_rows, max_bytes=max_bytes)
    return export_csvxls.create_generator(content_generator, file_format)

  @query_error_handler
  def parse_api_url(self, api_url):
    parsed_url = urlparse(api_url)
    return parsed_url.hostname, parsed_url.port, parsed_url.scheme

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
        } for col in columns]
    return response

  @query_error_handler
  def _show_catalogs(self):
    data = query_and_fetch(self.db, "SHOW CATALOGS")
    catalogs = data[0]
    catalog_names = [item[0] for item in catalogs]
    return catalog_names

  @query_error_handler
  def _show_databases(self):
    catalogs = self._show_catalogs()
    databases = []
    for catalog in catalogs:
        schemas_data = query_and_fetch(self.db, "SHOW SCHEMAS FROM %s" % (catalog))
        schemas_index = schemas_data[0]
        schemas = [row[0] for row in schemas_index]
        databases += [f'{catalog}.{schema}' for schema in schemas]
    return databases

  @query_error_handler
  def _show_tables(self, database):
    catalog, schema = database.split('.')
    data, description = query_and_fetch(self.db, "SHOW TABLES FROM %s.%s" % (catalog, schema))
    tables_name = [row[0] for row in data]
    return [{
        'name': table,
        'type': 'table',
        'comment': '',
    } for table in tables_name]

  @query_error_handler
  def _get_columns(self, database, table):
    catalog, schema = database.split('.')
    columns = query_and_fetch(self.db, "DESCRIBE %s.%s.%s" % (catalog, schema, table))
    columns_name = columns[0]
    return [{"comment": col[2] and col[2].strip(), "type": col[1], "name": col[0] and col[0].strip()} for col in columns_name]

  @query_error_handler
  def executeForDownload(self, notebook, snippet):
    if self.db is None:
      raise AuthenticationRequired()

    data, description = query_and_fetch_support_use(
      self.db, snippet['statement'],
      'USE ' + snippet['database'],
      conf.DOWNLOAD_ROW_LIMIT.get())

    has_result_set = data is not None

    return {
      'sync': True,
      'has_result_set': has_result_set,
      'result': {
        'has_more': False,
        'data': data if has_result_set else [],
        'meta': [{
          'name': col[0],
          'type': col[1],
          'comment': ''
        } for col in description] if has_result_set else [],
        'type': 'table'
      }
    }

  @query_error_handler
  def execute(self, notebook, snippet):
    if self.db is None:
      raise AuthenticationRequired()

    data, description = query_and_fetch_support_use(
      self.db,
      snippet['statement'],
      'USE ' + snippet['database'],
      1000)

    has_result_set = data is not None
    re = {
      'sync': True,
      'has_result_set': has_result_set,
      'result': {
        'has_more': False,
        'data': data if has_result_set else [],
        'meta': [{
          'name': col[0],
          'type': col[1],
          'comment': ''
        } for col in description] if has_result_set else [],
        'type': 'table'
      }
    }
    return re

  @query_error_handler
  def explain(self, notebook, snippet):
    statement = snippet['statement'].rstrip(';')
    explanation = ''

    if statement:
      try:
        result = query_and_fetch_support_use(self.db, 'EXPLAIN ' + statement, 'USE ' + snippet['database'])
        explanation = result
      except Exception as e:
        explanation = str(e)

    return {
      'status': 0,
      'explanation': explanation,
      'statement': statement
    }


class TrinoPythonExecutionWrapper(ExecutionWrapper):

    def __init__(self, trino_api, notebook, snippet):
        self.api = trino_api
        self.notebook = notebook
        self.snippet = snippet

    def fetch(self, handle, start_over=None, rows=None):
        handle = self.api.executeForDownload(self.notebook, self.snippet)
        result = handle.get('result')
        self.should_close = True
        return ResultWrapper(result.get('meta'), result.get('data'), result.get('has_more'))


class TrinPythonClientWrapper(object):

    def __init__(self, url, username, password, port, http_scheme, impersonation_user=None):
      if 'trino' not in sys.modules:
        raise Exception('Required trino module is not imported.')

      self.url = url
      self.username = username
      self.password = password
      self.port = port
      self.conn = None
      self.session_user = None
      self.http_scheme = http_scheme
      if impersonation_user:
        self.session_user = impersonation_user

    def test_connection(self, throw_exception=True):
      try:
        self.connect()
        return True
      except Exception as e:
        message = force_unicode(smart_str(e))
        if throw_exception:
          if 'Access denied' in message:
            raise AuthenticationRequired()
          raise
        else:
          return False
      finally:
        self.close()

    def connect(self):
      if self.conn is None:
        self.conn = connect(
          host=self.url,
          port=self.port,
          user=self.session_user,
          auth=BasicAuthentication(self.username, self.password),
          http_scheme=self.http_scheme)

    def cursor(self):
      return self.conn.cursor()

    def close(self):
      if self.conn is not None:
        self.conn.close()
        self.conn = None
