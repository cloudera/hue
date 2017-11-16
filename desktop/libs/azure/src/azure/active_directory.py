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
from __future__ import absolute_import

import logging

from time import time
from azure.conf import AZURE_ACCOUNTS, get_default_refresh_url
from desktop.lib.rest import http_client, resource

LOG = logging.getLogger(__name__)

class ActiveDirectory(object):
  def __init__(self, url=None, aws_access_key_id=None, aws_secret_access_key=None):
    self._access_key_id = aws_access_key_id
    self._secret_access_key = aws_secret_access_key
    self._url = url;

    self._client = http_client.HttpClient(url, logger=LOG)
    self._root = resource.Resource(self._client)
    self._token = None

  def get_token(self):
    is_token_expired = self._token is None or time() >= self._token["expires_on"]
    if is_token_expired:
      LOG.debug("Authenticating to Azure Active Directory: %s" % self._url)
      data = {
        "grant_type" : "client_credentials",
        "resource" : "https://management.core.windows.net/",
        "client_id" : self._access_key_id,
        "client_secret" : self._secret_access_key
      }
      self._token = self._root.post("/", data=data, log_response=False);
      self._token["expires_on"] = int(self._token["expires_on"])

    return self._token["token_type"] + " " + self._token["access_token"]

  @classmethod
  def from_config(cls, conf):
    access_key_id = AZURE_ACCOUNTS['default'].CLIENT_ID.get()
    secret_access_key = AZURE_ACCOUNTS['default'].CLIENT_SECRET.get()

    if None in (access_key_id, secret_access_key):
      raise ValueError('Can\'t create azure client, credential is not configured')

    url = get_default_refresh_url()

    return cls(
      url,
      aws_access_key_id=access_key_id,
      aws_secret_access_key=secret_access_key
    )