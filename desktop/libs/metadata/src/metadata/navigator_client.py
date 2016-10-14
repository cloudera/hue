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

from desktop.lib.rest import resource
from desktop.lib.rest.http_client import HttpClient, RestException

from hadoop.conf import HDFS_CLUSTERS

from metadata.conf import NAVIGATOR


_JSON_CONTENT_TYPE = 'application/json'
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
    self._root = resource.Resource(self._client, urlencode=False) # For search_entities_interactive

    self.__headers = {}
    self.__params = ()


  def _get_types_from_sources(self, sources):
    default_entity_types = entity_types = ('DATABASE', 'TABLE', 'PARTITION', 'FIELD', 'FILE', 'VIEW', 'OPERATION', 'DIRECTORY')

    if 'sql' in sources or 'hive' in sources or 'impala' in sources:
      default_entity_types = ('TABLE', 'VIEW')
      entity_types = ('TABLE', 'VIEW', 'DATABASE', 'PARTITION', 'FIELD')
    elif 'hdfs' in sources:
      entity_types = ('FILE', 'DIRECTORY')
      default_entity_types  = ('FILE', 'DIRECTORY')

    return default_entity_types, entity_types

  def search_entities(self, query_s, limit=100, offset=0, **filters):
    """
    Solr edismax query parser syntax.

    :param query_s: a query string of search terms (e.g. - sales quarterly);
      Currently the search will perform an OR boolean search for all terms (split on whitespace), against a whitelist
      of search_fields.
      TODO: support smarter boolean searching with arbitrary ordering and precedence of conditionals
    """
    search_fields = ('originalName', 'originalDescription', 'name', 'description', 'tags')

    sources = filters.get('sources', [])
    default_entity_types, entity_types = self._get_types_from_sources(sources)

    try:
      params = self.__params

      search_terms = [term for term in query_s.strip().split()]

      query_clauses = []
      user_filters = []
      for term in search_terms:
        if ':' not in term:
          query_clauses.append('OR'.join(['(%s:*%s*)' % (field, term) for field in search_fields]))
        else:
          name, val = term.split(':')
          if val and (name != 'type' or val in entity_types): # Manual filter allowed
            user_filters.append(term + '*') # e.g. type:VIEW ca

      filter_query = '*'

      if query_clauses:
        filter_query = 'OR'.join(['(%s)' % clause for clause in query_clauses])

      user_filter_clause = 'OR '.join(['(%s)' % f for f in user_filters]) or '*'
      source_filter_clause = 'OR'.join(['(%s:%s)' % ('type', entity_type) for entity_type in default_entity_types])

      filter_query = '%s AND (%s) AND (%s)' % (filter_query, user_filter_clause, source_filter_clause)

      params += (
        ('query', filter_query),
        ('offset', offset),
        ('limit', limit),
      )

      LOG.info(params)
      response = self._root.get('entities', headers=self.__headers, params=params)

      return response
    except RestException, e:
      msg = 'Failed to search for entities with search query: %s' % query_s
      LOG.exception(msg)
      raise NavigatorApiException(msg)


  def search_entities_interactive(self, query_s=None, limit=100, offset=0, facetFields=None, facetPrefix=None, facetRanges=None, filterQueries=None, firstClassEntitiesOnly=None, sources=None):
    try:
      pagination = {
        'offset': offset,
        'limit': limit,
      }

      entity_types = []
      if filterQueries is None:
        filterQueries = []

      if sources:
        default_entity_types, entity_types = self._get_types_from_sources(sources)
        fq_type = []

        if 'hive' in sources or 'impala' in sources:
          fq_type = default_entity_types
        elif 'hdfs' in sources:
          fq_type = entity_types

        filterQueries += ['{!tag=type} %s' % ' OR '.join(['type:%s' % fq for fq in fq_type])]

      search_terms = [term for term in query_s.strip().split()] if query_s else []
      query = []
      for term in search_terms:
        if ':' not in term:
          query.append(term)
        else:
          name, val = term.split(':')
          if val and val != '*' and (name != 'type' or val in entity_types):
            filterQueries.append(term)

      body = {'query': ' '.join(query) or '*'}


      body['facetFields'] = facetFields or [] # Currently mandatory in API
      if facetPrefix:
        body['facetPrefix'] = facetPrefix
      if facetRanges:
        body['facetRanges'] = facetRanges
      if filterQueries:
        body['filterQueries'] = filterQueries
      if firstClassEntitiesOnly:
        body['firstClassEntitiesOnly'] = firstClassEntitiesOnly

      data = json.dumps(body)
      LOG.info(data)
      response = self._root.post('interactive/entities?limit=%(limit)s&offset=%(offset)s' % pagination, data=data, contenttype=_JSON_CONTENT_TYPE)

      return response
    except RestException:
      msg = 'Failed to search for entities with search query %s' % json.dumps(body)
      LOG.exception(msg)
      raise NavigatorApiException(msg)


  def suggest(self, prefix=None):
    try:
      return self._root.get('interactive/suggestions?query=%s' % (prefix or '*'))
    except RestException, e:
      msg = 'Failed to search for entities with search query: %s' % prefix
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
      data = json.dumps(metadata)
      return self._root.put('entities/%s' % entity_id, params=self.__params, data=data, allow_redirects=True, clear_cookies=True)
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
