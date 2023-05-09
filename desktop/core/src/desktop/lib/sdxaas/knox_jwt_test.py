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
import unittest

from nose.tools import assert_equal, assert_raises

from desktop.conf import SDXAAS
from desktop.lib.sdxaas.knox_jwt import handle_knox_ha, fetch_jwt
from desktop.lib.exceptions_renderable import PopupException

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


def test_handle_knox_ha():
  with patch('desktop.lib.sdxaas.knox_jwt.requests_kerberos.HTTPKerberosAuth') as HTTPKerberosAuth:
    with patch('desktop.lib.sdxaas.knox_jwt.requests.get') as requests_get:

      requests_get.return_value = Mock(status_code=200)

      # Non-HA mode
      reset = SDXAAS.TOKEN_URL.set_for_testing('https://knox-gateway0.gethue.com:8443/dl-name/kt-kerberos/')

      try:
        knox_url = handle_knox_ha()
        assert_equal(knox_url, 'https://knox-gateway0.gethue.com:8443/dl-name/kt-kerberos/')
      finally:
        reset()

      # HA mode - where first URL sends 200 status code
      reset = SDXAAS.TOKEN_URL.set_for_testing(
        'https://knox-gateway0.gethue.com:8443/dl-name/kt-kerberos/, https://knox-gateway1.gethue.com:8443/dl-name/kt-kerberos/')

      try:
        knox_url = handle_knox_ha()
        assert_equal(knox_url, 'https://knox-gateway0.gethue.com:8443/dl-name/kt-kerberos/')
      finally:
        reset()

      # When no Knox URL is healthy
      requests_get.return_value = Mock(status_code=404)
      reset = SDXAAS.TOKEN_URL.set_for_testing(
        'https://knox-gateway0.gethue.com:8443/dl-name/kt-kerberos/, https://knox-gateway1.gethue.com:8443/dl-name/kt-kerberos/')

      try:
        knox_url = handle_knox_ha()
        assert_equal(knox_url, None)
      finally:
        reset()


def test_fetch_jwt():
  with patch('desktop.lib.sdxaas.knox_jwt.requests_kerberos.HTTPKerberosAuth') as HTTPKerberosAuth:
    with patch('desktop.lib.sdxaas.knox_jwt.requests.get') as requests_get:
      with patch('desktop.lib.sdxaas.knox_jwt.handle_knox_ha') as handle_knox_ha:

        handle_knox_ha.return_value = 'https://knox-gateway.gethue.com:8443/dl-name/kt-kerberos/'
        requests_get.return_value = Mock(text='{"access_token":"test_jwt_token"}')

        jwt_token = fetch_jwt()

        requests_get.assert_called_with(
          'https://knox-gateway.gethue.com:8443/dl-name/kt-kerberos/knoxtoken/api/v1/token?knox.token.include.groups=true', 
          auth=HTTPKerberosAuth(), 
          verify=False
        )
        assert_equal(jwt_token, "test_jwt_token")

        # Raises PopupException when knox_url is not available
        handle_knox_ha.return_value = None
        assert_raises(PopupException, fetch_jwt)
