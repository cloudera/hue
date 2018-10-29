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

import json

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true, assert_false

from django.contrib.auth.models import User
from django.urls import reverse

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access
from hadoop.pseudo_hdfs4 import is_live_cluster, get_db_prefix
from libsolr import conf as libsolr_conf
from libzookeeper import conf as libzookeeper_conf

from indexer.conf import get_solr_ensemble
from indexer.controller import CollectionManagerController


def test_get_ensemble():

  clears = []
  clears.append(libzookeeper_conf.ENSEMBLE.set_for_testing('zoo:2181'))
  clears.append(libsolr_conf.SOLR_ZK_PATH.set_for_testing('/solr'))
  try:
    assert_equal('zoo:2181/solr', get_solr_ensemble())
  finally:
    for clear in clears:
      clear()

  clears = []
  clears.append(libzookeeper_conf.ENSEMBLE.set_for_testing('zoo:2181,zoo2:2181'))
  clears.append(libsolr_conf.SOLR_ZK_PATH.set_for_testing('/solr2'))
  try:
    assert_equal('zoo:2181,zoo2:2181/solr2', get_solr_ensemble())
  finally:
    for clear in clears:
      clear()


class TestIndexerWithSolr:

  @classmethod
  def setup_class(cls):

    if not is_live_cluster():
      raise SkipTest()

    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "indexer")

    cls.db = CollectionManagerController(cls.user)

    resp = cls.client.post(reverse('indexer:install_examples'), {'data': 'log_analytics_demo'})
    content = json.loads(resp.content)

    assert_equal(content.get('status'), 0)

  @classmethod
  def teardown_class(cls):
    pass

  def test_is_solr_cloud_mode(self):
    assert_true(CollectionManagerController(self.user).is_solr_cloud_mode())

  def test_collection_exists(self):
    assert_false(self.db.collection_exists('does_not_exist'))

  def test_get_collections(self):
    self.db.get_collections()

  def test_create_and_delete_collection(self):
    name = get_db_prefix(name='solr') + 'test_create_collection'
    fields = [{'name': 'id', 'type': 'string'}, {'name': 'my_text', 'type': 'text_general'}]

    # We get exceptions if problems in both case there
    try:
      self.db.create_collection(name, fields, unique_key_field='id', df='my_text')
    finally:
      self.db.delete_collection(name, core=False)

  def test_collections_fields(self):
    uniquekey, fields = self.db.get_fields('log_analytics_demo')
    assert_equal('id', uniquekey)

    assert_true('protocol' in fields, fields)
    assert_true('country_code3' in fields, fields)
