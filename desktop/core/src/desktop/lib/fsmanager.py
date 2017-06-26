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

import sys
import logging

import aws
from aws.conf import is_enabled as is_s3_enabled

from desktop.lib.fs import ProxyFS
from hadoop import cluster

FS_CACHE = {}

DEFAULT_SCHEMA = 'hdfs'

FS_GETTERS = {
  "hdfs": cluster.get_hdfs,
  "s3a": aws.get_s3fs if is_s3_enabled() else None
}


def get_filesystem(name='default'):
  """
  Return the filesystem with the given name.
  If the filesystem is not defined, raises KeyError
  """
  if name not in FS_CACHE:
    FS_CACHE[name] = _make_fs(name)
  return FS_CACHE[name]


def _make_fs(name):
  fs_dict = {}
  for schema, getter in FS_GETTERS.iteritems():
    try:
      if getter is not None:
        fs = getter(name)
        fs_dict[schema] = fs
      else:
        raise Exception('Filesystem not configured for %s' % schema)
    except KeyError:
      if DEFAULT_SCHEMA == schema:
        logging.error('Can not get filesystem called "%s" for default schema "%s"' % (name, schema))
        exc_class, exc, tb = sys.exc_info()
        raise exc_class, exc, tb
      else:
        logging.warn('Can not get filesystem called "%s" for "%s" schema' % (name, schema))
    except Exception, e:
      logging.error('Failed to get filesystem called "%s" for "%s" schema: %s' % (name, schema, e))
  return ProxyFS(fs_dict, DEFAULT_SCHEMA)


def clear_cache():
  """
  Clears internal cache.  Returns
  something that can be given back to restore_cache.
  """
  global FS_CACHE
  old = FS_CACHE
  FS_CACHE = {}
  return old


def restore_cache(old_cache):
  """
  Restores cache from the result of a previous clear_cache call.
  """
  global FS_CACHE
  FS_CACHE = old_cache
