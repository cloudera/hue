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

from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal

from oozie.models2 import Workflow, find_dollar_variables, find_dollar_braced_variables, Node


LOG = logging.getLogger(__name__)


class TestEditor():

  def setUp(self):
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
