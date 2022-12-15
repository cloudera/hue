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
import logging

from azure.abfs.__init__ import strip_path, abfsdatetime_to_timestamp
from django.utils.encoding import smart_str

LOG = logging.getLogger(__name__)
CHAR_TO_OCT = {"---": 0, "--x": 1, "-w-": 2, "-wx": 3, "r--": 4, "r-x": 5, "rw-": 6, "rwx": 7}


class ABFSStat(object):

  def __init__(self, isDir, atime, mtime, size, path, owner='', group='', mode=None):
    self.name = strip_path(path)
    self.path = path
    self.isDir = isDir
    self.type = 'DIRECTORY' if isDir else 'FILE'
    try:
      self.atime = abfsdatetime_to_timestamp(atime) if atime else None
      self.mtime = abfsdatetime_to_timestamp(mtime) if mtime else None
    except:
      self.atime = 0
      self.mtime = 0
    self.size = size
    self.user = owner
    self.group = group
    self.mode = mode or (0o777 if isDir else 0o666)
    if self.isDir:
      self.mode |= stat.S_IFDIR
    else:
      self.mode |= stat.S_IFREG

  def __getitem__(self, key):
    try:
      return getattr(self, key)
    except AttributeError:
      raise KeyError(key)

  def __setitem__(self, key, value):
    # What about derivable values?
    setattr(self, key, value)

  def __repr__(self):
    return smart_str("<abfsStat %s>" % (self.path,))

  @property
  def aclBit(self):
    return False

  @classmethod
  def for_root(cls, path):
    return cls(True, 0, 0, 0, path)

  @classmethod
  def for_filesystems(cls, headers, resp, scheme):
    return cls(True, headers['date'], resp['lastModified'], 0, scheme + resp['name'])

  @classmethod
  def for_directory(cls, headers, resp, path):
    try:
      size = int(resp['contentLength'])
    except:
      size = 0
    try:
      isDir = resp['isDirectory'] == 'true'
    except:
      isDir = False
    try:
      permissions = ABFSStat.char_permissions_to_oct_permissions(resp['permissions'])
    except:
      permissions = None
    return cls(isDir, headers['date'], resp.get('lastModified'), size, path, resp.get('owner'), resp.get('group'), mode=permissions)

  @classmethod
  def for_single(cls, resp, path):
    size = int(resp['Content-Length'])
    isDir = resp['x-ms-resource-type'] == 'directory'
    try:
      permissions = ABFSStat.char_permissions_to_oct_permissions(resp['x-ms-permissions'])
    except:
      permissions = None
    return cls(isDir, resp['date'], resp['Last-Modified'], size, path, resp.get('x-ms-owner'), resp.get('x-ms-group'), mode=permissions)

  @classmethod
  def for_filesystem(cls, resp, path):
    return cls(True, resp['date'], resp['Last-Modified'], 0, path)

  @staticmethod
  def char_permissions_to_oct_permissions(permissions):
    try:
      octal_permissions = CHAR_TO_OCT[permissions[0:3]] * 64 + CHAR_TO_OCT[permissions[3:6]] * 8 + CHAR_TO_OCT[permissions[6:]]
    except:
      return None
    return octal_permissions

  def to_json_dict(self):
    """
    Returns a dictionary for easy serialization
    """
    keys = ('path', 'size', 'atime', 'mtime', 'mode', 'user', 'group', 'aclBit')
    res = {}
    for k in keys:
      res[k] = self[k]
    return res
