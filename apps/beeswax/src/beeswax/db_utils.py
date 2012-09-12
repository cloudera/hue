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

"""
Utils for interacting with Beeswaxd/Hive
"""

import logging
import thrift
import time

import hadoop.cluster

from beeswax import conf
from beeswax import models
from beeswax import hive_site
from beeswax.models import QueryHistory
from beeswaxd import BeeswaxService

from django.utils.encoding import smart_str, force_unicode
from desktop.lib import thrift_util
from hive_metastore import ThriftHiveMetastore
from beeswaxd.ttypes import BeeswaxException, QueryHandle, QueryNotFoundException

from django.utils.translation import ugettext_lazy as _

LOG = logging.getLogger(__name__)


def execute_directly(user, query_msg, query_server=None, design=None, notify=False):
  """
  execute_directly(user, query_msg [,design]) -> QueryHistory object

  This method also creates a QueryHistory object and saves it.
  user - Django user.
  query_msg - The thrift Query object.
  design - The SavedQuery object (i.e. design) associated with this query.
  notify - Whether to notify the user upon completion.
  """
  if query_server is None:
    query_server = get_query_server(support_ddl=True) # For convenience with DDL queries only

  query_history = QueryHistory(
                            owner=user,
                            query=query_msg.query,
                            server_host='%(server_host)s' % query_server,
                            server_port='%(server_port)d' % query_server,
                            server_name='%(server_name)s' % query_server,
                            last_state=QueryHistory.STATE.submitted.index,
                            design=design,
                            notify=notify)
  query_history.save()
  LOG.debug("Made new QueryHistory id %s user %s query: %s..." %
            (query_history.id, user, query_history.query[:25]))

  # Now submit it
  try:
    handle = db_client(query_server).query(query_msg)
    if not handle or not handle.id:
      # It really shouldn't happen
      msg = _("BeeswaxServer returning invalid handle for query id %(id)d [%(query)s]...") % \
            {'id': query_history.id, 'query': query_msg.query[:40]}
      raise Exception(msg)
  except BeeswaxException, bex:
    # Kind of expected (hql compile/syntax error, etc.)
    if bex.handle:
      query_history.server_id = bex.handle.id
      query_history.log_context = bex.handle.log_context
    query_history.save_state(QueryHistory.STATE.failed)
    raise bex
  except Exception, ex:
    LOG.exception(ex)
    query_history.save_state(QueryHistory.STATE.failed)
    raise ex

  # All good
  query_history.server_id = handle.id
  query_history.log_context = handle.log_context
  query_history.save_state(QueryHistory.STATE.running)
  return query_history


def wait_for_results(query_history, timeout_sec=30.0):
  """
  wait_for_results(query_history [,timeout_sec]) -> results or None

  timeout_sec: 0 to be non-blocking. Default to 30 seconds.
  Return the results when the query is completed, or None on timeout.
  May raise BeeswaxException.
  """
  SLEEP_INTERVAL = 0.5
  START_OVER = True

  handle = QueryHandle(id=query_history.server_id, log_context=query_history.log_context)

  curr = time.time()
  end = curr + timeout_sec
  while curr <= end:
    results = db_client(query_history.get_query_server()).fetch(handle, START_OVER, fetch_size=-1)
    if results.ready:
      return results
    time.sleep(SLEEP_INTERVAL)
    curr = time.time()
  return None


def execute_and_wait(user, query_msg, query_server=None, timeout_sec=30.0):
  """
  execute_and_wait(user, query_msg) -> results or None
  Combine execute_directly() and wait_for_results()
  May raise BeeswaxException
  """
  history = execute_directly(user, query_msg, query_server)
  result = wait_for_results(history, timeout_sec)
  return result


def get_query_state(query_history):
  """
  get_query_state(query_history) --> state enum

  Find out the *server* state of this query, and translate it to the *client* state.
  Expects to find the server_id from the ``query_history``.
  Return None on error. (It catches all anticipated exceptions.)
  """
  # First, we need the server handle
  ok, server_id = query_history.get_server_id()
  if not server_id:
    if not ok:
      return None
    return models.QueryHistory.STATE[query_history.last_state]

  # Now check the server state
  handle = QueryHandle(id=server_id, log_context=query_history.log_context)
  try:
    server_state = db_client(query_history.get_query_server()).get_state(handle)
    return models.QueryHistory.STATE_MAP[server_state]
  except QueryNotFoundException:
    LOG.debug("Query id %s has expired" % (query_history.id,))
    return models.QueryHistory.STATE.expired
  except thrift.transport.TTransport.TTransportException, ex:
    LOG.error("Failed to retrieve server state of submitted query id %s: %s" %
              (query_history.id, ex))
    return None


def get_query_server(name='default', support_ddl=False):
  if 'beeswax_server_host' in conf.QUERY_SERVERS['bind_to'] or 'beeswax_server_port' in conf.QUERY_SERVERS['bind_to']:
    return {
          'server_name': 'default',
          'server_host': conf.BEESWAX_SERVER_HOST.get(),
          'server_port': conf.BEESWAX_SERVER_PORT.get(),
          'support_ddl': True,
      }

  servers = conf.QUERY_SERVERS

  if support_ddl:
    if not servers[name].SUPPORT_DDL.get():
      for key in servers.keys():
        if servers[key].SUPPORT_DDL.get():
          name = key
          break

  config = servers[name]

  query_server = {
      'server_name': name,
      'server_host': config.SERVER_HOST.get(),
      'server_port': config.SERVER_PORT.get(),
      'support_ddl': config.SUPPORT_DDL.get(),
  }

  return query_server

#
# Note that thrift_util does client connection caching for us.
#
def db_client(query_server):
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
      no_start_over_support = [ config_variable for config_variable in self.get_default_configuration(False)
                                if config_variable.key == 'support_start_over' and config_variable.value == 'false' ]
      if no_start_over_support:
        copy = list(args)
        copy[1] = False
        args = copy

      res = self._client.fetch(*args, **kwargs)
      if res.ready:
        res.columns = [ force_unicode(col, errors='replace') for col in res.columns ]
        res.data = [ force_unicode(row, errors='replace') for row in res.data ]
      return res

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

  cluster_conf = hadoop.cluster.get_cluster_conf_for_job_submission()
  use_sasl = cluster_conf is not None and cluster_conf.SECURITY_ENABLED.get()

  client = thrift_util.get_client(BeeswaxService.Client,
                                  query_server['server_host'],
                                  query_server['server_port'],
                                  service_name=query_server['server_name'],
                                  kerberos_principal="hue",
                                  use_sasl=use_sasl,
                                  timeout_seconds=conf.BEESWAX_SERVER_CONN_TIMEOUT.get())
  return UnicodeBeeswaxClient(client)


def meta_client():
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

  _, host, port = hive_site.get_metastore()
  client = thrift_util.get_client(ThriftHiveMetastore.Client,
                                  host,
                                  port,
                                  service_name="Hive Metastore Server",
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
