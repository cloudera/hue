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

import json
from io import BytesIO as string_io
from unittest.mock import MagicMock, Mock, patch

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseNotModified, HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from aws.s3.s3fs import S3ListAllBucketsException
from desktop.lib.exceptions_renderable import PopupException
from filebrowser.api import copy, download, get_all_filesystems, listdir_paged, mkdir, move, rename, touch, UploadFileAPI
from filebrowser.conf import REDIRECT_DOWNLOAD, SHOW_DOWNLOAD_BUTTON
from hadoop.fs.exceptions import WebHdfsException


class TestTouchAPI:
  def test_touch_success(self):
    request = Mock(
      method="POST",
      POST={"path": "s3a://test-bucket/test-user/", "name": "test_file.txt"},
      fs=Mock(
        isfile=Mock(return_value=False),
        join=Mock(return_value="s3a://test-bucket/test-user/test_file.txt"),
        create=Mock(),
      ),
    )
    response = touch(request)

    assert response.status_code == 201
    request.fs.create.assert_called_once_with("s3a://test-bucket/test-user/test_file.txt")

  def test_touch_file_exists(self):
    request = Mock(
      method="POST",
      POST={"path": "s3a://test-bucket/test-user/", "name": "test_file.txt"},
      fs=Mock(
        isfile=Mock(return_value=True),
        join=Mock(return_value="s3a://test-bucket/test-user/test_file.txt"),
      ),
    )
    response = touch(request)

    assert response.status_code == 409
    assert response.content.decode("utf-8") == "Error creating test_file.txt file: File already exists."

  def test_touch_invalid_name(self):
    request = Mock(
      method="POST",
      POST={"path": "s3a://test-bucket/test-user/", "name": "test/file.txt"},
      fs=Mock(),
    )
    response = touch(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Slashes are not allowed in filename. Please choose a different name."

  def test_touch_no_path(self):
    request = Mock(
      method="POST",
      POST={"name": "test_file.txt"},
      fs=Mock(),
    )
    response = touch(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Missing parameters: path and name are required."

  def test_touch_no_name(self):
    request = Mock(
      method="POST",
      POST={"path": "s3a://test-bucket/test-user/"},
      fs=Mock(),
    )
    response = touch(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Missing parameters: path and name are required."


class TestMkdirAPI:
  def test_mkdir_success(self):
    request = Mock(
      method="POST",
      POST={"path": "s3a://test-bucket/test-user/", "name": "new_dir"},
      fs=Mock(
        mkdir=Mock(),
        isdir=Mock(return_value=False),
        join=Mock(return_value="s3a://test-bucket/test-user/new_dir"),
      ),
    )
    response = mkdir(request)

    assert response.status_code == 201
    request.fs.mkdir.assert_called_once_with("s3a://test-bucket/test-user/new_dir")

  def test_mkdir_directory_exists(self):
    request = Mock(
      method="POST",
      POST={"path": "s3a://test-bucket/test-user/", "name": "new_dir"},
      fs=Mock(
        mkdir=Mock(),
        isdir=Mock(return_value=True),
        join=Mock(return_value="s3a://test-bucket/test-user/new_dir"),
      ),
    )
    response = mkdir(request)

    assert response.status_code == 409
    assert response.content.decode("utf-8") == "Error creating new_dir directory: Directory already exists."

  def test_mkdir_invalid_name(self):
    request = Mock(
      method="POST",
      POST={"path": "s3a://test-bucket/test-user/", "name": "new#dir"},
      fs=Mock(
        mkdir=Mock(),
        isdir=Mock(return_value=False),
        join=Mock(return_value="s3a://test-bucket/test-user/new#dir"),
      ),
    )
    response = mkdir(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Slashes or hashes are not allowed in directory name. Please choose a different name."

  def test_mkdir_no_path(self):
    request = Mock(
      method="POST",
      POST={"name": "new_dir"},
      fs=Mock(
        mkdir=Mock(),
        isdir=Mock(return_value=False),
        join=Mock(return_value="s3a://test-bucket/test-user/new_dir"),
      ),
    )
    response = mkdir(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Missing required parameters: path and name are required."

  def test_mkdir_no_name(self):
    request = Mock(
      method="POST",
      POST={"path": "s3a://test-bucket/test-user/"},
      fs=Mock(
        mkdir=Mock(),
        isdir=Mock(return_value=False),
        join=Mock(return_value="s3a://test-bucket/test-user/new_dir"),
      ),
    )
    response = mkdir(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Missing required parameters: path and name are required."


class TestRenameAPI:
  @patch("filebrowser.api.RenameSerializer")
  @patch("filebrowser.api.rename_file_or_directory")
  def test_rename_success(self, mock_rename_operation, mock_serializer_class):
    # Create mock schema and serializer
    mock_schema = {"source_path": "/user/test/file.txt", "destination_path": "/user/test/file_new.txt"}
    mock_serializer = Mock(is_valid=Mock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_rename_operation.return_value = {"message": "Renamed successfully"}

    request = APIRequestFactory().post("/storage/rename", data=mock_schema, format="json")
    request.user = Mock(username="test_user")

    response = rename(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"message": "Renamed successfully"}
    mock_rename_operation.assert_called_once()

  @patch("filebrowser.api.RenameSerializer")
  def test_rename_invalid_data(self, mock_serializer_class):
    # Mock invalid serializer
    mock_serializer = Mock(is_valid=Mock(return_value=False), errors={"source_path": ["This field is required."]})
    mock_serializer_class.return_value = mock_serializer

    request = APIRequestFactory().post("/storage/rename", data={}, format="json")
    request.user = Mock(username="test_user")

    response = rename(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"source_path": ["This field is required."]}

  @patch("filebrowser.api.RenameSerializer")
  @patch("filebrowser.api.rename_file_or_directory")
  def test_rename_value_error(self, mock_rename_operation, mock_serializer_class):
    mock_schema = {"source_path": "/user/test/file.txt", "destination_path": "/user/test/existing.txt"}
    mock_serializer = Mock(is_valid=Mock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_rename_operation.side_effect = ValueError("Destination path already exists")

    request = APIRequestFactory().post("/storage/rename", data=mock_schema, format="json")
    request.user = Mock(username="test_user")

    response = rename(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"error": "Destination path already exists"}

  @patch("filebrowser.api.RenameSerializer")
  @patch("filebrowser.api.rename_file_or_directory")
  def test_rename_general_exception(self, mock_rename_operation, mock_serializer_class):
    mock_schema = {"source_path": "/user/test/file.txt", "destination_path": "/user/test/file_new.txt"}
    mock_serializer = Mock(is_valid=Mock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_rename_operation.side_effect = Exception("Filesystem error")

    request = APIRequestFactory().post("/storage/rename", data=mock_schema, format="json")
    request.user = Mock(username="test_user")

    response = rename(request)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "An unexpected error occurred during rename operation"}

  @patch("filebrowser.api.RenameSerializer")
  @patch("filebrowser.api.rename_file_or_directory")
  def test_rename_relative_path(self, mock_rename_operation, mock_serializer_class):
    mock_schema = {"source_path": "/user/test/document.txt", "destination_path": "document_v2.txt"}
    mock_serializer = Mock(is_valid=Mock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_rename_operation.return_value = {"message": "Renamed '/user/test/document.txt' to '/user/test/document_v2.txt' successfully"}

    request = APIRequestFactory().post("/storage/rename", data=mock_schema, format="json")
    request.user = Mock(username="test_user")

    response = rename(request)

    assert response.status_code == status.HTTP_200_OK
    assert "successfully" in response.data["message"]

  @patch("filebrowser.api.RenameSerializer")
  @patch("filebrowser.api.rename_file_or_directory")
  def test_rename_s3_paths(self, mock_rename_operation, mock_serializer_class):
    mock_schema = {"source_path": "s3a://bucket/folder/file.txt", "destination_path": "s3a://bucket/folder/file_renamed.txt"}
    mock_serializer = Mock(is_valid=Mock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_rename_operation.return_value = {"message": "Renamed successfully"}

    request = APIRequestFactory().post("/storage/rename", data=mock_schema, format="json")
    request.user = Mock(username="test_user")

    response = rename(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"message": "Renamed successfully"}

  @patch("filebrowser.api.RenameSerializer")
  @patch("filebrowser.api.rename_file_or_directory")
  def test_rename_directory(self, mock_rename_operation, mock_serializer_class):
    mock_schema = {"source_path": "/user/test/old_folder", "destination_path": "/user/test/new_folder"}
    mock_serializer = Mock(is_valid=Mock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_rename_operation.return_value = {"message": "Renamed '/user/test/old_folder' to '/user/test/new_folder' successfully"}

    request = APIRequestFactory().post("/storage/rename", data=mock_schema, format="json")
    request.user = Mock(username="test_user")

    response = rename(request)

    assert response.status_code == status.HTTP_200_OK
    assert "old_folder" in response.data["message"]
    assert "new_folder" in response.data["message"]

  @patch("filebrowser.api.RenameSerializer")
  @patch("filebrowser.api.rename_file_or_directory")
  @patch("filebrowser.api.LOG.exception")
  def test_rename_logs_exception(self, mock_log_exception, mock_rename_operation, mock_serializer_class):
    mock_schema = {"source_path": "/user/test/file.txt", "destination_path": "/user/test/file_new.txt"}
    mock_serializer = Mock(is_valid=Mock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_rename_operation.side_effect = Exception("Test error")

    request = APIRequestFactory().post("/storage/rename", data=mock_schema, format="json")
    request.user = Mock(username="test_user")

    response = rename(request)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    mock_log_exception.assert_called_once()
    assert "Error renaming file" in mock_log_exception.call_args[0][0]

  @patch("filebrowser.api.RenameSerializer")
  def test_rename_validation_errors(self, mock_serializer_class):
    # Mock serializer with multiple validation errors
    mock_serializer = Mock(
      is_valid=Mock(return_value=False),
      errors={"source_path": ["Path cannot be empty"], "destination_path": ["Path traversal patterns are not allowed"]},
    )
    mock_serializer_class.return_value = mock_serializer

    request = APIRequestFactory().post("/storage/rename", data={"source_path": "", "destination_path": "../etc"}, format="json")
    request.user = Mock(username="test_user")

    response = rename(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "source_path" in response.data
    assert "destination_path" in response.data

  @patch("filebrowser.api.RenameSerializer")
  @patch("filebrowser.api.rename_file_or_directory")
  def test_rename_unicode_paths(self, mock_rename_operation, mock_serializer_class):
    mock_schema = {"source_path": "/user/test/文档.txt", "destination_path": "/user/test/文档_新.txt"}
    mock_serializer = Mock(is_valid=Mock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_rename_operation.return_value = {"message": "Renamed '/user/test/文档.txt' to '/user/test/文档_新.txt' successfully"}

    request = APIRequestFactory().post("/storage/rename", data=mock_schema, format="json")
    request.user = Mock(username="test_user")

    response = rename(request)

    assert response.status_code == status.HTTP_200_OK
    assert "文档.txt" in response.data["message"]
    assert "文档_新.txt" in response.data["message"]

  @patch("filebrowser.api.RenameSerializer")
  @patch("filebrowser.api.rename_file_or_directory")
  def test_rename_special_characters(self, mock_rename_operation, mock_serializer_class):
    mock_schema = {
      "source_path": "/user/test/file with spaces & (special).txt",
      "destination_path": "/user/test/file_with_spaces_and_special.txt",
    }
    mock_serializer = Mock(is_valid=Mock(return_value=True), validated_data=mock_schema)
    mock_serializer_class.return_value = mock_serializer

    mock_rename_operation.return_value = {"message": "Renamed successfully"}

    request = APIRequestFactory().post("/storage/rename", data=mock_schema, format="json")
    request.user = Mock(username="test_user")

    response = rename(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"message": "Renamed successfully"}

  @patch("filebrowser.api.RenameSerializer")
  @patch("filebrowser.api.rename_file_or_directory")
  @patch("filebrowser.api.RenameSchema")
  def test_rename_schema_creation(self, mock_rename_schema_class, mock_rename_operation, mock_serializer_class):
    mock_schema_data = {"source_path": "/user/test/file.txt", "destination_path": "/user/test/file_new.txt"}
    mock_serializer = Mock(is_valid=Mock(return_value=True), validated_data=mock_schema_data)
    mock_serializer_class.return_value = mock_serializer

    mock_schema_instance = Mock()
    mock_rename_schema_class.return_value = mock_schema_instance

    mock_rename_operation.return_value = {"message": "Success"}

    request = APIRequestFactory().post("/storage/rename", data=mock_schema_data, format="json")
    request.user = Mock(username="test_user")

    rename(request)

    # Verify RenameSchema was created with the validated data
    mock_rename_schema_class.assert_called_once_with(**mock_schema_data)
    # Verify rename operation was called with the schema instance
    mock_rename_operation.assert_called_once_with(data=mock_schema_instance, username="test_user")


class TestMoveAPI:
  def test_move_success(self):
    request = Mock(
      method="POST",
      POST={"source_path": "s3a://test-bucket/test-user/src_dir/source.txt", "destination_path": "s3a://test-bucket/test-user/dst_dir"},
      fs=Mock(
        exists=Mock(side_effect=[True, False]),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value="s3a://test-bucket/test-user/src_dir"),
        join=Mock(return_value="s3a://test-bucket/test-user/dst_dir/source.txt"),
        normpath=Mock(
          side_effect=[
            "s3a://test-bucket/test-user/src_dir/source.txt",
            "s3a://test-bucket/test-user/dst_dir",
            "s3a://test-bucket/test-user/dst_dir",
          ]
        ),
        rename=Mock(),
      ),
    )
    response = move(request)

    assert response.status_code == 200
    request.fs.rename.assert_called_once_with("s3a://test-bucket/test-user/src_dir/source.txt", "s3a://test-bucket/test-user/dst_dir")

  def test_move_no_source_path(self):
    request = Mock(
      method="POST",
      POST={"destination_path": "s3a://test-bucket/test-user/dst_dir"},
      fs=Mock(),
    )
    response = move(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Missing required parameters: source_path and destination_path are required."

  def test_move_no_destination_path(self):
    request = Mock(
      method="POST",
      POST={"source_path": "s3a://test-bucket/test-user/src_dir/source.txt"},
      fs=Mock(),
    )
    response = move(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Missing required parameters: source_path and destination_path are required."

  def test_move_identical_paths(self):
    request = Mock(
      method="POST",
      POST={
        "source_path": "s3a://test-bucket/test-user/src_dir/source.txt",
        "destination_path": "s3a://test-bucket/test-user/src_dir/source.txt",
      },
      fs=Mock(
        normpath=Mock(side_effect=["s3a://test-bucket/test-user/src_dir/source.txt", "s3a://test-bucket/test-user/src_dir/source.txt"]),
      ),
    )
    response = move(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Source and destination paths must be different."

  def test_move_source_path_does_not_exist(self):
    request = Mock(
      method="POST",
      POST={
        "source_path": "s3a://test-bucket/test-user/src_dir/source.txt",
        "destination_path": "s3a://test-bucket/test-user/dst_dir",
      },
      fs=Mock(
        exists=Mock(return_value=False),
        normpath=Mock(side_effect=["s3a://test-bucket/test-user/src_dir/source.txt", "s3a://test-bucket/test-user/dst_dir"]),
      ),
    )
    response = move(request)

    assert response.status_code == 404
    assert response.content.decode("utf-8") == "Source file or folder does not exist."

  def test_move_destination_not_a_directory(self):
    request = Mock(
      method="POST",
      POST={
        "source_path": "s3a://test-bucket/test-user/src_dir/source.txt",
        "destination_path": "s3a://test-bucket/test-user/dst_dir",
      },
      fs=Mock(
        exists=Mock(return_value=True),
        isdir=Mock(return_value=False),
        normpath=Mock(side_effect=["s3a://test-bucket/test-user/src_dir/source.txt", "s3a://test-bucket/test-user/dst_dir"]),
      ),
    )
    response = move(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Destination path must be a directory."

  def test_move_destination_is_parent_of_source(self):
    request = Mock(
      method="POST",
      POST={
        "source_path": "s3a://test-bucket/test-user/src_dir/source.txt",
        "destination_path": "s3a://test-bucket/test-user/src_dir",
      },
      fs=Mock(
        exists=Mock(return_value=True),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value="s3a://test-bucket/test-user/src_dir"),
        normpath=Mock(
          side_effect=[
            "s3a://test-bucket/test-user/src_dir/source.txt",
            "s3a://test-bucket/test-user/src_dir",
            "s3a://test-bucket/test-user/src_dir",
          ]
        ),
      ),
    )
    response = move(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Destination cannot be the parent directory of source."

  def test_move_file_already_exists_at_destination(self):
    request = Mock(
      method="POST",
      POST={
        "source_path": "s3a://test-bucket/test-user/src_dir/source.txt",
        "destination_path": "s3a://test-bucket/test-user/dst_dir",
      },
      fs=Mock(
        exists=Mock(side_effect=[True, True]),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value="s3a://test-bucket/test-user/src_dir"),
        join=Mock(return_value="s3a://test-bucket/test-user/dst_dir/source.txt"),
        normpath=Mock(
          side_effect=[
            "s3a://test-bucket/test-user/src_dir/source.txt",
            "s3a://test-bucket/test-user/dst_dir",
            "s3a://test-bucket/test-user/dst_dir",
          ]
        ),
      ),
    )
    response = move(request)

    assert response.status_code == 409
    assert response.content.decode("utf-8") == "File or folder already exists at destination path."


class TestGetFilesystemsAPI:
  def test_get_all_filesystems_without_hdfs(self):
    with patch("filebrowser.api.fsmanager.get_filesystems") as get_filesystems:
      with patch("filebrowser.api.get_s3_home_directory") as get_s3_home_directory:
        with patch("filebrowser.api._is_hdfs_superuser") as _is_hdfs_superuser:
          get_filesystems.return_value = ["s3a", "ofs"]
          get_s3_home_directory.return_value = "s3a://test-bucket/test-user-home-dir/"
          _is_hdfs_superuser.return_value = False
          request = Mock(
            method="GET",
            user=Mock(),
          )

          response = get_all_filesystems(request)
          response_data = json.loads(response.content)

          assert response.status_code == 200
          assert response_data == [
            {"name": "s3a", "user_home_directory": "s3a://test-bucket/test-user-home-dir/", "config": {}},
            {"name": "ofs", "user_home_directory": "ofs://", "config": {}},
          ]

  def test_get_all_filesystems_success(self):
    with patch("filebrowser.api.fsmanager.get_filesystems") as get_filesystems:
      with patch("filebrowser.api.get_s3_home_directory") as get_s3_home_directory:
        with patch("filebrowser.api._is_hdfs_superuser") as _is_hdfs_superuser:
          with patch("filebrowser.api.User"):
            with patch("filebrowser.api.Group"):
              get_filesystems.return_value = ["hdfs", "s3a", "ofs"]
              get_s3_home_directory.return_value = "s3a://test-bucket/test-user-home-dir/"
              _is_hdfs_superuser.return_value = False
              request = Mock(
                method="GET",
                user=Mock(get_home_directory=Mock(return_value="/user/test-user")),
                fs=Mock(
                  superuser="test-user",
                  supergroup="test-supergroup",
                ),
              )

              response = get_all_filesystems(request)
              response_data = json.loads(response.content)

              assert response.status_code == 200
              assert response_data == [
                {
                  "name": "hdfs",
                  "user_home_directory": "/user/test-user",
                  "config": {
                    "is_trash_enabled": False,
                    "is_hdfs_superuser": False,
                    "groups": [],
                    "users": [],
                    "superuser": "test-user",
                    "supergroup": "test-supergroup",
                  },
                },
                {"name": "s3a", "user_home_directory": "s3a://test-bucket/test-user-home-dir/", "config": {}},
                {"name": "ofs", "user_home_directory": "ofs://", "config": {}},
              ]


class TestCopyAPI:
  def test_copy_normal_success(self):
    request = Mock(
      method="POST",
      POST={"source_path": "s3a://test-bucket/test-user/src_dir/source.txt", "destination_path": "s3a://test-bucket/test-user/dst_dir"},
      fs=Mock(
        exists=Mock(side_effect=[True, False]),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value="s3a://test-bucket/test-user/src_dir"),
        join=Mock(return_value="s3a://test-bucket/test-user/dst_dir/source.txt"),
        normpath=Mock(
          side_effect=[
            "s3a://test-bucket/test-user/src_dir/source.txt",
            "s3a://test-bucket/test-user/dst_dir",
            "s3a://test-bucket/test-user/dst_dir",
          ]
        ),
        copy=Mock(),
        user=Mock(),
      ),
    )
    response = copy(request)

    assert response.status_code == 200
    request.fs.copy.assert_called_once_with(
      "s3a://test-bucket/test-user/src_dir/source.txt", "s3a://test-bucket/test-user/dst_dir", recursive=True, owner=request.user
    )

  def test_copy_ofs_success(self):
    request = Mock(
      method="POST",
      POST={
        "source_path": "ofs://test_vol/test-bucket/test-user/src_dir/source.txt",
        "destination_path": "ofs://test_vol/test-bucket/test-user/dst_dir",
      },
      fs=Mock(
        exists=Mock(side_effect=[True, False]),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value="ofs://test_vol/test-bucket/test-user/src_dir"),
        join=Mock(return_value="ofs://test_vol/test-bucket/test-user/dst_dir/source.txt"),
        normpath=Mock(
          side_effect=[
            "ofs://test_vol/test-bucket/test-user/src_dir/source.txt",
            "ofs://test_vol/test-bucket/test-user/dst_dir",
            "ofs://test_vol/test-bucket/test-user/dst_dir",
          ]
        ),
        copy=Mock(return_value=""),
        user=Mock(),
      ),
    )
    response = copy(request)

    assert response.status_code == 200
    request.fs.copy.assert_called_once_with(
      "ofs://test_vol/test-bucket/test-user/src_dir/source.txt",
      "ofs://test_vol/test-bucket/test-user/dst_dir",
      recursive=True,
      owner=request.user,
    )

  def test_copy_ofs_skip_files_error(self):
    request = Mock(
      method="POST",
      POST={
        "source_path": "ofs://test_vol/test-bucket/test-user/src_dir/source.txt",
        "destination_path": "ofs://test_vol/test-bucket/test-user/dst_dir",
      },
      fs=Mock(
        exists=Mock(side_effect=[True, False]),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value="ofs://test_vol/test-bucket/test-user/src_dir"),
        join=Mock(return_value="ofs://test_vol/test-bucket/test-user/dst_dir/source.txt"),
        normpath=Mock(
          side_effect=[
            "ofs://test_vol/test-bucket/test-user/src_dir/source.txt",
            "ofs://test_vol/test-bucket/test-user/dst_dir",
            "ofs://test_vol/test-bucket/test-user/dst_dir",
          ]
        ),
        copy=Mock(return_value=("ofs://test_vol/test-bucket/test-user/src_dir/source.txt")),
        user=Mock(),
      ),
    )
    response = copy(request)

    assert response.status_code == 500
    assert json.loads(response.content) == {"skipped_files": "ofs://test_vol/test-bucket/test-user/src_dir/source.txt"}
    request.fs.copy.assert_called_once_with(
      "ofs://test_vol/test-bucket/test-user/src_dir/source.txt",
      "ofs://test_vol/test-bucket/test-user/dst_dir",
      recursive=True,
      owner=request.user,
    )

  def test_copy_no_source_path(self):
    request = Mock(
      method="POST",
      POST={"destination_path": "s3a://test-bucket/test-user/dst_dir"},
      fs=Mock(),
    )
    response = copy(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Missing required parameters: source_path and destination_path are required."

  def test_copy_no_destination_path(self):
    request = Mock(
      method="POST",
      POST={"source_path": "s3a://test-bucket/test-user/src_dir/source.txt"},
      fs=Mock(),
    )
    response = copy(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Missing required parameters: source_path and destination_path are required."

  def test_copy_identical_paths(self):
    request = Mock(
      method="POST",
      POST={
        "source_path": "s3a://test-bucket/test-user/src_dir/source.txt",
        "destination_path": "s3a://test-bucket/test-user/src_dir/source.txt",
      },
      fs=Mock(
        normpath=Mock(side_effect=["s3a://test-bucket/test-user/src_dir/source.txt", "s3a://test-bucket/test-user/src_dir/source.txt"]),
      ),
    )
    response = copy(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Source and destination paths must be different."

  def test_copy_source_path_does_not_exist(self):
    request = Mock(
      method="POST",
      POST={
        "source_path": "s3a://test-bucket/test-user/src_dir/source.txt",
        "destination_path": "s3a://test-bucket/test-user/dst_dir",
      },
      fs=Mock(
        exists=Mock(return_value=False),
        normpath=Mock(side_effect=["s3a://test-bucket/test-user/src_dir/source.txt", "s3a://test-bucket/test-user/dst_dir"]),
      ),
    )
    response = copy(request)

    assert response.status_code == 404
    assert response.content.decode("utf-8") == "Source file or folder does not exist."

  def test_copy_destination_not_a_directory(self):
    request = Mock(
      method="POST",
      POST={
        "source_path": "s3a://test-bucket/test-user/src_dir/source.txt",
        "destination_path": "s3a://test-bucket/test-user/dst_dir",
      },
      fs=Mock(
        exists=Mock(return_value=True),
        isdir=Mock(return_value=False),
        normpath=Mock(side_effect=["s3a://test-bucket/test-user/src_dir/source.txt", "s3a://test-bucket/test-user/dst_dir"]),
      ),
    )
    response = copy(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Destination path must be a directory."

  def test_copy_destination_is_parent_of_source(self):
    request = Mock(
      method="POST",
      POST={
        "source_path": "s3a://test-bucket/test-user/src_dir/source.txt",
        "destination_path": "s3a://test-bucket/test-user/src_dir",
      },
      fs=Mock(
        exists=Mock(return_value=True),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value="s3a://test-bucket/test-user/src_dir"),
        normpath=Mock(
          side_effect=[
            "s3a://test-bucket/test-user/src_dir/source.txt",
            "s3a://test-bucket/test-user/src_dir",
            "s3a://test-bucket/test-user/src_dir",
          ]
        ),
      ),
    )
    response = copy(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Destination cannot be the parent directory of source."

  def test_copy_file_already_exists_at_destination(self):
    request = Mock(
      method="POST",
      POST={
        "source_path": "s3a://test-bucket/test-user/src_dir/source.txt",
        "destination_path": "s3a://test-bucket/test-user/dst_dir",
      },
      fs=Mock(
        exists=Mock(side_effect=[True, True]),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value="s3a://test-bucket/test-user/src_dir"),
        join=Mock(return_value="s3a://test-bucket/test-user/dst_dir/source.txt"),
        normpath=Mock(
          side_effect=[
            "s3a://test-bucket/test-user/src_dir/source.txt",
            "s3a://test-bucket/test-user/dst_dir",
            "s3a://test-bucket/test-user/dst_dir",
          ]
        ),
      ),
    )
    response = copy(request)

    assert response.status_code == 409
    assert response.content.decode("utf-8") == "File or folder already exists at destination path."


class TestListAPI:
  def _create_mock_file_stats(self, name, path, size, user, group):
    mock_stats = MagicMock()
    mock_stats.path = path
    mock_stats.name = name
    mock_stats.size = size
    mock_stats.atime = 0
    mock_stats.mtime = 0
    mock_stats.type = "file"
    mock_stats.user = user
    mock_stats.group = group
    mock_stats.mode = 33188
    mock_stats.to_json_dict = Mock(
      return_value={
        "path": path,
        "aclBit": False,
        "size": size,
        "atime": 0,
        "mtime": 0,
        "type": "file",
        "user": user,
        "group": group,
        "mode": 33188,
      }
    )
    return mock_stats

  def _create_mock_paginator(self, all_stats):
    mock_page = MagicMock()
    mock_page.object_list = all_stats
    mock_page.has_next.return_value = False
    mock_page.has_previous.return_value = False
    mock_page.number = 1

    mock_paginator = MagicMock()
    mock_paginator.page.return_value = mock_page
    mock_paginator.per_page = 30
    mock_paginator.count = 2
    mock_paginator.num_pages = 1

    return mock_paginator

  def test_listdir_paged_success(self):
    with patch("filebrowser.api.is_admin") as is_admin:
      is_admin.return_value = False

      file1_stats = self._create_mock_file_stats(
        name="file1.txt", path="s3a://test-bucket/test-user/test-dir/file1.txt", size=100, user="user1", group="group1"
      )
      file2_stats = self._create_mock_file_stats(
        name="file2.txt", path="s3a://test-bucket/test-user/test-dir/file2.txt", size=200, user="user2", group="group2"
      )

      all_stats = [file2_stats, file1_stats]

      request = Mock(
        method="GET",
        GET={"pagenum": "1", "pagesize": "30", "path": "s3a://test-bucket/test-user/test-dir", "sortby": "name", "descending": "False"},
        user=Mock(has_hue_permission=Mock(return_value=False)),
        fs=Mock(
          listdir_stats=Mock(return_value=all_stats),
          do_as_user=Mock(return_value=all_stats),
          isdir=Mock(return_value=True),
          normpath=Mock(side_effect=["s3a://test-bucket/test-user/test-dir/file1.txt", "s3a://test-bucket/test-user/test-dir/file2.txt"]),
        ),
      )

      mock_paginator = self._create_mock_paginator(all_stats)

      with patch("filebrowser.api.Paginator", return_value=mock_paginator) as mock_paginator:
        response = listdir_paged(request)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data == {
          "files": [
            {
              "path": "s3a://test-bucket/test-user/test-dir/file1.txt",
              "aclBit": False,
              "size": 200,
              "atime": 0,
              "mtime": 0,
              "type": "file",
              "user": "user2",
              "group": "group2",
              "mode": 33188,
              "rwx": "-rw-r--r--+",
            },
            {
              "path": "s3a://test-bucket/test-user/test-dir/file2.txt",
              "aclBit": False,
              "size": 100,
              "atime": 0,
              "mtime": 0,
              "type": "file",
              "user": "user1",
              "group": "group1",
              "mode": 33188,
              "rwx": "-rw-r--r--+",
            },
          ],
          "page": {"page_number": 1, "page_size": 30, "total_pages": 1, "total_size": 2},
        }

        # Assert correct sorting
        assert response_data["files"][0]["path"] == "s3a://test-bucket/test-user/test-dir/file1.txt"
        assert response_data["files"][1]["path"] == "s3a://test-bucket/test-user/test-dir/file2.txt"

  def test_listdir_paged_sorting_by_size_descending(self):
    with patch("filebrowser.api.is_admin") as is_admin:
      is_admin.return_value = False

      file1_stats = self._create_mock_file_stats(
        name="file1.txt", path="s3a://test-bucket/test-user/test-dir/file1.txt", size=100, user="user1", group="group1"
      )
      file2_stats = self._create_mock_file_stats(
        name="file2.txt", path="s3a://test-bucket/test-user/test-dir/file2.txt", size=200, user="user2", group="group2"
      )
      file3_stats = self._create_mock_file_stats(
        name="file3.txt", path="s3a://test-bucket/test-user/test-dir/file3.txt", size=300, user="user3", group="group3"
      )
      file4_stats = self._create_mock_file_stats(
        name="file4.txt", path="s3a://test-bucket/test-user/test-dir/file4.txt", size=400, user="user4", group="group4"
      )

      all_stats = [file1_stats, file2_stats, file3_stats, file4_stats]

      request = Mock(
        method="GET",
        GET={
          "pagenum": "1",
          "pagesize": "30",
          "path": "s3a://test-bucket/test-user/test-dir",
          "sortby": "name",
          "descending": "True",
        },
        user=Mock(has_hue_permission=Mock(return_value=False)),
        fs=Mock(
          listdir_stats=Mock(side_effect=[all_stats, all_stats]),
          do_as_user=Mock(return_value=all_stats),
          isdir=Mock(return_value=True),
          normpath=Mock(
            side_effect=[
              "s3a://test-bucket/test-user/test-dir/file1.txt",
              "s3a://test-bucket/test-user/test-dir/file2.txt",
              "s3a://test-bucket/test-user/test-dir/file3.txt",
              "s3a://test-bucket/test-user/test-dir/file4.txt",
            ]
          ),
        ),
      )

      mock_paginator = self._create_mock_paginator(sorted(all_stats, key=lambda x: x.size, reverse=True))

      with patch("filebrowser.api.Paginator", return_value=mock_paginator) as mock_paginator:
        response = listdir_paged(request)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert "files" in response_data
        assert len(response_data["files"]) == 4

        # Assert correct sorting
        assert response_data["files"][0]["size"] == 400
        assert response_data["files"][1]["size"] == 300
        assert response_data["files"][2]["size"] == 200
        assert response_data["files"][3]["size"] == 100

  def test_listdir_paged_invalid_path(self):
    request = Mock(
      method="GET",
      GET={"pagenum": "1", "pagesize": "30", "path": "s3a://test-bucket/test-user/test-dir/test-file"},
      fs=Mock(
        isdir=Mock(return_value=False),
      ),
    )

    response = listdir_paged(request)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "s3a://test-bucket/test-user/test-dir/test-file is not a directory."

  def test_listdir_paged_error_while_listing_bucket(self):
    with patch("filebrowser.api.is_admin") as is_admin:
      is_admin.return_value = False

      request = Mock(
        method="GET",
        GET={"pagenum": "1", "pagesize": "30", "path": "s3a://test-bucket/"},
        fs=Mock(
          isdir=Mock(return_value=True),
          listdir_stats=Mock(side_effect=S3ListAllBucketsException("Failed to list all buckets")),
          do_as_user=Mock(side_effect=S3ListAllBucketsException("Failed to list all buckets")),
        ),
      )

      response = listdir_paged(request)

      assert response.status_code == 403
      assert response.content.decode("utf-8") == "Bucket listing is not allowed: Failed to list all buckets"


class TestDownloadAPI:
  def test_download_not_allowed(self):
    request = Mock(
      method="GET",
      GET={"path": "s3a://test-bucket/test-user/test_file.txt"},
      fs=Mock(),
    )

    reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(False)
    try:
      response = download(request)

      assert response.status_code == 403
      assert response.content.decode("utf-8") == "Download operation is not allowed."
    finally:
      reset()

  def test_download_file_not_exists(self):
    request = Mock(
      method="GET",
      GET={"path": "s3a://test-bucket/test-user/test_file.txt"},
      fs=Mock(
        exists=Mock(return_value=False),
      ),
    )

    reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(True)
    try:
      response = download(request)

      assert response.status_code == 404
      assert response.content.decode("utf-8") == "File does not exist: s3a://test-bucket/test-user/test_file.txt"
    finally:
      reset()

  def test_download_not_a_file(self):
    request = Mock(
      method="GET",
      GET={"path": "s3a://test-bucket/test-user/test_dir"},
      fs=Mock(
        exists=Mock(return_value=True),
        isfile=Mock(return_value=False),
      ),
    )

    reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(True)
    try:
      response = download(request)

      assert response.status_code == 400
      assert response.content.decode("utf-8") == "s3a://test-bucket/test-user/test_dir is not a file."
    finally:
      reset()

  def test_download_success(self):
    with patch("filebrowser.api.mimetypes.guess_type") as guess_type:
      with patch("filebrowser.api.was_modified_since") as was_modified_since:
        guess_type.return_value = ("text/plain", None)
        was_modified_since.return_value = True

        request = Mock(
          method="GET",
          GET={"path": "s3a://test-bucket/test-user/test_file.txt"},
          fs=Mock(
            exists=Mock(return_value=True),
            isfile=Mock(return_value=True),
            read=Mock(),
            open=Mock(return_value=string_io(b"Hello, World!")),
            stats=Mock(return_value={"mtime": 1731527620, "size": 1024, "name": "test_file.txt"}),
          ),
        )

        reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(True)
        try:
          response = download(request)
          stream_response_content = b"".join(response.streaming_content)

          assert isinstance(response, StreamingHttpResponse)
          assert response.status_code == 200
          assert stream_response_content.decode("utf-8") == "Hello, World!"
          assert response["Content-Disposition"] == "attachment; filename*=UTF-8''test_file.txt"
        finally:
          reset()

  def test_download_different_filename(self):
    with patch("filebrowser.api.mimetypes.guess_type") as guess_type:
      with patch("filebrowser.api.was_modified_since") as was_modified_since:
        guess_type.return_value = ("text/plain", None)
        was_modified_since.return_value = True

        # Normal filename
        request = Mock(
          method="GET",
          GET={"path": "s3a://test-bucket/test-user/test_file.txt"},
          fs=Mock(
            exists=Mock(return_value=True),
            isfile=Mock(return_value=True),
            read=Mock(),
            open=Mock(return_value=string_io(b"Hello, World!")),
            stats=Mock(return_value={"mtime": 1731527620, "size": 1024, "name": "test_file.txt"}),
          ),
        )

        reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(True)
        try:
          response = download(request)

          assert response.status_code == 200
          assert response["Content-Disposition"] == "attachment; filename*=UTF-8''test_file.txt"
        finally:
          reset()

        # Filename with whitespaces
        request = Mock(
          method="GET",
          GET={"path": "s3a://test-bucket/test-user/test file name.txt"},
          fs=Mock(
            exists=Mock(return_value=True),
            isfile=Mock(return_value=True),
            read=Mock(),
            open=Mock(return_value=string_io(b"Hello, World!")),
            stats=Mock(return_value={"mtime": 1731527620, "size": 1024, "name": "test file name.txt"}),
          ),
        )

        reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(True)
        try:
          response = download(request)

          assert response.status_code == 200
          assert response["Content-Disposition"] == "attachment; filename*=UTF-8''test%20file%20name.txt"
        finally:
          reset()

        # Filename with special characters
        request = Mock(
          method="GET",
          GET={"path": "s3a://test-bucket/test-user/Tжейкоб-åäö.csv"},
          fs=Mock(
            exists=Mock(return_value=True),
            isfile=Mock(return_value=True),
            read=Mock(),
            open=Mock(return_value=string_io(b"Hello, World!")),
            stats=Mock(return_value={"mtime": 1731527620, "size": 1024, "name": "Tжейкоб-åäö.csv"}),
          ),
        )

        reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(True)
        try:
          response = download(request)

          assert response.status_code == 200
          assert (
            response["Content-Disposition"] == "attachment; filename*=UTF-8''T%D0%B6%D0%B5%D0%B9%D0%BA%D0%BE%D0%B1-%C3%A5%C3%A4%C3%B6.csv"
          )
        finally:
          reset()

        # Filename with special characters and whitespaces
        request = Mock(
          method="GET",
          GET={"path": "s3a://test-bucket/test-user/Tжейкоб åäö.csv"},
          fs=Mock(
            exists=Mock(return_value=True),
            isfile=Mock(return_value=True),
            read=Mock(),
            open=Mock(return_value=string_io(b"Hello, World!")),
            stats=Mock(return_value={"mtime": 1731527620, "size": 1024, "name": "Tжейкоб åäö.csv"}),
          ),
        )

        reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(True)
        try:
          response = download(request)

          assert response.status_code == 200
          assert (
            response["Content-Disposition"] == "attachment; filename*=UTF-8''T%D0%B6%D0%B5%D0%B9%D0%BA%D0%BE%D0%B1%20%C3%A5%C3%A4%C3%B6.csv"
          )
        finally:
          reset()

        # Filename with % character
        request = Mock(
          method="GET",
          GET={"path": "s3a://test-bucket/test-user/test%file.txt"},
          fs=Mock(
            exists=Mock(return_value=True),
            isfile=Mock(return_value=True),
            read=Mock(),
            open=Mock(return_value=string_io(b"Hello, World!")),
            stats=Mock(return_value={"mtime": 1731527620, "size": 1024, "name": "test%file.txt"}),
          ),
        )

        reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(True)
        try:
          response = download(request)

          assert response.status_code == 200
          assert response["Content-Disposition"] == "attachment; filename*=UTF-8''test%25file.txt"
        finally:
          reset()

        # Filename with %20 character
        request = Mock(
          method="GET",
          GET={"path": "s3a://test-bucket/test-user/test%20file.txt"},
          fs=Mock(
            exists=Mock(return_value=True),
            isfile=Mock(return_value=True),
            read=Mock(),
            open=Mock(return_value=string_io(b"Hello, World!")),
            stats=Mock(return_value={"mtime": 1731527620, "size": 1024, "name": "test%20file.txt"}),
          ),
        )

        reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(True)
        try:
          response = download(request)

          assert response.status_code == 200
          assert response["Content-Disposition"] == "attachment; filename*=UTF-8''test%2520file.txt"
        finally:
          reset()

        # Filename with %20 character and whitespaces
        request = Mock(
          method="GET",
          GET={"path": "s3a://test-bucket/test-user/test%20file name.txt"},
          fs=Mock(
            exists=Mock(return_value=True),
            isfile=Mock(return_value=True),
            read=Mock(),
            open=Mock(return_value=string_io(b"Hello, World!")),
            stats=Mock(return_value={"mtime": 1731527620, "size": 1024, "name": "test%20file name.txt"}),
          ),
        )

        reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(True)
        try:
          response = download(request)

          assert response.status_code == 200
          assert response["Content-Disposition"] == "attachment; filename*=UTF-8''test%2520file%20name.txt"
        finally:
          reset()

  def test_download_file_redirection(self):
    with patch("filebrowser.api.mimetypes.guess_type") as guess_type:
      with patch("filebrowser.api.was_modified_since") as was_modified_since:
        guess_type.return_value = ("text/plain", None)
        was_modified_since.return_value = True

        request = Mock(
          method="GET",
          GET={"path": "s3a://test-bucket/test-user/test_file.txt"},
          fs=Mock(
            exists=Mock(return_value=True),
            isfile=Mock(return_value=True),
            read=Mock(),
            open=Mock(return_value=Mock(read_url=Mock(return_value="https://gethue.redirect.com/test_file.txt"))),
            stats=Mock(return_value={"mtime": 1731527620, "size": 1024, "name": "test_file.txt"}),
          ),
        )

        resets = [SHOW_DOWNLOAD_BUTTON.set_for_testing(True), REDIRECT_DOWNLOAD.set_for_testing(True)]
        try:
          response = download(request)

          assert response.status_code == 302
          assert isinstance(response, HttpResponseRedirect)

          assert response.redirect_override is True
          assert response.url == "https://gethue.redirect.com/test_file.txt"
        finally:
          for reset in resets:
            reset()

  def test_download_modified_since(self):
    with patch("filebrowser.api.mimetypes.guess_type") as guess_type:
      with patch("filebrowser.api.was_modified_since") as was_modified_since:
        guess_type.return_value = ("text/plain", None)
        was_modified_since.return_value = False

        request = Mock(
          method="GET",
          GET={"path": "s3a://test-bucket/test-user/test_file.txt"},
          fs=Mock(
            exists=Mock(return_value=True),
            isfile=Mock(return_value=True),
            stats=Mock(return_value={"mtime": 1731527620, "size": 1024, "name": "test_file.txt"}),
          ),
          META={"HTTP_IF_MODIFIED_SINCE": "Thu, 14 Jun 2018 10:00:00 GMT"},
        )

        reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(True)
        try:
          response = download(request)

          assert response.status_code == 304
          assert isinstance(response, HttpResponseNotModified)
        finally:
          reset()

  def test_download_read_permission_denied(self):
    with patch("filebrowser.api.mimetypes.guess_type") as guess_type:
      with patch("filebrowser.api.was_modified_since") as was_modified_since:
        guess_type.return_value = ("text/plain", None)
        was_modified_since.return_value = True

        request = Mock(
          method="GET",
          GET={"path": "s3a://test-bucket/test-user/test_file.txt"},
          user=Mock(username="test-hue-user"),
          fs=Mock(
            exists=Mock(return_value=True),
            isfile=Mock(return_value=True),
            stats=Mock(return_value={"mtime": 1731527620, "size": 1024, "name": "test_file.txt"}),
            open=Mock(return_value=string_io(b"Hello, World!")),
            read=Mock(side_effect=WebHdfsException(Mock(response=Mock(status_code=403, text="Signature Mismatch")))),
          ),
        )

        reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(True)
        try:
          response = download(request)

          assert response.status_code == 403
          assert (
            response.content.decode("utf-8")
            == "User test-hue-user is not authorized to download file at path: s3a://test-bucket/test-user/test_file.txt"
          )
        finally:
          reset()

  def test_download_abfs_zero_filesize_exception(self):
    with patch("filebrowser.api.mimetypes.guess_type") as guess_type:
      with patch("filebrowser.api.was_modified_since") as was_modified_since:
        guess_type.return_value = ("text/plain", None)
        was_modified_since.return_value = True

        request = Mock(
          method="GET",
          GET={"path": "abfs://test-container/test-user/test_file.txt"},
          fs=Mock(
            exists=Mock(return_value=True),
            isfile=Mock(return_value=True),
            stats=Mock(return_value={"mtime": 1731527620, "size": 0, "name": "test_file.txt"}),
            open=Mock(return_value=string_io(b"")),
            read=Mock(side_effect=WebHdfsException(Mock(response=Mock(status_code=416, text="Blob size is zero")))),
            _get_scheme=Mock(return_value="abfs"),
          ),
        )

        reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(True)
        try:
          response = download(request)
          stream_response_content = b"".join(response.streaming_content)

          assert isinstance(response, StreamingHttpResponse)
          assert response.status_code == 200
          assert stream_response_content.decode("utf-8") == ""
          assert response["Content-Disposition"] == "attachment; filename*=UTF-8''test_file.txt"
        finally:
          reset()

  def test_download_unknown_exception(self):
    with patch("filebrowser.api.mimetypes.guess_type") as guess_type:
      with patch("filebrowser.api.was_modified_since") as was_modified_since:
        guess_type.return_value = ("text/plain", None)
        was_modified_since.return_value = True

        request = Mock(
          method="GET",
          GET={"path": "s3a://test-bucket/test-user/test_file.txt"},
          fs=Mock(
            exists=Mock(return_value=True),
            isfile=Mock(return_value=True),
            stats=Mock(return_value={"mtime": 1731527620, "size": 1024, "name": "test_file.txt"}),
            open=Mock(return_value=string_io(b"Hello, World!")),
            read=Mock(side_effect=WebHdfsException(Mock(response=Mock(status_code=500, text="Internal Server Error")))),
          ),
        )

        reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(True)
        try:
          response = download(request)

          assert response.status_code == 500
        finally:
          reset()

  def test_download_audit_log(self):
    with patch("filebrowser.api.mimetypes.guess_type") as guess_type:
      with patch("filebrowser.api.was_modified_since") as was_modified_since:
        guess_type.return_value = ("text/plain", None)
        was_modified_since.return_value = True

        request = Mock(
          method="GET",
          GET={"path": "s3a://test-bucket/test-user/test_file.txt"},
          user=Mock(username="test-hue-user"),
          fs=Mock(
            exists=Mock(return_value=True),
            isfile=Mock(return_value=True),
            stats=Mock(return_value={"mtime": 1731527620, "size": 1024, "name": "test_file.txt"}),
            open=Mock(return_value=string_io(b"Hello, World!")),
            read=Mock(),
          ),
        )

        reset = SHOW_DOWNLOAD_BUTTON.set_for_testing(True)
        try:
          response = download(request)

          assert response.status_code == 200
          assert request.audit == {
            "operation": "DOWNLOAD",
            "operationText": 'User test-hue-user downloaded file at path "s3a://test-bucket/test-user/test_file.txt"',
            "allowed": True,
          }
        finally:
          reset()


class TestUploadFileAPI:
  def setup_method(self):
    self.view = UploadFileAPI()
    self.request = Mock()
    self.request.user = Mock(username="test_user")
    self.request.query_params = {}
    self.request.FILES = {}

  def test_post_success(self):
    self.request.FILES = {"file": {"path": "s3a://test-bucket/test-user/test/dest/file.txt", "size": 123}}

    response = self.view.post(self.request)

    assert response.status_code == 201
    assert response.data == {"file_stats": {"path": "s3a://test-bucket/test-user/test/dest/file.txt", "size": 123}}

  def test_post_file_upload_failed(self):
    self.request.FILES = {"file": "not_a_dict"}

    response = self.view.post(self.request)

    assert response.status_code == 400
    assert response.data is not None
    assert response.data.get("error") == "File upload failed or was not handled correctly by the upload handler."

  def test_post_raises_popup_exception(self):
    self.request.FILES = MagicMock()
    self.request.FILES.get.side_effect = PopupException("Test PopupException", error_code=403)

    response = self.view.post(self.request)

    assert response.status_code == 403
    assert response.data == {"error": "Test PopupException"}

  def test_post_raises_generic_exception(self):
    self.request.FILES = MagicMock()
    self.request.FILES.get.side_effect = Exception("Generic error")

    response = self.view.post(self.request)

    assert response.status_code == 500
    assert response.data == {"error": "An unexpected error occurred while uploading the file."}


class TestUploadFileAPIDispatch:

  def setup_method(self):
    self.factory = APIRequestFactory()
    self.view = UploadFileAPI()
    # A mock authenticated user for session-based tests
    self.authenticated_user = Mock(username="test_user", is_authenticated=True)

  @patch("filebrowser.api.UploadFileSerializer")
  @patch("filebrowser.api.get_user_fs")
  @patch.object(APIView, "dispatch")
  def test_dispatch_with_token_success(self, mock_super_dispatch, mock_get_user_fs, mock_serializer):
    request = self.factory.post("/fake-url?destination_path=s3a://path&overwrite=true")
    request.user = AnonymousUser()

    mock_authenticator = Mock()
    mock_authenticator.authenticate.return_value = (self.authenticated_user, "mock_token")
    self.view.get_authenticators = Mock(return_value=[mock_authenticator])

    mock_serializer.return_value.is_valid.return_value = True
    mock_serializer.return_value.validated_data = {"destination_path": "s3a://path", "overwrite": True}
    mock_get_user_fs.return_value.get_upload_handler.return_value = Mock(name="S3Handler")
    mock_super_dispatch.return_value = "SuccessResponse"

    response = self.view.dispatch(request)

    mock_authenticator.authenticate.assert_called_once_with(request)
    mock_get_user_fs.assert_called_once_with(self.authenticated_user.username)
    assert request.user == self.authenticated_user
    assert response == "SuccessResponse"

  def test_dispatch_with_invalid_token(self):
    request = self.factory.post("/fake-url")
    request.user = AnonymousUser()

    mock_authenticator = Mock()
    error_detail = {"detail": "Invalid token."}
    mock_authenticator.authenticate.side_effect = AuthenticationFailed(error_detail)
    self.view.get_authenticators = Mock(return_value=[mock_authenticator])

    response = self.view.dispatch(request)
    response_content = json.loads(response.content)

    assert isinstance(response, JsonResponse)
    assert response.status_code == 401
    assert response_content == error_detail

  def test_dispatch_with_no_credentials(self):
    request = self.factory.post("/fake-url")
    request.user = AnonymousUser()

    mock_authenticator = Mock()
    mock_authenticator.authenticate.return_value = None
    self.view.get_authenticators = Mock(return_value=[mock_authenticator])

    response = self.view.dispatch(request)
    response_content = json.loads(response.content)

    assert isinstance(response, JsonResponse)
    assert response.status_code == 401
    assert "not provided" in response_content["error"]

  @patch("filebrowser.api.UploadFileSerializer")
  @patch("filebrowser.api.get_user_fs")
  @patch.object(APIView, "dispatch")
  def test_dispatch_ui_pre_authenticated_user_success(self, mock_super_dispatch, mock_get_user_fs, mock_serializer):
    request = self.factory.post("/fake-url?destination_path=s3a://path&overwrite=true")
    request.user = self.authenticated_user

    mock_serializer.return_value.is_valid.return_value = True
    mock_serializer.return_value.validated_data = {"destination_path": "s3a://path", "overwrite": True}
    mock_get_user_fs.return_value.get_upload_handler.return_value = Mock(name="S3Handler")
    mock_super_dispatch.return_value = "SuccessResponse"

    response = self.view.dispatch(request)

    assert response == "SuccessResponse"

  @patch("filebrowser.api.UploadFileSerializer")
  def test_dispatch_ui_pre_authenticated_user_validation_error(self, mock_serializer):
    request = self.factory.post("/fake-url")
    request.user = self.authenticated_user

    error_detail = {"destination_path": ["This field is required."]}
    mock_serializer.return_value.is_valid.side_effect = ValidationError(error_detail)

    response = self.view.dispatch(request)
    response_content = json.loads(response.content)

    assert isinstance(response, JsonResponse)
    assert response.status_code == 400
    assert response_content == error_detail

  @patch("filebrowser.api.get_user_fs")
  @patch("filebrowser.api.UploadFileSerializer")
  def test_dispatch_ui_pre_authenticated_user_handler_not_found(self, mock_serializer, mock_get_user_fs):
    request = self.factory.post("/fake-url?destination_path=unsupported://path")
    request.user = self.authenticated_user

    mock_serializer.return_value.is_valid.return_value = True
    mock_serializer.return_value.validated_data = {"destination_path": "unsupported://path", "overwrite": False}
    mock_get_user_fs.return_value.get_upload_handler.return_value = None

    response = self.view.dispatch(request)
    response_content = json.loads(response.content)

    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    assert "No supported upload handler found" in response_content["error"]

  @patch("filebrowser.api.get_user_fs")
  @patch("filebrowser.api.UploadFileSerializer")
  def test_dispatch_ui_pre_authenticated_user_unexpected_exception(self, mock_serializer, mock_get_user_fs):
    request = self.factory.post("/fake-url?destination_path=s3a://path")
    request.user = self.authenticated_user

    mock_serializer.return_value.is_valid.return_value = True
    mock_serializer.return_value.validated_data = {"destination_path": "s3a://path", "overwrite": False}
    mock_get_user_fs.side_effect = Exception("Something went wrong!")

    response = self.view.dispatch(request)
    response_content = json.loads(response.content)

    assert isinstance(response, JsonResponse)
    assert response.status_code == 500
    assert "server error" in response_content["error"]
