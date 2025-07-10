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

from filebrowser.conf import ALLOW_FILE_EXTENSIONS, MAX_FILE_SIZE_UPLOAD_LIMIT, RESTRICT_FILE_EXTENSIONS
from filebrowser.schemas import UploadFileSchema


class TestUploadFileSchema:
  def test_valid_schema(self):
    mock_file = MagicMock()
    schema = UploadFileSchema(file=mock_file, filename="test.csv", filesize=1024, destination_path="/tmp/test", overwrite=False)

    assert schema.file == mock_file
    assert schema.filename == "test.csv"
    assert schema.filesize == 1024
    assert schema.destination_path == "/tmp/test"
    assert schema.overwrite is False

  def test_empty_filename(self):
    mock_file = MagicMock()

    with pytest.raises(ValidationError) as exc_info:
      UploadFileSchema(file=mock_file, filename="", filesize=1024, destination_path="/tmp/test")

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "filename" in str(errors[0]["loc"])
    assert "Filename cannot be empty" in str(errors[0]["msg"])

  def test_filename_with_path_separator(self):
    mock_file = MagicMock()

    with pytest.raises(ValidationError) as exc_info:
      UploadFileSchema(file=mock_file, filename="folder/test.csv", filesize=1024, destination_path="/tmp/test")

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "filename" in str(errors[0]["loc"])
    assert "Path separators are not allowed" in str(errors[0]["msg"])

  def test_file_too_large(self):
    resets = [MAX_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(1024)]  # 1 KiB limit
    try:
      mock_file = MagicMock()

      with pytest.raises(ValidationError) as exc_info:
        UploadFileSchema(
          file=mock_file,
          filename="test.csv",
          filesize=1024 * 1024,  # 1 MiB
          destination_path="/tmp/test",
        )

      errors = exc_info.value.errors()
      assert len(errors) == 1
      assert "filesize" in str(errors[0]["loc"])
      assert "File too large" in str(errors[0]["msg"])
      assert "Maximum file size is 1024 bytes" in str(errors[0]["msg"])
    finally:
      for reset in resets:
        reset()

  def test_no_file_size_limit(self):
    resets = [MAX_FILE_SIZE_UPLOAD_LIMIT.set_for_testing(-1)]
    try:
      mock_file = MagicMock()

      # Should accept any file size when limit is -1
      schema = UploadFileSchema(
        file=mock_file,
        filename="test.csv",
        filesize=1024 * 1024 * 1024 * 100,  # 100 GiB
        destination_path="/tmp/test",
      )
      assert schema.filesize == 1024 * 1024 * 1024 * 100
    finally:
      for reset in resets:
        reset()

  def test_empty_destination_path(self):
    mock_file = MagicMock()

    with pytest.raises(ValidationError) as exc_info:
      UploadFileSchema(file=mock_file, filename="test.csv", filesize=1024, destination_path="")

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert "destination_path" in str(errors[0]["loc"])
    assert "Destination path cannot be empty" in str(errors[0]["msg"])

  def test_restricted_file_extension(self):
    resets = [RESTRICT_FILE_EXTENSIONS.set_for_testing([".exe", ".bat", ".csv"])]
    try:
      mock_file = MagicMock()

      with pytest.raises(ValidationError) as exc_info:
        UploadFileSchema(file=mock_file, filename="test.csv", filesize=1024, destination_path="/tmp/test")

      errors = exc_info.value.errors()
      assert len(errors) == 1
      assert "filename" in str(errors[0]["loc"])
      assert "is restricted" in str(errors[0]["msg"])
    finally:
      for reset in resets:
        reset()

  def test_allowed_file_extension(self):
    resets = [ALLOW_FILE_EXTENSIONS.set_for_testing([".csv", ".txt"]), RESTRICT_FILE_EXTENSIONS.set_for_testing(None)]
    try:
      mock_file = MagicMock()

      # Should pass for allowed extension
      schema = UploadFileSchema(file=mock_file, filename="test.csv", filesize=1024, destination_path="/tmp/test")
      assert schema.filename == "test.csv"

      # Should fail for non-allowed extension
      with pytest.raises(ValidationError) as exc_info:
        UploadFileSchema(file=mock_file, filename="test.exe", filesize=1024, destination_path="/tmp/test")

      errors = exc_info.value.errors()
      assert "is not permitted" in str(errors[0]["msg"])
    finally:
      for reset in resets:
        reset()
