#!/usr/bin/env python
## -*- coding: utf-8 -*-
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
import logging
import re
import os
import StringIO
import shutil
import tempfile
import zipfile
from datetime import datetime

from itertools import chain

from nose.plugins.skip import SkipTest
from nose.plugins.attrib import attr
from nose.tools import raises, assert_true, assert_false, assert_equal, assert_not_equal
from django.contrib.auth.models import User
from django.urls import reverse

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access, add_permission, add_to_group, reformat_json, reformat_xml
from desktop.models import Document, Document2
import desktop.views as views

from hadoop import cluster as originalCluster
from hadoop.pseudo_hdfs4 import is_live_cluster
from jobsub.models import OozieDesign, OozieMapreduceAction
from liboozie import oozie_api
from liboozie.conf import OOZIE_URL
from liboozie.oozie_api_tests import OozieServerProvider
from liboozie.types import WorkflowList, Workflow as OozieWorkflow, Coordinator as OozieCoordinator,\
  Bundle as OozieBundle, CoordinatorList, WorkflowAction, BundleList

from oozie.conf import ENABLE_CRON_SCHEDULING, ENABLE_V2
from oozie.models import Dataset, Workflow, Node, Kill, Link, Job, Coordinator, History,\
  find_parameters, NODE_TYPES, Bundle
from oozie.models2 import _get_hiveserver2_url
from oozie.utils import workflow_to_dict, model_to_dict, smart_path, contains_symlink, convert_to_server_timezone
from oozie.importlib.workflows import import_workflow
from oozie.importlib.jobdesigner import convert_jobsub_design


LOG = logging.getLogger(__name__)


_INITIALIZED = False


class MockOozieApi:
  JSON_WORKFLOW_LIST = [{u'status': u'RUNNING', u'run': 0, u'startTime': u'Mon, 30 Jul 2012 22:35:48 GMT', u'appName': u'WordCount1', u'lastModTime': u'Mon, 30 Jul 2012 22:37:00 GMT', u'actions': [], u'acl': None, u'appPath': None, u'externalId': 'job_201208072118_0044', u'consoleUrl': u'http://runreal:11000/oozie?job=0000012-120725142744176-oozie-oozi-W', u'conf': None, u'parentId': None, u'createdTime': u'Mon, 30 Jul 2012 22:35:48 GMT', u'toString': u'Workflow id[0000012-120725142744176-oozie-oozi-W] status[SUCCEEDED]', u'endTime': u'Mon, 30 Jul 2012 22:37:00 GMT', u'id': u'0000012-120725142744176-oozie-oozi-W', u'group': None, u'user': u'test'},
                        {u'status': u'KILLED', u'run': 0, u'startTime': u'Mon, 30 Jul 2012 22:31:08 GMT', u'appName': u'WordCount2', u'lastModTime': u'Mon, 30 Jul 2012 22:32:20 GMT', u'actions': [], u'acl': None, u'appPath': None, u'externalId': '-', u'consoleUrl': u'http://runreal:11000/oozie?job=0000011-120725142744176-oozie-oozi-W', u'conf': None, u'parentId': None, u'createdTime': u'Mon, 30 Jul 2012 22:31:08 GMT', u'toString': u'Workflow id[0000011-120725142744176-oozie-oozi-W] status[SUCCEEDED]', u'endTime': u'Mon, 30 Jul 2012 22:32:20 GMT', u'id': u'0000011-120725142744176-oozie-oozi-W', u'group': None, u'user': u'test'},
                        {u'status': u'SUCCEEDED', u'run': 0, u'startTime': u'Mon, 30 Jul 2012 22:20:48 GMT', u'appName': u'WordCount3', u'lastModTime': u'Mon, 30 Jul 2012 22:22:00 GMT', u'actions': [], u'acl': None, u'appPath': None, u'externalId': '', u'consoleUrl': u'http://runreal:11000/oozie?job=0000009-120725142744176-oozie-oozi-W', u'conf': None, u'parentId': None, u'createdTime': u'Mon, 30 Jul 2012 22:20:48 GMT', u'toString': u'Workflow id[0000009-120725142744176-oozie-oozi-W] status[SUCCEEDED]', u'endTime': u'Mon, 30 Jul 2012 22:22:00 GMT', u'id': u'0000009-120725142744176-oozie-oozi-W', u'group': None, u'user': u'test'},
                        {u'status': u'SUCCEEDED', u'run': 0, u'startTime': u'Mon, 30 Jul 2012 22:16:58 GMT', u'appName': u'WordCount4', u'lastModTime': u'Mon, 30 Jul 2012 22:18:10 GMT', u'actions': [], u'acl': None, u'appPath': None, u'externalId': None, u'consoleUrl': u'http://runreal:11000/oozie?job=0000008-120725142744176-oozie-oozi-W', u'conf': None, u'parentId': None, u'createdTime': u'Mon, 30 Jul 2012 22:16:58 GMT', u'toString': u'Workflow id[0000008-120725142744176-oozie-oozi-W] status[SUCCEEDED]', u'endTime': u'Mon, 30 Jul 2012 22:18:10 GMT', u'id': u'0000008-120725142744176-oozie-oozi-W', u'group': None, u'user': u'test'},
                        {u'status': u'SUCCEEDED', u'run': 0, u'startTime': u'Fri, 24 Jul 2015 14:56:08 AEST', u'appName': u'WordCount5', u'lastModTime': u'Fri, 24 Jul 2015 14:57:17 AEST', u'actions': [], u'acl': None, u'appPath': None, u'externalId': None, u'consoleUrl': u'http://runreal:11000/oozie?job=0000008-120725142744176-oozie-oozi-W', u'conf': None, u'parentId': None, u'createdTime': u'Fri, 24 Jul 2015 14:56:08 AEST', u'toString': u'Workflow id[0000007-120725142744176-oozie-oozi-W] status[SUCCEEDED]', u'endTime': u'Fri, 24 Jul 2015 14:57:17 AEST', u'id': u'0000007-120725142744176-oozie-oozi-W', u'group': None, u'user': u'test'},
                        {u'status': u'RUNNING', u'run': 0, u'startTime': u'Mon, 30 Jul 2012 22:35:48 GMT', u'appName': u'WordCount1', u'lastModTime': u'Mon, 30 Jul 2012 22:37:00 GMT', u'actions': [], u'acl': None, u'appPath': None, u'externalId': 'job_201208072118_0044', u'consoleUrl': u'http://runreal:11000/oozie?job=0000006-120725142744176-oozie-oozi-W', u'conf': None, u'parentId': None, u'createdTime': u'Mon, 30 Jul 2012 22:35:48 GMT', u'toString': u'Workflow id[0000006-120725142744176-oozie-oozi-W] status[SUCCEEDED]', u'endTime': u'Mon, 30 Jul 2012 22:37:00 GMT', u'id': u'0000006-120725142744176-oozie-oozi-W', u'group': None, u'user': u'test'},
                        {u'status': u'RUNNING', u'run': 0, u'startTime': u'Mon, 30 Jul 2012 22:35:48 GMT', u'appName': u'TestUnicodeParam', u'lastModTime': u'Mon, 30 Jul 2012 22:37:00 GMT', u'actions': [], u'acl': None, u'appPath': None, u'externalId': 'job_201208072118_0044', u'consoleUrl': u'http://runreal:11000/oozie?job=0000005-120725142744176-oozie-oozi-W', u'conf': u'<property><name>unicode_param</name><value>�</value></property>', u'parentId': None, u'createdTime': u'Mon, 30 Jul 2012 22:35:48 GMT', u'toString': u'Workflow id[0000005-120725142744176-oozie-oozi-W] status[SUCCEEDED]', u'endTime': u'Mon, 30 Jul 2012 22:37:00 GMT', u'id': u'0000005-120725142744176-oozie-oozi-W', u'group': None, u'user': u'test'}]

  WORKFLOW_IDS = [wf['id'] for wf in JSON_WORKFLOW_LIST]
  WORKFLOW_DICT = dict([(wf['id'], wf) for wf in JSON_WORKFLOW_LIST])

  JSON_ACTION_COORDINATOR_LIST = [
      {u'status': u'SUCCEEDED', u'toString': u'WorkflowAction name[00000013-120706144403213-oozie-oozi-C@1] status[SUCCEEDED]', u'runConf': None, u'errorMessage': None, u'missingDependencies': u'', u'coordJobId': u'00000013-120706144403213-oozie-oozi-C', u'errorCode': None, u'actionNumber': 1, u'consoleUrl': None, u'nominalTime': u'Mon, 31 Dec 2012 16:00:00 PST', u'externalStatus': u'', u'createdConf': None, u'createdTime': u'Fri, 25 Jan 2013 10:53:39 PST', u'externalId': u'0000035-130124125317829-oozie-oozi-W', u'lastModifiedTime': u'Fri, 25 Jan 2013 10:53:51 PST', u'type': None, u'id': u'00000013-120706144403213-oozie-oozi-C@1', u'trackerUri': None},
      {u'status': u'SUCCEEDED', u'toString': u'WorkflowAction name[00000013-120706144403213-oozie-oozi-C@2] status[SUCCEEDED]', u'runConf': None, u'errorMessage': None, u'missingDependencies': u'', u'coordJobId': u'00000013-120706144403213-oozie-oozi-C', u'errorCode': None, u'actionNumber': 2, u'consoleUrl': None, u'nominalTime': u'Tue, 01 Jan 2013 16:00:00 PST', u'externalStatus': u'', u'createdConf': None, u'createdTime': u'Fri, 25 Jan 2013 10:56:27 PST', u'externalId': u'0000038-130124125317829-oozie-oozi-W', u'lastModifiedTime': u'Fri, 25 Jan 2013 10:56:41 PST', u'type': None, u'id': u'00000013-120706144403213-oozie-oozi-C@2', u'trackerUri': None},
      {u'status': u'SUCCEEDED', u'toString': u'WorkflowAction name[00000013-120706144403213-oozie-oozi-C@3] status[SUCCEEDED]', u'runConf': None, u'errorMessage': None, u'missingDependencies': u'', u'coordJobId': u'00000013-120706144403213-oozie-oozi-C', u'errorCode': None, u'actionNumber': 3, u'consoleUrl': None, u'nominalTime': u'Wed, 02 Jan 2013 16:00:00 PST', u'externalStatus': u'', u'createdConf': None, u'createdTime': u'Fri, 25 Jan 2013 08:59:38 PST', u'externalId': u'0000026-130124125317829-oozie-oozi-W', u'lastModifiedTime': u'Fri, 25 Jan 2013 09:00:05 PST', u'type': None, u'id': u'00000013-120706144403213-oozie-oozi-C@3', u'trackerUri': None},
      {u'status': u'SUCCEEDED', u'toString': u'WorkflowAction name[00000013-120706144403213-oozie-oozi-C@4] status[SUCCEEDED]', u'runConf': None, u'errorMessage': None, u'missingDependencies': u'', u'coordJobId': u'00000013-120706144403213-oozie-oozi-C', u'errorCode': None, u'actionNumber': 4, u'consoleUrl': None, u'nominalTime': u'Thu, 03 Jan 2013 16:00:00 PST', u'externalStatus': u'', u'createdConf': None, u'createdTime': u'Fri, 25 Jan 2013 10:53:39 PST', u'externalId': u'0000037-130124125317829-oozie-oozi-W', u'lastModifiedTime': u'Fri, 25 Jan 2013 10:54:17 PST', u'type': None, u'id': u'00000013-120706144403213-oozie-oozi-C@4', u'trackerUri': None}
  ]

  JSON_COORDINATOR_LIST = [{u'startTime': u'Sun, 01 Jul 2012 00:00:00 GMT', u'actions': [], u'frequency': 1, u'concurrency': 1, u'pauseTime': None, u'group': None, u'toString': u'Coornidator application id[0000041-120717205528122-oozie-oozi-C] status[RUNNING]', u'consoleUrl': None, u'mat_throttling': 0, u'status': u'RUNNING', u'conf': None, u'user': u'test', u'timeOut': 120, u'coordJobPath': u'hdfs://localhost:8020/user/test/demo2', u'timeUnit': u'DAY', u'coordJobId': u'0000041-120717205528122-oozie-oozi-C', u'coordJobName': u'DailyWordCount1', u'nextMaterializedTime': u'Wed, 04 Jul 2012 00:00:00 GMT', u'coordExternalId': None, u'acl': None, u'lastAction': u'Wed, 04 Jul 2012 00:00:00 GMT', u'executionPolicy': u'FIFO', u'timeZone': u'America/Los_Angeles', u'endTime': u'Wed, 04 Jul 2012 00:00:00 GMT'},
                           {u'startTime': u'Sun, 01 Jul 2012 00:00:00 GMT', u'actions': [], u'frequency': 1, u'concurrency': 1, u'pauseTime': None, u'group': None, u'toString': u'Coornidator application id[0000011-120706144403213-oozie-oozi-C] status[DONEWITHERROR]', u'consoleUrl': None, u'mat_throttling': 0, u'status': u'DONEWITHERROR', u'conf': None, u'user': u'test', u'timeOut': 120, u'coordJobPath': u'hdfs://localhost:8020/user/hue/jobsub/_romain_-design-2', u'timeUnit': u'DAY', u'coordJobId': u'0000011-120706144403213-oozie-oozi-C', u'coordJobName': u'DailyWordCount2', u'nextMaterializedTime': u'Thu, 05 Jul 2012 00:00:00 GMT', u'coordExternalId': None, u'acl': None, u'lastAction': u'Thu, 05 Jul 2012 00:00:00 GMT', u'executionPolicy': u'FIFO', u'timeZone': u'America/Los_Angeles', u'endTime': u'Wed, 04 Jul 2012 18:54:00 GMT'},
                           {u'startTime': u'Sun, 01 Jul 2012 00:00:00 GMT', u'actions': [], u'frequency': 1, u'concurrency': 1, u'pauseTime': None, u'group': None, u'toString': u'Coornidator application id[0000010-120706144403213-oozie-oozi-C] status[DONEWITHERROR]', u'consoleUrl': None, u'mat_throttling': 0, u'status': u'DONEWITHERROR', u'conf': None, u'user': u'test', u'timeOut': 120, u'coordJobPath': u'hdfs://localhost:8020/user/hue/jobsub/_romain_-design-2', u'timeUnit': u'DAY', u'coordJobId': u'0000010-120706144403213-oozie-oozi-C', u'coordJobName': u'DailyWordCount3', u'nextMaterializedTime': u'Thu, 05 Jul 2012 00:00:00 GMT', u'coordExternalId': None, u'acl': None, u'lastAction': u'Thu, 05 Jul 2012 00:00:00 GMT', u'executionPolicy': u'FIFO', u'timeZone': u'America/Los_Angeles', u'endTime': u'Wed, 04 Jul 2012 18:54:00 GMT'},
                           {u'startTime': u'Sun, 01 Jul 2012 00:00:00 GMT', u'actions': [], u'frequency': 1, u'concurrency': 1, u'pauseTime': None, u'group': None, u'toString': u'Coornidator application id[0000009-120706144403213-oozie-oozi-C] status[DONEWITHERROR]', u'consoleUrl': None, u'mat_throttling': 0, u'status': u'DONEWITHERROR', u'conf': None, u'user': u'test', u'timeOut': 120, u'coordJobPath': u'hdfs://localhost:8020/user/hue/jobsub/_romain_-design-2', u'timeUnit': u'DAY', u'coordJobId': u'0000009-120706144403213-oozie-oozi-C', u'coordJobName': u'DailyWordCount4', u'nextMaterializedTime': u'Thu, 05 Jul 2012 00:00:00 GMT', u'coordExternalId': None, u'acl': None, u'lastAction': u'Thu, 05 Jul 2012 00:00:00 GMT', u'executionPolicy': u'FIFO', u'timeZone': u'America/Los_Angeles', u'endTime': u'Wed, 04 Jul 2012 18:54:00 GMT'},
                           {u'startTime': u'Sun, 01 Jul 2012 00:00:00 GMT', u'actions': [], u'frequency': 1, u'concurrency': 1, u'pauseTime': None, u'group': None, u'toString': u'Coornidator application id[00000012-120706144403213-oozie-oozi-C] status[DONEWITHERROR]', u'consoleUrl': None, u'mat_throttling': 0, u'status': u'DONEWITHERROR', u'conf': None, u'user': u'test', u'timeOut': 120, u'coordJobPath': u'hdfs://localhost:8020/user/hue/jobsub/_romain_-design-2', u'timeUnit': u'DAY', u'coordJobId': u'0000009-120706144403213-oozie-oozi-C', u'coordJobName': u'DåilyWordCount5', u'nextMaterializedTime': u'Thu, 05 Jul 2012 00:00:00 GMT', u'coordExternalId': None, u'acl': None, u'lastAction': u'Thu, 05 Jul 2012 00:00:00 GMT', u'executionPolicy': u'FIFO', u'timeZone': u'America/Los_Angeles', u'endTime': u'Wed, 04 Jul 2012 18:54:00 GMT'},
                           {u'startTime': u'Sun, 01 Jul 2012 00:00:00 GMT', u'actions': JSON_ACTION_COORDINATOR_LIST, u'frequency': 1, u'concurrency': 1, u'pauseTime': None, u'group': None, u'toString': u'Coornidator application id[00000013-120706144403213-oozie-oozi-C] status[DONEWITHERROR]', u'consoleUrl': None, u'mat_throttling': 0, u'status': u'DONEWITHERROR', u'conf': None, u'user': u'test', u'timeOut': 120, u'coordJobPath': u'hdfs://localhost:8020/user/hue/jobsub/_romain_-design-2', u'timeUnit': u'DAY', u'coordJobId': u'00000013-120706144403213-oozie-oozi-C', u'coordJobName': u'DåilyWordCount6', u'nextMaterializedTime': u'Thu, 05 Jul 2012 00:00:00 GMT', u'coordExternalId': None, u'acl': None, u'lastAction': u'Thu, 05 Jul 2012 00:00:00 GMT', u'executionPolicy': u'FIFO', u'timeZone': u'America/Los_Angeles', u'endTime': u'Wed, 04 Jul 2012 18:54:00 GMT'}]
  COORDINATOR_IDS = [coord['coordJobId'] for coord in JSON_COORDINATOR_LIST]
  COORDINATOR_DICT = dict([(coord['coordJobId'], coord) for coord in JSON_COORDINATOR_LIST])

  JSON_BUNDLE_LIST = [
     {u'status': u'SUCCEEDED', u'toString': u'Bundle id[0000021-130210132208494-oozie-oozi-B] status[SUCCEEDED]', u'group': None, u'conf': u'<configuration>\r\n  <property>\r\n    <name>oozie.bundle.application.path</name>\r\n    <value>hdfs://localhost:8020/user/hue/oozie/workspaces/_romain_-oozie-22-1360636939.69</value>\r\n  </property>\r\n  <property>\r\n    <name>user.name</name>\r\n    <value>romain</value>\r\n  </property>\r\n  <property>\r\n    <name>oozie.use.system.libpath</name>\r\n    <value>true</value>\r\n  </property>\r\n  <property>\r\n    <name>nameNode</name>\r\n    <value>hdfs://localhost:8020</value>\r\n  </property>\r\n  <property>\r\n    <name>wf_application_path</name>\r\n    <value>hdfs://localhost:8020/user/hue/oozie/deployments/_romain_-oozie-5-1360649203.07</value>\r\n  </property>\r\n  <property>\r\n    <name>jobTracker</name>\r\n    <value>localhost:8021</value>\r\n  </property>\r\n  <property>\r\n    <name>hue-id-b</name>\r\n    <value>22</value>\r\n  </property>\r\n</configuration>', u'bundleJobName': u'MyBundle1', u'startTime': None, u'bundleCoordJobs': [], u'kickoffTime': u'Mon, 11 Feb 2013 08:33:00 PST', u'acl': None, u'bundleJobPath': u'hdfs://localhost:8020/user/hue/oozie/workspaces/_romain_-oozie-22-1360636939.69', u'createdTime': u'Mon, 11 Feb 2013 22:06:44 PST', u'timeOut': 0, u'consoleUrl': None, u'bundleExternalId': None, u'timeUnit': u'NONE', u'pauseTime': None, u'bundleJobId': u'0000021-130210132208494-oozie-oozi-B', u'endTime': None, u'user': u'test'},
     {u'status': u'KILLED', u'toString': u'Bundle id[0000020-130210132208494-oozie-oozi-B] status[KILLED]', u'group': None, u'conf': u'<configuration>\r\n  <property>\r\n    <name>oozie.bundle.application.path</name>\r\n    <value>hdfs://localhost:8020/user/hue/oozie/workspaces/_romain_-oozie-22-1360636939.69</value>\r\n  </property>\r\n  <property>\r\n    <name>user.name</name>\r\n    <value>romain</value>\r\n  </property>\r\n  <property>\r\n    <name>oozie.use.system.libpath</name>\r\n    <value>true</value>\r\n  </property>\r\n  <property>\r\n    <name>nameNode</name>\r\n    <value>hdfs://localhost:8020</value>\r\n  </property>\r\n  <property>\r\n    <name>wf_application_path</name>\r\n    <value>hdfs://localhost:8020/user/hue/oozie/deployments/_romain_-oozie-5-1360648977.2</value>\r\n  </property>\r\n  <property>\r\n    <name>jobTracker</name>\r\n    <value>localhost:8021</value>\r\n  </property>\r\n  <property>\r\n    <name>hue-id-b</name>\r\n    <value>22</value>\r\n  </property>\r\n</configuration>', u'bundleJobName': u'MyBundle2', u'startTime': None, u'bundleCoordJobs': [], u'kickoffTime': u'Mon, 11 Feb 2013 08:33:00 PST', u'acl': None, u'bundleJobPath': u'hdfs://localhost:8020/user/hue/oozie/workspaces/_romain_-oozie-22-1360636939.69', u'createdTime': u'Mon, 11 Feb 2013 22:02:58 PST', u'timeOut': 0, u'consoleUrl': None, u'bundleExternalId': None, u'timeUnit': u'NONE', u'pauseTime': None, u'bundleJobId': u'0000020-130210132208494-oozie-oozi-B', u'endTime': None, u'user': u'test'},
     {u'status': u'KILLED', u'toString': u'Bundle id[0000019-130210132208494-oozie-oozi-B] status[KILLED]', u'group': None, u'conf': u'<configuration>\r\n  <property>\r\n    <name>oozie.bundle.application.path</name>\r\n    <value>hdfs://localhost:8020/user/hue/oozie/workspaces/_romain_-oozie-22-1360636939.69</value>\r\n  </property>\r\n  <property>\r\n    <name>user.name</name>\r\n    <value>romain</value>\r\n  </property>\r\n  <property>\r\n    <name>oozie.use.system.libpath</name>\r\n    <value>true</value>\r\n  </property>\r\n  <property>\r\n    <name>nameNode</name>\r\n    <value>hdfs://localhost:8020</value>\r\n  </property>\r\n  <property>\r\n    <name>wf_application_path</name>\r\n    <value>hdfs://localhost:8020/user/hue/oozie/deployments/_romain_-oozie-5-1360639372.41</value>\r\n  </property>\r\n  <property>\r\n    <name>jobTracker</name>\r\n    <value>localhost:8021</value>\r\n  </property>\r\n  <property>\r\n    <name>hue-id-b</name>\r\n    <value>22</value>\r\n  </property>\r\n</configuration>', u'bundleJobName': u'MyBundle3', u'startTime': None, u'bundleCoordJobs': [], u'kickoffTime': u'Mon, 11 Feb 2013 08:33:00 PST', u'acl': None, u'bundleJobPath': u'hdfs://localhost:8020/user/hue/oozie/workspaces/_romain_-oozie-22-1360636939.69', u'createdTime': u'Mon, 11 Feb 2013 19:22:53 PST', u'timeOut': 0, u'consoleUrl': None, u'bundleExternalId': None, u'timeUnit': u'NONE', u'pauseTime': None, u'bundleJobId': u'0000019-130210132208494-oozie-oozi-B', u'endTime': None, u'user': u'test'}
  ]
  BUNDLE_IDS = [bundle['bundleJobId'] for bundle in JSON_BUNDLE_LIST]
  BUNDLE_DICT = dict([(bundle['bundleJobId'], bundle) for bundle in JSON_BUNDLE_LIST])

  WORKFLOW_ACTION = {u'status': u'OK', u'retries': 0, u'transition': u'end', u'stats': None, u'startTime': u'Fri, 10 Aug 2012 05:24:21 GMT', u'toString': u'Action name[WordCount] status[OK]', u'cred': u'null', u'errorMessage': None, u'errorCode': None, u'consoleUrl': u'http://localhost:50030/jobdetails.jsp?jobid=job_201208072118_0044', u'externalId': u'job_201208072118_0044', u'externalStatus': u'SUCCEEDED', u'conf': u'<map-reduce xmlns="uri:oozie:workflow:0.4">\r\n  <job-tracker>localhost:8021</job-tracker>\r\n  <name-node>hdfs://localhost:8020</name-node>\r\n  <configuration>\r\n    <property>\r\n      <name>mapred.mapper.regex</name>\r\n      <value>dream</value>\r\n    </property>\r\n    <property>\r\n      <name>mapred.input.dir</name>\r\n      <value>/user/test/words/20120702</value>\r\n    </property>\r\n    <property>\r\n      <name>mapred.output.dir</name>\r\n      <value>/user/test/out/rrwords/20120702</value>\r\n    </property>\r\n    <property>\r\n      <name>mapred.mapper.class</name>\r\n      <value>org.apache.hadoop.mapred.lib.RegexMapper</value>\r\n    </property>\r\n    <property>\r\n      <name>mapred.combiner.class</name>\r\n      <value>org.apache.hadoop.mapred.lib.LongSumReducer</value>\r\n    </property>\r\n    <property>\r\n      <name>mapred.reducer.class</name>\r\n      <value>org.apache.hadoop.mapred.lib.LongSumReducer</value>\r\n    </property>\r\n    <property>\r\n      <name>mapred.output.key.class</name>\r\n      <value>org.apache.hadoop.io.Text</value>\r\n    </property>\r\n    <property>\r\n      <name>mapred.output.value.class</name>\r\n      <value>org.apache.hadoop.io.LongWritable</value>\r\n    </property>\r\n  </configuration>\r\n</map-reduce>', u'type': u'map-reduce', u'trackerUri': u'localhost:8021', u'externalChildIDs': None, u'endTime': u'Fri, 10 Aug 2012 05:24:38 GMT', u'data': None, u'id': u'0000012-120725142744176-oozie-oozi-W@WordCount', u'name': u'WordCount', u'externalChildIDs': u'job_201302280955_0018,job_201302280955_0019,job_201302280955_0020'}

  JSON_ACTION_BUNDLE_LIST = [
      {u'status': u'SUCCEEDED', u'toString': u'WorkflowAction name[0000000-130117135211239-oozie-oozi-C@1] status[SUCCEEDED]', u'runConf': None, u'errorMessage': None, u'missingDependencies': u'', u'coordJobId': u'0000000-130117135211239-oozie-oozi-C', u'errorCode': None, u'actionNumber': 1, u'consoleUrl': None, u'nominalTime': u'Mon, 31 Dec 2012 16:00:00 PST', u'externalStatus': u'', u'createdConf': None, u'createdTime': u'Fri, 25 Jan 2013 10:53:39 PST', u'externalId': u'0000035-130124125317829-oozie-oozi-W', u'lastModifiedTime': u'Fri, 25 Jan 2013 10:53:51 PST', u'type': None, u'id': u'0000000-130117135211239-oozie-oozi-C@1', u'trackerUri': None},
      {u'status': u'SUCCEEDED', u'toString': u'WorkflowAction name[0000000-130117135211239-oozie-oozi-C@2] status[SUCCEEDED]', u'runConf': None, u'errorMessage': None, u'missingDependencies': u'', u'coordJobId': u'0000000-130117135211239-oozie-oozi-C', u'errorCode': None, u'actionNumber': 2, u'consoleUrl': None, u'nominalTime': u'Tue, 01 Jan 2013 16:00:00 PST', u'externalStatus': u'', u'createdConf': None, u'createdTime': u'Fri, 25 Jan 2013 10:56:27 PST', u'externalId': u'0000038-130124125317829-oozie-oozi-W', u'lastModifiedTime': u'Fri, 25 Jan 2013 10:56:41 PST', u'type': None, u'id': u'0000000-130117135211239-oozie-oozi-C@2', u'trackerUri': None},
      {u'status': u'SUCCEEDED', u'toString': u'WorkflowAction name[0000000-130117135211239-oozie-oozi-C@3] status[SUCCEEDED]', u'runConf': None, u'errorMessage': None, u'missingDependencies': u'', u'coordJobId': u'0000000-130117135211239-oozie-oozi-C', u'errorCode': None, u'actionNumber': 3, u'consoleUrl': None, u'nominalTime': u'Wed, 02 Jan 2013 16:00:00 PST', u'externalStatus': u'', u'createdConf': None, u'createdTime': u'Fri, 25 Jan 2013 08:59:38 PST', u'externalId': u'0000026-130124125317829-oozie-oozi-W', u'lastModifiedTime': u'Fri, 25 Jan 2013 09:00:05 PST', u'type': None, u'id': u'0000000-130117135211239-oozie-oozi-C@3', u'trackerUri': None},
      {u'status': u'SUCCEEDED', u'toString': u'WorkflowAction name[0000000-130117135211239-oozie-oozi-C@4] status[SUCCEEDED]', u'runConf': None, u'errorMessage': None, u'missingDependencies': u'', u'coordJobId': u'0000000-130117135211239-oozie-oozi-C', u'errorCode': None, u'actionNumber': 4, u'consoleUrl': None, u'nominalTime': u'Thu, 03 Jan 2013 16:00:00 PST', u'externalStatus': u'', u'createdConf': None, u'createdTime': u'Fri, 25 Jan 2013 10:53:39 PST', u'externalId': u'0000037-130124125317829-oozie-oozi-W', u'lastModifiedTime': u'Fri, 25 Jan 2013 10:54:17 PST', u'type': None, u'id': u'0000000-130117135211239-oozie-oozi-C@4', u'trackerUri': None}
  ]
  BUNDLE_ACTION = {u'startTime': u'Mon, 31 Dec 2012 16:00:00 PST', u'actions': [], u'frequency': 1, u'concurrency': 1, u'pauseTime': None, u'group': None, u'toString': u'Coordinator application id[0000022-130210132208494-oozie-oozi-C] status[SUCCEEDED]', u'consoleUrl': None, u'mat_throttling': 12, u'status': u'SUCCEEDED', u'conf': u'<configuration>\r\n  <property>\r\n    <name>oozie.coord.application.path</name>\r\n    <value>hdfs://localhost:8020/user/hue/oozie/deployments/_romain_-oozie-6-1360649203.56</value>\r\n  </property>\r\n  <property>\r\n    <name>oozie.bundle.application.path</name>\r\n    <value>hdfs://localhost:8020/user/hue/oozie/workspaces/_romain_-oozie-22-1360636939.69</value>\r\n  </property>\r\n  <property>\r\n    <name>market</name>\r\n    <value>France</value>\r\n  </property>\r\n  <property>\r\n    <name>user.name</name>\r\n    <value>romain</value>\r\n  </property>\r\n  <property>\r\n    <name>oozie.use.system.libpath</name>\r\n    <value>true</value>\r\n  </property>\r\n  <property>\r\n    <name>oozie.bundle.id</name>\r\n    <value>0000021-130210132208494-oozie-oozi-B</value>\r\n  </property>\r\n  <property>\r\n    <name>nameNode</name>\r\n    <value>hdfs://localhost:8020</value>\r\n  </property>\r\n  <property>\r\n    <name>wf_application_path</name>\r\n    <value>hdfs://localhost:8020/user/hue/oozie/deployments/_romain_-oozie-5-1360649203.07</value>\r\n  </property>\r\n  <property>\r\n    <name>jobTracker</name>\r\n    <value>localhost:8021</value>\r\n  </property>\r\n  <property>\r\n    <name>hue-id-b</name>\r\n    <value>22</value>\r\n  </property>\r\n</configuration>', u'user': u'romain', u'timeOut': 120, u'coordJobPath': u'hdfs://localhost:8020/user/hue/oozie/deployments/_romain_-oozie-6-1360649203.56', u'timeUnit': u'DAY', u'coordJobId': u'0000022-130210132208494-oozie-oozi-C', u'coordJobName': u'DailySleep', u'nextMaterializedTime': u'Fri, 04 Jan 2013 16:00:00 PST', u'coordExternalId': None, u'acl': None, u'lastAction': u'Fri, 04 Jan 2013 16:00:00 PST', u'executionPolicy': u'FIFO', u'timeZone': u'America/Los_Angeles', u'endTime': u'Fri, 04 Jan 2013 16:00:00 PST'}

  WORKFLOWS_SLAS = [
      {u'actualDuration': 68406, u'appType': u'WORKFLOW_JOB', u'appName': u'Forks', u'actualStart': u'Fri, 06 Dec 2013 14:01:53 PST', u'jobStatus': u'SUCCEEDED', u'id': u'0000002-131206135002457-oozie-oozi-W', u'expectedDuration': 1800000, u'nominalTime': u'Mon, 17 Jun 2013 17:01:00 PDT', u'slaStatus': u'MISS', u'lastModified': u'Fri, 06 Dec 2013 14:03:05 PST', u'actualEnd': u'Fri, 06 Dec 2013 14:03:01 PST', u'expectedEnd': u'Mon, 17 Jun 2013 17:31:00 PDT', u'expectedStart': u'Mon, 17 Jun 2013 17:11:00 PDT', u'user': u'romain'}
  ]

  def __init__(self, *args, **kwargs):
    self.api_version = 'v2'

  def setuser(self, user):
    pass

  @property
  def security_enabled(self):
    return False

  def submit_job(self, properties):
    return 'ONE-OOZIE-ID-W'

  def get_workflows(self, **kwargs):
    workflows = MockOozieApi.JSON_WORKFLOW_LIST
    user_filters = [val for key, val in kwargs['filters'] if key == 'user']
    if user_filters:
      workflows = filter(lambda wf: wf['user'] == user_filters[0], workflows)

    return WorkflowList(self, {'offset': 0, 'total': 5, 'workflows': workflows})

  def get_coordinators(self, **kwargs):
    coordinatorjobs = MockOozieApi.JSON_COORDINATOR_LIST
    user_filters = [val for key, val in kwargs['filters'] if key == 'user']
    if user_filters:
      coordinatorjobs = filter(lambda coord: coord['user'] == user_filters[0], coordinatorjobs)

    return CoordinatorList(self, {'offset': 0, 'total': 5, 'coordinatorjobs': coordinatorjobs})

  def get_bundles(self, **kwargs):
    bundlejobs = MockOozieApi.JSON_BUNDLE_LIST
    user_filters = [val for key, val in kwargs['filters'] if key == 'user']
    if user_filters:
      bundlejobs = filter(lambda coord: coord['user'] == user_filters[0], bundlejobs)

    return BundleList(self, {'offset': 0, 'total': 4, 'bundlejobs': bundlejobs})

  def get_job(self, job_id):
    if job_id in MockOozieApi.WORKFLOW_DICT:
      return OozieWorkflow(self, MockOozieApi.WORKFLOW_DICT[job_id])
    else:
      return OozieWorkflow(self, {'id': job_id, 'actions': []})

  def get_coordinator(self, job_id, **kwargs):
    if job_id in MockOozieApi.COORDINATOR_DICT:
      return OozieCoordinator(self, MockOozieApi.COORDINATOR_DICT[job_id])
    else:
      return OozieCoordinator(self, {'id': job_id, 'actions': []})

  def get_bundle(self, job_id):
    return OozieBundle(self, MockOozieApi.JSON_BUNDLE_LIST[0])

  def get_action(self, action_id):
    return WorkflowAction(MockOozieApi.WORKFLOW_ACTION)

  def job_control(self, job_id, action, parameters=None):
    return 'Done'

  def get_job_definition(self, jobid):
    if jobid == MockOozieApi.WORKFLOW_IDS[0]:
      return """<workflow-app name="MapReduce" xmlns="uri:oozie:workflow:0.4">
      <start to="Sleep"/>
      <action name="Sleep">
          <map-reduce>
              <job-tracker>${jobTracker}</job-tracker>
              <name-node>${nameNode}</name-node>
              <configuration>
                  <property>
                      <name>mapred.reduce.tasks</name>
                      <value>1</value>
                  </property>
                  <property>
                      <name>sleep.job.reduce.sleep.time</name>
                      <value>${REDUCER_SLEEP_TIME}</value>
                  </property>
              </configuration>
          </map-reduce>
          <ok to="end"/>
          <error to="kill"/>
      </action>
      <kill name="kill">
          <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
      </kill>
      <end name="end"/>
  </workflow-app>"""
    else:
      return """<workflow-app name="MapReduce" xmlns="uri:oozie:workflow:0.4">BAD</workflow-app>"""

  def get_job_log(self, jobid, logfilter=None):
    rows = {}
    rows['INFO'] = '2013-01-08 16:28:06,487  INFO ActionStartXCommand:539 - USER[romain] GROUP[-] TOKEN[] APP[MapReduce] JOB[0000002-130108101138395-oozie-oozi-W] ACTION[0000002-130108101138395-oozie-oozi-W@:start:] Start action [0000002-130108101138395-oozie-oozi-W@:start:] with user-retry state : userRetryCount [0], userRetryMax [0], userRetryInterval [10]'
    rows['DEBUG'] = '2013-01-08 16:28:06,487  DEBUG ActionStartXCommand:539 - USER[romain] GROUP[-] TOKEN[] APP[MapReduce] JOB[0000002-130108101138395-oozie-oozi-W] ACTION[0000002-130108101138395-oozie-oozi-W@:start:] Start action [0000002-130108101138395-oozie-oozi-W@:start:] with user-retry state : userRetryCount [0], userRetryMax [0], userRetryInterval [10]'
    rows['ERROR'] = '2013-01-08 16:28:06,487  ERROR ActionStartXCommand:539 - USER[romain] GROUP[-] TOKEN[] APP[MapReduce] JOB[0000002-130108101138395-oozie-oozi-W] ACTION[0000002-130108101138395-oozie-oozi-W@:start:] Start action [0000002-130108101138395-oozie-oozi-W@:start:] with user-retry state : userRetryCount [0], userRetryMax [0], userRetryInterval [10]'

    filterMap = {}
    for key, val in logfilter:
      filterMap[key] = val

    if 'loglevel' in filterMap:
      row = rows.get(filterMap['loglevel'])
    if 'text' in filterMap:
      row = '' if filterMap['text'] not in row else row
    if 'limit' in filterMap:
      row = ((row + '\n') * int(filterMap['limit'])).strip()

    return row

  def get_oozie_slas(self, **kwargs):
    return MockOozieApi.WORKFLOWS_SLAS

  def get_configuration(self):
    oozie_credentialclasses = """
           hbase=org.apache.oozie.action.hadoop.HbaseCredentials,
           hcat=org.apache.oozie.action.hadoop.HCatCredentials,
           hive2=org.apache.oozie.action.hadoop.Hive2Credentials
    """
    return {
        'oozie.credentials.credentialclasses': oozie_credentialclasses
    }

  def get_job_status(self, job_id):
    return {'status': "RUNNING"}


