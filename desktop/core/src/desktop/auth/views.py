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

from future import standard_library
standard_library.install_aliases()
try:
  import oauth2 as oauth
except:
  oauth = None

import cgi
import logging
import sys
from datetime import datetime

from axes.decorators import axes_dispatch
import django.contrib.auth.views
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth import login, get_backends, authenticate
from django.contrib.sessions.models import Session
from django.http import HttpResponseRedirect
from django.urls import reverse

from hadoop.fs.exceptions import WebHdfsException
from notebook.connectors.base import get_api
from useradmin.models import get_profile, UserProfile, User, Group
from useradmin.views import ensure_home_directory, require_change_password

from desktop.auth import forms as auth_forms
from desktop.auth.backend import OIDCBackend
from desktop.auth.forms import ImpersonationAuthenticationForm, OrganizationUserCreationForm, OrganizationAuthenticationForm
from desktop.conf import OAUTH, ENABLE_ORGANIZATIONS, SESSION
from desktop.lib import fsmanager
from desktop.lib.django_util import render, login_notrequired, JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.log.access import access_log, access_warn, last_access_map
from desktop.views import samlgroup_check, saml_login_headers
from desktop.settings import LOAD_BALANCER_COOKIE
from django.utils.encoding import smart_str


if sys.version_info[0] > 2:
  from urllib.parse import urlencode as urllib_urlencode
  from django.utils.translation import gettext as _
else:
  from urllib import urlencode as urllib_urlencode
  from django.utils.translation import ugettext as _


LOG = logging.getLogger()


def get_current_users():
  """Return dictionary of User objects and
  a dictionary of the user's IP address and last access time"""
  current_users = {}
  for session in Session.objects.all():
    try:
      uid = session.get_decoded().get(django.contrib.auth.SESSION_KEY)
    except SuspiciousOperation:
      # If secret_key changed, this resolution won't work.
      uid = None

    if uid is not None:
      try:
        userobj = User.objects.get(pk=uid)
        current_users[userobj] = last_access_map.get(userobj.username, {})
      except User.DoesNotExist:
        LOG.debug("User with id=%d does not exist" % uid)

  return current_users


def first_login_ever():
  backends = get_backends()
  for backend in backends:
    if hasattr(backend, 'is_first_login_ever') and backend.is_first_login_ever():
      return True
  return False


# We want unique method name to represent HUE-3 vs HUE-4 method call.
# This is required because of reverse('desktop.auth.views.dt_login') below which needs uniqueness to work correctly.
@login_notrequired
def dt_login_old(request, from_modal=False):
  return dt_login(request, from_modal)


