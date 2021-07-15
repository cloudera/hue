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

from rest_framework import authentication
from rest_framework import exceptions

from useradmin.models import User

LOG = logging.getLogger(__name__)


class JwtAuthentication(authentication.BaseAuthentication):

  def authenticate(self, request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')
    if not authorization_header:
      LOG.debug('JwtAuthentication: no authorization header')
      return None

    bearer = authorization_header[len('Bearer '):]
    if not bearer:
      LOG.debug('JwtAuthentication: no Bearer value')
      return None

    LOG.debug('JwtAuthentication: got token %s' % bearer)

    # Decode token via jwt module
    # check expiration, get userId, handle errors

    # token = '...'

    # cf. below similar to backend.py
    # user = find_or_create_user(
    #   username,
    #   password,
    #   is_superuser=False
    # )
    user = User.objects.get(username='test')

    # ensure_has_a_group(user)
    # user = rewrite_user(user)

    # We should persist the token (to reuse for communicating with external services as the user, e.g. Impala)
    # either via a new DB field (might just be cleaner, even if requires a DB migration) or in the json blob.
    # if ENABLE_ORGANIZATIONS.get():
    #   user.token = token
    # else:
    #   user.profile.update_data({'token': token})
    #   user.profile.save()

    return (user, None)
