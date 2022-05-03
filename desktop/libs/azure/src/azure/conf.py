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

from desktop.lib.conf import Config, UnspecifiedConfigSection, ConfigSection, coerce_password_from_script
from desktop.lib.idbroker import conf as conf_idbroker

from hadoop import core_site

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t
else:
  from django.utils.translation import ugettext_lazy as _t

LOG = logging.getLogger(__name__)

PERMISSION_ACTION_ABFS = "abfs_access"
PERMISSION_ACTION_ADLS = "adls_access"
REFRESH_URL = 'https://login.microsoftonline.com/<tenant_id>/oauth2/<version>token'
META_DATA_URL = 'http://169.254.169.254/metadata/instance'
AZURE_METADATA = None

def get_default_client_id():
  """
  Attempt to set AWS client id from script, else core-site, else None
  """
  client_id_script = AZURE_ACCOUNTS['default'].CLIENT_ID_SCRIPT.get()
  return client_id_script or core_site.get_adls_client_id() or core_site.get_azure_client_id()

def get_default_secret_key():
  """
  Attempt to set AWS secret key from script, else core-site, else None
  """
  client_secret_script = AZURE_ACCOUNTS['default'].CLIENT_SECRET_SCRIPT.get()
  return client_secret_script or core_site.get_adls_authentication_code() or core_site.get_azure_client_secret()

def get_default_tenant_id():
  """
  Attempt to set AWS tenant id from script, else core-site, else None
  """
  return AZURE_ACCOUNTS['default'].TENANT_ID_SCRIPT.get()

def get_refresh_url(conf, version):
  refresh_url = core_site.get_adls_refresh_url() or core_site.get_azure_client_endpoint()
  if not refresh_url:
    refresh_url = REFRESH_URL.replace('<tenant_id>', conf.TENANT_ID.get()).replace('<version>', version + '/' if version else '')
  return refresh_url

def get_default_region():
  return ""

def get_default_adls_url():
  return ADLS_CLUSTERS['default'].WEBHDFS_URL.get()

def get_default_adls_fs():
  return ADLS_CLUSTERS['default'].FS_DEFAULTFS.get()

def get_default_abfs_url():
  return ABFS_CLUSTERS['default'].WEBHDFS_URL.get()

def get_default_abfs_fs():
  default_fs = core_site.get_default_fs()

  return default_fs if default_fs and default_fs.startswith('abfs://') and \
                       ABFS_CLUSTERS['default'].ENABLE_DEFAULTFS_FROM_CORESITE.get() else ABFS_CLUSTERS['default'].FS_DEFAULTFS.get()

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
        help=_t("Execute this script to produce the ADLS client secret.")),
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
        help=_t("Execute this script to produce the ADLS tenant id.")),
    )
  )
)

ABFS_CLUSTERS = UnspecifiedConfigSection(
  "abfs_clusters",
  help="One entry for each ABFS cluster",
  each=ConfigSection(
    help="Information about a single ABFS cluster",
    members=dict(
      ENABLE_DEFAULTFS_FROM_CORESITE=Config(
        key="enable_defaultfs_from_coresite",
        type=bool,
        default=True,
        help="Enable this param to use the defaultFS from core-site.xml"),
      FS_DEFAULTFS=Config("fs_defaultfs", help="abfs://<container_name>@<account_name>.dfs.core.windows.net", type=str, default=None),
      WEBHDFS_URL=Config("webhdfs_url",
                         help="https://<account_name>.dfs.core.windows.net",
                         type=str, default=None),
    )
  )
)

def is_adls_enabled():
  return ('default' in list(AZURE_ACCOUNTS.keys()) and AZURE_ACCOUNTS['default'].get_raw() and AZURE_ACCOUNTS['default'].CLIENT_ID.get() \
    or (conf_idbroker.is_idbroker_enabled('azure') and has_azure_metadata())) and 'default' in list(ADLS_CLUSTERS.keys())

def is_abfs_enabled():
  from desktop.conf import RAZ  # Must be imported dynamically in order to have proper value

  return ('default' in list(AZURE_ACCOUNTS.keys()) and AZURE_ACCOUNTS['default'].get_raw() and AZURE_ACCOUNTS['default'].CLIENT_ID.get() \
    or (conf_idbroker.is_idbroker_enabled('azure') and has_azure_metadata())) and 'default' in list(ABFS_CLUSTERS.keys()) \
    or (RAZ.IS_ENABLED.get() and 'default' in list(ABFS_CLUSTERS.keys()))

def has_adls_access(user):
  from desktop.conf import RAZ  # Must be imported dynamically in order to have proper value
  from desktop.auth.backend import is_admin

  return user.is_authenticated and user.is_active and (
    is_admin(user) or user.has_hue_permission(action="adls_access", app="filebrowser") or RAZ.IS_ENABLED.get()
  )

def has_abfs_access(user):
  from desktop.conf import RAZ  # Must be imported dynamically in order to have proper value
  from desktop.auth.backend import is_admin

  return user.is_authenticated and user.is_active and (
    is_admin(user) or user.has_hue_permission(action="abfs_access", app="filebrowser") or RAZ.IS_ENABLED.get()
  )

def azure_metadata():
  global AZURE_METADATA
  if AZURE_METADATA is None:
    from desktop.lib.rest import http_client, resource
    client = http_client.HttpClient(META_DATA_URL, logger=LOG)
    root = resource.Resource(client)
    try:
      AZURE_METADATA = root.get('/compute', params={'api-version': '2019-06-04', 'format': 'json'}, headers={'Metadata': 'true'})
    except Exception as e:
      AZURE_METADATA = False
  return AZURE_METADATA

def has_azure_metadata():
  return azure_metadata() is not None

def config_validator(user):
  res = []

  import desktop.lib.fsmanager # Avoid cyclic loop

  if is_adls_enabled() or is_abfs_enabled():
    try:
      headers = desktop.lib.fsmanager.get_client(name='default', fs='abfs')._getheaders()
      if not headers.get('Authorization'):
        raise ValueError('Failed to obtain Azure authorization token')
    except Exception as e:
      LOG.exception('Failed to obtain Azure authorization token.')
      res.append(('azure', _t('Failed to obtain Azure authorization token, check your azure configuration.')))

  return res
