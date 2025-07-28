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

from filebrowser.conf import ALLOW_FILE_EXTENSIONS, RESTRICT_FILE_EXTENSIONS
from filebrowser.serializers import RenameSerializer, UploadFileSerializer


class TestUploadFileSerializer:
  def test_valid_data(self):
    serializer = UploadFileSerializer(data={"destination_path": "s3a://test_bucket/test/uploads/"})

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data["destination_path"] == "s3a://test_bucket/test/uploads/"
    assert serializer.validated_data["overwrite"] is False  # Default value

  def test_valid_data_with_overwrite(self):
    serializer = UploadFileSerializer(data={"destination_path": "s3a://test_bucket/test/uploads/", "overwrite": True})

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data["destination_path"] == "s3a://test_bucket/test/uploads/"
    assert serializer.validated_data["overwrite"] is True

  def test_missing_destination_path(self):
    serializer = UploadFileSerializer(data={})

    assert not serializer.is_valid()
    assert "destination_path" in serializer.errors
    assert any("required" in str(error).lower() for error in serializer.errors["destination_path"])

  def test_empty_destination_path(self):
    serializer = UploadFileSerializer(data={"destination_path": ""})

    assert not serializer.is_valid()
    assert "destination_path" in serializer.errors
    assert any("blank" in str(error).lower() for error in serializer.errors["destination_path"])

  def test_none_destination_path(self):
    serializer = UploadFileSerializer(data={"destination_path": None})

    assert not serializer.is_valid()
    assert "destination_path" in serializer.errors
    assert any("null" in str(error).lower() or "none" in str(error).lower() for error in serializer.errors["destination_path"])

  def test_overwrite_string_values(self):
    # Test with string 'true'
    serializer = UploadFileSerializer(data={"destination_path": "s3a://test_bucket/test/", "overwrite": "true"})

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data["overwrite"] is True

    # Test with string 'false'
    serializer = UploadFileSerializer(data={"destination_path": "s3a://test_bucket/test/", "overwrite": "false"})

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data["overwrite"] is False

  def test_overwrite_numeric_values(self):
    # Test with 1
    serializer = UploadFileSerializer(data={"destination_path": "s3a://test_bucket/test/", "overwrite": 1})

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data["overwrite"] is True

    # Test with 0
    serializer = UploadFileSerializer(data={"destination_path": "s3a://test_bucket/test/", "overwrite": 0})

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data["overwrite"] is False

  def test_invalid_overwrite_value(self):
    serializer = UploadFileSerializer(data={"destination_path": "s3a://test_bucket/test/", "overwrite": "invalid"})

    assert not serializer.is_valid()
    assert "overwrite" in serializer.errors

  def test_extra_fields_ignored(self):
    serializer = UploadFileSerializer(
      data={
        "destination_path": "s3a://test_bucket/test/uploads/",
        "overwrite": False,
        "extra_field": "should be ignored",
        "another_field": 123,
      }
    )

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert "extra_field" not in serializer.validated_data
    assert "another_field" not in serializer.validated_data
    assert len(serializer.validated_data) == 2  # Only destination_path and overwrite

  def test_various_path_formats(self):
    valid_paths = [
      "/user/test/",
      "/tmp/uploads/",
      "/home/user/documents/",
      "hdfs:///user/test/",
      "s3a://bucket/path/",
      "s3a://test_bucket/test folder/uploads/",  # Path with spaces
      "abfs://container@account.dfs.core.windows.net/path/",
      "./relative/path/",
      "../parent/path/",
    ]

    for path in valid_paths:
      serializer = UploadFileSerializer(data={"destination_path": path})
      assert serializer.is_valid(), f"Path '{path}' should be valid. Errors: {serializer.errors}"
      assert serializer.validated_data["destination_path"] == path


