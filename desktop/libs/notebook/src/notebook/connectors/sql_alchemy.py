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

Parameters are not saved at any time in the Hue database. The are currently not even cached in the Hue process. The clients serves these parameters
each time a query is sent.

Note: the SQL Alchemy engine could leverage create_session() and cache the engine object (without its credentials) like in the jdbc.py interpreter.
Note: this is currently supporting concurrent querying by one users as engine is a new object each time. Could use a thread global SQL Alchemy
session at some point.
Note: using the task server would not leverage any caching.
'''
from future import standard_library
standard_library.install_aliases()

from builtins import next
from builtins import object
import datetime
import json
import logging
import uuid
import re
import sys
import textwrap

from string import Template

from django.utils.translation import ugettext as _
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError

from desktop.lib import export_csvxls
from desktop.lib.i18n import force_unicode
from beeswax import data_export
from librdbms.server import dbms

from notebook.connectors.base import Api, QueryError, QueryExpired, _get_snippet_name, AuthenticationRequired
from notebook.models import escape_rows

if sys.version_info[0] > 2:
  from urllib.parse import quote_plus as urllib_quote_plus
  from past.builtins import long
else:
  from urllib import quote_plus as urllib_quote_plus


CONNECTION_CACHE = {}
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
    self.user = user
    self.options = interpreter['options']
    self.backticks = '"' if re.match('^(postgresql://|awsathena|elasticsearch)', self.options.get('url', '')) else '`'

  def _create_engine(self):
    if '${' in self.options['url']: # URL parameters substitution
      vars = {'user': self.user.username}
      for _prop in self.options['session']['properties']:
        if _prop['name'] == 'user':
          vars['USER'] = _prop['value']
        if _prop['name'] == 'password':
          vars['PASSWORD'] = _prop['value']
      raw_url = Template(self.options['url'])
      url = raw_url.safe_substitute(**vars)
    else:
      url = self.options['url']

    if url.startswith('awsathena+rest://'):
      url = url.replace(url[17:37], urllib_quote_plus(url[17:37]))
      url = url.replace(url[38:50], urllib_quote_plus(url[38:50]))
      s3_staging_dir = url.rsplit('s3_staging_dir=', 1)[1]
      url = url.replace(s3_staging_dir, urllib_quote_plus(s3_staging_dir))

    options = self.options.copy()
    options.pop('session', None)
    options.pop('url', None)

    return create_engine(url, **options)

  @query_error_handler
  def execute(self, notebook, snippet):
    guid = uuid.uuid4().hex

    engine = self._create_engine()
    connection = engine.connect()
    result = connection.execution_options(stream_results=True).execute(snippet['statement'])

    cache = {
      'connection': connection,
      'result': result,
      'meta': [{
          'name': col[0] if (type(col) is tuple or type(col) is dict) else col.name if hasattr(col, 'name') else col,
          'type': 'STRING_TYPE',
          'comment': ''
        } for col in result.cursor.description] if result.cursor else []
    }
    CONNECTION_CACHE[guid] = cache

    return {
      'sync': False,
      'has_result_set': True,
      'modified_row_count': 0,
      'guid': guid,
      'result': {
        'has_more': True,
        'data': [],
        'meta': cache['meta'],
        'type': 'table'
      }
    }

  @query_error_handler
  def check_status(self, notebook, snippet):
    guid = snippet['result']['handle']['guid']
    connection = CONNECTION_CACHE.get(guid)

    if connection:
      return {'status': 'available'}
    else:
      return {'status': 'canceled'}

  @query_error_handler
  def fetch_result(self, notebook, snippet, rows, start_over):
    guid = snippet['result']['handle']['guid']
    cache = CONNECTION_CACHE.get(guid)

    if cache:
      data = cache['result'].fetchmany(rows)
      meta = cache['meta']
      self._assign_types(data, meta)
    else:
      data = []
      meta = []

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
    result = {'status': -1}
    try:
      guid = snippet['result']['handle']['guid']
      connection = CONNECTION_CACHE.get(guid)
      if connection:
        connection['connection'].close()
        del CONNECTION_CACHE[guid]
      result['status'] = 0
    finally:
      return result


  @query_error_handler
  def get_log(self, notebook, snippet, startFrom=None, size=None):
    return ''


  @query_error_handler
  def close_statement(self, notebook, snippet):
    result = {'status': -1}

    try:
      guid = snippet['result']['handle']['guid']
      connection = CONNECTION_CACHE.get('guid')
      if connection:
        connection['connection'].close()
        del CONNECTION_CACHE[guid]
      result['status'] = 0
    finally:
      return result


  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None):
    engine = self._create_engine()
    inspector = inspect(engine)

    assist = Assist(inspector, engine, backticks=self.backticks)
    response = {'status': -1}

    if database is None:
      response['databases'] = [db or 'NULL' for db in assist.get_databases()]
    elif table is None:
      tables_meta = []
      database = self._fix_phoenix_empty_database(database)
      for t in assist.get_tables(database):
        t = self._fix_bigquery_db_prefixes(t)
        tables_meta.append({'name': t, 'type': 'Table', 'comment': ''})
      response['tables_meta'] = tables_meta
    elif column is None:
      database = self._fix_phoenix_empty_database(database)
      columns = assist.get_columns(database, table)
      response['columns'] = [col['name'] for col in columns]
      response['extended_columns'] = [{
          'autoincrement': col.get('autoincrement'),
          'comment': col.get('comment'),
          'default': col.get('default'),
          'name': col.get('name'),
          'nullable': col.get('nullable'),
          'type': str(col.get('type'))
        } for col in columns
      ]
    else:
      columns = assist.get_columns(database, table)
      response['name'] = next((col['name'] for col in columns if column == col['name']), '')
      response['type'] = next((str(col['type']) for col in columns if column == col['name']), '')

    response['status'] = 0
    return response


  @query_error_handler
  def get_sample_data(self, snippet, database=None, table=None, column=None, is_async=False, operation=None):
    engine = self._create_engine()
    inspector = inspect(engine)

    assist = Assist(inspector, engine, backticks=self.backticks)
    response = {'status': -1, 'result': {}}

    metadata, sample_data = assist.get_sample_data(database, table, column)
    has_result_set = sample_data is not None

    if sample_data:
      response['status'] = 0
      response['rows'] = escape_rows(sample_data)

    if table:
      columns = assist.get_columns(database, table)
      response['full_headers'] = [{
        'name': col.get('name'),
        'type': str(col.get('type')),
        'comment': ''
      } for col in columns]
    elif metadata:
      response['full_headers'] = [{
        'name': col[0] if type(col) is dict or type(col) is tuple else col,
        'type': 'STRING_TYPE',
        'comment': ''
      } for col in metadata]

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


  def _fix_phoenix_empty_database(self, database):
    return None if self.options['url'].startswith('phoenix://') and database == 'NULL' else database


  def _fix_bigquery_db_prefixes(self, table_or_column):
    if self.options['url'].startswith('bigquery://'):
      table_or_column = table_or_column.rsplit('.', 1)[1]
    return table_or_column


class Assist(object):

  def __init__(self, db, engine, backticks):
    self.db = db
    self.engine = engine
    self.backticks = backticks

  def get_databases(self):
    return self.db.get_schema_names()

  def get_tables(self, database, table_names=[]):
    return self.db.get_table_names(database)

  def get_columns(self, database, table):
    return self.db.get_columns(table, database)

  def get_sample_data(self, database, table, column=None):
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
    connection = self.engine.connect()
    try:
      result = connection.execution_options(stream_results=True).execute(statement)
      return result.cursor.description, result.fetchall()
    finally:
      connection.close()
