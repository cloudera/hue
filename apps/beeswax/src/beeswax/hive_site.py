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
Helper for reading hive-site.xml
"""

import errno
import logging
import os.path
import re

import beeswax.conf
from hadoop import confparse

LOG = logging.getLogger(__name__)

_HIVE_SITE_PATH = None                  # Path to hive-site.xml
_HIVE_SITE_DICT = None                  # A dictionary of name/value config options
_METASTORE_LOC_CACHE = None

_CNF_METASTORE_LOCAL = 'hive.metastore.local'
_CNF_METASTORE_URIS = 'hive.metastore.uris'

# Host is whatever up to the colon. Allow and ignore a trailing slash.
_THRIFT_URI_RE = re.compile("^thrift://([^:]+):(\d+)[/]?$")

class MalformedHiveSiteException(Exception):
  """Parsing error class used internally"""
  pass

def reset():
  """Reset the cached conf"""
  global _HIVE_SITE_DICT
  global _METASTORE_LOC_CACHE
  _HIVE_SITE_DICT = None
  _METASTORE_LOC_CACHE = None


def get_conf():
  """get_conf() ->  ConfParse object for hive-site.xml"""
  if _HIVE_SITE_DICT is None:
    _parse_hive_site()
  return _HIVE_SITE_DICT


def get_metastore():
  """
  get_metastore() -> (is_local, host, port)

  Look at both hive-site.xml and beeswax.conf, and return the location of the metastore.

  hive-site.xml supersedes beeswax.conf.
  - If hive-site says local metastore (default), then get host & port from beeswax.conf.
  - If hive-site says remote, then use the URI specified there, so that we don't need to
    configure things twice.
  """
  global _METASTORE_LOC_CACHE
  if not _METASTORE_LOC_CACHE:
    is_local = get_conf().getbool(_CNF_METASTORE_LOCAL, True)
    if is_local:
      host = beeswax.conf.BEESWAX_META_SERVER_HOST.get()
      port = beeswax.conf.BEESWAX_META_SERVER_PORT.get()
    else:
      thrift_uri = get_conf().get(_CNF_METASTORE_URIS)
      host, port = 'undefined', '0'
      if thrift_uri is None:
        LOG.fatal('Remote metastore uri ("%s") not found in hive config %s' %
                  (_CNF_METASTORE_URIS, _HIVE_SITE_PATH))
      else:
        match = _THRIFT_URI_RE.match(thrift_uri)
        if not match:
          LOG.fatal('Cannot understand remote metastore uri "%s"' % (thrift_uri,))
        else:
          host, port = match.groups()
    _METASTORE_LOC_CACHE = (is_local, host, int(port))
  return _METASTORE_LOC_CACHE


def _parse_hive_site():
  """
  Parse hive-site.xml and store in _HIVE_SITE_DICT
  """
  global _HIVE_SITE_DICT
  global _HIVE_SITE_PATH

  _HIVE_SITE_PATH = os.path.join(beeswax.conf.BEESWAX_HIVE_CONF_DIR.get(), 'hive-site.xml')
  try:
    data = file(_HIVE_SITE_PATH, 'r').read()
  except IOError, err:
    if err.errno != errno.ENOENT:
      LOG.error('Cannot read from "%s": %s' % (_HIVE_SITE_PATH, err))
      return
    # Keep going and make an empty ConfParse
    data = ""

  _HIVE_SITE_DICT = confparse.ConfParse(data)
