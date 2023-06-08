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
import logging
import requests
import requests_kerberos

from desktop.conf import SDXAAS
from desktop.lib.exceptions_renderable import PopupException

LOG = logging.getLogger()

_KNOX_TOKEN_API = '/knoxtoken/api/v1/token'
_KNOX_TOKEN_GET_PARAM_STRING = '?knox.token.include.groups=true'


def handle_knox_ha():
  knox_urls = SDXAAS.TOKEN_URL.get()
  auth_handler = requests_kerberos.HTTPKerberosAuth(mutual_authentication=requests_kerberos.OPTIONAL)
  res = None

  if knox_urls:
    # Config format is "['url1', 'url2']" for HA, so we need to clean up and split correctly in list.
    # For non-HA, its normal url string.
    knox_urls_list = knox_urls.replace("%20", "").replace("['", "").replace("']", "").replace("'", "").split(',')

    for k_url in knox_urls_list:
      try:
        res = requests.get(k_url.rstrip('/') + _KNOX_TOKEN_API, auth=auth_handler, verify=False)
      except Exception as e:
        if 'Name or service not known' in str(e):
          LOG.warning('Knox URL %s is not available.' % k_url)

      # Check response for None and if response code is successful (200) or authentication needed (401), use that host URL.
      if (res is not None) and (res.status_code in (200, 401)):
        return k_url


def fetch_jwt():
  '''
  Return JWT fetched from healthy Knox host.
  '''
  knox_url = handle_knox_ha()
  if not knox_url:
    raise PopupException('Knox URL not available to fetch JWT.')

  auth_handler = requests_kerberos.HTTPKerberosAuth(mutual_authentication=requests_kerberos.OPTIONAL)
  knox_response = None

  try:
    LOG.debug('Fetching Knox JWT from URL: %s' % knox_url)
    knox_response = requests.get(knox_url.rstrip('/') + _KNOX_TOKEN_API + _KNOX_TOKEN_GET_PARAM_STRING, auth=auth_handler, verify=False)
  except Exception as e:
    raise Exception('Error fetching JWT from Knox URL %s with exception: %s' % (knox_url, str(e)))

  jwt_token = None
  if knox_response:
    jwt_token = json.loads(knox_response.text)['access_token']
    LOG.debug('Retrieved Knox JWT: %s' % jwt_token)

  return jwt_token