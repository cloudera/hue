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


from nose.tools import assert_true, assert_equal


from zookeeper import stats
from zookeeper.conf import CLUSTERS
from zookeeper.views import _get_global_overview


class MockZooKeeperStats(object):

  def __init__(self, host, port):
    pass

  def get_stats(self):
    return {}



class ZooKeeperMockBase(object):

  def setUp(self):
    # Beware: Monkey patch ZooKeeper with Mock API
    if not hasattr(stats, 'OriginalZooKeeperApi'):
      stats.OriginalZooKeeperApi = stats.ZooKeeperStats

    stats.ZooKeeperStats = MockZooKeeperStats

  def tearDown(self):
    stats.ZooKeeperStats = stats.OriginalZooKeeperApi


class TestMockedZooKeeper(ZooKeeperMockBase):

  def test_get_global_overview(self):
    """Beware: this test is not testing, need to better mock the config."""
    finish = CLUSTERS.set_for_testing({'default': {'localhost:2181': {}}})

    try:
      _get_global_overview()

    finally:
      finish()

    finish = CLUSTERS.set_for_testing({'default': {'localhost:2181,localhost:2182': {}}})
    try:
      _get_global_overview()
    finally:
      finish()
