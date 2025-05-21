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
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union

import polars as pl
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

LOG = logging.getLogger()

# Import this at the module level to avoid repeatedly checking availability
try:
  import magic

  is_magic_lib_available = True
except ImportError as e:
  LOG.exception(f'Failed to import python-magic: {str(e)}')
  is_magic_lib_available = False


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


def guess_file_metadata(file_path: str, import_type: str, fs=None) -> Dict[str, Any]:
  """
  Guess the metadata of a file based on its content or extension.

  Args:
    file_path: Path to the file to analyze
    import_type: Type of import ('local' or 'remote')
    fs: File system object for remote files (default: None)

  Returns:
    Dict containing the file metadata:
      - type: File type (e.g., excel, csv, tsv)
      - sheet_names: List of sheet names (for Excel files)
      - field_separator: Field separator character (for delimited files)
      - quote_char: Quote character (for delimited files)
      - record_separator: Record separator (for delimited files)

  Raises:
    ValueError: If the file does not exist or parameters are invalid
    Exception: For various file processing errors
  """
  # Check if file exists based on import type
  if import_type == 'local' and not os.path.isfile(file_path):
    raise ValueError(f'Local file does not exist: {file_path}')
  elif import_type == 'remote' and fs and not fs.exists(file_path):
    raise ValueError(f'Remote file does not exist: {file_path}')

  # Open file based on import type
  fh = open(file_path, 'rb') if import_type == 'local' else fs.open(file_path, 'rb')

  try:
    # Read sample of file content for analysis
    sample = fh.read(16 * 1024)  # Read 16 KiB sample

    # Detect file type from content
    file_type = _detect_file_type(sample)

    if file_type == 'unknown':
      raise ValueError('Unable to detect file format')

    # Extract metadata based on detected file type
    if file_type == 'excel':
      metadata = _get_excel_metadata(fh)
    else:
      # CSV, TSV, or other delimited formats
      metadata = _get_delimited_metadata(sample, file_type)

    return metadata

  finally:
    # Ensure file handle is closed
    fh.close()


def _detect_file_type(file_sample) -> str:
  """
  Detect the file type based on its content.

  Args:
    file_sample: Binary sample of the file content

  Returns:
    String indicating the detected file type ('excel', 'delimiter_format', or 'unknown')

  Raises:
    Exception: If python-magic is not available
  """
  # Check if magic library is available
  if not is_magic_lib_available:
    error = "Unable to guess file type. python-magic or its dependency libmagic is not installed."
    LOG.error(error)
    raise Exception(error)

  # Use libmagic to detect MIME type from content
  file_type = magic.from_buffer(file_sample, mime=True)

  # Map MIME type to our simplified type categories
  if 'excel' in file_type or 'spreadsheet' in file_type:
    return 'excel'
  elif 'text' in file_type or 'csv' in file_type:
    # For text files, we'll analyze the content later to determine specific format
    return 'delimiter_format'

  return 'unknown'


def _get_excel_metadata(fh: BinaryIO) -> Dict[str, Any]:
  """
  Extract metadata for Excel files (.xlsx, .xls).

  Args:
    fh: File handle for the Excel file

  Returns:
    Dict containing Excel metadata:
      - type: 'excel'
      - sheet_names: List of sheet names

  Raises:
    Exception: If there's an error processing the Excel file
  """
  try:
    # Reset file position to beginning
    fh.seek(0)

    # Read Excel file and get sheet names
    sheet_names = pl.read_excel(BytesIO(fh.read()), sheet_id=0).keys()

    return {
      'type': 'excel',
      'sheet_names': list(sheet_names),
    }
  except Exception as e:
    message = f"Error detecting Excel file format: {e}"
    LOG.error(message, exc_info=True)
    raise Exception(message)


def _get_delimited_metadata(file_sample, file_type: str) -> Dict[str, Any]:
  """
  Extract metadata for delimited files (CSV, TSV, etc.).

  Args:
    file_sample: Binary or string sample of the file content
    file_type: Initial file type detection ('delimiter_format')

  Returns:
    Dict containing delimited file metadata:
      - type: Specific file type ('csv', 'tsv', etc.)
      - field_separator: Field separator character
      - quote_char: Quote character
      - record_separator: Record separator character

  Raises:
    Exception: If there's an error processing the delimited file
  """
  try:
    # Convert binary sample to string if needed
    if isinstance(file_sample, bytes):
      file_sample = file_sample.decode('utf-8', errors='replace')

    # Use CSV Sniffer to detect delimiter and other formatting
    dialect = csv.Sniffer().sniff(file_sample)

    # Refine file type based on detected delimiter
    if file_type == 'delimiter_format':
      if dialect.delimiter == ',':
        file_type = 'csv'
      elif dialect.delimiter == '\t':
        file_type = 'tsv'
      # Other delimiters remain as 'delimiter_format'

    return {
      'type': file_type,
      'field_separator': dialect.delimiter,
      'quote_char': dialect.quotechar,
      'record_separator': dialect.lineterminator,
    }
  except Exception as e:
    message = f"Error detecting delimited file format: {e}"
    LOG.error(message, exc_info=True)
    raise Exception(message)
