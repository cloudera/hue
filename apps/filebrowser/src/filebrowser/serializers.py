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
from pydantic import ValidationError
from rest_framework import serializers

from filebrowser.schemas import (
  CheckExistsSchema,
  CompressFilesSchema,
  CopyOperationSchema,
  CreateDirectorySchema,
  CreateFileSchema,
  DeleteOperationSchema,
  ExtractArchiveSchema,
  GetFileContentsSchema,
  GetStatsSchema,
  GetTrashPathSchema,
  ListDirectorySchema,
  MoveOperationSchema,
  RenameSchema,
  SaveFileSchema,
  SetOwnershipSchema,
  SetPermissionsSchema,
  SetReplicationSchema,
  TrashRestoreSchema,
)


class UploadFileSerializer(serializers.Serializer):
  """
  Validates the query parameters for the file upload API.
  """

  destination_path = serializers.CharField(required=True, allow_blank=False)
  overwrite = serializers.BooleanField(default=False)


class RenameSerializer(serializers.Serializer):
  """
  Validates the parameters for the file/directory rename API.
  """

  source_path = serializers.CharField(required=True, allow_blank=False)
  destination_path = serializers.CharField(required=True, allow_blank=False)

  def validate(self, data):
    try:
      RenameSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())

    return data


class GetFileContentsSerializer(serializers.Serializer):
  """
  Validates the parameters for the file contents API.
  """

  path = serializers.CharField(required=True, allow_blank=False)
  # Range specifiers (mutually exclusive)
  offset = serializers.IntegerField(required=False, min_value=0)
  length = serializers.IntegerField(required=False, min_value=1)
  begin = serializers.IntegerField(required=False, min_value=1)
  end = serializers.IntegerField(required=False, min_value=1)
  # Options
  encoding = serializers.CharField(required=False)
  compression = serializers.CharField(required=False)
  read_until_newline = serializers.BooleanField(default=False)

  def validate(self, data):
    try:
      GetFileContentsSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class DownloadFileSerializer(serializers.Serializer):
  """
  Validates the parameters for the file download API.
  """

  path = serializers.CharField(required=True, allow_blank=False, help_text="Path to the file to download")
  disposition = serializers.ChoiceField(
    choices=["attachment", "inline"],
    default="attachment",
    help_text="Content-Disposition type: 'attachment' forces download, 'inline' attempts browser display",
  )

  def validate_path(self, value):
    if not value or value.strip() != value:
      raise serializers.ValidationError("Path cannot be empty or contain only whitespace")

    if ".." in value or value.startswith("~"):
      raise serializers.ValidationError("Invalid path: path traversal patterns are not allowed")

    return value


