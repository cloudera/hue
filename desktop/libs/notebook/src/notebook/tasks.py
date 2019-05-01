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
import json
import logging
import StringIO
import sys

from celery.utils.log import get_task_logger
from celery import states

from django.core.cache import caches
from django.core.files.storage import get_storage_class
from django.contrib.auth.models import User
from django.db import transaction
from django.http import FileResponse, HttpRequest

from desktop.auth.backend import rewrite_user
from desktop.celery import app
from desktop.conf import TASK_SERVER
from desktop.lib import export_csvxls
from desktop.lib import fsmanager
from desktop.settings import CACHES_CELERY_KEY

from notebook.connectors.base import get_api, QueryExpired, ExecutionWrapper
from notebook.sql_utils import get_current_statement

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
storage_info = json.loads(TASK_SERVER.RESULT_STORAGE.get())
storage = get_storage_class(storage_info.get('backend'))(**storage_info.get('properties', {}))

class ExecutionWrapperCallback(object):
  def __init__(self, uuid, meta, f_log):
    self.meta = meta
    self.uuid = uuid
    self.f_log = f_log

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
    self.f_log.write(log)
    self.f_log.flush()

  def on_status(self, status):
    self.meta['status'] = status
    download_to_file.update_state(task_id=self.uuid, state='PROGRESS', meta=self.meta)

#TODO: Add periodic cleanup task
#TODO: UI should be able to close a query that is available, but not expired
@app.task()
def download_to_file(notebook, snippet, file_format='csv', max_rows=-1, **kwargs):
  from beeswax import data_export
  download_to_file.update_state(task_id=notebook['uuid'], state='STARTED', meta={})
  request = _get_request(**kwargs)
  api = get_api(request, snippet)

  meta = {'row_counter': 0, 'handle': {}, 'status': '', 'truncated': False}

  with storage.open(_log_key(notebook), 'wb') as f_log:
    result_wrapper = ExecutionWrapper(api, notebook, snippet, ExecutionWrapperCallback(notebook['uuid'], meta, f_log))
    content_generator = data_export.DataAdapter(result_wrapper, max_rows=max_rows, store_data_type_in_header=True) #TODO: Move FETCH_RESULT_LIMIT to front end
    response = export_csvxls.create_generator(content_generator, file_format)

    with storage.open(_result_key(notebook), 'wb') as f:
      for chunk in response:
        f.write(chunk)
        meta['row_counter'] = content_generator.row_counter
        meta['truncated'] = content_generator.is_truncated
        download_to_file.update_state(task_id=notebook['uuid'], state='AVAILABLE', meta=meta)

  return meta

@app.task(ignore_result=True)
def cancel_async(notebook, snippet, **kwargs):
  request = _get_request(**kwargs)
  get_api(request, snippet).cancel(notebook, snippet)

@app.task(ignore_result=True)
def close_statement_async(notebook, snippet, **kwargs):
  request = _get_request(**kwargs)
  get_api(request, snippet).close_statement(notebook, snippet)

#TODO: Convert csv to excel if needed
def download(*args, **kwargs):
  notebook = args[0]
  result = download_to_file.AsyncResult(args[0]['uuid'])
  state = result.state
  if state == states.PENDING:
    raise QueryExpired()
  elif state in states.EXCEPTION_STATES:
    result.maybe_reraise()

  info = result.wait() # TODO: Start returning data even if we're not done

  return export_csvxls.file_reader(storage.open(_result_key(notebook), 'rb'))

# Why we need this:
# 1) There is no way in celery to differentiate between a task that was submitted, but not yet started and a task that has been GCed.
# 2) The client will keep checking for data until the query is expired. The new definition for expired in this case is a task that has been GCed.
def _patch_status(notebook):
  result = download_to_file.AsyncResult(notebook['uuid'])
  result.backend.store_result(notebook['uuid'], None, "SUBMITTED")

def execute(*args, **kwargs):
  notebook = args[0]
  snippet = args[1]
  kwargs['max_rows'] = TASK_SERVER.FETCH_RESULT_LIMIT.get()
  _patch_status(notebook)
  download_to_file.apply_async(args=args, kwargs=kwargs, task_id=notebook['uuid'])

  should_close, resp = get_current_statement(snippet) # This redoes some of the work in api.execute. Other option is to pass statement, but then we'd have to modify notebook.api.
  #if should_close: #front end already calls close_statement for multi statement execution no need to do here. In addition, we'd have to figure out what was the previous guid.

  resp.update({'sync': False,
      'has_result_set': True,
      'modified_row_count': 0,
      'guid': '',
      'result': {
        'has_more': True,
        'data': [],
        'meta': [],
        'type': 'table'
      }})
  return resp

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
    return ''

  if not startFrom:
    with storage.open(_log_key(notebook), 'r') as f:
      return f.read()
  else:
    count = 0
    output = StringIO.StringIO()
    with storage.open(_log_key(notebook), 'r') as f:
      for line in f:
        count += 1
        if count <= startFrom:
          continue
        output.write(line)
    return output.getvalue()

