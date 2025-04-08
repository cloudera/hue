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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import polars as pl
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from desktop.lib.importer.serializers import LocalFileUploadSerializer

LOG = logging.getLogger()


# @dataclass
# class FileFormat:
#   """Data class representing file format configuration"""

#   type: str
#   has_header: bool
#   quote_char: str = '"'
#   record_separator: str = '\\n'
#   field_separator: str = ','


# class FormatDetector:
#   """Service class for detecting file formats"""

#   SAMPLE_SIZE = 16384  # 16KB for sampling
#   MIN_LINES = 5

#   def __init__(self, content: bytes, filename: str):
#     self.content = content
#     self.filename = filename
#     self._sample = self._get_sample()

#   def _get_sample(self) -> str:
#     """Get a sample of file content for format detection"""
#     try:
#       return self.content[: self.SAMPLE_SIZE].decode('utf-8')
#     except UnicodeDecodeError:
#       return self.content[: self.SAMPLE_SIZE].decode('latin-1')

#   def detect(self) -> FileFormat:
#     """Detect file format based on content and filename"""
#     if self._is_excel_file():
#       return self._get_excel_format()

#     return self._detect_delimited_format()

#   def _is_excel_file(self) -> bool:
#     """Check if file is Excel based on extension"""
#     return self.filename.lower().endswith(('.xlsx', '.xls'))

#   def _get_excel_format(self) -> FileFormat:
#     """Return Excel file format configuration"""
#     return FileFormat(type='excel', has_header=True)

#   def _detect_delimited_format(self) -> FileFormat:
#     """Detect format for delimited files like CSV"""
#     dialect = self._sniff_csv_dialect()

#     return FileFormat(
#       type='csv',
#       has_header=self._detect_header(),
#       quote_char=dialect.quotechar,
#       record_separator='\\n',  # Using standard newline
#       field_separator=dialect.delimiter,
#     )

#   def _sniff_csv_dialect(self) -> csv.Dialect:
#     """Detect CSV dialect using csv.Sniffer"""
#     try:
#       return csv.Sniffer().sniff(self._sample)
#     except csv.Error:
#       # Fallback to standard CSV format
#       return csv.excel

#   def _detect_header(self) -> bool:
#     """Detect if file has headers"""
#     try:
#       return csv.Sniffer().has_header(self._sample)
#     except csv.Error:
#       # Default to True if detection fails
#       return True


# @api_view(['POST'])
# @parser_classes([JSONParser, MultiPartParser])
# def detect_format(request: Request) -> Response:
#   """
#   Detects and returns the format configuration for input files/data sources.

#   Args:
#     request: REST framework Request object containing either:
#       - fileFormat: Dict with file details for HDFS files
#       - file: Uploaded file for local files

#   Returns:
#     Response with format configuration:
#       - type: Detected format type (csv, excel)
#       - hasHeader: Boolean indicating header presence
#       - fieldSeparator: Field delimiter for CSV
#       - recordSeparator: Record separator
#       - quoteChar: Quote character
#       - status: Operation status code

#   Raises:
#     400: Bad Request if file format/content cannot be processed
#   """
#   try:
#     if 'fileFormat' in request.data:
#       return _handle_hdfs_file(request)
#     elif 'file' in request.FILES:
#       return _handle_uploaded_file(request.FILES['file'])
#     else:
#       return Response({'error': 'No file or file format provided'}, status=status.HTTP_400_BAD_REQUEST)
#   except Exception as e:
#     return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# def _handle_uploaded_file(file) -> Response:
#   """Handle format detection for uploaded files"""
#   detector = FormatDetector(content=file.read(), filename=file.name)
#   file_format = detector.detect()

#   return Response(
#     {
#       'type': file_format.type,
#       'hasHeader': file_format.has_header,
#       'quoteChar': file_format.quote_char,
#       'recordSeparator': file_format.record_separator,
#       'fieldSeparator': file_format.field_separator,
#       'status': 0,
#     }
#   )


# def _handle_hdfs_file(request: Request) -> Response:
#   """Handle format detection for HDFS files"""
#   file_format = request.data.get('fileFormat', {})
#   path = file_format.get('path')

#   if not path:
#     return Response({'error': 'No path provided'}, status=status.HTTP_400_BAD_REQUEST)

#   if not request.fs.isfile(path):
#     return Response({'error': f'Path {path} is not a file'}, status=status.HTTP_400_BAD_REQUEST)

#   with request.fs.open(path) as stream:
#     detector = FormatDetector(content=stream.read(FormatDetector.SAMPLE_SIZE), filename=path)
#     file_format = detector.detect()

#   return Response(
#     {
#       'type': file_format.type,
#       'hasHeader': file_format.has_header,
#       'quoteChar': file_format.quote_char,
#       'recordSeparator': file_format.record_separator,
#       'fieldSeparator': file_format.field_separator,
#       'status': 0,
#     }
#   )

# TODO: Add api_error_handler decorator instead of method-wide try/except
@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_local_file(request: Request) -> Response:
  """
  Upload and process a CSV or Excel file, converting it to CSV format if needed.

  Returns the stored file path and metadata.
  """
  # Validate the request data using the serializer
  serializer = LocalFileUploadSerializer(data=request.data)

  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  try:
    upload_file = serializer.validated_data['file']
    file_extension = Path(upload_file.name).suffix.lower()[1:]

    # Generate a unique filename
    username = request.user.username
    safe_original_name = re.sub(r'[^0-9a-zA-Z]+', '_', upload_file.name)
    unique_id = uuid.uuid4().hex[:8]

    filename = f"{username}_{unique_id}_{safe_original_name}"

    # Process the file based on its type
    result = process_uploaded_file(upload_file, filename, file_extension)

    return Response(result, status=status.HTTP_201_CREATED)

  except Exception as e:
    return Response({"error": f"Error processing file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def process_uploaded_file(upload_file, filename: str, file_extension: str) -> Dict[str, Any]:
  """
  Process the uploaded file and convert to CSV if needed.

  Args:
    upload_file: The uploaded file object
    filename: The base filename to use
    file_extension: The file extension (csv, xlsx, xls)

  Returns:
    Dict containing file metadata
  """
  # TODO: Check if actually needed?
  file_type = 'csv' if file_extension == 'csv' else 'excel'

  # Create a temporary file with our generated filename
  temp_dir = tempfile.gettempdir()
  output_path = os.path.join(temp_dir, f"{filename}.csv")

  try:
    if file_extension == 'csv':
      df = pl.read_csv(upload_file.read())
    else:
      # For Excel files, use Polars and its default Calamine engine to read and convert to CSV.
      # TODO: Currently reads the first sheet. Check if we need to support multiple sheets or specific sheets as input.
      df = pl.read_excel(upload_file.read())

    df.write_csv(output_path)

    # Return metadata about the processed file
    file_stats = os.stat(output_path)

    # TODO: Verify response fields
    return {
      'filename': os.path.basename(output_path),
      'file_path': output_path,
      'row_count': len(df),
      'column_count': len(df.columns),
      'file_size_bytes': file_stats.st_size,
      # 'file_type': file_type,
    }

  except Exception as e:
    # Clean up the file if there was an error
    if os.path.exists(output_path):
      os.remove(output_path)
    raise e
