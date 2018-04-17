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

import logging

from django.core.cache import cache
from django.utils.translation import ugettext as _

from desktop.lib.rest.http_client import RestException, HttpClient
from desktop.lib.rest.resource import Resource
from desktop.lib.i18n import smart_unicode
from metadata.conf import MANAGER


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
    self._username = 'hue' #get_navigator_auth_username()
    self._password = 'hue' #get_navigator_auth_password()

    self.user = user
    self._client = HttpClient(self._api_url, logger=LOG)

    if security_enabled:
      self._client.set_kerberos_auth()
    else:
      self._client.set_basic_auth(self._username, self._password)

    self._client.set_verify(ssl_cert_ca_verify)
    self._root = Resource(self._client)


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
      clusters = self._root.get('clusters/')['items']

      if len(clusters) > 1:
        cluster = [cluster for cluster in clusters if cluster['name'] == cluster_name]
      else:
        cluster = clusters[0]

      services = self._root.get('clusters/%(name)s/services' % cluster)['items']
      kafka_service = [service for service in services if service['type'] == 'KAFKA'][0]

      kafka_roles = self._root.get('clusters/%(name)s/services/%(kafka_service)s/roles' % {'name': cluster['name'], 'kafka_service': kafka_service['name']})['items']
      kafka_broker_hostids = [broker_hostid['hostRef']['hostId'] for broker_hostid in kafka_roles if  broker_hostid['type'] == 'KAFKA_BROKER']

      hosts = self._root.get('hosts')['items']
      kafka_brokers_hosts = [host['hostname'] + ':9092' for host in hosts if host['hostId'] in kafka_broker_hostids]

      return ','.join(kafka_brokers_hosts)
    except RestException, e:
      raise ManagerApiException(e)
