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

from hadoop.core_site import get_conf

from django.utils.translation import ugettext as _

LOG = logging.getLogger(__name__)

_CNF_CAB_ADDRESS='fs.%s.ext.cab.address' # http://host:8444/gateway
_CNF_CAB_ADDRESS_DT_PATH='fs.%s.ext.cab.dt.path' # dt
_CNF_CAB_ADDRESS_PATH='fs.%s.ext.cab.path' # aws-cab
_CNF_CAB_USERNAME='fs.%s.ext.cab.username' # when not using kerberos
_CNF_CAB_PASSWORD='fs.%s.ext.cab.password'
SUPPORTED_FS = {'s3a': 's3a', 'adl': 'azure', 'abfs': 'azure', 'azure': 'azure', 'gs': 'gs'}

def validate_fs(fs=None):
  if fs in SUPPORTED_FS:
    return SUPPORTED_FS[fs]
  else:
    LOG.warn('Selected FS %s is not supported by Hue IDBroker client' % fs)
    return None

def get_cab_address(fs=None):
  fs = validate_fs(fs)
  return get_conf().get(_CNF_CAB_ADDRESS % fs) if fs else None

def get_cab_dt_path(fs=None):
  fs = validate_fs(fs)
  return get_conf().get(_CNF_CAB_ADDRESS_DT_PATH % fs) if fs else None

def get_cab_path(fs=None):
  fs = validate_fs(fs)
  return get_conf().get(_CNF_CAB_ADDRESS_PATH % fs) if fs else None

def get_cab_username(fs=None):
  fs = validate_fs(fs)
  return get_conf().get(_CNF_CAB_USERNAME % fs) if fs else None

def get_cab_password(fs=None):
  fs = validate_fs(fs)
  return get_conf().get(_CNF_CAB_PASSWORD % fs) if fs else None

def is_idbroker_enabled(fs=None):
  return get_cab_address(fs) is not None

def config_validator():
  res = []
  from desktop.lib.idbroker.client import IDBroker # Circular dependency
  if is_idbroker_enabled():
    try:
      for fs in SUPPORTED_FS:
        client = IDBroker.from_core_site(fs)
      token = client.get_auth_token()
      if not token:
        raise ValueError('Failed to obtain IDBroker Token')
    except Exception as e:
      LOG.exception('Failed to obtain IDBroker Token')
      res.append(('idbroker', _('Failed to obtain IDBroker Token, check your IDBroker configuration.')))

  return res