class MockFs():
  def __init__(self, logical_name=None):

    self.fs_defaultfs = 'hdfs://curacao:8020'
    self.logical_name = logical_name if logical_name else ''
    self.DEFAULT_USER = 'test'

  def setuser(self, user):
    pass

  def join(self, path1, path2):
    return path1 + path2

  def do_as_user(self, username, fn, *args, **kwargs):
    return ''

  def read(self, length=1024*1024):
    return 'data'

  def exists(self, path):
    return True

  def mkdir(self):
    pass

  def chmod(self):
    pass

  def stats(self, path):
    class MockWebHdfsStat(object):
      def __init__(self):
        self.isDir = True
    return MockWebHdfsStat()


class OozieMockBase(object):

  def setUp(self):
    # Beware: Monkey patch Oozie/LibOozie with Mock API
    if not hasattr(oozie_api, 'OriginalOozieApi'):
      oozie_api.OriginalOozieApi = oozie_api.OozieApi
    if not hasattr(Workflow.objects, 'original_check_workspace'):
      Workflow.objects.original_check_workspace = Workflow.objects.check_workspace
    Workflow.objects.check_workspace = lambda a, b: None
    oozie_api.OozieApi = MockOozieApi
    oozie_api._api_cache = None

    self.c = make_logged_in_client(is_superuser=False)
    grant_access("test", "test", "oozie")
    add_to_group("test")
    self.user = User.objects.get(username='test')

    self.wf = create_workflow(self.c, self.user)
    self.original_fs = originalCluster.FS_CACHE["default"]
    originalCluster.FS_CACHE["default"] = MockFs()


  def tearDown(self):
    oozie_api.OozieApi = oozie_api.OriginalOozieApi
    if originalCluster.FS_CACHE is None:
      originalCluster.FS_CACHE = {}
    originalCluster.FS_CACHE["default"] = self.original_fs
    Workflow.objects.check_workspace = Workflow.objects.original_check_workspace
    oozie_api._api_cache = None

    History.objects.all().delete()

    for coordinator in Coordinator.objects.all():
      coordinator.delete(skip_trash=True)
    for bundle in Bundle.objects.all():
      bundle.delete(skip_trash=True)


  def setup_simple_workflow(self):
    """ Creates a linear workflow """
    Link.objects.filter(parent__workflow=self.wf).delete()
    Link(parent=self.wf.start, child=self.wf.end, name="related").save()

    action1 = add_node(self.wf, 'action-name-1', 'mapreduce', [self.wf.start], {
      'description': '',
      'files': '[]',
      'jar_path': '/user/hue/oozie/examples/lib/hadoop-examples.jar',
      'job_properties': '[{"name":"sleep","value":"${SLEEP}"}]',
      'prepares': '[{"value":"${output}","type":"delete"},{"value":"/test","type":"mkdir"}]',
      'archives': '[]',
    })
    action2 = add_node(self.wf, 'action-name-2', 'mapreduce', [action1], {
      'description': '',
      'files': '[]',
      'jar_path': '/user/hue/oozie/examples/lib/hadoop-examples.jar',
      'job_properties': '[{"name":"sleep","value":"${SLEEP}"}]',
      'prepares': '[{"value":"${output}","type":"delete"},{"value":"/test","type":"mkdir"}]',
      'archives': '[]',
    })
    action3 = add_node(self.wf, 'action-name-3', 'mapreduce', [action2], {
      'description': '',
      'files': '[]',
      'jar_path': '/user/hue/oozie/examples/lib/hadoop-examples.jar',
      'job_properties': '[{"name":"sleep","value":"${SLEEP}"}]',
      'prepares': '[{"value":"${output}","type":"delete"},{"value":"/test","type":"mkdir"}]',
      'archives': '[]',
    })

    Link(parent=action3, child=self.wf.end, name="ok").save()


  def setup_forking_workflow(self):
    Link.objects.filter(parent__workflow=self.wf).delete()
    Link(parent=self.wf.start, child=self.wf.end, name="related").save()

    fork1 = add_node(self.wf, 'fork-name-1', 'fork', [self.wf.start])
    action1 = add_node(self.wf, 'action-name-1', 'mapreduce', [fork1])
    action2 = add_node(self.wf, 'action-name-2', 'mapreduce', [fork1])
    join1 = add_node(self.wf, 'join-name-1', 'join', [action1, action2])
    Link(parent=fork1, child=join1, name="related").save()

    action3 = add_node(self.wf, 'action-name-3', 'mapreduce', [join1])
    Link(parent=action3, child=self.wf.end, name="ok").save()


  def create_noop_workflow(self, name='noop-test'):
    Node.objects.filter(workflow__name=name).delete()
    Workflow.objects.filter(name=name).delete()

    if Document.objects.get_docs(self.user, Workflow).filter(name=name).exists():
      for doc in Document.objects.get_docs(self.user, Workflow).filter(name=name):
        if doc.content_object:
          self.c.post(reverse('oozie:delete_workflow') + '?skip_trash=true', {'job_selection': [doc.content_object.id]}, follow=True)
        else:
          doc.delete()

    wf = Workflow.objects.new_workflow(self.user)
    wf.name = name
    wf.save()
    wf.start.workflow = wf
    wf.end.workflow = wf
    wf.start.save()
    wf.end.save()

    Document.objects.link(wf, owner=wf.owner, name=wf.name, description=wf.description)

    Kill.objects.create(name='kill', workflow=wf, node_type=Kill.node_type)
    Link.objects.create(parent=wf.start, child=wf.end, name='related')
    Link.objects.create(parent=wf.start, child=wf.end, name="to")

    return wf


class OozieBase(OozieServerProvider):
  requires_hadoop = True
  integration = True

  def setUp(self):
    OozieServerProvider.setup_class()
    self.c = make_logged_in_client(is_superuser=False)
    self.user = User.objects.get(username="test")
    grant_access("test", "test", "oozie")
    add_to_group("test")
    self.cluster = OozieServerProvider.cluster

    self.install_examples()

  def install_examples(self):
    global _INITIALIZED
    if _INITIALIZED:
      return

    reset = ENABLE_V2.set_for_testing(True) # Somewhere this is reseted
    try:
      self.c.post(reverse('oozie:install_examples'))
    finally:
      reset()

    self.cluster.fs.do_as_user('test', self.cluster.fs.create_home_dir, '/user/test')

    _INITIALIZED = True


  def setup_simple_workflow(self):
    """ Creates a linear workflow """
    Link.objects.filter(parent__workflow=self.wf).delete()
    Link(parent=self.wf.start, child=self.wf.end, name="related").save()
    action1 = add_node(self.wf, 'action-name-1', 'mapreduce', [self.wf.start], {
      'description': '',
      'files': '[]',
      'jar_path': '/user/hue/oozie/examples/lib/hadoop-examples.jar',
      'job_properties': '[{"name":"sleep","value":"${SLEEP}"}]',
      'prepares': '[{"value":"${output}","type":"delete"},{"value":"/test","type":"mkdir"}]',
      'archives': '[]',
    })
    action2 = add_node(self.wf, 'action-name-2', 'mapreduce', [action1], {
      'description': '',
      'files': '[]',
      'jar_path': '/user/hue/oozie/examples/lib/hadoop-examples.jar',
      'job_properties': '[{"name":"sleep","value":"${SLEEP}"}]',
      'prepares': '[{"value":"${output}","type":"delete"},{"value":"/test","type":"mkdir"}]',
      'archives': '[]',
    })
    action3 = add_node(self.wf, 'action-name-3', 'mapreduce', [action2], {
      'description': '',
      'files': '[]',
      'jar_path': '/user/hue/oozie/examples/lib/hadoop-examples.jar',
      'job_properties': '[{"name":"sleep","value":"${SLEEP}"}]',
      'prepares': '[{"value":"${output}","type":"delete"},{"value":"/test","type":"mkdir"}]',
      'archives': '[]',
    })
    Link(parent=action3, child=self.wf.end, name="ok").save()


  def setup_forking_workflow(self):
    """ Creates a workflow with a fork """
    Link.objects.filter(parent__workflow=self.wf).delete()
    Link(parent=self.wf.start, child=self.wf.end, name="related").save()
    fork1 = add_node(self.wf, 'fork-name-1', 'fork', [self.wf.start])
    action1 = add_node(self.wf, 'action-name-1', 'mapreduce', [fork1])
    action2 = add_node(self.wf, 'action-name-2', 'mapreduce', [fork1])
    join1 = add_node(self.wf, 'join-name-1', 'join', [action1, action2])
    Link(parent=fork1, child=join1, name="related").save()
    action3 = add_node(self.wf, 'action-name-3', 'mapreduce', [join1])
    Link(parent=action3, child=self.wf.end, name="ok").save()


