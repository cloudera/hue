#!/bin/bash
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

#Clean up duplicate Hue permissions

#parse command line arguments
parse_arguments()
{
  # Test that we're using compatible getopt version.
  getopt -T > /dev/null
  if [[ $? -ne 4 ]]; then
    echo "Incompatible getopt version."
    exit 1
  fi

  # Parse short and long option parameters.
  OVERRIDE=
  VERBOSE=
  DESKTOP_DEBUG=false
  GETOPT=`getopt -n $0 -o o,v,h \
      -l override,verbose,help \
      -- "$@"`
  eval set -- "$GETOPT"
  while true;
  do
    case "$1" in
    -o|--override)
      OVERRIDE=true
      shift
      ;;
    -v|--verbose)
      VERBOSE=true
      shift
      ;;
    --)
      shift
      break
      ;;
    *)
      usage
      exit 1
      ;;
    esac
  done
  #
}

usage()
{
cat << EOF
usage: $0 [options]

Removes all duplicate permissions

OPTIONS
   -o|--override           Allow script to run as non-root, must set HUE_CONF_DIR manually before running
   -v|--verbose		   Enable verbose logging
   -h|--help               Show this message.
EOF
}

debug()
{
   if [[ ! -z $VERBOSE ]]
   then
      echo "$1" >> ${LOG_FILE}
   fi
}

