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


# Create custom view classes with login_notrequired = True for djangosaml2 1.9.3 compatibility
class LoginViewNoLoginRequired(LoginView):
  @csrf_exempt
  def dispatch(self, request, *args, **kwargs):
    return super().dispatch(request, *args, **kwargs)


class EchoAttributesViewNoLoginRequired(EchoAttributesView):
  @csrf_exempt
  def dispatch(self, request, *args, **kwargs):
    return super().dispatch(request, *args, **kwargs)


class MetadataViewNoLoginRequired(MetadataView):
  @csrf_exempt
  def dispatch(self, request, *args, **kwargs):
    return super().dispatch(request, *args, **kwargs)


class LogoutViewNoLoginRequired(LogoutView):
  @csrf_exempt
  def dispatch(self, request, *args, **kwargs):
    return super().dispatch(request, *args, **kwargs)


# Customize AssertionConsumerServiceView
class CustomAssertionConsumerServiceView(AssertionConsumerServiceView):
  @csrf_exempt
  def dispatch(self, request, *args, **kwargs):
    username_source = libsaml.conf.USERNAME_SOURCE.get().lower()
    return super().dispatch(request, *args, **kwargs)


# Set login_notrequired on dispatch methods so Django's as_view() copies it to the wrapper function
LoginViewNoLoginRequired.dispatch.login_notrequired = True
EchoAttributesViewNoLoginRequired.dispatch.login_notrequired = True
MetadataViewNoLoginRequired.dispatch.login_notrequired = True
LogoutViewNoLoginRequired.dispatch.login_notrequired = True
CustomAssertionConsumerServiceView.dispatch.login_notrequired = True


# Create LogoutServicePostView subclass if available
if LogoutServicePostView is not None:
  class LogoutServicePostViewNoLoginRequired(LogoutServicePostView):
    def dispatch(self, request, *args, **kwargs):
      return super().dispatch(request, *args, **kwargs)
  
  # Set login_notrequired on dispatch method
  LogoutServicePostViewNoLoginRequired.dispatch.login_notrequired = True
else:
  LogoutServicePostViewNoLoginRequired = None


# Expose the views with backward compatibility
login = LoginViewNoLoginRequired
echo_attributes = EchoAttributesViewNoLoginRequired
metadata = MetadataViewNoLoginRequired
assertion_consumer_service = CustomAssertionConsumerServiceView
logout_service = LogoutViewNoLoginRequired
logout_service_post = LogoutServicePostViewNoLoginRequired

# For direct class access in URLs
LoginView = LoginViewNoLoginRequired
EchoAttributesView = EchoAttributesViewNoLoginRequired
MetadataView = MetadataViewNoLoginRequired
LogoutView = LogoutViewNoLoginRequired
LogoutServicePostView = LogoutServicePostViewNoLoginRequired

__all__ = ['login', 'echo_attributes', 'assertion_consumer_service', 'metadata', 'logout_service', 'logout_service_post',
           'LoginView', 'EchoAttributesView', 'MetadataView', 'LogoutView', 'CustomAssertionConsumerServiceView', 'LogoutServicePostView']
