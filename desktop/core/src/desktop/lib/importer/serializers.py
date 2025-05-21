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
from rest_framework import serializers


class LocalFileUploadSerializer(serializers.Serializer):
  """Serializer for file upload validation.

  This serializer validates that the uploaded file is present and has an
  acceptable file format and size.

  Attributes:
    file: File field that must be included in the request
  """

  file = serializers.FileField(required=True, help_text="CSV or Excel file to upload and process")

  def validate_file(self, value):
    # TODO: Check upper limit for file size
    # Add file size validation (e.g., limit to 150 MiB)
    if value.size > 150 * 1024 * 1024:
      raise serializers.ValidationError("File too large. Maximum file size is 150 MiB.")

    return value


class GuessFileMetadataSerializer(serializers.Serializer):
  """Serializer for file metadata guessing request validation.

  This serializer validates the parameters required for guessing metadata from a file.

  Attributes:
    file_path: Path to the file
    import_type: Type of import (local or remote)
  """

  file_path = serializers.CharField(required=True, help_text="Full path to the file to analyze")
  import_type = serializers.ChoiceField(
    choices=['local', 'remote'], required=True, help_text="Whether the file is local or on a remote filesystem"
  )

  def validate(self, data):
    """Validate the complete data set."""
    # We can't check if the file exists here as we need the request object
    # This will be done in the view function
    return data


class PreviewFileSerializer(serializers.Serializer):
  """Serializer for file preview request validation.

  This serializer validates the parameters required for previewing file content.

  Attributes:
    file_path: Path to the file to preview
    file_type: Type of file format (csv, tsv, excel, delimiter_format)
    import_type: Type of import (local or remote)
    sql_dialect: Target SQL dialect for type mapping
    has_header: Whether the file has a header row (optional)
    sheet_name: Sheet name for Excel files (required when file_type is excel)
    field_separator: Field separator character (required for delimited files)
    quote_char: Quote character (required for delimited files)
    record_separator: Record separator character (required for delimited files)
  """

  file_path = serializers.CharField(required=True, help_text="Full path to the file to preview")
  file_type = serializers.ChoiceField(
    choices=['csv', 'tsv', 'excel', 'delimiter_format'], required=True, help_text="Type of file (csv, tsv, excel, delimiter_format)"
  )
  import_type = serializers.ChoiceField(
    choices=['local', 'remote'], required=True, help_text="Whether the file is local or on a remote filesystem"
  )
  sql_dialect = serializers.ChoiceField(
    choices=['hive', 'impala', 'trino', 'phoenix', 'sparksql'], required=True, help_text="SQL dialect for mapping column types"
  )
  # Default value for has_header is None, which means it needs to be set to True or False explicitly.
  # This allows the user to specify if the file has a header row or not.
  # If the value is not set, then we assume to auto-detect the header from file content.
  has_header = serializers.BooleanField(required=False, allow_null=True, default=None, help_text="Whether the file has a header row")

  # Excel-specific fields
  sheet_name = serializers.CharField(required=False, help_text="Sheet name for Excel files")

  # Delimited file-specific fields
  field_separator = serializers.CharField(required=False, help_text="Field separator character")
  quote_char = serializers.CharField(required=False, help_text="Quote character")
  record_separator = serializers.CharField(required=False, help_text="Record separator character")

  def validate(self, data):
    """Validate the complete data set with interdependent field validation."""
    if data.get('file_type') == 'excel' and not data.get('sheet_name'):
      raise serializers.ValidationError({"sheet_name": "Sheet name is required for Excel files"})

    if data.get('file_type') in ['csv', 'tsv', 'delimiter_format']:
      if not data.get('field_separator'):
        # If not provided, set default value based on file type
        if data.get('file_type') == 'csv':
          data['field_separator'] = ','
        elif data.get('file_type') == 'tsv':
          data['field_separator'] = '\t'
        else:
          raise serializers.ValidationError({"field_separator": "Field separator is required for delimited files"})

      if not data.get('quote_char'):
        data['quote_char'] = '"'  # Default quote character

      if not data.get('record_separator'):
        data['record_separator'] = '\n'  # Default record separator

    return data
