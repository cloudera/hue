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
import threading
import time

from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _

from desktop.lib.django_util import format_preserving_redirect
from desktop.lib.parameterization import substitute_variables
from filebrowser.views import location_to_url

from beeswax import hive_site
from beeswax.conf import HIVE_SERVER_HOST, HIVE_SERVER_PORT, LIST_PARTITIONS_LIMIT, SERVER_CONN_TIMEOUT, \
  AUTH_USERNAME, AUTH_PASSWORD, APPLY_NATURAL_SORT_MAX, QUERY_PARTITIONS_LIMIT
from beeswax.common import apply_natural_sort
from beeswax.design import hql_query
from beeswax.hive_site import hiveserver2_use_ssl
from beeswax.models import QueryHistory, QUERY_TYPES

LOG = logging.getLogger(__name__)


DBMS_CACHE = {}
DBMS_CACHE_LOCK = threading.Lock()

def get(user, query_server=None):
  global DBMS_CACHE
  global DBMS_CACHE_LOCK

  if query_server is None:
    query_server = get_query_server_config()

  DBMS_CACHE_LOCK.acquire()
  try:
    DBMS_CACHE.setdefault(user.username, {})

    if query_server['server_name'] not in DBMS_CACHE[user.username]:
      # Avoid circular dependency
      from beeswax.server.hive_server2_lib import HiveServerClientCompatible

      if query_server['server_name'] == 'impala':
        from impala.dbms import ImpalaDbms
        from impala.server import ImpalaServerClient
        DBMS_CACHE[user.username][query_server['server_name']] = ImpalaDbms(HiveServerClientCompatible(ImpalaServerClient(query_server, user)), QueryHistory.SERVER_TYPE[1][0])
      else:
        from beeswax.server.hive_server2_lib import HiveServerClient
        DBMS_CACHE[user.username][query_server['server_name']] = HiveServer2Dbms(HiveServerClientCompatible(HiveServerClient(query_server, user)), QueryHistory.SERVER_TYPE[1][0])

    return DBMS_CACHE[user.username][query_server['server_name']]
  finally:
    DBMS_CACHE_LOCK.release()


def get_query_server_config(name='beeswax', server=None):
  if name == 'impala':
    from impala.dbms import get_query_server_config as impala_query_server_config
    query_server = impala_query_server_config()
  else:
    kerberos_principal = hive_site.get_hiveserver2_kerberos_principal(HIVE_SERVER_HOST.get())

    query_server = {
        'server_name': 'beeswax', # Aka HiveServer2 now
        'server_host': HIVE_SERVER_HOST.get(),
        'server_port': HIVE_SERVER_PORT.get(),
        'principal': kerberos_principal,
        'http_url': '%(protocol)s://%(host)s:%(port)s/%(end_point)s' % {
            'protocol': 'https' if hiveserver2_use_ssl() else 'http',
            'host': HIVE_SERVER_HOST.get(),
            'port': hive_site.hiveserver2_thrift_http_port(),
            'end_point': hive_site.hiveserver2_thrift_http_path()
        },
        'transport_mode': 'http' if hive_site.hiveserver2_transport_mode() == 'HTTP' else 'socket',
        'auth_username': AUTH_USERNAME.get(),
        'auth_password': AUTH_PASSWORD.get()
    }

  if name == 'sparksql': # Spark SQL is almost the same as Hive
    from spark.conf import SQL_SERVER_HOST as SPARK_SERVER_HOST, SQL_SERVER_PORT as SPARK_SERVER_PORT

    query_server.update({
        'server_name': 'sparksql',
        'server_host': SPARK_SERVER_HOST.get(),
        'server_port': SPARK_SERVER_PORT.get()
    })

  debug_query_server = query_server.copy()
  debug_query_server['auth_password_used'] = bool(debug_query_server.pop('auth_password'))
  LOG.debug("Query Server: %s" % debug_query_server)

  return query_server


class QueryServerException(Exception):
  # Ideally the query handle will be stored here too.

  def __init__(self, e, message=''):
    super(QueryServerException, self).__init__(e)
    self.message = message


class QueryServerTimeoutException(Exception):

  def __init__(self, message=''):
    super(QueryServerTimeoutException, self).__init__(message)
    self.message = message


class NoSuchObjectException: pass


