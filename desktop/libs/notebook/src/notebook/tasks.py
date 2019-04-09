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
from __future__ import absolute_import, unicode_literals

from builtins import next
from builtins import str
import csv
import os
import json
import logging
import tempfile
import time

from celery.utils.log import get_task_logger
from celery import states

from django.contrib.auth.models import User
from django.db import transaction
from django.http import FileResponse, HttpRequest

from desktop.auth.backend import rewrite_user
from desktop.celery import app
from desktop.conf import TASK_SERVER
from desktop.lib.export_csvxls import FORMAT_TO_CONTENT_TYPE

from notebook.connectors.base import get_api, QueryExpired

LOG_TASK = get_task_logger(__name__)
LOG = logging.getLogger(__name__)
DOWNLOAD_COOKIE_AGE = 3600
STATE_MAP = {
  'SUBMITTED': 'waiting',
  states.RECEIVED: 'waiting',
  states.PENDING: 'waiting',
  states.STARTED: 'running',
  states.RETRY: 'running',
  'PROGRESS': 'running',
  'AVAILABLE': 'available',
  states.SUCCESS: 'available',
  states.FAILURE: 'failure',
  states.REVOKED: 'canceled',
  states.REJECTED: 'rejected',
  states.IGNORED: 'ignored'
}

#TODO: Add periodic cleanup task
#TODO: move file paths to a file like API so we can change implementation
#TODO: UI should be able to close a query that is available, but not expired
@app.task()
def download_to_file(notebook, snippet, file_format='csv', user_agent=None, postdict=None, user_id=None, create=False, store_data_type_in_header=False):
  download_to_file.update_state(task_id=notebook['uuid'], state='STARTED', meta={})
  request = _get_request(postdict, user_id)
  api = get_api(request, snippet)
  if create:
    handle = api.execute(notebook, snippet)
  else:
    handle = snippet['result']['handle']

  f, path = tempfile.mkstemp()
  f_log, path_log = tempfile.mkstemp()
  f_progress, path_progress = tempfile.mkstemp()
  try:
    os.write(f_progress, '0')
    meta = {'row_counter': 0, 'file_path': path, 'handle': handle, 'log_path': path_log, 'progress_path': path_progress, 'status': 'running', 'truncated': False} #TODO: Truncated
    download_to_file.update_state(task_id=notebook['uuid'], state='PROGRESS', meta=meta)
    _until_available(notebook, snippet, api, f_log, handle, meta)

    snippet['result']['handle'] = handle.copy()
    #TODO: Move PREFETCH_RESULT_COUNT to front end
    response = api.download(notebook, snippet, file_format, user_agent=user_agent, max_rows=TASK_SERVER.PREFETCH_RESULT_COUNT.get(), store_data_type_in_header=store_data_type_in_header)

    row_count = 0
    for chunk in response:
      os.write(f, chunk)
      row_count += chunk.count('\n')
      meta['row_counter'] = row_count - 1
      download_to_file.update_state(task_id=notebook['uuid'], state='AVAILABLE', meta=meta)

    snippet['result']['handle'] = handle.copy()
    api.close_statement(notebook, snippet)
  finally:
    os.close(f)
    os.close(f_log)
    os.close(f_progress)
  return meta

@app.task(ignore_result=True)
def cancel_async(notebook, snippet, postdict=None, user_id=None):
  request = _get_request(postdict, user_id)
  get_api(request, snippet).cancel(notebook, snippet)

@app.task(ignore_result=True)
def close_statement_async(notebook, snippet, postdict=None, user_id=None):
  request = _get_request(postdict, user_id)
  get_api(request, snippet).close_statement(notebook, snippet)

def _until_available(notebook, snippet, api, f, handle, meta):
  count = 0
  sleep_seconds = 1
  check_status_count = 0
  while True:
    snippet['result']['handle'] = handle.copy()
    response = api.check_status(notebook, snippet)
    meta['status'] = response['status']
    download_to_file.update_state(task_id=notebook['uuid'], state='PROGRESS', meta=meta)
    snippet['result']['handle'] = handle.copy()
    log = api.get_log(notebook, snippet, startFrom=count)
    os.write(f, log)
    count += log.count('\n')

    if response['status'] not in ['waiting', 'running', 'submitted']:
      break
    check_status_count += 1
    if check_status_count > 5:
      sleep_seconds = 5
    elif check_status_count > 10:
      sleep_seconds = 10
    time.sleep(sleep_seconds)

