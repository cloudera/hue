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

"""
Deprecated: not used anymore and will be empty
"""

import errno
import logging
import os.path

import conf
import confparse

__all = ['get_conf', 'get_trash_interval']

LOG = logging.getLogger(__name__)

_CORE_SITE_PATH = None                  # Path to core-site.xml
_CORE_SITE_DICT = None                  # A dictionary of name/value config options

_CNF_TRASH_INTERVAL = 'fs.trash.interval'

def reset():
  """Reset the cached conf"""
  global _CORE_SITE_DICT
  _CORE_SITE_DICT = None


def get_conf():
  """get_conf() ->  ConfParse object for core-site.xml"""
  if _CORE_SITE_DICT is None:
    _parse_core_site()
  return _CORE_SITE_DICT


def _parse_core_site():
  """
  Parse core-site.xml and store in _CORE_SITE_DICT
  """
  global _CORE_SITE_DICT
  global _CORE_SITE_PATH

  for indentifier in conf.HDFS_CLUSTERS.get():
    try:
      _CORE_SITE_PATH = os.path.join(conf.HDFS_CLUSTERS[indentifier].HADOOP_CONF_DIR.get(), 'core-site.xml') # Will KeyError and be empty as HADOOP_CONF_DIR does not exist anymore
      data = file(_CORE_SITE_PATH, 'r').read()
      break
    except KeyError:
      data = ""
    except IOError, err:
      if err.errno != errno.ENOENT:
        LOG.error('Cannot read from "%s": %s' % (_CORE_SITE_PATH, err))
        return
      # Keep going and make an empty ConfParse
      data = ""

  _CORE_SITE_DICT = confparse.ConfParse(data)


def get_trash_interval():
  """
  Get trash interval

  Also indicates whether trash is enabled or not.
  """
  return get_conf().get(_CNF_TRASH_INTERVAL)
