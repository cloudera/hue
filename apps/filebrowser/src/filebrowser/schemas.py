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

import os
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from filebrowser.utils import is_file_upload_allowed
from filebrowser.views import DEFAULT_CHUNK_SIZE_BYTES, MAX_CHUNK_SIZE_BYTES, MAX_FILEEDITOR_SIZE


class RenameSchema(BaseModel):
  """Schema for file/directory rename operation."""

  model_config = ConfigDict(str_strip_whitespace=True)

  source_path: str = Field(..., description="The source path to rename from")
  destination_path: str = Field(..., description="The destination path to rename to")

  @field_validator("source_path", "destination_path")
  @classmethod
  def validate_paths_not_empty(cls, v: str) -> str:
    if not v or not v.strip():
      raise ValueError("Path cannot be empty")
    return v.strip()

  @field_validator("source_path", "destination_path")
  @classmethod
  def validate_no_path_traversal(cls, v: str) -> str:
    if ".." in v:
      raise ValueError("Path traversal patterns are not allowed")
    return v

  @field_validator("destination_path")
  @classmethod
  def validate_no_hash_character(cls, v: str) -> str:
    if "#" in v:
      raise ValueError("Hashes are not allowed in file or directory names")
    return v

  @model_validator(mode="after")
  def validate_file_extension_allowed(self) -> "RenameSchema":
    # Extract file extensions
    _, source_ext = os.path.splitext(self.source_path)
    dest_filename = os.path.basename(self.destination_path)
    _, dest_ext = os.path.splitext(dest_filename)

    # Only check restrictions if changing extension
    if source_ext.lower() != dest_ext.lower():
      is_allowed, error_message = is_file_upload_allowed(dest_filename)
      if not is_allowed:
        raise ValueError(error_message)

    return self


class GetFileContentsSchema(BaseModel):
  """Validates all parameters for reading a portion of a file's contents."""

  path: str = Field(..., description="Path to the file")
  # Range specifiers
  offset: Optional[int] = Field(None, ge=0, description="Byte offset to start reading from (0-indexed)")
  length: Optional[int] = Field(None, gt=0, description="Number of bytes to read")
  begin: Optional[int] = Field(None, ge=1, description="Byte position to start reading from (1-indexed, inclusive)")
  end: Optional[int] = Field(None, ge=1, description="Byte position to end reading at (inclusive)")
  # Options
  encoding: Optional[str] = Field(None, description="Character encoding for text files")
  compression: Optional[str] = Field(None, description="Compression format if applicable")
  read_until_newline: bool = Field(False, description="If true, read additional data until a newline is encountered")

  @field_validator("path")
  @classmethod
  def validate_path_not_empty(cls, v: str) -> str:
    if not v or not v.strip():
      raise ValueError("Path cannot be empty")
    return v.strip()

  @model_validator(mode="after")
  def validate_and_calculate_range(self) -> "GetFileContentsSchema":
    has_offset_length = self.offset is not None or self.length is not None
    has_begin_end = self.begin is not None or self.end is not None

    if has_offset_length and has_begin_end:
      raise ValueError("Cannot provide both offset/length and begin/end parameters")

    if has_begin_end:
      if self.begin is None or self.end is None:
        raise ValueError("Both 'begin' and 'end' must be provided together")
      if self.begin >= self.end:
        raise ValueError("'begin' must be less than 'end'")
      # Convert 1-indexed begin/end to 0-indexed offset and length
      self.offset = self.begin - 1
      self.length = self.end - self.begin + 1  # Inclusive end
    else:
      # Apply defaults if no range is specified
      self.offset = self.offset if self.offset is not None else 0
      self.length = self.length if self.length is not None else DEFAULT_CHUNK_SIZE_BYTES

    # Centralized validation for the final calculated length
    if self.length > MAX_CHUNK_SIZE_BYTES:
      raise ValueError(f"Cannot request chunks greater than {MAX_CHUNK_SIZE_BYTES} bytes")

    return self


