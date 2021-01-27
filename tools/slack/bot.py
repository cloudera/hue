import os
from slack_sdk import WebClient
from pathlib import Path
from dotenv import load_dotenv
 
load_dotenv()
 
client = WebClient(token = os.getenv('SLACK_BOT_TOKEN'))
 
try:
  client.chat_postMessage(channel = '#dev-hue-bot', text = "test")
 
except SlackApiError as err:
  # You will get a SlackApiError if "ok" is False
  assert err.response["error"] # str like 'invalid_auth', 'channel_not_found'