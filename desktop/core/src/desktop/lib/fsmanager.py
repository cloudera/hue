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

import logging
from functools import partial

import aws.client
import azure.client
import desktop.lib.fs.gc.client
import desktop.lib.fs.ozone.client
from azure.conf import has_abfs_access, has_adls_access, is_abfs_enabled, is_adls_enabled
from desktop.conf import DEFAULT_USER, has_gs_access, has_ofs_access, is_gs_enabled, is_ofs_enabled, RAZ, USE_STORAGE_CONNECTORS
from desktop.lib.fs.proxyfs import ProxyFS
from desktop.lib.fs.s3.conf_utils import get_default_connector
from desktop.lib.fs.s3.core.s3fs import make_s3_client
from desktop.lib.idbroker import conf as conf_idbroker
from desktop.lib.python_util import current_ms_from_utc
from hadoop.cluster import _make_filesystem, get_hdfs
from hadoop.conf import has_hdfs_enabled

if USE_STORAGE_CONNECTORS.get():
  from desktop.lib.fs.s3.conf_utils import has_s3_access, is_enabled as is_s3_enabled
else:
  from aws.conf import has_s3_access, is_enabled as is_s3_enabled

SUPPORTED_FS = ['hdfs', 's3a', 'adl', 'abfs', 'gs', 'ofs']
CLIENT_CACHE = None
_DEFAULT_USER = DEFAULT_USER.get()


# FIXME: Should we check hue principal for the default user?
# FIXME: Caching via username has issues when users get deleted. Need to switch to userid, but bigger change
def _get_cache_key(fs, identifier, user=_DEFAULT_USER):
  return fs + ':' + identifier + ':' + str(user)


def clear_cache():
  global CLIENT_CACHE
  CLIENT_CACHE = None


def has_access(fs=None, user=None):
  if fs == 'hdfs':
    return True
  elif fs == 'adl':
    return has_adls_access(user)
  elif fs == 's3a':
    return has_s3_access(user)
  elif fs == 'abfs':
    return has_abfs_access(user)
  elif fs == 'gs':
    return has_gs_access(user)
  elif fs == 'ofs':
    return has_ofs_access(user)


def is_enabled(fs):
  if fs == 'hdfs':
    return has_hdfs_enabled()
  elif fs == 'adl':
    return is_adls_enabled()
  elif fs == 's3a':
    return is_s3_enabled()
  elif fs == 'abfs':
    return is_abfs_enabled()
  elif fs == 'gs':
    return is_gs_enabled()
  elif fs == 'ofs':
    return is_ofs_enabled()


def is_enabled_and_has_access(fs=None, user=None):
  return is_enabled(fs) and has_access(fs, user)


def _make_client(fs, name, user):
  if fs == 'hdfs':
    return _make_filesystem(name)
  elif fs == 's3a':
    if USE_STORAGE_CONNECTORS.get():
      # For storage connector system, use connector_id (default to 'default' or first available)
      connector_id = name if name != "default" else get_default_connector()
      return make_s3_client(connector_id, user)
    return aws.client._make_client(name, user)
  elif fs == 'adl':
    return azure.client._make_adls_client(name, user)
  elif fs == 'abfs':
    return azure.client._make_abfs_client(name, user)
  elif fs == 'gs':
    return desktop.lib.fs.gc.client._make_client(name, user)
  elif fs == 'ofs':
    return desktop.lib.fs.ozone.client._make_ofs_client(name, user)
  return None


def _get_client(fs=None):
  if fs == 'hdfs':
    return get_hdfs
  elif fs in ['s3a', 'adl', 'abfs', 'gs', 'ofs']:
    return partial(_get_client_cached, fs)
  return None


def _get_client_cached(fs, name, user):
  global CLIENT_CACHE
  if CLIENT_CACHE is None:
    CLIENT_CACHE = {}

  if (conf_idbroker.is_idbroker_enabled(fs) or RAZ.IS_ENABLED.get()):
    cache_key = _get_cache_key(fs, name, user)
  else:
    # By default, caching via default hue user key because there are no user-mapping like scenarios same as in IDBroker or RAZ.
    # For FS like S3 and ABFS: Default case is via access key and secret which just allows everyone to access everything.
    # For FS like HDFS and Ozone: This user mapping is handled behind the scenes and we are impersonating user for them.
    cache_key = _get_cache_key(fs, name)

  client = CLIENT_CACHE.get(cache_key)

  # Expiration from IDBroker returns java timestamp in MS
  if client and (client.expiration is None or client.expiration > int(current_ms_from_utc())):
    return client
  else:
    client = _make_client(fs, name, user)
    CLIENT_CACHE[cache_key] = client
    return client


def get_client(name='default', fs=None, user=_DEFAULT_USER):
  fs_getter = _get_client(fs)
  if fs_getter:
    return fs_getter(name, user)
  else:
    logging.warn('Can not get filesystem called "%s" for "%s" schema' % (name, fs))
    return None


def get_default_schema():
  fs = [fs for fs in SUPPORTED_FS if is_enabled(fs)]
  return fs[0] if fs else None


def get_filesystem(name='default'):
  """
  Return the filesystem with the given name.
  If the filesystem is not defined, raises KeyError
  """
  # Instead of taking a list of cached client, ProxyFS will now resolve the client based on scheme
  # The method to resolve clients returns a cached results if possible.
  pdict = {}
  for fs in SUPPORTED_FS:
    if is_enabled(fs):
      pdict[fs] = _get_client(fs)
  return ProxyFS(pdict, get_default_schema(), name) if pdict else None


def get_filesystems(user):
  return [fs for fs in SUPPORTED_FS if is_enabled(fs) and has_access(fs, user)]
