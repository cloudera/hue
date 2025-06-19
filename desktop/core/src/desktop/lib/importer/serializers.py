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

from rest_framework import serializers

from desktop.conf import IMPORTER


class LocalFileUploadSerializer(serializers.Serializer):
  """Serializer for file upload validation.

  This serializer validates that the uploaded file is present and has an
  acceptable file format and size.

  Attributes:
    file: File field that must be included in the request
  """

  file = serializers.FileField(required=True, help_text="CSV or Excel file to upload and process")

  def validate_file(self, value):
    # Check if the file type is restricted
    _, file_type = os.path.splitext(value.name)
    restricted_extensions = IMPORTER.RESTRICT_LOCAL_FILE_EXTENSIONS.get()
    if restricted_extensions and file_type.lower() in [ext.lower() for ext in restricted_extensions]:
      raise serializers.ValidationError(f'Uploading files with type "{file_type}" is not allowed. Hue is configured to restrict this type.')

    # Check file size
    max_size = IMPORTER.MAX_LOCAL_FILE_SIZE_UPLOAD_LIMIT.get()
    if value.size > max_size:
      max_size_mib = max_size / (1024 * 1024)
      raise serializers.ValidationError(f"File too large. Maximum file size is {max_size_mib:.0f} MiB.")

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
    choices=["local", "remote"], required=True, help_text="Whether the file is local or on a remote filesystem"
  )


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

  # Excel-specific fields
  sheet_name = serializers.CharField(required=False, help_text="Sheet name for Excel files")

  # Delimited file-specific fields
  field_separator = serializers.CharField(required=False, help_text="Field separator character")
  quote_char = serializers.CharField(required=False, help_text="Quote character")
  record_separator = serializers.CharField(required=False, help_text="Record separator character")

  def validate(self, data):
    """Validate the complete data set with interdependent field validation."""

    if data.get("file_type") == "excel" and not data.get("sheet_name"):
      raise serializers.ValidationError({"sheet_name": "Sheet name is required for Excel files."})

    if data.get("file_type") in ["csv", "tsv", "delimiter_format"]:
      if not data.get("field_separator"):
        # If not provided, set default value based on file type
        if data.get("file_type") == "csv":
          data["field_separator"] = ","
        elif data.get("file_type") == "tsv":
          data["field_separator"] = "\t"
        else:
          raise serializers.ValidationError({"field_separator": "Field separator is required for delimited files"})

      if not data.get("quote_char"):
        data["quote_char"] = '"'  # Default quote character

      if not data.get("record_separator"):
        data["record_separator"] = "\n"  # Default record separator

    return data


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

  # Excel-specific fields
  sheet_name = serializers.CharField(required=False, help_text="Sheet name for Excel files")

  def validate(self, data):
    """Validate the complete data set with interdependent field validation."""

    if data.get("file_type") == "excel" and not data.get("sheet_name"):
      raise serializers.ValidationError({"sheet_name": "Sheet name is required for Excel files."})

    return data


