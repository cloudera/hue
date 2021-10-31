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

from __future__ import absolute_import
from hadoop import conf
import logging
import os
import sys
import tempfile

from nose.tools import assert_true, assert_equal, assert_false, assert_not_equal, assert_raises

from desktop.models import get_remote_home_storage
from aws.conf import get_region

from hadoop import core_site

if sys.version_info[0] > 2:
  open_file = open
else:
  open_file = file

LOG = logging.getLogger(__name__)


def test_core_site():
  hadoop_home = tempfile.mkdtemp()
  finish = []

  try:
    xml = """<?xml version="1.0"?>
<configuration>
  <property>
    <name>fs.s3a.custom.signers</name>
    <value>RazS3SignerPlugin:org.apache.ranger.raz.hook.s3.RazS3SignerPlugin:org.apache.ranger.raz.hook.s3.RazS3SignerPluginInitializer</value>
  </property>
  <property>
    <name>fs.s3a.s3.signing-algorithm</name>
    <value>RazS3SignerPlugin</value>
  </property>
  <property>
    <name>fs.s3a.delegation.token.binding</name>
    <value>org.apache.ranger.raz.hook.s3.RazDelegationTokenBinding</value>
  </property>
  <property>
    <name>fs.s3a.ext.raz.rest.host.url</name>
    <value>https://gehue-adls-master:6082/</value>
  </property>
  <property>
    <name>fs.s3a.ext.raz.s3.access.cluster.name</name>
    <value>gehue-adls</value>
  </property>
  <property>
    <name>fs.s3a.bucket.gethue-dev.endpoint</name>
    <value>s3.us-west-2.amazonaws.com</value>
  </property>
  <property>    
    <name>fs.azure.ext.raz.rest.host.url</name>    
    <value>https://gehue-adls-master:6082/</value>  
  </property> 
  <property>
    <name>fs.azure.ext.raz.adls.access.cluster.name</name>
    <value>gehue-adls</value>
  </property>
  <property>
    <name>fs.defaultFS</name>
    <value>abfs://data@gethuedevstorage.dfs.core.windows.net/hue-adls</value>
  </property> 
</configuration>
    """
    open_file(os.path.join(hadoop_home, 'core-site.xml'), 'w').write(xml)

    finish = (
      conf.HDFS_CLUSTERS.set_for_testing({'default': {}}),
      conf.HDFS_CLUSTERS['default'].HADOOP_CONF_DIR.set_for_testing(hadoop_home)
    )
    core_site.reset()

    assert_equal(core_site.get_raz_api_url(), 'https://gehue-adls-master:6082/')
    assert_equal(core_site.get_raz_cluster_name(), 'gehue-adls')
    assert_equal(core_site.get_raz_s3_default_bucket(), {'host': 's3.us-west-2.amazonaws.com', 'bucket': 'gethue-dev'})

    assert_equal(core_site.get_default_fs(), 'abfs://data@gethuedevstorage.dfs.core.windows.net/hue-adls')

    assert_equal(get_remote_home_storage(), 's3a://gethue-dev')
    assert_equal(get_region(), 'us-west-2')
  finally:
    core_site.reset()
    for f in finish:
      f()
