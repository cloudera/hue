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
"""
JobSubmission daemon.

This is run as a separate process from the main web server.
The intention is that the actual act of job submission could
be separated from the web app onto a different machine or sandbox.
Furthermore, the implementation could change.
"""
# TODO(philip):
#  - Write stdout/stderr back to HDFS.
#  - Be more resilient to failures
#  - Cache localized files locally to avoid re-downloading
#  - Support multiple filesystems.  Jar might be local to server (via, say, NFS)

import sys
import os
import tempfile
import traceback
import shutil
import subprocess
import logging
import processing
import datetime
import stat

from thrift.transport.TSocket import TServerSocket
from thrift.transport.TTransport import TBufferedTransportFactory
from thrift.protocol.TBinaryProtocol import TBinaryProtocolFactory
from thrift.server.TServer import TThreadedServer

from django.contrib.auth.models import User
from django.core import urlresolvers

from jobsubd import JobSubmissionService
from jobsubd.ttypes import SubmissionHandle, JobData, State, SubmissionError, PreFabLocalizedFiles
from jobsub.server_models import ServerSubmissionState
from jobbrowser.views import single_job
import desktop.lib.django_util
from desktop.lib import i18n
import hadoop.cluster
import hadoop.conf
from hadoop.cluster import all_mrclusters, get_all_hdfs
import jobsub.conf

LOG = logging.getLogger(__name__)

HOST = jobsub.conf.JOBSUBD_HOST.get()
PORT = jobsub.conf.JOBSUBD_PORT.get()
FS = hadoop.cluster.get_hdfs()

def coerce_exceptions(f):
  """
  Wrapper/decorator that maps all excptions
  into SubmissionErrors, which get passed
  along via Thrift.  Prevents clients from seeing
  TTransportException.
  """
  def wrapper(*args, **kwds):
    try:
      return f(*args, **kwds)
    except SubmissionError, e:
      # These are already forwardable; no need for further wrapping.
      raise
    except:
      logging.exception("Coercing to SubmissionError")
      type, instance, _ = sys.exc_info()
      raise SubmissionError(
        message=str(instance),
        detail=traceback.format_exc())
  return wrapper

def run_plan(id, plan, tmp_dir):
  PlanRunner(id, plan, tmp_dir).run()

