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
import urlparse
import heapq

from desktop.lib.rest.http_client import HttpClient

from hadoop import cluster


LOG = logging.getLogger(__name__)

MAX_HEAP_SIZE = 20

_log_client_heap = []
_log_client_lock = threading.Lock()


def get_log_client(log_link):
  global _log_client_queue
  global MAX_HEAP_SIZE

  _log_client_lock.acquire()

  try:
    components = urlparse.urlsplit(log_link)
    base_url = '%(scheme)s://%(netloc)s' % {
      'scheme': components[0],
      'netloc': components[1]
    }

    # Takes on form (epoch time, client object)
    # Least Recently Used algorithm.
    client_tuple = next((tup for tup in _log_client_heap if tup[1].base_url == base_url), None)
    if client_tuple is None:
      client = HttpClient(base_url, logger=LOG)
      yarn_cluster = cluster.get_cluster_conf_for_job_submission()
      if yarn_cluster.SECURITY_ENABLED.get():
        client.set_kerberos_auth()
    else:
      _log_client_heap.remove(client_tuple)
      client = client_tuple[1]

    new_client_tuple = (time.time(), client)
    if len(_log_client_heap) >= MAX_HEAP_SIZE:
      heapq.heapreplace(_log_client_heap, new_client_tuple)
    else:
      heapq.heappush(_log_client_heap, new_client_tuple)

    return client
  finally:
    _log_client_lock.release()
