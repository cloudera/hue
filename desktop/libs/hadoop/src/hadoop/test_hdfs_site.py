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

from hadoop import hdfs_site


LOG = logging.getLogger(__name__)


def test_hdfs_site():
  hadoop_home = tempfile.mkdtemp()
  finish = None

  try:
    xml = """<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>

<configuration>
  <property>
    <name>sentry.authorization-provider.hdfs-path-prefixes</name>
    <value>/path/a,/path/b,/path/1</value>
  </property>
  <property>
    <name>sentry.hdfs.integration.path.prefixes</name>
    <value>/path/c,/path/d,/path/1</value>
  </property>
</configuration>
    """
    file(os.path.join(hadoop_home, 'hdfs-site.xml'), 'w').write(xml)

    finish = conf.HDFS_CLUSTERS['default'].HADOOP_CONF_DIR.set_for_testing(hadoop_home)
    hdfs_site.reset()

    assert_equal(set(hdfs_site.get_nn_sentry_prefixes()), set(['/path/a', '/path/b', '/path/c', '/path/d', '/path/1']))
    assert_equal(len(hdfs_site.get_nn_sentry_prefixes()), 5)
  finally:
    hdfs_site.reset()
    if finish:
      finish()
