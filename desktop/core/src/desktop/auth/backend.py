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
"""

from builtins import object
from importlib import import_module

import logging
LOG = logging.getLogger(__name__)

try:
  import ldap
except ImportError:
  LOG.warn('ldap module not found')
try:
  import pam
except ImportError:
  LOG.warn('pam module not found')
import requests

import django.contrib.auth.backends
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpResponseRedirect
from django.forms import ValidationError
from django.urls import reverse

try:
  from django_auth_ldap.backend import LDAPBackend
  from django_auth_ldap.config import LDAPSearch
except ImportError:
  LOG.warn('django_auth_ldap module not found')
  class LDAPSearch: pass
  class LDAPSearch: pass
from liboauth.metrics import oauth_authentication_time
try:
  from mozilla_django_oidc.auth import OIDCAuthenticationBackend, default_username_algo
  from mozilla_django_oidc.utils import absolutify, import_from_settings
except ImportError:
  LOG.warn('mozilla_django_oidc module not found')
  class OIDCAuthenticationBackend: pass

from desktop import metrics
from desktop.conf import AUTH, LDAP, OIDC, ENABLE_ORGANIZATIONS
from desktop.settings import LOAD_BALANCER_COOKIE

from filebrowser.conf import REMOTE_STORAGE_HOME
from useradmin import ldap_access
from useradmin.models import get_profile, get_default_user_group, UserProfile, User
from useradmin.organization import get_organization


# TODO: slowly move those utils to the useradmin module

def load_augmentation_class():
  """
  Loads the user augmentation class.
  Similar in spirit to django.contrib.auth.load_backend
  """
  try:
    class_name = AUTH.USER_AUGMENTOR.get()
    i = class_name.rfind('.')
    module, attr = class_name[:i], class_name[i + 1:]
    mod = import_module(module)
    klass = getattr(mod, attr)
    LOG.info("Augmenting users with class: %s" % (klass,))
    return klass
  except:
    LOG.exception('failed to augment class')
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
  We currently only re-write specific attributes, though this could be generalized.
  """
  if user is None:
    LOG.warn('Failed to rewrite user, user is None.')
  else:
    augment = get_user_augmentation_class()(user)
    for attr in ('get_groups', 'get_home_directory', 'has_hue_permission', 'get_permissions'):
      setattr(user, attr, getattr(augment, attr))

    setattr(user, 'profile', get_profile(user))
    setattr(user, 'auth_backend', user.profile.data.get('auth_backend'))
  return user


def is_admin(user):
  """
  Admin of the Organization. Typically can edit users, connectors...
  To rename to is_org_admin at some point.

  If ENABLE_ORGANIZATIONS is false:
    - Hue superusers are automatically also admin

  If ENABLE_ORGANIZATIONS is true:
    - Hue superusers might not be admin of the organization
  """
  is_admin = False

  if hasattr(user, 'is_superuser') and not ENABLE_ORGANIZATIONS.get():
    is_admin = user.is_superuser

  if not is_admin and user.is_authenticated():
    try:
      user = rewrite_user(user)
      is_admin = user.is_admin if ENABLE_ORGANIZATIONS.get() else user.has_hue_permission(action="superuser", app="useradmin")
    except Exception:
      LOG.exception("Could not validate if %s is a superuser, assuming False." % user)

  return is_admin


def is_hue_admin(user):
  """
  Hue service super user. Can manage global settings of the services used by all the organization.

  Independent of ENABLE_ORGANIZATIONS.
  """
  return hasattr(user, 'is_superuser') and user.is_superuser


class DefaultUserAugmentor(object):
  def __init__(self, parent):
    self._parent = parent

  def _get_profile(self):
    return get_profile(self._parent)

  def get_groups(self):
    return self._get_profile().get_groups()

  def get_home_directory(self, force_home=False):
    return REMOTE_STORAGE_HOME.get() if hasattr(REMOTE_STORAGE_HOME, 'get') and REMOTE_STORAGE_HOME.get() and not force_home \
        else self._get_profile().home_directory

  def has_hue_permission(self, action, app):
    return self._get_profile().has_hue_permission(action=action, app=app)

  def get_permissions(self):
    return self._get_profile().get_permissions()


