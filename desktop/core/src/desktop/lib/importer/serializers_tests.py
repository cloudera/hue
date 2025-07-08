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
from desktop.lib.importer.schemas import (
  GuessFileHeaderSchema,
  GuessFileMetadataSchema,
  LocalFileUploadSchema,
  PreviewFileSchema,
  SqlTypeMapperSchema,
)
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
      # validated_data now returns a schema object
      assert isinstance(serializer.validated_data, LocalFileUploadSchema)
      assert serializer.validated_data.file == test_file
      assert serializer.validated_data.filename == "test_file.csv"
      assert serializer.validated_data.filesize == test_file.size
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
      assert len(serializer.errors) > 0
      # The error structure might be different with Pydantic validation
      error_messages = str(serializer.errors)
      assert "not allowed" in error_messages or "restrict" in error_messages.lower()
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
      assert len(serializer.errors) > 0
      # Check for file size error
      error_messages = str(serializer.errors)
      assert "too large" in error_messages.lower() or "maximum" in error_messages.lower()
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
    # Scenario 1: Test with local import type
    local_valid_data = {"file_path": "/path/to/file.csv", "import_type": "local"}

    serializer = GuessFileMetadataSerializer(data=local_valid_data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert isinstance(serializer.validated_data, GuessFileMetadataSchema)
    assert serializer.validated_data.file_path == "/path/to/file.csv"
    assert serializer.validated_data.import_type == "local"

    # Scenario 2: Test with remote import type
    remote_valid_data = {"file_path": "s3a://bucket/user/test_user/file.csv", "import_type": "remote"}

    serializer = GuessFileMetadataSerializer(data=remote_valid_data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert isinstance(serializer.validated_data, GuessFileMetadataSchema)
    assert serializer.validated_data.file_path == "s3a://bucket/user/test_user/file.csv"
    assert serializer.validated_data.import_type == "remote"

  def test_missing_required_fields(self):
    # Scenario 1: Test missing file_path
    invalid_data = {"import_type": "local"}

    serializer = GuessFileMetadataSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert len(serializer.errors) > 0
    # Check for file_path error in serializer errors
    error_messages = str(serializer.errors)
    assert "file_path" in error_messages

    # Scenario 2: Test missing import_type
    invalid_data = {"file_path": "/path/to/file.csv"}

    serializer = GuessFileMetadataSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert len(serializer.errors) > 0
    # Check for import_type error in serializer errors
    error_messages = str(serializer.errors)
    assert "import_type" in error_messages

  def test_invalid_import_type(self):
    invalid_data = {
      "file_path": "/path/to/file.csv",
      "import_type": "invalid_type",  # Not one of 'local' or 'remote' (invalid_type)
    }

    serializer = GuessFileMetadataSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert len(serializer.errors) > 0
    error_messages = str(serializer.errors)
    assert "import_type" in error_messages


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
    # validated_data now returns a schema object
    assert isinstance(serializer.validated_data, PreviewFileSchema)
    assert serializer.validated_data.file_path == "/path/to/file.csv"
    assert serializer.validated_data.file_type == "csv"
    # Check that default values are set for quote_char and record_separator
    assert serializer.validated_data.quote_char == '"'
    assert serializer.validated_data.record_separator == "\n"

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
    assert isinstance(serializer.validated_data, PreviewFileSchema)
    assert serializer.validated_data.file_type == "excel"
    assert serializer.validated_data.sheet_name == "Sheet1"

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
    assert len(serializer.errors) > 0
    error_messages = str(serializer.errors)
    assert "file_type" in error_messages

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
    assert len(serializer.errors) > 0
    error_messages = str(serializer.errors)
    assert "Sheet name is required for Excel files" in error_messages

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
    assert len(serializer.errors) > 0
    error_messages = str(serializer.errors)
    assert "Field separator is required for delimited files" in error_messages

  def test_default_separators_by_file_type(self):
    # For CSV, field_separator should default to ','
    csv_data = {"file_path": "/path/to/file.csv", "file_type": "csv", "import_type": "local", "sql_dialect": "hive", "has_header": True}

    serializer = PreviewFileSerializer(data=csv_data)

    assert serializer.is_valid(), f"CSV serializer validation failed: {serializer.errors}"
    assert isinstance(serializer.validated_data, PreviewFileSchema)
    assert serializer.validated_data.field_separator == ","

    # For TSV, field_separator should default to '\t'
    tsv_data = {"file_path": "/path/to/file.tsv", "file_type": "tsv", "import_type": "local", "sql_dialect": "hive", "has_header": True}

    serializer = PreviewFileSerializer(data=tsv_data)

    assert serializer.is_valid(), f"TSV serializer validation failed: {serializer.errors}"
    assert isinstance(serializer.validated_data, PreviewFileSchema)
    assert serializer.validated_data.field_separator == "\t"

  def test_decode_escape_sequences_field_separator(self):
    # Test tab escape sequence
    data = {
      "file_path": "/path/to/file.csv",
      "file_type": "delimiter_format",
      "import_type": "local",
      "sql_dialect": "hive",
      "has_header": True,
      "field_separator": "\\t",  # Tab character as escape sequence
    }

    serializer = PreviewFileSerializer(data=data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data.field_separator == "\t"  # Should be decoded to actual tab

    # Test newline escape sequence
    data["field_separator"] = "\\n"
    serializer = PreviewFileSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data.field_separator == "\n"

    # Test backslash escape sequence
    data["field_separator"] = "\\\\"
    serializer = PreviewFileSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data.field_separator == "\\"

  def test_decode_escape_sequences_quote_char(self):
    # Test double quote escape sequence
    data = {
      "file_path": "/path/to/file.csv",
      "file_type": "csv",
      "import_type": "local",
      "sql_dialect": "hive",
      "has_header": True,
      "quote_char": '\\"',  # Escaped double quote
    }

    serializer = PreviewFileSerializer(data=data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data.quote_char == '"'

    # Test single quote escape sequence
    data["quote_char"] = "\\'"
    serializer = PreviewFileSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data.quote_char == "'"

    # Test Unicode escape sequence
    data["quote_char"] = "\\u0022"  # Unicode for double quote
    serializer = PreviewFileSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data.quote_char == '"'

  def test_decode_escape_sequences_record_separator(self):
    # Test newline escape sequence
    data = {
      "file_path": "/path/to/file.csv",
      "file_type": "csv",
      "import_type": "local",
      "sql_dialect": "hive",
      "has_header": True,
      "record_separator": "\\n",
    }

    serializer = PreviewFileSerializer(data=data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data.record_separator == "\n"

    # Test carriage return + newline (should be normalized to just newline)
    data["record_separator"] = "\\r\\n"
    serializer = PreviewFileSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data.record_separator == "\n"  # Should be normalized

    # Test just carriage return
    data["record_separator"] = "\\r"
    serializer = PreviewFileSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data.record_separator == "\r"

  def test_decode_escape_sequences_with_none_values(self):
    # Test that None values remain None
    data = {
      "file_path": "/path/to/file.csv",
      "file_type": "csv",
      "import_type": "local",
      "sql_dialect": "hive",
      "has_header": True,
      "field_separator": None,
      "quote_char": None,
      "record_separator": None,
    }

    serializer = PreviewFileSerializer(data=data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    # CSV defaults should be applied after None is processed
    assert serializer.validated_data.field_separator == ","
    assert serializer.validated_data.quote_char == '"'
    assert serializer.validated_data.record_separator == "\n"

  def test_decode_escape_sequences_with_complex_patterns(self):
    # Test multiple escape sequences in a single value
    data = {
      "file_path": "/path/to/file.csv",
      "file_type": "delimiter_format",
      "import_type": "local",
      "sql_dialect": "hive",
      "has_header": True,
      "field_separator": "\\t\\t",  # Double tab
      "quote_char": "\\x22",  # Hex escape for double quote
      "record_separator": "\\x0A",  # Hex escape for newline
    }

    serializer = PreviewFileSerializer(data=data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data.field_separator == "\t\t"
    assert serializer.validated_data.quote_char == '"'
    assert serializer.validated_data.record_separator == "\n"

  def test_decode_escape_sequences_preserves_regular_strings(self):
    # Test that regular strings without escape sequences are preserved
    data = {
      "file_path": "/path/to/file.csv",
      "file_type": "delimiter_format",
      "import_type": "local",
      "sql_dialect": "hive",
      "has_header": True,
      "field_separator": "|",
      "quote_char": "'",
      "record_separator": "###",
    }

    serializer = PreviewFileSerializer(data=data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data.field_separator == "|"
    assert serializer.validated_data.quote_char == "'"
    assert serializer.validated_data.record_separator == "###"


class TestSqlTypeMapperSerializer:
  def test_valid_sql_dialect(self):
    for dialect in ["hive", "impala", "trino", "phoenix", "sparksql"]:
      valid_data = {"sql_dialect": dialect}

      serializer = SqlTypeMapperSerializer(data=valid_data)

      assert serializer.is_valid(), f"Failed for dialect '{dialect}': {serializer.errors}"
      assert isinstance(serializer.validated_data, SqlTypeMapperSchema)
      assert serializer.validated_data.sql_dialect == dialect

  def test_invalid_sql_dialect(self):
    invalid_data = {"sql_dialect": "invalid_dialect"}

    serializer = SqlTypeMapperSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert len(serializer.errors) > 0
    error_messages = str(serializer.errors)
    assert "sql_dialect" in error_messages

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
    assert isinstance(serializer.validated_data, GuessFileHeaderSchema)
    assert serializer.validated_data.file_path == "/path/to/file.csv"
    assert serializer.validated_data.file_type == "csv"
    assert serializer.validated_data.import_type == "local"

  def test_valid_data_excel(self):
    valid_data = {"file_path": "/path/to/file.xlsx", "file_type": "excel", "import_type": "local", "sheet_name": "Sheet1"}

    serializer = GuessFileHeaderSerializer(data=valid_data)

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert isinstance(serializer.validated_data, GuessFileHeaderSchema)
    assert serializer.validated_data.file_type == "excel"
    assert serializer.validated_data.sheet_name == "Sheet1"

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
    assert len(serializer.errors) > 0
    error_messages = str(serializer.errors)
    assert "Sheet name is required for Excel files" in error_messages

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
    assert isinstance(serializer.validated_data, GuessFileHeaderSchema)

  def test_invalid_file_type(self):
    invalid_data = {
      "file_path": "/path/to/file.json",
      "file_type": "json",  # Not a valid choice
      "import_type": "local",
    }

    serializer = GuessFileHeaderSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert len(serializer.errors) > 0
    error_messages = str(serializer.errors)
    assert "file_type" in error_messages

  def test_invalid_import_type(self):
    invalid_data = {
      "file_path": "/path/to/file.csv",
      "file_type": "csv",
      "import_type": "invalid_type",  # Not a valid choice
    }

    serializer = GuessFileHeaderSerializer(data=invalid_data)

    assert not serializer.is_valid()
    assert len(serializer.errors) > 0
    error_messages = str(serializer.errors)
    assert "import_type" in error_messages
