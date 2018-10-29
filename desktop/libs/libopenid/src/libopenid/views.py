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

from django_openid_auth.views import login_begin as django_login_begin, login_complete

from desktop.lib.django_util import render
from django.core import urlresolvers
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

import libopenid.conf
from libopenid.backend import OpenIDBackend
from libopenid.forms import OpenIDLoginFormExt


__all__ = ['login_begin', 'login_complete']


def login_begin(request):
  redirect_to = request.GET.get('next', '/')
  is_first_login_ever = OpenIDBackend.is_first_login_ever()

  request.session.set_test_cookie()

  openid_url = getattr(settings, 'OPENID_SSO_SERVER_URL', None)
  identity_url_prefix = getattr(settings, 'OPENID_IDENTITY_URL_PREFIX', None)

  #Case of centralized server endpoint Get request
  if openid_url is not None:
     if request.method == 'GET':
       return render_to_response('openid-login.html', {
          'action': urlresolvers.reverse('openid-login'),
          'next': redirect_to,
          'first_login_ever': is_first_login_ever,
          'hide_field': True
       }, context_instance=RequestContext(request))

  return django_login_begin(request, template_name='openid-login.html', form_class = OpenIDLoginFormExt)


setattr(login_begin, 'login_notrequired', True)
setattr(login_complete, 'login_notrequired', True)
