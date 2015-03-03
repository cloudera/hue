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


LOG = logging.getLogger(__name__)

_HDFS_SITE_DICT = None


_CNF_NN_PERMISSIONS_UMASK_MODE = 'fs.permissions.umask-mode'
_CNF_NN_SENTRY_PREFIX = 'sentry.authorization-provider.hdfs-path-prefixes'


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

def get_nn_sentry_prefixes():
  return get_conf().get(_CNF_NN_SENTRY_PREFIX, '')


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
