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
import sys

from desktop import conf
from desktop.lib.raz.clients import AdlsRazClient
from desktop.lib.rest.http_client import HttpClient


if sys.version_info[0] > 2:
  import urllib.request, urllib.error
else:
  from urllib import quote as urllib_quote


LOG = logging.getLogger(__name__)


class RazHttpClient(HttpClient):

  def __init__(self):
    # Note: there is no concept of base_url and credentials anymore
    # Maybe create here: http_client.HttpClient(url, exc_class=WebHdfsException, logger=LOG)
    pass

  def execute(self, http_method, path, params=None, data=None, headers=None, allow_redirects=False, urlencode=True,
              files=None, stream=False, clear_cookies=False, timeout=conf.REST_CONN_TIMEOUT.get()):

    raz_client = AdlsRazClient()

    container = 'hue'
    storage_account = 'gethue.dfs.core.windows.net'

    # https://[storageaccountname].blob.core.windows.net/[containername]/[blobname]?sv=2014-02-14&sr=b&
    #   sig=pJL%2FWyed41tptiwBM5ymYre4qF8wzrO05tS5MCjkutc%3D&st=2015-01-02T01%3A40%3A51Z&se=2015-01-02T02%3A00%3A51Z&sp=r
    tmp_url = raz_client.get_url(storage_account, container, relative_path=path, perm='read')

    # TODO: get clean `path` etc

    return super(RazHttpClient, self).execute(http_method=http_method, path=tmp_url)
