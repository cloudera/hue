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
import os
from urllib.parse import urlsplit
from tabulate import tabulate

from desktop.lib.botserver.slack_client import slack_client, SLACK_VERIFICATION_TOKEN
from desktop.lib.botserver.api import _send_message
from desktop.lib.django_util import login_notrequired, JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document2, _get_gist_document, get_cluster_config
from desktop.api2 import _gist_create
from desktop.auth.backend import rewrite_user

from notebook.api import _fetch_result_data, _check_status, _execute_notebook
from notebook.models import MockRequest, get_api
from notebook.connectors.base import _get_snippet_name

from metadata.assistant.queries_utils import get_all_queries

from useradmin.models import User

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _

LOG = logging.getLogger()

class SlackBotException(PopupException):
  def __init__(self, msg, detail=None, error_code=200):
    PopupException.__init__(self, message=msg, detail=detail, error_code=error_code)


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
      parse_events(request, slack_message['event'])
  except ValueError as err:
    raise PopupException(_("Response content is not valid JSON"), detail=err)

  return HttpResponse(status=200)


def parse_events(request, event):
  """
  Parses the event according to its 'type'.

  """
  channel_id = event.get('channel')
  user_id = event.get('user')
  message_element = event['blocks'][0].get('elements', []) if event.get('blocks') else []

  if event.get('type') == 'message':
    handle_on_message(request.get_host(), request.is_secure(), channel_id, event.get('bot_id'), message_element, user_id, event.get('ts'))

  if event.get('type') == 'link_shared':
    handle_on_link_shared(request.get_host(), channel_id, event.get('message_ts'), event.get('links'), user_id)

  if event.get('type') == 'app_mention':
    handle_on_app_mention(request.get_host(), channel_id, user_id, event.get('text'), event.get('ts'))


def handle_on_app_mention(host_domain, channel_id, user_id, text, message_ts):
  if text and 'help' in text:
    help_msg_block = help_message(user_id)
    _send_message(channel_id, block_element=help_msg_block)

  if text and 'queries' in text:
    slack_user = check_slack_user_permission(host_domain, user_id)
    user = get_user(channel_id, slack_user, message_ts)

    handle_query_bank(channel_id, user_id)


def help_message(user_id):
  help_message = [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": ("Hey <@{user}>, I'm your SQL Assistant! "
        "I'm here to assist users with their SQL queries and *<{docs}|much more.>*\n"
        "Here are the few things I can help you with:").format(user=user_id, docs='https://docs.gethue.com/user/concept/#slack')
      }
    },
		{
			"type": "divider"
		},
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Share query/gist links* in channel which unfurls in a rich preview, showing query details and result in message thread if available."
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "Create a gist for your query, select the channel and *share directly from the Hue Editor* window."
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Detect SQL SELECT statements* in the channel and suggests a gist link for improved query discussions."
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "Type `@Hue queries` to explore a list of important queries from the latest *query bank*."
      }
    }
  ]

  return help_message


def handle_query_bank(channel_id, user_id):
  data = get_all_queries()

  message_block = [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "Hi <@{user}>, here is the list of all saved queries!".format(user=user_id)
      }
    },
    {
      "type": "divider"
    },
  ]

  for query in data:
    statement = query['data']['query']['statement']
    query_element = {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Name:* {name} \n *Statement:*\n ```{statement}```".format(name=query['name'], statement=statement)
      },
    }
    message_block.append(query_element)

  _send_message(channel_id, block_element=message_block)


def handle_on_message(host_domain, is_http_secure, channel_id, bot_id, elements, user_id, message_ts):
  # Ignore bot's own message since that will cause an infinite loop of messages if we respond.
  if bot_id is not None:
    return HttpResponse(status=200)
  
  for element_block in elements:
    text = element_block['elements'][0].get('text', '') if element_block.get('elements') else ''

    if 'hello hue' in text.lower():
      help_msg_block = help_message(user_id)
      _send_message(channel_id, block_element=help_msg_block)

    if text.lower().startswith('select'):
      handle_select_statement(host_domain, is_http_secure, channel_id, user_id, text.lower(), message_ts)


def handle_select_statement(host_domain, is_http_secure, channel_id, user_id, statement, message_ts):
  msg = 'Hi <@{user}> \n Looks like you are copy/pasting SQL, instead now you can send Editor links which unfurls in a rich preview!'.format(user=user_id)
  _send_message(channel_id, message=msg)

  # Check Slack user perms to send gist link
  slack_user = check_slack_user_permission(host_domain, user_id)
  user = get_user(channel_id, slack_user, message_ts)

  _make_select_statement_gist(host_domain, is_http_secure, user, channel_id, statement)


def _make_select_statement_gist(host_domain, is_http_secure, user, channel_id, statement):
  default_dialect = get_cluster_config(rewrite_user(user))['main_button_action']['dialect']
  gist_response = _gist_create(host_domain, is_http_secure, user, statement, default_dialect)

  msg = 'Here is the gist link\n {gist_link}'.format(gist_link=gist_response['link'])
  _send_message(channel_id, message=msg)


