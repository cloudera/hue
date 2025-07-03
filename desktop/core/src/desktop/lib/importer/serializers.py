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

from pydantic import ValidationError
from rest_framework import serializers

from desktop.lib.importer.schemas import (
  GuessFileHeaderSchema,
  GuessFileMetadataSchema,
  LocalFileUploadSchema,
  PreviewFileSchema,
  SqlTypeMapperSchema,
)


class LocalFileUploadSerializer(serializers.Serializer):
  """Serializer for file upload validation.

  This serializer validates that the uploaded file is present and has an
  acceptable file format and size.

  Attributes:
    file: File field that must be included in the request
  """

  file = serializers.FileField(required=True, help_text="CSV or Excel file to upload and process")

  def validate(self, data):
    uploaded_file = data["file"]
    schema_data = {"file": uploaded_file, "filename": uploaded_file.name, "filesize": uploaded_file.size}
    try:
      # The serializer now directly returns the validated Pydantic model instance.
      return LocalFileUploadSchema.model_validate(schema_data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())


class GuessFileMetadataSerializer(serializers.Serializer):
  """Serializer for file metadata guessing request validation.

  This serializer validates the parameters required for guessing metadata from a file.

  Attributes:
    file_path: Path to the file
    import_type: Type of import (local or remote)
  """

  file_path = serializers.CharField(required=True, help_text="Full path to the file to analyze")
  import_type = serializers.ChoiceField(
    choices=["local", "remote"], required=True, help_text="Whether the file is local or on a remote filesystem"
  )

  def validate(self, data):
    try:
      return GuessFileMetadataSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())


class PreviewFileSerializer(serializers.Serializer):
  """Serializer for file preview request validation.

  This serializer validates the parameters required for previewing file content.

  Attributes:
    file_path: Path to the file to preview
    file_type: Type of file format (csv, tsv, excel, delimiter_format)
    import_type: Type of import (local or remote)
    sql_dialect: Target SQL dialect for type mapping
    has_header: Whether the file has a header row or not
    sheet_name: Sheet name for Excel files (required when file_type is excel)
    field_separator: Field separator character (required for delimited files)
    quote_char: Quote character (required for delimited files)
    record_separator: Record separator character (required for delimited files)
  """

  file_path = serializers.CharField(required=True, help_text="Full path to the file to preview")
  file_type = serializers.ChoiceField(
    choices=["csv", "tsv", "excel", "delimiter_format"], required=True, help_text="Type of file (csv, tsv, excel, delimiter_format)"
  )
  import_type = serializers.ChoiceField(
    choices=["local", "remote"], required=True, help_text="Whether the file is local or on a remote filesystem"
  )
  sql_dialect = serializers.ChoiceField(
    choices=["hive", "impala", "trino", "phoenix", "sparksql"], required=True, help_text="SQL dialect for mapping column types"
  )
  has_header = serializers.BooleanField(required=True, help_text="Whether the file has a header row or not")
  sheet_name = serializers.CharField(required=False, help_text="Sheet name for Excel files")
  field_separator = serializers.CharField(required=False, allow_null=True, help_text="Field separator character")
  quote_char = serializers.CharField(required=False, allow_null=True, help_text="Quote character")
  record_separator = serializers.CharField(required=False, allow_null=True, help_text="Record separator character")

  def validate(self, data):
    try:
      # Pydantic will handle interdependent validation
      return PreviewFileSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())


class SqlTypeMapperSerializer(serializers.Serializer):
  """Serializer for SQL type mapping requests.

  This serializer validates the parameters required for retrieving type mapping information
  from Polars data types to SQL types for a specific dialect.

  Attributes:
    sql_dialect: Target SQL dialect for type mapping
  """

  sql_dialect = serializers.ChoiceField(
    choices=["hive", "impala", "trino", "phoenix", "sparksql"], required=True, help_text="SQL dialect for mapping column types"
  )

  def validate(self, data):
    try:
      return SqlTypeMapperSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())


class GuessFileHeaderSerializer(serializers.Serializer):
  """Serializer for file header guessing request validation.

  This serializer validates the parameters required for guessing if a file has a header row.

  Attributes:
    file_path: Path to the file to analyze
    file_type: Type of file format (csv, tsv, excel, delimiter_format)
    import_type: Type of import (local or remote)
    sheet_name: Sheet name for Excel files (required when file_type is excel)
  """

  file_path = serializers.CharField(required=True, help_text="Full path to the file to analyze")
  file_type = serializers.ChoiceField(
    choices=["csv", "tsv", "excel", "delimiter_format"], required=True, help_text="Type of file (csv, tsv, excel, delimiter_format)"
  )
  import_type = serializers.ChoiceField(
    choices=["local", "remote"], required=True, help_text="Whether the file is local or on a remote filesystem"
  )
  sheet_name = serializers.CharField(required=False, help_text="Sheet name for Excel files")

  def validate(self, data):
    try:
      # Pydantic will handle interdependent validation
      return GuessFileHeaderSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
