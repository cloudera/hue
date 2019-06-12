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
from desktop.conf import KERBEROS
from hive_metastore import ThriftHiveMetastore
from TCLIService.ttypes import TOperationState

from beeswax import hive_site
from beeswax.conf import SERVER_CONN_TIMEOUT
from beeswax.server.hive_server2_lib import ResultCompatible
from beeswax.models import HiveServerQueryHandle, QueryHistory
from beeswax.server.dbms import Table, DataTable


LOG = logging.getLogger(__name__)


class HiveTable(Table):

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


class HiveDataTable(DataTable):
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



class HiveMetastoreClient:

  def __init__(self, query_server, user):
    self.user = user
    self.query_server = query_server
    self.meta_client = self.meta_client()


  def get_databases(self, *args, **kwargs):
    return self.meta_client.get_all_databases()


  def get_tables(self, *args, **kwargs):
    return self.meta_client.get_tables(*args, **kwargs)


  def get_tables_meta(self, *args, **kwargs):
    meta_tables = self.meta_client.get_table_meta(*args, **kwargs)
    return [
      {'name': table.tableName, 'type': table.tableType, 'comment': table.comments, 'database': table.dbName}
      for table in meta_tables
    ]

  def get_table(self, *args, **kwargs):
    meta_table = self.meta_client.get_table(*args, **kwargs)

    table = HiveTable(meta_table)
    setattr(table, 'details', {'properties': {'table_type': meta_table.tableType}, 'stats': {'val': 1}})
    setattr(table, 'properties', [])
    setattr(table, 'stats', [{'val': 1}])
    setattr(table, 'is_impala_only', False)

    return table


  def get_partitions(self, db_name, tbl_name, max_parts):
    if max_parts is None:
      max_parts = -1
    return self.meta_client.get_partitions(db_name, tbl_name, max_parts)


  def use(self, query):
    pass


  def query(self, query, statement=0, with_multiple_session=False):
    return HiveServerQueryHandle(secret='mock', guid='mock')


  def get_state(self, handle):
    return QueryHistory.STATE.available


  def close(self, handle):
    pass


  def get_operation_status(self, handle):
    return MockFinishedOperation()


  def get_default_configuration(self, *args, **kwargs):
    return []


  def fetch(self, handle, start_over=False, max_rows=None):
    return EmptyResultCompatible()


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

    use_sasl, kerberos_principal_short_name = HiveMetastoreClient.get_security() # TODO Reuse from HiveServer2 lib

    client = thrift_util.get_client(
        ThriftHiveMetastore.Client,
        host=self.query_server['server_host'],
        port=self.query_server['server_port'],
        service_name="Hive Metastore Server",
        kerberos_principal=kerberos_principal_short_name,
        use_sasl=use_sasl,
        timeout_seconds=SERVER_CONN_TIMEOUT.get()
    )
    return UnicodeMetastoreClient(client)


class EmptyResultCompatible:
  def __init__(self):
    self.data_table = type('Col', (object,), {'cols': self.cols})
    self.rows = lambda: []
    self.has_more = False
    self.ready = True

  @property
  def columns(self):
    return self.cols()

  def cols(self):
    return []

  def full_cols(self):
    return []


class MockFinishedOperation():
  def __init__(self):
    self.operationState = TOperationState.FINISHED_STATE


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
