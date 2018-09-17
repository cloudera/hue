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

from django.core.cache import cache
from django.utils.translation import ugettext as _

from desktop.lib.rest.http_client import RestException, HttpClient
from desktop.lib.rest.resource import Resource
from desktop.lib.i18n import smart_unicode

from metadata.conf import MANAGER, get_navigator_auth_username, get_navigator_auth_password


LOG = logging.getLogger(__name__)
VERSION = 'v19'


class ManagerApiException(Exception):
  def __init__(self, message=None):
    self.message = message or _('No error message, please check the logs.')

  def __str__(self):
    return str(self.message)

  def __unicode__(self):
    return smart_unicode(self.message)


class ManagerApi(object):
  """
  https://cloudera.github.io/cm_api/
  """

  def __init__(self, user=None, security_enabled=False, ssl_cert_ca_verify=False):
    self._api_url = '%s/%s' % (MANAGER.API_URL.get().strip('/'), VERSION)
    self._username = get_navigator_auth_username()
    self._password = get_navigator_auth_password()

    self.user = user
    self._client = HttpClient(self._api_url, logger=LOG)

    if security_enabled:
      self._client.set_kerberos_auth()
    else:
      self._client.set_basic_auth(self._username, self._password)

    self._client.set_verify(ssl_cert_ca_verify)
    self._root = Resource(self._client)


  def has_service(self, service_name, cluster_name=None):
    cluster = self._get_cluster(cluster_name)
    try:
      services = self._root.get('clusters/%(cluster_name)s/serviceTypes' % {
        'cluster_name': cluster['name'],
        'service_name': service_name
      })['items']

      return service_name in services
    except RestException, e:
      raise ManagerApiException(e)


  def tools_echo(self):
    try:
      params = (
        ('message', 'hello'),
      )

      LOG.info(params)
      return self._root.get('tools/echo', params=params)
    except RestException, e:
      raise ManagerApiException(e)


  def get_kafka_brokers(self, cluster_name=None):
    try:
      cluster = self._get_cluster(cluster_name)
      services = self._root.get('clusters/%(name)s/services' % cluster)['items']

      service = [service for service in services if service['type'] == 'KAFKA'][0]
      broker_hosts = self._get_roles(cluster['name'], service['name'], 'KAFKA_BROKER')
      broker_hosts_ids = [broker_host['hostRef']['hostId'] for broker_host in broker_hosts]

      hosts = self._root.get('hosts')['items']
      brokers_hosts = [host['hostname'] + ':9092' for host in hosts if host['hostId'] in broker_hosts_ids]

      return ','.join(brokers_hosts)
    except RestException, e:
      raise ManagerApiException(e)


  def get_kudu_master(self, cluster_name=None):
    try:
      cluster = self._get_cluster(cluster_name)
      services = self._root.get('clusters/%(name)s/services' % cluster)['items']

      service = [service for service in services if service['type'] == 'KUDU'][0]
      master = self._get_roles(cluster['name'], service['name'], 'KUDU_MASTER')[0]

      master_host = self._root.get('hosts/%(hostId)s' % master['hostRef'])

      return master_host['hostname']
    except RestException, e:
      raise ManagerApiException(e)


  def get_kafka_topics(self, broker_host):
    try:
      client = HttpClient('http://%s:24042' % broker_host, logger=LOG)
      root = Resource(client)

      return root.get('/api/topics')
    except RestException, e:
      raise ManagerApiException(e)


  def update_flume_config(self, cluster_name, config):
    service = 'FLUME-1'
    cluster = self._get_cluster(cluster_name)
    roleConfigGroup = [role['roleConfigGroupRef']['roleConfigGroupName'] for role in self._get_roles(cluster['name'], service, 'AGENT')]
    data = {
      u'items': [{
        u'url': u'/api/v8/clusters/%(cluster_name)s/services/%(service)s/roleConfigGroups/%(roleConfigGroups)s/config?message=Updated%20service%20and%20role%20type%20configurations.'.replace('%(cluster_name)s', urllib.quote(cluster['name'])).replace('%(service)s', service).replace('%(roleConfigGroups)s', roleConfigGroup[0]),
        u'body': {
          u'items': [
            {u'name': u'agent_config_file', u'value': config}
          ]
        },
        u'contentType': u'application/json',
        u'method': u'PUT'
      }]
    }

    return self.batch(
      items=data
    )


  def update_and_refresh_flume(self, cluster_name, config):
    service = 'FLUME-1'
    cluster = self._get_cluster(cluster_name)
    roles = [role['name'] for role in self._get_roles(cluster['name'], service, 'AGENT')]

    self.update_flume_config(cluster['name'], config)
    return self.refresh_configs(cluster['name'], service, roles)


  def refresh_configs(self, cluster_name, service=None, roles=None):
    try:
      if service is None:
        return self._root.post('clusters/%(cluster_name)s/commands/refresh' % {'cluster_name': cluster_name}, contenttype="application/json")
      elif roles is None:
        return self._root.post('clusters/%(cluster_name)s/services/%(service)s/roleCommands/refresh' % {'cluster_name': cluster_name, 'service': service}, contenttype="application/json")
      else:
        return self._root.post(
            'clusters/%(cluster_name)s/services/%(service)s/roleCommands/refresh' % {'cluster_name': cluster_name, 'service': service},
            data=json.dumps({"items": roles}),
            contenttype="application/json"
        )
    except RestException, e:
      raise ManagerApiException(e)


  def batch(self, items):
    try:
      return self._root.post('batch', data=json.dumps(items), contenttype='application/json')
    except RestException, e:
      raise ManagerApiException(e)


  def _get_cluster(self, cluster_name=None):
    clusters = self._root.get('clusters/')['items']

    if cluster_name is not None:
      cluster = [cluster for cluster in clusters if cluster['name'] == cluster_name][0]
    else:
      cluster = clusters[0]

    return cluster


  def _get_roles(self, cluster_name, service_name, role_type):
    roles = self._root.get('clusters/%(cluster_name)s/services/%(service_name)s/roles' % {'cluster_name': cluster_name, 'service_name': service_name})['items']
    return [role for role in roles if role['type'] == role_type]