class PlanRunner(object):
  # Map of pre-fab files
  PREFAB_LOCALIZED_FILES = {
    PreFabLocalizedFiles.STREAMING: hadoop.conf.HADOOP_STREAMING_JAR.get(),
  }

  def __init__(self, id, plan, tmp_dir):
    self.id = id
    self.plan = plan
    self.tmp_dir = tmp_dir


  def _send_notification(self, hadoop_job_ids, is_success):
    try:
      username = self.plan.user
      user = User.objects.get(username=username)
      if not user.email:
        return

      if is_success:
        result = "succeeded"
      else:
        result = "failed"
      subject = "Hadoop job %s: %s" % (result, self.plan.name)
      body = "Hadoop job '%s' has %s.\n\n" % (self.plan.name, result)

      links = [ "Job ID: %s\n%s/#launch=JobBrowser:%s\n" %
                (job_id,
                 desktop.lib.django_util.get_desktop_uri_prefix(),
                 urlresolvers.reverse(single_job, kwargs={'jobid': job_id}))
                for job_id in hadoop_job_ids ]
      body += '\n'.join(links)

      user.email_user(subject, body)
      logging.info("Sent notification email about job %d." % (self.id,))
    except Exception, ex:
      # Catch all. SMTP can throw a large variety of errors.
      logging.error("Failed to send job completion notification via e-mail to %s: %s" % (username, ex))


  def setup_logging(self):
    # Write logs out into the same stderr file that the subprocesses use.
    root_logger = logging.getLogger()
    handler = logging.StreamHandler(self.stderr)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-6s %(module)s %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

  def run(self):
    try:
      try:
        self.stdout = self.internal_file("stdout", "a")
        self.stderr = self.internal_file("stderr", "a")
        # Touch the jobs file.
        self.internal_file("jobs", "a").close()

        self.setup_logging()

        self.work_dir = os.path.join(self.tmp_dir, "work")
        os.mkdir(self.work_dir)
        os.chdir(self.work_dir)

        success = True
        
        for step in self.plan.steps:
          if step.localize_files_step is not None:
            self.run_localize_files_step(step.localize_files_step)
          elif step.bin_hadoop_step is not None:
            self.run_bin_hadoop_step(step.bin_hadoop_step)
          else:
            raise Exception("Unexpected step to run: " % repr(step))

        # TODO(philip): Copy stdout/stderr to HDFS, on request?

      except Exception:
        logging.exception("jobsubd PlanRunner saw exception.")
        success = False
        raise
    finally:
      # We've finished, update the database
      state = ServerSubmissionState.objects.get(id=self.id)
      if success:
        state.submission_state = State.SUCCESS
      else:
        state.submission_state = State.FAILURE
      state.end_time = datetime.datetime.now()
      state.save()
      logging.info("Marked jobsubd job %d as done." % self.id)
      hadoop_job_ids = self.internal_file("jobs", "r").read().splitlines()
      self._send_notification(hadoop_job_ids, success)

      # TODO(philip): Clean up tmpdir after a while?

  def run_localize_files_step(self, step):
    for x in step.localize_files:
      self.localize_file(x)

  def localize_file(self, loc_file):
    assert os.path.sep not in loc_file.target_name, "Target %s must be filename in working directory." % repr(loc_file.target_name)

    target = os.path.join(self.work_dir, loc_file.target_name)
    if loc_file.pre_fab_localized_file is not None:
      source = self.PREFAB_LOCALIZED_FILES[loc_file.pre_fab_localized_file]
      LOG.info("Linking %s->%s" % (source, target))
      os.symlink(source, target)
    elif loc_file.path_on_hdfs is not None:
      # TODO(philip): Could do caching based on checksums here.
      FS.setuser(self.plan.user)
      LOG.info("Copying %s->%s" % (loc_file.path_on_hdfs, target))
      src = FS.open(loc_file.path_on_hdfs)
      try:
        dst = file(target, "w")
        try:
          shutil.copyfileobj(src, dst)
        finally:
          dst.close()
      finally:
        src.close()

  def internal_file(self, name, options="r"):
    return file(self.internal_file_name(name), options)

  def internal_file_name(self, name):
    return os.path.join(self.tmp_dir, name)

  def run_bin_hadoop_step(self, step):
    """
    user.name is used by FileSystem.getHomeDirectory().
    The environment variables for _USER and _GROUPS are used
    by the aspectj aspect to overwrite Hadoop's notion of 
    users and groups.
    """
    java_properties = {}
    java_properties["hue.suffix"] = "-via-hue"
    java_properties["user.name"] = self.plan.user
    java_prop_str = " ".join("-D%s=%s" % (k,v) for k, v in java_properties.iteritems())
    env = {      
      'HADOOP_HOME': hadoop.conf.HADOOP_HOME.get(), 
      'HADOOP_OPTS': "-javaagent:%s %s" % (jobsub.conf.ASPECTJWEAVER.get(), java_prop_str),
      'HADOOP_CLASSPATH': ':'.join([jobsub.conf.ASPECTPATH.get(),
                                    hadoop.conf.HADOOP_EXTRA_CLASSPATH_STRING.get()]),
      'HUE_JOBTRACE_LOG': self.internal_file_name("jobs"),
      'HUE_JOBSUB_USER': self.plan.user,
      'HUE_JOBSUB_GROUPS': ",".join(self.plan.groups),
      'LANG': os.getenv('LANG', i18n.get_site_encoding()),
    }

    all_clusters = []
    all_clusters += all_mrclusters().values()
    all_clusters += get_all_hdfs().values()
    delegation_token_files = []
    merged_token_file = tempfile.NamedTemporaryFile()
    try:
      LOG.debug("all_clusters: %s" % (repr(all_clusters),))
      for cluster in all_clusters:
        if cluster.security_enabled:
          cluster.setuser(self.plan.user)
          token = cluster.get_delegation_token()
          token_file = tempfile.NamedTemporaryFile()
          token_file.write(token.delegationTokenBytes)
          token_file.flush()
          delegation_token_files.append(token_file)
  
      java_home = os.getenv('JAVA_HOME')
      if java_home:
        env["JAVA_HOME"] = java_home
      for k, v in env.iteritems():
        assert v is not None, "Environment key %s missing value." % k
  
      base_args = [ hadoop.conf.HADOOP_BIN.get() ]
      if hadoop.conf.HADOOP_CONF_DIR.get():
        base_args.append("--config")
        base_args.append(hadoop.conf.HADOOP_CONF_DIR.get())
  
      if delegation_token_files:
        args = list(base_args) # Make a copy of the base args.
        args += ['jar', hadoop.conf.CREDENTIALS_MERGER_JAR.get(), merged_token_file.name]
        args += [token_file.name for token_file in delegation_token_files]
        LOG.debug("merging credentials files with comand: '%s'" % (' '.join(args),))
        merge_pipe = subprocess.Popen(args, shell=False, close_fds=True)
        retcode = merge_pipe.wait()
        if 0 != retcode:
          raise Exception("bin/hadoop returned non-zero %d while trying to merge credentials" % (retcode,))
        env['HADOOP_TOKEN_FILE_LOCATION'] = merged_token_file.name
  
      args = list(base_args) # Make a copy of the base args.
      args += step.arguments
      LOG.info("Starting %s.  (Env: %s)", repr(args), repr(env))
      LOG.info("Running: %s" % " ".join(args))
      self.pipe = subprocess.Popen(
        args,
        stdin=None,
        cwd=self.work_dir,
        stdout=self.stdout,
        stderr=self.stderr,
        shell=False,
        close_fds=True,
        env=env)
      retcode = self.pipe.wait()
      if 0 != retcode:
        raise Exception("bin/hadoop returned non-zero %d" % retcode)
      LOG.info("bin/hadoop returned %d" % retcode)
    finally:
      for token_file in delegation_token_files + [merged_token_file]:
        token_file.close()

