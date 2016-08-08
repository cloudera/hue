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
from __future__ import absolute_import

import stat
import posixpath

from aws.s3 import s3datetime_to_timestamp


class S3Stat(object):
  DIR_MODE = 0777 | stat.S_IFDIR
  FILE_MODE = 0666 | stat.S_IFREG

  def __init__(self, name, path, isDir, size, mtime):
    self.name = name
    self.path = path
    self.isDir = isDir
    self.size = size
    self.mtime = mtime

  def __getitem__(self, key):
    try:
      return getattr(self, key)
    except AttributeError:
      raise KeyError(key)

  def __setitem__(self, key, value):
    # What about derivable values?
    setattr(self, key, value)

  @property
  def type(self):
    return 'DIRECTORY' if self.isDir else 'FILE'

  @property
  def mode(self):
    return S3Stat.DIR_MODE if self.isDir else S3Stat.FILE_MODE

  @property
  def user(self):
    return ''

  @property
  def group(self):
    return ''

  @property
  def atime(self):
    return self.mtime

  @property
  def aclBit(self):
    return False

  @classmethod
  def from_bucket(cls, bucket):
    return cls(bucket.name, 's3a://%s' % bucket.name, True, 0, None)

  @classmethod
  def from_key(cls, key, is_dir=False):
    if key.name:
      name = posixpath.basename(key.name[:-1] if key.name[-1] == '/' else key.name)
      path = 's3a://%s/%s' % (key.bucket.name, key.name)
    else:
      name = ''
      path = 's3a://%s' % key.bucket.name

    size = key.size or 0

    s3_date = None
    if key.last_modified is not None:
      s3_date = key.last_modified
    elif hasattr(key, 'date') and key.date is not None:
      s3_date = key.date
    mtime = s3datetime_to_timestamp(s3_date) if s3_date else None

    return cls(name, path, is_dir, size, mtime)

  @classmethod
  def for_s3_root(cls):
    return cls('S3A', 's3a://', True, 0, None)

  def to_json_dict(self):
    """
    Returns a dictionary for easy serialization
    """
    keys = ('path', 'size', 'atime', 'mtime', 'mode', 'user', 'group', 'aclBit')
    res = {}
    for k in keys:
      res[k] = self[k]
    return res
