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
  
  def setUp(self):
    # Slack user email: test@example.com
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")

    # Other slack user email: test_not_me@example.com
    self.client_not_me = make_logged_in_client(username="test_not_me", groupname="default", recreate=True, is_superuser=False)
    self.user_not_me = User.objects.get(username="test_not_me")

  def test_send_hi_user(self):
    with patch('desktop.lib.botserver.views.slack_client.api_call') as api_call:
      api_call.return_value = {
        "ok": True
      }
      send_hi_user("channel", "user_id")
      api_call.assert_called_with(api_method='chat.postMessage', json={'channel': 'channel', 'text': 'Hi <@user_id> :wave:'})

      api_call.side_effect = PopupException('message')
      assert_raises(PopupException, send_hi_user, "channel", "user_id")

  def test_handle_on_message(self):
    with patch('desktop.lib.botserver.views.send_hi_user') as say_hi_user:
      
      response = handle_on_message("channel", "bot_id", "text", "user_id")
      assert_equal(response.status_code, 200)
      assert_false(say_hi_user.called)
      
      handle_on_message("channel", None, None, "user_id")
      assert_false(say_hi_user.called)

      handle_on_message("channel", None, "text", "user_id")
      assert_false(say_hi_user.called)

      handle_on_message("channel", None, "hello hue test", "user_id")
      assert_true(say_hi_user.called)
  
  def test_handle_query_history_link(self):
    with patch('desktop.lib.botserver.views.slack_client.chat_unfurl') as chat_unfurl:
      with patch('desktop.lib.botserver.views._make_unfurl_payload') as mock_unfurl_payload:
        with patch('desktop.lib.botserver.views.send_result_file') as send_result_file:
          with patch('desktop.lib.botserver.views.slack_client.users_info') as users_info:

            channel_id = "channel"
            message_ts = "12.1"
            user_id = "<@user_id>"

            links = [{"url": "https://demo.gethue.com/hue/editor?editor=12345"}]
            doc_data = {
              "dialect": "mysql",
              "snippets": [{
                "database": "hue",
                "statement_raw": "SELECT 5000",
              }]
            }
            doc = Document2.objects.create(id=12345, data=json.dumps(doc_data), owner=self.user)
            mock_unfurl_payload.return_value = {
              'payload': {},
              'file_status': True,
            }

            # Slack user is Hue user but without read access sends link
            users_info.return_value = {
              "ok": True,
              "user": {
                "profile": {
                  "email": "test_not_me@example.com"
                }
              }
            }
            assert_raises(PopupException, handle_on_link_shared, "channel", "12.1", links, "<@user_id>")

            # Slack user is Hue user with read access sends link
            doc.update_permission(self.user, is_link_on=True)
            handle_on_link_shared(channel_id, message_ts, links, user_id)

            assert_true(chat_unfurl.called)
            assert_true(send_result_file.called)

            # Document does not exist
            qhistory_url = "https://demo.gethue.com/hue/editor?editor=109644"
            assert_raises(PopupException, handle_on_link_shared, "channel", "12.1", [{"url": qhistory_url}], "<@user_id>")

            # Cannot unfurl link with invalid query link
            inv_qhistory_url = "https://demo.gethue.com/hue/editor/?type=4"
            assert_raises(PopupException, handle_on_link_shared, "channel", "12.1", [{"url": inv_qhistory_url}], "<@user_id>")

  def test_handle_gist_link(self):
    with patch('desktop.lib.botserver.views.slack_client.chat_unfurl') as chat_unfurl:
      with patch('desktop.lib.botserver.views._make_unfurl_payload') as mock_unfurl_payload:
        with patch('desktop.lib.botserver.views._get_gist_document') as _get_gist_document:
          with patch('desktop.lib.botserver.views.slack_client.users_info') as users_info:
            with patch('desktop.lib.botserver.views.send_result_file') as send_result_file:

              channel_id = "channel"
              message_ts = "12.1"
              user_id = "<@user_id>"

              doc_data = {"statement_raw": "SELECT 98765"}
              links = [{"url": "http://demo.gethue.com/hue/gist?uuid=some_uuid"}]
              _get_gist_document.return_value = Mock(data=json.dumps(doc_data), owner=self.user, extra='mysql')
              mock_unfurl_payload.return_value = {
                'payload': {},
                'file_status': False,
              }

              # Slack user who is Hue user sends link
              users_info.return_value = {
                "ok": True,
                "user": {
                  "profile": {
                    "email": "test_not_me@example.com"
                  }
                }
              }
              handle_on_link_shared(channel_id, message_ts, links, user_id)

              assert_true(chat_unfurl.called)
              assert_false(send_result_file.called)

              # Gist document does not exist
              _get_gist_document.side_effect = PopupException('Gist does not exist')
              gist_url = "https://demo.gethue.com/hue/gist?uuid=6d1c407b-d999-4dfd-ad23-d3a46c19a427"

              assert_raises(PopupException, handle_on_link_shared, "channel", "12.1", [{"url": gist_url}], "<@user_id>")

              # Cannot unfurl with invalid gist link
              inv_gist_url = "http://demo.gethue.com/hue/gist?uuids/=invalid_link"
              assert_raises(PopupException, handle_on_link_shared, "channel", "12.1", [{"url": inv_gist_url}], "<@user_id>")

  def test_slack_user_not_hue_user(self):
    with patch('desktop.lib.botserver.views.slack_client.users_info') as users_info:
      with patch('desktop.lib.botserver.views._get_gist_document') as _get_gist_document:
        
        # Can be checked similarly with query link too
        doc_data = {"statement_raw": "SELECT 98765"}
        links = [{"url": "http://demo.gethue.com/hue/gist?uuid=some_uuid"}]
        _get_gist_document.return_value = Mock(data=json.dumps(doc_data), owner=self.user, extra='mysql')

        users_info.return_value = {
          "ok": True,
          "user": {
            "profile": {
              "email": "test_user_not_exist@example.com"
            }
          }
        }
        assert_raises(PopupException, handle_on_link_shared, "channel", "12.1", links, "<@user_id>")