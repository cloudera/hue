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
#
# Tests for job submission.
#
# Notable absences:
#  Test pig and streaming.
#  Explicit test of error handling.
#  Test what happens when file doesn't exist for jar submission, say.

import copy
import re
import time
import posixpath
import shutil
import os

from nose.tools import assert_true, assert_false, assert_equal, assert_raises
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from django.contrib.auth.models import User

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access

from jobsub.models import JobDesign
from jobsub.parameterization import recursive_walk, find_variables, substitute_variables

from hadoop import mini_cluster
import hadoop

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
  assert_equal(Dorig, D, "Object unexpectedly modified.")

  # Test application and replacement
  def square(x):
    return x*x

  assert_equal(dict(a=4, b=9, c=dict(d=16, e=25)), recursive_walk(square, D))

def test_find_variables():
  A = dict(one="$a", 
        two=dict(c="foo $b $$"), 
        three=["${foo}", "xxx ${foo}"])
  assert_equal(set(["a", "b", "foo"]),
    find_variables(A))

def test_substitute_variables():
  data = ["$greeting", dict(a="${where} $where")]
  assert_equal(["hi", dict(a="there there")], 
    substitute_variables(data, dict(greeting="hi", where="there")))

  data = [None, "foo", dict(a=None)]
  assert_equal(data, substitute_variables(data, dict()), "Nothing to substitute")

def test_job_design_cycle():
  """
  Tests for the "job design" CMS.
  Submission requires a cluster, so that's separate.
  """
  raise SkipTest
  c = make_logged_in_client()

  # New should give us a form.
  response = c.get("/jobsub/new/jar")
  assert_true("form" in response.context[1]) # Two templates are evaluated.
  assert_equal(1, response.content.count("<form method"))

  # Streaming also:
  response = c.get("/jobsub/new/streaming")
  assert_true("form" in response.context[1])

  # Post back to create a new submission
  response = c.post("/jobsub/new/jar", 
    dict(name="test1", description="descr", jarfile="myfile", arguments="x y z", submit="Save"))
  job_id = response.context["saved"]
  assert_true(job_id)

  # Follow it
  edit_url = "/jobsub/edit/%d" % job_id
  response = c.get(edit_url)
  # Make sure we've seen our changes
  assert_true("x y z" in response.content)
  # Make an edit
  response = c.get(edit_url)
  assert_equal(1, response.content.count("<form method"))
  response = c.post(edit_url,
    dict(name="test1", jarfile="myfile", arguments="a b c", submit="Save"))
  assert_equal(job_id, response.context["saved"])
  assert_true("a b c" in c.get(edit_url).content)

  # Let's try save-submit
  response = c.post(edit_url, dict(name="test1", jarfile="myfile", arguments="a b c $fancy_parameter",
    save_submit="on"))
  assert_true("fancy_parameter" in response.content)

  # Add a second one, as a different user
  # Logging out and logging back in over Django's test client
  # doesn't seem to work, so we use a new client.
  c.logout()
  c = make_logged_in_client("test2", is_superuser=False)
  grant_access("test2", "test-grp", "jobsub")

  response = c.post("/jobsub/new/jar", 
    dict(name="test2", jarfile="myfile", arguments="x y z", submit="Save"))
  assert_true(response.context["saved"])
  
  # Now check list
  response = c.get("/jobsub/")
  assert_true("test1" in [ job_design.name for job_design in response.context["jobdesigns"] ])
  assert_true("test2" in [ job_design.name for job_design in response.context["jobdesigns"] ])

  # With an owner filter...
  response = c.get("/jobsub/", dict(owner="test2"))
  assert_false("test1" in [ job_design.name for job_design in response.context["jobdesigns"] ])
  assert_true("test2" in [ job_design.name for job_design in response.context["jobdesigns"] ])

  # Capture the id for later use
  id = response.context["jobdesigns"][0].id

  response = c.get("/jobsub/", dict(owner="doesnotexist"))
  assert_equal(0, len(response.context["jobdesigns"]))

  # With a name filter...
  # Create a job design without the string "test" in its name
  response = c.post("/jobsub/new/jar",
    dict(name="newjob1", jarfile="myfile", arguments="x y z", submit="Save"))
  assert_true(response.context["saved"])

  response = c.get('/jobsub/', dict(name="test"))
  assert_true('test1' in [ job_design.name for job_design in response.context['jobdesigns'] ])
  assert_true('test2' in [ job_design.name for job_design in response.context['jobdesigns'] ])
  assert_false('newjob1' in [job_design.name for job_design in response.context['jobdesigns'] ])

  # Combined filters
  response = c.get('/jobsub/', dict(owner="est2", name="tes"))
  assert_false('test1' in [ job_design.name for job_design in response.context['jobdesigns'] ])
  assert_true('test2' in [ job_design.name for job_design in response.context['jobdesigns'] ])
  assert_false('newjob1' in [job_design.name for job_design in response.context['jobdesigns'] ])

  response = c.get('/jobsub/', dict(name='doesnotexist'))
  assert_equal(0, len(response.context['jobdesigns']))

  # Let's try delete
  assert_true(JobDesign.objects.get(id=id))
  response = c.post("/jobsub/delete/%d" % id)
  assert_raises(JobDesign.DoesNotExist, JobDesign.objects.get, id=id)

  # Let's make sure we can't delete other people's designs.
  not_mine = JobDesign.objects.get(owner=User.objects.get(username="test"),name="test1")
  response = c.post("/jobsub/delete/%d" % not_mine.id)
  assert_true("Permission Denied." in response.context["error"])