class CreateTableSerializer(serializers.Serializer):
  """Serializer for table creation request validation.

  This serializer validates the parameters required for creating a SQL table from a file.

  Attributes:
    file_path: Path to the source file to import data from
    file_type: Type of file format (csv, tsv, excel, delimiter_format)
    import_type: Type of import (local or remote)
    sql_dialect: Target SQL dialect for table creation
    database_name: The database name in which to create the table
    table_name: The name of the table to create
    has_header: Whether the file has a header row
    columns: List of column definitions (each with name, type, etc.)
    partition_columns: List of partition column definitions (optional)
    external: Whether to create an external table (optional)
    external_path: External table location path (optional, required if external=True)
    table_format: Table storage format (text, parquet, orc, avro, kudu, iceberg) (optional)
    field_separator: Field separator character (required for delimited files)
    quote_char: Quote character (required for delimited files)
    record_separator: Record separator character (required for delimited files)
    sheet_name: Sheet name for Excel files (required when file_type is excel)
    comment: Table comment (optional)
    is_transactional: Whether to create a transactional table (optional, Hive only)
    is_iceberg: Whether to create an Iceberg table (optional)
    is_insert_only: Whether the transactional table is insert-only (optional)
    primary_keys: List of primary key column names (optional, required for Kudu tables)
  """

  # Source file information
  file_path = serializers.CharField(required=True, help_text="Path to the file to import data from")
  file_type = serializers.ChoiceField(
    choices=["csv", "tsv", "excel", "delimiter_format"], required=True, help_text="Type of file (csv, tsv, excel, delimiter_format)"
  )
  import_type = serializers.ChoiceField(
    choices=["local", "remote"], required=True, help_text="Whether the file is local or on a remote filesystem"
  )

  # Target table information
  sql_dialect = serializers.ChoiceField(
    choices=["hive", "impala", "trino", "phoenix", "sparksql"], required=True, help_text="SQL dialect for creating the table"
  )
  database_name = serializers.CharField(required=True, help_text="Database name where the table will be created")
  table_name = serializers.CharField(required=True, help_text="Name of the table to create")

  # Data format information
  has_header = serializers.BooleanField(default=False, help_text="Whether the file has a header row")

  # Column definitions
  columns = serializers.ListField(
    child=serializers.DictField(), required=True, help_text="List of column definitions with name, type, etc."
  )

  # Optional parameters
  partition_columns = serializers.ListField(
    child=serializers.DictField(), required=False, default=[], help_text="List of partition column definitions"
  )
  comment = serializers.CharField(required=False, allow_blank=True, default="", help_text="Table comment")

  # Table storage options
  external = serializers.BooleanField(default=False, help_text="Whether to create an external table")
  external_path = serializers.CharField(required=False, allow_blank=True, help_text="Location path for external tables")
  table_format = serializers.ChoiceField(
    choices=["text", "parquet", "orc", "avro", "kudu", "iceberg"], default="text", help_text="Storage format for the table"
  )

  # Hive/Impala specific options
  is_transactional = serializers.BooleanField(default=False, help_text="Whether to create a transactional table (Hive)")
  is_insert_only = serializers.BooleanField(default=False, help_text="Whether the transactional table is insert-only")
  is_iceberg = serializers.BooleanField(default=False, help_text="Whether to create an Iceberg table")

  # Kudu specific options
  primary_keys = serializers.ListField(
    child=serializers.CharField(), required=False, default=[], help_text="List of primary key column names (required for Kudu tables)"
  )

  # Excel-specific fields
  sheet_name = serializers.CharField(required=False, help_text="Sheet name for Excel files")

  # Delimited file-specific fields
  field_separator = serializers.CharField(required=False, help_text="Field separator character")
  quote_char = serializers.CharField(required=False, help_text="Quote character")
  record_separator = serializers.CharField(required=False, help_text="Record separator character")

  # Additional options
  load_data = serializers.BooleanField(default=True, help_text="Whether to load data from the file into the table")

  def validate(self, data):
    """Validate the complete data set with interdependent field validation."""

    # Validate Excel-specific parameters
    if data.get("file_type") == "excel" and not data.get("sheet_name"):
      raise serializers.ValidationError({"sheet_name": "Sheet name is required for Excel files."})

    # Validate delimited file-specific parameters
    if data.get("file_type") in ["csv", "tsv", "delimiter_format"]:
      if not data.get("field_separator"):
        # If not provided, set default value based on file type
        if data.get("file_type") == "csv":
          data["field_separator"] = ","
        elif data.get("file_type") == "tsv":
          data["field_separator"] = "\t"
        else:
          raise serializers.ValidationError({"field_separator": "Field separator is required for delimited files"})

      if not data.get("quote_char"):
        data["quote_char"] = '"'  # Default quote character

      if not data.get("record_separator"):
        data["record_separator"] = "\n"  # Default record separator

    # Validate external table parameters
    if data.get("external") and not data.get("external_path"):
      raise serializers.ValidationError({"external_path": "External path is required for external tables."})

    # Validate Kudu table parameters
    if data.get("table_format") == "kudu" and not data.get("primary_keys"):
      raise serializers.ValidationError({"primary_keys": "Primary keys are required for Kudu tables."})

    # Validate transaction table parameters
    if data.get("is_transactional") and data.get("sql_dialect") not in ["hive", "impala"]:
      raise serializers.ValidationError({"is_transactional": "Transactional tables are only supported in Hive and Impala."})

    # Validate Iceberg table parameters
    if data.get("is_iceberg") and data.get("sql_dialect") not in ["hive", "impala", "sparksql"]:
      raise serializers.ValidationError({"is_iceberg": "Iceberg tables are only supported in Hive, Impala, and SparkSQL."})

    return data
