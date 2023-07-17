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
import sys
import requests

from requests_kerberos import HTTPKerberosAuth
from hadoop.core_site import get_conf

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t
else:
  from django.utils.translation import ugettext_lazy as _t

LOG = logging.getLogger()

_CNF_CAB_ADDRESS = 'fs.%s.ext.cab.address' # http://host:8444/gateway
_CNF_CAB_ADDRESS_DT_PATH = 'fs.%s.ext.cab.dt.path' # dt
_CNF_CAB_ADDRESS_PATH = 'fs.%s.ext.cab.path' # aws-cab
_CNF_CAB_USERNAME = 'fs.%s.ext.cab.username' # when not using kerberos
_CNF_CAB_PASSWORD = 'fs.%s.ext.cab.password'
SUPPORTED_FS = {'s3a': 's3a', 'adl': 'azure', 'abfs': 'azure', 'azure': 'azure', 'gs': 'gs'}

def validate_fs(fs=None):
  if fs in SUPPORTED_FS:
    return SUPPORTED_FS[fs]
  else:
    LOG.warning('Selected FS %s is not supported by Hue IDBroker client' % fs)
    return None

def _handle_idbroker_ha(fs=None):
  fs = validate_fs(fs)
  idbrokeraddr = get_conf().get(_CNF_CAB_ADDRESS % fs) if fs else None
  response = None
  if fs:
    id_broker_addr = get_conf().get(_CNF_CAB_ADDRESS % fs)
    if id_broker_addr:
      id_broker_addr_list = id_broker_addr.split(',')
      for id_broker_addr in id_broker_addr_list:
        try:
          response = requests.get(id_broker_addr.rstrip('/') + '/dt/knoxtoken/api/v1/token', auth=HTTPKerberosAuth(), verify=False)
        except Exception as e:
          if 'Name or service not known' in str(e):
            LOG.warn('IDBroker %s is not available for use' % id_broker_addr)
        # Check response for None and if response code is successful (200) or authentication needed (401)
        if (response is not None) and (response.status_code in (200, 401)):
          idbrokeraddr = id_broker_addr
          break
      return idbrokeraddr
    else:
      return idbrokeraddr
  else:
    return idbrokeraddr

def get_cab_address(fs=None):
  return _handle_idbroker_ha(fs)

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
  from desktop.conf import RAZ  # Must be imported dynamically in order to have proper value

  return get_cab_address(fs) is not None and not RAZ.IS_ENABLED.get() # Skipping IDBroker for FS when RAZ is present

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
      res.append(('idbroker', _t('Failed to obtain IDBroker Token, check your IDBroker configuration.')))

  return res
