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
import logging

from django.conf import settings
from django.contrib.auth import authenticate, get_backends
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm as AuthAuthenticationForm, UserCreationForm as AuthUserCreationForm
from django.forms import CharField, TextInput, PasswordInput, ChoiceField, ValidationError
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _t, ugettext as _

from desktop import conf
from useradmin.hue_password_policy import hue_get_password_validators

from desktop.auth.backend import is_admin

LOG = logging.getLogger(__name__)


def get_backend_names():
  return get_backends and [backend.__class__.__name__ for backend in get_backends()]

def is_active_directory():
  return 'LdapBackend' in get_backend_names() and \
                          (bool(conf.LDAP.NT_DOMAIN.get()) or bool(conf.LDAP.LDAP_SERVERS.get()) or conf.LDAP.LDAP_URL.get() is not None)

def get_ldap_server_keys():
  return [(ldap_server_record_key) for ldap_server_record_key in conf.LDAP.LDAP_SERVERS.get()]

def get_server_choices():
  if conf.LDAP.LDAP_SERVERS.get():
    auth_choices = [(ldap_server_record_key, ldap_server_record_key) for ldap_server_record_key in conf.LDAP.LDAP_SERVERS.get()]
  else:
    auth_choices = [('LDAP', 'LDAP')]

  if is_active_directory() and 'AllowFirstUserDjangoBackend' in get_backend_names():
    auth_choices.append(('Local', _('Local')))

  return auth_choices


class AuthenticationForm(AuthAuthenticationForm):
  """
  Adds appropriate classes to authentication form
  """
  error_messages = {
    'invalid_login': _t("Invalid username or password"),
    'inactive': _t("Account deactivated. Please contact an administrator."),
  }

  username = CharField(label=_t("Username"), widget=TextInput(attrs={'maxlength': 30, 'placeholder': _t("Username"), 'autocomplete': 'off', 'autofocus': 'autofocus'}))
  password = CharField(label=_t("Password"), widget=PasswordInput(attrs={'placeholder': _t("Password"), 'autocomplete': 'off'}))

  def authenticate(self):
    return super(AuthenticationForm, self).clean()

  def clean(self):
    if conf.AUTH.EXPIRES_AFTER.get() > -1:
      try:
        user = User.objects.get(username=self.cleaned_data.get('username'))

        expires_delta = datetime.timedelta(seconds=conf.AUTH.EXPIRES_AFTER.get())
        if user.is_active and user.last_login + expires_delta < datetime.datetime.now():
          INACTIVE_EXPIRATION_DELTA = datetime.timedelta(days=365)
          if is_admin(user):
            if conf.AUTH.EXPIRE_SUPERUSERS.get():
              user.is_active = False
              user.last_login = datetime.datetime.now() + INACTIVE_EXPIRATION_DELTA
              user.save()
          else:
            user.is_active = False
            user.last_login = datetime.datetime.now() + INACTIVE_EXPIRATION_DELTA
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

    return self.authenticate()


class ImpersonationAuthenticationForm(AuthenticationForm):
  login_as = CharField(label=_t("Login as"), max_length=30, widget=TextInput(attrs={'placeholder': _t("Login as username"), 'autocomplete': 'off'}))

  def authenticate(self):
    try:
      super(AuthenticationForm, self).clean()
    except:
      # Expected to fail as login_as is nor provided by the parent Django AuthenticationForm, hence we redo it properly below.
      pass
    request = None
    self.user_cache = authenticate(request, username=self.cleaned_data.get('username'), password=self.cleaned_data.get('password'), login_as=self.cleaned_data.get('login_as'))
    return self.user_cache


class LdapAuthenticationForm(AuthenticationForm):
  """
  Adds NT_DOMAINS selector.
  """

  def __init__(self, *args, **kwargs):
    super(LdapAuthenticationForm, self).__init__(*args, **kwargs)
    self.fields['server'] = ChoiceField(choices=get_server_choices())
    self.error_messages['invalid_login'] = _t("Invalid username or password, or your LDAP groups not allowed")

  def authenticate(self):
    request = None
    username = self.cleaned_data.get('username') or ''
    password = self.cleaned_data.get('password')
    server = self.cleaned_data.get('server')

    if ('(' in username) or (')' in username) or ('*' in username):
      raise ValidationError(self.error_messages['invalid_login'])

    if username and password:
      try:
        self.user_cache = authenticate(request, username=username,
                                       password=password,
                                       server=server)
      except Exception as e:
        # If bind password incorrect will cause exception when sync group in login, suggest admin to test LDAP connection
        LOG.error("LDAP auth error: %s" % e)
        raise ValidationError(_("Please contact your administrator for LDAP connection setup."))

      if self.user_cache is None:
        from useradmin.ldap_access import get_connection as get_ldap_connection
        try:
          server_key = ''
          if conf.LDAP.LDAP_SERVERS.get():
            if server in conf.LDAP.LDAP_SERVERS.get():
              server_key = server
              ldap_config = conf.LDAP.LDAP_SERVERS.get()[server]
              get_ldap_connection(ldap_config)
          else:
            get_ldap_connection(conf.LDAP)
        except Exception as e:
          LOG.error("LDAP Exception: %s" % smart_str(e))
          raise ValidationError(smart_str(_("LDAP server %s Error: %s")) % (server_key, str(e)))

        raise ValidationError(
          self.error_messages['invalid_login'])
      elif not self.user_cache.is_active:
        raise ValidationError(self.error_messages['inactive'])
    return self.cleaned_data


class UserCreationForm(AuthUserCreationForm):
  """
  Accepts one password field and populates the others.
  password fields with the value of that password field
  Adds appropriate classes to authentication form.
  """
  password = CharField(label=_t("Password"),
                       widget=PasswordInput(attrs={'class': 'input-large'}),
                       validators=hue_get_password_validators())

  def __init__(self, data=None, *args, **kwargs):
    if data and 'password' in data:
      data = data.copy()
      data['password1'] = data['password']
      data['password2'] = data['password']
    super(UserCreationForm, self).__init__(data=data, *args, **kwargs)


class LdapUserCreationForm(UserCreationForm):
  def __init__(self, *args, **kwargs):
    super(LdapUserCreationForm, self).__init__(*args, **kwargs)
    self.fields['server'] = ChoiceField(choices=get_server_choices())
