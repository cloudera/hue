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

from filebrowser.api import rename, upload_file
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
            print(response.content)
            response_data = json.loads(response.content)

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

        assert response.status_code == 400
        assert response.content.decode('utf-8') == 'File type ".txt" is not allowed. Please choose a file with a different type.'
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

        assert response.status_code == 413
        assert response.content.decode('utf-8') == 'File exceeds maximum allowed size of 5 bytes. Please upload a smaller file.'
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
        assert response.content.decode('utf-8') == 'The file path s3a://test-bucket/test-user/test_file.txt already exists.'
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


class TestRenameAPI:
  def test_rename_success(self):
    request = Mock(
      method='POST',
      POST={'source_path': 's3a://test-bucket/test-user/source.txt', 'destination_path': 'new_name.txt'},
      body=Mock(),
      fs=Mock(
        exists=Mock(return_value=False),
        join=Mock(return_value='s3a://test-bucket/test-user/new_name.txt'),
        rename=Mock(),
      ),
    )
    reset = RESTRICT_FILE_EXTENSIONS.set_for_testing('')
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
      body=Mock(),
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
      body=Mock(),
      fs=Mock(
        rename=Mock(),
      ),
    )
    reset = RESTRICT_FILE_EXTENSIONS.set_for_testing('')
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
      body=Mock(),
      fs=Mock(
        rename=Mock(),
        exists=Mock(return_value=True),
        join=Mock(return_value='s3a://test-bucket/test-user/new_name.txt'),
      ),
    )
    reset = RESTRICT_FILE_EXTENSIONS.set_for_testing('')
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
      body=Mock(),
      fs=Mock(
        rename=Mock(),
      ),
    )
    reset = RESTRICT_FILE_EXTENSIONS.set_for_testing('')
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
      body=Mock(),
      fs=Mock(
        rename=Mock(),
      ),
    )
    reset = RESTRICT_FILE_EXTENSIONS.set_for_testing('')
    try:
      response = rename(request)

      assert response.status_code == 400
      assert response.content.decode('utf-8') == 'Missing required parameters: source_path and destination_path'
    finally:
      reset()
