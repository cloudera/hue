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

from django.conf.urls import url
from liboauth import views as liboauth_views

urlpatterns = [
       url(r'^accounts/login/$', liboauth_views.show_login_page, name='show_oauth_login'),
       url(r'^social_login/oauth/?$', liboauth_views.oauth_login, name='oauth_login'),
       url(r'^social_login/oauth_authenticated/?$', liboauth_views.oauth_authenticated, name='oauth_authenticated'),
]
