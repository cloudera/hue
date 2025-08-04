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
from functools import wraps

from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from desktop.lib.importer import operations
from desktop.lib.importer.serializers import (
  GuessFileHeaderSerializer,
  GuessFileMetadataSerializer,
  LocalFileUploadSerializer,
  PreviewFileSerializer,
  SqlTypeMapperSerializer,
)

LOG = logging.getLogger()


# TODO: Improve error response further with better context -- Error UX Phase 2
def api_error_handler(fn):
  """
  Decorator to handle exceptions and return a JSON response with an error message.
  """

  @wraps(fn)
  def decorator(*args, **kwargs):
    try:
      return fn(*args, **kwargs)
    except Exception as e:
      LOG.exception(f"Error running {fn.__name__}: {str(e)}")
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  return decorator


@api_view(["POST"])
@parser_classes([MultiPartParser])
@api_error_handler
def local_file_upload(request: Request) -> Response:
  """Handle the local file upload operation.

  This endpoint allows users to upload a file from their local system.
  Uploaded file is validated using LocalFileUploadSerializer and processed using local_file_upload operation.

  Args:
    request: Request object containing the file to upload

  Returns:
    Response containing the result of the local upload operation, including:
      - file_path: Path where the file was saved (if successful)

  Note:
    - File size limits apply based on MAX_LOCAL_FILE_SIZE_UPLOAD_LIMIT configuration.
    - File type restrictions apply based on RESTRICT_LOCAL_FILE_EXTENSIONS configuration.
  """

  serializer = LocalFileUploadSerializer(data=request.data)

  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  upload_data = serializer.validated_data

  LOG.info(f"User {request.user.username} is uploading a local file: {upload_data.filename}")
  result = operations.local_file_upload(upload_data, request.user.username)

  return Response(result, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@parser_classes([JSONParser])
@api_error_handler
def guess_file_metadata(request: Request) -> Response:
  """Guess the metadata of a file based on its content or extension.

  This API endpoint detects file type and extracts metadata properties such as
  delimiters for CSV files or sheet names for Excel files.

  Args:
    request: Request object containing query parameters:
      - file_path: Path to the file
      - import_type: 'local' or 'remote'

  Returns:
    Response containing file metadata including:
      - type: File type (e.g., excel, csv, tsv)
      - sheet_names: List of sheet names (for Excel files)
      - field_separator: Field separator character (for delimited files)
      - quote_char: Quote character (for delimited files)
      - record_separator: Record separator (for delimited files)
  """
  serializer = GuessFileMetadataSerializer(data=request.query_params)

  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  metadata_params = serializer.validated_data

  try:
    metadata = operations.guess_file_metadata(data=metadata_params, username=request.user.username)
    return Response(metadata, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    # Handle other errors
    LOG.exception(f"Error guessing file metadata: {e}", exc_info=True)
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@parser_classes([JSONParser])
@api_error_handler
def preview_file(request: Request) -> Response:
  """Preview a file based on its path and import type.

  Args:
    request: Request object containing query parameters for file preview

  Returns:
    Response containing a dict preview of the file content, including:
      - type: Type of the file (e.g., csv, tsv, excel)
      - columns: List of column metadata
      - preview_data: Sample data from the file
  """
  serializer = PreviewFileSerializer(data=request.query_params)
  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  preview_params = serializer.validated_data

  try:
    preview = operations.preview_file(data=preview_params, username=request.user.username)
    return Response(preview, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    LOG.exception(f"Error previewing file: {e}", exc_info=True)
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@parser_classes([JSONParser])
@api_error_handler
def guess_file_header(request: Request) -> Response:
  """Guess whether a file has a header row.

  This API endpoint analyzes a file to determine if it contains a header row based on the
  content pattern. It works for both Excel files and delimited text files (CSV, TSV, etc.)

  Args:
    request: Request object containing query parameters:
      - file_path: Path to the file
      - file_type: Type of file ('excel', 'csv', 'tsv', 'delimiter_format')
      - import_type: 'local' or 'remote'
      - sheet_name: Sheet name for Excel files (required for Excel)

  Returns:
    Response containing:
      - has_header: Boolean indicating whether the file has a header row
  """
  serializer = GuessFileHeaderSerializer(data=request.query_params)

  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  header_params = serializer.validated_data

  try:
    has_header = operations.guess_file_header(data=header_params, username=request.user.username)
    return Response({"has_header": has_header}, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    # Handle other errors
    LOG.exception(f"Error detecting file header: {e}", exc_info=True)
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@parser_classes([JSONParser])
@api_error_handler
def get_sql_type_mapping(request: Request) -> Response:
  """Get SQL types supported by a specific dialect.

  This API endpoint returns a sorted list of unique SQL types that are supported
  by a specific SQL dialect.

  Args:
    request: Request object containing query parameters:
      - sql_dialect: The SQL dialect to get types for (e.g., 'hive', 'impala', 'trino')

  Returns:
    Response containing a list of SQL types:
      - A sorted list of unique SQL type names supported by the specified dialect
  """
  serializer = SqlTypeMapperSerializer(data=request.query_params)

  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  type_mapping_params = serializer.validated_data

  try:
    type_mapping = operations.get_sql_type_mapping(type_mapping_params)
    return Response(type_mapping, status=status.HTTP_200_OK)
  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    LOG.exception(f"Error getting SQL type mapping: {e}", exc_info=True)
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