class TestAPI(OozieMockBase):

  def setUp(self):
    OozieMockBase.setUp(self)

    self.wf = Workflow.objects.get(name='wf-name-1', managed=True)

  @attr('integration')
  def test_workflow_save(self):
    if is_live_cluster():
      raise SkipTest('HUE-2897: Skipping because DB may not support unicode')

    self.setup_simple_workflow()

    workflow_dict = workflow_to_dict(self.wf)
    workflow_json = json.dumps(workflow_dict)

    response = self.c.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json})
    test_response_json = response.content
    test_response_json_object = json.loads(test_response_json)
    assert_equal(0, test_response_json_object['status'])

    # Change property and save
    workflow_dict = workflow_to_dict(self.wf)
    workflow_dict['description'] = 'Le workflow est testé. 한국어/조선말'
    workflow_json = json.dumps(workflow_dict)

    response = self.c.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json})
    test_response_json = response.content
    test_response_json_object = json.loads(test_response_json)
    assert_equal(0, test_response_json_object['status'])

    wf = Workflow.objects.get(id=self.wf.id)
    assert_equal(u'Le workflow est testé. 한국어/조선말', wf.description)
    assert_equal(self.wf.name, wf.name)

    # Change node and save
    workflow_dict = workflow_to_dict(self.wf)
    workflow_dict['nodes'][2]['name'] = 'new-name'
    node_id = workflow_dict['nodes'][2]['id']
    workflow_json = json.dumps(workflow_dict)

    response = self.c.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json})
    test_response_json = response.content
    test_response_json_object = json.loads(test_response_json)
    assert_equal(0, test_response_json_object['status'])

    node = Node.objects.get(id=node_id)
    assert_equal('new-name', node.name)

  def test_workflow_save_fail(self):
    self.setup_simple_workflow()

    # Bad workflow name
    workflow_dict = workflow_to_dict(self.wf)
    del workflow_dict['name']
    workflow_json = json.dumps(workflow_dict)

    response = self.c.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_equal(400, response.status_code)

    # Bad node name
    workflow_dict = workflow_to_dict(self.wf)
    del workflow_dict['nodes'][2]['name']
    workflow_json = json.dumps(workflow_dict)

    response = self.c.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_equal(400, response.status_code)

    # Bad control node name should still go through
    workflow_dict = workflow_to_dict(self.wf)
    del workflow_dict['nodes'][0]['name']
    workflow_json = json.dumps(workflow_dict)

    response = self.c.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_equal(200, response.status_code)

  def test_workflow_add_subworkflow_node(self):
    wf = self.create_noop_workflow()
    try:
      subworkflow_name = "subworkflow-1"
      subworkflow_id = "subworkflow:1"
      subworkflow_json = """{
        "description": "",
        "workflow": %(workflow)d,
        "child_links": [
          {
            "comment": "",
            "name": "ok",
            "parent": "%(id)s",
            "child": %(end)d
          },
          {
            "comment": "",
            "name": "error",
            "parent": "%(id)s",
            "child": %(kill)d
          }
        ],
        "node_type": "subworkflow",
        "sub_workflow": %(subworkflow)d,
        "job_properties": "[]",
        "name": "%(name)s",
        "id": "%(id)s",
        "propagate_configuration": true
      }"""
      subworkflow_json = subworkflow_json % {
        'workflow': wf.id,
        'subworkflow': self.wf.id,
        'end': wf.end.id,
        'kill': Kill.objects.get(workflow=wf).id,
        'name': subworkflow_name,
        'id': subworkflow_id
      }
      workflow_dict = workflow_to_dict(wf)
      workflow_dict['nodes'].append(json.loads(subworkflow_json))
      workflow_dict['nodes'][0]['child_links'][1]['child'] = subworkflow_id
      del workflow_dict['nodes'][0]['child_links'][1]['id']
      workflow_json = json.dumps(workflow_dict)

      response = self.c.post(reverse('oozie:workflow_save', kwargs={'workflow': wf.pk}), data={'workflow': workflow_json})
      test_response_json = response.content
      test_response_json_object = json.loads(test_response_json)
      assert_equal(0, test_response_json_object['status'], workflow_json)
    finally:
      wf.delete(skip_trash=True)


  def test_workflow_add_mapreduce_node(self):
    wf = self.create_noop_workflow()

    try:
      node_name = "mr-1"
      node_id = "mapreduce:1"
      node_json = """{
        "description": "",
        "workflow": %(workflow)d,
        "child_links": [
          {
            "comment": "",
            "name": "ok",
            "parent": "%(id)s",
            "child": %(end)d
          },
          {
            "comment": "",
            "name": "error",
            "parent": "%(id)s",
            "child": %(kill)d
          }
        ],
        "node_type": "mapreduce",
        "jar_path": "test",
        "job_properties": "[]",
        "files": "[]",
        "archives": "[]",
        "prepares": "[]",
        "name": "%(name)s",
        "id": "%(id)s"
      }"""
      node_json = node_json % {
        'workflow': wf.id,
        'end': wf.end.id,
        'kill': Kill.objects.get(workflow=wf).id,
        'name': node_name,
        'id': node_id
      }
      workflow_dict = workflow_to_dict(wf)
      workflow_dict['nodes'].append(json.loads(node_json))
      workflow_dict['nodes'][0]['child_links'][1]['child'] = node_id
      del workflow_dict['nodes'][0]['child_links'][1]['id']
      workflow_json = json.dumps(workflow_dict)

      response = self.c.post(reverse('oozie:workflow_save', kwargs={'workflow': wf.pk}), data={'workflow': workflow_json})

      test_response_json = response.content
      test_response_json_object = json.loads(test_response_json)
      assert_equal(0, test_response_json_object['status'], workflow_json)
    finally:
      wf.delete(skip_trash=True)

  def test_workflow(self):
    response = self.c.get(reverse('oozie:workflow', kwargs={'workflow': self.wf.pk}))
    test_response_json = response.content
    test_response_json_object = json.loads(test_response_json)

    assert_equal(0, test_response_json_object['status'])

  def test_workflow_fail(self):
    import oozie.views.api
    old_method = oozie.views.api._workflow
    def exception_method(*args, **kwargs):
      logging.error( 'here' )
      raise Exception("arg")
    oozie.views.api._workflow = exception_method

    try:
      response = self.c.get(reverse('oozie:workflow', kwargs={'workflow': self.wf.pk}))
      test_response_json = response.content
      test_response_json_object = json.loads(test_response_json)

      assert_equal(1, test_response_json_object['status'], test_response_json_object)
      assert_equal('arg', test_response_json_object['message'], test_response_json_object)
      assert_equal({}, test_response_json_object['details'], test_response_json_object)
    finally:
      oozie.views.api._workflow = old_method

  def test_workflow_validate_node(self):
    data = {"files":"[\"hive-site.xml\"]","job_xml":"hive-site.xml","description":"Show databases","workflow":17,"child_links":[{"comment":"","name":"ok","id":106,"parent":76,"child":74},{"comment":"","name":"error","id":107,"parent":76,"child":73}],"job_properties":"[{\"name\":\"oozie.hive.defaults\",\"value\":\"hive-site.xml\"}]","node_type":"hive","params":"[{\"value\":\"INPUT=/user/hue/oozie/workspaces/data\",\"type\":\"param\"}]","archives":"[]","node_ptr":76,"prepares":"[]","script_path":"hive.sql","id":76,"name":"Hive"}
    response = self.c.post(reverse('oozie:workflow_validate_node', kwargs={'workflow': self.wf.pk, 'node_type': 'hive'}), data={'node': json.dumps(data)}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    test_response_json = response.content
    test_response_json_object = json.loads(test_response_json)

    assert_equal(0, test_response_json_object['status'])
    assert_true('name' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['name']), test_response_json_object['data'])
    assert_true('description' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['description']), test_response_json_object['data'])
    assert_true('script_path' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['script_path']), test_response_json_object['data'])
    assert_true('job_xml' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['job_xml']), test_response_json_object['data'])
    assert_true('job_properties' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['job_properties']), test_response_json_object['data'])
    assert_true('files' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['files']), test_response_json_object['data'])
    assert_true('params' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['params']), test_response_json_object['data'])
    assert_true('prepares' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['prepares']), test_response_json_object['data'])
    assert_true('archives' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['archives']), test_response_json_object['data'])

  def test_workflow_validate_node_fail(self):
    # Empty files field
    data = {"job_xml":"hive-site.xml","description":"Show databases","workflow":17,"child_links":[{"comment":"","name":"ok","id":106,"parent":76,"child":74},{"comment":"","name":"error","id":107,"parent":76,"child":73}],"job_properties":"[{\"name\":\"oozie.hive.defaults\",\"value\":\"hive-site.xml\"}]","node_type":"hive","params":"[{\"value\":\"INPUT=/user/hue/oozie/workspaces/data\",\"type\":\"param\"}]","archives":"[]","node_ptr":76,"prepares":"[]","script_path":"hive.sql","id":76,"name":"Hive"}
    response = self.c.post(reverse('oozie:workflow_validate_node', kwargs={'workflow': self.wf.pk, 'node_type': 'hive'}), data={'node': json.dumps(data)}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    test_response_json = response.content
    test_response_json_object = json.loads(test_response_json)

    assert_equal(-1, test_response_json_object['status'])
    assert_true('name' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['name']), test_response_json_object['data'])
    assert_true('description' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['description']), test_response_json_object['data'])
    assert_true('script_path' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['script_path']), test_response_json_object['data'])
    assert_true('job_xml' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['job_xml']), test_response_json_object['data'])
    assert_true('job_properties' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['job_properties']), test_response_json_object['data'])
    assert_true('files' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(1, len(test_response_json_object['data']['files']), test_response_json_object['data'])
    assert_true('params' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['params']), test_response_json_object['data'])
    assert_true('prepares' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['prepares']), test_response_json_object['data'])
    assert_true('archives' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['archives']), test_response_json_object['data'])

    # Empty script path
    data = {"files":"[\"hive-site.xml\"]","job_xml":"hive-site.xml","description":"Show databases","workflow":17,"child_links":[{"comment":"","name":"ok","id":106,"parent":76,"child":74},{"comment":"","name":"error","id":107,"parent":76,"child":73}],"job_properties":"[{\"name\":\"oozie.hive.defaults\",\"value\":\"hive-site.xml\"}]","node_type":"hive","params":"[{\"value\":\"INPUT=/user/hue/oozie/workspaces/data\",\"type\":\"param\"}]","archives":"[]","node_ptr":76,"prepares":"[]","script_path":"","id":76,"name":"Hive"}
    response = self.c.post(reverse('oozie:workflow_validate_node', kwargs={'workflow': self.wf.pk, 'node_type': 'hive'}), data={'node': json.dumps(data)}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    test_response_json = response.content
    test_response_json_object = json.loads(test_response_json)

    assert_equal(-1, test_response_json_object['status'])
    assert_true('name' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['name']), test_response_json_object['data'])
    assert_true('description' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['description']), test_response_json_object['data'])
    assert_true('script_path' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(1, len(test_response_json_object['data']['script_path']), test_response_json_object['data'])
    assert_true('job_xml' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['job_xml']), test_response_json_object['data'])
    assert_true('job_properties' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['job_properties']), test_response_json_object['data'])
    assert_true('files' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['files']), test_response_json_object['data'])
    assert_true('params' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['params']), test_response_json_object['data'])
    assert_true('prepares' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['prepares']), test_response_json_object['data'])
    assert_true('archives' in test_response_json_object['data'], test_response_json_object['data'])
    assert_equal(0, len(test_response_json_object['data']['archives']), test_response_json_object['data'])

  def test_workflows(self):
    response = self.c.get(reverse('oozie:workflows') + "?managed=true", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    response_json_dict = json.loads(response.content)
    assert_equal(0, response_json_dict['status'])
    assert_equal(1, len(response_json_dict['data']['workflows']))

    response = self.c.get(reverse('oozie:workflows') + "?managed=false", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    response_json_dict = json.loads(response.content)
    assert_equal(0, response_json_dict['status'])
    assert_equal(0, len(response_json_dict['data']['workflows']))

  def test_workflows_fail(self):
    # Insert an exception
    import oozie.utils
    old_method = oozie.utils.model_to_dict
    def exception_method(*args, **kwargs):
      raise Exception("arg")
    oozie.utils.model_to_dict = exception_method

    try:
      response = self.c.post(reverse('oozie:workflows') + "?managed=true", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
      test_response_json = response.content
      test_response_json_object = json.loads(test_response_json)

      assert_equal(1, test_response_json_object['status'], test_response_json_object)
      assert_equal("Must be GET request.", test_response_json_object['message'], test_response_json_object)
      assert_equal({}, test_response_json_object['details'], test_response_json_object)
    finally:
      oozie.utils.model_to_dict = old_method

  def test_workflow_actions(self):
    response = self.c.get(reverse('oozie:workflow_actions', kwargs={'workflow': self.wf.pk}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    response_json_dict = json.loads(response.content)
    assert_equal(0, response_json_dict['status'])
    assert_equal(0, len(response_json_dict['data']['actions']))

    self.setup_simple_workflow()
    response = self.c.get(reverse('oozie:workflow_actions', kwargs={'workflow': self.wf.pk}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    response_json_dict = json.loads(response.content)
    assert_equal(0, response_json_dict['status'])
    assert_equal(3, len(response_json_dict['data']['actions']))

  def test_workflow_actions_fail(self):
    # Insert an exception
    import oozie.utils
    old_method = oozie.utils.model_to_dict
    def exception_method(*args, **kwargs):
      raise Exception("arg")
    oozie.utils.model_to_dict = exception_method

    try:
      response = self.c.post(reverse('oozie:workflow_actions', kwargs={'workflow': self.wf.pk}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
      test_response_json = response.content
      test_response_json_object = json.loads(test_response_json)

      assert_equal(1, test_response_json_object['status'], test_response_json_object)
      assert_equal("Must be GET request.", test_response_json_object['message'], test_response_json_object)
      assert_equal({}, test_response_json_object['details'], test_response_json_object)
    finally:
      oozie.utils.model_to_dict = old_method

  def test_autocomplete(self):
    response = self.c.get(reverse('oozie:autocomplete_properties'))
    test_response_json = response.content
    assert_true('mapred.input.dir' in test_response_json)


class TestApiPermissionsWithOozie(OozieBase):

  def setUp(self):
    raise SkipTest # Need to move to v2

    OozieBase.setUp(self)

    # When updating wf, update wf_json as well!
    self.wf = Workflow.objects.get(name='MapReduce', managed=True).clone(self.cluster.fs, self.user)

  def test_workflow_save(self):
    # Share
    self.wf.is_shared = True
    self.wf.save()
    Workflow.objects.check_workspace(self.wf, self.cluster.fs)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "oozie")

    workflow_dict = workflow_to_dict(self.wf)
    workflow_json = json.dumps(workflow_dict)

    response = client_not_me.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_equal(401, response.status_code, response.status_code)

    response = self.c.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    test_response_json = response.content
    test_response_json_object = json.loads(test_response_json)
    assert_equal(200, response.status_code, response)
    assert_equal(0, test_response_json_object['status'])

  def test_workflow_save_fail(self):
    # Unshare
    self.wf.is_shared = False
    self.wf.save()
    Workflow.objects.check_workspace(self.wf, self.cluster.fs)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "oozie")

    workflow_dict = workflow_to_dict(self.wf)
    del workflow_dict['name']
    workflow_json = json.dumps(workflow_dict)

    response = client_not_me.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_equal(401, response.status_code, response)

  def test_workflow(self):
    # Share
    self.wf.is_shared = True
    self.wf.doc.get().share_to_default()
    self.wf.save()
    Workflow.objects.check_workspace(self.wf, self.cluster.fs)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='default', recreate=True)
    grant_access("not_me", "test", "oozie")

    response = client_not_me.get(reverse('oozie:workflow', kwargs={'workflow': self.wf.pk}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    test_response_json = response.content
    test_response_json_object = json.loads(test_response_json)
    assert_equal(200, response.status_code, response)
    assert_equal(0, test_response_json_object['status'])

  def test_workflow_fail(self):
    # Unshare
    self.wf.is_shared = False
    self.wf.save()
    Workflow.objects.check_workspace(self.wf, self.cluster.fs)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "oozie")

    response = client_not_me.get(reverse('oozie:workflow', kwargs={'workflow': self.wf.pk}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_equal(401, response.status_code)



class TestEditor(OozieMockBase):

  def setUp(self):
    super(TestEditor, self).setUp()
    self.setup_simple_workflow()


  def test_workflow_name(self):
    try:
      workflow_dict = WORKFLOW_DICT.copy()
      workflow_count = Document.objects.available_docs(Workflow, self.user).count()

      workflow_dict['name'][0] = 'bad workflow name'
      response = self.c.post(reverse('oozie:create_workflow'), workflow_dict, follow=True)
      assert_equal(200, response.status_code)
      assert_equal(workflow_count, Document.objects.available_docs(Workflow, self.user).count(), response)

      workflow_dict['name'][0] = 'good-workflow-name'
      response = self.c.post(reverse('oozie:create_workflow'), workflow_dict, follow=True)
      assert_equal(200, response.status_code)
      assert_equal(workflow_count + 1, Document.objects.available_docs(Workflow, self.user).count(), response)
    finally:
      name = 'bad workflow name'
      if Workflow.objects.filter(name=name).exists():
        Node.objects.filter(workflow__name=name).delete()
        Workflow.objects.filter(name=name).delete()
      name = 'good-workflow-name'
      if Workflow.objects.filter(name=name).exists():
        Node.objects.filter(workflow__name=name).delete()
        Workflow.objects.filter(name=name).delete()


  def test_find_parameters(self):
    data = json.dumps({'sla': [
        {'key': 'enabled', 'value': True},
        {'key': 'nominal-time', 'value': '${time}'},]}
    )
    jobs = [Job(name="$a"),
            Job(name="foo ${b} $$"),
            Job(name="${foo}", description="xxx ${food}", data=data)]

    result = [find_parameters(job, ['name', 'description', 'sla']) for job in jobs]
    assert_equal(set(["b", "foo", "food", "time"]), reduce(lambda x, y: x | set(y), result, set()))


  def test_find_all_parameters(self):
    self.wf.data = json.dumps({'sla': [
        {'key': 'enabled', 'value': False},
        {'key': 'nominal-time', 'value': '${time}'},]}
    )
    assert_equal([{'name': u'output', 'value': u''}, {'name': u'SLEEP', 'value': ''}, {'name': u'market', 'value': u'US'}],
                 self.wf.find_all_parameters())

    self.wf.data = json.dumps({'sla': [
        {'key': 'enabled', 'value': True},
        {'key': 'nominal-time', 'value': '${time}'},]}
    )
    assert_equal([{'name': u'output', 'value': u''}, {'name': u'SLEEP', 'value': ''}, {'name': u'market', 'value': u'US'}, {'name': u'time', 'value': u''}],
                 self.wf.find_all_parameters())


  def test_workflow_has_cycle(self):
    action1 = Node.objects.get(workflow=self.wf, name='action-name-1')
    action3 = Node.objects.get(workflow=self.wf, name='action-name-3')

    assert_false(self.wf.has_cycle())

    ok = action3.get_link('ok')
    ok.child = action1
    ok.save()

    assert_true(self.wf.has_cycle())


  def test_workflow_gen_xml(self):
    assert_equal(
        '<workflow-app name="wf-name-1" xmlns="uri:oozie:workflow:0.4">\n'
        '    <global>\n'
        '        <job-xml>jobconf.xml</job-xml>\n'
        '        <configuration>\n'
        '            <property>\n'
        '                <name>sleep-all</name>\n'
        '                <value>${SLEEP}</value>\n'
        '            </property>\n'
        '         </configuration>\n'
        '    </global>\n'
        '    <start to="action-name-1"/>\n'
        '    <action name="action-name-1">\n'
        '        <map-reduce>\n'
        '           <job-tracker>${jobTracker}</job-tracker>\n'
        '            <name-node>${nameNode}</name-node>\n'
        '            <prepare>\n'
        '                <delete path="${nameNode}${output}"/>\n'
        '                <mkdir path="${nameNode}/test"/>\n'
        '            </prepare>\n'
        '            <configuration>\n'
        '                <property>\n'
        '                    <name>sleep</name>\n'
        '                    <value>${SLEEP}</value>\n'
        '                </property>\n'
        '            </configuration>\n'
        '        </map-reduce>\n'
        '        <ok to="action-name-2"/>\n'
        '        <error to="kill"/>\n'
        '    </action>\n'
        '    <action name="action-name-2">\n'
        '        <map-reduce>\n'
        '            <job-tracker>${jobTracker}</job-tracker>\n'
        '            <name-node>${nameNode}</name-node>\n'
        '            <prepare>\n'
        '                <delete path="${nameNode}${output}"/>\n'
        '                <mkdir path="${nameNode}/test"/>\n'
        '            </prepare>\n'
        '            <configuration>\n'
        '                <property>\n'
        '                    <name>sleep</name>\n'
        '                    <value>${SLEEP}</value>\n'
        '                </property>\n'
        '            </configuration>\n'
        '        </map-reduce>\n'
        '        <ok to="action-name-3"/>\n'
        '        <error to="kill"/>\n'
        '    </action>\n'
        '    <action name="action-name-3">\n'
        '        <map-reduce>\n'
        '            <job-tracker>${jobTracker}</job-tracker>\n'
        '            <name-node>${nameNode}</name-node>\n'
        '            <prepare>\n'
        '                <delete path="${nameNode}${output}"/>\n'
        '                <mkdir path="${nameNode}/test"/>\n'
        '            </prepare>\n'
        '            <configuration>\n'
        '                <property>\n'
        '                    <name>sleep</name>\n'
        '                    <value>${SLEEP}</value>\n'
        '                </property>\n'
        '            </configuration>\n'
        '        </map-reduce>\n'
        '        <ok to="end"/>\n'
        '        <error to="kill"/>\n'
        '    </action>\n'
        '    <kill name="kill">\n'
        '        <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>\n'
        '    </kill>\n'
        '    <end name="end"/>\n'
        '</workflow-app>'.split(), self.wf.to_xml({'output': '/path'}).split())


  def test_workflow_java_gen_xml(self):
    self.wf.node_set.filter(name='action-name-1').delete()

    action1 = add_node(self.wf, 'action-name-1', 'java', [self.wf.start], {
        u'name': 'MyTeragen',
        "description":"Generate N number of records",
        "main_class":"org.apache.hadoop.examples.terasort.TeraGen",
        "args":"1000 ${output_dir}/teragen",
        "files":'["my_file","my_file2"]',
        "job_xml":"",
        "java_opts":"-Dexample-property=natty",
        "jar_path":"/user/hue/oozie/workspaces/lib/hadoop-examples.jar",
        "prepares":'[{"value":"/test","type":"mkdir"}]',
        "archives":'[{"dummy":"","name":"my_archive"},{"dummy":"","name":"my_archive2"}]',
        "capture_output": True,
    })
    Link(parent=action1, child=self.wf.end, name="ok").save()

    xml = self.wf.to_xml({'output_dir': '/path'})

    assert_true("""
    <action name="MyTeragen">
        <java>
            <job-tracker>${jobTracker}</job-tracker>
            <name-node>${nameNode}</name-node>
            <prepare>
                  <mkdir path="${nameNode}/test"/>
            </prepare>
            <main-class>org.apache.hadoop.examples.terasort.TeraGen</main-class>
            <java-opts>-Dexample-property=natty</java-opts>
            <arg>1000</arg>
            <arg>${output_dir}/teragen</arg>
            <file>my_file#my_file</file>
            <file>my_file2#my_file2</file>
            <archive>my_archive#my_archive</archive>
            <archive>my_archive2#my_archive2</archive>
            <capture-output/>
        </java>
        <ok to="end"/>
        <error to="kill"/>
    </action>""" in xml, xml)


  def test_workflow_streaming_gen_xml(self):
    self.wf.node_set.filter(name='action-name-1').delete()

    action1 = add_node(self.wf, 'action-name-1', 'streaming', [self.wf.start], {
        u'name': 'MyStreaming',
        "description": "Generate N number of records",
        "main_class": "org.apache.hadoop.examples.terasort.TeraGen",
        "mapper": "MyMapper",
        "reducer": "MyReducer",
        "files": '["my_file"]',
        "archives":'[{"dummy":"","name":"my_archive"}]',
    })
    Link(parent=action1, child=self.wf.end, name="ok").save()

    xml = self.wf.to_xml()

    assert_true("""
    <action name="MyStreaming">
        <map-reduce>
            <job-tracker>${jobTracker}</job-tracker>
            <name-node>${nameNode}</name-node>
            <streaming>
                <mapper>MyMapper</mapper>
                <reducer>MyReducer</reducer>
            </streaming>
            <file>my_file#my_file</file>
            <archive>my_archive#my_archive</archive>
        </map-reduce>
        <ok to="end"/>
        <error to="kill"/>
    </action>""" in xml, xml)


  def test_workflow_shell_gen_xml(self):
    self.wf.node_set.filter(name='action-name-1').delete()

    action1 = add_node(self.wf, 'action-name-1', 'shell', [self.wf.start], {
        u'job_xml': 'my-job.xml',
        u'files': '["hello.py"]',
        u'name': 'Shell',
        u'job_properties': '[]',
        u'capture_output': True,
        u'command': 'hello.py',
        u'archives': '[]',
        u'prepares': '[]',
        u'params': '[{"value":"World!","type":"argument"}]',
        u'description': 'Execute a Python script printing its arguments'
    })
    Link(parent=action1, child=self.wf.end, name="ok").save()

    xml = self.wf.to_xml()

    assert_true("""
        <shell xmlns="uri:oozie:shell-action:0.1">
            <job-tracker>${jobTracker}</job-tracker>
            <name-node>${nameNode}</name-node>
              <job-xml>my-job.xml</job-xml>
            <exec>hello.py</exec>
              <argument>World!</argument>
            <file>hello.py#hello.py</file>
              <capture-output/>
        </shell>""" in xml, xml)

    action1.capture_output = False
    action1.save()

    xml = self.wf.to_xml()

    assert_true("""
        <shell xmlns="uri:oozie:shell-action:0.1">
            <job-tracker>${jobTracker}</job-tracker>
            <name-node>${nameNode}</name-node>
              <job-xml>my-job.xml</job-xml>
            <exec>hello.py</exec>
              <argument>World!</argument>
            <file>hello.py#hello.py</file>
        </shell>""" in xml, xml)


  def test_workflow_fs_gen_xml(self):
    self.wf.node_set.filter(name='action-name-1').delete()

    action1 = add_node(self.wf, 'action-name-1', 'fs', [self.wf.start], {
        u'name': 'MyFs',
        u'description': 'Execute a Fs action that manage files',
        u'deletes': '[{"name":"/to/delete"},{"name":"to/delete2"}]',
        u'mkdirs': '[{"name":"/to/mkdir"},{"name":"${mkdir2}"}]',
        u'moves': '[{"source":"/to/move/source","destination":"/to/move/destination"},{"source":"/to/move/source2","destination":"/to/move/destination2"}]',
        u'chmods': '[{"path":"/to/chmod","recursive":true,"permissions":"-rwxrw-rw-"},{"path":"/to/chmod2","recursive":false,"permissions":"755"}]',
        u'touchzs': '[{"name":"/to/touchz"},{"name":"/to/touchz2"}]'
    })
    Link(parent=action1, child=self.wf.end, name="ok").save()

    xml = self.wf.to_xml({'mkdir2': '/path'})

    assert_true("""
    <action name="MyFs">
        <fs>
              <delete path='${nameNode}/to/delete'/>
              <delete path='${nameNode}/user/${wf:user()}/to/delete2'/>
              <mkdir path='${nameNode}/to/mkdir'/>
              <mkdir path='${nameNode}${mkdir2}'/>
              <move source='${nameNode}/to/move/source' target='${nameNode}/to/move/destination'/>
              <move source='${nameNode}/to/move/source2' target='${nameNode}/to/move/destination2'/>
              <chmod path='${nameNode}/to/chmod' permissions='-rwxrw-rw-' dir-files='true'/>
              <chmod path='${nameNode}/to/chmod2' permissions='755' dir-files='false'/>
              <touchz path='${nameNode}/to/touchz'/>
              <touchz path='${nameNode}/to/touchz2'/>
        </fs>
        <ok to="end"/>
        <error to="kill"/>
    </action>""" in xml, xml)


  def test_workflow_email_gen_xml(self):
    self.wf.node_set.filter(name='action-name-1').delete()

    action1 = add_node(self.wf, 'action-name-1', 'email', [self.wf.start], {
        u'name': 'MyEmail',
        u'description': 'Execute an Email action',
        u'to': 'hue@hue.org,django@python.org',
        u'cc': '',
        u'subject': 'My subject',
        u'body': 'My body'
    })
    Link(parent=action1, child=self.wf.end, name="ok").save()

    xml = self.wf.to_xml()

    assert_true("""
    <action name="MyEmail">
        <email xmlns="uri:oozie:email-action:0.1">
            <to>hue@hue.org,django@python.org</to>
            <subject>My subject</subject>
            <body>My body</body>
        </email>
        <ok to="end"/>
        <error to="kill"/>
    </action>""" in xml, xml)

    action1.cc = 'lambda@python.org'
    action1.save()

    xml = self.wf.to_xml()

    assert_true("""
    <action name="MyEmail">
        <email xmlns="uri:oozie:email-action:0.1">
            <to>hue@hue.org,django@python.org</to>
              <cc>lambda@python.org</cc>
            <subject>My subject</subject>
            <body>My body</body>
        </email>
        <ok to="end"/>
        <error to="kill"/>
    </action>""" in xml, xml)


  def test_workflow_subworkflow_gen_xml(self):
    self.wf.node_set.filter(name='action-name-1').delete()

    wf_dict = WORKFLOW_DICT.copy()
    wf_dict['name'] = [u'wf-name-2']
    wf2 = create_workflow(self.c, self.user, wf_dict)

    action1 = add_node(self.wf, 'action-name-1', 'subworkflow', [self.wf.start], {
        u'name': 'MySubworkflow',
        u'description': 'Execute a subworkflow action',
        u'sub_workflow': wf2,
        u'propagate_configuration': True,
        u'job_properties': '[{"value":"World!","name":"argument"}]'
    })
    Link(parent=action1, child=self.wf.end, name="ok").save()

    xml = self.wf.to_xml()

    assert_true(re.search(
        '<sub-workflow>\W+'
            '<app-path>\${nameNode}/user/hue/oozie/workspaces/_test_-oozie-(.+?)</app-path>\W+'
            '<propagate-configuration/>\W+'
                '<configuration>\W+'
                '<property>\W+'
                    '<name>argument</name>\W+'
                    '<value>World!</value>\W+'
                '</property>\W+'
            '</configuration>\W+'
        '</sub-workflow>', xml, re.MULTILINE), xml)

    wf2.delete(skip_trash=True)

  def test_workflow_flatten_list(self):
    if is_live_cluster():
      raise SkipTest('HUE-2899: Needs to make results in a consistent order')

    assert_equal('[<Start: start>, <Mapreduce: action-name-1>, <Mapreduce: action-name-2>, <Mapreduce: action-name-3>, '
                 '<Kill: kill>, <End: end>]',
                 str(self.wf.node_list))

    # 1 2
    #  3
    self.setup_forking_workflow()

    assert_equal('[<Start: start>, <Fork: fork-name-1>, <Mapreduce: action-name-1>, <Mapreduce: action-name-2>, '
                 '<Join: join-name-1>, <Mapreduce: action-name-3>, <Kill: kill>, <End: end>]',
                 str(self.wf.node_list))


  def test_workflow_generic_gen_xml(self):
    self.wf.node_set.filter(name='action-name-1').delete()

    action1 = add_node(self.wf, 'action-name-1', 'generic', [self.wf.start], {
        u'name': 'Generic',
        u'description': 'Execute a Generic email action',
        u'xml': """
        <email xmlns="uri:oozie:email-action:0.1">
            <to>hue@hue.org,django@python.org</to>
            <subject>My subject</subject>
            <body>My body</body>
        </email>""",
    })
    Link(parent=action1, child=self.wf.end, name="ok").save()

    xml = self.wf.to_xml()

    assert_true("""
    <action name="Generic">
        <email xmlns="uri:oozie:email-action:0.1">
            <to>hue@hue.org,django@python.org</to>
            <subject>My subject</subject>
            <body>My body</body>
        </email>
        <ok to="end"/>
        <error to="kill"/>
    </action>""" in xml, xml)


  def test_workflow_hive_gen_xml(self):
    self.wf.node_set.filter(name='action-name-1').delete()

    action1 = add_node(self.wf, 'action-name-1', 'hive', [self.wf.start], {
        u'job_xml': 'my-job.xml',
        u'files': '["hello.py"]',
        u'name': 'MyHive',
        u'job_properties': '[]',
        u'script_path': 'hello.sql',
        u'archives': '[]',
        u'prepares': '[]',
        u'params': '[{"value":"World!","type":"argument"}]',
        u'description': ''
    })
    Link(parent=action1, child=self.wf.end, name="ok").save()

    xml = self.wf.to_xml()

    assert_true("""
<workflow-app name="wf-name-1" xmlns="uri:oozie:workflow:0.4">
  <global>
      <job-xml>jobconf.xml</job-xml>
            <configuration>
                <property>
                    <name>sleep-all</name>
                    <value>${SLEEP}</value>
                </property>
            </configuration>
  </global>
    <start to="MyHive"/>
    <action name="MyHive">
        <hive xmlns="uri:oozie:hive-action:0.2">
            <job-tracker>${jobTracker}</job-tracker>
            <name-node>${nameNode}</name-node>
              <job-xml>my-job.xml</job-xml>
            <script>hello.sql</script>
              <argument>World!</argument>
            <file>hello.py#hello.py</file>
        </hive>
        <ok to="end"/>
        <error to="kill"/>
    </action>
    <kill name="kill">
        <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
    </kill>
    <end name="end"/>
</workflow-app>""" in xml, xml)

    import beeswax
    from beeswax.tests import hive_site_xml

    tmpdir = tempfile.mkdtemp()
    saved = None
    try:
      # We just replace the Beeswax conf variable
      class Getter(object):
        def get(self):
          return tmpdir

      xml = hive_site_xml(is_local=False, use_sasl=True, kerberos_principal='hive/_HOST@test.com')
      file(os.path.join(tmpdir, 'hive-site.xml'), 'w').write(xml)

      beeswax.hive_site.reset()
      saved = beeswax.conf.HIVE_CONF_DIR
      beeswax.conf.HIVE_CONF_DIR = Getter()

      action1 = Node.objects.get(workflow=self.wf, name='MyHive')
      action1.credentials = [{'name': 'hcat', 'value': True}, {'name': 'hbase', 'value': False}, {'name': 'hive2', 'value': True}]
      action1.save()

      xml = self.wf.to_xml(mapping={
          'credentials': {
              'hcat': {
                  'xml_name': 'hcat',
                  'properties': [
                      ('hcat.metastore.uri', 'thrift://hue-koh-chang:9999'),
                      ('hcat.metastore.principal', 'hive')
                  ]
              },
              'hive2': {
                  'xml_name': 'hive2',
                  'properties': [
                      ('hive2.jdbc.url', 'jdbc:hive2://hue-koh-chang:8888'),
                      ('hive2.server.principal', 'hive')
                  ]
              }
          }
        }
      )

      assert_true("""
<workflow-app name="wf-name-1" xmlns="uri:oozie:workflow:0.4">
  <global>
      <job-xml>jobconf.xml</job-xml>
            <configuration>
                <property>
                    <name>sleep-all</name>
                    <value>${SLEEP}</value>
                </property>
            </configuration>
  </global>
  <credentials>
    <credential name="hcat" type="hcat">
      <property>
        <name>hcat.metastore.uri</name>
        <value>thrift://hue-koh-chang:9999</value>
      </property>
      <property>
        <name>hcat.metastore.principal</name>
        <value>hive</value>
      </property>
    </credential>
    <credential name="hive2" type="hive2">
      <property>
        <name>hive2.jdbc.url</name>
        <value>jdbc:hive2://hue-koh-chang:8888</value>
      </property>
      <property>
        <name>hive2.server.principal</name>
        <value>hive</value>
      </property>
    </credential>
  </credentials>
    <start to="MyHive"/>
    <action name="MyHive" cred="hcat,hive2">
        <hive xmlns="uri:oozie:hive-action:0.2">
            <job-tracker>${jobTracker}</job-tracker>
            <name-node>${nameNode}</name-node>
              <job-xml>my-job.xml</job-xml>
            <script>hello.sql</script>
              <argument>World!</argument>
            <file>hello.py#hello.py</file>
        </hive>
        <ok to="end"/>
        <error to="kill"/>
    </action>
    <kill name="kill">
        <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
    </kill>
    <end name="end"/>
</workflow-app>""" in xml, xml)

      # Test when no credentials are checked
      action1.credentials = [{'name': 'hcat', 'value': False}, {'name': 'hbase', 'value': False}, {'name': 'hive2', 'value': False}]
      action1.save()

      xml = self.wf.to_xml()

      assert_true("""
<workflow-app name="wf-name-1" xmlns="uri:oozie:workflow:0.4">
  <global>
      <job-xml>jobconf.xml</job-xml>
            <configuration>
                <property>
                    <name>sleep-all</name>
                    <value>${SLEEP}</value>
                </property>
            </configuration>
  </global>
    <start to="MyHive"/>
    <action name="MyHive">
        <hive xmlns="uri:oozie:hive-action:0.2">
            <job-tracker>${jobTracker}</job-tracker>
            <name-node>${nameNode}</name-node>
              <job-xml>my-job.xml</job-xml>
            <script>hello.sql</script>
              <argument>World!</argument>
            <file>hello.py#hello.py</file>
        </hive>
        <ok to="end"/>
        <error to="kill"/>
    </action>
    <kill name="kill">
        <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
    </kill>
    <end name="end"/>
</workflow-app>""" in xml, xml)


    finally:
      beeswax.hive_site.reset()
      if saved is not None:
        beeswax.conf.HIVE_CONF_DIR = saved
      shutil.rmtree(tmpdir)

    self.wf.node_set.filter(name='action-name-1').delete()


  def test_workflow_gen_workflow_sla(self):
    xml = self.wf.to_xml({'output': '/path'})
    assert_false('<sla' in xml, xml)
    assert_false('xmlns="uri:oozie:workflow:0.5"' in xml, xml)
    assert_false('xmlns:sla="uri:oozie:sla:0.2"' in xml, xml)

    sla = self.wf.sla
    sla[0]['value'] = True
    sla[1]['value'] = 'now' # nominal-time
    sla[3]['value'] = '${ 10 * MINUTES}' # should-end
    self.wf.sla = sla
    self.wf.save()

    xml = self.wf.to_xml({'output': '/path'})
    assert_true('xmlns="uri:oozie:workflow:0.5"' in xml, xml)
    assert_true('xmlns:sla="uri:oozie:sla:0.2"' in xml, xml)
    assert_true("""<end name="end"/>
          <sla:info>
            <sla:nominal-time>now</sla:nominal-time>
            <sla:should-end>${ 10 * MINUTES}</sla:should-end>
          </sla:info>
</workflow-app>""" in xml, xml)


  def test_workflow_gen_action_sla(self):
    xml = self.wf.to_xml({'output': '/path'})
    assert_false('<sla' in xml, xml)
    assert_false('xmlns="uri:oozie:workflow:0.5"' in xml, xml)
    assert_false('xmlns:sla="uri:oozie:sla:0.2"' in xml, xml)

    self.wf.node_set.filter(name='action-name-1').delete()

    action1 = add_node(self.wf, 'action-name-1', 'hive', [self.wf.start], {
        u'job_xml': 'my-job.xml',
        u'files': '["hello.py"]',
        u'name': 'MyHive',
        u'job_properties': '[]',
        u'script_path': 'hello.sql',
        u'archives': '[]',
        u'prepares': '[]',
        u'params': '[{"value":"World!","type":"argument"}]',
        u'description': ''
    })
    Link(parent=action1, child=self.wf.end, name="ok").save()

    xml = self.wf.to_xml()

    sla = action1.sla
    sla[0]['value'] = True
    sla[1]['value'] = 'now' # nominal-time
    sla[3]['value'] = '${ 10 * MINUTES}' # should-end
    action1.sla = sla
    action1.save()

    xml = self.wf.to_xml({'output': '/path'})
    assert_true('xmlns="uri:oozie:workflow:0.5"' in xml, xml)
    assert_true('xmlns:sla="uri:oozie:sla:0.2"' in xml, xml)
    assert_true("""<error to="kill"/>
          <sla:info>
            <sla:nominal-time>now</sla:nominal-time>
            <sla:should-end>${ 10 * MINUTES}</sla:should-end>
          </sla:info>
    </action>""" in xml, xml)


  def test_create_coordinator(self):
    create_coordinator(self.wf, self.c, self.user)


  def test_clone_coordinator(self):
    #@TODO@ Prakash fix this test
    raise SkipTest
    coord = create_coordinator(self.wf, self.c, self.user)
    coordinator_count = Document.objects.available_docs(Coordinator, self.user).count()

    response = self.c.post(reverse('oozie:clone_coordinator', args=[coord.id]), {}, follow=True)

    coord2 = Coordinator.objects.latest('id')
    assert_not_equal(coord.id, coord2.id)

    assert_equal(coordinator_count + 1, Document.objects.available_docs(Coordinator, self.user).count(), response)

    assert_equal(coord.dataset_set.count(), coord2.dataset_set.count())
    assert_equal(coord.datainput_set.count(), coord2.datainput_set.count())
    assert_equal(coord.dataoutput_set.count(), coord2.dataoutput_set.count())

    ds_ids = set(coord.dataset_set.values_list('id', flat=True))
    for node in coord2.dataset_set.all():
      assert_false(node.id in ds_ids)

    data_input_ids = set(coord.datainput_set.values_list('id', flat=True))
    for node in coord2.datainput_set.all():
      assert_false(node.id in data_input_ids)

    data_output_ids = set(coord.dataoutput_set.values_list('id', flat=True))
    for node in coord2.dataoutput_set.all():
      assert_false(node.id in data_output_ids)

    assert_not_equal(coord.deployment_dir, coord2.deployment_dir)
    assert_not_equal('', coord2.deployment_dir)

    # Bulk delete
    response = self.c.post(reverse('oozie:delete_coordinator'), {'job_selection': [coord.id, coord2.id]}, follow=True)
    assert_equal(coordinator_count - 1, Document.objects.available_docs(Coordinator, self.user).count(), response)


  def test_coordinator_workflow_access_permissions(self):
    raise SkipTest

    self.wf.is_shared = True
    self.wf.save()

    # Login as someone else not superuser
    client_another_me = make_logged_in_client(username='another_me', is_superuser=False, groupname='test')
    grant_access("another_me", "test", "oozie")
    coord = create_coordinator(self.wf, client_another_me, self.user)

    response = client_another_me.get(reverse('oozie:edit_coordinator', args=[coord.id]))
    assert_true('Editor' in response.content, response.content)
    assert_true('Save coordinator' in response.content, response.content)

    # Check can schedule a non personal/shared workflow
    workflow_select = '%s</option>' % self.wf
    response = client_another_me.get(reverse('oozie:edit_coordinator', args=[coord.id]))
    assert_true(workflow_select in response.content, response.content)

    self.wf.is_shared = False
    self.wf.save()

    response = client_another_me.get(reverse('oozie:edit_coordinator', args=[coord.id]))
    assert_false(workflow_select in response.content, response.content)

    self.wf.is_shared = True
    self.wf.save()

    # Edit
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_another_me.post(reverse('oozie:edit_coordinator', args=[coord.id]))
      assert_true(workflow_select in response.content, response.content)
      assert_true('Save coordinator' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_another_me.post(reverse('oozie:edit_coordinator', args=[coord.id]))
      assert_true('This field is required' in response.content, response.content)
      assert_false(workflow_select in response.content, response.content)
      assert_true('Save coordinator' in response.content, response.content)
    finally:
      finish()


  def test_coordinator_gen_xml(self):
    coord = create_coordinator(self.wf, self.c, self.user)

    finish = ENABLE_CRON_SCHEDULING.set_for_testing(False)

    try:
      assert_true(
  """<controls>
    <timeout>100</timeout>
    <concurrency>3</concurrency>
    <execution>FIFO</execution>
    <throttle>10</throttle>
  </controls>
  <action>
    <workflow>
      <app-path>${wf_application_path}</app-path>
      <configuration>
        <property>
          <name>username</name>
          <value>${coord:user()}</value>
        </property>
        <property>
          <name>SLEEP</name>
          <value>1000</value>
        </property>
        <property>
          <name>market</name>
          <value>US</value>
        </property>
      </configuration>
   </workflow>
  </action>
</coordinator-app>""" in coord.to_xml(), coord.to_xml())
    finally:
      finish()

    assert_true(
"""<controls>
    <timeout>100</timeout>
    <concurrency>3</concurrency>
    <execution>FIFO</execution>
    <throttle>10</throttle>
  </controls>
  <action>
    <workflow>
      <app-path>${wf_application_path}</app-path>
      <configuration>
        <property>
          <name>username</name>
          <value>${coord:user()}</value>
        </property>
        <property>
          <name>SLEEP</name>
          <value>1000</value>
        </property>
        <property>
          <name>market</name>
          <value>US</value>
        </property>
      </configuration>
   </workflow>
  </action>
</coordinator-app>""" in coord.to_xml(), coord.to_xml())


  def test_coordinator_gen_sla(self):
    coord = create_coordinator(self.wf, self.c, self.user)
    xml = coord.to_xml()

    assert_false('<sla' in xml, xml)
    assert_false('xmlns="uri:oozie:coordinator:0.4"' in xml, xml)
    assert_false('xmlns:sla="uri:oozie:sla:0.2"' in xml, xml)

    sla = coord.sla
    sla[0]['value'] = True
    sla[1]['value'] = 'now' # nominal-time
    sla[3]['value'] = '${ 10 * MINUTES}' # should-end
    coord.sla = sla
    coord.save()

    xml = coord.to_xml()
    assert_true('xmlns="uri:oozie:coordinator:0.4"' in xml, xml)
    assert_true('xmlns:sla="uri:oozie:sla:0.2"' in xml, xml)
    assert_true("""</workflow>
          <sla:info>
            <sla:nominal-time>now</sla:nominal-time>
            <sla:should-end>${ 10 * MINUTES}</sla:should-end>
          </sla:info>
  </action>""" in xml, xml)


  def test_coordinator_with_data_input_gen_xml(self):
    coord = create_coordinator(self.wf, self.c, self.user)
    create_dataset(coord, self.c)
    create_coordinator_data(coord, self.c)

    self.c.post(reverse('oozie:create_coordinator_dataset', args=[coord.id]), {
                          u'create-name': [u'MyDataset2'], u'create-frequency_number': [u'1'], u'create-frequency_unit': [u'days'],
                          u'create-uri': [u's3n://a-server/data/out/${YEAR}${MONTH}${DAY}'],
                          u'create-instance_choice': [u'single'],
                          u'instance_start': [u'-1'],
                          u'create-advanced_start_instance': [u'0'],
                          u'create-advanced_end_instance': [u'0'],
                          u'create-start_0': [u'07/01/2012'], u'create-start_1': [u'12:00 AM'],
                          u'create-timezone': [u'America/Los_Angeles'], u'create-done_flag': [u''],
                          u'create-description': [u'']})

    dataset = Dataset.objects.filter(coordinator=coord).order_by('-id')[0]

    self.c.post(reverse('oozie:create_coordinator_data', args=[coord.id, 'output']),
                         {u'output-name': [u'output_dir'], u'output-dataset': [dataset.id]})


    assert_true(
"""<uri-template>s3n://a-server/data/out/${YEAR}${MONTH}${DAY}</uri-template>
      <done-flag></done-flag>
    </dataset>
  </datasets>
  <input-events>
    <data-in name="input_dir" dataset="MyDataset">
    <start-instance>
        ${coord:current(-1)}
    </start-instance>
    <end-instance>
        ${coord:current(1)}
    </end-instance>
    </data-in>
  </input-events>
  <output-events>
    <data-out name="output_dir" dataset="MyDataset2">
      <instance>${coord:current(0)}</instance>
    </data-out>
  </output-events>
  <action>
    <workflow>
      <app-path>${wf_application_path}</app-path>
      <configuration>
          <property>
            <name>input_dir</name>
            <value>${coord:dataIn('input_dir')}</value>
          </property>
        <property>
          <name>output_dir</name>
          <value>${coord:dataOut('output_dir')}</value>
        </property>
        <property>
          <name>username</name>
          <value>${coord:user()}</value>
        </property>
        <property>
          <name>SLEEP</name>
          <value>1000</value>
        </property>
        <property>
          <name>market</name>
          <value>US</value>
        </property>
      </configuration>
   </workflow>
  </action>
</coordinator-app>""" in coord.to_xml(), coord.to_xml())


  def test_create_coordinator_dataset(self):
    coord = create_coordinator(self.wf, self.c, self.user)
    create_dataset(coord, self.c)


  def test_edit_coordinator_dataset(self):
    coord = create_coordinator(self.wf, self.c, self.user)
    create_dataset(coord, self.c)

    dataset = Dataset.objects.get(coordinator=coord)

    response = self.c.post(reverse('oozie:edit_coordinator_dataset', args=[dataset.id]), {
                        u'edit-name': [u'MyDataset'], u'edit-frequency_number': [u'1'], u'edit-frequency_unit': [u'days'],
                        u'edit-uri': [u'/data/${YEAR}${MONTH}${DAY}'],
                        u'edit-start_0': [u'07/01/2012'], u'edit-start_1': [u'12:00 AM'],
                        u'edit-instance_choice': [u'range'],
                        u'edit-advanced_start_instance': [u'-1'],
                        u'edit-advanced_end_instance': [u'${coord:current(1)}'],
                        u'edit-start_0': [u'07/01/2012'], u'edit-start_1': [u'12:00 AM'],
                        u'edit-timezone': [u'America/Los_Angeles'], u'edit-done_flag': [u''],
                        u'edit-description': [u'']}, follow=True)
    data = json.loads(response.content)
    assert_equal(0, data['status'], data['status'])

  def test_create_coordinator_input_data(self):
    coord = create_coordinator(self.wf, self.c, self.user)
    create_dataset(coord, self.c)

    create_coordinator_data(coord, self.c)


  def test_install_examples(self):
    self.c.post(reverse('oozie:install_examples'))


  def test_workflow_prepare(self):
    action1 = Node.objects.get(workflow=self.wf, name='action-name-1').get_full_node()

    action1.prepares = json.dumps([
                           {"type": "delete","value": "${output}"},
                           {"type": "delete","value": "out"},
                           {"type": "delete","value": "/user/test/out"},
                           {"type": "delete","value": "hdfs://localhost:8020/user/test/out"}])
    action1.save()

    xml = self.wf.to_xml({'output': '/path'})

    assert_true('<delete path="${nameNode}${output}"/>' in xml, xml)
    assert_true('<delete path="${nameNode}/user/${wf:user()}/out"/>' in xml, xml)
    assert_true('<delete path="${nameNode}/user/test/out"/>' in xml, xml)
    assert_true('<delete path="hdfs://localhost:8020/user/test/out"/>' in xml, xml)


  def test_get_workflow_parameters(self):
    assert_equal([{'name': u'output', 'value': ''}, {'name': u'SLEEP', 'value': ''}, {'name': u'market', 'value': u'US'}],
                 self.wf.find_all_parameters())


  def test_get_coordinator_parameters(self):
    coord = create_coordinator(self.wf, self.c, self.user)

    create_dataset(coord, self.c)
    create_coordinator_data(coord, self.c)

    assert_equal([{'name': u'output', 'value': ''}, {'name': u'market', 'value': u'US'}],
                 coord.find_all_parameters())


  def test_workflow_data_binds(self):
    response = self.c.get(reverse('oozie:edit_workflow', args=[self.wf.id]))
    assert_equal(1, response.content.count('checked: is_shared'), response.content)
    assert_true('checked: capture_output' in response.content, response.content)


  def test_xss_escape_js(self):
    hacked = '[{"name":"oozie.use.system.libpath","value":"true"}, {"name": "123\\"><script>alert(1)</script>", "value": "\'hacked\'"}]'
    escaped = '[{"name": "oozie.use.system.libpath", "value": "true"}, {"name": "123\\"\\u003e\\u003cscript\\u003ealert(1)\\u003c/script\\u003e", "value": "\'hacked\'"}]'

    self.wf.job_properties = hacked
    self.wf.parameters = hacked

    assert_equal(escaped, self.wf._escapejs_parameters_list(hacked))
    assert_equal(escaped, self.wf.job_properties_escapejs)
    assert_equal(escaped, self.wf.parameters_escapejs)


  def test_xss_html_escaping(self):
    data = WORKFLOW_DICT.copy()
    data['description'] = [u'"><script>alert(1);</script>']

    self.wf = create_workflow(self.c, self.user, workflow_dict=data)

    resp = self.c.get('/oozie/list_workflows/')
    assert_false('"><script>alert(1);</script>' in resp.content, resp.content)
    assert_true('&quot;&gt;&lt;script&gt;alert(1);&lt;/script&gt;' in resp.content, resp.content)


  def test_submit_workflow(self):
    # Check param popup
    response = self.c.get(reverse('oozie:submit_workflow', args=[self.wf.id]))
    assert_equal([{'name': u'output', 'value': ''},
                  {'name': u'SLEEP', 'value': ''},
                  {'name': u'market', 'value': u'US'}
                  ],
                  response.context[0]['params_form'].initial)

  def test_submit_coordinator(self):
    coord = create_coordinator(self.wf, self.c, self.user)

    # Check param popup, SLEEP is set by coordinator so not shown in the popup
    response = self.c.get(reverse('oozie:submit_coordinator', args=[coord.id]))
    assert_equal([{'name': u'output', 'value': ''},
                  {'name': u'market', 'value': u'US'}
                  ],
                  response.context[0]['params_form'].initial)

  def test_trash_workflow(self):
    previous_trashed = Document.objects.trashed_docs(Workflow, self.user).count()
    previous_available = Document.objects.available_docs(Workflow, self.user).count()
    response = self.c.post(reverse('oozie:delete_workflow'), {'job_selection': [self.wf.id]}, follow=True)
    assert_equal(200, response.status_code, response)
    assert_equal(previous_trashed + 1, Document.objects.trashed_docs(Workflow, self.user).count())
    assert_equal(previous_available - 1, Document.objects.available_docs(Workflow, self.user).count())


  def test_workflow_export(self):
    response = self.c.get(reverse('oozie:export_workflow', args=[self.wf.id]))
    zfile = zipfile.ZipFile(StringIO.StringIO(response.content))
    assert_true('workflow.xml' in zfile.namelist(), 'workflow.xml not in response')
    assert_true('workflow-metadata.json' in zfile.namelist(), 'workflow-metadata.json not in response')
    assert_equal(2, len(zfile.namelist()))

    workflow_xml = reformat_xml("""<workflow-app name="wf-name-1" xmlns="uri:oozie:workflow:0.4">
    <global>
        <job-xml>jobconf.xml</job-xml>
        <configuration>
            <property>
                <name>sleep-all</name>
                <value>${SLEEP}</value>
            </property>
        </configuration>
    </global>
    <start to="action-name-1"/>
    <action name="action-name-1">
        <map-reduce>
            <job-tracker>${jobTracker}</job-tracker>
            <name-node>${nameNode}</name-node>
            <prepare>
                <delete path="${nameNode}${output}"/>
                <mkdir path="${nameNode}/test"/>
            </prepare>
            <configuration>
                <property>
                    <name>sleep</name>
                    <value>${SLEEP}</value>
                </property>
            </configuration>
        </map-reduce>
        <ok to="action-name-2"/>
        <error to="kill"/>
    </action>
    <action name="action-name-2">
        <map-reduce>
            <job-tracker>${jobTracker}</job-tracker>
            <name-node>${nameNode}</name-node>
            <prepare>
                <delete path="${nameNode}${output}"/>
                <mkdir path="${nameNode}/test"/>
            </prepare>
            <configuration>
                <property>
                    <name>sleep</name>
                    <value>${SLEEP}</value>
                </property>
            </configuration>
        </map-reduce>
        <ok to="action-name-3"/>
        <error to="kill"/>
    </action>
    <action name="action-name-3">
        <map-reduce>
            <job-tracker>${jobTracker}</job-tracker>
            <name-node>${nameNode}</name-node>
            <prepare>
                <delete path="${nameNode}${output}"/>
                <mkdir path="${nameNode}/test"/>
            </prepare>
            <configuration>
                <property>
                    <name>sleep</name>
                    <value>${SLEEP}</value>
                </property>
            </configuration>
        </map-reduce>
        <ok to="end"/>
        <error to="kill"/>
    </action>
    <kill name="kill">
        <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
    </kill>
    <end name="end"/>
</workflow-app>""")

    workflow_metadata_json = reformat_json("""{
  "attributes": {
    "deployment_dir": "/user/hue/oozie/workspaces/_test_-oozie-13-1383539302.62",
    "description": ""
  },
  "nodes": {
    "action-name-1": {
      "attributes": {
        "jar_path": "/user/hue/oozie/examples/lib/hadoop-examples.jar"
      }
    },
    "action-name-2": {
      "attributes": {
        "jar_path": "/user/hue/oozie/examples/lib/hadoop-examples.jar"
      }
    },
    "action-name-3": {
      "attributes": {
        "jar_path": "/user/hue/oozie/examples/lib/hadoop-examples.jar"
      }
    }
  },
  "version": "0.0.1"
}""")
    result_workflow_metadata_json = reformat_json(zfile.read('workflow-metadata.json'))
    workflow_metadata_json = synchronize_workflow_attributes(workflow_metadata_json, result_workflow_metadata_json)
    assert_equal(workflow_xml, reformat_xml(zfile.read('workflow.xml')))
    assert_equal(workflow_metadata_json, result_workflow_metadata_json)


class TestEditorBundle(OozieMockBase):

  def setUp(self):
    super(TestEditorBundle, self).setUp()
    self.setup_simple_workflow()


  def test_create_bundle(self):
    create_bundle(self.c, self.user)


  def test_clone_bundle(self):
    #@TODO@ Prakash fix this test
    raise SkipTest
    bundle = create_bundle(self.c, self.user)
    bundle_count = Document.objects.available_docs(Bundle, self.user).count()

    response = self.c.post(reverse('oozie:clone_bundle', args=[bundle.id]), {}, follow=True)

    bundle2 = Bundle.objects.latest('id')
    assert_not_equal(bundle.id, bundle2.id)
    assert_equal(bundle_count + 1, Document.objects.available_docs(Bundle, self.user).count(), response)

    coord_ids = set(bundle.coordinators.values_list('id', flat=True))
    coord2_ids = set(bundle2.coordinators.values_list('id', flat=True))

    if coord_ids or coord2_ids:
      assert_not_equal(coord_ids, coord2_ids)

    assert_not_equal(bundle.deployment_dir, bundle2.deployment_dir)
    assert_not_equal('', bundle2.deployment_dir)

    # Bulk delete
    response = self.c.post(reverse('oozie:delete_bundle'), {'job_selection': [bundle.id, bundle2.id]}, follow=True)
    assert_equal(bundle_count - 1, Document.objects.available_docs(Bundle, self.user).count(), response)


  def test_delete_bundle(self):
    bundle = create_bundle(self.c, self.user)
    bundle_count = Document.objects.available_docs(Bundle, self.user).count()

    response = self.c.post(reverse('oozie:delete_bundle'), {'job_selection': [bundle.id]}, follow=True)

    assert_equal(bundle_count - 1, Document.objects.available_docs(Bundle, self.user).count(), response)


  def test_bundle_gen_xml(self):
    raise SkipTest()
    bundle = create_bundle(self.c, self.user)

    assert_true(
"""<bundle-app name="MyBundle"
  xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'
  xmlns="uri:oozie:coordinator:0.2">
  <parameters>
    <property>
        <name>market</name>
        <value>US,France</value>
    </property>
  </parameters>
  <controls>
     <kick-off-time>2012-07-01T00:00Z</kick-off-time>
  </controls>
</bundle-app>
""" in bundle.to_xml(), bundle.to_xml())


  def test_create_bundled_coordinator(self):
    raise SkipTest()
    bundle = create_bundle(self.c, self.user)
    coord = create_coordinator(self.wf, self.c, self.user)

    post = {
        u'name': [u'test2'], u'kick_off_time_0': [u'02/12/2013'], u'kick_off_time_1': [u'05:05 PM'],
        u'create-bundled-coordinator-parameters': [u'[{"name":"market","value":"US"}]'],
        u'schema_version': [u'uri:oozie:bundle:0.2', u'uri:oozie:bundle:0.2'], u'coordinators-MAX_NUM_FORMS': [u'0'],
        u'coordinators-INITIAL_FORMS': [u'0'],
        u'parameters': [u'[{"name":"oozie.use.system.libpath","value":"true"}]'], u'coordinators-TOTAL_FORMS': [u'0'],
        u'description': [u'ss']
    }

    response = self.c.get(reverse('oozie:create_bundled_coordinator', args=[bundle.id]))
    assert_true('Add coordinator' in response.content, response.content)

    response = self.c.post(reverse('oozie:create_bundled_coordinator', args=[bundle.id]), post, follow=True)
    assert_true('This field is required' in response.content, response.content)

    post['create-bundled-coordinator-coordinator'] = ['%s' % coord.id]
    response = self.c.post(reverse('oozie:create_bundled_coordinator', args=[bundle.id]), post, follow=True)
    assert_true('Coordinators' in response.content, response.content)

    xml = bundle.to_xml({
       'wf_%s_dir' % self.wf.id: '/deployment_path_wf',
       'coord_%s_dir' % coord.id: '/deployment_path_coord'
    })

    assert_true(
"""<bundle-app name="MyBundle"
  xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'
  xmlns="uri:oozie:coordinator:0.2">
  <parameters>
    <property>
        <name>market</name>
        <value>US,France</value>
    </property>
  </parameters>
  <controls>
     <kick-off-time>2012-07-01T00:00Z</kick-off-time>
  </controls>
  <coordinator name='MyCoord-1' >
     <app-path>${nameNode}/deployment_path_coord</app-path>
       <configuration>
         <property>
            <name>wf_application_path</name>
            <value>/deployment_path_wf</value>
        </property>
         <property>
            <name>market</name>
            <value>US</value>
        </property>
      </configuration>
  </coordinator>
</bundle-app>""" in xml, xml)


class TestImportWorkflow04(OozieMockBase):

  def setUp(self):
    super(TestImportWorkflow04, self).setUp()
    self.setup_simple_workflow()

  @raises(RuntimeError)
  def test_import_workflow_namespace_error(self):
    """
    Validates import for most basic workflow with an error.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-basic-namespace-missing.xml')
    contents = f.read()
    f.close()

    # Should throw PopupException
    import_workflow(workflow, contents)


  def test_import_workflow_basic(self):
    raise SkipTest()
    """
    Validates import for most basic workflow: start and end.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-basic.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    assert_equal(2, len(Node.objects.filter(workflow=workflow)))
    assert_equal(2, len(Link.objects.filter(parent__workflow=workflow)))
    assert_equal('done', Node.objects.get(workflow=workflow, node_type='end').name)
    assert_equal('uri:oozie:workflow:0.4', workflow.schema_version)
    workflow.delete(skip_trash=True)

  def test_import_workflow_credentials(self):
    """
    Validates import for workflow with credentials.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-credentials.xml')
    import_workflow(workflow, f.read())
    f.close()
    credentials = Node.objects.get(workflow=workflow, node_type='hive').credentials
    assert_equal(1, len(credentials))
    assert_equal('hcat', credentials[0]['name'])
    assert_equal(True, credentials[0]['value'])
    workflow.delete(skip_trash=True)


  def test_import_workflow_basic_global_config(self):
    raise SkipTest()
    """
    Validates import for basic workflow: start, end, and global configuration.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-basic-global-config.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    assert_equal(4, len(Node.objects.filter(workflow=workflow)))
    assert_equal(4, len(Link.objects.filter(parent__workflow=workflow)))
    assert_equal('done', Node.objects.get(workflow=workflow, node_type='end').name)
    assert_equal('uri:oozie:workflow:0.4', workflow.schema_version)
    assert_equal('job1.xml', workflow.job_xml)
    assert_equal('[{"name": "mapred.job.queue.name", "value": "${queueName}"}]', workflow.job_properties)
    workflow.delete(skip_trash=True)


  def test_import_workflow_decision(self):
    """
    Validates import for decision node: link comments (conditions), default link, decision end.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-decision.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    assert_equal(12, len(Node.objects.filter(workflow=workflow)))
    assert_equal(21, len(Link.objects.filter(parent__workflow=workflow)))
    assert_equal(1, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='decision', comment='${1 gt 2}', name='start')))
    assert_equal(1, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='decision', comment='', name='start')))
    assert_equal(1, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='decision', name='default')))
    assert_equal(1, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='decision', child__node_type='decisionend', name='related')))
    workflow.delete(skip_trash=True)


  def test_import_workflow_decision_complex(self):
    if is_live_cluster():
      raise SkipTest()

    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-decision-complex.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    assert_equal(14, len(Node.objects.filter(workflow=workflow)))
    assert_equal(27, len(Link.objects.filter(parent__workflow=workflow)))
    assert_equal(3, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='decision', comment='${ 1 gt 2 }', name='start')))
    assert_equal(0, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='decision', comment='', name='start')))
    assert_equal(3, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='decision', name='default')))
    assert_equal(3, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='decision', child__node_type='decisionend', name='related')))
    workflow.delete(skip_trash=True)


  def test_import_workflow_distcp(self):
    """
    Validates import for distcp node: params.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-distcp.0.1.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    assert_equal(4, len(Node.objects.filter(workflow=workflow)))
    assert_equal(4, len(Link.objects.filter(parent__workflow=workflow)))
    assert_equal('[{"type":"arg","value":"-overwrite"},{"type":"arg","value":"-m"},{"type":"arg","value":"${MAP_NUMBER}"},{"type":"arg","value":"/user/hue/oozie/workspaces/data"},{"type":"arg","value":"${OUTPUT}"}]', Node.objects.get(workflow=workflow, node_type='distcp').get_full_node().params)
    workflow.delete(skip_trash=True)


  def test_import_workflow_forks(self):
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-forks.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    assert_equal(12, len(Node.objects.filter(workflow=workflow)))
    assert_equal(20, len(Link.objects.filter(parent__workflow=workflow)))
    assert_equal(6, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='fork')))
    assert_equal(4, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='fork', name='start')))
    assert_equal(2, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='fork', child__node_type='join', name='related')))
    workflow.delete(skip_trash=True)


  def test_import_workflow_mapreduce(self):
    """
    Validates import for mapreduce node: job_properties.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-mapreduce.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    assert_equal(4, len(Node.objects.filter(workflow=workflow)))
    assert_equal(4, len(Link.objects.filter(parent__workflow=workflow)))
    assert_equal('[{"name":"mapred.reduce.tasks","value":"1"},{"name":"mapred.mapper.class","value":"org.apache.hadoop.examples.SleepJob"},{"name":"mapred.reducer.class","value":"org.apache.hadoop.examples.SleepJob"},{"name":"mapred.mapoutput.key.class","value":"org.apache.hadoop.io.IntWritable"},{"name":"mapred.mapoutput.value.class","value":"org.apache.hadoop.io.NullWritable"},{"name":"mapred.output.format.class","value":"org.apache.hadoop.mapred.lib.NullOutputFormat"},{"name":"mapred.input.format.class","value":"org.apache.hadoop.examples.SleepJob$SleepInputFormat"},{"name":"mapred.partitioner.class","value":"org.apache.hadoop.examples.SleepJob"},{"name":"mapred.speculative.execution","value":"false"},{"name":"sleep.job.map.sleep.time","value":"0"},{"name":"sleep.job.reduce.sleep.time","value":"1"}]', Node.objects.get(workflow=workflow, node_type='mapreduce').get_full_node().job_properties)
    workflow.delete(skip_trash=True)


  def test_import_workflow_pig(self):
    """
    Validates import for pig node: params.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-pig.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    node = Node.objects.get(workflow=workflow, node_type='pig').get_full_node()
    assert_equal(4, len(Node.objects.filter(workflow=workflow)))
    assert_equal(4, len(Link.objects.filter(parent__workflow=workflow)))
    assert_equal('aggregate.pig', node.script_path)
    assert_equal('[{"type":"param","value":"KEY=VALUE"},{"type":"argument","value":"-param"},{"type":"argument","value":"INPUT=/user/hue/oozie/workspaces/data"},{"type":"argument","value":"-param"},{"type":"argument","value":"OUTPUT=${output}"}]', node.params)
    workflow.delete(skip_trash=True)


  def test_import_workflow_sqoop(self):
    """
    Validates import for sqoop node: script_path, files.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-sqoop.0.2.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    assert_equal(4, len(Node.objects.filter(workflow=workflow)))
    assert_equal(4, len(Link.objects.filter(parent__workflow=workflow)))
    node = Node.objects.get(workflow=workflow, node_type='sqoop').get_full_node()
    assert_equal('["db.hsqldb.properties#db.hsqldb.properties","db.hsqldb.script#db.hsqldb.script"]', node.files)
    assert_equal('import --connect jdbc:hsqldb:file:db.hsqldb --table TT --target-dir ${output} -m 1', node.script_path)
    assert_equal('[{"type":"arg","value":"My invalid arg"},{"type":"arg","value":"My invalid arg 2"}]', node.params)
    workflow.delete(skip_trash=True)


  def test_import_workflow_ssh(self):
    """
    Validates import for ssh node: params.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-ssh.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    node = Node.objects.get(workflow=workflow, node_type='ssh').get_full_node()
    assert_equal('${user}@${host}', node.host)
    assert_equal('ls', node.command)
    assert_equal('[{"type":"args","value":"-l"}]', node.params)
    workflow.delete(skip_trash=True)


  def test_import_workflow_java(self):
    """
    Validates import for java node: main_class, args.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-java.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    assert_equal(5, len(Node.objects.filter(workflow=workflow)))
    assert_equal(6, len(Link.objects.filter(parent__workflow=workflow)))
    java_nodes = Node.objects.filter(workflow=workflow, node_type='java').order_by('name')
    tera_gen_node = java_nodes[0].get_full_node()
    tera_sort_node = java_nodes[1].get_full_node()
    assert_equal('org.apache.hadoop.examples.terasort.TeraGen', tera_gen_node.main_class)
    assert_equal('${records} ${output_dir}/teragen', tera_gen_node.args)
    assert_equal('org.apache.hadoop.examples.terasort.TeraSort', tera_sort_node.main_class)
    assert_equal('-Dmapred.reduce.tasks=${terasort_reducers} ${output_dir}/teragen ${output_dir}/terasort', tera_sort_node.args)
    assert_true(tera_gen_node.capture_output)
    assert_false(tera_sort_node.capture_output)
    workflow.delete(skip_trash=True)


  def test_import_workflow_shell(self):
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-shell.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    assert_equal(5, len(Node.objects.filter(workflow=workflow)))
    assert_equal(6, len(Link.objects.filter(parent__workflow=workflow)))
    shell_nodes = Node.objects.filter(workflow=workflow, node_type='shell').order_by('name')
    shell_1_node = shell_nodes[0].get_full_node()
    shell_2_node = shell_nodes[1].get_full_node()
    assert_equal('shell-1', shell_1_node.name)
    assert_equal('shell-2', shell_2_node.name)
    assert_equal('my-job.xml', shell_1_node.job_xml)
    assert_equal('hello.py', shell_1_node.command)
    assert_equal('[{"type":"argument","value":"World!"}]', shell_1_node.params)
    assert_true(shell_1_node.capture_output)
    assert_false(shell_2_node.capture_output)
    workflow.delete(skip_trash=True)


  def test_import_workflow_fs(self):
    """
    Validates import for fs node: chmods, deletes, mkdirs, moves, touchzs.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-fs.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    assert_equal(4, len(Node.objects.filter(workflow=workflow)))
    assert_equal(4, len(Link.objects.filter(parent__workflow=workflow)))
    node = Node.objects.get(workflow=workflow, node_type='fs').get_full_node()
    assert_equal('[{"path":"${nameNode}${output}/testfs/renamed","permissions":"700","recursive":"false"}]', node.chmods)
    assert_equal('[{"name":"${nameNode}${output}/testfs"}]', node.deletes)
    assert_equal('[{"name":"${nameNode}${output}/testfs"},{"name":"${nameNode}${output}/testfs/source"}]', node.mkdirs)
    assert_equal('[{"source":"${nameNode}${output}/testfs/source","destination":"${nameNode}${output}/testfs/renamed"}]', node.moves)
    assert_equal('[{"name":"${nameNode}${output}/testfs/new_file"}]', node.touchzs)
    workflow.delete(skip_trash=True)


  def test_import_workflow_email(self):
    """
    Validates import for email node: to, css, subject, body.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-email.0.1.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    assert_equal(4, len(Node.objects.filter(workflow=workflow)))
    assert_equal(4, len(Link.objects.filter(parent__workflow=workflow)))
    node = Node.objects.get(workflow=workflow, node_type='email').get_full_node()
    assert_equal('example@example.org', node.to)
    assert_equal('', node.cc)
    assert_equal('I love', node.subject)
    assert_equal('Hue', node.body)
    workflow.delete(skip_trash=True)


  def test_import_workflow_generic(self):
    """
    Validates import for generic node: xml.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-generic.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    assert_equal(4, len(Node.objects.filter(workflow=workflow)))
    assert_equal(4, len(Link.objects.filter(parent__workflow=workflow)))
    node = Node.objects.get(workflow=workflow, node_type='generic').get_full_node()
    assert_equal("<bleh test=\"test\">\n              <test>test</test>\n        </bleh>", node.xml)
    workflow.delete(skip_trash=True)


  def test_import_workflow_multi_kill_node(self):
    """
    Validates import for multiple kill nodes: xml.

    Kill nodes should be skipped and a single kill node should be created.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-java-multiple-kill.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    assert_equal('kill', Kill.objects.get(workflow=workflow).name)
    assert_equal(5, len(Node.objects.filter(workflow=workflow)))
    assert_equal(6, len(Link.objects.filter(parent__workflow=workflow)))
    nodes = [Node.objects.filter(workflow=workflow, node_type='java')[0].get_full_node(),
             Node.objects.filter(workflow=workflow, node_type='java')[1].get_full_node()]
    assert_equal('org.apache.hadoop.examples.terasort.TeraGen', nodes[0].main_class)
    assert_equal('${records} ${output_dir}/teragen', nodes[0].args)
    assert_equal('org.apache.hadoop.examples.terasort.TeraSort', nodes[1].main_class)
    assert_equal('-Dmapred.reduce.tasks=${terasort_reducers} ${output_dir}/teragen ${output_dir}/terasort', nodes[1].args)
    assert_true(nodes[0].capture_output)
    assert_false(nodes[1].capture_output)
    workflow.delete(skip_trash=True)

  def test_import_workflow_different_error_link(self):
    """
    Validates import with error link to end: main_class, args.

    If an error link cannot be resolved, default to 'kill' node.
    """

    if is_live_cluster():
      raise SkipTest('HUE-2899: Needs to make results in a consistent order')

    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-java-different-error-links.xml')
    import_workflow(workflow, f.read())
    f.close()
    workflow.save()
    assert_equal(5, len(Node.objects.filter(workflow=workflow)))
    assert_equal(6, len(Link.objects.filter(parent__workflow=workflow)))
    nodes = [Node.objects.filter(workflow=workflow, node_type='java')[0].get_full_node(),
             Node.objects.filter(workflow=workflow, node_type='java')[1].get_full_node()]
    assert_equal('org.apache.hadoop.examples.terasort.TeraGen', nodes[0].main_class)
    assert_equal('${records} ${output_dir}/teragen', nodes[0].args)
    assert_equal('org.apache.hadoop.examples.terasort.TeraSort', nodes[1].main_class)
    assert_equal('-Dmapred.reduce.tasks=${terasort_reducers} ${output_dir}/teragen ${output_dir}/terasort', nodes[1].args)
    assert_true(nodes[0].capture_output)
    assert_false(nodes[1].capture_output)
    assert_equal(1, len(Link.objects.filter(parent__workflow=workflow).filter(parent__name='TeraGenWorkflow').filter(name='error').filter(child__node_type='java')))
    assert_equal(1, len(Link.objects.filter(parent__workflow=workflow).filter(parent__name='TeraSort').filter(name='error').filter(child__node_type='kill')))
    workflow.delete(skip_trash=True)


class TestImportCoordinator02(OozieMockBase):

  def setUp(self):
    super(TestImportCoordinator02, self).setUp()
    self.setup_simple_workflow()

  def test_import_coordinator_simple(self):
    raise SkipTest
    coordinator_count = Document.objects.available_docs(Coordinator, self.user).count()

    # Create
    filename = os.path.abspath(os.path.dirname(__file__) + "/test_data/coordinators/0.2/test-basic.xml")
    fh = open(filename)
    response = self.c.post(reverse('oozie:import_coordinator'), {
      'name': ['test_coordinator'],
      'workflow': Workflow.objects.get(name='wf-name-1').pk,
      'definition_file': [fh],
      'description': ['test description']
    }, follow=True)
    fh.close()

    assert_equal(coordinator_count + 1, Document.objects.available_docs(Coordinator, self.user).count(), response)
    coordinator = Coordinator.objects.get(name='test_coordinator')
    assert_equal('[{"name":"oozie.use.system.libpath","value":"true"}]', coordinator.parameters)
    assert_equal('uri:oozie:coordinator:0.2', coordinator.schema_version)
    assert_equal('test description', coordinator.description)
    assert_equal(datetime.strptime('2013-06-03T00:00Z', '%Y-%m-%dT%H:%MZ'), coordinator.start)
    assert_equal(datetime.strptime('2013-06-05T00:00Z', '%Y-%m-%dT%H:%MZ'), coordinator.end)
    assert_equal('America/Los_Angeles', coordinator.timezone)
    assert_equal('days', coordinator.frequency_unit)
    assert_equal(1, coordinator.frequency_number)
    assert_equal(None, coordinator.timeout)
    assert_equal(None, coordinator.concurrency)
    assert_false(coordinator.execution)  # coordinator.execution can be None or empty string
    assert_equal(None, coordinator.throttle)
    assert_not_equal(None, coordinator.deployment_dir)


class TestPermissions(OozieBase):

  def setUp(self):
    super(TestPermissions, self).setUp()

    self.wf = create_workflow(self.c, self.user)
    self.setup_simple_workflow()

  def tearDown(self):
    try:
      self.wf.delete(skip_trash=True)
    except:
      LOG.exception('failed to tear down tests')

  def test_workflow_permissions(self):
    raise SkipTest

    response = self.c.get(reverse('oozie:edit_workflow', args=[self.wf.id]))
    assert_true('Editor' in response.content, response.content)
    assert_true('Save' in response.content, response.content)
    assert_false(self.wf.is_shared)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "oozie")

    # List
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:list_workflows'))
      assert_false('wf-name-1' in response.content, response.content)
    finally:
      finish()
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:list_workflows'))
      assert_false('wf-name-1' in response.content, response.content)
    finally:
      finish()

    # View
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:edit_workflow', args=[self.wf.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:edit_workflow', args=[self.wf.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    # Share it !
    self.wf = Workflow.objects.get(name='wf-name-1', managed=True)
    self.wf.is_shared = True
    self.wf.save()
    Workflow.objects.check_workspace(self.wf, self.cluster.fs)

    # List
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:list_workflows'))
      assert_equal(200, response.status_code)
      assert_true('wf-name-1' in response.content, response.content)
    finally:
      finish()

    # View
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:edit_workflow', args=[self.wf.id]))
      assert_false('Permission denied' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:edit_workflow', args=[self.wf.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    # Submit
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.post(reverse('oozie:submit_workflow', args=[self.wf.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(True)
    try:
      try:
        response = client_not_me.post(reverse('oozie:submit_workflow', args=[self.wf.id]))
        assert_false('Permission denied' in response.content, response.content)
      except IOError:
        pass
    finally:
      finish()

    # Move to trash
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.post(reverse('oozie:delete_workflow'), {'job_selection': [self.wf.id]})
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    response = self.c.post(reverse('oozie:delete_workflow'), {'job_selection': [self.wf.id]}, follow=True)
    assert_equal(200, response.status_code)

    # Trash
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:list_trashed_workflows'))
      assert_false(self.wf.name in response.content, response.content)
    finally:
      finish()

    response = self.c.get(reverse('oozie:list_trashed_workflows'))
    assert_true(self.wf.name in response.content, response.content)

    # Restore
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.post(reverse('oozie:restore_workflow'), {'job_selection': [self.wf.id]})
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    response = self.c.post(reverse('oozie:restore_workflow'), {'job_selection': [self.wf.id]}, follow=True)
    assert_equal(200, response.status_code)


  def test_coordinator_permissions(self):
    raise SkipTest

    coord = create_coordinator(self.wf, self.c, self.user)

    response = self.c.get(reverse('oozie:edit_coordinator', args=[coord.id]))
    assert_true('Editor' in response.content, response.content)
    assert_true('Save coordinator' in response.content, response.content)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "oozie")

    # List
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:list_coordinators'))
      assert_false('MyCoord' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:list_coordinators'))
      assert_false('MyCoord' in response.content, response.content)
    finally:
      finish()

    # View
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:edit_coordinator', args=[coord.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:edit_coordinator', args=[coord.id]))
      assert_false('MyCoord' in response.content, response.content)
    finally:
      finish()

    # Share it !
    wf = Workflow.objects.get(id=coord.workflow.id, managed=True)
    wf.is_shared = True
    wf.save()
    Workflow.objects.check_workspace(wf, self.cluster.fs)

    post = COORDINATOR_DICT.copy()
    post.update({
                 u'datainput_set-TOTAL_FORMS': [u'0'], u'datainput_set-INITIAL_FORMS': [u'0'], u'dataset_set-INITIAL_FORMS': [u'0'],
                 u'dataoutput_set-INITIAL_FORMS': [u'0'], u'datainput_set-MAX_NUM_FORMS': [u'0'], u'output-MAX_NUM_FORMS': [u''],
                 u'output-INITIAL_FORMS': [u'0'], u'dataoutput_set-TOTAL_FORMS': [u'0'], u'input-TOTAL_FORMS': [u'0'],
                 u'dataset_set-MAX_NUM_FORMS': [u'0'], u'dataoutput_set-MAX_NUM_FORMS': [u'0'], u'input-MAX_NUM_FORMS': [u''],
                 u'dataset_set-TOTAL_FORMS': [u'0'], u'input-INITIAL_FORMS': [u'0'], u'output-TOTAL_FORMS': [u'0']})

    post['is_shared'] = [u'on']
    post['workflow'] = coord.workflow.id
    self.c.post(reverse('oozie:edit_coordinator', args=[coord.id]), post)
    coord = Coordinator.objects.get(id=coord.id)
    assert_true(coord.is_shared)

    # List
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:list_coordinators'))
      assert_equal(200, response.status_code)
      assert_true('MyCoord' in response.content, response.content)
    finally:
      finish()

    # View
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:edit_coordinator', args=[coord.id]))
      assert_false('Permission denied' in response.content, response.content)
      assert_false('Save coordinator' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:edit_coordinator', args=[coord.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    # Edit
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.post(reverse('oozie:edit_coordinator', args=[coord.id]))
      assert_false('MyCoord' in response.content, response.content)
      assert_true('Not allowed' in response.content, response.content)
    finally:
      finish()

    # Submit
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.post(reverse('oozie:submit_coordinator', args=[coord.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(True)
    try:
      try:
        response = client_not_me.post(reverse('oozie:submit_coordinator', args=[coord.id]))
        assert_false('Permission denied' in response.content, response.content)
      except IOError:
        pass
    finally:
      finish()

    # Move to trash
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.post(reverse('oozie:delete_coordinator'), {'job_selection': [coord.id]})
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    response = self.c.post(reverse('oozie:delete_coordinator'), {'job_selection': [coord.id]}, follow=True)
    assert_equal(200, response.status_code)

    # List trash
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:list_trashed_coordinators'))
      assert_true(coord.name in response.content, response.content)
    finally:
      finish()
    finish = SHARE_JOBS.set_for_testing(False)

    response = client_not_me.get(reverse('oozie:list_trashed_coordinators'))
    assert_false(coord.name in response.content, response.content)

    # Restore
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.post(reverse('oozie:restore_coordinator'), {'job_selection': [coord.id]})
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    response = self.c.post(reverse('oozie:restore_coordinator'), {'job_selection': [coord.id]}, follow=True)
    assert_equal(200, response.status_code)

  def test_bundle_permissions(self):
    raise SkipTest

    bundle = create_bundle(self.c, self.user)

    response = self.c.get(reverse('oozie:edit_bundle', args=[bundle.id]))
    assert_true('Editor' in response.content, response.content)
    assert_true('MyBundle' in response.content, response.content)
    assert_true('Save' in response.content, response.content)
    assert_false(bundle.is_shared)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "oozie")

    # List
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:list_bundles'))
      assert_false('MyBundle' in response.content, response.content)
    finally:
      finish()
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:list_bundles'))
      assert_false('MyBundle' in response.content, response.content)
    finally:
      finish()

    # View
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:edit_bundle', args=[bundle.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:edit_bundle', args=[bundle.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    # Share it !
    bundle.is_shared = True
    bundle.save()

    # List
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:list_bundles'))
      assert_equal(200, response.status_code)
      assert_true('MyBundle' in response.content, response.content)
    finally:
      finish()

    # View
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:edit_bundle', args=[bundle.id]))
      assert_false('Permission denied' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:edit_bundle', args=[bundle.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    # Submit
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.post(reverse('oozie:submit_bundle', args=[bundle.id]),{
                     u'form-MAX_NUM_FORMS': [u''], u'form-INITIAL_FORMS': [u'0'], u'form-TOTAL_FORMS': [u'0']
                 })
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(True)
    try:
      try:
        response = client_not_me.post(reverse('oozie:submit_bundle', args=[bundle.id]), {
                       u'form-MAX_NUM_FORMS': [u''], u'form-INITIAL_FORMS': [u'0'], u'form-TOTAL_FORMS': [u'0']
                   })
        assert_false('Permission denied' in response.content, response.content)
      except IOError:
        pass
    finally:
      finish()

    # Delete
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.post(reverse('oozie:delete_bundle'), {'job_selection': [bundle.id]})
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    response = self.c.post(reverse('oozie:delete_bundle'), {'job_selection': [bundle.id]}, follow=True)
    assert_equal(200, response.status_code)

    # List trash
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:list_trashed_bundles'))
      assert_true(bundle.name in response.content, response.content)
    finally:
      finish()
    finish = SHARE_JOBS.set_for_testing(False)

    response = client_not_me.get(reverse('oozie:list_trashed_bundles'))
    assert_false(bundle.name in response.content, response.content)

    # Restore
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.post(reverse('oozie:restore_bundle'), {'job_selection': [bundle.id]})
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    response = self.c.post(reverse('oozie:restore_bundle'), {'job_selection': [bundle.id]}, follow=True)
    assert_equal(200, response.status_code)


class TestEditorWithOozie(OozieBase):

  def setUp(self):
    OozieBase.setUp(self)

    self.c = make_logged_in_client()
    self.wf = create_workflow(self.c, self.user)
    self.setup_simple_workflow()


  def tearDown(self):
    try:
      self.wf.delete(skip_trash=True)
    except:
      LOG.exception('failed to tear down tests')


  def test_create_workflow(self):
    dir_stat = self.cluster.fs.stats(self.wf.deployment_dir)
    assert_equal('test', dir_stat.user)
    assert_equal('hue', dir_stat.group)
    assert_equal('40711', '%o' % dir_stat.mode)


  def test_clone_workflow(self):
    raise SkipTest
    workflow_count = Document.objects.available_docs(Workflow, self.user).count()

    response = self.c.post(reverse('oozie:clone_workflow', args=[self.wf.id]), {}, follow=True)

    assert_equal(workflow_count + 1, Document.objects.available_docs(Workflow, self.user).count(), response)

    wf2 = Workflow.objects.latest('id')
    assert_not_equal(self.wf.id, wf2.id)
    assert_equal(self.wf.node_set.count(), wf2.node_set.count())

    node_ids = set(self.wf.node_set.values_list('id', flat=True))
    for node in wf2.node_set.all():
      assert_false(node.id in node_ids)

    assert_not_equal(self.wf.deployment_dir, wf2.deployment_dir)
    assert_not_equal('', wf2.deployment_dir)

    # Bulk delete
    response = self.c.post(reverse('oozie:delete_workflow'), {'job_selection': [self.wf.id, wf2.id]}, follow=True)
    assert_equal(workflow_count - 1, Document.objects.available_docs(Workflow, self.user).count(), response)


  def test_import_workflow(self):
    raise SkipTest
    workflow_count = Document.objects.available_docs(Workflow, self.user).count()

    # Create
    filename = os.path.abspath(os.path.dirname(__file__) + "/test_data/workflows/0.4/test-mapreduce.xml")
    fh = open(filename)
    response = self.c.post(reverse('oozie:import_workflow'), {
      'job_xml': [''],
      'name': ['test_workflow'],
      'parameters': ['[{"name":"oozie.use.system.libpath","value":"true"}]'],
      'deployment_dir': [''],
      'job_properties': ['[]'],
      'schema_version': ['0.4'],
      'definition_file': [fh],
      'description': ['']
    }, follow=True)
    fh.close()

    assert_equal(workflow_count + 1, Document.objects.available_docs(Workflow, self.user).count(), response)

  def test_delete_workflow(self):
    previous_trashed = Document.objects.trashed_docs(Workflow, self.user).count()
    previous_available = Document.objects.available_docs(Workflow, self.user).count()

    response = self.c.post(reverse('oozie:delete_workflow') + "?skip_trash=true", {'job_selection': [self.wf.id]}, follow=True)
    assert_equal(200, response.status_code, response)

    assert_equal(previous_trashed, Document.objects.trashed_docs(Workflow, self.user).count())
    assert_equal(previous_available - 1, Document.objects.available_docs(Workflow, self.user).count())


class TestImportWorkflow04WithOozie(OozieBase):

  def setUp(self):
    OozieBase.setUp(self)

    self.c = make_logged_in_client()
    self.wf = create_workflow(self.c, self.user)
    self.setup_simple_workflow()

    # in order to reference examples in Subworkflow, must be owned by current user.
    Workflow.objects.update(owner=self.user)


  def tearDown(self):
    self.wf.delete(skip_trash=True)


  def test_import_workflow_subworkflow(self):
    """
    Validates import for subworkflow node: propagate_configuration.
    """
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/workflows/0.4/test-subworkflow.xml')
    import_workflow(workflow, f.read(), None, self.cluster.fs)
    f.close()
    workflow.save()
    assert_equal(4, len(Node.objects.filter(workflow=workflow)))
    assert_equal(4, len(Link.objects.filter(parent__workflow=workflow)))
    node = Node.objects.get(workflow=workflow, node_type='subworkflow').get_full_node()
    assert_equal(True, node.propagate_configuration)
    workflow.delete(skip_trash=True)


class TestOozieSubmissions(OozieBase):

  def test_submit_hiveserver2_action(self):
    wf_uuid = "c1c3cba9-edec-fb6f-a526-9f80b66fe993"
    wf = Document2.objects.get(uuid=wf_uuid)
    wf.data.replace('hive2://localhost:10000/default', _get_hiveserver2_url())
    wf.save()

    # Somewhere we delete those by mistake
    doc = Document.objects.link(wf, owner=wf.owner, name=wf.name, description=wf.description, extra='workflow2')
    doc.share_to_default()

    response = self.c.post(reverse('oozie:editor_submit_workflow', kwargs={'doc_id': wf.id}),
                           data={
                               u'form-0-name': [u'oozie.use.system.libpath'],
                               u'form-MAX_NUM_FORMS': [u'1000'],
                               u'form-TOTAL_FORMS': [u'1'],
                               u'form-INITIAL_FORMS': [u'1'],
                               u'form-0-value': [u'True']
                           },
                           follow=True)
    job = OozieServerProvider.wait_until_completion(response.context[0]['oozie_workflow'].id)

    assert_true(job.status in ('SUCCEEDED', 'KILLED'), job.status) # Dies for some cluster setup reason


  def test_submit_spark_action(self):
    wf_uuid = "2d667ab2-70f9-c2bf-0726-abe84fa7130d"
    wf = Document2.objects.get(uuid=wf_uuid)

    # Somewhere we delete those by mistake
    doc = Document.objects.link(wf, owner=wf.owner, name=wf.name, description=wf.description, extra='workflow2')
    doc.share_to_default()

    response = self.c.post(reverse('oozie:editor_submit_workflow', kwargs={'doc_id': wf.id}),
                           data={
                               u'form-0-name': [u'oozie.use.system.libpath'],
                               u'form-MAX_NUM_FORMS': [u'1000'],
                               u'form-1-name': [u'input'],
                               u'form-TOTAL_FORMS': [u'3'],
                               u'form-1-value': [u'/user/hue/oozie/workspaces/data/sonnets.txt'],
                               u'form-2-name': [u'output'],
                               u'form-INITIAL_FORMS': [u'3'],
                               u'form-2-value': [u'here'],
                               u'form-0-value': [u'True']
                           },
                           follow=True)
    job = OozieServerProvider.wait_until_completion(response.context[0]['oozie_workflow'].id)

    assert_true(job.status in ('SUCCEEDED', 'KILLED'), job.status) # Dies for some cluster setup reason


  def test_oozie_page(self):
    if is_live_cluster():
      raise SkipTest('HUE-2898: Skipping test until it can be debugged')

    response = self.c.get(reverse('oozie:list_oozie_info'))
    assert_true('version' in response.content, response.content)
    assert_true('NORMAL' in response.content, response.content)

    assert_true('variables' in response.content, response.content)
    assert_true('timers' in response.content, response.content)
    assert_true('counters' in response.content, response.content)

    assert_true('ownMinTime' in response.content, response.content)
    assert_true('oozie.base.url' in response.content, response.content)

  def test_imported_workflow_submission(self):
    # Workflow owned by "temp_user"
    workflow_docs = '"[\\n{\\n  \\"pk\\": 50012, \\n  \\"model\\": \\"desktop.document2\\", \\n  \\"fields\\": {\\n    \\"search\\": null, \\n    \\"uuid\\": \\"c3f7f992-4a64-407b-86c4-da630f6b51a5\\", \\n    \\"extra\\": \\"\\", \\n    \\"type\\": \\"oozie-workflow2\\", \\n    \\"description\\": \\"\\", \\n    \\"is_history\\": false, \\n    \\"parent_directory\\": [\\n      \\"098ec28d-23b5-42b6-b4c3-be0b0da63832\\", \\n      1, \\n      false\\n    ], \\n    \\"is_managed\\": false, \\n    \\"last_modified\\": \\"2016-10-28T17:50:54.006\\", \\n    \\"version\\": 1, \\n    \\"owner\\": [\\n      \\"temp_user\\"\\n    ], \\n    \\"dependencies\\": [], \\n    \\"data\\": \\"{\\\\\\"layout\\\\\\": [{\\\\\\"oozieRows\\\\\\": [{\\\\\\"enableOozieDropOnBefore\\\\\\": true, \\\\\\"enableOozieDropOnSide\\\\\\": true, \\\\\\"enableOozieDrop\\\\\\": false, \\\\\\"widgets\\\\\\": [{\\\\\\"status\\\\\\": \\\\\\"\\\\\\", \\\\\\"logsURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"name\\\\\\": \\\\\\"Shell\\\\\\", \\\\\\"widgetType\\\\\\": \\\\\\"shell-widget\\\\\\", \\\\\\"oozieMovable\\\\\\": true, \\\\\\"ooziePropertiesExpanded\\\\\\": false, \\\\\\"externalIdUrl\\\\\\": \\\\\\"\\\\\\", \\\\\\"properties\\\\\\": {}, \\\\\\"isLoading\\\\\\": true, \\\\\\"offset\\\\\\": 0, \\\\\\"actionURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"progress\\\\\\": 0, \\\\\\"klass\\\\\\": \\\\\\"card card-widget span12\\\\\\", \\\\\\"oozieExpanded\\\\\\": false, \\\\\\"id\\\\\\": \\\\\\"f5f910c1-97ee-f7c0-1de4-048fbfbfce20\\\\\\", \\\\\\"size\\\\\\": 12}], \\\\\\"id\\\\\\": \\\\\\"1929b048-b8a3-ad10-5aff-488c1f2808f8\\\\\\", \\\\\\"columns\\\\\\": []}], \\\\\\"rows\\\\\\": [{\\\\\\"enableOozieDropOnBefore\\\\\\": true, \\\\\\"enableOozieDropOnSide\\\\\\": true, \\\\\\"enableOozieDrop\\\\\\": false, \\\\\\"widgets\\\\\\": [{\\\\\\"status\\\\\\": \\\\\\"\\\\\\", \\\\\\"logsURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"name\\\\\\": \\\\\\"Start\\\\\\", \\\\\\"widgetType\\\\\\": \\\\\\"start-widget\\\\\\", \\\\\\"oozieMovable\\\\\\": false, \\\\\\"ooziePropertiesExpanded\\\\\\": false, \\\\\\"externalIdUrl\\\\\\": \\\\\\"\\\\\\", \\\\\\"properties\\\\\\": {}, \\\\\\"isLoading\\\\\\": true, \\\\\\"offset\\\\\\": 0, \\\\\\"actionURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"progress\\\\\\": 0, \\\\\\"klass\\\\\\": \\\\\\"card card-widget span12\\\\\\", \\\\\\"oozieExpanded\\\\\\": false, \\\\\\"id\\\\\\": \\\\\\"3f107997-04cc-8733-60a9-a4bb62cebffc\\\\\\", \\\\\\"size\\\\\\": 12}], \\\\\\"id\\\\\\": \\\\\\"981a811d-2383-31d0-a5f0-e0eee44876f1\\\\\\", \\\\\\"columns\\\\\\": []}, {\\\\\\"enableOozieDropOnBefore\\\\\\": true, \\\\\\"enableOozieDropOnSide\\\\\\": true, \\\\\\"enableOozieDrop\\\\\\": false, \\\\\\"widgets\\\\\\": [{\\\\\\"status\\\\\\": \\\\\\"\\\\\\", \\\\\\"logsURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"name\\\\\\": \\\\\\"Shell\\\\\\", \\\\\\"widgetType\\\\\\": \\\\\\"shell-widget\\\\\\", \\\\\\"oozieMovable\\\\\\": true, \\\\\\"ooziePropertiesExpanded\\\\\\": false, \\\\\\"externalIdUrl\\\\\\": \\\\\\"\\\\\\", \\\\\\"properties\\\\\\": {}, \\\\\\"isLoading\\\\\\": true, \\\\\\"offset\\\\\\": 0, \\\\\\"actionURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"progress\\\\\\": 0, \\\\\\"klass\\\\\\": \\\\\\"card card-widget span12\\\\\\", \\\\\\"oozieExpanded\\\\\\": false, \\\\\\"id\\\\\\": \\\\\\"f5f910c1-97ee-f7c0-1de4-048fbfbfce20\\\\\\", \\\\\\"size\\\\\\": 12}], \\\\\\"id\\\\\\": \\\\\\"1929b048-b8a3-ad10-5aff-488c1f2808f8\\\\\\", \\\\\\"columns\\\\\\": []}, {\\\\\\"enableOozieDropOnBefore\\\\\\": true, \\\\\\"enableOozieDropOnSide\\\\\\": true, \\\\\\"enableOozieDrop\\\\\\": false, \\\\\\"widgets\\\\\\": [{\\\\\\"status\\\\\\": \\\\\\"\\\\\\", \\\\\\"logsURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"name\\\\\\": \\\\\\"End\\\\\\", \\\\\\"widgetType\\\\\\": \\\\\\"end-widget\\\\\\", \\\\\\"oozieMovable\\\\\\": false, \\\\\\"ooziePropertiesExpanded\\\\\\": false, \\\\\\"externalIdUrl\\\\\\": \\\\\\"\\\\\\", \\\\\\"properties\\\\\\": {}, \\\\\\"isLoading\\\\\\": true, \\\\\\"offset\\\\\\": 0, \\\\\\"actionURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"progress\\\\\\": 0, \\\\\\"klass\\\\\\": \\\\\\"card card-widget span12\\\\\\", \\\\\\"oozieExpanded\\\\\\": false, \\\\\\"id\\\\\\": \\\\\\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\\\\\\", \\\\\\"size\\\\\\": 12}], \\\\\\"id\\\\\\": \\\\\\"8fc98b1d-5a92-bf1e-1bd6-380b311b8f98\\\\\\", \\\\\\"columns\\\\\\": []}, {\\\\\\"enableOozieDropOnBefore\\\\\\": true, \\\\\\"enableOozieDropOnSide\\\\\\": true, \\\\\\"enableOozieDrop\\\\\\": false, \\\\\\"widgets\\\\\\": [{\\\\\\"status\\\\\\": \\\\\\"\\\\\\", \\\\\\"logsURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"name\\\\\\": \\\\\\"Kill\\\\\\", \\\\\\"widgetType\\\\\\": \\\\\\"kill-widget\\\\\\", \\\\\\"oozieMovable\\\\\\": true, \\\\\\"ooziePropertiesExpanded\\\\\\": false, \\\\\\"externalIdUrl\\\\\\": \\\\\\"\\\\\\", \\\\\\"properties\\\\\\": {}, \\\\\\"isLoading\\\\\\": true, \\\\\\"offset\\\\\\": 0, \\\\\\"actionURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"progress\\\\\\": 0, \\\\\\"klass\\\\\\": \\\\\\"card card-widget span12\\\\\\", \\\\\\"oozieExpanded\\\\\\": false, \\\\\\"id\\\\\\": \\\\\\"17c9c895-5a16-7443-bb81-f34b30b21548\\\\\\", \\\\\\"size\\\\\\": 12}], \\\\\\"id\\\\\\": \\\\\\"0a5ba4b8-3179-c50c-1203-e313aa13a4d1\\\\\\", \\\\\\"columns\\\\\\": []}], \\\\\\"oozieEndRow\\\\\\": {\\\\\\"enableOozieDropOnBefore\\\\\\": true, \\\\\\"enableOozieDropOnSide\\\\\\": true, \\\\\\"enableOozieDrop\\\\\\": false, \\\\\\"widgets\\\\\\": [{\\\\\\"status\\\\\\": \\\\\\"\\\\\\", \\\\\\"logsURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"name\\\\\\": \\\\\\"End\\\\\\", \\\\\\"widgetType\\\\\\": \\\\\\"end-widget\\\\\\", \\\\\\"oozieMovable\\\\\\": false, \\\\\\"ooziePropertiesExpanded\\\\\\": false, \\\\\\"externalIdUrl\\\\\\": \\\\\\"\\\\\\", \\\\\\"properties\\\\\\": {}, \\\\\\"isLoading\\\\\\": true, \\\\\\"offset\\\\\\": 0, \\\\\\"actionURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"progress\\\\\\": 0, \\\\\\"klass\\\\\\": \\\\\\"card card-widget span12\\\\\\", \\\\\\"oozieExpanded\\\\\\": false, \\\\\\"id\\\\\\": \\\\\\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\\\\\\", \\\\\\"size\\\\\\": 12}], \\\\\\"id\\\\\\": \\\\\\"8fc98b1d-5a92-bf1e-1bd6-380b311b8f98\\\\\\", \\\\\\"columns\\\\\\": []}, \\\\\\"oozieKillRow\\\\\\": {\\\\\\"enableOozieDropOnBefore\\\\\\": true, \\\\\\"enableOozieDropOnSide\\\\\\": true, \\\\\\"enableOozieDrop\\\\\\": false, \\\\\\"widgets\\\\\\": [{\\\\\\"status\\\\\\": \\\\\\"\\\\\\", \\\\\\"logsURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"name\\\\\\": \\\\\\"Kill\\\\\\", \\\\\\"widgetType\\\\\\": \\\\\\"kill-widget\\\\\\", \\\\\\"oozieMovable\\\\\\": true, \\\\\\"ooziePropertiesExpanded\\\\\\": false, \\\\\\"externalIdUrl\\\\\\": \\\\\\"\\\\\\", \\\\\\"properties\\\\\\": {}, \\\\\\"isLoading\\\\\\": true, \\\\\\"offset\\\\\\": 0, \\\\\\"actionURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"progress\\\\\\": 0, \\\\\\"klass\\\\\\": \\\\\\"card card-widget span12\\\\\\", \\\\\\"oozieExpanded\\\\\\": false, \\\\\\"id\\\\\\": \\\\\\"17c9c895-5a16-7443-bb81-f34b30b21548\\\\\\", \\\\\\"size\\\\\\": 12}], \\\\\\"id\\\\\\": \\\\\\"0a5ba4b8-3179-c50c-1203-e313aa13a4d1\\\\\\", \\\\\\"columns\\\\\\": []}, \\\\\\"enableOozieDropOnAfter\\\\\\": true, \\\\\\"oozieStartRow\\\\\\": {\\\\\\"enableOozieDropOnBefore\\\\\\": true, \\\\\\"enableOozieDropOnSide\\\\\\": true, \\\\\\"enableOozieDrop\\\\\\": false, \\\\\\"widgets\\\\\\": [{\\\\\\"status\\\\\\": \\\\\\"\\\\\\", \\\\\\"logsURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"name\\\\\\": \\\\\\"Start\\\\\\", \\\\\\"widgetType\\\\\\": \\\\\\"start-widget\\\\\\", \\\\\\"oozieMovable\\\\\\": false, \\\\\\"ooziePropertiesExpanded\\\\\\": false, \\\\\\"externalIdUrl\\\\\\": \\\\\\"\\\\\\", \\\\\\"properties\\\\\\": {}, \\\\\\"isLoading\\\\\\": true, \\\\\\"offset\\\\\\": 0, \\\\\\"actionURL\\\\\\": \\\\\\"\\\\\\", \\\\\\"progress\\\\\\": 0, \\\\\\"klass\\\\\\": \\\\\\"card card-widget span12\\\\\\", \\\\\\"oozieExpanded\\\\\\": false, \\\\\\"id\\\\\\": \\\\\\"3f107997-04cc-8733-60a9-a4bb62cebffc\\\\\\", \\\\\\"size\\\\\\": 12}], \\\\\\"id\\\\\\": \\\\\\"981a811d-2383-31d0-a5f0-e0eee44876f1\\\\\\", \\\\\\"columns\\\\\\": []}, \\\\\\"klass\\\\\\": \\\\\\"card card-home card-column span12\\\\\\", \\\\\\"enableOozieDropOnBefore\\\\\\": true, \\\\\\"drops\\\\\\": [\\\\\\"temp\\\\\\"], \\\\\\"id\\\\\\": \\\\\\"656fca35-ebb7-7ba6-6774-5bc22dcc9340\\\\\\", \\\\\\"size\\\\\\": 12}], \\\\\\"workflow\\\\\\": {\\\\\\"properties\\\\\\": {\\\\\\"job_xml\\\\\\": \\\\\\"\\\\\\", \\\\\\"description\\\\\\": \\\\\\"\\\\\\", \\\\\\"parameters\\\\\\": [{\\\\\\"name\\\\\\": \\\\\\"oozie.use.system.libpath\\\\\\", \\\\\\"value\\\\\\": true}], \\\\\\"sla_enabled\\\\\\": false, \\\\\\"deployment_dir\\\\\\": \\\\\\"/user/hue/oozie/workspaces/hue-oozie-1477697614.12\\\\\\", \\\\\\"schema_version\\\\\\": \\\\\\"uri:oozie:workflow:0.5\\\\\\", \\\\\\"sla\\\\\\": [{\\\\\\"value\\\\\\": false, \\\\\\"key\\\\\\": \\\\\\"enabled\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"${nominal_time}\\\\\\", \\\\\\"key\\\\\\": \\\\\\"nominal-time\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"\\\\\\", \\\\\\"key\\\\\\": \\\\\\"should-start\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"${30 * MINUTES}\\\\\\", \\\\\\"key\\\\\\": \\\\\\"should-end\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"\\\\\\", \\\\\\"key\\\\\\": \\\\\\"max-duration\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"\\\\\\", \\\\\\"key\\\\\\": \\\\\\"alert-events\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"\\\\\\", \\\\\\"key\\\\\\": \\\\\\"alert-contact\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"\\\\\\", \\\\\\"key\\\\\\": \\\\\\"notification-msg\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"\\\\\\", \\\\\\"key\\\\\\": \\\\\\"upstream-apps\\\\\\"}], \\\\\\"show_arrows\\\\\\": true, \\\\\\"wf1_id\\\\\\": null, \\\\\\"properties\\\\\\": []}, \\\\\\"name\\\\\\": \\\\\\"example-wf\\\\\\", \\\\\\"versions\\\\\\": [\\\\\\"uri:oozie:workflow:0.4\\\\\\", \\\\\\"uri:oozie:workflow:0.4.5\\\\\\", \\\\\\"uri:oozie:workflow:0.5\\\\\\"], \\\\\\"isDirty\\\\\\": true, \\\\\\"movedNode\\\\\\": null, \\\\\\"linkMapping\\\\\\": {\\\\\\"f5f910c1-97ee-f7c0-1de4-048fbfbfce20\\\\\\": [\\\\\\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\\\\\\"], \\\\\\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\\\\\\": [], \\\\\\"3f107997-04cc-8733-60a9-a4bb62cebffc\\\\\\": [\\\\\\"f5f910c1-97ee-f7c0-1de4-048fbfbfce20\\\\\\"], \\\\\\"17c9c895-5a16-7443-bb81-f34b30b21548\\\\\\": []}, \\\\\\"nodeIds\\\\\\": [\\\\\\"3f107997-04cc-8733-60a9-a4bb62cebffc\\\\\\", \\\\\\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\\\\\\", \\\\\\"17c9c895-5a16-7443-bb81-f34b30b21548\\\\\\", \\\\\\"f5f910c1-97ee-f7c0-1de4-048fbfbfce20\\\\\\"], \\\\\\"nodes\\\\\\": [{\\\\\\"properties\\\\\\": {}, \\\\\\"name\\\\\\": \\\\\\"Start\\\\\\", \\\\\\"children\\\\\\": [{\\\\\\"to\\\\\\": \\\\\\"f5f910c1-97ee-f7c0-1de4-048fbfbfce20\\\\\\"}], \\\\\\"actionParametersFetched\\\\\\": false, \\\\\\"type\\\\\\": \\\\\\"start-widget\\\\\\", \\\\\\"id\\\\\\": \\\\\\"3f107997-04cc-8733-60a9-a4bb62cebffc\\\\\\", \\\\\\"actionParameters\\\\\\": []}, {\\\\\\"properties\\\\\\": {}, \\\\\\"name\\\\\\": \\\\\\"End\\\\\\", \\\\\\"children\\\\\\": [], \\\\\\"actionParametersFetched\\\\\\": false, \\\\\\"type\\\\\\": \\\\\\"end-widget\\\\\\", \\\\\\"id\\\\\\": \\\\\\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\\\\\\", \\\\\\"actionParameters\\\\\\": []}, {\\\\\\"properties\\\\\\": {\\\\\\"body\\\\\\": \\\\\\"\\\\\\", \\\\\\"cc\\\\\\": \\\\\\"\\\\\\", \\\\\\"to\\\\\\": \\\\\\"\\\\\\", \\\\\\"enableMail\\\\\\": false, \\\\\\"message\\\\\\": \\\\\\"Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]\\\\\\", \\\\\\"subject\\\\\\": \\\\\\"\\\\\\"}, \\\\\\"name\\\\\\": \\\\\\"Kill\\\\\\", \\\\\\"children\\\\\\": [], \\\\\\"actionParametersFetched\\\\\\": false, \\\\\\"type\\\\\\": \\\\\\"kill-widget\\\\\\", \\\\\\"id\\\\\\": \\\\\\"17c9c895-5a16-7443-bb81-f34b30b21548\\\\\\", \\\\\\"actionParameters\\\\\\": []}, {\\\\\\"properties\\\\\\": {\\\\\\"files\\\\\\": [], \\\\\\"job_xml\\\\\\": \\\\\\"\\\\\\", \\\\\\"retry_interval\\\\\\": [], \\\\\\"retry_max\\\\\\": [], \\\\\\"job_properties\\\\\\": [], \\\\\\"capture_output\\\\\\": true, \\\\\\"shell_command\\\\\\": \\\\\\"ls\\\\\\", \\\\\\"arguments\\\\\\": [], \\\\\\"prepares\\\\\\": [], \\\\\\"credentials\\\\\\": [], \\\\\\"env_var\\\\\\": [], \\\\\\"sla\\\\\\": [{\\\\\\"value\\\\\\": false, \\\\\\"key\\\\\\": \\\\\\"enabled\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"${nominal_time}\\\\\\", \\\\\\"key\\\\\\": \\\\\\"nominal-time\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"\\\\\\", \\\\\\"key\\\\\\": \\\\\\"should-start\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"${30 * MINUTES}\\\\\\", \\\\\\"key\\\\\\": \\\\\\"should-end\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"\\\\\\", \\\\\\"key\\\\\\": \\\\\\"max-duration\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"\\\\\\", \\\\\\"key\\\\\\": \\\\\\"alert-events\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"\\\\\\", \\\\\\"key\\\\\\": \\\\\\"alert-contact\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"\\\\\\", \\\\\\"key\\\\\\": \\\\\\"notification-msg\\\\\\"}, {\\\\\\"value\\\\\\": \\\\\\"\\\\\\", \\\\\\"key\\\\\\": \\\\\\"upstream-apps\\\\\\"}], \\\\\\"archives\\\\\\": []}, \\\\\\"name\\\\\\": \\\\\\"shell-f5f9\\\\\\", \\\\\\"children\\\\\\": [{\\\\\\"to\\\\\\": \\\\\\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\\\\\\"}, {\\\\\\"error\\\\\\": \\\\\\"17c9c895-5a16-7443-bb81-f34b30b21548\\\\\\"}], \\\\\\"actionParametersFetched\\\\\\": false, \\\\\\"type\\\\\\": \\\\\\"shell-widget\\\\\\", \\\\\\"id\\\\\\": \\\\\\"f5f910c1-97ee-f7c0-1de4-048fbfbfce20\\\\\\", \\\\\\"actionParameters\\\\\\": []}], \\\\\\"id\\\\\\": null, \\\\\\"nodeNamesMapping\\\\\\": {\\\\\\"f5f910c1-97ee-f7c0-1de4-048fbfbfce20\\\\\\": \\\\\\"shell-f5f9\\\\\\", \\\\\\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\\\\\\": \\\\\\"End\\\\\\", \\\\\\"3f107997-04cc-8733-60a9-a4bb62cebffc\\\\\\": \\\\\\"Start\\\\\\", \\\\\\"17c9c895-5a16-7443-bb81-f34b30b21548\\\\\\": \\\\\\"Kill\\\\\\"}, \\\\\\"uuid\\\\\\": \\\\\\"4a471e2a-0993-651b-a9f7-4e7724e4a01a\\\\\\"}}\\", \\n    \\"name\\": \\"example-wf\\"\\n  }\\n}\\n]\\n"'
    response = self.c.post('/desktop/api2/doc/import/', {'documents': workflow_docs})
    data = json.loads(response.content)

    assert_true('message' in data, data)
    assert_true('Installed 1 object' in data['message'], data)
    wf_docs = Document2.objects.filter(name='example-wf')
    assert_equal(1, wf_docs.count()) # Successfully imported by 'test' user

    response = self.c.post(reverse('oozie:editor_submit_workflow', kwargs={'doc_id': wf_docs[0].id}),
                           data={
                               u'form-0-name': [u'oozie.use.system.libpath'],
                               u'form-MAX_NUM_FORMS': [u'1000'],
                               u'form-TOTAL_FORMS': [u'1'],
                               u'form-INITIAL_FORMS': [u'1'],
                               u'form-0-value': [u'True']
                           },
                           follow=True)
    job = OozieServerProvider.wait_until_completion(response.context[0]['oozie_workflow'].id)

    assert_true(job.status in ('SUCCEEDED', 'KILLED'), job.status)


class TestDashboardWithOozie(OozieBase):

  def setUp(self):
    super(TestDashboardWithOozie, self).setUp()

    self.c = make_logged_in_client()
    self.wf = create_workflow(self.c, self.user)
    self.setup_simple_workflow()

  def tearDown(self):
    try:
      self.wf.delete(skip_trash=True)
    except:
      LOG.exception('failed to tear down tests')

  def test_submit_external_workflow(self):
    # Check popup and reading workflow.xml and job.properties
    oozie_xml = self.wf.to_xml({'output': '/path'})
    deployment_dir = self.cluster.fs.mktemp(prefix='test_submit_external_workflow')
    application_path = deployment_dir + '/workflow.xml'

    self.cluster.fs.create(application_path, data=oozie_xml)

    response = self.c.get(reverse('oozie:submit_external_job', kwargs={'application_path': application_path}))
    assert_equal([{'name': 'SLEEP', 'value': ''}, {'name': 'output', 'value': ''}],
                  response.context[0]['params_form'].initial)

    oozie_properties = """
#
# Licensed to the Hue
#
nameNode=hdfs://localhost:8020
jobTracker=localhost:8021
my_prop_not_filtered=10
    """
    self.cluster.fs.create(deployment_dir + '/job.properties', data=oozie_properties)

    response = self.c.get(reverse('oozie:submit_external_job', kwargs={'application_path': application_path}))
    assert_equal([{'name': 'SLEEP', 'value': ''}, {'name': 'my_prop_not_filtered', 'value': '10'}, {'name': 'output', 'value': ''}],
                  response.context[0]['params_form'].initial)

    # Submit, just check if submittion worked
    response = self.c.post(reverse('oozie:submit_external_job', kwargs={'application_path': application_path}), {
        u'form-MAX_NUM_FORMS': [u''],
        u'form-TOTAL_FORMS': [u'3'],
        u'form-INITIAL_FORMS': [u'3'],
        u'form-0-name': [u'SLEEP'],
        u'form-0-value': [u'ilovesleep'],
        u'form-1-name': [u'my_prop_not_filtered'],
        u'form-1-value': [u'10'],
        u'form-2-name': [u'output'],
        u'form-2-value': [u'/path/output'],
    }, follow=True)

    assert_true('oozie_workflow' in response.context[0]._data.keys(), response.content)
    wf_id = response.context[0]._data['oozie_workflow'].id

    # Check if response contains log data
    response = self.c.get(reverse('oozie:get_oozie_job_log', args=[response.context[0]._data['oozie_workflow'].id]) + "?format=json&limit=100&loglevel=INFO&recent=2h:30m")
    data = json.loads(response.content)
    assert_true(len(data['log'].split('\n')) <= 100)
    assert_equal('RUNNING', data['status'])
    assert_true("INFO" in data['log'])

    # Clean-up
    response = self.c.post(reverse('oozie:manage_oozie_jobs', args=[wf_id, 'kill']))
    data = json.loads(response.content)
    assert_equal(0, data.get('status'), data)

  def test_oozie_not_running_message(self):
    raise SkipTest # Not reseting the oozie url for some reason

    finish = OOZIE_URL.set_for_testing('http://not_localhost:11000/bad')
    try:
      response = self.c.get(reverse('oozie:list_oozie_workflows'))
      assert_true('The Oozie server is not running' in response.content, response.content)
    finally:
      finish()

  def test_httppool(self):
    # With http pool the http connection is reused and so new connection count is 0
    superuser_client = make_logged_in_client(is_superuser=True)
    start_log = "--START HTTP POOL TEST--"
    LOG.warn(start_log)
    superuser_client.get(reverse('oozie:list_oozie_workflows'))
    superuser_client.get(reverse('oozie:list_oozie_workflows') + "?format=json")
    superuser_client.get(reverse('oozie:list_oozie_workflows') + "?format=json&status=RUNNING&status=PREP&status=SUSPENDED")
    superuser_client.get(reverse('oozie:list_oozie_workflows') + "?format=json&status=KILLED&status=FAILED")
    end_log = "--END HTTP POOL TEST--"
    LOG.warn(end_log)
    response = superuser_client.get(reverse(views.log_view))

    s1 = response._container[0].index(start_log)
    e1 = response._container[0].index(end_log)
    c1 = response._container[0][e1:s1].count('Starting new HTTP')
    assert_equal(c1, 0)

class TestDashboard(OozieMockBase):

  def test_manage_workflow_dashboard(self):
    # Display of buttons happens in js now
    response = self.c.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[0]]), {}, follow=True)
    assert_true(('%s/kill' % MockOozieApi.WORKFLOW_IDS[0]) in response.content, response.content)
    assert_true(('rerun_oozie_job/%s' % MockOozieApi.WORKFLOW_IDS[0]) in response.content, response.content)
    assert_true(('%s/suspend' % MockOozieApi.WORKFLOW_IDS[0]) in response.content, response.content)
    assert_true(('%s/resume' % MockOozieApi.WORKFLOW_IDS[0]) in response.content, response.content)

    response = self.c.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[1]]), {}, follow=True)
    assert_true(('%s/kill' % MockOozieApi.WORKFLOW_IDS[1]) in response.content, response.content)
    assert_true(('rerun_oozie_job/%s' % MockOozieApi.WORKFLOW_IDS[1]) in response.content, response.content)


  def test_manage_coordinator_dashboard(self):
    # Display of buttons happens in js now
    response = self.c.get(reverse('oozie:list_oozie_coordinator', args=[MockOozieApi.COORDINATOR_IDS[0]]), {}, follow=True)
    assert_true(('%s/kill' % MockOozieApi.COORDINATOR_IDS[0]) in response.content, response.content)
    assert_true(('rerun_oozie_coord/%s' % MockOozieApi.COORDINATOR_IDS[0]) in response.content, response.content)
    assert_true(('%s/suspend' % MockOozieApi.COORDINATOR_IDS[0]) in response.content, response.content)
    assert_true(('%s/resume' % MockOozieApi.COORDINATOR_IDS[0]) in response.content, response.content)

    # Test log filtering
    url = reverse('oozie:get_oozie_job_log', args=[MockOozieApi.COORDINATOR_IDS[0]])
    assert_true(url in response.content, response.content)
    response = self.c.get(url + "?format=json&limit=100&loglevel=INFO&text=MapReduce")
    data = json.loads(response.content)
    assert_true(len(data['log'].split('\n')) <= 100)
    assert_equal('RUNNING', data['status'])
    assert_true("INFO" in data['log'])


  def test_manage_bundles_dashboard(self):
    # Display of buttons happens in js now
    response = self.c.get(reverse('oozie:list_oozie_bundle', args=[MockOozieApi.BUNDLE_IDS[0]]), {}, follow=True)
    assert_true(('%s/kill' % MockOozieApi.BUNDLE_IDS[0]) in response.content, response.content)
    assert_true(('rerun_oozie_bundle/%s' % MockOozieApi.BUNDLE_IDS[0]) in response.content, response.content)
    assert_true(('%s/suspend' % MockOozieApi.BUNDLE_IDS[0]) in response.content, response.content)
    assert_true(('%s/resume' % MockOozieApi.BUNDLE_IDS[0]) in response.content, response.content)


  def test_rerun_coordinator(self):
    response = self.c.get(reverse('oozie:rerun_oozie_coord', args=[MockOozieApi.WORKFLOW_IDS[0], '/path']))
    assert_true('Rerun' in response.content, response.content)

  def test_sync_coord_workflow(self):
    wf_doc = save_temp_workflow(MockOozieApi.JSON_WORKFLOW_LIST[5], self.user)
    reset = ENABLE_V2.set_for_testing(True)
    try:
      response = self.c.get(reverse('oozie:sync_coord_workflow', args=[MockOozieApi.WORKFLOW_IDS[5]]))
      assert_equal([{'name':'Dryrun', 'value': False}, {'name':'ls_arg', 'value': '-l'}], response.context[0]['params_form'].initial)
    finally:
      wf_doc.delete()
      reset()

  def test_rerun_coordinator_permissions(self):
    post_data = {
        u'form-MAX_NUM_FORMS': [u''],
        u'nocleanup': [u'on'],
        u'refresh': [u'on'],
        u'form-TOTAL_FORMS': [u'0'],
        u'actions': [u'1'],
        u'form-INITIAL_FORMS': [u'0']
    }

    response = self.c.post(reverse('oozie:rerun_oozie_coord', args=[MockOozieApi.COORDINATOR_IDS[0], '/path']), post_data)
    assert_false('Permission denied' in response.content, response.content)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "oozie")

    response = client_not_me.post(reverse('oozie:rerun_oozie_coord', args=[MockOozieApi.COORDINATOR_IDS[0], '/path']), post_data)
    assert_true('Permission denied' in response.content, response.content)


  def test_rerun_bundle(self):
    response = self.c.get(reverse('oozie:rerun_oozie_coord', args=[MockOozieApi.WORKFLOW_IDS[0], '/path']))
    assert_true('Rerun' in response.content, response.content)


  def test_rerun_bundle_permissions(self):
    post_data = {
        u'end_1': [u'01:55 PM'],
        u'end_0': [u'03/02/2013'],
        u'refresh': [u'on'],
        u'nocleanup': [u'on'],
        u'start_0': [u'02/27/2013'],
        u'start_1': [u'01:55 PM'],
        u'coordinators': [u'DailySleep'],

        u'form-MAX_NUM_FORMS': [u''],
        u'form-TOTAL_FORMS': [u'3'],
        u'form-INITIAL_FORMS': [u'3'],
        u'form-0-name': [u'oozie.use.system.libpath'],
        u'form-0-value': [u'true'],
        u'form-1-name': [u'hue-id-b'],
        u'form-1-value': [u'22'],
        u'form-2-name': [u'oozie.bundle.application.path'],
        u'form-2-value': [u'hdfs://localhost:8020/path'],
    }

    response = self.c.post(reverse('oozie:rerun_oozie_bundle', args=[MockOozieApi.BUNDLE_IDS[0], '/path']), post_data)
    assert_false('Permission denied' in response.content, response.content)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "oozie")

    response = client_not_me.post(reverse('oozie:rerun_oozie_bundle', args=[MockOozieApi.BUNDLE_IDS[0], '/path']), post_data)
    assert_true('Permission denied' in response.content, response.content)


  def test_list_workflows(self):
    response = self.c.get(reverse('oozie:list_oozie_workflows'))
    assert_true('Running' in response.content, response.content)
    assert_true('Completed' in response.content, response.content)

    response = self.c.get(reverse('oozie:list_oozie_workflows') + "?format=json")
    assert_true(len(json.loads(response.content)['jobs']) == 0)

    response = self.c.get(reverse('oozie:list_oozie_workflows') + "?format=json&status=RUNNING&status=PREP&status=SUSPENDED")
    for wf_id in MockOozieApi.WORKFLOW_IDS:
      assert_true(wf_id in response.content, response.content)

    response = self.c.get(reverse('oozie:list_oozie_workflows') + "?format=json&status=KILLED&status=FAILED")
    for wf_id in MockOozieApi.WORKFLOW_IDS:
      assert_true(wf_id in response.content, response.content)


  def test_list_coordinators(self):
    response = self.c.get(reverse('oozie:list_oozie_coordinators'))
    assert_true('Running' in response.content, response.content)
    assert_true('Completed' in response.content, response.content)

    response = self.c.get(reverse('oozie:list_oozie_coordinators') + "?format=json")
    assert_true(len(json.loads(response.content)['jobs']) == 0)

    response = self.c.get(reverse('oozie:list_oozie_coordinators') + "?format=json&status=RUNNING&status=PREP&status=SUSPENDED")
    for coord_id in MockOozieApi.COORDINATOR_IDS:
      assert_true(coord_id in response.content, response.content)

    response = self.c.get(reverse('oozie:list_oozie_coordinators') + "?format=json&status=KILLED&status=FAILED&status=DONEWITHERROR")
    for coord_id in MockOozieApi.COORDINATOR_IDS:
      assert_true(coord_id in response.content, response.content)


  def test_list_bundles(self):
    response = self.c.get(reverse('oozie:list_oozie_bundles'))
    assert_true('Running' in response.content, response.content)
    assert_true('Completed' in response.content, response.content)

    response = self.c.get(reverse('oozie:list_oozie_bundles') + "?format=json&status=RUNNING")
    for coord_id in MockOozieApi.BUNDLE_IDS:
      assert_true(coord_id in response.content, response.content)

    response = self.c.get(reverse('oozie:list_oozie_bundles') + "?format=json&status=SUCCEEDED")
    for coord_id in MockOozieApi.BUNDLE_IDS:
      assert_true(coord_id in response.content, response.content)

    response = self.c.get(reverse('oozie:list_oozie_bundles') + "?format=json&status=KILLED")
    for coord_id in MockOozieApi.BUNDLE_IDS:
      assert_true(coord_id in response.content, response.content)


  def test_list_workflow(self):
    response = self.c.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[0]]))
    assert_true('Workflow WordCount1' in response.content, response.content)
    assert_true('Workflow' in response.content, response.content)

    response = self.c.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[0]]) + '?coordinator_job_id=%s' % MockOozieApi.COORDINATOR_IDS[0])
    assert_true('Workflow WordCount1' in response.content, response.content)
    assert_true('Workflow' in response.content, response.content)
    assert_true('DailyWordCount1' in response.content, response.content)
    assert_true('Coordinator' in response.content, response.content)

    # Test for unicode character '�' rendering
    response = self.c.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[6]]))
    assert_false('UnicodeEncodeError' in response.content, response.content)
    assert_true('TestUnicodeParam' in response.content, response.content)


  def test_list_workflow_action(self):
    response = self.c.get(reverse('oozie:list_oozie_workflow_action', args=['XXX']))
    assert_true('Action WordCount' in response.content, response.content)
    assert_true('job_201302280955_0018' in response.content, response.content)
    assert_true('job_201302280955_0019' in response.content, response.content)
    assert_true('job_201302280955_0020' in response.content, response.content)

    response = self.c.get(reverse('oozie:list_oozie_workflow_action', args=['XXX']) + '?coordinator_job_id=%s&bundle_job_id=%s' % (MockOozieApi.COORDINATOR_IDS[0], MockOozieApi.BUNDLE_IDS[0]))
    assert_true('Bundle' in response.content, response.content)
    assert_true('MyBundle1' in response.content, response.content)
    assert_true('Coordinator' in response.content, response.content)
    assert_true('DailyWordCount1' in response.content, response.content)
    assert_true('Workflow' in response.content, response.content)
    assert_true('WordCount1' in response.content, response.content)


  def test_list_coordinator(self):
    response = self.c.get(reverse('oozie:list_oozie_coordinator', args=[MockOozieApi.COORDINATOR_IDS[4]]))
    assert_true(u'Coordinator DåilyWordCount5' in response.content.decode('utf-8', 'replace'), response.content.decode('utf-8', 'replace'))
    assert_true('Workflow' in response.content, response.content)

    # Test action list
    response = self.c.get(reverse('oozie:list_oozie_coordinator', args=[MockOozieApi.COORDINATOR_IDS[5]]) + "?format=json&offset=1")
    assert_true('00000013-120706144403213-oozie-oozi-C@1' in response.content, response.content)
    assert_true('00000013-120706144403213-oozie-oozi-C@2' in response.content, response.content)
    assert_true('00000013-120706144403213-oozie-oozi-C@3' in response.content, response.content)
    assert_true('00000013-120706144403213-oozie-oozi-C@4' in response.content, response.content)


  def test_list_bundle(self):
    response = self.c.get(reverse('oozie:list_oozie_bundle', args=[MockOozieApi.BUNDLE_IDS[0]]))
    assert_true('Bundle MyBundle1' in response.content, response.content)
    assert_true('Coordinators' in response.content, response.content)

  def test_workflow_timezones(self):
    job = MockOozieApi.get_job(MockOozieApi(), '0000007-120725142744176-oozie-oozi-W')
    assert_equal(job.appName, 'WordCount5')

  def test_manage_oozie_jobs(self):
    try:
      self.c.get(reverse('oozie:manage_oozie_jobs', args=[MockOozieApi.COORDINATOR_IDS[0], 'kill']))
      assert False
    except:
      LOG.exception('failed to get oozie job')

    response = self.c.post(reverse('oozie:manage_oozie_jobs', args=[MockOozieApi.COORDINATOR_IDS[0], 'kill']))
    data = json.loads(response.content)
    assert_equal(0, data['status'])

    response = self.c.post(reverse('oozie:manage_oozie_jobs', args=[MockOozieApi.COORDINATOR_IDS[0], 'suspend']))
    data = json.loads(response.content)
    assert_equal(0, data['status'])

    response = self.c.post(reverse('oozie:manage_oozie_jobs', args=[MockOozieApi.COORDINATOR_IDS[0], 'resume']))
    data = json.loads(response.content)
    assert_equal(0, data['status'])

    params = {'actions': '1 2 3'}
    response = self.c.post(reverse('oozie:manage_oozie_jobs', args=[MockOozieApi.COORDINATOR_IDS[0], 'ignore']), params)
    data = json.loads(response.content)
    assert_equal(0, data['status'])

    params = {'end_time': u'Mon, 30 Jul 2012 22:35:48 GMT', 'pause_time': u'Mon, 30 Jul 2012 22:35:48 GMT',
              'concurrency': '1', 'clear_pause_time': 'True'}
    response = self.c.post(reverse('oozie:manage_oozie_jobs', args=[MockOozieApi.COORDINATOR_IDS[0], 'change']), params)
    data = json.loads(response.content)
    assert_equal(0, data['status'])


  def test_workflows_permissions(self):
    response = self.c.get(reverse('oozie:list_oozie_workflows') + '?format=json&status=SUCCEEDED')
    assert_true('WordCount1' in response.content, response.content)

    # Rerun
    response = self.c.get(reverse('oozie:rerun_oozie_job', kwargs={'job_id': MockOozieApi.WORKFLOW_IDS[0],
                                                                   'app_path': MockOozieApi.JSON_WORKFLOW_LIST[0]['appPath']}))
    assert_false('Permission denied.' in response.content, response.content)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test', recreate=True)
    grant_access("not_me", "not_me", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_workflows') + '?format=json&status=SUCCEEDED')
    assert_false('WordCount1' in response.content, response.content)

    # Rerun
    response = client_not_me.get(reverse('oozie:rerun_oozie_job', kwargs={'job_id': MockOozieApi.WORKFLOW_IDS[0],
                                                                          'app_path': MockOozieApi.JSON_WORKFLOW_LIST[0]['appPath']}))
    assert_true('Permission denied.' in response.content, response.content)

    # Add read only access
    add_permission("not_me", "dashboard_jobs_access", "dashboard_jobs_access", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_workflows')+"?format=json&status=SUCCEEDED")
    assert_true('WordCount1' in response.content, response.content)

    # Rerun
    response = client_not_me.get(reverse('oozie:rerun_oozie_job', kwargs={'job_id': MockOozieApi.WORKFLOW_IDS[0],
                                                                          'app_path': MockOozieApi.JSON_WORKFLOW_LIST[0]['appPath']}))
    assert_true('Permission denied.' in response.content, response.content)

  def test_workflow_permissions(self):
    response = self.c.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[0]]))
    assert_true('WordCount1' in response.content, response.content)
    assert_false('Permission denied' in response.content, response.content)

    response = self.c.get(reverse('oozie:list_oozie_workflow_action', args=['XXX']))
    assert_false('Permission denied' in response.content, response.content)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test', recreate=True)
    grant_access("not_me", "not_me", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[0]]))
    assert_true('Permission denied' in response.content, response.content)

    response = client_not_me.get(reverse('oozie:list_oozie_workflow_action', args=['XXX']))
    assert_true('Permission denied' in response.content, response.content)

    # Add read only access
    add_permission("not_me", "dashboard_jobs_access", "dashboard_jobs_access", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[0]]))
    assert_false('Permission denied' in response.content, response.content)


  def test_coordinators_permissions(self):
    response = self.c.get(reverse('oozie:list_oozie_coordinators')+"?format=json&status=SUCCEEDED")
    assert_true('DailyWordCount1' in response.content, response.content)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test', recreate=True)
    grant_access("not_me", "not_me", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_coordinators')+"?format=json&status=SUCCEEDED")
    assert_false('DailyWordCount1' in response.content, response.content)

    # Add read only access
    add_permission("not_me", "dashboard_jobs_access", "dashboard_jobs_access", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_coordinators')+"?format=json&status=SUCCEEDED")
    assert_true('DailyWordCount1' in response.content, response.content)


  def test_coordinator_permissions(self):
    response = self.c.get(reverse('oozie:list_oozie_coordinator', args=[MockOozieApi.COORDINATOR_IDS[0]]))
    assert_true('DailyWordCount1' in response.content, response.content)
    assert_false('Permission denied' in response.content, response.content)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test', recreate=True)
    grant_access("not_me", "not_me", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_coordinator', args=[MockOozieApi.COORDINATOR_IDS[0]]))
    assert_true('Permission denied' in response.content, response.content)

    # Add read only access
    add_permission("not_me", "dashboard_jobs_access", "dashboard_jobs_access", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_coordinator', args=[MockOozieApi.COORDINATOR_IDS[0]]))
    assert_false('Permission denied' in response.content, response.content)


  def test_bundles_permissions(self):
    response = self.c.get(reverse('oozie:list_oozie_bundles') + "?format=json&status=SUCCEEDED")
    assert_true('MyBundle1' in response.content, response.content)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test', recreate=True)
    grant_access("not_me", "not_me", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_bundles')+"?format=json&status=SUCCEEDED")
    assert_false('MyBundle1' in response.content, response.content)

    # Add read only access
    add_permission("not_me", "dashboard_jobs_access", "dashboard_jobs_access", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_bundles')+"?format=json&status=SUCCEEDED")
    assert_true('MyBundle1' in response.content, response.content)


  def test_bundle_permissions(self):
    response = self.c.get(reverse('oozie:list_oozie_bundle', args=[MockOozieApi.BUNDLE_IDS[0]]))
    assert_true('MyBundle1' in response.content, response.content)
    assert_false('Permission denied' in response.content, response.content)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test', recreate=True)
    grant_access("not_me", "not_me", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_bundle', args=[MockOozieApi.BUNDLE_IDS[0]]))
    assert_true('Permission denied' in response.content, response.content)

    # Add read only access
    add_permission("not_me", "dashboard_jobs_access", "dashboard_jobs_access", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_bundle', args=[MockOozieApi.BUNDLE_IDS[0]]))
    assert_false('Permission denied' in response.content, response.content)


  def test_good_workflow_status_graph(self):
    finish = ENABLE_V2.set_for_testing(False)
    try:
      workflow_count = Document.objects.available_docs(Workflow, self.user).count()

      response = self.c.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[0]]), {})

      assert_true(response.context[1]._data['workflow_graph'])
      assert_equal(Document.objects.available_docs(Workflow, self.user).count(), workflow_count)
    finally:
      finish()

  def test_bad_workflow_status_graph(self):
    finish = ENABLE_V2.set_for_testing(False)
    try:
      workflow_count = Document.objects.available_docs(Workflow, self.user).count()

      response = self.c.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[1]]), {})

      assert_true(response.context[1]['workflow_graph'] is None)
      assert_equal(Document.objects.available_docs(Workflow, self.user).count(), workflow_count)
    except:
      LOG.exception('failed to test workflow status graph')
      finish()

  def test_list_oozie_sla(self):
    response = self.c.get(reverse('oozie:list_oozie_sla'))
    assert_true('Oozie Dashboard' in response.content, response.content)

    response = self.c.get(reverse('oozie:list_oozie_sla') + "?format=json")
    for sla in MockOozieApi.WORKFLOWS_SLAS:
      assert_equal({"oozie_slas": []}, json.loads(response.content), response.content)

    response = self.c.post(reverse('oozie:list_oozie_sla') + "?format=json", {'job_name': 'kochang'})
    for sla in MockOozieApi.WORKFLOWS_SLAS:
      assert_true('MISS' in response.content, response.content)


class GeneralTestsWithOozie(OozieBase):
  def setUp(self):
    OozieBase.setUp(self)

  def test_import_jobsub_actions(self):
    design = OozieDesign(owner=self.user, name="test")
    action = OozieMapreduceAction(jar_path='/tmp/test.jar')
    action.action_type = OozieMapreduceAction.ACTION_TYPE
    action.save()
    design.root_action = action
    design.save()

    try:
      # There should be 3 from examples
      action = convert_jobsub_design(design)
      assert_equal(design.name, action.name)
      assert_equal(design.description, action.description)
      assert_equal(OozieMapreduceAction.ACTION_TYPE, action.node_type)
    finally:
      OozieDesign.objects.all().delete()
      OozieMapreduceAction.objects.all().delete()


class TestUtils(OozieMockBase):

  def setUp(self):
    OozieMockBase.setUp(self)

    # When updating wf, update wf_json as well!
    self.wf = Document.objects.get_docs(self.user, Workflow).get(name='wf-name-1').content_object


  def test_workflow_to_dict(self):
    workflow_dict = workflow_to_dict(self.wf)

    # Test properties
    assert_true('job_xml' in workflow_dict, workflow_dict)
    assert_true('is_shared' in workflow_dict, workflow_dict)
    assert_true('end' in workflow_dict, workflow_dict)
    assert_true('description' in workflow_dict, workflow_dict)
    assert_true('parameters' in workflow_dict, workflow_dict)
    assert_true('is_single' in workflow_dict, workflow_dict)
    assert_true('deployment_dir' in workflow_dict, workflow_dict)
    assert_true('schema_version' in workflow_dict, workflow_dict)
    assert_true('job_properties' in workflow_dict, workflow_dict)
    assert_true('start' in workflow_dict, workflow_dict)
    assert_true('nodes' in workflow_dict, workflow_dict)
    assert_true('id' in workflow_dict, workflow_dict)
    assert_true('name' in workflow_dict, workflow_dict)

    # Check links
    for node in workflow_dict['nodes']:
      assert_true('child_links' in node, node)

      for link in node['child_links']:
        assert_true('name' in link, link)
        assert_true('comment' in link, link)
        assert_true('parent' in link, link)
        assert_true('child' in link, link)


  def test_model_to_dict(self):
    node_dict = model_to_dict(self.wf.node_set.filter(node_type='start')[0])

    # Test properties
    assert_true('id' in node_dict)
    assert_true('name' in node_dict)
    assert_true('description' in node_dict)
    assert_true('node_type' in node_dict)
    assert_true('workflow' in node_dict)


  def test_smart_path(self):
    assert_equal('${nameNode}/user/${wf:user()}/out', smart_path('out', {'output': '/path/out'}))
    assert_equal('${nameNode}/path', smart_path('/path', {'output': '/path/out'}))
    assert_equal('${nameNode}/path', smart_path('/path', {}))
    assert_equal('${nameNode}${output}', smart_path('${output}', {'output': '/path/out'}))
    assert_equal('hdfs://nn${output}', smart_path('hdfs://nn${output}', {'output': '/path/out'}))

    assert_equal('${output}', smart_path('${output}', {}))
    assert_equal('${output}', smart_path('${output}', {'output': 'hdfs://nn/path/out'}))
    assert_equal('${output}', smart_path('${output}', {'output': '${path}'}))
    assert_equal('${output_dir}', smart_path('${output_dir}', {'output': '/path/out', 'output_dir': 'hdfs://nn/path/out'}))

    assert_equal('${nameNode}/user/${wf:user()}/out', smart_path(' out', {'output': '/path/out'}))
    assert_equal('${nameNode}/user/${wf:user()}/out', smart_path('  out  ', {'output': '/path/out'}))
    assert_equal('hdfs://nn${output}', smart_path(' hdfs://nn${output}', {'output': '/path/out'}))
    assert_equal('hdfs://nn${output}', smart_path(' hdfs://nn${output}  ', {'output': '/path/out'}))
    assert_equal('${output}', smart_path('${output}', None))


  def test_contains_symlink(self):
    assert_false(contains_symlink('out', {'output': '/path/out'}))
    assert_true(contains_symlink('out#out', {'output': '/path/out'}))
    assert_false(contains_symlink('${output}', {'output': '/path/out'}))
    assert_true(contains_symlink('hdfs://nn${output}', {'output': '/path/out#out'}))
    assert_false(contains_symlink('hdfs://nn${output}', {'output': '/path/out'}))
    assert_true(contains_symlink('hdfs://nn#${output}', {'output': 'output'}))
    assert_false(contains_symlink('${output}', {}))
    assert_false(contains_symlink('${output}', {'output': '${path}'}))
    assert_true(contains_symlink('${output_dir}', {'output': '/path/out', 'output_dir': 'hdfs://nn/path/out#out'}))

  def test_convert_to_server_timezone(self):
    # To UTC
    assert_equal(convert_to_server_timezone('2015-07-01T10:10', local_tz='America/Los_Angeles', server_tz='UTC', user='test'), u'2015-07-01T17:10Z')
    assert_equal(convert_to_server_timezone('2015-07-01T10:10', local_tz='Europe/Paris', server_tz='UTC', user='test'), u'2015-07-01T08:10Z')
    # To GMT(+/-)####
    assert_equal(convert_to_server_timezone('2015-07-01T10:10', local_tz='Asia/Jayapura', server_tz='GMT+0800', user='test'), u'2015-07-01T09:10+0800')
    assert_equal(convert_to_server_timezone('2015-07-01T10:10', local_tz='Australia/LHI', server_tz='GMT-0530', user='test'), u'2015-06-30T18:10-0530')
    # Previously created coordinators might have 'Z' appended, we consider them as UTC local time
    assert_equal(convert_to_server_timezone('2015-07-01T10:10Z', local_tz='America/Los_Angeles', server_tz='UTC', user='test'), u'2015-07-01T10:10Z')
    assert_equal(convert_to_server_timezone('2015-07-01T10:10Z', local_tz='Asia/Jayapura', server_tz='GMT+0800', user='test'), u'2015-07-01T18:10+0800')
    assert_equal(convert_to_server_timezone('2015-07-01T10:10Z', local_tz='Australia/LHI', server_tz='GMT-0530', user='test'), u'2015-07-01T04:40-0530')


# Utils
WORKFLOW_DICT = {
    u'deployment_dir': [u''], u'name': [u'wf-name-1'], u'description': [u''],
    u'schema_version': [u'uri:oozie:workflow:0.4'],
    u'parameters': [u'[{"name":"market","value":"US"}]'],
    u'job_xml': [u'jobconf.xml'],
    u'job_properties': [u'[{"name":"sleep-all","value":"${SLEEP}"}]']
}
COORDINATOR_DICT = {
    u'name': [u'MyCoord'], u'description': [u'Description of my coordinator'],
    u'workflow': [u'1'],
    u'frequency_number': [u'1'], u'frequency_unit': [u'days'],
    u'start_0': [u'07/01/2012'], u'start_1': [u'12:00 AM'],
    u'end_0': [u'07/04/2012'], u'end_1': [u'12:00 AM'],
    u'timezone': [u'America/Los_Angeles'],
    u'parameters': [u'[{"name":"market","value":"US"}]'],
    u'job_properties': [u'[{"name":"username","value":"${coord:user()}"},{"name":"SLEEP","value":"1000"}]'],
    u'timeout': [u'100'],
    u'concurrency': [u'3'],
    u'execution': [u'FIFO'],
    u'throttle': [u'10'],
    u'schema_version': [u'uri:oozie:coordinator:0.2'],
    u'cron_frequency': [u'0 0 * * *'],
    u'isAdvancedCron': [u'on'],
}
BUNDLE_DICT = {
    u'name': [u'MyBundle'], u'description': [u'Description of my bundle'],
    u'parameters': [u'[{"name":"market","value":"US,France"}]'],
    u'kick_off_time_0': [u'07/01/2012'], u'kick_off_time_1': [u'12:00 AM'],
    u'schema_version': [u'uri:oozie:coordinator:0.2']
}


def add_node(workflow, name, node_type, parents, attrs={}):
  """
  create a node of type node_type and associate the listed parents.
  """
  NodeClass = NODE_TYPES[node_type]
  node = NodeClass(workflow=workflow, node_type=node_type, name=name)
  for attr in attrs:
    setattr(node, attr, attrs[attr])
  node.save()

  # Add parent
  # If skipped, remember to preserve order: regular links first, then error link
  if parents:
    for parent in parents:
      name = 'ok'
      if parent.node_type == 'start' or parent.node_type == 'join':
        name = 'to'
      elif parent.node_type == 'fork' or parent.node_type == 'decision':
        name = 'start'
      link = Link(parent=parent, child=node, name=name)
      link.save()

  # Create error link
  if node_type != 'fork' and node_type != 'decision' and node_type != 'join':
    link = Link(parent=node, child=Kill.objects.get(name='kill', workflow=workflow), name="error")
  link.save()

  return node


def create_workflow(client, user, workflow_dict=WORKFLOW_DICT):
  name = str(workflow_dict['name'][0])

  # If not infinite looping
  Node.objects.filter(workflow__name=name).delete()

  # Leaking here for some reason
  for doc in list(chain(Document.objects.get_docs(user, Workflow).filter(name=name, extra=''),
                        Document.objects.filter(name='mapreduce1', owner__username='jobsub_test').all(),
                        Document.objects.filter(name='sleep_job-copy', owner__username='jobsub_test').all())):
    if doc.content_object:
      client.post(reverse('oozie:delete_workflow') + '?skip_trash=true', {'job_selection': [doc.content_object.id]}, follow=True)
    else:
      doc.delete()

  workflow_count = Document.objects.available_docs(Workflow, user).count()
  response = client.get(reverse('oozie:create_workflow'))
  assert_equal(workflow_count, Document.objects.available_docs(Workflow, user).count(), response)

  response = client.post(reverse('oozie:create_workflow'), workflow_dict, follow=True)
  assert_equal(200, response.status_code)

  assert_equal(workflow_count + 1, Document.objects.available_docs(Workflow, user).count())

  wf = Document.objects.get_docs(user, Workflow).get(name=name, extra='').content_object
  assert_not_equal('', wf.deployment_dir)
  assert_true(wf.managed)

  return wf


def create_coordinator(workflow, client, user):
  name = str(COORDINATOR_DICT['name'][0])

  if Document.objects.get_docs(user, Coordinator).filter(name=name).exists():
    for doc in Document.objects.get_docs(user, Coordinator).filter(name=name):
      if doc.content_object:
        client.post(reverse('oozie:delete_coordinator') + '?skip_trash=true', {'job_selection': [doc.content_object.id]}, follow=True)
      else:
        doc.delete()

  coord_count = Document.objects.available_docs(Coordinator, user).count()
  response = client.get(reverse('oozie:create_coordinator'))
  assert_equal(coord_count, Document.objects.available_docs(Coordinator, user).count(), response)

  post = COORDINATOR_DICT.copy()
  post['coordinatorworkflow'] = workflow.id
  response = client.post(reverse('oozie:create_coordinator'), post)
  assert_equal(coord_count + 1, Document.objects.available_docs(Coordinator, user).count(), response)

  return Document.objects.available_docs(Coordinator, user).get(name=name).content_object


def create_bundle(client, user):
  name = str(BUNDLE_DICT['name'][0])

  if Document.objects.get_docs(user, Bundle).filter(name=name).exists():
    for doc in Document.objects.get_docs(user, Bundle).filter(name=name):
      if doc.content_object:
        client.post(reverse('oozie:delete_bundle') + '?skip_trash=true', {'job_selection': [doc.content_object.id]}, follow=True)
      else:
        doc.delete()

  bundle_count = Document.objects.available_docs(Bundle, user).count()
  response = client.get(reverse('oozie:create_bundle'))
  assert_equal(bundle_count, Document.objects.available_docs(Bundle, user).count(), response)

  post = BUNDLE_DICT.copy()
  response = client.post(reverse('oozie:create_bundle'), post)
  assert_equal(bundle_count + 1, Document.objects.available_docs(Bundle, user).count(), response)

  return Document.objects.available_docs(Bundle, user).get(name=name).content_object


def create_dataset(coord, client):
  response = client.post(reverse('oozie:create_coordinator_dataset', args=[coord.id]), {
                        u'create-name': [u'MyDataset'], u'create-frequency_number': [u'1'], u'create-frequency_unit': [u'days'],
                        u'create-uri': [u'/data/${YEAR}${MONTH}${DAY}'],
                        u'create-instance_choice': [u'range'],
                        u'create-advanced_start_instance': [u'-1'],
                        u'create-advanced_end_instance': [u'${coord:current(1)}'],
                        u'create-start_0': [u'07/01/2012'], u'create-start_1': [u'12:00 AM'],
                        u'create-timezone': [u'America/Los_Angeles'], u'create-done_flag': [u''],
                        u'create-description': [u'']})
  data = json.loads(response.content)
  assert_equal(0, data['status'], data['data'])


def create_coordinator_data(coord, client):
  dataset = Dataset.objects.get(coordinator=coord)
  response = client.post(reverse('oozie:create_coordinator_data', args=[coord.id, 'input']),
                         {u'input-name': [u'input_dir'], u'input-dataset': [dataset.id]})
  data = json.loads(response.content)
  assert_equal(0, data['status'], data['data'])


def synchronize_workflow_attributes(workflow_json, correct_workflow_json):
  if isinstance(workflow_json, basestring):
    workflow_dict = json.loads(workflow_json)
  else:
    workflow_dict = workflow_json

  if isinstance(correct_workflow_json, basestring):
    correct_workflow_dict = json.loads(correct_workflow_json)
  else:
    correct_workflow_dict = correct_workflow_json

  if 'attributes' in workflow_dict and 'attributes' in correct_workflow_dict:
    workflow_dict['attributes']['deployment_dir'] = correct_workflow_dict['attributes']['deployment_dir']

  return reformat_json(workflow_dict)

def save_temp_workflow(wf, user):
    data = json.dumps({
          'layout': [{
              "size":12, "rows":[
                  {"widgets":[{"size":12, "name":"Start", "id":"3f107997-04cc-8733-60a9-a4bb62cebffc", "widgetType":"start-widget", "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span12"}]},
                  {"widgets":[{"size":12, "name":"Shell", "id":"3f107997-04cc-8733-60a9-a4bb62cebabc", "widgetType":"shell-widget", "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span12"}]},
                  {"widgets":[{"size":12, "name":"End", "id":"33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "widgetType":"end-widget", "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span12"}]},
                  {"widgets":[{"size":12, "name":"Kill", "id":"17c9c895-5a16-7443-bb81-f34b30b21548", "widgetType":"kill-widget", "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span12"}]}
              ],
              "drops":[ "temp"],
              "klass":"card card-home card-column span12"
          }],
          'workflow': {
              "id": None,
              "uuid": None,
              "name": "My Workflow",
              "properties": {
                  "deployment_dir": "",
                  "description": "",
                  "job_xml": "",
                  "sla_enabled": False,
                  "schema_version": "uri:oozie:workflow:0.5",
                  "properties": [],
                  "parameters": [{'name':'Dryrun', 'value': False}, {'name':'ls_arg', 'value': '-l'}],
                  "sla":  [
      {'key': 'enabled', 'value': False}, # Always first element
      {'key': 'nominal-time', 'value': '${nominal_time}'},
      {'key': 'should-start', 'value': ''},
      {'key': 'should-end', 'value': '${30 * MINUTES}'},
      {'key': 'max-duration', 'value': ''},
      {'key': 'alert-events', 'value': ''},
      {'key': 'alert-contact', 'value': ''},
      {'key': 'notification-msg', 'value': ''},
      {'key': 'upstream-apps', 'value': ''},
  ],
                  "show_arrows": True,
                  "wf1_id": None
              },
              "nodes":[
                  {"id":"3f107997-04cc-8733-60a9-a4bb62cebffc","name":"Start","type":"start-widget","properties":{},"children":[{'to': '3f107997-04cc-8733-60a9-a4bb62cebabc'}]},
                  {"id":"3f107997-04cc-8733-60a9-a4bb62cebabc","name":"shell-fc94","type":"shell-widget","properties":{'archives': [], 'arguments': [], 'capture_output': True, 'credentials': [], 'env_var': [], 'files': [], 'job_properties': [], 'job_xml': u'', 'prepares': [], 'retry_interval': [], 'retry_max': [], 'shell_command': 'ls', 'sla': []},"children":[{'to': '33430f0f-ebfa-c3ec-f237-3e77efa03d0a'}]},
                  {"id":"33430f0f-ebfa-c3ec-f237-3e77efa03d0a","name":"End","type":"end-widget","properties":{},"children":[]},
                  {"id":"17c9c895-5a16-7443-bb81-f34b30b21548","name":"Kill","type":"kill-widget","properties":{'message': 'Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]'},"children":[]}
              ]
          }
      })
    workflow_doc = Document2.objects.create(name='test', type='oozie-workflow2', owner=user, data=data)
    Document.objects.link(workflow_doc, owner=workflow_doc.owner, name=workflow_doc.name, description=workflow_doc.description, extra='workflow2')

    wf[u'conf'] = u'<configuration><property><name>hue-id-w</name><value>' + str(workflow_doc.id) + u'</value></property></configuration>'
    return workflow_doc
