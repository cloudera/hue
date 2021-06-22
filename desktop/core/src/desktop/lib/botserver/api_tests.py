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

    self.hostname = 'testserver.gethue.com'

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
      chat_postMessage.assert_called_with(channel='channel-1', text='@api_user: message with link', blocks=None, thread_ts=None)
      assert_true(data.get('ok'))
  
  def test_generate_slack_install_link(self):
    response = self.client.get(reverse('api:botserver.api.slack_install_link') + '/?hostname=' + self.hostname)
    data = json.loads(response.content)

    assert_equal(200, response.status_code)
    assert_equal(
      data.get('link'),
      ('https://api.slack.com/apps?new_app=1&manifest_yaml=_metadata%3A%0A++major_version%3A+1%0A++minor_version%3A+1%0Adisplay_information'
      '%3A%0A++background_color%3A+%27%23000000%27%0A++description%3A+Share+queries%2C+ask+where+is+the+data%2C+how+to+query+it..+questions.'
      '%0A++name%3A+SQL+Assistant%0Afeatures%3A%0A++app_home%3A%0A++++home_tab_enabled%3A+false%0A++++messages_tab_enabled%3A+false%0A++++'
      'messages_tab_read_only_enabled%3A+true%0A++bot_user%3A%0A++++always_online%3A+true%0A++++display_name%3A+Hue%0A++unfurl_domains%3A%'
      '0A++-+testserver.gethue.com%0Aoauth_config%3A%0A++scopes%3A%0A++++bot%3A%0A++++-+app_mentions%3Aread%0A++++-+channels%3Ahistory%0A'
      '++++-+channels%3Aread%0A++++-+chat%3Awrite%0A++++-+files%3Awrite%0A++++-+links%3Aread%0A++++-+links%3Awrite%0A++++-+users%3Aread%0'
      'A++++-+users%3Aread.email%0Asettings%3A%0A++event_subscriptions%3A%0A++++bot_events%3A%0A++++-+app_mention%0A++++-+link_shared%0A'
      '++++-+message.channels%0A++++request_url%3A+https%3A%2F%2Ftestserver.gethue.com%2Fdesktop%2Fslack%2Fevents%2F%0A++is_hosted%3A+false%'
      '0A++org_deploy_enabled%3A+false%0A++socket_mode_enabled%3A+false%0A')
    )
