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

  @classmethod
  def setUpClass(cls):
    if sys.version_info[0] < 3:
      raise SkipTest


  def setUp(self):
    self.client = make_logged_in_client(username="test_user", groupname="default", recreate=True, is_superuser=False)
    self.user = rewrite_user(User.objects.get(username="test_user"))

    self.sample_token = "eyJhbGciOiJSUzI1NiJ9.eyJhdWQiOlsid29ya2xvYWQtYXBwIiwicmFuZ2VyIl0sImV4cCI6MTYyNjI1Njg5MywiaWF" \
                        "0IjoxNjI2MjU2NTkzLCJpc3MiOiJDbG91ZGVyYTEiLCJqdGkiOiJpZDEiLCJzdWIiOiJ0ZXN0LXN1YmplY3QiLCJ1c2V" \
                        "yIjoidGVzdF91c2VyIn0.jvyVDxbWTAik0jbdUcIc9ZANNrJZUCWH-Pg7FloRhg0ZYAETd_AO3p5v_ppoMmVcPD2xBSr" \
                        "ngA5J3_A_zPBvQ_hdDlpb0_-mCCJfGhC5tju4bI9EE9Akdn2FrrsqrvQQ8cPyGsIlvoIxrK1De4f74MmUaxfN7Hrrcue" \
                        "1PTY4u4IB9cWQqV9vIcX99Od5PUaNekLIee-I8gweqvfGEEsW7qWUM63nh59_TOB3LLq-YcEuaX1h_oiTATeCssjk_ee" \
                        "9RrJGLNyKmC0WJ4UrEWn8a_T3bwCy8CMe0zV5PSuuvPHy0FvnTo2il5SDjGimxKcbpgNiJdfblslu6i35DlfiWg"
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
          "user": "test_user"
        }
        user, token = JwtAuthentication().authenticate(request=self.request)

        assert_true('jwt_access_token' in user.profile.data)
        assert_equal(user.profile.data['jwt_access_token'], self.sample_token)


  def test_check_token_verification_flag(self):
    with patch('desktop.auth.api_authentications.requests.get'):
      with patch('desktop.auth.api_authentications.jwt.algorithms.RSAAlgorithm.from_jwk'):
        with patch('desktop.auth.api_authentications.JwtAuthentication._handle_public_key'):

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


  def test_handle_public_key(self):
    with patch('desktop.auth.api_authentications.requests.get') as key_server_request:
      with patch('desktop.auth.api_authentications.jwt.decode') as jwt_decode:

        jwt_decode.return_value = {
          "user": "test_user"
        }
        jwk = {
          "keys": [
            {
              "kty": "RSA",
              "kid": "1",
              "alg": "RSA256",
              "n": "rtT3gR0NDIx6gv8xYLiPue_ItaIbognCGGgQbipp3IOuobu2RnJjedsIRBTEOdkVx-xjV6m92VYtrpW6gM9vldwTfI0UmoSLGKT"
                   "5uYd0JGHvYWoN9inCZYZcnala58T8HDgLiXa9KlEuQxGGQDemB3yf5rgS1OhLBKVsI8bMVgah7xNIiBOWsVeWIEr13Nem8HUuDq"
                   "gIpL_8TgjxFOqFcdqPCfoIZ89JKEiKbsGbU-lqs1xYChFscI_w7Jc7l6rvf2nsLGMFs3U4ZJvS4AUpVno2e527clXzQisfJKwb4"
                   "hjfKRMhHfnYfyJxaoHqWfx8DjXmH3CMqlWr_-hL3y1-4Q",
              "e": "AQAB",
              "d": "XVj4jcelH_4hq6_1_V6N3wlYcSKM_oeXStDFdQzQWR02MMS5HgQVeQqp7y_nVbvDFWvx3uySoWiSG5V2bzBStAE9plLtnVMHsbD"
                   "kZVsdeA-ScMDfk3_Ye7yx1ryF_RoAQlDqWAs-FUojGUxSEhekXnr8JYRDCcq9w01P4ApVL9iX9Togk8MFO68vKRykeFC21TGE87"
                   "-2_ieIMksDf25r-uhYzdN1FCJuzHRaYBUBgBRq82rgno1f1Y9_j8TN30NQtOLr5UtYkH-iKb_wqgocFG9GamEbBzzZW2_BwRhyw"
                   "Hm1ciJyiQ_Woikx798HoXlHOEHi8q4G-ay2JUFcbTyAAQ",
              "p": "5umhRLdRjv30UO53l9gmVs2nUJPD-Uv_vDzx27aemTqaBxjTj_rVo3_KUwunQ4Y9aaaQo9BvlxG-tlmtYuDHYKavxqFQ6Q6jci3"
                   "OWv2my9515akl5nUWj4SQD9xvve3b7x-nVGRefYmGvscXZU_Ryg1CZ_4FPsfljWwBTo7ggaE",
              "q": "wdOQhh0NOxj1oI3cod_IQxl-5UjBzRvkm6Yx9r2QyOn2wk60b_ExWA8CrEr-eOSSSc0TMf2Y8vbCjzXSkd2-Gbsz4OOC-AkxY5W"
                   "4FonLxF8AQabAXeIIfH7qF7Q0ByaZBFFaNQ3ejBunBa5ph0KUrxDrzVf1tcX3b8y8fHIudUE",
              "dp": "ctEaojtw72PxNsjMaJFOxvytRFClMnGKsMOxEynkBJbx_bNnhwEXd5vUM6Tov5ehM8Zhx0KeKgTlynAe2bqhCLr5Tg_qVmgz91"
                    "M1d2MGq_pqrw6DTOtNk4E7zNc0LMF4CZe4sSrTHSLkADqotHSTAR_EtEbHvubQiph4seIzWeE",
              "dq": "q_htG0D9czjC_i-_2PO3OCmP2BkEsloULDF51ST-J_TF1kKEf2mtUScIRRvIyjRqwwYsCMerg66CkxO6_2aRez0IW3kgw7dMVc"
                    "IJ8h1SaKmtjZJIzUN2Khdk1aEyJEIPs7AGbFog4YjLWRQVV0gwqV9HCAsJ27yIvG4XsgaQx8E",
              "qi": "lNOWMacUcZtytxeTfeR6OWbqufAp56cICNTZX82JDnoi2KCmyeUERl1tLdYC1giK2lNw5j57ojTigPpyhBdeZ-3NqlJEH8pq6g"
                    "JXNSpBOWTGzOT_EcW2jaCP4cT8q1Js3pFUynYPdXRU9FG0kdQgNIrDztNZJlPtdFxAVgCM4PY",
            }
          ]
        }
        key_server_request.return_value = Mock(
          content=json.dumps(jwk)
        )

        resets = [
          AUTH.JWT.VERIFY.set_for_testing(True),
          AUTH.JWT.KEY_SERVER_URL.set_for_testing('https://ext-authz:8000'),
          AUTH.JWT.ISSUER.set_for_testing('issuer'),
          AUTH.JWT.AUDIENCE.set_for_testing('audience')
        ]

        try:
          user, token = JwtAuthentication().authenticate(request=self.request)

          jwt_decode.assert_called_with(
            algorithms=['RS256'],
            audience=AUTH.JWT.AUDIENCE.get(),
            issuer=AUTH.JWT.ISSUER.get(),
            jwt=self.sample_token,
            key=b'-----BEGIN PUBLIC KEY-----\n'
            b'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArtT3gR0NDIx6gv8xYLiP\n'
            b'ue/ItaIbognCGGgQbipp3IOuobu2RnJjedsIRBTEOdkVx+xjV6m92VYtrpW6gM9v\n'
            b'ldwTfI0UmoSLGKT5uYd0JGHvYWoN9inCZYZcnala58T8HDgLiXa9KlEuQxGGQDem\n'
            b'B3yf5rgS1OhLBKVsI8bMVgah7xNIiBOWsVeWIEr13Nem8HUuDqgIpL/8TgjxFOqF\n'
            b'cdqPCfoIZ89JKEiKbsGbU+lqs1xYChFscI/w7Jc7l6rvf2nsLGMFs3U4ZJvS4AUp\n'
            b'Vno2e527clXzQisfJKwb4hjfKRMhHfnYfyJxaoHqWfx8DjXmH3CMqlWr/+hL3y1+\n'
            b'4QIDAQAB\n'
            b'-----END PUBLIC KEY-----\n',
            options={'verify_signature': True}
          )
          assert_equal(user, self.user)
        finally:
          for reset in resets:
            reset()
