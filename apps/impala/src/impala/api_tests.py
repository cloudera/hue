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

from builtins import object
import json
import logging
import sys

from django.urls import reverse
from nose.tools import assert_true, assert_equal, assert_false, assert_raises

from desktop.lib.django_test_util import make_logged_in_client

from impala import conf

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock

LOG = logging.getLogger()


class TestImpala(object):

  def setUp(self):
    self.client = make_logged_in_client()

  def test_invalidate(self):
    with patch('impala.api.beeswax_dbms') as beeswax_dbms:
      invalidate = Mock()
      beeswax_dbms.get = Mock(
        return_value=Mock(invalidate=invalidate)
      )

      response = self.client.post(reverse("impala:invalidate"), {
          'flush_all': False,
          'cluster': json.dumps({"credentials":{},"type":"direct","id":"default","name":"default"}),
          'database': 'default',
          'table': 'k8s_logs'
        }
      )

      invalidate.assert_called()

      assert_equal(response.status_code, 200)
      content = json.loads(response.content)
      assert_equal(content['message'], 'Successfully invalidated metadata')
