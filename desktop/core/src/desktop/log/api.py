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
import time
import socket
import logging
import zipfile
import tempfile
from wsgiref.util import FileWrapper

from django.http import HttpResponse

from desktop.auth.backend import is_admin
from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import smart_str
from desktop.log import DEFAULT_LOG_DIR

LOG = logging.getLogger()


# TODO: Improve error response further with better context -- Error UX Phase 2
def api_error_handler(view_fn):
  """
  Decorator to handle exceptions and return a JSON response with an error message.
  """

  def decorator(*args, **kwargs):
    try:
      return view_fn(*args, **kwargs)
    except Exception as e:
      LOG.exception(f'Error running {view_fn.__name__}: {str(e)}')
      return JsonResponse({'error': str(e)}, status=500)

  return decorator


@api_error_handler
def get_hue_logs(request):
  """
  Retrieves the last X characters of log messages from the log file.

  Args:
    request: The HTTP request object.

  Returns:
    A JSON response containing the current hostname and log messages.

  Raises:
    403: If user accessing the endpoint in not a Hue admin.
    404: If the log directory or file does not exist.
    500: If an internal server error occurs.

  Notes:
    This endpoint retrieves the last X characters of log messages from the log file.
    The log file is read up to the buffer size, and if it's smaller than the buffer size,
    the previous log file is read to complete the buffer.
  """
  if not is_admin(request.user):
    return HttpResponse("You must be a Hue admin to access this endpoint.", status=403)

  # Buffer size for reading log files
  LOG_BUFFER_SIZE = 32 * 1024

  log_directory = os.getenv("DESKTOP_LOG_DIR", DEFAULT_LOG_DIR)
  if not log_directory:
    return HttpResponse('The log directory is not set or does not exist.', status=404)

  log_file = os.path.join(log_directory, 'rungunicornserver.log')
  if not os.path.exists(log_file):
    return HttpResponse('The log file does not exist.', status=404)

  log_file_size = os.path.getsize(log_file)

  # Read the log file contents
  buffer = _read_log_file(LOG_BUFFER_SIZE, log_file, log_file_size)

  # If the log file is smaller than the buffer size, read the previous log file
  if log_file_size < LOG_BUFFER_SIZE:
    previous_log_file = os.path.join(log_directory, 'rungunicornserver.log.1')

    if os.path.exists(previous_log_file):
      prev_log_file_size = os.path.getsize(previous_log_file)
      # Read the previous log file contents
      buffer = _read_previous_log_file(LOG_BUFFER_SIZE, previous_log_file, prev_log_file_size, log_file_size) + buffer

  response = {'hue_hostname': socket.gethostname(), 'logs': ''.join(buffer)}
  return JsonResponse(response)


@api_error_handler
def download_hue_logs(request):
  """
  Downloads the last X characters of log messages from the log file as a zip attachment.

  Args:
    request: The HTTP request object.

  Returns:
    A zip file containing the log messages.

  Raises:
    403: If user accessing the endpoint in not a Hue admin.
    404: If the log directory or log file does not exist.
    500: If an internal server error occurs.

  Notes:
    This endpoint downloads the last X characters of log messages from the log file as a zip attachment.
    The log file is read up to the buffer size, and if it's smaller than the buffer size,
    the previous log file is read to complete the buffer.
  """
  if not is_admin(request.user):
    return HttpResponse("You must be a Hue admin to access this endpoint.", status=403)

  # Buffer size for reading log files for download (1 MiB)
  LOG_DOWNLOAD_BUFFER_SIZE = 1024 * 1024

  log_directory = os.getenv("DESKTOP_LOG_DIR", DEFAULT_LOG_DIR)
  if not log_directory:
    return HttpResponse('The log directory is not set or does not exist.', status=404)

  log_file = os.path.join(log_directory, 'rungunicornserver.log')
  if not os.path.exists(log_file):
    return HttpResponse('The log file does not exist.', status=404)

  log_file_size = os.path.getsize(log_file)

  # Read the log file contents
  buffer = _read_log_file(LOG_DOWNLOAD_BUFFER_SIZE, log_file, log_file_size)

  # If the log file is smaller than the buffer size, read the previous log file
  if log_file_size < LOG_DOWNLOAD_BUFFER_SIZE:
    previous_log_file = os.path.join(log_directory, 'rungunicornserver.log.1')

    if os.path.exists(previous_log_file):
      prev_log_file_size = os.path.getsize(previous_log_file)
      # Read the previous log file contents
      buffer = _read_previous_log_file(LOG_DOWNLOAD_BUFFER_SIZE, previous_log_file, prev_log_file_size, log_file_size) + buffer

  # Avoid loading large logs into memory by writing to a temp file line-by-line, allowing zipfile to handle the data more efficiently
  log_tmp = tempfile.NamedTemporaryFile("w+t", encoding='utf-8')
  for line in buffer:
    log_tmp.write(smart_str(line, errors='replace'))
  # Without flush, there is a chance to get truncated logs
  log_tmp.flush()

  tmp = tempfile.NamedTemporaryFile()
  zip_file = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
  zip_file.write(log_tmp.name, f"hue-logs/hue-{time.time()}.log")
  zip_file.close()
  length = tmp.tell()

  # If we don't seek to start of file, no bytes will be written
  tmp.seek(0)
  wrapper = FileWrapper(tmp)
  # Return the zip file as a response and set the Content-Disposition header to force the browser to download the file
  response = HttpResponse(wrapper, content_type="application/zip")
  response['Content-Disposition'] = f'attachment; filename=hue-logs-{time.time()}.zip'
  response['Content-Length'] = length

  return response


def _read_log_file(log_buffer_size, log_file, log_file_size):
  """
  Reads the log file contents up to the buffer size.

  Args:
    log_buffer_size: Maximum buffer size for reading logs.
    log_file: The log file path.
    log_file_size: The log file size.

  Returns:
    A list of log lines.
  """
  with open(log_file, 'rb') as fh:
    if log_file_size > log_buffer_size:
      fh.seek(log_file_size - log_buffer_size)
    else:
      fh.seek(0)
    return [line.decode('utf-8') for line in fh.readlines()]


def _read_previous_log_file(log_buffer_size, previous_log_file, prev_log_file_size, log_file_size):
  """
  Reads the previous log file contents up to the buffer size.

  Args:
    log_buffer_size: Maximum buffer size for reading logs.
    previous_log_file: The previous log file path.
    prev_log_file_size: The previous log file size.
    log_file_size: The current log file size.

  Returns:
    A list of log lines.
  """
  with open(previous_log_file, 'rb') as fh1:
    start_pos = max(0, prev_log_file_size - log_buffer_size - log_file_size)
    fh1.seek(start_pos)
    return [line.decode('utf-8') for line in fh1.readlines()]
