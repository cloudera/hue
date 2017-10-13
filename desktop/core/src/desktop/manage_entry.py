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

def entry():
  _deprecation_check(sys.argv[0])

  from django.core.exceptions import ImproperlyConfigured
  from django.core.management import execute_from_command_line, find_commands, find_management_module
  from django.core.management import LaxOptionParser
  from django.core.management.base import BaseCommand

  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desktop.settings')

  # What's the subcommand being run?
  # This code uses the same logic from django.core.management to handle command args
  argv = sys.argv[:]
  parser = LaxOptionParser(option_list=BaseCommand.option_list)
  parser.parse_args(argv)

  if len(argv) > 1:
    prof_id = subcommand = argv[1]
    commands_req_db = [ "changepassword", "createsuperuser",
                        "clean_history_docs", "convert_documents", "sync_documents",
                        "dbshell", "dumpdata", "loaddata", "shell",
                        "migrate", "syncdb",
                        "import_ldap_group", "import_ldap_user", "sync_ldap_users_and_groups", "useradmin_sync_with_unix" ]
    if subcommand in commands_req_db:
      #Check if this is a CM managed cluster
      cm_config_file = '/etc/cloudera-scm-agent/config.ini'
      if os.path.isfile(cm_config_file) and "--cm-managed" not in sys.argv:
        if not "HUE_CONF_DIR" in os.environ:
          print "ALERT: This appears to be a CM Managed environment"
          print "ALERT: HUE_CONF_DIR must be set when running hue commands in CM Managed environment"
          print "ALERT: Please run 'hue <command> --cm-managed'"
  else:
    prof_id = str(os.getpid())

  # Check if --cm-managed flag is set and strip it out
  # to prevent from sending to subcommands
  if "--cm-managed" in sys.argv:
    sys.argv.remove("--cm-managed")
    import ConfigParser
    from ConfigParser import NoOptionError
    config = ConfigParser.RawConfigParser()
    config.read(cm_config_file)
    try:
      cm_supervisor_dir = config.get('General', 'agent_wide_credential_cache_location')
    except NoOptionError:
      cm_supervisor_dir = '/var/run/cloudera-scm-agent'
      pass

    #Parse CM supervisor include file for Hue and set env vars
    cm_supervisor_dir = cm_supervisor_dir + '/supervisor/include'
    hue_env_conf = None
    envline = None
    cm_hue_string = "HUE_SERVER"


    for file in os.listdir(cm_supervisor_dir):
      if cm_hue_string in file:
        hue_env_conf = file

    if not hue_env_conf == None:
      if os.path.isfile(cm_supervisor_dir + "/" + hue_env_conf):
        hue_env_conf_file = open(cm_supervisor_dir + "/" + hue_env_conf, "r")
        for line in hue_env_conf_file:
          if "environment" in line:
            envline = line
          if "directory" in line:
            empty, hue_conf_dir = line.split("directory=")
            os.environ["HUE_CONF_DIR"] = hue_conf_dir.rstrip()
    else:
      print "This appears to be a CM managed cluster the"
      print "supervisor/include file for Hue could not be found"
      print "in order to successfully run commands that access"
      print "the database you need to set the following env vars:"
      print ""
      print "  export JAVA_HOME=<java_home>"
      print "  export HUE_CONF_DIR=\"/var/run/cloudera-scm-agent/process/\`ls -1 /var/run/cloudera-scm-agent/process | grep HUE_SERVER | sort -n | tail -1 \`\""
      print "  export HUE_IGNORE_PASSWORD_SCRIPT_ERRORS=1"
      print "  export HUE_DATABASE_PASSWORD=<hueDBpassword>"

    if not envline == None:
      empty, environment = envline.split("environment=")
      for envvar in environment.split(","):
        if "HADOOP_C" in envvar or "PARCEL" in envvar:
          envkey, envval = envvar.split("=")
          envval = envval.replace("'", "").rstrip()
          os.environ[envkey] = envval

    #Set JAVA_HOME:
    if "JAVA_HOME" not in os.environ.keys():
      parcel_dir=os.environ["PARCELS_ROOT"] + '/' + os.environ["PARCEL_DIRNAMES"]
      bigtop_javahome=parcel_dir + '/lib/bigtop-utils/bigtop-detect-javahome'
      if os.path.isfile(bigtop_javahome):
        command = "/bin/bash -c \"source " + bigtop_javahome + " && env\""
        proc = subprocess.Popen(command, stdout = subprocess.PIPE, shell = True)
        for procline in proc.stdout:
          (key, _, value) = procline.partition("=")
          if key == "JAVA_HOME":
            os.environ[key] = value.rstrip()
    
    if "JAVA_HOME" not in os.environ.keys():
      print "Not able to set JAVA_HOME.  Please set manually:"
      print "  export JAVA_HOME=<java_home>"

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
