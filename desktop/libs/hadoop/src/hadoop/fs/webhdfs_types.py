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

from django.utils.encoding import smart_str
from hadoop.fs.hadoopfs import Hdfs, decode_fs_path

class WebHdfsStat(object):
  """
  Information about a path in HDFS.

  Modelled after org.apache.hadoop.fs.FileStatus
  """

  def __init__(self, file_status, parent_path):
    self.name = decode_fs_path(file_status['pathSuffix'])
    self.path = Hdfs.join(parent_path, self.name)
    self.isDir = file_status['type'] == 'DIRECTORY'
    self.type = file_status['type']
    self.atime = file_status['accessTime'] / 1000
    self.mtime = file_status['modificationTime'] / 1000
    self.user = file_status['owner']
    self.group = file_status['group']
    self.size = file_status['length']
    self.blockSize = file_status['blockSize']
    self.replication = file_status['replication']
    self.aclBit = file_status.get('aclBit')
    self.fileId = file_status.get('fileId')

    self.mode = int(file_status['permission'], 8)
    if self.isDir:
      self.mode |= stat.S_IFDIR
    else:
      self.mode |= stat.S_IFREG

  def __unicode__(self):
    return "[WebHdfsStat] %7s %8s %8s %12s %s%s" % \
        (oct(self.mode), self.user, self.group, self.size, self.path,
         self.isDir and '/' or "")

  def __repr__(self):
    return smart_str("<WebHdfsStat %s>" % (self.path,))

  def __getitem__(self, key):
    try:
      return getattr(self, key)
    except AttributeError:
      raise KeyError(key)

  def __setitem__(self, key, value):
    setattr(self, key, value)

  def to_json_dict(self):
    """Returns a dictionary for easy serialization"""
    KEYS = ('path', 'size', 'atime', 'mtime', 'mode', 'user', 'group',
            'blockSize', 'replication')
    res = { }
    for k in KEYS:
      res[k] = getattr(self, k)
    return res


class WebHdfsContentSummary(object):
  """
  Content summary info on a directory
  """
  def __init__(self, summary):
    self.summary = summary

    for k, v in summary.iteritems():
      setattr(self, k, v)

  def __str__(self):
    return "[WebHdfsContentSummary] nDirs:%s; nFiles:%s (quota %s); du:%s (quota %s)" % \
        (self.directoryCount, self.fileCount, self.quota, self.spaceConsumed, self.spaceQuota)
