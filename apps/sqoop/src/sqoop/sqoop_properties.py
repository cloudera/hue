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
import os

from sqoop.conf import SQOOP_CONF_DIR


LOG = logging.getLogger(__name__)


_PROPERTIES_DICT = None
_CONF_SQOOP_AUTHENTICATION_TYPE = 'org.apache.sqoop.security.authentication.type'


def reset():
  global _PROPERTIES_DICT
  _PROPERTIES_DICT = None


def get_props():
  if _PROPERTIES_DICT is None:
    _parse_properties()
  return _PROPERTIES_DICT


def has_sqoop_has_security():
  return get_props().get(_CONF_SQOOP_AUTHENTICATION_TYPE, 'SIMPLE').upper() == 'KERBEROS'



def _parse_properties():
  global _PROPERTIES_DICT

  properties_file = os.path.join(SQOOP_CONF_DIR.get(), 'sqoop.properties')
  _PROPERTIES_DICT = _parse_site(properties_file)


def _parse_site(site_path):
  try:
    with open(site_path, 'r') as f:
      data = f.read()
  except IOError, err:
    if err.errno != errno.ENOENT:
      LOG.error('Cannot read from "%s": %s' % (site_path, err))
      return
    data = ""

  return dict([line.split('=', 1) for line in data.split('\n') if '=' in line and not line.startswith('#')])
