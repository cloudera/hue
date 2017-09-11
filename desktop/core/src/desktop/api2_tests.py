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
import re

from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal, assert_raises

from django.contrib.auth.models import User

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.models import Document2


class TestApi2():

  def setUp(self):
    self.client = make_logged_in_client(username="api2_user", groupname="default", recreate=True, is_superuser=False)

    self.user = User.objects.get(username="api2_user")

    grant_access(self.user.username, self.user.username, "desktop")

  def test_search_entities_interactive_xss(self):
    query = Document2.objects.create(name='<script>alert(5)</script>', description='<script>alert(5)</script>', type='query-hive', owner=self.user)

    try:
      response = self.client.post('/desktop/api/search/entities_interactive/', data={
        'sources': json.dumps(['documents']),
        'query_s': json.dumps('alert')
      })
      results = json.loads(response.content)['results']
      assert_true(results)
      result_json = json.dumps(results)
      assert_false(re.match('<(?!em)', result_json), result_json)
      assert_false(re.match('(?!em)>', result_json), result_json)
      assert_false('<script>' in result_json, result_json)
      assert_false('</script>' in result_json, result_json)
      assert_true('&lt;' in result_json, result_json)
      assert_true('&gt;' in result_json, result_json)
    finally:
      query.delete()
