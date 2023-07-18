#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import json
import logging
import sys

from django.urls import reverse
from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true
import os

from desktop.auth.backend import rewrite_user
from desktop.lib.django_test_util import make_logged_in_client
from useradmin.models import User

from jobbrowser.apis.query_api import QueryApi
from jobbrowser.apis.query_api import _convert_to_6_digit_ms_local_time

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


LOG = logging.getLogger()

class TestConvertTo6DigitMsLocalTime():
  @patch.dict(os.environ, {'TZ': 'America/New_York'})
  def convert_6_digit(self):
    start_time = "2023-07-14 12:00:00.123456"
    converted_time = _convert_to_6_digit_ms_local_time(start_time)

    # America/New_York timezone is UTC-4
    expected_time = "2023-07-14 08:00:00.123456"

    assert_equal(expected_time, converted_time)

  @patch.dict(os.environ, {'TZ': 'America/New_York'})
  def convert_3_digit(self):
    start_time = "2023-07-14 12:00:00.123"
    converted_time = _convert_to_6_digit_ms_local_time(start_time)

    # America/New_York timezone is UTC-4
    expected_time = "2023-07-14 08:00:00.123000"

    assert_equal(expected_time, converted_time)
      
  @patch.dict(os.environ, {'TZ': 'America/New_York'})
  def convert_9_digit(self):
    start_time = "2023-07-14 12:00:00.123456789"
    converted_time = _convert_to_6_digit_ms_local_time(start_time)

    # America/New_York timezone is UTC-4
    expected_time = "2023-07-14 08:00:00.123456"

    assert_equal(expected_time, converted_time)

  @patch.dict(os.environ, {'TZ': 'America/New_York'})
  def convert_0_digit(self):
    start_time = "2023-07-14 12:00:00"
    converted_time = _convert_to_6_digit_ms_local_time(start_time)

    # America/New_York timezone is UTC-4
    expected_time = "2023-07-14 08:00:00.000000"

    assert_equal(expected_time, converted_time)    

class TestApi():

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = rewrite_user(User.objects.get(username="test"))


  def test_download_profile(self):
    with patch('jobbrowser.apis.query_api._get_api') as _get_api:
      with patch('jobbrowser.apis.query_api.QueryApi._query_profile') as _query_profile:
        _query_profile.return_value = {'profile': 'Query (id=d94d2fb4815a05c4:b1ccec1500000000):\n  Summary:...'}

        appid = '00001'
        app_type = Mock()
        app_filters = []

        resp = QueryApi(self.user).profile(appid, app_type, 'download-profile', app_filters)

        assert_equal(resp.status_code, 200)
        assert_equal(resp['Content-Disposition'], 'attachment; filename="query-profile_00001.txt"')
        assert_equal(resp.content, b'Query (id=d94d2fb4815a05c4:b1ccec1500000000):\n  Summary:...')