def find_user(username):
  lookup = {'email': username} if ENABLE_ORGANIZATIONS.get() else {'username': username}

  try:
    user = User.objects.get(**lookup)
    LOG.debug("Found user %s" % user)
  except User.DoesNotExist:
    user = None

  return user


def create_user(username, password, is_superuser=True):
  if ENABLE_ORGANIZATIONS.get():
    organization = get_organization(email=username)
    attrs = {'email': username, 'organization': organization}
  else:
    attrs = {'username': username}

  user = User(**attrs)

  if password is None:
    user.set_unusable_password()
  else:
    user.set_password(password)

  user.is_superuser = is_superuser

  if ENABLE_ORGANIZATIONS.get():
    user.is_admin = is_superuser or not organization.organizationuser_set.exists() or not organization.is_multi_user
    user.save()
    ensure_has_a_group(user)

  user.save()

  LOG.info("User %s was created." % username)

  return user

def find_or_create_user(username, password=None, is_superuser=True):
  user = find_user(username)
  if user is None:
    user = create_user(username, password, is_superuser)
  return user

def ensure_has_a_group(user):
  default_group = get_default_user_group(user=user)

  if not user.groups.exists() and default_group is not None:
    user.groups.add(default_group)
    user.save()

def force_username_case(username):
  if AUTH.FORCE_USERNAME_LOWERCASE.get():
    username = username.lower()
  elif AUTH.FORCE_USERNAME_UPPERCASE.get():
    username = username.upper()
  return username


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
  def authenticate(self, username=None, email=None, password=None):
    if email is not None:
      username = email
    username = force_username_case(username)
    request = None

    user = super(AllowFirstUserDjangoBackend, self).authenticate(request, username=username, password=password)

    if user is not None:
      if user.is_active:
        user = rewrite_user(user)
        return user
      return user

    if self.is_first_login_ever():
      user = find_or_create_user(username, password)
      user = rewrite_user(user)
      userprofile = get_profile(user)
      userprofile.first_login = False
      userprofile.save()

      ensure_has_a_group(user)

      return user

    return None

  def get_user(self, user_id):
    user = super(AllowFirstUserDjangoBackend, self).get_user(user_id)
    user = rewrite_user(user)
    return user

  def is_first_login_ever(self):
    """ Return true if no one has ever logged in."""
    return User.objects.count() == 0


class ImpersonationBackend(django.contrib.auth.backends.ModelBackend):
  """
  Authenticate with a proxy user username/password but then login as another user.
  Does not support a multiple backends setup.
  """
  def authenticate(self, username=None, password=None, login_as=None):
    if not login_as:
      return

    request = None
    authenticated = super(ImpersonationBackend, self).authenticate(request, username, password)

    if not authenticated:
      raise PermissionDenied()

    user = find_or_create_user(login_as, password=None, is_superuser=False)
    ensure_has_a_group(user)

    return rewrite_user(user)

  def get_user(self, user_id):
    user = super(ImpersonationBackend, self).get_user(user_id)
    user = rewrite_user(user)
    return user


class OAuthBackend(DesktopBackendBase):
  """
  Deprecated, use liboauth.backend.OAuthBackend instead

  Heavily based on Twitter Oauth: https://github.com/simplegeo/python-oauth2#logging-into-django-w-twitter
  Requires: python-oauth2 and httplib2

  build/env/bin/python setup.py install https://github.com/simplegeo/python-oauth2
  build/env/bin/pip install httplib2
  """

  @oauth_authentication_time
  def authenticate(self, access_token):
    username = access_token['screen_name']
    password = access_token['oauth_token_secret']

    # Could save oauth_token detail in the user profile here

    user = find_or_create_user(username, password)
    user.is_superuser = False
    user.save()

    ensure_has_a_group(user)

    return user

  @classmethod
  def manages_passwords_externally(cls):
    return True


class AllowAllBackend(DesktopBackendBase):
  """
  Authentication backend that allows any user to login as long
  as they have a username. The users will be added to the 'default_user_group'.

  We want to ensure that already created users (e.g., from other backends)
  retain their superuser status, and any new users are not super users by default.
  """
  def check_auth(self, username, password):
    user = find_user(username)
    if user is None:
      user = create_user(username, password)
      user.is_superuser = False
      user.save()

    ensure_has_a_group(user)

    return user

  @classmethod
  def manages_passwords_externally(cls):
    return True


