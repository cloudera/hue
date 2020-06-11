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

import logging
import json
import sys

from django.urls import reverse
from nose.tools import assert_equal, assert_not_equal, assert_true, assert_false

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.connectors.models import Connector
from useradmin.models import User

from notebook.conf import EXAMPLES
from notebook.models import install_custom_examples

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock, MagicMock
else:
  from mock import patch, Mock, MagicMock


LOG = logging.getLogger(__name__)


class TestInstallCustomExamples():

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=True, is_admin=True)
    self.user = User.objects.get(username="test")


  def test_install_only_hive_queries(self):
    finish = [
      EXAMPLES.AUTO_LOAD.set_for_testing(True),
      EXAMPLES.QUERIES.set_for_testing(['Sample: Top salary', 'Queries Does not Exist'])
    ]

    try:
      with patch('notebook.models.get_ordered_interpreters') as get_ordered_interpreters:

        get_ordered_interpreters.return_value = [
          {
            'name': 'Hive',
            'type': 11,
            'dialect': 'hive',
            'interface': 'hiveserver2',
          },
          {
            'name': 'MySql',
            'type': 10,
            'dialect': 'mysql',
            'interface': 'sqlalchemy',
          }
        ]

        result = install_custom_examples()

        assert_equal(1, len(result))
        successes, errors = result[0]

        assert_equal([], errors)
        assert_equal(
            ['Query Sample: Top salary hive installed.'],
            successes,
        )
    finally:
      for f in finish:
        f()


  def test_install_auto_load_disabled(self):
    f = EXAMPLES.AUTO_LOAD.set_for_testing(False)
    try:
      result = install_custom_examples()

      assert_true(result is None, result)
    finally:
      f()
