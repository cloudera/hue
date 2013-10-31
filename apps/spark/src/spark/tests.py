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


import json
import time

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from nose.tools import assert_true, assert_equal

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access

from spark.models import create_or_update_script, SparkScript
from spark.api import OozieSparkApi, get


class TestSparkBase(object):
  SCRIPT_ATTRS = {
      'id': 1000,
      'name': 'Test',
      'script': 'print "spark"',
      'parameters': [],
      'resources': [],
      'hadoopProperties': []
  }

  def setUp(self):
    self.c = make_logged_in_client(is_superuser=False)
    grant_access("test", "test", "spark")
    self.user = User.objects.get(username='test')

  def create_script(self):
    return create_script(self.user)


def create_script(user, xattrs=None):
  attrs = {'user': user}
  attrs.update(TestSparkBase.SCRIPT_ATTRS)
  if xattrs is not None:
    attrs.update(xattrs)
  return create_or_update_script(**attrs)


class TestMock(TestSparkBase):

  def test_create_script(self):
    spark_script = self.create_script()
    assert_equal('Test', spark_script.dict['name'])

  def test_save(self):
    attrs = {'user': self.user,}
    attrs.update(TestSparkBase.SCRIPT_ATTRS)
    #attrs['type'] = json.dumps(TestSparkBase.SCRIPT_ATTRS['type']) # TODO: when support of Scala + Java
    attrs['parameters'] = json.dumps(TestSparkBase.SCRIPT_ATTRS['parameters'])
    attrs['resources'] = json.dumps(TestSparkBase.SCRIPT_ATTRS['resources'])
    attrs['hadoopProperties'] = json.dumps(TestSparkBase.SCRIPT_ATTRS['hadoopProperties'])

    # Save
    self.c.post(reverse('spark:save'), data=attrs, follow=True)

    # Update
    self.c.post(reverse('spark:save'), data=attrs, follow=True)

  def test_parse_oozie_logs(self):
    api = get(None, None, self.user)

    assert_equal('''Stdoutput aaa''', api._match_logs({'logs': [None, OOZIE_LOGS]}))


OOZIE_LOGS ="""  Log Type: stdout

  Log Length: 58465

  Oozie Launcher starts

  Heart beat
  Starting the execution of prepare actions
  Completed the execution of prepare actions successfully

  Files in current dir:/var/lib/hadoop-yarn/cache/yarn/nm-local-dir/usercache/romain/appcache/application_1383078934625_0050/container_1383078934625_0050_01_000002/.
  ======================
  File: .launch_container.sh.crc
  File: oozie-sharelib-oozie-3.3.2-cdh4.4.0-SNAPSHOT.jar

  Oozie Java/Map-Reduce/Pig action launcher-job configuration
  =================================================================
  Workflow job id   : 0000011-131105103808962-oozie-oozi-W
  Workflow action id: 0000011-131105103808962-oozie-oozi-W@spark

  Classpath         :
  ------------------------
  /var/lib/hadoop-yarn/cache/yarn/nm-local-dir/usercache/romain/appcache/application_1383078934625_0050/container_1383078934625_0050_01_000002
  /etc/hadoop/conf
  /usr/lib/hadoop/hadoop-nfs-2.1.0-cdh5.0.0-SNAPSHOT.jar
  /usr/lib/hadoop/hadoop-common-2.1.0-cdh5.0.0-SNAPSHOT.jar
  ------------------------

  Main class        : org.apache.oozie.action.hadoop.ShellMain

  Maximum output    : 2048

  Arguments         :

  Java System Properties:
  ------------------------
  #
  #Tue Nov 05 14:02:13 ICT 2013
  java.runtime.name=Java(TM) SE Runtime Environment
  oozie.action.externalChildIDs.properties=/var/lib/hadoop-yarn/cache/yarn/nm-local-dir/usercache/romain/appcache/application_1383078934625_0050/container_1383078934625_0050_01_000002/externalChildIds.properties
  sun.boot.library.path=/usr/lib/jvm/java-7-oracle/jre/lib/amd64
  ------------------------

  =================================================================

  >>> Invoking Main class now >>>


  Oozie Shell action configuration
  =================================================================
  Shell configuration:
  --------------------
  dfs.datanode.data.dir : file:///var/lib/hadoop-hdfs/cache/${user.name}/dfs/data
  dfs.namenode.checkpoint.txns : 1000000
  s3.replication : 3
  --------------------

  Current working dir /var/lib/hadoop-yarn/cache/yarn/nm-local-dir/usercache/romain/appcache/application_1383078934625_0050/container_1383078934625_0050_01_000002
  Full Command ..
  -------------------------
  0:spark.sh:
  List of passing environment
  -------------------------
  TERM=xterm:
  JSVC_HOME=/usr/lib/bigtop-utils:
  HADOOP_PREFIX=/usr/lib/hadoop:
  HADOOP_MAPRED_HOME=/usr/lib/hadoop-mapreduce:
  YARN_NICENESS=0:
  =================================================================

  >>> Invoking Shell command line now >>

  Stdoutput aaa
  Exit code of the Shell command 0
  <<< Invocation of Shell command completed <<<


  <<< Invocation of Main class completed <<<


  Oozie Launcher ends

"""
