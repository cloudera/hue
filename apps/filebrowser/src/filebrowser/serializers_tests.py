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

from filebrowser.serializers import UploadFileSerializer


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
    """Test serializer handles numeric boolean values correctly."""
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
