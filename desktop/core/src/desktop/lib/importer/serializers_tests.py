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


from django.core.files.uploadedfile import SimpleUploadedFile

from desktop.conf import IMPORTER
from desktop.lib.importer.serializers import (
  GuessFileHeaderSerializer,
  GuessFileMetadataSerializer,
  LocalFileUploadSerializer,
  PreviewFileSerializer,
  SqlTypeMapperSerializer,
)


class TestLocalFileUploadSerializer:
  def test_valid_file(self):
    resets = [
      IMPORTER.RESTRICT_LOCAL_FILE_EXTENSIONS.set_for_testing([]),
      IMPORTER.MAX_LOCAL_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(10 * 1024 * 1024),  # 10 MiB limit
    ]
    try:
      test_file = SimpleUploadedFile(name="test_file.csv", content=b"header1,header2\nvalue1,value2", content_type="text/csv")

      serializer = LocalFileUploadSerializer(data={"file": test_file})

      assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
      assert serializer.validated_data["file"] == test_file
    finally:
      for reset in resets:
        reset()

  def test_restricted_file_extension(self):
    resets = [
      IMPORTER.RESTRICT_LOCAL_FILE_EXTENSIONS.set_for_testing([".sh", ".csv", ".exe"]),
      IMPORTER.MAX_LOCAL_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(10 * 1024 * 1024),  # 10 MiB limit
    ]
    try:
      test_file = SimpleUploadedFile(
        name="test_file.exe", content=b"This is not a real executable", content_type="application/octet-stream"
      )

      serializer = LocalFileUploadSerializer(data={"file": test_file})

      assert not serializer.is_valid()
      assert "file" in serializer.errors
      assert serializer.errors["file"][0] == 'Uploading files with type ".exe" is not allowed. Hue is configured to restrict this type.'
    finally:
      for reset in resets:
        reset()

  def test_file_size_too_large(self):
    resets = [
      IMPORTER.RESTRICT_LOCAL_FILE_EXTENSIONS.set_for_testing([]),
      IMPORTER.MAX_LOCAL_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(10),  # Just 10 bytes
    ]
    try:
      test_file = SimpleUploadedFile(
        name="test_file.csv", content=b"This content is more than 10 bytes which exceeds our mock size limit", content_type="text/csv"
      )

      serializer = LocalFileUploadSerializer(data={"file": test_file})

      assert not serializer.is_valid()
      assert "file" in serializer.errors
      assert serializer.errors["file"][0] == "File too large. Maximum file size is 0 MiB."  # 10 bytes is very less than 1 MiB
    finally:
      for reset in resets:
        reset()

  def test_missing_file(self):
    serializer = LocalFileUploadSerializer(data={})

    assert not serializer.is_valid()
    assert "file" in serializer.errors
    assert serializer.errors["file"][0] == "No file was submitted."


