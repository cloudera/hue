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
import json
import os

from django.utils.translation import ugettext_lazy as _t, ugettext as _

from desktop.lib.conf import Config, coerce_bool, coerce_csv


BASEDIR = os.path.dirname(os.path.abspath(__file__))


def dict_list_map(value):
  if isinstance(value, str):
    d = {}
    for k, v in json.loads(value).iteritems():
      d[k] = (v,)
    return d
  elif isinstance(value, dict):
    return value
  return None


SERVER_ENDPOINT_URL = Config(
  key="server_endpoint_url",
  default="https://www.google.com/accounts/o8/id",
  type=str,
  help=_t("OpenId SSO endpoint url"))

IDENTITY_URL_PREFIX = Config(
  key="identity_url_prefix",
  default="https://app.onelogin.com/openid/your_company.com/",
  type=str,
  help=_t("Openid identity url prefix"))

CREATE_USERS_ON_LOGIN = Config(
  key="create_users_on_login",
  default=True,
  type=coerce_bool,
  help=_t("Create users from IdP on login."))

USE_EMAIL_FOR_USERNAME = Config(
  key="use_email_for_username",
  default=True,
  type=coerce_bool,
  help=_t("Use email for username."))


def config_validator(user):
  res = []
  if not SERVER_ENDPOINT_URL.get():
    res.append(("libopenid.server_endpoint_url", _("Required OPENID SSO endpoint URL is not provided.")))
  return res
