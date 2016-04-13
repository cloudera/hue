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
"""
Configuration options for the "user admin" application
"""

from desktop.lib.conf import Config, ConfigSection, coerce_bool
from django.utils.translation import ugettext_lazy as _

HOME_DIR_PERMISSIONS = Config(
    key="home_dir_permissions",
    help=_("New user home directory is created with these permissions"),
    type=str,
    default="0755")

DEFAULT_USER_GROUP = Config(
    key="default_user_group",
    help=_("The name of a default group for users at creation time, or at first login "
           "if the server is configured to authenticate against an external source."),
    type=str,
    default='default')

PASSWORD_POLICY = ConfigSection(
  key="password_policy",
  help=_("Configuration options for user password policy"),
  members=dict(
    IS_ENABLED = Config(
      key="is_enabled",
      help=_("Enable user password policy."),
      type=coerce_bool,
      default=False),

    PWD_RULE = Config(
      key="pwd_regex",
      help=_("The regular expression of password rule. The default rule requires that "
             "a password  must be at least 8 characters long, and must contain both "
             "uppercase and lowercase letters, at least one number, and at least one "
             "special character."),
      type=str,
      default="^(?=.*?[A-Z])(?=(.*[a-z]){1,})(?=(.*[\d]){1,})(?=(.*[\W_]){1,}).{8,}$"),

    PWD_HINT = Config(
      key="pwd_hint",
      help=_("Message about the password rule defined in pwd_regex"),
      type=str,
      default="The password must be at least 8 characters long, and must contain both " + \
              "uppercase and lowercase letters, at least one number, and at least " + \
              "one special character."),

    PWD_ERROR_MESSAGE = Config(
      key="pwd_error_message",
      help=_("The error message displayed if the provided password does not "
             "meet the enhanced password rule"),
      type=str,
      default="The password must be at least 8 characters long, and must contain both " + \
               "uppercase and lowercase letters, at least one number, and at least " + \
               "one special character.")
    )
  )
