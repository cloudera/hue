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

import sys
import json
import logging
from builtins import object
from subprocess import call

from django.utils.translation import gettext as _

from desktop.lib.i18n import smart_str
from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest.resource import Resource
from kafka.conf import KAFKA
from libzookeeper.conf import zkensemble

LOG = logging.getLogger()


class KafkaApiException(Exception):
  def __init__(self, message=None):
    self.message = message or _('No error message, please check the logs.')

  def __str__(self):
    return str(self.message)

  def __unicode__(self):
    return smart_str(self.message)


class KafkaApi(object):
  """
  https://github.com/confluentinc/kafka-rest
  """

  def __init__(self, user=None, security_enabled=False, ssl_cert_ca_verify=False):
    self._api_url = KAFKA.API_URL.get().strip('/') if KAFKA.API_URL.get() else ''

    self.user = user
    self._client = HttpClient(self._api_url, logger=LOG)
    self._root = Resource(self._client)

  def topics(self):
    try:
      response = self._root.get('topics')
      return json.loads(response)
    except RestException as e:
      raise KafkaApiException(e)

  def create_topic(self, name, partitions=1, replication_factor=1):
    # Create/delete topics are not available in the REST API.
    # Here only works with hack if command is available on the Hue host.
    try:
      return call(
        'kafka-topics --zookeeper %(zookeeper)s --create --if-not-exists --topic %(name)s --partitions %(partitions)s '
        '--replication-factor %(replication_factor)s' % {
           'zookeeper': zkensemble(),
           'name': name,
           'partitions': partitions,
           'replication_factor': replication_factor
      })
    except RestException as e:
      raise KafkaApiException(e)


class SchemaRegistryApi(object):
  """
  https://github.com/confluentinc/schema-registry
  """

  def __init__(self, user=None, security_enabled=False, ssl_cert_ca_verify=False):
    self._api_url = KAFKA.SCHEMA_REGISTRY_API_URL.get().strip('/') if KAFKA.SCHEMA_REGISTRY_API_URL.get() else ''

    self.user = user
    self._client = HttpClient(self._api_url, logger=LOG)
    self._root = Resource(self._client)

  def subjects(self):
    try:
      response = self._root.get('subjects')
      return json.loads(response)
    except RestException as e:
      raise KafkaApiException(e)

  def subject(self, name):
    try:
      response = self._root.get('subjects/%s/versions/latest' % name)
      return json.loads(response)
    except RestException as e:
      raise KafkaApiException(e)
