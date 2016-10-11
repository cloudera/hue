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
                         AUTH_PASSWORD_SCRIPT, default_ssl_validate
from desktop.lib.conf import Config, ConfigSection, coerce_bool, coerce_password_from_script
from desktop.lib.paths import get_config_root

from metadata.settings import DJANGO_APPS


def get_auth_username():
  """Get from top level default from desktop"""
  return DEFAULT_AUTH_USERNAME.get()


def get_auth_password():
  """Get from script or backward compatibility"""
  password = AUTH_PASSWORD_SCRIPT.get()
  if password:
    return password
  return DEFAULT_AUTH_PASSWORD.get()


def default_navigator_config_dir():
  """Get from usual main Hue config directory"""
  return get_config_root()


def default_navigator_url():
  """Get from usual main Hue config directory"""
  from metadata.metadata_sites import get_navigator_server_url
  return get_navigator_server_url() + '/api'


def get_optimizer_url():
  return OPTIMIZER.API_URL.get() and OPTIMIZER.API_URL.get().strip('/')


def has_optimizer():
  return bool(get_optimizer_url())


def get_navigator_url():
  return NAVIGATOR.API_URL.get() and NAVIGATOR.API_URL.get().strip('/')[:-3]


def has_navigator(user):
  return bool(get_navigator_url() and NAVIGATOR.AUTH_PASSWORD.get()) \
      and user.is_superuser or user.has_hue_permission(action="access", app=DJANGO_APPS[0])


OPTIMIZER = ConfigSection(
  key='optimizer',
  help=_t("""Configuration options for Optimizer API"""),
  members=dict(
    API_URL=Config(
      key='api_url',
      help=_t('Base URL to Optimizer API (e.g. - https://alpha.optimizer.cloudera.com/)'),
      default=None),

    PRODUCT_NAME=Config(
      key="product_name",
      help=_t("The name of the product or group which will have API access to the emails associated with it."),
      private=True,
      default=None),
    PRODUCT_SECRET=Config(
      key="product_secret",
      help=_t("A secret passphrase associated with the productName."),
      private=True,
      dynamic_default=get_auth_password),
    PRODUCT_SECRET_SCRIPT=Config(
      key="product_secret_script",
      help=_t("Execute this script to produce the product secret. This will be used when `product_secret` is not set."),
      private=True,
      type=coerce_password_from_script,
      default=None),
    PRODUCT_AUTH_SECRET=Config(
      key="product_auth_secret",
      help=_t("A secret passphrase associated with the productName."),
      private=True,
      dynamic_default=get_auth_password),
    PRODUCT_AUTH_SECRET_SCRIPT=Config(
      key="product_auth_secret_script",
      help=_t("Execute this script to produce the product secret. This will be used when `product_secret` is not set."),
      private=True,
      type=coerce_password_from_script,
      default=None),

    EMAIL=Config(
      key="email",
      help=_t("The email of the Optimizer account you want to associate with the Product."),
      private=True,
      dynamic_default=get_auth_username),
    EMAIL_PASSWORD=Config(
      key="email_password",
      help=_t("The password associated with the Optimizer account you to associate with the Product."),
      private=True,
      dynamic_default=get_auth_password),
    EMAIL_PASSWORD_SCRIPT=Config(
      key="password_script",
      help=_t("Execute this script to produce the email password. This will be used when `email_password` is not set."),
      private=True,
      type=coerce_password_from_script,
      default=None),

    SSL_CERT_CA_VERIFY = Config(
      key="ssl_cert_ca_verify",
      help=_t("In secure mode (HTTPS), if Optimizer SSL certificates have to be verified against certificate authority"),
      dynamic_default=default_ssl_validate,
      type=coerce_bool
    ),

    MOCKING = Config(
      key="mocking",
      help=_t("Use mock data"),
      default=False,
      type=coerce_bool
    )
  )
)


NAVIGATOR = ConfigSection(
  key='navigator',
  help=_t("""Configuration options for Navigator API"""),
  members=dict(
    API_URL=Config(
      key='api_url',
      help=_t('Base URL to Navigator API.'),
      dynamic_default=default_navigator_url),
    AUTH_USERNAME=Config(
      key="auth_username",
      help=_t("Auth username of the hue user used for authentications."),
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
    CONF_DIR = Config(
      key='conf_dir',
      help=_t('Navigator configuration directory, where navigator.client.properties is located.'),
      dynamic_default=default_navigator_config_dir
    )
  )
)
