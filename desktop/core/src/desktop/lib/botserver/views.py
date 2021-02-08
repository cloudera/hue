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

from django.shortcuts import render
from django.http import HttpResponse
from desktop.lib.django_util import login_notrequired, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from slack_sdk import WebClient

LOG = logging.getLogger(__name__)

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)


Client = WebClient(token=SLACK_BOT_USER_TOKEN)
BOT_ID = Client.api_call('auth.test')['user_id']

@login_notrequired
@csrf_exempt
def slack_events(request):
  slack_message = json.loads(request.body.decode('utf-8'))

  if slack_message['token'] != SLACK_VERIFICATION_TOKEN:
    return HttpResponse(status=403)

  # verification challenge
  if slack_message['type'] == 'url_verification':
    response_dict = {"challenge": slack_message.get('challenge')}
    return JsonResponse(response_dict, status=200)
  

  # Bot greeting when User says "hello hue"
  if 'event' in slack_message:
    event_message = slack_message['event']
   
    user_id = event_message.get('user')

    # ignore bot's own message
    if BOT_ID == user_id:
      return HttpResponse(status=200) 
            
    # process user's message              
    text = event_message.get('text')                     
    channel = event_message.get('channel')

    bot_text = 'Hi <@{}> :wave:'.format(user_id)
    if 'hello hue' in text.lower():
      Client.api_call(api_method='chat.postMessage', json={'channel': channel,'text': bot_text})
      return HttpResponse(status=200)

  return HttpResponse(status=200)


  