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

from builtins import object
import logging
import re
import sys
import threading
import time
import json

from django.core.cache import caches
from django.urls import reverse
from kazoo.client import KazooClient

from desktop.conf import CLUSTER_ID, has_connectors
from desktop.lib.django_util import format_preserving_redirect
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.parameterization import substitute_variables
from desktop.lib.view_util import location_to_url
from desktop.models import Cluster
from desktop.settings import CACHES_HIVE_DISCOVERY_KEY
from indexer.file_format import HiveFormat
from libzookeeper import conf as libzookeeper_conf

from azure.abfs import abfspath
from beeswax.conf import HIVE_SERVER_HOST, HIVE_SERVER_PORT, HIVE_SERVER_HOST, HIVE_HTTP_THRIFT_PORT, HIVE_METASTORE_HOST, \
    HIVE_METASTORE_PORT, LIST_PARTITIONS_LIMIT, SERVER_CONN_TIMEOUT, \
    AUTH_USERNAME, AUTH_PASSWORD, APPLY_NATURAL_SORT_MAX, QUERY_PARTITIONS_LIMIT, HIVE_DISCOVERY_HIVESERVER2_ZNODE, \
    HIVE_DISCOVERY_HS2, HIVE_DISCOVERY_LLAP, HIVE_DISCOVERY_LLAP_HA, HIVE_DISCOVERY_LLAP_ZNODE, CACHE_TIMEOUT, \
    LLAP_SERVER_HOST, LLAP_SERVER_PORT, LLAP_SERVER_THRIFT_PORT, USE_SASL as HIVE_USE_SASL, CLOSE_SESSIONS, has_session_pool, \
    MAX_NUMBER_OF_SESSIONS
from beeswax.common import apply_natural_sort
from beeswax.design import hql_query
from beeswax.hive_site import hiveserver2_use_ssl, hiveserver2_impersonation_enabled, get_hiveserver2_kerberos_principal, \
    hiveserver2_transport_mode, hiveserver2_thrift_http_path
from beeswax.models import QueryHistory, QUERY_TYPES


if sys.version_info[0] > 2:
  from django.utils.encoding import force_str
else:
  from django.utils.encoding import force_unicode as force_str

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _

LOG = logging.getLogger(__name__)


RESET_HS2_QUERY_SERVER = False
DBMS_CACHE = {}
DBMS_CACHE_LOCK = threading.Lock()
cache = caches[CACHES_HIVE_DISCOVERY_KEY]

# Using file cache to make sure eventlet threads are uniform, this cache is persistent on startup
# So we clear it to make sure the server resets hiveserver2 host.
def reset_ha():
  global RESET_HS2_QUERY_SERVER
  cache.clear()
  RESET_HS2_QUERY_SERVER = True


reset_ha()


def get_zk_hs2():
  hiveservers = None
  zk = KazooClient(hosts=libzookeeper_conf.ENSEMBLE.get(), read_only=True)
  zk.start()
  znode = HIVE_DISCOVERY_HIVESERVER2_ZNODE.get()
  if zk.exists(znode):
    LOG.debug("Selecting up Hive server via the following node {0}".format(znode))
    hiveservers = zk.get_children(znode)
  zk.stop()
  return hiveservers


