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
import urllib

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest import resource
from django.utils.translation import ugettext as _

from search.examples import demo_handler
from search.conf import EMPTY_QUERY, SECURITY_ENABLED


LOG = logging.getLogger(__name__)

DEFAULT_USER = 'hue'


def utf_quoter(what):
  return urllib.quote(unicode(what).encode('utf-8'), safe='~@#$&()*!+=:;,.?/\'')


class SolrApi(object):
  """
  http://wiki.apache.org/solr/CoreAdmin#CoreAdminHandler
  """
  def __init__(self, solr_url, user):
    self._url = solr_url
    self._user = user
    self._client = HttpClient(self._url, logger=LOG)
    self.security_enabled = SECURITY_ENABLED.get()
    if self.security_enabled:
      self._client.set_kerberos_auth()
    self._root = resource.Resource(self._client)

  def _get_params(self):
    if self.security_enabled:
      return (('doAs', self._user ),)
    return (('user.name', DEFAULT_USER), ('doAs', self._user),)

  @classmethod
  def _get_json(cls, response):
    if type(response) != dict:
      # Got 'plain/text' mimetype instead of 'application/json'
      try:
        response = json.loads(response)
      except ValueError, e:
        # Got some null bytes in the response
        LOG.error('%s: %s' % (unicode(e), repr(response)))
        response = json.loads(response.replace('\x00', ''))
    return response

  @demo_handler
  def query(self, solr_query, hue_core):
    try:
      params = self._get_params() + (
          ('q', solr_query['q'] or EMPTY_QUERY.get()),
          ('wt', 'json'),
          ('rows', solr_query['rows']),
          ('start', solr_query['start']),
      )

      params += hue_core.get_query(solr_query)

      fqs = solr_query['fq'].split('|')
      for fq in fqs:
        if fq:
          params += (('fq', urllib.unquote(utf_quoter(fq))),)

      response = self._root.get('%(collection)s/select' % solr_query, params)

      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  #@demo_handler
  def query2(self, solr_query, collection, query):
    
    params = self._get_params() + (
        ('q', query['q'] or EMPTY_QUERY.get()),
        ('wt', 'json'),
        ('rows', solr_query['rows']),
        ('start', solr_query['start']),
    )

    if any(collection['facets']):
      params += (
        ('facet', 'true'),
        ('facet.mincount', 0),
        ('facet.limit', 10),
      )
      for facet in collection['facets']:
        if facet['type'] == 'query':
          params += (('facet.query', '%s' % facet['field']),)
        elif facet['type'] == 'range':
          params += tuple([
             ('facet.range', '{!ex=%s}%s' % (facet['field'], facet['field'])),
             ('f.%s.facet.range.start' % facet['field'], facet['properties']['start']),
             ('f.%s.facet.range.end' % facet['field'], facet['properties']['end']),
             ('f.%s.facet.range.gap' % facet['field'], facet['properties']['gap']),]
          )          
        elif facet['type'] == 'field':
          params += (('facet.field', '{!ex=%s}%s' % (facet['field'], facet['field'])),)

    for fq in query['fqs']:
      params += (('fq', urllib.unquote(utf_quoter('{!tag=%s}{!field f=%s}%s' % (fq['field'], fq['field'], fq['filter'])))),)

    if collection['template']['fieldsSelected'] and collection['template']['isGridLayout']:
      fields = collection['template']['fieldsSelected'] + [collection['idField']] if collection['idField'] else []
      params += (('fl', urllib.unquote(utf_quoter(','.join(fields)))),)
    else:
      params += (('fl', '*'),)

    params += (
      ('hl', 'true'),
      ('hl.fl', '*'),
      ('hl.snippets', 3)
    )

    if collection['template']['fieldsSelected']:
      fields = []
      for field in collection['template']['fieldsSelected']:
        attribute_field = filter(lambda attribute: field == attribute['name'], collection['template']['fieldsAttributes'])
        if attribute_field:
          if attribute_field[0]['sort']['direction']:
            fields.append('%s %s' % (field, attribute_field[0]['sort']['direction']))
      if fields:
        params += (         
          ('sort', ','.join(fields)),
        )

    response = self._root.get('%(collection)s/select' % solr_query, params)

    return self._get_json(response)


  def suggest(self, solr_query, hue_core):
    try:
      params = self._get_params() + (
          ('q', solr_query['q']),
          ('wt', 'json'),
      )
      response = self._root.get('%(collection)s/suggest' % solr_query, params)
      if type(response) != dict:
        response = json.loads(response)
      return response
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def collections(self):
    try:
      params = self._get_params() + (
          ('detail', 'true'),
          ('path', '/clusterstate.json'),
      )
      response = self._root.get('zookeeper', params=params)
      return json.loads(response['znode']['data'])
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def collection_or_core(self, hue_collection):
    if hue_collection.is_core_only:
      return self.core(hue_collection.name)
    else:
      return self.collection(hue_collection.name)

  def collection(self, name):
    try:
      collections = self.collections()
      return collections[name]
    except Exception, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def cores(self):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
      )
      return self._root.get('admin/cores', params=params)['status']
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def core(self, core):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
          ('core', core),
      )
      return self._root.get('admin/cores', params=params)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def schema(self, core):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
          ('file', 'schema.xml'),
      )
      return self._root.get('%(core)s/admin/file' % {'core': core}, params=params)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def fields(self, core, dynamic=False):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
          ('fl', '*'),
      )
      if not dynamic:
        params += (('show', 'schema'),)
      response = self._root.get('%(core)s/admin/luke' % {'core': core}, params=params)
      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def luke(self, core):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
      )
      response = self._root.get('%(core)s/admin/luke' % {'core': core}, params=params)
      return self._get_json(response)    
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def schema_fields(self, core):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
      )
      response = self._root.get('%(core)s/schema/fields' % {'core': core}, params=params)
      return self._get_json(response)    
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))
    
  def stats(self, core, fields):
    try:
      params = (
          ('q', EMPTY_QUERY.get()),
          ('wt', 'json'),
          ('rows', 0),
          ('stats', 'true'),
      )      
      params += tuple([('stats.field', field) for field in fields])
      response = self._root.get('%(core)s/select' % {'core': core}, params=params)
      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))
    