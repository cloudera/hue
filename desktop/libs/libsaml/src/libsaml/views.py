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

from djangosaml2.views import login, echo_attributes, metadata,\
                              assertion_consumer_service, logout_service

try:
  from djangosaml2.views import logout_service_post
except ImportError:
  # We are on an older version of djangosaml2
  logout_service_post = None

import libsaml.conf


__all__ = ['login', 'echo_attributes', 'assertion_consumer_service', 'metadata']


if logout_service_post is None:
  _assertion_consumer_service = assertion_consumer_service

  @require_POST
  @csrf_exempt
  def assertion_consumer_service(request, config_loader_path=None, attribute_mapping=None, create_unknown_user=None):
    username_source = libsaml.conf.USERNAME_SOURCE.get().lower()
    return _assertion_consumer_service(request, config_loader_path, attribute_mapping, create_unknown_user, username_source)


setattr(logout_service, 'login_notrequired', True)
setattr(login, 'login_notrequired', True)
setattr(echo_attributes, 'login_notrequired', True)
setattr(assertion_consumer_service, 'login_notrequired', True)
setattr(metadata, 'login_notrequired', True)

if logout_service_post is not None:
  setattr(logout_service_post, 'login_notrequired', True)
