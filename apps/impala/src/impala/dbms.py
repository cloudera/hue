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

from desktop.conf import CLUSTER_ID, has_connectors
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_str
from desktop.models import Cluster
from beeswax.design import hql_query
from beeswax.models import QUERY_TYPES
from beeswax.server import dbms
from beeswax.server.dbms import HiveServer2Dbms, QueryServerException, QueryServerTimeoutException, \
  get_query_server_config as beeswax_query_server_config, get_query_server_config_via_connector

from impala import conf
from impala.impala_flags import get_hs2_http_port

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger()


def get_query_server_config(connector=None):
  if connector and has_connectors():
    query_server = get_query_server_config_via_connector(connector)
  else:
    server_port = get_hs2_http_port() if conf.USE_THRIFT_HTTP.get() and not conf.PROXY_ENDPOINT.get() else conf.SERVER_PORT.get()
    query_server = {
        'server_name': 'impala',
        'dialect': 'impala',
        'server_host': conf.SERVER_HOST.get(),
        'server_port': server_port,
        'principal': conf.IMPALA_PRINCIPAL.get(),
        'http_url': '%(protocol)s://%(host)s:%(port)s%(cli_endpoint)s' % {
            'protocol': 'https' if conf.SSL.ENABLED.get() else 'http',
            'host': conf.SERVER_HOST.get(),
            'port': server_port,
            'cli_endpoint': conf.PROXY_ENDPOINT.get()
          },
        'impersonation_enabled': conf.IMPERSONATION_ENABLED.get(),
        'querycache_rows': conf.QUERYCACHE_ROWS.get(),
        'QUERY_TIMEOUT_S': conf.QUERY_TIMEOUT_S.get(),
        'SESSION_TIMEOUT_S': conf.SESSION_TIMEOUT_S.get(),
        'auth_username': conf.AUTH_USERNAME.get(),
        'auth_password': conf.AUTH_PASSWORD.get(),
        'use_sasl': conf.USE_SASL.get(),
        'transport_mode': 'http' if conf.USE_THRIFT_HTTP.get() else 'socket',
    }

  debug_query_server = query_server.copy()
  debug_query_server['auth_password_used'] = bool(debug_query_server.pop('auth_password'))
  LOG.debug("Query Server: %s" % debug_query_server)

  return query_server


class ImpalaDbms(HiveServer2Dbms):

  @classmethod
  def get_nested_select(cls, database, table, column, nested=None):
    """
    Given a column or nested type, return the corresponding SELECT and FROM clauses in Impala's nested-type syntax
    """
    select_tokens = [column]
    from_tokens = [database, table]

    if nested:
      nested_tokens = nested.strip('/').split('/')
      while nested_tokens:
        token = nested_tokens.pop(0)
        if token not in ['key', 'value', 'item']:
          select_tokens.append(token)
        else:
          # if we encounter a reserved keyword, move current select_tokens to from_tokens and reset the select_tokens
          from_tokens.extend(select_tokens)
          select_tokens = []
          # if reserved keyword is the last token, make it the only select_token, otherwise we ignore and continue
          if not nested_tokens:
            select_tokens = [token]

    select_clause = '.'.join(select_tokens)
    from_clause = '.'.join('`%s`' % token.strip('`') for token in from_tokens)
    return select_clause, from_clause


  @classmethod
  def get_histogram_query(cls, database, table, column, nested=None):
    select_clause, from_clause = cls.get_nested_select(database, table, column, nested)
    return 'SELECT histogram(%s) FROM %s' % (select_clause, from_clause)


  # Deprecated
  def invalidate(self, database=None, table=None, flush_all=False):
    handle = None

    try:
      if flush_all or database is None:
        hql = "INVALIDATE METADATA"
        query = hql_query(hql, query_type=QUERY_TYPES[1])
        handle = self.execute_and_wait(query, timeout_sec=10.0)
      elif table is None:
        if not Cluster(self.client.user).get_app_config().get_hive_metastore_interpreters():
          raise PopupException(_("Hive and HMS not configured. Please do a full refresh"))
        diff_tables = self._get_different_tables(database)
        if len(diff_tables) > 10:
          raise PopupException(_("Too many tables (%d) to invalidate. Please do a full refresh") % len(diff_tables))
        else:
          for table in diff_tables:
            hql = "INVALIDATE METADATA `%s`.`%s`" % (database, table)
            query = hql_query(hql, query_type=QUERY_TYPES[1])
            handle = self.execute_and_wait(query, timeout_sec=10.0)
      else:
        hql = "INVALIDATE METADATA `%s`.`%s`" % (database, table)
        query = hql_query(hql, query_type=QUERY_TYPES[1])
        handle = self.execute_and_wait(query, timeout_sec=10.0)
    except QueryServerTimeoutException as e:
      # Allow timeout exceptions to propagate
      raise e
    except PopupException as e:
      raise e
    except Exception as e:
      msg = 'Failed to invalidate `%s`: %s' % (database or 'databases', e)
      raise QueryServerException(msg)
    finally:
      if handle:
        self.close(handle)


  def refresh_table(self, database, table):
    handle = None
    try:
      hql = "REFRESH `%s`.`%s`" % (database, table)
      query = hql_query(hql, database, query_type=QUERY_TYPES[1])
      handle = self.execute_and_wait(query, timeout_sec=10.0)
    except Exception as e:
      msg = 'Failed to refresh `%s`.`%s`' % (database, table)
      raise QueryServerException(msg)
    finally:
      if handle:
        self.close(handle)


  def get_histogram(self, database, table, column, nested=None):
    """
    Returns the results of an Impala SELECT histogram() FROM query for a given column or nested type.

    Assumes that the column/nested type is scalar.
    """
    results = []

    hql = self.get_histogram_query(database, table, column, nested)
    query = hql_query(hql)
    handle = self.execute_and_wait(query, timeout_sec=5.0)

    if handle:
      result = self.fetch(handle)
      try:
        histogram = list(result.rows())[0][0]  # actual histogram results is in first-and-only result row
        unique_values = set(histogram.split(', '))
        results = list(unique_values)
      except IndexError as e:
        LOG.warning('Failed to get histogram results, result set has unexpected format: %s' % smart_str(e))
      finally:
        self.close(handle)

    return results


  def get_exec_summary(self, query_handle, session_handle):
    return self.client._client.get_exec_summary(query_handle, session_handle)


  def get_runtime_profile(self, query_handle, session_handle):
    return self.client._client.get_runtime_profile(query_handle, session_handle)


  def _get_beeswax_tables(self, database):
    beeswax_query_server = dbms.get(
      user=self.client.user,
      query_server=beeswax_query_server_config(
        name=Cluster(self.client.user).get_app_config().get_hive_metastore_interpreters()[0]
      )
    )
    return beeswax_query_server.get_tables(database=database)


  def _get_different_tables(self, database):
    beeswax_tables = self._get_beeswax_tables(database)
    impala_tables = self.get_tables(database=database)
    return set(beeswax_tables).symmetric_difference(impala_tables)
