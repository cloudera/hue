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
from djangosaml2.views import AssertionConsumerServiceView, EchoAttributesView, LoginView, LogoutView, MetadataView

from desktop.lib.django_util import render

LoginView.dispatch.login_notrequired = True
EchoAttributesView.dispatch.login_notrequired = True
MetadataView.dispatch.login_notrequired = True
LogoutView.dispatch.login_notrequired = True
AssertionConsumerServiceView.dispatch.login_notrequired = True

try:
  from djangosaml2.views import LogoutServicePostView

  LogoutServicePostView.dispatch.login_notrequired = True
except ImportError:
  # We are on an older version of djangosaml2
  pass


def local_logout(request, next_page=None):
  """
  Local logout: clears Django session only, not the SAML session.
  Then presents a button to redirect to SAML login.
  """
  import libsaml.conf
  base_url = libsaml.conf.BASE_URL.get()
  logout_url = libsaml.conf.CDP_LOGOUT_URL.get()
  authenticate_url = logout_url.replace("logout", "authenticate")
  login_url = f"{authenticate_url}?loginRedirect={base_url}"

  return render('logged_out.mako', request, {
    'login_url': login_url,
  })


setattr(local_logout, 'login_notrequired', True)
