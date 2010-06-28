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

from beeswax import conf
from beeswax import models
from beeswax.models import QueryHistory
from beeswaxd import BeeswaxService

from desktop.lib import thrift_util
from hive_metastore import ThriftHiveMetastore
from beeswaxd.ttypes import BeeswaxException, QueryHandle, QueryNotFoundException

LOG = logging.getLogger(__name__)

# Timeouts in seconds for thrift calls to beeswax service and the
# hive metastore. The metastore could talk to an external DB, hence
# the larger timeout.
BEESWAX_SERVER_THRIFT_TIMEOUT = 10
METASTORE_THRIFT_TIMEOUT = 10

def execute_directly(user, query_msg, design=None, notify=False):
  """
  execute_directly(user, query_msg [,design]) -> QueryHistory object

  This method also creates a QueryHistory object and saves it.
  user - Django user.
  query_msg - The thrift Query object.
  design - The SavedQuery object (i.e. design) associated with this query.
  notify - Whether to notify the user upon completion.
  """
  query_history = QueryHistory(
                            owner=user,
                            query=query_msg.query,
                            last_state=QueryHistory.STATE.submitted.index,
                            design=design,
                            notify=notify)
  query_history.save()
  LOG.debug("Made new QueryHistory id %s user %s query: %s..." %
            (query_history.id, user, query_history.query[:25]))

  # Now submit it
  try:
    handle = db_client().query(query_msg)
    if not handle or not handle.id or not handle.log_context:
      # It really shouldn't happen
      msg = "BeeswaxServer returning invalid handle for query id %d [%s]..." % \
            (query_history.id, query_msg.query[:40])
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
    results = db_client().fetch(handle, START_OVER)
    if results.ready:
      return results
    time.sleep(SLEEP_INTERVAL)
    curr = time.time()
  return None


def execute_and_wait(user, query_msg, timeout_sec=30.0):
  """
  execute_and_wait(user, query_msg) -> results or None
  Combine execute_directly() and wait_for_results()
  May raise BeeswaxException
  """
  history = execute_directly(user, query_msg)
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
    server_state = db_client().get_state(handle)
    return models.QueryHistory.STATE_MAP[server_state]
  except QueryNotFoundException:
    LOG.debug("Query id %s has expired" % (query_history.id,))
    return models.QueryHistory.STATE.expired
  except thrift.transport.TTransport.TTransportException, ex:
    LOG.error("Failed to retrieve server state of submitted query id %s: %s" %
              (query_history.id, ex))
    return None

#
# Note that thrift_util does client connection caching for us.
#
def db_client():
  return thrift_util.get_client(BeeswaxService.Client,
                                conf.BEESWAX_SERVER_HOST.get(),
                                conf.BEESWAX_SERVER_PORT.get(),
                                service_name="Beeswax (Hive UI) Server",
                                timeout_seconds=BEESWAX_SERVER_THRIFT_TIMEOUT)

def meta_client():
  return thrift_util.get_client(ThriftHiveMetastore.Client,
                                conf.BEESWAX_META_SERVER_HOST.get(),
                                conf.BEESWAX_META_SERVER_PORT.get(),
                                service_name="Hive Metadata (Hive UI) Server",
                                timeout_seconds=METASTORE_THRIFT_TIMEOUT)