#TODO: Convert csv to excel if needed
def download(*args, **kwargs):
  result = download_to_file.AsyncResult(args[0]['uuid'])
  state = result.state
  if state == states.PENDING:
    raise QueryExpired()
  elif state in states.EXCEPTION_STATES:
    result.maybe_reraise()

  info = result.wait()
  response = FileResponse(open(info['file_path'], 'rb'), content_type=FORMAT_TO_CONTENT_TYPE.get('csv', 'application/octet-stream'))
  response['Content-Disposition'] = 'attachment; filename="%s.%s"' % (args[0]['uuid'], 'csv') #TODO: Add support for 3rd party (e.g. nginx file serving)
  response.set_cookie(
      'download-%s' % args[1]['id'],
      json.dumps({
        'truncated': info.get('truncated', False),
        'row_counter': info.get('row_counter', 0)
      }),
      max_age=DOWNLOAD_COOKIE_AGE
    )
  return response

# Why we need this:
# 1) There is no way in celery to differentiate between a task that was submitted, but not yet started and a task that has been GCed.
# 2) The client will keep checking for data until the query is expired. The new definition for expired in this case is a task that has been GCed.
def _patch_status(notebook):
  result = download_to_file.AsyncResult(notebook['uuid'])
  result.backend.store_result(notebook['uuid'], None, "SUBMITTED")

def execute(*args, **kwargs):
  notebook = args[0]
  kwargs['create'] = True
  kwargs['store_data_type_in_header'] = True
  _patch_status(notebook)
  download_to_file.apply_async(args=args, kwargs=kwargs, task_id=notebook['uuid'])
  return {'sync': False,
      'has_result_set': True,
      'modified_row_count': 0,
      'guid': '',
      'result': {
        'has_more': True,
        'data': [],
        'meta': [],
        'type': 'table'
      }}

def check_status(*args, **kwargs):
  notebook = args[0]
  result = download_to_file.AsyncResult(notebook['uuid'])
  state = result.state
  if state == states.PENDING:
    raise QueryExpired()
  elif state in states.EXCEPTION_STATES:
    result.maybe_reraise()

  info = result.info
  if not info or not info.get('status'):
    status = STATE_MAP[state]
  else:
    status = info.get('status')
  return {'status': status}

def get_log(notebook, snippet, startFrom=None, size=None, postdict=None, user_id=None):
  result = download_to_file.AsyncResult(notebook['uuid'])
  state = result.state
  if state == states.PENDING:
    raise QueryExpired()
  elif state == 'SUBMITTED' or states.state(state) < states.state('PROGRESS'):
    return ''
  elif state in states.EXCEPTION_STATES:
    result.maybe_reraise()
    return ''

  info = result.info
  if not startFrom:
    with open(info.get('log_path'), 'r') as f:
      return f.read()
  else:
    count = 0
    data = ''
    with open(info.get('log_path'), 'r') as f:
      for line in f:
        count += 1
        if count <= startFrom:
          continue
        data += line
    return data

def get_jobs(notebook, snippet, logs, **kwargs): #Re implement to fetch updated guid in download_to_file from DB
  result = download_to_file.AsyncResult(notebook['uuid'])
  state = result.state
  if state == states.PENDING:
    raise QueryExpired()
  elif state == 'SUBMITTED' or states.state(state) < states.state('PROGRESS'):
    return []
  elif state in states.EXCEPTION_STATES:
    result.maybe_reraise()
    return []

  info = result.info
  snippet['result']['handle'] = info.get('handle', {}).copy()

  request = _get_request(**kwargs)
  api = get_api(request, snippet)
  #insiduous problem where each call in hive api transform the guid/secret to binary form. get_log does the transform, but not get_jobs. get_jobs called after get_log so usually not an issue. Our get_log implementation doesn't
  if hasattr(api, '_get_handle'): # This is specific to impala, should be handled in hiveserver2
    api._get_handle(snippet)
  return api.get_jobs(notebook, snippet, logs)

