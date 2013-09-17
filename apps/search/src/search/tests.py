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

try:
  import json
except ImportError:
  import simplejson as json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from nose.tools import assert_true, assert_equal

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.lib.rest import resource


class MockResource():

  def __init__(self, client):
    pass


class TestSearchBase(object):

  def setUp(self):
    self.c = make_logged_in_client(username='test_search', is_superuser=False)
    grant_access('test_search', 'test_search', 'search')
    self.user = User.objects.get(username='test_search')

    self.prev_resource = resource.Resource
    resource.Resource = MockResource

  def tearDown(self):
    # Remove monkey patching
    resource.Resource = self.prev_resource


class TestWithMockedSolr(TestSearchBase):

  def test_index(self):
    response = self.c.get(reverse('search:index'))
    assert_true('search' in response.content, response.content)

  def test_strip_nulls(self):
    response = '{"uid":"1111111","method":"check_user"}\x00'
    response = json.loads(response.replace('\x00', '')) # Does not call real API

