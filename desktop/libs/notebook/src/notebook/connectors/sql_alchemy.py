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

'''
SQL Alchemy offers native connections to databases via dialects https://docs.sqlalchemy.org/en/latest/dialects/.

When the dialect of a paricular datavase is installed on the Hue API server, any of its URL connection strings should work.

e.g.
mysql://root:root@localhost:3306/hue

To offer more self service capabilities, parts of the URL can be parameterized.

Supported parameters are:

* USER
* PASSWORD

e.g.
mysql://${USER}:${PASSWORD}@localhost:3306/hue

Parameters are not saved at any time in the Hue database. The are currently not even cached in the Hue process.
The clients serves these parameters each time a query is sent in case the previously created engine is not there.

Note: create_session() could create the engine object (without its credentials) like in the other interpreters.
Note: its currently has one engine per user. This should be changed to one engine per URL but then it makes it complicated to close
all the queries of a user. It could also have an engine per Editor session and an engine for the managed queries (where Hue guarantees
to properly close queries).

Engines and connections
-----------------------
SqlAlchemy documentation is pretty good: https://docs.sqlalchemy.org/en/13/core/connections.html

Each URL is mapped to one engine and should be created once per process.
Each query statement grabs a connection from the engine and will return it after its close().
Disposing the engine closes all its connections.
'''
from future import standard_library
standard_library.install_aliases()

from builtins import next, object
import datetime
import json
import logging
import uuid
import re
import sys
import textwrap

from string import Template

from django.core.cache import caches
from django.utils.translation import ugettext as _
from sqlalchemy import create_engine, inspect, Table, MetaData
from sqlalchemy.exc import OperationalError, UnsupportedCompilationError, CompileError

from desktop.lib import export_csvxls
from desktop.lib.i18n import force_unicode
from beeswax import data_export
from librdbms.server import dbms

from notebook.connectors.base import Api, QueryError, QueryExpired, _get_snippet_name, AuthenticationRequired
from notebook.models import escape_rows

if sys.version_info[0] > 2:
  from urllib.parse import quote_plus as urllib_quote_plus
  from past.builtins import long
  from io import StringIO
else:
  from urllib import quote_plus as urllib_quote_plus
  from cStringIO import StringIO


ENGINES = {}
CONNECTIONS = {}
ENGINE_KEY = '%(username)s-%(connector_name)s'
URL_PATTERN = '(?P<driver_name>.+?://)(?P<host>[^:/ ]+):(?P<port>[0-9]*).*'

LOG = logging.getLogger(__name__)


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except OperationalError as e:
      message = str(e)
      if '1045' in message: # 'Access denied' # MySQL
        raise AuthenticationRequired(message=message)
      else:
        raise e
    except AuthenticationRequired:
      raise
    except QueryExpired:
      raise
    except Exception as e:
      message = force_unicode(e)
      if 'Invalid query handle' in message or 'Invalid OperationHandle' in message:
        raise QueryExpired(e)
      else:
        LOG.exception('Query Error')
        raise QueryError(message)
  return decorator


