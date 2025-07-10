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
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from filebrowser.conf import MAX_FILE_SIZE_UPLOAD_LIMIT
from filebrowser.utils import is_file_upload_allowed


class UploadFileSchema(BaseModel):
  """Schema for file upload validation.

  Validates file upload parameters including filename, size limits,
  and destination path. Ensures files meet security and size requirements.
  """
  model_config = ConfigDict(arbitrary_types_allowed=True)

  file: Any = Field(..., description="File to upload - can be Django UploadedFile, file-like object, bytes, or string")
  filename: str = Field(..., description="The name of the file")
  filesize: int = Field(..., description="The size of the file in bytes")
  destination_path: str = Field(..., description="Destination path for the file")
  overwrite: bool = Field(default=False, description="Whether to overwrite existing file")

  @field_validator("filename")
  @classmethod
  def validate_filename(cls, v: str) -> str:
    """Validate filename for security and upload restrictions."""
    if not v or v.strip() == "":
      raise ValueError("Filename cannot be empty")

    is_allowed, error_message = is_file_upload_allowed(v)
    if not is_allowed:
      raise ValueError(error_message)

    # Check for path traversal attempts in filename
    if os.path.sep in v:
      raise ValueError("Invalid filename. Path separators are not allowed.")

    return v

  @field_validator("filesize")
  @classmethod
  def validate_filesize(cls, v: int) -> int:
    """Validate file size against configured maximum limit."""
    max_size = MAX_FILE_SIZE_UPLOAD_LIMIT.get()

    # -1 means no limit
    if max_size == -1:
      return v

    if v > max_size:
      raise ValueError(f"File too large. Maximum file size is {max_size} bytes.")
    return v

  @field_validator("destination_path")
  @classmethod
  def validate_destination(cls, v: str) -> str:
    if not v or v.strip() == "":
      raise ValueError("Destination path cannot be empty")
    return v
