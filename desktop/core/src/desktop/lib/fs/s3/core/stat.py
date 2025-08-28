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
from dataclasses import dataclass, field
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
  mtime: Optional[int]  # Last modified time
  is_dir: bool  # True if directory

  # Optional S3-specific attributes
  etag: Optional[str] = None
  version_id: Optional[str] = None
  storage_class: Optional[str] = None
  metadata: Optional[Dict[str, str]] = None

  # Additional attributes needed for compatibility
  atime: Optional[int] = None  # Access time (same as mtime for S3)
  aclBit: bool = False  # ACL bit flag
  replication: int = 1  # Replication factor (always 1 for S3)
  user: str = ""  # Owner
  group: str = ""  # Group

  # Internal dict to store dynamic attributes
  _attrs: Dict[str, Any] = field(default_factory=dict)

  def __post_init__(self):
    # For backward compatibility - expose is_dir as isDir
    self.isDir = self.is_dir

  def __getitem__(self, key: str) -> Any:
    """Support dict-like access to attributes"""
    # First check internal attrs dict
    if key in self._attrs:
      return self._attrs[key]

    # Then check instance attributes
    if hasattr(self, key):
      return getattr(self, key)

    # Finally check property methods
    if key in ["type", "mode"]:
      return getattr(self, key)

    raise KeyError(key)

  def __setitem__(self, key: str, value: Any) -> None:
    """Support dict-like setting of attributes"""
    # For path and name attribute, also update the instance attribute
    if key == "path":
      self.path = value
    elif key == "name":
      self.name = value

    # Store in internal attrs dict
    self._attrs[key] = value

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
      mtime=int(obj.last_modified.timestamp()),  # Convert to timestamp
      atime=int(obj.last_modified.timestamp()),  # Convert to timestamp
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

    last_modified = head_response["LastModified"]
    if isinstance(last_modified, str):
      last_modified = datetime.strptime(last_modified, "%Y-%m-%dT%H:%M:%S.%fZ")
    timestamp = int(last_modified.timestamp())

    return cls(
      path=str(path),
      name=path.name(),
      size=head_response["ContentLength"],
      mtime=timestamp,  # Store as timestamp
      atime=timestamp,  # Store as timestamp
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

  def to_json_dict(self) -> Dict[str, Any]:
    """Convert to JSON-serializable dict"""
    base = {
      "path": self.path,
      "name": self.name,
      "size": self.size,
      "mtime": self.mtime,  # Already an integer timestamp
      "atime": self.atime,  # Already an integer timestamp
      "type": self.type,
      "mode": self.mode,
      "user": self.user,
      "group": self.group,
      "aclBit": self.aclBit,
      "replication": self.replication,
      "etag": self.etag,
      "version_id": self.version_id,
      "storage_class": self.storage_class,
      "metadata": self.metadata,
      "isDir": self.is_dir,  # Add for backward compatibility
    }
    # Include any dynamic attributes
    base.update(self._attrs)
    return base

  def __eq__(self, other: object) -> bool:
    """Compare stats"""
    if not isinstance(other, S3Stat):
      return NotImplemented
    return self.path == other.path and self.size == other.size and self.mtime == other.mtime and self.is_dir == other.is_dir
