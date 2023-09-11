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

from __future__ import absolute_import

from builtins import map
from future.utils import raise_
import calendar
import errno
import logging
import posixpath
import re
import sys
import time

from functools import wraps

from boto.exception import S3ResponseError
from hadoop.fs import normpath as fs_normpath


ERRNO_MAP = {
  403: errno.EACCES,
  404: errno.ENOENT
}
DEFAULT_ERRNO = errno.EINVAL

GS_PATH_RE = re.compile('^/*[gG][sS]://([^/]+)(/(.*?([^/]+)?/?))?$')
GS_ROOT = 'gs://'


def lookup_s3error(error):
  err_no = ERRNO_MAP.get(error.status, DEFAULT_ERRNO)
  return IOError(err_no, error.reason)


def translate_s3_error(fn):
  @wraps(fn)
  def wrapped(*args, **kwargs):
    try:
      return fn(*args, **kwargs)
    except S3ResponseError:
      _, exc, tb = sys.exc_info()
      logging.error('S3 error: %s' % exc)
      lookup = lookup_s3error(exc)
      raise_(lookup.__class__, lookup, tb)
  return wrapped


def parse_uri(uri):
  """
  Returns tuple (bucket_name, key_name, key_basename).
  Raises ValueError if invalid GS URI is passed.
  """
  match = GS_PATH_RE.match(uri)
  if not match:
    raise ValueError("Invalid GS URI: %s" % uri)
  key = match.group(3) or ''
  basename = match.group(4) or ''
  return match.group(1), key, basename

def is_root(uri):
  """
  Check if URI is GS root (gs://)
  """
  return uri.lower() == GS_ROOT


def abspath(cd, uri):
  """
  Returns absolute URI, examples:

  abspath('gs://bucket/key', key2') == 'gs://bucket/key/key2'
  abspath('gs://bucket/key', 'gs://bucket2/key2') == 'gs://bucket2/key2'
  """
  if cd.lower().startswith(GS_ROOT):
    uri = join(cd, uri)
  else:
    uri = normpath(join(cd, uri))
  return uri


def join(*comp_list):
  def _prep(uri):
    try:
      return '/%s/%s' % parse_uri(uri)[:2]
    except ValueError:
      return '/' if is_root(uri) else uri
  joined = posixpath.join(*list(map(_prep, comp_list)))
  if joined and joined[0] == '/':
    joined = 'gs:/%s' % joined
  return joined


def normpath(path):
  """
  Return normalized path but ignore leading GS_ROOT prefix if it exists
  """
  if path.lower().startswith(GS_ROOT):
    if is_root(path):
      normalized = path
    else:
      normalized = '%s%s' % (GS_ROOT, fs_normpath(path[len(GS_ROOT):]))
  else:
    normalized = fs_normpath(path)
  return normalized
