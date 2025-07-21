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
import tempfile
import zipfile
from unittest.mock import MagicMock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from desktop.conf import IMPORTER
from desktop.lib.importer import operations
from desktop.lib.importer.schemas import (
  GuessFileHeaderSchema,
  GuessFileMetadataSchema,
  LocalFileUploadSchema,
  PreviewFileSchema,
  SqlTypeMapperSchema,
)


class TestLocalFileUpload:
  def test_local_file_upload_success(self):
    resets = [
      IMPORTER.RESTRICT_LOCAL_FILE_EXTENSIONS.set_for_testing([".exe", ".bat"]),
      IMPORTER.MAX_LOCAL_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(10 * 1024 * 1024),  # 10 MiB limit
    ]

    try:
      test_file = SimpleUploadedFile(name="test_file.csv", content=b"header1,header2\nvalue1,value2", content_type="text/csv")

      # Create schema object
      schema = LocalFileUploadSchema(file=test_file, filename="test_file.csv", filesize=test_file.size)

      result = operations.local_file_upload(schema, "test_user")

      assert "file_path" in result
      file_path = result["file_path"]

      # Verify the file path contains expected components
      assert "test_user_" in file_path
      assert "_test_file.csv" in file_path
      assert file_path.startswith(tempfile.gettempdir())

      # Verify the file was created and has the right content
      assert os.path.exists(file_path)
      with open(file_path, "rb") as f:
        assert f.read() == b"header1,header2\nvalue1,value2"

    finally:
      # Clean up in case assertion fails
      if os.path.exists(result["file_path"]):
        os.remove(result["file_path"])

      for reset in resets:
        reset()

  def test_local_file_upload_empty_username(self):
    test_file = SimpleUploadedFile(name="test_file.csv", content=b"header1,header2\nvalue1,value2", content_type="text/csv")

    # Create schema object
    schema = LocalFileUploadSchema(file=test_file, filename="test_file.csv", filesize=test_file.size)

    with pytest.raises(ValueError, match="Username cannot be None or empty."):
      operations.local_file_upload(schema, "")

  @patch("tempfile.NamedTemporaryFile")
  @patch("shutil.copyfileobj")
  def test_local_file_upload_exception_handling_with_cleanup(self, mock_copyfileobj, mock_tempfile):
    resets = [
      IMPORTER.RESTRICT_LOCAL_FILE_EXTENSIONS.set_for_testing([".exe", ".bat"]),
      IMPORTER.MAX_LOCAL_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(10 * 1024 * 1024),  # 10 MiB limit
    ]

    # Mock the temporary file
    mock_file = MagicMock()
    mock_file.name = "/tmp/test_user_12345678_test_file.csv"
    mock_tempfile.return_value = mock_file
    mock_file.__enter__.return_value = mock_file

    # Make copyfileobj raise an exception
    mock_copyfileobj.side_effect = IOError("Test IO Error")

    test_file = SimpleUploadedFile(name="test_file.csv", content=b"header1,header2\nvalue1,value2", content_type="text/csv")

    # Create schema object
    schema = LocalFileUploadSchema(file=test_file, filename="test_file.csv", filesize=test_file.size)

    # Create the temp file for testing cleanup
    with open(mock_file.name, "w") as f:
      f.write("temp")

    try:
      with pytest.raises(IOError, match="Test IO Error"):
        operations.local_file_upload(schema, "test_user")

      # Verify the file was cleaned up after the exception
      assert not os.path.exists(mock_file.name), "Temporary file was not cleaned up after exception"

    finally:
      # Clean up in case assertion fails
      if os.path.exists(mock_file.name):
        os.remove(mock_file.name)

      for reset in resets:
        reset()

  def test_local_file_upload_special_characters_in_filename(self):
    resets = [
      IMPORTER.RESTRICT_LOCAL_FILE_EXTENSIONS.set_for_testing([".exe", ".bat"]),
      IMPORTER.MAX_LOCAL_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(10 * 1024 * 1024),  # 10 MiB limit
    ]

    # Test with special characters in filename
    test_file = SimpleUploadedFile(name="test file (with) [special] {chars} & symbols!.csv", content=b"data", content_type="text/csv")

    # Create schema object
    schema = LocalFileUploadSchema(file=test_file, filename="test file (with) [special] {chars} & symbols!.csv", filesize=test_file.size)

    result = operations.local_file_upload(schema, "test_user")

    try:
      assert "file_path" in result
      file_path = result["file_path"]

      # Verify the file was created
      assert os.path.exists(file_path)

      # Verify filename is sanitized properly
      assert "_test file (with) [special] {chars} & symbols!.csv" in file_path

    finally:
      # Clean up the file
      if os.path.exists(result["file_path"]):
        os.remove(result["file_path"])

      for reset in resets:
        reset()


