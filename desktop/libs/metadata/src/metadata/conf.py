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

from django.utils.translation import ugettext_lazy as _t

from desktop.conf import AUTH_USERNAME as DEFAULT_AUTH_USERNAME, AUTH_PASSWORD as DEFAULT_AUTH_PASSWORD, \
  AUTH_PASSWORD_SCRIPT, coerce_password_from_script
from desktop.lib.conf import Config, ConfigSection, coerce_string


def get_auth_username():
  """Get from top level default from desktop"""
  return DEFAULT_AUTH_USERNAME.get()


def get_auth_password():
  """Get from script or backward compatibility"""
  password = AUTH_PASSWORD_SCRIPT.get()
  if password:
    return password
  return DEFAULT_AUTH_PASSWORD.get()


NAVIGATOR = ConfigSection(
  key='navigator',
  help=_t("""Configuration options for Navigator API"""),
  members=dict(
    API_URL=Config(
      key='api_url',
      help=_t('Base URL to Navigator API'),
      default='http://localhost:7187/api/v2',
      type=coerce_string),
    AUTH_USERNAME=Config(
      key="auth_username",
      help=_t("Auth username of the hue user used for authentications."),
      private=True,
      dynamic_default=get_auth_username),
    AUTH_PASSWORD=Config(
      key="auth_password",
      help=_t("LDAP/PAM/.. password of the hue user used for authentications."),
      private=True,
      dynamic_default=get_auth_password),
    AUTH_PASSWORD_SCRIPT=Config(
      key="auth_password_script",
      help=_t("Execute this script to produce the auth password. This will be used when `auth_password` is not set."),
      private=True,
      type=coerce_password_from_script,
      default=None),
  )
)
