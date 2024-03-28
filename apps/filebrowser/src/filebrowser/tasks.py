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
import subprocess
import os

from celery.utils.log import get_task_logger
from celery import states
from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone

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
  user_id = kwargs["user_id"]
  scheme = kwargs["scheme"]
  postdict = kwargs.get("postdict", None)
  request = _get_request(postdict=postdict, user_id=user_id, scheme=scheme)
  kwargs["username"] = request.user.username
  kwargs["task_name"] = "fileupload"
  kwargs["state"] = "STARTED"
  now = timezone.now()
  kwargs["task_start"]=now.strftime("%Y-%m-%dT%H:%M:%S")
  # kwargs["task_start"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
  upload_file_task.update_state(task_id=task_id, state='STARTED', meta=kwargs)
  try:
    from filebrowser.views import UPLOAD_CLASSES
    upload_class = UPLOAD_CLASSES.get(kwargs["scheme"], None)
    _fs = upload_class(request, args=[], **kwargs)
    kwargs["state"] = "RUNNING"
    upload_file_task.update_state(task_id=task_id, state='RUNNING', meta=kwargs)
    _fs.upload_chunks()
  except Exception as err:
    kwargs["state"] = "FAILURE"
    upload_file_task.update_state(task_id=task_id, state='FAILURE', meta=kwargs)
    raise Exception(f"Upload failed %s" % err)

  kwargs["state"] = "SUCCESS"
  kwargs["started"] = now.strftime("%Y-%m-%dT%H:%M:%S")
  kwargs["task_end"] = now.strftime("%Y-%m-%dT%H:%M:%S")
  upload_file_task.update_state(task_id=task_id, state='SUCCESS', meta=kwargs)
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

@app.task()
def document_cleanup_task( **kwargs):
    keep_days = kwargs.get('keep_days')
    task_id = kwargs.get("qquuid")
    now = timezone.now()

    kwargs["username"] = kwargs["username"]
    kwargs["task_name"] = "document_cleanup"
    kwargs["state"] = "STARTED"
    kwargs["parameters"] = keep_days
    kwargs["task_id"] = task_id
    kwargs["progress"] = "0%"
    kwargs["task_start"] = now.strftime("%Y-%m-%dT%H:%M:%S")

    try:
        INSTALL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
        document_cleanup_task.update_state(task_id=task_id, state='RUNNING', meta=kwargs)
        subprocess.check_call([INSTALL_DIR + '/build/env/bin/hue', 'desktop_document_cleanup', f'--keep-days={keep_days}'])
        kwargs["state"] = "SUCCESS"
        LOG.info(f"Document_cleanup_task completed successfully.")
    except Exception as err:
        document_cleanup_task.update_state(task_id=task_id, state='FAILURE', meta=kwargs)
        raise Exception(f"Upload failed %s" % err)

    kwargs["state"] = "SUCCESS"
    kwargs["progress"] = "100%"
    kwargs["task_end"] = now.strftime("%Y-%m-%dT%H:%M:%S")
    document_cleanup_task.update_state(task_id=task_id, state='SUCCESS', meta=kwargs)

    return

import os
import shutil
import psutil
from datetime import datetime, timedelta

@app.task()
def check_disk_usage_and_clean_task(**kwargs):
    task_id = kwargs.get("qquuid")
    default_cleanup_threshold = 90
    cleanup_threshold = kwargs.get('cleanup_threshold', default_cleanup_threshold)
    username = kwargs.get("username", "celery_scheduler")
    now = timezone.now()
    kwargs = {
        "username": username,
        "task_name": "tmp_cleanup",
        "task_id": task_id,
        "parameters": cleanup_threshold,
        "progress": "0%",
        "task_start": now.strftime("%Y-%m-%dT%H:%M:%S")
    }

    disk_usage = psutil.disk_usage('/')
    if disk_usage.percent >= int(cleanup_threshold):
        LOG.info(f"Disk usage is above {cleanup_threshold}%, cleaning up /tmp directory...")
        tmp_dir = '/tmp'
        for filename in os.listdir(tmp_dir):
            file_path = os.path.join(tmp_dir, filename)
            try:
                file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                # Make file_modified_time timezone-aware
                file_modified_time = timezone.make_aware(file_modified_time, timezone.get_default_timezone())
                if file_modified_time < now - timedelta(minutes=15):
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    LOG.info(f"Deleted {file_path}")
            except PermissionError:
                LOG.warning(f"Permission denied: unable to delete {file_path}")
            except Exception as err:
                check_disk_usage_and_clean_task.update_state(task_id=task_id, state='FAILURE', meta=kwargs)
                raise Exception(f"Failed to delete {file_path}. Reason: {err}")

        kwargs["progress"] = "100%"
        check_disk_usage_and_clean_task.update_state(task_id=task_id, state='SUCCESS', meta=kwargs)
        LOG.info("/tmp directory cleaned.")

    else:
        kwargs["progress"] = "100%"
        check_disk_usage_and_clean_task.update_state(task_id=task_id, state='SUCCESS', meta=kwargs)
        LOG.info(f"Disk usage is {disk_usage.percent}%, no need to clean up.")

    # Get available disk space after cleanup
    free_space = psutil.disk_usage('/tmp').free
    return {'free_space': free_space}

