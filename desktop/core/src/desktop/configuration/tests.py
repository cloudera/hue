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
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from builtins import object

import pytest

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.models import DefaultConfiguration
from useradmin.models import get_default_user_group, User


@pytest.mark.django_db
class TestDefaultConfiguration(object):

  def setup_method(self):
    self.client = make_logged_in_client(username="test_admin", groupname="default", recreate=False, is_superuser=True)
    self.client_user = make_logged_in_client(username="test_user", groupname="default", recreate=False, is_superuser=False)

    self.admin = User.objects.get(username="test_admin")
    self.user = User.objects.get(username="test_user")

    self.group = get_default_user_group()

    grant_access(self.admin.username, self.admin.username, "desktop")
    grant_access(self.user.username, self.user.username, "desktop")

  def teardown_method(self):
    DefaultConfiguration.objects.all().delete()

  def test_update_default_and_group_configurations(self):
    configuration = {
      'hive': {
        'default': [
          {
            'multiple': True,
            'value': [],
            'nice_name': 'Settings',
            'key': 'settings',
            'help_text': 'Hive configuration properties.',
            'type': 'settings',
            'options': []
          }
        ]
      }
    }

    # Verify no default configuration found for app
    configs = DefaultConfiguration.objects.filter(app='hive', is_default=True)
    assert configs.count() == 0

    # Save configuration
    response = self.client.post("/desktop/api/configurations/", {'configuration': json.dumps(configuration)})
    content = json.loads(response.content)
    assert content['status'] == 0, content
    assert 'configuration' in content, content

    config = DefaultConfiguration.objects.get(app='hive', is_default=True)
    assert config.properties_list == configuration['hive']['default'], config.properties_list

    # Update with group configuration
    configuration = {
      'hive': {
        'default': [
          {
            'multiple': True,
            'value': [{'key': 'hive.execution.engine', 'value': 'mr'}],
            'nice_name': 'Settings',
            'key': 'settings',
            'help_text': 'Hive configuration properties.',
            'type': 'settings',
            'options': []
          }
        ],
        'groups': [
          {
            'group_ids': [self.group.id],
            'properties': {
              'multiple': True,
              'value': [{'key': 'hive.execution.engine', 'value': 'spark'}],
              'nice_name': 'Settings',
              'key': 'settings',
              'help_text': 'Hive configuration properties.',
              'type': 'settings',
              'options': []
            }
          }
        ]
      }
    }

    response = self.client.post("/desktop/api/configurations/", {'configuration': json.dumps(configuration)})
    content = json.loads(response.content)
    assert content['status'] == 0, content
    assert 'configuration' in content, content

    config = DefaultConfiguration.objects.get(app='hive', is_default=True)
    assert config.properties_list == configuration['hive']['default'], config.properties_list

    config = DefaultConfiguration.objects.get(app='hive', groups__in=[self.group])
    assert config.properties_list == configuration['hive']['groups'][0]['properties'], config.properties_list

  def test_get_default_configurations(self):
    app = 'hive'
    properties = [
      {
        "multiple": True,
        "value": [{
          "path": "/user/test/myudfs.jar",
          "type": "jar"
        }],
        "nice_name": "Files",
        "key": "files",
        "help_text": "Add one or more files, jars, or archives to the list of resources.",
        "type": "hdfs-files"
      },
      {
        "multiple": True,
        "value": [{
          "class_name": "org.hue.udf.MyUpper",
          "name": "myUpper"
        }],
        "nice_name": "Functions",
        "key": "functions",
        "help_text": "Add one or more registered UDFs (requires function name and fully-qualified class name).",
        "type": "functions"
      },
      {
        "multiple": True,
        "value": [{
          "key": "mapreduce.job.queuename",
          "value": "mr"
        }],
        "nice_name": "Settings",
        "key": "settings",
        "help_text": "Hive and Hadoop configuration properties.",
        "type": "settings",
        "options": [
          "hive.map.aggr",
          "hive.exec.compress.output",
          "hive.exec.parallel",
          "hive.execution.engine",
          "mapreduce.job.queuename"
        ]
      }
    ]
    configuration = {
      app: {
        'default': properties
      }
    }

    # No configurations returns null
    response = self.client.get("/desktop/api/configurations/user", {
      'app': 'hive',
      'user_id': self.user.id})
    content = json.loads(response.content)
    assert content['status'] == 0, content
    assert content['configuration'] is None, content

    # Creating a default configuration returns default
    response = self.client.post("/desktop/api/configurations/", {'configuration': json.dumps(configuration)})

    response = self.client.get("/desktop/api/configurations/user", {
      'app': 'hive',
      'user_id': self.user.id})
    content = json.loads(response.content)
    assert content['status'] == 0, content
    assert content['configuration']['app'] == 'hive', content
    assert content['configuration']['is_default'], content
    assert content['configuration']['user'] is None, content
    assert content['configuration']['group_ids'] == [], content
    assert content['configuration']['properties'] == properties, content

    # Creating a group configuration returns group config
    group_properties = [{
      'multiple': True,
      'value': [{'key': 'hive.execution.engine', 'value': 'spark'}],
      'nice_name': 'Settings',
      'key': 'settings',
      'help_text': 'Hive configuration properties.',
      'type': 'settings',
      'options': []
    }]
    configuration = {
      app: {
        'default': properties,
        'groups': [
          {
            'group_ids': [self.group.id],
            'properties': group_properties
          }
        ]
      }
    }

    response = self.client.post("/desktop/api/configurations/", {'configuration': json.dumps(configuration)})

    response = self.client.get("/desktop/api/configurations/user", {
      'app': 'hive',
      'user_id': self.user.id})
    content = json.loads(response.content)
    assert content['status'] == 0, content
    assert content['configuration']['app'] == 'hive', content
    assert not content['configuration']['is_default'], content
    assert content['configuration']['user'] is None, content
    assert content['configuration']['group_ids'] == [self.group.id], content
    assert content['configuration']['properties'] == group_properties, content

    # Creating a user configuration returns user config
    user_properties = [{
      'files': [{'type': 'JAR', 'path': '/user/test/udfs.jar'}],
      'settings': [{'key': 'hive.execution.engine', 'value': 'spark'}]
    }]
    response = self.client.post("/desktop/api/configurations/user", {
      'app': 'hive',
      'user_id': self.user.id,
      'properties': json.dumps(user_properties)
    })

    response = self.client.get("/desktop/api/configurations/user", {
      'app': 'hive',
      'user_id': self.user.id})
    content = json.loads(response.content)
    assert content['status'] == 0, content
    assert content['configuration']['app'] == 'hive', content
    assert not content['configuration']['is_default'], content
    assert content['configuration']['user'] == self.user.username, content
    assert content['configuration']['group_ids'] == [], content
    assert content['configuration']['properties'] == user_properties, content


