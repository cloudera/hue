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

from itertools import islice

from django.core.cache import cache
from django.utils.translation import ugettext as _

from desktop.lib.rest import resource
from desktop.lib.rest.unsecure_http_client import UnsecureHttpClient
from desktop.lib.rest.http_client import RestException

from hadoop.conf import HDFS_CLUSTERS
from libsentry.privilege_checker import get_checker
from libsentry.sentry_site import get_hive_sentry_provider

from metadata.conf import NAVIGATOR, get_navigator_auth_password, get_navigator_auth_username
from metadata.catalog.base import CatalogAuthException, CatalogApiException, CatalogEntityDoesNotExistException, Api
from metadata.metadata_sites import get_navigator_hue_server_name

LOG = logging.getLogger(__name__)
VERSION = 'v9'
_JSON_CONTENT_TYPE = 'application/json'
CLUSTER_SOURCE_IDS_CACHE_KEY = 'nav-cluster-source-ids-id'

_HAS_CATALOG_NAMESPACE = None


def get_cluster_source_ids(api):
  '''
  ClusterName is handled by getting the list of sourceIds of a Cluster. We can't filter directly on a clusterName.
  '''
  cluster_source_ids = cache.get(CLUSTER_SOURCE_IDS_CACHE_KEY)

  if cluster_source_ids is None:
    cluster_source_ids = ''
    if get_navigator_hue_server_name():
      sources = api.get_cluster_source_ids()
      LOG.info('Navigator cluster source ids: %s' % (sources,))
      if sources:
        # Sometimes sourceId seems to be missing
        source_ids = ['sourceId:%s' % (_id.get('sourceId') or _id.get('identity')) for _id in sources]
        cluster_source_ids = '(' + ' OR '.join(source_ids) + ') AND '
      else:
        # 0 means always false
        cluster_source_ids = 'sourceId:0 AND'
    cache.set(CLUSTER_SOURCE_IDS_CACHE_KEY, cluster_source_ids, 60 * 60 * 12) # 1/2 Day

  return cluster_source_ids


def get_filesystem_host():
  host = None
  hadoop_fs = HDFS_CLUSTERS['default'].FS_DEFAULTFS.get()
  match = re.search(r"^hdfs://(?P<host>[a-z0-9\.-]+):\d[4]", hadoop_fs)
  if match:
    host = match.group('host')
  return host


