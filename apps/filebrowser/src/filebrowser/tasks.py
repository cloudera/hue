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

from celery.utils.log import get_task_logger
from celery import states
from django.db import transaction
from django.http import HttpRequest

from desktop.auth.backend import rewrite_user
from desktop.celery import app
from desktop.conf import TASK_SERVER
from desktop.lib import fsmanager
from useradmin.models import User

LOG_TASK = get_task_logger(__name__)
LOG = logging.getLogger()
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

@app.task
def error_handler(request, exc, traceback):
    print('Task {0} raised exception: {1!r}\n{2!r}'.format(
          request.id, exc, traceback))
    
@app.task()
def upload_file_task(**kwargs):
  task_id = kwargs.get("qquuid")
  upload_file_task.update_state(task_id=task_id, state='STARTED', meta={})
  print(kwargs)
  user_id = kwargs["user_id"]
  scheme = kwargs["scheme"]
  postdict = kwargs.get("postdict", None)
  try:
    request = _get_request(postdict=postdict, user_id=user_id, scheme=scheme)
    from filebrowser.views import UPLOAD_CLASSES
    upload_class = UPLOAD_CLASSES.get(kwargs["scheme"], None)
    _fs = upload_class(request, args=[], **kwargs)
    _fs.upload_chunks()
    upload_file_task.update_state(task_id=task_id, state='PROGRESS', meta={})
  except Exception as err:
    upload_file_task.update_state(task_id=task_id, state='FAILURE', meta={})
    raise Exception(f"Upload failed {err=}, {type(err)=}")
  
  return
  
def _get_request(postdict=None, user_id=None, scheme=None):
  request = HttpRequest()
  request.POST = postdict
  request.fs_ref = "default"
  request.fs = fsmanager.get_filesystem(request.fs_ref)
  request.jt = None

  user = User.objects.get(id=user_id)
  user = rewrite_user(user)
  request.user = user

  return request
