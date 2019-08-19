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
from __future__ import absolute_import

import json
import os
import tempfile
import string

from django.contrib.auth.models import User
from nose.tools import eq_

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access, add_to_group

from googleCS.gs.gstest_utils import GSTestBase




class GSFSTest(GSTestBase):

  @classmethod
  def setUpClass(cls):
    GSTestBase.setUpClass()
    if not cls.shouldSkip():
      cls.fs = GSFileSystem(cls.gs_connection)

      cls.c = make_logged_in_client(username='test', is_superuser=False)
      grant_access('test', 'test', 'filebrowser')
      add_to_group('test')
      cls.user = User.objects.get(username="test")


  def test_read(self):
    path = self.get_test_path('test_read.txt')
    with self.cleaning(path):
      key = self.get_key(path)
      key.set_contents_from_string('Hello')

      eq_('Hel', self.fs.read(path, 0, 3))
      eq_('ell', self.fs.read(path, 1, 3))