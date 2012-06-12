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

from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal
from django.core.urlresolvers import reverse

from desktop.lib.django_test_util import make_logged_in_client

from oozie.models import Workflow, Node, Job, Coordinator, Fork
from oozie import conf
from desktop.lib.test_utils import grant_access


def test_find_paramters():
  jobs = [Job(name="$a"),
          Job(name="foo $b $$"),
          Job(name="${foo}", description="xxx ${foo}")]

  result = [job.find_parameters(['name', 'description']) for job in jobs]
  assert_equal(set(["a", "b", "foo"]), reduce(lambda x, y: x | set(y), result, set()))


def test_create_workflow():
  create_workflow()


def test_move_up():
  c = make_logged_in_client()

  Workflow.objects.all().delete()
  wf = create_workflow()

  # 1
  # 2
  # 3
  action1 = Node.objects.get(name='action-name-1')
  action2 = Node.objects.get(name='action-name-2')
  action3 = Node.objects.get(name='action-name-3')

  # 1 2 3
  move_up(c, wf, action2)
  move_up(c, wf, action3)

  # 1 2
  # 3
  move_up(c, wf, action1)
  move_up(c, wf, action2)

  # 1
  # 2
  # 3
  move_up(c, wf, action2)

  # 1 2
  #  3
  action4 = add_action(wf.id, action2.id, 'name-4')
  move_up(c, wf, action4)

  # 1 2 3 4


def test_move_down():
  c = make_logged_in_client()

  Workflow.objects.all().delete()
  wf = create_workflow()

  action1 = Node.objects.get(name='action-name-1')
  action2 = Node.objects.get(name='action-name-2')
  action3 = Node.objects.get(name='action-name-3')

  # 1
  # 2
  # 3
  move_down(c, wf, action1)
  move_down(c, wf, action2)

  # 1
  # 2
  # 3
  move_down(c, wf, action2)
  move_down(c, wf, action1)

  # 1 2 3
  move_down(c, wf, action3)
  move_down(c, wf, action2)

  # 1
  # 2 3
  action4 = add_action(wf.id, action2.id, 'name-4')

  #  1
  # 2 3
  # 4
  move_down(c, wf, action4)
  move_down(c, wf, action3)
  move_down(c, wf, action4)

  # 1
  # 2
  # 3
  # 4


def test_decision_node():
  c = make_logged_in_client()

  Workflow.objects.all().delete()
  wf = create_workflow()

  action1 = Node.objects.get(name='action-name-1')
  action2 = Node.objects.get(name='action-name-2')

  move_down(c, wf, action1)
  fork = action1.get_parent()

  # 1 2
  #  3
  reponse = c.get(reverse('oozie:edit_workflow_fork', args=[fork.id]), {}, follow=True)
  assert_equal(200, reponse.status_code)

  assert_false(fork.has_decisions())

  reponse = c.post(reverse('oozie:edit_workflow_fork', args=[fork.id]), {
      u'form-MAX_NUM_FORMS': [u'0'], u'form-TOTAL_FORMS': [u'2'], u'form-INITIAL_FORMS': [u'2'],
      u'form-0-comment': [u'output'], u'form-0-id': [action1.id],
      u'form-1-comment': [u'output'], u'form-1-id': [action2.id],
      u'child': [wf.end.id]}, follow=True)
  assert_equal(200, reponse.status_code)

  #assert_equal(Fork.ACTION_DECISION_TYPE, fork.node_type)
  #assert_true(fork.has_decisions(), reponse.content)


def test_workflow_gen_xml():
  Workflow.objects.all().delete()
  wf = create_workflow()

  assert_equal(
      '<workflow-app name="wf-name-1" xmlns="uri:oozie:workflow:0.2">\n'
      '    <start to="action-name-1"/>\n'
      '    <action name="action-name-1">\n'
      '        <map-reduce>\n'
      '           <job-tracker>${jobTracker}</job-tracker>\n'
      '            <name-node>${nameNode}</name-node>\n'
      '        </map-reduce>\n'
      '        <ok to="action-name-2"/>\n'
      '        <error to="kill"/>\n'
      '    </action>\n'
      '    <action name="action-name-2">\n'
      '        <map-reduce>\n'
      '            <job-tracker>${jobTracker}</job-tracker>\n'
      '            <name-node>${nameNode}</name-node>\n'
      '        </map-reduce>\n'
      '        <ok to="action-name-3"/>\n'
      '        <error to="kill"/>\n'
      '    </action>\n'
      '    <action name="action-name-3">\n'
      '        <map-reduce>\n'
      '            <job-tracker>${jobTracker}</job-tracker>\n'
      '            <name-node>${nameNode}</name-node>\n'
      '        </map-reduce>\n'
      '        <ok to="end"/>\n'
      '        <error to="kill"/>\n'
      '    </action>\n'
      '    <kill name="kill">\n'
      '        <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>\n'
      '    </kill>\n'
      '    <end name="end"/>\n'
      '</workflow-app>'.split(), wf.to_xml().split())


