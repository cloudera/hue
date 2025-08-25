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

import stat
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Union

from desktop.lib.fs.s3.core.path import S3Path


@dataclass
class S3Stat:
  """
  File/directory statistics for S3 objects.
  Compatible with os.stat_result interface.
  """

  path: str  # Full path
  name: str  # File/directory name
  size: int  # Size in bytes
  mtime: Optional[datetime]  # Last modified time
  is_dir: bool  # True if directory

  # Optional S3-specific attributes
  etag: Optional[str] = None
  version_id: Optional[str] = None
  storage_class: Optional[str] = None
  metadata: Optional[Dict[str, str]] = None

  @property
  def mode(self) -> int:
    """Get file mode (permissions)"""
    if self.is_dir:
      return stat.S_IFDIR | 0o777  # rwxrwxrwx
    return stat.S_IFREG | 0o666  # rw-rw-rw-

  @property
  def type(self) -> str:
    """Get file type"""
    return "DIRECTORY" if self.is_dir else "FILE"

  @classmethod
  def for_root(cls) -> "S3Stat":
    """Create stats for root directory"""
    return cls(path="s3a://", name="S3", size=0, mtime=None, is_dir=True)

  @classmethod
  def from_bucket(cls, bucket) -> "S3Stat":
    """
    Create stats from bucket.

    Args:
        bucket: boto3 Bucket object

    Returns:
        S3Stat instance
    """
    return cls(
      path=f"s3a://{bucket.name}",
      name=bucket.name,
      size=0,
      mtime=None,  # Buckets don't have mtime
      is_dir=True,
    )

  @classmethod
  def from_object(cls, obj) -> "S3Stat":
    """
    Create stats from S3 object.

    Args:
        obj: boto3 Object object

    Returns:
        S3Stat instance
    """
    return cls(
      path=f"s3a://{obj.bucket_name}/{obj.key}",
      name=obj.key.rstrip("/").split("/")[-1],
      size=obj.content_length,
      mtime=obj.last_modified,
      is_dir=obj.key.endswith("/"),
      etag=obj.e_tag.strip('"') if obj.e_tag else None,
      version_id=obj.version_id,
      storage_class=obj.storage_class,
      metadata=obj.metadata,
    )

  @classmethod
  def from_head(cls, head_response: Dict[str, Any], path: Union[str, S3Path]) -> "S3Stat":
    """
    Create stats from head_object response.

    Args:
        head_response: Response from head_object API call
        path: S3 path

    Returns:
        S3Stat instance
    """
    if isinstance(path, str):
      path = S3Path.from_path(path)

    return cls(
      path=str(path),
      name=path.name(),
      size=head_response["ContentLength"],
      mtime=head_response["LastModified"],
      is_dir=path.key.endswith("/"),
      etag=head_response.get("ETag", "").strip('"'),
      version_id=head_response.get("VersionId"),
      storage_class=head_response.get("StorageClass"),
      metadata=head_response.get("Metadata"),
    )

  @classmethod
  def for_directory(cls, path: Union[str, S3Path]) -> "S3Stat":
    """
    Create stats for directory path.

    Args:
        path: S3 path

    Returns:
        S3Stat instance
    """
    if isinstance(path, str):
      path = S3Path.from_path(path)

    return cls(path=str(path), name=path.name(), size=0, mtime=None, is_dir=True)

  def to_json(self) -> Dict[str, Any]:
    """Convert to JSON-serializable dict"""
    return {
      "path": self.path,
      "name": self.name,
      "size": self.size,
      "mtime": self.mtime.isoformat() if self.mtime else None,
      "type": self.type,
      "mode": self.mode,
      "etag": self.etag,
      "version_id": self.version_id,
      "storage_class": self.storage_class,
      "metadata": self.metadata,
    }

  def __eq__(self, other: object) -> bool:
    """Compare stats"""
    if not isinstance(other, S3Stat):
      return NotImplemented
    return self.path == other.path and self.size == other.size and self.mtime == other.mtime and self.is_dir == other.is_dir