class SqlAlchemyApi(Api):

  def __init__(self, user, interpreter):
    super(SqlAlchemyApi, self).__init__(user=user, interpreter=interpreter)
    self.options = interpreter['options']

    if interpreter.get('dialect_properties'):
      self.backticks = interpreter['dialect_properties']['sql_identifier_quote']
    else:
      self.backticks = '"' if re.match('^(postgresql://|awsathena|elasticsearch|phoenix)', self.options.get('url', '')) else '`'

  def _get_engine_key(self):
    return ENGINE_KEY % {
      'username': self.user.username,
      'connector_name': self.interpreter['name']
    }

  def _get_engine(self):
    engine_key = self._get_engine_key()

    if engine_key not in ENGINES:
      ENGINES[engine_key] = self._create_engine()

    return ENGINES[engine_key]

  def _create_engine(self):
    if '${' in self.options['url']:  # URL parameters substitution
      vars = {'USER': self.user.username}

      if '${PASSWORD}' in self.options['url']:
        auth_provided = False
        if 'session' in self.options:
          for _prop in self.options['session']['properties']:
            if _prop['name'] == 'user':
              vars['USER'] = _prop['value']
              auth_provided = True
            if _prop['name'] == 'password':
              vars['PASSWORD'] = _prop['value']
              auth_provided = True

        if not auth_provided:
          raise AuthenticationRequired(message='Missing username and/or password')

      raw_url = Template(self.options['url'])
      url = raw_url.safe_substitute(**vars)
    else:
      url = self.options['url']

    if url.startswith('awsathena+rest://'):
      url = url.replace(url[17:37], urllib_quote_plus(url[17:37]))
      url = url.replace(url[38:50], urllib_quote_plus(url[38:50]))
      s3_staging_dir = url.rsplit('s3_staging_dir=', 1)[1]
      url = url.replace(s3_staging_dir, urllib_quote_plus(s3_staging_dir))

    if self.options.get('has_impersonation'):
      m = re.search(URL_PATTERN, url)
      driver_name = m.group('driver_name')

      if not driver_name:
        raise QueryError('Driver name of %(url)s could not be found and impersonation is turned on' % {'url': url})

      url = url.replace(driver_name, '%(driver_name)s%(username)s@' % {
        'driver_name': driver_name,
        'username': self.user.username
      })

    if self.options.get('credentials_json'):
      self.options['credentials_info'] = json.loads(
          self.options.pop('credentials_json')
      )

    # Enables various SqlAlchemy args to be passed along for both Hive & Presto connectors
    # Refer to SqlAlchemy pyhive for more details
    if self.options.get('connect_args'):
      self.options['connect_args'] = json.loads(
          self.options.pop('connect_args')
      )

    options = self.options.copy()
    options.pop('session', None)
    options.pop('url', None)
    options.pop('has_ssh', None)
    options.pop('has_impersonation', None)
    options.pop('ssh_server_host', None)

    options['pool_pre_ping'] = not url.startswith('phoenix://')  # Should be moved to dialect when connectors always on

    return create_engine(url, **options)


  def _get_session(self, notebook, snippet):
    for session in notebook['sessions']:
      if session['type'] == snippet['type']:
        return session

    return None


  def _create_connection(self, engine):
    connection = None
    try:
      connection = engine.connect()
    except Exception as e:
      engine_key = self._get_engine_key()
      ENGINES.pop(engine_key, None)

      raise AuthenticationRequired(message='Could not establish connection to datasource: %s' % e)

    return connection


  @query_error_handler
  def execute(self, notebook, snippet):
    guid = uuid.uuid4().hex

    session = self._get_session(notebook, snippet)
    if session is not None:
      self.options['session'] = session

    engine = self._get_engine()
    connection = self._create_connection(engine)
    statement = snippet['statement']

    if self.interpreter['dialect_properties'].get('trim_statement_semicolon', True):
      statement = statement.strip().rstrip(';')

    if self.interpreter['dialect_properties'].get('has_use_statement') and snippet.get('database'):
      connection.execute(
        'USE %(sql_identifier_quote)s%(database)s%(sql_identifier_quote)s' % {
          'sql_identifier_quote': self.interpreter['dialect_properties']['sql_identifier_quote'],
          'database': snippet['database'],
        }
      )

    result = connection.execute(statement)

    cache = {
      'connection': connection,
      'result': result,
      'meta': [
        {
          'name': col[0] if (type(col) is tuple or type(col) is dict) else col.name if hasattr(col, 'name') else col,
          'type': 'STRING_TYPE',
          'comment': ''
        }
        for col in result.cursor.description
      ] if result.cursor else []
    }
    CONNECTIONS[guid] = cache

    return {
      'sync': False,
      'has_result_set': result.cursor != None,
      'modified_row_count': 0,
      'guid': guid,
      'result': {
        'has_more': result.cursor != None,
        'data': [],
        'meta': cache['meta'],
        'type': 'table'
      }
    }


  @query_error_handler
  def explain(self, notebook, snippet):
    session = self._get_session(notebook, snippet)
    if session is not None:
      self.options['session'] = session

    engine = self._get_engine()
    connection = self._create_connection(engine)
    statement = snippet['statement']

    explanation = ''

    if statement:
      if self.options['url'].startswith('bigquery://'):
        explanation = ''

    return {
      'status': 0,
      'explanation': explanation,
      'statement': statement
    }


  @query_error_handler
  def check_status(self, notebook, snippet):
    guid = snippet['result']['handle']['guid']
    connection = CONNECTIONS.get(guid)

    response = {'status': 'canceled'}

    if connection:
      cursor = connection['result'].cursor
      if self.options['url'].startswith('presto://') and cursor and cursor.poll():
        response['status'] = 'running'
      elif snippet['result']['handle']['has_result_set']:
        response['status'] = 'available'
      else:
        response['status'] = 'success'
    else:
      raise QueryExpired()

    return response


  @query_error_handler
  def progress(self, notebook, snippet, logs=''):
    progress = 50
    if self.options['url'].startswith('presto://'):
      guid = snippet['result']['handle']['guid']
      handle = CONNECTIONS.get(guid)
      stats = None
      progress = 100
      try:
        if handle and handle['result'].cursor:
          stats = handle['result'].cursor.poll()
      except AssertionError as e:
        LOG.warn('Query probably not running anymore: %s' % e)
      if stats:
        stats = stats.get('stats', {})
        progress = stats.get('completedSplits', 0) * 100 // stats.get('totalSplits', 1)
    return progress


  @query_error_handler
  def fetch_result(self, notebook, snippet, rows, start_over):
    guid = snippet['result']['handle']['guid']
    handle = CONNECTIONS.get(guid)

    if handle:
      data = handle['result'].fetchmany(rows)
      meta = handle['meta']
      self._assign_types(data, meta)
    else:
      raise QueryExpired()

    return {
      'has_more': data and len(data) >= rows or False,
      'data': data if data else [],
      'meta': meta if meta else [],
      'type': 'table'
    }


  def _assign_types(self, results, meta):
    result = results and results[0]
    if result:
      for index, col in enumerate(result):
        if isinstance(col, int):
          meta[index]['type'] = 'INT_TYPE'
        elif isinstance(col, float):
          meta[index]['type'] = 'FLOAT_TYPE'
        elif isinstance(col, long):
          meta[index]['type'] = 'BIGINT_TYPE'
        elif isinstance(col, bool):
          meta[index]['type'] = 'BOOLEAN_TYPE'
        elif isinstance(col, datetime.date):
          meta[index]['type'] = 'TIMESTAMP_TYPE'
        else:
          meta[index]['type'] = 'STRING_TYPE'


  @query_error_handler
  def fetch_result_metadata(self):
    pass


  @query_error_handler
  def cancel(self, notebook, snippet):
    return self.close_statement(notebook, snippet)


  @query_error_handler
  def get_log(self, notebook, snippet, startFrom=None, size=None):
    return ''


  @query_error_handler
  def close_statement(self, notebook, snippet):
    result = {'status': -1}

    try:
      guid = snippet['result']['handle']['guid']
      connection = CONNECTIONS.get(guid)
      if connection:
        connection['connection'].close()
        del CONNECTIONS[guid]
      result['status'] = 0
    finally:
      return result


  def close_session(self, session):
    engine = self._get_engine()
    engine.dispose()  # ENGINE_KEY currently includes the current user


  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None, operation=None):
    if snippet['type'] == 'phoenix':
      if database:
        database = database.upper()
      if table:
        table = table.upper()
    engine = self._get_engine()
    inspector = inspect(engine)

    assist = Assist(inspector, engine, backticks=self.backticks)
    response = {'status': -1}

    if operation == 'functions':
      response['functions'] = []
    elif operation == 'function':
      response['function'] = {}
    elif database is None:
      response['databases'] = [db or '' for db in assist.get_databases()]
    elif table is None:
      tables_meta = []
      for t in assist.get_table_names(database):
        t = self._fix_bigquery_db_prefixes(t)
        tables_meta.append({'name': t, 'type': 'Table', 'comment': ''})
      for t in assist.get_view_names(database):
        t = self._fix_bigquery_db_prefixes(t)
        tables_meta.append({'name': t, 'type': 'View', 'comment': ''})
      response['tables_meta'] = tables_meta
    elif column is None:
      columns = assist.get_columns(database, table)

      response['columns'] = [col['name'] for col in columns]
      response['extended_columns'] = [{
          'autoincrement': col.get('autoincrement'),
          'comment': col.get('comment'),
          'default': col.get('default'),
          'name': col.get('name'),
          'nullable': col.get('nullable'),
          'type': self._get_column_type_name(col),
        }
        for col in columns
      ]
      response.update(assist.get_keys(database, table))
    else:
      columns = assist.get_columns(database, table)
      response['name'] = next((col['name'] for col in columns if column == col['name']), '')
      response['type'] = next((str(col['type']) for col in columns if column == col['name']), '')

    response['status'] = 0
    return response


  @query_error_handler
  def get_sample_data(self, snippet, database=None, table=None, column=None, is_async=False, operation=None):
    engine = self._get_engine()
    inspector = inspect(engine)

    assist = Assist(inspector, engine, backticks=self.backticks, api=self)
    response = {'status': -1, 'result': {}}

    metadata, sample_data = assist.get_sample_data(database, table, column=column, operation=operation)

    response['status'] = 0
    response['rows'] = escape_rows(sample_data)

    if table and operation != 'hello':
      columns = assist.get_columns(database, table)
      response['full_headers'] = [{
          'name': col.get('name'),
          'type': self._get_column_type_name(col),
          'comment': ''
        } for col in columns
      ]
    elif metadata:
      response['full_headers'] = [{
        'name': col[0] if type(col) is dict or type(col) is tuple else col.name if hasattr(col, 'name') else col,
        'type': 'STRING_TYPE',
        'comment': ''
      } for col in metadata
    ]

    return response

  @query_error_handler
  def get_browse_query(self, snippet, database, table, partition_spec=None):
    return textwrap.dedent('''\
      SELECT *
      FROM %(backticks)s%(database)s%(backticks)s.%(backticks)s%(table)s%(backticks)s
      LIMIT 1000
      ''' % {
        'database': database,
        'table': table,
        'backticks': self.backticks
    })


  def _get_column_type_name(self, col):
    try:
      name = str(col.get('type'))
    except (UnsupportedCompilationError, CompileError):
      name = col.get('type').__visit_name__.lower()

    return name


  def _fix_bigquery_db_prefixes(self, table_or_column):
    if self.options['url'].startswith('bigquery://'):
      table_or_column = table_or_column.rsplit('.', 1)[-1]
    return table_or_column


