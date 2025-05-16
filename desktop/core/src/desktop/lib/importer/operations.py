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
import re
import csv
import uuid
import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import polars as pl
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

LOG = logging.getLogger()


def local_file_upload(upload_file, username: str) -> Dict[str, str]:
  """Uploads a local file to a temporary directory with a unique filename.

  This function takes an uploaded file and username, generates a unique filename,
  and saves the file to a temporary directory. The filename is created using
  the username, a unique ID, and a sanitized version of the original filename.

  Args:
    upload_file: The uploaded file object from Django's file upload handling.
    username: The username of the user uploading the file.

  Returns:
    Dict[str, str]: A dictionary containing:
      - file_path: The full path where the file was saved

  Raises:
    ValueError: If upload_file or username is None/empty
    Exception: If there are issues with file operations

  Example:
    >>> result = upload_local_file(request.FILES['file'], 'hue_user')
    >>> print(result)
    {'file_path': '/tmp/hue_user_a1b2c3d4_myfile.txt'}
  """
  if not upload_file:
    raise ValueError("Upload file cannot be None or empty")

  if not username:
    raise ValueError("Username cannot be None or empty")

  # Generate a unique filename
  unique_id = uuid.uuid4().hex[:8]
  filename = f"{username}_{unique_id}_{upload_file.name}"

  # Create a temporary file with our generated filename
  temp_dir = tempfile.gettempdir()
  destination_path = os.path.join(temp_dir, filename)

  try:
    # Simply write the file content to temporary location
    with open(destination_path, 'wb') as destination:
      for chunk in upload_file.chunks():
        destination.write(chunk)

    return {'file_path': destination_path}

  except Exception as e:
    # Clean up the file if there was an error
    if os.path.exists(destination_path):
      os.remove(destination_path)
    raise e
