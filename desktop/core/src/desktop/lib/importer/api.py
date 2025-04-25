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
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# TODO: Check if we need try/except for python-magic import because of libmagic
import magic
import polars as pl
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from desktop.lib.importer.serializers import LocalFileUploadSerializer

LOG = logging.getLogger()


# TODO: Improve error response further with better context -- Error UX Phase 2
def api_error_handler(view_fn):
  """
  Decorator to handle exceptions and return a JSON response with an error message.
  """

  @wraps(view_fn)
  def decorator(*args, **kwargs):
    try:
      return view_fn(*args, **kwargs)
    except Exception as e:
      LOG.exception(f'Error running {view_fn.__name__}: {str(e)}')
      return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  return decorator


@api_view(['POST'])
@parser_classes([MultiPartParser])
@api_error_handler
def upload_local_file(request: Request) -> Response:
  """
  Upload a local file and process it.

  Args:
    request: The request object containing the file to be uploaded.

  Returns:
    Response: A response object containing the result of the upload.

  Raises:
    ValidationError: If the file is not valid or if there are issues processing it.
  """

  # Validate the request data using the serializer
  serializer = LocalFileUploadSerializer(data=request.data)

  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  upload_file = serializer.validated_data['file']

  # Generate a unique filename
  username = request.user.username
  safe_original_name = re.sub(r'[^0-9a-zA-Z]+', '_', upload_file.name)
  unique_id = uuid.uuid4().hex[:8]

  filename = f"{username}_{unique_id}_{safe_original_name}"

  # Process the file based on its type
  result = process_uploaded_file(upload_file, filename)

  return Response(result, status=status.HTTP_201_CREATED)


def process_uploaded_file(upload_file, filename: str) -> Dict[str, Any]:
  """
  Process the uploaded file and save it to a temporary location.

  Args:
    upload_file: The uploaded file object
    filename: The base filename to use

  Returns:
    A dictionary containing the filename and file path
  """
  # Create a temporary file with our generated filename
  temp_dir = tempfile.gettempdir()
  destination_path = os.path.join(temp_dir, filename)

  try:
    # Simply write the file content to temporary location
    with open(destination_path, 'wb') as destination:
      for chunk in upload_file.chunks():
        destination.write(chunk)

    return {'filename': filename, 'file_path': destination_path}

  except Exception as e:
    # Clean up the file if there was an error
    if os.path.exists(destination_path):
      os.remove(destination_path)
    raise e


@api_view(['POST'])
@parser_classes([JSONParser])
@api_error_handler
def detect_file_metadata(request: Request) -> Response:
  """
  Detect and extract metadata from a file.

  Args:
    request: Request object containing file_path

  Returns:
    Response containing file metadata including:
    - File type
    - Format-specific metadata (delimiters, headers, etc.)
    - Column information
    - Sample data
  """
  # TODO: Check if we need only one API for both file metadata detection and field type detection
  # TODO: Something like /preview API?
  file_path = request.data.get('file_path')

  # TODO: Also change logic to support remote file paths
  import_type = request.data.get('import_type')

  if not file_path or not os.path.exists(file_path):
    return Response({'error': 'Invalid or missing file path'}, status=status.HTTP_400_BAD_REQUEST)

  # Detect file type
  file_type = _detect_file_type(file_path)

  if file_type == 'unknown':
    return Response({'error': 'Unable to detect file format'}, status=status.HTTP_400_BAD_REQUEST)

  # Extract metadata based on file type
  if file_type == 'excel':
    metadata = _get_excel_metadata(file_path)
  else:  # csv or tsv
    metadata = _get_delimited_metadata(file_path, file_type)

  return Response(metadata, status=status.HTTP_200_OK)


def _detect_file_type(file_path: str, content_sample: Optional[bytes] = None) -> str:
  """Detect file type using both extension and content analysis"""
  # Try extension first
  extension = Path(file_path).suffix.lower()[1:]

  if extension in ['xlsx', 'xls']:
    return 'excel'
  elif extension in ['csv', 'tsv']:
    return extension

  # If no extension or unknown, use libmagic to detect file type from content
  detected_type = 'unknown'
  if not extension or extension not in ['xlsx', 'xls', 'csv', 'tsv']:
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)

    if 'excel' in file_type or 'spreadsheet' in file_type:
      detected_type = 'excel'
    elif 'text' in file_type or 'csv' in file_type:
      # For text files, analyze content to determine if CSV/TSV
      detected_type = _analyze_delimited_content(file_path)

  return detected_type


def _analyze_delimited_content(file_path: str, sample_size: int = 16384) -> str:
  """Analyze content to determine if it's CSV, TSV or other format"""
  try:
    with open(file_path, 'r', encoding='utf-8') as f:
      # TODO: Make sample size configurable or atleast store in constant variable? If configuring, need to set max limit?
      sample = f.read(sample_size)
      dialect = csv.Sniffer().sniff(sample)

      if dialect.delimiter == '\t':
        return 'tsv'
      elif dialect.delimiter == ',':
        return 'csv'

  except Exception as e:
    pass
  return 'unknown'


def _get_excel_metadata(file_path: str) -> Dict[str, Any]:
  """Extract metadata for Excel files"""
  # TODO: Currently sending first sheet only, check if we need to send all sheets
  df = pl.read_excel(file_path)
  # excel_file = pl.read_excel(file_path, read_csv_options={'infer_schema_length': 1000})

  # TODO: Check if any other way to extract details of sheets
  sheet_names = pl.read_excel(file_path, sheet_id=None).keys()

  return {
    'type': 'excel',
    'sheet_names': list(sheet_names),
    'sheet_count': len(sheet_names),
    'columns': df.columns,
    'column_count': len(df.columns),
    'row_count': df.height,
    'sample_data': df.head(5).to_dict(as_series=False),
    'column_types': {col: str(df[col].dtype) for col in df.columns},
  }


def _get_delimited_metadata(file_path: str, file_type: str) -> Dict[str, Any]:
  """Extract metadata for CSV/TSV files"""
  # Sample the file first
  with open(file_path, 'r', encoding='utf-8') as f:
    # TODO: Make sample size configurable or atleast store in constant variable? If configuring, need to set max limit?
    sample = f.read(16384)

  try:
    dialect = csv.Sniffer().sniff(sample)
    has_header = csv.Sniffer().has_header(sample)
  except Exception as e:
    # Does it makes sense to have logic like below?
    # TODO: Check if we can remove it after discussion + testing.
    dialect = csv.excel
    has_header = True

  # Read with detected dialect
  df = pl.read_csv(file_path, separator=dialect.delimiter, has_header=has_header)

  return {
    'type': file_type,
    'has_header': has_header,
    'field_separator': dialect.delimiter,
    'record_separator': '\\n',  # Default to standard newline, could be improved?
    'quote_char': dialect.quotechar,
    'columns': df.columns,
    'column_count': len(df.columns),
    'row_count': df.height,
    'sample_data': df.head(5).to_dict(as_series=False),
    'column_types': {col: str(df[col].dtype) for col in df.columns},
  }