@login_notrequired
@axes_dispatch
def dt_login(request, from_modal=False):
  if request.method == 'GET':
    redirect_to = request.GET.get('next', '/')
  else:
    redirect_to = request.POST.get('next', '/')
  is_first_login_ever = first_login_ever()
  backend_names = auth_forms.get_backend_names()
  is_active_directory = auth_forms.is_active_directory()
  is_ldap_option_selected = 'server' not in request.POST or request.POST.get('server') == 'LDAP' or \
      request.POST.get('server') in auth_forms.get_ldap_server_keys()

  if is_active_directory and is_ldap_option_selected:
    UserCreationForm = auth_forms.LdapUserCreationForm
    AuthenticationForm = auth_forms.LdapAuthenticationForm
  else:
    UserCreationForm = auth_forms.UserCreationForm
    if 'ImpersonationBackend' in backend_names:
      AuthenticationForm = ImpersonationAuthenticationForm
    else:
      AuthenticationForm = auth_forms.AuthenticationForm
    if ENABLE_ORGANIZATIONS.get():
      UserCreationForm = OrganizationUserCreationForm
      AuthenticationForm = OrganizationAuthenticationForm

  if request.method == 'POST':
    request.audit = {
      'operation': 'USER_LOGIN',
      'username': request.POST.get('username', request.POST.get('email'))
    }

    # For first login, need to validate user info!
    first_user_form = is_first_login_ever and UserCreationForm(data=request.POST) or None
    first_user = first_user_form and first_user_form.is_valid()

    if first_user or not is_first_login_ever:
      auth_form = AuthenticationForm(request=request, data=request.POST)

      if auth_form.is_valid():
        # Must login by using the AuthenticationForm. It provides 'backend' on the User object.
        user = auth_form.get_user()
        userprofile = get_profile(user)

        login(request, user)
        # If Test cookie exists , it should be deleted
        if request.session.test_cookie_worked():
          request.session.delete_test_cookie()
        if request.fs is None:
          request.fs = fsmanager.get_filesystem(request.fs_ref)
        try:
          ensure_home_directory(request.fs, user)
        except (IOError, WebHdfsException) as e:
          LOG.error('Could not create home directory at login for %s.' % user, exc_info=e)

        if require_change_password(userprofile):
          return HttpResponseRedirect('/hue' + reverse('useradmin:useradmin.views.edit_user', kwargs={'username': user.username}))

        userprofile.first_login = False
        userprofile.last_activity = datetime.now()
        if userprofile.creation_method == UserProfile.CreationMethod.EXTERNAL: # This is to fix a bug in Hue 4.3
          userprofile.creation_method = UserProfile.CreationMethod.EXTERNAL.name
        userprofile.update_data({'auth_backend': user.backend})
        try:
          userprofile.update_data({'X-Forwarded-For': request.META['HTTP_X_FORWARDED_FOR']})
        except KeyError as e:
          LOG.error('HTTP-X-FORWARDED-FOR header not found: %s' %smart_str(e))
        userprofile.save()

        msg = 'Successful login for user: %s' % user.username
        request.audit['operationText'] = msg
        access_warn(request, msg)
        if from_modal or request.GET.get('fromModal', 'false') == 'true':
          return JsonResponse({'auth': True})
        else:
          return HttpResponseRedirect(redirect_to)
      else:
        request.audit['allowed'] = False
        msg = 'Failed login for user: %s' % request.POST.get('username', request.POST.get('email'))
        request.audit['operationText'] = msg
        access_warn(request, msg)
        if from_modal or request.GET.get('fromModal', 'false') == 'true':
          return JsonResponse({'auth': False})
  else:
    first_user_form = None
    auth_form = AuthenticationForm()
    # SAML/OIDC user is already authenticated in djangosaml2.views.login
    if hasattr(request, 'fs') and (
        'KnoxSpnegoDjangoBackend' in backend_names or 'SpnegoDjangoBackend' in backend_names or 'OIDCBackend' in backend_names or
        'SAML2Backend' in backend_names
      ) and request.user.is_authenticated:
      if request.fs is None:
        request.fs = fsmanager.get_filesystem(request.fs_ref)
      try:
        ensure_home_directory(request.fs, request.user)
      except (IOError, WebHdfsException) as e:
        LOG.error('Could not create home directory for %s user %s.' % ('OIDC' if 'OIDCBackend' in backend_names else 'SAML', request.user))
    if request.user.is_authenticated and not from_modal:
      return HttpResponseRedirect(redirect_to)

  if is_active_directory and not is_ldap_option_selected and \
      request.method == 'POST' and request.user.username != request.POST.get('username'):
    # local user login failed, give the right auth_form with 'server' field
    auth_form = auth_forms.LdapAuthenticationForm()
  
  if not from_modal and SESSION.ENABLE_TEST_COOKIE.get():
    request.session.set_test_cookie()

  if 'SAML2Backend' in backend_names:
    request.session['samlgroup_permitted_flag'] = samlgroup_check(request)
    saml_login_headers(request)

  renderable_path = 'login.mako'
  if from_modal:
    renderable_path = 'login_modal.mako'

  response = render(renderable_path, request, {
    'action': reverse('desktop_auth_views_dt_login'),
    'form': first_user_form or auth_form,
    'next': redirect_to,
    'first_login_ever': is_first_login_ever,
    'login_errors': request.method == 'POST',
    'backend_names': backend_names,
    'active_directory': is_active_directory,
    'user': request.user
  })

  if not request.user.is_authenticated:
    response.delete_cookie(LOAD_BALANCER_COOKIE) # Note: might be re-balanced to another Hue on login.

  return response


