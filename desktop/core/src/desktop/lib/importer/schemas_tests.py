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

from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from desktop.conf import IMPORTER
from desktop.lib.importer.schemas import (
  GuessFileHeaderSchema,
  GuessFileMetadataSchema,
  LocalFileUploadSchema,
  PreviewFileSchema,
  SqlTypeMapperSchema,
)


class TestLocalFileUploadSchema:
  def test_valid_file_upload(self):
    resets = [
      IMPORTER.RESTRICT_LOCAL_FILE_EXTENSIONS.set_for_testing([".exe", ".bat"]),
      IMPORTER.MAX_LOCAL_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(10 * 1024 * 1024),  # 10 MiB limit
    ]
    try:
      mock_file = MagicMock()
      schema = LocalFileUploadSchema(file=mock_file, filename="test.csv", filesize=1024)

      assert schema.file == mock_file
      assert schema.filename == "test.csv"
      assert schema.filesize == 1024
    finally:
      for reset in resets:
        reset()

  def test_restricted_file_extension(self):
    resets = [IMPORTER.RESTRICT_LOCAL_FILE_EXTENSIONS.set_for_testing([".exe", ".bat", ".csv"])]
    try:
      mock_file = MagicMock()

      with pytest.raises(ValidationError) as exc_info:
        LocalFileUploadSchema(file=mock_file, filename="test.csv", filesize=1024)

      errors = exc_info.value.errors()
      assert len(errors) == 1
      assert "filename" in str(errors[0]["loc"])
      assert "not allowed" in str(errors[0]["msg"])
    finally:
      for reset in resets:
        reset()

  def test_file_too_large(self):
    resets = [IMPORTER.MAX_LOCAL_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(1024 * 1024)]  # 1 MiB
    try:
      mock_file = MagicMock()

      with pytest.raises(ValidationError) as exc_info:
        LocalFileUploadSchema(file=mock_file, filename="test.csv", filesize=1024 * 1024 * 2)  # 2 MiB

      errors = exc_info.value.errors()
      assert len(errors) == 1
      assert "filesize" in str(errors[0]["loc"])
      assert "too large" in str(errors[0]["msg"])
    finally:
      for reset in resets:
        reset()

  def test_case_insensitive_extension_check(self):
    resets = [
      IMPORTER.RESTRICT_LOCAL_FILE_EXTENSIONS.set_for_testing([".EXE", ".BAT"]),
      IMPORTER.MAX_LOCAL_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(1024 * 1024 * 10),  # 10 MiB limit
    ]
    try:
      mock_file = MagicMock()

      with pytest.raises(ValidationError) as exc_info:
        LocalFileUploadSchema(file=mock_file, filename="test.exe", filesize=1024)

      errors = exc_info.value.errors()
      assert len(errors) == 1
      assert "filename" in str(errors[0]["loc"])
      assert "not allowed" in str(errors[0]["msg"])
    finally:
      for reset in resets:
        reset()

  def test_missing_file(self):
    with pytest.raises(ValidationError) as exc_info:
      LocalFileUploadSchema()

    errors = exc_info.value.errors()
    assert len(errors) == 3
    assert "file" in str(errors[0]["loc"])
    assert "filename" in str(errors[1]["loc"])
    assert "filesize" in str(errors[2]["loc"])


class TestGuessFileMetadataSchema:
  def test_valid_local_file_metadata(self):
    schema = GuessFileMetadataSchema(file_path="/path/to/test.csv", import_type="local")

    assert schema.file_path == "/path/to/test.csv"
    assert schema.import_type == "local"

  def test_valid_remote_file_metadata(self):
    schema = GuessFileMetadataSchema(file_path="s3a://bucket/test.csv", import_type="remote")

    assert schema.file_path == "s3a://bucket/test.csv"
    assert schema.import_type == "remote"

  def test_invalid_import_type(self):
    with pytest.raises(ValidationError) as exc_info:
      GuessFileMetadataSchema(file_path="/path/to/test.csv", import_type="invalid")

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "import_type" in str(errors[0]["loc"])

  def test_missing_required_fields(self):
    with pytest.raises(ValidationError) as exc_info:
      GuessFileMetadataSchema()

    errors = exc_info.value.errors()
    assert len(errors) == 2  # file_path and import_type are required

  def test_invalid_file_path(self):
    with pytest.raises(ValidationError) as exc_info:
      GuessFileMetadataSchema(file_path="", import_type="local")

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "file_path" in str(errors[0]["loc"])


