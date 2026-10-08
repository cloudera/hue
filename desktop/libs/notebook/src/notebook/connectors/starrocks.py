import sys

from future import standard_library
from sqlalchemy.engine.result import ResultProxy

standard_library.install_aliases()
from builtins import next, object
import logging
from django.core.cache import caches
from sqlalchemy.engine.base import Connection, Engine
from past.builtins import long
import datetime
from sqlalchemy import create_engine, inspect, Table, MetaData, text
from sqlalchemy.exc import UnsupportedCompilationError, CompileError, ProgrammingError, NoSuchTableError, \
  OperationalError

from notebook.connectors.base import Api, AuthenticationRequired, QueryError, QueryExpired
from desktop.lib.i18n import force_unicode, smart_str

LOG = logging.getLogger()

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
      elif '(MySQLdb.ProgrammingError)' in message:
        raise QueryError(message).with_traceback(sys.exc_info()[2])
      elif 'Access denied' in message:
        raise AuthenticationRequired('您没有权限执行查询操作，请通过飞书进行工单申请: https://applink.feishu.cn/T8S49ukvF4wc')
      else:
        LOG.exception('Query Error')
        raise QueryError(message)
  return decorator

class StarrocksApi(Api):
  def __init__(self, user, interpreter):
    super().__init__(user, interpreter=interpreter)
    self.options = interpreter['options']
    self.url = self.options['url']
    self.credentials = None
    self.starrocks_engine:Engine = None
    self.load_credentials_from_cache()

  def load_credentials_from_cache(self):
    default_cache = caches['redis']
    password = default_cache.get(self.user.username)
    if password:
      self.credentials = {'user': self.user.username, 'password': password}

  def save_credentials_to_cache(self):
    if self.credentials and 'password' in self.credentials:
      default_cache =  caches['redis']
      default_cache.set(self.user.username, self.credentials['password'], timeout=604800)

  def _construct_url(self, user, password):
    parts = self.url.split('://')
    host_info = parts[1].split('?')
    host_part = host_info[0]
    params_part = '?' + host_info[1] if len(host_info) > 1 else ''
    return f'{parts[0]}://{user}:{password}@{host_part}{params_part}'

  def _get_engine_connection(self, user, password):
    new_url = self._construct_url(user, password)
    try:
      self.starrocks_engine = create_engine(new_url)
      return self.starrocks_engine.connect()
    except Exception as e:
      raise AuthenticationRequired(e)

  def create_session(self, lang=None, properties=None):
    properties = {p['name']: p['value'] for p in properties} if properties else {}
    if 'password' in properties:
      user = properties.get('user') or self.options.get('user')
      password = properties.pop('password')
      try:
        self._get_engine_connection(user, password)
        inspector = inspect(self.starrocks_engine)
        assist = Assist(inspector, self.starrocks_engine)
        LOG.error(assist.get_databases())
        self.credentials = {'user': user, 'password': password}
        self.save_credentials_to_cache()
      except Exception as e:
        raise AuthenticationRequired(e)
    if not self.credentials:
      raise AuthenticationRequired("Credentials are required to create a session.").with_traceback(sys.exc_info()[2])
    return {'properties': self.credentials}

  def execute(self, notebook, snippet):
    if not self.credentials:
      raise AuthenticationRequired("Credentials are required to execute a query.")
    current_statement = self._get_current_statement(notebook, snippet)
    response = {
      'sync': False,
      'has_result_set': True,
      'modified_row_count': 0,
      'result': {
        'has_more': True,
        'data': [],
        'meta': [],
        'type': 'table'
      }
    }
    response.update(current_statement)
    return response

  @query_error_handler
  def fetch_result(self, notebook, snippet, rows, start_over):
    current_statement = self._get_current_statement(notebook, snippet)
    statement = current_statement['statement']
    user = self.credentials['user']
    password = self.credentials['password']
    connection: Connection = self._get_engine_connection(user, password)
    result: ResultProxy = connection.execution_options(stream_results=True).execute(text(statement))
    try:
      data = result.fetchmany(rows)
      meta = [
        {
          'name': col[0] if isinstance(col, (tuple, dict)) else col.name if hasattr(col, 'name') else col,
          'type': '',
          'comment': ''
        }
        for col in result.cursor.description
      ] if result.cursor else []
      self._assign_types(data, meta)

      return {
        'has_more': data and len(data) >= rows or False,
        'data': data if data else [],
        'meta': meta if meta else [],
        'type': 'table',
        'sqltype': 'starrocks'
      }
    except Exception as e:
      message = force_unicode(smart_str(e))
      if message in "This result object does not return rows. It has been closed automatically.":
        response = {
          'sync': True,
          'has_result_set': True,
          'result': {
            'has_more': False,
            'data': [],
            'meta': [],
            'type': 'table'
          }
        }
        return response
      else:
        raise QueryError(e).with_traceback(sys.exc_info()[2])
    finally:
      if connection:
        connection.close()
      if self.starrocks_engine:
        self.starrocks_engine.dispose()

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
  def close_statement(self, notebook, snippet):
    return {'status': -1}

  @query_error_handler
  def fetch_result_metadata(self):
    pass

  @query_error_handler
  def cancel(self, notebook, snippet):
    return {'status': 0}

  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None, operation=None):
    try:
      user = self.credentials['user']
      password = self.credentials['password']
      self._get_engine_connection(user, password)
      inspector = inspect(self.starrocks_engine)

      assist = Assist(inspector, self.starrocks_engine)
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
    except Exception as e:
      raise AuthenticationRequired(e)
    finally:
      if self.starrocks_engine:
        self.starrocks_engine.dispose()

  @query_error_handler
  def check_status(self, notebook, snippet):
    return {'status': 'available'}

  @query_error_handler
  def explain(self, notebook, snippet):
    connection = self.starrocks_engine.connect()
    statement = snippet['statement']
    explanation = ''
    try:
      result = connection.execute('EXPLAIN ' + statement)
      explanation = "\n".join("{}: {},".format(k, v) for row in result for k, v in row.items())
    except ProgrammingError:
      pass
    except Exception as e:
      LOG.debug('')
      raise e
    return {
      'status': 0,
      'explanation': explanation,
      'statement': statement
    }

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

  def __init__(self, db, engine, api=None):
    self.db = db
    self.engine = engine
    self.api = api

  def get_databases(self):
    return self.db.get_schema_names()

  def get_table_names(self, database, table_names=[]):
    return self.db.get_table_names(database)

  def get_view_names(self, database, view_names=[]):
    try:
      return self.db.get_view_names(database)
    except NotImplementedError:
      return []

  def get_tables(self, database, table_names=[]):
    return self.get_table_names(database) + self.get_view_names(database)

  def get_columns(self, database, table):
    try:
      return self.db.get_columns(table, database)
    except NoSuchTableError:
      return []

  def get_sample_data(self, database, table, column=None, operation=None):
    statement = "SELECT 'Hello World!'"
    connection = self.api._create_connection(self.engine)
    try:
      result = connection.execute(statement)
      return result.cursor.description, result.fetchall()
    finally:
      connection.close()

  def get_keys(self, database, table):
    meta = MetaData()
    try:
      metaTable = Table(table, meta, schema=database, autoload=True, autoload_with=self.engine)
    except ProgrammingError:
      LOG.debug("Table %s.%s could not be found and this is probably expected" % (database, table))
      return {}

    return {
      'foreign_keys': [{
          'name': fk.parent.name,
          'to': fk.target_fullname
        }
        for fk in metaTable.foreign_keys
      ],
      'primary_keys': [{'name': pk.name} for pk in metaTable.primary_key.columns]
    }