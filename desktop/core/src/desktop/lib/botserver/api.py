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
import yaml
import sys
import os
from urllib.parse import quote_plus

from desktop.lib.botserver.slack_client import slack_client
from desktop.lib.exceptions_renderable import PopupException
from desktop.decorators import api_error_handler
from desktop.lib.django_util import JsonResponse, login_notrequired
from desktop.settings import BASE_DIR

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _

LOG = logging.getLogger()

@api_error_handler
def get_channels(request):

  try:
    response = slack_client.users_conversations()
  except Exception as e:
    raise PopupException(_('Error fetching channels where bot is present'), detail=e)

  bot_channels = [channel.get('name') for channel in response.get('channels')]

  return JsonResponse({
    'channels': bot_channels,
  })

@api_error_handler
def send_message(request):
  channel = request.POST.get('channel')
  message = request.POST.get('message')

  message = '@' + (request.user.get_full_name() or request.user.username) + ': ' + message
  slack_response = _send_message(channel, message)

  return JsonResponse({
    'ok': slack_response.get('ok'),
  })

@login_notrequired
@api_error_handler
def generate_slack_install_link(request):
  hostname = request.GET.get('hostname')
  hostname_without_port = hostname.split(':')[0] if ':' in hostname else hostname

  install_link = 'https://api.slack.com/apps?new_app=1&manifest_yaml='

  with open(os.path.join(BASE_DIR, 'tools/slack/manifest.yml')) as manifest:
    data = yaml.safe_load(manifest)

    data['features']['unfurl_domains'] = [hostname_without_port]
    data['settings']['event_subscriptions']['request_url'] = 'https://' + hostname + '/desktop/slack/events/'

    changed_data = yaml.safe_dump(data)
    install_link += quote_plus(changed_data)

  return JsonResponse({'link': install_link})

def _send_message(channel_info, message=None, block_element=None, message_ts=None):
  try:
    return slack_client.chat_postMessage(channel=channel_info, text=message, blocks=block_element, thread_ts=message_ts)
  except Exception as e:
    raise PopupException(_("Error posting message in channel"), detail=e)