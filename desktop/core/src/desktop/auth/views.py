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
  pass

import cgi
import datetime
import logging
import urllib

import django.contrib.auth.views
from django.core import urlresolvers
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth import login, get_backends, authenticate
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from hadoop.fs.exceptions import WebHdfsException
from useradmin.views import ensure_home_directory

from desktop.auth import forms as auth_forms
from desktop.lib.django_util import render
from desktop.lib.django_util import login_notrequired
from desktop.log.access import access_warn, last_access_map
from desktop.conf import AUTH, LDAP, OAUTH, DEMO_ENABLED


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


def get_backend_name():
  return get_backends() and get_backends()[0].__class__.__name__


@login_notrequired
def dt_login(request):
  redirect_to = request.REQUEST.get('next', '/')
  is_first_login_ever = first_login_ever()
  backend_name = get_backend_name()
  is_active_directory = backend_name == 'LdapBackend' and ( bool(LDAP.NT_DOMAIN.get()) or bool(LDAP.LDAP_SERVERS.get()) )

  if is_active_directory:
    UserCreationForm = auth_forms.LdapUserCreationForm
    AuthenticationForm = auth_forms.LdapAuthenticationForm
  else:
    UserCreationForm = auth_forms.UserCreationForm
    AuthenticationForm = auth_forms.AuthenticationForm

  if request.method == 'POST':
    # For first login, need to validate user info!
    first_user_form = is_first_login_ever and UserCreationForm(data=request.POST) or None
    first_user = first_user_form and first_user_form.is_valid()

    if first_user or not is_first_login_ever:
      auth_form = AuthenticationForm(data=request.POST)

      if auth_form.is_valid():
        # Must login by using the AuthenticationForm.
        # It provides 'backends' on the User object.
        user = auth_form.get_user()
        login(request, user)
        if request.session.test_cookie_worked():
          request.session.delete_test_cookie()

        if is_first_login_ever or backend_name in ('AllowAllBackend', 'LdapBackend'):
          # Create home directory for first user.
          try:
            ensure_home_directory(request.fs, user.username)
          except (IOError, WebHdfsException), e:
            LOG.error(_('Could not create home directory.'), exc_info=e)
            request.error(_('Could not create home directory.'))

        access_warn(request, '"%s" login ok' % (user.username,))
        return HttpResponseRedirect(redirect_to)

      else:
        access_warn(request, 'Failed login for user "%s"' % (request.POST.get('username'),))

  else:
    first_user_form = None
    auth_form = AuthenticationForm()

  if DEMO_ENABLED.get() and not 'admin' in request.REQUEST:
    user = authenticate(username='', password='')
    login(request, user)
    ensure_home_directory(request.fs, user.username)
    return HttpResponseRedirect(redirect_to)

  request.session.set_test_cookie()
  return render('login.mako', request, {
    'action': urlresolvers.reverse('desktop.auth.views.dt_login'),
    'form': first_user_form or auth_form,
    'next': redirect_to,
    'first_login_ever': is_first_login_ever,
    'login_errors': request.method == 'POST',
    'backend_name': backend_name,
    'active_directory': is_active_directory
  })


def dt_logout(request, next_page=None):
  """Log out the user"""
  backends = get_backends()
  if backends:
    for backend in backends:
      if hasattr(backend, 'logout'):
        response = backend.logout(request, next_page)
        if response:
          return response

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