class JobSubmissionServiceImpl(object):
  @coerce_exceptions
  def get_job_data(self, handle):
    # TODO: Could use waitpid(pid, WNOHANG) to update the
    # state, not to mention update the state if it's no longer
    # running.

    # Look up the submission
    state = ServerSubmissionState.objects.get(id=handle.id)

    def job_file(name):
      """Helper to make a directory name."""
      return file(os.path.join(state.tmp_dir, name))

    # Handle stdout, stderr
    def tail(name):
      """Helper to find the last 10K of a file."""
      TAIL_SIZE = 10*1024 # 10KB
      try:
        f = job_file(name)
        try:
          file_size = os.stat(f.name)[stat.ST_SIZE]
          seek = max(0, file_size - TAIL_SIZE)
          f.seek(seek)
          return f.read(TAIL_SIZE)
        finally:
          f.close()
      except IOError:
        return "No longer available."

    j = JobData()
    j.stdout_tail = tail("stdout")
    j.stderr_tail = tail("stderr")
    j.state = state.submission_state
    try:
      j.hadoop_job_ids = job_file("jobs").read().splitlines()
    except IOError:
      j.hadoop_job_ids = []
    return j

  @coerce_exceptions
  def submit(self, plan):
    """
    Starts a subprocess to manage the submission, and returns quickly.
    """
    tmp_dir = tempfile.mkdtemp(dir="/tmp", prefix="jobsub-")
    state = ServerSubmissionState(submission_state=State.SUBMITTED, tmp_dir=tmp_dir)
    state.save() # Early save to get an "id"

    process = processing.Process(target=run_plan, args=(state.id, plan, tmp_dir), name=plan.name)
    process.setDaemon(True)
    process.start()

    state.pid = process.getPid()
    state.submission_state = State.RUNNING
    state.save()

    return SubmissionHandle(id=state.id)

def main():
  """
  main() loop, called from jobsubd management command.
  """
  LOG.info("Starting daemon on port %s" % PORT)
  sock = TServerSocket(PORT)
  sock.host = HOST
  TThreadedServer(JobSubmissionService.Processor(JobSubmissionServiceImpl()),
    sock,
    TBufferedTransportFactory(),
    TBinaryProtocolFactory()).serve()
