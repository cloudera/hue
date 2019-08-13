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
from hadoop.core_site import get_google_access_key, get_google_secret_key, get_goggle_refresh_token, get_google_access_token

def get_default_access_key_id():
  """
  Attempt to set AWS access key ID from script, else core-site, else None
  """
  access_key_id_script = GOOGLE_ACCOUNTS['default'].ACCESS_KEY_ID_SCRIPT.get()
  return access_key_id_script or get_google_access_key()


def get_default_secret_key():
  """
  Attempt to set google secret key from script, else core-site, else None
  """
  secret_access_key_script = GOOGLE_ACCOUNTS['default'].SECRET_ACCESS_KEY_SCRIPT.get()
  return secret_access_key_script or get_google_secret_key()


def get_default_session_token():
  """
  Attempt to set AWS secret key from script, else core-site, else None
  """
  return get_s3a_session_token()


GOOGLE_ACCOUNTS = UnspecifiedConfigSection(
  'google_accounts',
  help=_('One entry for each Google account'),
  each=ConfigSection(
    help=_('Information about single Google account'),
    members=dict(
      ACCESS_KEY_ID=Config(
        key='access_key_id',
        type=str,
        dynamic_default=get_default_access_key_id
      ),
      ACCESS_KEY_ID_SCRIPT=Config(
        key='access_key_id_script',
        default=None,
        private=True,
        type=coerce_password_from_script,
        help=_("Execute this script to produce the AWS access key ID.")),
      SECRET_ACCESS_KEY=Config(
        key='secret_access_key',
        type=str,
        private=True,
        dynamic_default=get_default_secret_key
      ),
      SECRET_ACCESS_KEY_SCRIPT=Config(
        key='secret_access_key_script',
        default=None,
        private=True,
        type=coerce_password_from_script,
        help=_("Execute this script to produce the AWS secret access key.")
      )
    )
  )
)