def get(user, query_server=None, cluster=None):
  global DBMS_CACHE
  global DBMS_CACHE_LOCK
  global RESET_HS2_QUERY_SERVER

  if query_server is None:
    query_server = get_query_server_config(connector=cluster)

  DBMS_CACHE_LOCK.acquire()
  try:
    DBMS_CACHE.setdefault(user.id, {})

    if query_server['server_name'] not in DBMS_CACHE[user.id]:
      # Avoid circular dependency
      from beeswax.server.hive_server2_lib import HiveServerClientCompatible

      if query_server.get('dialect') == 'impala':
        from impala.dbms import ImpalaDbms
        from impala.server import ImpalaServerClient
        DBMS_CACHE[user.id][query_server['server_name']] = ImpalaDbms(
            HiveServerClientCompatible(ImpalaServerClient(query_server, user)),
            QueryHistory.SERVER_TYPE[1][0]
        )
      elif query_server['server_name'] == 'hms':
        from beeswax.server.hive_metastore_server import HiveMetastoreClient
        DBMS_CACHE[user.id][query_server['server_name']] = HiveServer2Dbms(
            HiveMetastoreClient(query_server, user),
            QueryHistory.SERVER_TYPE[1][0]
        )
      else:
        from beeswax.server.hive_server2_lib import HiveServerClient
        DBMS_CACHE[user.id][query_server['server_name']] = HiveServer2Dbms(
            HiveServerClientCompatible(HiveServerClient(query_server, user)),
            QueryHistory.SERVER_TYPE[1][0]
        )
    elif RESET_HS2_QUERY_SERVER:
      from beeswax.server.hive_server2_lib import HiveServerClient, HiveServerClientCompatible
      RESET_HS2_QUERY_SERVER = False
      LOG.debug('Setting DBMS cache for the new hs2')
      DBMS_CACHE[user.id].clear()
      DBMS_CACHE[user.id][query_server['server_name']] = HiveServer2Dbms(
        HiveServerClientCompatible(HiveServerClient(query_server, user)),
        QueryHistory.SERVER_TYPE[1][0]
      )
    return DBMS_CACHE[user.id][query_server['server_name']]
  finally:
    DBMS_CACHE_LOCK.release()


