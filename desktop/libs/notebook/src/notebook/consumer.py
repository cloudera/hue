from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):

  async def connect(self):
    await self.accept()

    await self.send(text_data=json.dumps({
      'type': 'channel_name',
      'data': self.channel_name,
      'accept': True
    }))


  async def task_progress(self, event):
    await self.send(text_data=json.dumps({
      'type': 'task_progress',
      'data': event["data"]
    }))


def _send_to_channel(channel_name, message_type, message_data):
  channel_layer = get_channel_layer()
  async_to_sync(channel_layer.send)(channel_name, {
      "type": message_type,
      "data": message_data,
  })
