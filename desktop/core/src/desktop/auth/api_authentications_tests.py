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

import json
import sys

from nose.tools import assert_equal, assert_true, assert_false, assert_raises
from nose.plugins.skip import SkipTest

from desktop.auth.backend import rewrite_user
from desktop.auth.api_authentications import JwtAuthentication
from desktop.lib.django_test_util import make_logged_in_client
from desktop.conf import AUTH

from rest_framework import exceptions

from useradmin.models import User


if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock, MagicMock
else:
  from mock import patch, Mock, MagicMock


class TestJwtAuthentication():

  def setUp(self):
    self.client = make_logged_in_client(username="test_user", groupname="default", recreate=True, is_superuser=False)
    self.user = rewrite_user(User.objects.get(username="test_user"))

    self.sample_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6InJ0R1VlRjlickdVa3pTZUk1YUg2REpaa1hFQXJ3cHFNcWJTTlo0aTd3SGMifQ.e" \
                        "yJhdWQiOlsid29ya2xvYWQtYXBwIiwicmFuZ2VyIl0sImV4cCI6MTYyNjI1Njg5MywiaWF0IjoxNjI2MjU2NTkzLCJpc" \
                        "3MiOiJDbG91ZGVyYTEiLCJqdGkiOiJpZDEiLCJzdWIiOiJ0ZXN0X3VzZXIifQ.jvyVDxbWTAik0jbdUcIc9ZANNrJZUC" \
                        "WH-Pg7FloRhg0ZYAETd_AO3p5v_ppoMmVcPD2xBSrngA5J3_A_zPBvQ_hdDlpb0_-mCCJfGhC5tju4bI9EE9Akdn2Frr" \
                        "sqrvQQ8cPyGsIlvoIxrK1De4f74MmUaxfN7Hrrcue1PTY4u4IB9cWQqV9vIcX99Od5PUaNekLIee-I8gweqvfGEEsW7q" \
                        "WUM63nh59_TOB3LLq-YcEuaX1h_oiTATeCssjk_ee9RrJGLNyKmC0WJ4UrEWn8a_T3bwCy8CMe0zV5PSuuvPHy0FvnTo" \
                        "2il5SDjGimxKcbpgNiJdfblslu6i35DlfiWg"

    self.request = MagicMock(
      META={
        "HTTP_AUTHORIZATION": "Bearer " + self.sample_token
      }
    )


  def test_authenticate_existing_user(self):
    with patch('desktop.auth.api_authentications.jwt.decode') as jwt_decode:
      with patch('desktop.auth.api_authentications.requests.get'):
        jwt_decode.return_value = {
          "sub": "test_user"
        }
        resets = [
          AUTH.JWT.VERIFY.set_for_testing(False),
          AUTH.JWT.USERNAME_HEADER.set_for_testing('sub')
        ]

        try:
          user, token = JwtAuthentication().authenticate(request=self.request)

          assert_equal(user, self.user)
          assert_true(user.is_authenticated)
          assert_false(user.is_superuser)
        finally:
          for reset in resets:
            reset()


  def test_authenticate_new_user(self):
    with patch('desktop.auth.api_authentications.jwt.decode') as jwt_decode:
      with patch('desktop.auth.api_authentications.requests.get'):
        jwt_decode.return_value = {
          "sub": "test_new_user"
        }

        assert_false(User.objects.filter(username="test_new_user").exists())

        resets = [
          AUTH.JWT.VERIFY.set_for_testing(False),
          AUTH.JWT.USERNAME_HEADER.set_for_testing('sub')
        ]
        try:
          user, token = JwtAuthentication().authenticate(request=self.request)

          assert_true(User.objects.filter(username="test_new_user").exists())
          assert_equal(User.objects.get(username="test_new_user"), user)
          assert_true(user.is_authenticated)
          assert_false(user.is_superuser)
        finally:
          for reset in resets:
            reset()


  def test_failed_authentication(self):
    with patch('desktop.auth.api_authentications.jwt.decode') as jwt_decode:
      with patch('desktop.auth.api_authentications.requests.get'):
        with patch('desktop.auth.api_authentications.JwtAuthentication._handle_public_key'):

          # Invalid token
          jwt_decode.side_effect = exceptions.AuthenticationFailed('JwtAuthentication: Invalid token')
          assert_raises(exceptions.AuthenticationFailed, JwtAuthentication().authenticate, self.request)

          # Expired token
          jwt_decode.side_effect = exceptions.AuthenticationFailed('JwtAuthentication: Token expired')
          assert_raises(exceptions.AuthenticationFailed, JwtAuthentication().authenticate, self.request)


  def test_check_user_token_storage(self):
    with patch('desktop.auth.api_authentications.jwt.decode') as jwt_decode:
      with patch('desktop.auth.api_authentications.requests.get'):
        jwt_decode.return_value = {
          "sub": "test_user"
        }
        resets = [
          AUTH.JWT.VERIFY.set_for_testing(False),
          AUTH.JWT.USERNAME_HEADER.set_for_testing('sub')
        ]
        try:
          user, token = JwtAuthentication().authenticate(request=self.request)

          assert_true('jwt_access_token' in user.profile.data)
          assert_equal(user.profile.data['jwt_access_token'], self.sample_token)
        finally:
          for reset in resets:
            reset()


  def test_check_token_verification_flag(self):
    with patch('desktop.auth.api_authentications.requests.get'):
      with patch('desktop.auth.api_authentications.jwt.algorithms.RSAAlgorithm.from_jwk'):
        with patch('desktop.auth.api_authentications.JwtAuthentication._handle_public_key'):

          # When verification flag is True for old sample token
          resets = [
            AUTH.JWT.VERIFY.set_for_testing(True),
            AUTH.JWT.USERNAME_HEADER.set_for_testing('sub')
          ]
          try:
            assert_raises(exceptions.AuthenticationFailed, JwtAuthentication().authenticate, self.request)
          finally:
            for reset in resets:
              reset()

          # When verification flag is False
          resets = [
            AUTH.JWT.VERIFY.set_for_testing(False),
            AUTH.JWT.USERNAME_HEADER.set_for_testing('sub')
          ]
          try:
            user, token = JwtAuthentication().authenticate(request=self.request)

            assert_equal(user, self.user)
          finally:
            for reset in resets:
              reset()


  def test_handle_public_key(self):
    with patch('desktop.auth.api_authentications.requests.get') as key_server_request:
      with patch('desktop.auth.api_authentications.jwt.decode') as jwt_decode:

        jwt_decode.return_value = {
          "sub": "test_user"
        }
        jwk = {
          "keys": [
            {
              "kty": "RSA",
              "e": "AQAB",
              "use": "sig",
              "kid": "rtGUeF9brGUkzSeI5aH6DJZkXEArwpqMqbSNZ4i7wHc",
              "alg": "RS256",
              "n": "we9gTbRxHl4Ye9mY9abYl_WHgx5QYZTwnHO5G5MX9gOiCbbxBqcOifVywX1_ienElksDIvjuQFL7zOSoXipuBUcfTwdtiOgBpNF"
              "TvtMB4xjrYABg2nm47umJXNjN9KtMCC49sMp8bOvpgTvedghPhpGBDPoljYL_1VFAezjilCIaaa1NdXQDBSBdupQoxuVrkMiskmVt6lJ"
              "MAiSPTteOtzXtm1WKvJftKZVk1bdrv-XqMQDxoiPirGZSwqkaKDmrdBinK0LbUPNt06BA7cXl04cgp2eu11tpY6cgnvWEfvK32S1IHci"
              "XLipfwb1uHIdgX8i1pyiGj_JAQHodICzSww"
            }
          ]
        }
        key_server_request.return_value = Mock(
          content=json.dumps(jwk)
        )

        resets = [
          AUTH.JWT.VERIFY.set_for_testing(True),
          AUTH.JWT.USERNAME_HEADER.set_for_testing('sub'),
          AUTH.JWT.KEY_SERVER_URL.set_for_testing('https://ext-authz:8000'),
          AUTH.JWT.ISSUER.set_for_testing('issuer'),
          AUTH.JWT.AUDIENCE.set_for_testing('audience')
        ]

        try:
          user, token = JwtAuthentication().authenticate(request=self.request)

          jwt_decode.assert_called_with(
            algorithms=['RS256'],
            audience='audience',
            issuer='issuer',
            jwt=self.sample_token, 
            key=b'-----BEGIN PUBLIC KEY-----\n'
            b'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwe9gTbRxHl4Ye9mY9abY\n'
            b'l/WHgx5QYZTwnHO5G5MX9gOiCbbxBqcOifVywX1/ienElksDIvjuQFL7zOSoXipu\n'
            b'BUcfTwdtiOgBpNFTvtMB4xjrYABg2nm47umJXNjN9KtMCC49sMp8bOvpgTvedghP\n'
            b'hpGBDPoljYL/1VFAezjilCIaaa1NdXQDBSBdupQoxuVrkMiskmVt6lJMAiSPTteO\n'
            b'tzXtm1WKvJftKZVk1bdrv+XqMQDxoiPirGZSwqkaKDmrdBinK0LbUPNt06BA7cXl\n'
            b'04cgp2eu11tpY6cgnvWEfvK32S1IHciXLipfwb1uHIdgX8i1pyiGj/JAQHodICzS\n'
            b'wwIDAQAB\n-----END PUBLIC KEY-----\n',
            options={'verify_signature': True}
          )
          assert_equal(user, self.user)
        finally:
          for reset in resets:
            reset()
