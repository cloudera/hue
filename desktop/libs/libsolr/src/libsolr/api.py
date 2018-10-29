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
import urllib

from itertools import groupby

from django.utils.translation import ugettext as _

from dashboard.facet_builder import _compute_range_facet
from dashboard.models import Collection2
from desktop.lib.exceptions_renderable import PopupException
from desktop.conf import SERVER_USER
from desktop.lib.i18n import force_unicode
from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest import resource

from libsolr.conf import SSL_CERT_CA_VERIFY


LOG = logging.getLogger(__name__)


try:
  from search.conf import EMPTY_QUERY, SECURITY_ENABLED, SOLR_URL
except ImportError, e:
  LOG.warn('Solr Search is not enabled')


def utf_quoter(what):
  return urllib.quote(unicode(what).encode('utf-8'), safe='~@#$&()*!+=;,.?/\'')


class SolrApi(object):
  """
  http://wiki.apache.org/solr/CoreAdmin#CoreAdminHandler
  """
  def __init__(self, solr_url=None, user=None, security_enabled=False, ssl_cert_ca_verify=SSL_CERT_CA_VERIFY.get()):
    if solr_url is None and hasattr(SOLR_URL, 'get'):
      solr_url = SOLR_URL.get()

    if solr_url:
      self._url = solr_url
      self._user = user
      self._client = HttpClient(self._url, logger=LOG)
      self.security_enabled = security_enabled or SECURITY_ENABLED.get()

      if self.security_enabled:
        self._client.set_kerberos_auth()

      self._client.set_verify(ssl_cert_ca_verify)

      self._root = resource.Resource(self._client)

      # The Kerberos handshake requires two requests in order to authenticate,
      # but if our first request is a PUT/POST, it might flat-out reject the
      # first request if the body is too large. So, connect here in order to get
      # a cookie so future PUT/POSTs will be pre-authenticated.
      if self.security_enabled:
        self._root.invoke('HEAD', '/')


  def query(self, collection, query):
    solr_query = {}

    solr_query['collection'] = collection['name']

    if query.get('download'):
      solr_query['rows'] = 1000
      solr_query['start'] = 0
    else:
      solr_query['rows'] = int(collection['template']['rows'] or 10)
      solr_query['start'] = int(query['start'])

    solr_query['rows'] = min(solr_query['rows'], 1000)
    solr_query['start'] = min(solr_query['start'], 10000)

    params = self._get_params() + (
        ('q', self._get_q(query)),
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
      json_facets = {}

      timeFilter = self._get_range_borders(collection, query)

      for facet in collection['facets']:
        if facet['type'] == 'query':
          params += (('facet.query', '%s' % facet['field']),)
        elif facet['type'] == 'range' or facet['type'] == 'range-up':
          keys = {
              'id': '%(id)s' % facet,
              'field': facet['field'],
              'key': '%(field)s-%(id)s' % facet,
              'start': facet['properties']['start'],
              'end': facet['properties']['end'],
              'gap': facet['properties']['gap'],
              'mincount': int(facet['properties']['mincount'])
          }

          if facet['properties']['canRange'] or timeFilter and timeFilter['time_field'] == facet['field'] and (facet['id'] not in timeFilter['time_filter_overrides'] or facet['widgetType'] != 'histogram-widget'):
            keys.update(self._get_time_filter_query(timeFilter, facet, collection))

          params += (
             ('facet.range', '{!key=%(key)s ex=%(id)s f.%(field)s.facet.range.start=%(start)s f.%(field)s.facet.range.end=%(end)s f.%(field)s.facet.range.gap=%(gap)s f.%(field)s.facet.mincount=%(mincount)s}%(field)s' % keys),
          )
        elif facet['type'] == 'field':
          keys = {
              'id': '%(id)s' % facet,
              'field': facet['field'],
              'key': '%(field)s-%(id)s' % facet,
              'limit': int(facet['properties'].get('limit', 10)) + (1 if facet['widgetType'] == 'facet-widget' else 0),
              'mincount': int(facet['properties']['mincount'])
          }

          params += (
              ('facet.field', '{!key=%(key)s ex=%(id)s f.%(field)s.facet.limit=%(limit)s f.%(field)s.facet.mincount=%(mincount)s}%(field)s' % keys),
          )
        elif facet['type'] == 'nested':
          _f = {}
          if facet['properties']['facets']:
            self._n_facet_dimension(facet, _f, facet['properties']['facets'], 1, timeFilter, collection, can_range = facet['properties']['canRange'])

          if facet['properties'].get('domain'):
            if facet['properties']['domain'].get('blockParent') or facet['properties']['domain'].get('blockChildren'):
              _f['domain'] = {}
              if facet['properties']['domain'].get('blockParent'):
                _f['domain']['blockParent'] = ' OR '.join(facet['properties']['domain']['blockParent'])
              if facet['properties']['domain'].get('blockChildren'):
                _f['domain']['blockChildren'] = ' OR '.join(facet['properties']['domain']['blockChildren'])

          if _f:
            sort = {'count': facet['properties']['facets'][0]['sort']}
            for i, agg in enumerate(self._get_dimension_aggregates(facet['properties']['facets'][1:])):
              if agg['sort'] != 'default':
                agg_function = self._get_aggregate_function(agg)
                sort = {'agg_%02d_%02d:%s' % (1, i, agg_function): agg['sort']}

            if sort.get('count') == 'default':
              sort['count'] = 'desc'

            dim_key = [key for key in _f['facet'].keys() if 'dim' in key][0]
            _f['facet'][dim_key].update({
                  'excludeTags': facet['id'],
                  'offset': 0,
                  'numBuckets': True,
                  'allBuckets': True,
                  'sort': sort
                  #'prefix': '' # Forbidden on numeric fields
              })
            json_facets[facet['id']] = _f['facet'][dim_key]
        elif facet['type'] == 'function':
          if facet['properties']['facets']:
            json_facets[facet['id']] = self._get_aggregate_function(facet['properties']['facets'][0])
            if facet['properties']['compare']['is_enabled']:
              # TODO: global compare override
              unit = re.split('\d+', facet['properties']['compare']['gap'])[1]
              json_facets[facet['id']] = {
                'type': 'range',
                'field': collection['timeFilter'].get('field'),
                'start': 'NOW/%s-%s-%s' % (unit, facet['properties']['compare']['gap'], facet['properties']['compare']['gap']),
                'end': 'NOW/%s' % unit,
                'gap': '+%(gap)s' % facet['properties']['compare'],
                'facet': {facet['id']: json_facets[facet['id']]}
              }
            if facet['properties']['filter']['is_enabled']:
              json_facets[facet['id']] = {
                'type': 'query',
                'q': facet['properties']['filter']['query'] or EMPTY_QUERY.get(),
                'facet': {facet['id']: json_facets[facet['id']]}
              }
            json_facets['processEmpty'] = True
        elif facet['type'] == 'pivot':
          if facet['properties']['facets'] or facet['widgetType'] == 'map-widget':
            fields = facet['field']
            fields_limits = []
            for f in facet['properties']['facets']:
              fields_limits.append('f.%s.facet.limit=%s' % (f['field'], f['limit']))
              fields_limits.append('f.%s.facet.mincount=%s' % (f['field'], f['mincount']))
              fields += ',' + f['field']
            keys = {
                'id': '%(id)s' % facet,
                'key': '%(field)s-%(id)s' % facet,
                'field': facet['field'],
                'fields': fields,
                'limit': int(facet['properties'].get('limit', 10)),
                'mincount': int(facet['properties']['mincount']),
                'fields_limits': ' '.join(fields_limits)
            }
            params += (
                ('facet.pivot', '{!key=%(key)s ex=%(id)s f.%(field)s.facet.limit=%(limit)s f.%(field)s.facet.mincount=%(mincount)s %(fields_limits)s}%(fields)s' % keys),
            )

      if json_facets:
        params += (
            ('json.facet', json.dumps(json_facets)),
        )

    params += self._get_fq(collection, query)

    fl = urllib.unquote(utf_quoter(','.join(Collection2.get_field_list(collection))))

    nested_fields = self._get_nested_fields(collection)
    if nested_fields:
      fl += urllib.unquote(utf_quoter(',[child parentFilter="%s"]' % ' OR '.join(nested_fields)))

    if collection['template']['moreLikeThis'] and fl != ['*']: # Potential conflict with nested documents
      id_field = collection.get('idField', 'id')
      params += (
        ('mlt', 'true'),
        ('mlt.fl', fl.replace(',%s' % id_field, '')),
        ('mlt.mintf', 1),
        ('mlt.mindf', 1),
        ('mlt.maxdf', 50),
        ('mlt.maxntp', 1000),
        ('mlt.count', 10),
        #('mlt.minwl', 1),
        #('mlt.maxwl', 1),
      )
      fl = '*'

    params += (('fl', fl),)

    params += (
      ('hl', 'true'),
      ('hl.fl', '*'),
      ('hl.snippets', 5),
      ('hl.fragsize', 1000),
    )

    #if query.get('timezone'):
    #  params += (('TZ', query.get('timezone')),)

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


  def _n_facet_dimension(self, widget, _f, facets, dim, timeFilter, collection, can_range=None):
    facet = facets[0]
    f_name = 'dim_%02d:%s' % (dim, facet['field'])

    if facet['aggregate']['function'] == 'count':
      if 'facet' not in _f:
        _f['facet'] = {f_name: {}}
      else:
        _f['facet'][f_name] = {}
      _f = _f['facet']

      sort = {'count': facet['sort']}
      for i, agg in enumerate(self._get_dimension_aggregates(facets)):
        if agg['sort'] != 'default':
          agg_function = self._get_aggregate_function(agg)
          sort = {'agg_%02d_%02d:%s' % (dim, i, agg_function): agg['sort']}
      if sort.get('count') == 'default':
        sort['count'] = 'desc'

      _f[f_name] = {
          'type': 'terms',
          'field': '%(field)s' % facet,
          'limit': int(facet.get('limit', 10)),
          'numBuckets': True,
          'allBuckets': True,
          'sort': sort,
          'missing': facet.get('missing', False)
          #'prefix': '' # Forbidden on numeric fields
      }
      if int(facet['mincount']):
        _f[f_name]['mincount'] = int(facet['mincount']) # Forbidden on n > 0 field if mincount = 0

      if 'start' in facet and not facet.get('type') == 'field':
        _f[f_name].update({
            'type': 'range',
            'start': facet['start'],
            'end': facet['end'],
            'gap': facet['gap']
        })

        # Only on dim 1 currently
        if can_range or (timeFilter and timeFilter['time_field'] == facet['field'] and (widget['id'] not in timeFilter['time_filter_overrides'])): # or facet['widgetType'] != 'bucket-widget'):
          facet['widgetType'] = widget['widgetType']
          _f[f_name].update(self._get_time_filter_query(timeFilter, facet, collection))

      if widget['widgetType'] == 'tree2-widget' and facets[-1]['aggregate']['function'] != 'count':
        _f['subcount'] = self._get_aggregate_function(facets[-1])

      if len(facets) > 1: # Get n+1 dimension
        if facets[1]['aggregate']['function'] == 'count':
          self._n_facet_dimension(widget, _f[f_name], facets[1:], dim + 1, timeFilter, collection)
        else:
          self._n_facet_dimension(widget, _f[f_name], facets[1:], dim, timeFilter, collection)
    else:
      agg_function = self._get_aggregate_function(facet)
      _f['facet'] = {
          'agg_%02d_00:%s' % (dim, agg_function): agg_function
      }
      for i, _f_agg in enumerate(facets[1:], 1):
        if _f_agg['aggregate']['function'] != 'count':
          agg_function = self._get_aggregate_function(_f_agg)
          _f['facet']['agg_%02d_%02d:%s' % (dim, i, agg_function)] = agg_function
        else:
          self._n_facet_dimension(widget, _f, facets[i:], dim + 1, timeFilter, collection) # Get n+1 dimension
          break


  def select(self, collection, query=None, rows=100, start=0):
    if query is None:
      query = EMPTY_QUERY.get()

    params = self._get_params() + (
        ('q', query),
        ('wt', 'json'),
        ('rows', rows),
        ('start', start),
    )

    response = self._root.get('%s/select' % collection, params)
    return self._get_json(response)


  def suggest(self, collection, query):
    try:
      params = self._get_params() + (
          ('suggest', 'true'),
          ('suggest.build', 'true'),
          ('suggest.q', query['q']),
          ('wt', 'json'),
      )
      if query.get('dictionary'):
        params += (
            ('suggest.dictionary', query['dictionary']),
        )
      response = self._root.get('%s/suggest' % collection, params)
      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  def collections(self): # To drop, used in indexer v1
    try:
      params = self._get_params() + (
          ('detail', 'true'),
          ('path', '/clusterstate.json'),
      )
      response = self._root.get('zookeeper', params=params)
      return json.loads(response['znode'].get('data', '{}'))
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  def collections2(self):
    try:
      params = self._get_params() + (
          ('action', 'LIST'),
          ('wt', 'json'),
      )
      return self._root.get('admin/collections', params=params)['collections']
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  def config(self, name):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
      )
      response = self._root.get('%s/config' % name, params=params)
      return self._get_json(response)['config']
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  def configs(self):
    try:
      params = self._get_params() + (
          ('action', 'LIST'),
          ('wt', 'json'),
      )
      return self._root.get('admin/configs', params=params)['configSets']
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  def create_config(self, name, base_config, immutable=False):
    try:
      params = self._get_params() + (
          ('action', 'CREATE'),
          ('name', name),
          ('baseConfigSet', base_config),
          ('configSetProp.immutable', immutable),
          ('wt', 'json'),
      )
      return self._root.post('admin/configs', params=params, contenttype='application/json')
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  def delete_config(self, name):
    response = {'status': -1, 'message': ''}

    try:
      params = self._get_params() + (
        ('action', 'DELETE'),
        ('name', name),
        ('wt', 'json')
      )

      data = self._root.get('admin/configs', params=params)
      if data['responseHeader']['status'] == 0:
        response['status'] = 0
      else:
        response['message'] = "Could not remove config: %s" % data
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))
    return response


  def list_aliases(self):
    try:
      params = self._get_params() + (
          ('action', 'LISTALIASES'),
          ('wt', 'json'),
      )
      return self._root.get('admin/collections', params=params)['aliases'] or []
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


  def create_collection2(self, name, config_name=None, shards=1, replication=1, **kwargs):
    try:
      params = self._get_params() + (
        ('action', 'CREATE'),
        ('name', name),
        ('numShards', shards),
        ('replicationFactor', replication),
        ('wt', 'json')
      )
      if config_name:
        params += (
          ('collection.configName', config_name),
        )
      if kwargs:
        params += tuple(((key, val) for key, val in kwargs.iteritems()))

      response = self._root.post('admin/collections', params=params, contenttype='application/json')
      response_data = self._get_json(response)
      if response_data.get('failure'):
        raise PopupException(_('Collection could not be created: %(failure)s') % response_data)
      else:
        return response_data
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  def update_config(self, name, properties):
    try:
      params = self._get_params() + (
        ('wt', 'json'),
      )

      response = self._root.post('%(collection)s/config' % {'collection': name}, params=params, data=json.dumps(properties), contenttype='application/json')
      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  def add_fields(self, name, fields):
    try:
      params = self._get_params() + (
        ('wt', 'json'),
      )

      data = {'add-field': fields}

      response = self._root.post('%(collection)s/schema' % {'collection': name}, params=params, data=json.dumps(data), contenttype='application/json')
      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  def create_core(self, name, instance_dir, shards=1, replication=1):
    try:
      params = self._get_params() + (
        ('action', 'CREATE'),
        ('name', name),
        ('instanceDir', instance_dir),
        ('wt', 'json'),
      )

      response = self._root.post('admin/cores', params=params, contenttype='application/json')
      if response.get('responseHeader', {}).get('status', -1) == 0:
        return True
      else:
        LOG.error("Could not create core. Check response:\n%s" % json.dumps(response, indent=2))
        return False
    except RestException, e:
      if 'already exists' in e.message:
        LOG.warn("Could not create collection.", exc_info=True)
        return False
      else:
        raise PopupException(e, title=_('Error while accessing Solr'))


  def create_alias(self, name, collections):
    try:
      params = self._get_params() + (
        ('action', 'CREATEALIAS'),
        ('name', name),
        ('collections', ','.join(collections)),
        ('wt', 'json'),
      )

      response = self._root.post('admin/collections', params=params, contenttype='application/json')
      if response.get('responseHeader', {}).get('status', -1) != 0:
        raise PopupException(_("Could not create or edit alias: %s") % response)
      else:
        return response
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  def delete_alias(self, name):
    try:
      params = self._get_params() + (
        ('action', 'DELETEALIAS'),
        ('name', name),
        ('wt', 'json'),
      )

      response = self._root.post('admin/collections', params=params, contenttype='application/json')
      if response.get('responseHeader', {}).get('status', -1) != 0:
        msg = _("Could not delete alias. Check response:\n%s") % json.dumps(response, indent=2)
        LOG.error(msg)
        raise PopupException(msg)
    except RestException, e:
        raise PopupException(e, title=_('Error while accessing Solr'))


  def delete_collection(self, name):
    response = {'status': -1, 'message': ''}

    try:
      params = self._get_params() + (
        ('action', 'DELETE'),
        ('name', name),
        ('wt', 'json')
      )

      data = self._root.post('admin/collections', params=params, contenttype='application/json')
      if data['responseHeader']['status'] == 0:
        response['status'] = 0
      else:
        response['message'] = "Could not remove collection: %s" % data
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))
    return response


  def remove_core(self, name):
    try:
      params = self._get_params() + (
        ('action', 'UNLOAD'),
        ('name', name),
        ('deleteIndex', 'true'),
        ('wt', 'json')
      )

      response = self._root.post('admin/cores', params=params, contenttype='application/json')
      if 'success' in response:
        return True
      else:
        LOG.error("Could not remove core. Check response:\n%s" % json.dumps(response, indent=2))
        return False
    except RestException, e:
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


  def get_schema(self, collection):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
      )
      response = self._root.get('%(core)s/schema' % {'core': collection}, params=params)
      return self._get_json(response)['schema']
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  # Deprecated
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
      response = self._root.get('%(core)s/schema' % {'core': core}, params=params)
      response_json = self._get_json(response)
      fields = response_json['schema']['fields']
      if response_json['schema'].get('uniqueKey'):
        for field in fields:
          if field['name'] == response_json['schema']['uniqueKey']:
            field['primary_key'] = 'true'
      return {
        'fields': fields,
        'responseHeader': response_json['responseHeader']
      }
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def stats(self, core, fields, query=None, facet=''):
    try:
      params = self._get_params() + (
          ('q', self._get_q(query) if query is not None else EMPTY_QUERY.get()),
          ('wt', 'json'),
          ('rows', 0),
          ('stats', 'true'),
      )

      if query is not None:
        params += self._get_fq(None, query)

      if facet:
        params += (('stats.facet', facet),)

      params += tuple([('stats.field', field) for field in fields])
      response = self._root.get('%(core)s/select' % {'core': core}, params=params)

      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def terms(self, core, field, properties=None):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
          ('rows', 0),
          ('terms.fl', field),
      )
      if properties:
        for key, val in properties.iteritems():
          params += ((key, val),)

      response = self._root.get('%(core)s/terms' % {'core': core}, params=params)
      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  def info_system(self):
    try:
      params = self._get_params() + (
        ('wt', 'json'),
      )

      response = self._root.get('admin/info/system', params=params)
      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  def sql(self, collection, statement):
    try:
      if 'limit' not in statement.lower(): # rows is not supported
        statement = statement + ' LIMIT 100'

      params = self._get_params() + (
          ('wt', 'json'),
          ('rows', 0),
          ('stmt', statement),
          ('rows', 100),
          ('start', 0),
      )

      response = self._root.get('%(collection)s/sql' % {'collection': collection}, params=params)
      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def get(self, core, doc_id):
    collection_name = core['name']
    try:
      params = self._get_params() + (
          ('id', doc_id),
          ('wt', 'json'),
      )
      response = self._root.get('%(core)s/get' % {'core': collection_name}, params=params)
      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  def export(self, name, query, fl, sort, rows=100):
    try:
      params = self._get_params() + (
          ('q', query),
          ('fl', fl),
          ('sort', sort),
          ('rows', rows),
          ('wt', 'json'),
      )
      response = self._root.get('%(name)s/export' % {'name': name}, params=params)
      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  def update(self, collection_or_core_name, data, content_type='csv', version=None, **kwargs):
    if content_type == 'csv':
      content_type = 'application/csv'
    elif content_type == 'json':
      content_type = 'application/json'
    else:
      LOG.error("Trying to update collection  %s with content type %s. Allowed content types: csv/json" % (collection_or_core_name, content_type))

    params = self._get_params() + (
        ('wt', 'json'),
        ('overwrite', 'true'),
        ('commit', 'true'),
    )
    if version is not None:
      params += (
        ('_version_', version),
        ('versions', 'true')
      )
    if kwargs:
      params += tuple(((key, val) for key, val in kwargs.iteritems()))

    response = self._root.post('%s/update' % collection_or_core_name, contenttype=content_type, params=params, data=data)
    return self._get_json(response)


  # Deprecated
  def aliases(self):
    try:
      params = self._get_params() + ( # Waiting for SOLR-4968
          ('detail', 'true'),
          ('path', '/aliases.json'),
      )
      response = self._root.get('zookeeper', params=params)
      return json.loads(response['znode'].get('data', '{}')).get('collection', {})
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  # Deprecated
  def create_collection(self, name, shards=1, replication=1):
    try:
      params = self._get_params() + (
        ('action', 'CREATE'),
        ('name', name),
        ('numShards', shards),
        ('replicationFactor', replication),
        ('collection.configName', name),
        ('wt', 'json')
      )

      response = self._root.post('admin/collections', params=params, contenttype='application/json')
      if 'success' in response:
        return True
      else:
        LOG.error("Could not create collection. Check response:\n%s" % json.dumps(response, indent=2))
        return False
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  # Deprecated
  def remove_collection(self, name):
    try:
      params = self._get_params() + (
        ('action', 'DELETE'),
        ('name', name),
        ('wt', 'json')
      )

      response = self._root.post('admin/collections', params=params, contenttype='application/json')
      if 'success' in response:
        return True
      else:
        LOG.error("Could not remove collection. Check response:\n%s" % json.dumps(response, indent=2))
        return False
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


  def _get_params(self):
    if self.security_enabled:
      return (('doAs', self._user ),)
    return (('user.name', SERVER_USER.get()), ('doAs', self._user),)

  def _get_q(self, query):
    q_template = '(%s)' if len(query['qs']) >= 2 else '%s'
    return 'OR'.join([q_template % (q['q'] or EMPTY_QUERY.get()) for q in query['qs']]).encode('utf-8')

  @classmethod
  def _get_aggregate_function(cls, facet):
    f = facet['aggregate']

    if f['function'] == 'formula':
      return f['formula']
    elif f['function'] == 'field':
      return f['value']
    else:
      fields = [facet['field']]
      if f['function'] == 'median':
        f['function'] = 'percentile'
        fields.append('50')
      elif f['function'] == 'percentile':
        fields.append(str(f['percentile']))
        f['function'] = 'percentile'
      return '%s(%s)' % (f['function'], ','.join(fields))

  def _get_range_borders(self, collection, query):
    props = {}

    time_field = collection['timeFilter'].get('field')

    if time_field and (collection['timeFilter']['value'] != 'all' or collection['timeFilter']['type'] == 'fixed'):
      # fqs overrides main time filter
      # No longer override
      props['time_filter_overrides'] = []
      props['time_field'] = time_field

      if collection['timeFilter']['type'] == 'rolling':
        props['field'] = collection['timeFilter']['field']
        props['from'] = 'NOW-%s' % collection['timeFilter']['value']
        props['to'] = 'NOW'
        props['gap'] = GAPS.get(collection['timeFilter']['value'])
      elif collection['timeFilter']['type'] == 'fixed':
        props['field'] = collection['timeFilter']['field']
        props['from'] = collection['timeFilter'].get('from', 'NOW-7DAYS')
        props['to'] = collection['timeFilter'].get('to', 'NOW')
        props['fixed'] = True

    return props

  def _get_time_filter_query(self, timeFilter, facet, collection):
    properties = facet.get('properties', facet)
    if timeFilter:
      props = {}
      # If the start & end are equal to min/max, then we want to show the whole domain (either interval now-x or static)
      # In that case use timeFilter values
      if properties['start'] == properties['min'] and properties['end'] == properties['max']:
        stat_facet = {'min': timeFilter['from'], 'max': timeFilter['to']}
        properties['start'] = None
        properties['end'] = None
      else: # The user has zoomed in. Only show that section.
        stat_facet = {'min': properties['min'], 'max': properties['max']}
      _compute_range_facet(facet['widgetType'], stat_facet, props, properties['start'], properties['end'],
                           SLOTS=properties['slot'])
      gap = props['gap']
      return {
        'min': '%(min)s' % props,
        'max': '%(max)s' % props,
        'start': '%(start)s' % props,
        'end': '%(end)s' % props,
        'gap': '%(gap)s' % props,
      }
    else:
      props = {}
      # If the start & end are equal to min/max, then we want to show the whole domain. Since min/max can change, we fetch latest values and update start/end
      if properties['start'] == properties['min'] and properties['end'] == properties['max']:
        stats_json = self.stats(collection['name'], [facet['field']])
        stat_facet = stats_json['stats']['stats_fields'][facet['field']]
        properties['start'] = None
        properties['end'] = None
      else: # the user has zoomed in. Only show that section.
        stat_facet = {'min': properties['min'], 'max': properties['max']}
      _compute_range_facet(facet['widgetType'], stat_facet, props, properties['start'], properties['end'], SLOTS = properties['slot'])
      return {
        'start': '%(start)s' % props,
        'end': '%(end)s' % props,
        'gap': '%(gap)s' % props,
        'min': '%(min)s' % props,
        'max': '%(max)s' % props,
      }

  def _get_fq(self, collection, query):
    params = ()
    timeFilter = {}

    if collection:
      timeFilter = self._get_range_borders(collection, query)
    if timeFilter and not timeFilter.get('time_filter_overrides'):
      params += (('fq', urllib.unquote(utf_quoter('%(field)s:[%(from)s TO %(to)s]' % timeFilter))),)

    # Merge facets queries on same fields
    grouped_fqs = groupby(query['fqs'], lambda x: (x['type'], x['field']))
    merged_fqs = []
    for key, group in grouped_fqs:
      field_fq = next(group)
      for fq in group:
        for f in fq['filter']:
          field_fq['filter'].append(f)
      merged_fqs.append(field_fq)

    for fq in merged_fqs:
      if fq['type'] == 'field':
        fields = fq['field'] if type(fq['field']) == list else [fq['field']] # 2D facets support
        for field in fields:
          f = []
          for _filter in fq['filter']:
            values = _filter['value'] if type(_filter['value']) == list else [_filter['value']] # 2D facets support
            if fields.index(field) < len(values): # Lowest common field denominator
              value = values[fields.index(field)]
              if value or value is False:
                exclude = '-' if _filter['exclude'] else ''
                if value is not None and ' ' in force_unicode(value):
                  value = force_unicode(value).replace('"', '\\"')
                  f.append('%s%s:"%s"' % (exclude, field, value))
                else:
                  f.append('%s{!field f=%s}%s' % (exclude, field, value))
              else: # Handle empty value selection that are returned using solr facet.missing
                value = "*"
                exclude = '-'
                f.append('%s%s:%s' % (exclude, field, value))
          _params ='{!tag=%(id)s}' % fq + ' '.join(f)
          params += (('fq', urllib.unquote(utf_quoter(_params))),)
      elif fq['type'] == 'range':
        params += (('fq', '{!tag=%(id)s}' % fq + ' '.join([urllib.unquote(
                    utf_quoter('%s%s:[%s TO %s}' % ('-' if field['exclude'] else '', fq['field'], f['from'], f['to']))) for field, f in zip(fq['filter'], fq['properties'])])),)
      elif fq['type'] == 'range-up':
        params += (('fq', '{!tag=%(id)s}' % fq + ' '.join([urllib.unquote(
                    utf_quoter('%s%s:[%s TO %s}' % ('-' if field['exclude'] else '', fq['field'], f['from'] if fq['is_up'] else '*', '*' if fq['is_up'] else f['from'])))
                                                          for field, f in zip(fq['filter'], fq['properties'])])),)
      elif fq['type'] == 'map':
        _keys = fq.copy()
        _keys.update(fq['properties'])
        params += (('fq', '{!tag=%(id)s}' % fq + urllib.unquote(
                    utf_quoter('%(lat)s:[%(lat_sw)s TO %(lat_ne)s} AND %(lon)s:[%(lon_sw)s TO %(lon_ne)s}' % _keys))),)

    nested_fields = self._get_nested_fields(collection)
    if nested_fields:
      params += (('fq', urllib.unquote(utf_quoter(' OR '.join(nested_fields)))),)

    return params


  def _get_dimension_aggregates(self, facets):
    aggregates = []
    for agg in facets:
      if agg['aggregate']['function'] != 'count':
        aggregates.append(agg)
      else:
        return aggregates
    return aggregates


  def _get_nested_fields(self, collection):
    if collection and collection.get('nested') and collection['nested']['enabled']:
      return [field['filter'] for field in self._flatten_schema(collection['nested']['schema']) if field['selected']]
    else:
      return []


  def _flatten_schema(self, level):
    fields = []
    for field in level:
      fields.append(field)
      if field['values']:
        fields.extend(self._flatten_schema(field['values']))
    return fields


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


  def uniquekey(self, collection):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
      )
      response = self._root.get('%s/schema/uniquekey' % collection, params=params)
      return self._get_json(response)['uniqueKey']
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


