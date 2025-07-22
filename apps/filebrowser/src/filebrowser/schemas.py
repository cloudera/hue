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

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from filebrowser.utils import is_file_upload_allowed


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