@pytest.mark.usefixtures("cleanup_temp_files")
class TestGuessFileMetadata:
  @pytest.fixture
  def cleanup_temp_files(self):
    """Fixture to clean up temporary files after tests."""
    temp_files = []

    yield temp_files

    # Clean up after test
    for file_path in temp_files:
      if os.path.exists(file_path):
        os.remove(file_path)

  @patch("desktop.lib.importer.operations.is_magic_lib_available", True)
  @patch("desktop.lib.importer.operations.magic")
  def test_guess_file_metadata_csv(self, mock_magic, cleanup_temp_files):
    # Create a temporary CSV file
    test_content = "col1,col2,col3\nval1,val2,val3\nval4,val5,val6"
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(test_content.encode("utf-8"))
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    # Mock magic.from_buffer to return text/csv MIME type
    mock_magic.from_buffer.return_value = "text/plain"

    # Create schema object
    schema = GuessFileMetadataSchema(file_path=temp_file.name, import_type="local")

    result = operations.guess_file_metadata(data=schema, username="test_user")

    assert result == {
      "type": "csv",
      "field_separator": ",",
      "quote_char": '"',
      "record_separator": "\r\n",
    }

  @patch("desktop.lib.importer.operations.is_magic_lib_available", True)
  @patch("desktop.lib.importer.operations.magic")
  def test_guess_file_metadata_tsv(self, mock_magic, cleanup_temp_files):
    # Create a temporary TSV file
    test_content = "col1\tcol2\tcol3\nval1\tval2\tval3\nval4\tval5\tval6"
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(test_content.encode("utf-8"))
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    # Mock magic.from_buffer to return text/plain MIME type
    mock_magic.from_buffer.return_value = "text/plain"

    # Create schema object
    schema = GuessFileMetadataSchema(file_path=temp_file.name, import_type="local")

    result = operations.guess_file_metadata(data=schema, username="test_user")

    assert result == {
      "type": "tsv",
      "field_separator": "\t",
      "quote_char": '"',
      "record_separator": "\r\n",
    }

  @patch("desktop.lib.importer.operations.is_magic_lib_available", True)
  @patch("desktop.lib.importer.operations.magic")
  @patch("desktop.lib.importer.operations._get_sheet_names_xlsx")
  def test_guess_file_metadata_excel(self, mock_get_sheet_names, mock_magic, cleanup_temp_files):
    # Create a simple .xlsx file
    test_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
      <sheets>
      <sheet name="Sheet1" sheetId="1"/>
      <sheet name="Sheet2" sheetId="2"/>
      <sheet name="Sheet3" sheetId="3"/>
      </sheets>
    </workbook>"""

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    temp_file.write(test_content.encode("utf-8"))
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    # Mock magic.from_buffer to return Excel MIME type
    mock_magic.from_buffer.return_value = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    # Mock _get_sheet_names_xlsx to return sheet names
    mock_get_sheet_names.return_value = ["Sheet1", "Sheet2", "Sheet3"]

    # Create schema object
    schema = GuessFileMetadataSchema(file_path=temp_file.name, import_type="local")

    result = operations.guess_file_metadata(data=schema, username="test_user")

    assert result == {
      "type": "excel",
      "sheet_names": ["Sheet1", "Sheet2", "Sheet3"],
    }

  @patch("desktop.lib.importer.operations.is_magic_lib_available", True)
  @patch("desktop.lib.importer.operations.magic")
  def test_guess_file_metadata_unsupported_type(self, mock_magic, cleanup_temp_files):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(b"Binary content")
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    # Mock magic.from_buffer to return an unsupported MIME type
    mock_magic.from_buffer.return_value = "application/octet-stream"

    # Create schema object
    schema = GuessFileMetadataSchema(file_path=temp_file.name, import_type="local")

    with pytest.raises(ValueError, match="Unable to detect file format."):
      operations.guess_file_metadata(data=schema, username="test_user")

  def test_guess_file_metadata_nonexistent_file(self):
    # Create schema object
    schema = GuessFileMetadataSchema(file_path="/path/to/nonexistent/file.csv", import_type="local")

    with pytest.raises(ValueError, match="Local file does not exist."):
      operations.guess_file_metadata(data=schema, username="test_user")

  def test_guess_remote_file_metadata_no_username(self):
    # Create schema object
    schema = GuessFileMetadataSchema(file_path="s3a://bucket/user/test_user/test.csv", import_type="remote")

    with pytest.raises(ValueError, match="Username is required"):
      operations.guess_file_metadata(data=schema, username="")

  def test_guess_file_metadata_empty_file(self, cleanup_temp_files):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    # Create schema object
    schema = GuessFileMetadataSchema(file_path=temp_file.name, import_type="local")

    with pytest.raises(ValueError, match="File is empty, cannot detect file format."):
      operations.guess_file_metadata(data=schema, username="test_user")

  @patch("desktop.lib.importer.operations.is_magic_lib_available", False)
  def test_guess_file_metadata_no_magic_lib(self, cleanup_temp_files):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(b"Content")
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    # Create schema object
    schema = GuessFileMetadataSchema(file_path=temp_file.name, import_type="local")

    with pytest.raises(RuntimeError, match="Unable to guess file type. python-magic or its dependency libmagic is not installed."):
      operations.guess_file_metadata(data=schema, username="test_user")


@pytest.mark.usefixtures("cleanup_temp_files")
class TestPreviewFile:
  @pytest.fixture
  def cleanup_temp_files(self):
    """Fixture to clean up temporary files after tests."""
    temp_files = []

    yield temp_files

    # Clean up after test
    for file_path in temp_files:
      if os.path.exists(file_path):
        os.remove(file_path)

  @patch("desktop.lib.importer.operations.pl")
  def test_preview_excel_file(self, mock_pl, cleanup_temp_files):
    # Minimal Excel file content (not a real Excel binary, just placeholder for test)
    test_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
      <sheets>
      <sheet name="Sheet1" sheetId="1"/>
      </sheets>
    </workbook>"""

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    temp_file.write(test_content.encode("utf-8"))
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    mock_df = MagicMock(
      height=2,
      columns=["col1", "col2"],
      schema={"col1": "Int32", "col2": "Utf8"},
      to_dict=MagicMock(return_value={"col1": [1, 2], "col2": ["foo", "bar"]}),
    )

    mock_pl.read_excel.return_value = mock_df

    # Create schema object
    schema = PreviewFileSchema(
      file_path=temp_file.name, file_type="excel", import_type="local", sql_dialect="hive", has_header=True, sheet_name="Sheet1"
    )

    result = operations.preview_file(data=schema, username="test_user")

    assert result == {
      "type": "excel",
      "columns": [
        {"name": "col1", "type": "INT"},
        {"name": "col2", "type": "STRING"},
      ],
      "preview_data": {"col1": [1, 2], "col2": ["foo", "bar"]},
    }

  def test_preview_csv_file(self, cleanup_temp_files):
    # Create a temporary CSV file
    test_content = "col1,col2\n1.1,true\n2.2,false"
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(test_content.encode("utf-8"))
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    # Create schema object
    schema = PreviewFileSchema(
      file_path=temp_file.name,
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      field_separator=",",
      quote_char='"',
      record_separator="\n",
    )

    result = operations.preview_file(data=schema, username="test_user")

    assert result == {
      "type": "csv",
      "columns": [
        {"name": "col1", "type": "DOUBLE"},
        {"name": "col2", "type": "BOOLEAN"},
      ],
      "preview_data": {"col1": [1.1, 2.2], "col2": [True, False]},
    }

  def test_preview_csv_file_with_header_false(self, cleanup_temp_files):
    # Create a temporary CSV file
    test_content = "sample1,sample2\n1.1,true\n2.2,false"
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(test_content.encode("utf-8"))
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    # Create schema object
    schema = PreviewFileSchema(
      file_path=temp_file.name,
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=False,  # No header in this case
      field_separator=",",
      quote_char='"',
      record_separator="\n",
    )

    result = operations.preview_file(data=schema, username="test_user")

    assert result == {
      "type": "csv",
      "columns": [{"name": "column_1", "type": "STRING"}, {"name": "column_2", "type": "STRING"}],
      "preview_data": {"column_1": ["sample1", "1.1", "2.2"], "column_2": ["sample2", "true", "false"]},
    }

  def test_preview_empty_csv_file(self, cleanup_temp_files):
    # Create a temporary CSV file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(b" ")
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    # Create schema object
    schema = PreviewFileSchema(
      file_path=temp_file.name,
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      field_separator=",",
      quote_char='"',
      record_separator="\n",
    )

    result = operations.preview_file(data=schema, username="test_user")

    assert result == {
      "type": "csv",
      "columns": [],
      "preview_data": {},
    }

  def test_preview_remote_file_no_username(self):
    # Create schema object
    schema = PreviewFileSchema(
      file_path="s3a://bucket/user/test_user/test.csv", file_type="csv", import_type="remote", sql_dialect="hive", has_header=True
    )

    with pytest.raises(ValueError, match="Username is required"):
      operations.preview_file(data=schema, username="")

  @patch("os.path.exists")
  def test_preview_nonexistent_local_file(self, mock_exists):
    mock_exists.return_value = False

    # Create schema object
    schema = PreviewFileSchema(
      file_path="/path/to/nonexistent.csv", file_type="csv", import_type="local", sql_dialect="hive", has_header=True
    )

    with pytest.raises(ValueError, match="Local file does not exist: /path/to/nonexistent.csv"):
      operations.preview_file(data=schema, username="test_user")

  def test_preview_trino_dialect_type_mapping(self, cleanup_temp_files):
    test_content = "string_col\nfoo\nbar"
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(test_content.encode("utf-8"))
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    # Create schema object
    schema = PreviewFileSchema(
      file_path=temp_file.name,
      file_type="csv",
      import_type="local",
      sql_dialect="trino",  # Trino dialect for different type mapping
      has_header=True,
      field_separator=",",
    )

    result = operations.preview_file(data=schema, username="test_user")

    # Check the result for Trino-specific type mapping
    assert result["columns"][0]["type"] == "VARCHAR"  # Not STRING


