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

import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm as AuthAuthenticationForm, UserCreationForm as AuthUserCreationForm
from django.forms import CharField, TextInput, PasswordInput, ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _t, ugettext as _

from desktop import conf


class AuthenticationForm(AuthAuthenticationForm):
  """
  Adds appropriate classes to authentication form
  """
  error_messages = {
    'invalid_login': _t("Invalid username or password."),
    'inactive': _t("Account deactivated. Please contact an administrator."),
  }

  username = CharField(label=_t("Username"), max_length=30, widget=TextInput(attrs={'maxlength': 30, 'placeholder': _t("Username"), "autofocus": "autofocus"}))
  password = CharField(label=_t("Password"), widget=PasswordInput(attrs={'placeholder': _t("Password")}))

  def clean(self):
    if conf.AUTH.EXPIRES_AFTER.get() > -1:
      try:
        user = User.objects.get(username=self.cleaned_data.get('username'))

        expires_delta = datetime.timedelta(seconds=conf.AUTH.EXPIRES_AFTER.get())
        if user.is_active and user.last_login + expires_delta < datetime.datetime.now():
          if user.is_superuser:
            if conf.AUTH.EXPIRE_SUPERUSERS.get():
              user.is_active = False
              user.save()
          else:
            user.is_active = False
            user.save()

        if not user.is_active:
          if settings.ADMINS:
            raise ValidationError(mark_safe(_("Account deactivated. Please contact an <a href=\"mailto:%s\">administrator</a>.") % settings.ADMINS[0][1]))
          else:
            raise ValidationError(self.error_messages['inactive'])
      except User.DoesNotExist:
        # Skip because we couldn't find a user for that username.
        # This means the user managed to get their username wrong.
        pass

    return super(AuthenticationForm, self).clean()


class UserCreationForm(AuthUserCreationForm):
  """
  Accepts one password field and populates the others.
  password fields with the value of that password field
  Adds appropriate classes to authentication form.
  """
  password = CharField(label=_t("Password"), widget=PasswordInput(attrs={'class': 'input-large'}))

  def __init__(self, data=None, *args, **kwargs):
    if data and 'password' in data:
      data = data.copy()
      data['password1'] = data['password']
      data['password2'] = data['password']
    super(UserCreationForm, self).__init__(data=data, *args, **kwargs)
