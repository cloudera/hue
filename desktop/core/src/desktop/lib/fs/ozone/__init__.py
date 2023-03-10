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

import re
import posixpath

from hadoop.fs import normpath as fs_normpath


OFS_ROOT = 'ofs://'
OFS_PATH_RE = re.compile('^/*[oO][fF][sS]?://([^/]+)(/(.*?([^/]+)?/?))?$')


def is_root(uri):
  """
  Check if URI is OFS root (ofs://)
  """
  return uri.lower() == OFS_ROOT


def normpath(path):
  """
  Return normalized path but ignore leading OFS_ROOT prefix if it exists
  normpath('ofs://vol1/') == 'ofs://vol1'
  """
  if path.lower().startswith(OFS_ROOT):
    if is_root(path):
      normalized = path
    else:
      normalized = '%s%s' % (OFS_ROOT, fs_normpath(path[len(OFS_ROOT):]))
  else:
    normalized = fs_normpath(path)
  return normalized


def abspath(path, key):
  """
  Returns absolute URI, examples:

  abspath('ofs://volume/bucket/key', key2') == 'ofs://volume/bucket/key/key2'
  abspath('ofs://volume/bucket/key', 'ofs://volume/bucket2/key2') == 'ofs://volume/bucket2/key2'
  """
  if path.lower().startswith(OFS_ROOT):
    key = join(path, key)
  else:
    key = normpath(join(path, key))
  return key


def join(*comp_list):
  def _prep(uri):
    try:
      return '/%s/%s' % parse_uri(uri)[:2]
    except ValueError:
      return '/' if is_root(uri) else uri
  joined = posixpath.join(*list(map(_prep, comp_list)))
  if joined and joined[0] == '/':
    joined = 'ofs:/%s' % joined
  return joined


def _append_separator(path):
  if path and not path.endswith('/'):
    path += '/'
  return path


def parse_uri(uri):
  """
  Returns tuple (volume_name, key_name, key_basename).
  Raises ValueError if invalid OFS URI is passed.
  
  ofs://volume1/bucket1/key1/key2 -> 
  group1 -> volume1
  group2 -> /bucket1/key1/key2
  group3 -> bucket1/key1/key2
  group4 -> key2
  """
  match = OFS_PATH_RE.match(uri)
  if not match:
    raise ValueError("Invalid OFS URI: %s" % uri)
  key_name = match.group(3) or ''
  key_basename = match.group(4) or ''
  return match.group(1), key_name, key_basename


def parent_path(path):
  parent_dir = _append_separator(path)
  if not is_root(parent_dir):
    volume_name, key_name, key_basename = parse_uri(path)
    if not key_basename:  # volume is top-level so return root
      parent_dir = OFS_ROOT
    else:
      volume_path = '%s%s' % (OFS_ROOT, volume_name)
      key_path = '/'.join(key_name.split('/')[:-1])
      parent_dir = abspath(volume_path, key_path)
  return parent_dir