def setup_cluster_fs(cluster):
  """
  Irritatingly, pi doesn't run unless /user/test exists.
  """
  cluster.fs.setuser(cluster.superuser)
  if not cluster.fs.exists("/user/test"):
    cluster.fs.mkdir("/user/test")
  cluster.fs.chown("/user/test", "test", "test")
  if not cluster.fs.exists("/tmp"):
    cluster.fs.mkdir("/tmp")
  cluster.fs.chmod("/tmp", int('777', 8))
  cluster.fs.setuser("test")
setup_cluster_fs.__test__ = False # Don't confuse nose.

@attr('requires_hadoop')
def test_job_submission():
  raise SkipTest
  JARNAME = posixpath.basename(hadoop.conf.HADOOP_EXAMPLES_JAR.get())
  c = make_logged_in_client()
  cluster = mini_cluster.shared_cluster(conf=True)
  jobsubd = in_process_jobsubd(cluster.config_dir)

  # Remember the number of pending jobs beforehand
  n_pending = c.get("/jobsub/status_bar/").context["pending_count"]

  try:
      # Create a job
      response = c.post("/jobsub/new/jar", dict(
        name="wordcount", 
        jarfile="/user/test/%s" % JARNAME,
        arguments="wordcount $input $output", submit="Save"))
      design_id = response.context["saved"]

      # Submission should get a parameterization form
      response = c.get("/jobsub/submit/%d" % design_id)
      assert_true("<form " in response.content)

      # Create home dir
      setup_cluster_fs(cluster)

      # Prepare sample data
      f = cluster.fs.open("/user/test/input", "w")
      f.write("alpha beta gamma\nepsilon zeta theta\nalpha beta\n")
      f.close()
      # We also have to upload the jar file
      src = file(hadoop.conf.HADOOP_EXAMPLES_JAR.get())
      try:
        dst = cluster.fs.open("/user/test/%s" % JARNAME, "w")
        try:
          shutil.copyfileobj(src, dst)
        finally:
	  dst.close()
      finally:
        src.close()

      # Status_bar should be at original
      assert_equal(n_pending, c.get("/jobsub/status_bar/").context["pending_count"])

      # Let's parameterize and submit
      INPUT, OUTPUT = "/user/test/input", "/user/test/output"
      response = c.post("/jobsub/submit/%d" % design_id, 
        dict(input=INPUT, output=OUTPUT))
      watch_id = parse_out_id(response)

      # Status bar at original + 1
      assert_equal(n_pending + 1, c.get("/jobsub/status_bar/").context["pending_count"])

      # Let's take a look
      response = watch_till_complete(c, watch_id)
      assert_equal(1, len(response.context["job_data"].hadoop_job_ids), 
        "Should have launched and captured exactly one Hadoop job")
      submission = Submission.objects.get(id=watch_id)
      assert_equal(["wordcount", INPUT, OUTPUT],
                   submission.submission_plan.steps[1].bin_hadoop_step.arguments[2:])

      hadoop_job_id = response.context["job_data"].hadoop_job_ids[0]

      # Status bar back to original
      assert_equal(n_pending, c.get("/jobsub/status_bar/").context["pending_count"])

      # Make sure the counts are right:
      lines = cluster.fs.open("/user/test/output/part-r-00000").read().splitlines()
      counts = {}
      for line in lines:
        word, count = line.split("\t", 2)
        count = int(count)
        counts[word] = count
      assert_equal(dict(alpha=2, beta=2, gamma=1, epsilon=1, zeta=1, theta=1), counts)

      # And check that the output file has correct permissions.
      assert_equal("test", cluster.fs.stats("/user/test/output/part-r-00000")["user"],
        "Wrong username for job output.")
      assert_equal("test", cluster.fs.stats("/user/test/output/part-r-00000")["group"],
        "Wrong groupname for job output.")

      # Just to be sure it really happened, check the Job struct
      # There's no way to get just one job (eek!)...
      job_map = dict([ (x.jobID.asString, x) for x in cluster.jt.completed_jobs().jobs ])
      this_job = job_map[hadoop_job_id]
      # Check username and group
      assert_equal("test", this_job.profile.user)

      # Let's kill the temporary directory, and make sure watch
      # output still works.  We do file deletion very explicitly,
      # because tests that might mistakenly delete your home directory
      # tend to cause unhappiness.
      server_id = Submission.objects.get(id=watch_id).submission_handle.id
      tmp_dir = ServerSubmissionState.objects.get(id=server_id).tmp_dir
      for filename in ("jobs", "stderr", "stdout", os.path.join("work", "tmp.jar")):
        os.remove(os.path.join(tmp_dir, filename))
      os.rmdir(os.path.join(tmp_dir, "work"))
      os.rmdir(tmp_dir)
      response = c.get("/jobsub/watch/%d" % watch_id)
      assert_true("No longer available" in response.content)
  finally:
    cluster.shutdown()
    jobsubd.exit()
    
