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
from typing import Any, Dict

from filebrowser.schemas import RenameSchema
from filebrowser.utils import get_user_fs

LOG = logging.getLogger()


def rename_file_or_directory(data: RenameSchema, username: str) -> Dict[str, Any]:
  """
  Renames a file or directory.

  Args:
    data (RenameSchema): The rename data.
    username (str): The user performing the operation.

  Returns:
    dict: A dictionary with a success message.

  Raises:
    ValueError: If the username is empty, or if the source path does not exist, or if the destination path already exists.
    Exception: If the rename operation fails.
  """
  if not username:
    raise ValueError("Username is required and cannot be empty.")

  source_path = data.source_path
  destination_path = data.destination_path

  fs = get_user_fs(username)

  # Handle relative destination paths
  if "/" not in destination_path:
    source_dir = os.path.dirname(source_path)
    destination_path = fs.join(source_dir, destination_path)

  # Normalize destination path after potential modification
  destination_path_normalized = fs.normpath(destination_path)

  # Check if source exists
  if not fs.exists(source_path):
    raise ValueError(f"Source path does not exist: {source_path}")

  # Check if destination already exists
  if fs.exists(destination_path_normalized):
    raise ValueError(f"Destination path already exists: {destination_path_normalized}")

  LOG.info(f"User {username} is renaming {source_path} to {destination_path_normalized}")

  try:
    fs.rename(source_path, destination_path_normalized)
  except Exception as e:
    LOG.exception(f"Error during rename operation: {e}")
    raise Exception(f"Failed to rename file: {str(e)}")

  return {"message": f"Renamed '{source_path}' to '{destination_path_normalized}' successfully"}
