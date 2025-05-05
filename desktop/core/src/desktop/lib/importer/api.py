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

import polars as pl
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from desktop.lib.importer.operations import local_file_upload
from desktop.lib.importer.serializers import LocalFileUploadSerializer

LOG = logging.getLogger()

try:
  import magic

  is_magic_lib_available = True
except ImportError as e:
  LOG.exception(f'Failed to import python-magic: {str(e)}')
  is_magic_lib_available = False


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
  file_path = request.query_params.get('file_path')
  import_type = request.query_params.get('import_type')

  # TODO: Add serializer for validating query params
  if not file_path:
    return Response({'error': "Missing parameters: file_path is required."}, status=status.HTTP_400_BAD_REQUEST)

  if not import_type:
    return Response({'error': "Missing parameters: import_type is required."}, status=status.HTTP_400_BAD_REQUEST)

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
  """Detect the file type based on its content."""
  # Use libmagic to detect file type from its sample content
  # Not depending on file extension as it can be misleading sometimes such as a CSV file with TSV or Excel content
  detected_type = 'unknown'
  if not is_magic_lib_available:
    error = "Unable to guess file type. python-magic or its dependency libmagic is not installed."
    LOG.error(error)
    raise Exception(error)

  file_type = magic.from_buffer(file_sample, mime=True)

  if 'excel' in file_type or 'spreadsheet' in file_type:
    detected_type = 'excel'
  elif 'text' in file_type or 'csv' in file_type:
    # For text files, analyze content later to determine if CSV/TSV or other related format
    detected_type = 'delimiter_format'

  return detected_type


def _get_excel_metadata(fh) -> Dict[str, Any]:
  """Extract metadata for Excel files (.xlsx, .xls)"""
  try:
    fh.seek(0)  # Reset file handle first
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
  """Extract metadata for delimited files (CSV, TSV, etc.)"""
  try:
    # Convert bytes to string if needed
    if isinstance(file_sample, bytes):
      file_sample = file_sample.decode('utf-8', errors='replace')

    dialect = csv.Sniffer().sniff(file_sample)

    # After sniffing, try determining the file type based on the delimiter for better distinction
    if file_type == 'delimiter_format':
      if dialect.delimiter == ',':
        file_type = 'csv'
      elif dialect.delimiter == '\t':
        file_type = 'tsv'
      # TODO: We can try mapping other delimiters like '|', ';', etc. if needed else generic 'delimiter_format' is set as file_type

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


@api_view(['GET'])
@parser_classes([JSONParser])
@api_error_handler
def preview_file(request: Request) -> Response:
  """Preview a file based on its path and import type.

  Args:
    request: Request object containing file_path and import_type
  Returns:
    Response containing a preview of the file content
  """
  file_path = request.query_params.get('file_path')
  file_type = request.query_params.get('file_type')
  import_type = request.query_params.get('import_type')
  sql_dialect = request.query_params.get('sql_dialect')
  has_header = request.query_params.get('has_header')

  # TODO: Add serializer for validating query params
  if not file_path:
    return Response({'error': "Missing parameters: file_path is required."}, status=status.HTTP_400_BAD_REQUEST)

  if not import_type:
    return Response({'error': "Missing parameters: import_type is required."}, status=status.HTTP_400_BAD_REQUEST)

  if not file_type:
    return Response({'error': "Missing parameters: file_type is required."}, status=status.HTTP_400_BAD_REQUEST)

  if not sql_dialect:
    return Response({'error': "Missing parameters: sql_dialect is required."}, status=status.HTTP_400_BAD_REQUEST)

  if (import_type == 'local' and not os.path.isfile(file_path)) or (import_type == 'remote' and not request.fs.exists(file_path)):
    return Response({'error': f'File does not exist: {file_path}'}, status=status.HTTP_404_NOT_FOUND)

  fh = open(file_path, 'rb') if import_type == 'local' else request.fs.open(file_path, 'rb')
  try:
    if file_type == 'excel':
      sheet_name = request.query_params.get('sheet_name')

      if not sheet_name:
        return Response({'error': "Missing parameters: sheet_name is required."}, status=status.HTTP_400_BAD_REQUEST)

      result = _preview_excel_file(fh, file_type, sheet_name, sql_dialect, has_header)
    elif file_type in ['csv', 'tsv', 'delimiter_format']:
      field_separator = request.query_params.get('field_separator', ',')
      quote_char = request.query_params.get('quote_char', '"')
      record_separator = request.query_params.get('record_separator', '\n')

      if not field_separator or not quote_char or not record_separator:
        return Response(
          {'error': "Missing parameters: field_separator, quote_char, and record_separator are required."},
          status=status.HTTP_400_BAD_REQUEST,
        )

      result = _preview_delimited_file(fh, file_type, field_separator, quote_char, record_separator, sql_dialect, has_header)
    else:
      return Response({'error': f'Unsupported file type: {file_type}'}, status=status.HTTP_400_BAD_REQUEST)
  finally:
    # Close the file handle
    fh.close()

  return Response(result, status=status.HTTP_200_OK)