class CreateFileSerializer(serializers.Serializer):
  """
  Validates the parameters for the file creation API.
  """

  path = serializers.CharField(required=True, allow_blank=False, help_text="Path where the file should be created")
  overwrite = serializers.BooleanField(default=False, help_text="Whether to overwrite if file exists")
  encoding = serializers.CharField(default="utf-8", help_text="Character encoding for the file")
  initial_content = serializers.CharField(required=False, help_text="Initial content to write to the file")

  def validate(self, data):
    try:
      CreateFileSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class SaveFileSerializer(serializers.Serializer):
  """
  Validates the parameters for the file save/edit API.
  """

  path = serializers.CharField(required=True, allow_blank=False, help_text="Path to the file to save")
  contents = serializers.CharField(required=True, help_text="File contents to save")
  encoding = serializers.CharField(default="utf-8", help_text="Character encoding for the file")
  create_parent_dirs = serializers.BooleanField(default=False, help_text="Create parent directories if they don't exist")

  def validate(self, data):
    try:
      SaveFileSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class ListDirectorySerializer(serializers.Serializer):
  """
  Validates the parameters for the directory listing API.
  """

  path = serializers.CharField(default="/", help_text="Directory path to list")
  pagenum = serializers.IntegerField(default=1, min_value=1, max_value=10000, help_text="Page number (1-10000)")
  pagesize = serializers.IntegerField(default=30, min_value=1, max_value=1000, help_text="Items per page (1-1000)")
  sortby = serializers.ChoiceField(
    choices=["name", "size", "type", "mtime", "atime", "user", "group"],
    default="name",
    help_text="Sort by field",
  )
  descending = serializers.BooleanField(default=False, help_text="Sort in descending order")
  filter = serializers.CharField(required=False, max_length=255, help_text="Filter results by filename substring")

  def validate(self, data):
    try:
      ListDirectorySchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class CreateDirectorySerializer(serializers.Serializer):
  """
  Validates the parameters for the directory creation API.
  """

  path = serializers.CharField(required=True, allow_blank=False, help_text="Full path of the directory to create")

  def validate(self, data):
    try:
      CreateDirectorySchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class GetStatsSerializer(serializers.Serializer):
  """
  Validates the parameters for the path statistics API.
  """

  path = serializers.CharField(required=True, allow_blank=False)
  include_content_summary = serializers.BooleanField(default=False)

  def validate(self, data):
    try:
      GetStatsSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class CheckExistsSerializer(serializers.Serializer):
  """Serializer for checking if paths exist."""

  paths = serializers.ListField(child=serializers.CharField(), required=True, min_length=1)

  def validate(self, data):
    try:
      CheckExistsSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class CopyOperationSerializer(serializers.Serializer):
  """Serializer for copy operation."""

  source_paths = serializers.ListField(child=serializers.CharField(), required=True, min_length=1)
  destination_path = serializers.CharField(required=True, allow_blank=False)

  def validate(self, data):
    try:
      CopyOperationSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class MoveOperationSerializer(serializers.Serializer):
  """Serializer for move operation."""

  source_paths = serializers.ListField(child=serializers.CharField(), required=True, min_length=1)
  destination_path = serializers.CharField(required=True, allow_blank=False)

  def validate(self, data):
    try:
      MoveOperationSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class DeleteOperationSerializer(serializers.Serializer):
  """Serializer for delete operation."""

  paths = serializers.ListField(child=serializers.CharField(), required=True, min_length=1)
  skip_trash = serializers.BooleanField(default=False)

  def validate(self, data):
    try:
      DeleteOperationSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class TrashRestoreSerializer(serializers.Serializer):
  """Serializer for restoring from trash."""

  paths = serializers.ListField(child=serializers.CharField(), required=True, min_length=1)

  def validate(self, data):
    try:
      TrashRestoreSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class SetPermissionsSerializer(serializers.Serializer):
  """Serializer for setting file/directory permissions."""

  paths = serializers.ListField(child=serializers.CharField(), required=True, min_length=1)
  mode = serializers.CharField(required=False)
  recursive = serializers.BooleanField(default=False)
  # Individual permission fields
  user_read = serializers.BooleanField(required=False)
  user_write = serializers.BooleanField(required=False)
  user_execute = serializers.BooleanField(required=False)
  group_read = serializers.BooleanField(required=False)
  group_write = serializers.BooleanField(required=False)
  group_execute = serializers.BooleanField(required=False)
  other_read = serializers.BooleanField(required=False)
  other_write = serializers.BooleanField(required=False)
  other_execute = serializers.BooleanField(required=False)
  sticky = serializers.BooleanField(required=False)

  def validate(self, data):
    try:
      SetPermissionsSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class SetOwnershipSerializer(serializers.Serializer):
  """Serializer for setting file/directory ownership."""

  paths = serializers.ListField(child=serializers.CharField(), required=True, min_length=1)
  user = serializers.CharField(required=False)
  group = serializers.CharField(required=False)
  recursive = serializers.BooleanField(default=False)

  def validate(self, data):
    try:
      SetOwnershipSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class SetReplicationSerializer(serializers.Serializer):
  """Serializer for setting replication factor."""

  path = serializers.CharField(required=True, allow_blank=False)
  replication_factor = serializers.IntegerField(required=True, min_value=1)

  def validate(self, data):
    try:
      SetReplicationSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class CompressFilesSerializer(serializers.Serializer):
  """Serializer for compressing files."""

  file_names = serializers.ListField(child=serializers.CharField(), required=True, min_length=1)
  upload_path = serializers.CharField(required=True, allow_blank=False)
  archive_name = serializers.CharField(required=True, allow_blank=False)

  def validate(self, data):
    try:
      CompressFilesSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class ExtractArchiveSerializer(serializers.Serializer):
  """Serializer for extracting archives."""

  upload_path = serializers.CharField(required=True, allow_blank=False)
  archive_name = serializers.CharField(required=True, allow_blank=False)

  def validate(self, data):
    try:
      ExtractArchiveSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data


class GetTrashPathSerializer(serializers.Serializer):
  """Serializer for getting trash path."""

  path = serializers.CharField(required=True, allow_blank=False)

  def validate(self, data):
    try:
      GetTrashPathSchema.model_validate(data)
    except ValidationError as e:
      raise serializers.ValidationError(e.errors())
    return data
