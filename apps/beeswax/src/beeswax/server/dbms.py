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
import thrift
import time

from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _

from beeswax import hive_site
from beeswax.conf import HIVE_SERVER_HOST, HIVE_SERVER_PORT,\
  BROWSE_PARTITIONED_TABLE_LIMIT
from beeswax.design import hql_query
from beeswax.models import QueryHistory, HIVE_SERVER2, BEESWAX

from filebrowser.views import location_to_url
from desktop.lib.django_util import format_preserving_redirect
from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)


def get(user, query_server=None):
  # Avoid circular dependency
  from beeswax.server.hive_server2_lib import HiveServerClientCompatible, HiveServerClient

  if query_server is None:
    query_server = get_query_server_config()

  return Dbms(HiveServerClientCompatible(HiveServerClient(query_server, user)), QueryHistory.SERVER_TYPE[1][0])


def get_query_server_config(name='beeswax'):
  if name == 'impala':
    from impala.conf import SERVER_HOST as IMPALA_SERVER_HOST, SERVER_PORT as IMPALA_SERVER_PORT, \
        IMPALA_PRINCIPAL, IMPERSONATION_ENABLED

    query_server = {
        'server_name': 'impala',
        'server_host': IMPALA_SERVER_HOST.get(),
        'server_port': IMPALA_SERVER_PORT.get(),
        'principal': IMPALA_PRINCIPAL.get(),
        'impersonation_enabled': IMPERSONATION_ENABLED.get()
    }
  else:
    kerberos_principal = hive_site.get_hiveserver2_kerberos_principal(HIVE_SERVER_HOST.get())

    query_server = {
        'server_name': 'beeswax', # Aka HiveServer2 now
        'server_host': HIVE_SERVER_HOST.get(),
        'server_port': HIVE_SERVER_PORT.get(),
        'principal': kerberos_principal
    }
    LOG.debug("Query Server: %s" % query_server)

  return query_server


class QueryServerException(Exception):
  # Ideally the query handle will be stored here too.

  def __init__(self, e, message=''):
    super(QueryServerException, self).__init__(e)
    self.message = message


class NoSuchObjectException: pass


