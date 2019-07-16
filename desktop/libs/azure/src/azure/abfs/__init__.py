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

import errno
import re

ABFS_PATH_RE = re.compile('^/*[aA][bB][fF][sS]{1,2}://([^/]+)(/(.*?(([^/]+/)*/?))?)?$') # bug here
ABFS_ROOT_S = 'abfss://'
ABFS_ROOT = 'abfs://'

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
  return uri.lower() == ABFS_ROOT or uri.lower() == ABFS_ROOT_S

def strip_scheme(path):
    filesystem, file_path = parse_uri(path)[:2]
    path = filesystem + '/' + file_path
    return path