def test_workflow_permissions():
  c = make_logged_in_client()

  Workflow.objects.all().delete()
  wf = create_workflow()

  response = c.get(reverse('oozie:edit_workflow', args=[wf.id]))

  # Login as someone else
  client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
  grant_access("not_me", "test", "oozie")


  # Edit
  finish = conf.SHARE_JOBS.set_for_testing(True)
  try:
    resp = client_not_me.get(reverse('oozie:edit_workflow', args=[wf.id]))
    assert_true('wf-name-1' in resp.content, resp.content)
  finally:
    finish()
  finish = conf.SHARE_JOBS.set_for_testing(False)
  try:
    resp = client_not_me.get(reverse('oozie:edit_workflow', args=[wf.id]))
    assert_false('wf-name-1' in resp.content, resp.content)
  finally:
    finish()

  # Share
  wf.is_shared = True
  wf.save()
  finish = conf.SHARE_JOBS.set_for_testing(True)
  try:
    resp = client_not_me.get(reverse('oozie:edit_workflow', args=[wf.id]))
    assert_true('wf-name-1' in resp.content, resp.content)
  finally:
    finish()

  # Delete
  finish = conf.SHARE_JOBS.set_for_testing(False)
  try:
    resp = client_not_me.post(reverse('oozie:delete_workflow', args=[wf.id]))
    assert_true('Permission denied' in resp.content, resp.content)
  finally:
    finish()

  response = c.post(reverse('oozie:delete_workflow', args=[wf.id]), follow=True)
  assert_equal(200, response.status_code)


# test multi fork
# test submit wf


def test_coordinator_gen_xml():
  Workflow.objects.all().delete()
  Coordinator.objects.all().delete()

  wf = create_workflow()
  coord = create_coordinator(wf)

  assert_equal(
      '<coordinator-app name="MyCoord"\n'
      '  frequency="${coord:days(1)}"\n'
      '  start="2012-07-01T00:00Z" end="2012-07-04T00:00Z" timezone="America/Los_Angeles"\n'
      '  xmlns="uri:oozie:coordinator:0.1">\n'
      '  <!--\n'
      '  <controls>\n'
      '    <timeout>[TIME_PERIOD]</timeout>\n'
      '    <concurrency>[CONCURRENCY]</concurrency>\n'
      '    <execution>[EXECUTION_STRATEGY]</execution>\n'
      '  </controls>\n'
      '  -->\n'
      '  <action>\n'
      '    <workflow>\n'
      '      <app-path>${wf_application_path}</app-path>\n'
      '      <configuration>\n'
      '     </configuration>\n'
      '   </workflow>\n'
      '  </action>\n'
      '</coordinator-app>\n'.split(), coord.to_xml().split())


def add_action(workflow, action, name):
  c = make_logged_in_client()

  response = c.post("/oozie/new_action/%s/%s/%s" % (workflow, 'mapreduce', action), {
     u'files': [u'[]'], u'name': [name], u'jar_path': [u'/tmp/.file.jar'], u'job_properties': [u'[]'], u'archives': [u'[]'], u'description': [u'']})
  assert_true(Node.objects.filter(name=name).exists(), response)
  return Node.objects.get(name=name)


def create_workflow():
  c = make_logged_in_client()

  workflow_count = Workflow.objects.count()
  response = c.get(reverse('oozie:create_workflow'))
  assert_equal(workflow_count, Workflow.objects.count(), response)

  response = c.post(reverse('oozie:create_workflow'), {u'deployment_dir': [u''], u'name': [u'wf-name-1'], u'description': [u'']})
  assert_equal(workflow_count + 1, Workflow.objects.count(), response)

  wf = Workflow.objects.get()
  assert_not_equal('', wf.deployment_dir)

  action1 = add_action(wf.id, wf.start.id, 'action-name-1')
  action2 = add_action(wf.id, action1.id, 'action-name-2')
  action3 = add_action(wf.id, action2.id, 'action-name-3')

  return wf


def create_coordinator(workflow):
  c = make_logged_in_client()

  coord_count = Coordinator.objects.count()
  response = c.get(reverse('oozie:create_coordinator'))
  assert_equal(coord_count, Coordinator.objects.count(), response)

  response = c.post(reverse('oozie:create_coordinator'), {u'end': [u'2012-07-04 00:00:00'], u'name': [u'MyCoord'], u'frequency_number': [u'1'], u'workflow': [workflow.id], u'frequency_unit': [u'days'], u'start': [u'2012-07-01 00:00:00'], u'timezone': [u'America/Los_Angeles'], u'description': [u'']})
  assert_equal(coord_count + 1, Coordinator.objects.count(), response)

  return Coordinator.objects.get()


def move(c, wf, direction, action):
  try:
    print wf.get_hierarchy()
    print direction, action
    assert_equal(200, c.post(reverse(direction, args=[action.id]), {}, follow=True).status_code)
  except:
    raise


def move_up(c, wf, action):
  move(c, wf, 'oozie:move_up_action', action)


def move_down(c, wf, action):
  move(c, wf, 'oozie:move_down_action', action)