def dt_logout(request, next_page=None):
  """Log out the user"""
  username = request.user.get_username()
  request.audit = {
    'username': username,
    'operation': 'USER_LOGOUT',
    'operationText': 'Logged out user: %s' % username
  }

  # Close Impala session on logout
  session_app = "impala"
  if request.user.has_hue_permission(action='access', app=session_app):
    session = {"type": session_app, "sourceMethod": " dt_logout"}
    try:
      get_api(request, session).close_session(session)
    except PopupException as e:
      LOG.warning("Error closing %s session: %s" % (session_app, e.message.encode('utf-8')))
    except Exception as e:
      LOG.warning("Error closing %s session: %s" % (session_app, e))

  backends = get_backends()
  if backends:
    for backend in backends:
      if hasattr(backend, 'logout'):
        try:
          response = backend.logout(request, next_page)
          if response:
            return response
        except Exception as e:
          LOG.warning('Potential error on logout for user: %s with exception: %s' % (username, e))

  if len([backend for backend in backends if hasattr(backend, 'logout')]) == len(backends):
    LOG.warning("Failed to log out from all backends for user: %s" % (username))

  response = django.contrib.auth.views.LogoutView.as_view(next_page=next_page)(request)
  response.delete_cookie(LOAD_BALANCER_COOKIE)
  return response


def profile(request):
  """
  Dumps JSON for user-profile information.
  """
  return render(None, request, _profile_dict(request.user))

def _profile_dict(user):
  return dict(
    username=user.username,
    first_name=user.first_name,
    last_name=user.last_name,
    last_login=str(user.last_login), # datetime object needs to be converted
    email=user.email
  )


# OAuth is based on Twitter as example.

@login_notrequired
def oauth_login(request):
  assert oauth is not None

  consumer = oauth.Consumer(OAUTH.CONSUMER_KEY.get(), OAUTH.CONSUMER_SECRET.get())
  client = oauth.Client(consumer)
  resp, content = client.request(
      OAUTH.REQUEST_TOKEN_URL.get(), "POST", body=urllib_urlencode({
      'oauth_callback': 'http://' + request.get_host() + '/login/oauth_authenticated/'
  }))

  if resp['status'] != '200':
    raise Exception(_("Invalid response from OAuth provider: %s") % resp)

  request.session['request_token'] = dict(cgi.parse_qsl(content))

  url = "%s?oauth_token=%s" % (OAUTH.AUTHENTICATE_URL.get(), request.session['request_token']['oauth_token'])

  return HttpResponseRedirect(url)


@login_notrequired
def oauth_authenticated(request):
  consumer = oauth.Consumer(OAUTH.CONSUMER_KEY.get(), OAUTH.CONSUMER_SECRET.get())
  token = oauth.Token(request.session['request_token']['oauth_token'], request.session['request_token']['oauth_token_secret'])
  client = oauth.Client(consumer, token)

  resp, content = client.request(OAUTH.ACCESS_TOKEN_URL.get(), "GET")
  if resp['status'] != '200':
    raise Exception(_("Invalid response from OAuth provider: %s") % resp)

  access_token = dict(cgi.parse_qsl(content))

  user = authenticate(access_token=access_token)
  login(request, user)

  redirect_to = request.GET.get('next', '/')
  return HttpResponseRedirect(redirect_to)


@login_notrequired
def oidc_failed(request):
  if request.user.is_authenticated:
    return HttpResponseRedirect('/')
  access_warn(request, "401 Unauthorized by oidc")
  return render("oidc_failed.mako", request, dict(uri=request.build_absolute_uri()), status=401)
