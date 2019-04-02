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

from metadata.conf import CATALOG, get_catalog_auth_password, get_catalog_auth_username
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
    self._username = get_catalog_auth_username()
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


  def search_entities_interactive(self, query_s=None, limit=100, offset=0, facetFields=None, facetPrefix=None, facetRanges=None, filterQueries=None, firstClassEntitiesOnly=None, sources=None):
    try:
      pagination = {
        'offset': offset,
        'limit': CATALOG.FETCH_SIZE_SEARCH_INTERACTIVE.get(),
      }

      f = {
          "outputFormat" : {
            "type" : "dynamic"
          },
          "name" : {
            "type" : "dynamic"
          },
          "lastModified" : {
            "type" : "date"
          },
          "sourceType" : {
            "type" : "dynamic"
          },
          "parentPath" : {
            "type" : "dynamic"
          },
          "lastAccessed" : {
            "type" : "date"
          },
          "type" : {
            "type" : "dynamic"
          },
          "sourceId" : {
            "type" : "dynamic"
          },
          "partitionColNames" : {
            "type" : "dynamic"
          },
          "serDeName" : {
            "type" : "dynamic"
          },
          "created" : {
            "type" : "date"
          },
          "fileSystemPath" : {
            "type" : "dynamic"
          },
          "compressed" : {
            "type" : "bool"
          },
          "clusteredByColNames" : {
            "type" : "dynamic"
          },
          "originalName" : {
            "type" : "dynamic"
          },
          "owner" : {
            "type" : "dynamic"
          },
          "extractorRunId" : {
            "type" : "dynamic"
          },
          "userEntity" : {
            "type" : "bool"
          },
          "sortByColNames" : {
            "type" : "dynamic"
          },
          "inputFormat" : {
            "type" : "dynamic"
          },
          "serDeLibName" : {
            "type" : "dynamic"
          },
          "originalDescription" : {
            "type" : "dynamic"
          },
          "lastModifiedBy" : {
            "type" : "dynamic"
          }
        }

      auto_field_facets = ["tags", "type"] + f.keys()
      query_s = (query_s.strip() if query_s else '') + '*'

      last_query_term = [term for term in query_s.split()][-1]

      if last_query_term and last_query_term != '*':
        last_query_term = last_query_term.rstrip('*')
        (fname, fval) = last_query_term.split(':') if ':' in last_query_term else (last_query_term, '')
        auto_field_facets = [f for f in auto_field_facets if f.startswith(fname)]

      facetFields = facetFields or auto_field_facets[:5]

      entity_types = []
      fq_type = []
      if filterQueries is None:
        filterQueries = []

      if sources:
        default_entity_types, entity_types = self._get_types_from_sources(sources)

        if 'sql' in sources or 'hive' in sources or 'impala' in sources:
          fq_type = default_entity_types
          filterQueries.append('sourceType:HIVE OR sourceType:IMPALA')
        elif 'hdfs' in sources:
          fq_type = entity_types
        elif 's3' in sources:
          fq_type = default_entity_types
          filterQueries.append('sourceType:s3')

        if query_s.strip().endswith('type:*'): # To list all available types
          fq_type = entity_types

      search_terms = [term for term in query_s.strip().split()] if query_s else []
      query = []
      for term in search_terms:
        if ':' not in term:
          query.append(self._get_boosted_term(term))
        else:
          name, val = term.split(':')
          if val: # Allow to type non default types, e.g for SQL: type:FIEL*
            if name == 'type': # Make sure type value still makes sense for the source
              term = '%s:%s' % (name, val.upper())
              fq_type = entity_types
            if name.lower() not in ['type', 'tags', 'owner', 'originalname', 'originaldescription', 'lastmodifiedby']:
              # User Defined Properties are prefixed with 'up_', i.e. "department:sales" -> "up_department:sales"
              query.append('up_' + term)
            else:
              filterQueries.append(term)

      filterQueries.append('deleted:false')

      body = {'query': ' '.join(query) or '*'}
      if fq_type:
        filterQueries += ['{!tag=type} %s' % ' OR '.join(['type:%s' % fq for fq in fq_type])]

      source_ids = self.get_cluster_source_ids()
      if source_ids:
        body['query'] = source_ids + '(' + body['query'] + ')'

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

      response = self._root.get('/search/basic?typeName=hbase_table') #?limit=%(limit)s&offset=%(offset)s' % pagination)
      response['results'] = [self._massage_entity(entity) for entity in response.pop('entities')]

      return response
    except RestException, e:
      print(e)
      LOG.error('Failed to search for entities with search query: %s' % json.dumps(body))
      if e.code == 401:
        raise CatalogAuthException(_('Failed to authenticate.'))
      else:
        raise CatalogApiException(e.message)

  def _massage_entity(self, entity):
    return {
        "name": entity['attributes'].get('name', entity['attributes'].get('qualifiedName')),
        "description": entity['attributes'].get('description'),
         "owner": entity.get('owner'),
         "sourceType": entity['typeName'],
         "partColNames":[
            # "date"
         ],
         "type": "TABLE", # TODO
         "internalType": entity['typeName'],
         "status": entity['status'], # Specific to Atlas
         "tags": entity['classificationNames'],
         "classificationNames": entity['classificationNames'], # Specific to Atlas
         "meaningNames": entity['meaningNames'], # Specific to Atlas
         "meanings": entity['meanings'], # [{"displayText":"Stock","confidence":0, "termGuid":"32892437-931b-43d3-9aad-400f7f8d2a73","relationGuid":"e8856c09-a3a1-4a85-b841-709b30f93923"}] # Specific to Atlas
         "originalDescription": None,
         "customProperties": None,
         "properties":{
         },
         "identity": entity['guid'],
         "created": entity['attributes']['createTime'], #"2019-03-28T19:30:30.000Z",
         "parentPath": "/default",
         "originalName": entity['attributes']['qualifiedName'],
        #  "lastAccessed":"1970-01-01T00:00:00.000Z"
        #  "clusteredByColNames":null,
        #  "outputFormat":"org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
        #  "firstClassParentId":null,
        #  "extractorRunId":"7##1",
        #  "sourceId":"7",
        #  "lastModified":null,
        #  "packageName":"nav",
        #  "compressed":false,
        #  "metaClassName":"hv_table"
        #  "deleted":false,
        #  "technicalProperties":null,
        #  "userEntity":false,
        #  "serdeProps":null,
        #  "serdeLibName":"org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
        #  "lastModifiedBy":null,
        #  "selectionName":"web_logs",
        #  "sortByColNames":null,
        #  "inputFormat":"org.apache.hadoop.mapred.TextInputFormat",
        #  "serdeName":null,
        #  "deleteTime":null,
        #  "fileSystemPath":"hdfs://self-service-dw-1.gce.cloudera.com:8020/user/hive/warehouse/web_logs",
      }

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
