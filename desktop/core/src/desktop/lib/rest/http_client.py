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

import cookielib
import logging
import posixpath
import urllib
import urllib2

__docformat__ = "epytext"

LOG = logging.getLogger(__name__)

class RestException(Exception):
  """
  Any error result from the Rest API is converted into this exception type.
  """
  def __init__(self, error):
    Exception.__init__(self, error)
    self._error = error
    self._code = None
    self._message = str(error)
    # See if there is a code or a message. (For urllib2.HTTPError.)
    try:
      self._code = error.getcode()
      self._message = error.read()
    except AttributeError:
      pass

  def __str__(self):
    res = self._message or ""
    if self._code is not None:
      res += " (error %s)" % (self._code,)
    return res

  def get_parent_ex(self):
    if isinstance(self._error, Exception):
      return self._error
    return None

  @property
  def code(self):
    return self._code

  @property
  def message(self):
    return self._message


class HttpClient(object):
  """
  Basic HTTP client tailored for rest APIs.
  """
  def __init__(self, base_url, exc_class=None, logger=None):
    """
    @param base_url: The base url to the API.
    @param exc_class: An exception class to handle non-200 results.

    Creates an HTTP(S) client to connect to the Cloudera Manager API.
    """
    self._base_url = base_url.rstrip('/')
    self._exc_class = exc_class or RestException
    self._logger = logger or LOG
    self._headers = { }

    # Make a basic auth handler that does nothing. Set credentials later.
    self._passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    authhandler = urllib2.HTTPBasicAuthHandler(self._passmgr)

    # Make a cookie processor
    cookiejar = cookielib.CookieJar()

    self._opener = urllib2.build_opener(
      urllib2.HTTPCookieProcessor(cookiejar), authhandler)


  def set_basic_auth(self, username, password, realm):
    """
    Set up basic auth for the client
    @param username: Login name.
    @param password: Login password.
    @param realm: The authentication realm.
    @return: The current object
    """
    self._passmgr.add_password(realm, self._base_url, username, password)
    return self

  def set_headers(self, headers):
    """
    Add headers to the request
    @param headers: A dictionary with the key value pairs for the headers
    @return: The current object
    """
    self._headers = headers
    return self


  @property
  def base_url(self):
    return self._base_url

  @property
  def logger(self):
    return self._logger

  def execute(self, http_method, path, params=None, data=None):
    """
    Submit an HTTP request.
    @param http_method: GET, POST, PUT, DELETE
    @param path: The path of the resource.
    @param params: Key-value parameter data.
    @param data: The data to attach to the body of the request.

    @return: The result of urllib2.urlopen()
    """
    # Prepare URL and params
    url = self._make_url(path, params)
    if http_method in ("GET", "DELETE"):
      if data is not None:
        self.logger.warn(
            "GET method does not pass any data. Path '%s'" % (path,))
        data = None

    # Setup the request
    request = urllib2.Request(url, data)
    # Hack/workaround because urllib2 only does GET and POST
    request.get_method = lambda: http_method
    for k, v in self._headers.items():
      request.add_header(k, v)

    # Call it
    self.logger.debug("%s %s" % (http_method, url))
    try:
      return self._opener.open(request)
    except urllib2.HTTPError, ex:
      raise self._exc_class(ex)

  def _make_url(self, path, params):
    res = self._base_url
    if path:
      res += posixpath.normpath('/' + path)
    if params:
      param_str = urllib.urlencode(params)
      res += '?' + param_str
    return res