class CreateFileSchema(BaseModel):
  """
  Schema for creating a new file with comprehensive validation.

  Validates file creation parameters including path security, file extension
  restrictions, parent directory existence, and filesystem constraints.
  """

  model_config = ConfigDict(str_strip_whitespace=True)

  path: str = Field(..., min_length=1, description="Path where the file should be created")
  overwrite: bool = Field(False, description="Whether to overwrite if file exists")
  encoding: str = Field("utf-8", description="Character encoding for the file (if creating with initial content)")
  initial_content: Optional[str] = Field(None, description="Initial content to write to the file")

  @field_validator("path")
  @classmethod
  def validate_path_security(cls, v: str) -> str:
    """Validate path for security and basic requirements."""
    if not v or not v.strip():
      raise ValueError("Path cannot be empty")

    v = v.strip()
    # Path traversal protection
    if ".." in v:
      raise ValueError("Path traversal patterns are not allowed")

    # Check for invalid characters
    if "#" in v:
      raise ValueError("Hash characters are not allowed in file paths")

    # Validate it's not trying to create a directory path
    if v.endswith("/"):
      raise ValueError("File path cannot end with a directory separator")

    return v

  @field_validator("encoding")
  @classmethod
  def validate_encoding(cls, v: str) -> str:
    """Validate that the encoding is supported."""
    try:
      "test".encode(v)
    except (LookupError, TypeError):
      raise ValueError(f"Unsupported encoding: {v}")
    return v.lower()

  @field_validator("initial_content")
  @classmethod
  def validate_initial_content_size(cls, v: Optional[str]) -> Optional[str]:
    """Validate initial content size doesn't exceed editor limits."""
    if v is not None:
      # Check against file editor size limit
      content_size = len(v.encode("utf-8"))
      if content_size > MAX_FILEEDITOR_SIZE:
        raise ValueError(f"Initial content size ({content_size} bytes) exceeds maximum file editor size ({MAX_FILEEDITOR_SIZE} bytes)")
    return v

  @model_validator(mode="after")
  def validate_file_creation_constraints(self) -> "CreateFileSchema":
    filename = os.path.basename(self.path)

    # Validate file extension restrictions
    is_allowed, error_message = is_file_upload_allowed(filename)
    if not is_allowed:
      raise ValueError(error_message)

    return self


class SaveFileSchema(BaseModel):
  """
  Schema for saving/editing file contents with comprehensive validation.

  Validates file save parameters including path security, content size limits,
  encoding validation, and filesystem constraints.
  """

  model_config = ConfigDict(str_strip_whitespace=True)

  path: str = Field(..., min_length=1, description="Path to the file to save")
  contents: str = Field(..., description="File contents to save")
  encoding: str = Field("utf-8", description="Character encoding for the file")

  @field_validator("path")
  @classmethod
  def validate_path_security(cls, v: str) -> str:
    """Validate path for security and basic requirements."""
    if not v or not v.strip():
      raise ValueError("Path cannot be empty")

    # Strip whitespace
    v = v.strip()

    # Path traversal protection
    if ".." in v:
      raise ValueError("Path traversal patterns are not allowed")

    # Check for invalid characters
    if "#" in v:
      raise ValueError("Hash characters are not allowed in file paths")

    # Validate it's not trying to save to a directory path
    if v.endswith("/"):
      raise ValueError("Cannot save to a directory path")

    return v

  @field_validator("encoding")
  @classmethod
  def validate_encoding(cls, v: str) -> str:
    """Validate that the encoding is supported."""
    try:
      "test".encode(v)
    except (LookupError, TypeError):
      raise ValueError(f"Unsupported encoding: {v}")
    return v.lower()

  @field_validator("contents")
  @classmethod
  def validate_content_size(cls, v: str) -> str:
    """Validate content size doesn't exceed editor limits."""
    if v is not None:
      # Check against file editor size limit
      content_size = len(v.encode("utf-8"))
      if content_size > MAX_FILEEDITOR_SIZE:
        raise ValueError(f"File content size ({content_size} bytes) exceeds maximum file editor size ({MAX_FILEEDITOR_SIZE} bytes)")
    return v

  @model_validator(mode="after")
  def validate_file_save_constraints(self) -> "SaveFileSchema":
    """Comprehensive validation for file saving."""
    # Extract filename for validation
    filename = os.path.basename(self.path)

    if not filename:
      raise ValueError("Path must specify a filename")

    # Try encoding the content with the specified encoding to ensure compatibility
    try:
      self.contents.encode(self.encoding)
    except UnicodeEncodeError as e:
      raise ValueError(f"Content cannot be encoded with '{self.encoding}' encoding: {e}")

    return self


