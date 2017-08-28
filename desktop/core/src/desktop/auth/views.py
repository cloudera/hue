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


try:
  import oauth2 as oauth
except:
  oauth = None

import cgi
import logging
import urllib
from datetime import datetime

from axes.decorators import watch_login
import django.contrib.auth.views
from django.core import urlresolvers
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth import login, get_backends, authenticate
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from desktop.auth import forms as auth_forms
from desktop.lib.django_util import render
from desktop.lib.django_util import login_notrequired
from desktop.lib.django_util import JsonResponse
from desktop.log.access import access_warn, last_access_map
from desktop.conf import LDAP, OAUTH, DEMO_ENABLED

from hadoop.fs.exceptions import WebHdfsException
from useradmin.models import get_profile
from useradmin.views import ensure_home_directory, require_change_password


LOG = logging.getLogger(__name__)


def get_current_users():
  """Return dictionary of User objects and
  a dictionary of the user's IP address and last access time"""
  current_users = { }
  for session in Session.objects.all():
    try:
      uid = session.get_decoded().get(django.contrib.auth.SESSION_KEY)
    except SuspiciousOperation:
      # If secret_key changed, this resolution won't work.
      uid = None

    if uid is not None:
      try:
        userobj = User.objects.get(pk=uid)
        current_users[userobj] = last_access_map.get(userobj.username, { })
      except User.DoesNotExist:
        LOG.debug("User with id=%d does not exist" % uid)

  return current_users


def first_login_ever():
  backends = get_backends()
  for backend in backends:
    if hasattr(backend, 'is_first_login_ever') and backend.is_first_login_ever():
      return True
  return False


def get_backend_names():
  return get_backends and [backend.__class__.__name__ for backend in get_backends()]


@login_notrequired
@watch_login
def dt_login(request, from_modal=False):
  redirect_to = request.REQUEST.get('next', '/')
  is_first_login_ever = first_login_ever()
  backend_names = get_backend_names()
  is_active_directory = 'LdapBackend' in backend_names and ( bool(LDAP.NT_DOMAIN.get()) or bool(LDAP.LDAP_SERVERS.get()) )

  if is_active_directory:
    UserCreationForm = auth_forms.LdapUserCreationForm
    AuthenticationForm = auth_forms.LdapAuthenticationForm
  else:
    UserCreationForm = auth_forms.UserCreationForm
    AuthenticationForm = auth_forms.AuthenticationForm

  if request.method == 'POST':
    request.audit = {
      'operation': 'USER_LOGIN',
      'username': request.POST.get('username')
    }

    # For first login, need to validate user info!
    first_user_form = is_first_login_ever and UserCreationForm(data=request.POST) or None
    first_user = first_user_form and first_user_form.is_valid()

    if first_user or not is_first_login_ever:
      auth_form = AuthenticationForm(data=request.POST)

      if auth_form.is_valid():
        # Must login by using the AuthenticationForm.
        # It provides 'backends' on the User object.
        user = auth_form.get_user()
        userprofile = get_profile(user)

        login(request, user)

        if request.session.test_cookie_worked():
          request.session.delete_test_cookie()

        try:
          ensure_home_directory(request.fs, user)
        except (IOError, WebHdfsException), e:
          LOG.error('Could not create home directory at login for %s.' % user, exc_info=e)

        if require_change_password(userprofile):
          return HttpResponseRedirect(urlresolvers.reverse('useradmin.views.edit_user', kwargs={'username': user.username}))

        userprofile.first_login = False
        userprofile.last_activity = datetime.now()
        userprofile.save()

        msg = 'Successful login for user: %s' % user.username
        request.audit['operationText'] = msg
        access_warn(request, msg)
        if from_modal or request.REQUEST.get('fromModal', 'false') == 'true':
          return JsonResponse({'auth': True})
        else:
          return HttpResponseRedirect(redirect_to)
      else:
        request.audit['allowed'] = False
        msg = 'Failed login for user: %s' % request.POST.get('username')
        request.audit['operationText'] = msg
        access_warn(request, msg)
        if from_modal or request.REQUEST.get('fromModal', 'false') == 'true':
          return JsonResponse({'auth': False})

  else:
    first_user_form = None
    auth_form = AuthenticationForm()
    # SAML user is already authenticated in djangosaml2.views.login
    if 'SAML2Backend' in backend_names and request.user.is_authenticated():
      try:
        ensure_home_directory(request.fs, request.user)
      except (IOError, WebHdfsException), e:
        LOG.error('Could not create home directory for SAML user %s.' % request.user)

  if DEMO_ENABLED.get() and not 'admin' in request.REQUEST and request.user.username != 'hdfs':
    user = authenticate(username=request.user.username, password='HueRocks')
    login(request, user)
    ensure_home_directory(request.fs, user.username)
    return HttpResponseRedirect(redirect_to)

  if not from_modal:
    request.session.set_test_cookie()

  renderable_path = 'login.mako'
  if from_modal:
    renderable_path = 'login_modal.mako'

  return render(renderable_path, request, {
    'action': urlresolvers.reverse('desktop.auth.views.dt_login'),
    'form': first_user_form or auth_form,
    'next': redirect_to,
    'first_login_ever': is_first_login_ever,
    'login_errors': request.method == 'POST',
    'backend_names': backend_names,
    'active_directory': is_active_directory
  })


def dt_logout(request, next_page=None):
  """Log out the user"""
  username = request.user.get_username()
  request.audit = {
    'username': username,
    'operation': 'USER_LOGOUT',
    'operationText': 'Logged out user: %s' % username
  }
  backends = get_backends()
  if backends:
    for backend in backends:
      if hasattr(backend, 'logout'):
        try:
          response = backend.logout(request, next_page)
          if response:
            return response
        except Exception, e:
          LOG.warn('Potential error on logout for user: %s with exception: %s' % (username, e))

  if len(filter(lambda backend: hasattr(backend, 'logout'), backends)) == len(backends):
    LOG.warn("Failed to log out from all backends for user: %s" % (username))
  return django.contrib.auth.views.logout(request, next_page)


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
    email=user.email)


# OAuth is based on Twitter as example.

@login_notrequired
def oauth_login(request):
  assert oauth is not None

  consumer = oauth.Consumer(OAUTH.CONSUMER_KEY.get(), OAUTH.CONSUMER_SECRET.get())
  client = oauth.Client(consumer)
  resp, content = client.request(OAUTH.REQUEST_TOKEN_URL.get(), "POST", body=urllib.urlencode({
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

  redirect_to = request.REQUEST.get('next', '/')
  return HttpResponseRedirect(redirect_to)

