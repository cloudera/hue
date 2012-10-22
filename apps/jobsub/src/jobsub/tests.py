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

import copy
import logging

from nose.tools import assert_true, assert_false, assert_equal, assert_raises
from django.contrib.auth.models import User

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from liboozie.oozie_api_test import OozieServerProvider

from jobsub import conf
from jobsub.management.commands import jobsub_setup
from jobsub.models import OozieDesign, OozieMapreduceAction, OozieStreamingAction
from jobsub.parameterization import recursive_walk, find_variables, substitute_variables


LOG = logging.getLogger(__name__)


def test_recursive_walk():
  def f(_):
    f.leafs += 1
  f.leafs = 0

  # Test that we apply the function the right number of times
  recursive_walk(f, [0,1,2])
  assert_equal(3, f.leafs)
  f.leafs = 0

  recursive_walk(f, 1)
  assert_equal(1, f.leafs)
  f.leafs = 0

  D = dict(a=2, b=3, c=dict(d=4, e=5))
  Dorig = copy.deepcopy(D)
  recursive_walk(f, D)
  assert_equal(4, f.leafs)
  assert_equal(Dorig, D, 'Object unexpectedly modified.')

  # Test application and replacement
  def square(x):
    return x * x

  assert_equal(dict(a=4, b=9, c=dict(d=16, e=25)), recursive_walk(square, D))

def test_find_variables():
  A = dict(one='$a',
        two=dict(c='foo $b $$'),
        three=['${foo}', 'xxx ${foo}'])
  assert_equal(set(['a', 'b', 'foo']),
    find_variables(A))

def test_substitute_variables():
  data = ['$greeting', dict(a='${where} $where')]
  assert_equal(['hi', dict(a='there there')],
    substitute_variables(data, dict(greeting='hi', where='there')))

  data = [None, 'foo', dict(a=None)]
  assert_equal(data, substitute_variables(data, dict()), 'Nothing to substitute')

def test_job_design_cycle():
  """
  Tests for the "job design" CMS.
  Submission requires a cluster, so that's separate.
  """
  c = make_logged_in_client()

  # New should give us a form.
  response = c.get('/jobsub/new_design/java')
  assert_equal(1, response.content.count('action="/jobsub/new_design/java" method="POST"'))

  # Streaming also:
  response = c.get('/jobsub/new_design/streaming')
  assert_equal(1, response.content.count('action="/jobsub/new_design/streaming" method="POST"'))

  # Post back to create a new submission
  design_count = OozieDesign.objects.count()
  response = c.post('/jobsub/new_design/java', {
     u'wf-name': [u'name-1'],
     u'wf-description': [u'description name-1'],
     u'action-args': [u'x y z'],
     u'action-main_class': [u'MyClass'],
     u'action-jar_path': [u'myfile.jar'],
     u'action-java_opts': [u''],
     u'action-archives': [u'[]'],
     u'action-job_properties': [u'[]'],
     u'action-files': [u'[]']})
  assert_equal(design_count + 1, OozieDesign.objects.count())
  job_id = OozieDesign.objects.get(name='name-1').id

  response = c.post('/jobsub/new_design/mapreduce', {
     u'wf-name': [u'name-2'],
     u'wf-description': [u'description name-2'],
     u'action-args': [u'x y z'],
     u'action-jar_path': [u'myfile.jar'],
     u'action-archives': [u'[]'],
     u'action-job_properties': [u'[]'],
     u'action-files': [u'[]']})

  # Follow it
  edit_url = '/jobsub/edit_design/%d' % job_id
  response = c.get(edit_url)
  assert_true('x y z' in response.content, response.content)

  # Make an edit
  response = c.post(edit_url, {
     u'wf-name': [u'name-1'],
     u'wf-description': [u'description name-1'],
     u'action-args': [u'a b c'],
     u'action-main_class': [u'MyClass'],
     u'action-jar_path': [u'myfile.jar'],
     u'action-java_opts': [u''],
     u'action-archives': [u'[]'],
     u'action-job_properties': [u'[]'],
     u'action-files': [u'[]']})
  assert_true('a b c' in c.get(edit_url).content)

  # Try to post
  response = c.post('/jobsub/new_design/java',
    dict(name='test2', jarfile='myfile.jar', arguments='x y z', submit='Save'))
  assert_false('This field is required' in response)

  # Now check list
  response = c.get('/jobsub/')
  for design in OozieDesign.objects.all():
    assert_true(design.name in response.content, response.content)

  # With some filters
  response = c.get('/jobsub/', dict(name='name-1'))
  assert_true('name-1' in response.content, response.content)
  assert_false('name-2' in response.content, response.content)

  response = c.get('/jobsub/', dict(owner='doesnotexist'))
  assert_false('doesnotexist' in response.content)

  response = c.get('/jobsub/', dict(owner='test', name='name-1'))
  assert_true('name-1' in response.content, response.content)
  assert_false('name-2' in response.content, response.content)

  response = c.get('/jobsub/', dict(name="name"))
  assert_true('name-1' in response.content, response.content)
  assert_true('name-2' in response.content, response.content)
  assert_false('doesnotexist' in response.content, response.content)

  # Combined filters
  response = c.get('/jobsub/', dict(owner="test", name="name-2"))
  assert_false('name-1' in response.content, response.content)
  assert_true('name-2' in response.content, response.content)
  assert_false('doesnotexist' in response.content, response.content)

  # Try delete
  job_id = OozieDesign.objects.get(name='name-1').id
  response = c.post('/jobsub/delete_design/%d' % job_id)
  assert_raises(OozieDesign.DoesNotExist, OozieDesign.objects.get, id=job_id)

  # Let's make sure we can't delete other people's designs.
  c.logout()
  c = make_logged_in_client('test2', is_superuser=False)
  grant_access('test2', 'test-grp', 'jobsub')

  not_mine = OozieDesign.objects.get(name='name-2')
  response = c.post('/jobsub/delete_design/%d' % not_mine.id)
  assert_true('Permission denied.' in response.content, response.content)


