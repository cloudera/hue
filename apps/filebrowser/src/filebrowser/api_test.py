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
from unittest.mock import MagicMock, Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile

from aws.s3.s3fs import S3ListAllBucketsException
from filebrowser.api import copy, get_all_filesystems, listdir_paged, mkdir, move, rename, touch, upload_file
from filebrowser.conf import (
  MAX_FILE_SIZE_UPLOAD_LIMIT,
  RESTRICT_FILE_EXTENSIONS,
)


class TestSimpleFileUploadAPI:
  def test_file_upload_success(self):
    with patch('filebrowser.api.string_io') as string_io:
      with patch('filebrowser.api.stat_absolute_path') as stat_absolute_path:
        with patch('filebrowser.api._massage_stats') as _massage_stats:
          request = Mock(
            method='POST',
            META=Mock(),
            POST={'destination_path': 's3a://test-bucket/test-user/'},
            FILES={'file': SimpleUploadedFile('test_file.txt', b'Hello World!')},
            body=Mock(),
            fs=Mock(
              join=Mock(),
              exists=Mock(side_effect=[False, True]),
              isdir=Mock(return_value=False),
              upload_v1=Mock(return_value=None),
              stats=Mock(),
              rmtree=Mock(),
            ),
          )

          _massage_stats.return_value = {
            "path": "s3a://test-bucket/test-user/test_file.txt",
            "size": 12,
            "atime": 1731527617,
            "mtime": 1731527620,
            "mode": 33188,
            "user": "test-user",
            "group": "test-user",
            "blockSize": 134217728,
            "replication": 3,
            "type": "file",
            "rwx": "-rw-r--r--",
          }

          resets = [
            RESTRICT_FILE_EXTENSIONS.set_for_testing(''),
            MAX_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(-1),
          ]
          try:
            response = upload_file(request)
            response_data = json.loads(response.content)

            request.fs.rmtree.assert_not_called()
            assert response.status_code == 200
            assert response_data['uploaded_file_stats'] == {
              "path": "s3a://test-bucket/test-user/test_file.txt",
              "size": 12,
              "atime": 1731527617,
              "mtime": 1731527620,
              "mode": 33188,
              "user": "test-user",
              "group": "test-user",
              "blockSize": 134217728,
              "replication": 3,
              "type": "file",
              "rwx": "-rw-r--r--",
            }
          finally:
            for reset in resets:
              reset()

  def test_upload_invalid_file_type(self):
    with patch('filebrowser.api.string_io') as string_io:
      request = Mock(
        method='POST',
        META=Mock(),
        POST={'destination_path': 's3a://test-bucket/test-user/'},
        FILES={'file': SimpleUploadedFile('test_file.txt', b'Hello World!')},
        body=Mock(),
        fs=Mock(
          join=Mock(),
          exists=Mock(side_effect=[False, True]),
          isdir=Mock(return_value=False),
          upload_v1=Mock(return_value=None),
          stats=Mock(),
        ),
      )
      resets = [
        RESTRICT_FILE_EXTENSIONS.set_for_testing('.exe,.txt'),
        MAX_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(-1),
      ]
      try:
        response = upload_file(request)
        res_content = response.content.decode('utf-8')

        assert response.status_code == 400
        assert res_content == 'Uploading files with type ".txt" is not allowed. Hue is configured to restrict this type.'
      finally:
        for reset in resets:
          reset()

  def test_upload_file_exceeds_max_size(self):
    with patch('filebrowser.api.string_io') as string_io:
      request = Mock(
        method='POST',
        META=Mock(),
        POST={'destination_path': 's3a://test-bucket/test-user/'},
        FILES={'file': SimpleUploadedFile('test_file.txt', b'Hello World!')},
        body=Mock(),
        fs=Mock(
          join=Mock(),
          exists=Mock(side_effect=[False, True]),
          isdir=Mock(return_value=False),
          upload_v1=Mock(return_value=None),
          stats=Mock(),
        ),
      )
      resets = [
        RESTRICT_FILE_EXTENSIONS.set_for_testing(''),
        MAX_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(5),
      ]
      try:
        response = upload_file(request)
        res_content = response.content.decode('utf-8')

        assert response.status_code == 413
        assert res_content == 'File exceeds maximum allowed size of 5 bytes. Hue is configured to restrict uploads larger than this limit.'
      finally:
        for reset in resets:
          reset()

  def test_upload_file_already_exists(self):
    with patch('filebrowser.api.string_io') as string_io:
      request = Mock(
        method='POST',
        META=Mock(),
        POST={'destination_path': 's3a://test-bucket/test-user/'},
        FILES={'file': SimpleUploadedFile('test_file.txt', b'Hello World!')},
        body=Mock(),
        fs=Mock(
          join=Mock(return_value='s3a://test-bucket/test-user/test_file.txt'),
          exists=Mock(return_value=True),
          isdir=Mock(return_value=True),
          upload_v1=Mock(return_value=None),
          stats=Mock(),
        ),
      )
      resets = [
        RESTRICT_FILE_EXTENSIONS.set_for_testing(''),
        MAX_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(-1),
      ]
      try:
        response = upload_file(request)

        assert response.status_code == 409
        assert response.content.decode('utf-8') == 'The file test_file.txt already exists at the destination path.'
      finally:
        for reset in resets:
          reset()

  def test_overwrite_existing_file_success(self):
    with patch('filebrowser.api.string_io') as string_io:
      with patch('filebrowser.api.stat_absolute_path') as stat_absolute_path:
        with patch('filebrowser.api._massage_stats') as _massage_stats:
          request = Mock(
            method='POST',
            META=Mock(),
            POST={'destination_path': 's3a://test-bucket/test-user/', 'overwrite': True},
            FILES={'file': SimpleUploadedFile('test_file.txt', b'Hello World!')},
            body=Mock(),
            fs=Mock(
              join=Mock(return_value='s3a://test-bucket/test-user/test_file.txt'),
              exists=Mock(side_effect=[True, True]),
              isdir=Mock(return_value=False),
              upload_v1=Mock(return_value=None),
              stats=Mock(),
              rmtree=Mock(),
            ),
          )

          _massage_stats.return_value = {
            "path": "s3a://test-bucket/test-user/test_file.txt",
            "size": 12,
            "atime": 1731527617,
            "mtime": 1731527620,
            "mode": 33188,
            "user": "test-user",
            "group": "test-user",
            "blockSize": 134217728,
            "replication": 3,
            "type": "file",
            "rwx": "-rw-r--r--",
          }

          resets = [
            RESTRICT_FILE_EXTENSIONS.set_for_testing(''),
            MAX_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(-1),
          ]
          try:
            response = upload_file(request)
            response_data = json.loads(response.content)

            request.fs.rmtree.assert_called_once_with('s3a://test-bucket/test-user/test_file.txt')
            assert response.status_code == 200
            assert response_data['uploaded_file_stats'] == {
              "path": "s3a://test-bucket/test-user/test_file.txt",
              "size": 12,
              "atime": 1731527617,
              "mtime": 1731527620,
              "mode": 33188,
              "user": "test-user",
              "group": "test-user",
              "blockSize": 134217728,
              "replication": 3,
              "type": "file",
              "rwx": "-rw-r--r--",
            }
          finally:
            for reset in resets:
              reset()

  def test_overwrite_existing_file_exception(self):
    with patch('filebrowser.api.string_io') as string_io:
      request = Mock(
        method='POST',
        META=Mock(),
        POST={'destination_path': 's3a://test-bucket/test-user/', 'overwrite': True},
        FILES={'file': SimpleUploadedFile('test_file.txt', b'Hello World!')},
        body=Mock(),
        fs=Mock(
          join=Mock(return_value='s3a://test-bucket/test-user/test_file.txt'),
          exists=Mock(side_effect=[True, True]),
          isdir=Mock(return_value=False),
          upload_v1=Mock(return_value=None),
          stats=Mock(),
          rmtree=Mock(side_effect=Exception('Filesystem rmtree exception')),
        ),
      )

      resets = [
        RESTRICT_FILE_EXTENSIONS.set_for_testing(''),
        MAX_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(-1),
      ]
      try:
        response = upload_file(request)

        request.fs.rmtree.assert_called_once_with('s3a://test-bucket/test-user/test_file.txt')
        assert response.status_code == 500
        assert response.content.decode('utf-8') == 'Failed to remove already existing file.'
      finally:
        for reset in resets:
          reset()

  def test_destination_path_does_not_exists(self):
    with patch('filebrowser.api.string_io') as string_io:
      request = Mock(
        method='POST',
        META=Mock(),
        POST={'destination_path': 's3a://test-bucket/test-user/'},
        FILES={'file': SimpleUploadedFile('test_file.txt', b'Hello World!')},
        body=Mock(),
        fs=Mock(
          join=Mock(),
          exists=Mock(return_value=False),
          isdir=Mock(return_value=True),
          upload_v1=Mock(return_value=None),
          stats=Mock(),
        ),
      )
      resets = [
        RESTRICT_FILE_EXTENSIONS.set_for_testing(''),
        MAX_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(-1),
      ]
      try:
        response = upload_file(request)

        assert response.status_code == 404
        assert response.content.decode('utf-8') == 'The destination path s3a://test-bucket/test-user/ does not exist.'
      finally:
        for reset in resets:
          reset()

  def test_file_upload_failure(self):
    with patch('filebrowser.api.string_io') as string_io:
      request = Mock(
        method='POST',
        META=Mock(),
        POST={'destination_path': 's3a://test-bucket/test-user/'},
        FILES={'file': SimpleUploadedFile('test_file.txt', b'Hello World!')},
        body=Mock(),
        fs=Mock(
          join=Mock(return_value='s3a://test-bucket/test-user/test_file.txt'),
          exists=Mock(side_effect=[False, True]),
          isdir=Mock(return_value=True),
          upload_v1=Mock(side_effect=Exception('Upload exception occured!')),
          stats=Mock(),
        ),
      )
      resets = [
        RESTRICT_FILE_EXTENSIONS.set_for_testing(''),
        MAX_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(-1),
      ]
      try:
        response = upload_file(request)

        assert response.status_code == 500
        assert response.content.decode('utf-8') == 'Upload to s3a://test-bucket/test-user/test_file.txt failed: Upload exception occured!'
      finally:
        for reset in resets:
          reset()


