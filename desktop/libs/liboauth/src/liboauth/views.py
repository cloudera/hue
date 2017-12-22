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
 
import logging
import urllib
import httplib2

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

from desktop.auth.backend import AllowFirstUserDjangoBackend
from desktop.auth.forms import UserCreationForm, AuthenticationForm
from desktop.lib.django_util import render
from desktop.lib.django_util import login_notrequired
from desktop.log.access import access_warn, last_access_map

import liboauth.conf
from liboauth.backend import OAuthBackend


@login_notrequired
def show_login_page(request, login_errors=False):
   """Used by the non-jframe login"""
   redirect_to = request.GET.get('next', '/')
   is_first_login_ever = OAuthBackend.is_first_login_ever()

   request.session.set_test_cookie()
   return render('oauth-login.mako', request, {
     'action': urlresolvers.reverse('oauth_login'),
     'next': redirect_to,
     'first_login_ever': is_first_login_ever,
     'login_errors': request.method == 'POST' or login_errors,
     'socialGoogle':   liboauth.conf.CONSUMER_KEY_GOOGLE.get() != "" and liboauth.conf.CONSUMER_SECRET_GOOGLE.get() != "",
     'socialFacebook': liboauth.conf.CONSUMER_KEY_FACEBOOK.get() != "" and liboauth.conf.CONSUMER_SECRET_FACEBOOK.get() != "",
     'socialLinkedin': liboauth.conf.CONSUMER_KEY_LINKEDIN.get() != "" and liboauth.conf.CONSUMER_SECRET_LINKEDIN.get() != "",
     'socialTwitter':  liboauth.conf.CONSUMER_KEY_TWITTER.get() != "" and liboauth.conf.CONSUMER_SECRET_TWITTER.get() != ""
 })



@login_notrequired
def oauth_login(request):

  if 'social' not in request.GET:
      raise Exception(_("Invalid request: %s") % resp)
  else:
      url = OAuthBackend.handleLoginRequest(request)

  return HttpResponseRedirect(url)

  
@login_notrequired
def oauth_authenticated(request):
   
  access_token, next = OAuthBackend.handleAuthenticationRequest(request)
  if access_token == "":
      return show_login_page(request, True)
  user = authenticate(access_token = access_token)
  login(request, user)
  return HttpResponseRedirect(next)
