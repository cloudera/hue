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

from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIRequestFactory

from desktop.lib.importer import api


class TestLocalFileUploadAPI:
  @patch("desktop.lib.importer.api.LocalFileUploadSerializer")
  @patch("desktop.lib.importer.api.operations.local_file_upload")
  def test_local_file_upload_success(self, mock_local_file_upload, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_file = SimpleUploadedFile("test.csv", b"content")
    mock_schema = MagicMock()
    mock_schema.file = mock_file
    mock_schema.filename = "test.csv"
    mock_schema.filesize = 7

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_local_file_upload.return_value = {"file_path": "/tmp/user_12345_test.csv"}

    request = APIRequestFactory().post("importer/upload/file/")
    request.user = MagicMock(username="test_user")

    response = api.local_file_upload(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == {"file_path": "/tmp/user_12345_test.csv"}
    mock_local_file_upload.assert_called_once_with(mock_schema, "test_user")

  @patch("desktop.lib.importer.api.LocalFileUploadSerializer")
  def test_local_file_upload_invalid_data(self, mock_serializer_class):
    mock_serializer = MagicMock(is_valid=MagicMock(return_value=False), errors={"file": ["File too large"]})
    mock_serializer_class.return_value = mock_serializer

    request = APIRequestFactory().post("importer/upload/file/")
    request.user = MagicMock(username="test_user")

    response = api.local_file_upload(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"file": ["File too large"]}

  @patch("desktop.lib.importer.api.LocalFileUploadSerializer")
  @patch("desktop.lib.importer.api.operations.local_file_upload")
  def test_local_file_upload_operation_error(self, mock_local_file_upload, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_file = SimpleUploadedFile("test.csv", b"content")
    mock_schema = MagicMock()
    mock_schema.file = mock_file
    mock_schema.filename = "test.csv"
    mock_schema.filesize = 7

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_local_file_upload.side_effect = IOError("Operation error")

    request = APIRequestFactory().post("importer/upload/file/")
    request.user = MagicMock(username="test_user")

    response = api.local_file_upload(request)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Operation error"}


class TestGuessFileMetadataAPI:
  @patch("desktop.lib.importer.api.GuessFileMetadataSerializer")
  @patch("desktop.lib.importer.api.operations.guess_file_metadata")
  def test_guess_csv_file_metadata_success(self, mock_guess_file_metadata, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "/path/to/test.csv"
    mock_schema.import_type = "local"

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_guess_file_metadata.return_value = {"type": "csv", "field_separator": ",", "quote_char": '"', "record_separator": "\n"}

    request = APIRequestFactory().get("importer/file/guess_metadata/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.csv", "import_type": "local"}

    response = api.guess_file_metadata(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"type": "csv", "field_separator": ",", "quote_char": '"', "record_separator": "\n"}
    mock_guess_file_metadata.assert_called_once_with(data=mock_schema, username="test_user")

  @patch("desktop.lib.importer.api.GuessFileMetadataSerializer")
  @patch("desktop.lib.importer.api.operations.guess_file_metadata")
  def test_guess_excel_file_metadata_success(self, mock_guess_file_metadata, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "/path/to/test.xlsx"
    mock_schema.import_type = "local"

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_guess_file_metadata.return_value = {"type": "excel", "sheet_names": ["Sheet1", "Sheet2"]}

    request = APIRequestFactory().get("importer/file/guess_metadata/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.xlsx", "import_type": "local"}

    response = api.guess_file_metadata(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"type": "excel", "sheet_names": ["Sheet1", "Sheet2"]}
    mock_guess_file_metadata.assert_called_once_with(data=mock_schema, username="test_user")

  @patch("desktop.lib.importer.api.GuessFileMetadataSerializer")
  @patch("desktop.lib.importer.api.operations.guess_file_metadata")
  def test_guess_file_metadata_remote_csv_file(self, mock_guess_file_metadata, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "s3a://bucket/user/test_user/test.csv"
    mock_schema.import_type = "remote"

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_guess_file_metadata.return_value = {"type": "csv", "field_separator": ",", "quote_char": '"', "record_separator": "\n"}
    mock_fs = MagicMock()

    request = APIRequestFactory().get("importer/file/guess_metadata/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "s3a://bucket/user/test_user/test.csv", "import_type": "remote"}
    request.fs = mock_fs

    response = api.guess_file_metadata(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"type": "csv", "field_separator": ",", "quote_char": '"', "record_separator": "\n"}
    mock_guess_file_metadata.assert_called_once_with(data=mock_schema, username="test_user")

  @patch("desktop.lib.importer.api.GuessFileMetadataSerializer")
  def test_guess_file_metadata_invalid_data(self, mock_serializer_class):
    mock_serializer = MagicMock(is_valid=MagicMock(return_value=False), errors={"file_path": ["This field is required"]})
    mock_serializer_class.return_value = mock_serializer

    request = APIRequestFactory().get("importer/file/guess_metadata/")
    request.user = MagicMock(username="test_user")
    request.query_params = {}

    response = api.guess_file_metadata(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"file_path": ["This field is required"]}

  @patch("desktop.lib.importer.api.GuessFileMetadataSerializer")
  @patch("desktop.lib.importer.api.operations.guess_file_metadata")
  def test_guess_file_metadata_value_error(self, mock_guess_file_metadata, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "/path/to/test.csv"
    mock_schema.import_type = "local"

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_guess_file_metadata.side_effect = ValueError("File does not exist")

    request = APIRequestFactory().get("importer/file/guess_metadata/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.csv", "import_type": "local"}

    response = api.guess_file_metadata(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"error": "File does not exist"}

  @patch("desktop.lib.importer.api.GuessFileMetadataSerializer")
  @patch("desktop.lib.importer.api.operations.guess_file_metadata")
  def test_guess_file_metadata_operation_error(self, mock_guess_file_metadata, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "/path/to/test.csv"
    mock_schema.import_type = "local"

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_guess_file_metadata.side_effect = RuntimeError("Operation error")

    request = APIRequestFactory().get("importer/file/guess_metadata/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.csv", "import_type": "local"}

    response = api.guess_file_metadata(request)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Operation error"}


class TestPreviewFileAPI:
  @patch("desktop.lib.importer.api.PreviewFileSerializer")
  @patch("desktop.lib.importer.api.operations.preview_file")
  def test_preview_csv_file_success(self, mock_preview_file, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "/path/to/test.csv"
    mock_schema.file_type = "csv"
    mock_schema.import_type = "local"
    mock_schema.sql_dialect = "hive"
    mock_schema.has_header = True
    mock_schema.field_separator = ","
    mock_schema.quote_char = '"'
    mock_schema.record_separator = "\n"

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_preview_result = {
      "type": "csv",
      "columns": [{"name": "col1", "type": "INT"}, {"name": "col2", "type": "STRING"}],
      "preview_data": {"col1": [1, 2], "col2": ["a", "b"]},
    }
    mock_preview_file.return_value = mock_preview_result

    request = APIRequestFactory().get("importer/file/preview/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.csv", "file_type": "csv", "import_type": "local"}

    response = api.preview_file(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == mock_preview_result
    mock_preview_file.assert_called_once_with(data=mock_schema, username="test_user")

  @patch("desktop.lib.importer.api.PreviewFileSerializer")
  @patch("desktop.lib.importer.api.operations.preview_file")
  def test_preview_excel_file_success(self, mock_preview_file, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "/path/to/test.xlsx"
    mock_schema.file_type = "excel"
    mock_schema.import_type = "local"
    mock_schema.sql_dialect = "hive"
    mock_schema.has_header = True
    mock_schema.sheet_name = "Sheet1"

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_preview_result = {
      "type": "excel",
      "columns": [{"name": "col1", "type": "INT"}, {"name": "col2", "type": "STRING"}],
      "preview_data": {"col1": [1, 2], "col2": ["a", "b"]},
    }
    mock_preview_file.return_value = mock_preview_result

    request = APIRequestFactory().get("importer/file/preview/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.xlsx", "file_type": "excel", "import_type": "local"}

    response = api.preview_file(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == mock_preview_result
    mock_preview_file.assert_called_once_with(data=mock_schema, username="test_user")

  @patch("desktop.lib.importer.api.PreviewFileSerializer")
  @patch("desktop.lib.importer.api.operations.preview_file")
  def test_preview_tsv_file_success(self, mock_preview_file, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "/path/to/test.tsv"
    mock_schema.file_type = "tsv"
    mock_schema.import_type = "local"
    mock_schema.sql_dialect = "impala"
    mock_schema.has_header = True
    mock_schema.field_separator = "\t"
    mock_schema.quote_char = '"'
    mock_schema.record_separator = "\n"

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_preview_result = {
      "type": "tsv",
      "columns": [{"name": "id", "type": "INT"}, {"name": "name", "type": "STRING"}],
      "preview_data": {"id": [1, 2], "name": ["Product A", "Product B"]},
    }
    mock_preview_file.return_value = mock_preview_result

    request = APIRequestFactory().get("importer/file/preview/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.tsv", "file_type": "tsv", "import_type": "local"}

    response = api.preview_file(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == mock_preview_result
    mock_preview_file.assert_called_once_with(data=mock_schema, username="test_user")

  @patch("desktop.lib.importer.api.PreviewFileSerializer")
  @patch("desktop.lib.importer.api.operations.preview_file")
  def test_preview_remote_csv_file_success(self, mock_preview_file, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "s3a://bucket/user/test_user/test.csv"
    mock_schema.file_type = "csv"
    mock_schema.import_type = "remote"
    mock_schema.sql_dialect = "hive"
    mock_schema.has_header = True
    mock_schema.field_separator = ","
    mock_schema.quote_char = '"'
    mock_schema.record_separator = "\n"

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_preview_result = {
      "type": "csv",
      "columns": [{"name": "col1", "type": "INT"}, {"name": "col2", "type": "STRING"}],
      "preview_data": {"col1": [1, 2], "col2": ["a", "b"]},
    }

    mock_preview_file.return_value = mock_preview_result
    mock_fs = MagicMock()

    request = APIRequestFactory().get("importer/file/preview/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "s3a://bucket/user/test_user/test.csv", "file_type": "csv", "import_type": "remote"}
    request.fs = mock_fs

    response = api.preview_file(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == mock_preview_result
    mock_preview_file.assert_called_once_with(data=mock_schema, username="test_user")

  @patch("desktop.lib.importer.api.PreviewFileSerializer")
  def test_preview_file_invalid_data(self, mock_serializer_class):
    mock_serializer = MagicMock(is_valid=MagicMock(return_value=False), errors={"file_type": ["Not a valid choice."]})
    mock_serializer_class.return_value = mock_serializer

    request = APIRequestFactory().get("importer/file/preview/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.pdf", "file_type": "pdf", "import_type": "local"}

    response = api.preview_file(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"file_type": ["Not a valid choice."]}

  @patch("desktop.lib.importer.api.PreviewFileSerializer")
  def test_preview_file_missing_required_param(self, mock_serializer_class):
    mock_serializer = MagicMock(is_valid=MagicMock(return_value=False), errors={"sql_dialect": ["This field is required."]})
    mock_serializer_class.return_value = mock_serializer

    request = APIRequestFactory().get("importer/file/preview/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.csv", "file_type": "csv", "import_type": "local"}

    response = api.preview_file(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"sql_dialect": ["This field is required."]}

  @patch("desktop.lib.importer.api.PreviewFileSerializer")
  @patch("desktop.lib.importer.api.operations.preview_file")
  def test_preview_file_value_error(self, mock_preview_file, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "/path/to/test.csv"
    mock_schema.file_type = "csv"
    mock_schema.import_type = "local"
    mock_schema.sql_dialect = "hive"
    mock_schema.has_header = True
    mock_schema.field_separator = ","
    mock_schema.quote_char = '"'
    mock_schema.record_separator = "\n"

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_preview_file.side_effect = ValueError("File does not exist")

    request = APIRequestFactory().get("importer/file/preview/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.csv", "file_type": "csv", "import_type": "local"}

    response = api.preview_file(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"error": "File does not exist"}

  @patch("desktop.lib.importer.api.PreviewFileSerializer")
  @patch("desktop.lib.importer.api.operations.preview_file")
  def test_preview_file_operation_error(self, mock_preview_file, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "/path/to/test.csv"
    mock_schema.file_type = "csv"
    mock_schema.import_type = "local"
    mock_schema.sql_dialect = "hive"
    mock_schema.has_header = True
    mock_schema.field_separator = ","
    mock_schema.quote_char = '"'
    mock_schema.record_separator = "\n"

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_preview_file.side_effect = RuntimeError("Operation error")

    request = APIRequestFactory().get("importer/file/preview/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.csv", "file_type": "csv", "import_type": "local"}

    response = api.preview_file(request)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Operation error"}


class TestGuessFileHeaderAPI:
  @patch("desktop.lib.importer.api.GuessFileHeaderSerializer")
  @patch("desktop.lib.importer.api.operations.guess_file_header")
  def test_guess_csv_file_header_success(self, mock_guess_file_header, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "/path/to/test.csv"
    mock_schema.file_type = "csv"
    mock_schema.import_type = "local"
    mock_schema.sheet_name = None

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_guess_file_header.return_value = True

    request = APIRequestFactory().get("importer/file/guess_header/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.csv", "file_type": "csv", "import_type": "local"}

    response = api.guess_file_header(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"has_header": True}
    mock_guess_file_header.assert_called_once_with(data=mock_schema, username="test_user")

  @patch("desktop.lib.importer.api.GuessFileHeaderSerializer")
  @patch("desktop.lib.importer.api.operations.guess_file_header")
  def test_guess_excel_file_header_success(self, mock_guess_file_header, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "/path/to/test.xlsx"
    mock_schema.file_type = "excel"
    mock_schema.import_type = "local"
    mock_schema.sheet_name = "Sheet1"

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_guess_file_header.return_value = True

    request = APIRequestFactory().get("importer/file/guess_header/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.xlsx", "file_type": "excel", "import_type": "local", "sheet_name": "Sheet1"}

    response = api.guess_file_header(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"has_header": True}
    mock_guess_file_header.assert_called_once_with(data=mock_schema, username="test_user")

  @patch("desktop.lib.importer.api.GuessFileHeaderSerializer")
  @patch("desktop.lib.importer.api.operations.guess_file_header")
  def test_guess_remote_csv_file_header_success(self, mock_guess_file_header, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "s3a://bucket/user/test_user/test.csv"
    mock_schema.file_type = "csv"
    mock_schema.import_type = "remote"
    mock_schema.sheet_name = None

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_guess_file_header.return_value = True
    mock_fs = MagicMock()

    request = APIRequestFactory().get("importer/file/guess_header/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "s3a://bucket/user/test_user/test.csv", "file_type": "csv", "import_type": "remote"}
    request.fs = mock_fs

    response = api.guess_file_header(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"has_header": True}
    mock_guess_file_header.assert_called_once_with(data=mock_schema, username="test_user")

  @patch("desktop.lib.importer.api.GuessFileHeaderSerializer")
  @patch("desktop.lib.importer.api.operations.guess_file_header")
  def test_guess_remote_csv_file_header_success_false_value(self, mock_guess_file_header, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "s3a://bucket/user/test_user/test.csv"
    mock_schema.file_type = "csv"
    mock_schema.import_type = "remote"
    mock_schema.sheet_name = None

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_guess_file_header.return_value = False
    mock_fs = MagicMock()

    request = APIRequestFactory().get("importer/file/guess_header/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "s3a://bucket/user/test_user/test.csv", "file_type": "csv", "import_type": "remote"}
    request.fs = mock_fs

    response = api.guess_file_header(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"has_header": False}
    mock_guess_file_header.assert_called_once_with(data=mock_schema, username="test_user")

  @patch("desktop.lib.importer.api.GuessFileHeaderSerializer")
  def test_guess_file_header_invalid_data(self, mock_serializer_class):
    mock_serializer = MagicMock(is_valid=MagicMock(return_value=False), errors={"file_type": ["This field is required"]})
    mock_serializer_class.return_value = mock_serializer

    request = APIRequestFactory().get("importer/file/guess_header/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.csv", "import_type": "local"}

    response = api.guess_file_header(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"file_type": ["This field is required"]}

  @patch("desktop.lib.importer.api.GuessFileHeaderSerializer")
  @patch("desktop.lib.importer.api.operations.guess_file_header")
  def test_guess_file_header_value_error(self, mock_guess_file_header, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "/path/to/test.csv"
    mock_schema.file_type = "csv"
    mock_schema.import_type = "local"
    mock_schema.sheet_name = None

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_guess_file_header.side_effect = ValueError("File does not exist")

    request = APIRequestFactory().get("importer/file/guess_header/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.csv", "file_type": "csv", "import_type": "local"}

    response = api.guess_file_header(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"error": "File does not exist"}

  @patch("desktop.lib.importer.api.GuessFileHeaderSerializer")
  @patch("desktop.lib.importer.api.operations.guess_file_header")
  def test_guess_file_header_operation_error(self, mock_guess_file_header, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.file_path = "/path/to/test.csv"
    mock_schema.file_type = "csv"
    mock_schema.import_type = "local"
    mock_schema.sheet_name = None

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_guess_file_header.side_effect = RuntimeError("Operation error")

    request = APIRequestFactory().get("importer/file/guess_header/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"file_path": "/path/to/test.csv", "file_type": "csv", "import_type": "local"}

    response = api.guess_file_header(request)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Operation error"}


class TestSqlTypeMappingAPI:
  @patch("desktop.lib.importer.api.SqlTypeMapperSerializer")
  @patch("desktop.lib.importer.api.operations.get_sql_type_mapping")
  def test_get_sql_type_mapping_success(self, mock_get_sql_type_mapping, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.sql_dialect = "hive"

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_get_sql_type_mapping.return_value = [
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

    request = APIRequestFactory().get("importer/sql_type_mapping/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"sql_dialect": "hive"}

    response = api.get_sql_type_mapping(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == [
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
    mock_get_sql_type_mapping.assert_called_once_with(mock_schema)

  @patch("desktop.lib.importer.api.SqlTypeMapperSerializer")
  def test_get_sql_type_mapping_invalid_dialect(self, mock_serializer_class):
    mock_serializer = MagicMock(is_valid=MagicMock(return_value=False), errors={"sql_dialect": ["Not a valid choice."]})
    mock_serializer_class.return_value = mock_serializer

    request = APIRequestFactory().get("importer/sql_type_mapping/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"sql_dialect": "invalid_dialect"}

    response = api.get_sql_type_mapping(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"sql_dialect": ["Not a valid choice."]}

  @patch("desktop.lib.importer.api.SqlTypeMapperSerializer")
  @patch("desktop.lib.importer.api.operations.get_sql_type_mapping")
  def test_get_sql_type_mapping_value_error(self, mock_get_sql_type_mapping, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.sql_dialect = "hive"

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_get_sql_type_mapping.side_effect = ValueError("Unsupported dialect")

    request = APIRequestFactory().get("importer/sql_type_mapping/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"sql_dialect": "hive"}

    response = api.get_sql_type_mapping(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"error": "Unsupported dialect"}

  @patch("desktop.lib.importer.api.SqlTypeMapperSerializer")
  @patch("desktop.lib.importer.api.operations.get_sql_type_mapping")
  def test_get_sql_type_mapping_operation_error(self, mock_get_sql_type_mapping, mock_serializer_class):
    # Create a mock schema object that will be returned by the serializer
    mock_schema = MagicMock()
    mock_schema.sql_dialect = "hive"

    mock_serializer = MagicMock(is_valid=MagicMock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_get_sql_type_mapping.side_effect = RuntimeError("Operation error")

    request = APIRequestFactory().get("importer/sql_type_mapping/")
    request.user = MagicMock(username="test_user")
    request.query_params = {"sql_dialect": "hive"}

    response = api.get_sql_type_mapping(request)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Operation error"}