def get_query_server_config(name='beeswax', connector=None):
  if connector and has_connectors(): # TODO: Give empty connector when no connector in use
    LOG.debug("Query via connector %s" % name)
    query_server = get_query_server_config_via_connector(connector)
  else:
    LOG.debug("Query via ini %s" % name)
    if name == "llap":
      activeEndpoint = cache.get('llap')
      if activeEndpoint is None:
        if HIVE_DISCOVERY_LLAP.get():
          LOG.debug("Checking zookeeper for discovering Hive LLAP server endpoint")
          zk = KazooClient(hosts=libzookeeper_conf.ENSEMBLE.get(), read_only=True)
          zk.start()
          if HIVE_DISCOVERY_LLAP_HA.get():
            znode = "{0}/instances".format(HIVE_DISCOVERY_LLAP_ZNODE.get())
            LOG.debug("Setting up Hive LLAP HA with the following node {0}".format(znode))
            if zk.exists(znode):
              hiveservers = zk.get_children(znode)
              if not hiveservers:
                raise PopupException(_('There is no running Hive LLAP server available'))
              LOG.info("Available Hive LLAP servers: {0}".format(hiveservers))
              for server in hiveservers:
                llap_servers = json.loads(zk.get("{0}/{1}".format(znode, server))[0])["internal"][0]
                if llap_servers["api"] == "activeEndpoint":
                  LOG.info("Selecting Hive LLAP server: {0}".format(llap_servers))
                  cache.set(
                    "llap",
                    json.dumps({
                        "host": llap_servers["addresses"][0]["host"],
                        "port": llap_servers["addresses"][0]["port"]
                      }),
                      CACHE_TIMEOUT.get()
                  )
            else:
              LOG.error("Hive LLAP endpoint not found, reverting to config values")
              cache.set("llap", json.dumps({"host": HIVE_SERVER_HOST.get(), "port": HIVE_HTTP_THRIFT_PORT.get()}), CACHE_TIMEOUT.get())
          else:
            znode = "{0}".format(HIVE_DISCOVERY_LLAP_ZNODE.get())
            LOG.debug("Setting up Hive LLAP with the following node {0}".format(znode))
            if zk.exists(znode):
              hiveservers = zk.get_children(znode)
              for server in hiveservers:
                cache.set(
                  "llap",
                  json.dumps({
                    "host": server.split(';')[0].split('=')[1].split(":")[0],
                    "port": server.split(';')[0].split('=')[1].split(":")[1]
                  })
                )
          zk.stop()
        else:
          LOG.debug("Zookeeper discovery not enabled, reverting to config values")
          cache.set("llap", json.dumps({"host": LLAP_SERVER_HOST.get(), "port": LLAP_SERVER_THRIFT_PORT.get()}), CACHE_TIMEOUT.get())

      activeEndpoint = json.loads(cache.get("llap"))

    elif name != 'hms' and name != 'impala':
      activeEndpoint = cache.get("hiveserver2")
      if activeEndpoint is None:
        if HIVE_DISCOVERY_HS2.get():
          hiveservers = get_zk_hs2()
          LOG.debug("Available Hive Servers: {0}".format(hiveservers))
          if not hiveservers:
            LOG.error('There are no running Hive server available')
            raise PopupException(_('There are no running Hive server available'))
          server_to_use = 0
          LOG.debug("Selected Hive server {0}: {1}".format(server_to_use, hiveservers[server_to_use]))
          cache.set(
            "hiveserver2",
            json.dumps({
              "host": hiveservers[server_to_use].split(";")[0].split("=")[1].split(":")[0],
              "port": hiveservers[server_to_use].split(";")[0].split("=")[1].split(":")[1]
            })
          )
        else:
          cache.set("hiveserver2", json.dumps({"host": HIVE_SERVER_HOST.get(), "port": HIVE_HTTP_THRIFT_PORT.get()}))
      else:
        # Setting hs2 cache in-case there is no HS2 discovery
        cache.set("hiveserver2", json.dumps({"host": HIVE_SERVER_HOST.get(), "port": HIVE_HTTP_THRIFT_PORT.get()}))
        if HIVE_DISCOVERY_HS2.get():
          # Replace ActiveEndpoint if the current HS2 is down
          hiveservers = get_zk_hs2()
          if hiveservers:
            server_to_use = 0
            hs2_host_name = hiveservers[server_to_use].split(";")[0].split("=")[1].split(":")[0]
            hs2_in_active_endpoint = hs2_host_name in activeEndpoint
            LOG.debug("Is the current HS2 active {0}".format(hs2_in_active_endpoint))
            if not hs2_in_active_endpoint:
              LOG.error(
                'Current HiveServer is down, working to connect with the next available HiveServer from Zookeeper')
              reset_ha()
              server_to_use = 0
              LOG.debug("Selected HiveServer {0}: {1}".format(server_to_use, hiveservers[server_to_use]))
              cache.set(
                "hiveserver2",
                json.dumps({
                  "host": hiveservers[server_to_use].split(";")[0].split("=")[1].split(":")[0],
                  "port": hiveservers[server_to_use].split(";")[0].split("=")[1].split(":")[1]
                })
              )
          else:
            LOG.error('Currently there are no HiveServer2 running')
            raise PopupException(_('Currently there are no HiveServer2 running'))

      activeEndpoint = json.loads(cache.get("hiveserver2"))

    if name == 'impala':
      from impala.dbms import get_query_server_config as impala_query_server_config
      query_server = impala_query_server_config()
    elif name == 'hms':
      kerberos_principal = get_hiveserver2_kerberos_principal(HIVE_SERVER_HOST.get())
      query_server = {
          'server_name': 'hms',
          'server_host': HIVE_METASTORE_HOST.get() if not cluster_config else cluster_config.get('server_host'),
          'server_port': HIVE_METASTORE_PORT.get(),
          'principal': kerberos_principal,
          'transport_mode': 'http' if hiveserver2_transport_mode() == 'HTTP' else 'socket',
          'auth_username': AUTH_USERNAME.get(),
          'auth_password': AUTH_PASSWORD.get(),
          'use_sasl': HIVE_USE_SASL.get()
      }
    else:
      kerberos_principal = get_hiveserver2_kerberos_principal(HIVE_SERVER_HOST.get())
      query_server = {
          'server_name': 'beeswax' if name != 'hplsql' else 'hplsql',
          'server_host': activeEndpoint["host"],
          'server_port': LLAP_SERVER_PORT.get() if name == 'llap' else HIVE_SERVER_PORT.get(),
          'principal': kerberos_principal,
          'http_url': '%(protocol)s://%(host)s:%(port)s/%(end_point)s' % {
              'protocol': 'https' if hiveserver2_use_ssl() else 'http',
              'host': activeEndpoint["host"],
              'port': activeEndpoint["port"],
              'end_point': hiveserver2_thrift_http_path()
            },
          'transport_mode': 'http' if hiveserver2_transport_mode() == 'HTTP' else 'socket',
          'auth_username': AUTH_USERNAME.get(),
          'auth_password': AUTH_PASSWORD.get(),
          'use_sasl': HIVE_USE_SASL.get(),
          'close_sessions': CLOSE_SESSIONS.get(),
          'has_session_pool': has_session_pool(),
          'max_number_of_sessions': MAX_NUMBER_OF_SESSIONS.get()
        }

    if name == 'sparksql':  # Extends Hive as very similar
      from spark.conf import SQL_SERVER_HOST as SPARK_SERVER_HOST, SQL_SERVER_PORT as SPARK_SERVER_PORT, USE_SASL as SPARK_USE_SASL

      query_server.update({
          'server_name': 'sparksql',
          'server_host': SPARK_SERVER_HOST.get(),
          'server_port': SPARK_SERVER_PORT.get(),
          'use_sasl': SPARK_USE_SASL.get()
      })

  if not query_server.get('dialect'):
    query_server['dialect'] = query_server['server_name']

  debug_query_server = query_server.copy()
  debug_query_server['auth_password_used'] = bool(debug_query_server.pop('auth_password', None))
  LOG.debug("Query Server: %s" % debug_query_server)

  return query_server


