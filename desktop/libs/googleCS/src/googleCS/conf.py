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
#from hadoop.core_site import get_google_access_key, get_google_secret_key, get_google_authorize_code

PERMISSION_ACTION_GOOGLE = "google_access"
REDIRECT_URI = ""

def get_default_client_id():
  """
  Attempt to set AWS access key ID from script, else core-site, else None
  """
  access_key_id_script = GOOGLE_ACCOUNTS['default'].ACCESS_KEY_ID_SCRIPT.get()
  return access_key_id_script #or get_google_access_key()


def get_default_secret_key():
  """
  Attempt to set google secret key from script, else core-site, else None
  """
  secret_access_key_script = GOOGLE_ACCOUNTS['default'].SECRET_KEY_SCRIPT.get()
  return secret_access_key_script #or get_google_secret_key()


def get_default_authorize_code():
  """
  Attempt to set AWS secret key from script, else core-site, else None
  """
  authorize_code_script = GOOGLE_ACCOUNTS['default'].AUTHORIZE_CODE_SCRIPT.get()
  return authorize_code_script #or get_google_authorize_code()


GOOGLE_ACCOUNTS = UnspecifiedConfigSection(
  'google_accounts',
  help=_('One entry for each Google account'),
  each=ConfigSection(
    help=_('Information about single Google account'),
    members=dict(
      CLIENT_ID=Config(
        key='client_id',
        type=str,
        dynamic_default=get_default_client_id
      ),
      CLIENT_ID_SCRIPT=Config(
        key='client_id_script',
        default=None,
        private=True,
        type=coerce_password_from_script,
        help=_("Execute this script to produce the AWS access key ID.")),
      SECRET_KEY=Config(
        key='secret_access_key',
        type=str,
        private=True,
        dynamic_default=get_default_secret_key
      ),
      SECRET_KEY_SCRIPT=Config(
        key='secret_access_key_script',
        default=None,
        private=True,
        type=coerce_password_from_script,
        help=_("Execute this script to produce the AWS secret access key.")
      )
    )
  )
)

def is_googlefs_enabled():
  return ('default' in list(GOOGLE_ACCOUNTS_ACCOUNTS.keys()) and GOOGLE_ACCOUNTS['default'].get_raw() and GOOGLE_ACCOUNTS['default'].CLIENT_ID.get() is not None )

def has_googlefs_access(user):
  from desktop.auth.backend import is_admin
  return user.is_authenticated() and user.is_active and (is_admin(user) or user.has_hue_permission(action="google_access", app="filebrowser"))
