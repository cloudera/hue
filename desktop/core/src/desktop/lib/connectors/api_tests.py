#!/usr/bin/env python
## -*- coding: utf-8 -*-
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
import sys
import unittest

from django.urls import reverse
from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true, assert_false

from desktop.auth.backend import rewrite_user, is_admin
from desktop.conf import ENABLE_CONNECTORS, ENABLE_ORGANIZATIONS
from desktop.lib.connectors.api import _get_installed_connectors
from desktop.lib.django_test_util import make_logged_in_client

from useradmin.models import User, update_app_permissions, get_default_user_group, Connector
from useradmin.permissions import HuePermission, GroupPermission

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


class TestApi(object):

  def setUp(self):
    self.client = make_logged_in_client(username="admin_test_connector", recreate=True, is_superuser=False, is_admin=True)
    self.user = User.objects.get(username="admin_test_connector")

  @classmethod
  def setUpClass(cls):
    cls._class_resets = [
      ENABLE_CONNECTORS.set_for_testing(True),
    ]

  @classmethod
  def tearDownClass(cls):
    for reset in cls._class_resets:
      reset()


  def test_install_connector_examples(self):

    with patch('desktop.lib.connectors.api._create_connector_examples') as _create_connector_examples:
      with patch('desktop.lib.connectors.api.update_app_permissions') as update_app_permissions:
        _create_connector_examples.return_value = ['Connector 1'], ['Connector 2']

        response = self.client.post(
          reverse('connectors.api.install_connector_examples')
        )
        data = json.loads(response.content)

        assert_equal(200, response.status_code)
        assert_equal(
            'Added connectors: Connector 1. '
            'Already installed connectors: Connector 2',
            data['message'],
            data
        )
