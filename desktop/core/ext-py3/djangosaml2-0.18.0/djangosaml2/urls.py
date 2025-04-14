# Copyright (C) 2010-2012 Yaco Sistemas (http://www.yaco.es)
# Copyright (C) 2009 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login, name='saml2_login'),
    path('acs/', views.assertion_consumer_service, name='saml2_acs'),
    path('logout/', views.logout, name='saml2_logout'),
    path('ls/', views.logout_service, name='saml2_ls'),
    path('ls/post/', views.logout_service_post, name='saml2_ls_post'),
    path('metadata/', views.metadata, name='saml2_metadata'),
]
