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

from nose.tools import assert_true, assert_equal, assert_false

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access

from django.contrib.auth.models import User, Group
from django.urls import reverse

from useradmin.models import HuePermission, GroupPermission

from security.api.hive import _to_sentry_privilege


class TestSecurity():

  def test_permissions(self):
    client = make_logged_in_client(username='test_permissions', groupname='test_permissions', is_superuser=False)
    grant_access("test_permissions", "test_permissions", "security")
    user = User.objects.get(username='test_permissions')

    def check(client, assertz):
      response = client.get(reverse("security:hive"))
      assertz("Impersonate the user" in response.content, response.content)

    # Forbidden
    check(client, assert_false)

    # Allowed
    group, created = Group.objects.get_or_create(name='test_permissions')
    perm, created = HuePermission.objects.get_or_create(app='security', action='impersonate')
    GroupPermission.objects.get_or_create(group=group, hue_permission=perm)

    check(client, assert_true)

  def test_permissions(self):
    privilege = {
      'privilegeScope': 'URI',
      'serverName': 'server1',
      'dbName': 'default',
      'tableName': 'sample_07',
      'columnName': '',
      'URI': u'/tmp/à',
      'action': 'ALL',
      'timestamp': 0,
      'grantOption': 0
    }
    _to_sentry_privilege(privilege)
