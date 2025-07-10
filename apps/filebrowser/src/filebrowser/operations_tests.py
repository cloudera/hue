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

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from filebrowser.operations import _prepare_file_data, upload_file as operations_upload_file
from filebrowser.schemas import UploadFileSchema


class TestUploadFile:

  @patch("filebrowser.operations.get_user_filesystem")
  def test_upload_file_success(self, mock_get_fs):
    # Mock filesystem
    mock_fs = MagicMock()
    mock_fs.isdir.side_effect = [True, True]  # destination is dir, then check again
    mock_fs.join.return_value = "/tmp/test/test.csv"
    mock_fs.exists.side_effect = [True, False]  # destination exists, file doesn't exist
    mock_fs.upload_file.return_value = None
    mock_fs.stats.return_value = MagicMock(path="/tmp/test/test.csv", size=1024, mode=33188)
    mock_get_fs.return_value = mock_fs

    # Create test data
    file_data = BytesIO(b"test content")
    schema = UploadFileSchema(file=file_data, filename="test.csv", filesize=12, destination_path="/tmp/test", overwrite=False)

    with patch("filebrowser.operations._massage_stats") as mock_massage:
      mock_massage.return_value = {"path": "/tmp/test/test.csv", "size": 12, "type": "file"}

      result = operations_upload_file(data=schema, username="testuser")

    assert "uploaded_file_stats" in result
    assert result["uploaded_file_stats"]["path"] == "/tmp/test/test.csv"
    mock_fs.upload_file.assert_called_once()

  @patch("filebrowser.operations.get_user_filesystem")
  def test_upload_file_destination_not_found(self, mock_get_fs):
    mock_fs = MagicMock()
    mock_fs.isdir.return_value = False
    mock_fs.exists.return_value = False
    mock_get_fs.return_value = mock_fs

    schema = UploadFileSchema(
      file=BytesIO(b"content"), filename="test.csv", filesize=7, destination_path="/nonexistent/path", overwrite=False
    )

    with pytest.raises(ValueError, match="does not exist"):
      operations_upload_file(data=schema, username="testuser")

  @patch("filebrowser.operations.get_user_filesystem")
  def test_upload_file_already_exists(self, mock_get_fs):
    mock_fs = MagicMock()
    mock_fs.isdir.return_value = True
    mock_fs.join.return_value = "/tmp/test/test.csv"
    mock_fs.exists.side_effect = [True, True]  # destination exists, file exists
    mock_get_fs.return_value = mock_fs

    schema = UploadFileSchema(file=BytesIO(b"content"), filename="test.csv", filesize=7, destination_path="/tmp/test", overwrite=False)

    with pytest.raises(FileExistsError, match="already exists"):
      operations_upload_file(data=schema, username="testuser")

  @patch("filebrowser.operations.get_user_filesystem")
  def test_upload_file_overwrite_existing(self, mock_get_fs):
    mock_fs = MagicMock()
    mock_fs.isdir.return_value = True
    mock_fs.join.return_value = "/tmp/test/test.csv"
    mock_fs.exists.side_effect = [True, True]  # destination exists, file exists
    mock_fs.rmtree.return_value = None
    mock_fs.upload_file.return_value = None
    mock_fs.stats.return_value = MagicMock(path="/tmp/test/test.csv", size=7, mode=33188)
    mock_get_fs.return_value = mock_fs

    schema = UploadFileSchema(file=BytesIO(b"content"), filename="test.csv", filesize=7, destination_path="/tmp/test", overwrite=True)

    with patch("filebrowser.operations._massage_stats") as mock_massage:
      mock_massage.return_value = {"path": "/tmp/test/test.csv", "size": 7}
      result = operations_upload_file(data=schema, username="testuser")

    mock_fs.rmtree.assert_called_once_with("/tmp/test/test.csv")
    assert "uploaded_file_stats" in result

  @patch("filebrowser.operations.get_user_filesystem")
  def test_upload_file_permission_error(self, mock_get_fs):
    mock_fs = MagicMock()
    mock_fs.isdir.return_value = True
    mock_fs.join.return_value = "/tmp/test/test.csv"
    mock_fs.exists.side_effect = [True, False]
    mock_fs.upload_file.side_effect = Exception("Permission denied")
    mock_get_fs.return_value = mock_fs

    schema = UploadFileSchema(file=BytesIO(b"content"), filename="test.csv", filesize=7, destination_path="/tmp/test", overwrite=False)

    with pytest.raises(PermissionError, match="does not have permissions"):
      operations_upload_file(data=schema, username="testuser")

  def test_prepare_file_data_django_uploaded_file(self):
    # Mock Django UploadedFile with chunks
    mock_file = MagicMock()
    mock_file.chunks.return_value = [b"chunk1", b"chunk2", b"chunk3"]

    result = _prepare_file_data(mock_file)

    assert isinstance(result, BytesIO)
    assert result.read() == b"chunk1chunk2chunk3"

  def test_prepare_file_data_file_like_object(self):
    # File-like object with read() method
    file_obj = BytesIO(b"file content")

    result = _prepare_file_data(file_obj)

    assert isinstance(result, BytesIO)
    assert result.read() == b"file content"

  def test_prepare_file_data_bytes(self):

    result = _prepare_file_data(b"raw bytes")

    assert isinstance(result, BytesIO)
    assert result.read() == b"raw bytes"

  def test_prepare_file_data_string(self):
    result = _prepare_file_data("string content")

    assert isinstance(result, BytesIO)
    assert result.read() == b"string content"

  def test_prepare_file_data_unsupported_type(self):
    with pytest.raises(ValueError, match="Unsupported file object type"):
      _prepare_file_data(12345)  # Integer is not supported
