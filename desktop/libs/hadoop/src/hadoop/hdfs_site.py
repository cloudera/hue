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

import errno
import logging
import os.path

import conf
import confparse
from hadoop.conf import DEFAULT_NN_HTTP_PORT

LOG = logging.getLogger(__name__)

_HDFS_SITE_DICT = None

_CNF_NN_PERMISSIONS_UMASK_MODE = 'fs.permissions.umask-mode'
_CNF_NN_SENTRY_PREFIXES = 'sentry.authorization-provider.hdfs-path-prefixes' # Deprecated
_CNF_NN_SENTRY_PATH_PREFIXES = 'sentry.hdfs.integration.path.prefixes'
_CNF_NN_PERMISSIONS_SUPERGROUP = 'dfs.permissions.superusergroup'
_CNF_HTTP_POLICY = 'dfs.http.policy'
_CNF_WEBHDFS_HTTPS_PORT = 'dfs.https.port'

def reset():
  global _HDFS_SITE_DICT
  _HDFS_SITE_DICT = None


def get_conf():
  if _HDFS_SITE_DICT is None:
    _parse_hdfs_site()
  return _HDFS_SITE_DICT


def get_umask_mode():
  umask = get_conf().get(_CNF_NN_PERMISSIONS_UMASK_MODE, '022')
  if len(umask) < 4:
    umask = "1" + umask

  return int(umask, 8)

def get_webhdfs_ssl():
  settings = {"protocol": "http", "port": DEFAULT_NN_HTTP_PORT}
  if get_conf().get(_CNF_HTTP_POLICY, 'http') == "HTTPS_ONLY":
    settings["protocol"] = 'https'
    settings["port"] = get_conf().get(_CNF_WEBHDFS_HTTPS_PORT, DEFAULT_NN_HTTP_PORT)
  return settings

def get_nn_sentry_prefixes():
  prefixes = set()

  if get_conf().get(_CNF_NN_SENTRY_PREFIXES, ''):
    prefixes |= set(get_conf().get(_CNF_NN_SENTRY_PREFIXES, '').split(','))

  if get_conf().get(_CNF_NN_SENTRY_PATH_PREFIXES, ''):
    prefixes |= set(get_conf().get(_CNF_NN_SENTRY_PATH_PREFIXES, '').split(','))

  return list(prefixes)


def get_supergroup():
  return get_conf().get(_CNF_NN_PERMISSIONS_SUPERGROUP, 'supergroup')


def _parse_hdfs_site():
  global _HDFS_SITE_DICT
  hdfs_site_path = ''

  try:
    hdfs_site_path = os.path.join(conf.HDFS_CLUSTERS['default'].HADOOP_CONF_DIR.get(), 'hdfs-site.xml')
    data = file(hdfs_site_path, 'r').read()
  except KeyError:
    data = ""
  except IOError, err:
    if err.errno != errno.ENOENT:
      LOG.error('Cannot read from "%s": %s' % (hdfs_site_path, err))
      return
    # Keep going and make an empty ConfParse
    data = ""

  _HDFS_SITE_DICT = confparse.ConfParse(data)
