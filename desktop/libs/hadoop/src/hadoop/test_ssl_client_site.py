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

import conf
import logging
import os
import tempfile

from nose.tools import assert_true, assert_equal, assert_false, assert_not_equal, assert_raises

from hadoop import ssl_client_site


LOG = logging.getLogger(__name__)


def test_ssl_client_site():
  hadoop_home = tempfile.mkdtemp()
  finish = None

  try:
    xml = """<?xml version="1.0" encoding="UTF-8"?>

<configuration>
  <property>
    <name>ssl.client.truststore.location</name>
    <value>/etc/cdep-ssl-conf/CA_STANDARD/truststore.jks</value>
  </property>
  <property>
    <name>ssl.client.truststore.password</name>
    <value>cloudera</value>
  </property>
  <property>
    <name>ssl.client.truststore.type</name>
    <value>jks</value>
  </property>
  <property>
    <name>ssl.client.truststore.reload.interval</name>
    <value>10000</value>
  </property>
</configuration>

    """
    file(os.path.join(hadoop_home, 'ssl-client.xml'), 'w').write(xml)

    finish = conf.HDFS_CLUSTERS['default'].HADOOP_CONF_DIR.set_for_testing(hadoop_home)
    ssl_client_site.reset()

    assert_equal('/etc/cdep-ssl-conf/CA_STANDARD/truststore.jks', ssl_client_site.get_trustore_location())
  finally:
    ssl_client_site.reset()
    if finish:
      finish()
