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

from boto.exception import S3ResponseError
from hadoop.fs import normpath as fs_normpath


ERRNO_MAP = {
  403: errno.EACCES,
  404: errno.ENOENT
}
DEFAULT_ERRNO = errno.EINVAL

S3_PATH_RE = re.compile('^/*[sS]3[aA]?://([^/]+)(/(.*?([^/]+)?/?))?$')
S3_ROOT = 's3://'
S3A_ROOT = 's3a://'


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
      raise lookup.__class__, lookup, tb
  return wrapped


def parse_uri(uri):
  """
  Returns tuple (bucket_name, key_name, key_basename).
  Raises ValueError if invalid S3 URI is passed.
  """
  match = S3_PATH_RE.match(uri)
  if not match:
    raise ValueError("Invalid S3 URI: %s" % uri)
  key = match.group(3) or ''
  basename = match.group(4) or ''
  return match.group(1), key, basename


def is_root(uri):
  """
  Check if URI is S3 root (S3A://)
  """
  return uri.lower() == S3A_ROOT


def abspath(cd, uri):
  """
  Returns absolute URI, examples:

  abspath('s3a://bucket/key', key2') == 's3a://bucket/key/key2'
  abspath('s3a://bucket/key', 's3a://bucket2/key2') == 'sa://bucket2/key2'
  """
  if cd.lower().startswith(S3A_ROOT):
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
  joined = posixpath.join(*map(_prep, comp_list))
  if joined and joined[0] == '/':
    joined = 's3a:/%s' % joined
  return joined


def normpath(path):
  """
  Return normalized path but ignore leading S3A_ROOT prefix if it exists
  """
  if path.lower().startswith(S3A_ROOT):
    if is_root(path):
      normalized = path
    else:
      normalized = '%s%s' % (S3A_ROOT, fs_normpath(path[len(S3A_ROOT):]))
  else:
    normalized = fs_normpath(path)
  return normalized


def s3datetime_to_timestamp(datetime):
  """
  Returns timestamp (seconds) by datetime string from S3 API responses.
  S3 REST API returns two types of datetime strings:
  * `Thu, 26 Feb 2015 20:42:07 GMT` for Object HEAD requests
    (see http://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectHEAD.html);
  * `2015-02-26T20:42:07.000Z` for Bucket GET requests
    (see http://docs.aws.amazon.com/AmazonS3/latest/API/RESTBucketGET.html).
  """
  # There is chance (depends on platform) to get
  # `'z' is a bad directive in format ...` error (see https://bugs.python.org/issue6641),
  # but S3 always returns time in GMT, so `GMT` and `.000Z` can be pruned.
  try:
    stripped = time.strptime(datetime[:-4], '%a, %d %b %Y %H:%M:%S')
    assert datetime[-4:] == ' GMT', 'Time [%s] is not in GMT.' % datetime
  except ValueError:
    stripped = time.strptime(datetime[:-5], '%Y-%m-%dT%H:%M:%S')
    assert datetime[-5:] == '.000Z', 'Time [%s] is not in GMT.' % datetime
  return int(calendar.timegm(stripped))
