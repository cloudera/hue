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

from nose.tools import assert_equal, assert_true, assert_false

from django.contrib.auth.models import User
from django.urls import reverse

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access

from indexer.solr_client import SolrClient


class TestSolrClient:

  @classmethod
  def setup_class(cls):
    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "indexer")

    global _IS_SOLR_CLOUD
    global _IS_SOLR_6_OR_MORE
    global _IS_SOLR_WITH_HDFS
    global _ZOOKEEPER_HOST

    SolrClient._reset_properties()


  def test_get_ensemble_cdh_solr(self):
    try:
      client = SolrClient(self.user, api=MockSolrCdhCloudHdfsApi())

      assert_true(client.is_solr_cloud_mode())
      assert_false(client.is_solr_six_or_more())
      assert_true(client.is_solr_with_hdfs())
      assert_equal('hue.com:2181/solr', client.get_zookeeper_host())
    finally:
      SolrClient._reset_properties()


  def test_get_ensemble_upstream_solr(self):
    try:
      client = SolrClient(self.user, api=MockSolrUpstreamCloudApi())

      assert_true(client.is_solr_cloud_mode())
      assert_true(client.is_solr_six_or_more())
      assert_false(client.is_solr_with_hdfs())
      assert_equal('localhost:9983', client.get_zookeeper_host())
    finally:
      SolrClient._reset_properties()


class MockSolrCdhCloudHdfsApi():
  def info_system(self):
    return {"responseHeader":{"status":0,"QTime":5},"mode":"solrcloud","lucene":{"solr-spec-version":"4.10.3","solr-impl-version":"4.10.3-cdh5.13.0-SNAPSHOT Unversioned directory - jenkins - 2017-06-23 06:37:12","lucene-spec-version":"4.10.3","lucene-impl-version":"4.10.3-cdh5.13.0-SNAPSHOT Unversioned directory - jenkins - 2017-06-23 06:29:40"},"jvm":{"version":"1.7.0_67 24.65-b04","name":"Oracle Corporation Java HotSpot(TM) 64-Bit Server VM","spec":{"vendor":"Oracle Corporation","name":"Java Platform API Specification","version":"1.7"},"jre":{"vendor":"Oracle Corporation","version":"1.7.0_67"},"vm":{"vendor":"Oracle Corporation","name":"Java HotSpot(TM) 64-Bit Server VM","version":"24.65-b04"},"processors":4,"memory":{"free":"454.3 MB","total":"574.2 MB","max":"574.2 MB","used":"119.9 MB (%20.9)","raw":{"free":476406496,"total":602144768,"max":602144768,"used":125738272,"used%":20.88173453995701}},"jmx":{"bootclasspath":"/usr/java/jdk1.7.0_67-cloudera/jre/lib/resources.jar:/usr/java/jdk1.7.0_67-cloudera/jre/lib/rt.jar:/usr/java/jdk1.7.0_67-cloudera/jre/lib/sunrsasign.jar:/usr/java/jdk1.7.0_67-cloudera/jre/lib/jsse.jar:/usr/java/jdk1.7.0_67-cloudera/jre/lib/jce.jar:/usr/java/jdk1.7.0_67-cloudera/jre/lib/charsets.jar:/usr/java/jdk1.7.0_67-cloudera/jre/lib/jfr.jar:/usr/java/jdk1.7.0_67-cloudera/jre/classes","classpath":"/opt/cloudera/parcels/CDH-5.13.0-1.cdh5.13.0.p0.24/lib/bigtop-tomcat/bin/bootstrap.jar","commandLineArgs":["-Djava.util.logging.config.file=/var/lib/solr/tomcat-deployment/conf/logging.properties","-Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager","-Djdk.tls.ephemeralDHKeySize=2048","-Djava.net.preferIPv4Stack=true","-Dsolr.hdfs.blockcache.enabled=true","-Dsolr.hdfs.blockcache.direct.memory.allocation=true","-Dsolr.hdfs.blockcache.blocksperbank=16384","-Dsolr.hdfs.blockcache.slab.count=1","-DzkClientTimeout=15000","-Xms622854144","-Xmx622854144","-XX:MaxDirectMemorySize=810549248","-XX:+UseParNewGC","-XX:+UseConcMarkSweepGC","-XX:CMSInitiatingOccupancyFraction=70","-XX:+CMSParallelRemarkEnabled","-Dsolr.ulog.tlogDfsReplication=2","-XX:+HeapDumpOnOutOfMemoryError","-XX:HeapDumpPath=/tmp/SOLR-1_SOLR-1-SOLR_SERVER-9a1415864f5a8fab60dc81b173a83bfb_pid12692.hprof","-XX:OnOutOfMemoryError=/usr/lib64/cmf/service/common/killparent.sh","-DzkHost=hue.com:2181/solr","-Dsolr.solrxml.location=zookeeper","-Dsolr.hdfs.home=hdfs://hue.com:8020/solr","-Dsolr.hdfs.confdir=/run/cloudera-scm-agent/process/35-solr-SOLR_SERVER/hadoop-conf","-Dsolr.authentication.simple.anonymous.allowed=true","-Dsolr.security.proxyuser.hue.hosts=*","-Dsolr.security.proxyuser.hue.groups=*","-Dhost=hue.com","-Djetty.port=8983","-Dsolr.host=hue.com","-Dsolr.port=8983","-DuseCachedStatsBetweenGetMBeanInfoCalls=true","-DdisableSolrFieldCacheMBeanEntryListJmx=true","-Dlog4j.configuration=file:///run/cloudera-scm-agent/process/35-solr-SOLR_SERVER/log4j.properties","-Dsolr.log=/var/log/solr","-Dsolr.admin.port=8984","-Dsolr.tomcat.backlog=4096","-Dsolr.tomcat.connectionTimeout=180000","-Dsolr.tomcat.keepAliveTimeout=600000","-Dsolr.tomcat.maxKeepAliveRequests=-1","-Dsolr.max.connector.thread=10000","-Dsolr.tomcat.connectionLinger=300","-Dsolr.tomcat.bufferSize=131072","-Dsolr.solr.home=/var/lib/solr","-Djava.endorsed.dirs=/opt/cloudera/parcels/CDH-5.13.0-1.cdh5.13.0.p0.24/lib/bigtop-tomcat/endorsed","-Dcatalina.base=/var/lib/solr/tomcat-deployment","-Dcatalina.home=/opt/cloudera/parcels/CDH-5.13.0-1.cdh5.13.0.p0.24/lib/bigtop-tomcat","-Djava.io.tmpdir=/var/lib/solr/"],"startTime":"2017-06-26T12:38:28.188Z","upTimeMS":19292106}},"system":{"name":"Linux","version":"3.10.0-514.21.1.el7.x86_64","arch":"amd64","systemLoadAverage":0.6,"committedVirtualMemorySize":3105255424,"freePhysicalMemorySize":1010851840,"freeSwapSpaceSize":0,"processCpuTime":41140000000,"totalPhysicalMemorySize":27396968448,"totalSwapSpaceSize":0,"openFileDescriptorCount":56,"maxFileDescriptorCount":32768,"uname":"Linux hue.com 3.10.0-514.21.1.el7.x86_64 #1 SMP Thu May 25 17:04:51 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux\n","uptime":" 11:00:00 up  6:03,  0 users,  load average: 0.60, 1.33, 1.43\n"}}