@attr('requires_hadoop')
def test_jobsub_setup_and_samples():
  """
  Merely exercises jobsub_setup, and then runs
  all the examples.
  """
  raise SkipTest
  cluster = mini_cluster.shared_cluster(conf=True)
  jobsubd = in_process_jobsubd(cluster.config_dir)
  try:
    c = make_logged_in_client()

    # Create a job, to make sure that it sticks around
    response = c.post("/jobsub/new/jar", dict(
      name="should_stick_around", 
      jarfile="foo",
      arguments="foo", submit="Save"))
    design_id = response.context["saved"]

    import jobsub.management.commands.jobsub_setup as jobsub_setup
    if not jobsub_setup.Command().has_been_setup():
      jobsub_setup.Command().handle()

    # Make sure we have three job designs now.
    assert_equal(3, JobDesign.objects.filter(name__startswith="Example: ").count())

    # Make sure "should_stick_around" is still there
    assert_equal(1, JobDesign.objects.filter(name="should_stick_around").count())

    # Make sure sample user got created.
    assert_equal(1, User.objects.filter(username="sample").count())
    assert_equal(1, User.objects.filter(username="test").count())

    # And now submit and run the samples
    # pi Example
    # Irritatingly, /user/test needs to exist first
    setup_cluster_fs(cluster)
    id = JobDesign.objects.get(name__contains="Example: Pi").id
    response = c.get("/jobsub/submit/%d" % id)
    assert_true("Iterations per mapper" in response.content)
    assert_true("Num of mappers" in response.content)
    response = c.post("/jobsub/submit/%d" % id, dict(
      iterations_per_mapper=10,
      num_of_mappers=1))
    response = watch_till_complete(c, parse_out_id(response))

    assert_true("Estimated value of Pi is" in response.context["job_data"].stdout_tail)
    assert_true("bin/hadoop returned 0" in response.content)

    # Wordcount example
    id = JobDesign.objects.get(name__contains="Example: Streaming Wordcount").id
    response = c.get("/jobsub/submit/%d" % id)
    response = c.post("/jobsub/submit/%d" % id, dict(
      output="/user/test/jobsub-streaming-test"))
    response = watch_till_complete(c, parse_out_id(response))

    assert_true("streaming.StreamJob: Job complete:" in response.context["job_data"].stderr_tail)
    assert_true(cluster.fs.exists("/user/test/jobsub-streaming-test/part-00000"))

    # Not running sleep example, since it adds little.
  finally:
    jobsubd.exit()
    cluster.shutdown()

def watch_till_complete(client, watch_id, timeout_sec=60):
  """
  Watches a certain job until it completes.
  Returns response when response.context["completed"] is true.
  """
  location = "/jobsub/watch/%d" % watch_id
  response = client.get(location)
  start = time.time()
  while not response.context["completed"]:
    assert_true(time.time() - start < timeout_sec,
                "Should take less than %s seconds to complete job." % (timeout_sec,))
    time.sleep(1.0)
    response = client.get(location)
  return response

def parse_out_id(response):
  """
  Extracts first integer grouping from response["Location"]

  HttpRedirectResponses tend to have ids stuck in them
  that are useful for continuing the test.
  """
  return int(re.match("^http://testserver/.*(\d+).*", response["Location"]).groups()[0])