def handle_on_link_shared(host_domain, channel_id, message_ts, links, user_id):
  for item in links:
    path = urlsplit(item['url'])[2]
    id_type, qid = urlsplit(item['url'])[3].split('=')
    query_id = {'id': qid} if qid.isdigit() else {'uuid': qid}

    try:
      if path == '/hue/editor' and id_type == 'editor':
        doc = Document2.objects.get(**query_id)
        doc_type = 'query'
      elif path == '/hue/gist' and id_type == 'uuid':
        doc = _get_gist_document(**query_id)
        doc_type = 'gist'
      else:
        err_msg = 'Could not access the query, please check the link again.'
        _send_message(channel_id, message=err_msg, message_ts=message_ts)
        raise SlackBotException(_("Cannot unfurl link"))
    except Document2.DoesNotExist:
      err_msg = 'Query document not found or does not exist.'
      _send_message(channel_id, message=err_msg, message_ts=message_ts)

      msg = "Document with {key} does not exist".format(key=query_id)
      raise SlackBotException(_(msg))

    # Permission check for Slack user to be Hue user
    slack_user = check_slack_user_permission(host_domain, user_id)
    user = get_user(channel_id, slack_user, message_ts) if not slack_user['is_bot'] else doc.owner
    doc.can_read_or_exception(user)

    request = MockRequest(user=rewrite_user(user))

    payload = _make_unfurl_payload(request, item['url'], id_type, doc, doc_type)
    try:
      slack_client.chat_unfurl(channel=channel_id, ts=message_ts, unfurls=payload['payload'])
    except Exception as e:
      raise SlackBotException(_("Cannot unfurl link"), detail=e)
    
    # Generate and upload result xlsx file only if result available
    if payload['file_status']:
      send_result_file(request, channel_id, message_ts, doc, 'xls')


def get_user(channel_id, slack_user, message_ts):
  try:
    return User.objects.get(username=slack_user.get('user_email_prefix'))
  except User.DoesNotExist:
    err_msg = 'Corresponding Hue user not found or does not have access.'
    _send_message(channel_id, message=err_msg, message_ts=message_ts)
    raise SlackBotException(_("Slack user does not have access to the query"))


def check_slack_user_permission(host_domain, user_id):
  try:
    slack_user = slack_client.users_info(user=user_id)
  except Exception as e:
    raise SlackBotException(_("Cannot find query owner in Slack"), detail=e)

  response = {
    'is_bot': slack_user['user']['is_bot'],
  }
  if not slack_user['user']['is_bot']:
    email_prefix, email_domain = slack_user['user']['profile']['email'].split('@')
    if email_domain == '.'.join(host_domain.split('.')[-2:]):
      response['user_email_prefix'] = email_prefix

  return response


def send_result_file(request, channel_id, message_ts, doc, file_format):
  notebook = json.loads(doc.data)
  snippet = notebook['snippets'][0]
  snippet['statement'] = notebook['snippets'][0]['statement_raw']

  content_generator = get_api(request, snippet).download(notebook, snippet, file_format)

  file_format = 'xlsx'
  file_name = _get_snippet_name(notebook)

  try:
    slack_client.files_upload(
      channels=channel_id,
      file=next(content_generator), 
      thread_ts=message_ts,
      filetype=file_format,
      filename='{name}.{format}'.format(name=file_name, format=file_format),
      initial_comment='Here is your result file!'
    )
  except Exception as e:
    raise SlackBotException(_("Cannot upload result file"), detail=e)


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

  return tabulate(table, headers=['Columns({count})'.format(count=idx+1), '', ''], tablefmt="simple")


def _make_unfurl_payload(request, url, id_type, doc, doc_type):
  doc_data = json.loads(doc.data)
  statement = doc_data['snippets'][0]['statement_raw'] or 'No statement' if id_type == 'editor' else doc_data.get('statement_raw', '')
  dialect = doc_data.get('dialect') or doc_data.get('type', '') if id_type == 'editor' else doc.extra

  file_status = False
  result_section = None

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

    result_section = {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Query result:*\n```{result}```".format(result=unfurl_result),
      }
    }

  payload_data = {
    'url': url,
    'name': doc.name,
    'doc_type': doc_type,
    'dialect': dialect,
    'user': doc.owner.get_full_name() or doc.owner.username,
    'query': statement if len(statement) < 150 else (statement[:150] + '...'),
  }

  payload = {
    url: {
      "color": "#025BA6",
      "blocks": [
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "\n*<{url}|Open {name} {doc_type} of {dialect} dialect created by {user} in Hue>*".format(**payload_data),
          }
        },
        {
          "type": "divider"
				},
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*Statement:*\n```{query}```".format(**payload_data)
          }
        },
      ]
    }
  }

  if result_section is not None:
    payload[url]['blocks'].append(result_section)

  return {'payload': payload, 'file_status': file_status}