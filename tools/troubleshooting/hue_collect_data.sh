#!/bin/bash

#NOTE: This script requires curl, strace and lsof to be installed. It
# must be run on the Hue server. Set HUE_USER to a user in Hue with 
# Superuser access to get thread dumps.  Set HUE_PASSWORD to HUE_USER's 
# password.

# Location for output files
OUTPUT_DIR=/tmp/hue_collect_data

# Location of Hue logs

HUE_LOG_DIR=/var/log/hue

# Please change USER to contain the user to login
HUE_USER="admin"

# Please change PASSWORD to contain the password for the above user
HUE_PASSWORD="admin"

# Set to true for more debug
VERBOSE="false"

#How many seconds of strace to capture on each run
STRACE_WAIT=15

#Number of data gathering runs
RUNS=4

#Time to wait between each run
RUN_WAIT=30

main()
{

if [[ ! ${USER} =~ .*root* ]]
then
   echo "Script must be run as root: exiting"
   exit 1
fi

get_cm_process_dir

#This is necessary to handle AD auth, doesn't seem to hurt non-ad auth
#if they have multiple ldap servers or for some reason the drop down
#at login says something other than "LDAP", then this must match the drop
#down
HUE_AUTH_SERVER="LDAP"
DATE=$(date '+%Y%m%d-%H%M')
OUTPUT_DIR=${OUTPUT_DIR}/${DATE}
HOSTNAME=$(hostname)
HUE_SERVER=${HOSTNAME}
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
HUE_USAGE_FILE=${OUTPUT_DIR}/cpu_mem_usage
HUE_THREADS_FILE=${OUTPUT_DIR}/threads
HUE_STRACE_FILE=${OUTPUT_DIR}/strace
HUE_LSOF_FILE=${OUTPUT_DIR}/lsof
COOKIE_JAR=${OUTPUT_DIR}/${USER}_cookie.jar

echo "Making ${OUTPUT_DIR} if it does not exist"
mkdir -p ${OUTPUT_DIR}

hue_login
echo "Gathering info:"
for (( x=1; x<=${RUNS}; x++ ))
do
   DATE=$(date '+%Y%m%d-%H%M%S')
   echo "DATE: ${DATE}"
   echo "Getting a thread dump:"
   do_curl \
	GET \
	"${HUE_THREADS_URL}" \
	-L -o ${HUE_THREADS_FILE}_${DATE}

   echo "Getting CPU and Memory usage"
   do_ps
   echo "PID CPU MEM MEM_MB" >> ${HUE_USAGE_FILE}_${DATE}
   echo "${PID} ${CPU} ${MEM} ${MEM_MB}" >> ${HUE_USAGE_FILE}_${DATE}
   echo "free -m results" >> ${HUE_USAGE_FILE}_${DATE}
   free -m >> ${HUE_USAGE_FILE}_${DATE}

   echo "Getting strace"
   do_strace \
        ${PID} \
        ${STRACE_WAIT} \
        -o ${HUE_STRACE_FILE}_${DATE} -T -t
   echo "Getting open connections"
   do_lsof \
        ${PID} \
        ${HUE_LSOF_FILE}_${DATE}

   sleep ${RUN_WAIT}
done

mkdir ${OUTPUT_DIR}/logs
cp -pr ${HUE_LOG_DIR}/* ${OUTPUT_DIR}/logs 

echo "Collecting done, please zip ${OUTPUT_DIR} and upload to the ticket"
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

   if [ -z ${LOG_FILE} ]
   then
      LOG_FILE=/tmp/lsof.log
   fi

   STRACE=$(which strace)
   if [ ! -f ${STRACE} ]
   then
      echo "strace not found, unable to collect strace info"
   else
      ${STRACE} -o ${LOG_FILE} -p ${SPID} ${ARGS} &
      sleep ${WAIT}
      kill $!
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
   PS_COMMAND=$(ps aux | grep [r]uncherrypyserver | awk '{print $6" "$2" "$3" "$12}')
   MEM=$(echo ${PS_COMMAND} | awk '{print $1}')
   MEM_MB=$(expr ${MEM} / 1024)
   PID=$(echo ${PS_COMMAND} | awk '{print $2}')
   CPU=$(echo ${PS_COMMAND} | awk '{print $3}')
   PROC=$(echo ${PS_COMMAND} | awk '{print $4}')
}

function get_cm_process_dir()
{
   if [[ -d /var/run/cloudera-scm-agent/process ]]
   then
      HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/`ls -1 /var/run/cloudera-scm-agent/process | grep HUE | sort -n | tail -1 `"
   else
      HUE_CONF_DIR=/etc/hue/conf
   fi
   HUE_INI=${HUE_CONF_DIR}/hue.ini
}

debug()
{

  if [[ ! -z $VERBOSE ]]
  then
    echo "$1" >> ${LOG_FILE}
  fi

}

main "$@"
