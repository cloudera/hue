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
import logging
import tempfile
import posixpath
from nose.tools import assert_not_equal
from hadoop.fs import normpath as fs_normpath

LOG = logging.getLogger(__name__)

ABFS_PATH_RE = re.compile('^/*[aA][bB][fF][sS]{1,2}://([$a-z0-9](?!.*--)[-a-z0-9]{1,61}[a-z0-9])(/(.*?)/?)?$') # bug here
#also changed becuase some bug in
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
  base_direct_name = match.group(2) or ''
  LOG.debug("File System: %s,Directory Name: %s, Other: %s" %(match.group(1), direct_name, base_direct_name) )
  return match.group(1), direct_name, base_direct_name

def is_root(uri):
  """
  Checks if Uri is the Root Directory
  """
  return uri.lower() == ABFS_ROOT or uri.lower() == ABFS_ROOT_S


def strip_scheme(path):
  """
  returns the path without abfss:// or abfs://
  """
  try:
    filesystem, file_path = parse_uri(path)[:2]
  except:
    return path
  assert_not_equal(filesystem, '', 'File System must be Specified')
  path = filesystem + '/' + file_path
  return path
  
def strip_path(path):
  """
  Return only the end of a path given another path(Work In Progress/Not Ready)
  """
  match = ABFS_PATH_RE.match(path)
  if not match:
    raise ValueError("Invalid ABFS URI: %s" % path)
  split_path = path.split('/')
  return split_path[len(split_path) - 1]

def normpath(path):
  """
  Return the normlized path, but ignore leading prefix if it exists
  """
  if is_root(path):
    return path
  elif path.lower().startswith(ABFS_ROOT):
    normalized = '%s%s' % (ABFS_ROOT, fs_normpath(path[len(ABFS_ROOT):]))
  elif path.lower().startswith(ABFS_ROOT_S):
    normalized = '%s%s' % (ABFS_ROOT_S, fs_normpath(path[len(ABFS_ROOT_S):]))
  else:
    normalized = fs_normpath(path)
  return normalized

def parent_path(path):
  """
  Returns the parent of the specified folder
  """
  if is_root(path):
    return path
  filesystem, directory_name, other = parse_uri(path)
  parent = None
  if filesystem is None:
    if path.lower() == ABFS_ROOT_S:
      return ABFS_ROOT_S
    return ABFS_ROOT
  else:
    parent = '/'.join(directory_name.split('/')[:-1])
  if path.lower().startswith(ABFS_ROOT):
    return normpath(ABFS_ROOT + filesystem + '/' + parent)
  return normpath(ABFS_ROOT_S + filesystem + '/' + parent)

def join(first,*complist):
  """
  Join a path on to another path
  """
  def _prep(uri):
    try:
      return '/%s/%s' % parse_uri(uri)[:2]
    except ValueError:
      return '/' if is_root(uri) else uri
  listings = [first]
  listings.extend(complist)
  joined = posixpath.join(*list(map(_prep, listings)))
  if joined and joined[0] == '/':
    if first.startswith(ABFS_ROOT_S):
      joined = 'abfss:/%s' % joined
    else:
      joined = 'abfs:/%s' % joined
  return joined