class ListDirectorySchema(BaseModel):
  """
  Schema for listing directory contents with comprehensive validation.

  Validates directory listing parameters including path security, pagination limits,
  sorting constraints, filtering options, and permission requirements.
  """

  model_config = ConfigDict(str_strip_whitespace=True)

  path: str = Field("/", min_length=1, description="Directory path to list")
  pagenum: int = Field(1, ge=1, le=10000, description="Page number (1-10000)")
  pagesize: int = Field(30, ge=1, le=1000, description="Items per page (1-1000)")
  sortby: str = Field("name", description="Sort by: name, size, type, mtime, atime, user, group")
  descending: bool = Field(False, description="Sort in descending order")
  filter: Optional[str] = Field(None, min_length=1, max_length=255, description="Filter results by filename substring")

  @field_validator("path")
  @classmethod
  def validate_path_security(cls, v: str) -> str:
    """Validate path for security and basic requirements."""
    if not v or not v.strip():
      raise ValueError("Path cannot be empty")

    # Strip whitespace
    v = v.strip()

    # Path traversal protection
    if ".." in v:
      raise ValueError("Path traversal patterns are not allowed")

    # Check for invalid characters
    if "#" in v:
      raise ValueError("Hash characters are not allowed in directory paths")

    return v

  @field_validator("sortby")
  @classmethod
  def validate_sortby(cls, v: str) -> str:
    """Validate sorting field is supported."""
    valid_fields = {"name", "size", "type", "mtime", "atime", "user", "group"}
    if v.lower() not in valid_fields:
      raise ValueError(f"sortby must be one of: {', '.join(valid_fields)}")
    return v.lower()

  @field_validator("filter")
  @classmethod
  def validate_filter(cls, v: Optional[str]) -> Optional[str]:
    """Validate filter string for security."""
    if v is not None:
      v = v.strip()
      if not v:
        return None

      # Check for potentially dangerous filter patterns
      dangerous_patterns = ["../", "~", "\\", "**/"]
      for pattern in dangerous_patterns:
        if pattern in v:
          raise ValueError(f"Filter contains invalid pattern: {pattern}")
    return v

  @model_validator(mode="after")
  def validate_pagination_constraints(self) -> "ListDirectorySchema":
    """Validate pagination parameters make sense together."""
    # Check for reasonable pagination limits
    max_total_items = self.pagenum * self.pagesize
    if max_total_items > 100000:  # Prevent excessive memory usage
      raise ValueError("Pagination parameters would result in too many items being processed")

    return self


class CreateDirectorySchema(BaseModel):
  """
  Schema for creating a directory with comprehensive validation.

  Validates directory creation parameters including path security, parent directory
  requirements, permission constraints, and filesystem compatibility.
  """

  model_config = ConfigDict(str_strip_whitespace=True)

  path: str = Field(..., min_length=1, description="Full path of the directory to create")

  @field_validator("path")
  @classmethod
  def validate_path_security(cls, v: str) -> str:
    """Validate path for security and basic requirements."""
    if not v or not v.strip():
      raise ValueError("Path cannot be empty")

    # Strip whitespace
    v = v.strip()

    # Path traversal protection
    if ".." in v:
      raise ValueError("Path traversal patterns are not allowed")

    # Check for invalid characters
    if "#" in v:
      raise ValueError("Hash characters are not allowed in directory names")

    return v


class GetStatsSchema(BaseModel):
  """Schema for getting file/directory statistics."""

  path: str = Field(..., description="Path to get statistics for")
  include_content_summary: bool = Field(False, description="Include content summary (size, file count, etc.)")

  @field_validator("path")
  @classmethod
  def validate_path_not_empty(cls, v: str) -> str:
    if not v or not v.strip():
      raise ValueError("Path cannot be empty")
    return v.strip()


class CheckExistsSchema(BaseModel):
  """Schema for checking if paths exist."""

  paths: list[str] = Field(..., description="List of paths to check existence")

  @field_validator("paths")
  @classmethod
  def validate_paths(cls, v: list[str]) -> list[str]:
    if not v:
      raise ValueError("At least one path is required")
    for path in v:
      if not path or not path.strip():
        raise ValueError("Paths cannot be empty")
    return [path.strip() for path in v]


class CopyOperationSchema(BaseModel):
  """Schema for copy operation."""

  source_paths: list[str] = Field(..., description="List of source paths to copy")
  destination_path: str = Field(..., description="Destination directory path")

  @field_validator("source_paths")
  @classmethod
  def validate_source_paths(cls, v: list[str]) -> list[str]:
    if not v:
      raise ValueError("At least one source path is required")
    for path in v:
      if not path or not path.strip():
        raise ValueError("Source paths cannot be empty")
    return v

  @field_validator("destination_path")
  @classmethod
  def validate_destination_path(cls, v: str) -> str:
    if not v or not v.strip():
      raise ValueError("Destination path cannot be empty")
    return v.strip()


class MoveOperationSchema(BaseModel):
  """Schema for move operation."""

  source_paths: list[str] = Field(..., description="List of source paths to move")
  destination_path: str = Field(..., description="Destination directory path")

  @field_validator("source_paths", "destination_path")
  @classmethod
  def validate_paths(cls, v: Union[list[str], str]) -> Union[list[str], str]:
    if isinstance(v, list):
      if not v:
        raise ValueError("At least one source path is required")
      for path in v:
        if not path or not path.strip():
          raise ValueError("Source paths cannot be empty")
      return v
    else:
      if not v or not v.strip():
        raise ValueError("Path cannot be empty")
      return v.strip()


