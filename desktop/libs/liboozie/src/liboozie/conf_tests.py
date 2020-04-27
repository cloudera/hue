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

import sys

from nose.tools import assert_true, assert_false, assert_equal

from useradmin.models import User
from desktop.lib.django_test_util import make_logged_in_client

from liboozie.conf import config_validator


if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


class TestGetConfigErrors():

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="empty", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")

  def test_check_config_oozie_disabled(self):
    with patch('liboozie.conf.appmanager') as appmanager:
      with patch('liboozie.conf.OOZIE_URL.get') as OOZIE_URL_get:
        appmanager.get_apps_dict.return_value = []  # No oozie app but Oozie URL specified.
        OOZIE_URL_get.return_value = 'http://localhost:11000/oozie'

        assert_equal(
          [],
          config_validator(self.user)
        )
