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

from django.core.cache import cache
from django.utils.translation import ugettext as _

from desktop.lib.rest import resource
from desktop.lib.rest.unsecure_http_client import UnsecureHttpClient
from desktop.lib.rest.http_client import RestException

from metadata.conf import CATALOG, get_catalog_auth_password
from metadata.catalog.base import CatalogAuthException, CatalogApiException, CatalogEntityDoesNotExistException, Api

LOG = logging.getLogger(__name__)

_HAS_CATALOG_NAMESPACE = None
_JSON_CONTENT_TYPE = 'application/json'


class AtlasApi(Api):
  """
  https://atlas.apache.org
  """
  DEFAULT_SEARCH_FIELDS = (('originalName', 3), ('originalDescription', 1), ('name', 10), ('description', 3), ('tags', 5))
  CATALOG_NAMESPACE = '__cloudera_internal_catalog_hue'

  def __init__(self, user=None):
    super(AtlasApi, self).__init__(user)

    self._api_url = CATALOG.API_URL.get().strip('/')
    self._username = CATALOG.SERVER_USER.get()
    self._password = get_catalog_auth_password()

    # Navigator does not support Kerberos authentication while other components usually requires it
    self._client = UnsecureHttpClient(self._api_url, logger=LOG)
    self._client.set_basic_auth(self._username, self._password)
    self._root = resource.Resource(self._client, urlencode=False) # For search_entities_interactive

    self.__headers = {}
    self.__params = ()

    #self._fillup_properties() # Disabled currently


  def _get_types_from_sources(self, sources):
    default_entity_types = entity_types = ('DATABASE', 'TABLE', 'PARTITION', 'FIELD', 'FILE', 'VIEW', 'S3BUCKET', 'OPERATION', 'DIRECTORY')

    if 'sql' in sources or 'hive' in sources or 'impala' in sources:
      entity_types = ('TABLE', 'VIEW', 'DATABASE', 'PARTITION', 'FIELD')
      default_entity_types = ('TABLE', 'VIEW')
    elif 'hdfs' in sources:
      entity_types = ('FILE', 'DIRECTORY')
      default_entity_types  = ('FILE', 'DIRECTORY')
    elif 's3' in sources:
      entity_types = ('FILE', 'DIRECTORY', 'S3BUCKET')
      default_entity_types  = ('DIRECTORY', 'S3BUCKET')

    return default_entity_types, entity_types

  def adapt_atlas_entity_to_navigator(self, atlas_entity):
    nav_entity = {
      "created": 'createTime' in atlas_entity['attributes'] and atlas_entity['attributes']['createTime'],
      "customProperties": None,
      "description": atlas_entity['attributes'].get('description'),
      "identity": atlas_entity['guid'],
      "internalType": atlas_entity['typeName'],
      "meaningNames": atlas_entity['meaningNames'], # Atlas specific
      "meanings": atlas_entity['meanings'], # Atlas specific
      "name": atlas_entity['attributes'].get('name'),
      "original_name": atlas_entity['attributes'].get('name'),
      "originalDescription": None,
      "originalName": atlas_entity['attributes'].get('name'),
      "owner": atlas_entity.get('owner'),
      "parentPath": '', # Set below
      "properties": {}, # Set below
      "sourceType": '', # Set below
      "tags": atlas_entity['classificationNames'],
      "type": atlas_entity['typeName'].lower().replace("hive_", "").replace("column", "field").upper()
    }

    if atlas_entity['typeName'].lower().startswith('hive_'):
      nav_entity['sourceType'] = 'HIVE'
      qualified_path_parts = re.sub(r'@.*$', '', atlas_entity['attributes'].get('qualifiedName')).split('.')
      qualified_path_parts.pop()
      nav_entity['parentPath'] = '/' + '/'.join(qualified_path_parts)

    if 'classifications' in atlas_entity:
      for atlas_classification in atlas_entity['classifications']:
        if 'attributes' in atlas_classification:
          for key, value in atlas_classification['attributes'].iteritems():
            nav_entity['properties'][key] = value

    return nav_entity

  def search_entities_interactive(self, query_s=None, limit=100, offset=0, facetFields=None, facetPrefix=None, facetRanges=None, filterQueries=None, firstClassEntitiesOnly=None, sources=None):
    try:
      response = {
        "status": 0,
        "results": [],
        "facets": {
          "tags": {}
        }
      }

      # list_tags should return empty response for Atlas
      if (not query_s and facetFields and 'tags' in facetFields):
        return response

      query_s = (query_s.strip() if query_s else '') + '*'
      atlas_dsl_query = 'from %s where name like \'%s\' limit %s' % ('hive_table', query_s, limit)

      atlas_response = self._root.get('/v2/search/dsl?query=%s' % atlas_dsl_query)

      if 'entities' in atlas_response:
        for atlas_entity in atlas_response['entities']:
          response['results'].append(self.adapt_atlas_entity_to_navigator(atlas_entity))

      return response
    except RestException, e:
      print(e)
      LOG.error('Failed to search for entities with search query: %s' % atlas_dsl_query)
      if e.code == 401:
        raise CatalogAuthException(_('Failed to authenticate.'))
      else:
        raise CatalogApiException(e.message)

  def search_entities(self, query_s, limit=100, offset=0, raw_query=False, **filters):
    pass


  def suggest(self, prefix=None):
    try:
      return self._root.get('interactive/suggestions?query=%s' % (prefix or '*'))
    except RestException, e:
      msg = 'Failed to search for entities with search query: %s' % prefix
      LOG.error(msg)
      raise CatalogApiException(e.message)


  def find_entity(self, source_type, type, name, **filters):
    """
    GET /api/v3/entities?query=((sourceType:<source_type>)AND(type:<type>)AND(originalName:<name>))
    http://cloudera.github.io/navigator/apidocs/v3/path__v3_entities.html
    """
    try:
      params = self.__params

      query_filters = {
        'sourceType': source_type,
        'originalName': name,
        'deleted': 'false'
      }

      for key, value in filters.items():
        query_filters[key] = value

      filter_query = 'AND'.join('(%s:%s)' % (key, value) for key, value in query_filters.items())
      filter_query = '%(type)s AND %(filter_query)s' % {
        'type': '(type:%s)' % 'TABLE OR type:VIEW' if type == 'TABLE' else type, # Impala does not always say that a table is actually a view
        'filter_query': filter_query
      }

      source_ids = self.get_cluster_source_ids()
      if source_ids:
        filter_query = source_ids + '(' + filter_query + ')'

      params += (
        ('query', filter_query),
        ('offset', 0),
        ('limit', 2),  # We are looking for single entity, so limit to 2 to check for multiple results
      )

      response = self._root.get('entities', headers=self.__headers, params=params)

      if not response:
        raise CatalogEntityDoesNotExistException('Could not find entity with query filters: %s' % str(query_filters))
      elif len(response) > 1:
        raise CatalogApiException('Found more than 1 entity with query filters: %s' % str(query_filters))

      return response[0]
    except RestException, e:
      msg = 'Failed to find entity: %s' % str(e)
      LOG.error(msg)
      raise CatalogApiException(e.message)


  def get_entity(self, entity_id):
    """
    GET /api/v3/entities/:id
    http://cloudera.github.io/navigator/apidocs/v3/path__v3_entities_-id-.html
    """
    try:
      return self._root.get('entities/%s' % entity_id, headers=self.__headers, params=self.__params)
    except RestException, e:
      msg = 'Failed to get entity %s: %s' % (entity_id, str(e))
      LOG.error(msg)
      raise CatalogApiException(e.message)


  def update_entity(self, entity, **metadata):
    """
    PUT /api/v3/entities/:id
    http://cloudera.github.io/navigator/apidocs/v3/path__v3_entities_-id-.html
    """
    try:
      # Workarounds NAV-6187: if we don't re-send those, they would get erased.
      properties = {
        'name': entity['name'],
        'description': entity['description'],
        'properties': entity['properties'] or {},
        'customProperties': entity['customProperties'] or {}
      }
      properties.update(metadata)
      data = json.dumps(properties)

      return self._root.put('entities/%(identity)s' % entity, params=self.__params, data=data, contenttype=_JSON_CONTENT_TYPE, allow_redirects=True, clear_cookies=True)
    except RestException, e:
      msg = 'Failed to update entity %s: %s' % (entity['identity'], e)
      LOG.error(msg)
      raise CatalogApiException(e.message)


  def get_cluster_source_ids(self):
    return []
    # params = (
    #   ('query', 'clusterName:"%s"' % get_navigator_hue_server_name()),
    #   ('limit', 200),
    # )

    # LOG.info(params)
    # return self._root.get('entities', headers=self.__headers, params=params)


  def add_tags(self, entity_id, tags):
    entity = self.get_entity(entity_id)
    new_tags = entity['tags'] or []
    new_tags.extend(tags)
    return self.update_entity(entity, tags=new_tags)


  def delete_tags(self, entity_id, tags):
    entity = self.get_entity(entity_id)
    new_tags = entity['tags'] or []
    for tag in tags:
      if tag in new_tags:
        new_tags.remove(tag)
    return self.update_entity(entity, tags=new_tags)


  def update_properties(self, entity_id, properties, modified_custom_metadata=None, deleted_custom_metadata_keys=None):
    entity = self.get_entity(entity_id)

    if modified_custom_metadata:
      properties['properties'] = entity['properties'] or {}
      properties['properties'].update(modified_custom_metadata)
    if deleted_custom_metadata_keys:
      properties['properties'] = entity['properties'] or {}
      for key in deleted_custom_metadata_keys:
        if key in properties['properties']:
          del properties['properties'][key]
    return self.update_entity(entity, **properties)


  def delete_metadata_properties(self, entity_id, property_keys):
    entity = self.get_entity(entity_id)
    new_props = entity['properties'] or {}
    for key in property_keys:
      if key in new_props:
        del new_props[key]
    return self.update_entity(entity, properties=new_props)


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
      LOG.error(msg)
      raise CatalogApiException(e.message)


  def create_namespace(self, namespace, description=None):
    try:
      data = json.dumps({'name': namespace, 'description': description})
      return self._root.post('models/namespaces/', data=data, contenttype=_JSON_CONTENT_TYPE, clear_cookies=True)
    except RestException, e:
      msg = 'Failed to create namespace: %s' % namespace
      LOG.error(msg)
      raise CatalogApiException(e.message)


  def get_namespace(self, namespace):
    try:
      return self._root.get('models/namespaces/%(namespace)s' % {'namespace': namespace})
    except RestException, e:
      msg = 'Failed to get namespace: %s' % namespace
      LOG.error(msg)
      raise CatalogApiException(e.message)


  def create_namespace_property(self, namespace, properties):
    try:
      data = json.dumps(properties)
      return self._root.post('models/namespaces/%(namespace)s/properties' % {'namespace': namespace}, data=data, contenttype=_JSON_CONTENT_TYPE, clear_cookies=True)
    except RestException, e:
      msg = 'Failed to create namespace %s property' % namespace
      LOG.error(msg)
      raise CatalogApiException(e.message)


  def get_namespace_properties(self, namespace):
    try:
      return self._root.get('models/namespaces/%(namespace)s/properties' % {'namespace': namespace})
    except RestException, e:
      msg = 'Failed to create namespace %s property' % namespace
      LOG.error(msg)
      raise CatalogApiException(e.message)


  def map_namespace_property(self, clazz, properties):
    try:
      data = json.dumps(properties)
      return self._root.post('models/packages/nav/classes/%(class)s/properties' % {'class': clazz}, data=data, contenttype=_JSON_CONTENT_TYPE, clear_cookies=True)
    except RestException, e:
      msg = 'Failed to map class %s property' % clazz
      LOG.error(msg)
      raise CatalogApiException(e.message)


  def get_model_properties_mapping(self):
    try:
      return self._root.get('models/properties/mappings')
    except RestException, e:
      msg = 'Failed to get models properties mappings'
      LOG.error(msg)
      raise CatalogApiException(e.message)


  def _fillup_properties(self):
    global _HAS_CATALOG_NAMESPACE

    if _HAS_CATALOG_NAMESPACE is None:
      response = self.get_namespace(namespace=AtlasApi.CATALOG_NAMESPACE)
      if not response:
        self.create_namespace(namespace=AtlasApi.CATALOG_NAMESPACE, description="Set of fields to augment the data catalog")

      properties = self.get_namespace_properties(namespace=AtlasApi.CATALOG_NAMESPACE)

      if not [_property for _property in properties if _property['name'] == 'relatedDocuments']:
        self.create_namespace_property(namespace=AtlasApi.CATALOG_NAMESPACE, properties={
          "name": "relatedDocuments",
          "displayName": "Related documents",
          "description": "List of Hue document UUIDs related to this entity",
          "multiValued": True,
          "maxLength": 36,
          "pattern": ".*", # UUID
          "enumValues": None,
          "type": "TEXT"
         })

        # Might want to check if the mapping is already done
        for clazz in ('hv_table', 'hv_view'):
          self.map_namespace_property(clazz, properties=[{
             "namespace": AtlasApi.CATALOG_NAMESPACE,
             "name": "relatedDocuments"
          }])

      _HAS_CATALOG_NAMESPACE = True


  def _get_boosted_term(self, term):
    return 'AND'.join([
      '(%s)' % 'OR'.join(['(%s:%s*^%s)' % (field, term, weight) for (field, weight) in AtlasApi.DEFAULT_SEARCH_FIELDS]),  # Matching fields
      '(%s)' % 'OR'.join(['(%s:[* TO *])' % field for (field, weight) in AtlasApi.DEFAULT_SEARCH_FIELDS]) # Boost entities with enriched fields
      # Could add certain customProperties and properties
    ])

  def _clean_path(self, path):
    return path.rstrip('/').split('/')[-1], self._escape_slashes(path.rstrip('/'))


  def _escape_slashes(self, s):
    return s.replace('/', '\/')
