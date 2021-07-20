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
import jwt

from rest_framework import authentication, exceptions

from desktop.auth.backend import find_or_create_user, ensure_has_a_group, rewrite_user
from desktop.conf import ENABLE_ORGANIZATIONS

from useradmin.models import User

LOG = logging.getLogger(__name__)


class JwtAuthentication(authentication.BaseAuthentication):

  def authenticate(self, request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    if not authorization_header:
      LOG.debug('JwtAuthentication: no authorization header')
      return None

    header, access_token = authorization_header.split(' ')

    if header != 'Bearer':
      LOG.debug('JwtAuthentication: no Bearer header')
      return None

    if not access_token:
      LOG.debug('JwtAuthentication: no Bearer value')
      return None

    LOG.debug('JwtAuthentication: got access token %s' % access_token)

    try:
      payload = jwt.decode(access_token, 'secret', algorithms=["HS256"])
    except jwt.DecodeError:
      raise exceptions.AuthenticationFailed('JwtAuthentication: Invalid token')
    except jwt.ExpiredSignatureError:
      raise exceptions.AuthenticationFailed('JwtAuthentication: Token expired')
    except Exception as e:
      raise exceptions.AuthenticationFailed(e)

    user = find_or_create_user(payload['userId'], is_superuser=False)
    ensure_has_a_group(user)
    user = rewrite_user(user)

    # Persist the token (to reuse for communicating with external services as the user, e.g. Impala)
    if ENABLE_ORGANIZATIONS.get():
      user.token = access_token
    else:
      user.profile.update_data({'jwt_access_token': access_token})
      user.profile.save()

    return (user, None)
