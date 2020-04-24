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
import logging
import sys

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true, assert_raises
from requests.exceptions import ReadTimeout

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access
from useradmin.models import User

from beeswax.api import _autocomplete


if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


LOG = logging.getLogger(__name__)


class TestApi():

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")

  def test_autocomplete_time_out(self):

    get_tables_meta=Mock(
      side_effect=ReadTimeout("HTTPSConnectionPool(host='gethue.com', port=10001): Read timed out. (read timeout=120)")
    )
    db = Mock(
      get_tables_meta=get_tables_meta
    )

    resp = _autocomplete(db, database='database')

    assert_equal(
      resp,
      {
        'code': 500,
        'error': "HTTPSConnectionPool(host='gethue.com', port=10001): Read timed out. (read timeout=120)"
      }
    )
