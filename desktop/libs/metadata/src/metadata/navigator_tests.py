#!/usr/bin/env python
# -- coding: utf-8 --
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

from desktop.auth.backend import rewrite_user
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access
from hadoop.pseudo_hdfs4 import is_live_cluster

from metadata.conf import has_navigator, NAVIGATOR, get_navigator_auth_password,\
  get_navigator_auth_username
from metadata.navigator_api import _augment_highlighting
from metadata.navigator_client import NavigatorApi


LOG = logging.getLogger(__name__)


class TestNavigator(object):

  @classmethod
  def setup_class(cls):
    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    cls.user = rewrite_user(cls.user)
    add_to_group('test')
    grant_access("test", "test", "metadata")

    if not is_live_cluster() or not has_navigator(cls.user):
      raise SkipTest

    cls.api = NavigatorApi(cls.user)


  @classmethod
  def teardown_class(cls):
    cls.user.is_superuser = False
    cls.user.save()


  def test_search_entities_view(self):
    resp = self.client.post(reverse('metadata:search_entities'), {'query_s': json.dumps('châteaux'), 'limit': 25, 'sources': json.dumps(['sql'])})
    json_resp = json.loads(resp.content)
    assert_equal(0, json_resp['status'], json_resp)


  def test_search_entities_interactive_view(self):
    resp = self.client.post(reverse('metadata:search_entities_interactive'), {'query_s': json.dumps('châteaux'), 'limit': 10, 'sources': json.dumps(['sql'])})
    json_resp = json.loads(resp.content)
    assert_equal(0, json_resp['status'], json_resp)


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
    assert_equal(set(tags + ['hue_test']), set(json_resp['entity']['tags']))

    resp = self.client.post(reverse('metadata:delete_tags'), self._format_json_body({'id': entity_id, 'tags': ['hue_test']}))
    json_resp = json.loads(resp.content)
    assert_equal(0, json_resp['status'], json_resp)
    assert_true(tags, json_resp['entity']['tags'])


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


  def test_search_entities_interactive(self):
    resp = self.client.post(reverse('metadata:list_tags'), self._format_json_body({'prefix': 'hue'}))
    json_resp = json.loads(resp.content)
    assert_true('tags' in json_resp)
    assert_equal(0, json_resp['status'], json_resp)


  def test_suggest(self):
    resp = self.client.post(reverse('metadata:suggest'), self._format_json_body({'prefix': 'hue'}))
    json_resp = json.loads(resp.content)
    assert_true('suggest' in json_resp)
    assert_equal(0, json_resp['status'], json_resp)


  def test_lineage(self):
    # TODO: write me
    pass


  def _format_json_body(self, post_dict):
    json_dict = {}
    for key, value in post_dict.items():
      json_dict[key] = json.dumps(value)
    return json_dict


class TestNavigatorAPI(object):

  def test_augment_highlighting_emty_db_name(self):
    query_s = 'type:database*'
    records = [
      {u'customProperties': None, u'deleteTime': None, u'fileSystemPath': u'hdfs://Enchilada/data/marketsriskcalc/work/hive', u'description': None, u'params': None, u'type': u'DATABASE', u'internalType': u'hv_database', u'sourceType': u'HIVE', u'tags': None, u'deleted': False, u'technicalProperties': None, u'userEntity': False, u'originalDescription': None, u'metaClassName': u'hv_database', u'properties': None, u'identity': u'51002517', u'firstClassParentId': None, u'name': None, u'extractorRunId': u'845beb21b95783c4f55276a4ae38a332##3', u'sourceId': u'56850544', u'packageName': u'nav', u'parentPath': None, u'originalName': u'marketsriskcalc_work'}, {u'customProperties': None, u'deleteTime': None, u'fileSystemPath': u'hdfs://Enchilada/data/catssolprn/work/hive', u'description': None, u'params': None, u'type': u'DATABASE', u'internalType': u'hv_database', u'sourceType': u'HIVE', u'tags': None, u'deleted': False, u'technicalProperties': None, u'userEntity': False, u'originalDescription': None, u'metaClassName': u'hv_database', u'properties': None, u'identity': u'51188932', u'firstClassParentId': None, u'name': None, u'extractorRunId': u'845beb21b95783c4f55276a4ae38a332##3', u'sourceId': u'56850544', u'packageName': u'nav', u'parentPath': None, u'originalName': u'catssolprn_work'}
    ]

    _augment_highlighting(query_s, records)
    assert_equal('', records[0]['parentPath'])

  def test_navigator_conf(self):
    resets = [
      NAVIGATOR.AUTH_CM_USERNAME.set_for_testing('cm_username'),
      NAVIGATOR.AUTH_CM_PASSWORD.set_for_testing('cm_pwd'),
      NAVIGATOR.AUTH_LDAP_USERNAME.set_for_testing('ldap_username'),
      NAVIGATOR.AUTH_LDAP_PASSWORD.set_for_testing('ldap_pwd'),
      NAVIGATOR.AUTH_SAML_USERNAME.set_for_testing('saml_username'),
      NAVIGATOR.AUTH_SAML_PASSWORD.set_for_testing('saml_pwd'),
    ]

    reset = NAVIGATOR.AUTH_TYPE.set_for_testing('CMDB')

    try:
      assert_equal('cm_username', get_navigator_auth_username())
      assert_equal('cm_pwd', get_navigator_auth_password())

      reset()
      reset = NAVIGATOR.AUTH_TYPE.set_for_testing('ldap')

      assert_equal('ldap_username', get_navigator_auth_username())
      assert_equal('ldap_pwd', get_navigator_auth_password())

      reset()
      reset = NAVIGATOR.AUTH_TYPE.set_for_testing('SAML')

      assert_equal('saml_username', get_navigator_auth_username())
      assert_equal('saml_pwd', get_navigator_auth_password())
    finally:
      reset()
      for _reset in resets:
        _reset()
