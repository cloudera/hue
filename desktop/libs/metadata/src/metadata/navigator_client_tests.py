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

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal

from hadoop.pseudo_hdfs4 import is_live_cluster

from metadata.conf import has_navigator
from metadata.navigator_client import NavigatorApi


LOG = logging.getLogger(__name__)


class MockedRoot():
  def get(self, relpath=None, params=None, headers=None, clear_cookies=False):
    return params


class TestNavigatorclient:

  @classmethod
  def setup_class(cls):
    if not is_live_cluster() or not has_navigator(): # Until v1
      raise SkipTest

  def test_search_entities(self):
    api = NavigatorApi()
    api._root = MockedRoot()

    assert_equal(
        '((originalName:*cases*)OR(originalDescription:*cases*)OR(name:*cases*)OR(description:*cases*)OR(tags:*cases*)) AND ((type:TABLE)OR(type:VIEW))',
        api.search_entities(query_s='cases', sources=['hive'])[0][1]
    )

    assert_equal(
        '* AND ((type:FIELD))',
        api.search_entities(query_s='type:FIELD', sources=['hive'])[0][1]
    )

    # type:
    # type:VIEW
    # type:VIEW ca
    # type:VIEW ca owner:hue
    # type:(VIEW OR TABLE)
    # type:(VIEW OR TABLE) ca
    # ca es
    # "ca es"
    # ca OR es
    # tags:a