class MockSolrUpstreamCloudApi():
  def info_system(self):
    return {"responseHeader":{"status":0,"QTime":27},"mode":"solrcloud","zkHost":"localhost:9983","solr_home":"/home/romain/apps/solr-6.7.0-315/server/solr","lucene":{"solr-spec-version":"6.7.0","solr-impl-version":"6.7.0-315 d9d3369cd755160a1187604e353dcb915f65cf3d - jenkins - 2017-06-22 23:27:25","lucene-spec-version":"6.7.0","lucene-impl-version":"6.7.0-315 d9d3369cd755160a1187604e353dcb915f65cf3d - jenkins - 2017-06-22 23:22:48"},"jvm":{"version":"1.8.0_131 25.131-b11","name":"Oracle Corporation Java HotSpot(TM) 64-Bit Server VM","spec":{"vendor":"Oracle Corporation","name":"Java Platform API Specification","version":"1.8"},"jre":{"vendor":"Oracle Corporation","version":"1.8.0_131"},"vm":{"vendor":"Oracle Corporation","name":"Java HotSpot(TM) 64-Bit Server VM","version":"25.131-b11"},"processors":8,"memory":{"free":"347.5 MB","total":"490.7 MB","max":"490.7 MB","used":"143.2 MB (%29.2)","raw":{"free":364345024,"total":514523136,"max":514523136,"used":150178112,"used%":29.187824898898228}},"jmx":{"bootclasspath":"/usr/lib/jvm/java-8-oracle/jre/lib/resources.jar:/usr/lib/jvm/java-8-oracle/jre/lib/rt.jar:/usr/lib/jvm/java-8-oracle/jre/lib/sunrsasign.jar:/usr/lib/jvm/java-8-oracle/jre/lib/jsse.jar:/usr/lib/jvm/java-8-oracle/jre/lib/jce.jar:/usr/lib/jvm/java-8-oracle/jre/lib/charsets.jar:/usr/lib/jvm/java-8-oracle/jre/lib/jfr.jar:/usr/lib/jvm/java-8-oracle/jre/classes","classpath":"/home/romain/apps/solr-6.7.0-315/server/lib/gmetric4j-1.0.7.jar:/home/romain/apps/solr-6.7.0-315/server/lib/javax.servlet-api-3.1.0.jar:/home/romain/apps/solr-6.7.0-315/server/lib/jetty-continuation-9.3.14.v20161028.jar:/home/romain/apps/solr-6.7.0-315/server/lib/jetty-deploy-9.3.14.v20161028.jar:/home/romain/apps/solr-6.7.0-315/server/lib/jetty-http-9.3.14.v20161028.jar:/home/romain/apps/solr-6.7.0-315/server/lib/jetty-io-9.3.14.v20161028.jar:/home/romain/apps/solr-6.7.0-315/server/lib/jetty-jmx-9.3.14.v20161028.jar:/home/romain/apps/solr-6.7.0-315/server/lib/jetty-rewrite-9.3.14.v20161028.jar:/home/romain/apps/solr-6.7.0-315/server/lib/jetty-security-9.3.14.v20161028.jar:/home/romain/apps/solr-6.7.0-315/server/lib/jetty-server-9.3.14.v20161028.jar:/home/romain/apps/solr-6.7.0-315/server/lib/jetty-servlet-9.3.14.v20161028.jar:/home/romain/apps/solr-6.7.0-315/server/lib/jetty-servlets-9.3.14.v20161028.jar:/home/romain/apps/solr-6.7.0-315/server/lib/jetty-util-9.3.14.v20161028.jar:/home/romain/apps/solr-6.7.0-315/server/lib/jetty-webapp-9.3.14.v20161028.jar:/home/romain/apps/solr-6.7.0-315/server/lib/jetty-xml-9.3.14.v20161028.jar:/home/romain/apps/solr-6.7.0-315/server/lib/metrics-core-3.2.2.jar:/home/romain/apps/solr-6.7.0-315/server/lib/metrics-ganglia-3.2.2.jar:/home/romain/apps/solr-6.7.0-315/server/lib/metrics-graphite-3.2.2.jar:/home/romain/apps/solr-6.7.0-315/server/lib/metrics-jetty9-3.2.2.jar:/home/romain/apps/solr-6.7.0-315/server/lib/metrics-jvm-3.2.2.jar:/home/romain/apps/solr-6.7.0-315/server/lib/ext/jcl-over-slf4j-1.7.7.jar:/home/romain/apps/solr-6.7.0-315/server/lib/ext/jul-to-slf4j-1.7.7.jar:/home/romain/apps/solr-6.7.0-315/server/lib/ext/log4j-1.2.17.jar:/home/romain/apps/solr-6.7.0-315/server/lib/ext/slf4j-api-1.7.7.jar:/home/romain/apps/solr-6.7.0-315/server/lib/ext/slf4j-log4j12-1.7.7.jar:/home/romain/apps/solr-6.7.0-315/server/resources","commandLineArgs":["-Xms512m","-Xmx512m","-XX:NewRatio=3","-XX:SurvivorRatio=4","-XX:TargetSurvivorRatio=90","-XX:MaxTenuringThreshold=8","-XX:+UseConcMarkSweepGC","-XX:+UseParNewGC","-XX:ConcGCThreads=4","-XX:ParallelGCThreads=4","-XX:+CMSScavengeBeforeRemark","-XX:PretenureSizeThreshold=64m","-XX:+UseCMSInitiatingOccupancyOnly","-XX:CMSInitiatingOccupancyFraction=50","-XX:CMSMaxAbortablePrecleanTime=6000","-XX:+CMSParallelRemarkEnabled","-XX:+ParallelRefProcEnabled","-XX:-OmitStackTraceInFastThrow","-verbose:gc","-XX:+PrintHeapAtGC","-XX:+PrintGCDetails","-XX:+PrintGCDateStamps","-XX:+PrintGCTimeStamps","-XX:+PrintTenuringDistribution","-XX:+PrintGCApplicationStoppedTime","-Xloggc:/home/romain/apps/solr-6.7.0-315/server/logs/solr_gc.log","-XX:+UseGCLogFileRotation","-XX:NumberOfGCLogFiles=9","-XX:GCLogFileSize=20M","-DzkClientTimeout=15000","-DzkRun","-Dsolr.log.dir=/home/romain/apps/solr-6.7.0-315/server/logs","-Djetty.port=8983","-DSTOP.PORT=7983","-DSTOP.KEY=solrrocks","-Duser.timezone=UTC","-Djetty.home=/home/romain/apps/solr-6.7.0-315/server","-Dsolr.solr.home=/home/romain/apps/solr-6.7.0-315/server/solr","-Dsolr.install.dir=/home/romain/apps/solr-6.7.0-315","-Xss256k","-Dsolr.jetty.https.port=8983","-Dsolr.log.muteconsole","-XX:OnOutOfMemoryError=/home/romain/apps/solr-6.7.0-315/bin/oom_solr.sh 8983 /home/romain/apps/solr-6.7.0-315/server/logs"],"startTime":"2017-06-26T06:24:23.913Z","upTimeMS":11754607}},"system":{"name":"Linux","arch":"amd64","availableProcessors":8,"systemLoadAverage":0.86,"version":"3.13.0-119-generic","committedVirtualMemorySize":6303285248,"freePhysicalMemorySize":282312704,"freeSwapSpaceSize":0,"processCpuLoad":0.0,"processCpuTime":54960000000,"systemCpuLoad":0.0,"totalPhysicalMemorySize":16439906304,"totalSwapSpaceSize":0,"maxFileDescriptorCount":4096,"openFileDescriptorCount":201,"uname":"Linux unreal 3.13.0-119-generic #166-Ubuntu SMP Wed May 3 12:18:55 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux\n","uptime":" 10:59:00 up 6 days,  3:59,  7 users,  load average: 0.86, 0.69, 0.68\n"}}