class PamBackend(DesktopBackendBase):
  """
  Authentication backend that uses PAM to authenticate logins. The first user to
  login will become the superuser.
  """

  @metrics.pam_authentication_time
  def authenticate(self, request=None, username=None, password=None):
    username = force_username_case(username)

    if pam.authenticate(username, password, AUTH.PAM_SERVICE.get()):
      is_super = False
      if User.objects.count() == 0:
        is_super = True

      try:
        if AUTH.IGNORE_USERNAME_CASE.get():
          user = User.objects.get(username__iexact=username)
        else:
          user = User.objects.get(username=username)
      except User.DoesNotExist:
        user = find_or_create_user(username, None)
        if user is not None and user.is_active:
          profile = get_profile(user)
          profile.creation_method = UserProfile.CreationMethod.EXTERNAL.name
          profile.save()
          user.is_superuser = is_super

          ensure_has_a_group(user)

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
        username = force_username_case(username)

        try:
          #Avoid circular import from is_admin
          from useradmin.forms import validate_username
          validate_username(username)

          if LDAP.IGNORE_USERNAME_CASE.get():
            try:
              return User.objects.get(username__iexact=username), False
            except User.DoesNotExist:
              return User.objects.get_or_create(username=username)
          else:
            return User.objects.get_or_create(username=username)
        except ValidationError as e:
          LOG.exception("LDAP username is invalid: %s" % username)

    self._backend = _LDAPBackend()

  def add_ldap_config(self, ldap_config):
    ldap_url = ldap_config.LDAP_URL.get()
    if ldap_url is None:
      LOG.warn("Could not find LDAP URL required for authentication.")
      return None
    else:
      setattr(self._backend.settings, 'SERVER_URI', ldap_config.LDAP_URL.get())

    if ldap_url.lower().startswith('ldaps') and ldap_config.USE_START_TLS.get():
      LOG.warn("Cannot configure LDAP with SSL and enable STARTTLS.")

    if ldap_config.SEARCH_BIND_AUTHENTICATION.get():
      # New Search/Bind Auth
      base_dn = ldap_config.BASE_DN.get()
      user_name_attr = ldap_config.USERS.USER_NAME_ATTR.get()
      user_filter = ldap_config.USERS.USER_FILTER.get()
      if not user_filter.startswith('('):
        user_filter = '(' + user_filter + ')'

      if ldap_config.BIND_DN.get():
        bind_dn = ldap_config.BIND_DN.get()
        setattr(self._backend.settings, 'BIND_DN', bind_dn)

        bind_password = ldap_config.BIND_PASSWORD.get()
        if not bind_password:
          bind_password = ldap_config.BIND_PASSWORD_SCRIPT.get()
        setattr(self._backend.settings, 'BIND_PASSWORD', bind_password)

      if user_filter is None:
        search_bind_results = LDAPSearch(base_dn,
            ldap.SCOPE_SUBTREE, "(" + user_name_attr + "=%(user)s)")

      else:
        search_bind_results = LDAPSearch(base_dn,
            ldap.SCOPE_SUBTREE, "(&(" + user_name_attr + "=%(user)s)" + user_filter + ")")

      setattr(self._backend.settings, 'USER_SEARCH', search_bind_results)
    else:
      nt_domain = ldap_config.NT_DOMAIN.get()
      if nt_domain is None:
        pattern = ldap_config.LDAP_USERNAME_PATTERN.get()
        pattern = pattern.replace('<username>', '%(user)s')
        setattr(self._backend.settings, 'USER_DN_TEMPLATE', pattern)
      else:
        # %(user)s is a special string that will get replaced during the authentication process
        setattr(self._backend.settings, 'USER_DN_TEMPLATE', "%(user)s@" + nt_domain)

    # If Secure ldaps is specified in hue.ini then ldap code automatically use SSL/TLS communication
    if not ldap_url.lower().startswith('ldaps'):
      setattr(self._backend.settings, 'START_TLS', ldap_config.USE_START_TLS.get())

    # Certificate-related config settings
    if ldap_config.LDAP_CERT.get():
      ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)
      ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, ldap_config.LDAP_CERT.get())
    else:
      ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

    if ldap_config.FOLLOW_REFERRALS.get():
      ldap.set_option(ldap.OPT_REFERRALS, 1)
    else:
      ldap.set_option(ldap.OPT_REFERRALS, 0)

  def add_ldap_config_for_server(self, server):
    if LDAP.LDAP_SERVERS.get():
      # Choose from multiple server configs
      if server in LDAP.LDAP_SERVERS.get():
        self.add_ldap_config(LDAP.LDAP_SERVERS.get()[server])
    else:
      self.add_ldap_config(LDAP)

  @metrics.ldap_authentication_time
  def authenticate(self, request=None, username=None, password=None, server=None):
    self.add_ldap_config_for_server(server)

    username_filter_kwargs = ldap_access.get_ldap_user_kwargs(username)

    # Do this check up here, because the auth call creates a django user upon first login per user
    is_super = False
    if not UserProfile.objects.filter(creation_method=UserProfile.CreationMethod.EXTERNAL.name).exists():
      # If there are no LDAP users already in the system, the first one will
      # become a superuser
      is_super = True
    elif User.objects.filter(**username_filter_kwargs).exists():
      # If the user already exists, we shouldn't change its superuser
      # privileges. However, if there's a naming conflict with a non-external
      # user, we should do the safe thing and turn off superuser privs.
      existing_user = User.objects.get(**username_filter_kwargs)
      existing_profile = get_profile(existing_user)
      if existing_profile.creation_method == UserProfile.CreationMethod.EXTERNAL.name:
        is_super = User.objects.get(**username_filter_kwargs).is_superuser
    elif not LDAP.CREATE_USERS_ON_LOGIN.get():
      LOG.warn("Create users when they login with their LDAP credentials is turned off")
      return None

    try:
      allowed_group = self.check_ldap_access_groups(server, username)
      if allowed_group:
        user = self._backend.authenticate(username=username, password=password)
      else:
        LOG.warn("%s not in an allowed login group" % username)
        return None
    except ImproperlyConfigured as detail:
      LOG.warn("LDAP was not properly configured: %s", detail)
      return None

    if user is not None and user.is_active:
      profile = get_profile(user)
      profile.creation_method = UserProfile.CreationMethod.EXTERNAL.name
      profile.save()
      user.is_superuser = is_super
      user = rewrite_user(user)

      ensure_has_a_group(user)

      if LDAP.SYNC_GROUPS_ON_LOGIN.get():
        self.import_groups(server, user)

    return user

  def get_user(self, user_id):
    user = self._backend.get_user(user_id)
    user = rewrite_user(user)
    return user

  def check_ldap_access_groups(self, server, username):
    #Avoid circular import from is_admin
    from useradmin.views import get_find_groups_filter
    allowed_group = False

    if LDAP.LOGIN_GROUPS.get() and LDAP.LOGIN_GROUPS.get() != ['']:
      login_groups = LDAP.LOGIN_GROUPS.get()
      connection = ldap_access.get_connection_from_server(server)
      try:
        user_info = connection.find_users(username, find_by_dn=False)
      except Exception as e:
        LOG.warn("Failed to find LDAP user: %s" % e)

      if not user_info:
        LOG.warn("Could not get LDAP details for users with pattern %s" % username)
        return False

      ldap_info = user_info[0]
      group_ldap_info = connection.find_groups("*", group_filter=get_find_groups_filter(ldap_info, server))
      for group in group_ldap_info:
        if group['name'] in login_groups:
          return True

    else:
      #Login groups not set default to True
      allowed_group = True

    return allowed_group

  def import_groups(self, server, user):
    connection = ldap_access.get_connection_from_server(server)
    #Avoid circular import from is_admin
    from useradmin.views import import_ldap_users
    import_ldap_users(connection, user.username, sync_groups=True, import_by_dn=False, server=server)

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

  @metrics.spnego_authentication_time
  def authenticate(self, request=None, username=None):
    username = self.clean_username(username)
    username = force_username_case(username)
    is_super = False
    if User.objects.count() == 0:
      is_super = True

    try:
      if AUTH.IGNORE_USERNAME_CASE.get():
        user = User.objects.get(username__iexact=username)
      else:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
      user = find_or_create_user(username, None)
      if user is not None and user.is_active:
        profile = get_profile(user)
        profile.creation_method = UserProfile.CreationMethod.EXTERNAL.name
        profile.save()
        user.is_superuser = is_super

        ensure_has_a_group(user)

        user.save()

    if user is not None:
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


