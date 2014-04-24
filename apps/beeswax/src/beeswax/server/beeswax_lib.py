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
import re
import thrift

from django.utils.encoding import smart_str, force_unicode
from django.utils.translation import ugettext as _

import hadoop.cluster

from desktop.lib import thrift_util
from hive_metastore import ThriftHiveMetastore
from desktop.conf import KERBEROS
from beeswaxd import BeeswaxService
from beeswaxd.ttypes import QueryNotFoundException

from beeswax import conf
from beeswax import models
from beeswax import hive_site
from beeswax.models import BeeswaxQueryHandle
from beeswax.server.dbms import Table, DataTable

LOG = logging.getLogger(__name__)


class BeeswaxTable(Table):

  def __init__(self, table_obj):
    self.table_obj = table_obj

  @property
  def name(self):
    return self.table_obj.tableName

  @property
  def is_view(self):
    return self.table_obj.tableType == 'VIRTUAL_VIEW'

  @property
  def partition_keys(self):
    return self.table_obj.partitionKeys

  @property
  def path_location(self):
    return self.table_obj.sd.location

  @property
  def parameters(self):
    return self.table_obj.parameters

  @property
  def cols(self):
    return self.table_obj.sd.cols

  @property
  def comment(self):
    return self.table_obj.parameters.get('comment')


class BeeswaxDataTable(DataTable):
  def __init__(self, results):
    self.results = results
    self.has_more = results.has_more
    self.startRowOffset = results.start_row
    self.columns = results.columns

  @property
  def ready(self):
    return self.results.ready

  def cols(self):
    return self.results.columns

  def rows(self):
    """
    Results come back tab-delimited, and this splits
    them back up into reasonable things.
    """
    def parse_result_row(row):
      return row.split("\t")

    for row in self.results.data:
      yield parse_result_row(row)



