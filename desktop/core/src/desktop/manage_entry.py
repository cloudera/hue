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
    os.environ["SKIP_RELOAD"] = "True"
    if 'LD_LIBRARY_PATH' in os.environ:
      print "We need to reload the process to include any LD_LIBRARY_PATH changes"
      try:
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

  # What's the subcommand being run?
  # This code uses the same logic from django.core.management to handle command args
  subcommand = None

  # Check if legacy --cm-managed flag is set and strip it out
  if "--cm-managed" in sys.argv:
    sys.argv.remove("--cm-managed")

  # Legit check for cm managed so we don't need flags
  cm_agent_process = subprocess.Popen('ps -ef | grep "[c]m agent\|[c]mf-agent" | awk \'{print $2}\'', shell=True, stdout=subprocess.PIPE)
  cm_agent_pid = cm_agent_process.communicate()[0].split('\n')[0]
  if cm_agent_pid != '':
    cm_managed = True
  else:
    cm_managed = False

  if len(sys.argv) > 1:
    subcommand = sys.argv[1]
  parser = CommandParser(None, usage="%(prog)s subcommand [options] [args]", add_help=False)
  parser.parse_known_args(sys.argv[2:])

  if len(sys.argv) > 1:
    prof_id = subcommand = sys.argv[1]
  else:
    prof_id = str(os.getpid())

  # CM managed configure env vars
  # Only run if CM isn't running the command
  if cm_managed and not "HADOOP_CREDSTORE_PASSWORD" in os.environ.keys():
    try:
      supervisor_process = subprocess.Popen('ps -ef | grep [s]upervisord | awk \'{print $2}\'', shell=True, stdout=subprocess.PIPE)
      supervisor_pid = supervisor_process.communicate()[0].split('\n')[0]
      cm_supervisor_dir = os.path.realpath('/proc/%s/cwd' % supervisor_pid)
    except Exception, e:
      LOG.exception("Unable to get valid supervisord, make sure you are running as root and make sure the CM supervisor is running")

    #Parse CM supervisor include file for Hue and set env vars
    print "cm_supervisor_dir: %s" % cm_supervisor_dir
    cm_agent_run_dir = os.path.dirname(cm_supervisor_dir)
    cm_process_dir = cm_agent_run_dir + '/process'
    hue_env_conf = None
    envline = None
    cm_hue_string = "HUE_SERVER"

    for file in os.listdir(cm_supervisor_dir):
      if cm_hue_string in file:
        hue_env_conf = file
        hue_env_conf = cm_supervisor_dir + "/" + hue_env_conf

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
      os.environ["HUE_CONF_DIR"] = "/etc/hue/conf"
      print "This appears to be a CM managed cluster, but the"
      print "supervisor/include file for Hue could not be found"
      print "in order to successfully run commands that access"
      print "the database you need to set the following env vars:"
      print ""
      print "  export JAVA_HOME=<java_home>"
      print "  export HUE_CONF_DIR=/path/to/cloudera-scm-agent/process/<id>-hue-HUE_SERVER"
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

    cloudera_config_script = None
    if os.path.isfile('/usr/lib64/cmf/service/common/cloudera-config.sh'):
      cloudera_config_script = '/usr/lib64/cmf/service/common/cloudera-config.sh'
    elif os.path.isfile('/opt/cloudera/cm-agent/service/common/cloudera-config.sh'):
      cloudera_config_script = '/opt/cloudera/cm-agent/service/common/cloudera-config.sh'

    JAVA_HOME = None
    if cloudera_config_script is not None:
      locate_java = subprocess.Popen(['bash', '-c', '. %s; locate_java_home' % cloudera_config_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      for line in iter(locate_java.stdout.readline,''):
        if 'JAVA_HOME' in line:
          JAVA_HOME = line.rstrip().split('=')[1]

    if JAVA_HOME is not None:
      os.environ["JAVA_HOME"] = JAVA_HOME
    else:
      print "JAVA_HOME must be set and can't be found, please set JAVA_HOME environment variable"
      sys.exit(1)

    oracle_check_process = subprocess.Popen('grep -i oracle %s/hue*ini' % os.environ["HUE_CONF_DIR"], shell=True, stdout=subprocess.PIPE)
    oracle_check = oracle_check_process.communicate()[0]
    if not oracle_check == '':
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

  if not "SKIP_RELOAD" in os.environ.keys():
    reload_with_cm_env(cm_managed)

  #Get desktop settings so we can give guidance
  from django.conf import settings
  from django.core.exceptions import ImproperlyConfigured
  try:
    settings.INSTALLED_APPS
  except ImproperlyConfigured as exc:
    self.settings_exception = exc
  from desktop.conf import DATABASE as desktop_database

  print "Using the following config make sure it looks correct"
  print "HUE_CONF_DIR: %s" % os.environ['HUE_CONF_DIR']
  print "DB Engine: %s" % desktop_database.ENGINE.get()
  print "DB Name: %s" % desktop_database.NAME.get()
  print "DB User: %s" % desktop_database.USER.get()
  print "DB Host: %s" % desktop_database.HOST.get()
  print "DB Port: %s" % str(desktop_database.PORT.get())

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
