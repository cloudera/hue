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
import pytest
import unittest
from django.test import TestCase
from desktop.conf import is_gs_enabled
from desktop.lib.fsmanager import get_client

LOG = logging.getLogger()


class TestGCS(TestCase):
  def setup_method(self, method):
    if not is_gs_enabled():
      pytest.skip('gs not enabled')

  def test_with_credentials(self):
    # Simple test that makes sure no errors are thrown.
    client = get_client(fs='gs')
    buckets = client.listdir_stats('gs://')
    LOG.info(len(buckets))
