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

from desktop.conf import has_channels


LOG = logging.getLogger()


if has_channels():
  from asgiref.sync import async_to_sync
  from channels.generic.websocket import AsyncWebsocketConsumer
  from channels.layers import get_channel_layer


  class EditorConsumer(AsyncWebsocketConsumer):

    async def connect(self):
      await self.accept()

      LOG.info('User %(user)s connected to WS Editor.' % self.scope)

      await self.send(
        text_data=json.dumps({
          'type': 'channel_name',
          'data': self.channel_name,
          'accept': True
        })
      )


    async def task_progress(self, event):
      await self.send(
        text_data=json.dumps({
          'type': 'query_progress',
          'data': event["data"]
        })
      )

    async def task_result(self, event):
      await self.send(
        text_data=json.dumps({
          'type': 'query_result',
          'data': event["data"]
        })
      )


  def _send_to_channel(channel_name, message_type, message_data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(
      channel_name, {
        "type": message_type,
        "data": message_data,
      }
    )
