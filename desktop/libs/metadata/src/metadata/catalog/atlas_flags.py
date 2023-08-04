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

LOG = logging.getLogger()

_FLAGS = None

_ADDRESS = 'atlas.rest.address'
_KERBEROS = 'atlas.authentication.method.kerberos'


def reset():
  global _FLAGS
  _FLAGS = None


def get_conf():
  if _FLAGS is None:
    _parse_flags()
  return _FLAGS


def get_address():
  return get_conf().get(_ADDRESS)

def get_api_url():
  address = get_address()
  return address if address else None

def is_kerberos_enabled():
  return get_conf().get(_KERBEROS,'').upper() == 'TRUE'


def _parse_flags():
  from metadata import conf
  global _FLAGS

  try:
    flags_path = os.path.join(conf.CATALOG.CONF_DIR.get(), 'atlas-application.properties')
    _FLAGS = dict(line.strip().split('=', 1) for line in open(flags_path) if '=' in line)
  except IOError as err:
    if err.errno != errno.ENOENT:
      LOG.error('Cannot read from "%s": %s' % (flags_path, err))
    _FLAGS = {}
  except Exception as ex:
    LOG.error('Failed to parse config from "%s": %s' % (flags_path, ex))
    _FLAGS = {}
