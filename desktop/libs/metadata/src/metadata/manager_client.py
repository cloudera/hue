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

import base64
import json
import logging
import urllib
import urllib2

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


  def get_spark_history_server_configs(self, cluster_name=None):
    service_name = "SPARK_ON_YARN"
    shs_role_type = "SPARK_YARN_HISTORY_SERVER"

    try:
      cluster = self._get_cluster(cluster_name)
      services = self._root.get('clusters/%(cluster_name)s/services' % {
        'cluster_name': cluster['name'],
        'service_name': service_name
      })['items']

      service_display_names = [service['displayName'] for service in services if service['type'] == service_name]


      if service_display_names:
        spark_service_display_name = service_display_names[0]

        servers = self._root.get('clusters/%(cluster_name)s/services/%(spark_service_display_name)s/roles' % {
          'cluster_name': cluster['name'],
          'spark_service_display_name': spark_service_display_name
        })['items']

        shs_server_names = [server['name'] for server in servers if server['type'] == shs_role_type]
        shs_server_name = shs_server_names[0] if shs_server_names else None
        shs_server_hostRef = [server['hostRef'] for server in servers if server['type'] == shs_role_type]
        shs_server_hostId = shs_server_hostRef[0]['hostId'] if shs_server_hostRef else None

        if shs_server_name and shs_server_hostId:
          shs_server_configs = self._root.get('clusters/%(cluster_name)s/services/%(spark_service_display_name)s/roles/%(shs_server_name)s/config' % {
            'cluster_name': cluster['name'],
            'spark_service_display_name': spark_service_display_name,
            'shs_server_name': shs_server_name
          }, params={'view': 'full'})['items']
          return shs_server_hostId, shs_server_configs
    except Exception, e:
      LOG.warn("Check Spark History Server via ManagerApi: %s" % e)

    return None, None

  def get_spark_history_server_url(self, cluster_name=None):
    shs_server_hostId, shs_server_configs = self.get_spark_history_server_configs(cluster_name=cluster_name)

    if shs_server_hostId and shs_server_configs:
      shs_ui_port = None
      shs_ssl_port = None
      shs_ssl_enabled = None
      for config in shs_server_configs:
        if 'relatedName' in config and 'default' in config:
          if config['relatedName'] == 'spark.history.ui.port':
            shs_ui_port = config['default']
          if config['relatedName'] == 'spark.ssl.historyServer.port':
            shs_ssl_port = config['default']
          if config['relatedName'] == 'spark.ssl.historyServer.enabled':
            shs_ssl_enabled = config['default']
      shs_ui_host = self._root.get('hosts/%(hostId)s' % {'hostId': shs_server_hostId})
      shs_ui_hostname = shs_ui_host['hostname'] if shs_ui_host else None

      return self.assemble_shs_url(shs_ui_hostname, shs_ui_port, shs_ssl_port, shs_ssl_enabled)

    return None

  def get_spark_history_server_security_enabled(self, cluster_name=None):
    shs_server_hostId, shs_server_configs = self.get_spark_history_server_configs(cluster_name=cluster_name)

    if shs_server_configs:
      for config in shs_server_configs:
        if 'relatedName' in config and 'default' in config and config['relatedName'] == 'history_server_spnego_enabled':
          shs_security_enabled = config['default']
          return shs_security_enabled and shs_security_enabled == 'true'

    return False

  def assemble_shs_url(self, shs_ui_hostname, shs_ui_port=None, shs_ssl_port=None, shs_ssl_enabled=None):
    if not shs_ui_hostname or not shs_ui_port or not shs_ssl_port or not shs_ssl_enabled:
      LOG.warn("Spark conf not found!")
      return None

    protocol = 'https' if shs_ssl_enabled.lower() == 'true' else 'http'
    shs_url = '%(protocol)s://%(hostname)s:%(port)s' % {
      'protocol': protocol,
      'hostname': shs_ui_hostname,
      'port': shs_ssl_port if shs_ssl_enabled.lower() == 'true' else shs_ui_port,
    }

    return shs_url

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

      hosts = self._get_hosts('KAFKA', 'KAFKA_BROKER', cluster_name=cluster_name)

      brokers_hosts = [host['hostname'] + ':9092' for host in hosts]

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


  def update_flume_config(self, cluster_name, config_name, config_value):
    service = 'FLUME-1'
    cluster = self._get_cluster(cluster_name)
    roleConfigGroup = [role['roleConfigGroupRef']['roleConfigGroupName'] for role in self._get_roles(cluster['name'], service, 'AGENT')]
    data = {
      u'items': [{
        u'url': u'/api/v8/clusters/%(cluster_name)s/services/%(service)s/roleConfigGroups/%(roleConfigGroups)s/config?message=Updated%20service%20and%20role%20type%20configurations.'.replace('%(cluster_name)s', urllib.quote(cluster['name'])).replace('%(service)s', service).replace('%(roleConfigGroups)s', roleConfigGroup[0]),
        u'body': {
          u'items': [
            {u'name': config_name, u'value': config_value}
          ]
        },
        u'contentType': u'application/json',
        u'method': u'PUT'
      }]
    }

    return self.batch(
      items=data
    )


  def get_flume_agents(self, cluster_name=None):
    return [host['hostname'] for host in self._get_hosts('FLUME', 'AGENT', cluster_name=cluster_name)]


  def _get_hosts(self, service_name, role_name, cluster_name=None):
    try:
      cluster = self._get_cluster(cluster_name)
      services = self._root.get('clusters/%(name)s/services' % cluster)['items']

      service = [service for service in services if service['type'] == service_name][0]
      hosts = self._get_roles(cluster['name'], service['name'], role_name)
      hosts_ids = [host['hostRef']['hostId'] for host in hosts]

      hosts = self._root.get('hosts')['items']
      return [host for host in hosts if host['hostId'] in hosts_ids]
    except RestException, e:
      raise ManagerApiException(e)


  def refresh_flume(self, cluster_name, restart=False):
    service = 'FLUME-1'
    cluster = self._get_cluster(cluster_name)
    roles = [role['name'] for role in self._get_roles(cluster['name'], service, 'AGENT')]

    if restart:    
      return self.restart_services(cluster['name'], service, roles)
    else:
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


  def restart_services(self, cluster_name, service=None, roles=None):
    try:
      if service is None:
        return self._root.post('clusters/%(cluster_name)s/commands/restart' % {'cluster_name': cluster_name}, contenttype="application/json")
      elif roles is None:
        return self._root.post('clusters/%(cluster_name)s/services/%(service)s/roleCommands/restart' % {'cluster_name': cluster_name, 'service': service}, contenttype="application/json")
      else:
        return self._root.post(
            'clusters/%(cluster_name)s/services/%(service)s/roleCommands/restart' % {'cluster_name': cluster_name, 'service': service},
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


  def get_impalad_config(self, key=None, impalad_host=None, cluster_name=None):
    if not key or not impalad_host:
      return None

    service_name = "IMPALA"
    role_type = 'IMPALAD'

    try:
      cluster = self._get_cluster(cluster_name)
      services = self._root.get('clusters/%(cluster_name)s/services' % {
        'cluster_name': cluster['name'],
        'service_name': service_name
      })['items']

      service_display_names = [service['displayName'] for service in services if service['type'] == service_name]

      hosts = self._root.get('hosts')['items']
      impalad_hostIds = [host['hostId'] for host in hosts if host['hostname'] == impalad_host]

      if impalad_hostIds and service_display_names:
        impalad_hostId = impalad_hostIds[0]
        impala_service_display_name = service_display_names[0]

        servers = self._root.get('clusters/%(cluster_name)s/services/%(spark_service_display_name)s/roles' % {
          'cluster_name': cluster['name'],
          'spark_service_display_name': impala_service_display_name
        })['items']

        impalad_server_names = [server['name'] for server in servers if server['type'] == role_type and server['hostRef']['hostId'] == impalad_hostId]
        impalad_server_name = impalad_server_names[0] if impalad_server_names else None

        if impalad_server_name:
          server_configs = self._root.get('clusters/%(cluster_name)s/services/%(spark_service_display_name)s/roles/%(shs_server_name)s/config' % {
            'cluster_name': cluster['name'],
            'spark_service_display_name': impala_service_display_name,
            'shs_server_name': impalad_server_name
          }, params={'view': 'full'})['items']

          for config in server_configs:
            if 'relatedName' in config and 'value' in config:
              if config['relatedName'] == key:
                return config['value']

    except Exception, e:
      LOG.warn("Get Impala Daemon API configurations via ManangerAPI: %s" % e)

    return None