@pytest.mark.usefixtures("cleanup_temp_files")
class TestGuessFileHeader:
  @pytest.fixture
  def cleanup_temp_files(self):
    """Fixture to clean up temporary files after tests."""
    temp_files = []

    yield temp_files

    # Clean up after test
    for file_path in temp_files:
      if os.path.exists(file_path):
        os.remove(file_path)

  def test_guess_header_csv(self, cleanup_temp_files):
    test_content = "header1,header2\nvalue1,value2\nvalue3,value4"
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(test_content.encode("utf-8"))
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    # Create schema object
    schema = GuessFileHeaderSchema(file_path=temp_file.name, file_type="csv", import_type="local")

    result = operations.guess_file_header(data=schema, username="test_user")

    assert result

  @patch("desktop.lib.importer.operations.pl")
  @patch("desktop.lib.importer.operations.csv.Sniffer")
  def test_guess_header_excel(self, mock_sniffer, mock_pl, cleanup_temp_files):
    test_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
      <sheets>
      <sheet name="Sheet1" sheetId="1"/>
      </sheets>
    </workbook>"""

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    temp_file.write(test_content.encode("utf-8"))
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    # Mock polars read_excel and CSV conversion
    mock_pl.read_excel.return_value.write_csv.return_value = "header1,header2\nvalue1,value2\nvalue3,value4"

    # Mock csv.Sniffer
    mock_sniffer_instance = MagicMock()
    mock_sniffer_instance.has_header.return_value = True
    mock_sniffer.return_value = mock_sniffer_instance

    # Create schema object
    schema = GuessFileHeaderSchema(file_path=temp_file.name, file_type="excel", import_type="local", sheet_name="Sheet1")

    result = operations.guess_file_header(data=schema, username="test_user")

    assert result

  def test_guess_header_nonexistent_local_file(self):
    # Create schema object
    schema = GuessFileHeaderSchema(file_path="/path/to/nonexistent/file.csv", file_type="csv", import_type="local")

    with pytest.raises(ValueError, match="Local file does not exist"):
      operations.guess_file_header(data=schema, username="test_user")

  def test_guess_header_remote_file_no_username(self):
    # Create schema object
    schema = GuessFileHeaderSchema(file_path="s3a://bucket/user/test_user/test.csv", file_type="csv", import_type="remote")

    with pytest.raises(ValueError, match="Username is required"):
      operations.guess_file_header(data=schema, username="")


class TestSqlTypeMapping:
  def test_get_sql_type_mapping_hive(self):
    # Create schema object
    schema = SqlTypeMapperSchema(sql_dialect="hive")

    result = operations.get_sql_type_mapping(schema)

    # Test that Hive returns the expected unique SQL types
    expected_hive_types = [
      "ARRAY",
      "BIGINT",
      "BINARY",
      "BOOLEAN",
      "DATE",
      "DECIMAL",
      "DOUBLE",
      "FLOAT",
      "INT",
      "INTERVAL DAY TO SECOND",
      "SMALLINT",
      "STRING",
      "STRUCT",
      "TIMESTAMP",
      "TINYINT",
    ]
    assert result == expected_hive_types

  def test_get_sql_type_mapping_trino(self):
    # Create schema object
    schema = SqlTypeMapperSchema(sql_dialect="trino")

    result = operations.get_sql_type_mapping(schema)

    # Test that Trino returns the expected unique SQL types
    expected_trino_types = [
      "ARRAY",
      "BIGINT",
      "BOOLEAN",
      "DATE",
      "DECIMAL",
      "DOUBLE",
      "INTEGER",
      "INTERVAL DAY TO SECOND",
      "JSON",
      "REAL",
      "ROW",
      "SMALLINT",
      "STRING",
      "TIMESTAMP",
      "TINYINT",
      "VARBINARY",
      "VARCHAR",
    ]
    assert result == expected_trino_types

  def test_get_sql_type_mapping_phoenix(self):
    # Create schema object
    schema = SqlTypeMapperSchema(sql_dialect="phoenix")

    result = operations.get_sql_type_mapping(schema)

    # Test that Phoenix returns the expected unique SQL types
    expected_phoenix_types = [
      "ARRAY",
      "BIGINT",
      "BOOLEAN",
      "DATE",
      "DECIMAL",
      "DOUBLE",
      "FLOAT",
      "INT",
      "SMALLINT",
      "STRING",
      "TIME",
      "TIMESTAMP",
      "TINYINT",
      "UNSIGNED_INT",
      "UNSIGNED_LONG",
      "UNSIGNED_SMALLINT",
      "UNSIGNED_TINYINT",
      "VARBINARY",
      "VARCHAR",
    ]
    assert result == expected_phoenix_types

  def test_get_sql_type_mapping_impala(self):
    # Create schema object
    schema = SqlTypeMapperSchema(sql_dialect="impala")

    result = operations.get_sql_type_mapping(schema)

    # Test that Impala returns the expected unique SQL types
    # Note: Impala doesn't support INTERVAL types, so Duration maps to STRING
    expected_impala_types = [
      "ARRAY",
      "BIGINT",
      "BINARY",
      "BOOLEAN",
      "DATE",
      "DECIMAL",
      "DOUBLE",
      "FLOAT",
      "INT",
      "SMALLINT",
      "STRING",
      "STRUCT",
      "TIMESTAMP",
      "TINYINT",
    ]
    assert result == expected_impala_types

  def test_get_sql_type_mapping_sparksql(self):
    # Create schema object
    schema = SqlTypeMapperSchema(sql_dialect="sparksql")

    result = operations.get_sql_type_mapping(schema)

    # Test that SparkSQL returns the expected unique SQL types (same as Hive)
    expected_sparksql_types = [
      "ARRAY",
      "BIGINT",
      "BINARY",
      "BOOLEAN",
      "DATE",
      "DECIMAL",
      "DOUBLE",
      "FLOAT",
      "INT",
      "INTERVAL DAY TO SECOND",
      "SMALLINT",
      "STRING",
      "STRUCT",
      "TIMESTAMP",
      "TINYINT",
    ]
    assert result == expected_sparksql_types

  def test_get_sql_type_mapping_all_dialects_consistency(self):
    # Test that all dialects return a non-empty list of SQL types
    dialects = ["hive", "impala", "sparksql", "trino", "phoenix"]

    for dialect in dialects:
      schema = SqlTypeMapperSchema(sql_dialect=dialect)
      result = operations.get_sql_type_mapping(schema)

      # Ensure result is a list
      assert isinstance(result, list), f"Result for {dialect} is not a list"

      # Ensure the list is not empty
      assert len(result) > 0, f"Empty result for {dialect} dialect"

      # Ensure all items in the list are strings
      for sql_type in result:
        assert isinstance(sql_type, str), f"Invalid type in result for {dialect}: {sql_type}"
        assert len(sql_type) > 0, f"Empty SQL type string in {dialect} dialect"

  def test_get_polars_to_sql_mapping(self):
    # Test the internal function that returns the full mapping

    # Test Hive dialect
    hive_mapping = operations._get_polars_to_sql_mapping("hive")
    assert isinstance(hive_mapping, dict)
    assert hive_mapping["Int32"] == "INT"
    assert hive_mapping["Utf8"] == "STRING"
    assert hive_mapping["Boolean"] == "BOOLEAN"

    # Test Trino dialect with overrides
    trino_mapping = operations._get_polars_to_sql_mapping("trino")
    assert isinstance(trino_mapping, dict)
    assert trino_mapping["Int32"] == "INTEGER"  # Override
    assert trino_mapping["Float32"] == "REAL"  # Override
    assert trino_mapping["Utf8"] == "VARCHAR"  # Override
    assert trino_mapping["Boolean"] == "BOOLEAN"  # No override

    # Test unsupported dialect
    with pytest.raises(ValueError, match="Unsupported dialect"):
      operations._get_polars_to_sql_mapping("unsupported_dialect")

  def test_map_polars_dtype_to_sql_type(self):
    # Test comprehensive type mapping for each dialect

    # Hive dialect tests
    assert operations._map_polars_dtype_to_sql_type("hive", "Int8") == "TINYINT"
    assert operations._map_polars_dtype_to_sql_type("hive", "Int32") == "INT"
    assert operations._map_polars_dtype_to_sql_type("hive", "Float64") == "DOUBLE"
    assert operations._map_polars_dtype_to_sql_type("hive", "Utf8") == "STRING"
    assert operations._map_polars_dtype_to_sql_type("hive", "Boolean") == "BOOLEAN"
    assert operations._map_polars_dtype_to_sql_type("hive", "Date") == "DATE"
    assert operations._map_polars_dtype_to_sql_type("hive", "Array") == "ARRAY"

    # Trino dialect tests (with overrides)
    assert operations._map_polars_dtype_to_sql_type("trino", "Int32") == "INTEGER"
    assert operations._map_polars_dtype_to_sql_type("trino", "Float32") == "REAL"
    assert operations._map_polars_dtype_to_sql_type("trino", "Utf8") == "VARCHAR"
    assert operations._map_polars_dtype_to_sql_type("trino", "Binary") == "VARBINARY"
    assert operations._map_polars_dtype_to_sql_type("trino", "Struct") == "ROW"
    assert operations._map_polars_dtype_to_sql_type("trino", "Object") == "JSON"

    # Phoenix dialect tests (with unsigned types)
    assert operations._map_polars_dtype_to_sql_type("phoenix", "UInt8") == "UNSIGNED_TINYINT"
    assert operations._map_polars_dtype_to_sql_type("phoenix", "UInt32") == "UNSIGNED_INT"
    assert operations._map_polars_dtype_to_sql_type("phoenix", "UInt64") == "UNSIGNED_LONG"
    assert operations._map_polars_dtype_to_sql_type("phoenix", "Time") == "TIME"
    assert operations._map_polars_dtype_to_sql_type("phoenix", "Duration") == "STRING"
    assert operations._map_polars_dtype_to_sql_type("phoenix", "Struct") == "STRING"

    # Impala dialect tests (with Duration override)
    assert operations._map_polars_dtype_to_sql_type("impala", "Duration") == "STRING"
    assert operations._map_polars_dtype_to_sql_type("impala", "Int32") == "INT"  # No override
    assert operations._map_polars_dtype_to_sql_type("impala", "Utf8") == "STRING"  # No override

    # Test error for unknown type
    with pytest.raises(ValueError, match="No mapping for Polars dtype"):
      operations._map_polars_dtype_to_sql_type("hive", "UnknownType")


@pytest.mark.usefixtures("cleanup_temp_files")
class TestExcelSheetNames:
  @pytest.fixture
  def cleanup_temp_files(self):
    """Fixture to clean up temporary files after tests."""
    temp_files = []

    yield temp_files

    # Clean up after test
    for file_path in temp_files:
      if os.path.exists(file_path):
        os.remove(file_path)

  def test_get_sheet_names_xlsx(self, cleanup_temp_files):
    # Create a temporary Excel file with minimal XML structure
    with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp_file:
      # Create a minimal XLSX with workbook.xml
      with zipfile.ZipFile(tmp_file.name, "w") as zip_file:
        # Create a minimal workbook.xml file
        workbook_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
          <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
            <sheets>
              <sheet name="Sheet1" sheetId="1"/>
              <sheet name="Sheet2" sheetId="2"/>
              <sheet name="CustomSheet" sheetId="3"/>
            </sheets>
          </workbook>"""
        zip_file.writestr("xl/workbook.xml", workbook_xml)

      cleanup_temp_files.append(tmp_file.name)

      # Test the function
      with open(tmp_file.name, "rb") as f:
        sheet_names = operations._get_sheet_names_xlsx(f)

      assert sheet_names == ["Sheet1", "Sheet2", "CustomSheet"]
