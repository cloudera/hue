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

try:
  import json
except ImportError:
  import simplejson as json
import logging

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

  def _join_uri(self, relpath):
    if relpath is None:
      return self._path
    return (self._path + '/' + relpath).strip('/')

  def _invoke(self, method, relpath=None, json_decode=True, **params):
    """
    Invoke an API method.
    @return: JSON dictionary.
    """
    path = self._join_uri(relpath)
    res = self._client.execute(method, path, **params)
    if not json_decode:
      return res

    try:
      # Return JSON
      json_dict = json.loads(res)
      return json_dict
    except Exception, ex:
      self._client.logger.exception('Server response: %s' % (res,))
      raise ex


  def get(self, relpath=None, **params):
    """
    Invoke the GET method on a resource.
    @param relpath: Optional. A relative path to this resource's path.
    @param params: Key-value data.

    @return: A dictionary of the JSON result.
    """
    return self._invoke("GET", relpath, **params)


  def get_raw(self, relpath=None, **params):
    """
    Invoke the GET method on a resource.
    @param relpath: Optional. A relative path to this resource's path.
    @param params: Key-value data.

    @return: Raw response body.
    """
    return self._invoke("GET", relpath, json_decode=False, **params)


  def post(self, relpath=None, **params):
    """
    Invoke the POST method on a resource.
    @param relpath: Optional. A relative path to this resource's path.
    @param params: Key-value data.

    @return: A dictionary of the JSON result.
    """
    return self._invoke("POST", relpath, **params)


  def put(self, relpath=None, **params):
    """
    Invoke the PUT method on a resource.
    @param relpath: Optional. A relative path to this resource's path.
    @param params: Key-value data.

    @return: A dictionary of the JSON result.
    """
    return self._invoke("PUT", relpath, **params)