class TestPreviewFileSchema:
  def test_valid_csv_preview(self):
    schema = PreviewFileSchema(
      file_path="/path/to/test.csv",
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      field_separator=",",
      quote_char='"',
      record_separator="\n",
    )

    assert schema.file_path == "/path/to/test.csv"
    assert schema.file_type == "csv"
    assert schema.import_type == "local"
    assert schema.sql_dialect == "hive"
    assert schema.has_header is True
    assert schema.field_separator == ","
    assert schema.quote_char == '"'
    assert schema.record_separator == "\n"

  def test_csv_default_values(self):
    schema = PreviewFileSchema(file_path="/path/to/test.csv", file_type="csv", import_type="local", sql_dialect="hive", has_header=False)

    assert schema.field_separator == ","
    assert schema.quote_char == '"'
    assert schema.record_separator == "\n"

  def test_tsv_default_values(self):
    schema = PreviewFileSchema(file_path="/path/to/test.tsv", file_type="tsv", import_type="local", sql_dialect="hive", has_header=False)

    assert schema.field_separator == "\t"
    assert schema.quote_char == '"'
    assert schema.record_separator == "\n"

  def test_excel_requires_sheet_name(self):
    with pytest.raises(ValidationError) as exc_info:
      PreviewFileSchema(file_path="/path/to/test.xlsx", file_type="excel", import_type="local", sql_dialect="hive", has_header=False)

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "Sheet name is required for Excel files" in str(errors[0]["msg"])

  def test_valid_excel_preview(self):
    schema = PreviewFileSchema(
      file_path="/path/to/test.xlsx",
      file_type="excel",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      sheet_name="Sheet1",
    )

    assert schema.file_type == "excel"
    assert schema.sheet_name == "Sheet1"

  def test_delimiter_format_requires_field_separator(self):
    with pytest.raises(ValidationError) as exc_info:
      PreviewFileSchema(
        file_path="/path/to/test.txt", file_type="delimiter_format", import_type="local", sql_dialect="hive", has_header=False
      )

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "Field separator is required for delimited files" in str(errors[0]["msg"])

  def test_valid_delimiter_format(self):
    schema = PreviewFileSchema(
      file_path="/path/to/test.txt",
      file_type="delimiter_format",
      import_type="local",
      sql_dialect="hive",
      has_header=False,
      field_separator="|",
    )

    assert schema.field_separator == "|"
    assert schema.quote_char == '"'
    assert schema.record_separator == "\n"

  def test_invalid_file_type(self):
    with pytest.raises(ValidationError) as exc_info:
      PreviewFileSchema(file_path="/path/to/test.pdf", file_type="pdf", import_type="local", sql_dialect="hive", has_header=False)

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "file_type" in str(errors[0]["loc"])

  def test_invalid_file_path(self):
    with pytest.raises(ValidationError) as exc_info:
      PreviewFileSchema(file_path="", file_type="csv", import_type="local", sql_dialect="hive", has_header=False)

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "file_path" in str(errors[0]["loc"])

  def test_invalid_sql_dialect(self):
    with pytest.raises(ValidationError) as exc_info:
      PreviewFileSchema(file_path="/path/to/test.csv", file_type="csv", import_type="local", sql_dialect="mysql", has_header=False)

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "sql_dialect" in str(errors[0]["loc"])

  def test_decode_escape_sequences_field_separator(self):
    # Test tab escape sequence
    schema = PreviewFileSchema(
      file_path="/path/to/test.txt",
      file_type="delimiter_format",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      field_separator="\\t",  # Tab character as escape sequence
    )

    assert schema.field_separator == "\t"  # Should be decoded to actual tab

    # Test newline escape sequence
    schema = PreviewFileSchema(
      file_path="/path/to/test.txt",
      file_type="delimiter_format",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      field_separator="\\n",
    )
    assert schema.field_separator == "\n"

    # Test backslash escape sequence
    schema = PreviewFileSchema(
      file_path="/path/to/test.txt",
      file_type="delimiter_format",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      field_separator="\\\\",
    )
    assert schema.field_separator == "\\"

  def test_decode_escape_sequences_quote_char(self):
    # Test double quote escape sequence
    schema = PreviewFileSchema(
      file_path="/path/to/test.csv",
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      quote_char='\\"',  # Escaped double quote
    )

    assert schema.quote_char == '"'

    # Test single quote escape sequence
    schema = PreviewFileSchema(
      file_path="/path/to/test.csv",
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      quote_char="\\'",
    )
    assert schema.quote_char == "'"

    # Test Unicode escape sequence
    schema = PreviewFileSchema(
      file_path="/path/to/test.csv",
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      quote_char="\\u0022",  # Unicode for double quote
    )
    assert schema.quote_char == '"'

  def test_decode_escape_sequences_record_separator(self):
    # Test newline escape sequence
    schema = PreviewFileSchema(
      file_path="/path/to/test.csv",
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      record_separator="\\n",
    )

    assert schema.record_separator == "\n"

    # Test carriage return + newline (should be normalized to just newline)
    schema = PreviewFileSchema(
      file_path="/path/to/test.csv",
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      record_separator="\\r\\n",
    )
    assert schema.record_separator == "\n"  # Should be normalized

    # Test just carriage return
    schema = PreviewFileSchema(
      file_path="/path/to/test.csv",
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      record_separator="\\r",
    )
    assert schema.record_separator == "\r"

  def test_decode_escape_sequences_with_none_values(self):
    # Test that None values are handled properly and defaults are set
    schema = PreviewFileSchema(
      file_path="/path/to/test.csv",
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      field_separator=None,
      quote_char=None,
      record_separator=None,
    )

    # CSV defaults should be applied
    assert schema.field_separator == ","
    assert schema.quote_char == '"'
    assert schema.record_separator == "\n"

  def test_decode_escape_sequences_with_complex_patterns(self):
    # Test multiple escape sequences in a single value
    schema = PreviewFileSchema(
      file_path="/path/to/test.txt",
      file_type="delimiter_format",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      field_separator="\\t\\t",  # Double tab
      quote_char="\\x22",  # Hex escape for double quote
      record_separator="\\x0A",  # Hex escape for newline
    )

    assert schema.field_separator == "\t\t"
    assert schema.quote_char == '"'
    assert schema.record_separator == "\n"

  def test_decode_escape_sequences_preserves_regular_strings(self):
    # Test that regular strings without escape sequences are preserved
    schema = PreviewFileSchema(
      file_path="/path/to/test.txt",
      file_type="delimiter_format",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      field_separator="|",
      quote_char="'",
      record_separator="###",
    )

    assert schema.field_separator == "|"
    assert schema.quote_char == "'"
    assert schema.record_separator == "###"

  def test_decode_escape_sequences_mixed_scenarios(self):
    # Test various escape sequence patterns
    test_cases = [
      ("\\x09", "\t"),  # Hex escape for tab
      ("\\u0009", "\t"),  # Unicode escape for tab
      ("\\a", "\a"),  # Bell/alert character
      ("\\b", "\b"),  # Backspace
      ("\\f", "\f"),  # Form feed
      ("\\v", "\v"),  # Vertical tab
      ("\\0", "\0"),  # Null character
    ]

    for input_val, expected_val in test_cases:
      schema = PreviewFileSchema(
        file_path="/path/to/test.txt",
        file_type="delimiter_format",
        import_type="local",
        sql_dialect="hive",
        has_header=True,
        field_separator=input_val,
      )
      assert schema.field_separator == expected_val, f"Failed for input: {repr(input_val)}"

  def test_record_separator_normalization(self):
    # Test that \r\n is normalized to \n
    schema = PreviewFileSchema(
      file_path="/path/to/test.csv",
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      record_separator="\r\n",  # Already decoded value
    )
    assert schema.record_separator == "\n"  # Should be normalized

    # But \r alone should remain as \r
    schema = PreviewFileSchema(
      file_path="/path/to/test.csv",
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      record_separator="\r",
    )
    assert schema.record_separator == "\r"  # Should NOT be normalized


