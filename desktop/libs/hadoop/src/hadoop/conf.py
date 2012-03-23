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
"""Settings to configure your Hadoop cluster."""
from desktop.lib.conf import Config, UnspecifiedConfigSection, ConfigSection, validate_path, coerce_bool
import fnmatch
import logging
import os

DEFAULT_NN_HTTP_PORT = 50070

HADOOP_HOME = Config(
  key="hadoop_home",
  default=os.environ.get("HADOOP_HOME", "/usr/lib/hadoop"),
  help=("Path to directory holding hadoop libs - HADOOP_HOME in " +
        "hadoop parlance; defaults to environment variable, when" +
        "set.")
)

HADOOP_MR1_HOME = Config(
  key="hadoop_mr1_home",
  default=os.environ.get("HADOOP_MR1_HOME", "/usr/lib/hadoop-0.20-mapreduce"),
  help=("Path to directory holding hadoop libs - HADOOP_HOME in " +
        "hadoop parlance; defaults to environment variable, when" +
        "set.")
)

def hadoop_bin_from_hadoop_home():
  """Returns $HADOOP_HOME/bin/hadoop"""
  return os.path.join(HADOOP_HOME.get(), "bin/hadoop")

HADOOP_BIN = Config("hadoop_bin",
  help="Path to your Hadoop binary",
  dynamic_default=hadoop_bin_from_hadoop_home,
  type=str)

# TODO(philip): This will need more love for dealing with multiple clusters.
HADOOP_CONF_DIR = Config(
  key="hadoop_conf_dir",
  default="/etc/hadoop/conf",
  help="Directory to pass to hadoop_bin (from Hadoop configuration) as the --config flag.",
)

def find_file_recursive(desired_glob, root=None):
  if root is None:
    root_f = lambda: HADOOP_HOME.get()
  else:
    root_f = lambda: not callable(root) and root or root()

  def f():
    for dirpath, dirnames, filenames in os.walk(root_f()):
      matches = fnmatch.filter(filenames, desired_glob)
      if matches:
        if len(matches) != 1:
          logging.warning("Found multiple jars matching %s: %s" %
                          (desired_glob, matches))
        return os.path.join(dirpath, matches[0])

    logging.error("Trouble finding jars matching %s" % (desired_glob,))
    return None

  if root is None:
    root_str = "$HADOOP_HOME"
  else:
    root_str = root
  f.__doc__ = "Finds %s/%s" % (root_str, desired_glob)
  return f

HADOOP_EXAMPLES_JAR = Config(
  key="hadoop_examples_jar",
  dynamic_default=find_file_recursive("hadoop-*examples*.jar", lambda: HADOOP_MR1_HOME.get()),
  help="Path to the hadoop-examples.jar (used for tests and jobdesigner setup)",
  type=str,
  private=True)

HADOOP_STREAMING_JAR = Config(
  key="hadoop_streaming_jar",
  dynamic_default=find_file_recursive("hadoop-*streaming*.jar", lambda: HADOOP_MR1_HOME.get()),
  help="Path to the hadoop-streaming.jar (used by jobdesigner)",
  type=str,
  private=True)

HADOOP_TEST_JAR = Config("hadoop_test_jar",
  help="[Used by testing code.] Path to hadoop-test.jar",
  dynamic_default=find_file_recursive("hadoop-*test*.jar", lambda: HADOOP_MR1_HOME.get()),
  type=str,
  private=True)

HADOOP_PLUGIN_CLASSPATH = Config("hadoop_plugin_classpath",
  help="[Used only in testing code.] Path to the Hadoop plugin jar.",
  type=str,
  dynamic_default=find_file_recursive("hue-plugins-*.jar",
                root=os.path.join(os.path.dirname(__file__), '..', '..', 'java-lib')),
  private=True)

SUDO_SHELL_JAR = Config("hadoop_sudo_shell_jar",
  help="Tool that allows a proxy user UGI to be used to upload files.",
  type=str,
  dynamic_default=find_file_recursive("sudo-shell-*.jar",
                root=os.path.join(os.path.dirname(__file__), '..', '..', 'sudo-shell', 'java-lib')),
  private=True)

CREDENTIALS_MERGER_JAR = Config("hadoop_credentials_merger_jar",
  help="Tool that is capable of merging multiple files containing delegation tokens into one.",
  type=str,
  dynamic_default=find_file_recursive("credentials-merger-*.jar",
                root=os.path.join(os.path.dirname(__file__), '..', '..', 'credentials-merger', 'java-lib')),
  private=True)