class TestJobsubWithHadoop(OozieServerProvider):

  def setUp(self):
    OozieServerProvider.setup_class()
    self.cluster.fs.do_as_user('test', self.cluster.fs.create_home_dir, '/user/jobsub_test')
    self.cluster.fs.do_as_superuser(self.cluster.fs.chmod, '/user/jobsub_test', 0777, True)
    self.client = make_logged_in_client(username='jobsub_test')

    # Ensure access to MR folder
    self.cluster.fs.do_as_superuser(self.cluster.fs.chmod, '/tmp', 0777, recursive=True)

  def test_jobsub_setup(self):
    # User 'test' triggers the setup of the examples.
    # 'hue' home will be deleted, the examples installed in the new one
    # and 'test' will try to access them.
    self.cluster.fs.setuser('jobsub_test')

    username = 'hue'
    home_dir = '/user/%s/' % username
    finish = conf.REMOTE_DATA_DIR.set_for_testing('%s/jobsub' % home_dir)

    try:
      data_dir = conf.REMOTE_DATA_DIR.get()

      if not jobsub_setup.Command().has_been_setup():
        self.cluster.fs.setuser(self.cluster.fs.superuser)
        if self.cluster.fs.exists(home_dir):
          self.cluster.fs.rmtree(home_dir)

        jobsub_setup.Command().handle()

      self.cluster.fs.setuser('jobsub_test')
      stats = self.cluster.fs.stats(home_dir)
      assert_equal(stats['user'], username)
      assert_equal(oct(stats['mode']), '040755') #04 because is a dir

      stats = self.cluster.fs.stats(data_dir)
      assert_equal(stats['user'], username)
      assert_equal(oct(stats['mode']), '041777')

      # Only examples should have been created by 'hue'
      stats = self.cluster.fs.listdir_stats(data_dir)
      sample_stats = filter(lambda stat: stat.user == username, stats)
      assert_equal(len(sample_stats), 2)
    finally:
      finish()

  def test_jobsub_setup_and_run_samples(self):
    """
    Merely exercises jobsub_setup, and then runs the sleep example.
    """
    if not jobsub_setup.Command().has_been_setup():
      jobsub_setup.Command().handle()
    self.cluster.fs.setuser('jobsub_test')

    assert_equal(3, OozieDesign.objects.filter(owner__username='sample').count())
    assert_equal(2, OozieMapreduceAction.objects.filter(ooziedesign__owner__username='sample').count())
    assert_equal(1, OozieStreamingAction.objects.filter(ooziedesign__owner__username='sample').count())

    # Make sure sample user got created.
    assert_equal(1, User.objects.filter(username='sample').count())

    # Clone design
    assert_equal(0, OozieDesign.objects.filter(owner__username='jobsub_test').count())
    jobid = OozieDesign.objects.get(name='sleep_job', owner__username='sample').id

    self.client.post('/jobsub/clone_design/%d' % jobid)
    assert_equal(1, OozieDesign.objects.filter(owner__username='jobsub_test').count())
    jobid = OozieDesign.objects.get(owner__username='jobsub_test').id

    # And now submit and run the sleep sample
    response = self.client.post('/jobsub/submit_design/%d' % jobid, {
        'num_reduces': 1,
        'num_maps': 1,
        'map_sleep_time': 1,
        'reduce_sleep_time': 1}, follow=True)

    assert_true('PREP' in response.content or 'OK' in response.content, response.content)
    assert_true(str(jobid) in response.content)

    oozie_job_id = response.context['jobid']
    job = OozieServerProvider.wait_until_completion(oozie_job_id, timeout=120, step=1)
    logs = OozieServerProvider.oozie.get_job_log(oozie_job_id)

    assert_equal('SUCCEEDED', job.status, logs)


    # Grep
    n = OozieDesign.objects.filter(owner__username='jobsub_test').count()
    jobid = OozieDesign.objects.get(name='grep_example').id

    self.client.post('/jobsub/clone_design/%d' % jobid)
    assert_equal(n + 1, OozieDesign.objects.filter(owner__username='jobsub_test').count())
    jobid = OozieDesign.objects.get(owner__username='jobsub_test', name__contains='sleep_job').id

    # And now submit and run the sleep sample
    response = self.client.post('/jobsub/submit_design/%d' % jobid, {
        'num_reduces': 1,
        'num_maps': 1,
        'map_sleep_time': 1,
        'reduce_sleep_time': 1}, follow=True)

    assert_true('PREP' in response.content or 'DONE' in response.content, response.content)
    assert_true(str(jobid) in response.content)

    oozie_job_id = response.context['jobid']
    job = OozieServerProvider.wait_until_completion(oozie_job_id, timeout=60, step=1)
    logs = OozieServerProvider.oozie.get_job_log(oozie_job_id)

    assert_equal('SUCCEEDED', job.status, logs)
