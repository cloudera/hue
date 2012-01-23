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

"""
Return types from WebHDFS api calls.
"""

import stat

from hadoop.fs.hadoopfs import Hdfs

class WebHdfsStat(object):
  """
  Information about a path in HDFS.

  Modelled after org.apache.hadoop.fs.FileStatus
  """

  def __init__(self, file_status, parent_path):
    self.path = Hdfs.join(parent_path, file_status['pathSuffix'])
    self.isDir = file_status['type'] == 'DIRECTORY'
    self.atime = file_status['accessTime'] / 1000
    self.mtime = file_status['modificationTime'] / 1000
    self.user = file_status['owner']
    self.group = file_status['group']
    self.size = file_status['length']
    self.blockSize = file_status['blockSize']
    self.replication = file_status['replication']

    self.mode = int(file_status['permission'], 8)
    if self.isDir:
      self.mode |= stat.S_IFDIR
    else:
      self.mode |= stat.S_IFREG

  def __str__(self):
    return "[WebHdfsStat] %6s %8s %8s %12s %s%s" % \
        (oct(self.mode), self.user, self.group, self.size, self.path,
         self.isDir and '/' or "")

  def __repr__(self):
    return "<WebHdfsStat %s>" % (self.path,)

  def __getitem__(self, key):
    try:
      return getattr(self, key)
    except AttributeError:
      raise KeyError(key)

  def __setitem__(self, key, value):
    setattr(self, key, value)
