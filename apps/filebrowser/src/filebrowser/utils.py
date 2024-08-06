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
import io
import os
import logging
from datetime import datetime
from urllib.parse import urlparse

import redis

from desktop.conf import TASK_SERVER_V2
from desktop.lib.django_util import JsonResponse
from filebrowser.conf import ARCHIVE_UPLOAD_TEMPDIR

LOG = logging.getLogger()


DEFAULT_WRITE_SIZE = 1024 * 1024 * 128


def calculate_total_size(uuid, totalparts):
  total = 0
  files = [os.path.join(ARCHIVE_UPLOAD_TEMPDIR.get(), f'{uuid}_{i}') for i in range(totalparts)]
  for file_path in files:
    try:
      total += os.path.getsize(file_path)
    except FileNotFoundError:
      LOG.error(f"calculate_total_size: The file '{file_path}' does not exist.")
    except OSError as e:
      LOG.error(f"calculate_total_size: For the file '{file_path}' error occurred: {e}")
  return total


def generate_chunks(uuid, totalparts, default_write_size=DEFAULT_WRITE_SIZE):
  fp = io.BytesIO()
  total = 0
  files = [os.path.join(ARCHIVE_UPLOAD_TEMPDIR.get(), f'{uuid}_{i}') for i in range(totalparts)]
  for file_path in files:
    with open(file_path, 'rb') as f:
      while True:
        # Read the file in portions, e.g., 1MB at a time
        portion = f.read(1 * 1024 * 1024)
        if not portion:
          break
        fp.write(portion)
        total = total + len(portion)
        # If buffer size is more than 128MB, yield the chunk
        if fp.tell() >= default_write_size:
          fp.seek(0)
          yield fp, total
          fp.close()
          fp = io.BytesIO()
  # Yield any remaining data in the buffer
  if fp.tell() > 0:
    fp.seek(0)
    yield fp, total + fp.tell()
    fp.close()
  # chances are the chunk is zero and we never yielded
  else:
    fp.close()
  for file_path in files:
    os.remove(file_path)


def parse_broker_url(broker_url):
  parsed_url = urlparse(broker_url)
  host = parsed_url.hostname
  port = parsed_url.port
  db = int(parsed_url.path.lstrip('/'))
  return redis.Redis(host=host, port=port, db=db)


def get_available_space_for_file_uploads(request):
  redis_client = parse_broker_url(TASK_SERVER_V2.BROKER_URL.get())
  try:
    upload_available_space = int(redis_client.get('upload_available_space'))
    if upload_available_space is None:
      raise ValueError("upload_available_space key not set in Redis")
    return JsonResponse({'upload_available_space': upload_available_space})
  except Exception as e:
    LOG.exception("Failed to get available space: %s", str(e))
    return JsonResponse({'error': str(e)}, status=500)
  finally:
    redis_client.close()


def reserve_space_for_file_uploads(uuid, file_size):
  redis_client = parse_broker_url(TASK_SERVER_V2.BROKER_URL.get())
  try:
    upload_available_space = int(redis_client.get('upload_available_space'))
    if upload_available_space is None:
      raise ValueError("upload_available_space key not set in Redis")
    if upload_available_space >= file_size:
      redis_client.decrby('upload_available_space', file_size)
      redis_client.set(f'upload__{uuid}', file_size)
      redis_client.set(f'upload__{uuid}_timestamp', int(datetime.now().timestamp()))
      return True
    else:
      return False
  except Exception as e:
    LOG.exception("Failed to reserve space: %s", str(e))
    return False
  finally:
    redis_client.close()


def release_reserved_space_for_file_uploads(uuid):
  redis_client = parse_broker_url(TASK_SERVER_V2.BROKER_URL.get())
  try:
    reserved_space = redis_client.get(f'upload__{uuid}')
    if reserved_space:
      file_size = int(redis_client.get(f'upload__{uuid}'))
      redis_client.incrby('upload_available_space', file_size)
      redis_client.delete(f'upload__{uuid}')
      redis_client.delete(f'upload__{uuid}_timestamp')
  except Exception as e:
    LOG.exception("Failed to release reserved space: %s", str(e))
  finally:
    redis_client.close()
