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

import sys

from nose.tools import assert_equal

from desktop.auth.backend import LdapBackend, rewrite_user
from desktop.lib.django_test_util import make_logged_in_client
from useradmin.models import User

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock

class TestLdapBackend():
    
  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = rewrite_user(User.objects.get(username="test"))

  def test_authenticate(self):
    with patch('desktop.auth.backend.LdapBackend.check_ldap_access_groups') as check_ldap_access_groups:
      check_ldap_access_groups.return_value = True

      user = LdapBackend().authenticate(request=Mock(), username=Mock(), password=Mock(), server=Mock())

      assert_equal(user, None)