def fetch_result(notebook, snippet, rows, start_over, **kwargs):
  result = download_to_file.AsyncResult(notebook['uuid'])
  state = result.state
  data = []
  cols = []
  results = {
      'has_more': False,
      'data': data,
      'meta': cols,
      'type': 'table'
    }
  if state == states.PENDING:
    raise QueryExpired()
  elif state in states.EXCEPTION_STATES:
    result.maybe_reraise()
    return results
  elif state not in [states.SUCCESS, 'AVAILABLE']:
    return results

  info = result.info
  skip = 0
  if not start_over:
    with open(info.get('progress_path'), 'r') as f:
      skip = int(f.read())
  target = skip + rows

  with open(info.get('file_path'), 'r') as f:
    csv_reader = csv.reader(f, delimiter=','.encode('utf-8'))
    first = next(csv_reader)
    for col in first:
      split = col.split('|')
      if len(split) > 1:
        cols.append({'name': split[0], 'type': split[1], 'comment': None})
      else:
        cols.append({'name': split[0], 'type': 'STRING_TYPE', 'comment': None})
    count = 0
    for row in csv_reader:
      count += 1
      if count <= skip:
        continue
      data.append(row)
      if count >= target:
        break

  with open(info.get('progress_path'), 'w') as f:
    f.write(str(count))

  results['has_more'] = count < info.get('row_counter') or state == states.state('PROGRESS')

  return results

def fetch_result_size(*args, **kwargs):
  notebook = args[0]
  result = download_to_file.AsyncResult(notebook['uuid'])
  state = result.state
  if state == states.PENDING:
    raise QueryExpired()
  elif state == 'SUBMITTED' or states.state(state) < states.state('PROGRESS'):
    return {'rows': 0}
  elif state in states.EXCEPTION_STATES:
    result.maybe_reraise()
    return {'rows': 0}

  info = result.info
  return {'rows': info.get('row_counter', 0)}

def cancel(*args, **kwargs):
  notebook = args[0]
  snippet = args[1]
  result = download_to_file.AsyncResult(notebook['uuid'])
  state = result.state
  if state == states.PENDING:
    raise QueryExpired()
  elif state == 'SUBMITTED' or states.state(state) < states.state('PROGRESS'):
    return {'status': -1}
  elif state in states.EXCEPTION_STATES:
    result.maybe_reraise()
    return {'status': -1}

  info = result.info
  snippet['result']['handle'] = info.get('handle', {}).copy()
  cancel_async.apply_async(args=args, kwargs=kwargs, task_id=_cancel_statement_async_id(notebook))
  result.forget()
  os.remove(info.get('file_path'))
  os.remove(info.get('log_path'))
  os.remove(info.get('progress_path'))
  return {'status': 0}

def close_statement(*args, **kwargs):
  notebook = args[0]
  snippet = args[1]
  result = download_to_file.AsyncResult(notebook['uuid'])
  state = result.state
  if state == states.PENDING:
    raise QueryExpired()
  elif state == 'SUBMITTED' or states.state(state) < states.state('PROGRESS'):
    return {'status': -1}
  elif state in states.EXCEPTION_STATES:
    result.maybe_reraise()
    return {'status': -1}

  info = result.info
  snippet['result']['handle'] = info.get('handle', {}).copy()
  close_statement_async.apply_async(args=args, kwargs=kwargs, task_id=_close_statement_async_id(notebook))
  result.forget()
  os.remove(info.get('file_path'))
  os.remove(info.get('log_path'))
  os.remove(info.get('progress_path'))
  return {'status': 0}

def _cancel_statement_async_id(notebook):
  return notebook['uuid'] + '_cancel'

def _close_statement_async_id(notebook):
  return notebook['uuid'] + '_close'

def _get_request(postdict=None, user_id=None):
  request = HttpRequest()
  request.POST = postdict
  user = User.objects.get(id=user_id)
  user = rewrite_user(user)
  request.user = user
  return request