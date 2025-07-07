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
from unittest.mock import MagicMock, mock_open, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from desktop.lib.importer import operations


class TestLocalFileUpload:
  @patch("uuid.uuid4")
  def test_local_file_upload_success(self, mock_uuid):
    # Mock uuid to get a predictable filename
    mock_uuid.return_value.hex = "12345678"

    test_file = SimpleUploadedFile(name="test_file.csv", content=b"header1,header2\nvalue1,value2", content_type="text/csv")

    result = operations.local_file_upload(test_file, "test_user")

    # Get the expected file path
    temp_dir = tempfile.gettempdir()
    expected_path = os.path.join(temp_dir, "test_user_12345678_test_file.csv")

    try:
      assert "file_path" in result
      assert result["file_path"] == expected_path

      # Verify the file was created and has the right content
      assert os.path.exists(expected_path)
      with open(expected_path, "rb") as f:
        assert f.read() == b"header1,header2\nvalue1,value2"

    finally:
      # Clean up the file
      if os.path.exists(expected_path):
        os.remove(expected_path)

      assert not os.path.exists(expected_path), "Temporary file was not cleaned up properly"

  def test_local_file_upload_none_file(self):
    with pytest.raises(ValueError, match="Upload file cannot be None or empty."):
      operations.local_file_upload(None, "test_user")

  def test_local_file_upload_none_username(self):
    test_file = SimpleUploadedFile(name="test_file.csv", content=b"header1,header2\nvalue1,value2", content_type="text/csv")

    with pytest.raises(ValueError, match="Username cannot be None or empty."):
      operations.local_file_upload(test_file, None)

  @patch("os.path.join")
  @patch("builtins.open", new_callable=mock_open)
  def test_local_file_upload_exception_handling(self, mock_file_open, mock_join):
    # Setup mocks to raise an exception when opening the file
    mock_file_open.side_effect = IOError("Test IO Error")
    mock_join.return_value = "/tmp/test_user_12345678_test_file.csv"

    test_file = SimpleUploadedFile(name="test_file.csv", content=b"header1,header2\nvalue1,value2", content_type="text/csv")

    with pytest.raises(Exception, match="Test IO Error"):
      operations.local_file_upload(test_file, "test_user")


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

    result = operations.guess_file_metadata(temp_file.name, "local")

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

    result = operations.guess_file_metadata(temp_file.name, "local")

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

    result = operations.guess_file_metadata(temp_file.name, "local")

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

    with pytest.raises(ValueError, match="Unable to detect file format."):
      operations.guess_file_metadata(temp_file.name, "local")

  def test_guess_file_metadata_nonexistent_file(self):
    file_path = "/path/to/nonexistent/file.csv"

    with pytest.raises(ValueError, match="Local file does not exist."):
      operations.guess_file_metadata(file_path, "local")

  def test_guess_remote_file_metadata_no_fs(self):
    with pytest.raises(ValueError, match="File system object is required for remote import type"):
      operations.guess_file_metadata(
        file_path="s3a://bucket/user/test_user/test.csv",  # Remote file path
        import_type="remote",  # Remote file but no fs provided
      )

  def test_guess_file_metadata_empty_file(self, cleanup_temp_files):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    with pytest.raises(ValueError, match="File is empty, cannot detect file format."):
      operations.guess_file_metadata(temp_file.name, "local")

  @patch("desktop.lib.importer.operations.is_magic_lib_available", False)
  def test_guess_file_metadata_no_magic_lib(self, cleanup_temp_files):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(b"Content")
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    with pytest.raises(RuntimeError, match="Unable to guess file type. python-magic or its dependency libmagic is not installed."):
      operations.guess_file_metadata(temp_file.name, "local")


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

    result = operations.preview_file(
      file_path=temp_file.name, file_type="excel", import_type="local", sql_dialect="hive", has_header=True, sheet_name="Sheet1"
    )

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

    result = operations.preview_file(
      file_path=temp_file.name,
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      field_separator=",",
      quote_char='"',
      record_separator="\n",
    )

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

    result = operations.preview_file(
      file_path=temp_file.name,
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=False,  # No header in this case
      field_separator=",",
      quote_char='"',
      record_separator="\n",
    )

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

    result = operations.preview_file(
      file_path=temp_file.name,
      file_type="csv",
      import_type="local",
      sql_dialect="hive",
      has_header=True,
      field_separator=",",
      quote_char='"',
      record_separator="\n",
    )

    assert result == {
      "type": "csv",
      "columns": [],
      "preview_data": {},
    }

  def test_preview_invalid_file_path(self):
    with pytest.raises(ValueError, match="File path cannot be empty"):
      operations.preview_file(file_path="", file_type="csv", import_type="local", sql_dialect="hive", has_header=True)

  def test_preview_unsupported_file_type(self):
    with pytest.raises(ValueError, match="Unsupported file type: json"):
      operations.preview_file(
        file_path="/path/to/test.json",
        file_type="json",  # Unsupported type
        import_type="local",
        sql_dialect="hive",
        has_header=True,
      )

  def test_preview_unsupported_sql_dialect(self):
    with pytest.raises(ValueError, match="Unsupported SQL dialect: mysql"):
      operations.preview_file(
        file_path="/path/to/test.csv",
        file_type="csv",
        import_type="local",
        sql_dialect="mysql",  # Unsupported dialect
        has_header=True,
      )

  def test_preview_remote_file_no_fs(self):
    with pytest.raises(ValueError, match="File system object is required for remote import type"):
      operations.preview_file(
        file_path="s3a://bucket/user/test_user/test.csv",  # Remote file path
        file_type="csv",
        import_type="remote",  # Remote file but no fs provided
        sql_dialect="hive",
        has_header=True,
      )

  @patch("os.path.exists")
  def test_preview_nonexistent_local_file(self, mock_exists):
    mock_exists.return_value = False

    with pytest.raises(ValueError, match="Local file does not exist: /path/to/nonexistent.csv"):
      operations.preview_file(
        file_path="/path/to/nonexistent.csv", file_type="csv", import_type="local", sql_dialect="hive", has_header=True
      )

  def test_preview_trino_dialect_type_mapping(self, cleanup_temp_files):
    test_content = "string_col\nfoo\nbar"
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(test_content.encode("utf-8"))
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    result = operations.preview_file(
      file_path=temp_file.name,
      file_type="csv",
      import_type="local",
      sql_dialect="trino",  # Trino dialect for different type mapping
      has_header=True,
      field_separator=",",
    )

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

    result = operations.guess_file_header(file_path=temp_file.name, file_type="csv", import_type="local")

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

    result = operations.guess_file_header(file_path=temp_file.name, file_type="excel", import_type="local", sheet_name="Sheet1")

    assert result

  def test_guess_header_excel_no_sheet_name(self, cleanup_temp_files):
    test_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
    </workbook>"""

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    temp_file.write(test_content.encode("utf-8"))
    temp_file.close()

    cleanup_temp_files.append(temp_file.name)

    with pytest.raises(ValueError, match="Sheet name is required for Excel files"):
      operations.guess_file_header(
        file_path=temp_file.name,
        file_type="excel",
        import_type="local",
        # Missing sheet_name
      )

  def test_guess_header_invalid_path(self):
    with pytest.raises(ValueError, match="File path cannot be empty"):
      operations.guess_file_header(file_path="", file_type="csv", import_type="local")

  def test_guess_header_unsupported_file_type(self):
    with pytest.raises(ValueError, match="Unsupported file type: json"):
      operations.guess_file_header(
        file_path="/path/to/test.json",
        file_type="json",  # Unsupported type
        import_type="local",
      )

  def test_guess_header_nonexistent_local_file(self):
    with pytest.raises(ValueError, match="Local file does not exist"):
      operations.guess_file_header(file_path="/path/to/nonexistent.csv", file_type="csv", import_type="local")

  def test_guess_header_remote_file_no_fs(self):
    with pytest.raises(ValueError, match="File system object is required for remote import type"):
      operations.guess_file_header(
        file_path="hdfs:///path/to/test.csv",
        file_type="csv",
        import_type="remote",  # Remote but no fs provided
      )


class TestSqlTypeMapping:
  def test_get_sql_type_mapping_hive(self):
    mappings = operations.get_sql_type_mapping("hive")

    # Check some key mappings for Hive
    assert mappings["Int32"] == "INT"
    assert mappings["Utf8"] == "STRING"
    assert mappings["Float64"] == "DOUBLE"
    assert mappings["Boolean"] == "BOOLEAN"
    assert mappings["Decimal"] == "DECIMAL"

  def test_get_sql_type_mapping_trino(self):
    mappings = operations.get_sql_type_mapping("trino")

    # Check some key mappings for Trino that differ from Hive
    assert mappings["Int32"] == "INTEGER"
    assert mappings["Utf8"] == "VARCHAR"
    assert mappings["Binary"] == "VARBINARY"
    assert mappings["Float32"] == "REAL"
    assert mappings["Struct"] == "ROW"
    assert mappings["Object"] == "JSON"

  def test_get_sql_type_mapping_phoenix(self):
    mappings = operations.get_sql_type_mapping("phoenix")

    # Check some key mappings for Phoenix
    assert mappings["UInt32"] == "UNSIGNED_INT"
    assert mappings["Utf8"] == "VARCHAR"
    assert mappings["Time"] == "TIME"
    assert mappings["Struct"] == "STRING"  # Phoenix treats structs as strings
    assert mappings["Duration"] == "STRING"  # Phoenix treats durations as strings

  def test_get_sql_type_mapping_impala(self):
    result = operations.get_sql_type_mapping("impala")

    # Impala uses the base mappings, so check those
    assert result["Int32"] == "INT"
    assert result["Int64"] == "BIGINT"
    assert result["Float64"] == "DOUBLE"
    assert result["Utf8"] == "STRING"

  def test_get_sql_type_mapping_sparksql(self):
    result = operations.get_sql_type_mapping("sparksql")

    # SparkSQL uses the base mappings, so check those
    assert result["Int32"] == "INT"
    assert result["Int64"] == "BIGINT"
    assert result["Float64"] == "DOUBLE"
    assert result["Utf8"] == "STRING"

  def test_get_sql_type_mapping_unsupported_dialect(self):
    with pytest.raises(ValueError, match="Unsupported dialect: mysql"):
      operations.get_sql_type_mapping("mysql")

  def test_map_polars_dtype_to_sql_type(self):
    # Test with Hive dialect
    assert operations._map_polars_dtype_to_sql_type("hive", "Int64") == "BIGINT"
    assert operations._map_polars_dtype_to_sql_type("hive", "Float32") == "FLOAT"

    # Test with Trino dialect
    assert operations._map_polars_dtype_to_sql_type("trino", "Int64") == "BIGINT"
    assert operations._map_polars_dtype_to_sql_type("trino", "Float32") == "REAL"

    # Test unsupported type
    with pytest.raises(ValueError, match="No mapping for Polars dtype"):
      operations._map_polars_dtype_to_sql_type("hive", "NonExistentType")


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
