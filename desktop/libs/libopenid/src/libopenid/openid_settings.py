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


import libopenid.conf
import logging

import django_openid_auth
import desktop.conf

from desktop.lib import security_util


__all__ = ['OPENID_CONFIG', 'OPENID_CREATE_USERS', 'OPENID_SSO_SERVER_URL', 'OPENID_USE_EMAIL_FOR_USERNAME', 'OPENID_IDENTITY_URL_PREFIX']


OPENID_CONFIG = {  
  # set to 1 to output debugging information
  'debug': 1,
}

# openid sso endpoint url
OPENID_SSO_SERVER_URL  = libopenid.conf.SERVER_ENDPOINT_URL.get();

OPENID_CREATE_USERS = libopenid.conf.CREATE_USERS_ON_LOGIN.get();

OPENID_USE_EMAIL_FOR_USERNAME = libopenid.conf.USE_EMAIL_FOR_USERNAME.get();

OPENID_IDENTITY_URL_PREFIX = libopenid.conf.IDENTITY_URL_PREFIX.get();
