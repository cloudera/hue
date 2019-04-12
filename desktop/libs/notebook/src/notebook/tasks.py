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
from desktop.lib import export_csvxls

from notebook.connectors.base import get_api, QueryExpired, ResultWrapper

LOG_TASK = get_task_logger(__name__)
LOG = logging.getLogger(__name__)
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

class ResultWrapperCallback(object):
  def __init__(self, uuid, meta, log_file_handle):
    self.meta = meta
    self.uuid = uuid
    self.log_file_handle = log_file_handle

  def on_execute(self, handle):
    if handle.get('sync', False) and handle['result'].get('data'):
      handle_without_data = handle.copy()
      handle_without_data['result'] = {}
      for key in filter(lambda x: x != 'data', list(handle['result'].keys())):
        handle_without_data['result'][key] = handle['result'][key]
    else:
      handle_without_data = handle
    self.meta['handle'] = handle_without_data

  def on_log(self, log):
    os.write(self.log_file_handle, log)

  def on_status(self, status):
    self.meta['status'] = status
    download_to_file.update_state(task_id=self.uuid, state='PROGRESS', meta=self.meta)

#TODO: Add periodic cleanup task
#TODO: move file paths to a file like API so we can change implementation
#TODO: UI should be able to close a query that is available, but not expired
@app.task()
def download_to_file(notebook, snippet, file_format='csv', postdict=None, user_id=None, max_rows=-1):
  from beeswax import data_export
  download_to_file.update_state(task_id=notebook['uuid'], state='STARTED', meta={})
  request = _get_request(postdict, user_id)
  api = get_api(request, snippet)

  f, path = tempfile.mkstemp()
  f_log, path_log = tempfile.mkstemp()
  f_progress, path_progress = tempfile.mkstemp()
  try:
    os.write(f_progress, '0')

    meta = {'row_counter': 0, 'file_path': path, 'handle': {}, 'log_path': path_log, 'progress_path': path_progress, 'status': 'running', 'truncated': False} #TODO: Truncated

    result_wrapper = ResultWrapper(api, notebook, snippet, ResultWrapperCallback(notebook['uuid'], meta, f_log))
    content_generator = data_export.DataAdapter(result_wrapper, max_rows=max_rows, store_data_type_in_header=True) #TODO: Move PREFETCH_RESULT_COUNT to front end
    response = export_csvxls.create_generator(content_generator, file_format)

    for chunk in response:
      os.write(f, chunk)
      meta['row_counter'] = content_generator.row_counter
      download_to_file.update_state(task_id=notebook['uuid'], state='AVAILABLE', meta=meta)

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

#TODO: Convert csv to excel if needed
def download(*args, **kwargs):
  result = download_to_file.AsyncResult(args[0]['uuid'])
  state = result.state
  if state == states.PENDING:
    raise QueryExpired()
  elif state in states.EXCEPTION_STATES:
    result.maybe_reraise()

  info = result.wait() # TODO: Start returning data even if we're not done

  return export_csvxls.file_reader(open(info['file_path'], 'rb'))

# Why we need this:
# 1) There is no way in celery to differentiate between a task that was submitted, but not yet started and a task that has been GCed.
# 2) The client will keep checking for data until the query is expired. The new definition for expired in this case is a task that has been GCed.
def _patch_status(notebook):
  result = download_to_file.AsyncResult(notebook['uuid'])
  result.backend.store_result(notebook['uuid'], None, "SUBMITTED")

def execute(*args, **kwargs):
  notebook = args[0]
  kwargs['max_rows'] = TASK_SERVER.PREFETCH_RESULT_COUNT.get()
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

  return {'status': STATE_MAP[state]}

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