class Dbms:
  """SQL"""

  def __init__(self, client, server_type):
    self.client = client
    self.server_type = server_type


  def get_table(self, database, table_name):
    # DB name not supported in SHOW PARTITIONS required in Table
    self.use(database)

    return self.client.get_table(database, table_name)


  def get_tables(self, database='default', table_names='.*'):
    return self.client.get_tables(database, table_names)


  def get_databases(self):
    return self.client.get_databases()


  def execute_query(self, query, design):
    return self.execute_and_watch(query, design=design)


  def select_star_from(self, database, table):
    hql = "SELECT * FROM `%s.%s` %s" % (database, table.name, self._get_browse_limit_clause(table))
    return self.execute_statement(hql)


  def execute_statement(self, hql):
    query = hql_query(hql)
    return self.execute_and_watch(query)


  def fetch(self, query_handle, start_over=False, rows=None):
    no_start_over_support = [config_variable for config_variable in self.get_default_configuration(False)
                                             if config_variable.key == 'support_start_over'
                                               and config_variable.value == 'false']
    if no_start_over_support:
      start_over = False

    return self.client.fetch(query_handle, start_over, rows)


  def close_operation(self, query_handle):
    if self.server_type == BEESWAX:
      raise PopupException(_('%s interface does not support close_operation. %s interface does.') % (BEESWAX, HIVE_SERVER2))

    return self.client.close_operation(query_handle)

  def open_session(self, user):
    return self.client.open_session(user)

  def cancel_operation(self, query_handle):
    resp = self.client.cancel_operation(query_handle)
    if self.client.query_server['server_name'] == 'impala':
      resp = self.client.close_operation(query_handle)
    return resp


  def get_sample(self, database, table):
    """No samples if it's a view (HUE-526)"""
    if not table.is_view:
      limit = min(100, BROWSE_PARTITIONED_TABLE_LIMIT.get())
      hql = "SELECT * FROM `%s.%s` LIMIT %s" % (database, table.name, limit)
      query = hql_query(hql)
      handle = self.execute_and_wait(query, timeout_sec=5.0)

      if handle:
        return self.fetch(handle)


  def drop_table(self, database, table):
    if table.is_view:
      hql = "DROP VIEW `%s.%s`" % (database, table.name,)
    else:
      hql = "DROP TABLE `%s.%s`" % (database, table.name,)

    return self.execute_statement(hql)


  def load_data(self, database, table, form, design):
    hql = "LOAD DATA INPATH"
    hql += " '%s'" % form.cleaned_data['path']
    if form.cleaned_data['overwrite']:
      hql += " OVERWRITE"
    hql += " INTO TABLE "
    hql += "`%s.%s`" % (database, table.name,)
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


  def drop_tables(self, database, tables, design):
    hql = []

    for table in tables:
      if table.is_view:
        hql.append("DROP VIEW `%s.%s`" % (database, table.name,))
      else:
        hql.append("DROP TABLE `%s.%s`" % (database, table.name,))
    query = hql_query(';'.join(hql), database)
    design.data = query.dumps()
    design.save()

    return self.execute_query(query, design)


  def drop_database(self, database):
    return self.execute_statement("DROP DATABASE `%s`" % database)


  def drop_databases(self, databases, design):
    hql = []

    for database in databases:
      hql.append("DROP DATABASE `%s`" % database)
    query = hql_query(';'.join(hql), database)
    design.data = query.dumps()
    design.save()

    return self.execute_query(query, design)

  def insert_query_into_directory(self, query_history, target_dir):
    design = query_history.design.get_design()

    hql = "INSERT OVERWRITE DIRECTORY '%s' %s" % (target_dir, design.query['query'])
    return self.execute_statement(hql)


  def create_table_as_a_select(self, request, query_history, target_table, result_meta):
    design = query_history.design.get_design()
    database = design.query['database']

    # Case 1: Hive Server 2 backend or results straight from an existing table
    if result_meta.in_tablename:
      hql = 'CREATE TABLE `%s.%s` AS %s' % (database, target_table, design.query['query'])
      #query = hql_query(hql, database=database)
      query_history = self.execute_statement(hql)
      url = redirect(reverse('beeswax:watch_query', args=[query_history.id]) + '?on_success_url=' + reverse('metastore:describe_table', args=[database, target_table]))
    else:
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

    return url


  def use(self, database):
    query = hql_query('USE %s' % database)
    self.client.query(query)
    # TODO sync + close query

  def get_log(self, query_handle):
    return self.client.get_log(query_handle)


  def get_state(self, handle):
    return self.client.get_state(handle)


  def execute_and_wait(self, query, timeout_sec=30.0):
    """
    Run query and check status until it finishes or timeouts.
    """
    SLEEP_INTERVAL = 0.5

    handle = self.client.query(query)
    curr = time.time()
    end = curr + timeout_sec

    while curr <= end:
      state = self.client.get_state(handle)
      if state not in (QueryHistory.STATE.running, QueryHistory.STATE.submitted):
        return handle
      time.sleep(SLEEP_INTERVAL)
      curr = time.time()
    return None


  def execute_next_statement(self, query_history):
    query_history.statement_number += 1
    query_history.last_state = QueryHistory.STATE.submitted.index
    query_history.save()
    query = query_history.design.get_design()
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
        msg = _("Server returning invalid handle for query id %(id)d [%(query)s]...") % \
              {'id': query_history.id, 'query': query[:40]}
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


  def get_partitions(self, db_name, table, max_parts=None):
    if max_parts is None or max_parts > BROWSE_PARTITIONED_TABLE_LIMIT.get():
      max_parts = BROWSE_PARTITIONED_TABLE_LIMIT.get()

    # DB name not supported in SHOW PARTITIONS
    self.use(db_name)

    return self.client.get_partitions(db_name, table.name, max_parts)

  def get_partition(self, db_name, table_name, partition_id):
    table = self.get_table(db_name, table_name)
    partitions = self.get_partitions(db_name, table, max_parts=None)

    partition_query = ""
    for idx, key in enumerate(partitions[partition_id].values):
      partition_query += (idx > 0 and " AND " or "") + table.partition_keys[idx].name + "='%s'" % key

    hql = "SELECT * FROM `%s.%s` WHERE %s" % (db_name, table_name, partition_query)

    return self.execute_statement(hql)


  def explain(self, statement):
    return self.client.explain(statement)


  def getStatus(self):
    return self.client.getStatus()


  def get_default_configuration(self, include_hadoop):
    return self.client.get_default_configuration(include_hadoop)


  def _get_browse_limit_clause(self, table):
    """Get the limit clause when browsing a partitioned table"""
    if table.partition_keys:
      limit = BROWSE_PARTITIONED_TABLE_LIMIT.get()
      if limit > 0:
        return "LIMIT %d" % (limit,)
    return ""


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

  if not hasattr(exc, 'message') or not exc.message:
    error_message = _("Unknown exception.")
  else:
    error_message = force_unicode(exc.message, strings_only=True, errors='replace')
  return error_message, log
