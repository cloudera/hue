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

import sys
import unittest

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true, assert_false

from desktop.auth.backend import rewrite_user, create_user
from desktop.conf import ENABLE_ORGANIZATIONS
from desktop.lib.django_test_util import make_logged_in_client

from useradmin.models import User, Group, Organization


if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


class TestOrganizationSingleUser(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    if not ENABLE_ORGANIZATIONS.get():  # Skip for now as depends on DB changes
      raise SkipTest

    cls.user1 = create_user('user1@gethue.com', 'test', is_superuser=False)
    cls.user2 = create_user('user2@gethue.com', 'test', is_superuser=False)
    cls.user3 = create_user('user3@gethue.com', 'test', is_superuser=False)
    cls.user4 = create_user('user4@gethue.com', 'test', is_superuser=False)

    cls.client1 = make_logged_in_client(username=cls.user1.username)
    cls.client2 = make_logged_in_client(username=cls.user2.username)

  @classmethod
  def tearDownClass(cls):
    cls.user1.delete()
    cls.user2.delete()
    cls.user3.delete()
    cls.user4.delete()


  def test_users_groups(self):
    assert_equal(4, User.objects.count())
    assert_equal(4, Organization.objects.count())

    assert_equal(4, Group.objects.count())


  def test_get_users(self):

    response = self.client2.get('/useradmin/api/get_users/')
    data = json.loads(response.content)

    assert_equal(0, data['status'])
    assert_true('users' in data)
    assert_equal([ ], [user['username'] for user in data['users']])
