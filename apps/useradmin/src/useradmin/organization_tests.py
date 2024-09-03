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
import logging
from unittest.mock import Mock, patch

import pytest
from django.core.exceptions import FieldError
from django.test import TestCase

from desktop.auth.backend import create_user, rewrite_user
from desktop.conf import ENABLE_ORGANIZATIONS
from desktop.lib.django_test_util import make_logged_in_client
from desktop.models import Document2
from useradmin.models import Group, HuePermission, Organization, User

LOG = logging.getLogger()


class TestOrganizationSingleUser(TestCase):

  @classmethod
  def setup_class(cls):
    if not ENABLE_ORGANIZATIONS.get():  # Skip for now as depends on DB changes
      pytest.skip("Skipping Test")

    cls.user1 = create_user('user1@testorg.gethue.com', 'test', is_superuser=False)
    cls.user2 = create_user('user2@testorg.gethue.com', 'test', is_superuser=True)
    cls.user3 = create_user('user3@testorg.gethue.com', 'test', is_superuser=False)
    cls.user4 = create_user('user4@testorg.gethue.com', 'test', is_superuser=False)

    cls.client1 = make_logged_in_client(username=cls.user1.username)
    cls.client2 = make_logged_in_client(username=cls.user2.username)

  @classmethod
  def teardown_class(cls):
    cls.user1.delete()
    cls.user2.delete()
    cls.user3.delete()
    cls.user4.delete()

  def test_login(self):
    client = make_logged_in_client(username=self.user1.username)
    client = make_logged_in_client(username=self.user1.username)

  def test_user_group(self):
    user1_organization = Organization.objects.get(name='user1@testorg.gethue.com')

    assert 'user1@testorg.gethue.com' == self.user1.email
    assert self.user1.is_admin
    assert user1_organization == self.user1.organization
    assert (
      list(Group.objects.filter(name='default', organization=user1_organization)) ==
      list(self.user1.groups.all()))

  def test_users_groups(self):
    assert 4 == User.objects.filter(email__contains='testorg.gethue.com').count(), User.objects.all()
    assert 4 == Organization.objects.filter(name__contains='testorg.gethue.com').count(), Organization.objects.all()
    assert 4 == Group.objects.filter(organization__name__contains='testorg.gethue.com').count(), Group.objects.all()

  def test_get_users(self):
    # View
    response = self.client1.get('/useradmin/users/')
    assert [self.user1] == list(response.context[0]['users'])

    # API
    response = self.client1.get('/useradmin/api/get_users/')
    data = json.loads(response.content)

    assert 0 == data['status']
    assert [self.user1.email] == [user['username'] for user in data['users']]

  def test_get_groups(self):
    # View
    response = self.client1.get('/useradmin/groups/')
    assert list(self.user1.groups.all()) == list(response.context[0]['groups'])

  def test_get_permissions(self):
    # View
    response = self.client1.get('/useradmin/permissions/')
    assert (
      list(HuePermission.objects.filter(organizationgroup__user=self.user1)) ==
      list(response.context[0]['permissions']))

  def test_get_documents(self):
    document = Document2.objects.create(
        name='TestOrganizationSingleUser.test_get_documents',
        type='query-hive',
        owner=self.user1,
    )

    try:
      # API
      response = self.client1.post('/desktop/api2/docs/?text=TestOrganizationSingleUser.test_get_document')
      data = json.loads(response.content)

      assert [document.id] == [doc['id'] for doc in data['documents']]

      # Admin other Org
      response = self.client2.post('/desktop/api2/docs/?text=TestOrganizationSingleUser.test_get_document')
      data = json.loads(response.content)

      assert [] == data['documents']
    finally:
      document.delete()

  def test_orm_compatiblity(self):
    User.objects.get(username=self.user1.email)

    User.objects.order_by('username')

    User.objects.filter(groups__in=Group.objects.all()).order_by('username')

    User.objects.values_list('username', flat=True)
    try:
      assert not User.objects.filter(groups__in=[]).values_list('username', flat=True)
      assert User.objects.filter(groups__in=Group.objects.all()).values_list('username', flat=True)
    except FieldError as e:
      LOG.warning('Test currently skipped')

    self.client2.get('/useradmin/groups/edit/default')