HDFS_CLUSTERS = UnspecifiedConfigSection(
  "hdfs_clusters",
  help="One entry for each HDFS cluster",
  each=ConfigSection(
    help="Information about a single HDFS cluster",
    members=dict(
      # Deprecated
      NN_HOST=Config("namenode_host", help="Host/IP for name node"),

      NN_THRIFT_PORT=Config("thrift_port", help="Thrift port for name node", default=10090,
                            type=int),
      NN_HDFS_PORT=Config("hdfs_port", help="Hadoop IPC port for the name node", default=8020,
                            type=int),
      # End deprecation
      FS_DEFAULTFS=Config("fs_defaultfs", help="The equivalent of fs.defaultFS (aka fs.default.name)",
                          default="hdfs://localhost:8020"),
      WEBHDFS_URL=Config("webhdfs_url",
                         help="The URL to WebHDFS/HttpFS service. Defaults to " +
                         "the WebHDFS URL on the NameNode.",
                         type=str, default=None),
      NN_KERBEROS_PRINCIPAL=Config("nn_kerberos_principal", help="Kerberos principal for NameNode",
                                   default="hdfs", type=str),
      DN_KERBEROS_PRINCIPAL=Config("dn_kerberos_principal", help="Kerberos principal for DataNode",
                                   default="hdfs", type=str),
      SECURITY_ENABLED=Config("security_enabled", help="Is running with Kerberos authentication",
                              default=False, type=coerce_bool),
      TEMP_DIR=Config("temp_dir", help="HDFS directory for temporary files",
                      default='/tmp', type=str),
    )
  )
)

MR_CLUSTERS = UnspecifiedConfigSection(
  "mapred_clusters",
  help="One entry for each MapReduce cluster",
  each=ConfigSection(
    help="Information about a single MapReduce cluster",
    members=dict(
      JT_HOST=Config("jobtracker_host", help="Host/IP for JobTracker"),
      JT_PORT=Config("jobtracker_port",
                     default=8021,
                     help="Service port for the JobTracker",
                     type=int),
      JT_THRIFT_PORT=Config("thrift_port", help="Thrift port for JobTracker", default=9290,
                            type=int),
      JT_KERBEROS_PRINCIPAL=Config("jt_kerberos_principal", help="Kerberos principal for JobTracker",
                                   default="mapred", type=str),
      SECURITY_ENABLED=Config("security_enabled", help="Is running with Kerberos authentication",
                              default=False, type=coerce_bool),
      SUBMIT_TO=Config('submit_to', help="Whether Hue should use this cluster to run jobs",
                       default=False, type=coerce_bool),
    )
  )
)

YARN_CLUSTERS = UnspecifiedConfigSection(
  "yarn_clusters",
  help="One entry for each Yarn cluster. Currently only one cluster "
       "(called 'default') is supported.",
  each=ConfigSection(
    help="Information about a single Yarn cluster",
    members=dict(
      RM_HOST=Config("resourcemanager_host",
                     default='localhost',
                     help="Host/IP for the ResourceManager"),
      RM_PORT=Config("resourcemanager_port",
                     default=8032,
                     type=int,
                     help="Service port for the ResourceManager"),
      SUBMIT_TO=Config('submit_to', help="Whether Hue should use this cluster to run jobs",
                       default=False, type=coerce_bool),
    )
  )
)


def config_validator():
  """
  config_validator() -> [ (config_variable, error_message) ]

  Called by core check_config() view.
  """
  from hadoop.fs import webhdfs
  from hadoop import job_tracker
  res = [ ]

  # HADOOP_HOME
  res.extend(validate_path(HADOOP_HOME, is_dir=True))
  # HADOOP_BIN
  res.extend(validate_path(HADOOP_BIN, is_dir=False))

  # JARs: even though these are private, we need them to run jobsub
  res.extend(validate_path(HADOOP_EXAMPLES_JAR, is_dir=False))
  res.extend(validate_path(HADOOP_STREAMING_JAR, is_dir=False))

  submit_to = [ ]

  # HDFS_CLUSTERS
  has_default = False
  for name in HDFS_CLUSTERS.keys():
    cluster = HDFS_CLUSTERS[name]
    res.extend(webhdfs.test_fs_configuration(cluster))
    if name == 'default':
      has_default = True
  if not has_default:
    res.append("hadoop.hdfs_clusters", "You should have an HDFS called 'default'.")

  # MR_CLUSTERS
  for name in MR_CLUSTERS.keys():
    cluster = MR_CLUSTERS[name]
    res.extend(job_tracker.test_jt_configuration(cluster))
    if cluster.SUBMIT_TO.get():
      submit_to.append('mapred_clusters.' + name)

  # Only one cluster should have submit_to
  for name in YARN_CLUSTERS.keys():
    cluster = YARN_CLUSTERS[name]
    if cluster.SUBMIT_TO.get():
      submit_to.append('yarn_clusters.' + name)

  if len(submit_to) > 1:
    res.append(("hadoop", "Only one cluster may enable 'submit_to'. "
                "But it is enabled in the following clusters: " + 
                ', '.join(submit_to)))
  elif len(submit_to) == 0:
    res.append(("hadoop", "Please designate one of the MapReduce or "
                "Yarn clusters with `submit_to=true' in order to run jobs."))

  return res