def get_jobs(notebook, snippet, logs, **kwargs): #Re implement to fetch updated guid in download_to_file from DB
  result = download_to_file.AsyncResult(notebook['uuid'])
  state = result.state
  if state == states.PENDING:
    raise QueryExpired()
  elif state == 'SUBMITTED' or states.state(state) < states.state('PROGRESS'):
    return []
  elif state in states.EXCEPTION_STATES:
    return []

  info = result.info
  snippet['result']['handle'] = info.get('handle', {}).copy()

  request = _get_request(**kwargs)
  api = get_api(request, snippet)
  return api.get_jobs(notebook, snippet, logs)

def progress(notebook, snippet, logs=None, **kwargs):
  result = download_to_file.AsyncResult(notebook['uuid'])
  state = result.state
  if state == states.PENDING:
    raise QueryExpired()
  elif state == 'SUBMITTED' or states.state(state) < states.state('PROGRESS'):
    return 1
  elif state in states.EXCEPTION_STATES:
    return 1

  info = result.info
  snippet['result']['handle'] = info.get('handle', {}).copy()
  request = _get_request(**kwargs)
  api = get_api(request, snippet)
  return api.progress(notebook, snippet, logs=logs)

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
    skip = caches[CACHES_CELERY_KEY].get(_fetch_progress_key(notebook), default=0)
  target = skip + rows

  if info.get('handle', {}).get('has_result_set', False):
    csv.field_size_limit(sys.maxsize)
    count = 0
    with storage.open(_result_key(notebook)) as f:
      csv_reader = csv.reader(f, delimiter=','.encode('utf-8'))
      first = next(csv_reader, None)
      if first: # else no data to read
        for col in first:
          split = col.split('|')
          split_type = split[1] if len(split) > 1 else 'STRING_TYPE'
          cols.append({'name': split[0], 'type': split_type, 'comment': None})
        for row in csv_reader:
          count += 1
          if count <= skip:
            continue
          data.append(row)
          if count >= target:
            break

    caches[CACHES_CELERY_KEY].set(_fetch_progress_key(notebook), count, timeout=None)

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
  status = 0
  if state == states.PENDING:
    raise QueryExpired()
  elif state == 'SUBMITTED' or states.state(state) < states.state('PROGRESS'):
    status = -1
  elif state in states.EXCEPTION_STATES:
    status = -1

  if status == 0:
    info = result.info
    snippet['result']['handle'] = info.get('handle', {}).copy()
    cancel_async.apply_async(args=args, kwargs=kwargs, task_id=_cancel_statement_async_id(notebook))

  result.forget()
  _cleanup(notebook)
  return {'status': status}

def close_statement(*args, **kwargs):
  notebook = args[0]
  snippet = args[1]
  result = download_to_file.AsyncResult(notebook['uuid'])
  state = result.state
  status = 0
  if state == states.PENDING:
    raise QueryExpired()
  elif state == 'SUBMITTED' or states.state(state) < states.state('PROGRESS'):
    status = -1
  elif state in states.EXCEPTION_STATES:
    status = -1

  if status == 0:
    info = result.info
    snippet['result']['handle'] = info.get('handle', {}).copy()
    close_statement_async.apply_async(args=args, kwargs=kwargs, task_id=_close_statement_async_id(notebook))

  result.forget()
  _cleanup(notebook)
  return {'status': status}

def _cleanup(notebook):
  storage.delete(_result_key(notebook))
  storage.delete(_log_key(notebook))
  caches[CACHES_CELERY_KEY].delete(_fetch_progress_key(notebook))

def _log_key(notebook):
  return notebook['uuid'] + '_log'

def _result_key(notebook):
  return notebook['uuid'] + '_result'

def _fetch_progress_key(notebook):
  return notebook['uuid'] + '_fetch_progress'

def _cancel_statement_async_id(notebook):
  return notebook['uuid'] + '_cancel'

def _close_statement_async_id(notebook):
  return notebook['uuid'] + '_close'

def _get_request(postdict=None, user_id=None):
  request = HttpRequest()
  request.POST = postdict
  request.fs_ref = 'default'
  request.fs = fsmanager.get_filesystem(request.fs_ref)
  request.jt = None
  user = User.objects.get(id=user_id)
  user = rewrite_user(user)
  request.user = user
  return request