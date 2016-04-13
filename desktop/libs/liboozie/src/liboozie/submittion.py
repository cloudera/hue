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
import os
import re
import time

from django.utils.functional import wraps
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_str
from desktop.lib.parameterization import find_variables
from hadoop import cluster
from hadoop.fs.hadoopfs import Hdfs

from liboozie.oozie_api import get_oozie
from liboozie.conf import REMOTE_DEPLOYMENT_DIR
from liboozie.credentials import Credentials

LOG = logging.getLogger(__name__)


def submit_dryrun(run_func):
  def decorate(self, deployment_dir=None):
    if self.oozie_id is not None:
      raise Exception(_("Submission already submitted (Oozie job id %s)") % (self.oozie_id,))

    jt_address = cluster.get_cluster_addr_for_job_submission()

    if deployment_dir is None:
      self._update_properties(jt_address) # Needed as we need to set some properties like Credentials before
      deployment_dir = self.deploy()

    self._update_properties(jt_address, deployment_dir)
    if self.properties.get('dryrun'):
      self.api.dryrun(self.properties)
    return run_func(self, deployment_dir)
  return wraps(run_func)(decorate)


class Submission(object):
  """
  Represents one unique Oozie submission.

  Actions are:
  - submit
  - rerun
  """
  def __init__(self, user, job=None, fs=None, jt=None, properties=None, oozie_id=None):
    self.job = job
    self.user = user
    self.fs = fs
    self.jt = jt # Deprecated with YARN, we now use logical names only for RM
    self.oozie_id = oozie_id
    self.api = get_oozie(self.user)

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

  @submit_dryrun
  def run(self, deployment_dir=None):
    """
    Take care of all the actions of submitting a Oozie workflow.
    Returns the oozie job id if all goes well.
    """

    self.oozie_id = self.api.submit_job(self.properties)
    LOG.info("Submitted: %s" % (self,))

    if self._is_workflow():
      self.api.job_control(self.oozie_id, 'start')
      LOG.info("Started: %s" % (self,))

    return self.oozie_id

  def rerun(self, deployment_dir, fail_nodes=None, skip_nodes=None):
    jt_address = cluster.get_cluster_addr_for_job_submission()

    self._update_properties(jt_address, deployment_dir)
    self.properties.update({'oozie.wf.application.path': deployment_dir})

    if fail_nodes:
      self.properties.update({'oozie.wf.rerun.failnodes': fail_nodes})
    elif not skip_nodes:
      self.properties.update({'oozie.wf.rerun.failnodes': 'false'}) # Case empty 'skip_nodes' list
    else:
      self.properties.update({'oozie.wf.rerun.skip.nodes': skip_nodes})

    self.api.rerun(self.oozie_id, properties=self.properties)

    LOG.info("Rerun: %s" % (self,))

    return self.oozie_id


  def rerun_coord(self, deployment_dir, params):
    jt_address = cluster.get_cluster_addr_for_job_submission()

    self._update_properties(jt_address, deployment_dir)
    self.properties.update({'oozie.coord.application.path': deployment_dir})

    self.api.job_control(self.oozie_id, action='coord-rerun', properties=self.properties, parameters=params)
    LOG.info("Rerun: %s" % (self,))

    return self.oozie_id


  def rerun_bundle(self, deployment_dir, params):
    jt_address = cluster.get_cluster_addr_for_job_submission()

    self._update_properties(jt_address, deployment_dir)
    self.properties.update({'oozie.bundle.application.path': deployment_dir})
    self.api.job_control(self.oozie_id, action='bundle-rerun', properties=self.properties, parameters=params)
    LOG.info("Rerun: %s" % (self,))

    return self.oozie_id


  def deploy(self):
    try:
      deployment_dir = self._create_deployment_dir()
    except Exception, ex:
      msg = _("Failed to create deployment directory: %s" % ex)
      LOG.exception(msg)
      raise PopupException(message=msg, detail=str(ex))

    if self.api.security_enabled:
      jt_address = cluster.get_cluster_addr_for_job_submission()
      self._update_properties(jt_address) # Needed for coordinator deploying workflows

    oozie_xml = self.job.to_xml(self.properties)
    self._do_as(self.user.username , self._copy_files, deployment_dir, oozie_xml)

    if hasattr(self.job, 'actions'):
      for action in self.job.actions:
        # Make sure XML is there
        # Don't support shared sub-worfklow
        if action.node_type == 'subworkflow':
          node = action.get_full_node()
          sub_deploy = Submission(self.user, node.sub_workflow, self.fs, self.jt, self.properties)
          sub_deploy.deploy()

    return deployment_dir


  def get_external_parameters(self, application_path):
    """From XML and job.properties HDFS files"""
    deployment_dir = os.path.dirname(application_path)
    xml = self.fs.do_as_user(self.user, self.fs.read, application_path, 0, 1 * 1024**2)

    properties_file = deployment_dir + '/job.properties'
    if self.fs.do_as_user(self.user, self.fs.exists, properties_file):
      properties = self.fs.do_as_user(self.user, self.fs.read, properties_file, 0, 1 * 1024**2)
    else:
      properties = None

    return self._get_external_parameters(xml, properties)

  def _get_external_parameters(self, xml, properties=None):
    from oozie.models import DATASET_FREQUENCY
    parameters = dict([(var, '') for var in find_variables(xml, include_named=False) if not self._is_coordinator() or var not in DATASET_FREQUENCY])

    if properties:
      parameters.update(dict([re.split(r'(?<!\\)=', line.strip())
                              for line in properties.split('\n') if not line.startswith('#') and len(re.split(r'(?<!\\)=', line.strip())) == 2]))
    return parameters

  def _update_properties(self, jobtracker_addr, deployment_dir=None):
    LOG.info('Using FS %s and JT %s' % (self.fs, self.jt))

    if self.jt and self.jt.logical_name:
      jobtracker_addr = self.jt.logical_name

    if self.fs.logical_name:
      fs_defaultfs = self.fs.logical_name
    else:
      fs_defaultfs = self.fs.fs_defaultfs

    self.properties.update({
      'jobTracker': jobtracker_addr,
      'nameNode': fs_defaultfs,
    })

    if self.job and deployment_dir:
      self.properties.update({
        self.job.get_application_path_key(): self.fs.get_hdfs_path(deployment_dir),
        self.job.HUE_ID: self.job.id
      })

    # Generate credentials when using security
    if self.api.security_enabled:
      credentials = Credentials()
      credentials.fetch(self.api)
      self.properties['credentials'] = credentials.get_properties()

  def _create_deployment_dir(self):
    """
    Return the job deployment directory in HDFS, creating it if necessary.
    The actual deployment dir should be 0711 owned by the user
    """
    # Automatic setup of the required directories if needed
    create_directories(self.fs)

    # Case of a shared job
    if self.user != self.job.owner:
      path = Hdfs.join(REMOTE_DEPLOYMENT_DIR.get(), '_%s_-oozie-%s-%s' % (self.user.username, self.job.id, time.time()))
      # Shared coords or bundles might not have any existing workspaces
      if self.fs.exists(self.job.deployment_dir):
        self.fs.copy_remote_dir(self.job.deployment_dir, path, owner=self.user, dir_mode=0711)
      else:
        self._create_dir(path)
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
      self._do_as(self.user.username, self.fs.mkdir, path, perms)

    self._do_as(self.user.username, self.fs.chmod, path, perms)

    return path

  def _copy_files(self, deployment_dir, oozie_xml):
    """
    Copy XML and the jar_path files from Java or MR actions to the deployment directory.
    This should run as the workflow user.
    """
    xml_path = self.fs.join(deployment_dir, self.job.get_application_filename())
    self.fs.create(xml_path, overwrite=True, permission=0644, data=smart_str(oozie_xml))
    LOG.debug("Created %s" % (xml_path,))

    # List jar files
    files = []
    lib_path = self.fs.join(deployment_dir, 'lib')
    if hasattr(self.job, 'node_list'):
      for node in self.job.node_list:
        if hasattr(node, 'jar_path') and not node.jar_path.startswith(lib_path):
          files.append(node.jar_path)

    # Copy the jar files to the workspace lib
    if files:
      for jar_file in files:
        LOG.debug("Updating %s" % jar_file)
        jar_lib_path = self.fs.join(lib_path, self.fs.basename(jar_file))
        # Refresh if needed
        if self.fs.exists(jar_lib_path):
          stat_src = self.fs.stats(jar_file)
          stat_dest = self.fs.stats(jar_lib_path)
          if stat_src.fileId != stat_dest.fileId:
            self.fs.remove(jar_lib_path, skip_trash=True)
        self.fs.copyfile(jar_file, jar_lib_path)

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

  def _is_workflow(self):
    from oozie.models import Workflow
    return Workflow.get_application_path_key() in self.properties

  def _is_coordinator(self):
    from oozie.models import Coordinator
    return Coordinator.get_application_path_key() in self.properties


def create_directories(fs, directory_list=[]):
  # If needed, create the remote home, deployment and data directories
  directories = [REMOTE_DEPLOYMENT_DIR.get()] + directory_list

  for directory in directories:
    if not fs.do_as_user(fs.DEFAULT_USER, fs.exists, directory):
      remote_home_dir = Hdfs.join('/user', fs.DEFAULT_USER)
      if directory.startswith(remote_home_dir):
        # Home is 755
        fs.do_as_user(fs.DEFAULT_USER, fs.create_home_dir, remote_home_dir)
      # Shared by all the users
      fs.do_as_user(fs.DEFAULT_USER, fs.mkdir, directory, 01777)
      fs.do_as_user(fs.DEFAULT_USER, fs.chmod, directory, 01777) # To remove after https://issues.apache.org/jira/browse/HDFS-3491