class TestSqlTypeMapperSchema:
  def test_valid_sql_dialects(self):
    valid_dialects = ["hive", "impala", "trino", "phoenix", "sparksql"]

    for dialect in valid_dialects:
      schema = SqlTypeMapperSchema(sql_dialect=dialect)
      assert schema.sql_dialect == dialect

  def test_invalid_sql_dialect(self):
    with pytest.raises(ValidationError) as exc_info:
      SqlTypeMapperSchema(sql_dialect="mysql")

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "sql_dialect" in str(errors[0]["loc"])

  def test_missing_sql_dialect(self):
    with pytest.raises(ValidationError) as exc_info:
      SqlTypeMapperSchema()

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "sql_dialect" in str(errors[0]["loc"])


class TestGuessFileHeaderSchema:
  def test_valid_csv_header_guess(self):
    schema = GuessFileHeaderSchema(file_path="/path/to/test.csv", file_type="csv", import_type="local")

    assert schema.file_path == "/path/to/test.csv"
    assert schema.file_type == "csv"
    assert schema.import_type == "local"
    assert schema.sheet_name is None

  def test_excel_requires_sheet_name(self):
    with pytest.raises(ValidationError) as exc_info:
      GuessFileHeaderSchema(file_path="/path/to/test.xlsx", file_type="excel", import_type="local")

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "Sheet name is required for Excel files" in str(errors[0]["msg"])

  def test_valid_excel_header_guess(self):
    schema = GuessFileHeaderSchema(file_path="/path/to/test.xlsx", file_type="excel", import_type="local", sheet_name="Sheet1")

    assert schema.file_type == "excel"
    assert schema.sheet_name == "Sheet1"

  def test_valid_remote_file_header_guess(self):
    schema = GuessFileHeaderSchema(file_path="s3a://bucket/test.csv", file_type="csv", import_type="remote")

    assert schema.file_path == "s3a://bucket/test.csv"
    assert schema.import_type == "remote"

  def test_all_file_types(self):
    valid_file_types = ["csv", "tsv", "delimiter_format"]

    for file_type in valid_file_types:
      schema = GuessFileHeaderSchema(file_path=f"/path/to/test.{file_type}", file_type=file_type, import_type="local")
      assert schema.file_type == file_type

  def test_invalid_file_type(self):
    with pytest.raises(ValidationError) as exc_info:
      GuessFileHeaderSchema(file_path="/path/to/test.pdf", file_type="pdf", import_type="local")

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "file_type" in str(errors[0]["loc"])

  def test_missing_required_fields(self):
    with pytest.raises(ValidationError) as exc_info:
      GuessFileHeaderSchema(file_path="/path/to/test.csv")

    errors = exc_info.value.errors()
    assert len(errors) >= 2  # At least file_type and import_type are missing

  def test_invalid_file_path(self):
    with pytest.raises(ValidationError) as exc_info:
      GuessFileHeaderSchema(file_path="", file_type="csv", import_type="local")

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "file_path" in str(errors[0]["loc"])