class TestRenameSerializer:
  def test_valid_data_absolute_paths(self):
    serializer = RenameSerializer(
      data={"source_path": "/user/test/documents/report.txt", "destination_path": "/user/test/documents/report_v2.txt"}
    )

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data["source_path"] == "/user/test/documents/report.txt"
    assert serializer.validated_data["destination_path"] == "/user/test/documents/report_v2.txt"

  def test_valid_data_relative_destination(self):
    serializer = RenameSerializer(data={"source_path": "/user/test/documents/report.txt", "destination_path": "report_v2.txt"})

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"
    assert serializer.validated_data["source_path"] == "/user/test/documents/report.txt"
    assert serializer.validated_data["destination_path"] == "report_v2.txt"

  def test_missing_source_path(self):
    serializer = RenameSerializer(data={"destination_path": "/user/test/file_new.txt"})

    assert not serializer.is_valid()
    assert "source_path" in serializer.errors
    assert any("required" in str(error).lower() for error in serializer.errors["source_path"])

  def test_missing_destination_path(self):
    serializer = RenameSerializer(data={"source_path": "/user/test/file.txt"})

    assert not serializer.is_valid()
    assert "destination_path" in serializer.errors
    assert any("required" in str(error).lower() for error in serializer.errors["destination_path"])

  def test_empty_source_path(self):
    serializer = RenameSerializer(data={"source_path": "", "destination_path": "/user/test/file_new.txt"})

    assert not serializer.is_valid()
    assert "source_path" in serializer.errors
    assert any("blank" in str(error).lower() for error in serializer.errors["source_path"])

  def test_empty_destination_path(self):
    serializer = RenameSerializer(data={"source_path": "/user/test/file.txt", "destination_path": ""})

    assert not serializer.is_valid()
    assert "destination_path" in serializer.errors
    assert any("blank" in str(error).lower() for error in serializer.errors["destination_path"])

  def test_null_values(self):
    serializer = RenameSerializer(data={"source_path": None, "destination_path": None})

    assert not serializer.is_valid()
    assert "source_path" in serializer.errors
    assert "destination_path" in serializer.errors

  def test_schema_validation_integration(self):
    # Test path traversal detection
    serializer = RenameSerializer(data={"source_path": "/user/test/../admin/file.txt", "destination_path": "/user/test/file.txt"})

    assert not serializer.is_valid()
    errors_str = str(serializer.errors)
    assert "Path traversal patterns are not allowed" in errors_str

  def test_hash_character_validation(self):
    serializer = RenameSerializer(data={"source_path": "/user/test/file.txt", "destination_path": "/user/test/file#new.txt"})

    assert not serializer.is_valid()
    errors_str = str(serializer.errors)
    assert "Hashes are not allowed" in errors_str

  def test_file_extension_restriction(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing(None)
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing([".exe", ".bat"])

    try:
      serializer = RenameSerializer(data={"source_path": "/user/test/script.txt", "destination_path": "/user/test/script.exe"})

      assert not serializer.is_valid()
      errors_str = str(serializer.errors)
      assert "is restricted" in errors_str
    finally:
      reset_allow()
      reset_restrict()

  def test_file_extension_allow_list(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing([".txt", ".csv"])
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing(None)

    try:
      # Not allowed extension
      serializer = RenameSerializer(data={"source_path": "/user/test/data.txt", "destination_path": "/user/test/data.xml"})

      assert not serializer.is_valid()
      errors_str = str(serializer.errors)
      assert "is not permitted" in errors_str

      # Allowed extension
      serializer = RenameSerializer(data={"source_path": "/user/test/data.txt", "destination_path": "/user/test/data.csv"})

      assert serializer.is_valid()
    finally:
      reset_allow()
      reset_restrict()

  def test_whitespace_trimming(self):
    serializer = RenameSerializer(data={"source_path": "  /user/test/file.txt  ", "destination_path": "  /user/test/file_new.txt  "})

    assert serializer.is_valid()
    assert serializer.validated_data["source_path"] == "/user/test/file.txt"
    assert serializer.validated_data["destination_path"] == "/user/test/file_new.txt"

  def test_extra_fields_ignored(self):
    serializer = RenameSerializer(
      data={
        "source_path": "/user/test/file.txt",
        "destination_path": "/user/test/file_new.txt",
        "extra_field": "should be ignored",
        "another_field": 123,
      }
    )

    assert serializer.is_valid()
    assert serializer.validated_data["source_path"] == "/user/test/file.txt"
    assert serializer.validated_data["destination_path"] == "/user/test/file_new.txt"
    assert "extra_field" not in serializer.validated_data

  def test_various_path_formats(self):
    valid_paths = [
      ("/user/test/file.txt", "/user/test/file_new.txt"),
      ("s3a://bucket/folder/file.txt", "s3a://bucket/folder/file_new.txt"),
      ("hdfs://namenode:9000/user/file.txt", "hdfs://namenode:9000/user/file_new.txt"),
      ("abfs://container@account/path/file.txt", "abfs://container@account/path/file_new.txt"),
      ("/path with spaces/file.txt", "/path with spaces/file_new.txt"),
      ("/user/test/文档.txt", "/user/test/文档_新.txt"),  # Unicode paths
    ]

    for source, dest in valid_paths:
      serializer = RenameSerializer(data={"source_path": source, "destination_path": dest})
      assert serializer.is_valid(), f"Paths '{source}' -> '{dest}' should be valid. Errors: {serializer.errors}"

  def test_complex_validation_errors(self):
    serializer = RenameSerializer(
      data={
        "source_path": "  ",  # Empty after trimming
        "destination_path": "../etc/passwd#hacked",  # Multiple issues
      }
    )

    assert not serializer.is_valid()
    errors_str = str(serializer.errors)
    # The blank validation happens at serializer level
    assert "blank" in errors_str.lower()

  def test_same_extension_rename(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing([".txt"])
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing([".exe"])

    try:
      serializer = RenameSerializer(data={"source_path": "/user/test/document.txt", "destination_path": "/user/test/document_renamed.txt"})

      assert serializer.is_valid()
    finally:
      reset_allow()
      reset_restrict()

  def test_directory_rename(self):
    serializer = RenameSerializer(data={"source_path": "/user/test/old_folder", "destination_path": "/user/test/new_folder"})

    assert serializer.is_valid()

  def test_special_characters_in_names(self):
    serializer = RenameSerializer(
      data={"source_path": "/user/test/file & document (1).txt", "destination_path": "/user/test/file @ document [2024].txt"}
    )

    assert serializer.is_valid()

  def test_very_long_paths(self):
    long_name = "a" * 200
    serializer = RenameSerializer(
      data={"source_path": f"/user/test/{long_name}/file.txt", "destination_path": f"/user/test/{long_name}/file_new.txt"}
    )

    assert serializer.is_valid()

  def test_validation_error_format(self):
    serializer = RenameSerializer(data={"source_path": "/user/test/file.txt", "destination_path": "/user/test/file#new.txt"})

    assert not serializer.is_valid()
    # Check that errors are in the expected format
    assert isinstance(serializer.errors, dict)
    # The error should be in non_field_errors since it's from model validation
    assert any("Hashes are not allowed" in str(error) for errors in serializer.errors.values() for error in errors)
