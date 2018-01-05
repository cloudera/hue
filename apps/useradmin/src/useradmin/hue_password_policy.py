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


from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from useradmin.conf import PASSWORD_POLICY

import re


_PASSWORD_POLICY = None


class PasswordPolicy(object):

  def __init__(self, is_enabled, rule, hint, error_message):

    self._is_enabled = is_enabled
    self._rule = rule
    self._hint = hint
    self._message = error_message
    self._valid_pattern = re.compile(self._rule)

  def validate_password(self, password):
    if self._is_enabled and not self._valid_pattern.match(password):
      raise ValidationError(_(self._message))

  @property
  def password_hint(self):
    return _(self._hint)

  @property
  def is_enabled(self):
    return self._is_enabled


def get_password_policy():
  global _PASSWORD_POLICY
  if _PASSWORD_POLICY is None:
    _PASSWORD_POLICY = PasswordPolicy(is_enabled=PASSWORD_POLICY.IS_ENABLED.get(),
                                      rule=PASSWORD_POLICY.PWD_RULE.get(),
                                      hint=PASSWORD_POLICY.PWD_HINT.get(),
                                      error_message=PASSWORD_POLICY.PWD_ERROR_MESSAGE.get())

  return _PASSWORD_POLICY


def reset_password_policy():
  global _PASSWORD_POLICY
  _PASSWORD_POLICY = None


def hue_get_password_validators():
  def validate_against_policy(password):
    get_password_policy().validate_password(password)

  return [validate_against_policy]


def is_password_policy_enabled():
  return get_password_policy().is_enabled


def get_password_hint():
  return  get_password_policy().password_hint
