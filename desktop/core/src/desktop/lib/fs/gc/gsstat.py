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
import posixpath

from aws.s3 import s3datetime_to_timestamp
from aws.s3.s3stat import S3Stat


class GSStat(S3Stat):
  """Custom class for Google Cloud Storage (GS) file statistics.

  This class extends S3Stat and provides methods for creating GSStat objects from GS bucket and key objects.
  """

  def __init__(self, name, path, isDir, size, mtime):
    super().__init__(
      name=name,
      path=path,
      isDir=isDir,
      size=size,
      mtime=mtime
    )


  @classmethod
  def from_bucket(cls, bucket, fs='gs'):
    """Create a GSStat object from a GS bucket.

    Args:
      bucket: The GS bucket object.
      fs (str): The file system (e.g., 'gs').

    Returns:
      GSStat: A GSStat object representing the GS bucket.
    """
    return cls(bucket.name, '%s://%s' % (fs, bucket.name), True, 0, None)


  @classmethod
  def from_key(cls, key, is_dir=False, fs='gs'):
    """Create a GSStat object from a GS key object.

    Args:
      key: The GS key object.
      is_dir (bool): True if the key represents a directory, False otherwise.
      fs (str): The file system (e.g., 'gs').

    Returns:
      GSStat: A GSStat object representing the GS key.
    """
    if key.name:
      name = posixpath.basename(key.name[:-1] if key.name[-1] == '/' else key.name)
      path = '%s://%s/%s' % (fs, key.bucket.name, key.name)
    else:
      name = ''
      path = '%s://%s' % (fs, key.bucket.name)

    size = key.size or 0

    s3_date = None
    if key.last_modified is not None:
      s3_date = key.last_modified
    elif hasattr(key, 'date') and key.date is not None:
      s3_date = key.date
    mtime = s3datetime_to_timestamp(s3_date) if s3_date else None

    return cls(name, path, is_dir, size, mtime)


  @classmethod
  def for_gs_root(cls):
    """Create a GSStat object representing the root of the GS file system.

    Returns:
      GSStat: A GSStat object representing the root of the GS file system.
    """
    return cls('GS', 'gs://', True, 0, None)


  def to_json_dict(self):
    """Returns a dictionary representation of the GSStat object for easy serialization."""

    keys = ('path', 'size', 'atime', 'mtime', 'mode', 'user', 'group', 'aclBit')
    res = {}
    for k in keys:
      res[k] = self[k]
    return res
