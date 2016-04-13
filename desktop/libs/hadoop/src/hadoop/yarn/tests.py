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

from nose.tools import assert_true, assert_equal, assert_not_equal

from hadoop.yarn import clients


LOG = logging.getLogger(__name__)


def test_get_log_client():
  old_max_heap_size = clients.MAX_HEAP_SIZE
  clients.MAX_HEAP_SIZE = 2
  try:
    log_link1 = "http://test1:8041/container/nonsense"
    log_link2 = "http://test2:8041/container/nonsense"
    log_link3 = "http://test3:8041/container/nonsense"

    c1 = clients.get_log_client(log_link1)
    c2 = clients.get_log_client(log_link2)

    assert_not_equal(c1, c2)
    assert_equal(c1, clients.get_log_client(log_link1))

    clients.get_log_client(log_link3)

    assert_equal(2, len(clients._log_client_heap))
    base_urls = [tup[1].base_url for tup in clients._log_client_heap]
    assert_true('http://test1:8041' in base_urls)
    assert_true('http://test3:8041' in base_urls)
  finally:
    clients.MAX_HEAP_SIZE = old_max_heap_size
