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
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile

from filebrowser.api import copy, get_all_filesystems, mkdir, move, rename, upload_file
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
            {'file_system': 's3a', 'user_home_directory': 's3a://test-bucket/test-user-home-dir/', 'config': {}},
            {'file_system': 'ofs', 'user_home_directory': 'ofs://', 'config': {}},
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
                  'file_system': 'hdfs',
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
                {'file_system': 's3a', 'user_home_directory': 's3a://test-bucket/test-user-home-dir/', 'config': {}},
                {'file_system': 'ofs', 'user_home_directory': 'ofs://', 'config': {}},
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
