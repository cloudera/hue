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

import aws.client
import azure.client

from aws.conf import is_enabled as is_s3_enabled, has_s3_access
from azure.conf import is_adls_enabled, is_abfs_enabled, has_adls_access, has_abfs_access
from hadoop.cluster import get_hdfs
from hadoop.conf import has_hdfs_enabled
from desktop.lib.fs.proxyfs import ProxyFS

SUPPORTED_FS = ['hdfs', 's3a', 'adl', 'abfs']


def has_access(fs=None, user=None):
  if fs == 'hdfs':
    return True
  elif fs == 'adl':
    return has_adls_access(user)
  elif fs == 's3a':
    return has_s3_access(user)
  elif fs == 'abfs':
    return has_abfs_access(user)


def is_enabled(fs=None):
  if fs == 'hdfs':
    return has_hdfs_enabled()
  elif fs == 'adl':
    return is_adls_enabled()
  elif fs == 's3a':
    return is_s3_enabled()
  elif fs == 'abfs':
    return is_abfs_enabled()

def is_enabled_and_has_access(fs=None, user=None):
  return is_enabled(fs) and has_access(fs, user)

def _get_client(fs=None):
  if fs == 'hdfs':
    return get_hdfs
  elif fs == 's3a':
    return aws.client.get_client
  elif fs == 'adl':
    return azure.client.get_client
  elif fs == 'abfs':
    return azure.client.get_client_abfs
  return None


def get_client(name='default', fs=None, user=None):
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
  return ProxyFS(pdict, get_default_schema(), name)


def get_filesystems(user):
  return [fs for fs in SUPPORTED_FS if is_enabled(fs) and has_access(fs, user)]




