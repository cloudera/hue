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

import logging

from subprocess import CalledProcessError

from django.utils.translation import ugettext_lazy as _t

from desktop.conf import AUTH_USERNAME as DEFAULT_AUTH_USERNAME, CLUSTER_ID as DEFAULT_CLUSTER_ID
from desktop.lib.conf import Config, ConfigSection, coerce_bool, coerce_password_from_script
from desktop.lib.paths import get_config_root

from metadata.settings import DJANGO_APPS


OPTIMIZER_AUTH_PASSWORD = None
NAVIGATOR_AUTH_PASSWORD = None

LOG = logging.getLogger(__name__)


def get_auth_username():
  """Get from top level default from desktop"""
  return DEFAULT_AUTH_USERNAME.get()


def default_navigator_config_dir():
  """Get from usual main Hue config directory"""
  return get_config_root()


def default_navigator_url():
  """Get from usual main Hue config directory"""
  from metadata.metadata_sites import get_navigator_server_url
  return get_navigator_server_url() + '/api'


def get_optimizer_url():
  return OPTIMIZER.HOSTNAME.get() and OPTIMIZER.HOSTNAME.get().strip('/')

def has_optimizer():
  return bool(OPTIMIZER.AUTH_KEY_ID.get())


def get_navigator_url():
  return NAVIGATOR.API_URL.get() and NAVIGATOR.API_URL.get().strip('/')[:-3]

def has_navigator(user):
  return bool(get_navigator_url() and get_navigator_auth_password()) \
      and (user.is_superuser or user.has_hue_permission(action="access", app=DJANGO_APPS[0]))


def get_security_default():
  '''Get default security value from Hadoop'''
  from hadoop import cluster # Avoid dependencies conflicts
  cluster = cluster.get_yarn()

  return cluster.SECURITY_ENABLED.get()


def get_optimizer_password_script():
  '''Get default password from secured file'''
  global OPTIMIZER_AUTH_PASSWORD

  if OPTIMIZER_AUTH_PASSWORD is None:
    OPTIMIZER_AUTH_PASSWORD = OPTIMIZER.AUTH_KEY_SECRET_SCRIPT.get()

  return OPTIMIZER_AUTH_PASSWORD


OPTIMIZER = ConfigSection(
  key='optimizer',
  help=_t("""Configuration options for Optimizer API"""),
  members=dict(
    HOSTNAME=Config(
      key='hostname',
      help=_t('Hostname to Optimizer API or compatible service.'),
      default='navoptapi.us-west-1.optimizer.altus.cloudera.com'),

    AUTH_KEY_ID=Config(
      key="auth_key_id",
      help=_t("The name of the key of the service."),
      private=False,
      default=None),
    AUTH_KEY_SECRET=Config(
      key="auth_key_secret",
      help=_t("The private part of the key associated with the auth_key."),
      private=True,
      dynamic_default=get_optimizer_password_script),
    AUTH_KEY_SECRET_SCRIPT=Config(
      key="auth_key_secret_script",
      help=_t("Execute this script to produce the auth_key secret. This will be used when `auth_key_secret` is not set."),
      private=True,
      type=coerce_password_from_script,
      default=None),
    TENANT_ID=Config(
      key="tenant_id",
      help=_t("The name of the workload where queries are uploaded and optimizations are calculated from. Automatically guessed from auth_key and cluster_id if not specified."),
      private=True,
      default=None),
    CLUSTER_ID=Config(
      key="cluster_id",
      help=_t("The name of the cluster used to determine the tenant id when this one is not specified. Defaults to the cluster Id or 'default'."),
      private=True,
      default=DEFAULT_CLUSTER_ID.get()),

    APPLY_SENTRY_PERMISSIONS = Config(
      key="apply_sentry_permissions",
      help=_t("Perform Sentry privilege filtering. Default to true automatically if the cluster is secure."),
      dynamic_default=get_security_default,
      type=coerce_bool
    ),
    CACHEABLE_TTL=Config(
      key='cacheable_ttl',
      type=int,
      help=_t('The cache TTL in milliseconds for the assist/autocomplete/etc calls. Set to 0 to disable the cache.'),
      default=10 * 24 * 60 * 60 * 1000),
    AUTO_UPLOAD_QUERIES = Config(
      key="auto_upload_queries",
      help=_t("Automatically upload queries after their execution in order to improve recommendations."),
      default=True,
      type=coerce_bool
    ),
    AUTO_UPLOAD_DDL = Config(
      key="auto_upload_ddl",
      help=_t("Automatically upload queried tables DDL in order to improve recommendations."),
      default=True,
      type=coerce_bool
    ),
    AUTO_UPLOAD_STATS = Config(
      key="auto_upload_stats",
      help=_t("Automatically upload queried tables and columns stats in order to improve recommendations."),
      default=False,
      type=coerce_bool
    ),
    QUERY_HISTORY_UPLOAD_LIMIT = Config(
      key="query_history_upload_limit",
      help=_t("Allow admins to upload the last N executed queries in the quick start wizard. Use 0 to disable."),
      default=10000,
      type=int
    ),
  )
)


