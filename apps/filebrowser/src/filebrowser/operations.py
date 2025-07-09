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
import os
import posixpath
from io import BytesIO
from typing import Any, Dict, Union

from filebrowser.schemas import SimpleFileUploadSchema
from filebrowser.utils import get_user_filesystem
from filebrowser.views import filetype, rwx, stat_absolute_path

LOG = logging.getLogger()


def simple_file_upload(data: SimpleFileUploadSchema, username: str) -> Dict[str, Any]:
  """
  Uploads a file to the specified destination using the filesystem's simple_file_upload method.

  This function handles the core upload logic, including validation, path checking,
  and delegating to the appropriate filesystem handler. It supports multiple input types
  for maximum flexibility across different usage contexts (web, CLI, MCP).

  Args:
    data: A Pydantic schema containing the file to upload, destination path, and overwrite flag
    username: The username of the user uploading the file

  Returns:
    Dict[str, Any]: A dictionary containing:
      - uploaded_file_stats: Statistics about the uploaded file
      - path: The full path where the file was uploaded

  Raises:
    FileNotFoundError: If the destination path doesn't exist
    FileExistsError: If the file already exists and overwrite is False
    PermissionError: If the user doesn't have write access to the destination
    Exception: For other filesystem-related errors
  """
  destination_path = data.destination_path
  overwrite = data.overwrite

  fs = get_user_filesystem(username)

  # Check if the destination path is a directory and the file name contains a path separator
  # This prevents directory traversal attacks
  if fs.isdir(destination_path) and posixpath.sep in data.filename:
    raise ValueError("Invalid filename. Path separators are not allowed.")

  # Determine the full file path
  if fs.isdir(destination_path):
    filepath = fs.join(destination_path, data.filename)
  else:
    # If destination is not a directory, use it as the full file path
    filepath = destination_path
    destination_path = os.path.dirname(filepath)

  # Check if the destination directory exists
  if not fs.exists(destination_path):
    raise FileNotFoundError(f"The destination path {destination_path} does not exist.")

  # Check if the file already exists
  if fs.exists(filepath):
    if overwrite:
      try:
        fs.rmtree(filepath)
      except Exception as e:
        LOG.exception(f"Failed to remove existing file at {filepath}")
        raise Exception(f"Failed to remove already existing file: {e}")
    else:
      raise FileExistsError(f"The file {data.filename} already exists at the destination path.")

  # Prepare file data for upload
  file_data = _prepare_file_data(data.file)
  try:
    fs.simple_file_upload(file_data=file_data, destination=filepath, username=username)

    stats = fs.stats(filepath)
    result = {"uploaded_file_stats": _massage_stats(fs, stat_absolute_path(filepath, stats)), "path": filepath}
    return result

  except Exception as e:
    LOG.exception(f"Failed to upload file to {filepath}")

    if "permission" in str(e).lower():
      raise PermissionError(f'User {username} does not have permissions to write to path "{destination_path}".')
    else:
      raise Exception(f"Upload to {filepath} failed: {str(e)}")


def _prepare_file_data(file_obj: Any) -> Union[BytesIO, bytes]:
  """
  Prepare file data from various input types.

  Args:
      file_obj: Can be Django UploadedFile, file-like object, or bytes

  Returns:
      BytesIO or bytes object containing the file data
  """
  # Handle Django UploadedFile
  if hasattr(file_obj, "chunks"):
    file_data = BytesIO()
    for chunk in file_obj.chunks():
      file_data.write(chunk)
    file_data.seek(0)
    return file_data

  # Handle file-like object with read() method
  elif hasattr(file_obj, "read"):
    if hasattr(file_obj, "seek"):
      file_obj.seek(0)
    data = file_obj.read()
    if isinstance(data, str):
      data = data.encode("utf-8")
    return BytesIO(data)

  # Handle raw bytes
  elif isinstance(file_obj, bytes):
    return BytesIO(file_obj)

  # Handle string data
  elif isinstance(file_obj, str):
    return BytesIO(file_obj.encode("utf-8"))

  else:
    raise ValueError(f"Unsupported file object type: {type(file_obj)}")


def _massage_stats(fs, stats):
  """
  Massage a stats record as returned by the filesystem implementation
  into the format expected by the API response.
  """
  stats_dict = stats.to_json_dict()
  normalized_path = fs.normpath(stats_dict.get("path"))

  stats_dict.update(
    {
      "path": normalized_path,
      "type": filetype(stats.mode),
      "rwx": rwx(stats.mode, stats.aclBit),
    }
  )

  return stats_dict
