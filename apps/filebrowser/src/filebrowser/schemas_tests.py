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

import pytest
from pydantic import ValidationError

from filebrowser.conf import ALLOW_FILE_EXTENSIONS, RESTRICT_FILE_EXTENSIONS
from filebrowser.schemas import RenameSchema


class TestRenameSchema:
  def test_valid_rename_same_directory(self):
    data = {"source_path": "/user/test/documents/report.txt", "destination_path": "/user/test/documents/report_v2.txt"}
    schema = RenameSchema(**data)
    assert schema.source_path == "/user/test/documents/report.txt"
    assert schema.destination_path == "/user/test/documents/report_v2.txt"

  def test_valid_rename_relative_path(self):
    data = {"source_path": "/user/test/documents/report.txt", "destination_path": "report_v2.txt"}
    schema = RenameSchema(**data)
    assert schema.source_path == "/user/test/documents/report.txt"
    assert schema.destination_path == "report_v2.txt"

  def test_valid_rename_different_directory(self):
    data = {"source_path": "/user/test/documents/report.txt", "destination_path": "/user/test/archive/report.txt"}
    schema = RenameSchema(**data)
    assert schema.source_path == "/user/test/documents/report.txt"
    assert schema.destination_path == "/user/test/archive/report.txt"

  def test_whitespace_trimming(self):
    data = {"source_path": "  /user/test/file.txt  ", "destination_path": "  /user/test/file_new.txt  "}
    schema = RenameSchema(**data)
    assert schema.source_path == "/user/test/file.txt"
    assert schema.destination_path == "/user/test/file_new.txt"

  def test_empty_source_path(self):
    data = {"source_path": "", "destination_path": "/user/test/file.txt"}
    with pytest.raises(ValidationError) as exc_info:
      RenameSchema(**data)
    assert "Path cannot be empty" in str(exc_info.value)

  def test_empty_destination_path(self):
    data = {"source_path": "/user/test/file.txt", "destination_path": ""}
    with pytest.raises(ValidationError) as exc_info:
      RenameSchema(**data)
    assert "Path cannot be empty" in str(exc_info.value)

  def test_whitespace_only_paths(self):
    data = {"source_path": "   ", "destination_path": "/user/test/file.txt"}
    with pytest.raises(ValidationError) as exc_info:
      RenameSchema(**data)
    assert "Path cannot be empty" in str(exc_info.value)

  def test_path_traversal_in_source(self):
    data = {"source_path": "/user/test/../admin/file.txt", "destination_path": "/user/test/file.txt"}
    with pytest.raises(ValidationError) as exc_info:
      RenameSchema(**data)
    assert "Path traversal patterns are not allowed" in str(exc_info.value)

  def test_path_traversal_in_destination(self):
    data = {"source_path": "/user/test/file.txt", "destination_path": "/user/test/../admin/file.txt"}
    with pytest.raises(ValidationError) as exc_info:
      RenameSchema(**data)
    assert "Path traversal patterns are not allowed" in str(exc_info.value)

  def test_hash_character_in_destination(self):
    data = {"source_path": "/user/test/file.txt", "destination_path": "/user/test/file#new.txt"}
    with pytest.raises(ValidationError) as exc_info:
      RenameSchema(**data)
    assert "Hashes are not allowed in file or directory names" in str(exc_info.value)

  def test_hash_character_allowed_in_source(self):
    data = {"source_path": "/user/test/file#old.txt", "destination_path": "/user/test/file_new.txt"}
    schema = RenameSchema(**data)
    assert schema.source_path == "/user/test/file#old.txt"

  def test_file_extension_change_without_restrictions(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing(None)
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing(None)

    try:
      data = {"source_path": "/user/test/document.txt", "destination_path": "/user/test/document.pdf"}
      schema = RenameSchema(**data)
      assert schema.source_path == "/user/test/document.txt"
      assert schema.destination_path == "/user/test/document.pdf"
    finally:
      reset_allow()
      reset_restrict()

  def test_file_extension_change_with_restrict_list(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing(None)
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing([".exe", ".bat", ".cmd"])

    try:
      data = {"source_path": "/user/test/script.txt", "destination_path": "/user/test/script.exe"}
      with pytest.raises(ValidationError) as exc_info:
        RenameSchema(**data)
      assert "is restricted" in str(exc_info.value)
    finally:
      reset_allow()
      reset_restrict()

  def test_file_extension_change_with_allow_list(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing([".txt", ".csv", ".json"])
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing(None)

    try:
      # Allowed extension change
      data = {"source_path": "/user/test/data.txt", "destination_path": "/user/test/data.csv"}
      schema = RenameSchema(**data)
      assert schema.destination_path == "/user/test/data.csv"

      # Not allowed extension change
      data = {"source_path": "/user/test/data.txt", "destination_path": "/user/test/data.xml"}
      with pytest.raises(ValidationError) as exc_info:
        RenameSchema(**data)
      assert "is not permitted" in str(exc_info.value)
    finally:
      reset_allow()
      reset_restrict()

  def test_same_extension_case_insensitive(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing([".txt"])
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing(None)

    try:
      data = {"source_path": "/user/test/document.TXT", "destination_path": "/user/test/document_renamed.txt"}
      schema = RenameSchema(**data)
      assert schema.destination_path == "/user/test/document_renamed.txt"
    finally:
      reset_allow()
      reset_restrict()

  def test_rename_directory(self):
    data = {"source_path": "/user/test/old_folder", "destination_path": "/user/test/new_folder"}
    schema = RenameSchema(**data)
    assert schema.source_path == "/user/test/old_folder"
    assert schema.destination_path == "/user/test/new_folder"

  def test_special_characters_in_paths(self):
    data = {
      "source_path": "/user/test/file with spaces & special-chars_123.txt",
      "destination_path": "/user/test/file (renamed) @ 2024.txt",
    }
    schema = RenameSchema(**data)
    assert schema.source_path == "/user/test/file with spaces & special-chars_123.txt"
    assert schema.destination_path == "/user/test/file (renamed) @ 2024.txt"

  def test_unicode_characters_in_paths(self):
    data = {"source_path": "/user/test/文档.txt", "destination_path": "/user/test/документ.txt"}
    schema = RenameSchema(**data)
    assert schema.source_path == "/user/test/文档.txt"
    assert schema.destination_path == "/user/test/документ.txt"

  def test_very_long_paths(self):
    long_path = "/user/test/" + "a" * 200 + "/file.txt"
    data = {"source_path": long_path, "destination_path": long_path + "_new"}
    schema = RenameSchema(**data)
    assert schema.source_path == long_path
    assert schema.destination_path == long_path + "_new"

  def test_multiple_validation_errors(self):
    data = {"source_path": "  ", "destination_path": "../etc/passwd"}
    with pytest.raises(ValidationError) as exc_info:
      RenameSchema(**data)
    error_str = str(exc_info.value)
    assert "Path cannot be empty" in error_str
    assert "Path traversal patterns are not allowed" in error_str

  def test_s3_paths(self):
    data = {"source_path": "s3a://bucket/folder/file.txt", "destination_path": "s3a://bucket/folder/file_renamed.txt"}
    schema = RenameSchema(**data)
    assert schema.source_path == "s3a://bucket/folder/file.txt"
    assert schema.destination_path == "s3a://bucket/folder/file_renamed.txt"

  def test_both_allow_and_restrict_lists_configured(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing([".txt", ".csv", ".exe"])
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing([".exe", ".bat"])

    try:
      # File in allow list but also in restrict list
      data = {"source_path": "/user/test/script.txt", "destination_path": "/user/test/script.exe"}
      with pytest.raises(ValidationError) as exc_info:
        RenameSchema(**data)
      assert "is restricted" in str(exc_info.value)

      # File in allow list and not in restrict list
      data = {"source_path": "/user/test/data.txt", "destination_path": "/user/test/data.csv"}
      schema = RenameSchema(**data)
      assert schema.destination_path == "/user/test/data.csv"
    finally:
      reset_allow()
      reset_restrict()
