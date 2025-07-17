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

import codecs
import os
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from desktop.conf import IMPORTER


class LocalFileUploadSchema(BaseModel):
  model_config = ConfigDict(arbitrary_types_allowed=True)

  file: Any = Field(..., description="CSV or Excel file to upload and process")
  filename: str = Field(..., description="The name of the file")
  filesize: int = Field(..., description="The size of the file in bytes")

  @field_validator("filename")
  @classmethod
  def validate_filename(cls, v: str) -> str:
    # Check if the file type is restricted
    _, file_type = os.path.splitext(v)
    restricted_extensions = IMPORTER.RESTRICT_LOCAL_FILE_EXTENSIONS.get()
    if restricted_extensions and file_type.lower() in [ext.lower() for ext in restricted_extensions]:
      raise ValueError(f'Uploading files with type "{file_type}" is not allowed. Hue is configured to restrict this type.')
    return v

  @field_validator("filesize")
  @classmethod
  def validate_filesize(cls, v: int) -> int:
    # Check file size
    max_size = IMPORTER.MAX_LOCAL_FILE_SIZE_UPLOAD_LIMIT.get()
    if v > max_size:
      max_size_mib = max_size / (1024 * 1024)
      raise ValueError(f"File too large. Maximum file size is {max_size_mib:.0f} MiB.")
    return v


class GuessFileMetadataSchema(BaseModel):
  file_path: str = Field(..., description="Full path to the file to analyze")
  import_type: Literal["local", "remote"] = Field(..., description="Whether the file is local or on a remote filesystem")

  @field_validator("file_path")
  @classmethod
  def file_path_not_blank(cls, v: str) -> str:
    if not v or v.strip() == "":
      raise ValueError("File path cannot be empty or whitespace.")
    return v


class PreviewFileSchema(BaseModel):
  file_path: str = Field(..., description="Full path to the file to preview")
  file_type: Literal["csv", "tsv", "excel", "delimiter_format"] = Field(..., description="Type of file (csv, tsv, excel, delimiter_format)")
  import_type: Literal["local", "remote"] = Field(..., description="Whether the file is local or on a remote filesystem")
  sql_dialect: Literal["hive", "impala", "trino", "phoenix", "sparksql"] = Field(..., description="SQL dialect for mapping column types")
  has_header: bool = Field(..., description="Whether the file has a header row or not")
  sheet_name: Optional[str] = Field(None, description="Sheet name for Excel files")
  field_separator: Optional[str] = Field(None, description="Field separator character")
  quote_char: Optional[str] = Field(None, description="Quote character")
  record_separator: Optional[str] = Field(None, description="Record separator character")

  @field_validator("file_path")
  @classmethod
  def file_path_not_blank(cls, v: str) -> str:
    if not v or v.strip() == "":
      raise ValueError("File path cannot be empty or whitespace.")
    return v

  @field_validator("field_separator", "quote_char", "record_separator", mode="before")
  @classmethod
  def decode_escape_sequences(cls, value: Optional[str]) -> Optional[str]:
    if value is None:
      return value
    return codecs.decode(value, "unicode_escape")

  @model_validator(mode="after")
  def set_defaults_and_validate_dependencies(self) -> "PreviewFileSchema":
    # Validate sheet_name dependency for excel files
    if self.file_type == "excel" and not self.sheet_name:
      raise ValueError("Sheet name is required for Excel files.")

    # Normalize record separator
    if self.record_separator == "\r\n":
      self.record_separator = "\n"

    # Set defaults for delimited files
    if self.file_type in ["csv", "tsv", "delimiter_format"]:
      if self.field_separator is None:
        if self.file_type == "csv":
          self.field_separator = ","
        elif self.file_type == "tsv":
          self.field_separator = "\t"
        else:
          raise ValueError("Field separator is required for delimited files")

      if self.quote_char is None:
        self.quote_char = '"'

      if self.record_separator is None:
        self.record_separator = "\n"

    return self


class SqlTypeMapperSchema(BaseModel):
  sql_dialect: Literal["hive", "impala", "trino", "phoenix", "sparksql"] = Field(..., description="SQL dialect for mapping column types")


class GuessFileHeaderSchema(BaseModel):
  file_path: str = Field(..., description="Full path to the file to analyze")
  file_type: Literal["csv", "tsv", "excel", "delimiter_format"] = Field(..., description="Type of file (csv, tsv, excel, delimiter_format)")
  import_type: Literal["local", "remote"] = Field(..., description="Whether the file is local or on a remote filesystem")
  sheet_name: Optional[str] = Field(None, description="Sheet name for Excel files")

  @field_validator("file_path")
  @classmethod
  def file_path_not_blank(cls, v: str) -> str:
    if not v or v.strip() == "":
      raise ValueError("File path cannot be empty or whitespace.")
    return v

  @model_validator(mode="after")
  def sheet_name_required_for_excel(self) -> "GuessFileHeaderSchema":
    if self.file_type == "excel" and not self.sheet_name:
      raise ValueError("Sheet name is required for Excel files.")
    return self