GAPS = {
    '5MINUTES': {
        'histogram-widget': {'coeff': '+3', 'unit': 'SECONDS'}, # ~100 slots
        'timeline-widget': {'coeff': '+3', 'unit': 'SECONDS'}, # ~100 slots
        'bucket-widget': {'coeff': '+3', 'unit': 'SECONDS'}, # ~100 slots
        'bar-widget': {'coeff': '+3', 'unit': 'SECONDS'}, # ~100 slots
        'facet-widget': {'coeff': '+1', 'unit': 'MINUTES'}, # ~10 slots
        'pie-widget': {'coeff': '+1', 'unit': 'MINUTES'} # ~10 slots
    },
    '30MINUTES': {
        'histogram-widget': {'coeff': '+20', 'unit': 'SECONDS'},
        'timeline-widget': {'coeff': '+20', 'unit': 'SECONDS'},
        'bucket-widget': {'coeff': '+20', 'unit': 'SECONDS'},
        'bar-widget': {'coeff': '+20', 'unit': 'SECONDS'},
        'facet-widget': {'coeff': '+5', 'unit': 'MINUTES'},
        'pie-widget': {'coeff': '+5', 'unit': 'MINUTES'},
    },
    '1HOURS': {
        'histogram-widget': {'coeff': '+30', 'unit': 'SECONDS'},
        'timeline-widget': {'coeff': '+30', 'unit': 'SECONDS'},
        'bucket-widget': {'coeff': '+30', 'unit': 'SECONDS'},
        'bar-widget': {'coeff': '+30', 'unit': 'SECONDS'},
        'facet-widget': {'coeff': '+10', 'unit': 'MINUTES'},
        'pie-widget': {'coeff': '+10', 'unit': 'MINUTES'}
    },
    '12HOURS': {
        'histogram-widget': {'coeff': '+7', 'unit': 'MINUTES'},
        'timeline-widget': {'coeff': '+7', 'unit': 'MINUTES'},
        'bucket-widget': {'coeff': '+7', 'unit': 'MINUTES'},
        'bar-widget': {'coeff': '+7', 'unit': 'MINUTES'},
        'facet-widget': {'coeff': '+1', 'unit': 'HOURS'},
        'pie-widget': {'coeff': '+1', 'unit': 'HOURS'}
    },
    '1DAYS': {
        'histogram-widget': {'coeff': '+15', 'unit': 'MINUTES'},
        'timeline-widget': {'coeff': '+15', 'unit': 'MINUTES'},
        'bucket-widget': {'coeff': '+15', 'unit': 'MINUTES'},
        'bar-widget': {'coeff': '+15', 'unit': 'MINUTES'},
        'facet-widget': {'coeff': '+3', 'unit': 'HOURS'},
        'pie-widget': {'coeff': '+3', 'unit': 'HOURS'}
    },
    '2DAYS': {
        'histogram-widget': {'coeff': '+30', 'unit': 'MINUTES'},
        'timeline-widget': {'coeff': '+30', 'unit': 'MINUTES'},
        'bucket-widget': {'coeff': '+30', 'unit': 'MINUTES'},
        'bar-widget': {'coeff': '+30', 'unit': 'MINUTES'},
        'facet-widget': {'coeff': '+6', 'unit': 'HOURS'},
        'pie-widget': {'coeff': '+6', 'unit': 'HOURS'}
    },
    '7DAYS': {
        'histogram-widget': {'coeff': '+3', 'unit': 'HOURS'},
        'timeline-widget': {'coeff': '+3', 'unit': 'HOURS'},
        'bucket-widget': {'coeff': '+3', 'unit': 'HOURS'},
        'bar-widget': {'coeff': '+3', 'unit': 'HOURS'},
        'facet-widget': {'coeff': '+1', 'unit': 'DAYS'},
        'pie-widget': {'coeff': '+1', 'unit': 'DAYS'}
    },
    '1MONTHS': {
        'histogram-widget': {'coeff': '+12', 'unit': 'HOURS'},
        'timeline-widget': {'coeff': '+12', 'unit': 'HOURS'},
        'bucket-widget': {'coeff': '+12', 'unit': 'HOURS'},
        'bar-widget': {'coeff': '+12', 'unit': 'HOURS'},
        'facet-widget': {'coeff': '+5', 'unit': 'DAYS'},
        'pie-widget': {'coeff': '+5', 'unit': 'DAYS'}
    },
    '3MONTHS': {
        'histogram-widget': {'coeff': '+1', 'unit': 'DAYS'},
        'timeline-widget': {'coeff': '+1', 'unit': 'DAYS'},
        'bucket-widget': {'coeff': '+1', 'unit': 'DAYS'},
        'bar-widget': {'coeff': '+1', 'unit': 'DAYS'},
        'facet-widget': {'coeff': '+30', 'unit': 'DAYS'},
        'pie-widget': {'coeff': '+30', 'unit': 'DAYS'}
    },
    '1YEARS': {
        'histogram-widget': {'coeff': '+3', 'unit': 'DAYS'},
        'timeline-widget': {'coeff': '+3', 'unit': 'DAYS'},
        'bucket-widget': {'coeff': '+3', 'unit': 'DAYS'},
        'bar-widget': {'coeff': '+3', 'unit': 'DAYS'},
        'facet-widget': {'coeff': '+12', 'unit': 'MONTHS'},
        'pie-widget': {'coeff': '+12', 'unit': 'MONTHS'}
    },
    '2YEARS': {
        'histogram-widget': {'coeff': '+7', 'unit': 'DAYS'},
        'timeline-widget': {'coeff': '+7', 'unit': 'DAYS'},
        'bucket-widget': {'coeff': '+7', 'unit': 'DAYS'},
        'bar-widget': {'coeff': '+7', 'unit': 'DAYS'},
        'facet-widget': {'coeff': '+3', 'unit': 'MONTHS'},
        'pie-widget': {'coeff': '+3', 'unit': 'MONTHS'}
    },
    '10YEARS': {
        'histogram-widget': {'coeff': '+1', 'unit': 'MONTHS'},
        'timeline-widget': {'coeff': '+1', 'unit': 'MONTHS'},
        'bucket-widget': {'coeff': '+1', 'unit': 'MONTHS'},
        'bar-widget': {'coeff': '+1', 'unit': 'MONTHS'},
        'facet-widget': {'coeff': '+1', 'unit': 'YEARS'},
        'pie-widget': {'coeff': '+1', 'unit': 'YEARS'}
    }
}