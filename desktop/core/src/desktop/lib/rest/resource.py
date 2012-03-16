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

try:
  import json
except ImportError:
  import simplejson as json
import logging
import posixpath

LOG = logging.getLogger(__name__)


class Resource(object):
  """
  Encapsulates a resource, and provides actions to invoke on it.
  """
  def __init__(self, client, relpath=""):
    """
    @param client: A Client object.
    @param relpath: The relative path of the resource.
    """
    self._client = client
    self._path = relpath.strip('/')

  @property
  def base_url(self):
    return self._client.base_url

  def _join_uri(self, relpath):
    if relpath is None:
      return self._path
    return self._path + posixpath.normpath('/' + relpath)

  def invoke(self, method, relpath=None, params=None, data=None, headers=None):
    """
    Invoke an API method.
    @return: Raw body or JSON dictionary (if response content type is JSON).
    """
    path = self._join_uri(relpath)
    resp = self._client.execute(method,
                                path,
                                params=params,
                                data=data,
                                headers=headers)
    try:
      body = resp.read()
    except Exception, ex:
      raise Exception("Command '%s %s' failed: %s" %
                      (method, path, ex))

    self._client.logger.debug(
        "%s Got response: %s%s" %
        (method, body[:32], len(body) > 32 and "..." or ""))

    # Is the response application/json?
    if len(body) != 0 and \
          resp.info().getmaintype() == "application" and \
          resp.info().getsubtype() == "json":
      try:
        json_dict = json.loads(body)
        return json_dict
      except Exception, ex:
        self._client.logger.exception('JSON decode error: %s' % (body,))
        raise ex
    else:
      return body


  def get(self, relpath=None, params=None):
    """
    Invoke the GET method on a resource.
    @param relpath: Optional. A relative path to this resource's path.
    @param params: Key-value data.

    @return: A dictionary of the JSON result.
    """
    return self.invoke("GET", relpath, params)


  def delete(self, relpath=None, params=None):
    """
    Invoke the DELETE method on a resource.
    @param relpath: Optional. A relative path to this resource's path.
    @param params: Key-value data.

    @return: A dictionary of the JSON result.
    """
    return self.invoke("DELETE", relpath, params)


  def post(self, relpath=None, params=None, data=None, contenttype=None):
    """
    Invoke the POST method on a resource.
    @param relpath: Optional. A relative path to this resource's path.
    @param params: Key-value data.
    @param data: Optional. Body of the request.
    @param contenttype: Optional. 

    @return: A dictionary of the JSON result.
    """
    return self.invoke("POST", relpath, params, data,
                       self._make_headers(contenttype))


  def put(self, relpath=None, params=None, data=None, contenttype=None):
    """
    Invoke the PUT method on a resource.
    @param relpath: Optional. A relative path to this resource's path.
    @param params: Key-value data.
    @param data: Optional. Body of the request.
    @param contenttype: Optional. 

    @return: A dictionary of the JSON result.
    """
    return self.invoke("PUT", relpath, params, data,
                       self._make_headers(contenttype))


  def _make_headers(self, contenttype=None):
    if contenttype:
      return { 'Content-Type': contenttype }
    return None
