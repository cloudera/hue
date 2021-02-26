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

import logging
import json
from urllib.parse import urlsplit
from pprint import pprint

from desktop import conf
from desktop.conf import ENABLE_GIST_PREVIEW
from desktop.lib.django_util import login_notrequired, JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document2, _get_gist_document

from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

LOG = logging.getLogger(__name__)

SLACK_VERIFICATION_TOKEN = conf.SLACK.SLACK_VERIFICATION_TOKEN.get()
SLACK_BOT_USER_TOKEN = conf.SLACK.SLACK_BOT_USER_TOKEN.get()

slack_client = None
if conf.SLACK.IS_ENABLED.get():
  from slack_sdk import WebClient
  slack_client = WebClient(token=SLACK_BOT_USER_TOKEN)


@login_notrequired
@csrf_exempt
def slack_events(request):
  try:
    slack_message = json.loads(request.body)
    
    if slack_message['token'] != SLACK_VERIFICATION_TOKEN:
      return HttpResponse(status=403)

    # challenge verification
    if slack_message['type'] == 'url_verification':
      response_dict = {"challenge": slack_message['challenge']}
      return JsonResponse(response_dict, status=200)
    
    if 'event' in slack_message:
      event_message = slack_message['event']
      parse_events(event_message)
  except ValueError as err:
    raise PopupException(_("Response content is not valid JSON"), detail=err)

  return HttpResponse(status=200)


def parse_events(event):
  """
  Parses the event according to its 'type'.

  """
  channel_id = event.get('channel')
  if event.get('type') == 'message':
    handle_on_message(channel_id, event.get('bot_id'), event.get('text'), event.get('user'))

  if event.get('type') == 'link_shared':
    handle_on_link_shared(channel_id, event.get('message_ts'), event.get('links'))


def handle_on_message(channel_id, bot_id, text, user_id):
  # ignore bot's own message since that will cause an infinite loop of messages if we respond.
  if bot_id:
    return HttpResponse(status=200)
  
  if slack_client:
    if text and 'hello hue' in text.lower():
      response = say_hi_user(channel_id, user_id)

      if not response['ok']:
        raise PopupException(_("Error posting message"), detail=response["error"])


def handle_on_link_shared(channel_id, message_ts, links):
  for item in links:
    path = urlsplit(item['url'])[2]
    queryid_or_uuid = urlsplit(item['url'])[3]  # if /hue/editor/ then query_id else if /hue/gist then uuid

    if path == '/hue/editor':
      query_id = queryid_or_uuid.split('=')[1]
      doc2 = Document2.objects.get(id=query_id)
      doc2_data = json.loads(doc2.data)

      statement = doc2_data['snippets'][0]['statement_raw']
      dialect = doc2_data['dialect'].capitalize()
      database = doc2_data['snippets'][0]['database'].capitalize()
      
      payload = make_query_history_payload(item['url'], statement, dialect, database)
      response = slack_client.chat_unfurl(channel=channel_id, ts=message_ts, unfurls=payload)
      if response['ok']:
        raise PopupException(_("Cannot unfurl query history link"), detail=response["error"])

    if path == '/hue/gist' and ENABLE_GIST_PREVIEW.get():
      gist_uuid = queryid_or_uuid.split('=')[1]
      gist_doc = _get_gist_document(uuid=gist_uuid)
      gist_doc_data = json.loads(gist_doc.data)

      statement = gist_doc_data['statement_raw']
      created_by = gist_doc.owner.get_full_name() or gist_doc.owner.username
      dialect = gist_doc.extra.capitalize()
      
      payload = make_gist_payload(item['url'], statement, dialect, created_by)
      response = slack_client.chat_unfurl(channel=channel_id, ts=message_ts, unfurls=payload)
      if not response['ok']:
        raise PopupException(_("Cannot unfurl gist link"), detail=response["error"])

def say_hi_user(channel_id, user_id):
  """
  Sends Hi<user_id> message in a specific channel.

  """
  bot_message = 'Hi <@{}> :wave:'.format(user_id)
  return slack_client.api_call(api_method='chat.postMessage', json={'channel': channel_id, 'text': bot_message})


def make_gist_payload(url, statement, dialect, created_by):
  gist_payload = {
    url: {
      "color": "#025BA6",
      "blocks": [
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "\n*<{}|Hue - SQL Gist>*".format(url)
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": statement if len(statement) < 150 else (statement[:150] + '...')
          }
        },
        {
          "type": "section",
          "fields": [
            {
              "type": "mrkdwn",
              "text": "*Dialect:*\n{}".format(dialect)
            },
            {
              "type": "mrkdwn",
              "text": "*Created By:*\n{}".format(created_by)
            }
          ]
        }
      ]
    }
  }
  return gist_payload


def make_query_history_payload(url, statement, dialect, database):
  payload = {
    url: {
      "color": "#025BA6",
      "blocks": [
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "\n*<{}|Hue - SQL Editor>*".format(url)
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": statement if len(statement) < 150 else (statement[:150] + '...')
          }
        },
        {
          "type": "section",
          "fields": [
            {
              "type": "mrkdwn",
              "text": "*Dialect:*\n{}".format(dialect)
            },
            {
              "type": "mrkdwn",
              "text": "*Database:*\n{}".format(database)
            }
          ]
        }
      ]
    }
  }
  return payload

