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

    # Slack user: test
    cls.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    cls.user = User.objects.get(username="test")

    # Other slack user: test_not_me
    cls.client_not_me = make_logged_in_client(username="test_not_me", groupname="default", recreate=True, is_superuser=False)
    cls.user_not_me = User.objects.get(username="test_not_me")

  def setUp(self):
    self.host_domain = 'testserver.gethue.com'
    self.is_http_secure = True # https if true else http

    self.email_domain = '.'.join(self.host_domain.split('.')[-2:])

  def test_handle_on_message(self):
    with patch('desktop.lib.botserver.views._send_message') as _send_message:
      with patch('desktop.lib.botserver.views.detect_select_statement') as detect_select_statement:
      
        channel_id = "channel"
        bot_id = "bot_id"
        user_id = "user_id"
        message_element = [{
          'elements': [{
            'text': 'hello hue test'
          }]
        }]

        # Bot sending message
        response = handle_on_message(self.host_domain, self.is_http_secure, channel_id, bot_id, message_element, user_id)
        assert_equal(response.status_code, 200)
        assert_false(_send_message.called)

        # Greeting user
        handle_on_message(self.host_domain, self.is_http_secure, channel_id, None, message_element, user_id)
        _send_message.assert_called_with(channel_id, 'Hi <@user_id> :wave:')

        # Detect SQL
        message_element = [
          {
            'elements': [{
              'text': 'Hi Team, need help with query',
            }],
          },
          {
            'elements': [{
              'text': 'SELECT 1',
            }],
          },
        ]

        handle_on_message(self.host_domain, self.is_http_secure, channel_id, None, message_element, user_id)
        detect_select_statement.assert_called_with(self.host_domain, self.is_http_secure, channel_id, user_id, 'select 1')

  def test_detect_select_statement(self):
    with patch('desktop.lib.botserver.views.check_slack_user_permission') as check_slack_user:
      with patch('desktop.lib.botserver.views.get_user') as get_user:
        with patch('desktop.lib.botserver.views.get_cluster_config') as get_cluster_config:
          with patch('desktop.lib.botserver.views._send_message') as _send_message:
            with patch('desktop.lib.botserver.views._gist_create') as _gist_create:

              channel_id = "channel"
              user_id = "user_id"
              statement = 'select 1'

              get_user.return_value = self.user

              get_cluster_config.return_value = {
                'default_sql_interpreter': 'hive'
              }
              _gist_create.return_value = {
                'link': 'gist_link'
              }

              detect_select_statement(self.host_domain, self.is_http_secure, channel_id, user_id, statement)
              _send_message.assert_called_with(
                channel_id, 
                ('Hi <@user_id>\n'
                'Looks like you are copy/pasting SQL, instead now you can send Editor links which unfurls in a rich preview!\n'
                'Here is the gist link\n gist_link')
              )

  def test_handle_query_history_link(self):
    with patch('desktop.lib.botserver.views.slack_client.chat_unfurl') as chat_unfurl:
      with patch('desktop.lib.botserver.views._check_status') as check_status:
        with patch('desktop.lib.botserver.views.send_result_file') as send_result_file:
          with patch('desktop.lib.botserver.views.slack_client.users_info') as users_info:
            with patch('desktop.lib.botserver.views._query_result') as query_result:
              with patch('desktop.lib.botserver.views._make_result_table') as result_table:

                channel_id = "channel"
                message_ts = "12.1"
                user_id = "<@user_id>"

                doc_data = {
                  "dialect": "mysql",
                  "snippets": [{
                    "statement_raw": "SELECT 5000",
                  }],
                  'uuid': 'doc uuid'
                }
                doc = Document2.objects.create(data=json.dumps(doc_data), owner=self.user)
                links = [{"url": "https://{host_domain}/hue/editor?editor=".format(host_domain=self.host_domain) + str(doc.id)}]

                # Slack user is Hue user but without read access sends link
                users_info.return_value = {
                  "ok": True,
                  "user": {
                    "is_bot": False,
                    "profile": {
                      "email": "test_not_me@{domain}".format(domain=self.email_domain)
                    }
                  }
                }
                assert_raises(PopupException, handle_on_link_shared, self.host_domain, "channel", "12.1", links, "<@user_id>")

                # Slack user is Hue user with read access sends link
                doc.update_permission(self.user, is_link_on=True)

                check_status.return_value = {'query_status': {'status': 'available'}, 'status': 0}
                query_result.return_value = {
                  'data': [[5000]],
                  'meta': [{'comment': '', 'name': '5000', 'type': 'INT_TYPE'}],
                }
                result_table.return_value = '  Columns(1)\n------------  ----\n        5000  5000'

                handle_on_link_shared(self.host_domain, channel_id, message_ts, links, user_id)

                query_preview = {
                  links[0]['url']: {
                  "color": "#025BA6",
                  "blocks": [
                    {
                      "type": "section",
                      "text": {
                        "type": "mrkdwn",
                        "text": "\n*<{url}|Open  query of mysql dialect created by test in Hue>*".format(url=links[0]['url']),
                        }
                    },
                    {
                      "type": "divider",
                    },
                    {
                      "type": "section",
                      "text": {
                        "type": "mrkdwn",
                        "text": "*Statement:*\n```SELECT 5000```",
                        }
                      },
                      {
                        'type': 'section',
                        'text': {
                          'type': 'mrkdwn',
                          'text': "*Query result:*\n```  Columns(1)\n------------  ----\n        5000  5000```",
                        }
                      }
                    ]
                  }
                }

                chat_unfurl.assert_called_with(channel=channel_id, ts=message_ts, unfurls=query_preview)
                assert_true(send_result_file.called)

                # Document does not exist
                qhistory_url = "https://{host_domain}/hue/editor?editor=109644".format(host_domain=self.host_domain)
                assert_raises(PopupException, handle_on_link_shared, self.host_domain, "channel", "12.1", [{"url": qhistory_url}], "<@user_id>")

                # Cannot unfurl link with invalid query link
                inv_qhistory_url = "https://{host_domain}/hue/editor/?type=4".format(host_domain=self.host_domain)
                assert_raises(PopupException, handle_on_link_shared, self.host_domain, "channel", "12.1", [{"url": inv_qhistory_url}], "<@user_id>")

  def test_handle_gist_link(self):
    with patch('desktop.lib.botserver.views.slack_client.chat_unfurl') as chat_unfurl:
      with patch('desktop.lib.botserver.views.slack_client.users_info') as users_info:
        with patch('desktop.lib.botserver.views.send_result_file') as send_result_file:

          channel_id = "channel"
          message_ts = "12.1"
          user_id = "<@user_id>"

          doc_data = {"statement_raw": "SELECT 98765"}
          gist_doc = Document2.objects.create(
            name='Mysql Query',
            type='gist',
            owner=self.user,
            data=json.dumps(doc_data),
            extra='mysql'
          )
          links = [{"url": "https://{host_domain}/hue/gist?uuid=".format(host_domain=self.host_domain) + gist_doc.uuid}]

          # Slack user who is Hue user sends link
          users_info.return_value = {
            "ok": True,
            "user": {
              "is_bot": False,
              "profile": {
                "email": "test@{domain}".format(domain=self.email_domain)
              }
            }
          }
          handle_on_link_shared(self.host_domain, channel_id, message_ts, links, user_id)

          gist_preview = {
            links[0]['url']: {
            "color": "#025BA6",
            "blocks": [
              {
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "\n*<{url}|Open Mysql Query gist of mysql dialect created by test in Hue>*".format(url=links[0]['url']),
                  }
              },
              {
                "type": "divider",
              },
              {
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "*Statement:*\n```SELECT 98765```",
                  }
                },
              ]
            }
          }

          chat_unfurl.assert_called_with(channel=channel_id, ts=message_ts, unfurls=gist_preview)
          assert_false(send_result_file.called)

          # Gist link sent directly from Hue to Slack via bot
          users_info.return_value = {
            "ok": True,
            "user": {
              "is_bot": True,
            }
          }
          handle_on_link_shared(self.host_domain, channel_id, message_ts, links, user_id)

          chat_unfurl.assert_called_with(channel=channel_id, ts=message_ts, unfurls=gist_preview)
          assert_false(send_result_file.called)

          # Gist document does not exist
          gist_url = "https://{host_domain}/hue/gist?uuid=6d1c407b-d999-4dfd-ad23-d3a46c19a427".format(host_domain=self.host_domain)
          assert_raises(PopupException, handle_on_link_shared, self.host_domain, "channel", "12.1", [{"url": gist_url}], "<@user_id>")

          # Cannot unfurl with invalid gist link
          inv_gist_url = "https://{host_domain}/hue/gist?uuids/=invalid_link".format(host_domain=self.host_domain)
          assert_raises(PopupException, handle_on_link_shared, self.host_domain, "channel", "12.1", [{"url": inv_gist_url}], "<@user_id>")

  def test_slack_user_not_hue_user(self):
    with patch('desktop.lib.botserver.views.slack_client.users_info') as users_info:
      with patch('desktop.lib.botserver.views._get_gist_document') as _get_gist_document:
        with patch('desktop.lib.botserver.views.slack_client.chat_postMessage') as chat_postMessage:
        
          # Can be checked similarly with query link too
          doc_data = {"statement_raw": "SELECT 98765"}
          links = [{"url": "https://{host_domain}/hue/gist?uuid=some_uuid".format(host_domain=self.host_domain)}]
          _get_gist_document.return_value = Mock(data=json.dumps(doc_data), owner=self.user, extra='mysql')

          # Same domain but diff email prefix
          users_info.return_value = {
            "ok": True,
            "user": {
              "is_bot": False,
              "profile": {
                "email": "test_user_not_exist@{domain}".format(domain=self.email_domain)
              }
            }
          }
          assert_raises(PopupException, handle_on_link_shared, self.host_domain, "channel", "12.1", links, "<@user_id>")

          # Different domain but same email prefix
          users_info.return_value = {
            "ok": True,
            "user": {
              "is_bot": False,
              "profile": {
                "email": "test@example.com"
              }
            }
          }
          assert_raises(PopupException, handle_on_link_shared, self.host_domain, "channel", "12.1", links, "<@user_id>")