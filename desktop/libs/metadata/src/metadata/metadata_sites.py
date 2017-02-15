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


LOG = logging.getLogger(__name__)


_SITE_DICT = None

_CONF_NAVIGATOR_SERVER_URL = 'navigator.server.url'
_CONF_NAVIGATOR_AUDIT_LOG_DIR = 'audit_event_log_dir'
_CONF_NAVIGATOR_AUDIT_MAX_FILE_SIZE = 'navigator.audit_log_max_file_size'
_CONF_NAVIGATOR_HUE_SERVER_NAME = 'navigator.client.clusterName'


def reset():
  global _SITE_DICT
  _SITE_DICT = None


def get_conf(name='navigator'):
  if _SITE_DICT is None:
    _parse_sites()
  return _SITE_DICT[name]


def get_navigator_server_url():
  """Returns the navigator.server.url"""
  return get_conf('navigator-lineage').get(_CONF_NAVIGATOR_SERVER_URL, 'http://localhost:7187')


def get_navigator_audit_log_dir():
  """Returns audit_event_log_dir"""
  return get_conf().get(_CONF_NAVIGATOR_AUDIT_LOG_DIR, '')


def get_navigator_audit_max_file_size():
  """Returns navigator.audit_log_max_file_size in MB"""
  size = get_conf().get(_CONF_NAVIGATOR_AUDIT_MAX_FILE_SIZE, '100')
  return '%sMB' % size.strip() if size else "100MB"


def get_navigator_hue_server_name():
  return get_conf('navigator-lineage').get(_CONF_NAVIGATOR_HUE_SERVER_NAME, '')


def _parse_sites():
  from metadata.conf import NAVIGATOR

  global _SITE_DICT
  _SITE_DICT ={}

  paths = [
    ('navigator', os.path.join(NAVIGATOR.CONF_DIR.get(), 'navigator.client.properties')), # 'audit'
    ('navigator-lineage', os.path.join(NAVIGATOR.CONF_DIR.get(), 'navigator.lineage.client.properties')),
  ]

  for name, path in paths:
    _SITE_DICT[name] = _parse_property(path)


def _parse_property(file_path):
  try:
    return dict(line.strip().rsplit('=', 1) for line in open(file_path) if '=' in line)
  except IOError, err:
    if err.errno != errno.ENOENT:
      LOG.error('Cannot read from "%s": %s' % (file_path, err))
    return {}
