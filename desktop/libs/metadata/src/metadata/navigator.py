#!/usr/bin/env python
# -- coding: utf-8 --
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

from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest import resource

from metadata.conf import NAVIGATOR


LOG = logging.getLogger(__name__)


class NavigatorApiException(Exception):
  pass


class NavigatorApi(object):
  """
  http://cloudera.github.io/navigator/apidocs/v2/index.html
  """

  def __init__(self, api_url=None, user=None, password=None):
    self._api_url = (api_url or NAVIGATOR.API_URL.get()).strip('/')
    self._username = user or NAVIGATOR.AUTH_USERNAME.get()
    self._password = password or NAVIGATOR.AUTH_PASSWORD.get()

    self._client = HttpClient(self._api_url, logger=LOG)
    self._client.set_basic_auth(self._username, self._password)
    self._root = resource.Resource(self._client)

    self.__headers = {}
    self.__params = ()


  def find_entity(self, source_type, type, name, **filters):
    """
    GET /api/v2/entities?query=((sourceType:<source_type>)AND(type:<type>)AND(originalName:<name>))
    http://cloudera.github.io/navigator/apidocs/v2/path__v2_entities.html
    """
    try:
      params = self.__params

      query_filters = {
        'sourceType': source_type,
        'type': type,
        'originalName': name,
        'deleted': 'false'
      }
      for key, value in filters.items():
        query_filters[key] = value

      filter_query = 'AND'.join('(%s:%s)' % (key, value) for key, value in query_filters.items())

      params += (
        ('query', filter_query),
        ('offset', 0),
        ('limit', 2),  # We are looking for single entity, so limit to 2 to check for multiple results
      )

      response = self._root.get('entities', headers=self.__headers, params=params)

      if len(response) == 0:
        raise NavigatorApiException('Could not find entity with query filters: %s' % str(query_filters))
      elif len(response) > 1:
        raise NavigatorApiException('Found more than 1 entity with query filters: %s' % str(query_filters))

      return response[0]
    except RestException, e:
      raise NavigatorApiException('Failed to find entity: %s' % str(e))


  def get_entity(self, entity_id):
    """
    GET /api/v2/entities/:id
    http://cloudera.github.io/navigator/apidocs/v2/path__v2_entities_-id-.html
    """
    try:
      return self._root.get('entities/%s' % entity_id, headers=self.__headers, params=self.__params)
    except RestException, e:
      raise NavigatorApiException('Failed to get entity %s: %s' % (entity_id, str(e)))


  def update_entity(self, entity_id, **metadata):
    """
    PUT /api/v2/entities/:id
    http://cloudera.github.io/navigator/apidocs/v2/path__v2_entities_-id-.html
    """
    try:
      # TODO: Check permissions of entity
      data = json.dumps(metadata)
      response = self._root.put('entities/%s' % entity_id, params=self.__params, data=data)
      return response
    except RestException, e:
      raise NavigatorApiException('Failed to update entity %s: %s' % (entity_id, str(e)))


  def get_database(self, name):
    return self.find_entity(source_type='HIVE', type='DATABASE', name=name)


  def get_table(self, database_name, table_name):
    parent_path = '\/%s' % database_name
    return self.find_entity(source_type='HIVE', type='TABLE', name=table_name, parentPath=parent_path)


  def get_directory(self, path):
    dir_name, dir_path = self._clean_path(path)
    return self.find_entity(source_type='HDFS', type='DIRECTORY', name=dir_name, fileSystemPath=dir_path)


  def get_file(self, path):
    file_name, file_path = self._clean_path(path)
    return self.find_entity(source_type='HDFS', type='FILE', name=file_name, fileSystemPath=file_path)


  def add_tags(self, entity_id, tags):
    entity = self.get_entity(entity_id)
    new_tags = entity['tags'] or []
    new_tags.extend(tags)
    return self.update_entity(entity_id, tags=new_tags)


  # TODO: remove_tags?


  def _clean_path(self, path):
    return path.rstrip('/').split('/')[-1], self._escape_slashes(path.rstrip('/'))


  def _escape_slashes(self, s):
    return s.replace('/', '\/')
