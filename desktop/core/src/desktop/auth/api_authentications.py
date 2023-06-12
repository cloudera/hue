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
import requests
import jwt
import json
import sys

from cryptography.hazmat.primitives import serialization
from rest_framework import authentication, exceptions

from desktop.auth.backend import find_or_create_user, ensure_has_a_group, rewrite_user
from desktop.conf import ENABLE_ORGANIZATIONS, AUTH

from useradmin.models import User

LOG = logging.getLogger(__name__)


class JwtAuthentication(authentication.BaseAuthentication):

  def authenticate(self, request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    if not authorization_header:
      LOG.debug('JwtAuthentication: no authorization header from %s' % request.path)
      return None

    header, access_token = authorization_header.split(' ')

    if header != 'Bearer':
      LOG.debug('JwtAuthentication: no Bearer header from %s' % request.path)
      return None

    if not access_token:
      LOG.debug('JwtAuthentication: no Bearer value from %s' % request.path)
      return None

    LOG.debug('JwtAuthentication: got access token from %s: %s' % (request.path, access_token))

    try:
      public_key_pem = self._handle_public_key(access_token) if AUTH.JWT.VERIFY.get() else ''
    except Exception as e:
      LOG.error('JwtAuthentication: Error fetching public key %s' % str(e))
      raise exceptions.AuthenticationFailed(e)

    params = {
      'jwt': access_token,
      'key': public_key_pem,
      'issuer': AUTH.JWT.ISSUER.get(),
      'audience': AUTH.JWT.AUDIENCE.get(),
      'algorithms': ["RS256"],
      'options': {
        'verify_signature': AUTH.JWT.VERIFY.get()
      }
    }

    try:
      payload = jwt.decode(**params)
    except jwt.DecodeError:
      LOG.error('JwtAuthentication: Invalid token')
      raise exceptions.AuthenticationFailed('JwtAuthentication: Invalid token')
    except jwt.ExpiredSignatureError:
      LOG.error('JwtAuthentication: Token expired')
      raise exceptions.AuthenticationFailed('JwtAuthentication: Token expired')
    except jwt.InvalidIssuerError:
      LOG.error('JwtAuthentication: issuer not match')
      raise exceptions.AuthenticationFailed('JwtAuthentication: issuer not matching')
    except jwt.InvalidAudienceError:
      LOG.error('JwtAuthentication: audience not match or no audience')
      raise exceptions.AuthenticationFailed('JwtAuthentication: audience not matching or no audience')
    except Exception as e:
      LOG.error('JwtAuthentication: %s' % str(e))
      raise exceptions.AuthenticationFailed(e)


    if payload.get(AUTH.JWT.USERNAME_HEADER.get()) is None: 
      LOG.debug('JwtAuthentication: no username in token')
      return None

    LOG.debug('JwtAuthentication: got username %s' % (payload.get(AUTH.JWT.USERNAME_HEADER.get())))

    user = find_or_create_user(payload.get(AUTH.JWT.USERNAME_HEADER.get()), is_superuser=False)
    ensure_has_a_group(user)
    user = rewrite_user(user)

    # Persist the token (to reuse for communicating with external services as the user, e.g. Impala)
    if ENABLE_ORGANIZATIONS.get():
      user.token = access_token
    else:
      user.profile.update_data({'jwt_access_token': access_token})
      user.profile.save()

    return (user, None)

  def _handle_public_key(self, access_token):
    token_metadata = jwt.get_unverified_header(access_token)
    kid = token_metadata.get('kid')

    if AUTH.JWT.KEY_SERVER_URL.get():
      response = requests.get(AUTH.JWT.KEY_SERVER_URL.get(), verify=False)
      jwk = json.loads(response.content)

      if jwk.get('keys'):
        for key in jwk.get('keys'):
          if key.get('kid') and key.get('kid') == kid:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
            public_key_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                     format=serialization.PublicFormat.SubjectPublicKeyInfo)

            return public_key_pem


class DummyCustomAuthentication(authentication.BaseAuthentication):
  """
  Only for local development environment does not have an external authentication service
  """

  def authenticate(self, request):
    LOG.debug('DummyCustomAuthentication: %s' % request.path)
    user = find_or_create_user(username='hue', password='hue')
    ensure_has_a_group(user)
    user = rewrite_user(user)
    user.is_active = True

    return (user, None)
