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

#This script will grab current Hue configuration for ldap
#and run ldapsearch commands to validate the config
#NOTE: This script requires ldapsearch to be installed

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
  OUTPUT_DIR=/tmp/hue_ldap_test
  TEST_USER=
  TEST_GROUP=
  HUE_CONF_DIR=
  GETOPT=`getopt -n $0 -o o:,u:,g:,c:,v,h \
      -l outdir:,user:,group:,conf:,verbose,help \
      -- "$@"`
  eval set -- "$GETOPT"
  while true;
  do
    case "$1" in
    -o|--outdir)
      OUTPUT_DIR=$2
      shift 2
      ;;
    -u|--user)
      TEST_USER=$2
      shift 2
      ;;
    -g|--group)
      TEST_GROUP=$2
      shift 2
      ;;
    -c|--conf)
      HUE_CONF_DIR=$2
      shift 2
      ;;
    -v|--verbose)
      VERBOSE=1
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

Tests Hue Server Ldap Config by runnning ldapsearch:

OPTIONS
   -o|--outdir <outdir>    Location to dump ldap test report - default /tmp/hue_ldap_test.
   -u|--user <user>        Required: User that exists in ldap to search for
   -g|--group <group>      Group that exists in ldap to search for - default, does not search for group.
   -c|--conf <dir>         Custom Hue conf directory with hue.ini for quicker testing - default, hue process dir.
   -h|--help               Show this message.
EOF
}

debug()
{
   if [[ ! -z $VERBOSE ]]
   then
      echo "$1"
   fi
}

report()
{
   echo "$1" | tee -a ${REPORT_FILE}
}

message()
{
   case "$1" in
   "SEARCH_METHOD")
     MESSAGE="WARN: ldap_username_pattern, nt_domain and search_bind_authentication are exclusive, only one should be set at a time."
     ;;
   *)
     MESSAGE="Unknown message type"
     ;;
   esac
   if [[ -z $2 ]]
   then
     echo "${MESSAGE}" | tee -a ${REPORT_FILE}
   fi
}

