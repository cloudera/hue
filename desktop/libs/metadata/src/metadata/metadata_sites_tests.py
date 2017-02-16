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
import os
import shutil
import tempfile

from nose.tools import assert_equal

import metadata_sites
from metadata.conf import NAVIGATOR
from metadata.metadata_sites import get_navigator_server_url

LOG = logging.getLogger(__name__)


class TestReadConfiguration:

  def test_navigator_site(self):
    tmpdir = tempfile.mkdtemp()
    resets = [
        NAVIGATOR.CONF_DIR.set_for_testing(tmpdir)
    ]

    try:
      file(os.path.join(tmpdir, 'navigator.lineage.client.properties'), 'w').write("""
navigator.client.serviceType=HUE
navigator.server.url=http://hue-rocks.com:7187
navigator.client.roleName=HUE-1-HUE_SERVER-50cf99601c4bf64e9ccded4c8cd96d12
navigator.client.roleType=HUE_SERVER
audit_event_log_dir=/var/log/hue/audit
navigator.audit_log_max_file_size=100
      """)

      metadata_sites.reset()

      assert_equal(get_navigator_server_url(), 'http://hue-rocks.com:7187')
    finally:
      metadata_sites.reset()
      for reset in resets:
        reset()
      shutil.rmtree(tmpdir)


  def test_missing_navigator_site(self):
    tmpdir = tempfile.mkdtemp()
    shutil.rmtree(tmpdir)

    resets = [
        NAVIGATOR.CONF_DIR.set_for_testing(tmpdir)
    ]

    try:
      metadata_sites.reset()

      assert_equal(get_navigator_server_url(), 'http://localhost:7187')
    finally:
      metadata_sites.reset()
      for reset in resets:
        reset()