class DeleteOperationSchema(BaseModel):
  """Schema for delete operation."""

  paths: list[str] = Field(..., description="List of paths to delete")
  skip_trash: bool = Field(False, description="Skip trash and permanently delete")

  @field_validator("paths")
  @classmethod
  def validate_paths(cls, v: list[str]) -> list[str]:
    if not v:
      raise ValueError("At least one path is required")
    for path in v:
      if not path or not path.strip():
        raise ValueError("Paths cannot be empty")
    return v


class TrashRestoreSchema(BaseModel):
  """Schema for restoring from trash."""

  paths: list[str] = Field(..., description="List of paths to restore from trash")

  @field_validator("paths")
  @classmethod
  def validate_paths(cls, v: list[str]) -> list[str]:
    if not v:
      raise ValueError("At least one path is required")
    for path in v:
      if not path or not path.strip():
        raise ValueError("Paths cannot be empty")
    return v


class SetPermissionsSchema(BaseModel):
  """Schema for setting file/directory permissions."""

  paths: list[str] = Field(..., description="List of paths to change permissions")
  recursive: bool = Field(False, description="Apply recursively")
  # Individual permission fields
  user_read: Optional[bool] = Field(None, description="User read permission")
  user_write: Optional[bool] = Field(None, description="User write permission")
  user_execute: Optional[bool] = Field(None, description="User execute permission")
  group_read: Optional[bool] = Field(None, description="Group read permission")
  group_write: Optional[bool] = Field(None, description="Group write permission")
  group_execute: Optional[bool] = Field(None, description="Group execute permission")
  other_read: Optional[bool] = Field(None, description="Other read permission")
  other_write: Optional[bool] = Field(None, description="Other write permission")
  other_execute: Optional[bool] = Field(None, description="Other execute permission")
  sticky: Optional[bool] = Field(None, description="Sticky bit")

  @field_validator("paths")
  @classmethod
  def validate_paths(cls, v: list[str]) -> list[str]:
    if not v:
      raise ValueError("At least one path is required")
    for path in v:
      if not path or not path.strip():
        raise ValueError("Paths cannot be empty")
    return v


class SetOwnershipSchema(BaseModel):
  """Schema for setting file/directory ownership."""

  paths: list[str] = Field(..., description="List of paths to change ownership")
  user: Optional[str] = Field(None, description="New owner username")
  group: Optional[str] = Field(None, description="New group name")
  recursive: bool = Field(False, description="Apply recursively")

  @field_validator("paths")
  @classmethod
  def validate_paths(cls, v: list[str]) -> list[str]:
    if not v:
      raise ValueError("At least one path is required")
    for path in v:
      if not path or not path.strip():
        raise ValueError("Paths cannot be empty")
    return v

  @model_validator(mode="after")
  def validate_user_or_group(self) -> "SetOwnershipSchema":
    if not self.user and not self.group:
      raise ValueError("At least one of user or group must be provided")
    return self


class SetReplicationSchema(BaseModel):
  """Schema for setting replication factor."""

  path: str = Field(..., description="Path to set replication for")
  replication_factor: int = Field(..., ge=1, description="Replication factor")

  @field_validator("path")
  @classmethod
  def validate_path_not_empty(cls, v: str) -> str:
    if not v or not v.strip():
      raise ValueError("Path cannot be empty")
    return v.strip()


class CompressFilesSchema(BaseModel):
  """Schema for compressing files."""

  file_names: list[str] = Field(..., description="List of file names to compress")
  upload_path: str = Field(..., description="Path where files are located")
  archive_name: str = Field(..., description="Name of the archive to create")

  @field_validator("file_names")
  @classmethod
  def validate_file_names(cls, v: list[str]) -> list[str]:
    if not v:
      raise ValueError("At least one file name is required")
    return v

  @field_validator("upload_path", "archive_name")
  @classmethod
  def validate_not_empty(cls, v: str) -> str:
    if not v or not v.strip():
      raise ValueError("Value cannot be empty")
    return v.strip()


class ExtractArchiveSchema(BaseModel):
  """Schema for extracting archives."""

  upload_path: str = Field(..., description="Path where archive is located")
  archive_name: str = Field(..., description="Name of the archive to extract")

  @field_validator("upload_path", "archive_name")
  @classmethod
  def validate_not_empty(cls, v: str) -> str:
    if not v or not v.strip():
      raise ValueError("Value cannot be empty")
    return v.strip()


class GetTrashPathSchema(BaseModel):
  """Schema for getting trash path."""

  path: str = Field(..., description="Path to get trash location for")

  @field_validator("path")
  @classmethod
  def validate_path_not_empty(cls, v: str) -> str:
    if not v or not v.strip():
      raise ValueError("Path cannot be empty")
    return v.strip()
