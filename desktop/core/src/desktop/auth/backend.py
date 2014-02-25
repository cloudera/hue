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
Authentication backend classes for Desktop.

These classes should implement the interface described at:
  http://docs.djangoproject.com/en/1.0/topics/auth/#writing-an-authentication-backend

In addition, the User classes they return must support:
 - get_groups() (returns a list of strings)
 - get_home_directory() (returns None or a string)
 - has_hue_permission(action, app) -> boolean
Because Django's models are sometimes unfriendly, you'll want
User to remain a django.contrib.auth.models.User object.

In Desktop, only one authentication backend may be specified.
"""
from django.contrib.auth.models import User
import django.contrib.auth.backends
import logging
import desktop.conf
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from useradmin.models import get_profile, get_default_user_group, UserProfile
from useradmin.views import import_ldap_users
from useradmin import ldap_access

import pam
from django_auth_ldap.backend import LDAPBackend, ldap_settings
import ldap
from django_auth_ldap.config import LDAPSearch


LOG = logging.getLogger(__name__)

def load_augmentation_class():
  """
  Loads the user augmentation class.
  Similar in spirit to django.contrib.auth.load_backend
  """
  try:
    class_name = desktop.conf.AUTH.USER_AUGMENTOR.get()
    i = class_name.rfind('.')
    module, attr = class_name[:i], class_name[i+1:]
    mod = import_module(module)
    klass = getattr(mod, attr)
    LOG.info("Augmenting users with class: %s" % (klass,))
    return klass
  except:
    raise ImproperlyConfigured("Could not find user_augmentation_class: %s" % (class_name,))

_user_augmentation_class = None
def get_user_augmentation_class():
  global _user_augmentation_class

  if _user_augmentation_class is None:
    _user_augmentation_class = load_augmentation_class()
  return _user_augmentation_class

def rewrite_user(user):
  """
  Rewrites the user according to the augmentation class.
  We currently only re-write specific attributes,
  though this could be generalized.
  """
  augment = get_user_augmentation_class()(user)
  for attr in ("get_groups", "get_home_directory", "has_hue_permission"):
    setattr(user, attr, getattr(augment, attr))
  return user

class DefaultUserAugmentor(object):
  def __init__(self, parent):
    self._parent = parent

  def _get_profile(self):
    return get_profile(self._parent)

  def get_groups(self):
    return self._get_profile().get_groups()

  def get_home_directory(self):
    return self._get_profile().home_directory

  def has_hue_permission(self, action, app):
    return self._get_profile().has_hue_permission(action=action, app=app)

def find_or_create_user(username, password=None):
  try:
    user = User.objects.get(username=username)
    LOG.debug("Found user %s in the db" % username)
  except User.DoesNotExist:
    LOG.info("Materializing user %s in the database" % username)
    user = User(username=username)
    if password is None:
      user.set_unusable_password()
    else:
      user.set_password(password)
    user.is_superuser = True
    user.save()
  return user

class DesktopBackendBase(object):
  """
  Abstract base class for providing external authentication schemes.

  Extend this class and implement check_auth
  """
  def authenticate(self, username, password):
    if self.check_auth(username, password):
      user = find_or_create_user(username)
      user = rewrite_user(user)
      return user
    else:
      return None

  def get_user(self, user_id):
    try:
      user = User.objects.get(pk=user_id)
      user = rewrite_user(user)
      return user
    except User.DoesNotExist:
      return None

  def check_auth(self, username, password):
    """
    Implementors should return a boolean value which determines
    whether the given username and password pair is valid.
    """
    raise NotImplemented("Abstract class - must implement check_auth")


class AllowFirstUserDjangoBackend(django.contrib.auth.backends.ModelBackend):
  """
  Allows the first user in, but otherwise delegates to Django's
  ModelBackend.
  """
  def authenticate(self, username=None, password=None):
    user = super(AllowFirstUserDjangoBackend, self).authenticate(username, password)
    if user is not None:
      if user.is_active:
        user = rewrite_user(user)
        return user
      return None

    if self.is_first_login_ever():
      user = find_or_create_user(username, password)
      user = rewrite_user(user)

      default_group = get_default_user_group()
      if default_group is not None:
        user.groups.add(default_group)
        user.save()

      return user

    return None

  def get_user(self, user_id):
    user = super(AllowFirstUserDjangoBackend, self).get_user(user_id)
    user = rewrite_user(user)
    return user

  def is_first_login_ever(self):
    """ Return true if no one has ever logged in to Desktop yet. """
    return User.objects.count() == 0


class OAuthBackend(DesktopBackendBase):
  """
  Deprecated, use liboauth.backend.OAuthBackend instead

  Heavily based on Twitter Oauth: https://github.com/simplegeo/python-oauth2#logging-into-django-w-twitter
  Requires: python-oauth2 and httplib2

  build/env/bin/python setup.py install https://github.com/simplegeo/python-oauth2
  build/env/bin/pip install httplib2
  """

  def authenticate(self, access_token):
    username = access_token['screen_name']
    password = access_token['oauth_token_secret']

    # Could save oauth_token detail in the user profile here

    user = find_or_create_user(username, password)
    user.is_superuser = False
    user.save()

    default_group = get_default_user_group()
    if default_group is not None:
      user.groups.add(default_group)

    return user

  @classmethod
  def manages_passwords_externally(cls):
    return True


class AllowAllBackend(DesktopBackendBase):
  """
  Authentication backend that allows any user to login as long
  as they have a username. The users will be added to the 'default_user_group'.
  """
  def check_auth(self, username, password):
    user = find_or_create_user(username, None)
    user.is_superuser = False
    user.save()
    default_group = get_default_user_group()
    if default_group is not None:
      user.groups.add(default_group)

    return user

  @classmethod
  def manages_passwords_externally(cls):
    return True



class PamBackend(DesktopBackendBase):
  """
  Authentication backend that uses PAM to authenticate logins. The first user to
  login will become the superuser.
  """
  def check_auth(self, username, password):
    if pam.authenticate(username, password, desktop.conf.AUTH.PAM_SERVICE.get()):
      is_super = False
      if User.objects.count() == 0:
        is_super = True

      try:
        user = User.objects.get(username=username)
      except User.DoesNotExist:
        user = find_or_create_user(username, None)
        if user is not None and user.is_active:
          profile = get_profile(user)
          profile.creation_method = UserProfile.CreationMethod.EXTERNAL
          profile.save()
          user.is_superuser = is_super

          default_group = get_default_user_group()
          if default_group is not None:
            user.groups.add(default_group)

          user.save()

      user = rewrite_user(user)
      return user

    return None

  @classmethod
  def manages_passwords_externally(cls):
    return True


class LdapBackend(object):
  """
  Authentication backend that uses LDAP to authenticate logins.
  The first user to login will become the superuser.
  """
  def __init__(self):
    # Delegate to django_auth_ldap.LDAPBackend
    class _LDAPBackend(LDAPBackend):
      def get_or_create_user(self, username, ldap_user):
        username = desktop.conf.LDAP.FORCE_USERNAME_LOWERCASE.get() and username.lower() or username
        if desktop.conf.LDAP.IGNORE_USERNAME_CASE.get():
          try:
            return User.objects.get(username__iexact=username), False
          except User.DoesNotExist:
            return User.objects.get_or_create(username=username)
        else:
          return User.objects.get_or_create(username=username)

    self._backend = _LDAPBackend()

    ldap_settings.AUTH_LDAP_SERVER_URI = desktop.conf.LDAP.LDAP_URL.get()
    if ldap_settings.AUTH_LDAP_SERVER_URI is None:
      LOG.warn("Could not find LDAP URL required for authentication.")
      return None

    if desktop.conf.LDAP.SEARCH_BIND_AUTHENTICATION.get():
      # New Search/Bind Auth
      base_dn = desktop.conf.LDAP.BASE_DN.get()
      user_name_attr = desktop.conf.LDAP.USERS.USER_NAME_ATTR.get()
      user_filter = desktop.conf.LDAP.USERS.USER_FILTER.get()
      if not user_filter.startswith('('):
        user_filter = '(' + user_filter + ')'

      if desktop.conf.LDAP.BIND_DN.get():
        bind_dn = desktop.conf.LDAP.BIND_DN.get()
        ldap_settings.AUTH_LDAP_BIND_DN = bind_dn
        bind_password = desktop.conf.LDAP.BIND_PASSWORD.get()
        ldap_settings.AUTH_LDAP_BIND_PASSWORD = bind_password

      if user_filter is None:
        search_bind_results = LDAPSearch(base_dn,
            ldap.SCOPE_SUBTREE, "(" + user_name_attr + "=%(user)s)")

      else:
        search_bind_results = LDAPSearch(base_dn,
            ldap.SCOPE_SUBTREE, "(&(" + user_name_attr + "=%(user)s)" + user_filter + ")")

      ldap_settings.AUTH_LDAP_USER_SEARCH = search_bind_results
    else:
      nt_domain = desktop.conf.LDAP.NT_DOMAIN.get()
      if nt_domain is None:
        pattern = desktop.conf.LDAP.LDAP_USERNAME_PATTERN.get()
        pattern = pattern.replace('<username>', '%(user)s')
        ldap_settings.AUTH_LDAP_USER_DN_TEMPLATE = pattern
      else:
        # %(user)s is a special string that will get replaced during the authentication process
        ldap_settings.AUTH_LDAP_USER_DN_TEMPLATE = "%(user)s@" + nt_domain

    # Certificate-related config settings
    if desktop.conf.LDAP.LDAP_CERT.get():
      ldap_settings.AUTH_LDAP_START_TLS = desktop.conf.LDAP.USE_START_TLS.get()
      ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
      ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, desktop.conf.LDAP.LDAP_CERT.get())
    else:
      ldap_settings.AUTH_LDAP_START_TLS = False
      ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

  def authenticate(self, username=None, password=None):
    username_filter_kwargs = ldap_access.get_ldap_user_kwargs(username)

    # Do this check up here, because the auth call creates a django user upon first login per user
    is_super = False
    if not UserProfile.objects.filter(creation_method=str(UserProfile.CreationMethod.EXTERNAL)).exists():
      # If there are no LDAP users already in the system, the first one will
      # become a superuser
      is_super = True
    elif User.objects.filter(**username_filter_kwargs).exists():
      # If the user already exists, we shouldn't change its superuser
      # privileges. However, if there's a naming conflict with a non-external
      # user, we should do the safe thing and turn off superuser privs.
      existing_user = User.objects.get(**username_filter_kwargs)
      existing_profile = get_profile(existing_user)
      if existing_profile.creation_method == str(UserProfile.CreationMethod.EXTERNAL):
        is_super = User.objects.get(**username_filter_kwargs).is_superuser
    elif not desktop.conf.LDAP.CREATE_USERS_ON_LOGIN.get():
      return None

    try:
      user = self._backend.authenticate(username, password)
    except ImproperlyConfigured, detail:
      LOG.warn("LDAP was not properly configured: %s", detail)
      return None

    if user is not None and user.is_active:
      profile = get_profile(user)
      profile.creation_method = UserProfile.CreationMethod.EXTERNAL
      profile.save()
      user.is_superuser = is_super
      user = rewrite_user(user)

      default_group = get_default_user_group()
      if default_group is not None:
        user.groups.add(default_group)
        user.save()

      return user

    return None

  def get_user(self, user_id):
    user = self._backend.get_user(user_id)
    user = rewrite_user(user)
    return user

  @classmethod
  def manages_passwords_externally(cls):
    return True


class SpnegoDjangoBackend(django.contrib.auth.backends.ModelBackend):
  """
  A note about configuration:

  The HTTP/_HOST@REALM principal (where _HOST is the fully qualified domain
  name of the server running Hue) needs to be exported to a keytab file.
  The keytab file can either be located in /etc/krb5.keytab or you can set
  the KRB5_KTNAME environment variable to point to another location
  (e.g. /etc/hue/hue.keytab).
  """
  def authenticate(self, username=None):
    username = self.clean_username(username)
    is_super = False
    if User.objects.count() == 0:
      is_super = True

    try:
      user = User.objects.get(username=username)
    except User.DoesNotExist:
      user = find_or_create_user(username, None)
      if user is not None and user.is_active:
        profile = get_profile(user)
        profile.creation_method = UserProfile.CreationMethod.EXTERNAL
        profile.save()
        user.is_superuser = is_super

        default_group = get_default_user_group()
        if default_group is not None:
          user.groups.add(default_group)

        user.save()

    user = rewrite_user(user)
    return user

  def clean_username(self, username):
    if '@' in username:
      return username.split('@')[0]
    return username

  def get_user(self, user_id):
    user = super(SpnegoDjangoBackend, self).get_user(user_id)
    user = rewrite_user(user)
    return user



class RemoteUserDjangoBackend(django.contrib.auth.backends.RemoteUserBackend):
  """
  Delegates to Django's RemoteUserBackend and requires HueRemoteUserMiddleware
  """
  def authenticate(self, remote_user=None):
    username = self.clean_username(remote_user)
    username = desktop.conf.AUTH.FORCE_USERNAME_LOWERCASE.get() and username.lower() or username
    is_super = False
    if User.objects.count() == 0:
      is_super = True

    try:
      if desktop.conf.AUTH.IGNORE_USERNAME_CASE.get():
        user = User.objects.get(username__iexact=username)
      else:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
      user = find_or_create_user(username, None)
      if user is not None and user.is_active:
        profile = get_profile(user)
        profile.creation_method = UserProfile.CreationMethod.EXTERNAL
        profile.save()
        user.is_superuser = is_super

        default_group = get_default_user_group()
        if default_group is not None:
          user.groups.add(default_group)

        user.save()

    user = rewrite_user(user)
    return user

  def get_user(self, user_id):
    user = super(RemoteUserDjangoBackend, self).get_user(user_id)
    user = rewrite_user(user)
    return user

