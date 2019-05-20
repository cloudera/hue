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

from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q

from nose.plugins.attrib import attr
from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal, assert_raises

from desktop.conf import USE_DEFAULT_CONFIGURATION, USE_NEW_EDITOR
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_permission, add_to_group, grant_access, remove_from_group
from desktop.models import DefaultConfiguration, Document, Document2
from notebook.models import make_notebook, make_notebook2
from notebook.api import _save_notebook

from oozie.conf import ENABLE_V2
from oozie.importlib.workflows import generate_v2_graph_nodes
from oozie.models2 import Node, Workflow, WorkflowConfiguration, find_dollar_variables, find_dollar_braced_variables, \
    _create_graph_adjaceny_list, _get_hierarchy_from_adj_list, WorkflowBuilder, WorkflowDepthReached
from oozie.tests import OozieMockBase, save_temp_workflow, MockOozieApi


LOG = logging.getLogger(__name__)


class TestEditor(OozieMockBase):

  def setUp(self):
    super(TestEditor, self).setUp()
    self.wf = Workflow()

    self.client_not_me = make_logged_in_client(username="not_perm_user", groupname="default", recreate=True,
                                               is_superuser=False)
    self.user_not_me = User.objects.get(username="not_perm_user")


  @attr('integration')
  def test_create_new_workflow(self):
    response = self.c.get(reverse('oozie:new_workflow'))
    assert_equal(200, response.status_code)


  def test_create_new_coordinator(self):
    response = self.c.get(reverse('oozie:new_coordinator'))
    assert_equal(200, response.status_code)


  def test_create_new_bundle(self):
    response = self.c.get(reverse('oozie:new_bundle'))
    assert_equal(200, response.status_code)


  def test_parsing(self):
    assert_equal(['input', 'LIMIT', 'out'], find_dollar_variables("""
data = '$input';
$out = LIMIT data $LIMIT; -- ${nah}
$output = STORE "$out";
    """))

    assert_equal(['max_salary', 'limit'], find_dollar_variables("""
SELECT sample_07.description, sample_07.salary
FROM
  sample_07
WHERE
( sample_07.salary > $max_salary)
ORDER BY sample_07.salary DESC
LIMIT $limit"""))


  def test_hive_script_parsing(self):
    assert_equal(['field', 'tablename', 'LIMIT'], find_dollar_braced_variables("""
    SELECT ${field}
    FROM ${hivevar:tablename}
    LIMIT ${hiveconf:LIMIT}
    """))

    assert_equal(['field', 'tablename', 'LIMIT'], find_dollar_braced_variables("SELECT ${field} FROM ${hivevar:tablename} LIMIT ${hiveconf:LIMIT}"))


  def test_workflow_gen_xml(self):
    assert_equal([
        u'<workflow-app', u'name="My', u'Workflow"', u'xmlns="uri:oozie:workflow:0.5">', u'<start', u'to="End"/>', u'<kill', u'name="Kill">', u'<message>Action', u'failed,',
        u'error', u'message[${wf:errorMessage(wf:lastErrorNode())}]</message>', u'</kill>', u'<end', u'name="End"/>', u'</workflow-app>'],
        self.wf.to_xml({'output': '/path'}).split()
    )

  def test_workflow_map_reduce_gen_xml(self):
    wf = Workflow(data="{\"layout\": [{\"oozieRows\": [{\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"MapReduce job\", \"widgetType\": \"mapreduce-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\", \"size\": 12}], \"id\": \"e2caca14-8afc-d7e0-287c-88accd0b4253\", \"columns\": []}], \"rows\": [{\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Start\", \"widgetType\": \"start-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"size\": 12}], \"id\": \"ff63ee3f-df54-2fa3-477b-65f5e0f0632c\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"MapReduce job\", \"widgetType\": \"mapreduce-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\", \"size\": 12}], \"id\": \"e2caca14-8afc-d7e0-287c-88accd0b4253\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"End\", \"widgetType\": \"end-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"size\": 12}], \"id\": \"6a13d869-d04c-8431-6c5c-dbe67ea33889\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Kill\", \"widgetType\": \"kill-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"size\": 12}], \"id\": \"e3b56553-7a4f-43d2-b1e2-4dc433280095\", \"columns\": []}], \"oozieEndRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"End\", \"widgetType\": \"end-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"size\": 12}], \"id\": \"6a13d869-d04c-8431-6c5c-dbe67ea33889\", \"columns\": []}, \"oozieKillRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Kill\", \"widgetType\": \"kill-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"size\": 12}], \"id\": \"e3b56553-7a4f-43d2-b1e2-4dc433280095\", \"columns\": []}, \"enableOozieDropOnAfter\": true, \"oozieStartRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Start\", \"widgetType\": \"start-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"size\": 12}], \"id\": \"ff63ee3f-df54-2fa3-477b-65f5e0f0632c\", \"columns\": []}, \"klass\": \"card card-home card-column span12\", \"enableOozieDropOnBefore\": true, \"drops\": [\"temp\"], \"id\": \"0c1908e7-0096-46e7-a16b-b17b1142a730\", \"size\": 12}], \"workflow\": {\"properties\": {\"job_xml\": \"\", \"description\": \"\", \"wf1_id\": null, \"sla_enabled\": false, \"deployment_dir\": \"/user/hue/oozie/workspaces/hue-oozie-1430228904.58\", \"schema_version\": \"uri:oozie:workflow:0.5\", \"sla\": [{\"key\": \"enabled\", \"value\": false}, {\"key\": \"nominal-time\", \"value\": \"${nominal_time}\"}, {\"key\": \"should-start\", \"value\": \"\"}, {\"key\": \"should-end\", \"value\": \"${30 * MINUTES}\"}, {\"key\": \"max-duration\", \"value\": \"\"}, {\"key\": \"alert-events\", \"value\": \"\"}, {\"key\": \"alert-contact\", \"value\": \"\"}, {\"key\": \"notification-msg\", \"value\": \"\"}, {\"key\": \"upstream-apps\", \"value\": \"\"}], \"show_arrows\": true, \"parameters\": [{\"name\": \"oozie.use.system.libpath\", \"value\": true}], \"properties\": []}, \"name\": \"My Workflow\", \"versions\": [\"uri:oozie:workflow:0.4\", \"uri:oozie:workflow:0.4.5\", \"uri:oozie:workflow:0.5\"], \"isDirty\": true, \"movedNode\": null, \"linkMapping\": {\"0cf2d5d5-2315-0bda-bd53-0eec257e943f\": [\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\"], \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\": [], \"3f107997-04cc-8733-60a9-a4bb62cebffc\": [\"0cf2d5d5-2315-0bda-bd53-0eec257e943f\"], \"17c9c895-5a16-7443-bb81-f34b30b21548\": []}, \"nodeIds\": [\"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\"], \"nodes\": [{\"properties\": {}, \"name\": \"Start\", \"children\": [{\"to\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\"}], \"actionParametersFetched\": false, \"type\": \"start-widget\", \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"actionParameters\": []}, {\"properties\": {}, \"name\": \"End\", \"children\": [], \"actionParametersFetched\": false, \"type\": \"end-widget\", \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"actionParameters\": []}, {\"properties\": {\"message\": \"Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]\"}, \"name\": \"Kill\", \"children\": [], \"actionParametersFetched\": false, \"type\": \"kill-widget\", \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"actionParameters\": []}, {\"properties\": {\"retry_max\": [{\"value\": \"5\"}], \"files\": [], \"job_xml\": \"\", \"jar_path\": \"my_jar\", \"job_properties\": [{\"name\": \"prop_1_name\", \"value\": \"prop_1_value\"}], \"archives\": [], \"prepares\": [], \"credentials\": [], \"sla\": [{\"key\": \"enabled\", \"value\": false}, {\"key\": \"nominal-time\", \"value\": \"${nominal_time}\"}, {\"key\": \"should-start\", \"value\": \"\"}, {\"key\": \"should-end\", \"value\": \"${30 * MINUTES}\"}, {\"key\": \"max-duration\", \"value\": \"\"}, {\"key\": \"alert-events\", \"value\": \"\"}, {\"key\": \"alert-contact\", \"value\": \"\"}, {\"key\": \"notification-msg\", \"value\": \"\"}, {\"key\": \"upstream-apps\", \"value\": \"\"}]}, \"name\": \"mapreduce-0cf2\", \"children\": [{\"to\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\"}, {\"error\": \"17c9c895-5a16-7443-bb81-f34b30b21548\"}], \"actionParametersFetched\": false, \"type\": \"mapreduce-widget\", \"id\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\", \"actionParameters\": []}], \"id\": 50019, \"nodeNamesMapping\": {\"0cf2d5d5-2315-0bda-bd53-0eec257e943f\": \"mapreduce-0cf2\", \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\": \"End\", \"3f107997-04cc-8733-60a9-a4bb62cebffc\": \"Start\", \"17c9c895-5a16-7443-bb81-f34b30b21548\": \"Kill\"}, \"uuid\": \"084f4d4c-00f1-62d2-e27e-e153c1f9acfb\"}}")

    assert_equal([
        u'<workflow-app', u'name="My', u'Workflow"', u'xmlns="uri:oozie:workflow:0.5">',
        u'<start', u'to="mapreduce-0cf2"/>',
        u'<kill', u'name="Kill">', u'<message>Action', u'failed,', u'error', u'message[${wf:errorMessage(wf:lastErrorNode())}]</message>', u'</kill>',
        u'<action', u'name="mapreduce-0cf2"', 'retry-max="5">',
        u'<map-reduce>',
        u'<job-tracker>${jobTracker}</job-tracker>',
        u'<name-node>${nameNode}</name-node>',
        u'<configuration>',
        u'<property>',
        u'<name>prop_1_name</name>',
        u'<value>prop_1_value</value>',
        u'</property>',
        u'</configuration>',
        u'</map-reduce>',
        u'<ok', u'to="End"/>',
        u'<error', u'to="Kill"/>',
        u'</action>',
        u'<end', u'name="End"/>',
        u'</workflow-app>'
        ],
        wf.to_xml({'output': '/path'}).split()
    )

  def test_workflow_java_gen_xml(self):
    wf = Workflow(data="{\"layout\": [{\"oozieRows\": [{\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Java program\", \"widgetType\": \"java-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": true, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"6ddafdc4-c070-95f0-4211-328e9f31daf6\", \"size\": 12}], \"id\": \"badb3c81-78d6-8099-38fc-87a9904ba78c\", \"columns\": []}], \"rows\": [{\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Start\", \"widgetType\": \"start-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"size\": 12}], \"id\": \"adc3fe69-36eb-20f8-09ac-38fada1582b2\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Java program\", \"widgetType\": \"java-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": true, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"6ddafdc4-c070-95f0-4211-328e9f31daf6\", \"size\": 12}], \"id\": \"badb3c81-78d6-8099-38fc-87a9904ba78c\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"End\", \"widgetType\": \"end-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"size\": 12}], \"id\": \"107bdacf-a37a-d69e-98dd-5801407cb57e\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Kill\", \"widgetType\": \"kill-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"size\": 12}], \"id\": \"81e1869c-a2c3-66d2-c703-719335ea45cb\", \"columns\": []}], \"oozieEndRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"End\", \"widgetType\": \"end-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"size\": 12}], \"id\": \"107bdacf-a37a-d69e-98dd-5801407cb57e\", \"columns\": []}, \"oozieKillRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Kill\", \"widgetType\": \"kill-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"size\": 12}], \"id\": \"81e1869c-a2c3-66d2-c703-719335ea45cb\", \"columns\": []}, \"enableOozieDropOnAfter\": true, \"oozieStartRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Start\", \"widgetType\": \"start-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"size\": 12}], \"id\": \"adc3fe69-36eb-20f8-09ac-38fada1582b2\", \"columns\": []}, \"klass\": \"card card-home card-column span12\", \"enableOozieDropOnBefore\": true, \"drops\": [\"temp\"], \"id\": \"8e0f37a5-2dfb-7329-be44-78e60b2cf62b\", \"size\": 12}], \"workflow\": {\"properties\": {\"job_xml\": \"\", \"description\": \"\", \"wf1_id\": null, \"sla_enabled\": false, \"deployment_dir\": \"/user/hue/oozie/workspaces/hue-oozie-1449080135.8\", \"schema_version\": \"uri:oozie:workflow:0.5\", \"properties\": [], \"show_arrows\": true, \"parameters\": [{\"name\": \"oozie.use.system.libpath\", \"value\": true}], \"sla\": [{\"value\": false, \"key\": \"enabled\"}, {\"value\": \"${nominal_time}\", \"key\": \"nominal-time\"}, {\"value\": \"\", \"key\": \"should-start\"}, {\"value\": \"${30 * MINUTES}\", \"key\": \"should-end\"}, {\"value\": \"\", \"key\": \"max-duration\"}, {\"value\": \"\", \"key\": \"alert-events\"}, {\"value\": \"\", \"key\": \"alert-contact\"}, {\"value\": \"\", \"key\": \"notification-msg\"}, {\"value\": \"\", \"key\": \"upstream-apps\"}]}, \"name\": \"My Workflow\", \"versions\": [\"uri:oozie:workflow:0.4\", \"uri:oozie:workflow:0.4.5\", \"uri:oozie:workflow:0.5\"], \"isDirty\": false, \"movedNode\": null, \"linkMapping\": {\"6ddafdc4-c070-95f0-4211-328e9f31daf6\": [\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\"], \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\": [], \"3f107997-04cc-8733-60a9-a4bb62cebffc\": [\"6ddafdc4-c070-95f0-4211-328e9f31daf6\"], \"17c9c895-5a16-7443-bb81-f34b30b21548\": []}, \"nodeIds\": [\"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"6ddafdc4-c070-95f0-4211-328e9f31daf6\"], \"nodes\": [{\"properties\": {}, \"name\": \"Start\", \"children\": [{\"to\": \"6ddafdc4-c070-95f0-4211-328e9f31daf6\"}], \"actionParametersFetched\": false, \"type\": \"start-widget\", \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"actionParameters\": []}, {\"properties\": {}, \"name\": \"End\", \"children\": [], \"actionParametersFetched\": false, \"type\": \"end-widget\", \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"actionParameters\": []}, {\"properties\": {\"body\": \"\", \"cc\": \"\", \"to\": \"\", \"enableMail\": false, \"message\": \"Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]\", \"subject\": \"\"}, \"name\": \"Kill\", \"children\": [], \"actionParametersFetched\": false, \"type\": \"kill-widget\", \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"actionParameters\": []}, {\"properties\": {\"files\": [{\"value\": \"/my_file\"}], \"job_xml\": [], \"jar_path\": \"/my/jar\", \"java_opts\": [{\"value\": \"-Dsun.security.jgss.debug=true\"}], \"retry_max\": [], \"retry_interval\": [], \"job_properties\": [], \"capture_output\": false, \"main_class\": \"MyClass\", \"arguments\": [{\"value\": \"my_arg\"}], \"prepares\": [], \"credentials\": [], \"sla\": [{\"value\": false, \"key\": \"enabled\"}, {\"value\": \"${nominal_time}\", \"key\": \"nominal-time\"}, {\"value\": \"\", \"key\": \"should-start\"}, {\"value\": \"${30 * MINUTES}\", \"key\": \"should-end\"}, {\"value\": \"\", \"key\": \"max-duration\"}, {\"value\": \"\", \"key\": \"alert-events\"}, {\"value\": \"\", \"key\": \"alert-contact\"}, {\"value\": \"\", \"key\": \"notification-msg\"}, {\"value\": \"\", \"key\": \"upstream-apps\"}], \"archives\": []}, \"name\": \"java-6dda\", \"children\": [{\"to\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\"}, {\"error\": \"17c9c895-5a16-7443-bb81-f34b30b21548\"}], \"actionParametersFetched\": false, \"type\": \"java-widget\", \"id\": \"6ddafdc4-c070-95f0-4211-328e9f31daf6\", \"actionParameters\": []}], \"id\": 50247, \"nodeNamesMapping\": {\"6ddafdc4-c070-95f0-4211-328e9f31daf6\": \"java-6dda\", \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\": \"End\", \"3f107997-04cc-8733-60a9-a4bb62cebffc\": \"Start\", \"17c9c895-5a16-7443-bb81-f34b30b21548\": \"Kill\"}, \"uuid\": \"2667d60e-d894-c27b-6e6f-0333704c0989\"}}")

    assert_equal([
        u'<workflow-app', u'name="My', u'Workflow"', u'xmlns="uri:oozie:workflow:0.5">',
        u'<start', u'to="java-6dda"/>',
        u'<kill', u'name="Kill">',
        u'<message>Action', u'failed,',
        u'error', u'message[${wf:errorMessage(wf:lastErrorNode())}]</message>',
        u'</kill>',
        u'<action', u'name="java-6dda">',
        u'<java>',
        u'<job-tracker>${jobTracker}</job-tracker>',
        u'<name-node>${nameNode}</name-node>',
        u'<main-class>MyClass</main-class>',
        u'<java-opts>-Dsun.security.jgss.debug=true</java-opts>',
        u'<arg>my_arg</arg>',
        u'<file>/my_file#my_file</file>',
        u'</java>',
        u'<ok', u'to="End"/>',
        u'<error', u'to="Kill"/>',
        u'</action>',
        u'<end', u'name="End"/>',
        u'</workflow-app>'
        ],
        wf.to_xml({'output': '/path'}).split()
    )

  def test_workflow_generic_gen_xml(self):
    workflow = """{"layout": [{"oozieRows": [{"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Generic", "widgetType": "generic-widget", "oozieMovable": true, "ooziePropertiesExpanded": true, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "e96bb09b-84d1-6864-5782-42942bab97cb", "size": 12}], "id": "ed10631a-f264-9a3b-aa09-b04cb76f5c32", "columns": []}], "rows": [{"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Start", "widgetType": "start-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "size": 12}], "id": "68d83128-2c08-28f6-e9d1-a912d20f8af5", "columns": []}, {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Generic", "widgetType": "generic-widget", "oozieMovable": true, "ooziePropertiesExpanded": true, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "e96bb09b-84d1-6864-5782-42942bab97cb", "size": 12}], "id": "ed10631a-f264-9a3b-aa09-b04cb76f5c32", "columns": []}, {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "End", "widgetType": "end-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "size": 12}], "id": "7bf3cdc7-f79b-ff36-b152-e37217c40ccb", "columns": []}, {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Kill", "widgetType": "kill-widget", "oozieMovable": true, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "size": 12}], "id": "07c4f1bd-8f58-ea51-fc3d-50acf74d6747", "columns": []}], "oozieEndRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "End", "widgetType": "end-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "size": 12}], "id": "7bf3cdc7-f79b-ff36-b152-e37217c40ccb", "columns": []}, "oozieKillRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Kill", "widgetType": "kill-widget", "oozieMovable": true, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "size": 12}], "id": "07c4f1bd-8f58-ea51-fc3d-50acf74d6747", "columns": []}, "enableOozieDropOnAfter": true, "oozieStartRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Start", "widgetType": "start-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "size": 12}], "id": "68d83128-2c08-28f6-e9d1-a912d20f8af5", "columns": []}, "klass": "card card-home card-column span12", "enableOozieDropOnBefore": true, "drops": ["temp"], "id": "0e8b5e24-4f78-0f76-fe91-0c8e7f0d290a", "size": 12}], "workflow": {"properties": {"job_xml": "", "description": "", "wf1_id": null, "sla_enabled": false, "deployment_dir": "/user/hue/oozie/workspaces/hue-oozie-1446487280.19", "schema_version": "uri:oozie:workflow:0.5", "properties": [], "show_arrows": true, "parameters": [{"name": "oozie.use.system.libpath", "value": true}], "sla": [{"value": false, "key": "enabled"}, {"value": "${nominal_time}", "key": "nominal-time"}, {"value": "", "key": "should-start"}, {"value": "${30 * MINUTES}", "key": "should-end"}, {"value": "", "key": "max-duration"}, {"value": "", "key": "alert-events"}, {"value": "", "key": "alert-contact"}, {"value": "", "key": "notification-msg"}, {"value": "", "key": "upstream-apps"}]}, "name": "My Workflow 3", "versions": ["uri:oozie:workflow:0.4", "uri:oozie:workflow:0.4.5", "uri:oozie:workflow:0.5"], "isDirty": false, "movedNode": null, "linkMapping": {"17c9c895-5a16-7443-bb81-f34b30b21548": [], "33430f0f-ebfa-c3ec-f237-3e77efa03d0a": [], "3f107997-04cc-8733-60a9-a4bb62cebffc": ["e96bb09b-84d1-6864-5782-42942bab97cb"], "e96bb09b-84d1-6864-5782-42942bab97cb": ["33430f0f-ebfa-c3ec-f237-3e77efa03d0a"]}, "nodeIds": ["3f107997-04cc-8733-60a9-a4bb62cebffc", "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "17c9c895-5a16-7443-bb81-f34b30b21548", "e96bb09b-84d1-6864-5782-42942bab97cb"], "nodes": [{"properties": {}, "name": "Start", "children": [{"to": "e96bb09b-84d1-6864-5782-42942bab97cb"}], "actionParametersFetched": false, "type": "start-widget", "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "actionParameters": []}, {"properties": {}, "name": "End", "children": [], "actionParametersFetched": false, "type": "end-widget", "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "actionParameters": []}, {"properties": {"message": "Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]"}, "name": "Kill", "children": [], "actionParametersFetched": false, "type": "kill-widget", "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "actionParameters": []}, {"properties": {"xml": "<my_action xmlns=\\"uri:oozie:my_action-action:0.1\\">\\n</my_action>", "credentials": [], "retry_max": [], "sla": [{"key": "enabled", "value": false}, {"key": "nominal-time", "value": "${nominal_time}"}, {"key": "should-start", "value": ""}, {"key": "should-end", "value": "${30 * MINUTES}"}, {"key": "max-duration", "value": ""}, {"key": "alert-events", "value": ""}, {"key": "alert-contact", "value": ""}, {"key": "notification-msg", "value": ""}, {"key": "upstream-apps", "value": ""}], "retry_interval": []}, "name": "generic-e96b", "children": [{"to": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a"}, {"error": "17c9c895-5a16-7443-bb81-f34b30b21548"}], "actionParametersFetched": false, "type": "generic-widget", "id": "e96bb09b-84d1-6864-5782-42942bab97cb", "actionParameters": []}], "id": 50027, "nodeNamesMapping": {"17c9c895-5a16-7443-bb81-f34b30b21548": "Kill", "33430f0f-ebfa-c3ec-f237-3e77efa03d0a": "End", "3f107997-04cc-8733-60a9-a4bb62cebffc": "Start", "e96bb09b-84d1-6864-5782-42942bab97cb": "generic-e96b"}, "uuid": "83fb9dc4-8687-e369-9220-c8501a93d446"}}"""
    wf = Workflow(data=workflow)
    assert_equal([
        u'<workflow-app', u'name="My', u'Workflow', u'3"', u'xmlns="uri:oozie:workflow:0.5">',
        u'<start', u'to="generic-e96b"/>',
        u'<kill', u'name="Kill">', u'<message>Action', u'failed,', u'error', u'message[${wf:errorMessage(wf:lastErrorNode())}]</message>', u'</kill>',
          u'<action', u'name="generic-e96b">', u'<my_action', u'xmlns="uri:oozie:my_action-action:0.1">', u'</my_action>',
          u'<ok', u'to="End"/>', u'<error', u'to="Kill"/>',
        u'</action>',
        u'<end', u'name="End"/>',
        u'</workflow-app>'],
       wf.to_xml({'output': '/path'}).split()
    )

  def test_workflow_email_on_kill_node_xml(self):
    workflow = """{"history": {"oozie_id": "0000013-151015155856463-oozie-oozi-W", "properties": {"oozie.use.system.libpath": "True", "security_enabled": false, "dryrun": false, "jobTracker": "localhost:8032", "oozie.wf.application.path": "hdfs://localhost:8020/user/hue/oozie/workspaces/hue-oozie-1445431078.26", "hue-id-w": 6, "nameNode": "hdfs://localhost:8020"}}, "layout": [{"oozieRows": [], "rows": [{"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Start", "widgetType": "start-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "size": 12}], "id": "9cf57679-292c-d980-8053-1180a84eaa54", "columns": []}, {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "End", "widgetType": "end-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "size": 12}], "id": "f8f22c81-a9eb-5138-64cf-014ae588d0ca", "columns": []}, {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Kill", "widgetType": "kill-widget", "oozieMovable": true, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "size": 12}], "id": "31f194ff-cd4f-faef-652d-0c5f66a80f97", "columns": []}], "oozieEndRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "End", "widgetType": "end-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "size": 12}], "id": "f8f22c81-a9eb-5138-64cf-014ae588d0ca", "columns": []}, "oozieKillRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Kill", "widgetType": "kill-widget", "oozieMovable": true, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "size": 12}], "id": "31f194ff-cd4f-faef-652d-0c5f66a80f97", "columns": []}, "enableOozieDropOnAfter": true, "oozieStartRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Start", "widgetType": "start-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "size": 12}], "id": "9cf57679-292c-d980-8053-1180a84eaa54", "columns": []}, "klass": "card card-home card-column span12", "enableOozieDropOnBefore": true, "drops": ["temp"], "id": "1920900a-a735-7e66-61d4-23de384e8f62", "size": 12}], "workflow": {"properties": {"job_xml": "", "description": "", "wf1_id": null, "sla_enabled": false, "deployment_dir": "/user/hue/oozie/workspaces/hue-oozie-1445431078.26", "schema_version": "uri:oozie:workflow:0.5", "properties": [], "show_arrows": true, "parameters": [{"name": "oozie.use.system.libpath", "value": true}], "sla": [{"value": false, "key": "enabled"}, {"value": "${nominal_time}", "key": "nominal-time"}, {"value": "", "key": "should-start"}, {"value": "${30 * MINUTES}", "key": "should-end"}, {"value": "", "key": "max-duration"}, {"value": "", "key": "alert-events"}, {"value": "", "key": "alert-contact"}, {"value": "", "key": "notification-msg"}, {"value": "", "key": "upstream-apps"}]}, "name": "My real Workflow 1", "versions": ["uri:oozie:workflow:0.4", "uri:oozie:workflow:0.4.5", "uri:oozie:workflow:0.5"], "isDirty": false, "movedNode": null, "linkMapping": {"33430f0f-ebfa-c3ec-f237-3e77efa03d0a": [], "3f107997-04cc-8733-60a9-a4bb62cebffc": ["33430f0f-ebfa-c3ec-f237-3e77efa03d0a"], "17c9c895-5a16-7443-bb81-f34b30b21548": []}, "nodeIds": ["3f107997-04cc-8733-60a9-a4bb62cebffc", "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "17c9c895-5a16-7443-bb81-f34b30b21548"], "nodes": [{"properties": {}, "name": "Start", "children": [{"to": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a"}], "actionParametersFetched": false, "type": "start-widget", "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "actionParameters": []}, {"properties": {}, "name": "End", "children": [], "actionParametersFetched": false, "type": "end-widget", "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "actionParameters": []}, {"properties": {"body": "", "cc": "", "to": "hue@gethue.com", "enableMail": true, "message": "Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]", "subject": "Error on workflow"}, "name": "Kill", "children": [], "actionParametersFetched": false, "type": "kill-widget", "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "actionParameters": []}], "id": 50020, "nodeNamesMapping": {"33430f0f-ebfa-c3ec-f237-3e77efa03d0a": "End", "3f107997-04cc-8733-60a9-a4bb62cebffc": "Start", "17c9c895-5a16-7443-bb81-f34b30b21548": "Kill"}, "uuid": "330c70c8-33fb-16e1-68fb-c42582c7d178"}}"""
    wf = Workflow(data=workflow)
    assert_equal([
        u'<workflow-app', u'name="My', u'real', u'Workflow', u'1"', u'xmlns="uri:oozie:workflow:0.5">',
        u'<start', u'to="End"/>',
        u'<action', u'name="Kill">',
          u'<email', u'xmlns="uri:oozie:email-action:0.2">', u'<to>hue@gethue.com</to>', u'<subject>Error', u'on', u'workflow</subject>', u'<body></body>', u'</email>',
          u'<ok', u'to="Kill-kill"/>', u'<error', u'to="Kill-kill"/>',
        u'</action>',
        u'<kill', u'name="Kill-kill">',
          u'<message>Action', u'failed,', u'error', u'message[${wf:errorMessage(wf:lastErrorNode())}]</message>',
        u'</kill>',
        u'<end', u'name="End"/>',
        u'</workflow-app>'],
       wf.to_xml({'output': '/path'}).split()
    )


  def test_workflow_submission_on_email_notification(self):
    workflow = """{"history": {"oozie_id": "0000013-151015155856463-oozie-oozi-W", "properties": {"oozie.use.system.libpath": "True", "security_enabled": false, "dryrun": false, "jobTracker": "localhost:8032", "oozie.wf.application.path": "hdfs://localhost:8020/user/hue/oozie/workspaces/hue-oozie-1445431078.26", "email_checkbox": "True", "hue-id-w": 6, "nameNode": "hdfs://localhost:8020"}}, "layout": [{"oozieRows": [], "rows": [{"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Start", "widgetType": "start-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "size": 12}], "id": "9cf57679-292c-d980-8053-1180a84eaa54", "columns": []}, {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "End", "widgetType": "end-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "size": 12}], "id": "f8f22c81-a9eb-5138-64cf-014ae588d0ca", "columns": []}, {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Kill", "widgetType": "kill-widget", "oozieMovable": true, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "size": 12}], "id": "31f194ff-cd4f-faef-652d-0c5f66a80f97", "columns": []}], "oozieEndRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "End", "widgetType": "end-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "size": 12}], "id": "f8f22c81-a9eb-5138-64cf-014ae588d0ca", "columns": []}, "oozieKillRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Kill", "widgetType": "kill-widget", "oozieMovable": true, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "size": 12}], "id": "31f194ff-cd4f-faef-652d-0c5f66a80f97", "columns": []}, "enableOozieDropOnAfter": true, "oozieStartRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Start", "widgetType": "start-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "size": 12}], "id": "9cf57679-292c-d980-8053-1180a84eaa54", "columns": []}, "klass": "card card-home card-column span12", "enableOozieDropOnBefore": true, "drops": ["temp"], "id": "1920900a-a735-7e66-61d4-23de384e8f62", "size": 12}], "workflow": {"properties": {"job_xml": "", "description": "", "wf1_id": null, "sla_enabled": false, "deployment_dir": "/user/hue/oozie/workspaces/hue-oozie-1445431078.26", "schema_version": "uri:oozie:workflow:0.5", "properties": [], "show_arrows": true, "parameters": [{"name": "oozie.use.system.libpath", "value": true}], "sla": [{"value": false, "key": "enabled"}, {"value": "${nominal_time}", "key": "nominal-time"}, {"value": "", "key": "should-start"}, {"value": "${30 * MINUTES}", "key": "should-end"}, {"value": "", "key": "max-duration"}, {"value": "", "key": "alert-events"}, {"value": "", "key": "alert-contact"}, {"value": "", "key": "notification-msg"}, {"value": "", "key": "upstream-apps"}]}, "name": "My real Workflow 1", "versions": ["uri:oozie:workflow:0.4", "uri:oozie:workflow:0.4.5", "uri:oozie:workflow:0.5"], "isDirty": false, "movedNode": null, "linkMapping": {"33430f0f-ebfa-c3ec-f237-3e77efa03d0a": [], "3f107997-04cc-8733-60a9-a4bb62cebffc": ["33430f0f-ebfa-c3ec-f237-3e77efa03d0a"], "17c9c895-5a16-7443-bb81-f34b30b21548": []}, "nodeIds": ["3f107997-04cc-8733-60a9-a4bb62cebffc", "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "17c9c895-5a16-7443-bb81-f34b30b21548"], "nodes": [{"properties": {}, "name": "Start", "children": [{"to": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a"}], "actionParametersFetched": false, "type": "start-widget", "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "actionParameters": []}, {"properties": {}, "name": "End", "children": [], "actionParametersFetched": false, "type": "end-widget", "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "actionParameters": []}, {"properties": {"body": "", "cc": "", "to": "hue@gethue.com", "enableMail": true, "message": "Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]", "subject": "Error on workflow"}, "name": "Kill", "children": [], "actionParametersFetched": false, "type": "kill-widget", "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "actionParameters": []}], "id": 50020, "nodeNamesMapping": {"33430f0f-ebfa-c3ec-f237-3e77efa03d0a": "End", "3f107997-04cc-8733-60a9-a4bb62cebffc": "Start", "17c9c895-5a16-7443-bb81-f34b30b21548": "Kill"}, "uuid": "330c70c8-33fb-16e1-68fb-c42582c7d178"}}"""
    wf = Workflow(data=workflow, user=self.user)
    assert_equal([
        u'<workflow-app', u'name="My', u'real', u'Workflow', u'1"', u'xmlns="uri:oozie:workflow:0.5">',
        u'<start', u'to="End"/>',
        u'<action', u'name="Kill">',
          u'<email', u'xmlns="uri:oozie:email-action:0.2">',
            u'<to>hue@gethue.com</to>', u'<subject>Error', u'on', u'workflow</subject>', u'<body></body>',
          u'</email>',
          u'<ok', u'to="Kill-kill"/>',
          u'<error', u'to="Kill-kill"/>',
        u'</action>',
        u'<kill', u'name="Kill-kill">',
          u'<message>Action', u'failed,', u'error', u'message[${wf:errorMessage(wf:lastErrorNode())}]</message>',
        u'</kill>',
        u'<action', u'name="End">',
          u'<email', u'xmlns="uri:oozie:email-action:0.2">',
            u'<to>test@localhost</to>', u'<subject>${wf:name()}', u'execution', u'successful</subject>', u'<body></body>', u'<content_type>text/plain</content_type>',
          u'</email>',
          u'<ok', u'to="End-kill"/>',
          u'<error', u'to="End-kill"/>',
        u'</action>',
        u'<end', u'name="End-kill"/>',
        u'</workflow-app>'],
       wf.to_xml({'output': '/path', 'send_email': 'True'}).split()
    )


  def test_workflow_email_gen_xml(self):
    self.maxDiff = None
    workflow = """{"history": {"oozie_id": "0000013-151015155856463-oozie-oozi-W", "properties": {"oozie.use.system.libpath": "True", "security_enabled": false, "dryrun": false, "jobTracker": "localhost:8032", "oozie.wf.application.path": "hdfs://localhost:8020/user/hue/oozie/workspaces/hue-oozie-1445431078.26", "hue-id-w": 6, "nameNode": "hdfs://localhost:8020"}}, "layout": [{"oozieRows": [], "rows": [{"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Start", "widgetType": "start-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "size": 12}], "id": "9cf57679-292c-d980-8053-1180a84eaa54", "columns": []}, {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "End", "widgetType": "end-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "size": 12}], "id": "f8f22c81-a9eb-5138-64cf-014ae588d0ca", "columns": []}, {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Kill", "widgetType": "kill-widget", "oozieMovable": true, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "size": 12}], "id": "31f194ff-cd4f-faef-652d-0c5f66a80f97", "columns": []}], "oozieEndRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "End", "widgetType": "end-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "size": 12}], "id": "f8f22c81-a9eb-5138-64cf-014ae588d0ca", "columns": []}, "oozieKillRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Kill", "widgetType": "kill-widget", "oozieMovable": true, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "size": 12}], "id": "31f194ff-cd4f-faef-652d-0c5f66a80f97", "columns": []}, "enableOozieDropOnAfter": true, "oozieStartRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Start", "widgetType": "start-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "size": 12}], "id": "9cf57679-292c-d980-8053-1180a84eaa54", "columns": []}, "klass": "card card-home card-column span12", "enableOozieDropOnBefore": true, "drops": ["temp"], "id": "1920900a-a735-7e66-61d4-23de384e8f62", "size": 12}], "workflow": {"properties": {"job_xml": "", "description": "", "wf1_id": null, "sla_enabled": false, "deployment_dir": "/user/hue/oozie/workspaces/hue-oozie-1445431078.26", "schema_version": "uri:oozie:workflow:0.5", "properties": [], "show_arrows": true, "parameters": [{"name": "oozie.use.system.libpath", "value": true}], "sla": [{"value": false, "key": "enabled"}, {"value": "${nominal_time}", "key": "nominal-time"}, {"value": "", "key": "should-start"}, {"value": "${30 * MINUTES}", "key": "should-end"}, {"value": "", "key": "max-duration"}, {"value": "", "key": "alert-events"}, {"value": "", "key": "alert-contact"}, {"value": "", "key": "notification-msg"}, {"value": "", "key": "upstream-apps"}]}, "name": "My real Workflow 1", "versions": ["uri:oozie:workflow:0.4", "uri:oozie:workflow:0.4.5", "uri:oozie:workflow:0.5"], "isDirty": false, "movedNode": null, "linkMapping": {"33430f0f-ebfa-c3ec-f237-3e77efa03d0a": [], "3f107997-04cc-8733-60a9-a4bb62cebffc": ["33430f0f-ebfa-c3ec-f237-3e77efa03d0a"], "17c9c895-5a16-7443-bb81-f34b30b21548": []}, "nodeIds": ["3f107997-04cc-8733-60a9-a4bb62cebffc", "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "17c9c895-5a16-7443-bb81-f34b30b21548"], "nodes": [{"properties": {}, "name": "Start", "children": [{"to": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a"}], "actionParametersFetched": false, "type": "start-widget", "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "actionParameters": []}, {"properties": {}, "name": "End", "children": [], "actionParametersFetched": false, "type": "end-widget", "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "actionParameters": []}, {"properties": {"body": "This\\n\\ncontains\\n\\n\\nnew lines.", "bcc": "example@bcc.com", "content_type": "text/plain", "cc": "", "to": "hue@gethue.com", "enableMail": true, "message": "Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]", "subject": "Error on workflow"}, "name": "Kill", "children": [], "actionParametersFetched": false, "type": "kill-widget", "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "actionParameters": []}], "id": 50020, "nodeNamesMapping": {"33430f0f-ebfa-c3ec-f237-3e77efa03d0a": "End", "3f107997-04cc-8733-60a9-a4bb62cebffc": "Start", "17c9c895-5a16-7443-bb81-f34b30b21548": "Kill"}, "uuid": "330c70c8-33fb-16e1-68fb-c42582c7d178"}}"""
    wf = Workflow(data=workflow)
    assert_equal(u'<workflow-app name="My real Workflow 1" xmlns="uri:oozie:workflow:0.5">\n    <start to="End"/>\n    <action name="Kill">\n        <email xmlns="uri:oozie:email-action:0.2">\n            <to>hue@gethue.com</to>\n            <subject>Error on workflow</subject>\n            <body>This\n\ncontains\n\n\nnew lines.</body>\n        </email>\n        <ok to="Kill-kill"/>\n        <error to="Kill-kill"/>\n    </action>\n    <kill name="Kill-kill">\n        <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>\n    </kill>\n    <end name="End"/>\n</workflow-app>', wf.to_xml({'output': '/path'}))

  def test_job_validate_xml_name(self):
    job = Workflow()

    job.update_name('a')
    assert_equal('a', job.validated_name)

    job.update_name('aa')
    assert_equal('aa', job.validated_name)

    job.update_name('%a')
    assert_equal('%a', job.validated_name)

    job.update_name(u'你好')
    assert_equal(u'你好', job.validated_name)

    job.update_name('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaz')
    assert_equal(len('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), len(job.validated_name))

    job.update_name('My <...> 1st W$rkflow [With] (Bad) letter$')
    assert_equal('My &lt;...&gt; 1st W$rkflow [With] (Bad) lette', job.validated_name)

  def test_ignore_dead_fork_link(self):
    data = {'id': 1, 'type': 'fork', 'children': [{'to': 1, 'id': 1}, {'to': 2, 'id': 2}], 'properties': {}, 'name': 'my-fork'} # to --> 2 does not exist
    fork = Node(data)

    node_mapping = {1: fork} # Point to ourself

    assert_equal(['<fork', 'name="my-fork">', '<path', 'start="my-fork"', '/>', '</fork>'], fork.to_xml(node_mapping=node_mapping).split())

  def test_action_gen_xml_prepare(self):
    # Prepare has a value
    data = {
        u'properties': {
            u'files': [], u'job_xml': [], u'parameters': [], u'retry_interval': [], u'retry_max': [], u'job_properties': [], u'arguments': [],
            u'prepares': [{u'type': u'mkdir', u'value': u'/my_dir'}],
            u'credentials': [], u'script_path': u'my_pig.pig',
            u'sla': [{u'key': u'enabled', u'value': False}, {u'key': u'nominal-time', u'value': u'${nominal_time}'}, {u'key': u'should-start', u'value': u''}, {u'key': u'should-end', u'value': u'${30 * MINUTES}'}, {u'key': u'max-duration', u'value': u''}, {u'key': u'alert-events', u'value': u''}, {u'key': u'alert-contact', u'value': u''}, {u'key': u'notification-msg', u'value': u''}, {u'key': u'upstream-apps', u'value': u''}],
            u'archives': []
        },
        u'type': u'pig-widget',
        u'id': u'c59d1947-7ce0-ef34-22b2-d64b9fc5bf9a',
        u'name': u'pig-c59d',
        "children":[{"to": "c59d1947-7ce0-ef34-22b2-d64b9fc5bf9a"}, {"error": "c59d1947-7ce0-ef34-22b2-d64b9fc5bf9a"}]
    }

    pig_node = Node(data)
    node_mapping = {"c59d1947-7ce0-ef34-22b2-d64b9fc5bf9a": pig_node}

    xml = pig_node.to_xml(node_mapping=node_mapping)
    xml = [row.strip() for row in xml.split()]

    assert_true(u'<prepare>' in xml, xml)
    assert_true(u'<mkdir' in xml, xml)
    assert_true(u'path="${nameNode}/my_dir"/>' in xml, xml)

    # Prepare has empty value and is skipped
    pig_node.data['properties']['prepares'] = [{u'type': u'mkdir', u'value': u''}]

    xml = pig_node.to_xml(node_mapping=node_mapping)
    xml = [row.strip() for row in xml.split()]

    assert_false(u'<prepare>' in xml, xml)
    assert_false(u'<mkdir' in xml, xml)

    # Prepare has a value and an empty value
    pig_node.data['properties']['prepares'] = [{u'type': u'mkdir', u'value': u'/my_dir'}, {u'type': u'rm', u'value': u''}]

    xml = pig_node.to_xml(node_mapping=node_mapping)
    xml = [row.strip() for row in xml.split()]

    assert_true(u'<prepare>' in xml, xml)
    assert_true(u'<mkdir' in xml, xml)
    assert_true(u'path="${nameNode}/my_dir"/>' in xml, xml)

    assert_false(u'<rm' in xml, xml)

  def test_upgrade_nodes_in_workflow(self):

    wf = Workflow(data="{\"layout\": [{\"oozieRows\": [{\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Sqoop 1\", \"widgetType\": \"sqoop-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"79774a62-94e3-2ddb-554f-b83640fa5b03\", \"size\": 12}], \"id\": \"0f54ae72-7122-ad7c-fb31-aa715e15a707\", \"columns\": []}], \"rows\": [{\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Start\", \"widgetType\": \"start-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"size\": 12}], \"id\": \"371cf19e-0c45-1e40-2887-5de4033c2a01\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Sqoop 1\", \"widgetType\": \"sqoop-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"79774a62-94e3-2ddb-554f-b83640fa5b03\", \"size\": 12}], \"id\": \"0f54ae72-7122-ad7c-fb31-aa715e15a707\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"End\", \"widgetType\": \"end-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"size\": 12}], \"id\": \"40cfacb5-0622-4305-1473-8f70e287668b\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Kill\", \"widgetType\": \"kill-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"size\": 12}], \"id\": \"373c9cc8-c64a-f1ef-5486-f18ec52620e3\", \"columns\": []}], \"oozieEndRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"End\", \"widgetType\": \"end-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"size\": 12}], \"id\": \"40cfacb5-0622-4305-1473-8f70e287668b\", \"columns\": []}, \"oozieKillRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Kill\", \"widgetType\": \"kill-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"size\": 12}], \"id\": \"373c9cc8-c64a-f1ef-5486-f18ec52620e3\", \"columns\": []}, \"enableOozieDropOnAfter\": true, \"oozieStartRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Start\", \"widgetType\": \"start-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"size\": 12}], \"id\": \"371cf19e-0c45-1e40-2887-5de4033c2a01\", \"columns\": []}, \"klass\": \"card card-home card-column span12\", \"enableOozieDropOnBefore\": true, \"drops\": [\"temp\"], \"id\": \"a8549012-ec27-4686-d71a-c6ff95785ff9\", \"size\": 12}], \"workflow\": {\"properties\": {\"job_xml\": \"\", \"description\": \"\", \"wf1_id\": null, \"sla_enabled\": false, \"deployment_dir\": \"/user/hue/oozie/workspaces/hue-oozie-1438808722.99\", \"schema_version\": \"uri:oozie:workflow:0.5\", \"properties\": [], \"show_arrows\": true, \"parameters\": [{\"name\": \"oozie.use.system.libpath\", \"value\": true}], \"sla\": [{\"value\": false, \"key\": \"enabled\"}, {\"value\": \"${nominal_time}\", \"key\": \"nominal-time\"}, {\"value\": \"\", \"key\": \"should-start\"}, {\"value\": \"${30 * MINUTES}\", \"key\": \"should-end\"}, {\"value\": \"\", \"key\": \"max-duration\"}, {\"value\": \"\", \"key\": \"alert-events\"}, {\"value\": \"\", \"key\": \"alert-contact\"}, {\"value\": \"\", \"key\": \"notification-msg\"}, {\"value\": \"\", \"key\": \"upstream-apps\"}]}, \"name\": \"My Workflow\", \"versions\": [\"uri:oozie:workflow:0.4\", \"uri:oozie:workflow:0.4.5\", \"uri:oozie:workflow:0.5\"], \"isDirty\": true, \"movedNode\": null, \"linkMapping\": {\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\": [], \"3f107997-04cc-8733-60a9-a4bb62cebffc\": [\"79774a62-94e3-2ddb-554f-b83640fa5b03\"], \"79774a62-94e3-2ddb-554f-b83640fa5b03\": [\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\"], \"17c9c895-5a16-7443-bb81-f34b30b21548\": []}, \"nodeIds\": [\"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"79774a62-94e3-2ddb-554f-b83640fa5b03\"], \"nodes\": [{\"properties\": {}, \"name\": \"Start\", \"children\": [{\"to\": \"79774a62-94e3-2ddb-554f-b83640fa5b03\"}], \"actionParametersFetched\": false, \"type\": \"start-widget\", \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"actionParameters\": []}, {\"properties\": {}, \"name\": \"End\", \"children\": [], \"actionParametersFetched\": false, \"type\": \"end-widget\", \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"actionParameters\": []}, {\"properties\": {\"message\": \"Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]\"}, \"name\": \"Kill\", \"children\": [], \"actionParametersFetched\": false, \"type\": \"kill-widget\", \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"actionParameters\": []}, {\"name\": \"sqoop-7977\", \"actionParametersUI\": [], \"children\": [{\"to\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\"}, {\"error\": \"17c9c895-5a16-7443-bb81-f34b30b21548\"}], \"properties\": {\"files\": [], \"job_xml\": \"\", \"parameters\": [], \"job_properties\": [], \"command\": \"import  --connect jdbc:hsqldb:file:db.hsqldb --table TT --target-dir hdfs://localhost:8020/user/foo -m 1\", \"archives\": [], \"prepares\": [], \"credentials\": [], \"sla\": [{\"value\": false, \"key\": \"enabled\"}, {\"value\": \"${nominal_time}\", \"key\": \"nominal-time\"}, {\"value\": \"\", \"key\": \"should-start\"}, {\"value\": \"${30 * MINUTES}\", \"key\": \"should-end\"}, {\"value\": \"\", \"key\": \"max-duration\"}, {\"value\": \"\", \"key\": \"alert-events\"}, {\"value\": \"\", \"key\": \"alert-contact\"}, {\"value\": \"\", \"key\": \"notification-msg\"}, {\"value\": \"\", \"key\": \"upstream-apps\"}]}, \"actionParametersFetched\": true, \"type\": \"sqoop-widget\", \"id\": \"79774a62-94e3-2ddb-554f-b83640fa5b03\", \"actionParameters\": []}], \"id\": null, \"nodeNamesMapping\": {\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\": \"End\", \"3f107997-04cc-8733-60a9-a4bb62cebffc\": \"Start\", \"79774a62-94e3-2ddb-554f-b83640fa5b03\": \"sqoop-7977\", \"17c9c895-5a16-7443-bb81-f34b30b21548\": \"Kill\"}, \"uuid\": \"b5511e29-c9cc-7f40-0d3a-6dd768f3b1e9\"}}")

    assert_true('parameters' in json.loads(wf.data)['workflow']['nodes'][3]['properties'], wf.data)
    assert_false('arguments' in json.loads(wf.data)['workflow']['nodes'][3]['properties'], wf.data) # Does not exist yet

    data = wf.get_data()

    assert_true('parameters' in data['workflow']['nodes'][3]['properties'], wf.data)
    assert_true('arguments' in data['workflow']['nodes'][3]['properties'], wf.data) # New field transparently added

  def test_action_gen_xml_java_opts(self):
    # Contains java_opts
    data = {u'name': u'java-fc05', u'properties': {u'files': [], u'job_xml': [], u'jar_path': u'/user/romain/hadoop-mapreduce-examples.jar', u'java_opts': [{u'value': u'-debug -Da -Db=1'}], u'retry_max': [], u'retry_interval': [], u'job_properties': [], u'capture_output': False, u'main_class': u'MyClass', u'arguments': [], u'prepares': [], u'credentials': [], u'sla': [{u'value': False, u'key': u'enabled'}, {u'value': u'${nominal_time}', u'key': u'nominal-time'}, {u'value': u'', u'key': u'should-start'}, {u'value': u'${30 * MINUTES}', u'key': u'should-end'}, {u'value': u'', u'key': u'max-duration'}, {u'value': u'', u'key': u'alert-events'}, {u'value': u'', u'key': u'alert-contact'}, {u'value': u'', u'key': u'notification-msg'}, {u'value': u'', u'key': u'upstream-apps'}], u'archives': []}, u'actionParametersFetched': False, u'id': u'fc05d86f-9f07-7a8d-6256-e6abfa87cf77', u'type': u'java-widget', u'children': [{u'to': u'33430f0f-ebfa-c3ec-f237-3e77efa03d0a'}, {u'error': u'17c9c895-5a16-7443-bb81-f34b30b21548'}], u'actionParameters': []}

    java_node = Node(data)
    node_mapping = {"fc05d86f-9f07-7a8d-6256-e6abfa87cf77": java_node, "33430f0f-ebfa-c3ec-f237-3e77efa03d0a": java_node, "17c9c895-5a16-7443-bb81-f34b30b21548": java_node} # Last 2 are actually kill and ok nodes

    xml = java_node.to_xml(node_mapping=node_mapping)
    xml = [row.strip() for row in xml.split('\n')]

    assert_false("<java-opts>[{u&#39;value&#39;: u&#39;-debug -Da -Db=1&#39;}]</java-opts>" in xml, xml)
    assert_true("<java-opts>-debug -Da -Db=1</java-opts>" in xml, xml)

  def test_workflow_create_single_action_data(self):
    workflow = Workflow(data="{\"layout\": [{\"oozieRows\": [{\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"MapReduce job\", \"widgetType\": \"mapreduce-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\", \"size\": 12}], \"id\": \"e2caca14-8afc-d7e0-287c-88accd0b4253\", \"columns\": []}], \"rows\": [{\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Start\", \"widgetType\": \"start-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"size\": 12}], \"id\": \"ff63ee3f-df54-2fa3-477b-65f5e0f0632c\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"MapReduce job\", \"widgetType\": \"mapreduce-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\", \"size\": 12}], \"id\": \"e2caca14-8afc-d7e0-287c-88accd0b4253\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"End\", \"widgetType\": \"end-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"size\": 12}], \"id\": \"6a13d869-d04c-8431-6c5c-dbe67ea33889\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Kill\", \"widgetType\": \"kill-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"size\": 12}], \"id\": \"e3b56553-7a4f-43d2-b1e2-4dc433280095\", \"columns\": []}], \"oozieEndRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"End\", \"widgetType\": \"end-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"size\": 12}], \"id\": \"6a13d869-d04c-8431-6c5c-dbe67ea33889\", \"columns\": []}, \"oozieKillRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Kill\", \"widgetType\": \"kill-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"size\": 12}], \"id\": \"e3b56553-7a4f-43d2-b1e2-4dc433280095\", \"columns\": []}, \"enableOozieDropOnAfter\": true, \"oozieStartRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Start\", \"widgetType\": \"start-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"size\": 12}], \"id\": \"ff63ee3f-df54-2fa3-477b-65f5e0f0632c\", \"columns\": []}, \"klass\": \"card card-home card-column span12\", \"enableOozieDropOnBefore\": true, \"drops\": [\"temp\"], \"id\": \"0c1908e7-0096-46e7-a16b-b17b1142a730\", \"size\": 12}], \"workflow\": {\"properties\": {\"job_xml\": \"\", \"description\": \"\", \"wf1_id\": null, \"sla_enabled\": false, \"deployment_dir\": \"/user/hue/oozie/workspaces/hue-oozie-1430228904.58\", \"schema_version\": \"uri:oozie:workflow:0.5\", \"sla\": [{\"key\": \"enabled\", \"value\": false}, {\"key\": \"nominal-time\", \"value\": \"${nominal_time}\"}, {\"key\": \"should-start\", \"value\": \"\"}, {\"key\": \"should-end\", \"value\": \"${30 * MINUTES}\"}, {\"key\": \"max-duration\", \"value\": \"\"}, {\"key\": \"alert-events\", \"value\": \"\"}, {\"key\": \"alert-contact\", \"value\": \"\"}, {\"key\": \"notification-msg\", \"value\": \"\"}, {\"key\": \"upstream-apps\", \"value\": \"\"}], \"show_arrows\": true, \"parameters\": [{\"name\": \"oozie.use.system.libpath\", \"value\": true}], \"properties\": []}, \"name\": \"My Workflow\", \"versions\": [\"uri:oozie:workflow:0.4\", \"uri:oozie:workflow:0.4.5\", \"uri:oozie:workflow:0.5\"], \"isDirty\": true, \"movedNode\": null, \"linkMapping\": {\"0cf2d5d5-2315-0bda-bd53-0eec257e943f\": [\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\"], \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\": [], \"3f107997-04cc-8733-60a9-a4bb62cebffc\": [\"0cf2d5d5-2315-0bda-bd53-0eec257e943f\"], \"17c9c895-5a16-7443-bb81-f34b30b21548\": []}, \"nodeIds\": [\"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\"], \"nodes\": [{\"properties\": {}, \"name\": \"Start\", \"children\": [{\"to\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\"}], \"actionParametersFetched\": false, \"type\": \"start-widget\", \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"actionParameters\": []}, {\"properties\": {}, \"name\": \"End\", \"children\": [], \"actionParametersFetched\": false, \"type\": \"end-widget\", \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"actionParameters\": []}, {\"properties\": {\"message\": \"Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]\"}, \"name\": \"Kill\", \"children\": [], \"actionParametersFetched\": false, \"type\": \"kill-widget\", \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"actionParameters\": []}, {\"properties\": {\"retry_max\": [{\"value\": \"5\"}], \"files\": [], \"job_xml\": \"\", \"jar_path\": \"my_jar\", \"job_properties\": [{\"name\": \"prop_1_name\", \"value\": \"prop_1_value\"}], \"archives\": [], \"prepares\": [], \"credentials\": [], \"sla\": [{\"key\": \"enabled\", \"value\": false}, {\"key\": \"nominal-time\", \"value\": \"${nominal_time}\"}, {\"key\": \"should-start\", \"value\": \"\"}, {\"key\": \"should-end\", \"value\": \"${30 * MINUTES}\"}, {\"key\": \"max-duration\", \"value\": \"\"}, {\"key\": \"alert-events\", \"value\": \"\"}, {\"key\": \"alert-contact\", \"value\": \"\"}, {\"key\": \"notification-msg\", \"value\": \"\"}, {\"key\": \"upstream-apps\", \"value\": \"\"}]}, \"name\": \"mapreduce-0cf2\", \"children\": [{\"to\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\"}, {\"error\": \"17c9c895-5a16-7443-bb81-f34b30b21548\"}], \"actionParametersFetched\": false, \"type\": \"mapreduce-widget\", \"id\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\", \"actionParameters\": []}], \"id\": 50019, \"nodeNamesMapping\": {\"0cf2d5d5-2315-0bda-bd53-0eec257e943f\": \"mapreduce-0cf2\", \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\": \"End\", \"3f107997-04cc-8733-60a9-a4bb62cebffc\": \"Start\", \"17c9c895-5a16-7443-bb81-f34b30b21548\": \"Kill\"}, \"uuid\": \"084f4d4c-00f1-62d2-e27e-e153c1f9acfb\"}}")

    single_action_wf_data = workflow.create_single_action_workflow_data('0cf2d5d5-2315-0bda-bd53-0eec257e943f')
    single_action_wf = Workflow(data=single_action_wf_data)
    assert_true(len(single_action_wf.nodes) == 4)

    # Validating DAG: Start -> node -> Kill/End
    _data = json.loads(single_action_wf_data)
    start_node = [node for node in _data['workflow']['nodes'] if node['name'] == 'Start'][0]
    submit_node = [node for node in _data['workflow']['nodes'] if node['id'] == '0cf2d5d5-2315-0bda-bd53-0eec257e943f'][0]
    end_node = [node for node in _data['workflow']['nodes'] if node['name'] == 'End'][0]
    kill_node = [node for node in _data['workflow']['nodes'] if node['name'] == 'Kill'][0]

    assert_true(submit_node['id'] in str(start_node['children']))
    assert_true(end_node['id'] in str(submit_node['children']))
    assert_true(kill_node['id'] in str(submit_node['children']))

  def test_submit_single_action(self):
    wf_doc = save_temp_workflow(MockOozieApi.JSON_WORKFLOW_LIST[5], self.user)
    reset = ENABLE_V2.set_for_testing(True)
    try:
      response = self.c.get(reverse('oozie:submit_single_action', args=[wf_doc.id, '3f107997-04cc-8733-60a9-a4bb62cebabc']))
      assert_equal([{'name':'Dryrun', 'value': False}, {'name':'ls_arg', 'value': '-l'}], response.context[0]._data['params_form'].initial)
    except Exception, ex:
      logging.exception(ex)
    finally:
      reset()
      wf_doc.delete()

  def test_list_bundles_page(self):
    response = self.c.get(reverse('oozie:list_editor_bundles'))
    assert_true('bundles_json' in response.context[0]._data, response.context)

  def test_workflow_dependencies(self):
    wf_data = """{"layout": [{"oozieRows": [{"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Sub workflow", "widgetType": "subworkflow-widget", "oozieMovable": true, "ooziePropertiesExpanded": false, "externalIdUrl": "", "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "9a24c7b1-b031-15d6-4086-e8af63be7ed4", "size": 12}], "id": "a566315f-e0e0-f408-fabd-c4576cc4041d", "columns": []}], "rows": [{"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Start", "widgetType": "start-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "externalIdUrl": "", "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "size": 12}], "id": "ec1fbd7f-ff6c-95eb-a865-ed3a3a00fc59", "columns": []}, {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Sub workflow", "widgetType": "subworkflow-widget", "oozieMovable": true, "ooziePropertiesExpanded": false, "externalIdUrl": "", "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "9a24c7b1-b031-15d6-4086-e8af63be7ed4", "size": 12}], "id": "a566315f-e0e0-f408-fabd-c4576cc4041d", "columns": []}, {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "End", "widgetType": "end-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "externalIdUrl": "", "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "size": 12}], "id": "cd1a181a-9db0-c295-78e4-4d67ecedd057", "columns": []}, {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Kill", "widgetType": "kill-widget", "oozieMovable": true, "ooziePropertiesExpanded": false, "externalIdUrl": "", "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "size": 12}], "id": "caf2a089-c5d2-4a55-5b90-2a691be25884", "columns": []}], "oozieEndRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "End", "widgetType": "end-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "externalIdUrl": "", "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "size": 12}], "id": "cd1a181a-9db0-c295-78e4-4d67ecedd057", "columns": []}, "oozieKillRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Kill", "widgetType": "kill-widget", "oozieMovable": true, "ooziePropertiesExpanded": false, "externalIdUrl": "", "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "size": 12}], "id": "caf2a089-c5d2-4a55-5b90-2a691be25884", "columns": []}, "enableOozieDropOnAfter": true, "oozieStartRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Start", "widgetType": "start-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "externalIdUrl": "", "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "size": 12}], "id": "ec1fbd7f-ff6c-95eb-a865-ed3a3a00fc59", "columns": []}, "klass": "card card-home card-column span12", "enableOozieDropOnBefore": true, "drops": ["temp"], "id": "f162ea58-e396-9703-c2b4-329bad4c9fa9", "size": 12}], "workflow": {"properties": {"job_xml": "", "description": "", "parameters": [{"name": "oozie.use.system.libpath", "value": true}], "sla_enabled": false, "deployment_dir": "/user/hue/oozie/workspaces/hue-oozie-1462236042.61", "schema_version": "uri:oozie:workflow:0.5", "sla": [{"value": false, "key": "enabled"}, {"value": "${nominal_time}", "key": "nominal-time"}, {"value": "", "key": "should-start"}, {"value": "${30 * MINUTES}", "key": "should-end"}, {"value": "", "key": "max-duration"}, {"value": "", "key": "alert-events"}, {"value": "", "key": "alert-contact"}, {"value": "", "key": "notification-msg"}, {"value": "", "key": "upstream-apps"}], "show_arrows": true, "wf1_id": null, "properties": []}, "name": "test-sub", "versions": ["uri:oozie:workflow:0.4", "uri:oozie:workflow:0.4.5", "uri:oozie:workflow:0.5"], "isDirty": true, "movedNode": null, "linkMapping": {"17c9c895-5a16-7443-bb81-f34b30b21548": [], "33430f0f-ebfa-c3ec-f237-3e77efa03d0a": [], "9a24c7b1-b031-15d6-4086-e8af63be7ed4": ["33430f0f-ebfa-c3ec-f237-3e77efa03d0a"], "3f107997-04cc-8733-60a9-a4bb62cebffc": ["9a24c7b1-b031-15d6-4086-e8af63be7ed4"]}, "nodeIds": ["3f107997-04cc-8733-60a9-a4bb62cebffc", "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "17c9c895-5a16-7443-bb81-f34b30b21548", "9a24c7b1-b031-15d6-4086-e8af63be7ed4"], "nodes": [{"properties": {"uuid": "7705a9dd-164e-67eb-8758-2573800c86e1", "workflow": "7705a9dd-164e-67eb-8758-2573800c86e6", "retry_interval": [], "retry_max": [], "job_properties": [], "credentials": [], "propagate_configuration": true, "sla": [{"key": "enabled", "value": false}, {"key": "nominal-time", "value": "${nominal_time}"}, {"key": "should-start", "value": ""}, {"key": "should-end", "value": "${30 * MINUTES}"}, {"key": "max-duration", "value": ""}, {"key": "alert-events", "value": ""}, {"key": "alert-contact", "value": ""}, {"key": "notification-msg", "value": ""}, {"key": "upstream-apps", "value": ""}]}, "name": "hive-sql", "children": [{"to": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a"}, {"error": "17c9c895-5a16-7443-bb81-f34b30b21548"}], "actionParametersFetched": false, "type": "hive-document-widget", "id": "9a24c7b1-b031-15d6-4086-e8af63be7ed3", "actionParameters": []}, {"properties": {}, "name": "Start", "children": [{"to": "9a24c7b1-b031-15d6-4086-e8af63be7ed4"}], "actionParametersFetched": false, "type": "start-widget", "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "actionParameters": []}, {"properties": {}, "name": "End", "children": [], "actionParametersFetched": false, "type": "end-widget", "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "actionParameters": []}, {"properties": {"body": "", "cc": "", "to": "", "enableMail": false, "message": "Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]", "subject": ""}, "name": "Kill", "children": [], "actionParametersFetched": false, "type": "kill-widget", "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "actionParameters": []}, {"properties": {"workflow": "7705a9dd-164e-67eb-8758-2573800c86e5", "retry_interval": [], "retry_max": [], "job_properties": [], "credentials": [], "propagate_configuration": true, "sla": [{"value": false, "key": "enabled"}, {"value": "${nominal_time}", "key": "nominal-time"}, {"value": "", "key": "should-start"}, {"value": "${30 * MINUTES}", "key": "should-end"}, {"value": "", "key": "max-duration"}, {"value": "", "key": "alert-events"}, {"value": "", "key": "alert-contact"}, {"value": "", "key": "notification-msg"}, {"value": "", "key": "upstream-apps"}]}, "name": "subworkflow-9a24", "children": [{"to": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a"}, {"error": "17c9c895-5a16-7443-bb81-f34b30b21548"}], "actionParametersFetched": false, "type": "subworkflow-widget", "id": "9a24c7b1-b031-15d6-4086-e8af63be7ed4", "actionParameters": []}], "id": null, "nodeNamesMapping": {"17c9c895-5a16-7443-bb81-f34b30b21548": "Kill", "33430f0f-ebfa-c3ec-f237-3e77efa03d0a": "End", "9a24c7b1-b031-15d6-4086-e8af63be7ed4": "subworkflow-9a24", "3f107997-04cc-8733-60a9-a4bb62cebffc": "Start"}, "uuid": "73c6219d-272f-db98-3cd9-d413ea2625ac"}}"""
    wf_doc1 = Document2.objects.create(name='test', type='oozie-workflow2', owner=self.user, data=wf_data)
    Document.objects.link(wf_doc1, owner=wf_doc1.owner, name=wf_doc1.name, description=wf_doc1.description, extra='workflow2')

    # Add history dependency
    wf_doc1.is_history = True
    wf_doc1.dependencies.add(wf_doc1)

    # Add coordinator dependency
    coord_data = {
          'id': None,
          'uuid': None,
          'name': 'My Schedule',
          'variables': [], # Aka workflow parameters
          'properties': {
              'description': '',
              'deployment_dir': '',
              'schema_version': 'uri:oozie:coordinator:0.2',
              'frequency_number': 1,
              'frequency_unit': 'days',
              'cron_frequency': '0 0 * * *',
              'cron_advanced': False,
              'timezone': '',
              'start': '${start_date}',
              'end': '${end_date}',
              'workflow': None,
              'timeout': None,
              'concurrency': None,
              'execution': None,
              'throttle': None,
              'job_xml': '',
              'credentials': [],
              'parameters': [
                  {'name': 'oozie.use.system.libpath', 'value': True},
                  {'name': 'start_date', 'value': ''},
                  {'name': 'end_date', 'value': ''}
              ],
              'sla': WorkflowConfiguration.SLA_DEFAULT
          }
      }
    wf_doc2 = Document2.objects.create(name='test', type='oozie-coordinator2', owner=wf_doc1.owner, data=coord_data)
    wf_doc1.dependencies.add(wf_doc2)
    wf_doc1.save()

    workflow_data = json.loads(wf_data)['workflow']
    layout_data = json.loads(wf_data)['layout']

    # Add query doc to Doc2
    hive_node_props = [node['properties'] for node in workflow_data['nodes'] if node['type'] == 'hive-document-widget'][0]
    query_doc = Document2.objects.create(name='test', uuid=hive_node_props['uuid'], type='query-hive', owner=wf_doc1.owner, description='test')

    # Add subworkflow doc to Doc2
    subworkflow_node_props = [node['properties'] for node in workflow_data['nodes'] if node['type'] == 'subworkflow-widget'][0]
    subworkflow_doc = Document2.objects.create(name='test', uuid=subworkflow_node_props['workflow'], type='oozie-workflow2', owner=wf_doc1.owner, description='test')

    workflow_data['id'] = wf_doc1.id
    response = self.c.post(reverse('oozie:save_workflow'), {'workflow': json.dumps(workflow_data), 'layout': json.dumps(layout_data)})
    response = json.loads(response.content)

    assert_true(response['status'] == 0)
    workflow_doc = Document2.objects.get(id=response['id'])

    # Validating dependencies after saving the workflow
    assert_equal(workflow_doc.dependencies.all().count(), 4)
    assert_equal(workflow_doc.dependencies.filter(type='oozie-coordinator2').count(), 1)
    assert_equal(workflow_doc.dependencies.filter(type='query-hive').count(), 1)
    assert_equal((workflow_doc.dependencies.filter(Q(is_history=False) & Q(type='oozie-workflow2'))).count(), 1)
    assert_equal((workflow_doc.dependencies.filter(Q(is_history=True) & Q(type='oozie-workflow2'))).count(), 1)

    wf_doc1.delete()
    wf_doc2.delete()
    workflow_doc.delete()
    subworkflow_doc.delete()
    query_doc.delete()


  def test_editor_access_permissions(self):
    group = 'no_editor'

    try:
      # Block editor section
      response = self.c.get(reverse('oozie:list_editor_workflows'))
      assert_equal(response.status_code, 200)
      response = self.c.get(reverse('oozie:list_workflows'))
      assert_equal(response.status_code, 200)

      add_permission('test', 'no_editor', 'disable_editor_access', 'oozie')

      response = self.c.get(reverse('oozie:list_editor_workflows'))
      assert_equal(response.status_code, 401)
      response = self.c.get(reverse('oozie:list_workflows'))
      assert_equal(response.status_code, 200)

      # Admin are not affected
      admin = make_logged_in_client('admin', 'admin', is_superuser=True, recreate=True, groupname=group)

      response = admin.get(reverse('oozie:list_editor_workflows'))
      assert_equal(response.status_code, 200)
      response = admin.get(reverse('oozie:list_workflows'))
      assert_equal(response.status_code, 200)
    finally:
      remove_from_group("test", group)


  def test_share_workflow(self):
    try:
      wf_doc = save_temp_workflow(MockOozieApi.JSON_WORKFLOW_LIST[5], self.user)

      # other user cannot view document
      response = self.client_not_me.get(reverse('oozie:edit_workflow'), {'uuid': wf_doc.uuid})
      assert_equal(response.status_code, 401)

      # Share write perm by user
      if USE_NEW_EDITOR.get():
        wf_doc.share(wf_doc.owner, name='write', users=[self.user_not_me])
      else:
        wf_doc.doc.get().sync_permissions({'write': {'user_ids': [self.user_not_me.id], 'group_ids': []}})

      # other user can access document
      response = self.client_not_me.get(reverse('oozie:edit_workflow'), {'workflow': wf_doc.uuid})
      assert_false('Document does not exist or you don&#39;t have the permission to access it.' in response.content, response.content)
    finally:
      wf_doc.delete()


  def test_list_editor_workflows(self):
    wf_doc = save_temp_workflow(MockOozieApi.JSON_WORKFLOW_LIST[5], self.user)
    reset = ENABLE_V2.set_for_testing(True)
    try:
      response = self.c.get(reverse('oozie:list_editor_workflows'))
      assert_equal(response.status_code, 200)
      data = json.loads(response.context[0]['workflows_json'])
      uuids = [doc['uuid'] for doc in data]
      assert_true(wf_doc.uuid in uuids, data)

      # Trash workflow and verify it no longer appears in list
      response = self.c.post('/desktop/api2/doc/delete', {'uuid': json.dumps(wf_doc.uuid)})
      response = self.c.get(reverse('oozie:list_editor_workflows'))
      assert_equal(response.status_code, 200)
      data = json.loads(response.context[0]['workflows_json'])
      uuids = [doc['uuid'] for doc in data]
      assert_false(wf_doc.uuid in uuids, data)
    finally:
      reset()
      wf_doc.delete()


  def test_workflow_properties(self):
    reset = USE_DEFAULT_CONFIGURATION.set_for_testing(True)

    try:
      # Test that a new workflow will be initialized with default properties if no saved configs exist
      wf = Workflow(user=self.user)
      data = json.loads(wf.data)
      assert_equal(data['workflow']['properties'], Workflow.get_workflow_properties_for_user(self.user))

      # Setup a test Default configuration, NOTE: this is an invalid format for testing only
      properties = [
        {
          'multiple': False,
          'value': '/user/test/oozie',
          'nice_name': 'Workspace',
          'key': 'deployment_dir',
          'help_text': 'Specify the deployment directory.',
          'type': 'hdfs-file'
        }, {
          'multiple': True,
          'value': [
            {
              'value': 'test',
              'key': 'mapred.queue.name'
            }
          ],
          'nice_name': 'Hadoop Properties',
          'key': 'properties',
          'help_text': 'Hadoop configuration properties.',
          'type': 'settings'
        }
      ]

      wf_props = Workflow.get_properties()
      config = DefaultConfiguration(app=WorkflowConfiguration.APP_NAME, properties=json.dumps(properties), is_default=True)
      config.save()
      wf_props.update(config.properties_dict)
      wf_props.update({'wf1_id': None, 'description': ''})

      # Test that a new workflow will be initialized with Default saved config if it exists
      wf = Workflow(user=self.user)
      data = json.loads(wf.data)
      assert_equal(data['workflow']['properties'], wf_props)

      # Test that a new workflow will be initialized with Group saved config if it exists
      properties = [
        {
            'multiple': True,
            'value': [
                {
                    'value': 'org.myorg.WordCount.Map',
                    'key': 'mapred.mapper.class'
                },
                {
                    'value': 'org.myorg.WordCount.Reduce',
                    'key': 'mapred.reducer.class'
                }
            ],
            'nice_name': 'Hadoop Properties',
            'key': 'properties',
            'help_text': 'Hadoop configuration properties.',
            'type': 'settings'
        }
      ]

      wf_props = Workflow.get_properties()
      config = DefaultConfiguration.objects.create(app=WorkflowConfiguration.APP_NAME,
        properties=json.dumps(properties),
        is_default=False)
      config.groups.add(self.user.groups.first())
      config.save()
      wf_props.update(config.properties_dict)
      wf_props.update({'wf1_id': None, 'description': ''})

      # Test that a new workflow will be initialized with Default saved config if it exists
      wf = Workflow(user=self.user)
      data = json.loads(wf.data)
      assert_equal(data['workflow']['properties'], wf_props)
    finally:
      reset()


class TestExternalWorkflowGraph(object):

  def setUp(self):
    self.wf = Workflow()

    self.c = make_logged_in_client(is_superuser=False)
    grant_access("test", "test", "oozie")
    add_to_group("test")
    self.user = User.objects.get(username='test')

  def test_graph_generation_from_xml(self):
    f = open('apps/oozie/src/oozie/test_data/xslt2/test-workflow.xml')
    self.wf.definition = f.read()
    self.node_list = [{u'node_type': u'start', u'ok_to': u'fork-68d4', u'name': u''}, {u'node_type': u'kill', u'ok_to': u'', u'name': u'Kill'}, {u'path2': u'shell-0f44', u'node_type': u'fork', u'ok_to': u'', u'name': u'fork-68d4', u'path1': u'subworkflow-a13f'}, {u'node_type': u'join', u'ok_to': u'End', u'name': u'join-775e'}, {u'node_type': u'end', u'ok_to': u'', u'name': u'End'}, {u'subworkflow': {u'app-path': u'${nameNode}/user/hue/oozie/deployments/_admin_-oozie-50001-1427488969.48'}, u'node_type': u'sub-workflow', u'ok_to': u'join-775e', u'name': u'subworkflow-a13f', u'error_to': u'Kill'}, {u'shell': {u'command': u'ls'}, u'node_type': u'shell', u'ok_to': u'join-775e', u'name': u'shell-0f44', u'error_to': u'Kill'}]
    assert_equal(self.node_list, generate_v2_graph_nodes(self.wf.definition))

  def test_get_graph_adjacency_list(self):
    self.node_list = [{u'node_type': u'start', u'ok_to': u'fork-68d4', u'name': u''}, {u'node_type': u'kill', u'ok_to': u'', u'name': u'kill'}, {u'path2': u'shell-0f44', u'node_type': u'fork', u'ok_to': u'', u'name': u'fork-68d4', u'path1': u'subworkflow-a13f'}, {u'node_type': u'join', u'ok_to': u'end', u'name': u'join-775e'}, {u'node_type': u'end', u'ok_to': u'', u'name': u'end'}, {u'node_type': u'sub-workflow', u'ok_to': u'join-775e', u'sub-workflow': {u'app-path': u'${nameNode}/user/hue/oozie/deployments/_admin_-oozie-50001-1427488969.48'}, u'name': u'subworkflow-a13f', u'error_to': u'kill'}, {u'shell': {u'command': u'ls'}, u'node_type': u'shell', u'ok_to': u'join-775e', u'name': u'shell-0f44', u'error_to': u'kill'}]
    adj_list = _create_graph_adjaceny_list(self.node_list)

    assert_true(len(adj_list) == 7)
    assert_true('subworkflow-a13f' in adj_list.keys())
    assert_true(adj_list['shell-0f44']['shell']['command'] == 'ls')
    assert_equal(adj_list['fork-68d4'], {u'path2': u'shell-0f44', u'node_type': u'fork', u'ok_to': u'', u'name': u'fork-68d4', u'path1': u'subworkflow-a13f'})

  def test_get_hierarchy_from_adj_list(self):
    self.wf.definition = """<workflow-app name="ls-4thread" xmlns="uri:oozie:workflow:0.5">
        <start to="fork-fe93"/>
        <kill name="Kill">
            <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
        </kill>
        <action name="shell-5429">
            <shell xmlns="uri:oozie:shell-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <exec>ls</exec>
                  <capture-output/>
            </shell>
            <ok to="join-7f80"/>
            <error to="Kill"/>
        </action>
        <action name="shell-bd90">
            <shell xmlns="uri:oozie:shell-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <exec>ls</exec>
                  <capture-output/>
            </shell>
            <ok to="join-7f80"/>
            <error to="Kill"/>
        </action>
        <fork name="fork-fe93">
            <path start="shell-5429" />
            <path start="shell-bd90" />
            <path start="shell-d64c" />
            <path start="shell-d8cc" />
        </fork>
        <join name="join-7f80" to="End"/>
        <action name="shell-d64c">
            <shell xmlns="uri:oozie:shell-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <exec>ls</exec>
                  <capture-output/>
            </shell>
            <ok to="join-7f80"/>
            <error to="Kill"/>
        </action>
        <action name="shell-d8cc">
            <shell xmlns="uri:oozie:shell-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <exec>ls</exec>
                  <capture-output/>
            </shell>
            <ok to="join-7f80"/>
            <error to="Kill"/>
        </action>
        <end name="End"/>
    </workflow-app>"""

    node_list = generate_v2_graph_nodes(self.wf.definition)
    adj_list = _create_graph_adjaceny_list(node_list)

    node_hierarchy = ['start']
    _get_hierarchy_from_adj_list(adj_list, adj_list['start']['ok_to'], node_hierarchy)

    assert_equal(node_hierarchy, ['start', [u'fork-fe93', [[u'shell-bd90'], [u'shell-d64c'], [u'shell-5429'], [u'shell-d8cc']], u'join-7f80'], ['Kill'], ['End']])

  def test_gen_workflow_data_from_xml(self):
    self.wf.definition = """<workflow-app name="fork-fork-test" xmlns="uri:oozie:workflow:0.5">
        <start to="fork-949d"/>
        <kill name="Kill">
            <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
        </kill>
        <action name="shell-eadd">
            <shell xmlns="uri:oozie:shell-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <exec>ls</exec>
                  <capture-output/>
            </shell>
            <ok to="join-1a0f"/>
            <error to="Kill"/>
        </action>
        <action name="shell-f4c1">
            <shell xmlns="uri:oozie:shell-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <exec>ls</exec>
                  <capture-output/>
            </shell>
            <ok to="join-3bba"/>
            <error to="Kill"/>
        </action>
        <fork name="fork-949d">
            <path start="fork-e5fa" />
            <path start="shell-3dd5" />
        </fork>
        <join name="join-ca1a" to="End"/>
        <action name="shell-ef70">
            <shell xmlns="uri:oozie:shell-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <exec>ls</exec>
                  <capture-output/>
            </shell>
            <ok to="join-1a0f"/>
            <error to="Kill"/>
        </action>
        <fork name="fork-37d7">
            <path start="shell-eadd" />
            <path start="shell-ef70" />
        </fork>
        <join name="join-1a0f" to="join-ca1a"/>
        <action name="shell-3dd5">
            <shell xmlns="uri:oozie:shell-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <exec>ls</exec>
                  <capture-output/>
            </shell>
            <ok to="fork-37d7"/>
            <error to="Kill"/>
        </action>
        <action name="shell-2ba8">
            <shell xmlns="uri:oozie:shell-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <exec>ls</exec>
                  <capture-output/>
            </shell>
            <ok to="join-3bba"/>
            <error to="Kill"/>
        </action>
        <fork name="fork-e5fa">
            <path start="shell-f4c1" />
            <path start="shell-2ba8" />
        </fork>
        <join name="join-3bba" to="join-ca1a"/>
        <end name="End"/>
    </workflow-app>"""

    workflow_data = Workflow.gen_workflow_data_from_xml(self.user, self.wf)

    assert_true(len(workflow_data['layout'][0]['rows']) == 6)
    assert_true(len(workflow_data['workflow']['nodes']) == 14)
    assert_equal(workflow_data['layout'][0]['rows'][1]['widgets'][0]['widgetType'], 'fork-widget')
    assert_equal(workflow_data['workflow']['nodes'][0]['name'], 'start-3f10')

  def test_gen_workflow_data_from_xml_for_email(self):
    self.wf.definition = """<workflow-app name="My_Workflow" xmlns="uri:oozie:workflow:0.5">
        <start to="email-0377"/>
        <kill name="Kill">
            <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
        </kill>
        <action name="email-0377">
            <email xmlns="uri:oozie:email-action:0.2">
                <to>example@example.com</to>
                <subject>sub</subject>
                <bcc>example@bcc.com</bcc>
                <body>bod</body>
                <content_type>text/plain</content_type>
            </email>
            <ok to="End"/>
            <error to="Kill"/>
        </action>
        <end name="End"/>
    </workflow-app>"""

    workflow_data = Workflow.gen_workflow_data_from_xml(self.user, self.wf)

    assert_true(len(workflow_data['layout'][0]['rows']) == 4)
    assert_true(len(workflow_data['workflow']['nodes']) == 4)
    assert_equal(workflow_data['layout'][0]['rows'][1]['widgets'][0]['widgetType'], 'email-widget')
    assert_equal(workflow_data['workflow']['nodes'][0]['name'], 'start-3f10')

  def test_gen_workflow_data_from_xml_for_fs(self):
    self.wf.definition = """<workflow-app name="My_Workflow" xmlns="uri:oozie:workflow:0.5">
        <start to="fs-d2ff"/>
        <kill name="Kill">
            <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
        </kill>
        <action name="fs-d2ff">
            <fs>
                  <delete path='${nameNode}/user/admin/y'/>
                  <delete path='${nameNode}/user/admin/a'/>
                  <mkdir path='${nameNode}/user/admin/sai'/>
                  <mkdir path='${nameNode}/user/admin/sai1'/>
                  <move source='${nameNode}/user/admin/sai/test' target='${nameNode}/user/admin/sai/test1'/>
                  <move source='${nameNode}/user/admin/b' target='${nameNode}/user/admin/c'/>
                  <touchz path='${nameNode}/user/admin/sai/test'/>
                  <touchz path='${nameNode}/user/admin/temp1'/>
            </fs>
            <ok to="End"/>
            <error to="Kill"/>
        </action>
        <end name="End"/>
    </workflow-app>"""

    workflow_data = Workflow.gen_workflow_data_from_xml(self.user, self.wf)

    assert_true(len(workflow_data['layout'][0]['rows']) == 4)
    assert_true(len(workflow_data['workflow']['nodes']) == 4)
    assert_equal(workflow_data['layout'][0]['rows'][1]['widgets'][0]['widgetType'], 'fs-widget')
    assert_true(len(workflow_data['workflow']['nodes'][1]['properties']['deletes']), 2)
    assert_equal(workflow_data['workflow']['nodes'][1]['properties']['deletes'][0]['value'], u'${nameNode}/user/admin/y')

  def test_gen_workflow_data_from_xml_for_decision_node(self):
    self.wf.definition = """<workflow-app xmlns="uri:oozie:workflow:0.5" name="capture-output-wf">
      <credentials>
        <credential name="hive2" type="hive2">
          <property>
            <name>hive2.jdbc.url</name>
            <value>jdbc:hive2://huetest-1.gce.cloudera.com:10000/default</value>
          </property>
          <property>
            <name>hive2.server.principal</name>
            <value>hive/huetest-1.gce.cloudera.com@GCE.CLOUDERA.COM</value>
          </property>
        </credential>
      </credentials>

        <start to="fork1"/>

        <fork name="fork1">
            <path start="capture-shell"/>
            <path start="hive-node"/>
        </fork>
        <action name="capture-shell">
            <shell xmlns="uri:oozie:shell-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <exec>capture-shell.sh</exec>
                <file>capture-shell.sh#capture-shell.sh</file>
                <capture-output/>
            </shell>
            <ok to="join1"/>
            <error to="fail"/>
        </action>
        <action name="hive-node" cred="hive2">
            <hive2 xmlns="uri:oozie:hive2-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <jdbc-url>jdbc:hive2://huetest-1.gce.cloudera.com:10000/default</jdbc-url>
                <script>/user/cconner/chris1.sql</script>
            </hive2>
            <ok to="join1"/>
            <error to="fail"/>
        </action>

        <join name="join1" to="email1"/>

        <action name="email1">
            <email xmlns="uri:oozie:email-action:0.1">
                <to>oozie@admin1.sec.cloudera.com</to>
                <subject>capture output workflow</subject>
                <body>yay</body>
            </email>
            <ok to="java-decision"/>
            <error to="fail"/>
        </action>

        <action name='java-decision'>
            <java>
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <configuration>
                    <property>
                        <name>mapred.job.queue.name</name>
                        <value>${queueName}</value>
                    </property>
                </configuration>
                <main-class>com.test.CurrentTime</main-class>
                <capture-output/>
            </java>
            <ok to="java-decision1" />
            <error to="fail" />
        </action>
        <decision name="java-decision1">
               <switch>
               <case to="end">${(wf:actionData('java-decision')['key1'] == "true")}</case>
               <default to="fail" />
               </switch>
        </decision>

        <kill name="fail">
            <message>Hive failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
        </kill>
        <end name="end"/>
    </workflow-app>
    """

    workflow_data = Workflow.gen_workflow_data_from_xml(self.user, self.wf)

    assert_true(len(workflow_data['layout'][0]['rows']) == 10)
    assert_true(len(workflow_data['workflow']['nodes']) == 10)
    assert_equal(workflow_data['layout'][0]['rows'][6]['widgets'][0]['widgetType'], 'decision-widget')
    assert_equal(workflow_data['workflow']['nodes'][7]['type'], 'decision-widget')
    assert_true(len(workflow_data['workflow']['nodes'][7]['children']) == 2)

  def test_gen_workflow_data_from_xml_for_oozie_old_schemas(self):

    common_wf_definition = """<workflow-app name="My Workflow" xmlns="uri:oozie:workflow:%s">
        <start to="fork-b429"/>
        <kill name="Kill">
            <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
        </kill>
        <action name="hive-ee32" cred="hive2">
            <hive2 xmlns="uri:oozie:hive2-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <jdbc-url>jdbc:hive2://nightly-unsecure-1.gce.cloudera.com:10000/default</jdbc-url>
                <script>${wf:appPath()}/hive-ee32.sql</script>
            </hive2>
            <ok to="join-508b"/>
            <error to="Kill"/>
        </action>
        <action name="hive-97a4" cred="hcat">
            <hive xmlns="uri:oozie:hive-action:0.2">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                  <job-xml>test.xml</job-xml>
                <script>test.sql</script>
            </hive>
            <ok to="streaming-5fab"/>
            <error to="Kill"/>
        </action>
        <fork name="fork-b429">
            <path start="hive-97a4" />
            <path start="pig-2bcf" />
        </fork>
        <join name="join-508b" to="spark-017b"/>
        <action name="hive2-d643" cred="hive2">
            <hive2 xmlns="uri:oozie:hive2-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <jdbc-url>jdbc:hive2://nightly-unsecure-1.gce.cloudera.com:10000/default</jdbc-url>
                <script>test.sql</script>
            </hive2>
            <ok to="decision-aac9"/>
            <error to="Kill"/>
        </action>
        <action name="impala-58ee">
            <shell xmlns="uri:oozie:shell-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <exec>impala-58ee.sh</exec>
                <file>impala-58ee.sh#impala-58ee.sh</file>
                <file>test.impala#test.impala</file>
            </shell>
            <ok to="join-508b"/>
            <error to="Kill"/>
        </action>
        <decision name="decision-aac9">
            <switch>
                <case to="hive-ee32">
                  ${ 1 gt 0 }
                </case>
                <case to="impala-58ee">
                  ${ 1 gt 0 }
                </case>
                <default to="join-508b"/>
            </switch>
        </decision>
        <action name="pig-2bcf">
            <pig>
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <script>test.pig</script>
            </pig>
            <ok to="hive2-d643"/>
            <error to="Kill"/>
        </action>
        <action name="spark-d71c">
            <spark xmlns="uri:oozie:spark-action:0.2">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <master>yarn</master>
                <mode>client</mode>
                <name>MySpark</name>
                <jar>/user/admin/test.jar</jar>
                <file>test.spark#test.spark</file>
            </spark>
            <ok to="mapreduce-3787"/>
            <error to="Kill"/>
        </action>
        <action name="spark-017b">
            <spark xmlns="uri:oozie:spark-action:0.2">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <master>yarn</master>
                <mode>client</mode>
                <name>MySpark</name>
                <jar>/user/admin/test.jar</jar>
                <file>test.spark#test.spark</file>
            </spark>
            <ok to="fork-1576"/>
            <error to="Kill"/>
        </action>
        <action name="sqoop-c419">
            <sqoop xmlns="uri:oozie:sqoop-action:0.2">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <command>import  --connect jdbc:hsqldb:file:db.hsqldb --table TT --target-dir hdfs://localhost:8020/user/foo -m 1</command>
            </sqoop>
            <ok to="join-ebde"/>
            <error to="Kill"/>
        </action>
        <action name="mapreduce-3787">
            <map-reduce>
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
            </map-reduce>
            <ok to="join-508b"/>
            <error to="Kill"/>
        </action>
        <action name="shell-1c31">
            <shell xmlns="uri:oozie:shell-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <exec>ls</exec>
                  <capture-output/>
            </shell>
            <ok to="join-ebde"/>
            <error to="Kill"/>
        </action>
        <fork name="fork-1576">
            <path start="sqoop-c419" />
            <path start="shell-1c31" />
        </fork>
        <join name="join-ebde" to="End"/>
        <action name="ssh-8ab6">
            <ssh xmlns="uri:oozie:ssh-action:0.1">
                <host>user@host.com</host>
                <command>ls</command>
                <capture-output/>
            </ssh>
            <ok to="spark-d71c"/>
            <error to="Kill"/>
        </action>
        <action name="email-d815">
            <email xmlns="uri:oozie:email-action:0.2">
                <to>test</to>
                <subject>test</subject>
                <body>test</body>
                <content_type>text/plain</content_type>
            </email>
            <ok to="ssh-8ab6"/>
            <error to="Kill"/>
        </action>
        <action name="streaming-5fab">
            <map-reduce>
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                <streaming>
                    <mapper>test</mapper>
                    <reducer>test</reducer>
                </streaming>
            </map-reduce>
            <ok to="distcp-daa7"/>
            <error to="Kill"/>
        </action>
        <action name="distcp-daa7">
            <distcp xmlns="uri:oozie:distcp-action:0.1">
                <job-tracker>${jobTracker}</job-tracker>
                <name-node>${nameNode}</name-node>
                  <arg>test</arg>
                  <arg>test</arg>
            </distcp>
            <ok to="email-d815"/>
            <error to="Kill"/>
        </action>
        <end name="End"/>
    </workflow-app>
    """

    self.wf.definition = common_wf_definition % 0.4
    workflow_data_04 = Workflow.gen_workflow_data_from_xml(self.user, self.wf)

    self.wf.definition = common_wf_definition % 0.3
    workflow_data_03 = Workflow.gen_workflow_data_from_xml(self.user, self.wf)

    self.wf.definition = common_wf_definition % 0.2
    workflow_data_02 = Workflow.gen_workflow_data_from_xml(self.user, self.wf)

    self.wf.definition = common_wf_definition % 0.1
    workflow_data_01 = Workflow.gen_workflow_data_from_xml(self.user, self.wf)

    assert_true(len(workflow_data_01['layout'][0]['rows']) ==
                len(workflow_data_02['layout'][0]['rows']) ==
                len(workflow_data_03['layout'][0]['rows']) ==
                len(workflow_data_04['layout'][0]['rows']) ==
                10)
    assert_true(len(workflow_data_01['workflow']['nodes']) ==
                len(workflow_data_02['workflow']['nodes']) ==
                len(workflow_data_03['workflow']['nodes']) ==
                len(workflow_data_04['workflow']['nodes']) ==
                22)
    assert_true(workflow_data_01['layout'][0]['rows'][5]['widgets'][0]['widgetType'] ==
                workflow_data_02['layout'][0]['rows'][5]['widgets'][0]['widgetType'] ==
                workflow_data_03['layout'][0]['rows'][5]['widgets'][0]['widgetType'] ==
                workflow_data_04['layout'][0]['rows'][5]['widgets'][0]['widgetType'] ==
                'fork-widget')
    assert_true(workflow_data_01['workflow']['nodes'][7]['type'] ==
                workflow_data_02['workflow']['nodes'][7]['type'] ==
                workflow_data_03['workflow']['nodes'][7]['type'] ==
                workflow_data_04['workflow']['nodes'][7]['type'] ==
                'hive-widget')
    assert_true(len(workflow_data_01['workflow']['nodes'][7]['children']) ==
                len(workflow_data_02['workflow']['nodes'][7]['children']) ==
                len(workflow_data_03['workflow']['nodes'][7]['children']) ==
                len(workflow_data_04['workflow']['nodes'][7]['children']) ==
                2)

  def test_gen_workflow_data_from_xml_for_spark_schema02(self):
    self.wf.definition = """<workflow-app name="My_Workflow" xmlns="uri:oozie:workflow:0.5">
    <start to="spark-fa35"/>
    <kill name="Kill">
        <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
    </kill>
    <action name="spark-fa35">
        <spark xmlns="uri:oozie:spark-action:0.2">
            <job-tracker>${jobTracker}</job-tracker>
            <name-node>${nameNode}</name-node>
            <master>local[*]</master>
            <mode>client</mode>
            <name>MySpark</name>
            <jar>wordcount.py</jar>
            <file>/user/admin/wordcount.py#wordcount.py</file>
        </spark>
        <ok to="End"/>
        <error to="Kill"/>
    </action>
    <end name="End"/>
    </workflow-app>
    """

    workflow_data = Workflow.gen_workflow_data_from_xml(self.user, self.wf)

    assert_true(len(workflow_data['layout'][0]['rows']) == 4)
    assert_true(len(workflow_data['workflow']['nodes']) == 4)
    assert_equal(workflow_data['layout'][0]['rows'][1]['widgets'][0]['widgetType'], 'spark-widget')
    assert_true(len(workflow_data['workflow']['nodes'][1]['children']) == 2)

  def test_gen_workflow_data_for_xml_with_generic_nodes(self):
    self.wf.definition = """<workflow-app name="Test" xmlns="uri:oozie:workflow:0.5" xmlns:sla="uri:oozie:sla:0.2">
        <start to="email-0aaa"/>
        <kill name="Kill">
            <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
        </kill>
        <action name="email-0aaa">
            <generic_action xmlns="uri:oozie:email-action:0.2">
                <to>test</to>
                <subject>test</subject>
                <body>test</body>
                <content_type>text/plain</content_type>
            </generic_action>
            <ok to="End"/>
            <error to="Kill"/>
              <sla:info>
                <sla:nominal-time>${nominal_time}</sla:nominal-time>
                <sla:should-start>10</sla:should-start>
                <sla:should-end>${30 * MINUTES}</sla:should-end>
              </sla:info>
        </action>
        <end name="End"/>
    </workflow-app>
    """

    workflow_data = Workflow.gen_workflow_data_from_xml(self.user, self.wf)

    assert_true(len(workflow_data['layout'][0]['rows']) == 4)
    assert_true(len(workflow_data['workflow']['nodes']) == 4)
    assert_equal(workflow_data['layout'][0]['rows'][1]['widgets'][0]['widgetType'], 'generic-widget')
    assert_true(len(workflow_data['workflow']['nodes'][1]['children']) == 2)

  def test_gen_workflow_data_for_xml_with_multiple_generic_nodes(self):
    self.wf.definition = """<workflow-app name="Test" xmlns="uri:oozie:workflow:0.5" xmlns:sla="uri:oozie:sla:0.2">
        <start to="email-1"/>
        <kill name="Kill">
            <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
        </kill>
        <action name="email-1">
            <generic_action xmlns="uri:oozie:email-action:0.2">
                <to>test</to>
                <subject>test</subject>
                <body>test</body>
                <content_type>text/plain</content_type>
            </generic_action>
            <ok to="email-2"/>
            <error to="Kill"/>
              <sla:info>
                <sla:nominal-time>${nominal_time}</sla:nominal-time>
                <sla:should-start>10</sla:should-start>
                <sla:should-end>${30 * MINUTES}</sla:should-end>
              </sla:info>
        </action>
        <action name="email-2">
            <generic_action2 xmlns="uri:oozie:email-action:0.2">
                <to>test</to>
                <subject>test</subject>
                <body>test</body>
                <content_type>text/plain</content_type>
            </generic_action2>
            <ok to="End"/>
            <error to="Kill"/>
        </action>
        <end name="End"/>
    </workflow-app>
    """

    workflow_data = Workflow.gen_workflow_data_from_xml(self.user, self.wf)

    assert_true(len(workflow_data['layout'][0]['rows']) == 5)
    assert_true(len(workflow_data['workflow']['nodes']) == 5)
    assert_equal(workflow_data['layout'][0]['rows'][1]['widgets'][0]['widgetType'], 'generic-widget')
    assert_true(len(workflow_data['workflow']['nodes'][1]['children']) == 2)

  def test_get_hierarchy_from_adj_list_throws_exception(self):
      self.wf.definition = """<workflow-app
    name="${Payer} ${Project_Name} Sub Workflow Group7_8 ${YYYYMMDDHHMM}"
    xmlns="uri:oozie:workflow:0.5">
    <global>
    <job-tracker>${JobTracker}</job-tracker>
    <name-node>${NameNode}</name-node>
    <configuration>
      <property>
        <name>mapred.job.queue.name</name>
        <value>${QueueName}</value>
      </property>
      <property>
        <name>oozie.launcher.mapred.map.child.java.opts</name>
        <value>-Xmx2048m</value>
      </property>
      <property>
        <name>mapred.map.child.java.opts</name>
        <value>-Xmx8192m</value>
      </property>
      <property>
        <name>mapred.reduce.child.java.opts</name>
        <value>-Xmx6144m</value>
      </property>
    </configuration>
    </global>
    <start to="AAA_Check"/>
    <decision name="AAA_Check">
    <switch>
      <case to="Sqoop_AAA_Sub_WF1a">${fs:dirSize(AAA_WC_Path) eq 6 }</case>
      <case to="Sqoop_AAA_Sub_WF1b">${fs:dirSize(AAA_WC_Path) gt 0 }</case>
      <default to="BBB_Check"/>
    </switch>
    </decision>
    <action name="Sqoop_AAA_Sub_WF1a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="BBB_Check" />
    <error to="kill" />
    </action>
    <action name="Sqoop_AAA_Sub_WF1b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="BBB_Check" />
    <error to="kill" />
    </action>
    <decision name="BBB_Check">
    <switch>
      <case to="Sqoop_BBB_Sub_WF2a">${fs:dirSize(BBB_WC_Path) eq 6 }</case>
      <case to="Sqoop_BBB_Sub_WF2b">${fs:dirSize(BBB_WC_Path) gt 0 }</case>
      <default to="CCC_Check"/>
    </switch>
    </decision>
    <action name="Sqoop_BBB_Sub_WF2a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="CCC_Check" />
    <error to="kill" />
    </action>

    <action name="Sqoop_BBB_Sub_WF2b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="CCC_Check" />
    <error to="kill" />
    </action>

    <decision name="CCC_Check">
    <switch>
      <case to="Sqoop_CCC_Sub_WF3a">${fs:dirSize(CCC_WC_Path) eq 6 }</case>
      <case to="Sqoop_CCC_Sub_WF3b">${fs:dirSize(CCC_WC_Path) gt 0 }</case>
      <default to="DDD_Check"/>
    </switch>
    </decision>
    <action name="Sqoop_CCC_Sub_WF3a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="DDD_Check" />
    <error to="kill" />
    </action>
    <action name="Sqoop_CCC_Sub_WF3b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="DDD_Check" />
    <error to="kill" />
    </action>
    <decision name="DDD_Check">
    <switch>
      <case to="Sqoop_DDD_Sub_WF4a">${fs:dirSize(DDD_WC_Path) eq 6 }</case>
      <case to="Sqoop_DDD_Sub_WF4b">${fs:dirSize(DDD_WC_Path) gt 0 }</case>
      <default to="EEE_Check"/>
    </switch>
    </decision>
    <action name="Sqoop_DDD_Sub_WF4a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="EEE_Check" />
    <error to="kill" />
    </action>
    <action name="Sqoop_DDD_Sub_WF4b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="EEE_Check" />
    <error to="kill" />
    </action>
    <decision name="EEE_Check">
    <switch>
      <case to="Sqoop_EEE_Sub_WF5a">${fs:dirSize(EEE_WC_Path) eq 6 }</case>
      <case to="Sqoop_EEE_Sub_WF5b">${fs:dirSize(EEE_WC_Path) gt 0 }</case>
      <default to="FFF_Check"/>
    </switch>
    </decision>
    <action name="Sqoop_EEE_Sub_WF5a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="FFF_Check" />
    <error to="kill" />
    </action>
    <action name="Sqoop_EEE_Sub_WF5b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="FFF_Check" />
    <error to="kill" />
    </action>
    <decision name="FFF_Check">
    <switch>
      <case to="Sqoop_FFF_Sub_WF6a">${fs:dirSize(FFF_WC_Path) eq 6 }</case>
      <case to="Sqoop_FFF_Sub_WF6b">${fs:dirSize(FFF_WC_Path) gt 0 }</case>
      <default to="GGG_Check"/>
    </switch>
    </decision>
    <action name="Sqoop_FFF_Sub_WF6a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="GGG_Check" />
    <error to="kill" />
    </action>
    <action name="Sqoop_FFF_Sub_WF6b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="GGG_Check" />
    <error to="kill" />
    </action>
    <decision name="GGG_Check">
    <switch>
      <case to="Sqoop_GGG_Sub_WF7a">${fs:dirSize(GGG_WC_Path) eq 6 }</case>
      <case to="Sqoop_GGG_Sub_WF7b">${fs:dirSize(GGG_WC_Path) gt 0 }</case>
      <default to="HHH_Check"/>
    </switch>
    </decision>
    <action name="Sqoop_GGG_Sub_WF7a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="HHH_Check" />
    <error to="kill" />
    </action>
    <action name="Sqoop_GGG_Sub_WF7b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="HHH_Check" />
    <error to="kill" />
    </action>
    <decision name="HHH_Check">
    <switch>
      <case to="Sqoop_HHH_Sub_WF8a">${fs:dirSize(HHH_WC_Path) eq 6 }</case>
      <case to="Sqoop_HHH_Sub_WF8b">${fs:dirSize(HHH_WC_Path) gt 0 }</case>
      <default to="IIII_Check"/>
    </switch>
    </decision>
    <action name="Sqoop_HHH_Sub_WF8a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="IIII_Check" />
    <error to="kill" />
    </action>
    <action name="Sqoop_HHH_Sub_WF8b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="IIII_Check" />
    <error to="kill" />
    </action>
    <decision name="IIII_Check">
    <switch>
      <case to="Sqoop_IIII_Sub_WF9a">${fs:dirSize(IIII_WC_Path) eq 6 }</case>
      <case to="Sqoop_IIII_Sub_WF9b">${fs:dirSize(IIII_WC_Path) gt 0 }</case>
      <default to="JJJ_Check"/>
    </switch>
    </decision>
    <action name="Sqoop_IIII_Sub_WF9a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="JJJ_Check" />
    <error to="kill" />
    </action>
    <action name="Sqoop_IIII_Sub_WF9b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="JJJ_Check" />
    <error to="kill" />
    </action>
    <decision name="JJJ_Check">
    <switch>
      <case to="Sqoop_JJJ_Sub_WF10a">${fs:dirSize(JJJ_WC_Path) eq 6 }</case>
      <case to="Sqoop_JJJ_Sub_WF10b">${fs:dirSize(JJJ_WC_Path) gt 0 }</case>
      <default to="KKK_Check"/>
    </switch>
    </decision>
    <action name="Sqoop_JJJ_Sub_WF10a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="KKK_Check" />
    <error to="kill" />
    </action>
    <action name="Sqoop_JJJ_Sub_WF10b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="KKK_Check" />
    <error to="kill" />
    </action>
    <decision name="KKK_Check">
    <switch>
      <case to="Sqoop_KKK_Sub_WF11a">${fs:dirSize(KKK_WC_Path) eq 6 }</case>
      <case to="Sqoop_KKK_Sub_WF11b">${fs:dirSize(KKK_WC_Path) gt 0 }</case>
      <default to="LLL_Check"/>
    </switch>
    </decision>
    <action name="Sqoop_KKK_Sub_WF11a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="LLL_Check" />
    <error to="kill" />
    </action>
    <action name="Sqoop_KKK_Sub_WF11b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="LLL_Check" />
    <error to="kill" />
    </action>
    <decision name="LLL_Check">
    <switch>
      <case to="Sqoop_LLL_Sub_WF12a">${fs:dirSize(LLL_WC_Path) eq 6 }</case>
      <case to="Sqoop_LLL_Sub_WF12b">${fs:dirSize(LLL_WC_Path) gt 0 }</case>
      <default to="MMM_Check"/>
    </switch>
    </decision>
    <action name="Sqoop_LLL_Sub_WF12a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="MMM_Check" />
    <error to="kill" />
    </action>
    <action name="Sqoop_LLL_Sub_WF12b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="MMM_Check" />
    <error to="kill" />
    </action>
    <decision name="MMM_Check">
    <switch>
      <case to="Sqoop_MMM_Sub_WF13a">${fs:dirSize(MMM_WC_Path) eq 6 }</case>
      <case to="Sqoop_MMM_Sub_WF13b">${fs:dirSize(MMM_WC_Path) gt 0 }</case>
      <default to="MMMDxcd_Check"/>
    </switch>
    </decision>
    <action name="Sqoop_MMM_Sub_WF13a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="MMMDxcd_Check" />
    <error to="kill" />
    </action>
    <action name="Sqoop_MMM_Sub_WF13b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="MMMDxcd_Check" />
    <error to="kill" />
    </action>
    <decision name="MMMDxcd_Check">
    <switch>
      <case to="Sqoop_MMMDxcd_Sub_WF14a">${fs:dirSize(MMMDxcd_WC_Path) eq 6 }</case>
      <case to="Sqoop_MMMDxcd_Sub_WF14b">${fs:dirSize(MMMDxcd_WC_Path) gt 0 }</case>
      <default to="NNN_Check"/>
    </switch>
    </decision>
    <action name="Sqoop_MMMDxcd_Sub_WF14a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="NNN_Check" />
    <error to="kill" />
    </action>
    <action name="Sqoop_MMMDxcd_Sub_WF14b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="NNN_Check" />
    <error to="kill" />
    </action>
    <decision name="NNN_Check">
    <switch>
      <case to="Sqoop_NNN_Sub_WF15a">${fs:dirSize(NNN_WC_Path) eq 6 }</case>
      <case to="Sqoop_NNN_Sub_WF15b">${fs:dirSize(NNN_WC_Path) gt 0 }</case>
      <default to="VCHI_HomeHealthMedicare_Check"/>
    </switch>
    </decision>
    <action name="Sqoop_NNN_Sub_WF15a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="OOO_Check" />
    <error to="kill" />
    </action>
    <action name="Sqoop_NNN_Sub_WF15b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="OOO_Check" />
    <error to="kill" />
    </action>
    <decision name="OOO_Check">
    <switch>
      <case to="Sqoop_OOO_Sub_WF18a">${fs:dirSize(OOO_WC_Path) eq 6 }</case>
      <case to="Sqoop_OOO_Sub_WF18b">${fs:dirSize(OOO_WC_Path) gt 0 }</case>
      <default to="end"/>
    </switch>
    </decision>
    <action name="Sqoop_OOO_Sub_WF18a">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="end" />
    <error to="kill" />
    </action>
    <action name="Sqoop_OOO_Sub_WF18b">
    <sub-workflow>
    <app-path>${APP_PATH}/ABC_Sqoop_Sub_WF.xml</app-path>
    <propagate-configuration/>
      <configuration/>
    </sub-workflow>
    <ok to="end" />
    <error to="kill" />
    </action>
    <kill name="kill">
    <message>"Killed job due to error: ${wf:errorMessage(wf:lastErrorNode())}"</message>
    </kill>
    <end name="end" />
    </workflow-app>
    """
      self.node_list = generate_v2_graph_nodes(self.wf.definition)
      adj_list = _create_graph_adjaceny_list(self.node_list)
      node_hierarchy = ['start']
      assert_raises(WorkflowDepthReached, _get_hierarchy_from_adj_list, adj_list, adj_list['start']['ok_to'],
                    node_hierarchy)

class TestModelAPI(OozieMockBase):

  def setUp(self):
    super(TestModelAPI, self).setUp()
    self.wf = Workflow()

    self.client_not_me = make_logged_in_client(username="not_perm_user", groupname="default", recreate=True, is_superuser=False)
    self.user_not_me = User.objects.get(username="not_perm_user")


  def test_gen_workflow_from_document(self):
    notebook = make_notebook(name='Browse', editor_type='hive', statement='SHOW TABLES', status='ready')
    notebook_doc, save_as = _save_notebook(notebook.get_data(), self.user)

    workflow_doc = WorkflowBuilder().create_workflow(document=notebook_doc, user=self.user, managed=True)

    workflow = Workflow(document=workflow_doc, user=self.user)

    _data = workflow.get_data()
    assert_equal(len(_data['workflow']['nodes']), 4)


  def test_gen_pig_document(self):
    notebook = make_notebook(name='Browse', editor_type='pig', statement='ls', status='ready')
    notebook_doc, save_as = _save_notebook(notebook.get_data(), self.user)

    workflow_doc = WorkflowBuilder().create_workflow(document=notebook_doc, user=self.user, managed=True)

    workflow = Workflow(document=workflow_doc, user=self.user)

    _data = workflow.get_data()
    assert_equal(len(_data['workflow']['nodes']), 4)


  def test_find_all_parameters_check_validity(self):
    wf_data = Workflow.get_default_workflow()

    wf_data['properties'] = Workflow.get_properties()
    wf_data['nodes'] = [{
          u'name': u'Start',
          u'properties': {'parameters': [{'value': 'a=1'}, {'value': 'b'}, {'value': ''}, {'value':'c=d=1'}]},
          u'id': u'3f107997-04cc-8733-60a9-a4bb62cebffc',
          u'type': u'document-widget',
          u'children': [{u'to': u'33430f0f-ebfa-c3ec-f237-3e77efa03d0a'}],
          u'actionParameters': [],
        }]

    assert_equal({u'a': u'1', u'c': u'd=1'}, Workflow(data=json.dumps({'workflow': wf_data})).find_parameters())


  def test_gen_hive_xml(self):
    notebook = make_notebook(name='Browse', editor_type='hive', statement='SHOW TABLES', status='ready')
    notebook_doc, save_as = _save_notebook(notebook.get_data(), self.user)

    workflow_doc = WorkflowBuilder().create_workflow(document=notebook_doc, user=self.user, managed=True)

    workflow = Workflow(document=workflow_doc, user=self.user)
    assert_true(re.search('<script>\$\{wf:appPath\(\)}/hive\-....\.sql</script>', workflow.to_xml({'output': '/path'})))


  def test_gen_workflow_from_notebook(self):
    snippets = [
      {
         'status': 'running',
         'statement_raw': 'SHOW TABLES',
         'statement': 'SHOW TABLES',
         'type': 'hive',
         'properties': {
         },
         'database': 'default',
      },
      {
        'type': 'java',
        'status': 'running',
        'properties':  {
          'files': [],
          'class': 'org.apache.solr.hadoop.MapReduceIndexerTool',
          'app_jar': '/user/hue/app.jar',
          'arguments': [
              '--morphline-file',
              'morphline.conf',
          ],
          'archives': [],
        }
      }
    ]

    notebook = make_notebook2(name='2 actions', snippets=snippets)
    notebook_data = notebook.get_data()
    workflow_doc = WorkflowBuilder().create_notebook_workflow(notebook=notebook_data, user=self.user, managed=True)
    workflow = Workflow(document=workflow_doc, user=self.user)

    _data = workflow.get_data()

    assert_equal(len(_data['workflow']['nodes']), 5)
    assert_equal(len(re.findall('<ok to="java-', workflow.to_xml())), 1, workflow.to_xml())
    assert_equal(len(re.findall('<action name="hive-', workflow.to_xml())), 1, workflow.to_xml())
    assert_equal(len(re.findall('<action name="java-', workflow.to_xml())), 1, workflow.to_xml())
