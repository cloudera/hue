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

try:
    from django.conf.urls import patterns, handler500, url
# Fallback for Django versions < 1.4
except ImportError:
    from django.conf.urls.defaults import patterns, handler500, url

urlpatterns = patterns(
    'djangosaml2.views',
    url(r'^login/$', 'login', name='saml2_login'),
    url(r'^acs/$', 'assertion_consumer_service', name='saml2_acs'),
    url(r'^logout/$', 'logout', name='saml2_logout'),
    url(r'^ls/$', 'logout_service', name='saml2_ls'),
    url(r'^ls/post/$', 'logout_service_post', name='saml2_ls_post'),
    url(r'^metadata/$', 'metadata', name='saml2_metadata'),
)

handler500 = handler500
