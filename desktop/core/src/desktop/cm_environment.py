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

import logging
import os
import os.path
import re
import subprocess
import sys

from hue_shared import which

LOG = logging.getLogger(__name__)


"""
Class to configure Hue environment from CM
"""


def set_cm_environment():
  """
  Collect environment from CM supervisor
  """
  hue_config = {}
  hue_bin_dir = "/usr/lib/hue"
  hue_path = "/usr/lib/hue"
  parcel_name = "CDH"
  parcel_dir = "/opt/cloudera/parcels"
  dbengine = None
  cm_agent_process = subprocess.Popen('ps -ef | grep "[c]m agent\|[c]mf-agent" | awk \'{print $2}\'', shell=True,
                                      stdout=subprocess.PIPE)
  cm_agent_pid = cm_agent_process.communicate()[0].split('\n')[0]
  if cm_agent_pid != '':
    try:
      supervisor_process = subprocess.Popen('ps -ef | grep [s]upervisord | awk \'{print $2}\'', shell=True,
                                            stdout=subprocess.PIPE)
      supervisor_pid = supervisor_process.communicate()[0].split('\n')[0]
      cm_supervisor_dir = os.path.realpath('/proc/%s/cwd' % supervisor_pid)
      if supervisor_pid == '':
        LOG.exception("This appears to be a CM enabled cluster and supervisord is not running")
        LOG.exception("Make sure you are running as root and CM supervisord is running")
        sys.exit(1)
    except Exception, e:
      LOG.exception("This appears to be a CM enabled cluster and supervisord is not running")
      LOG.exception("Make sure you are running as root and CM supervisord is running")
      sys.exit(1)

    # Parse CM supervisor include file for Hue and set env vars
    cm_supervisor_dir = cm_supervisor_dir + '/include'
    cm_agent_run_dir = os.path.dirname(cm_supervisor_dir)
    hue_env_conf = None
    envline = None
    cm_hue_string = "HUE_SERVER"

    for file in os.listdir(cm_supervisor_dir):
      if cm_hue_string in file:
        hue_env_conf = file

    if not hue_env_conf == None:
      if os.path.isfile(cm_supervisor_dir + "/" + hue_env_conf):
        hue_env_conf_file = open(cm_supervisor_dir + "/" + hue_env_conf, "r")
        LOG.info("Setting CM managed environment using supervisor include: %s" % hue_env_conf_file)
        for line in hue_env_conf_file:
          if "environment" in line:
            envline = line
          if "directory" in line:
            empty, hue_conf_dir = line.split("directory=")
            os.environ["HUE_CONF_DIR"] = hue_conf_dir.rstrip()
            sys.path.append(os.environ["HUE_CONF_DIR"])

    if not envline == None:
      empty, environment = envline.split("environment=")
      for envvar in environment.split(","):
        if "HADOOP_C" in envvar or "PARCEL" in envvar or "DESKTOP" in envvar or "ORACLE" in envvar or "LIBRARY" in \
            envvar or "CMF" in envvar:
          envkey, envval = envvar.split("=")
          envval = envval.replace("'", "").rstrip()
          if "LIBRARY" not in envkey:
            os.environ[envkey] = envval
          elif "LD_LIBRARY_PATH" not in os.environ.keys():
            os.environ[envkey] = envval

    if "PARCELS_ROOT" in os.environ:
      parcel_dir = os.environ["PARCELS_ROOT"]

    if "PARCEL_DIRNAMES" in os.environ:
      parcel_names = os.environ["PARCEL_DIRNAMES"].split(':')
      for parcel_name_temp in parcel_names:
        if parcel_name_temp.startswith("CDH"):
          parcel_name = parcel_name_temp

    if os.path.isdir("%s/%s/lib/hue" % (parcel_dir, parcel_name)):
      hue_path = "%s/%s/lib/hue" % (parcel_dir, parcel_name)
    hue_bin_dir = "%s/build/env/bin" % hue_path

    cloudera_config_script = None
    if os.path.isfile('/usr/lib64/cmf/service/common/cloudera-config.sh'):
      cloudera_config_script = '/usr/lib64/cmf/service/common/cloudera-config.sh'
    elif os.path.isfile('/opt/cloudera/cm-agent/service/common/cloudera-config.sh'):
      cloudera_config_script = '/opt/cloudera/cm-agent/service/common/cloudera-config.sh'

    JAVA_HOME = None
    if cloudera_config_script is not None:
      locate_java = subprocess.Popen(['bash', '-c', '. %s; locate_java_home' % cloudera_config_script],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      for line in iter(locate_java.stdout.readline, ''):
        if 'JAVA_HOME' in line:
          JAVA_HOME = line.rstrip().split('=')[1]

    if JAVA_HOME is not None:
      os.environ["JAVA_HOME"] = JAVA_HOME

    if "JAVA_HOME" not in os.environ:
      print "JAVA_HOME must be set and can't be found, please set JAVA_HOME environment variable"
      sys.exit(1)

    hue_config["LD_LIBRARY_PATH"] = None
    for line in open(os.environ["HUE_CONF_DIR"] + "/hue_safety_valve_server.ini"):
      if re.search("engine=", line):
        dbengine = line
    if dbengine is None:
      for line in open(os.environ["HUE_CONF_DIR"] + "/hue_safety_valve.ini"):
        if re.search("engine=", line):
          dbengine = line
    if dbengine is None:
      for line in open(os.environ["HUE_CONF_DIR"] + "/hue.ini"):
        if re.search("engine=", line):
          dbengine = line

    if dbengine is not None and "oracle" in dbengine.lower():
      # Make sure we set Oracle Client if configured
      if "LD_LIBRARY_PATH" not in os.environ.keys():
        if "SCM_DEFINES_SCRIPTS" in os.environ.keys():
          for scm_script in os.environ["SCM_DEFINES_SCRIPTS"].split(":"):
            if "ORACLE_INSTANT_CLIENT" in scm_script:
              if os.path.isfile(scm_script):
                oracle_source = subprocess.Popen(". %s; env" % scm_script, stdout=subprocess.PIPE, shell=True,
                                                 executable="/bin/bash")
                for line in oracle_source.communicate()[0].splitlines():
                  if "LD_LIBRARY_PATH" in line:
                    var, oracle_ld_path = line.split("=")
                    os.environ["LD_LIBRARY_PATH"] = oracle_ld_path

      if "LD_LIBRARY_PATH" not in os.environ.keys() or not os.path.isfile(
              "%s/libclntsh.so.11.1" % os.environ["LD_LIBRARY_PATH"]):
        print "You are using Oracle for backend DB"
        if "LD_LIBRARY_PATH" in os.environ.keys():
          print "LD_LIBRARY_PATH set to %s" % os.environ["LD_LIBRARY_PATH"]
          print "LD_LIBRARY_PATH does not contain libclntsh.so.11.1"
          print "Please set LD_LIBRARY_PATH correctly and rerun"

        else:
          print "LD_LIBRARY_PATH can't be found, if you are using ORACLE for your Hue database"
          print "then it must be set, if not, you can ignore"

        print "Here is an exmple, ONLY INCLUDE ONE PATH and NO VARIABLES"
        print "  export LD_LIBRARY_PATH=/path/to/instantclient"
        sys.exit(1)

  else:
    print "CM does not appear to be running on this server"
    print "If this is a CM managed cluster make sure the agent and supervisor are running"
    print "Running with /etc/hue/conf as the HUE_CONF_DIR"
    os.environ["HUE_CONF_DIR"] = "/etc/hue/conf"

  hue_config['hue_path'] = hue_path
  hue_config['hue_bin_dir'] = hue_bin_dir
  hue_config['HUE_CONF_DIR'] = os.environ["HUE_CONF_DIR"]
  hue_config['parcel_name'] = parcel_name
  hue_config['parcel_dir'] = parcel_dir
  if dbengine is not None and "oracle" in dbengine.lower():
    hue_config['LD_LIBRARY_PATH'] = os.environ["LD_LIBRARY_PATH"]

  return hue_config


def reload_with_cm_env():
  try:
    from django.db.backends.oracle.base import Oracle_datetime
  except:
    os.environ["SKIP_RELOAD"] = "True"
    if 'LD_LIBRARY_PATH' in os.environ:
      LOG.info("We need to reload the process to include any LD_LIBRARY_PATH changes")
      try:
        os.execv(sys.argv[0], sys.argv)
      except Exception, exc:
        LOG.warn('Failed re-exec:', exc)
        sys.exit(1)


def check_security():
  from hadoop import conf
  hdfs_config = conf.HDFS_CLUSTERS['default']
  security_enabled = False
  if hdfs_config.SECURITY_ENABLED.get():
    KLIST = which('klist')
    if KLIST is None:
      LOG.exception("klist is required, please install and rerun")
      sys.exit(1)
    klist_cmd = '%s | grep "Default principal"' % KLIST
    klist_check = subprocess.Popen(klist_cmd, shell=True, stdout=subprocess.PIPE)
    klist_princ = klist_check.communicate()[0].split(': ')[1]
    if not 'hue/' in klist_princ:
      LOG.exception("klist failed, please contact support: %s" % klist_princ)
      sys.exit(1)
    LOG.info("Security enabled using principal: %s" % klist_princ)
    LOG.info("You can imitate by running following export:")
    LOG.info("OSRUN: export KRB5CCNAME=%s" % os.environ['KRB5CCNAME'])
    security_enabled = True

  return security_enabled
