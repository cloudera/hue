import os
from slack_sdk import WebClient
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter

#Create .env file and load it
load_dotenv()
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.getenv('SIGNING_SECRET'), '/slack/events', app)
 
client = WebClient(token=os.getenv('SLACK_BOT_TOKEN')) # Add SLACK_BOT_TOKEN in .env
BOT_ID = client.api_call('auth.test')['user_id']
 
@slack_event_adapter.on('message')
def message(payload):
  """Greets the user if user says hello hue, 
  else sends the same message as reply """
  event = payload.get('event', {}) # Get event else return empty dictionary
  channel_id = event.get('channel')
  user_id = event.get('user')
  text = event.get('text')
 
  if BOT_ID != user_id:
    if "hello hue" in text.lower():
      text = f'Hello <@{user_id}> :wave:'
    client.chat_postMessage(channel=channel_id, text=text)
 
if __name__ == '__main__':
  app.run(debug=True)