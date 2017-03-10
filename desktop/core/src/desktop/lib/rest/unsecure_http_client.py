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
import threading

from desktop import conf

from desktop.lib.rest.http_client import HttpClient, RestException

__docformat__ = "epytext"

LOG = logging.getLogger(__name__)

CACHE_UNSECURE_SESSION = None
CACHE_UNSECURE_SESSION_LOCK = threading.Lock()

def get_unsecure_httponly_request_session():
  global CACHE_UNSECURE_SESSION
  if CACHE_UNSECURE_SESSION is None:
    CACHE_UNSECURE_SESSION_LOCK.acquire()
    try:
      if CACHE_UNSECURE_SESSION is None:
        CACHE_UNSECURE_SESSION = requests.Session()
        CACHE_UNSECURE_SESSION.mount('http://', requests.adapters.HTTPAdapter(pool_connections=conf.CHERRYPY_SERVER_THREADS.get(), pool_maxsize=conf.CHERRYPY_SERVER_THREADS.get()))
    finally:
      CACHE_UNSECURE_SESSION_LOCK.release()
  return CACHE_UNSECURE_SESSION

class UnsecureHttpClient(HttpClient):
  """
  HTTP Client that should not be used with Kerberos in order to keep the pool separate from the kerberized one.

  This allow to have a pool of HTTP client with Kerberos authentication and another one without, in case the components are not all secure or all unsecure.
  """
  def __init__(self, base_url, exc_class=None, logger=None):
    """
    @param base_url: The base url to the API.
    @param exc_class: An exception class to handle non-200 results.
    """
    self._base_url = base_url.rstrip('/')
    self._exc_class = exc_class or RestException
    self._logger = logger or LOG
    self._session = get_unsecure_httponly_request_session()
    self._cookies = None
