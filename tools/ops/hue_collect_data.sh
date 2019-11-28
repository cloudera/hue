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

# NOTE: This script requires curl, strace and lsof to be installed. It
# must be run on the Hue server. Set HUE_USER to a user in Hue with 
# Superuser access to get thread dumps.  Set HUE_PASSWORD to HUE_USER's 
# password.

# Please change USER to contain the user to login
HUE_USER="admin"

# Please change PASSWORD to contain the password for the above user
HUE_PASSWORD="admin"

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
  STRACE_WAIT=15
  RUNS=4
  RUN_WAIT=30
  OUTPUT_DIR_BASE=/tmp/hue_collect_data
  COLLECT_STRACE=true
  COLLECT_LSOF=true
  COLLECT_NETSTAT=true
  COLLECT_THREADS=
  #This is necessary to handle AD auth, doesn't seem to hurt non-ad auth
  #if they have multiple ldap servers or for some reason the drop down
  #at login says something other than "LDAP", then this must match the drop
  #down
  HUE_AUTH_SERVER="LDAP"
  COLLECT_INSTANCE=true
  GETOPT=`getopt -n $0 -o s,l,n,w:,r:,t,u:,p:,i,o:,d:,y:,a:,h \
      -l strace,,lsof,netstat,wait:,runs:,threads,hueuser:,huepass:,instance,outdir:,huelog:,swait:,authserver:,help \
      -- "$@"`
  eval set -- "$GETOPT"
  while true;
  do
    case "$1" in
    -s|--strace)
      COLLECT_STRACE=
      shift
      ;;
    -y|--swait)
      STRACE_WAIT=$2
      shift 2
      ;;
    -l|--lsof)
      COLLECT_LSOF=
      shift
      ;;
    -n|--netstat)
      COLLECT_NETSTAT=
      shift
      ;;
    -t|--threads)
      COLLECT_THREADS=$1
      shift
      ;;
    -u|--hueuser)
      HUE_USER=$2
      shift 2
      ;;
    -p|--huepass)
      HUE_PASSWORD=$2
      shift 2
      ;;
    -a|--authserver)
      HUE_AUTH_SERVER=$2
      shift 2
      ;;
    -i|--instance)
      COLLECT_INSTANCE=
      shift
      ;;
    -w|--wait)
      RUN_WAIT=$2
      shift 2
      ;;
    -r|--runs)
      RUNS=$2
      shift 2
      ;;
    -o|--outdir)
      OUTPUT_DIR_BASE=$2
      shift 2
      ;;
    -d|--huelog)
      HUE_LOG_DIR=$2
      shift 2
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

Collects troubleshooting data from Hue server:

OPTIONS
   -s|--strace             Setting this will disable collecting strace, default 
                           strace will be collected
   -y|--swait <secs>       Interval to wait before stopping strace - default 15.
   -l|--lsof               Setting this will disable collecting lsof, default
                           lsof will be collected
   -n|--netstat            Setting this will disable collecting netstat, default
                           netstat will be collected
   -t|--threads            This will enable thread collection, default threads
                           will NOT be collected
   -u|--hueuser		   Hue username for collecting threads - must be admin user - default admin.
   -p|--huepass		   Hue password for collecting threads - default admin.
   -a|--authserver         This is the Ldap auth server name in the hue.ini if using
                           multiple ldap servers for auth.  Must be set to the auth 
                           server that "hueuser" belongs to.
   -i|--instance	   Setting this will disable collecting CM Hue configs, default
                           CM Hue configs will be collected
   -w|--wait <secs>        Seconds to wait between runs of collecting data - default 30.
   -r|--runs <numruns>     Number of times to collect data - default 4.
   -o|--outdir <outdir>    Location to dump collected data - default /tmp/hue_collect_data.
   -h|--help               Show this message.
EOF
}

