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
import urllib.parse
from pprint import pprint

from desktop import conf
from desktop.lib.django_util import login_notrequired, JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document2

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
  except ValueError as e:
    raise PopupException(_("Response content is not valid JSON"), detail=e)

  return HttpResponse(status=200)


def parse_events(event):
  """
  Parses the event according to its 'type'.
  """

  # To-do: Creating function for every type to de-congest
  if event.get('type') == 'message':
    user_id = event.get('user')
    text = event.get('text')
    channel = event.get('channel')

    # ignore bot's own message since that will cause an infinite loop of messages if we respond.
    if event.get('bot_id'):
      return HttpResponse(status=200)
    
    if slack_client:
      if text and 'hello hue' in text.lower():
        response = say_hi_user(channel, user_id)
        if response['ok']:
          return HttpResponse(status=200)
        else:
          raise PopupException(response["error"])

  if event.get('type') == 'link_shared':
    channel_id = event.get('channel')
    message_ts = event.get('message_ts')
    links = event.get('links')

    for item in links:
      path = urllib.parse.urlsplit(item['url'])[2]
      queryid_or_uuid = urllib.parse.urlsplit(item['url'])[3]  # if /hue/editor/ then query_id else if /hue/gist then uuid

      if path == '/hue/editor':
        query_id = queryid_or_uuid.split('=')[1]
        doc2 = Document2.objects.get(id=query_id)
        doc2_data = json.loads(doc2.data)

        query_statement = doc2_data['snippets'][0]['statement_raw']
        dialect = doc2_data['dialect']
        database = doc2_data['snippets'][0]['database']

        payload = {
          item['url']: {
            "blocks": [
              {
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "\n*<{}|Hue - SQL Editor>*".format((item['url']))
                }
              },
              {
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": query_statement
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

        response = slack_client.chat_unfurl(channel=channel_id, ts=message_ts, unfurls=payload)

def say_hi_user(channel, user_id):
  """
  Sends Hi<user_id> message in a specific channel.
  """
 
  bot_message = 'Hi <@{}> :wave:'.format(user_id)
  return slack_client.api_call(api_method='chat.postMessage', json={'channel': channel, 'text': bot_message})