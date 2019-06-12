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
from django.urls import reverse

from dashboard.models import Collection2
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access
from hadoop.pseudo_hdfs4 import is_live_cluster

from libsolr.api import SolrApi


LOG = logging.getLogger(__name__)


try:
  # App can be blacklisted
  from search.conf import SOLR_URL
  search_enabled = True
except:
  search_enabled = False
  LOG.exception('Testing libsolr requires the search app to not be blacklisted')


class TestLibSolrWithSolr:
  integration = True

  @classmethod
  def setup_class(cls):

    if not is_live_cluster() or not search_enabled:
      raise SkipTest

    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "libsolr")
    grant_access("test", "test", "search")

    cls.user.is_superuser = True
    cls.user.save()

    resp = cls.client.post(reverse('search:install_examples'))
    content = json.loads(resp.content)

    cls.user.is_superuser = False
    cls.user.save()

    assert_equal(content.get('status'), 0)

  @classmethod
  def teardown_class(cls):
    cls.user.is_superuser = False
    cls.user.save()

  def test_is_solr_cloud_mode(self):
    raise SkipTest # collections() no longer work
    SolrApi(SOLR_URL.get(), self.user).collections()

  def test_query(self):
    collection = Collection2(user=self.user, name='log_analytics_demo')
    collection = json.loads(collection.get_json(self.user))

    query = {'qs': [{'q': ''}], 'fqs': [], 'start': 0}

    SolrApi(SOLR_URL.get(), self.user).query(collection['collection'], query)
