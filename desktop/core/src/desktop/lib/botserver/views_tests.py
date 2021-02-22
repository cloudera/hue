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
import logging
import unittest
import sys

from nose.tools import assert_equal, assert_true
from django.test import TestCase
from desktop.lib.botserver.views import *

if sys.version_info[0] > 2:
  from unittest.mock import patch
else:
  from mock import patch

LOG = logging.getLogger(__name__)

class TestBotServer(unittest.TestCase):
  def test_get_bot_id(self):
    with patch('desktop.lib.botserver.views.slack_client') as slack_client_mock:
      slack_client_mock.api_call("users.list").return_value = {
        'members': [
          {
            'name': 'hue_bot',
            'deleted': False,
            'id': 'U01K99VEDR9'
          }
        ]
      }
      bot_id = get_bot_id('hue_bot')
      assert_equal(bot_id, 'U01K99VEDR9')
  





