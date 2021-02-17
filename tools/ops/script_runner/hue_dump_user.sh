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

#Test to search for doc1 and doc2

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
  USERNAME=
  VERBOSE=
  DESKTOP_DEBUG=false
  GETOPT=`getopt -n $0 -o o,u:,v,h \
      -l override,username:,verbose,help \
      -- "$@"`
  eval set -- "$GETOPT"
  while true;
  do
    case "$1" in
    -o|--override)
      OVERRIDE=true
      shift
      ;;
    -u|--username)
      USERNAME=$2
      shift 2
      ;;
    -v|--verbose)
      VERBOSE=true
      DESKTOP_DEBUG=true
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

Exports all user objects:

OPTIONS
   -o|--override           Allow script to run as non-root, must set HUE_CONF_DIR manually before running
   -u|--username <user>    User to export objects from.
   -v|--verbose            Verbose logging, off by default
   -h|--help               Show this message.
EOF
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
  export CDH_HOME COMMAND HUE_IGNORE_PASSWORD_SCRIPT_ERRORS

#  echo "COMMAND: echo \"from django.db import connection; cursor = connection.cursor(); cursor.execute('select count(*) from auth_user')\" | ${TEST_COMMAND}" | tee -a ${LOG_FILE}
#  echo "from django.db import connection; cursor = connection.cursor(); cursor.execute('select count(*) from auth_user')" | ${TEST_COMMAND} | tee -a ${LOG_FILE}
  if [[ $? -ne 0 ]]
  then
    echo "DB connect test did not work, HUE_DATABASE_PASSWORD may not be correct"
    echo "If the next query test fails check password in CM: http://<cmhostname>:7180/api/v5/cm/deployment and search for HUE_SERVER and database to find correct password"
  fi

#  ${COMMAND} <<EOF 2>&1 > /dev/null
  ${COMMAND} <<EOF
username = "${USERNAME}"
LOGFILE = "${LOG_FILE}"
logrotatesize=${LOG_ROTATE_SIZE}
backupcount=${LOG_ROTATE_COUNT}

import logging
import logging.handlers
from django.contrib.auth.models import User
import customdumpdata

LOG = logging.getLogger()
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh = logging.handlers.RotatingFileHandler(LOGFILE, maxBytes = (1048576*logrotatesize), backupCount = backupcount)
fh.setFormatter(format)
LOG.addHandler(fh)
LOG.setLevel(logging.INFO)

user = User.objects.get(username = username)

print ""
print ""

customdumpdata.Command().handle_noargs('desktop.Document', 'desktop.Document2', 'beeswax.SavedQuery', 'beeswax.QueryHistory', format='json', indent=2, exclude=[], use_natural_keys=True, use_base_manager=False, user=user)
EOF

}

main "$@"
