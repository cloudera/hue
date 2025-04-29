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
from io import BytesIO
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

from desktop.lib.importer.operations import local_file_upload
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
def upload_file(request: Request) -> Response:
  """Handle the local file upload operation.

  This endpoint allows users to upload a file from their local system.
  Uploaded file is validated using LocalFileUploadSerializer and processed using local_file_upload operation.

  Args:
    request: Request object containing the file to upload

  Returns:
    Response containing the result of the upload operation

  Note:
    - File size limits apply based on server configuration
    - Supported file types: CSV, TSV, Excel
  """

  # Validate the request data using the serializer
  serializer = LocalFileUploadSerializer(data=request.data)

  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  upload_file = serializer.validated_data['file']

  LOG.info(f'User {request.user.username} is uploading a local file: {upload_file.name}')
  res = local_file_upload(upload_file, request.user.username)

  return Response(res, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@parser_classes([JSONParser])
@api_error_handler
def guess_file_metadata(request: Request) -> Response:
  """
  Guess the metadata of a file based on its content or extension.

  Args:
    request: Request object containing file_path and import_type

  Returns:
    Response containing file metadata including:
      - type: File type (e.g., excel, csv, tsv)
      - sheet_names: List of sheet names (for Excel files)
      - field_separator: Field separator character
      - quote_char: Quote character
      - record_separator: Record separator
  """
  file_path = request.data.get('file_path')
  import_type = request.data.get('import_type')

  if not file_path or not os.path.exists(file_path):
    return Response({'error': "Missing parameters: file_path is required."}, status=status.HTTP_400_BAD_REQUEST)

  if (import_type == 'local' and not os.path.isfile(file_path)) or (import_type == 'remote' and not request.fs.exists(file_path)):
    return Response({'error': f'File does not exist: {file_path}'}, status=status.HTTP_404_NOT_FOUND)

  fh = open(file_path, 'rb') if import_type == 'local' else request.fs.open(file_path, 'rb')
  try:
    sample = fh.read(16 * 1024)  # Read 16 KiB sample of the file to analyze its content

    # Detect file type
    file_type = _detect_file_type(file_path, sample)

    if file_type == 'unknown':
      return Response({'error': 'Unable to detect file format'}, status=status.HTTP_400_BAD_REQUEST)

    # Extract metadata based on file type
    if file_type == 'excel':
      metadata = _get_excel_metadata(fh)
    else:
      # CSV or TSV or other delimited formats
      metadata = _get_delimited_metadata(sample, file_type)  # Send sample for sniffing
  finally:
    # Close the file handle
    fh.close()

  return Response(metadata, status=status.HTTP_200_OK)


def _detect_file_type(file_path: str, file_sample) -> str:
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
    file_type = magic.from_buffer(file_sample, mime=True)

    if 'excel' in file_type or 'spreadsheet' in file_type:
      detected_type = 'excel'
    elif 'text' in file_type or 'csv' in file_type:
      # For text files, analyze content later to determine if CSV/TSV or other related format
      detected_type = 'delimited_other'

  return detected_type


def _get_excel_metadata(fh) -> Dict[str, Any]:
  """Extract metadata for Excel files (.xlsx, .xls)"""
  fh.seek(0)  # Reset file handle to read the file again
  sheet_names = pl.read_excel(BytesIO(fh.read()), sheet_id=0).keys()

  return {
    'type': 'excel',
    'sheet_names': list(sheet_names),
  }


def _get_delimited_metadata(file_sample, file_type: str) -> Dict[str, Any]:
  """Extract metadata for delimited files (CSV, TSV, etc.)"""
  try:
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(file_sample)
    # has_header = sniffer.has_header(file_sample)  # TODO: Need to do like old implementation to check for has_header?

    # TODO: Should we handle scenario where user uploads a file with extension .csv but the content is actually TSV or other format?
    if file_type == 'delimited_other':
      # TODO: Extend to support other delimiters like '|', ';', etc. if needed else generic 'delimited_other' is set as file_type
      if dialect.delimiter == '\t':
        file_type = 'tsv'
      elif dialect.delimiter == ',':
        file_type = 'csv'

    return {
      'type': file_type,
      # 'has_header': has_header,
      'field_separator': dialect.delimiter,
      'quote_char': dialect.quotechar,
      'record_separator': dialect.lineterminator,
    }

  except Exception as e:
    LOG.error(f"Error detecting file format: {e}")
    return {}
