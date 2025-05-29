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
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from djangosaml2.views import AssertionConsumerServiceView, EchoAttributesView, LoginView, LogoutView, MetadataView

try:
  from djangosaml2.views import LogoutServicePostView
except ImportError:
  # We are on an older version of djangosaml2
  LogoutServicePostView = None

import libsaml.conf


# Customize AssertionConsumerServiceView
class CustomAssertionConsumerServiceView(AssertionConsumerServiceView):
  def dispatch(self, request, *args, **kwargs):
    username_source = libsaml.conf.USERNAME_SOURCE.get().lower()
    return super().dispatch(request, *args, **kwargs)

# Expose the views


login = LoginView
echo_attributes = EchoAttributesView
metadata = MetadataView
assertion_consumer_service = CustomAssertionConsumerServiceView
logout_service = LogoutView
logout_service_post = LogoutServicePostView

__all__ = ['login', 'echo_attributes', 'assertion_consumer_service', 'metadata', 'logout_service', 'logout_service_post']

# Set login_notrequired attribute
for view in [LogoutView, LoginView, EchoAttributesView, AssertionConsumerServiceView, MetadataView]:
  setattr(view, 'login_notrequired', True)

if LogoutServicePostView is not None:
  setattr(LogoutServicePostView, 'login_notrequired', True)
