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

from azure.abfs.__init__ import strip_path, abfsdatetime_to_timestamp
from django.utils.encoding import smart_str

class ABFSStat(object):
  DIR_MODE = 0o777 | stat.S_IFDIR
  FILE_MODE = 0o666 | stat.S_IFREG

  def __init__(self, file_stats, path):
    self.name = strip_path(path)
    self.path = path
    try:
      self.isDir = file_stats['x-ms-resource-type'] == 'directory'
      self.type = file_stats['x-ms-resource-type'].upper()
    except:
      self.isDir = True
      self.type = 'DIRECTORY'
    self.atime = abfsdatetime_to_timestamp(file_stats['Date']) if file_stats['Date'] else None
    self.mtime = abfsdatetime_to_timestamp(file_stats['Last-Modified']) if file_stats['Last-Modified'] else None
    try:
      self.size = file_stats['Content-Length']
    except:
      self.size = '0'
    
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
  def mode(self):
    return ABFSStat.DIR_MODE if self.isDir else ABFSStat.FILE_MODE
  
  @property
  def user(self):
    return ''

  @property
  def group(self):
    return ''
  
  @property
  def aclBit(self):
    return False
  
  def to_json_dict(self):
    """
    Returns a dictionary for easy serialization
    """
    keys = ('path', 'size', 'atime', 'mtime', 'mode', 'user', 'group', 'aclBit')
    res = {}
    for k in keys:
      res[k] = self[k]
    return res
    