def get_navigator_auth_type():
  return NAVIGATOR.AUTH_TYPE.get().lower()


def get_navigator_auth_username():
  '''Get the username to authenticate with.'''

  if get_navigator_auth_type() == 'ldap':
    return NAVIGATOR.AUTH_LDAP_USERNAME.get()
  elif get_navigator_auth_type() == 'saml':
    return NAVIGATOR.AUTH_SAML_USERNAME.get()
  else:
    return NAVIGATOR.AUTH_CM_USERNAME.get()

def get_navigator_auth_password():
  '''Get the password to authenticate with.'''
  global NAVIGATOR_AUTH_PASSWORD

  if NAVIGATOR_AUTH_PASSWORD is None:
    try:
      if get_navigator_auth_type() == 'ldap':
        NAVIGATOR_AUTH_PASSWORD = NAVIGATOR.AUTH_LDAP_PASSWORD.get()
      elif get_navigator_auth_type() == 'saml':
        NAVIGATOR_AUTH_PASSWORD = NAVIGATOR.AUTH_SAML_PASSWORD.get()
      else:
        NAVIGATOR_AUTH_PASSWORD = NAVIGATOR.AUTH_CM_PASSWORD.get()
    except CalledProcessError:
      LOG.exception('Could not read Navigator password file, need to restart Hue to re-enable it.')

  return NAVIGATOR_AUTH_PASSWORD

def get_navigator_cm_password():
  '''Get default password from secured file'''
  return NAVIGATOR.AUTH_CM_PASSWORD_SCRIPT.get()

def get_navigator_ldap_password():
  '''Get default password from secured file'''
  return NAVIGATOR.AUTH_LDAP_PASSWORD_SCRIPT.get()

def get_navigator_saml_password():
  '''Get default password from secured file'''
  return NAVIGATOR.AUTH_SAML_PASSWORD_SCRIPT.get()


def has_navigator_file_search(user):
  return has_navigator(user) and NAVIGATOR.ENABLE_FILE_SEARCH.get()


NAVIGATOR = ConfigSection(
  key='navigator',
  help=_t("""Configuration options for Navigator API"""),
  members=dict(
    API_URL=Config(
      key='api_url',
      help=_t('Base URL to Navigator API.'),
      dynamic_default=default_navigator_url),
    AUTH_TYPE=Config(
      key="navmetadataserver_auth_type",
      help=_t("Which authentication to use: CM or external via LDAP or SAML."),
      default='CMDB'),

    AUTH_CM_USERNAME=Config(
      key="navmetadataserver_cmdb_user",
      help=_t("Username of the CM user used for authentication."),
      dynamic_default=get_auth_username),
    AUTH_CM_PASSWORD=Config(
      key="navmetadataserver_cmdb_password",
      help=_t("CM password of the user used for authentication."),
      private=True,
      dynamic_default=get_navigator_cm_password),
    AUTH_CM_PASSWORD_SCRIPT=Config(
      key="navmetadataserver_cmdb_password_script",
      help=_t("Execute this script to produce the CM password. This will be used when the plain password is not set."),
      private=True,
      type=coerce_password_from_script,
      default=None),

    AUTH_LDAP_USERNAME=Config(
      key="navmetadataserver_ldap_user",
      help=_t("Username of the LDAP user used for authentication."),
      dynamic_default=get_auth_username),
    AUTH_LDAP_PASSWORD=Config(
      key="navmetadataserver_ldap_password",
      help=_t("LDAP password of the user used for authentication."),
      private=True,
      dynamic_default=get_navigator_ldap_password),
    AUTH_LDAP_PASSWORD_SCRIPT=Config(
      key="navmetadataserver_ldap_password_script",
      help=_t("Execute this script to produce the LDAP password. This will be used when the plain password is not set."),
      private=True,
      type=coerce_password_from_script,
      default=None),

    AUTH_SAML_USERNAME=Config(
      key="navmetadataserver_saml_user",
      help=_t("Username of the SAML user used for authentication."),
      dynamic_default=get_auth_username),
    AUTH_SAML_PASSWORD=Config(
      key="navmetadataserver_saml_password",
      help=_t("SAML password of the user used for authentication."),
      private=True,
      dynamic_default=get_navigator_saml_password),
    AUTH_SAML_PASSWORD_SCRIPT=Config(
      key="navmetadataserver_saml_password_script",
      help=_t("Execute this script to produce the SAML password. This will be used when the plain password  is not set."),
      private=True,
      type=coerce_password_from_script,
      default=None),

    CONF_DIR = Config(
      key='conf_dir',
      help=_t('Navigator configuration directory, where navigator.client.properties is located.'),
      dynamic_default=default_navigator_config_dir
    ),
    APPLY_SENTRY_PERMISSIONS = Config(
      key="apply_sentry_permissions",
      help=_t("Perform Sentry privilege filtering. Default to true automatically if the cluster is secure."),
      dynamic_default=get_security_default,
      type=coerce_bool
    ),
    FETCH_SIZE_SEARCH = Config(
      key="fetch_size_search",
      help=_t("Max number of items to fetch in one call in object search."),
      default=450,
      type=int
    ),
    FETCH_SIZE_SEARCH_INTERACTIVE = Config(
      key="fetch_size_search_interactive",
      help=_t("Max number of items to fetch in one call in object search autocomplete."),
      default=450,
      type=int
    ),

    ENABLE_FILE_SEARCH = Config(
      key="enable_file_search",
      help=_t("Enable to search HDFS, S3 files."),
      type=coerce_bool,
      default=False
    )
  )
)


