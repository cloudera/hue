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

import os

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true, assert_false, assert_not_equal

from django.contrib.auth.models import User

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access
from hadoop.pseudo_hdfs4 import is_live_cluster

from libsentry.conf import HOSTNAME, PORT, SENTRY_CONF_DIR
from libsentry.client import SentryClient


class TestWithSentry:
  requires_hadoop = True

  @classmethod
  def setup_class(cls):

    if not is_live_cluster():
      raise SkipTest('Sentry tests require a live sentry server')

    if not os.path.exists(os.path.join(SENTRY_CONF_DIR.get(), 'sentry-site.xml')):
      raise SkipTest('Could not find sentry-site.xml, skipping sentry tests')

    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "libsentry")

    cls.db = SentryClient(HOSTNAME.get(), PORT.get(), 'test')

  @classmethod
  def teardown_class(cls):
    pass


  def test_get_collections(self):
    resp = self.db.list_sentry_roles_by_group() # Non Sentry Admin can do that
    assert_not_equal(0, resp.status.value, resp)
    assert_true('denied' in resp.status.message, resp)

    resp = self.db.list_sentry_roles_by_group(groupName='*')
    assert_equal(0, resp.status.value, resp)