class TestGuessFileMetadataSerializer:
  def test_valid_data(self):
    # Test with local import type
    local_valid_data = {"file_path": "/path/to/file.csv", "import_type": "local"}

    serializer = GuessFileMetadataSerializer(data=local_valid_data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data == local_valid_data

    # Test with remote import type
    remote_valid_data = {"file_path": "s3a://bucket/user/test_user/file.csv", "import_type": "remote"}

    serializer = GuessFileMetadataSerializer(data=remote_valid_data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data == remote_valid_data

  def test_missing_required_fields(self):
    # Test missing file_path
    invalid_data = {"import_type": "local"}

    serializer = GuessFileMetadataSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert "file_path" in serializer.errors

    # Test missing import_type
    invalid_data = {"file_path": "/path/to/file.csv"}

    serializer = GuessFileMetadataSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert "import_type" in serializer.errors

  def test_invalid_import_type(self):
    invalid_data = {
      "file_path": "/path/to/file.csv",
      "import_type": "invalid_type",  # Not one of 'local' or 'remote'
    }

    serializer = GuessFileMetadataSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert "import_type" in serializer.errors
    assert serializer.errors["import_type"][0] == '"invalid_type" is not a valid choice.'


class TestPreviewFileSerializer:
  def test_valid_csv_data(self):
    valid_data = {
      "file_path": "/path/to/file.csv",
      "file_type": "csv",
      "import_type": "local",
      "sql_dialect": "hive",
      "has_header": True,
      "field_separator": ",",
    }

    serializer = PreviewFileSerializer(data=valid_data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    # Check that default values are set for quote_char and record_separator
    assert serializer.validated_data["quote_char"] == '"'
    assert serializer.validated_data["record_separator"] == "\n"

  def test_valid_excel_data(self):
    valid_data = {
      "file_path": "/path/to/file.xlsx",
      "file_type": "excel",
      "import_type": "local",
      "sql_dialect": "hive",
      "has_header": True,
      "sheet_name": "Sheet1",
    }

    serializer = PreviewFileSerializer(data=valid_data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"

  def test_missing_required_fields(self):
    # Test with minimal data
    invalid_data = {
      "file_path": "/path/to/file.csv",
    }

    serializer = PreviewFileSerializer(data=invalid_data)

    assert not serializer.is_valid()
    # Check that all required fields are reported as missing
    for field in ["file_type", "import_type", "sql_dialect", "has_header"]:
      assert field in serializer.errors

  def test_invalid_file_type(self):
    invalid_data = {
      "file_path": "/path/to/file.json",
      "file_type": "json",  # Not a valid choice
      "import_type": "local",
      "sql_dialect": "hive",
      "has_header": True,
    }

    serializer = PreviewFileSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert "file_type" in serializer.errors
    assert serializer.errors["file_type"][0] == '"json" is not a valid choice.'

  def test_excel_without_sheet_name(self):
    invalid_data = {
      "file_path": "/path/to/file.xlsx",
      "file_type": "excel",
      "import_type": "local",
      "sql_dialect": "hive",
      "has_header": True,
      # Missing sheet_name
    }

    serializer = PreviewFileSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert "sheet_name" in serializer.errors
    assert serializer.errors["sheet_name"][0] == "Sheet name is required for Excel files."

  def test_delimited_without_field_separator(self):
    # For delimiter_format type (not csv/tsv) field separator is required
    invalid_data = {
      "file_path": "/path/to/file.txt",
      "file_type": "delimiter_format",
      "import_type": "local",
      "sql_dialect": "hive",
      "has_header": True,
      # Missing field_separator
    }

    serializer = PreviewFileSerializer(data=invalid_data)
    assert not serializer.is_valid()
    assert "field_separator" in serializer.errors

  def test_default_separators_by_file_type(self):
    # For CSV, field_separator should default to ','
    csv_data = {"file_path": "/path/to/file.csv", "file_type": "csv", "import_type": "local", "sql_dialect": "hive", "has_header": True}

    serializer = PreviewFileSerializer(data=csv_data)

    assert serializer.is_valid(), f"CSV serializer validation failed: {serializer.errors}"
    assert serializer.validated_data["field_separator"] == ","

    # For TSV, field_separator should default to '\t'
    tsv_data = {"file_path": "/path/to/file.tsv", "file_type": "tsv", "import_type": "local", "sql_dialect": "hive", "has_header": True}

    serializer = PreviewFileSerializer(data=tsv_data)

    assert serializer.is_valid(), f"TSV serializer validation failed: {serializer.errors}"
    assert serializer.validated_data["field_separator"] == "\t"


class TestSqlTypeMapperSerializer:
  def test_valid_sql_dialect(self):
    for dialect in ["hive", "impala", "trino", "phoenix", "sparksql"]:
      valid_data = {"sql_dialect": dialect}

      serializer = SqlTypeMapperSerializer(data=valid_data)

      assert serializer.is_valid(), f"Failed for dialect '{dialect}': {serializer.errors}"
      assert serializer.validated_data["sql_dialect"] == dialect

  def test_invalid_sql_dialect(self):
    invalid_data = {"sql_dialect": "invalid_dialect"}

    serializer = SqlTypeMapperSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert "sql_dialect" in serializer.errors
    assert serializer.errors["sql_dialect"][0] == '"invalid_dialect" is not a valid choice.'

  def test_missing_sql_dialect(self):
    invalid_data = {}  # Empty data

    serializer = SqlTypeMapperSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert "sql_dialect" in serializer.errors
    assert serializer.errors["sql_dialect"][0] == "This field is required."


class TestGuessFileHeaderSerializer:
  def test_valid_data_csv(self):
    valid_data = {"file_path": "/path/to/file.csv", "file_type": "csv", "import_type": "local"}

    serializer = GuessFileHeaderSerializer(data=valid_data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data == valid_data

  def test_valid_data_excel(self):
    valid_data = {"file_path": "/path/to/file.xlsx", "file_type": "excel", "import_type": "local", "sheet_name": "Sheet1"}

    serializer = GuessFileHeaderSerializer(data=valid_data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data == valid_data

  def test_missing_required_fields(self):
    # Missing file_path
    invalid_data = {"file_type": "csv", "import_type": "local"}

    serializer = GuessFileHeaderSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert "file_path" in serializer.errors

    # Missing file_type
    invalid_data = {"file_path": "/path/to/file.csv", "import_type": "local"}

    serializer = GuessFileHeaderSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert "file_type" in serializer.errors

    # Missing import_type
    invalid_data = {"file_path": "/path/to/file.csv", "file_type": "csv"}

    serializer = GuessFileHeaderSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert "import_type" in serializer.errors

  def test_excel_without_sheet_name(self):
    invalid_data = {
      "file_path": "/path/to/file.xlsx",
      "file_type": "excel",
      "import_type": "local",
      # Missing sheet_name
    }

    serializer = GuessFileHeaderSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert "sheet_name" in serializer.errors
    assert serializer.errors["sheet_name"][0] == "Sheet name is required for Excel files."

  def test_non_excel_with_sheet_name(self):
    # This should pass, as sheet_name is optional for non-Excel files
    valid_data = {
      "file_path": "/path/to/file.csv",
      "file_type": "csv",
      "import_type": "local",
      "sheet_name": "Sheet1",  # Unnecessary but not invalid
    }

    serializer = GuessFileHeaderSerializer(data=valid_data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"

  def test_invalid_file_type(self):
    invalid_data = {
      "file_path": "/path/to/file.json",
      "file_type": "json",  # Not a valid choice
      "import_type": "local",
    }

    serializer = GuessFileHeaderSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert "file_type" in serializer.errors
    assert serializer.errors["file_type"][0] == '"json" is not a valid choice.'

  def test_invalid_import_type(self):
    invalid_data = {
      "file_path": "/path/to/file.csv",
      "file_type": "csv",
      "import_type": "invalid_type",  # Not a valid choice
    }

    serializer = GuessFileHeaderSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert "import_type" in serializer.errors
    assert serializer.errors["import_type"][0] == '"invalid_type" is not a valid choice.'
