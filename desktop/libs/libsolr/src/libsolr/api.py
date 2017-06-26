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

from desktop.lib.exceptions_renderable import PopupException
from desktop.conf import SERVER_USER
from desktop.lib.conf import BoundConfig
from desktop.lib.i18n import force_unicode
from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest import resource
from dashboard.facet_builder import _compute_range_facet

from search.conf import EMPTY_QUERY, SECURITY_ENABLED

from libsolr.conf import SSL_CERT_CA_VERIFY


LOG = logging.getLogger(__name__)


def utf_quoter(what):
  return urllib.quote(unicode(what).encode('utf-8'), safe='~@#$&()*!+=;,.?/\'')

def search_enabled():
  return type(SECURITY_ENABLED) == BoundConfig


class SolrApi(object):
  """
  http://wiki.apache.org/solr/CoreAdmin#CoreAdminHandler
  """
  def __init__(self, solr_url, user,
               security_enabled=SECURITY_ENABLED.get() if search_enabled() else SECURITY_ENABLED.default,
               ssl_cert_ca_verify=SSL_CERT_CA_VERIFY.get()):
    self._url = solr_url
    self._user = user
    self._client = HttpClient(self._url, logger=LOG)
    self.security_enabled = security_enabled

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

          if timeFilter and timeFilter['time_field'] == facet['field'] and (facet['id'] not in timeFilter['time_filter_overrides'] or facet['widgetType'] != 'histogram-widget'):
            keys.update(self._get_time_filter_query(timeFilter, facet))

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
          _f = {
              'field': facet['field'],
              'limit': int(facet['properties'].get('limit', 10)) + (1 if facet['widgetType'] == 'text-facet-widget' else 0),
              'mincount': int(facet['properties']['mincount']),
              'sort': {'count': facet['properties']['sort']},
          }

          if facet['properties']['domain'].get('blockParent') or facet['properties']['domain'].get('blockChildren'):
            _f['domain'] = {}
            if facet['properties']['domain'].get('blockParent'):
              _f['domain']['blockParent'] = ' OR '.join(facet['properties']['domain']['blockParent'])
            if facet['properties']['domain'].get('blockChildren'):
              _f['domain']['blockChildren'] = ' OR '.join(facet['properties']['domain']['blockChildren'])

          if 'start' in facet['properties'] and not facet['properties'].get('type') == 'field':
            _f.update({
                'type': 'range',
                'start': facet['properties']['start'],
                'end': facet['properties']['end'],
                'gap': facet['properties']['gap'],
            })
            if timeFilter and timeFilter['time_field'] == facet['field'] and (facet['id'] not in timeFilter['time_filter_overrides'] or facet['widgetType'] != 'bucket-widget'):
              _f.update(self._get_time_filter_query(timeFilter, facet))
          else:
            _f.update({
                'type': 'terms',
                'field': facet['field'],
                'excludeTags': facet['id'],
                'offset': 0,
                'numBuckets': True,
                'allBuckets': True,
                #'prefix': '' # Forbidden on numeric fields
            })
            if facet['properties']['canRange'] and not facet['properties']['isDate']:
              del _f['mincount'] # Numeric fields do not support

          if facet['properties']['facets']:
            self._n_facet_dimension(facet, _f, facet['properties']['facets'], 1)
            if facet['widgetType'] == 'text-facet-widget':
              _fname = _f['facet'].keys()[0]
              _f['sort'] = {_fname: facet['properties']['sort']}
              # domain = '-d2:NaN' # Solr 6.4

          json_facets[facet['id']] = _f
        elif facet['type'] == 'function':
          json_facets[facet['id']] = self._get_aggregate_function(facet)
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

    from dashboard.models import Collection2
    fl = urllib.unquote(utf_quoter(','.join(Collection2.get_field_list(collection))))

    nested_fields = self._get_nested_fields(collection)
    if nested_fields:
      fl += urllib.unquote(utf_quoter(',[child parentFilter="%s"]' % ' OR '.join(nested_fields)))

    params += (('fl', fl),)

    params += (
      ('hl', 'true'),
      ('hl.fl', '*'),
      ('hl.snippets', 5),
      ('hl.fragsize', 1000),
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


  def _n_facet_dimension(self, widget, _f, facets, dim):
    facet = facets[0]
    f_name = 'dim_%02d:%s' % (dim, facet['field'])

    if facet['aggregate']['function'] == 'count':
      if 'facet' not in _f:
        _f['facet'] = {f_name: {}}
      else:
        _f['facet'][f_name] = {}
      _f = _f['facet']

      _f[f_name] = {
          'type': 'terms',
          'field': '%(field)s' % facet,
          'limit': int(facet.get('limit', 10)),
          'mincount': int(facet['mincount']),
          'numBuckets': True,
          'allBuckets': True,
          #'prefix': '' # Forbidden on numeric fields
      }
      if widget['widgetType'] == 'tree2-widget' and facets[-1]['aggregate']['function'] != 'count':
        _f['subcount'] = self._get_aggregate_function(facets[-1])

      if len(facets) > 1: # Get n+1 dimension
        if facets[1]['aggregate']['function'] == 'count':
          self._n_facet_dimension(widget, _f[f_name], facets[1:], dim + 1)
        else:
          self._n_facet_dimension(widget, _f[f_name], facets[1:], dim)
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
          self._n_facet_dimension(widget, _f, facets[i:], dim + 1) # Get n+1 dimension
          break


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


  def configs(self):
    try:
      params = self._get_params() + (
          ('action', 'LIST'),
          ('wt', 'json'),
      )
      return self._root.get('admin/configs', params=params)['configSets']
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))


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

  def create_or_modify_alias(self, name, collections):
    try:
      params = self._get_params() + (
        ('action', 'CREATEALIAS'),
        ('name', name),
        ('collections', ','.join(collections)),
        ('wt', 'json'),
      )

      response = self._root.post('admin/collections', params=params, contenttype='application/json')
      if response.get('responseHeader', {}).get('status', -1) != 0:
        msg = _("Could not create or edit alias. Check response:\n%s") % json.dumps(response, indent=2)
        LOG.error(msg)
        raise PopupException(msg)
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

  def remove_collection(self, name, replication=1):
    try:
      params = self._get_params() + (
        ('action', 'DELETE'),
        ('name', name),
        ('replicationFactor', replication),
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

  def add_fields(self, collection, fields):
    try:
      params = self._get_params()
      return self._root.post('%s/schema/fields' % collection, params=params, data=json.dumps(fields), contenttype='application/json')
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

  def _get_params(self):
    if self.security_enabled:
      return (('doAs', self._user ),)
    return (('user.name', SERVER_USER.get()), ('doAs', self._user),)

  def _get_q(self, query):
    q_template = '(%s)' if len(query['qs']) >= 2 else '%s'
    return 'OR'.join([q_template % (q['q'] or EMPTY_QUERY.get()) for q in query['qs']]).encode('utf-8')

  @classmethod
  def _get_aggregate_function(cls, facet):
    if 'properties' in facet:
      f = facet['properties']['aggregate'] # Level 1 facet
    else:
      f = facet['aggregate']

    if not f['ops']:
      f['ops'] = [{'function': 'field', 'value': facet['field'], 'ops': []}]

    return cls.__get_aggregate_function(f)

  @classmethod
  def __get_aggregate_function(cls, f):
    if f['function'] == 'field':
      return f['value']
    else:
      fields = []
      for _f in f['ops']:
        fields.append(cls.__get_aggregate_function(_f))
      if f['function'] == 'median':
        f['function'] = 'percentile'
        fields.append('50')
      elif f['function'] == 'percentiles':
        fields.extend(map(lambda a: str(a), [_p['value'] for _p in f['percentiles']]))
      return '%s(%s)' % (f['function'], ','.join(fields))

  def _get_range_borders(self, collection, query):
    props = {}

    time_field = collection['timeFilter'].get('field')

    if time_field and (collection['timeFilter']['value'] != 'all' or collection['timeFilter']['type'] == 'fixed'):
      # fqs overrides main time filter
      fq_time_ids = [fq['id'] for fq in query['fqs'] if fq['field'] == time_field]
      props['time_filter_overrides'] = fq_time_ids
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

  def _get_time_filter_query(self, timeFilter, facet):
    if 'fixed' in timeFilter:
      props = {}
      stat_facet = {'min': timeFilter['from'], 'max': timeFilter['to']}
      _compute_range_facet(facet['widgetType'], stat_facet, props, stat_facet['min'], stat_facet['max'])
      gap = props['gap']
      unit = re.split('\d+', gap)[1]
      return {
        'start': '%(from)s/%(unit)s' % {'from': timeFilter['from'], 'unit': unit},
        'end': '%(to)s/%(unit)s' % {'to': timeFilter['to'], 'unit': unit},
        'gap': '%(gap)s' % props, # add a 'auto'
      }
    else:
      gap = timeFilter['gap'][facet['widgetType']]
      return {
        'start': '%(from)s/%(unit)s' % {'from': timeFilter['from'], 'unit': gap['unit']},
        'end': '%(to)s/%(unit)s' % {'to': timeFilter['to'], 'unit': gap['unit']},
        'gap': '%(coeff)s%(unit)s/%(unit)s' % gap, # add a 'auto'
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
              exclude = '-' if _filter['exclude'] else ''
              if value is not None and ' ' in force_unicode(value):
                value = force_unicode(value).replace('"', '\\"')
                f.append('%s%s:"%s"' % (exclude, field, value))
              else:
                f.append('%s{!field f=%s}%s' % (exclude, field, value))
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

  def update(self, collection_or_core_name, data, content_type='csv', version=None):
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
    response = self._root.post('%s/update' % collection_or_core_name, contenttype=content_type, params=params, data=data)
    return self._get_json(response)


GAPS = {
    '5MINUTES': {
        'histogram-widget': {'coeff': '+3', 'unit': 'SECONDS'}, # ~100 slots
        'timeline-widget': {'coeff': '+3', 'unit': 'SECONDS'}, # ~100 slots
        'bucket-widget': {'coeff': '+3', 'unit': 'SECONDS'}, # ~100 slots
        'bar-widget': {'coeff': '+3', 'unit': 'SECONDS'}, # ~100 slots
        'facet-widget': {'coeff': '+1', 'unit': 'MINUTES'}, # ~10 slots
    },
    '30MINUTES': {
        'histogram-widget': {'coeff': '+20', 'unit': 'SECONDS'},
        'timeline-widget': {'coeff': '+20', 'unit': 'SECONDS'},
        'bucket-widget': {'coeff': '+20', 'unit': 'SECONDS'},
        'bar-widget': {'coeff': '+20', 'unit': 'SECONDS'},
        'facet-widget': {'coeff': '+5', 'unit': 'MINUTES'},
    },
    '1HOURS': {
        'histogram-widget': {'coeff': '+30', 'unit': 'SECONDS'},
        'timeline-widget': {'coeff': '+30', 'unit': 'SECONDS'},
        'bucket-widget': {'coeff': '+30', 'unit': 'SECONDS'},
        'bar-widget': {'coeff': '+30', 'unit': 'SECONDS'},
        'facet-widget': {'coeff': '+10', 'unit': 'MINUTES'},
    },
    '12HOURS': {
        'histogram-widget': {'coeff': '+7', 'unit': 'MINUTES'},
        'timeline-widget': {'coeff': '+7', 'unit': 'MINUTES'},
        'bucket-widget': {'coeff': '+7', 'unit': 'MINUTES'},
        'bar-widget': {'coeff': '+7', 'unit': 'MINUTES'},
        'facet-widget': {'coeff': '+1', 'unit': 'HOURS'},
    },
    '1DAYS': {
        'histogram-widget': {'coeff': '+15', 'unit': 'MINUTES'},
        'timeline-widget': {'coeff': '+15', 'unit': 'MINUTES'},
        'bucket-widget': {'coeff': '+15', 'unit': 'MINUTES'},
        'bar-widget': {'coeff': '+15', 'unit': 'MINUTES'},
        'facet-widget': {'coeff': '+3', 'unit': 'HOURS'},
    },
    '2DAYS': {
        'histogram-widget': {'coeff': '+30', 'unit': 'MINUTES'},
        'timeline-widget': {'coeff': '+30', 'unit': 'MINUTES'},
        'bucket-widget': {'coeff': '+30', 'unit': 'MINUTES'},
        'bar-widget': {'coeff': '+30', 'unit': 'MINUTES'},
        'facet-widget': {'coeff': '+6', 'unit': 'HOURS'},
    },
    '7DAYS': {
        'histogram-widget': {'coeff': '+3', 'unit': 'HOURS'},
        'timeline-widget': {'coeff': '+3', 'unit': 'HOURS'},
        'bucket-widget': {'coeff': '+3', 'unit': 'HOURS'},
        'bar-widget': {'coeff': '+3', 'unit': 'HOURS'},
        'facet-widget': {'coeff': '+1', 'unit': 'DAYS'},
    },
    '1MONTHS': {
        'histogram-widget': {'coeff': '+12', 'unit': 'HOURS'},
        'timeline-widget': {'coeff': '+12', 'unit': 'HOURS'},
        'bucket-widget': {'coeff': '+12', 'unit': 'HOURS'},
        'bar-widget': {'coeff': '+12', 'unit': 'HOURS'},
        'facet-widget': {'coeff': '+5', 'unit': 'DAYS'},
    },
    '3MONTHS': {
        'histogram-widget': {'coeff': '+1', 'unit': 'DAYS'},
        'timeline-widget': {'coeff': '+1', 'unit': 'DAYS'},
        'bucket-widget': {'coeff': '+1', 'unit': 'DAYS'},
        'bar-widget': {'coeff': '+1', 'unit': 'DAYS'},
        'facet-widget': {'coeff': '+30', 'unit': 'DAYS'},
    },
    '1YEARS': {
        'histogram-widget': {'coeff': '+3', 'unit': 'DAYS'},
        'timeline-widget': {'coeff': '+3', 'unit': 'DAYS'},
        'bucket-widget': {'coeff': '+3', 'unit': 'DAYS'},
        'bar-widget': {'coeff': '+3', 'unit': 'DAYS'},
        'facet-widget': {'coeff': '+12', 'unit': 'MONTHS'},
    },
    '2YEARS': {
        'histogram-widget': {'coeff': '+7', 'unit': 'DAYS'},
        'timeline-widget': {'coeff': '+7', 'unit': 'DAYS'},
        'bucket-widget': {'coeff': '+7', 'unit': 'DAYS'},
        'bar-widget': {'coeff': '+7', 'unit': 'DAYS'},
        'facet-widget': {'coeff': '+3', 'unit': 'MONTHS'},
    },
    '10YEARS': {
        'histogram-widget': {'coeff': '+1', 'unit': 'MONTHS'},
        'timeline-widget': {'coeff': '+1', 'unit': 'MONTHS'},
        'bucket-widget': {'coeff': '+1', 'unit': 'MONTHS'},
        'bar-widget': {'coeff': '+1', 'unit': 'MONTHS'},
        'facet-widget': {'coeff': '+1', 'unit': 'YEARS'},
    }
}