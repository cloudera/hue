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

from nose.tools import assert_equal, assert_true

import beeswax.conf

from liboozie.credentials import Credentials


LOG = logging.getLogger(__name__)


class TestCredentials():
  CREDENTIALS = {
    "hcat": "org.apache.oozie.action.hadoop.HCatCredentials",
    "hive2": "org.apache.oozie.action.hadoop.Hive2Credentials",
    "hbase": "org.apache.oozie.action.hadoop.HbaseCredentials"
  }

  def test_parse_oozie(self):
    oozie_credentialclasses = """
           hbase=org.apache.oozie.action.hadoop.HbaseCredentials,
           hcat=org.apache.oozie.action.hadoop.HCatCredentials,
           hive2=org.apache.oozie.action.hadoop.Hive2Credentials
    """
    oozie_config = {'oozie.credentials.credentialclasses': oozie_credentialclasses}

    creds = Credentials()

    assert_equal({
        'hive2': 'org.apache.oozie.action.hadoop.Hive2Credentials',
        'hbase': 'org.apache.oozie.action.hadoop.HbaseCredentials',
        'hcat': 'org.apache.oozie.action.hadoop.HCatCredentials'
      }, creds._parse_oozie(oozie_config)
    )

  def test_gen_properties(self):
    creds = Credentials(credentials=TestCredentials.CREDENTIALS.copy())

    hive_properties = {
      'thrift_uri': 'thrift://hue-koh-chang:9999',
      'kerberos_principal': 'hive',
      'hive2.server.principal': 'hive',
    }

    finish = (
      beeswax.conf.HIVE_SERVER_HOST.set_for_testing('hue-koh-chang'),
      beeswax.conf.HIVE_SERVER_PORT.set_for_testing(12345),
    )

    try:
      assert_equal({
          'hcat': {
            'xml_name': 'hcat',
            'properties': [
                ('hcat.metastore.uri', 'thrift://hue-koh-chang:9999'),
                ('hcat.metastore.principal', 'hive')
            ]},
         'hive2': {
            'xml_name': 'hive2',
            'properties': [
                ('hive2.jdbc.url', 'jdbc:hive2://hue-koh-chang:12345/default'),
                ('hive2.server.principal', 'hive')
          ]},
         'hbase': {
             'xml_name': 'hbase',
             'properties': []
          }
        }, creds.get_properties(hive_properties))
    finally:
      for f in finish:
        f()
