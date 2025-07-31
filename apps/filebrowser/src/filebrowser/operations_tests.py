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

from unittest.mock import Mock, patch

import pytest

from filebrowser.operations import rename_file_or_directory
from filebrowser.schemas import RenameSchema


class TestRenameFileOrDirectory:
  @patch("filebrowser.operations.get_user_fs")
  def test_successful_rename_absolute_path(self, mock_get_user_fs):
    mock_fs = Mock()
    mock_fs.exists.side_effect = [True, False]  # source exists, destination doesn't
    mock_fs.normpath.return_value = "/user/test/file_new.txt"
    mock_fs.rename.return_value = None
    mock_get_user_fs.return_value = mock_fs

    data = RenameSchema(source_path="/user/test/file.txt", destination_path="/user/test/file_new.txt")
    result = rename_file_or_directory(data, "test_user")

    assert result["message"] == "Renamed '/user/test/file.txt' to '/user/test/file_new.txt' successfully"
    mock_fs.rename.assert_called_once_with("/user/test/file.txt", "/user/test/file_new.txt")

  @patch("os.path.dirname")
  @patch("filebrowser.operations.get_user_fs")
  def test_successful_rename_relative_path(self, mock_get_user_fs, mock_dirname):
    mock_fs = Mock()
    mock_fs.exists.side_effect = [True, False]  # source exists, destination doesn't
    mock_fs.join.return_value = "/user/test/file_new.txt"
    mock_fs.normpath.return_value = "/user/test/file_new.txt"
    mock_fs.rename.return_value = None
    mock_get_user_fs.return_value = mock_fs
    mock_dirname.return_value = "/user/test"

    data = RenameSchema(source_path="/user/test/file.txt", destination_path="file_new.txt")
    result = rename_file_or_directory(data, "test_user")

    assert result["message"] == "Renamed '/user/test/file.txt' to '/user/test/file_new.txt' successfully"
    mock_fs.join.assert_called_once_with("/user/test", "file_new.txt")
    mock_fs.rename.assert_called_once_with("/user/test/file.txt", "/user/test/file_new.txt")

  def test_empty_username_raises_error(self):
    data = RenameSchema(source_path="/user/test/file.txt", destination_path="/user/test/file_new.txt")

    with pytest.raises(ValueError, match="Username is required and cannot be empty"):
      rename_file_or_directory(data, "")

    with pytest.raises(ValueError, match="Username is required and cannot be empty"):
      rename_file_or_directory(data, None)

  @patch("filebrowser.operations.get_user_fs")
  def test_source_path_not_exists(self, mock_get_user_fs):
    mock_fs = Mock()
    mock_fs.exists.return_value = False  # source doesn't exist
    mock_get_user_fs.return_value = mock_fs

    data = RenameSchema(source_path="/user/test/nonexistent.txt", destination_path="/user/test/new.txt")
    with pytest.raises(ValueError, match="Source path does not exist: /user/test/nonexistent.txt"):
      rename_file_or_directory(data, "test_user")

  @patch("filebrowser.operations.get_user_fs")
  def test_destination_path_already_exists(self, mock_get_user_fs):
    mock_fs = Mock()
    mock_fs.exists.side_effect = [True, True]  # both source and destination exist
    mock_fs.normpath.return_value = "/user/test/existing_file.txt"
    mock_get_user_fs.return_value = mock_fs

    data = RenameSchema(source_path="/user/test/file.txt", destination_path="/user/test/existing_file.txt")
    with pytest.raises(ValueError, match="Destination path already exists: /user/test/existing_file.txt"):
      rename_file_or_directory(data, "test_user")

  @patch("filebrowser.operations.get_user_fs")
  def test_filesystem_rename_error(self, mock_get_user_fs):
    mock_fs = Mock()
    mock_fs.exists.side_effect = [True, False]  # source exists, destination doesn't
    mock_fs.normpath.return_value = "/user/test/file_new.txt"
    mock_fs.rename.side_effect = Exception("Permission denied")
    mock_get_user_fs.return_value = mock_fs

    data = RenameSchema(source_path="/user/test/file.txt", destination_path="/user/test/file_new.txt")
    with pytest.raises(Exception, match="Failed to rename file: Permission denied"):
      rename_file_or_directory(data, "test_user")

  @patch("filebrowser.operations.get_user_fs")
  def test_rename_directory(self, mock_get_user_fs):
    mock_fs = Mock()
    mock_fs.exists.side_effect = [True, False]  # source exists, destination doesn't
    mock_fs.normpath.return_value = "/user/test/new_folder"
    mock_fs.rename.return_value = None
    mock_get_user_fs.return_value = mock_fs

    data = RenameSchema(source_path="/user/test/old_folder", destination_path="/user/test/new_folder")
    result = rename_file_or_directory(data, "test_user")

    assert result["message"] == "Renamed '/user/test/old_folder' to '/user/test/new_folder' successfully"
    mock_fs.rename.assert_called_once_with("/user/test/old_folder", "/user/test/new_folder")

  @patch("filebrowser.operations.get_user_fs")
  def test_move_to_different_directory(self, mock_get_user_fs):
    mock_fs = Mock()
    mock_fs.exists.side_effect = [True, False]  # source exists, destination doesn't
    mock_fs.normpath.return_value = "/user/test/archive/file.txt"
    mock_fs.rename.return_value = None
    mock_get_user_fs.return_value = mock_fs

    data = RenameSchema(source_path="/user/test/documents/file.txt", destination_path="/user/test/archive/file.txt")
    result = rename_file_or_directory(data, "test_user")

    assert result["message"] == "Renamed '/user/test/documents/file.txt' to '/user/test/archive/file.txt' successfully"
    mock_fs.rename.assert_called_once_with("/user/test/documents/file.txt", "/user/test/archive/file.txt")

  @patch("filebrowser.operations.get_user_fs")
  def test_rename_with_special_characters(self, mock_get_user_fs):
    mock_fs = Mock()
    mock_fs.exists.side_effect = [True, False]
    mock_fs.normpath.return_value = "/user/test/file (copy) 2024.txt"
    mock_fs.rename.return_value = None
    mock_get_user_fs.return_value = mock_fs

    data = RenameSchema(source_path="/user/test/file & document.txt", destination_path="/user/test/file (copy) 2024.txt")
    result = rename_file_or_directory(data, "test_user")

    assert "successfully" in result["message"]

  @patch("filebrowser.operations.get_user_fs")
  def test_rename_s3_paths(self, mock_get_user_fs):
    mock_fs = Mock()
    mock_fs.exists.side_effect = [True, False]
    mock_fs.normpath.return_value = "s3a://bucket/folder/file_new.txt"
    mock_fs.rename.return_value = None
    mock_get_user_fs.return_value = mock_fs

    data = RenameSchema(source_path="s3a://bucket/folder/file.txt", destination_path="s3a://bucket/folder/file_new.txt")
    result = rename_file_or_directory(data, "test_user")

    assert result["message"] == "Renamed 's3a://bucket/folder/file.txt' to 's3a://bucket/folder/file_new.txt' successfully"

  @patch("filebrowser.operations.get_user_fs")
  def test_relative_path_with_subdirectory(self, mock_get_user_fs):
    mock_fs = Mock()
    mock_fs.exists.side_effect = [True, False]
    mock_fs.normpath.return_value = "/user/test/subfolder/file.txt"
    mock_fs.rename.return_value = None
    mock_get_user_fs.return_value = mock_fs

    data = RenameSchema(source_path="/user/test/file.txt", destination_path="/user/test/subfolder/file.txt")
    result = rename_file_or_directory(data, "test_user")

    assert "successfully" in result["message"]
    mock_fs.rename.assert_called_once_with("/user/test/file.txt", "/user/test/subfolder/file.txt")

  @patch("filebrowser.operations.LOG.info")
  @patch("filebrowser.operations.get_user_fs")
  def test_logging_on_success(self, mock_get_user_fs, mock_log_info):
    mock_fs = Mock()
    mock_fs.exists.side_effect = [True, False]
    mock_fs.normpath.return_value = "/user/test/file_new.txt"
    mock_fs.rename.return_value = None
    mock_get_user_fs.return_value = mock_fs

    data = RenameSchema(source_path="/user/test/file.txt", destination_path="/user/test/file_new.txt")
    rename_file_or_directory(data, "test_user")

    mock_log_info.assert_called_once_with("User test_user is renaming /user/test/file.txt to /user/test/file_new.txt")

  @patch("filebrowser.operations.LOG.exception")
  @patch("filebrowser.operations.get_user_fs")
  def test_logging_on_error(self, mock_get_user_fs, mock_log_exception):
    mock_fs = Mock()
    mock_fs.exists.side_effect = [True, False]
    mock_fs.normpath.return_value = "/user/test/file_new.txt"
    mock_fs.rename.side_effect = Exception("Access denied")
    mock_get_user_fs.return_value = mock_fs

    data = RenameSchema(source_path="/user/test/file.txt", destination_path="/user/test/file_new.txt")
    with pytest.raises(Exception):
      rename_file_or_directory(data, "test_user")

    mock_log_exception.assert_called_once()
    assert "Error during rename operation" in mock_log_exception.call_args[0][0]

  @patch("filebrowser.operations.get_user_fs")
  def test_unicode_paths(self, mock_get_user_fs):
    mock_fs = Mock()
    mock_fs.exists.side_effect = [True, False]
    mock_fs.normpath.return_value = "/user/test/文档_新.txt"
    mock_fs.rename.return_value = None
    mock_get_user_fs.return_value = mock_fs

    data = RenameSchema(source_path="/user/test/文档.txt", destination_path="/user/test/文档_新.txt")
    result = rename_file_or_directory(data, "test_user")

    assert "successfully" in result["message"]
    mock_fs.rename.assert_called_once_with("/user/test/文档.txt", "/user/test/文档_新.txt")

  @patch("filebrowser.operations.get_user_fs")
  def test_normpath_called_on_destination(self, mock_get_user_fs):
    mock_fs = Mock()
    mock_fs.exists.side_effect = [True, False]
    mock_fs.normpath.return_value = "/user/test/file_new.txt"
    mock_fs.rename.return_value = None
    mock_get_user_fs.return_value = mock_fs

    data = RenameSchema(source_path="/user/test/file.txt", destination_path="/user/test/./file_new.txt")
    rename_file_or_directory(data, "test_user")

    mock_fs.normpath.assert_called_with("/user/test/./file_new.txt")
    mock_fs.rename.assert_called_once_with("/user/test/file.txt", "/user/test/file_new.txt")
