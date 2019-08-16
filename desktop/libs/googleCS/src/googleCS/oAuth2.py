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

from __future__ import absolute_import

from builtins import object
import logging

from time import time
from googleCS.conf import GOOGLE_ACCOUNTS, REDIRECT_URI
from desktop.lib.rest import http_client, resource

LOG = logging.getLogger(__name__)

class GoogleOAuth2(object):
  def __init__(self, url=None, aws_access_key_id=None, aws_secret_access_key=None, google_au_code = None, ):
    self._access_key_id = aws_access_key_id
    self._secret_access_key = aws_secret_access_key
    self._authorize_code = google_au_code
    self._url = url;

    self._client = http_client.HttpClient(url, logger=LOG)
    self._root = resource.Resource(self._client)
    self._token = None
    self._refresh_token = None


  def get_token(self):
    if self._token is None:
      return self._get_token()
    elif time() >= self._token["expires_on"]:
      return self._refresh_access_token()
    return self._token["token_type"] + " " + self._token["access_token"]

  def _get_token(self, params=None):
    is_token_expired = self._token is None or time() >= self._token["expires_on"]
    if is_token_expired:
      LOG.debug("Authenticating to Google APIs: %s" % self._url)
      data = {
        "grant_type" : "client_credentials",
        "client_id" : self._access_key_id,
        "client_secret" : self._secret_access_key
      }
      data.update(params)
      self._token = self._root.post("/", data=data, log_response=False);
      self._refresh_token = self._token["refresh_token"]
      self._token["expires_on"] = int(self._token.get("expires_on", self._token.get("expires_in")))

    return self._token["token_type"] + " " + self._token["access_token"]


  def _refresh_access_token(self):
    LOG.debug("Refreshing Token for Google APIs: %s" % self._url)
    data = {
      "grant_type" : "refresh_token",
      "refresh_token" : self._refresh_token,
      "client_id" : self._access_key_id,
      "client_secret" : self._secret_access_key
    }
    data.update(params)
    try:
      self._token = self._root.post("/", data=data, log_response=False);
      if "refresh_token" in self._token:
        self._refresh_token = self._token['refresh_token']
      self._token["expires_on"] = int(self._token.get("expires_on", self._token.get("expires_in")))
    except:
      return self._get_token()
    return self._token["token_type"] + " " + self._token["access_token"]
  
  @classmethod
  def from_config(cls, conf='default', version=None):
    access_key_id = GOOGLE_ACCOUNTS['default'].CLIENT_ID.get()
    secret_access_key = GOOGLE_ACCOUNTS['default'].CLIENT_SECRET.get()
    authorizecode = GOOGLE_ACCOUNTS['default'].AUTHORIZE_CODE.get()

    if None in (access_key_id, secret_access_key):
      raise ValueError('Can\'t create google client, credential is not configured')

    url = "https://www.googleapis.com/oauth2/v4/token"

    return cls(
      url,
      aws_access_key_id=access_key_id,
      aws_secret_access_key=secret_access_key,
      google_au_code=authorizecode
    )