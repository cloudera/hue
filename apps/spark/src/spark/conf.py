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
import os
import sys

from django.utils.translation import ugettext_lazy as _t, ugettext as _

from desktop.conf import default_ssl_validate
from desktop.lib.conf import Config, coerce_bool
from spark.settings import NICE_NAME


LOG = logging.getLogger(__name__)


# Livy
LIVY_SERVER_URL = Config(
  key="livy_server_url",
  help=_t("The Livy Server URL."),
  default="")

# Deprecated
LIVY_SERVER_HOST = Config(
  key="livy_server_host",
  help=_t("Host address of the Livy Server."),
  default="localhost")

# Deprecated
LIVY_SERVER_PORT = Config(
  key="livy_server_port",
  help=_t("Port of the Livy Server."),
  default="8998")

LIVY_SERVER_SESSION_KIND = Config( # Note: this one is ignored by Livy, this should match the current Spark mode
   key="livy_server_session_kind",
   help=_t("Configure livy to start in local 'process' mode, or 'yarn' workers."),
   default="yarn")

SECURITY_ENABLED = Config(
  key="security_enabled",
  help=_t("Whether Livy requires client to perform Kerberos authentication."),
  default=False,
  type=coerce_bool)

CSRF_ENABLED = Config(
  key="csrf_enabled",
  help=_t("Whether Livy requres client to have CSRF enabled."),
  default=False,
  type=coerce_bool)

# Spark SQL
SQL_SERVER_HOST = Config(
  key="sql_server_host",
  help=_t("Host where SparkSQL server is running."),
  default="localhost")

SQL_SERVER_PORT = Config(
  key="sql_server_port",
  help=_t("Port the SparkSQL server runs on."),
  default=10000,
  type=int)

SSL_CERT_CA_VERIFY = Config(
  key="ssl_cert_ca_verify",
  help=_t("Choose whether Hue should validate certificates received from the server."),
  dynamic_default=default_ssl_validate,
  type=coerce_bool
)


def get_livy_server_url():
  url = LIVY_SERVER_URL.get()
  if not url:
    # backward compatibility
    url = 'http://%s:%s' % (LIVY_SERVER_HOST.get(), LIVY_SERVER_PORT.get())
  return url

def get_spark_status(user):
  from spark.job_server_api import get_api
  status = None

  try:
    if not 'test' in sys.argv: # Avoid tests hanging
      get_api(user).get_status()
      status = 'OK'
  except:
    LOG.exception('failed to get spark status')

  return status


def config_validator(user):
  res = []

  status = get_spark_status(user)

  if status != 'OK':
    res.append((NICE_NAME, _("The app won't work without a running Livy Spark Server")))

  return res
