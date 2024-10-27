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
import json
import unittest
from unittest.mock import Mock, patch

import pytest
from django.urls import reverse

from desktop.auth.backend import is_admin, rewrite_user
from desktop.conf import ENABLE_CONNECTORS, ENABLE_ORGANIZATIONS
from desktop.lib.connectors.api import _get_installed_connectors
from desktop.lib.django_test_util import make_logged_in_client
from useradmin.models import Connector, User, get_default_user_group, update_app_permissions
from useradmin.permissions import GroupPermission, HuePermission


@pytest.mark.django_db
class TestApi(object):

  def setup_method(self):
    self.client = make_logged_in_client(username="admin_test_connector", recreate=True, is_superuser=False, is_admin=True)
    self.user = User.objects.get(username="admin_test_connector")

  @classmethod
  def setup_class(cls):
    cls._class_resets = [
      ENABLE_CONNECTORS.set_for_testing(True),
    ]

  @classmethod
  def teardown_class(cls):
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

        assert 200 == response.status_code
        assert (
            'Added connectors: Connector 1. '
            'Already installed connectors: Connector 2' ==
            data['message']), data
