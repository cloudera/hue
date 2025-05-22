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
from desktop.lib.importer.serializers import GuessFileMetadataSerializer, LocalFileUploadSerializer, PreviewFileSerializer

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
  """

  serializer = LocalFileUploadSerializer(data=request.data)

  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  uploaded_file = serializer.validated_data['file']

  LOG.info(f'User {request.user.username} is uploading a local file: {uploaded_file.name}')
  res = operations.local_file_upload(uploaded_file, request.user.username)

  return Response(res, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@parser_classes([JSONParser])
@api_error_handler
def guess_file_metadata(request: Request) -> Response:
  """
  Guess the metadata of a file based on its content or extension.

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

  validated_data = serializer.validated_data
  file_path = validated_data['file_path']
  import_type = validated_data['import_type']

  try:
    metadata = operations.guess_file_metadata(
      file_path=file_path, import_type=import_type, fs=request.fs if import_type == 'remote' else None
    )

    return Response(metadata, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    # Handle other errors
    LOG.exception(f"Error guessing file metadata: {str(e)}")
    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@parser_classes([JSONParser])
@api_error_handler
def preview_file(request: Request) -> Response:
  """Preview a file based on its path and import type.

  Args:
    request: Request object containing query parameters for file preview

  Returns:
    Response containing a preview of the file content
  """
  serializer = PreviewFileSerializer(data=request.query_params)
  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  # Get validated data
  validated_data = serializer.validated_data
  file_path = validated_data['file_path']
  file_type = validated_data['file_type']
  import_type = validated_data['import_type']
  sql_dialect = validated_data['sql_dialect']
  has_header = validated_data.get('has_header')

  try:
    if file_type == 'excel':
      sheet_name = validated_data.get('sheet_name')

      result = operations.preview_file(
        file_path=file_path,
        file_type=file_type,
        import_type=import_type,
        sql_dialect=sql_dialect,
        has_header=has_header,
        sheet_name=sheet_name,
        fs=request.fs if import_type == 'remote' else None,
      )
    else:  # Delimited file types
      field_separator = validated_data.get('field_separator')
      quote_char = validated_data.get('quote_char')
      record_separator = validated_data.get('record_separator')

      result = operations.preview_file(
        file_path=file_path,
        file_type=file_type,
        import_type=import_type,
        sql_dialect=sql_dialect,
        has_header=has_header,
        field_separator=field_separator,
        quote_char=quote_char,
        record_separator=record_separator,
        fs=request.fs if import_type == 'remote' else None,
      )

    return Response(result, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    LOG.exception(f"Error previewing file: {str(e)}")
    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