class TestTouchAPI:
  def test_touch_success(self):
    request = Mock(
      method='POST',
      POST={'path': 's3a://test-bucket/test-user/', 'name': 'test_file.txt'},
      fs=Mock(
        isfile=Mock(return_value=False),
        join=Mock(return_value='s3a://test-bucket/test-user/test_file.txt'),
        create=Mock(),
      ),
    )
    response = touch(request)

    assert response.status_code == 201
    request.fs.create.assert_called_once_with('s3a://test-bucket/test-user/test_file.txt')

  def test_touch_file_exists(self):
    request = Mock(
      method='POST',
      POST={'path': 's3a://test-bucket/test-user/', 'name': 'test_file.txt'},
      fs=Mock(
        isfile=Mock(return_value=True),
        join=Mock(return_value='s3a://test-bucket/test-user/test_file.txt'),
      ),
    )
    response = touch(request)

    assert response.status_code == 409
    assert response.content.decode('utf-8') == 'Error creating test_file.txt file: File already exists.'

  def test_touch_invalid_name(self):
    request = Mock(
      method='POST',
      POST={'path': 's3a://test-bucket/test-user/', 'name': 'test/file.txt'},
      fs=Mock(),
    )
    response = touch(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Slashes are not allowed in filename. Please choose a different name.'

  def test_touch_no_path(self):
    request = Mock(
      method='POST',
      POST={'name': 'test_file.txt'},
      fs=Mock(),
    )
    response = touch(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Missing parameters: path and name are required.'

  def test_touch_no_name(self):
    request = Mock(
      method='POST',
      POST={'path': 's3a://test-bucket/test-user/'},
      fs=Mock(),
    )
    response = touch(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Missing parameters: path and name are required.'


class TestMkdirAPI:
  def test_mkdir_success(self):
    request = Mock(
      method='POST',
      POST={'path': 's3a://test-bucket/test-user/', 'name': 'new_dir'},
      fs=Mock(
        mkdir=Mock(),
        isdir=Mock(return_value=False),
        join=Mock(return_value='s3a://test-bucket/test-user/new_dir'),
      ),
    )
    response = mkdir(request)

    assert response.status_code == 201
    request.fs.mkdir.assert_called_once_with('s3a://test-bucket/test-user/new_dir')

  def test_mkdir_directory_exists(self):
    request = Mock(
      method='POST',
      POST={'path': 's3a://test-bucket/test-user/', 'name': 'new_dir'},
      fs=Mock(
        mkdir=Mock(),
        isdir=Mock(return_value=True),
        join=Mock(return_value='s3a://test-bucket/test-user/new_dir'),
      ),
    )
    response = mkdir(request)

    assert response.status_code == 409
    assert response.content.decode('utf-8') == 'Error creating new_dir directory: Directory already exists.'

  def test_mkdir_invalid_name(self):
    request = Mock(
      method='POST',
      POST={'path': 's3a://test-bucket/test-user/', 'name': 'new#dir'},
      fs=Mock(
        mkdir=Mock(),
        isdir=Mock(return_value=False),
        join=Mock(return_value='s3a://test-bucket/test-user/new#dir'),
      ),
    )
    response = mkdir(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Slashes or hashes are not allowed in directory name. Please choose a different name.'

  def test_mkdir_no_path(self):
    request = Mock(
      method='POST',
      POST={'name': 'new_dir'},
      fs=Mock(
        mkdir=Mock(),
        isdir=Mock(return_value=False),
        join=Mock(return_value='s3a://test-bucket/test-user/new_dir'),
      ),
    )
    response = mkdir(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Missing required parameters: path and name are required.'

  def test_mkdir_no_name(self):
    request = Mock(
      method='POST',
      POST={'path': 's3a://test-bucket/test-user/'},
      fs=Mock(
        mkdir=Mock(),
        isdir=Mock(return_value=False),
        join=Mock(return_value='s3a://test-bucket/test-user/new_dir'),
      ),
    )
    response = mkdir(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Missing required parameters: path and name are required.'


class TestRenameAPI:
  def test_rename_success(self):
    request = Mock(
      method='POST',
      POST={'source_path': 's3a://test-bucket/test-user/source.txt', 'destination_path': 'new_name.txt'},
      fs=Mock(
        exists=Mock(return_value=False),
        join=Mock(return_value='s3a://test-bucket/test-user/new_name.txt'),
        rename=Mock(),
      ),
    )
    reset = RESTRICT_FILE_EXTENSIONS.set_for_testing(None)
    try:
      response = rename(request)

      assert response.status_code == 200
      request.fs.rename.assert_called_once_with('s3a://test-bucket/test-user/source.txt', 's3a://test-bucket/test-user/new_name.txt')
    finally:
      reset()

  def test_rename_restricted_file_type(self):
    request = Mock(
      method='POST',
      POST={'source_path': 's3a://test-bucket/test-user/source.txt', 'destination_path': 'new_name.exe'},
      fs=Mock(
        rename=Mock(),
      ),
    )
    reset = RESTRICT_FILE_EXTENSIONS.set_for_testing('.exe,.txt')
    try:
      response = rename(request)

      assert response.status_code == 403
      assert response.content.decode('utf-8') == 'Cannot rename file to a restricted file type: ".exe"'
    finally:
      reset()

  def test_rename_hash_in_path(self):
    request = Mock(
      method='POST',
      POST={'source_path': 's3a://test-bucket/test-user/source.txt', 'destination_path': 'new#name.txt'},
      fs=Mock(
        rename=Mock(),
      ),
    )
    reset = RESTRICT_FILE_EXTENSIONS.set_for_testing(None)
    try:
      response = rename(request)

      assert response.status_code == 400
      assert response.content.decode('utf-8') == 'Hashes are not allowed in file or directory names. Please choose a different name.'
    finally:
      reset()

  def test_rename_destination_exists(self):
    request = Mock(
      method='POST',
      POST={'source_path': 's3a://test-bucket/test-user/source.txt', 'destination_path': 'new_name.txt'},
      fs=Mock(
        rename=Mock(),
        exists=Mock(return_value=True),
        join=Mock(return_value='s3a://test-bucket/test-user/new_name.txt'),
      ),
    )
    reset = RESTRICT_FILE_EXTENSIONS.set_for_testing(None)
    try:
      response = rename(request)

      assert response.status_code == 409
      assert response.content.decode('utf-8') == 'The destination path s3a://test-bucket/test-user/new_name.txt already exists.'
    finally:
      reset()

  def test_rename_no_source_path(self):
    request = Mock(
      method='POST',
      POST={'destination_path': 'new_name.txt'},
      fs=Mock(
        rename=Mock(),
      ),
    )
    reset = RESTRICT_FILE_EXTENSIONS.set_for_testing(None)
    try:
      response = rename(request)

      assert response.status_code == 400
      assert response.content.decode('utf-8') == 'Missing required parameters: source_path and destination_path'
    finally:
      reset()

  def test_rename_no_destination_path(self):
    request = Mock(
      method='POST',
      POST={'source_path': 's3a://test-bucket/test-user/source.txt'},
      fs=Mock(
        rename=Mock(),
      ),
    )
    reset = RESTRICT_FILE_EXTENSIONS.set_for_testing(None)
    try:
      response = rename(request)

      assert response.status_code == 400
      assert response.content.decode('utf-8') == 'Missing required parameters: source_path and destination_path'
    finally:
      reset()


class TestMoveAPI:
  def test_move_success(self):
    request = Mock(
      method='POST',
      POST={'source_path': 's3a://test-bucket/test-user/src_dir/source.txt', 'destination_path': 's3a://test-bucket/test-user/dst_dir'},
      fs=Mock(
        exists=Mock(side_effect=[True, False]),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value='s3a://test-bucket/test-user/src_dir'),
        join=Mock(return_value='s3a://test-bucket/test-user/dst_dir/source.txt'),
        normpath=Mock(
          side_effect=[
            's3a://test-bucket/test-user/src_dir/source.txt',
            's3a://test-bucket/test-user/dst_dir',
            's3a://test-bucket/test-user/dst_dir',
          ]
        ),
        rename=Mock(),
      ),
    )
    response = move(request)

    assert response.status_code == 200
    request.fs.rename.assert_called_once_with('s3a://test-bucket/test-user/src_dir/source.txt', 's3a://test-bucket/test-user/dst_dir')

  def test_move_no_source_path(self):
    request = Mock(
      method='POST',
      POST={'destination_path': 's3a://test-bucket/test-user/dst_dir'},
      fs=Mock(),
    )
    response = move(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Missing required parameters: source_path and destination_path are required.'

  def test_move_no_destination_path(self):
    request = Mock(
      method='POST',
      POST={'source_path': 's3a://test-bucket/test-user/src_dir/source.txt'},
      fs=Mock(),
    )
    response = move(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Missing required parameters: source_path and destination_path are required.'

  def test_move_identical_paths(self):
    request = Mock(
      method='POST',
      POST={
        'source_path': 's3a://test-bucket/test-user/src_dir/source.txt',
        'destination_path': 's3a://test-bucket/test-user/src_dir/source.txt',
      },
      fs=Mock(
        normpath=Mock(side_effect=['s3a://test-bucket/test-user/src_dir/source.txt', 's3a://test-bucket/test-user/src_dir/source.txt']),
      ),
    )
    response = move(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Source and destination paths must be different.'

  def test_move_source_path_does_not_exist(self):
    request = Mock(
      method='POST',
      POST={
        'source_path': 's3a://test-bucket/test-user/src_dir/source.txt',
        'destination_path': 's3a://test-bucket/test-user/dst_dir',
      },
      fs=Mock(
        exists=Mock(return_value=False),
        normpath=Mock(side_effect=['s3a://test-bucket/test-user/src_dir/source.txt', 's3a://test-bucket/test-user/dst_dir']),
      ),
    )
    response = move(request)

    assert response.status_code == 404
    assert response.content.decode('utf-8') == 'Source file or folder does not exist.'

  def test_move_destination_not_a_directory(self):
    request = Mock(
      method='POST',
      POST={
        'source_path': 's3a://test-bucket/test-user/src_dir/source.txt',
        'destination_path': 's3a://test-bucket/test-user/dst_dir',
      },
      fs=Mock(
        exists=Mock(return_value=True),
        isdir=Mock(return_value=False),
        normpath=Mock(side_effect=['s3a://test-bucket/test-user/src_dir/source.txt', 's3a://test-bucket/test-user/dst_dir']),
      ),
    )
    response = move(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Destination path must be a directory.'

  def test_move_destination_is_parent_of_source(self):
    request = Mock(
      method='POST',
      POST={
        'source_path': 's3a://test-bucket/test-user/src_dir/source.txt',
        'destination_path': 's3a://test-bucket/test-user/src_dir',
      },
      fs=Mock(
        exists=Mock(return_value=True),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value='s3a://test-bucket/test-user/src_dir'),
        normpath=Mock(
          side_effect=[
            's3a://test-bucket/test-user/src_dir/source.txt',
            's3a://test-bucket/test-user/src_dir',
            's3a://test-bucket/test-user/src_dir',
          ]
        ),
      ),
    )
    response = move(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Destination cannot be the parent directory of source.'

  def test_move_file_already_exists_at_destination(self):
    request = Mock(
      method='POST',
      POST={
        'source_path': 's3a://test-bucket/test-user/src_dir/source.txt',
        'destination_path': 's3a://test-bucket/test-user/dst_dir',
      },
      fs=Mock(
        exists=Mock(side_effect=[True, True]),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value='s3a://test-bucket/test-user/src_dir'),
        join=Mock(return_value='s3a://test-bucket/test-user/dst_dir/source.txt'),
        normpath=Mock(
          side_effect=[
            's3a://test-bucket/test-user/src_dir/source.txt',
            's3a://test-bucket/test-user/dst_dir',
            's3a://test-bucket/test-user/dst_dir',
          ]
        ),
      ),
    )
    response = move(request)

    assert response.status_code == 409
    assert response.content.decode('utf-8') == 'File or folder already exists at destination path.'


class TestGetFilesystemsAPI:
  def test_get_all_filesystems_without_hdfs(self):
    with patch('filebrowser.api.fsmanager.get_filesystems') as get_filesystems:
      with patch('filebrowser.api.get_s3_home_directory') as get_s3_home_directory:
        with patch('filebrowser.api._is_hdfs_superuser') as _is_hdfs_superuser:
          get_filesystems.return_value = ['s3a', 'ofs']
          get_s3_home_directory.return_value = 's3a://test-bucket/test-user-home-dir/'
          _is_hdfs_superuser.return_value = False
          request = Mock(
            method='GET',
            user=Mock(),
          )

          response = get_all_filesystems(request)
          response_data = json.loads(response.content)

          assert response.status_code == 200
          assert response_data == [
            {'name': 's3a', 'user_home_directory': 's3a://test-bucket/test-user-home-dir/', 'config': {}},
            {'name': 'ofs', 'user_home_directory': 'ofs://', 'config': {}},
          ]

  def test_get_all_filesystems_success(self):
    with patch('filebrowser.api.fsmanager.get_filesystems') as get_filesystems:
      with patch('filebrowser.api.get_s3_home_directory') as get_s3_home_directory:
        with patch('filebrowser.api._is_hdfs_superuser') as _is_hdfs_superuser:
          with patch('filebrowser.api.User') as User:
            with patch('filebrowser.api.Group') as Group:
              get_filesystems.return_value = ['hdfs', 's3a', 'ofs']
              get_s3_home_directory.return_value = 's3a://test-bucket/test-user-home-dir/'
              _is_hdfs_superuser.return_value = False
              request = Mock(
                method='GET',
                user=Mock(get_home_directory=Mock(return_value='/user/test-user')),
                fs=Mock(
                  superuser='test-user',
                  supergroup='test-supergroup',
                ),
              )

              response = get_all_filesystems(request)
              response_data = json.loads(response.content)

              assert response.status_code == 200
              assert response_data == [
                {
                  'name': 'hdfs',
                  'user_home_directory': '/user/test-user',
                  'config': {
                    'is_trash_enabled': False,
                    'is_hdfs_superuser': False,
                    'groups': [],
                    'users': [],
                    'superuser': 'test-user',
                    'supergroup': 'test-supergroup',
                  },
                },
                {'name': 's3a', 'user_home_directory': 's3a://test-bucket/test-user-home-dir/', 'config': {}},
                {'name': 'ofs', 'user_home_directory': 'ofs://', 'config': {}},
              ]


class TestCopyAPI:
  def test_copy_normal_success(self):
    request = Mock(
      method='POST',
      POST={'source_path': 's3a://test-bucket/test-user/src_dir/source.txt', 'destination_path': 's3a://test-bucket/test-user/dst_dir'},
      fs=Mock(
        exists=Mock(side_effect=[True, False]),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value='s3a://test-bucket/test-user/src_dir'),
        join=Mock(return_value='s3a://test-bucket/test-user/dst_dir/source.txt'),
        normpath=Mock(
          side_effect=[
            's3a://test-bucket/test-user/src_dir/source.txt',
            's3a://test-bucket/test-user/dst_dir',
            's3a://test-bucket/test-user/dst_dir',
          ]
        ),
        copy=Mock(),
        user=Mock(),
      ),
    )
    response = copy(request)

    assert response.status_code == 200
    request.fs.copy.assert_called_once_with(
      's3a://test-bucket/test-user/src_dir/source.txt', 's3a://test-bucket/test-user/dst_dir', recursive=True, owner=request.user
    )

  def test_copy_ofs_success(self):
    request = Mock(
      method='POST',
      POST={
        'source_path': 'ofs://test_vol/test-bucket/test-user/src_dir/source.txt',
        'destination_path': 'ofs://test_vol/test-bucket/test-user/dst_dir',
      },
      fs=Mock(
        exists=Mock(side_effect=[True, False]),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value='ofs://test_vol/test-bucket/test-user/src_dir'),
        join=Mock(return_value='ofs://test_vol/test-bucket/test-user/dst_dir/source.txt'),
        normpath=Mock(
          side_effect=[
            'ofs://test_vol/test-bucket/test-user/src_dir/source.txt',
            'ofs://test_vol/test-bucket/test-user/dst_dir',
            'ofs://test_vol/test-bucket/test-user/dst_dir',
          ]
        ),
        copy=Mock(return_value=''),
        user=Mock(),
      ),
    )
    response = copy(request)

    assert response.status_code == 200
    request.fs.copy.assert_called_once_with(
      'ofs://test_vol/test-bucket/test-user/src_dir/source.txt',
      'ofs://test_vol/test-bucket/test-user/dst_dir',
      recursive=True,
      owner=request.user,
    )

  def test_copy_ofs_skip_files_error(self):
    request = Mock(
      method='POST',
      POST={
        'source_path': 'ofs://test_vol/test-bucket/test-user/src_dir/source.txt',
        'destination_path': 'ofs://test_vol/test-bucket/test-user/dst_dir',
      },
      fs=Mock(
        exists=Mock(side_effect=[True, False]),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value='ofs://test_vol/test-bucket/test-user/src_dir'),
        join=Mock(return_value='ofs://test_vol/test-bucket/test-user/dst_dir/source.txt'),
        normpath=Mock(
          side_effect=[
            'ofs://test_vol/test-bucket/test-user/src_dir/source.txt',
            'ofs://test_vol/test-bucket/test-user/dst_dir',
            'ofs://test_vol/test-bucket/test-user/dst_dir',
          ]
        ),
        copy=Mock(return_value=('ofs://test_vol/test-bucket/test-user/src_dir/source.txt')),
        user=Mock(),
      ),
    )
    response = copy(request)

    assert response.status_code == 500
    assert json.loads(response.content) == {'skipped_files': 'ofs://test_vol/test-bucket/test-user/src_dir/source.txt'}
    request.fs.copy.assert_called_once_with(
      'ofs://test_vol/test-bucket/test-user/src_dir/source.txt',
      'ofs://test_vol/test-bucket/test-user/dst_dir',
      recursive=True,
      owner=request.user,
    )

  def test_copy_no_source_path(self):
    request = Mock(
      method='POST',
      POST={'destination_path': 's3a://test-bucket/test-user/dst_dir'},
      fs=Mock(),
    )
    response = copy(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Missing required parameters: source_path and destination_path are required.'

  def test_copy_no_destination_path(self):
    request = Mock(
      method='POST',
      POST={'source_path': 's3a://test-bucket/test-user/src_dir/source.txt'},
      fs=Mock(),
    )
    response = copy(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Missing required parameters: source_path and destination_path are required.'

  def test_copy_identical_paths(self):
    request = Mock(
      method='POST',
      POST={
        'source_path': 's3a://test-bucket/test-user/src_dir/source.txt',
        'destination_path': 's3a://test-bucket/test-user/src_dir/source.txt',
      },
      fs=Mock(
        normpath=Mock(side_effect=['s3a://test-bucket/test-user/src_dir/source.txt', 's3a://test-bucket/test-user/src_dir/source.txt']),
      ),
    )
    response = copy(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Source and destination paths must be different.'

  def test_copy_source_path_does_not_exist(self):
    request = Mock(
      method='POST',
      POST={
        'source_path': 's3a://test-bucket/test-user/src_dir/source.txt',
        'destination_path': 's3a://test-bucket/test-user/dst_dir',
      },
      fs=Mock(
        exists=Mock(return_value=False),
        normpath=Mock(side_effect=['s3a://test-bucket/test-user/src_dir/source.txt', 's3a://test-bucket/test-user/dst_dir']),
      ),
    )
    response = copy(request)

    assert response.status_code == 404
    assert response.content.decode('utf-8') == 'Source file or folder does not exist.'

  def test_copy_destination_not_a_directory(self):
    request = Mock(
      method='POST',
      POST={
        'source_path': 's3a://test-bucket/test-user/src_dir/source.txt',
        'destination_path': 's3a://test-bucket/test-user/dst_dir',
      },
      fs=Mock(
        exists=Mock(return_value=True),
        isdir=Mock(return_value=False),
        normpath=Mock(side_effect=['s3a://test-bucket/test-user/src_dir/source.txt', 's3a://test-bucket/test-user/dst_dir']),
      ),
    )
    response = copy(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Destination path must be a directory.'

  def test_copy_destination_is_parent_of_source(self):
    request = Mock(
      method='POST',
      POST={
        'source_path': 's3a://test-bucket/test-user/src_dir/source.txt',
        'destination_path': 's3a://test-bucket/test-user/src_dir',
      },
      fs=Mock(
        exists=Mock(return_value=True),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value='s3a://test-bucket/test-user/src_dir'),
        normpath=Mock(
          side_effect=[
            's3a://test-bucket/test-user/src_dir/source.txt',
            's3a://test-bucket/test-user/src_dir',
            's3a://test-bucket/test-user/src_dir',
          ]
        ),
      ),
    )
    response = copy(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Destination cannot be the parent directory of source.'

  def test_copy_file_already_exists_at_destination(self):
    request = Mock(
      method='POST',
      POST={
        'source_path': 's3a://test-bucket/test-user/src_dir/source.txt',
        'destination_path': 's3a://test-bucket/test-user/dst_dir',
      },
      fs=Mock(
        exists=Mock(side_effect=[True, True]),
        isdir=Mock(return_value=True),
        parent_path=Mock(return_value='s3a://test-bucket/test-user/src_dir'),
        join=Mock(return_value='s3a://test-bucket/test-user/dst_dir/source.txt'),
        normpath=Mock(
          side_effect=[
            's3a://test-bucket/test-user/src_dir/source.txt',
            's3a://test-bucket/test-user/dst_dir',
            's3a://test-bucket/test-user/dst_dir',
          ]
        ),
      ),
    )
    response = copy(request)

    assert response.status_code == 409
    assert response.content.decode('utf-8') == 'File or folder already exists at destination path.'


class TestListAPI:
  def _create_mock_file_stats(self, name, path, size, user, group):
    mock_stats = MagicMock()
    mock_stats.path = path
    mock_stats.name = name
    mock_stats.size = size
    mock_stats.atime = 0
    mock_stats.mtime = 0
    mock_stats.type = 'file'
    mock_stats.user = user
    mock_stats.group = group
    mock_stats.mode = 33188
    mock_stats.to_json_dict = Mock(
      return_value={
        'path': path,
        'aclBit': False,
        'size': size,
        'atime': 0,
        'mtime': 0,
        'type': 'file',
        'user': user,
        'group': group,
        'mode': 33188,
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
    with patch('filebrowser.api.is_admin') as is_admin:
      is_admin.return_value = False

      file1_stats = self._create_mock_file_stats(
        name='file1.txt', path='s3a://test-bucket/test-user/test-dir/file1.txt', size=100, user='user1', group='group1'
      )
      file2_stats = self._create_mock_file_stats(
        name='file2.txt', path='s3a://test-bucket/test-user/test-dir/file2.txt', size=200, user='user2', group='group2'
      )

      all_stats = [file2_stats, file1_stats]

      request = Mock(
        method='GET',
        GET={'pagenum': '1', 'pagesize': '30', 'path': 's3a://test-bucket/test-user/test-dir', 'sortby': 'name', 'descending': 'False'},
        user=Mock(has_hue_permission=Mock(return_value=False)),
        fs=Mock(
          listdir_stats=Mock(return_value=all_stats),
          do_as_user=Mock(return_value=all_stats),
          isdir=Mock(return_value=True),
          normpath=Mock(side_effect=['s3a://test-bucket/test-user/test-dir/file1.txt', 's3a://test-bucket/test-user/test-dir/file2.txt']),
        ),
      )

      mock_paginator = self._create_mock_paginator(all_stats)

      with patch('filebrowser.api.Paginator', return_value=mock_paginator) as mock_paginator:
        response = listdir_paged(request)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data == {
          'files': [
            {
              'path': 's3a://test-bucket/test-user/test-dir/file1.txt',
              'aclBit': False,
              'size': 200,
              'atime': 0,
              'mtime': 0,
              'type': 'file',
              'user': 'user2',
              'group': 'group2',
              'mode': 33188,
              'rwx': '-rw-r--r--+',
            },
            {
              'path': 's3a://test-bucket/test-user/test-dir/file2.txt',
              'aclBit': False,
              'size': 100,
              'atime': 0,
              'mtime': 0,
              'type': 'file',
              'user': 'user1',
              'group': 'group1',
              'mode': 33188,
              'rwx': '-rw-r--r--+',
            },
          ],
          'page': {'page_number': 1, 'page_size': 30, 'total_pages': 1, 'total_size': 2},
        }

        # Assert correct sorting
        assert response_data['files'][0]['path'] == 's3a://test-bucket/test-user/test-dir/file1.txt'
        assert response_data['files'][1]['path'] == 's3a://test-bucket/test-user/test-dir/file2.txt'

  def test_listdir_paged_sorting_by_size_descending(self):
    with patch('filebrowser.api.is_admin') as is_admin:
      is_admin.return_value = False

      file1_stats = self._create_mock_file_stats(
        name='file1.txt', path='s3a://test-bucket/test-user/test-dir/file1.txt', size=100, user='user1', group='group1'
      )
      file2_stats = self._create_mock_file_stats(
        name='file2.txt', path='s3a://test-bucket/test-user/test-dir/file2.txt', size=200, user='user2', group='group2'
      )
      file3_stats = self._create_mock_file_stats(
        name='file3.txt', path='s3a://test-bucket/test-user/test-dir/file3.txt', size=300, user='user3', group='group3'
      )
      file4_stats = self._create_mock_file_stats(
        name='file4.txt', path='s3a://test-bucket/test-user/test-dir/file4.txt', size=400, user='user4', group='group4'
      )

      all_stats = [file1_stats, file2_stats, file3_stats, file4_stats]

      request = Mock(
        method='GET',
        GET={
          'pagenum': '1',
          'pagesize': '30',
          'path': 's3a://test-bucket/test-user/test-dir',
          'sortby': 'name',
          'descending': 'True',
        },
        user=Mock(has_hue_permission=Mock(return_value=False)),
        fs=Mock(
          listdir_stats=Mock(side_effect=[all_stats, all_stats]),
          do_as_user=Mock(return_value=all_stats),
          isdir=Mock(return_value=True),
          normpath=Mock(
            side_effect=[
              's3a://test-bucket/test-user/test-dir/file1.txt',
              's3a://test-bucket/test-user/test-dir/file2.txt',
              's3a://test-bucket/test-user/test-dir/file3.txt',
              's3a://test-bucket/test-user/test-dir/file4.txt',
            ]
          ),
        ),
      )

      mock_paginator = self._create_mock_paginator(sorted(all_stats, key=lambda x: x.size, reverse=True))

      with patch('filebrowser.api.Paginator', return_value=mock_paginator) as mock_paginator:
        response = listdir_paged(request)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert 'files' in response_data
        assert len(response_data['files']) == 4

        # Assert correct sorting
        assert response_data['files'][0]['size'] == 400
        assert response_data['files'][1]['size'] == 300
        assert response_data['files'][2]['size'] == 200
        assert response_data['files'][3]['size'] == 100

  def test_listdir_paged_invalid_path(self):
    request = Mock(
      method='GET',
      GET={'pagenum': '1', 'pagesize': '30', 'path': 's3a://test-bucket/test-user/test-dir/test-file'},
      fs=Mock(
        isdir=Mock(return_value=False),
      ),
    )

    response = listdir_paged(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 's3a://test-bucket/test-user/test-dir/test-file is not a directory.'

  def test_listdir_paged_error_while_listing_bucket(self):
    with patch('filebrowser.api.is_admin') as is_admin:
      is_admin.return_value = False

      request = Mock(
        method='GET',
        GET={'pagenum': '1', 'pagesize': '30', 'path': 's3a://test-bucket/'},
        fs=Mock(
          isdir=Mock(return_value=True),
          listdir_stats=Mock(side_effect=S3ListAllBucketsException('Failed to list all buckets')),
          do_as_user=Mock(side_effect=S3ListAllBucketsException('Failed to list all buckets')),
        ),
      )

      response = listdir_paged(request)

      assert response.status_code == 403
      assert response.content.decode('utf-8') == 'Bucket listing is not allowed: Failed to list all buckets'
