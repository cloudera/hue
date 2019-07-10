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

ABFS_PATH_RE = re.compile('^/*[aA][bB][fF][sS]{2}://([^/@]+)(@([^/.]+)[.]dfs.core[.]windows[.]net/([^/]+)?)?$')
#ABFS_PATH_RE = re.compile('^/*[aA][bB][fF][sS]{2}://([^/@]+)$')
ABFS_ROOT = 'abfs://'

def parse_uri(uri):
  """
  Returns container_name, Account_name and filesystem_name
  Raises ValueError if invalid ABFS URI is passed.
  """
  match = ABFS_PATH_RE.match(uri)
  if not match:
    raise ValueError("Invalid ABFS URI: %s" % uri)
  filesystem_name = match.group(4) or ''
  account_name = match.group(3) or ''
  return match.group(1), account_name, filesystem_name

def is_root(uri):
  return uri.lower() == ABFS_ROOT
