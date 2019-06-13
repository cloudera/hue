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

import logging
import os
import os.path
import fnmatch
import sys
import traceback
import subprocess

LOG = logging.getLogger(__name__)

def _deprecation_check(arg0):
  """HUE-71. Deprecate build/env/bin/desktop"""
  if os.path.basename(arg0) == 'desktop':
    to_use = os.path.join(os.path.dirname(arg0), 'hue')
    msg = "Warning: '%s' has been deprecated. Please use '%s' instead." % (arg0, to_use)
    print >> sys.stderr, msg
    LOG.warn(msg)

def reload_with_cm_env(cm_managed):
  try:
    from django.db.backends.oracle.base import Oracle_datetime
  except:
    if 'LD_LIBRARY_PATH' in os.environ:
      print "We need to reload the process to include LD_LIBRARY_PATH for Oracle backend"
      try:
        if cm_managed:
          sys.argv.append("--cm-managed")
 
        sys.argv.append("--skip-reload")
        os.execv(sys.argv[0], sys.argv)
      except Exception, exc:
        print 'Failed re-exec: %s' % exc
        sys.exit(1)

def entry():
  _deprecation_check(sys.argv[0])

  from django.core.exceptions import ImproperlyConfigured
  from django.core.management import execute_from_command_line, find_commands
  from django.core.management import CommandParser
  from django.core.management.base import BaseCommand

  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desktop.settings')
  cm_config_file = '/etc/cloudera-scm-agent/config.ini'
  ld_path_orig = None
  if "LD_LIBRARY_PATH" in os.environ.keys():
    ld_path_orig = os.environ["LD_LIBRARY_PATH"]

  # What's the subcommand being run?
  # This code uses the same logic from django.core.management to handle command args
  subcommand = None
  if "--skip-reload" in sys.argv:
    skip_reload = True
    sys.argv.remove("--skip-reload")
  else:
    skip_reload = False

  # Check if --cm-managed flag is set and strip it out
  # to prevent from sending to subcommands
  if "--cm-managed" in sys.argv:
    sys.argv.remove("--cm-managed")
    cm_managed = True
  else:
    cm_managed = False

  if len(sys.argv) > 1:
    subcommand = sys.argv[1]
  parser = CommandParser(None, usage="%(prog)s subcommand [options] [args]", add_help=False)
  parser.parse_known_args(sys.argv[2:])

  if len(sys.argv) > 1:
    prof_id = subcommand = sys.argv[1]
    #Check if this is a CM managed cluster
    if os.path.isfile(cm_config_file) and not cm_managed and not skip_reload:
        print "ALERT: This appears to be a CM Managed environment"
        print "ALERT: HUE_CONF_DIR must be set when running hue commands in CM Managed environment"
        print "ALERT: Please run 'hue <command> --cm-managed'"
  else:
    prof_id = str(os.getpid())

  # CM managed configure env vars
  if cm_managed:
    import ConfigParser
    from ConfigParser import NoOptionError
    config = ConfigParser.RawConfigParser()
    config.read(cm_config_file)
    try:
      cm_agent_run_dir = config.get('General', 'agent_wide_credential_cache_location')
    except NoOptionError:
      cm_agent_run_dir = '/var/run/cloudera-scm-agent'
      pass

    #Parse CM supervisor include file for Hue and set env vars
    cm_supervisor_dir = cm_agent_run_dir + '/supervisor/include'
    cm_process_dir = cm_agent_run_dir + '/process'
    hue_env_conf = None
    envline = None
    cm_hue_string = "HUE_SERVER"

    for file in os.listdir(cm_supervisor_dir):
      if cm_hue_string in file:
        hue_env_conf = file
        hue_env_conf = cm_supervisor_dir + "/" + hue_env_conf

    if hue_env_conf == None:
      process_dirs = fnmatch.filter(os.listdir(cm_process_dir), '*%s*' % cm_hue_string)
      process_dirs.sort()
      hue_process_dir = cm_process_dir + "/" + process_dirs[-1]
      hue_env_conf = fnmatch.filter(os.listdir(hue_process_dir), 'supervisor.conf')[0]
      hue_env_conf = hue_process_dir + "/" + hue_env_conf

    if not hue_env_conf == None:
      if os.path.isfile(hue_env_conf):
        hue_env_conf_file = open(hue_env_conf, "r")
        for line in hue_env_conf_file:
          if "environment" in line:
            envline = line
          if "directory" in line:
            empty, hue_conf_dir = line.split("directory=")
            os.environ["HUE_CONF_DIR"] = hue_conf_dir.rstrip()
    else:
      print "This appears to be a CM managed cluster, but the"
      print "supervisor/include file for Hue could not be found"
      print "in order to successfully run commands that access"
      print "the database you need to set the following env vars:"
      print ""
      print "  export JAVA_HOME=<java_home>"
      print "  export HUE_CONF_DIR=\"%s/`ls -1 %s | grep %s | sort -n | tail -1 `\"" % (cm_processs_dir, cm_process_dir, cm_hue_string)
      print "  export HUE_IGNORE_PASSWORD_SCRIPT_ERRORS=1"
      print "  export HUE_DATABASE_PASSWORD=<hueDBpassword>"
      print "If using Oracle as your database:"
      print "  export LD_LIBRARY_PATH=/path/to/instantclient"
      print ""
      print "If the above does not work, make sure Hue has been started on this server."

    if not envline == None:
      empty, environment = envline.split("environment=")
      for envvar in environment.split(","):
        include_env_vars = ("HADOOP_C", "PARCEL", "SCM_DEFINES", "LD_LIBRARY")
        if any(include_env_var in envvar for include_env_var in include_env_vars):
          envkey, envval = envvar.split("=")
          envval = envval.replace("'", "").rstrip()
          os.environ[envkey] = envval

    #Set JAVA_HOME
    if "JAVA_HOME" not in os.environ.keys():
      if os.path.isfile('/usr/lib64/cmf/service/common/cloudera-config.sh'):
        locate_java = subprocess.Popen(
          ['bash', '-c', '. /usr/lib64/cmf/service/common/cloudera-config.sh; locate_java_home'], stdout=subprocess.PIPE,
          stderr=subprocess.PIPE)
      elif os.path.isfile('/opt/cloudera/cm-agent/service/common/cloudera-config.sh'):
        locate_java = subprocess.Popen(
          ['bash', '-c', '. /opt/cloudera/cm-agent/service/common/cloudera-config.sh; locate_java_home'],
          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      else:
        locate_java = None

      JAVA_HOME = "UNKNOWN"

      if locate_java is not None:
        for line in iter(locate_java.stdout.readline, ''):
          if 'JAVA_HOME' in line:
            JAVA_HOME = line.rstrip().split('=')[1]

      if JAVA_HOME != "UNKNOWN":
        os.environ["JAVA_HOME"] = JAVA_HOME

      if "JAVA_HOME" not in os.environ.keys():
        print "JAVA_HOME must be set and can't be found, please set JAVA_HOME environment variable"
        print "  export JAVA_HOME=<java_home>"
        sys.exit(1)

    #Make sure we set Oracle Client if configured
    if "LD_LIBRARY_PATH" not in os.environ.keys():
      if "SCM_DEFINES_SCRIPTS" in os.environ.keys():
        for scm_script in os.environ["SCM_DEFINES_SCRIPTS"].split(":"):
          if "ORACLE" in scm_script:
            if os.path.isfile(scm_script):
              oracle_source = subprocess.Popen(". %s; env" % scm_script, stdout=subprocess.PIPE, shell=True, executable="/bin/bash")
              for line in oracle_source.communicate()[0].splitlines():
                if "LD_LIBRARY_PATH" in line:
                  var, oracle_ld_path = line.split("=")
                  os.environ["LD_LIBRARY_PATH"] = oracle_ld_path

    if "LD_LIBRARY_PATH" not in os.environ.keys():
      print "LD_LIBRARY_PATH can't be found, if you are using ORACLE for your Hue database"
      print "then it must be set, if not, you can ignore"
      print "  export LD_LIBRARY_PATH=/path/to/instantclient"

  if "LD_LIBRARY_PATH" in os.environ.keys():
    if ld_path_orig is not None and ld_path_orig == os.environ["LD_LIBRARY_PATH"]:
      skip_reload = True

  if not skip_reload:
    reload_with_cm_env(cm_managed)

  try:
    # Let django handle the normal execution
    if os.getenv("DESKTOP_PROFILE"):
      _profile(prof_id, lambda: execute_from_command_line(sys.argv))
    else:
      execute_from_command_line(sys.argv)
  except ImproperlyConfigured, e:
    if len(sys.argv) > 1 and sys.argv[1] == 'is_db_alive' and 'oracle' in str(e).lower():
      print >> sys.stderr, e # Oracle connector is improperly configured
      sys.exit(10)
    else:
      raise e
  except subprocess.CalledProcessError, e:
    if "altscript.sh" in str(e).lower():
      print "%s" % e
      print "HUE_CONF_DIR seems to be set to CM location and '--cm-managed' flag not used"

def _profile(prof_id, func):
  """
  Wrap a call with a profiler
  """
  # Note that some distro don't come with pstats
  import pstats
  try:
    import cProfile as profile
  except ImportError:
    import profile

  PROF_DAT = '/tmp/desktop-profile-%s.dat' % (prof_id,)

  prof = profile.Profile()
  try:
    prof.runcall(func)
  finally:
    if os.path.exists(PROF_DAT):
      os.remove(PROF_DAT)
    prof.dump_stats(PROF_DAT)
    # Sort the calls by time spent and show top 50
    pstats.Stats(PROF_DAT).sort_stats('time').print_stats(50)
    print >>sys.stderr, "Complete profile data in %s" % (PROF_DAT,)
