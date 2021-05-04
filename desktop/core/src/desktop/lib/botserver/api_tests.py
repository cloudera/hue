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
import sys
import unittest

from django.urls import reverse
from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true, assert_false, assert_raises

from desktop import conf
from desktop.lib.django_test_util import make_logged_in_client

from useradmin.models import User

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock

class TestApi(object):

  def setUp(self):
    self.client = make_logged_in_client(username="api_user", recreate=True, is_superuser=False, is_admin=True)
    self.user = User.objects.get(username="api_user")

  @classmethod
  def setUpClass(cls):
    if not conf.SLACK.IS_ENABLED.get():
      raise SkipTest

  def test_get_channels(self):
    with patch('desktop.lib.botserver.api.slack_client.users_conversations') as users_conversations:

      users_conversations.return_value = {
        'ok': True,
        'channels': [
          {
            'name': 'channel-1',
          },
          {
            'name': 'channel-2',
          }
        ],
        "response_metadata": {
          "next_cursor": "",
        }
      }

      response = self.client.get(reverse('botserver.api.get_channels'))
      data = json.loads(response.content)

      assert_equal(200, response.status_code)
      assert_equal(['channel-1', 'channel-2'], data.get('channels'))

  def test_send_message(self):
    with patch('desktop.lib.botserver.api.slack_client.chat_postMessage') as chat_postMessage:

      chat_postMessage.return_value = {
         "ok": True,
      }

      response = self.client.post(reverse('botserver.api.send_message'), {'channel': 'channel-1', 'message': 'message with link'})
      data = json.loads(response.content)

      assert_equal(200, response.status_code)
      chat_postMessage.assert_called_with(channel='channel-1', text='@api_user: message with link')
      assert_true(data.get('ok'))