def get_query_server_config_via_connector(connector):
  # TODO: connector is actually a notebook interpreter
  connector_name = full_connector_name = connector['type']
  compute_name = None
  if connector.get('compute'):
    compute_name = connector['compute']['name']
    full_connector_name = '%s-%s' % (connector_name, compute_name)
  LOG.debug("Query cluster connector %s compute %s" % (connector_name, compute_name))

  if connector['options'].get('has_ssh') == 'true':
    server_host = '127.0.0.1'
    server_port = connector['options']['server_port']
  else:
    server_host = (connector['compute']['options'] if 'compute' in connector else connector['options'])['server_host']
    server_port = int((connector['compute']['options'] if 'compute' in connector else connector['options'])['server_port'])

  if 'impersonation_enabled' in connector['options']:
    impersonation_enabled = connector['options']['impersonation_enabled'] == 'true'
  else:
    impersonation_enabled = hiveserver2_impersonation_enabled()

  return {
      'dialect': connector['dialect'],
      'server_name': full_connector_name,
      'server_host': server_host,
      'server_port': server_port,
      'principal': 'TODO',
      'auth_username': AUTH_USERNAME.get(),
      'auth_password': AUTH_PASSWORD.get(),

      'impersonation_enabled': impersonation_enabled,
      'use_sasl': connector['options'].get('use_sasl', 'true') == 'true',
      'SESSION_TIMEOUT_S': 15 * 60,
      'querycache_rows': 1000,
      'QUERY_TIMEOUT_S': 15 * 60,
  }


class QueryServerException(Exception):
  # Ideally the query handle will be stored here too.

  def __init__(self, e, message=''):
    super(QueryServerException, self).__init__(e)
    self.message = message


class InvalidSessionQueryServerException(QueryServerException):
  def __init__(self, e, message=''):
    super(InvalidSessionQueryServerException, self).__init__(e, message=message)


class QueryServerTimeoutException(Exception):

  def __init__(self, message=''):
    super(QueryServerTimeoutException, self).__init__(message)
    self.message = message


