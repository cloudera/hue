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
from __future__ import absolute_import

import logging
import unittest

from azure.abfs.abfs import ABFS
from azure.active_directory import ActiveDirectory
from azure.conf import ABFS_CLUSTERS, is_abfs_enabled

from nose.plugins.skip import SkipTest

LOG = logging.getLogger(__name__)

"""
Interfaces for ADLS via HttpFs/WebHDFS
"""
class ABFSTestBase(unittest.TestCase):
  integration = True

  def setUp(self):
    if not is_abfs_enabled():
      raise SkipTest
    self.client = ABFS.from_config(ABFS_CLUSTERS['default'], ActiveDirectory.from_config(None, version='v2.0'))

  def tearDown(self):
    pass

  def test_list(self):
    self.client.listdir('abfs://')
    pass