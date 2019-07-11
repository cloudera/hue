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

import calendar
import errno
import logging
import posixpath
import re
import sys
import time

from functools import wraps

from hadoop.fs import normpath as fs_normpath


ERRNO_MAP = {
  403: errno.EACCES,
  404: errno.ENOENT
}
DEFAULT_ERRNO = errno.EINVAL

#ABFS_PATH_RE = re.compile('^/*[aA][bB][fF][sS]{2}://([^/@]+)(@([^/.]+)[.]dfs.core[.]windows[.]net/(([^?]+)[?](directory=([^&]+))?)?)?$')
ABFS_PATH_RE = re.compile('^/*[aA][bB][fF][sS]{2}://([^/]+)(/(.*?([^/]+)?/?))?$')
ABFS_ROOT = 'abfss://'
ABFS_FS_DEFAULT = re.compile('^/*[aA][bB][fF][sS]{2}://([^/]+)@([^.]+)[.]([^/]+)(/([^?]*))?$')

def parse_uri(uri):
  """
  Returns filesystem_name, direct_name, base_direct_name
  Raises ValueError if invalid ABFS URI is passed.
  """
  match = ABFS_PATH_RE.match(uri)
  if not match:
    raise ValueError("Invalid ABFS URI: %s" % uri)
  direct_name = match.group(3) or ''
  base_direct_name = match.group(4) or ''
  return match.group(1), direct_name, base_direct_name

def is_root(uri):
  return uri.lower() == ABFS_ROOT

def parse_defaultfs(fs_default):
  match = ABFS_FS_DEFAULT.match(fs_default)
  if not match:
    raise ValueError("Invalid fs_default: %s" % fs_default)
  account_name = match.group(2) or ''
  dns_sufix = match.group(3) or ''
  file_system = match.group(5) or ''
  return account_name, dns_sufix, file_system