class HiveServer2Dbms(object):

  def __init__(self, client, server_type):
    self.client = client
    self.server_type = server_type
    self.server_name = self.client.query_server.get('dialect') if self.client.query_server['server_name'].isdigit() \
        else self.client.query_server['server_name']


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
    hql += ', '.join(["'%s'='%s'" % (k, v) for k, v in list(properties.items())])
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
    database = database.lower()  # Impala is case sensitive

    if self.server_name in ('beeswax', 'sparksql'):
      identifier = self.to_matching_wildcard(table_names)
    else:
      identifier = None  # Impala

    if self.server_name == 'sparksql':
      tables = self._get_tables_via_sparksql(database, identifier)
    else:
      tables = self.client.get_tables_meta(database, identifier)

    if len(tables) <= APPLY_NATURAL_SORT_MAX.get():
      tables = apply_natural_sort(tables, key='name')
    return tables


  def get_tables(self, database='default', table_names='*', table_types=None):
    database = database.lower()  # Impala is case sensitive

    if self.server_name in ('beeswax', 'sparksql'):
      identifier = self.to_matching_wildcard(table_names)
    else:
      identifier = None

    tables = self.client.get_tables(database, identifier, table_types)

    if len(tables) <= APPLY_NATURAL_SORT_MAX.get():
      tables = apply_natural_sort(tables)
    return tables


  def _get_tables_via_sparksql(self, database, table_names='*'):
    hql = "SHOW TABLES IN %s" % database
    if table_names != '*':
      identifier = self.to_matching_wildcard(table_names)
      hql += " LIKE '%s'" % (identifier)

    query = hql_query(hql)
    timeout = SERVER_CONN_TIMEOUT.get()

    handle = self.execute_and_wait(query, timeout_sec=timeout)

    if handle:
      result = self.fetch(handle, rows=5000)
      self.close(handle)

      # We get back: database | tableName | isTemporary
      return [{
          'name': row[1],
          'type': 'VIEW' if row[2] else 'TABLE',
          'comment': ''
        }
        for row in result.rows()
      ]
    else:
      return []


  def get_table(self, database, table_name):
    try:
      return self.client.get_table(database, table_name)
    except QueryServerException as e:
      LOG.debug("Seems like %s.%s could be a Kudu table" % (database, table_name))
      if 'java.lang.ClassNotFoundException' in e.message and [
            prop
            for prop in self.get_table_properties(database, table_name, property_name='storage_handler').rows()
            if 'KuduStorageHandler' in prop[0]
        ]:
        query_server = get_query_server_config('impala')
        db = get(self.client.user, query_server)
        table = db.get_table(database, table_name)
        table.is_impala_only = True
        return table
      else:
        raise e


  def alter_table(self, database, table_name, new_table_name=None, comment=None, tblproperties=None):
    table_obj = self.get_table(database, table_name)
    if table_obj is None:
      raise PopupException(_("Failed to find the table: %s") % table_name)

    if table_obj.is_view:
      hql = 'ALTER VIEW `%s`.`%s`' % (database, table_name)
    else:
      hql = 'ALTER TABLE `%s`.`%s`' % (database, table_name)

    if new_table_name:
      table_name = new_table_name
      hql += ' RENAME TO `%s`' % table_name
    elif comment is not None:
      hql += " SET TBLPROPERTIES ('comment' = '%s')" % comment
    elif tblproperties:
      hql += " SET TBLPROPERTIES (%s)" % ' ,'.join("'%s' = '%s'" % (k, v) for k, v in list(tblproperties.items()))

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


  def alter_column(self, database, table_name, column_name, new_column_name, column_type, comment=None, partition_spec=None, cascade=False):
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
    if self.server_name.startswith('impala'):
      query = hql_query(hql, QUERY_TYPES[1])
    else:
      query = hql_query(hql, QUERY_TYPES[0])
    return self.execute_and_watch(query)


  def fetch(self, query_handle, start_over=False, rows=None):
    no_start_over_support = [
        config_variable
        for config_variable in self.get_default_configuration(False)
        if config_variable.key == 'support_start_over' and config_variable.value == 'false'
    ]
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
    if self.client.query_server.get('dialect') == 'impala':
      resp = self.client.close_operation(query_handle)
    return resp


  def get_sample(self, database, table, column=None, nested=None, limit=100, generate_sql_only=False, operation=None):
    result = None
    hql = None

    # Filter on max # of partitions for partitioned tables
    column = '`%s`' % column if column else '*'
    if operation == 'hello':
      hql = "SELECT 'Hello World!'"
    elif table.partition_keys:
      hql = self._get_sample_partition_query(database, table, column, limit, operation)
    elif self.server_name.startswith('impala'):
      if column or nested:
        from impala.dbms import ImpalaDbms
        select_clause, from_clause = ImpalaDbms.get_nested_select(database, table.name, column, nested)
        if operation == 'distinct':
          hql = 'SELECT DISTINCT %s FROM %s LIMIT %s;' % (select_clause, from_clause, limit)
        elif operation == 'max':
          hql = 'SELECT max(%s) FROM %s;' % (select_clause, from_clause)
        elif operation == 'min':
          hql = 'SELECT min(%s) FROM %s;' % (select_clause, from_clause)
        else:
          hql = 'SELECT %s FROM %s LIMIT %s;' % (select_clause, from_clause, limit)
      else:
        hql = "SELECT * FROM `%s`.`%s` LIMIT %s;" % (database, table.name, limit)
    else:
      if operation == 'distinct':
        hql = "SELECT DISTINCT %s FROM `%s`.`%s` LIMIT %s;" % (column, database, table.name, limit)
      elif operation == 'max':
        hql = "SELECT max(%s) FROM `%s`.`%s`;" % (column, database, table.name)
      elif operation == 'min':
        hql = "SELECT min(%s) FROM `%s`.`%s`;" % (column, database, table.name)
      else:
        hql = "SELECT %s FROM `%s`.`%s` LIMIT %s;" % (column, database, table.name, limit)
      # TODO: Add nested select support for HS2

    if hql:
      if generate_sql_only:
        return hql
      else:
        query = hql_query(hql)
        handle = self.execute_and_wait(query, timeout_sec=5.0)

        if handle:
          result = self.fetch(handle, rows=100)
          self.close(handle)

    return result


  def _get_sample_partition_query(self, database, table, column='*', limit=100, operation=None):
    max_parts = QUERY_PARTITIONS_LIMIT.get()
    partitions = self.get_partitions(database, table, partition_spec=None, max_parts=max_parts)

    if partitions and max_parts:
      # Need to reformat partition specs for where clause syntax
      partition_specs = [part.partition_spec.replace(',', ' AND ') for part in partitions]
      partition_filters = ' OR '.join(['(%s)' % partition_spec for partition_spec in partition_specs])
      partition_clause = 'WHERE %s' % partition_filters
    else:
      partition_clause = ''

    if operation == 'distinct':
      prefix = 'SELECT DISTINCT %s' % column
    elif operation == 'max':
      prefix = 'SELECT max(%s)' % column
    elif operation == 'min':
      prefix = 'SELECT min(%s)' % column
    else:
      prefix = 'SELECT %s' % column

    return prefix + " FROM `%(database)s`.`%(table)s` %(partition_clause)s LIMIT %(limit)s" % \
      {'database': database, 'table': table.name, 'partition_clause': partition_clause, 'limit': limit}


  def analyze_table(self, database, table):
    if self.server_name.startswith('impala'):
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
    if self.server_name.startswith('impala'):
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

    if self.server_name.startswith('impala'):
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
    if self.server_name.startswith('impala'):
      hql = 'SHOW COLUMN STATS `%(database)s`.`%(table)s`' % {'database': database, 'table': table}
    else:
      hql = 'DESCRIBE FORMATTED `%(database)s`.`%(table)s` `%(column)s`' % {'database': database, 'table': table, 'column': column}

    query = hql_query(hql)
    handle = self.execute_and_wait(query, timeout_sec=5.0)

    if handle:
      result = self.fetch(handle, rows=100)
      self.close(handle)
      data = list(result.rows())

      if self.server_name.startswith('impala'):
        if column == -1: # All the columns
          return [self._extract_impala_column(col) for col in data]
        else:
          data = [col for col in data if col[0] == column][0]
          return self._extract_impala_column(data)
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

  def _extract_impala_column(self, col):
    return [
        {'col_name': col[0]},
        {'data_type': col[1]},
        {'distinct_count': col[2]},
        {'num_nulls': col[3]},
        {'max_col_len': col[4]},
        {'avg_col_len': col[5]},
    ]

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

    hql = '''
      SELECT %(column)s, COUNT(*) AS ct
      FROM `%(database)s`.`%(table)s` %(prefix_match)s
      GROUP BY %(column)s
      ORDER BY ct DESC
      LIMIT %(limit)s''' % {
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


  def load_data(self, database, table, form_data, design, generate_ddl_only=False):
    hql = "LOAD DATA INPATH"
    source_path = "%(path)s" % form_data
    if source_path.lower().startswith("abfs"): #this is to check if its using an ABFS path
      source_path = abfspath(source_path)
    hql += " '%s'" % source_path
    if form_data['overwrite']:
      hql += " OVERWRITE"
    hql += " INTO TABLE "
    hql += "`%s`.`%s`" % (database, table)
    if form_data['partition_columns']:
      hql += " PARTITION ("
      vals = ["%s='%s'" % (column_name, column_value) for column_name, column_value in form_data['partition_columns']]
      hql += ", ".join(vals)
      hql += ")"

    if generate_ddl_only:
      return hql
    else:
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
      return query.hql_query
    else:
      design.data = query.dumps()
      design.save()

      return self.execute_query(query, design)


  def drop_database(self, database):
    return self.execute_statement("DROP DATABASE `%s`" % database)


  def drop_databases(self, databases, design, generate_ddl_only=False):
    hql = []

    for database in databases:
      hql.append("DROP DATABASE `%s` CASCADE" % database)
    query = hql_query(';'.join(hql), database)

    if generate_ddl_only:
      return query.hql_query
    else:
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
      except Exception as ex:
        query = hql_query('DROP TABLE `%s`' % target_table)
        try:
          self.execute_and_wait(query)
        except Exception as double_trouble:
          LOG.exception('Failed to drop table "%s" as well: %s' % (target_table, double_trouble))
        raise ex
      url = format_preserving_redirect(request, reverse('metastore:index'))

    return query_history


  def use(self, database, session=None):
    query = hql_query('USE `%s`' % database)
    return self.client.use(query, session=session)


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
    except Exception as e:
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

    query_history.last_state = QueryHistory.STATE.submitted.value
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
          last_state=QueryHistory.STATE.submitted.value,
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
    except QueryServerException as ex:
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

    LOG.debug(
      "Updated QueryHistory id %s user %s statement_number: %s" % (
        query_history.id, self.client.user, query_history.statement_number
      )
    )

    return query_history


  def get_results_metadata(self, handle):
    return self.client.get_results_metadata(handle)


  def close(self, handle):
    return self.client.close(handle)


  def get_partitions(self, db_name, table, partition_spec=None, max_parts=None, reverse_sort=True):
    if max_parts is None or max_parts > LIST_PARTITIONS_LIMIT.get():
      max_parts = LIST_PARTITIONS_LIMIT.get()

    return self.client.get_partitions(db_name, table.name, partition_spec, max_parts=max_parts, reverse_sort=reverse_sort)


  def get_partition(self, db_name, table_name, partition_spec, generate_ddl_only=False):
    if partition_spec and self.server_name.startswith('impala'): # partition_spec not supported
      partition_query = " AND ".join(partition_spec.split(','))
    else:
      table = self.get_table(db_name, table_name)
      partitions = self.get_partitions(db_name, table, partition_spec=partition_spec)

      if len(partitions) != 1:
        raise QueryServerException(_("Query did not return exactly one partition result: %s") % partitions)

      partition = partitions[0]
      partition_query = " AND ".join(partition.partition_spec.split(','))

    hql = "SELECT * FROM `%s`.`%s` WHERE %s" % (db_name, table_name, partition_query)

    if generate_ddl_only:
      return hql
    else:
      return self.execute_statement(hql)


  def describe_partition(self, db_name, table_name, partition_spec):
    return self.client.get_table(db_name, table_name, partition_spec=partition_spec)


  def drop_partitions(self, db_name, table_name, partition_specs, design=None, generate_ddl_only=False):
    hql = []

    for partition_spec in partition_specs:
      hql.append("ALTER TABLE `%s`.`%s` DROP IF EXISTS PARTITION (%s) PURGE" % (db_name, table_name, partition_spec))

    hql = ';'.join(hql)
    query = hql_query(hql, db_name)

    if generate_ddl_only:
      return hql
    else:
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


  def get_functions(self, prefix=None, database=None):
    '''
    Not using self.client.get_functions() as pretty limited. More comments there.
    '''
    result = None

    function_filter = "'%s*'" % prefix if prefix else ''

    if self.client.query_server['dialect'] == 'impala':
      if database is None:
        database = '_impala_builtins'

    hql = 'SHOW FUNCTIONS %(function_filter)s %(database_filter)s' % {
      'function_filter': "'%s*'" % prefix if prefix else '',
      'database_filter': (' IN %s' % database) if database else ''
    }

    query = hql_query(hql)
    handle = self.execute_and_wait(query, timeout_sec=5.0)

    if handle:
      rows = self.fetch(handle, rows=1000).rows()
      self.close(handle)

    return rows


  def get_function(self, name):
    hql = 'DESCRIBE FUNCTION EXTENDED `%(name)s`' % {
      'name': name,
    }

    query = hql_query(hql)
    handle = self.execute_and_wait(query, timeout_sec=5.0)

    if handle:
      rows = self.fetch(handle, rows=100).rows()
      self.close(handle)

    return rows


  def get_query_metadata(self, query):
    hql = 'SELECT * FROM ( %(query)s ) t LIMIT 0' % {'query': query.strip(';')}

    query = hql_query(hql)
    handle = self.execute_and_wait(query, timeout_sec=15.0)

    if handle:
      result = self.fetch(handle, rows=5000)
      self.close(handle)

    return result


  def explain(self, query):
    return self.client.explain(query)


  def get_primary_keys(self, database_name, table_name, catalog_name=None):

    return self.client.get_primary_keys(
      database_name=database_name,
      table_name=table_name,
      catalog_name=catalog_name
    )


  def get_foreign_keys(self, parent_catalog_name=None, parent_database_name=None, parent_table_name=None, foreign_catalog_name=None,
      foreign_database_name=None, foreign_table_name=None):

    return self.client.get_foreign_keys(
      parent_catalog_name=parent_catalog_name,
      parent_database_name=parent_database_name,
      parent_table_name=parent_table_name,
      foreign_catalog_name=foreign_catalog_name,
      foreign_database_name=foreign_database_name,
      foreign_table_name=foreign_table_name
    )


  def get_status(self):
    return self.client.getStatus()


  def get_default_configuration(self, include_hadoop):
    return self.client.get_default_configuration(include_hadoop)


class Table(object):
  """
  Represents the metadata of a Hive Table.
  """
  @property
  def hdfs_link(self):
    return location_to_url(self.path_location)


class DataTable(object):
  """
  Represents the data of a Hive Table.

  If the dataset has more rows, a new fetch should be done in order to return a new data table with the next rows.
  """
  pass


class SubQueryTable(object):

  def __init__(self, db, query):
    self.query = query
    # Table Properties
    self.name = 'Test'
    cols = db.get_query_metadata(query).data_table.cols()
    for col in cols:
      col.name = re.sub('^t\.', '', col.name)
      col.type = HiveFormat.FIELD_TYPE_TRANSLATE.get(col.type, 'string')
    self.cols = cols
    self.hdfs_link = None
    self.comment = None
    self.is_impala_only = False
    self.is_view = False
    self.partition_keys = []
    self.properties = {}


# TODO decorator?
def expand_exception(exc, db, handle=None):
  try:
    if handle is not None:
      log = db.get_log(handle)
    elif hasattr(exc, 'get_rpc_handle') or hasattr(exc, 'log_context'):
      log = db.get_log(exc)
    else:
      log = ''
  except Exception as e:
    # Always show something, even if server has died on the job.
    log = _("Could not retrieve logs: %s." % e)

  if not exc.args or not exc.args[0]:
    error_message = _("Unknown exception.")
  else:
    error_message = force_str(exc.args[0], strings_only=True, errors='replace')
  return error_message, log
