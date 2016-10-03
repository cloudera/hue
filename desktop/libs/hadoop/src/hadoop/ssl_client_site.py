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


_SSL_SITE_PATH = None                  # Path to ssl-client.xml
_SSL_SITE_DICT = None                  # A dictionary of name/value config options

_CNF_TRUSTORE_LOCATION = 'ssl.client.truststore.location'

LOG = logging.getLogger(__name__)


def reset():
  global _SSL_SITE_DICT
  _SSL_SITE_DICT = None


def get_conf():
  if _SSL_SITE_DICT is None:
    _parse_ssl_client_site()
  return _SSL_SITE_DICT


def _parse_ssl_client_site():
  global _SSL_SITE_DICT
  global _SSL_SITE_PATH

  for indentifier in conf.HDFS_CLUSTERS.get():
    try:
      _SSL_SITE_PATH = os.path.join(conf.HDFS_CLUSTERS[indentifier].HADOOP_CONF_DIR.get(), 'ssl-client.xml')
      data = file(_SSL_SITE_PATH, 'r').read()
      break
    except KeyError:
      data = ""
    except IOError, err:
      if err.errno != errno.ENOENT:
        LOG.error('Cannot read from "%s": %s' % (_SSL_SITE_PATH, err))
        return
      # Keep going and make an empty ConfParse
      data = ""

  _SSL_SITE_DICT = confparse.ConfParse(data)


def get_trustore_location():
  return get_conf().get(_CNF_TRUSTORE_LOCATION)
