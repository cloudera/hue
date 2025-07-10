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

from django.core.files.uploadedfile import SimpleUploadedFile

from filebrowser.conf import RESTRICT_FILE_EXTENSIONS
from filebrowser.schemas import UploadFileSchema
from filebrowser.serializers import UploadFileSerializer


class TestUploadFileSerializer:
  def test_valid_serializer(self):
    test_file = SimpleUploadedFile(name="test_file.csv", content=b"header1,header2\nvalue1,value2", content_type="text/csv")

    serializer = UploadFileSerializer(data={"file": test_file, "destination_path": "/tmp/test", "overwrite": True})

    assert serializer.is_valid(), f"Serializer validation failed: {serializer.errors}"

    # validated_data should be a UploadFileSchema instance
    assert isinstance(serializer.validated_data, UploadFileSchema)
    assert serializer.validated_data.file == test_file
    assert serializer.validated_data.filename == "test_file.csv"
    assert serializer.validated_data.filesize == test_file.size
    assert serializer.validated_data.destination_path == "/tmp/test"
    assert serializer.validated_data.overwrite is True

  def test_missing_file(self):
    serializer = UploadFileSerializer(data={"destination_path": "/tmp/test"})

    assert not serializer.is_valid()
    assert "file" in serializer.errors
    assert "No file was submitted." in str(serializer.errors["file"])

  def test_missing_destination_path(self):
    test_file = SimpleUploadedFile("test.csv", b"content")

    serializer = UploadFileSerializer(data={"file": test_file})

    assert not serializer.is_valid()
    assert "destination_path" in serializer.errors

  def test_default_overwrite_value(self):
    test_file = SimpleUploadedFile("test.csv", b"content")

    serializer = UploadFileSerializer(data={"file": test_file, "destination_path": "/tmp/test"})

    assert serializer.is_valid()
    assert serializer.validated_data.overwrite is False

  def test_pydantic_validation_errors_propagated(self):
    resets = [RESTRICT_FILE_EXTENSIONS.set_for_testing([".csv"])]
    try:
      test_file = SimpleUploadedFile("test.csv", b"content")

      serializer = UploadFileSerializer(data={"file": test_file, "destination_path": "/tmp/test"})

      assert not serializer.is_valid()
      error_messages = str(serializer.errors)
      assert "is restricted" in error_messages
    finally:
      for reset in resets:
        reset()
