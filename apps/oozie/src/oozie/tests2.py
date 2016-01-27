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

from django.core.urlresolvers import reverse

from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal

from oozie.conf import ENABLE_V2
from oozie.importlib.workflows import generate_v2_graph_nodes
from oozie.models2 import Workflow, find_dollar_variables, find_dollar_braced_variables, Node, _create_graph_adjaceny_list, _get_hierarchy_from_adj_list
from oozie.tests import OozieMockBase, save_temp_workflow, MockOozieApi


LOG = logging.getLogger(__name__)


class TestEditor(OozieMockBase):

  def setUp(self):
    super(TestEditor, self).setUp()
    self.wf = Workflow()


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


  def test_workflow_gen_xml(self):
    assert_equal([
        u'<workflow-app', u'name="My_Workflow"', u'xmlns="uri:oozie:workflow:0.5">', u'<start', u'to="End"/>', u'<kill', u'name="Kill">', u'<message>Action', u'failed,',
        u'error', u'message[${wf:errorMessage(wf:lastErrorNode())}]</message>', u'</kill>', u'<end', u'name="End"/>', u'</workflow-app>'],
        self.wf.to_xml({'output': '/path'}).split()
    )

  def test_workflow_map_reduce_gen_xml(self):
    wf = Workflow(data="{\"layout\": [{\"oozieRows\": [{\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"MapReduce job\", \"widgetType\": \"mapreduce-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\", \"size\": 12}], \"id\": \"e2caca14-8afc-d7e0-287c-88accd0b4253\", \"columns\": []}], \"rows\": [{\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Start\", \"widgetType\": \"start-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"size\": 12}], \"id\": \"ff63ee3f-df54-2fa3-477b-65f5e0f0632c\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"MapReduce job\", \"widgetType\": \"mapreduce-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\", \"size\": 12}], \"id\": \"e2caca14-8afc-d7e0-287c-88accd0b4253\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"End\", \"widgetType\": \"end-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"size\": 12}], \"id\": \"6a13d869-d04c-8431-6c5c-dbe67ea33889\", \"columns\": []}, {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Kill\", \"widgetType\": \"kill-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"size\": 12}], \"id\": \"e3b56553-7a4f-43d2-b1e2-4dc433280095\", \"columns\": []}], \"oozieEndRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"End\", \"widgetType\": \"end-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"size\": 12}], \"id\": \"6a13d869-d04c-8431-6c5c-dbe67ea33889\", \"columns\": []}, \"oozieKillRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Kill\", \"widgetType\": \"kill-widget\", \"oozieMovable\": true, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"size\": 12}], \"id\": \"e3b56553-7a4f-43d2-b1e2-4dc433280095\", \"columns\": []}, \"enableOozieDropOnAfter\": true, \"oozieStartRow\": {\"enableOozieDropOnBefore\": true, \"enableOozieDropOnSide\": true, \"enableOozieDrop\": false, \"widgets\": [{\"status\": \"\", \"logsURL\": \"\", \"name\": \"Start\", \"widgetType\": \"start-widget\", \"oozieMovable\": false, \"ooziePropertiesExpanded\": false, \"properties\": {}, \"isLoading\": true, \"offset\": 0, \"actionURL\": \"\", \"progress\": 0, \"klass\": \"card card-widget span12\", \"oozieExpanded\": false, \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"size\": 12}], \"id\": \"ff63ee3f-df54-2fa3-477b-65f5e0f0632c\", \"columns\": []}, \"klass\": \"card card-home card-column span12\", \"enableOozieDropOnBefore\": true, \"drops\": [\"temp\"], \"id\": \"0c1908e7-0096-46e7-a16b-b17b1142a730\", \"size\": 12}], \"workflow\": {\"properties\": {\"job_xml\": \"\", \"description\": \"\", \"wf1_id\": null, \"sla_enabled\": false, \"deployment_dir\": \"/user/hue/oozie/workspaces/hue-oozie-1430228904.58\", \"schema_version\": \"uri:oozie:workflow:0.5\", \"sla\": [{\"key\": \"enabled\", \"value\": false}, {\"key\": \"nominal-time\", \"value\": \"${nominal_time}\"}, {\"key\": \"should-start\", \"value\": \"\"}, {\"key\": \"should-end\", \"value\": \"${30 * MINUTES}\"}, {\"key\": \"max-duration\", \"value\": \"\"}, {\"key\": \"alert-events\", \"value\": \"\"}, {\"key\": \"alert-contact\", \"value\": \"\"}, {\"key\": \"notification-msg\", \"value\": \"\"}, {\"key\": \"upstream-apps\", \"value\": \"\"}], \"show_arrows\": true, \"parameters\": [{\"name\": \"oozie.use.system.libpath\", \"value\": true}], \"properties\": []}, \"name\": \"My Workflow\", \"versions\": [\"uri:oozie:workflow:0.4\", \"uri:oozie:workflow:0.4.5\", \"uri:oozie:workflow:0.5\"], \"isDirty\": true, \"movedNode\": null, \"linkMapping\": {\"0cf2d5d5-2315-0bda-bd53-0eec257e943f\": [\"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\"], \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\": [], \"3f107997-04cc-8733-60a9-a4bb62cebffc\": [\"0cf2d5d5-2315-0bda-bd53-0eec257e943f\"], \"17c9c895-5a16-7443-bb81-f34b30b21548\": []}, \"nodeIds\": [\"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\"], \"nodes\": [{\"properties\": {}, \"name\": \"Start\", \"children\": [{\"to\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\"}], \"actionParametersFetched\": false, \"type\": \"start-widget\", \"id\": \"3f107997-04cc-8733-60a9-a4bb62cebffc\", \"actionParameters\": []}, {\"properties\": {}, \"name\": \"End\", \"children\": [], \"actionParametersFetched\": false, \"type\": \"end-widget\", \"id\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\", \"actionParameters\": []}, {\"properties\": {\"message\": \"Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]\"}, \"name\": \"Kill\", \"children\": [], \"actionParametersFetched\": false, \"type\": \"kill-widget\", \"id\": \"17c9c895-5a16-7443-bb81-f34b30b21548\", \"actionParameters\": []}, {\"properties\": {\"retry_max\": [{\"value\": \"5\"}], \"files\": [], \"job_xml\": \"\", \"jar_path\": \"my_jar\", \"job_properties\": [{\"name\": \"prop_1_name\", \"value\": \"prop_1_value\"}], \"archives\": [], \"prepares\": [], \"credentials\": [], \"sla\": [{\"key\": \"enabled\", \"value\": false}, {\"key\": \"nominal-time\", \"value\": \"${nominal_time}\"}, {\"key\": \"should-start\", \"value\": \"\"}, {\"key\": \"should-end\", \"value\": \"${30 * MINUTES}\"}, {\"key\": \"max-duration\", \"value\": \"\"}, {\"key\": \"alert-events\", \"value\": \"\"}, {\"key\": \"alert-contact\", \"value\": \"\"}, {\"key\": \"notification-msg\", \"value\": \"\"}, {\"key\": \"upstream-apps\", \"value\": \"\"}]}, \"name\": \"mapreduce-0cf2\", \"children\": [{\"to\": \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\"}, {\"error\": \"17c9c895-5a16-7443-bb81-f34b30b21548\"}], \"actionParametersFetched\": false, \"type\": \"mapreduce-widget\", \"id\": \"0cf2d5d5-2315-0bda-bd53-0eec257e943f\", \"actionParameters\": []}], \"id\": 50019, \"nodeNamesMapping\": {\"0cf2d5d5-2315-0bda-bd53-0eec257e943f\": \"mapreduce-0cf2\", \"33430f0f-ebfa-c3ec-f237-3e77efa03d0a\": \"End\", \"3f107997-04cc-8733-60a9-a4bb62cebffc\": \"Start\", \"17c9c895-5a16-7443-bb81-f34b30b21548\": \"Kill\"}, \"uuid\": \"084f4d4c-00f1-62d2-e27e-e153c1f9acfb\"}}")

    assert_equal([
        u'<workflow-app', u'name="My_Workflow"', u'xmlns="uri:oozie:workflow:0.5">',
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
        u'<workflow-app', u'name="My_Workflow"', u'xmlns="uri:oozie:workflow:0.5">',
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
        u'<workflow-app', u'name="My_Workflow_3"', u'xmlns="uri:oozie:workflow:0.5">',
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
        u'<workflow-app', u'name="My_real_Workflow_1"', u'xmlns="uri:oozie:workflow:0.5">',
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

  def test_workflow_email_gen_xml(self):
    self.maxDiff = None
    workflow = """{"history": {"oozie_id": "0000013-151015155856463-oozie-oozi-W", "properties": {"oozie.use.system.libpath": "True", "security_enabled": false, "dryrun": false, "jobTracker": "localhost:8032", "oozie.wf.application.path": "hdfs://localhost:8020/user/hue/oozie/workspaces/hue-oozie-1445431078.26", "hue-id-w": 6, "nameNode": "hdfs://localhost:8020"}}, "layout": [{"oozieRows": [], "rows": [{"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Start", "widgetType": "start-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "size": 12}], "id": "9cf57679-292c-d980-8053-1180a84eaa54", "columns": []}, {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "End", "widgetType": "end-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "size": 12}], "id": "f8f22c81-a9eb-5138-64cf-014ae588d0ca", "columns": []}, {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Kill", "widgetType": "kill-widget", "oozieMovable": true, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "size": 12}], "id": "31f194ff-cd4f-faef-652d-0c5f66a80f97", "columns": []}], "oozieEndRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "End", "widgetType": "end-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "size": 12}], "id": "f8f22c81-a9eb-5138-64cf-014ae588d0ca", "columns": []}, "oozieKillRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Kill", "widgetType": "kill-widget", "oozieMovable": true, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "size": 12}], "id": "31f194ff-cd4f-faef-652d-0c5f66a80f97", "columns": []}, "enableOozieDropOnAfter": true, "oozieStartRow": {"enableOozieDropOnBefore": true, "enableOozieDropOnSide": true, "enableOozieDrop": false, "widgets": [{"status": "", "logsURL": "", "name": "Start", "widgetType": "start-widget", "oozieMovable": false, "ooziePropertiesExpanded": false, "properties": {}, "isLoading": true, "offset": 0, "actionURL": "", "progress": 0, "klass": "card card-widget span12", "oozieExpanded": false, "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "size": 12}], "id": "9cf57679-292c-d980-8053-1180a84eaa54", "columns": []}, "klass": "card card-home card-column span12", "enableOozieDropOnBefore": true, "drops": ["temp"], "id": "1920900a-a735-7e66-61d4-23de384e8f62", "size": 12}], "workflow": {"properties": {"job_xml": "", "description": "", "wf1_id": null, "sla_enabled": false, "deployment_dir": "/user/hue/oozie/workspaces/hue-oozie-1445431078.26", "schema_version": "uri:oozie:workflow:0.5", "properties": [], "show_arrows": true, "parameters": [{"name": "oozie.use.system.libpath", "value": true}], "sla": [{"value": false, "key": "enabled"}, {"value": "${nominal_time}", "key": "nominal-time"}, {"value": "", "key": "should-start"}, {"value": "${30 * MINUTES}", "key": "should-end"}, {"value": "", "key": "max-duration"}, {"value": "", "key": "alert-events"}, {"value": "", "key": "alert-contact"}, {"value": "", "key": "notification-msg"}, {"value": "", "key": "upstream-apps"}]}, "name": "My real Workflow 1", "versions": ["uri:oozie:workflow:0.4", "uri:oozie:workflow:0.4.5", "uri:oozie:workflow:0.5"], "isDirty": false, "movedNode": null, "linkMapping": {"33430f0f-ebfa-c3ec-f237-3e77efa03d0a": [], "3f107997-04cc-8733-60a9-a4bb62cebffc": ["33430f0f-ebfa-c3ec-f237-3e77efa03d0a"], "17c9c895-5a16-7443-bb81-f34b30b21548": []}, "nodeIds": ["3f107997-04cc-8733-60a9-a4bb62cebffc", "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "17c9c895-5a16-7443-bb81-f34b30b21548"], "nodes": [{"properties": {}, "name": "Start", "children": [{"to": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a"}], "actionParametersFetched": false, "type": "start-widget", "id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "actionParameters": []}, {"properties": {}, "name": "End", "children": [], "actionParametersFetched": false, "type": "end-widget", "id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "actionParameters": []}, {"properties": {"body": "This\\n\\ncontains\\n\\n\\nnew lines.", "bcc": "example@bcc.com", "content_type": "text/plain", "cc": "", "to": "hue@gethue.com", "enableMail": true, "message": "Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]", "subject": "Error on workflow"}, "name": "Kill", "children": [], "actionParametersFetched": false, "type": "kill-widget", "id": "17c9c895-5a16-7443-bb81-f34b30b21548", "actionParameters": []}], "id": 50020, "nodeNamesMapping": {"33430f0f-ebfa-c3ec-f237-3e77efa03d0a": "End", "3f107997-04cc-8733-60a9-a4bb62cebffc": "Start", "17c9c895-5a16-7443-bb81-f34b30b21548": "Kill"}, "uuid": "330c70c8-33fb-16e1-68fb-c42582c7d178"}}"""
    wf = Workflow(data=workflow)
    assert_equal(u'<workflow-app name="My_real_Workflow_1" xmlns="uri:oozie:workflow:0.5">\n    <start to="End"/>\n    <action name="Kill">\n        <email xmlns="uri:oozie:email-action:0.2">\n            <to>hue@gethue.com</to>\n            <subject>Error on workflow</subject>\n            <body>This\n\ncontains\n\n\nnew lines.</body>\n        </email>\n        <ok to="Kill-kill"/>\n        <error to="Kill-kill"/>\n    </action>\n    <kill name="Kill-kill">\n        <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>\n    </kill>\n    <end name="End"/>\n</workflow-app>', wf.to_xml({'output': '/path'}))

  def test_job_validate_xml_name(self):
    job = Workflow()

    job.update_name('a')
    assert_equal('a', job.validated_name)

    job.update_name('aa')
    assert_equal('aa', job.validated_name)

    job.update_name('%a')
    assert_equal('_a', job.validated_name)

    job.update_name('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaz')
    assert_equal(len('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), len(job.validated_name))

    job.update_name('My <...> 1st W$rkflow [With] (Bad) letter$')
    assert_equal('My_______1st_W$rkflow__With___Bad__lette', job.validated_name)

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
      assert_equal([{'name':'Dryrun', 'value': False}, {'name':'ls_arg', 'value': '-l'}], response.context['params_form'].initial)
    except Exception, ex:
      logging.exception(ex)
    finally:
      reset()
      wf_doc.delete()

  def test_list_bundles_page(self):
    response = self.c.get(reverse('oozie:list_editor_bundles'))
    assert_true('bundles_json' in response.context, response.context)


class TestExternalWorkflowGraph():

  def setUp(self):
    self.wf = Workflow()

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

    assert_equal(node_hierarchy, ['start', [u'fork-fe93', [[u'shell-bd90'], [u'shell-d64c'], [u'shell-5429'], [u'shell-d8cc']], u'join-7f80'], ['kill'], ['end']])

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

    workflow_data = Workflow.gen_workflow_data_from_xml('test', self.wf)

    assert_true(len(workflow_data['layout'][0]['rows']) == 6)
    assert_true(len(workflow_data['workflow']['nodes']) == 14)
    assert_equal(workflow_data['layout'][0]['rows'][1]['widgets'][0]['widgetType'], 'fork-widget')
    assert_equal(workflow_data['workflow']['nodes'][0]['name'], 'start-3f10')

  def test_gen_workflow_data_for_email(self):
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

    workflow_data = Workflow.gen_workflow_data_from_xml('test', self.wf)

    assert_true(len(workflow_data['layout'][0]['rows']) == 4)
    assert_true(len(workflow_data['workflow']['nodes']) == 4)
    assert_equal(workflow_data['layout'][0]['rows'][1]['widgets'][0]['widgetType'], 'email-widget')
    assert_equal(workflow_data['workflow']['nodes'][0]['name'], 'start-3f10')