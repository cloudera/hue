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

import sys

from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal, assert_raises
from django.urls import reverse

from desktop.api_public import get_django_request
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access

from useradmin.models import User

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock, MagicMock
else:
  from mock import patch, Mock, MagicMock


class TestEditorApi():

  def setUp(self):
    self.client = make_logged_in_client(username="api_user", recreate=True, is_superuser=False)
    self.client_not_me = make_logged_in_client(username="not_api_user", recreate=True, is_superuser=False)

    self.user = User.objects.get(username="api_user")
    self.user_not_me = User.objects.get(username="not_api_user")

    grant_access(self.user.username, self.user.username, "desktop")
    grant_access(self.user_not_me.username, self.user_not_me.username, "desktop")

  def test_urls_exist(self):
    assert_equal(reverse('api:editor_execute', args=['hive']), '/api/editor/execute/hive')


  def test_get_django_request(self):
    request = Mock()

    django_request = get_django_request(request)

    assert_true(
      hasattr(django_request.user, 'has_hue_permission')
    )
