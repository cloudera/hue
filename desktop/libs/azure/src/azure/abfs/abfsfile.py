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
import errno
import os
import logging

from hadoop.fs.hadoopfs import require_open
from azure.abfs.__init__ import normpath


LOG = logging.getLogger(__name__)
SEEK_SET, SEEK_CUR, SEEK_END = os.SEEK_SET, os.SEEK_CUR, os.SEEK_END


class ABFSFile(object):
  """ Represents an open file on ABFS. """

  def __init__(self, fs, path, mode="r"):
    self.fs = fs
    self.path = normpath(path)
    self.pos = 0
    self.closed = False

    if mode != "r":
      raise Exception("buffering and write support not yet implemented") # NYI

    stat = self._stat()

    if stat is None:
      raise IOError(errno.ENOENT, "No such file or directory: '%s'" % path)
    if stat.isDir:
      raise IOError(errno.EISDIR, "Is a directory: '%s'" % path)
    #TODO(todd) somehow we need to check permissions here - maybe we need an access() call?

  # Minimal context manager implementation.
  # See: http://www.python.org/doc/2.5.2/lib/typecontextmanager.html
  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.close()
    return False # don't supress exceptions.

  @require_open
  def seek(self, offset, whence=0):
    """ Set the file pointer to the given spot. @see file.seek """
    if whence == SEEK_SET:
      self.pos = offset
    elif whence == SEEK_CUR:
      self.pos += offset
    elif whence == SEEK_END:
      self.pos = self._stat().length + offset
    else:
      raise IOError(errno.EINVAL, "Invalid argument to seek for whence")

  @require_open
  def tell(self):
    return self.pos

  @require_open
  def read(self, length=0):
    """
    Read the given number of bytes from this file.
    If EOF has been reached, returns the empty string.

    @param length the number of bytes wanted
    """
    resp = ""
    try:
      resp = self.fs.read(self.path, offset=self.pos, length=str(length))
      self.pos += length
    except:
      resp =''
    return resp

  def close(self):
    self.closed = True

  def _stat(self):
    if not hasattr(self, "_stat_cache"):
      self._stat_cache = self.fs.stats(self.path)
    return self._stat_cache
