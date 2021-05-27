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
import sys

from desktop.lib.botserver.slack_client import slack_client
from desktop.lib.exceptions_renderable import PopupException
from desktop.decorators import api_error_handler
from desktop.lib.django_util import JsonResponse

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _

LOG = logging.getLogger(__name__)

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

def _send_message(channel_info, message=None, block_element=None):
  try:
    return slack_client.chat_postMessage(channel=channel_info, text=message, blocks=block_element)
  except Exception as e:
    raise PopupException(_("Error posting message in channel"), detail=e)