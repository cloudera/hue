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

import cookielib
import logging
import urllib
import urllib2

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
    if isinstance(error, urllib2.HTTPError):
      self._code = error.getcode()
      self._message = error.read()

  def __str__(self):
    res = self._message
    if self._code is not None:
      res += " (error %s)" % (self._code,)
    return res


class HttpClient(object):
  """
  Basic HTTP client tailed for rest APIs.
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
    """
    self._passmgr.add_password(realm, self._base_url, username, password)


  @property
  def base_url(self):
    return self._base_url

  @property
  def logger(self):
    return self._logger

  def execute(self, http_method, path, **params):
    """
    Submit an HTTP request.
    @param http_method: GET, POST, PUT, DELETE
    @param path: The path of the resource.
    @param params: Key-value data.

    @rtype: json
    @return: The JSON result of the API call.
    """
    # Prepare URL and params
    param_str = urllib.urlencode(params)
    if http_method in ("GET", "DELETE"):
      url = "%s/%s?%s" % (self._base_url, path, param_str)
      data = None
    elif http_method == "POST":
      url = "%s/%s" % (self._base_url, path)
      data = param_str
    elif http_method == "PUT":
      url = "%s/%s" % (self._base_url, path)
      data = param_str
    else:
      raise NotImplementedError("Method type %s not supported" % (http_method,))

    # Setup the request
    request = urllib2.Request(url)
    request.get_method = lambda: http_method
    request.get_data = lambda: data

    # Call it
    self.logger.debug("%s %s" % (http_method, url))
    try:
      call = self._opener.open(request)
    except urllib2.HTTPError, ex:
      raise self._exc_class(ex)

    try:
      resp = call.read()
      self.logger.debug("%s Got response: %s%s" %
                        (http_method, resp[:32], len(resp) > 32 and "..." or ""))
    except Exception, ex:
      raise Exception("Command '%s %s' failed: %s" %
                      (http_method, path, ex))
    return resp