@pytest.mark.django_db
class TestConfigurationAuthorization(object):
  """
  Regression tests for ISEC-V2026-03: DefaultConfiguration API must not allow IDOR on user_id or
  unprivileged access to global default/group configuration.
  """

  def setup_method(self):
    self.client = make_logged_in_client(username="test_admin", groupname="default", recreate=False, is_superuser=True)
    self.client_user = make_logged_in_client(username="test_user", groupname="default", recreate=False, is_superuser=False)

    self.admin = User.objects.get(username="test_admin")
    self.user = User.objects.get(username="test_user")

    self.group = get_default_user_group()

    grant_access(self.admin.username, self.admin.username, "desktop")
    grant_access(self.user.username, self.user.username, "desktop")

  def teardown_method(self):
    DefaultConfiguration.objects.all().delete()

  def test_non_admin_cannot_list_or_update_global_configurations(self):
    response = self.client_user.get("/desktop/api/configurations/")
    content = json.loads(response.content)
    assert content['status'] == -1
    assert 'admin' in content['message'].lower()

    response = self.client_user.post(
      "/desktop/api/configurations/",
      {'configuration': json.dumps({'hive': {'default': []}})},
    )
    content = json.loads(response.content)
    assert content['status'] == -1

  def test_non_admin_cannot_read_other_users_effective_configuration(self):
    response = self.client_user.get("/desktop/api/configurations/user", {
      'app': 'hive',
      'user_id': self.admin.id,
    })
    content = json.loads(response.content)
    assert content['status'] == -1
    assert 'permission' in content['message'].lower()

  def test_non_admin_cannot_save_configuration_for_other_user(self):
    response = self.client_user.post("/desktop/api/configurations/user", {
      'app': 'hive',
      'user_id': self.admin.id,
      'properties': json.dumps([{'key': 'settings', 'value': []}]),
    })
    content = json.loads(response.content)
    assert content['status'] == -1
    assert DefaultConfiguration.objects.filter(app='hive', user=self.admin).count() == 0

  def test_non_admin_can_read_and_save_own_user_configuration(self):
    user_properties = [{'settings': [{'key': 'hive.execution.engine', 'value': 'tez'}]}]

    response = self.client_user.post("/desktop/api/configurations/user", {
      'app': 'hive',
      'user_id': self.user.id,
      'properties': json.dumps(user_properties),
    })
    content = json.loads(response.content)
    assert content['status'] == 0, content

    response = self.client_user.get("/desktop/api/configurations/user", {
      'app': 'hive',
      'user_id': self.user.id,
    })
    content = json.loads(response.content)
    assert content['status'] == 0, content
    assert content['configuration']['user'] == self.user.username
    assert content['configuration']['properties'] == user_properties

  def test_admin_can_read_other_users_effective_configuration(self):
    response = self.client.get("/desktop/api/configurations/user", {
      'app': 'hive',
      'user_id': self.user.id,
    })
    content = json.loads(response.content)
    assert content['status'] == 0, content

  def test_non_admin_cannot_delete_default_configuration(self):
    default_config = DefaultConfiguration.objects.create(app='hive', is_default=True, properties='[]')

    response = self.client_user.post("/desktop/api/configurations/delete/", {'id': default_config.id})
    content = json.loads(response.content)
    assert content['status'] == -1
    assert DefaultConfiguration.objects.filter(id=default_config.id).exists()

  def test_non_admin_cannot_delete_other_users_configuration(self):
    other_user_config = DefaultConfiguration.objects.create(
      app='hive',
      is_default=False,
      user=self.admin,
      properties='[]',
    )

    response = self.client_user.post("/desktop/api/configurations/delete/", {'id': other_user_config.id})
    content = json.loads(response.content)
    assert content['status'] == -1
    assert DefaultConfiguration.objects.filter(id=other_user_config.id).exists()

  def test_user_can_delete_own_configuration(self):
    own_config = DefaultConfiguration.objects.create(
      app='hive',
      is_default=False,
      user=self.user,
      properties='[]',
    )

    response = self.client_user.post("/desktop/api/configurations/delete/", {'id': own_config.id})
    content = json.loads(response.content)
    assert content['status'] == 0, content
    assert not DefaultConfiguration.objects.filter(id=own_config.id).exists()

  def test_non_admin_cannot_delete_group_configuration(self):
    group_config = DefaultConfiguration.objects.create(app='hive', is_default=False, properties='[]')
    group_config.groups.add(self.group)

    response = self.client_user.post("/desktop/api/configurations/delete/", {'id': group_config.id})
    content = json.loads(response.content)
    assert content['status'] == -1
    assert DefaultConfiguration.objects.filter(id=group_config.id).exists()

  def test_admin_can_delete_any_configuration(self):
    user_config = DefaultConfiguration.objects.create(
      app='hive',
      is_default=False,
      user=self.user,
      properties='[]',
    )

    response = self.client.post("/desktop/api/configurations/delete/", {'id': user_config.id})
    content = json.loads(response.content)
    assert content['status'] == 0, content
    assert not DefaultConfiguration.objects.filter(id=user_config.id).exists()
