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
import os
import shutil
import logging
import subprocess
from datetime import datetime, timedelta

import pytz
import psutil
from celery import states
from celery.utils.log import get_task_logger
from django.http import HttpRequest
from django.utils import timezone

from desktop.auth.backend import rewrite_user
from desktop.celery import app
from desktop.conf import TASK_SERVER_V2
from desktop.lib import fsmanager
from filebrowser.utils import release_reserved_space_for_file_uploads, reserve_space_for_file_uploads

if hasattr(TASK_SERVER_V2, 'get') and TASK_SERVER_V2.ENABLED.get():
  from desktop.settings import TIME_ZONE, initialize_free_disk_space_in_redis, parse_broker_url
from filebrowser.views import UPLOAD_CLASSES
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
  file_size = kwargs.get("qqtotalfilesize")
  user_id = kwargs["user_id"]
  scheme = kwargs["scheme"]
  postdict = kwargs.get("postdict", None)
  request = _get_request(postdict=postdict, user_id=user_id, scheme=scheme)
  kwargs["username"] = request.user.username
  kwargs["task_name"] = "fileupload"
  kwargs["state"] = "STARTED"
  kwargs["task_start"] = timezone.now().astimezone(pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%dT%H:%M:%S")
  kwargs["started"] = timezone.now().astimezone(pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%dT%H:%M:%S")
  upload_file_task.update_state(task_id=task_id, state='STARTED', meta=kwargs)

  # Reserve space for upload
  if not reserve_space_for_file_uploads(task_id, file_size):
    kwargs["state"] = "FAILURE"
    upload_file_task.update_state(task_id=task_id, state='FAILURE', meta=kwargs)
    raise Exception("Insufficient space for upload")

  try:
    upload_class = UPLOAD_CLASSES.get(kwargs["scheme"])
    _fs = upload_class(request, args=[], **kwargs)
    kwargs["state"] = "RUNNING"
    upload_file_task.update_state(task_id=task_id, state='RUNNING', meta=kwargs)
    _fs.upload_chunks()
  except Exception as err:
    kwargs["state"] = "FAILURE"
    upload_file_task.update_state(task_id=task_id, state='FAILURE', meta=kwargs)
    raise Exception(f"Upload failed %s" % err)

  kwargs["state"] = "SUCCESS"
  kwargs["task_end"] = timezone.now().astimezone(pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%dT%H:%M:%S.%f")
  kwargs["progress"] = "100%"
  upload_file_task.update_state(task_id=task_id, state='SUCCESS', meta=kwargs)
  release_reserved_space_for_file_uploads(task_id)
  return None


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
def document_cleanup_task(**kwargs):
  keep_days = kwargs.get('keep_days')
  task_id = kwargs.get("qquuid")

  kwargs["username"] = kwargs["username"]
  kwargs["task_name"] = "document_cleanup"
  kwargs["state"] = "STARTED"
  kwargs["parameters"] = keep_days
  kwargs["task_id"] = task_id
  kwargs["progress"] = "0%"
  kwargs["task_start"] = timezone.now().astimezone(pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%dT%H:%M:%S")

  try:
    INSTALL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    document_cleanup_task.update_state(task_id=task_id, state='RUNNING', meta=kwargs)
    subprocess.check_call([INSTALL_DIR + '/build/env/bin/hue', 'desktop_document_cleanup', f'--keep-days={keep_days}'])
    kwargs["state"] = "SUCCESS"
    LOG.info(f"Document_cleanup_task completed successfully.")
  except Exception as err:
    kwargs["state"] = "FAILURE"
    document_cleanup_task.update_state(task_id=task_id, state='FAILURE', meta=kwargs)
    raise Exception(f"Upload failed %s" % err)

  kwargs["state"] = "SUCCESS"
  kwargs["progress"] = "100%"
  kwargs["task_end"] = timezone.now().astimezone(pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%dT%H:%M:%S.%f")
  document_cleanup_task.update_state(task_id=task_id, state='SUCCESS', meta=kwargs)

  return None


@app.task()
def check_disk_usage_and_clean_task(**kwargs):
  task_id = kwargs.get("qquuid")
  cleanup_threshold = kwargs.get('cleanup_threshold', TASK_SERVER_V2.DISK_USAGE_CLEANUP_THRESHOLD)
  username = kwargs.get("username", "celery_scheduler")
  now = timezone.now().astimezone(pytz.timezone(TIME_ZONE))
  kwargs = {
    "username": username,
    "task_name": "tmp_cleanup",
    "task_id": task_id,
    "parameters": cleanup_threshold,
    "progress": "0%",
    "task_start": now.strftime("%Y-%m-%dT%H:%M:%S.%f"),
  }

  check_disk_usage_and_clean_task.update_state(task_id=task_id, state=states.STARTED, meta=kwargs)

  def delete_old_files(directory, current_time, time_delta):
    for root, dirs, files in os.walk(directory):
      for file in files:
        file_path = os.path.join(root, file)
        try:
          file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
          file_modified_time = timezone.make_aware(file_modified_time, timezone.get_default_timezone())
          if file_modified_time < current_time - time_delta:
            if os.path.isfile(file_path) or os.path.islink(file_path):
              os.unlink(file_path)
              LOG.info(f"Deleted file {file_path}")
        except PermissionError:
          LOG.warning(f"Permission denied: unable to delete {file_path}")
        except Exception as err:
          check_disk_usage_and_clean_task.update_state(task_id=task_id, state=states.FAILURE, meta=kwargs)
          raise Exception(f"Failed to delete {file_path}. Reason: {err}")
        finally:
          kwargs["task_end"] = timezone.now().astimezone(pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%dT%H:%M:%S.%f")

  disk_usage = psutil.disk_usage('/')
  if disk_usage.percent >= int(cleanup_threshold):
    LOG.info(f"Disk usage is above {cleanup_threshold}%, cleaning up /tmp directory...")
    tmp_dir = '/tmp'
    delete_old_files(tmp_dir, now, timedelta(minutes=TASK_SERVER_V2.DISK_USAGE_AND_CLEAN_TASK_TIME_DELTA.get()))
    kwargs["progress"] = "100%"
    kwargs["task_end"] = timezone.now().astimezone(pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%dT%H:%M:%S.%f")
    check_disk_usage_and_clean_task.update_state(task_id=task_id, state=states.SUCCESS, meta=kwargs)
    LOG.info("/tmp directory cleaned.")
  else:
    kwargs["progress"] = "100%"
    kwargs["task_end"] = timezone.now().astimezone(pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%dT%H:%M:%S.%f")
    check_disk_usage_and_clean_task.update_state(task_id=task_id, state=states.SUCCESS, meta=kwargs)
    LOG.info(f"Disk usage is {disk_usage.percent}%, no need to clean up.")

  # Get available disk space after cleanup
  free_space = psutil.disk_usage('/tmp').free
  return {'free_space': free_space}


@app.task()
def cleanup_stale_uploads(**kwargs):
  timedelta_minutes = kwargs.get("timeout_minutes", TASK_SERVER_V2.CLEANUP_STALE_UPLOADS_TASK_TIME_DELTA.get())
  username = kwargs.get("username", "celery_scheduler")
  task_id = kwargs.get("qquuid")
  kwargs = {
    "username": username,
    "task_name": "cleanup_stale_uploads",
    "task_id": task_id,
    "parameters": timedelta_minutes,
    "progress": "0%",
    "task_start": timezone.now().astimezone(pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%dT%H:%M:%S"),
  }
  cleanup_stale_uploads.update_state(task_id=task_id, state=states.STARTED, meta=kwargs)
  redis_client = parse_broker_url(TASK_SERVER_V2.BROKER_URL.get())
  try:
    current_time = int(datetime.now().timestamp())

    for key in redis_client.scan_iter('upload__*'):
      timestamp_key = f'{key.decode()}_timestamp'
      timestamp = redis_client.get(timestamp_key)

      if timestamp:
        timestamp = int(timestamp)
        if current_time - timestamp > timedelta_minutes * 60:
          file_size = int(redis_client.get(key))
          redis_client.incrby('upload_available_space', file_size)
          redis_client.delete(key)
          redis_client.delete(timestamp_key)
    initialize_free_disk_space_in_redis()
    kwargs["progress"] = "100%"
    kwargs["task_end"] = timezone.now().astimezone(pytz.timezone(TIME_ZONE)).strftime("%Y-%m-%dT%H:%M:%S.%f")
    cleanup_stale_uploads.update_state(task_id=task_id, state=states.SUCCESS, meta=kwargs)
  except Exception as e:
    cleanup_stale_uploads.update_state(task_id=task_id, state=states.FAILURE, meta={"error": str(e)})
    LOG.exception("Failed to cleanup stale uploads: %s", str(e))
  finally:
    redis_client.close()
