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

#Restarts Hue

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
  CM_HOSTNAME="localhost"
  CM_PORT="7180"
  CM_HTTP="http"
  CM_API="v11"
  CM_USERNAME="admin"
  CM_PASSWORD_INPUT=
  ENCODE_LOCATION=/var/lib/hue

  GETOPT=`getopt -n $0 -o c:,p:,u:,w:,n,s,l:,h \
      -l cmhost:,cmport:,cmuser:,cmpass:,newpass,ssl,encodeloc:,help \
      -- "$@"`
  eval set -- "$GETOPT"
  while true;
  do
    case "$1" in
    -c|--cmhost)
      CM_HOSTNAME=$2
      shift 2
      ;;
    -p|--cmport)
      CM_PORT=$2
      shift 2
      ;;
    -u|--cmuser)
      CM_USERNAME=$2
      shift 2
      ;;
    -w|--cmpass)
      CM_PASSWORD_INPUT=$2
      shift 2
      ;;
    -n|--newpass)
      NEW_PASS=1
      shift
      ;;
    -s|--ssl)
      CM_HTTP="https"
      shift
      ;;
    -l|--encodeloc)
      ENCODE_LOCATION=$2
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

  ENC_PASSWORD_FILE=${ENCODE_LOCATION}/`basename "$0" | awk -F\. '{print $1}'`.enc
}

usage() {
cat << EOF
usage: $0 [options]

Restarts Hue instances with high memory utilization through CM:

OPTIONS
   -c|--cmhost <hostname>      Host where CM is running - default localhost.
   -p|--cmport <port>          Port CM is running on - default ${CM_PORT}.
   -u|--cmuser <cm_user>       Admin User in CM - default admin.
   -w|--cmpass <user_pass>     Admin User password in CM, required on first run, no default. Will prompt
                               if not provided through this flag. Future runs will use
                               encrypted version in <enc_loc>/`basename "$0" | awk -F\. '{print $1}'`.enc
   -s|--ssl                    Enable SSL.
   -n|--newpass                Prompt for a new password.
   -l|--encodeloc <enc_loc>    Location to store encoded password in file - default /var/lib/hue.
   -v|--verbose                Enable verbose logging.
   -h|--help                   Show this message.
EOF
}

main() {

   parse_arguments "$@"

   if [[ ! ${USER} =~ .*root.* ]]
   then
      echo "Script must be run as root: exiting"
      exit 1
   fi

   if [[ ! -d ${ENCODE_LOCATION} ]]
   then
      mkdir -p ${ENCODE_LOCATION}
   fi

   if [[ ! -z ${CM_PASSWORD_INPUT} ]]
   then
      echo ${CM_PASSWORD_INPUT} | base64 > ${ENC_PASSWORD_FILE}
      chown root:root ${ENC_PASSWORD_FILE}
      chmod 600 ${ENC_PASSWORD_FILE}
   fi

   if [[ -z ${CM_PASSWORD_INPUT} ]]
   then
      if [[ ! -f ${ENC_PASSWORD_FILE} ]] || [[ ! -z ${NEW_PASS} ]]
      then
         message "CM Admin user password required on first run"
         read -s -p "Please enter password:" CM_PASSWORD_INPUT
         echo "New password provided"
         echo ${CM_PASSWORD_INPUT} | base64 > ${ENC_PASSWORD_FILE}
         chown root:root ${ENC_PASSWORD_FILE}
         chmod 600 ${ENC_PASSWORD_FILE}
      fi
   fi

   if [[ ! -f ${ENC_PASSWORD_FILE} ]]
   then
      message "CM Admin password has not been provided and this is"
      message "is first run of the script.  Please run again and"
      message "provide password."
      exit 1
   else
      CM_PASSWORD=`cat ${ENC_PASSWORD_FILE} | base64 --decode`
   fi

   if [[ ${CM_HTTP} =~ .*https.* ]]
   then
      if [[ ${CM_PORT} =~ .*7180.* ]]
      then
         CM_PORT=7183
      fi
   fi

   CLUSTERNAME=$(urlencode "$(curl -L -s -k -X GET -u ${CM_USERNAME}:${CM_PASSWORD} "${CM_HTTP}://${CM_HOSTNAME}:${CM_PORT}/api/${CM_API}/clusters" | grep '"name" :' | awk -F\" '{print $4}')")

   SERVICENAME=$(urlencode "$(curl -L -s -k -X GET -u ${CM_USERNAME}:${CM_PASSWORD} "${CM_HTTP}://${CM_HOSTNAME}:${CM_PORT}/api/${CM_API}/clusters/${CLUSTERNAME}/services" | grep -B1 '"HUE"' | grep '"name" :' | awk -F\" '{print $4}')")

   ROLES_JSON="{ \"items\" : [ \""

   while read -r ROLE
   do
      ROLES_JSON="${ROLES_JSON}${ROLE}\",\""
   done < <(curl -L -s -k -X GET -u ${CM_USERNAME}:${CM_PASSWORD} "${CM_HTTP}://${CM_HOSTNAME}:${CM_PORT}/api/${CM_API}/clusters/${CLUSTERNAME}/services/${SERVICENAME}/roles" | grep ${SERVICENAME}- | grep '"name" :' | awk -F\" '{print $4}')

   ROLES_JSON=$(echo ${ROLES_JSON} | sed "s/,\"$/ ] }/g")

   RESTART_API_URL="/api/${CM_API}/clusters/${CLUSTERNAME}/services/${SERVICENAME}/roleCommands/restart"

   message "Restarting Hue process -u ${CM_USERNAME}:${CM_PASSWORD}: ${CM_HTTP}://${CM_HOSTNAME}:${CM_PORT}${RESTART_API_URL}: Roles: ${ROLES_JSON}"
   RESULTS=`curl -s -X POST -u ${CM_USERNAME}:${CM_PASSWORD} -i -H "content-type:application/json" -d "${ROLES_JSON}" "${CM_HTTP}://${CM_HOSTNAME}:${CM_PORT}${RESTART_API_URL}"`
}

urlencode() {
    # urlencode <string>
    old_lc_collate=$LC_COLLATE
    LC_COLLATE=C

    local length="${#1}"
    for (( i = 0; i < length; i++ )); do
        local c="${1:i:1}"
        case $c in
            [a-zA-Z0-9.~_-]) printf "$c" ;;
            *) printf '%%%02X' "'$c" ;;
        esac
    done

    LC_COLLATE=$old_lc_collate
}

message()
{
  echo "$1"
}

main "$@"