class HiveServer2Dbms(object):

  def __init__(self, client, server_type):
    self.client = client
    self.server_type = server_type
    self.server_name = self.client.query_server['server_name']


  @classmethod
  def to_matching_wildcard(cls, identifier=None):
    cleaned = "*"
    if identifier and identifier.strip() != "*":
      cleaned = "*%s*" % identifier.strip().strip("*")
    return cleaned


  def get_databases(self, database_names='*'):
    if database_names != '*':
      database_names = self.to_matching_wildcard(database_names)

    databases = self.client.get_databases(schemaName=database_names)

    if len(databases) <= APPLY_NATURAL_SORT_MAX.get():
      databases = apply_natural_sort(databases)

    return databases


  def get_database(self, database):
    return self.client.get_database(database)


  def alter_database(self, database, properties):
    hql = 'ALTER database `%s` SET DBPROPERTIES (' % database
    hql += ', '.join(["'%s'='%s'" % (k, v) for k, v in properties.items()])
    hql += ');'

    timeout = SERVER_CONN_TIMEOUT.get()
    query = hql_query(hql)
    handle = self.execute_and_wait(query, timeout_sec=timeout)

    if handle:
      self.close(handle)
    else:
      msg = _("Failed to execute alter database statement: %s") % hql
      raise QueryServerException(msg)

    return self.client.get_database(database)


  def get_tables_meta(self, database='default', table_names='*', table_types=None):
    database = database.lower() # Impala is case sensitive

    if self.server_name == 'beeswax':
      identifier = self.to_matching_wildcard(table_names)
    else:
      identifier = None
    tables = self.client.get_tables_meta(database, identifier, table_types)
    if len(tables) <= APPLY_NATURAL_SORT_MAX.get():
      tables = apply_natural_sort(tables, key='name')
    return tables


  def get_tables(self, database='default', table_names='*', table_types=None):
    database = database.lower() # Impala is case sensitive

    if self.server_name == 'beeswax':
      identifier = self.to_matching_wildcard(table_names)
    else:
      identifier = None
    tables = self.client.get_tables(database, identifier, table_types)
    if len(tables) <= APPLY_NATURAL_SORT_MAX.get():
      tables = apply_natural_sort(tables)
    return tables


  def get_table(self, database, table_name):
    try:
      return self.client.get_table(database, table_name)
    except QueryServerException, e:
      LOG.debug("Seems like %s.%s could be a Kudu table" % (database, table_name))
      if 'java.lang.ClassNotFoundException' in e.message and [prop for prop in self.get_table_properties(database, table_name, property_name='storage_handler').rows() if 'KuduStorageHandler' in prop[0]]:
        query_server = get_query_server_config('impala')
        db = get(self.client.user, query_server)
        table = db.get_table(database, table_name)
        table.is_impala_only = True
        return table
      else:
        raise e


  def alter_table(self, database, table_name, new_table_name=None, comment=None, tblproperties=None):
    hql = 'ALTER TABLE `%s`.`%s`' % (database, table_name)

    if new_table_name:
      table_name = new_table_name
      hql += ' RENAME TO `%s`' % table_name
    elif comment:
      hql += " SET TBLPROPERTIES ('comment' = '%s')" % comment
    elif tblproperties:
      hql += " SET TBLPROPERTIES (%s)" % ' ,'.join("'%s' = '%s'" % (k, v) for k, v in tblproperties.items())

    timeout = SERVER_CONN_TIMEOUT.get()
    query = hql_query(hql)
    handle = self.execute_and_wait(query, timeout_sec=timeout)

    if handle:
      self.close(handle)
    else:
      msg = _("Failed to execute alter table statement: %s") % hql
      raise QueryServerException(msg)

    return self.client.get_table(database, table_name)


  def get_column(self, database, table_name, column_name):
    table = self.get_table(database, table_name)
    for col in table.cols:
      if col.name == column_name:
        return col
    return None


  def alter_column(self, database, table_name, column_name, new_column_name, column_type, comment=None,
                   partition_spec=None, cascade=False):
    hql = 'ALTER TABLE `%s`.`%s`' % (database, table_name)

    if partition_spec:
      hql += ' PARTITION (%s)' % partition_spec

    hql += ' CHANGE COLUMN `%s` `%s` %s' % (column_name, new_column_name, column_type.upper())

    if comment:
      hql += " COMMENT '%s'" % comment

    if cascade:
      hql += ' CASCADE'

    timeout = SERVER_CONN_TIMEOUT.get()
    query = hql_query(hql)
    handle = self.execute_and_wait(query, timeout_sec=timeout)

    if handle:
      self.close(handle)
    else:
      msg = _("Failed to execute alter column statement: %s") % hql
      raise QueryServerException(msg)

    return self.get_column(database, table_name, new_column_name)


  def execute_query(self, query, design):
    return self.execute_and_watch(query, design=design)


  def select_star_from(self, database, table, limit=1000):
    if table.partition_keys:  # Filter on max number of partitions for partitioned tables
      hql = self._get_sample_partition_query(database, table, limit=limit) # Currently need a limit
    else:
      hql = "SELECT * FROM `%s`.`%s` LIMIT %d;" % (database, table.name, limit)
    return self.execute_statement(hql)


  def get_select_star_query(self, database, table, limit=1000):
    if table.partition_keys:  # Filter on max number of partitions for partitioned tables
      hql = self._get_sample_partition_query(database, table, limit=limit) # Currently need a limit
    else:
      hql = "SELECT * FROM `%s`.`%s` LIMIT %d;" % (database, table.name, limit)
    return hql


  def execute_statement(self, hql):
    if self.server_name == 'impala':
      query = hql_query(hql, QUERY_TYPES[1])
    else:
      query = hql_query(hql, QUERY_TYPES[0])
    return self.execute_and_watch(query)


  def fetch(self, query_handle, start_over=False, rows=None):
    no_start_over_support = [config_variable for config_variable in self.get_default_configuration(False)
                                             if config_variable.key == 'support_start_over'
                                               and config_variable.value == 'false']
    if no_start_over_support:
      start_over = False

    return self.client.fetch(query_handle, start_over, rows)


  def close_operation(self, query_handle):
    return self.client.close_operation(query_handle)


  def open_session(self, user):
    return self.client.open_session(user)


  def close_session(self, session):
    resp = self.client.close_session(session)

    if resp.status.statusCode != 0:
      session.status_code = resp.status.statusCode
      session.save()
      raise QueryServerException(_('Failed to close session, session handle may already be closed or timed out.'))
    else:
      session.status_code = 4  # Set to ttypes.TStatusCode.INVALID_HANDLE_STATUS
      session.save()

    return session


  def cancel_operation(self, query_handle):
    resp = self.client.cancel_operation(query_handle)
    if self.client.query_server['server_name'] == 'impala':
      resp = self.client.close_operation(query_handle)
    return resp


  def get_sample(self, database, table, column=None, nested=None, limit=100):
    result = None
    hql = None

    # Filter on max # of partitions for partitioned tables
    column = '`%s`' % column if column else '*'
    if table.partition_keys:
      hql = self._get_sample_partition_query(database, table, column, limit)
    elif self.server_name == 'impala':
      if column or nested:
        from impala.dbms import ImpalaDbms
        select_clause, from_clause = ImpalaDbms.get_nested_select(database, table.name, column, nested)
        hql = 'SELECT %s FROM %s LIMIT %s;' % (select_clause, from_clause, limit)
      else:
        hql = "SELECT * FROM `%s`.`%s` LIMIT %s;" % (database, table.name, limit)
    else:
      hql = "SELECT %s FROM `%s`.`%s` LIMIT %s;" % (column, database, table.name, limit)
      # TODO: Add nested select support for HS2

    if hql:
      query = hql_query(hql)
      handle = self.execute_and_wait(query, timeout_sec=5.0)

      if handle:
        result = self.fetch(handle, rows=100)
        self.close(handle)

    return result


  def _get_sample_partition_query(self, database, table, column='*', limit=100):
    max_parts = QUERY_PARTITIONS_LIMIT.get()
    partitions = self.get_partitions(database, table, partition_spec=None, max_parts=max_parts)

    if partitions and max_parts:
      # Need to reformat partition specs for where clause syntax
      partition_specs = [part.partition_spec.replace(',', ' AND ') for part in partitions]
      partition_filters = ' OR '.join(['(%s)' % partition_spec for partition_spec in partition_specs])
      partition_clause = 'WHERE %s' % partition_filters
    else:
      partition_clause = ''

    return "SELECT %(column)s FROM `%(database)s`.`%(table)s` %(partition_clause)s LIMIT %(limit)s" % \
      {'column': column, 'database': database, 'table': table.name, 'partition_clause': partition_clause, 'limit': limit}


  def analyze_table(self, database, table):
    if self.server_name == 'impala':
      hql = 'COMPUTE STATS `%(database)s`.`%(table)s`' % {'database': database, 'table': table}
    else:
      table_obj = self.get_table(database, table)
      partition_spec = ''
      if table_obj.partition_keys:
        partition_keys = ','.join([part.name for part in table_obj.partition_keys])
        partition_spec = 'PARTITION(%(partition_keys)s)' % {'partition_keys': partition_keys}

      hql = 'ANALYZE TABLE `%(database)s`.`%(table)s` %(partition_spec)s COMPUTE STATISTICS' % \
            {'database': database, 'table': table, 'partition_spec': partition_spec}

    return self.execute_statement(hql)


  def analyze_table_columns(self, database, table):
    if self.server_name == 'impala':
      hql = 'COMPUTE STATS `%(database)s`.`%(table)s`' % {'database': database, 'table': table}
    else:
      table_obj = self.get_table(database, table)
      if table_obj.partition_keys:
        raise NotImplementedError('HIVE-4861: COMPUTE STATISTICS FOR COLUMNS not supported for partitioned-tables.')
      else:
        hql = 'ANALYZE TABLE `%(database)s`.`%(table)s` COMPUTE STATISTICS FOR COLUMNS' % {'database': database, 'table': table}

    return self.execute_statement(hql)


  def get_table_stats(self, database, table):
    stats = []

    if self.server_name == 'impala':
      hql = 'SHOW TABLE STATS `%(database)s`.`%(table)s`' % {'database': database, 'table': table}

      query = hql_query(hql)
      handle = self.execute_and_wait(query, timeout_sec=5.0)

      if handle:
        result = self.fetch(handle, rows=100)
        self.close(handle)
        stats = list(result.rows())
    else:
      table = self.get_table(database, table)
      stats = table.stats

    return stats


  def get_table_columns_stats(self, database, table, column):
    if self.server_name == 'impala':
      hql = 'SHOW COLUMN STATS `%(database)s`.`%(table)s`' % {'database': database, 'table': table}
    else:
      hql = 'DESCRIBE FORMATTED `%(database)s`.`%(table)s` `%(column)s`' % {'database': database, 'table': table, 'column': column}

    query = hql_query(hql)
    handle = self.execute_and_wait(query, timeout_sec=5.0)

    if handle:
      result = self.fetch(handle, rows=100)
      self.close(handle)
      data = list(result.rows())

      if self.server_name == 'impala':
        data = [col for col in data if col[0] == column][0]
        return [
            {'col_name': data[0]},
            {'data_type': data[1]},
            {'distinct_count': data[2]},
            {'num_nulls': data[3]},
            {'max_col_len': data[4]},
            {'avg_col_len': data[5]},
        ]
      else:
        return [
            {'col_name': data[2][0]},
            {'data_type': data[2][1]},
            {'min': data[2][2]},
            {'max': data[2][3]},
            {'num_nulls': data[2][4]},
            {'distinct_count': data[2][5]},
            {'avg_col_len': data[2][6]},
            {'max_col_len': data[2][7]},
            {'num_trues': data[2][8]},
            {'num_falses': data[2][9]}
        ]
    else:
      return []


  def get_table_properties(self, database, table, property_name=None):
    hql = 'SHOW TBLPROPERTIES `%s`.`%s`' % (database, table)
    if property_name:
      hql += ' ("%s")' % property_name

    query = hql_query(hql)
    handle = self.execute_and_wait(query, timeout_sec=5.0)

    if handle:
      result = self.fetch(handle, rows=100)
      self.close(handle)
      return result


  def get_table_describe(self, database, table):
    hql = 'DESCRIBE `%s`.`%s`' % (database, table)

    query = hql_query(hql)
    handle = self.execute_and_wait(query, timeout_sec=5.0)

    if handle:
      result = self.fetch(handle, rows=100)
      self.close(handle)
      return result


  def get_top_terms(self, database, table, column, limit=30, prefix=None):
    limit = min(limit, 100)
    prefix_match = ''
    if prefix:
      prefix_match = "WHERE CAST(%(column)s AS STRING) LIKE '%(prefix)s%%'" % {'column': column, 'prefix': prefix}

    hql = 'SELECT %(column)s, COUNT(*) AS ct FROM `%(database)s`.`%(table)s` %(prefix_match)s GROUP BY %(column)s ORDER BY ct DESC LIMIT %(limit)s' % {
        'database': database, 'table': table, 'column': column, 'prefix_match': prefix_match, 'limit': limit,
    }

    query = hql_query(hql)
    handle = self.execute_and_wait(query, timeout_sec=60.0) # Hive is very slow

    if handle:
      result = self.fetch(handle, rows=limit)
      self.close(handle)
      return list(result.rows())
    else:
      return []


  def drop_table(self, database, table):
    if table.is_view:
      hql = "DROP VIEW `%s`.`%s`" % (database, table.name,)
    else:
      hql = "DROP TABLE `%s`.`%s`" % (database, table.name,)

    return self.execute_statement(hql)


  def load_data(self, database, table, form, design):
    hql = "LOAD DATA INPATH"
    hql += " '%s'" % form.cleaned_data['path']
    if form.cleaned_data['overwrite']:
      hql += " OVERWRITE"
    hql += " INTO TABLE "
    hql += "`%s`.`%s`" % (database, table.name,)
    if form.partition_columns:
      hql += " PARTITION ("
      vals = []
      for key, column_name in form.partition_columns.iteritems():
        vals.append("%s='%s'" % (column_name, form.cleaned_data[key]))
      hql += ", ".join(vals)
      hql += ")"

    query = hql_query(hql, database)
    design.data = query.dumps()
    design.save()

    return self.execute_query(query, design)


  def drop_tables(self, database, tables, design, skip_trash=False, generate_ddl_only=False):
    hql = []

    for table in tables:
      if table.is_view:
        hql.append("DROP VIEW `%s`.`%s`" % (database, table.name,))
      else:
        drop_query = "DROP TABLE `%s`.`%s`" % (database, table.name,)
        drop_query += skip_trash and " PURGE" or ""
        hql.append(drop_query)

    query = hql_query(';'.join(hql), database)
    
    if generate_ddl_only:
      return query
    else:   
      design.data = query.dumps()
      design.save()
  
      return self.execute_query(query, design)


  def drop_database(self, database):
    return self.execute_statement("DROP DATABASE `%s`" % database)


  def drop_databases(self, databases, design):
    hql = []

    for database in databases:
      hql.append("DROP DATABASE `%s` CASCADE" % database)
    query = hql_query(';'.join(hql), database)
    design.data = query.dumps()
    design.save()

    return self.execute_query(query, design)

  def _get_and_validate_select_query(self, design, query_history):
    query = design.get_query_statement(query_history.statement_number)
    if not query.strip().lower().startswith('select'):
      raise Exception(_('Only SELECT statements can be saved. Provided query: %(query)s') % {'query': query})

    return query

  def insert_query_into_directory(self, query_history, target_dir):
    design = query_history.design.get_design()
    database = design.query['database']
    self.use(database)
    query = self._get_and_validate_select_query(design, query_history)
    hql = "INSERT OVERWRITE DIRECTORY '%s' %s" % (target_dir, query)
    return self.execute_statement(hql)


  def create_table_as_a_select(self, request, query_history, target_database, target_table, result_meta):
    design = query_history.design.get_design()
    database = design.query['database']

    # Case 1: Hive Server 2 backend or results straight from an existing table
    if result_meta.in_tablename:
      self.use(database)
      query = self._get_and_validate_select_query(design, query_history)
      hql = 'CREATE TABLE `%s`.`%s` AS %s' % (target_database, target_table, query)
      query_history = self.execute_statement(hql)
    else:
      # FYI: this path is dead since moving to HiveServer2
      #
      # Case 2: The results are in some temporary location
      # Beeswax backward compatibility and optimization
      # 1. Create table
      cols = ''
      schema = result_meta.schema
      for i, field in enumerate(schema.fieldSchemas):
        if i != 0:
          cols += ',\n'
        cols += '`%s` %s' % (field.name, field.type)

      # The representation of the delimiter is messy.
      # It came from Java as a string, which might has been converted from an integer.
      # So it could be "1" (^A), or "10" (\n), or "," (a comma literally).
      delim = result_meta.delim
      if not delim.isdigit():
        delim = str(ord(delim))

      hql = '''
            CREATE TABLE `%s` (
            %s
            )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY '\%s'
            STORED AS TextFile
            ''' % (target_table, cols, delim.zfill(3))

      query = hql_query(hql)
      self.execute_and_wait(query)

      try:
        # 2. Move the results into the table's storage
        table_obj = self.get_table('default', target_table)
        table_loc = request.fs.urlsplit(table_obj.path_location)[2]
        result_dir = request.fs.urlsplit(result_meta.table_dir)[2]
        request.fs.rename_star(result_dir, table_loc)
        LOG.debug("Moved results from %s to %s" % (result_meta.table_dir, table_loc))
        request.info(request, _('Saved query results as new table %(table)s.') % {'table': target_table})
        query_history.save_state(QueryHistory.STATE.expired)
      except Exception, ex:
        query = hql_query('DROP TABLE `%s`' % target_table)
        try:
          self.execute_and_wait(query)
        except Exception, double_trouble:
          LOG.exception('Failed to drop table "%s" as well: %s' % (target_table, double_trouble))
        raise ex
      url = format_preserving_redirect(request, reverse('metastore:index'))

    return query_history


  def use(self, database):
    query = hql_query('USE `%s`' % database)
    return self.client.use(query)


  def get_log(self, query_handle, start_over=True):
    return self.client.get_log(query_handle, start_over)


  def get_state(self, handle):
    return self.client.get_state(handle)


  def get_operation_status(self, handle):
    return self.client.get_operation_status(handle)


  def execute_and_wait(self, query, timeout_sec=30.0, sleep_interval=0.5):
    """
    Run query and check status until it finishes or timeouts.

    Check status until it finishes or timeouts.
    """
    handle = self.client.query(query)
    curr = time.time()
    end = curr + timeout_sec

    while curr <= end:
      state = self.client.get_state(handle)
      if state not in (QueryHistory.STATE.running, QueryHistory.STATE.submitted):
        return handle
      time.sleep(sleep_interval)
      curr = time.time()

    # Query timed out, so attempt to cancel operation and raise exception
    msg = "The query timed out after %(timeout)d seconds, canceled query." % {'timeout': timeout_sec}
    LOG.warning(msg)
    try:
      self.cancel_operation(handle)
    except Exception, e:
      msg = "Failed to cancel query."
      LOG.warning(msg)
      self.close_operation(handle)
      raise QueryServerException(e, message=msg)

    raise QueryServerTimeoutException(message=msg)


  def execute_next_statement(self, query_history, hql_query):
    if query_history.is_success() or query_history.is_expired():
      # We need to go to the next statement only if the previous one passed
      query_history.statement_number += 1
    else:
      # We need to update the query in case it was fixed
      query_history.refresh_design(hql_query)

    query_history.last_state = QueryHistory.STATE.submitted.index
    query_history.save()
    query = query_history.design.get_design()

    # In case of multiquery, we need to re-replace the parameters as we save the non substituted query
    if query._data_dict['query']['is_parameterized']:
      real_query = substitute_variables(query._data_dict['query']['query'], query_history.get_extra('parameters'))
      query._data_dict['query']['query'] = real_query

    return self.execute_and_watch(query, query_history=query_history)


  def execute_and_watch(self, query, design=None, query_history=None):
    """
    Run query and return a QueryHistory object in order to see its progress on a Web page.
    """
    hql_query = query.hql_query
    if query_history is None:
      query_history = QueryHistory.build(
          owner=self.client.user,
          query=hql_query,
          server_host='%(server_host)s' % self.client.query_server,
          server_port='%(server_port)d' % self.client.query_server,
          server_name='%(server_name)s' % self.client.query_server,
          server_type=self.server_type,
          last_state=QueryHistory.STATE.submitted.index,
          design=design,
          notify=query.query.get('email_notify', False),
          query_type=query.query['type'],
          statement_number=0
      )
      query_history.save()

      LOG.debug("Made new QueryHistory id %s user %s query: %s..." % (query_history.id, self.client.user, query_history.query[:25]))

    try:
      handle = self.client.query(query, query_history.statement_number)
      if not handle.is_valid():
        msg = _("Server returning invalid handle for query id %(id)d [%(query)s]...") % {'id': query_history.id, 'query': query[:40]}
        raise QueryServerException(msg)
    except QueryServerException, ex:
      LOG.exception(ex)
      # Kind of expected (hql compile/syntax error, etc.)
      if hasattr(ex, 'handle') and ex.handle:
        query_history.server_id, query_history.server_guid = ex.handle.id, ex.handle.id
        query_history.log_context = ex.handle.log_context
      query_history.save_state(QueryHistory.STATE.failed)
      raise ex

    # All good
    query_history.server_id, query_history.server_guid = handle.get()
    query_history.operation_type = handle.operation_type
    query_history.has_results = handle.has_result_set
    query_history.modified_row_count = handle.modified_row_count
    query_history.log_context = handle.log_context
    query_history.query_type = query.query['type']
    query_history.set_to_running()
    query_history.save()

    LOG.debug("Updated QueryHistory id %s user %s statement_number: %s" % (query_history.id, self.client.user, query_history.statement_number))

    return query_history


  def get_results_metadata(self, handle):
    return self.client.get_results_metadata(handle)


  def close(self, handle):
    return self.client.close(handle)


  def get_partitions(self, db_name, table, partition_spec=None, max_parts=None, reverse_sort=True):
    if max_parts is None or max_parts > LIST_PARTITIONS_LIMIT.get():
      max_parts = LIST_PARTITIONS_LIMIT.get()

    return self.client.get_partitions(db_name, table.name, partition_spec, max_parts=max_parts, reverse_sort=reverse_sort)


  def get_partition(self, db_name, table_name, partition_spec):
    table = self.get_table(db_name, table_name)
    partitions = self.get_partitions(db_name, table, partition_spec=partition_spec)

    if len(partitions) != 1:
      raise NoSuchObjectException(_("Query did not return exactly one partition result"))

    partition = partitions[0]
    partition_query = " AND ".join(partition.partition_spec.split(','))

    hql = "SELECT * FROM `%s`.`%s` WHERE %s" % (db_name, table_name, partition_query)

    return self.execute_statement(hql)


  def describe_partition(self, db_name, table_name, partition_spec):
    return self.client.get_table(db_name, table_name, partition_spec=partition_spec)


  def drop_partitions(self, db_name, table_name, partition_specs, design):
    hql = []

    for partition_spec in partition_specs:
      hql.append("ALTER TABLE `%s`.`%s` DROP IF EXISTS PARTITION (%s) PURGE" % (db_name, table_name, partition_spec))

    query = hql_query(';'.join(hql), db_name)
    design.data = query.dumps()
    design.save()

    return self.execute_query(query, design)


  def get_indexes(self, db_name, table_name):
    hql = 'SHOW FORMATTED INDEXES ON `%(table)s` IN `%(database)s`' % {'table': table_name, 'database': db_name}

    query = hql_query(hql)
    handle = self.execute_and_wait(query, timeout_sec=15.0)

    if handle:
      result = self.fetch(handle, rows=5000)
      self.close(handle)

    return result


  def get_configuration(self):
    return self.client.get_configuration()


  def get_functions(self, prefix=None):
    filter = '"%s.*"' % prefix if prefix else '".*"'
    hql = 'SHOW FUNCTIONS %s' % filter

    query = hql_query(hql)
    handle = self.execute_and_wait(query, timeout_sec=15.0)

    if handle:
      result = self.fetch(handle, rows=5000)
      self.close(handle)

    return result


  def explain(self, query):
    return self.client.explain(query)


  def getStatus(self):
    return self.client.getStatus()


  def get_default_configuration(self, include_hadoop):
    return self.client.get_default_configuration(include_hadoop)


class Table:
  """
  Represents the metadata of a Hive Table.
  """
  @property
  def hdfs_link(self):
    return location_to_url(self.path_location)


class DataTable:
  """
  Represents the data of a Hive Table.

  If the dataset has more rows, a new fetch should be done in order to return a new data table with the next rows.
  """
  pass


# TODO decorator?
def expand_exception(exc, db, handle=None):
  try:
    if handle is not None:
      log = db.get_log(handle)
    elif hasattr(exc, 'get_rpc_handle') or hasattr(exc, 'log_context'):
      log = db.get_log(exc)
    else:
      log = ''
  except Exception, e:
    # Always show something, even if server has died on the job.
    log = _("Could not retrieve logs: %s." % e)

  if not exc.args or not exc.args[0]:
    error_message = _("Unknown exception.")
  else:
    error_message = force_unicode(exc.args[0], strings_only=True, errors='replace')
  return error_message, log
