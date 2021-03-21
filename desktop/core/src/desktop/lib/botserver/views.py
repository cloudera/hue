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
from tabulate import tabulate

from desktop import conf
from desktop.conf import ENABLE_GIST_PREVIEW
from desktop.lib.django_util import login_notrequired, JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document2, _get_gist_document
from desktop.auth.backend import rewrite_user

from notebook.api import _fetch_result_data, _check_status, _execute_notebook
from notebook.models import MockRequest, get_api
from notebook.connectors.base import _get_snippet_name

from useradmin.models import User

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
  # Ignore bot's own message since that will cause an infinite loop of messages if we respond.
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
    id_type, qid = urlsplit(item['url'])[3].split('=')

    try:
      if path == '/hue/editor' and id_type == 'editor':
        doc = Document2.objects.get(id=qid)
        doc_type = 'Query'
      elif path == '/hue/gist' and id_type == 'uuid' and ENABLE_GIST_PREVIEW.get():
        doc = _get_gist_document(uuid=qid)
        doc_type = 'Gist'
      else:
        raise PopupException(_("Cannot unfurl link"))
    except Document2.DoesNotExist:
      msg = "Document with {key}={value} does not exist".format(key='uuid' if id_type == 'uuid' else 'id', value=qid)
      raise PopupException(_(msg))

    # Mock request for query execution and fetch result
    user = rewrite_user(User.objects.get(username=doc.owner.username))
    request = MockRequest(user=user)

    payload = _make_unfurl_payload(request, item['url'], id_type, doc, doc_type)
    response = slack_client.chat_unfurl(channel=channel_id, ts=message_ts, unfurls=payload['payload'])
    if not response['ok']:
      raise PopupException(_("Cannot unfurl link"), detail=response["error"])
    
    # Generate and upload result xlsx file only if result available
    if payload['file_status']:
      notebook = json.loads(doc.data)
      snippet = notebook['snippets'][0]
      snippet['statement'] = notebook['snippets'][0]['statement_raw']
      file_format = 'xlsx'
      file_name = _get_snippet_name(notebook)

      content_generator = get_api(request, snippet).download(notebook, snippet, file_format='xls')

      response = slack_client.files_upload(
        channels=channel_id, 
        file=next(content_generator), 
        thread_ts=message_ts,
        filetype=file_format,
        filename='{}.{}'.format(file_name, file_format),
        initial_comment='Here is your result file!'
        )

def _query_result(request, notebook, max_rows):
  snippet = notebook['snippets'][0]
  snippet['statement'] = notebook['snippets'][0]['statement_raw']

  query_execute = _execute_notebook(request, notebook, snippet)

  history_uuid = query_execute['history_uuid']
  status = _check_status(request, operation_id=history_uuid)
  if status['query_status']['status'] == 'available':
    res = _fetch_result_data(request, operation_id=history_uuid, rows=max_rows)
    return res['result']

  return None


def _make_result_table(result):
  # Make result pivot table
  table = []
  meta = result['meta']
  data = result['data']

  for idx, column in enumerate(meta):
    pivot_row = []
    pivot_row.append(column['name'])
    for row_data in data:
      # Replace non-breaking space HTML entity with whitespace
      if isinstance(row_data[idx], str):
        row_data[idx] = row_data[idx].replace('&nbsp;', ' ') 
      pivot_row.append(row_data[idx])

    table.append(pivot_row)

  return tabulate(table, headers=['Columns({})'.format(idx+1), '', ''], tablefmt="simple")


def _make_unfurl_payload(request, url, id_type, doc, doc_type):
  doc_data = json.loads(doc.data)
  statement = doc_data['snippets'][0]['statement_raw'] if id_type == 'editor' else doc_data['statement_raw']
  dialect = doc_data['dialect'] if id_type == 'editor' else doc.extra
  created_by = doc.owner.get_full_name() or doc.owner.username
  name = doc.name or dialect

  file_status = False

  if id_type == 'editor':
    max_rows = 2
    unfurl_result = 'Query result has expired or could not be found'
    try:
      status = _check_status(request, operation_id=doc_data['uuid'])
      if status['query_status']['status'] == 'available':
        fetch_result = _query_result(request, json.loads(doc.data), max_rows)
        if fetch_result is not None:
          unfurl_result = _make_result_table(fetch_result)
          file_status = True
    except:
      pass
  else:
    unfurl_result = 'Result is not available for Gist'

  payload = {
    url: {
      "color": "#025BA6",
      "blocks": [
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "\n*<{}|Open {} {} in Hue - SQL Editor>*".format(url, name, doc_type)
          }
        },
        {
          "type": "divider"
				},
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*Statement:*\n```{}```".format(statement if len(statement) < 150 else (statement[:150] + '...'))
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
              "text": "*Created by:*\n{}".format(created_by)
            }
          ]
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*Query result:*\n```{}```".format(unfurl_result),
          }
				}
      ]
    }
  }

  return {'payload': payload, 'file_status': file_status}


def say_hi_user(channel_id, user_id):
  """
  Sends Hi<user_id> message in a specific channel.

  """
  bot_message = 'Hi <@{}> :wave:'.format(user_id)
  return slack_client.api_call(api_method='chat.postMessage', json={'channel': channel_id, 'text': bot_message})