class Assist(object):

  def __init__(self, db, engine, backticks, api=None):
    self.db = db
    self.engine = engine
    self.backticks = backticks
    self.api = api

  def get_databases(self):
    return self.db.get_schema_names()

  def get_table_names(self, database, table_names=[]):
    return self.db.get_table_names(database)

  def get_view_names(self, database, view_names=[]):
    return self.db.get_view_names(database)

  def get_tables(self, database, table_names=[]):
    return self.get_table_names(database) + self.get_view_names(database)

  def get_columns(self, database, table):
    return self.db.get_columns(table, database)

  def get_sample_data(self, database, table, column=None, operation=None):
    if operation == 'hello':
      statement = "SELECT 'Hello World!'"
    else:
      column = '%(backticks)s%(column)s%(backticks)s' % {'backticks': self.backticks, 'column': column} if column else '*'
      statement = textwrap.dedent('''\
        SELECT %(column)s
        FROM %(backticks)s%(database)s%(backticks)s.%(backticks)s%(table)s%(backticks)s
        LIMIT %(limit)s
        ''' % {
          'database': database,
          'table': table,
          'column': column,
          'limit': 100,
          'backticks': self.backticks
      })

    connection = self.api._create_connection(self.engine)
    try:
      result = connection.execute(statement)
      return result.cursor.description, result.fetchall()
    finally:
      connection.close()

  def get_keys(self, database, table):
    meta = MetaData()
    metaTable = Table(table, meta, schema=database, autoload=True, autoload_with=self.engine)

    return {
      'foreign_keys': [{
          'name': fk.parent.name,
          'to': fk.target_fullname
        }
        for fk in metaTable.foreign_keys
      ],
      'primary_keys': [{'name': pk.name} for pk in metaTable.primary_key.columns]
    }