class KnoxSpnegoDjangoBackend(django.contrib.auth.backends.ModelBackend):
  """
  Knox Trusted proxy passes GET parameter doAs
  """

  @metrics.spnego_authentication_time
  def authenticate(self, request=None, username=None):
    username = self.clean_username(username, request)
    username = force_username_case(username)
    is_super = False
    if User.objects.count() == 0:
      is_super = True

    try:
      if AUTH.IGNORE_USERNAME_CASE.get():
        user = User.objects.get(username__iexact=username)
      else:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
      user = find_or_create_user(username, None)
      if user is not None and user.is_active:
        profile = get_profile(user)
        profile.creation_method = UserProfile.CreationMethod.EXTERNAL.name
        profile.save()
        user.is_superuser = is_super

        ensure_has_a_group(user)

        user.save()

    if user is not None:
      user = rewrite_user(user)

    return user

  def clean_username(self, username, request):
    # Grab doAs parameter here
    doas_user = request.GET.get("doAs", "")
    return doas_user

  def get_user(self, user_id):
    user = super(KnoxSpnegoDjangoBackend, self).get_user(user_id)
    user = rewrite_user(user)
    return user


class RemoteUserDjangoBackend(django.contrib.auth.backends.RemoteUserBackend):
  """
  Delegates to Django's RemoteUserBackend and requires HueRemoteUserMiddleware
  """
  def authenticate(self, remote_user=None):
    username = self.clean_username(remote_user)
    username = force_username_case(username)
    is_super = False
    if User.objects.count() == 0:
      is_super = True

    try:
      if AUTH.IGNORE_USERNAME_CASE.get():
        user = User.objects.get(username__iexact=username)
      else:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
      user = find_or_create_user(username, None)
      if user is not None and user.is_active:
        profile = get_profile(user)
        profile.creation_method = UserProfile.CreationMethod.EXTERNAL.name
        profile.save()
        user.is_superuser = is_super

        ensure_has_a_group(user)

        user.save()

    user = rewrite_user(user)
    return user

  def get_user(self, user_id):
    user = super(RemoteUserDjangoBackend, self).get_user(user_id)
    user = rewrite_user(user)
    return user


