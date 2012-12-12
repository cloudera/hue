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

import logging

import django.contrib.auth.views
from django.core import urlresolvers
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth import login, get_backends
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from hadoop.fs.exceptions import WebHdfsException
from useradmin.views import ensure_home_directory

from desktop.auth.backend import AllowFirstUserDjangoBackend
from desktop.auth.forms import UserCreationForm, AuthenticationForm
from desktop.lib.django_util import render
from desktop.lib.django_util import login_notrequired
from desktop.log.access import access_warn, last_access_map

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
    if isinstance(backend, AllowFirstUserDjangoBackend) and backend.is_first_login_ever():
      return True
  return False


@login_notrequired
def dt_login(request):
  """Used by the non-jframe login"""
  redirect_to = request.REQUEST.get('next', '/')
  is_first_login_ever = first_login_ever()

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

        if is_first_login_ever:
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

  request.session.set_test_cookie()
  return render('login.mako', request, {
    'action': urlresolvers.reverse('desktop.auth.views.dt_login'),
    'form': first_user_form or auth_form,
    'next': redirect_to,
    'first_login_ever': is_first_login_ever,
    'login_errors': request.method == 'POST',
  })


def dt_logout(request, next_page=None):
  """Log out the user"""
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
