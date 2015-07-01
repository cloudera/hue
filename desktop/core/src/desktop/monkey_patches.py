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

import re

from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from desktop.lib.django_util import get_username_re_rule


def monkey_patch_username_validator():
  """
  In 1.6, the `User.username` field gained some validation rules to check that
  it conformed to a particular regex. Unfortunately we use to support a more
  liberal username scheme. The proper solution would be to use our own custom
  user model, but that touches a lot of code. It's easier if we just modify the
  regular expression inside the username validator.
  """

  username = User._meta.get_field("username")

  regex = re.compile('^%s$' % get_username_re_rule())

  for validator in username.validators:
    if isinstance(validator, RegexValidator):
      validator.regex = regex


monkey_patch_username_validator()