class OIDCBackend(OIDCAuthenticationBackend):
  def authenticate(self, **kwargs):
    self.request = kwargs.pop('request', None)
    if not self.request:
      return None

    state = self.request.GET.get('state')
    code = self.request.GET.get('code')
    nonce = kwargs.pop('nonce', None)

    if not code or not state:
      return None

    reverse_url = import_from_settings('OIDC_AUTHENTICATION_CALLBACK_URL', 'oidc_authentication_callback')

    token_payload = {
      'client_id': self.OIDC_RP_CLIENT_ID,
      'client_secret': self.OIDC_RP_CLIENT_SECRET,
      'grant_type': 'authorization_code',
      'code': code,
      'redirect_uri': absolutify(
        self.request,
        reverse(reverse_url)
      ),
    }

    # Get the token
    token_info = self.get_token(token_payload)
    id_token = token_info.get('id_token')
    access_token = token_info.get('access_token')
    refresh_token = token_info.get('refresh_token')

    # Validate the token
    verified_id = self.verify_token(id_token, nonce=nonce)

    if verified_id:
      self.save_refresh_tokens(refresh_token)
      user = self.get_or_create_user(access_token, id_token, verified_id)
      user = rewrite_user(user)
      return user

    return None

  def filter_users_by_claims(self, claims):
    username = claims.get(import_from_settings('OIDC_USERNAME_ATTRIBUTE', 'preferred_username'))
    if not username:
      return self.UserModel.objects.none()
    return self.UserModel.objects.filter(username__iexact=username)

  def save_refresh_tokens(self, refresh_token):
    session = self.request.session

    if import_from_settings('OIDC_STORE_REFRESH_TOKEN', False):
      session['oidc_refresh_token'] = refresh_token

  def create_user(self, claims):
    """Return object for a newly created user account."""
    # Overriding lib's logic, use preferred_username from oidc as username

    username = claims.get(import_from_settings('OIDC_USERNAME_ATTRIBUTE', 'preferred_username'), '')
    email = claims.get('email', '')
    first_name = claims.get('given_name', '')
    last_name = claims.get('family_name', '')

    if not username:
      if not email:
        LOG.debug("OpenID Connect no username and email while creating new user")
        return None
      username = default_username_algo(email)

    return self.UserModel.objects.create_user(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_superuser=self.is_hue_superuser(claims)
    )

  def get_or_create_user(self, access_token, id_token, verified_id):
    user = super(OIDCBackend, self).get_or_create_user(access_token, id_token, verified_id)
    if not user and not import_from_settings('OIDC_CREATE_USER', True):
      # in this case, user is login from Keycloak, but not allow create
      self.logout(self.request, next_page=import_from_settings('LOGIN_REDIRECT_URL_FAILURE', '/'))
    return user

  def get_user(self, user_id):
    user = super(OIDCBackend, self).get_user(user_id)
    user = rewrite_user(user)
    return user

  def update_user(self, user, claims):
    if user.is_superuser != self.is_hue_superuser(claims):
      user.is_superuser = self.is_hue_superuser(claims)
      user.save()
    return user

  def is_hue_superuser(self, claims):
    """
    To use this feature, setup in Keycloak:
      1. add the name of Hue superuser group to superuser_group in hue.ini
      2. in Keycloak, go to your_realm --> your_clients --> Mappers, add a mapper
           Mapper Type: Group Membership (this is predefined mapper type)
           Token Claim Name: group_membership (required exact string)
    """
    sueruser_group = '/' + OIDC.SUPERUSER_GROUP.get()
    if sueruser_group:
      return sueruser_group in claims.get('group_membership', [])
    return False

  def logout(self, request, next_page):
    # https://stackoverflow.com/questions/46689034/logout-user-via-keycloak-rest-api-doesnt-work
    if request.session.get('_auth_user_backend', '') != 'desktop.auth.backend.OIDCBackend':
      return None

    session = request.session
    access_token = session.get('oidc_access_token', '')
    refresh_token = session.get('oidc_refresh_token', '')

    if access_token and refresh_token:
      oidc_logout_url = OIDC.LOGOUT_REDIRECT_URL.get()
      client_id = import_from_settings('OIDC_RP_CLIENT_ID')
      client_secret = import_from_settings('OIDC_RP_CLIENT_SECRET')
      oidc_verify_ssl = import_from_settings('OIDC_VERIFY_SSL')
      form = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
      }
      headers = {
        'Authorization': 'Bearer {0}'.format(access_token),
        'Content-Type': 'application/x-www-form-urlencoded'
      }
      resp = requests.post(oidc_logout_url, data=form, headers=headers, verify=oidc_verify_ssl)
      if resp.status_code >= 200 and resp.status_code < 300:
        LOG.debug("OpenID Connect logout succeed!")
        delete_oidc_session_tokens(session)
        auth.logout(request)
        response = HttpResponseRedirect(next_page)
        response.delete_cookie(LOAD_BALANCER_COOKIE)
        return response
      else:
        LOG.error("OpenID Connect logout failed: %s" % resp.content)
    else:
      LOG.warn("OpenID Connect tokens are not available, logout skipped!")
    return None

  # def filter_users_by_claims(self, claims):

  # def verify_claims(self, claims):

def delete_oidc_session_tokens(session):
  if session:
    if 'oidc_access_token' in session:
      del session['oidc_access_token']
    if 'oidc_id_token' in session:
      del session['oidc_id_token']
    if 'oidc_id_token_expiration' in session:
      del session['oidc_id_token_expiration']
    if 'oidc_login_next' in session:
      del session['oidc_login_next']
    if 'oidc_refresh_token' in session:
      del session['oidc_refresh_token']
    if 'oidc_state' in session:
      del session['oidc_state']
