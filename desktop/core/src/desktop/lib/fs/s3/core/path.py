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

from dataclasses import dataclass
from typing import Optional
from urllib.parse import unquote, urlparse

from desktop.lib.fs.s3.constants import S3_DELIMITER


@dataclass
class S3Path:
  """
  Represents an S3 path with bucket and key components.
  Handles path parsing, normalization, and manipulation.
  """

  bucket: Optional[str]
  key: Optional[str]

  @classmethod
  def from_path(cls, path: str) -> "S3Path":
    """
    Create S3Path from string path.

    Args:
      path: S3 path (s3://bucket/key or s3a://bucket/key)

    Returns:
      S3Path instance

    Raises:
      ValueError: If path is not a valid S3 path
    """
    if path in ("s3://", "s3a://"):
      return cls(bucket=None, key=None)

    parsed = urlparse(path)
    if parsed.scheme not in ("s3", "s3a"):
      raise ValueError(f"Invalid S3 path: {path}")

    # Get bucket from netloc if present, otherwise from path
    bucket = parsed.netloc
    path_parts = parsed.path.lstrip("/").split("/", 1)

    if not bucket and path_parts:
      bucket = path_parts[0]
      key = path_parts[1] if len(path_parts) > 1 else None
    else:
      key = parsed.path.lstrip("/") if parsed.path else None

    # Normalize empty strings to None
    bucket = unquote(bucket) if bucket else None
    key = unquote(key) if key else None

    return cls(bucket=bucket, key=key)

  def is_root(self) -> bool:
    """Check if path is root (s3:// or s3a://)"""
    return self.bucket is None

  def is_bucket(self) -> bool:
    """Check if path is a bucket (s3://bucket/)"""
    return self.bucket is not None and self.key is None

  def join(self, *components: str) -> "S3Path":
    """
    Join path components.

    Args:
      *components: Path components to join

    Returns:
      New S3Path with joined components
    """
    if self.is_root() and not components:
      return self

    # Start with current path components
    parts = []
    if self.bucket:
      parts.append(self.bucket)
    if self.key:
      parts.append(self.key.rstrip("/"))

    # Add new components
    for comp in components:
      # Skip empty components
      if not comp:
        continue

      # Handle absolute paths
      if comp.startswith("s3://") or comp.startswith("s3a://"):
        return S3Path.from_path(comp)

      # Add component
      parts.append(comp.strip("/"))

    # Reconstruct path
    if not parts:
      return S3Path(None, None)

    return S3Path(bucket=parts[0], key=S3_DELIMITER.join(parts[1:]) if len(parts) > 1 else None)

  def parent(self) -> "S3Path":
    """Get parent path"""
    if self.is_root():
      return self
    if self.is_bucket():
      return S3Path(None, None)

    # Split key into components
    key_parts = self.key.rstrip("/").split("/")
    if len(key_parts) == 1:
      # Key is in bucket root
      return S3Path(self.bucket, None)

    # Remove last component
    return S3Path(bucket=self.bucket, key="/".join(key_parts[:-1]))

  def name(self) -> str:
    """Get path name (last component)"""
    if self.is_root():
      return ""
    if self.is_bucket():
      return self.bucket

    return self.key.rstrip("/").split("/")[-1]

  def add_suffix(self, suffix: str) -> "S3Path":
    """Add suffix to path name"""
    if self.is_root() or self.is_bucket():
      raise ValueError("Cannot add suffix to root or bucket")

    return S3Path(bucket=self.bucket, key=f"{self.key.rstrip('/')}{suffix}")

  def with_trailing_slash(self) -> "S3Path":
    """Ensure path ends with slash"""
    if self.is_root() or self.is_bucket():
      return self

    if not self.key.endswith("/"):
      return S3Path(bucket=self.bucket, key=f"{self.key}/")
    return self

  def without_trailing_slash(self) -> "S3Path":
    """Remove trailing slash"""
    if self.is_root() or self.is_bucket():
      return self

    return S3Path(bucket=self.bucket, key=self.key.rstrip("/"))

  def __str__(self) -> str:
    """Convert to string path"""
    if self.is_root():
      return "s3a://"
    elif self.is_bucket():
      return f"s3a://{self.bucket}"
    else:
      return f"s3a://{self.bucket}/{self.key}"

  def __eq__(self, other: object) -> bool:
    """Compare paths"""
    if not isinstance(other, S3Path):
      return NotImplemented
    return self.bucket == other.bucket and self.key == other.key

  def __hash__(self) -> int:
    """Hash path"""
    return hash((self.bucket, self.key))
