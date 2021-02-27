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

from nose.tools import assert_equal, assert_true, assert_false, assert_raises
from nose.plugins.skip import SkipTest
from django.test import TestCase

from desktop.lib.botserver.views import *
from desktop import conf
from desktop.models import Document2, _get_gist_document
from desktop.lib.django_test_util import make_logged_in_client
from useradmin.models import User


if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock

LOG = logging.getLogger(__name__)

class TestBotServer(unittest.TestCase):
  
  @classmethod
  def setUpClass(cls):
    if not conf.SLACK.IS_ENABLED.get():
      raise SkipTest

  def test_say_hi_user(self):
    with patch('desktop.lib.botserver.views.slack_client.api_call') as api_call:
      api_call.return_value = {
        "ok": True
      }
      response = say_hi_user("channel", "user_id")
      api_call.assert_called_with(api_method='chat.postMessage', json={'channel': 'channel', 'text': 'Hi <@user_id> :wave:'})
      assert_true(response['ok'])
  
  def test_handle_on_message(self):
    with patch('desktop.lib.botserver.views.say_hi_user') as say_hi_user:
      
      response = handle_on_message("channel", "bot_id", "text", "user_id")
      assert_equal(response.status_code, 200)
      assert_false(say_hi_user.called)
      
      handle_on_message("channel", None, None, "user_id")
      assert_false(say_hi_user.called)

      handle_on_message("channel", None, "text", "user_id")
      assert_false(say_hi_user.called)

      handle_on_message("channel", None, "hello hue test", "user_id")
      assert_true(say_hi_user.called)

  def test_handle_on_link_shared(self):
    with patch('desktop.lib.botserver.views.slack_client.chat_unfurl') as chat_unfurl:
      with patch('desktop.lib.botserver.views._make_unfurl_payload') as mock_unfurl_payload:
        with patch('desktop.lib.botserver.views.Document2.objects.get') as document2_objects_get:
          with patch('desktop.lib.botserver.views._get_gist_document') as _get_gist_document:
        
            client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
            user = User.objects.get(username="test")
            channel_id = "channel"
            message_ts = "12.1"

            # qhistory link
            links = [{"url": "https://demo.gethue.com/hue/editor?editor=123456"}]
            doc_data = {
              "dialect": "mysql",
              "snippets": [{
                "database": "hue",
                "statement_raw": "SELECT 5000",
              }]
            }
            document2_objects_get.return_value = Mock(data=json.dumps(doc_data), owner=user)
            handle_on_link_shared(channel_id, message_ts, links)
            mock_unfurl_payload.assert_called_with(links[0]["url"], "SELECT 5000", "Mysql", "test")
            assert_true(chat_unfurl.called)

            # gist link
            doc_data = {"statement_raw": "SELECT 98765"}
            _get_gist_document.return_value = Mock(data=json.dumps(doc_data), owner=user, extra='mysql')
            links = [{"url": "http://demo.gethue.com/hue/gist?uuid=random"}]
            handle_on_link_shared(channel_id, message_ts, links)
            mock_unfurl_payload.assert_called_with(links[0]["url"], "SELECT 98765", "Mysql", "test")
            assert_true(chat_unfurl.called)

            # Cannot unfurl link
            assert_raises(PopupException, handle_on_link_shared, "channel", "12.1", [{"url": "https://demo.gethue.com/hue/editor/?type=4"}])
            assert_raises(PopupException, handle_on_link_shared, "channel", "12.1", [{"url": "http://demo.gethue.com/hue/gist?uuids/=xyz"}])
