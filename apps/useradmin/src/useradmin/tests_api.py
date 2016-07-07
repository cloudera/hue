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

from nose.tools import assert_equal, assert_false, assert_true
from django.contrib.auth.models import User, Group

from desktop.lib.django_test_util import make_logged_in_client


class TestUseradminApi(object):

  def setUp(self):
    self.client = make_logged_in_client(username="hue_test_admin", groupname="hue_test_admin", recreate=True, is_superuser=True)
    self.user = User.objects.get(username="hue_test_admin")

    self.non_superuser_client = make_logged_in_client(username="hue_test_user", groupname="hue_test_user", recreate=True, is_superuser=False)
    self.non_superuser = User.objects.get(username="hue_test_user")

    self.test_group = Group.objects.create(name="hue_test_group")
    self.non_superuser.groups.add(self.test_group)
    self.non_superuser.save()

  def test_get_users(self):
    # Test get all users
    response = self.client.get('/useradmin/api/get_users/')
    data = json.loads(response.content)
    assert_equal(0, data['status'])
    assert_true('users' in data)
    assert_true(self.user.username in [user['username'] for user in data['users']])
    assert_true(self.non_superuser.username in [user['username'] for user in data['users']])

    # Test get by username
    response = self.client.get('/useradmin/api/get_users/', {'username': self.non_superuser.username})
    data = json.loads(response.content)
    assert_equal(1, len(data['users']), data['users'])
    assert_true(self.non_superuser.username in [user['username'] for user in data['users']])

    # Test filter by group
    response = self.client.get('/useradmin/api/get_users/', {'groups': [self.test_group.name]})
    data = json.loads(response.content)
    assert_equal(1, len(data['users']), data['users'])
    assert_true(self.non_superuser.username in [user['username'] for user in data['users']])
