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
import time

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from hadoop import cluster
from hadoop.fs.hadoopfs import Hdfs
from liboozie.oozie_api import get_oozie

from liboozie.conf import REMOTE_DEPLOYMENT_DIR


LOG = logging.getLogger(__name__)


class Submission(object):
  """
  Represents one unique Oozie submission.

  Actions are:
  - submit
  - rerun
  """
  def __init__(self, user, job=None, fs=None, properties=None, oozie_id=None):
    self.job = job
    self.user = user
    self.fs = fs
    self.oozie_id = oozie_id

    if properties is not None:
      self.properties = properties
    else:
      self.properties = {}

  def __str__(self):
    if self.oozie_id:
      res = "Submission for job '%s'." % (self.oozie_id,)
    else:
      res = "Submission for job '%s' (id %s, owner %s)." % (self.job.name, self.job.id, self.user)
    if self.oozie_id:
      res += " -- " + self.oozie_id
    return res

  def run(self):
    """
    Take care of all the actions of submitting a Oozie workflow.
    Returns the oozie job id if all goes well.
    """
    if self.oozie_id is not None:
      raise Exception(_("Submission already submitted (Oozie job id %s)") % (self.oozie_id,))

    jobtracker = cluster.get_cluster_addr_for_job_submission()

    deployment_dir = self.deploy()

    try:
      prev = get_oozie().setuser(self.user.username)
      self._update_properties(jobtracker, deployment_dir)
      self.oozie_id = get_oozie().submit_job(self.properties)
      LOG.info("Submitted: %s" % (self,))

      if self.job.get_type() == 'workflow':
        get_oozie().job_control(self.oozie_id, 'start')
        LOG.info("Started: %s" % (self,))
    finally:
      get_oozie().setuser(prev)

    return self.oozie_id

  def rerun(self, deployment_dir, fail_nodes=None, skip_nodes=None):
    jobtracker = cluster.get_cluster_addr_for_job_submission()

    try:
      prev = get_oozie().setuser(self.user.username)
      self._update_properties(jobtracker, deployment_dir)
      self.properties.update({'oozie.wf.application.path': deployment_dir})

      if fail_nodes:
        self.properties.update({'oozie.wf.rerun.failnodes': fail_nodes})
      elif not skip_nodes:
        self.properties.update({'oozie.wf.rerun.failnodes': 'false'}) # Case empty 'skip_nodes' list
      else:
        self.properties.update({'oozie.wf.rerun.skip.nodes': skip_nodes})

      get_oozie().rerun(self.oozie_id, properties=self.properties)

      LOG.info("Rerun: %s" % (self,))
    finally:
      get_oozie().setuser(prev)

    return self.oozie_id


  def rerun_coord(self, deployment_dir, params):
    jobtracker = cluster.get_cluster_addr_for_job_submission()

    try:
      prev = get_oozie().setuser(self.user.username)
      self._update_properties(jobtracker, deployment_dir)
      self.properties.update({'oozie.coord.application.path': deployment_dir})

      get_oozie().job_control(self.oozie_id, action='coord-rerun', properties=self.properties, parameters=params)
      LOG.info("Rerun: %s" % (self,))
    finally:
      get_oozie().setuser(prev)

    return self.oozie_id


  def rerun_bundle(self, deployment_dir, params):
    jobtracker = cluster.get_cluster_addr_for_job_submission()

    try:
      prev = get_oozie().setuser(self.user.username)
      self._update_properties(jobtracker, deployment_dir)
      self.properties.update({'oozie.bundle.application.path': deployment_dir})
      get_oozie().job_control(self.oozie_id, action='bundle-rerun', properties=self.properties, parameters=params)
      LOG.info("Rerun: %s" % (self,))
    finally:
      get_oozie().setuser(prev)

    return self.oozie_id


  def deploy(self):
    try:
      deployment_dir = self._create_deployment_dir()
    except Exception, ex:
      msg = _("Failed to access deployment directory.")
      LOG.exception(msg)
      raise PopupException(message=msg, detail=str(ex))

    oozie_xml = self.job.to_xml(self.properties)
    self._do_as(self.user.username , self._copy_files, deployment_dir, oozie_xml)

    if hasattr(self.job, 'actions'):
      for action in self.job.actions:
        # Make sure XML is there
        # Don't support shared sub-worfklow
        if action.node_type == 'subworkflow':
          node = action.get_full_node()
          sub_deploy = Submission(self.user, node.sub_workflow, self.fs, self.properties)
          sub_deploy.deploy()

    return deployment_dir

  def _update_properties(self, jobtracker_addr, deployment_dir):
    properties = {
      'jobTracker': jobtracker_addr,
      'nameNode': self.fs.fs_defaultfs,
    }

    if self.job:
      properties.update({
        self.job.get_application_path_key(): self.fs.get_hdfs_path(deployment_dir),
        self.job.HUE_ID: self.job.id
      })

    properties.update(self.properties)

    self.properties = properties

  def _create_deployment_dir(self):
    """
    Return the job deployment directory in HDFS, creating it if necessary.
    The actual deployment dir should be 0711 owned by the user
    """
    if self.user != self.job.owner:
      path = Hdfs.join(REMOTE_DEPLOYMENT_DIR.get(), '_%s_-oozie-%s-%s' % (self.user.username, self.job.id, time.time()))
      self.fs.copy_remote_dir(self.job.deployment_dir, path, owner=self.user, dir_mode=0711)
    else:
      path = self.job.deployment_dir
      self._create_dir(path)
    return path

  def _create_dir(self, path, perms=0711):
    """
    Return the directory in HDFS, creating it if necessary.
    """
    try:
      statbuf = self.fs.stats(path)
      if not statbuf.isDir:
        msg = _("Path is not a directory: %s.") % (path,)
        LOG.error(msg)
        raise Exception(msg)
    except IOError, ex:
      if ex.errno != errno.ENOENT:
        msg = _("Error accessing directory '%s': %s.") % (path, ex)
        LOG.exception(msg)
        raise IOError(ex.errno, msg)

    if not self.fs.exists(path):
      self._do_as(self.user.username , self.fs.mkdir, path, perms)

    self._do_as(self.user.username , self.fs.chmod, path, perms)

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
    if hasattr(self.job, 'node_list'):
      for node in self.job.node_list:
        if hasattr(node, 'jar_path') and node.jar_path.startswith('/'):
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
    prev_user = self.fs.user
    try:
      self.fs.setuser(username)
      return fn(*args, **kwargs)
    finally:
      self.fs.setuser(prev_user)

  def remove_deployment_dir(self):
    """Delete the workflow deployment directory."""
    try:
      path = self.job.deployment_dir
      if self._do_as(self.user.username , self.fs.exists, path):
        self._do_as(self.user.username , self.fs.rmtree, path)
    except Exception, ex:
      LOG.warn("Failed to clean up workflow deployment directory for "
               "%s (owner %s). Caused by: %s",
               self.job.name, self.user, ex)
