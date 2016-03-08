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

from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal, assert_raises

from django.contrib.auth.models import User

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.models import DefaultConfiguration
from useradmin.models import get_default_user_group


class TestDefaultConfiguration(object):

  def setUp(self):
    self.client = make_logged_in_client(username="test_admin", groupname="default", recreate=False, is_superuser=True)
    self.client_user = make_logged_in_client(username="test_user", groupname="default", recreate=False, is_superuser=False)

    self.admin = User.objects.get(username="test_admin")
    self.user = User.objects.get(username="test_user")

    self.group = get_default_user_group()

    grant_access(self.admin.username, self.admin.username, "desktop")
    grant_access(self.user.username, self.user.username, "desktop")


  def tearDown(self):
    DefaultConfiguration.objects.all().delete()


  def test_save_default_configuration(self):
    app = 'hive'
    is_default = True
    properties = {
        'settings': [{'key': 'hive.execution.engine', 'value': 'spark'}]
    }

    # Create new default configuration
    configs = DefaultConfiguration.objects.filter(app=app, is_default=is_default)
    assert_equal(configs.count(), 0)

    response = self.client.post("/desktop/api/configurations/save", {
        'app': 'hive',
        'properties': json.dumps(properties),
        'is_default': is_default})
    content = json.loads(response.content)
    assert_equal(content['status'], 0, content)
    assert_true('configuration' in content, content)

    config = DefaultConfiguration.objects.get(app=app, is_default=is_default)
    assert_equal(config.properties_dict, properties, config.properties_dict)

    # Update same default configuration
    properties = {
        'settings': [{'key': 'hive.execution.engine', 'value': 'mr'}]
    }

    response = self.client.post("/desktop/api/configurations/save", {
        'app': 'hive',
        'properties': json.dumps(properties),
        'is_default': is_default})
    content = json.loads(response.content)
    assert_equal(content['status'], 0, content)
    assert_true('configuration' in content, content)

    config = DefaultConfiguration.objects.get(app=app, is_default=is_default)
    assert_equal(config.properties_dict, properties, config.properties_dict)


  def test_get_default_configurations(self):
    app = 'hive'
    properties = {
        'settings': [{'key': 'hive.execution.engine', 'value': 'spark'}]
    }

    # No configurations returns null
    response = self.client.get("/desktop/api/configurations/user", {
        'app': 'hive',
        'user_id': self.user.id})
    content = json.loads(response.content)
    assert_equal(content['status'], 0, content)
    assert_equal(content['configuration'], None, content)

    # Creating a default configuration returns default
    response = self.client.post("/desktop/api/configurations/save", {
        'app': 'hive',
        'properties': json.dumps(properties),
        'is_default': True})

    response = self.client.get("/desktop/api/configurations/user", {
        'app': 'hive',
        'user_id': self.user.id})
    content = json.loads(response.content)
    assert_equal(content['status'], 0, content)
    assert_equal(content['configuration']['app'], 'hive', content)
    assert_equal(content['configuration']['is_default'], True, content)
    assert_equal(content['configuration']['user'], None, content)
    assert_equal(content['configuration']['group'], None, content)
    assert_equal(content['configuration']['properties'], properties, content)

    # Creating a group configuration returns group config
    properties = {
        'settings': [{'key': 'hive.execution.engine', 'value': 'mr'}]
    }
    response = self.client.post("/desktop/api/configurations/save", {
        'app': 'hive',
        'properties': json.dumps(properties),
        'is_default': False,
        'group_id': self.group.id})

    response = self.client.get("/desktop/api/configurations/user", {
        'app': 'hive',
        'user_id': self.user.id})
    content = json.loads(response.content)
    assert_equal(content['status'], 0, content)
    assert_equal(content['configuration']['app'], 'hive', content)
    assert_equal(content['configuration']['is_default'], False, content)
    assert_equal(content['configuration']['user'], None, content)
    assert_equal(content['configuration']['group'], self.group.name, content)
    assert_equal(content['configuration']['properties'], properties, content)

    # Creating a user configuration returns user config
    properties = {
        'files': [{'type': 'JAR', 'path': '/user/test/udfs.jar'}],
        'settings': [{'key': 'hive.execution.engine', 'value': 'spark'}]
    }
    response = self.client.post("/desktop/api/configurations/save", {
        'app': 'hive',
        'properties': json.dumps(properties),
        'is_default': False,
        'user_id': self.user.id})

    response = self.client.get("/desktop/api/configurations/user", {
        'app': 'hive',
        'user_id': self.user.id})
    content = json.loads(response.content)
    assert_equal(content['status'], 0, content)
    assert_equal(content['configuration']['app'], 'hive', content)
    assert_equal(content['configuration']['is_default'], False, content)
    assert_equal(content['configuration']['user'], self.user.username, content)
    assert_equal(content['configuration']['group'], None, content)
    assert_equal(content['configuration']['properties'], properties, content)
