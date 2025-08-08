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

from django.urls import re_path

LOG = logging.getLogger()

try:
  from libsaml.views import AssertionConsumerServiceView, EchoAttributesView, LoginView, LogoutView, MetadataView

  urlpatterns = [
    re_path(r'^logout/$', LogoutView.as_view(), name='saml2_logout'),
    re_path(r'^ls/$', LogoutView.as_view(), name='saml2_ls'),
    re_path(r'^acs/$', AssertionConsumerServiceView.as_view(), name='saml2_acs'),
    re_path(r'^login/$', LoginView.as_view(), name='saml2_login'),
    re_path(r'^metadata/$', MetadataView.as_view(), name='saml2_metadata'),
    re_path(r'^test/$', EchoAttributesView.as_view())
  ]

  try:
    from libsaml.views import LogoutServicePostView

    urlpatterns += [
      re_path(r'^ls/post/$', LogoutServicePostView.as_view(), name='saml2_ls_post')
    ]
  except ImportError:
    # We are on an older version of djangosaml2
    pass
except ImportError:
  LOG.warning('djangosaml2 module not found')