class NavigatorApi(Api):
  """
  http://cloudera.github.io/navigator/apidocs/v3/index.html
  """
  DEFAULT_SEARCH_FIELDS = (('originalName', 3), ('originalDescription', 1), ('name', 10), ('description', 3), ('tags', 5))
  CATALOG_NAMESPACE = '__cloudera_internal_catalog_hue'

  def __init__(self, user=None):
    super(NavigatorApi, self).__init__(user)

    self._api_url = '%s/%s' % (NAVIGATOR.API_URL.get().strip('/'), VERSION)
    self._username = get_navigator_auth_username()
    self._password = get_navigator_auth_password()

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
        'limit': NAVIGATOR.FETCH_SIZE_SEARCH_INTERACTIVE.get(),
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

      query_s = query_s.replace('tag:', 'tags:').replace('classification:', 'tags:')

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

      source_ids = get_cluster_source_ids(self)
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
      response = self._root.post('interactive/entities?limit=%(limit)s&offset=%(offset)s' % pagination, data=data, contenttype=_JSON_CONTENT_TYPE, clear_cookies=True)

      response['results'] = list(islice(self._secure_results(response['results']), limit)) # Apply Sentry perms

      return response
    except RestException, e:
      LOG.error('Failed to search for entities with search query: %s' % json.dumps(body))
      if e.code == 401:
        raise CatalogAuthException(_('Failed to authenticate.'))
      else:
        raise CatalogApiException(e.message)



  def search_entities(self, query_s, limit=100, offset=0, raw_query=False, **filters):
    """
    Solr edismax query parser syntax.

    :param query_s: a query string of search terms (e.g. - sales quarterly);
      Currently the search will perform an OR boolean search for all terms (split on whitespace), against a whitelist of search_fields.
    """
    sources = filters.get('sources', [])
    default_entity_types, entity_types = self._get_types_from_sources(sources)

    try:
      params = self.__params
      if not raw_query:
        query_s = query_s.replace('{', '\\{').replace('}', '\\}').replace('(', '\\(').replace(')', '\\)').replace('[', '\\[').replace(']', '\\]')

        search_terms = [term for term in query_s.strip().split()]

        query_clauses = []
        user_filters = []
        source_type_filter = []

        for term in search_terms:
          if ':' not in term:
            if ('sql' in sources or 'hive' in sources or 'impala' in sources):
              if '.' in term:
                parent, term = term.rsplit('.', 1)
                user_filters.append('parentPath:"/%s"' % parent.replace('.', '/'))
            query_clauses.append(self._get_boosted_term(term))
          else:
            name, val = term.split(':')
            if val:
              if name == 'type':
                term = '%s:%s' % (name, val.upper().strip('*'))
                default_entity_types = entity_types # Make sure type value still makes sense for the source
              user_filters.append(term + '*') # Manual filter allowed e.g. type:VIE* ca

        filter_query = '*'

        if query_clauses:
          filter_query = 'OR'.join(['(%s)' % clause for clause in query_clauses])

        user_filter_clause = 'AND '.join(['(%s)' % f for f in user_filters]) or '*'
        source_filter_clause = 'OR'.join(['(%s:%s)' % ('type', entity_type) for entity_type in default_entity_types])

        if 's3' in sources:
          source_type_filter.append('sourceType:s3')
        elif 'sql' in sources or 'hive' in sources or 'impala' in sources:
          source_type_filter.append('sourceType:HIVE OR sourceType:IMPALA')

        filter_query = '%s AND (%s) AND (%s)' % (filter_query, user_filter_clause, source_filter_clause)
        if source_type_filter:
          filter_query += ' AND (%s)' % 'OR '.join(source_type_filter)

        source_ids = get_cluster_source_ids(self)
        if source_ids:
          filter_query = source_ids + '(' + filter_query + ')'
      else:
        filter_query = query_s

      params += (
        ('query', filter_query),
        ('offset', offset),
        ('limit', NAVIGATOR.FETCH_SIZE_SEARCH.get()),
      )

      LOG.info(params)
      response = self._root.get('entities', headers=self.__headers, params=params)

      response = list(islice(self._secure_results(response), limit)) # Apply Sentry perms

      return response
    except RestException, e:
      LOG.error('Failed to search for entities with search query: %s' % query_s)
      if e.code == 401:
        raise CatalogAuthException(_('Failed to authenticate.'))
      else:
        raise CatalogApiException(e)


  def _secure_results(self, results, checker=None):
    # TODO: to move directly to Catalog API
    if NAVIGATOR.APPLY_SENTRY_PERMISSIONS.get():
      checker = get_checker(self.user, checker)
      action = 'SELECT'

      def getkey(result):
        key = {u'server': get_hive_sentry_provider()}

        if result['type'] == 'TABLE' or result['type'] == 'VIEW':
          key['db'] = result.get('parentPath', '') and result.get('parentPath', '').strip('/')
          key['table'] = result.get('originalName', '')
        elif result['type'] == 'DATABASE':
          key['db'] = result.get('originalName', '')
        elif result['type'] == 'FIELD':
          parents = result.get('parentPath', '').strip('/').split('/')
          if len(parents) == 2:
            key['db'], key['table'] = parents
            key['column'] = result.get('originalName', '')

        return key

      return checker.filter_objects(results, action, key=getkey)
    else:
      return results


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

      source_ids = get_cluster_source_ids(self)
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
    params = (
      ('query', 'clusterName:"%s"' % get_navigator_hue_server_name()),
      ('limit', 200),
    )

    LOG.info(params)
    return self._root.get('entities', headers=self.__headers, params=params)


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
      response = self.get_namespace(namespace=NavigatorApi.CATALOG_NAMESPACE)
      if not response:
        self.create_namespace(namespace=NavigatorApi.CATALOG_NAMESPACE, description="Set of fields to augment the data catalog")

      properties = self.get_namespace_properties(namespace=NavigatorApi.CATALOG_NAMESPACE)

      if not [_property for _property in properties if _property['name'] == 'relatedDocuments']:
        self.create_namespace_property(namespace=NavigatorApi.CATALOG_NAMESPACE, properties={
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
             "namespace": NavigatorApi.CATALOG_NAMESPACE,
             "name": "relatedDocuments"
          }])

      _HAS_CATALOG_NAMESPACE = True


  def _get_boosted_term(self, term):
    return 'AND'.join([
      '(%s)' % 'OR'.join(['(%s:%s*^%s)' % (field, term, weight) for (field, weight) in NavigatorApi.DEFAULT_SEARCH_FIELDS]),  # Matching fields
      '(%s)' % 'OR'.join(['(%s:[* TO *])' % field for (field, weight) in NavigatorApi.DEFAULT_SEARCH_FIELDS]) # Boost entities with enriched fields
      # Could add certain customProperties and properties
    ])

  def _clean_path(self, path):
    return path.rstrip('/').split('/')[-1], self._escape_slashes(path.rstrip('/'))


  def _escape_slashes(self, s):
    return s.replace('/', '\/')