MANAGER = ConfigSection(
  key='manager',
  help=_t("""Configuration options for Manager API"""),
  members=dict(
    API_URL=Config(
      key='api_url',
      help=_t('Base URL to API.'),
      default=None),
 
    AUTH_CM_USERNAME=Config(
      key="navmetadataserver_cmdb_user",
      help=_t("Username of the CM user used for authentication."),
      dynamic_default=get_auth_username),
    AUTH_CM_PASSWORD=Config(
      key="navmetadataserver_cmdb_password",
      help=_t("CM password of the user used for authentication."),
      private=True,
      dynamic_default=get_navigator_cm_password),
    AUTH_CM_PASSWORD_SCRIPT=Config(
      key="navmetadataserver_cmdb_password_script",
      help=_t("Execute this script to produce the CM password. This will be used when the plain password is not set."),
      private=True,
      type=coerce_password_from_script,
      default=None),

    AUTH_LDAP_USERNAME=Config(
      key="navmetadataserver_ldap_user",
      help=_t("Username of the LDAP user used for authentication."),
      dynamic_default=get_auth_username),
    AUTH_LDAP_PASSWORD=Config(
      key="navmetadataserver_ldap_password",
      help=_t("LDAP password of the user used for authentication."),
      private=True,
      dynamic_default=get_navigator_ldap_password),
    AUTH_LDAP_PASSWORD_SCRIPT=Config(
      key="navmetadataserver_ldap_password_script",
      help=_t("Execute this script to produce the LDAP password. This will be used when the plain password is not set."),
      private=True,
      type=coerce_password_from_script,
      default=None),

    AUTH_SAML_USERNAME=Config(
      key="navmetadataserver_saml_user",
      help=_t("Username of the SAML user used for authentication."),
      dynamic_default=get_auth_username),
    AUTH_SAML_PASSWORD=Config(
      key="navmetadataserver_saml_password",
      help=_t("SAML password of the user used for authentication."),
      private=True,
      dynamic_default=get_navigator_saml_password),
    AUTH_SAML_PASSWORD_SCRIPT=Config(
      key="navmetadataserver_saml_password_script",
      help=_t("Execute this script to produce the SAML password. This will be used when the plain password  is not set."),
      private=True,
      type=coerce_password_from_script,
      default=None),

    CONF_DIR = Config(
      key='conf_dir',
      help=_t('Navigator configuration directory, where navigator.client.properties is located.'),
      dynamic_default=default_navigator_config_dir
    ),
    APPLY_SENTRY_PERMISSIONS = Config(
      key="apply_sentry_permissions",
      help=_t("Perform Sentry privilege filtering. Default to true automatically if the cluster is secure."),
      dynamic_default=get_security_default,
      type=coerce_bool
    ),
    FETCH_SIZE_SEARCH = Config(
      key="fetch_size_search",
      help=_t("Max number of items to fetch in one call in object search."),
      default=450,
      type=int
    ),
    FETCH_SIZE_SEARCH_INTERACTIVE = Config(
      key="fetch_size_search_interactive",
      help=_t("Max number of items to fetch in one call in object search autocomplete."),
      default=450,
      type=int
    ),

    ENABLE_FILE_SEARCH = Config(
      key="enable_file_search",
      help=_t("Enable to search HDFS, S3 files."),
      type=coerce_bool,
      default=False
    )
  )
)


KAFKA = ConfigSection(
  key='kafka',
  help=_t("""Configuration options for Kafka API"""),
  members=dict(
    API_URL=Config(
      key='api_url',
      help=_t('Base URL to API.'),
      default=None),
  )
)


def test_metadata_configurations(user):
  from libsentry.conf import is_enabled

  result = []

  if not is_enabled() and NAVIGATOR.APPLY_SENTRY_PERMISSIONS.get():
    result.append(("metadata", "Please enable Sentry when using metadata with Security."))

  return result
