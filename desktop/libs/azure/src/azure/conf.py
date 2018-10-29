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


from django.utils.translation import ugettext_lazy as _, ugettext as _t

from desktop.lib.conf import Config, UnspecifiedConfigSection, ConfigSection, coerce_password_from_script
from hadoop.core_site import get_adls_client_id, get_adls_authentication_code, get_adls_refresh_url

LOG = logging.getLogger(__name__)

REFRESH_URL = 'https://login.microsoftonline.com/<tenant_id>/oauth2/token'


def get_default_client_id():
  """
  Attempt to set AWS client id from script, else core-site, else None
  """
  client_id_script = AZURE_ACCOUNTS['default'].CLIENT_ID_SCRIPT.get()
  return client_id_script or get_adls_client_id()

def get_default_secret_key():
  """
  Attempt to set AWS secret key from script, else core-site, else None
  """
  client_secret_script = AZURE_ACCOUNTS['default'].CLIENT_SECRET_SCRIPT.get()
  return client_secret_script or get_adls_authentication_code()

def get_default_tenant_id():
  """
  Attempt to set AWS tenant id from script, else core-site, else None
  """
  tenant_id_script = AZURE_ACCOUNTS['default'].TENANT_ID_SCRIPT.get()
  return tenant_id_script or get_adls_refresh_url()

def get_default_refresh_url():
  refresh_url = REFRESH_URL.replace('<tenant_id>', AZURE_ACCOUNTS['default'].TENANT_ID.get())
  refresh_url = refresh_url if refresh_url else get_adls_refresh_url()
  return refresh_url or get_adls_refresh_url()

def get_default_region():
  return ""

def get_default_adls_url():
  return ADLS_CLUSTERS['default'].WEBHDFS_URL.get()

def get_default_adls_fs():
  return ADLS_CLUSTERS['default'].FS_DEFAULTFS.get()

ADLS_CLUSTERS = UnspecifiedConfigSection(
  "adls_clusters",
  help="One entry for each ADLS cluster",
  each=ConfigSection(
    help="Information about a single ADLS cluster",
    members=dict(
      FS_DEFAULTFS=Config("fs_defaultfs", help="adl://<account_name>.azuredatalakestore.net", type=str, default=None),
      WEBHDFS_URL=Config("webhdfs_url",
                         help="https://<account_name>.azuredatalakestore.net/webhdfs/v1",
                         type=str, default=None),
    )
  )
)

AZURE_ACCOUNTS = UnspecifiedConfigSection(
  "azure_accounts",
  help="One entry for each Azure account",
  each=ConfigSection(
    help="Information about a single azure account",
    members=dict(
      CLIENT_ID=Config(
        key="client_id",
        type=str,
        dynamic_default=get_default_client_id,
        help="https://docs.microsoft.com/en-us/azure/data-lake-store/data-lake-store-service-to-service-authenticate-rest-api"),
      CLIENT_ID_SCRIPT=Config(
        key="client_id_script",
        type=coerce_password_from_script,
        default=None,
        private=True,
        help="Execute this script to produce the ADLS client id."),
      CLIENT_SECRET=Config(
        key="client_secret",
        type=str,
        dynamic_default=get_default_secret_key,
        private=True,
        help="https://docs.microsoft.com/en-us/azure/data-lake-store/data-lake-store-service-to-service-authenticate-rest-api"),
      CLIENT_SECRET_SCRIPT=Config(
        key='client_secret_script',
        type=coerce_password_from_script,
        default=None,
        private=True,
        help=_("Execute this script to produce the ADLS client secret.")),
      TENANT_ID=Config(
        key="tenant_id",
        type=str,
        dynamic_default=get_default_tenant_id,
        help="https://docs.microsoft.com/en-us/azure/data-lake-store/data-lake-store-service-to-service-authenticate-rest-api"),
      TENANT_ID_SCRIPT=Config(
        key='tenant_id_script',
        type=coerce_password_from_script,
        default=None,
        private=True,
        help=_("Execute this script to produce the ADLS tenant id.")),
    )
  )
)


def is_adls_enabled():
  return ('default' in AZURE_ACCOUNTS.keys() and AZURE_ACCOUNTS['default'].get_raw() and AZURE_ACCOUNTS['default'].CLIENT_ID.get() is not None)

def has_adls_access(user):
  from desktop.auth.backend import is_admin
  return user.is_authenticated() and user.is_active and (is_admin(user) or user.has_hue_permission(action="adls_access", app="filebrowser"))

def config_validator(user):
  res = []

  import azure.client # Avoid cyclic loop

  if is_adls_enabled():
    try:
      headers = azure.client.get_client('default')._getheaders()
      if not headers.get('Authorization'):
        raise ValueError('Failed to obtain Azure authorization token')
    except Exception, e:
      LOG.exception('Failed to obtain Azure authorization token.')
      res.append(('azure', _t('Failed to obtain Azure authorization token, check your azure configuration.')))

  return res