main()
{

   parse_arguments "$@"

   if [[ ! ${USER} =~ .*root* ]]
   then
      echo "Script must be run as root: exiting"
      exit 1
   fi

   AGENT_PROCESS_DIR="/var/run/cloudera-scm-agent/process"
   START_DATE=$(date '+%Y%m%d-%H%M')
   MKDIR="mkdir -p"

   for PID in `ps aux | grep [r]uncherrypyserver | awk '{print $2}'`
   do
      if [[ ! ${PID} == ?(-)+([0-9]) ]]
      then
        echo "Unable to get PID from Process, either Hue is not running on this host or Hue is not using CherryPy server"
        exit 1
      fi

      OUTPUT_DIR_DATE=${OUTPUT_DIR_BASE}/${START_DATE}
      OUTPUT_DIR=${OUTPUT_DIR_DATE}/${PID}
      HUE_USAGE_FILE=${OUTPUT_DIR}/cpu_mem_usage/cpu_mem_usage
      HUE_THREADS_FILE=${OUTPUT_DIR}/threads/threads
      HUE_STRACE_FILE=${OUTPUT_DIR}/strace/strace
      HUE_LSOF_FILE=${OUTPUT_DIR}/lsof/lsof
      HUE_ENVIRON_FILE=${OUTPUT_DIR}/environ/environ
      HUE_CMDLINE_FILE=${OUTPUT_DIR}/cmdline/cmdline
      HUE_LIMITS_FILE=${OUTPUT_DIR}/limits/limits
      HUE_NETSTAT_FILE=${OUTPUT_DIR}/netstat/netstat
      HUE_SUDO=${OUTPUT_DIR}/sudo
      HUE_CONFS=${OUTPUT_DIR}/confs
      COOKIE_JAR=${OUTPUT_DIR}/${USER}_cookie.jar

      HOSTNAME=$(hostname)
      HUE_SERVER=${HOSTNAME}

      echo "Making ${OUTPUT_DIR} if it does not exist"
      ${MKDIR} ${OUTPUT_DIR}

      get_cm_process_dir ${PID}

      if [[ -f ${CM_PROPS} ]]
      then
         HUE_LOG_DIR=`grep log_dir ${CM_PROPS} | awk '{print $3}'`
      else
         HUE_LOG_DIR=/var/log/hue
      fi
      HUE_PORT=`grep http_port ${HUE_INI} | awk -F= '{print $2}'`
      if [[ -z ${HUE_PORT} ]]
      then
         HUE_PORT=8888
      fi
      SSL_CERT=`grep ssl_certificate ${HUE_INI} | awk -F= '{print $2}'`
      if [[ ! -z ${SSL_CERT} ]]
      then
         HUE_HTTP="https"
      else
         HUE_HTTP="http"
      fi
      HUE_PASS_URL="${HUE_HTTP}://${HUE_SERVER}:${HUE_PORT}/accounts/login/"
      HUE_THREADS_URL="${HUE_HTTP}://${HUE_SERVER}:${HUE_PORT}/desktop/debug/threads"
   
      if [[ ! -z ${COLLECT_THREADS} ]]
      then
         hue_login
      fi
   
      echo "Gathering info:"
      for (( x=1; x<=${RUNS}; x++ ))
      do
         DATE=$(date '+%Y%m%d-%H%M%S')
         echo "DATE: ${DATE}"
      
         echo "Getting CPU and Memory usage"
         do_ps ${PID}
         ${MKDIR} `dirname ${HUE_USAGE_FILE}`
         echo "PID CPU MEM MEM_MB" >> ${HUE_USAGE_FILE}_${DATE}
         echo "${PID} ${CPU} ${MEM} ${MEM_MB}" >> ${HUE_USAGE_FILE}_${DATE}
         echo "free -m results" >> ${HUE_USAGE_FILE}_${DATE}
         free -m >> ${HUE_USAGE_FILE}_${DATE}
   
         if [[ ${COLLECT_NETSTAT} ]]
         then
            echo "Gathering netstat info"
            ${MKDIR} `dirname ${HUE_NETSTAT_FILE}`
            netstat -anp | grep ${PID} >> ${HUE_NETSTAT_FILE}_${DATE}
         fi

         if [[ ${COLLECT_STRACE} ]]
         then
            echo "Getting strace"
            ${MKDIR} `dirname ${HUE_STRACE_FILE}`
            do_strace \
                 ${PID} \
                 ${STRACE_WAIT} \
                 -o ${HUE_STRACE_FILE}_${DATE} -T -t
         fi

         if [[ ${COLLECT_LSOF} ]]
         then
            echo "Getting open connections"
            ${MKDIR} `dirname ${HUE_LSOF_FILE}`
            do_lsof \
                 ${PID} \
                 ${HUE_LSOF_FILE}_${DATE}
         fi

         if [[ ! -z ${COLLECT_THREADS} ]]
         then
            echo "Getting a thread dump:"
            ${MKDIR} `dirname ${HUE_THREADS_FILE}`
            do_curl \
                 GET \
                 "${HUE_THREADS_URL}" \
                 -L -o ${HUE_THREADS_FILE}_${DATE}
         fi

         sleep ${RUN_WAIT}
      done
   
      if [[ ! -z ${COLLECT_INSTANCE} ]]
      then
         echo "Gathering CM config instances"
         do_instances ${HUE_PORT}
      fi

      echo "Gathering process info"
      ${MKDIR} `dirname ${HUE_ENVIRON_FILE}`
      strings /proc/${PID}/environ >> ${HUE_ENVIRON_FILE}_${DATE}
      ${MKDIR} `dirname ${HUE_CMDLINE_FILE}`
      strings /proc/${PID}/cmdline >> ${HUE_CMDLINE_FILE}_${DATE}
      ${MKDIR} `dirname ${HUE_LIMITS_FILE}`
      strings /proc/${PID}/limits >> ${HUE_LIMITS_FILE}_${DATE}

      ${MKDIR} ${OUTPUT_DIR}/logs
      cp -pr ${HUE_LOG_DIR}/* ${OUTPUT_DIR}/logs 

   done

   echo "Gathering environment info"
   do_sudo \
        ${HUE_SUDO} \
        ${DATE}

  if [[ ! -z ${STRACE_PID} ]]
   then
      echo "strace still running, waiting for it to complete: ${STRACE_PID}"
      wait ${STRACE_PID}
   fi

   echo "Collecting done, please zip ${OUTPUT_DIR_DATE} and upload to the ticket"
}

function do_curl() {

   METHOD=$1
   shift
   URL=$1
   shift
   ARGS=$@

   CURL=$(which curl)
   if [ -z ${COOKIE_JAR} ]
   then
      COOKIE_JAR=/tmp/cookie.jar
   fi
   if [ -f ${COOKIE_JAR} ]
   then
      CSRF_TOKEN=`grep ${HOSTNAME} ${COOKIE_JAR} | grep csrftoken | cut -f 7`
   fi
   if [ ! -f ${CURL} ]
   then
      echo "curl not found, unable to run any curl commands"
   else
      ${CURL} \
         ${CURL_OPTS} \
         -k \
         -e "${HUE_HTTP}://${HUE_SERVER}:${HUE_PORT}/" \
         -b @${COOKIE_JAR} \
         -c ${COOKIE_JAR} \
         -H "X-CSRFToken: ${CSRF_TOKEN}" \
         -X ${METHOD} \
         -s \
         -f \
         ${URL} \
         ${ARGS}
   fi

}

function hue_login() {
   echo "Login to Hue to get Cookie:"
   do_curl \
	GET \
	"${HUE_PASS_URL}" \
	-L 2>&1 > /dev/null

   do_curl \
        POST \
        "${HUE_PASS_URL}" \
        -F username=${HUE_USER} -F password="${HUE_PASSWORD}" -F server="${HUE_AUTH_SERVER}" 2>&1 > /dev/null
}

function do_strace()
{
   SPID=$1
   shift
   WAIT=$1
   shift
   ARGS=$@

   STRACE=$(which strace)
   if [ ! -f ${STRACE} ]
   then
      echo "strace not found, unable to collect strace info"
   else
      if [[ ! -z ${STRACE_PID} ]]
      then
         echo "strace still running, waiting for it to complete: ${STRACE_PID}"
         wait ${STRACE_PID}
      fi
      timeout ${WAIT}s ${STRACE} -f -v -p ${SPID} ${ARGS} &
      STRACE_PID=$!
   fi
}

function do_lsof()
{
   LPID=$1
   shift
   LOG_FILE=$1
   shift
   ARGS=$@

   if [ -z ${LOG_FILE} ]
   then
      LOG_FILE=/tmp/lsof.log
   fi

   LSOF=$(which lsof)
   if [ ! -f ${LSOF} ]
   then
      echo "lsof not found, unable to determine number of connections"
   else
      ${LSOF} -P -p ${LPID} ${ARGS} > ${LOG_FILE}
   fi
}

function do_ps()
{
   PID=$1
   shift
   PS_COMMAND=$(ps aux | grep ${PID} | grep [r]uncherrypyserver | tail -1 | awk '{print $6" "$2" "$3" "$12}')
   MEM=$(echo ${PS_COMMAND} | awk '{print $1}')
   CPU=$(echo ${PS_COMMAND} | awk '{print $3}')
   PROC=$(echo ${PS_COMMAND} | awk '{print $4}')
   MEM_MB=$(expr ${MEM} / 1024)
}

function do_sudo()
{
   HUE_SUDO=$1
   shift
   DATE=$1
   shift
   ARGS=$@
   sudo -u hue /bin/bash -c "/usr/bin/env" >> ${HUE_SUDO}_env_${DATE}
   sudo -u hue /bin/bash -c "/usr/bin/env which python2.6" >> ${HUE_SUDO}_python_${DATE}
}

function get_cm_process_dir()
{
   PID=$1
   shift
   if [[ -d ${AGENT_PROCESS_DIR} ]]
   then
      HUE_CONF_DIR=`strings /proc/${PID}/environ | grep HUE_CONF_DIR | awk -F\= '{print $2}'`
   else
      HUE_CONF_DIR=/etc/hue/conf
   fi
   HUE_INI=${HUE_CONF_DIR}/hue.ini
   CM_PROPS=${HUE_CONF_DIR}/cloudera-monitor.properties
}

function do_instances()
{
   HUE_PORT=$1
   ${MKDIR} ${HUE_CONFS}
   if [[ -d ${AGENT_PROCESS_DIR} ]]
   then
      for x in `find ${AGENT_PROCESS_DIR}/*hue-HUE_SERVER -name "hue.ini" -exec grep -H ${HUE_PORT} {} \; | awk -F\/ '{print $6}' | sort -n | tail -3`
      do
         cp -pr ${AGENT_PROCESS_DIR}/$x ${HUE_CONFS}
      done
   else
      cp -pr /etc/hue/conf ${HUE_CONFS}/0-hue-HUE_SERVER
   fi
   for x in `find ${HUE_CONFS} -name "*" -type f`
   do
      sed -i "/password/Id" $x
   done
}

main "$@"
