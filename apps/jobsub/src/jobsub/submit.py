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
Handle design submission.
"""

import errno
import logging

from desktop.lib import django_mako
from desktop.lib.django_util import PopupException
import hadoop.cluster

from jobsub import conf, models
from jobsub.oozie_lib.oozie_api import get_oozie

LOG = logging.getLogger(__name__)


class Submission(object):
  """Represents one submission"""
  def __init__(self, design_obj, fs):
    self._design_obj = design_obj
    self._username = design_obj.owner.username
    self._action = design_obj.get_root_action()
    self._fs = fs
    self._job_id = None       # The oozie workflow instance id

  def __unicode__(self):
    res = "Submission for job design '%s' (id %s, owner %s)" % \
        (self._design_obj.name, self._design_obj.id, self._username)
    if self.job_id:
      res += " -- " + self.job_id
    return res

  @property
  def job_id(self):
    return self._job_id

  def _do_as(self, username, fn, *args, **kwargs):
    curr_user = self._fs.setuser(username)
    try:
      fn(*args, **kwargs)
    finally:
      self._fs.setuser(curr_user)


  def run(self):
    """
    Take care of all the actions of submitting a workflow/design.
    Returns the oozie job id if all goes well.
    """
    if self.job_id is not None:
      raise Exception("Job design already submitted (Oozie job id %s)" % (self.job_id,))

    fs_defaultfs = self._fs.fs_defaultfs
    jobtracker = hadoop.cluster.get_cluster_for_job_submission()

    try:
      wf_dir = self._get_and_create_deployment_dir()
    except Exception, ex:
      LOG.exception("Failed to access deployment directory")
      raise PopupException(message="Failed to access deployment directory",
                           detail=str(ex))

    wf_xml = self._generate_workflow_xml(fs_defaultfs)
    self._do_as(self._username, self._copy_files, wf_dir, wf_xml)
    LOG.info("Prepared deployment directory at '%s' for %s" % (wf_dir, self))

    try:
      prev = get_oozie().setuser(self._username)
      self._job_id = get_oozie().submit_workflow(
            self._fs.get_hdfs_path(wf_dir),
            properties={ 'jobTracker': jobtracker })
      LOG.info("Submitted: %s" % (self,))

      # Now we need to run it
      get_oozie().job_control(self.job_id, 'start')
      LOG.info("Started: %s" % (self,))
    finally:
      get_oozie().setuser(prev)

    return self.job_id
    

  def _copy_files(self, wf_dir, wf_xml):
    """
    Copy the files over to the deployment directory. This should run as the
    design owner.
    """
    xml_path = self._fs.join(wf_dir, 'workflow.xml')
    self._fs.create(xml_path, overwrite=True, permission=0644, data=wf_xml)
    LOG.debug("Created %s" % (xml_path,))

    # Copy the jar over
    if self._action.action_type in (models.OozieMapreduceAction.ACTION_TYPE,
                                    models.OozieJavaAction.ACTION_TYPE):
      lib_path = self._fs.join(wf_dir, 'lib')
      if self._fs.exists(lib_path):
        LOG.debug("Cleaning up old %s" % (lib_path,))
        self._fs.rmtree(lib_path)

      self._fs.mkdir(lib_path, 0755)
      LOG.debug("Created %s" % (lib_path,))

      jar = self._action.jar_path
      self._fs.copyfile(jar, self._fs.join(lib_path, self._fs.basename(jar)))


  def _generate_workflow_xml(self, namenode):
    """Return a string that is the workflow.xml of this workflow"""
    action_type = self._design_obj.root_action.action_type
    data = {
      'design': self._design_obj,
      'nameNode': namenode,
    }

    if action_type == models.OozieStreamingAction.ACTION_TYPE:
      tmpl = "workflow-streaming.xml.mako"
    elif action_type == models.OozieMapreduceAction.ACTION_TYPE:
      tmpl = "workflow-mapreduce.xml.mako"
    elif action_type == models.OozieJavaAction.ACTION_TYPE:
      tmpl = "workflow-java.xml.mako"
    return django_mako.render_to_string(tmpl, data)


  def _get_and_create_deployment_dir(self):
    """
    Return the workflow deployment directory in HDFS,
    creating it if necessary.

    May raise Exception.
    """
    path = self._get_deployment_dir()
    try:
      statbuf = self._fs.stats(path)
      if not statbuf.isDir:
        msg = "Workflow deployment path is not a directory: %s" % (path,)
        LOG.error(msg)
        raise Exception(msg)
      return path
    except IOError, ex:
      if ex.errno != errno.ENOENT:
        LOG.error("Error accessing workflow directory: %s" % (path,))
        raise ex
      self._create_deployment_dir(path)
      return path


  def _create_deployment_dir(self, path):
    # Make the REMOTE_DATA_DIR, and have it owned by hue
    data_repo = conf.REMOTE_DATA_DIR.get()
    if not self._fs.exists(data_repo):
      self._do_as(self._fs.DEFAULT_USER, self._fs.mkdir, data_repo, 01777)

    # The actual deployment dir should be 0711 owned by the user
    self._do_as(self._username, self._fs.mkdir, path, 0711)


  def _get_deployment_dir(self):
    """Return the workflow deployment directory"""
    if self._fs is None:
      raise PopupException("Failed to obtain HDFS reference. "
                           "Please check your configuration.")

    # We could have collision with usernames. But there's no good separator.
    # Hope people don't create crazy usernames.
    return self._fs.join(conf.REMOTE_DATA_DIR.get(),
                         "_%s_-design-%s" % (self._username, self._design_obj.id))


  def remove_deployment_dir(self):
    """Delete the workflow deployment directory. Does not throw."""
    try:
      path = self._get_deployment_dir()
      if self._do_as(self._username, self._fs.exists, path):
        self._do_as(self._username, self._fs.rmtree, path)
    except Exception, ex:
      LOG.warn("Failed to clean up workflow deployment directory for "
               "%s (owner %s). Caused by: %s",
               self._design_obj.name, self._design_obj.owner.username, ex)
