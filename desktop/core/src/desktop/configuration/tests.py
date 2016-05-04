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
    assert_equal(configs.count(), 0)

    # Save configuration
    response = self.client.post("/desktop/api/configurations/", {'configuration': json.dumps(configuration)})
    content = json.loads(response.content)
    assert_equal(content['status'], 0, content)
    assert_true('configuration' in content, content)

    config = DefaultConfiguration.objects.get(app='hive', is_default=True)
    assert_equal(config.properties_list, configuration['hive']['default'], config.properties_list)

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
        'groups': {
          str(self.group.id): [
            {
              'multiple': True,
              'value': [{'key': 'hive.execution.engine', 'value': 'spark'}],
              'nice_name': 'Settings',
              'key': 'settings',
              'help_text': 'Hive configuration properties.',
              'type': 'settings',
              'options': []
            }
          ]
        }
      }
    }

    response = self.client.post("/desktop/api/configurations/", {'configuration': json.dumps(configuration)})
    content = json.loads(response.content)
    assert_equal(content['status'], 0, content)
    assert_true('configuration' in content, content)

    config = DefaultConfiguration.objects.get(app='hive', is_default=True)
    assert_equal(config.properties_list, configuration['hive']['default'], config.properties_list)

    config = DefaultConfiguration.objects.get(app='hive', group=self.group)
    assert_equal(config.properties_list, configuration['hive']['groups'][str(self.group.id)], config.properties_list)


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
    assert_equal(content['status'], 0, content)
    assert_equal(content['configuration'], None, content)

    # Creating a default configuration returns default
    response = self.client.post("/desktop/api/configurations/", {'configuration': json.dumps(configuration)})

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
        'groups': {
          str(self.group.id): group_properties
        }
      }
    }

    response = self.client.post("/desktop/api/configurations/", {'configuration': json.dumps(configuration)})

    response = self.client.get("/desktop/api/configurations/user", {
      'app': 'hive',
      'user_id': self.user.id})
    content = json.loads(response.content)
    assert_equal(content['status'], 0, content)
    assert_equal(content['configuration']['app'], 'hive', content)
    assert_equal(content['configuration']['is_default'], False, content)
    assert_equal(content['configuration']['user'], None, content)
    assert_equal(content['configuration']['group'], self.group.name, content)
    assert_equal(content['configuration']['properties'], group_properties, content)

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
    assert_equal(content['status'], 0, content)
    assert_equal(content['configuration']['app'], 'hive', content)
    assert_equal(content['configuration']['is_default'], False, content)
    assert_equal(content['configuration']['user'], self.user.username, content)
    assert_equal(content['configuration']['group'], None, content)
    assert_equal(content['configuration']['properties'], user_properties, content)
