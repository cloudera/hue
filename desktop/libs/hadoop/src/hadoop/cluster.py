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

from hadoop.fs import hadoopfs, webhdfs, LocalSubFileSystem
from hadoop.job_tracker import LiveJobTracker

from desktop.lib.paths import get_build_dir
from hadoop import conf
import os
import logging

LOG = logging.getLogger(__name__)

def _make_filesystem(identifier):
  choice = os.getenv("FB_FS")
  if choice == "testing":
    path = os.path.join(get_build_dir(), "fs")
    if not os.path.isdir(path):
      LOG.warning(
        ("Could not find fs directory: %s. Perhaps you need to run " +
        "manage.py filebrowser_test_setup?") % path)
    return LocalSubFileSystem(path)
  else:
    cluster_conf = conf.HDFS_CLUSTERS[identifier]
    # The only way to disable webhdfs is to specify an empty value
    if cluster_conf.WEBHDFS_URL.get() != '':
      return webhdfs.WebHdfs.from_config(cluster_conf)
    else:
      return hadoopfs.HadoopFileSystem.from_config(
        cluster_conf,
        hadoop_bin_path=conf.HADOOP_BIN.get())

def _make_mrcluster(identifier):
  cluster_conf = conf.MR_CLUSTERS[identifier]
  return LiveJobTracker.from_conf(cluster_conf)

FS_CACHE = None
def get_hdfs(identifier="default"):
  global FS_CACHE
  get_all_hdfs()
  return FS_CACHE[identifier]

def get_all_hdfs():
  global FS_CACHE
  if FS_CACHE is not None:
    return FS_CACHE

  FS_CACHE = {}
  for identifier in conf.HDFS_CLUSTERS.keys():
    FS_CACHE[identifier] = _make_filesystem(identifier)
  return FS_CACHE

MR_CACHE = None

def get_default_mrcluster():
  global MR_CACHE
  try:
    return get_mrcluster()
  except KeyError:
    # Return an arbitrary cluster
    candidates = all_mrclusters()
    if candidates:
      return candidates.values()[0]
    return None

def get_next_ha_mrcluster():
  """
  Return the next available JT instance or None
  
  This method currently works for distincting between active/standby JT as a standby JT does not respond.
  A cleaner but more complicated way would be to do something like the MRHAAdmin tool and
  org.apache.hadoop.ha.HAServiceStatus#getServiceStatus().
  """
  candidates = all_mrclusters()
  has_ha = sum([conf.MR_CLUSTERS[name].SUBMIT_TO.get() for name in conf.MR_CLUSTERS.keys()]) >= 2

  for name in conf.MR_CLUSTERS.keys():
    config = conf.MR_CLUSTERS[name]
    if config.SUBMIT_TO.get():
      jt = candidates[name]
      if has_ha:
        try:
          status = jt.cluster_status()
          if status.stateAsString == 'RUNNING':
            return (config, jt)
          else:
            LOG.info('JobTracker %s is not RUNNING, skipping it: %s' % (name, status))
        except Exception, ex:
          LOG.info('JobTracker %s is not available, skipping it: %s' % (name, ex))
      else:
        return (config, jt)
  return None

def get_mrcluster(identifier="default"):
  global MR_CACHE
  all_mrclusters()
  return MR_CACHE[identifier]

def all_mrclusters():
  global MR_CACHE
  if MR_CACHE is not None:
    return MR_CACHE
  MR_CACHE = {}
  for identifier in conf.MR_CLUSTERS.keys():
    MR_CACHE[identifier] = _make_mrcluster(identifier)
  return MR_CACHE

def get_cluster_conf_for_job_submission():
  """
  Check the `submit_to' for each MR/Yarn cluster, and return the
  config section of first one that enables submission.

  HA support for MR1.
  """
  for name in conf.YARN_CLUSTERS.keys():
    yarn = conf.YARN_CLUSTERS[name]
    if yarn.SUBMIT_TO.get():
      return yarn

  mr = get_next_ha_mrcluster()

  if mr is not None:
    config, jt = mr
    return config
  else:
    return None

def get_cluster_addr_for_job_submission():
  """
  Check the `submit_to' for each MR/Yarn cluster, and return the
  host:port of first one that enables submission.
  """
  conf = get_cluster_conf_for_job_submission()
  if conf is None:
    return None
  return "%s:%s" % (conf.HOST.get(), conf.PORT.get())

def is_yarn():
  cluster = get_cluster_conf_for_job_submission()
  return cluster is not None and 'IS_YARN' in cluster.config.members

def clear_caches():
  """
  Clears cluster's internal caches.  Returns
  something that can be given back to restore_caches.
  """
  global FS_CACHE, MR_CACHE
  old = FS_CACHE, MR_CACHE
  FS_CACHE, MR_CACHE = None, None
  return old

def restore_caches(old):
  """
  Restores caches from the result of a previous clear_caches call.
  """
  global FS_CACHE, MR_CACHE
  FS_CACHE, MR_CACHE = old
