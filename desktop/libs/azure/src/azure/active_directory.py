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

from builtins import object
import logging

from azure.conf import get_refresh_url
from desktop.lib.python_util import current_ms_from_utc
from desktop.lib.rest import http_client, resource

LOG = logging.getLogger()

class ActiveDirectory(object):
  def __init__(self, url=None, aws_access_key_id=None, aws_secret_access_key=None, version=None):
    self._access_key_id = aws_access_key_id
    self._secret_access_key = aws_secret_access_key
    self._url = url;

    self._client = http_client.HttpClient(url, logger=LOG)
    self._root = resource.Resource(self._client)
    self._version = version


  def get_token(self):
    if not self._version:
      return self._get_token({"resource": "https://management.core.windows.net/"})
    else:
      return self._get_token({"scope": "https://storage.azure.com/.default"})


  def _get_token(self, params=None):
    LOG.debug("Authenticating to Azure Active Directory: %s" % self._url)
    data = {
      "grant_type" : "client_credentials",
      "client_id" : self._access_key_id,
      "client_secret" : self._secret_access_key
    }
    data.update(params)
    token = self._root.post("/", data=data, log_response=False)
    token["expires_on"] = int(token.get("expires_on", (current_ms_from_utc() + int(token.get("expires_in")) * 1000) / 1000))
    return token


  @classmethod
  def from_config(cls, conf=None, version=None):
    access_key_id = conf.CLIENT_ID.get()
    secret_access_key = conf.CLIENT_SECRET.get()

    if None in (access_key_id, secret_access_key):
      raise ValueError('Can\'t create azure client, credential is not configured')

    url = get_refresh_url(conf, version)

    return cls(
      url,
      aws_access_key_id=access_key_id,
      aws_secret_access_key=secret_access_key,
      version=version
    )