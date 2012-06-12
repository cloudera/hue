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

import errno
import logging

from desktop.lib.django_util import PopupException
from hadoop import cluster
from liboozie.oozie_api import get_oozie


LOG = logging.getLogger(__name__)


class Submission(object):
  """Represents one unique Oozie submission"""
  def __init__(self, job, fs, properties=None):
    self.job = job
    self.username = job.owner.username
    self.fs = fs
    self.oozie_id = None

    if properties is not None:
      self.properties = properties
    else:
      self.properties = {}

  def __unicode__(self):
    res = "Submission for job '%s' (id %s, owner %s)" % (self.job.name, self.job.id, self.username)
    if self.oozie_id:
      res += " -- " + self.oozie_id
    return res

  def run(self):
    """
    Take care of all the actions of submitting a Oozie workflow.
    Returns the oozie job id if all goes well.
    """
    if self.oozie_id is not None:
      raise Exception("Submission already submitted (Oozie job id %s)" % (self.oozie_id,))

    jobtracker = cluster.get_cluster_addr_for_job_submission()

    deployment_dir = self.deploy()

    try:
      prev = get_oozie().setuser(self.username )
      self._update_properties(jobtracker, deployment_dir)
      self.oozie_id = get_oozie().submit_job(self.properties)
      LOG.info("Submitted: %s" % (self,))

      if self.job.get_type() == 'workflow':
        get_oozie().job_control(self.oozie_id, 'start')
        LOG.info("Started: %s" % (self,))
    finally:
      get_oozie().setuser(prev)

    return self.oozie_id

  def deploy(self):
    try:
      deployment_dir = self._create_deployment_dir()
    except Exception, ex:
      LOG.exception("Failed to access deployment directory")
      raise PopupException(message="Failed to access deployment directory",
                           detail=str(ex))

    oozie_xml = self.job.to_xml()
    self._do_as(self.username , self._copy_files, deployment_dir, oozie_xml)

    return deployment_dir

  def _update_properties(self, jobtracker_addr, deployment_dir):
    properties = {
        'jobTracker': jobtracker_addr,
        'nameNode': self.fs.fs_defaultfs,
        self.job.get_application_path_key(): self.fs.get_hdfs_path(deployment_dir),
        'hue-id': self.job.id}
    properties.update(self.properties)
    self.properties = properties

  def _create_deployment_dir(self):
    """
    Return the job deployment directory in HDFS, creating it if necessary.
    """
    path = self.job.deployment_dir

    try:
      statbuf = self.fs.stats(path)
      if not statbuf.isDir:
        msg = "Workflow deployment path is not a directory: %s" % (path,)
        LOG.error(msg)
        raise Exception(msg)
      return path
    except IOError, ex:
      if ex.errno != errno.ENOENT:
        msg = "Error accessing workflow directory '%s': %s" % (path, ex)
        LOG.exception(msg)
        raise IOError(ex.errno, msg)
    # The actual deployment dir should be 0711 owned by the user
    if not self.fs.exists(path):
      self._do_as(self.username , self.fs.mkdir, path, 0711)
    return path

  def _copy_files(self, deployment_dir, oozie_xml):
    """
    Copy the files over to the deployment directory. This should run as the
    design owner.
    """
    xml_path = self.fs.join(deployment_dir, self.job.get_application_filename())
    self.fs.create(xml_path, overwrite=True, permission=0644, data=oozie_xml)
    LOG.debug("Created %s" % (xml_path,))

    # Copy the files over
    files = []
    if hasattr(self.job, 'nodes'):
      for node in self.job.nodes:
        if hasattr(node, 'lib_path'):
          files.append(node.jar_path)

    if files:
      lib_path = self.fs.join(deployment_dir, 'lib')
      if self.fs.exists(lib_path):
        LOG.debug("Cleaning up old %s" % (lib_path,))
        self.fs.rmtree(lib_path)

      self.fs.mkdir(lib_path, 0755)
      LOG.debug("Created %s" % (lib_path,))

      for file in files:
        self.fs.copyfile(file, self.fs.join(lib_path, self.fs.basename(file)))

  def _do_as(self, username, fn, *args, **kwargs):
    curr_user = self.fs.setuser(username)
    try:
      fn(*args, **kwargs)
    finally:
      self.fs.setuser(curr_user)

  def remove_deployment_dir(self):
    """Delete the workflow deployment directory."""
    try:
      path = self.job.deployment_dir
      if self._do_as(self.username , self.fs.exists, path):
        self._do_as(self.username , self.fs.rmtree, path)
    except Exception, ex:
      LOG.warn("Failed to clean up workflow deployment directory for "
               "%s (owner %s). Caused by: %s",
               self.job.name, self.job.owner.username, ex)
