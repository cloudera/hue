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
import re

from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest import resource

from hadoop.conf import HDFS_CLUSTERS

from metadata.conf import NAVIGATOR


LOG = logging.getLogger(__name__)
VERSION = 'v9'


def get_filesystem_host():
  host = None
  hadoop_fs = HDFS_CLUSTERS['default'].FS_DEFAULTFS.get()
  match = re.search(r"^hdfs://(?P<host>[a-z0-9\.-]+):\d[4]", hadoop_fs)
  if match:
    host = match.group('host')
  return host


class NavigatorApiException(Exception):
  pass


class NavigatorApi(object):
  """
  http://cloudera.github.io/navigator/apidocs/v3/index.html
  """

  def __init__(self, api_url=None, user=None, password=None):
    self._api_url = '%s/%s' % ((api_url or NAVIGATOR.API_URL.get()).strip('/'), VERSION)
    self._username = user or NAVIGATOR.AUTH_USERNAME.get()
    self._password = password or NAVIGATOR.AUTH_PASSWORD.get()

    self._client = HttpClient(self._api_url, logger=LOG)
    self._client.set_basic_auth(self._username, self._password)
    self._root = resource.Resource(self._client)

    self.__headers = {}
    self.__params = ()


  def search_entities(self, query_s, limit=100, offset=0, **filters):
    """
    GET /api/v3/entities?query=()
    http://cloudera.github.io/navigator/apidocs/v3/path__v3_entities.html
    :param query_s: a query string of search terms (e.g. - sales quarterly);
      Currently the search will perform an OR boolean search for all terms (split on whitespace), against a whitelist
      of search_fields.
      TODO: support smarter boolean searching with arbitrary ordering and precedence of conditionals
    :param filters: TODO: IMPLEMENT ME, required to support property search
    """
    search_fields = ('originalName', 'originalDescription', 'name', 'description', 'tags')
    entity_types = ('DATABASE', 'TABLE', 'PARTITION', 'FIELD', 'FILE', 'OPERATION')

    sources = filters.get('sources', [])

    if 'hive' in sources or 'impala' in sources:
      entity_types = ('DATABASE', 'TABLE', 'PARTITION', 'FIELD')

    try:
      params = self.__params

      search_terms = [term.lower() for term in query_s.strip().split()]

      query_clauses = []
      for term in search_terms:
        query_clauses.append('OR'.join(['(%s:*%s*)' % (field, term) for field in search_fields]))

      filter_query = '(originalName:*.*)'
      if search_terms:
        filter_query = 'OR'.join(['(%s)' % clause for clause in query_clauses])

      type_filter_clause = 'OR'.join(['(%s:%s)' % ('type', entity_type) for entity_type in entity_types])
      filter_query = '%sAND(%s)' % (filter_query, type_filter_clause)

      params += (
        ('query', filter_query),
        ('offset', offset),
        ('limit', limit),
      )

      response = self._root.get('entities', headers=self.__headers, params=params)

      return response
    except RestException, e:
      msg = 'Failed to search for entities with search query: %s' % query_s
      LOG.exception(msg)
      raise NavigatorApiException(msg)


  def find_entity(self, source_type, type, name, **filters):
    """
    GET /api/v3/entities?query=((sourceType:<source_type>)AND(type:<type>)AND(originalName:<name>))
    http://cloudera.github.io/navigator/apidocs/v3/path__v3_entities.html
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

      # TODO: Uncomment following block after demo, b/c we really want the entities that current Hue knows about in HDFS
      # hadoop_fs = get_filesystem_host()
      hadoop_fs = re.search(r"^(http|https)://(?P<host>[a-z0-9\.-]+):.*", self._api_url).group('host')
      if hadoop_fs:
        query_filters['fileSystemPath'] = '*%(path)s*' % {'path': hadoop_fs}

      filter_query = 'AND'.join('(%s:%s)' % (key, value) for key, value in query_filters.items())

      params += (
        ('query', filter_query),
        ('offset', 0),
        ('limit', 2),  # We are looking for single entity, so limit to 2 to check for multiple results
      )

      response = self._root.get('entities', headers=self.__headers, params=params)

      if not response:
        raise NavigatorApiException('Could not find entity with query filters: %s' % str(query_filters))
      elif len(response) > 1:
        raise NavigatorApiException('Found more than 1 entity with query filters: %s' % str(query_filters))

      return response[0]
    except RestException, e:
      msg = 'Failed to find entity: %s' % str(e)
      LOG.exception(msg)
      raise NavigatorApiException(msg)


  def get_entity(self, entity_id):
    """
    GET /api/v3/entities/:id
    http://cloudera.github.io/navigator/apidocs/v3/path__v3_entities_-id-.html
    """
    try:
      return self._root.get('entities/%s' % entity_id, headers=self.__headers, params=self.__params)
    except RestException, e:
      msg = 'Failed to get entity %s: %s' % (entity_id, str(e))
      LOG.exception(msg)
      raise NavigatorApiException(msg)


  def update_entity(self, entity_id, **metadata):
    """
    PUT /api/v3/entities/:id
    http://cloudera.github.io/navigator/apidocs/v3/path__v3_entities_-id-.html
    """
    try:
      # TODO: Check permissions of entity
      data = json.dumps(metadata)
      return self._root.put('entities/%s' % entity_id, params=self.__params, data=data, allow_redirects=True,
                            clear_cookies=True)
    except RestException, e:
      msg = 'Failed to update entity %s: %s' % (entity_id, str(e))
      LOG.exception(msg)
      raise NavigatorApiException(msg)


  def get_database(self, name):
    return self.find_entity(source_type='HIVE', type='DATABASE', name=name)


  def get_table(self, database_name, table_name):
    parent_path = '\/%s' % database_name
    return self.find_entity(source_type='HIVE', type='TABLE', name=table_name, parentPath=parent_path)


  def get_field(self, database_name, table_name, field_name):
    parent_path = '\/%s\/%s' % (database_name, table_name)
    return self.find_entity(source_type='HIVE', type='FIELD', name=field_name, parentPath=parent_path)


  def get_partition(self, database_name, table_name, partition_spec):
    raise NotImplementedError


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


  def delete_tags(self, entity_id, tags):
    entity = self.get_entity(entity_id)
    new_tags = entity['tags'] or []
    for tag in tags:
      if tag in new_tags:
        new_tags.remove(tag)
    return self.update_entity(entity_id, tags=new_tags)


  def update_properties(self, entity_id, properties):
    entity = self.get_entity(entity_id)
    new_props = entity['properties'] or {}
    new_props.update(properties)
    return self.update_entity(entity_id, properties=new_props)


  def delete_properties(self, entity_id, property_keys):
    entity = self.get_entity(entity_id)
    new_props = entity['properties'] or {}
    for key in property_keys:
      if key in new_props:
        del new_props[key]
    return self.update_entity(entity_id, properties=new_props)


  def get_lineage(self, entity_id):
    """
    GET /api/v3/lineage/entityIds=:id
    http://cloudera.github.io/navigator/apidocs/v3/path__v3_lineage.html
    """
    try:
      params = self.__params

      params += (
        ('entityIds', entity_id),
      )

      return self._root.get('lineage', headers=self.__headers, params=params)
    except RestException, e:
      msg = 'Failed to get lineage for entity ID %s: %s' % (entity_id, str(e))
      LOG.exception(msg)
      raise NavigatorApiException(msg)



  def _clean_path(self, path):
    return path.rstrip('/').split('/')[-1], self._escape_slashes(path.rstrip('/'))


  def _escape_slashes(self, s):
    return s.replace('/', '\/')