main()
{

  parse_arguments "$@"

  SCRIPT_DIR="$( cd -P "$( dirname "$0" )" && pwd )"
  PYTHONPATH=${SCRIPT_DIR}/lib:${PYTHONPATH}
  export SCRIPT_DIR PYTHONPATH

  #SET IMPORTANT ENV VARS
  if [[ -z ${HUE_CONF_DIR} ]]
  then
    if [ -d "/var/run/cloudera-scm-agent/process" ]
    then
      HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/`ls -1 /var/run/cloudera-scm-agent/process | grep HUE_SERVER | sort -n | tail -1 `"
    else
      HUE_CONF_DIR="/etc/hue/conf"
    fi
    export HUE_CONF_DIR
  fi

  if [[ ! ${USER} =~ .*root* ]]
  then
    if [[ -z ${OVERRIDE} ]]
    then
      echo "Script must be run as root: exiting"
      exit 1
    fi
  else
    if [[ $(ps -ef | grep "[h]ue runc" | awk '{print }') ]]
    then
      DESKTOP_LOG_DIR=$(strings /proc/$(ps -ef | grep "[h]ue runc" | awk '{print }' | awk '{print $2}')/environ | grep DESKTOP_LOG_DIR | awk -F\= '{print $2}')
    fi
  fi

  if [[ -z ${DESKTOP_LOG_DIR} ]]
  then
    DESKTOP_LOG_DIR=${HUE_CONF_DIR}/logs
  fi
  if [[ ! -f ${DESKTOP_LOG_DIR} ]]
  then
    mkdir -p ${DESKTOP_LOG_DIR}
  fi
  LOG_FILE=${DESKTOP_LOG_DIR}/`basename "$0" | awk -F\. '{print $1}'`.log
  LOG_ROTATE_SIZE=10 #MB before rotating, size in MB before rotating log to .1
  LOG_ROTATE_COUNT=5 #number of log files, so 20MB max

  PARCEL_DIR=/opt/cloudera/parcels/CDH
  if [ ! -d "/usr/lib/hadoop" ]
  then
    CDH_HOME=$PARCEL_DIR
  else
    CDH_HOME=/usr
  fi

  if [ -d "${CDH_HOME}/lib/hue/build/env/bin" ]
  then
    COMMAND="${CDH_HOME}/lib/hue/build/env/bin/hue shell"
    TEST_COMMAND="${CDH_HOME}/lib/hue/build/env/bin/hue dbshell"
  else
    COMMAND="${CDH_HOME}/share/hue/build/env/bin/hue shell"
    TEST_COMMAND="${CDH_HOME}/share/hue/build/env/bin/hue dbshell"
  fi

  ORACLE_ENGINE_CHECK=$(grep engine ${HUE_CONF_DIR}/hue* | grep -i oracle)
  if [[ ! -z ${ORACLE_ENGINE_CHECK} ]]
  then
    if [[ -z ${ORACLE_HOME} ]]
    then
      ORACLE_PARCEL=/opt/cloudera/parcels/ORACLE_INSTANT_CLIENT/instantclient_11_2
      if [[ -d ${ORACLE_PARCEL} ]]
      then
        ORACLE_HOME=${ORACLE_PARCEL}
        LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${ORACLE_HOME}
        export LD_LIBRARY_PATH ORACLE_HOME
      fi
    fi
    if [[ -z ${ORACLE_HOME} ]]
    then
      echo "It looks like you are using Oracle as your backend"
      echo "ORACLE_HOME must be set to the correct Oracle client"
      echo "before running this script"
      exit 1
    fi
  fi

  HUE_IGNORE_PASSWORD_SCRIPT_ERRORS=1
  if [[ -z ${HUE_DATABASE_PASSWORD} ]]
  then
    echo "CDH 5.5 and above requires that you set the environment variable:"
    echo "HUE_DATABASE_PASSWORD=<dbpassword>"
    exit 1
  fi
  PGPASSWORD=${HUE_DATABASE_PASSWORD}
  export CDH_HOME COMMAND HUE_IGNORE_PASSWORD_SCRIPT_ERRORS PGPASSWORD

  debug "Validating DB connectivity"
#  echo "COMMAND: echo \"from django.db import connection; cursor = connection.cursor(); cursor.execute('select count(*) from auth_user')\" | ${TEST_COMMAND}" | tee -a ${LOG_FILE}
#  echo "from django.db import connection; cursor = connection.cursor(); cursor.execute('select count(*) from auth_user')" | ${TEST_COMMAND} | tee -a ${LOG_FILE}

  QUIT_COMMAND="quit"
  PG_ENGINE_CHECK=$(grep engine ${HUE_CONF_DIR}/hue* | grep -i postgres)
  if [[ ! -z ${PG_ENGINE_CHECK} ]]
  then
    QUIT_COMMAND='\q'
  fi

#  echo "Running echo ${QUIT_COMMAND} | ${TEST_COMMAND}"
#  echo ${QUIT_COMMAND} | ${TEST_COMMAND}
  if [[ $? -ne 0 ]]
  then
    echo "HUE_DATABASE_PASSWORD is incorrect.  Please check CM: http://${HOSTNAME}:7180/api/v5/cm/deployment and search for HUE_SERVER and database to find correct password"
    exit 1
  fi

debug "Running ${COMMAND}"
${COMMAND} >> /dev/null 2>&1 <<EOF
from useradmin.models import HuePermission, GroupPermission
from datetime import date, timedelta
import desktop.conf
import logging
import logging.handlers
import sys

LOGFILE="${LOG_FILE}"
log = logging.getLogger('')
log.setLevel(logging.INFO)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

fh = logging.handlers.RotatingFileHandler(LOGFILE, maxBytes = (1048576*logrotatesize), backupCount = backupcount)
fh.setFormatter(format)
log.addHandler(fh)

log.info('HUE_CONF_DIR: ${HUE_CONF_DIR}')
log.info("DB Engine: %s" % desktop.conf.DATABASE.ENGINE.get())
log.info("DB Name: %s" % desktop.conf.DATABASE.NAME.get())
log.info("DB User: %s" % desktop.conf.DATABASE.USER.get())
log.info("DB Host: %s" % desktop.conf.DATABASE.HOST.get())
log.info("DB Port: %s" % str(desktop.conf.DATABASE.PORT.get()))
log.info("Removing duplicate Hue permissions")

apps = []
for perm in HuePermission.objects.all():
  apps.append(perm.app)


for app in sorted(set(apps)):
  log.info("")
  log.info("Working on app: %s" % app)
  perms = HuePermission.objects.filter(app=app)
  for perm in perms:
    permsdistinct = HuePermission.objects.filter(app=app, description = perm.description)
    print "len: %s: app: %s: description: %s: id: %s" % (len(permsdistinct), perm.app, perm.description, perm.id)
    if len(permsdistinct) > 1:
      try:
        group = GroupPermission.objects.get(hue_permission=perm)
        if group.group_id != 1:
          log.info("Cleaning up Hue permission for only default group: %s" % perm.__dict__)
          HuePermission.objects.filter(app=app, id = perm.id).delete()
      except:
        pass


for app in sorted(set(apps)):
  log.info("")
  log.info("Working on app because no special perms assigned: %s" % app)
  perms = HuePermission.objects.filter(app=app)
  for perm in perms:
    permsdistinct = HuePermission.objects.filter(app=app, description = perm.description)
    if len(permsdistinct) > 1:
      log.info("Cleaning up Hue permission: %s" % perm.__dict__)
      HuePermission.objects.filter(app=app, id = perm.id).delete()


EOF

echo ""
echo "Logs can be found in ${DESKTOP_LOG_DIR}"

unset PGPASSWORD

}

main "$@"
