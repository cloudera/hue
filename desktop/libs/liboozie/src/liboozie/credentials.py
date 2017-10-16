#!/usr/bin/env python
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

from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


class Credentials(object):
  NAME_TO_CLASS_MAPPING = {
      "hcat": "org.apache.oozie.action.hadoop.HCatCredentials",
      "hive2": "org.apache.oozie.action.hadoop.Hive2Credentials",
      "hbase": "org.apache.oozie.action.hadoop.HbaseCredentials",
  }

  def __init__(self, credentials=None):
    if credentials is None:
      self.credentials = {}
    else:
      self.credentials = credentials

  def fetch(self, oozie_api):
    configuration = oozie_api.get_configuration()
    self.credentials = self._parse_oozie(configuration)

  def _parse_oozie(self, configuration_dic):
    return dict([cred.strip().split('=') for cred in configuration_dic.get('oozie.credentials.credentialclasses', '').strip().split(',') if cred])

  @property
  def class_to_name_credentials(self):
    return dict((v,k) for k, v in self.credentials.iteritems())

  def get_properties(self, hive_properties=None):
    credentials = {}
    from beeswax import hive_site, conf

    if not hasattr(conf.HIVE_SERVER_HOST, 'get'):
      LOG.warn('Could not get all the Oozie credentials: beeswax app is blacklisted.')
    else:
      if hive_properties is None:
        hive_properties = hive_site.get_metastore()
        if hive_properties:
          hive_properties['hive2.server.principal'] = hive_site.get_hiveserver2_kerberos_principal(conf.HIVE_SERVER_HOST.get())

      if not hive_properties:
        hive_properties = {}
        LOG.warn('Could not get all the Oozie credentials: hive-site.xml required on the Hue host.')

      credentials[self.hive_name] = {
        'xml_name': self.hive_name,
        'properties': [
           ('hcat.metastore.uri', hive_properties.get('thrift_uri')),
           ('hcat.metastore.principal', hive_properties.get('kerberos_principal')),
        ]
      }

      credentials[self.hiveserver2_name] = {
        'xml_name': self.hiveserver2_name,
        'properties': [
           ('hive2.jdbc.url', hive_site.hiveserver2_jdbc_url()),
           ('hive2.server.principal', hive_properties.get('hive2.server.principal')),
        ]
      }

    credentials[self.hbase_name] = {
      'xml_name': self.hbase_name,
      'properties': []
    }

    return credentials

  @property
  def hive_name(self):
    return self.class_to_name_credentials.get('org.apache.oozie.action.hadoop.HCatCredentials')

  @property
  def hiveserver2_name(self):
    return self.class_to_name_credentials.get('org.apache.oozie.action.hadoop.Hive2Credentials')

  @property
  def hbase_name(self):
    return self.class_to_name_credentials.get('org.apache.oozie.action.hadoop.HbaseCredentials')