main()
{
   parse_arguments "$@"

   LDAPSEARCH=$(which ldapsearch)

   if [[ -z ${TEST_USER} ]]
   then
      echo "-u <ldapuser> required"
      usage
      exit 1
   fi

   if [[ ! ${USER} =~ .*root* ]]
   then
      echo "Script must be run as root: exiting"
      exit 1
   fi

   if [[ ! -f ${LDAPSEARCH} ]]
   then
      echo "ldapsearch not found, please install ldapsearch"
      exit 1
   else
      LDAPSEARCH_COMMAND="${LDAPSEARCH} -x -LLL"
   fi

   AGENT_PROCESS_DIR="/var/run/cloudera-scm-agent/process"
   PARCEL_DIR=/opt/cloudera/parcels/CDH
   ORACLE_HOME=/opt/cloudera/parcels/ORACLE_INSTANT_CLIENT/instantclient_11_2/
   LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${ORACLE_HOME}

   if [ ! -d "/usr/lib/hadoop" ]
   then
      CDH_HOME=$PARCEL_DIR
   else
      CDH_HOME=/usr
   fi

   if [[ -z ${HUE_CONF_DIR} ]]
   then
      if [ -d "${AGENT_PROCESS_DIR}" ]
      then
         HUE_CONF_DIR="${AGENT_PROCESS_DIR}/`ls -1 ${AGENT_PROCESS_DIR} | grep HUE | sort -n | tail -1 `"
      else
         HUE_CONF_DIR="/etc/hue/conf"
      fi
   fi
   TMP_ENV_FILE=${HUE_CONF_DIR}/hue_tmp_env.sh
   TMP_PASS_FILE=${HUE_CONF_DIR}/hue_tmp_ldap_pass.txt
   TMP_FILE=${HUE_CONF_DIR}/hue_tmp.txt
   touch ${TMP_ENV_FILE}
   chmod 600 ${TMP_ENV_FILE}
   touch ${TMP_PASS_FILE}
   chmod 600 ${TMP_PASS_FILE}
   mkdir -p ${OUTPUT_DIR}
   REPORT_FILE=${OUTPUT_DIR}/hue_ldap_report.txt
   rm -f ${REPORT_FILE}

   if [ -d "${CDH_HOME}/lib/hue/build/env/bin" ]
   then
      COMMAND="${CDH_HOME}/lib/hue/build/env/bin/hue shell"
   else
      COMMAND="${CDH_HOME}/share/hue/build/env/bin/hue shell"
   fi

   export CDH_HOME HUE_CONF_DIR ORACLE_HOME LD_LIBRARY_PATH COMMAND
   report "CDH_HOME: ${CDH_HOME}"
   report "HUE_CONF_DIR: ${HUE_CONF_DIR}"
   report ""

   ${COMMAND} >> /dev/null 2>&1 <<EOF
import desktop.conf

def write_property( hue_ldap_conf_file, ldap_config, property_name):
  if property_name != "bind_password":
    try:
      func = getattr(ldap_config, "%s" % (property_name.upper()))
    except AttributeError:
      print 'function not found "%s" ()' % (property_name.upper().get())
    else:
      property_value=func.get()
  else:
    try:
      property_value = desktop.conf.get_ldap_bind_password(ldap_config)
    except AttributeError:
      property_value = ldap_config.BIND_PASSWORD.get()
  hue_ldap_conf_file.write("%s=\"%s\"\n" % (property_name,property_value))
  return

hue_ldap_conf_file = open('${TMP_ENV_FILE}', 'w')
hue_ldap_conf_file.write("#!/bin/bash\n")
server = None
ldap_config = desktop.conf.LDAP.LDAP_SERVERS.get()[server] if server else desktop.conf.LDAP

write_property( hue_ldap_conf_file, ldap_config, "ldap_url")
write_property( hue_ldap_conf_file, ldap_config, "bind_dn")
write_property( hue_ldap_conf_file, ldap_config, "bind_password")
write_property( hue_ldap_conf_file, ldap_config, "ldap_cert")
write_property( hue_ldap_conf_file, ldap_config, "search_bind_authentication")
write_property( hue_ldap_conf_file, ldap_config, "base_dn")
write_property( hue_ldap_conf_file, ldap_config, "nt_domain")
write_property( hue_ldap_conf_file, ldap_config, "use_start_tls")
write_property( hue_ldap_conf_file, ldap_config, "ldap_username_pattern")
write_property( hue_ldap_conf_file, ldap_config, "follow_referrals")
write_property( hue_ldap_conf_file, ldap_config.USERS, "user_filter")
write_property( hue_ldap_conf_file, ldap_config.USERS, "user_name_attr")
write_property( hue_ldap_conf_file, ldap_config.GROUPS, "group_filter")
write_property( hue_ldap_conf_file, ldap_config.GROUPS, "group_name_attr")
write_property( hue_ldap_conf_file, ldap_config.GROUPS, "group_member_attr")
EOF

source ${TMP_ENV_FILE}

if [[ -z ${ldap_url} ]]
then
   report "Required attribute ldap_url is not set"
   exit 1
else
   LDAPSEARCH_COMMAND="${LDAPSEARCH_COMMAND} -H ${ldap_url}"
fi

if [[ -z ${ldap_cert} || ${ldap_cert} =~ .*None.* ]]
then
   LDAPSEARCH_COMMAND="LDAPTLS_REQCERT=never ${LDAPSEARCH_COMMAND}"
else
   LDAPSEARCH_COMMAND="LDAPTLS_REQCERT=ALLOW LDAPTLS_CACERT=${ldap_cert} ${LDAPSEARCH_COMMAND}"
fi

LDAPSEARCH_COMMAND_NOBASE=${LDAPSEARCH_COMMAND}
if [[ -z ${base_dn} || ${base_dn} == "None" ]]
then
   if [[ -z ${ldap_username_pattern} || ${ldap_username_pattern} == "None" ]]
   then
      report "WARN: base_dn is not set and may be required"
   fi
else
   LDAPSEARCH_COMMAND="${LDAPSEARCH_COMMAND} -b \"${base_dn}\""
fi

LDAPSEARCH_COMMAND_NOAUTH=${LDAPSEARCH_COMMAND}
if [[ ! -z ${bind_dn} && ${bind_dn} != "None" ]]
then
   if [[ -z ${bind_password} || ${bind_password} == "None" ]]
   then
      report "WARN: if bind_dn is set, then bind_password is required"
   fi
   if [[ ! -z ${nt_domain} && ${nt_domain} != "None" ]]
   then
      bind_dn=${bind_dn}@${nt_domain}
   fi
   echo -n "${bind_password}" > ${TMP_PASS_FILE}
   LDAPSEARCH_COMMAND="${LDAPSEARCH_COMMAND} -D ${bind_dn// /\\ } -y ${TMP_PASS_FILE}"
   LDAPSEARCH_COMMAND_NOBASE="${LDAPSEARCH_COMMAND} -D ${bind_dn// /\\ } -y ${TMP_PASS_FILE}"
fi

SEARCH_METHOD_FLAG=
if [[ ${search_bind_authentication} == "True" ]]
then
   if [[ ! -z ${nt_domain} && ${nt_domain} != "None" ]]
   then
      message "SEARCH_METHOD" ${SEARCH_METHOD_FLAG}
      SEARCH_METHOD_FLAG=true
   fi
   if [[ ! -z ${ldap_username_pattern} && ${ldap_username_pattern} != "None" ]]
   then
      message "SEARCH_METHOD" ${SEARCH_METHOD_FLAG}
      SEARCH_METHOD_FLAG=true
   fi
fi

if [[ ! -z ${nt_domain} && ${nt_domain} != "None"  ]]
then
   if [[ ${search_bind_authentication} == "True" ]]
   then
      message "SEARCH_METHOD" ${SEARCH_METHOD_FLAG}
      SEARCH_METHOD_FLAG=true
   fi
   if [[ ! -z ${ldap_username_pattern} && ${ldap_username_pattern} != "None" ]]
   then
      message "SEARCH_METHOD" ${SEARCH_METHOD_FLAG}
      SEARCH_METHOD_FLAG=true
   fi
fi

if [[ ! -z ${ldap_username_pattern} && ${ldap_username_pattern} != "None"  ]]
then
   if [[ ${search_bind_authentication} == "True" ]]
   then
      message "SEARCH_METHOD" ${SEARCH_METHOD_FLAG}
      SEARCH_METHOD_FLAG=true
   fi
   if [[ ! -z ${nt_domain} && ${nt_domain} != "None" ]]
   then
      message "SEARCH_METHOD" ${SEARCH_METHOD_FLAG}
      SEARCH_METHOD_FLAG=true
   fi
fi

USER_FILTER="(&(${user_filter})(${user_name_attr}=${TEST_USER}))"
GROUP_FILTER="(&(${group_filter})(${group_name_attr}=${TEST_GROUP}))"
cat ${TMP_ENV_FILE} | grep -v bind_password | grep -v bash >> ${REPORT_FILE}
report ""
if [[ ! -z ${ldap_username_pattern} && ${ldap_username_pattern} != "None"  ]]
then
   LDAPSEARCH_USER_COMMAND="${LDAPSEARCH_COMMAND_NOBASE} -b \"${ldap_username_pattern//\<username\>/${TEST_USER}}\""
else
   LDAPSEARCH_USER_COMMAND="${LDAPSEARCH_COMMAND} '${USER_FILTER}'"
fi
report "Running ldapsearch command on user ${TEST_USER}:"
report "${LDAPSEARCH_USER_COMMAND}"
eval ${LDAPSEARCH_USER_COMMAND} 2>&1 | grep -vi password | tee ${TMP_FILE}
USER_BIND_DN=`grep -i "dn:" ${TMP_FILE} | awk -F\: '{print $2}'`
cat ${TMP_FILE} >> ${REPORT_FILE}

report ""
LDAPSEARCH_USER_COMMAND="${LDAPSEARCH_COMMAND_NOBASE} '(${user_name_attr}=${TEST_USER})'"
report "Running ldapsearch command on user ${TEST_USER} without base or filter:"
report "${LDAPSEARCH_USER_COMMAND}"
eval ${LDAPSEARCH_USER_COMMAND} 2>&1 | grep -vi password | tee -a ${REPORT_FILE}

report ""
if [[ ! -z ${TEST_GROUP} ]]
then
   LDAPSEARCH_GROUP_COMMAND="${LDAPSEARCH_COMMAND} '${GROUP_FILTER}'"
   report "Running ldapsearch command on group ${TEST_GROUP}:"
   report "${LDAPSEARCH_GROUP_COMMAND}"
   eval ${LDAPSEARCH_GROUP_COMMAND} 2>&1 | tee -a ${REPORT_FILE}
   report ""
   LDAPSEARCH_GROUP_COMMAND="${LDAPSEARCH_COMMAND_NOBASE} '(${group_name_attr}=${TEST_GROU})'"
   report "Running ldapsearch command on group ${TEST_GROUP} without base or filter:"
   report "${LDAPSEARCH_GROUP_COMMAND}"
   eval ${LDAPSEARCH_GROUP_COMMAND} 2>&1 | tee -a ${REPORT_FILE}
fi
report ""

LDAPSEARCH_ROOT_COMMAND="${LDAPSEARCH_COMMAND_NOBASE} -s base -b ''"
report "Running ldapsearch command on root dse:"
report "${LDAPSEARCH_ROOT_COMMAND}"
eval ${LDAPSEARCH_ROOT_COMMAND} 2>&1 | tee -a ${REPORT_FILE}

LDAPSEARCH_USER_BIND_COMMAND="${LDAPSEARCH_COMMAND_NOAUTH} -D ${USER_BIND_DN// /\\ } -W '${USER_FILTER}' dn ${user_name_attr}"
report "Running ldapsearch command binding as ${USER_BIND_DN}(${TEST_USER}):"
report "When prompted please enter ${USER_BIND_DN}'s password:"
report "${LDAPSEARCH_USER_BIND_COMMAND}"
eval ${LDAPSEARCH_USER_BIND_COMMAND} 2>&1 | tee -a ${REPORT_FILE}

echo "View ${REPORT_FILE} for more details"

rm -f ${TMP_ENV_FILE} ${TMP_PASS_FILE} ${TMP_FILE}

}

main "$@"
