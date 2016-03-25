#!/usr/bin/env python
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

import logging
import json

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from hadoop.pseudo_hdfs4 import is_live_cluster
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access

from metadata.navigator_client import NavigatorApi, is_navigator_enabled


LOG = logging.getLogger(__name__)


class TestNavigatorApi(object):

  @classmethod
  def setup_class(cls):

    if not is_live_cluster() or not is_navigator_enabled():
      raise SkipTest

    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "metadata")
    grant_access("test", "test", "navigator")

    cls.api = NavigatorApi()


  @classmethod
  def teardown_class(cls):
    cls.user.is_superuser = False
    cls.user.save()


  def test_search_entities(self):
    # TODO: write me
    pass


  def test_find_entity(self):
    entity = self.api.find_entity(source_type='HIVE', type='DATABASE', name='default')
    assert_true('identity' in entity, entity)


  def test_api_find_entity(self):
    resp = self.client.get(reverse('metadata:find_entity'), {'type': 'database', 'name': 'default'})
    json_resp = json.loads(resp.content)
    assert_equal(0, json_resp['status'])
    assert_true('entity' in json_resp, json_resp)
    assert_true('identity' in json_resp['entity'], json_resp)


  def test_api_tags(self):
    entity = self.api.find_entity(source_type='HIVE', type='DATABASE', name='default')
    entity_id = entity['identity']
    tags = entity['tags'] or []

    resp = self.client.post(reverse('metadata:add_tags'), self._format_json_body({'id': entity_id}))
    json_resp = json.loads(resp.content)
    # add_tags requires a list of tags
    assert_equal(-1, json_resp['status'])

    resp = self.client.post(reverse('metadata:add_tags'), self._format_json_body({'id': entity_id, 'tags': ['hue_test']}))
    json_resp = json.loads(resp.content)
    assert_equal(0, json_resp['status'], json_resp)
    assert_equal(tags + ['hue_test'], json_resp['entity']['tags'])

    resp = self.client.post(reverse('metadata:delete_tags'), self._format_json_body({'id': entity_id, 'tags': ['hue_test']}))
    json_resp = json.loads(resp.content)
    assert_equal(0, json_resp['status'], json_resp)
    assert_equal(entity['tags'] , json_resp['entity']['tags'])


  def test_api_properties(self):
    entity = self.api.find_entity(source_type='HIVE', type='DATABASE', name='default')
    entity_id = entity['identity']
    props = entity['properties'] or {}

    resp = self.client.post(reverse('metadata:update_properties'), self._format_json_body({'id': entity_id, 'properties': {'hue': 'test'}}))
    json_resp = json.loads(resp.content)
    assert_equal(0, json_resp['status'], json_resp)
    props.update({'hue': 'test'})
    assert_equal(props, json_resp['entity']['properties'])

    resp = self.client.post(reverse('metadata:delete_properties'), self._format_json_body({'id': entity_id, 'keys': ['hue']}))
    json_resp = json.loads(resp.content)
    assert_equal(0, json_resp['status'], json_resp)
    del props['hue']
    assert_equal(entity['properties'], json_resp['entity']['properties'])


  def test_lineage(self):
    # TODO: write me
    pass


  def _format_json_body(self, post_dict):
    json_dict = {}
    for key, value in post_dict.items():
      json_dict[key] = json.dumps(value)
    return json_dict