def _preview_excel_file(fh, file_type: str, sheet_name: str, dialect: str, has_header) -> Response:
  """Preview an Excel file (.xlsx, .xls)"""
  try:
    if has_header is None:
      fh.seek(0)
      csv_snippet = pl.read_excel(source=BytesIO(fh.read()), sheet_name=sheet_name).head(20).write_csv(file=None)

      if isinstance(csv_snippet, bytes):
        csv_snippet = csv_snippet.decode('utf-8', errors='replace')

      has_header = csv.Sniffer().has_header(csv_snippet)

    fh.seek(0)
    df = pl.read_excel(BytesIO(fh.read()), sheet_name=sheet_name, has_header=has_header)

    schema = df.schema
    preview_data = df.head(50).to_dict(as_series=False)

    result = {
      'type': file_type,
      'has_header': has_header,
      'columns': [{'name': col, 'type': map_polars_to_sql(dialect, str(schema[col]))} for col in df.columns],
      'preview_data': preview_data,
    }

    return result

  except Exception as e:
    message = f"Error previewing Excel file: {e}"
    LOG.error(message, exc_info=True)
    raise Exception(message)


def _preview_delimited_file(
  fh, file_type: str, field_separator: str, quote_char: str, record_separator: str, dialect: str, has_header
) -> Response:
  """Preview a delimited file (CSV, TSV, etc.)"""
  try:
    if has_header is None:
      fh.seek(0)
      has_header = csv.Sniffer().has_header(fh.read(16 * 1024).decode('utf-8', errors='replace'))

    fh.seek(0)
    df = pl.read_csv(
      BytesIO(fh.read()),
      separator=field_separator,
      quote_char=quote_char,
      eol_char=record_separator,
      has_header=has_header,
      ignore_errors=True,
    )

    schema = df.schema
    preview_data = df.head(50).to_dict(as_series=False)

    result = {
      'type': file_type,
      'has_header': has_header,
      'columns': [{'name': col, 'type': map_polars_to_sql(dialect, str(schema[col]))} for col in df.columns],
      'preview_data': preview_data,
    }

    return result

  except Exception as e:
    message = f"Error previewing delimited file: {e}"
    LOG.error(message, exc_info=True)
    raise Exception(message)


def map_polars_to_sql(dialect: str, polars_type: str) -> str:
  """
  Map a Polars dtype to the corresponding SQL type for a given dialect.

  Supports all Polars dtypes as listed in the Polars docs:
  Int8, Int16, Int32, Int64, UInt8, UInt16, UInt32, UInt64,
  Float32, Float64, Decimal, Boolean, Utf8/String, Categorical, Enum,
  Binary, Date, Time, Datetime, Duration, Array, List, Struct,
  Object, Null, Unknown.

  Args:
    dialect: One of "hive", "impala", "trino", "phoenix", "sparksql".
    polars_type: Polars dtype name as string.

  Returns:
    A string representing the SQL type.

  Raises:
    ValueError: If the dialect or polars_type is not supported.
  """
  # Base mapping for most engines (Hive, Impala, SparkSQL)
  base_map = {
    # signed ints
    "Int8": "TINYINT",
    "Int16": "SMALLINT",
    "Int32": "INT",
    "Int64": "BIGINT",
    # unsigned ints → same size signed by default (Hive/Impala/SparkSQL)
    "UInt8": "TINYINT",
    "UInt16": "SMALLINT",
    "UInt32": "INT",
    "UInt64": "BIGINT",
    # floats & decimal
    "Float32": "FLOAT",
    "Float64": "DOUBLE",
    "Decimal": "DECIMAL",  # Hive/Impala/SparkSQL use DECIMAL(precision,scale)
    # boolean, string, binary
    "Boolean": "BOOLEAN",
    "Utf8": "STRING",  # STRING covers Hive/VARCHAR/CHAR for default
    "String": "STRING",
    "Categorical": "STRING",
    "Enum": "STRING",
    "Binary": "BINARY",
    # temporal
    "Date": "DATE",
    "Time": "TIMESTAMP",  # Hive/Impala/SparkSQL have no pure TIME type
    "Datetime": "TIMESTAMP",
    "Duration": "INTERVAL DAY TO SECOND",
    # nested & other
    "Array": "ARRAY",
    "List": "ARRAY",
    "Struct": "STRUCT",
    "Object": "STRING",
    "Null": "STRING",  # no SQL NULL type—use STRING or handle as special case
    "Unknown": "STRING",
  }

  # Per‑dialect overrides for the few differences
  overrides = {
    "hive": {},
    "impala": {},
    "sparksql": {},
    "trino": {
      "Int32": "INTEGER",
      "UInt32": "INTEGER",
      "Utf8": "VARCHAR",
      "String": "VARCHAR",
      "Binary": "VARBINARY",
      "Float32": "REAL",
      "Struct": "ROW",
      "Object": "JSON",
      "Duration": "INTERVAL DAY TO SECOND",  # explicit SQL syntax
    },
    "phoenix": {
      **{f"UInt{b}": f"UNSIGNED_{t}" for b, t in [(8, "TINYINT"), (16, "SMALLINT"), (32, "INT"), (64, "LONG")]},
      "Utf8": "VARCHAR",
      "String": "VARCHAR",
      "Binary": "VARBINARY",
      "Duration": "STRING",  # Phoenix treats durations as strings
      "Struct": "STRING",  # no native STRUCT type
      "Object": "VARCHAR",
      "Time": "TIME",  # Phoenix has its own TIME type
      "Decimal": "DECIMAL",  # up to precision 38
    },
  }

  dl = dialect.lower()
  if dl not in overrides:
    raise ValueError(f"Unsupported dialect: {dialect}")

  # Merge base_map and overrides[dl] into a new dict, giving precedence to any overlapping keys in overrides[dl]
  mapping = {**base_map, **overrides[dl]}

  if polars_type not in mapping:
    raise ValueError(f"No mapping for Polars dtype {polars_type} in dialect {dialect}")

  return mapping[polars_type]
