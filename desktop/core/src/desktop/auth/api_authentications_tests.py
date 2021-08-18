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

    self.sample_token = "eyJhbGciOiJSUzI1NiJ9.eyJhdWQiOlsid29ya2xvYWQtYXBwIiwicmFuZ2VyIl0sImV4cCI6MTYyNjI1Njg5MywiaWF0IjoxNjI2MjU2NTkzLCJpc3MiOiJDbG91ZGVyYTEiLCJqdGkiOiJpZDEiLCJzdWIiOiJ0ZXN0LXN1YmplY3QiLCJ1c2VyIjoidGVzdF91c2VyIn0.jvyVDxbWTAik0jbdUcIc9ZANNrJZUCWH-Pg7FloRhg0ZYAETd_AO3p5v_ppoMmVcPD2xBSrngA5J3_A_zPBvQ_hdDlpb0_-mCCJfGhC5tju4bI9EE9Akdn2FrrsqrvQQ8cPyGsIlvoIxrK1De4f74MmUaxfN7Hrrcue1PTY4u4IB9cWQqV9vIcX99Od5PUaNekLIee-I8gweqvfGEEsW7qWUM63nh59_TOB3LLq-YcEuaX1h_oiTATeCssjk_ee9RrJGLNyKmC0WJ4UrEWn8a_T3bwCy8CMe0zV5PSuuvPHy0FvnTo2il5SDjGimxKcbpgNiJdfblslu6i35DlfiWg"
    self.request = MagicMock(
      META={
        "HTTP_AUTHORIZATION": "Bearer " + self.sample_token
      }
    )


  def test_authenticate_existing_user(self):
    with patch('desktop.auth.api_authentications.jwt.decode') as jwt_decode:
      with patch('desktop.auth.api_authentications.requests.get'):

        jwt_decode.return_value = {
          "user": "test_user"
        }

        user, token = JwtAuthentication().authenticate(request=self.request)

        assert_equal(user, self.user)
        assert_true(user.is_authenticated)
        assert_false(user.is_superuser)


  def test_authenticate_new_user(self):
    with patch('desktop.auth.api_authentications.jwt.decode') as jwt_decode:
      with patch('desktop.auth.api_authentications.requests.get'):

        jwt_decode.return_value = {
          "user": "test_new_user"
        }

        assert_false(User.objects.filter(username="test_new_user").exists())

        user, token = JwtAuthentication().authenticate(request=self.request)

        assert_true(User.objects.filter(username="test_new_user").exists())
        assert_equal(User.objects.get(username="test_new_user"), user)
        assert_true(user.is_authenticated)
        assert_false(user.is_superuser)


  def test_failed_authentication(self):
    with patch('desktop.auth.api_authentications.jwt.decode') as jwt_decode:
      with patch('desktop.auth.api_authentications.requests.get'):

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
          "user": "test_user"
        }
        user, token = JwtAuthentication().authenticate(request=self.request)

        assert_true('jwt_access_token' in user.profile.data)
        assert_equal(user.profile.data['jwt_access_token'], self.sample_token)


  def test_check_token_verification_flag(self):
    with patch('desktop.auth.api_authentications.requests.get'):

      # When verification flag is True for old sample token
      reset = AUTH.JWT.VERIFY.set_for_testing(True)
      try:
        assert_raises(exceptions.AuthenticationFailed, JwtAuthentication().authenticate, self.request)
      finally:
        reset()

      # When verification flag is False
      reset = AUTH.JWT.VERIFY.set_for_testing(False)
      try:
        user, token = JwtAuthentication().authenticate(request=self.request)

        assert_equal(user, self.user)
      finally:
        reset()
