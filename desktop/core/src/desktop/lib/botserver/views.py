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
from pprint import pprint

from django.shortcuts import render
from django.http import HttpResponse
from desktop.lib.django_util import login_notrequired, JsonResponse
from desktop import conf
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from slack_sdk import WebClient

LOG = logging.getLogger(__name__)

SLACK_VERIFICATION_TOKEN = conf.SLACK.SLACK_VERIFICATION_TOKEN.get()
SLACK_BOT_USER_TOKEN = conf.SLACK.SLACK_BOT_USER_TOKEN.get()


slack_client = WebClient(token=SLACK_BOT_USER_TOKEN)
appname = "hue_bot"


@login_notrequired
@csrf_exempt
def slack_events(request):
  slack_message = json.loads(request.body.decode('utf-8'))

  if slack_message['token'] != SLACK_VERIFICATION_TOKEN:
    return HttpResponse(status=403)

  # challenge verification
  if slack_message['type'] == 'url_verification':
    response_dict = {"challenge": slack_message.get('challenge')}
    return JsonResponse(response_dict, status=200)
  
  if 'event' in slack_message:
    event_message = slack_message['event']
    parse_events(event_message)

  return HttpResponse(status=200)

def parse_events(event_message):
  user_id = event_message.get('user')
  text = event_message.get('text')
  channel = event_message.get('channel')
  BOT_ID = get_bot_id(appname)

  # ignore bot's own message
  if BOT_ID == user_id:
    return HttpResponse(status=200)

  if 'hello hue' in text.lower():
    say_hi_user(channel, user_id)
  
def say_hi_user(channel, user_id):
  # App greets when user says "hello hue"
  bot_message = f'Hi <@{user_id}> :wave:'
  slack_client.api_call(api_method='chat.postMessage', json={'channel': channel, 'text': bot_message})
  return HttpResponse(status=200)

def get_bot_id(botusername):
  response = slack_client.api_call('users.list')
  users = response['members']
  for user in users:
    if 'name' in user and botusername in user.get('name') and not user.get('deleted'):
      return user.get('id')