class BeeswaxClient:
  NO_RESULT_SET_RE = re.compile('DROP|CREATE|ALTER|LOAD|USE', re.IGNORECASE)

  def __init__(self, query_server, user):
    self.user = user
    self.query_server = query_server
    self.db_client = self.db_client(query_server)
    self.meta_client = self.meta_client()

  def make_query(self, hql_query, statement=0):
    # HUE-535 without having to modify Beeswaxd, add 'use database' as first option
    if self.query_server['server_name'] == 'impala':
      configuration = [','.join(['%(key)s=%(value)s' % setting for setting in hql_query.settings])]
    else:
      configuration = ['use ' + hql_query.query.get('database', 'default')]
      configuration.extend(hql_query.get_configuration())

    query_statement = hql_query.get_query_statement(statement)
    thrift_query = BeeswaxService.Query(query=query_statement, configuration=configuration)
    thrift_query.hadoop_user = self.user.username
    return thrift_query


  def get_databases(self, *args, **kwargs):
    if self.query_server['server_name'] == 'impala':
      return ['default']
    else:
      return self.meta_client.get_all_databases()


  def get_tables(self, *args, **kwargs):
    return self.meta_client.get_tables(*args, **kwargs)


  def get_table(self, *args, **kwargs):
    table = self.meta_client.get_table(*args, **kwargs)
    return BeeswaxTable(table)


  def query(self, query, statement=0):
    thrift_query = self.make_query(query, statement)
    handle = self.db_client.query(thrift_query)
    # Fake has_result_set
    has_result_set = not BeeswaxClient.NO_RESULT_SET_RE.match(thrift_query.query) is not None
    return BeeswaxQueryHandle(secret=handle.id, has_result_set=has_result_set, log_context=handle.log_context)


  def fetch(self, handle, start_over=True, rows=-1):
    if rows is None:
      rows = -1

    rpc_handle = handle.get_rpc_handle()
    results = self.db_client.fetch(rpc_handle, start_over, rows)

    if results.ready:
      # Impala does not return the name of the columns, need to fetch separately
      if self.query_server['server_name'] == 'impala':
        results.columns = [column.name for column in self.get_results_metadata(handle).schema.fieldSchemas]
      return BeeswaxDataTable(results)


  def cancel_operation(self, handle):
    raise Exception(_('Query cancelation is not supported by the Beeswax interface. Please use the Hive Server 2 interface instead.'))


  def get_log(self, handle):
    return self.db_client.get_log(handle.log_context)


  def get_state(self, handle):
    return self.db_client.get_state(handle)


  def get_results_metadata(self, handle):
    handle = handle.get_rpc_handle()
    return self.db_client.get_results_metadata(handle)


  def close_operation(self, handle):
    handle = handle.get_rpc_handle()
    
    self.db_client.close(handle)
    self.db_client.clean(handle.log_context)


  def get_partitions(self, db_name, tbl_name, max_parts):
    if max_parts is None:
      max_parts = -1
    return self.meta_client.get_partitions(db_name, tbl_name, max_parts)


  def explain(self, statement):
    thrift_query = self.make_query(statement)
    return self.db_client.explain(thrift_query)


  def echo(self, text):
    return self.db_client.echo(text)


  def getStatus(self):
    return self.meta_client.getStatus()


  def get_default_configuration(self, *args, **kwargs):
    return self.db_client.get_default_configuration(*args, **kwargs)

  @classmethod
  def get_security(cls, query_server=None):
    cluster_conf = hadoop.cluster.get_cluster_conf_for_job_submission()
    use_sasl = cluster_conf is not None and cluster_conf.SECURITY_ENABLED.get()

    if query_server is not None:
      principal = query_server['principal']
    else:
      principal = KERBEROS.HUE_PRINCIPAL.get()

    # We should integrate hive_site.get_metastore() here in the future
    if principal:
      kerberos_principal_short_name = principal.split('/', 1)[0]
    else:
      kerberos_principal_short_name = None

    return use_sasl, kerberos_principal_short_name

  def db_client(self, query_server):
    """Get the Thrift client to talk to beeswax server"""

    class UnicodeBeeswaxClient(object):
      """Wrap the thrift client to take and return Unicode"""
      def __init__(self, client):
        self._client = client

      def __getattr__(self, attr):
        if attr in self.__dict__:
          return self.__dict__[attr]
        return getattr(self._client, attr)

      def query(self, query):
        _encode_struct_attr(query, 'query')
        return self._client.query(query)

      def explain(self, query):
        _encode_struct_attr(query, 'query')
        res = self._client.explain(query)
        return _decode_struct_attr(res, 'textual')

      def fetch(self, *args, **kwargs):
        res = self._client.fetch(*args, **kwargs)
        if res.ready:
          res.columns = [ force_unicode(col, errors='replace') for col in res.columns ]
          res.data = [ force_unicode(row, errors='replace') for row in res.data ]
        return res

      def get_state(self, handle):
        """
        get_query_state(query_history) --> state enum

        Find out the *server* state of this query, and translate it to the *client* state.
        Expects to find the server_id from the ``query_history``.
        Return None on error. (It catches all anticipated exceptions.)
        """
        rpc_handle = handle.get_rpc_handle()

        try:
          rpc_state = self._client.get_state(rpc_handle)
          return models.BeeswaxQueryHistory.STATE_MAP[rpc_state]
        except QueryNotFoundException:
          LOG.debug("Query id %s has expired" % (handle.secret,))
          return models.QueryHistory.STATE.expired
        except thrift.transport.TTransport.TTransportException, ex:
          LOG.error("Failed to retrieve server state of submitted query id %s: %s" % (handle.secret, ex)) # queryhistory.id
          return None


      def dump_config(self):
        res = self._client.dump_config()
        return force_unicode(res, errors='replace')

      def echo(self, msg):
        return self._client.echo(smart_str(msg))

      def get_log(self, *args, **kwargs):
        res = self._client.get_log(*args, **kwargs)
        return force_unicode(res, errors='replace')

      def get_default_configuration(self, *args, **kwargs):
        config_list = self._client.get_default_configuration(*args, **kwargs)
        for config in config_list:
          _decode_struct_attr(config, 'key')
          _decode_struct_attr(config, 'value')
          _decode_struct_attr(config, 'desc')
        return config_list

      def get_results_metadata(self, *args, **kwargs):
        res = self._client.get_results_metadata(*args, **kwargs)
        return _decode_struct_attr(res, 'table_dir')

    use_sasl, kerberos_principal_short_name = BeeswaxClient.get_security(query_server)

    client = thrift_util.get_client(BeeswaxService.Client,
                                    query_server['server_host'],
                                    query_server['server_port'],
                                    service_name=query_server['server_name'],
                                    kerberos_principal=kerberos_principal_short_name,
                                    use_sasl=use_sasl,
                                    timeout_seconds=conf.BEESWAX_SERVER_CONN_TIMEOUT.get())
    return UnicodeBeeswaxClient(client)


  def meta_client(self):
    """Get the Thrift client to talk to the metastore"""

    class UnicodeMetastoreClient(object):
      """Wrap the thrift client to take and return Unicode."""
      def __init__(self, client):
        self._client = client

      def __getattr__(self, attr):
        if attr in self.__dict__:
          return self.__dict__[attr]
        return getattr(self._client, attr)

      def _encode_storage_descriptor(self, sd):
        _encode_struct_attr(sd, 'location')
        for col in sd.cols:
          _encode_struct_attr(col, 'comment')
        self._encode_map(sd.parameters)

      def _decode_storage_descriptor(self, sd):
        _decode_struct_attr(sd, 'location')
        for col in sd.cols:
          _decode_struct_attr(col, 'comment')
        self._decode_map(sd.parameters)

      def _encode_map(self, mapp):
        for key, value in mapp.iteritems():
          mapp[key] = smart_str(value, strings_only=True)

      def _decode_map(self, mapp):
        for key, value in mapp.iteritems():
          mapp[key] = force_unicode(value, strings_only=True, errors='replace')

      def create_database(self, name, description):
        description = smart_str(description)
        return self._client.create_database(name, description)

      def get_database(self, *args, **kwargs):
        db = self._client.get_database(*args, **kwargs)
        return _decode_struct_attr(db, 'description')

      def get_fields(self, *args, **kwargs):
        res = self._client.get_fields(*args, **kwargs)
        for fschema in res:
          _decode_struct_attr(fschema, 'comment')
        return res

      def get_table(self, *args, **kwargs):
        res = self._client.get_table(*args, **kwargs)
        self._decode_storage_descriptor(res.sd)
        self._decode_map(res.parameters)
        return res

      def alter_table(self, dbname, tbl_name, new_tbl):
        self._encode_storage_descriptor(new_tbl.sd)
        self._encode_map(new_tbl.parameters)
        return self._client.alter_table(dbname, tbl_name, new_tbl)

      def _encode_partition(self, part):
        self._encode_storage_descriptor(part.sd)
        self._encode_map(part.parameters)
        return part

      def _decode_partition(self, part):
        self._decode_storage_descriptor(part.sd)
        self._decode_map(part.parameters)
        return part

      def add_partition(self, new_part):
        self._encode_partition(new_part)
        part = self._client.add_partition(new_part)
        return self._decode_partition(part)

      def get_partition(self, *args, **kwargs):
        part = self._client.get_partition(*args, **kwargs)
        return self._decode_partition(part)

      def get_partitions(self, *args, **kwargs):
        part_list = self._client.get_partitions(*args, **kwargs)
        for part in part_list:
          self._decode_partition(part)
        return part_list

      def alter_partition(self, db_name, tbl_name, new_part):
        self._encode_partition(new_part)
        return self._client.alter_partition(db_name, tbl_name, new_part)

    # Use service name from kerberos principal set in hive-site.xml
    _, host, port, metastore_kerberos_principal = hive_site.get_metastore()
    use_sasl, kerberos_principal_short_name = BeeswaxClient.get_security()
    kerberos_principal_short_name = metastore_kerberos_principal and metastore_kerberos_principal.split('/', 1)[0] or None
    client = thrift_util.get_client(ThriftHiveMetastore.Client,
                                    host,
                                    port,
                                    service_name="Hive Metastore Server",
                                    kerberos_principal=kerberos_principal_short_name,
                                    use_sasl=use_sasl,
                                    timeout_seconds=conf.METASTORE_CONN_TIMEOUT.get())
    return UnicodeMetastoreClient(client)


def _decode_struct_attr(struct, attr):
  try:
    val = getattr(struct, attr)
  except AttributeError:
    return struct
  unival = force_unicode(val, strings_only=True, errors='replace')
  setattr(struct, attr, unival)
  return struct


def _encode_struct_attr(struct, attr):
  try:
    unival = getattr(struct, attr)
  except AttributeError:
    return struct
  val = smart_str(unival, strings_only=True)
  setattr(struct, attr, val)
  return struct

